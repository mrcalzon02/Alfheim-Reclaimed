# Alfheim Golems — implementation plan

Status: **plan only; project scaffold, registrations and jar do not exist**  
Planned mod ID: `alfheim_golems`  
Planned artifact: `alfheim_golems-0.1.0.jar`  
Target: Minecraft 1.20.1, Forge 47.4.10, Java 17  
Gameplay contract: `../../../alfheim_reclaimed_design/ELVEN_GOLEMS.md`

## Mod boundary

This is a third independent first-party Gradle project beside `alfheim_companion` and
`alfheim_leyworks`. It owns golem entities, cores and effigies, the Manna Stone Command Gem,
work-order persistence and UI, machine adapters, Deep spawning and combat summon vessels.

It must not import companion memory, inference or command code. A future optional integration can
publish a read-only summary such as active/blocked counts; golem orders remain deterministic and
server-authoritative.

Initial hard dependency: Forge only. FTB Chunks/Teams support is an optional compile-time adapter
against the exact installed jars and fails closed for protected interaction when present but
unavailable. Alfheim Leyworks is a recipe/content integration, not a Java dependency; Manna Stone
Storage is addressed through Forge capabilities.

## Registration plan

### Entities

- `elven_worker_golem`: small persistent owned/wild entity; synced `Element` and `Disposition`.
- `elven_artisan_golem`: player-height persistent owned/wild entity; synced element/disposition.
- `elven_sentinel_golem`: player-height wild or temporary-summon entity; summoned instances carry
  owner UUID and expiry tick but no inventory capability.

`Element` is the closed enum FIRE/WATER/EARTH/AIR. `Disposition` is OWNED/WILD/SUMMONED. Invalid or
missing saved values fall back safely (wild Earth for natural entities; no owner is ever inferred).

### Items

- reusable `manna_stone_command_gem`;
- four aligned variants of `simple_golem_core`, `advanced_golem_core` and `combat_golem_core`;
- four Worker effigies and four Artisan effigies;
- four consumable Sentinel Vessels;
- damaged cores, core fragments, chassis plates, control lattice, movement lattice and temporal
  binding ingredients required by the layered recipes.

Physical aligned item IDs are preferred over hidden NBT recipes in 1.20.1: JEI can display and trace
them, tags can group each core family, and recipes do not require a custom serializer merely to set
an element.

### Data

- entity attributes, damage-type/element tags, loot tables and spawn biome modifier;
- recipes and advancement/quest triggers;
- item tags `simple_golem_cores`, `advanced_golem_cores`, `combat_golem_cores`,
  `golem_core_fragments`, `golem_chassis_materials`;
- block tags for valid Deep floors, crafting stations and supported furnace families;
- configuration for ranges, capacities, scheduler budget, spawn weights, loot caps, summon lifetime
  and per-owner golem limits.

## Code shape

```text
com.continuityworks.alfheimgolems
  AlfheimGolems
  registry/        ModEntities, ModItems, ModMenus, ModDataSerializers
  entity/          WorkerGolem, ArtisanGolem, SentinelGolem, Element, Disposition
  brain/           bounded goals and state-machine activities
  inventory/       golem item handlers, reservations, transfer transactions
  order/           WorkOrder, WorkStep, Endpoint, ItemFilter, OrderScheduler
  crafting/        recipe matching, grid execution, remainder handling
  machine/         MachineAdapter SPI and adapter registry
  machine/vanilla/ FurnaceAdapter, CraftingTableAdapter, GenericItemHandlerAdapter
  command/         gem binding, order validation, group control
  network/         bounded client requests and server snapshots
  menu/            gem, order editor and golem inventory menus
  integration/ftb/ claim/team adapter loaded only when its mods are present
  spawn/           Deep placement predicates and density controls
  summon/          vessel placement and sentinel lifetime/ownership
  data/            SavedData for networks, groups and work orders
```

The entity goal layer handles walking, following, staying, fighting and reaching a station. The
order state machine decides only among validated steps. Inventory mutation is isolated from both so
it can be unit-tested without entity navigation.

## Work-order model

Minimum step enum:

- `TAKE`, `PUT`, `FUEL`, `CRAFT_2X2`, `CRAFT_3X3`, `OPERATE`, `WAIT_FOR_RESULT`, `RETURN_HOME`.

Every step carries a bounded endpoint ID and filter ID. Positions/faces live in server SavedData and
are created only after a server ray trace of the gem interaction. The client may request an enum,
quantity and known ID; it may not supply an arbitrary dimension/position as authority.

The execution state machine is:

`validate -> simulate -> reserve capacity -> extract to golem -> navigate -> revalidate -> insert ->
wait/observe -> collect output -> deliver -> complete`.

After any committed extraction, the golem inventory is the recovery ledger. There is no rollback
that invents a copy in the source. Cancellation sends carried items to the configured return endpoint
or pauses for the owner when that endpoint cannot accept them.

## Machine-adapter contract

An adapter must provide:

1. a side-safe predicate proving it owns the target block entity;
2. accepted input/fuel/catalyst slots and simulation support;
3. an observable start/completion state or a safe output predicate;
4. extraction rules that cannot steal unrelated products;
5. claim and reach revalidation before each mutation;
6. automated tests and one dedicated-server acceptance scenario.

Adapters are admitted in this order:

1. vanilla furnace, blast furnace and smoker;
2. generic sided `IItemHandler` transport with no claim that it starts a process;
3. Manna Stone Storage regression case;
4. Create basin/depot or other selected Create machines after API audit;
5. Ars Nouveau apparatus/chambers;
6. Botania/MythicBotany inventories and open-world processors;
7. Occultism and remaining pack machines.

An adapter stays absent when the installed version offers no safe observable contract. The UI says
“unsupported machine”; it never guesses slot meaning.

## Goal-oriented continuous development

Development is organized around playable outcomes, not around completing packages or registering a
long list of items. Each goal must leave the mod in a coherent, testable state. A stage can contain
many small changes, but none may claim the next acceptance state until its gate evidence exists.

**Zero-manual-validation rule:** no stage or production gate may require the pack owner to launch a
world, perform a playtest, inspect a screen or sign off visually. Codex owns the validation work.
Runtime gates use automated GameTests, scripted dedicated-server scenarios, scripted fresh-world
surveys and automated client launches/captures. A presentation detail that cannot be checked by an
automated harness may be recorded as non-blocking polish, but it cannot be made a condition for the
next development stage.

### Goal hierarchy

| Level | Meaning | Example |
|---|---|---|
| Product goal | durable player outcome | “A player can delegate repetitive workshop work without losing items.” |
| Stage goal | one independently valuable vertical capability | “One Fire Worker safely moves items between two chests.” |
| Slice | smallest end-to-end change that advances the stage | bind owner; mark endpoint; move one stack; expose one status |
| Task | implementation unit with no standalone acceptance claim | class, model, packet, recipe or test fixture |

A task is not allowed to masquerade as progress merely because it compiles. Stage progress is the
count of accepted slices and resolved risks. The durable live ledger is `GOAL_LEDGER.md`.

### The development loop

Every slice follows the same loop:

1. **Frame the goal.** Record player outcome, non-goals, dependencies and the riskiest assumption.
2. **Write the acceptance examples first.** Include the success path and at least one loss,
   duplication, ownership, unload or expiry failure path as applicable.
3. **Spike only the uncertainty.** Inspect the installed API or make a disposable proof when a modded
   machine, entity hook or claims call is uncertain. A spike does not ship and cannot advance status.
4. **Implement the thinnest vertical slice.** Carry the behavior from input/UI through server
   validation to world mutation, persistence and player-visible status.
5. **Run the proportional gate.** Unit/static checks first, then GameTest/dedicated server, then
   scripted fresh-world or automated client validation when the behavior requires it.
6. **Measure and record.** Store command, result, artifact hash, runtime world, known limits and
   acceptance state in the goal ledger and `EXECUTION_STATE.md`.
7. **Decide.** Accept, repair the same slice, deliberately defer it with a resumption condition, or
   reject the approach. Do not begin dependent breadth while a safety-critical gate is red.

### Acceptance states and WIP limits

`proposed -> ready -> active -> static validated -> automated runtime validated -> automated
client/fresh-world validated -> production admitted`.

`deferred` requires a named reason and resumption condition. `rejected` records the evidence and
replacement approach. `blocked` is reserved for an external dependency or decision that prevents
meaningful work.

Only one safety-critical slice may be **active** at a time: inventory transaction, ownership/claims,
persistence/migration, spawning, or combat expiry. One unrelated visual/content slice may run beside
it. This keeps diagnosis bounded while still allowing art or text to progress.

### Universal gates

| Gate | Question | Required evidence |
|---|---|---|
| U0 — ready | Is the outcome bounded and testable? | goal card, non-goals, dependency check, acceptance examples |
| U1 — compile/data | Is the artifact structurally valid? | Java 17 `test build`, metadata/content check, JSON/resource parse |
| U2 — invariant | Can it lose, duplicate, steal or invent state? | unit/property tests plus adversarial GameTests for the relevant invariant |
| U3 — dedicated server | Is registration, networking and persistence side-safe? | clean full-pack boot, scenario run, save/restart/reload, clean shutdown |
| U4 — multiplayer authority | Does the server reject the wrong actor? | owner/team/non-owner, revoked permission and malformed/stale packet cases |
| U5 — automated client | Does the rendered interaction satisfy objective presentation rules? | scripted client launch and interaction; captured frames at GUI scales 1-4; model/texture resolution, hitbox, label bounds, contrast and state-icon assertions |
| U6 — world/economy | Does it appear and pay out at the intended rate? | multi-seed spawn/loot survey and progression cost comparison |
| U7 — performance | Is representative scale affordable? | controlled MSPT/entity/ticket measurements against a baseline |
| U8 — admission | Is it taught, recoverable and shippable? | quest/JEI path, config defaults, migration note, byte-identical client/server jars |

U2, U3 and U4 are stop gates. A red result returns the current slice to **active**; it cannot be
waived by later client success. U5-U7 may be deliberately deferred only when that behavior is not yet
enabled in normal progression. No deferral may be converted into a request for owner-run validation.

## Staged delivery plan

### G0 — foundation, reproducibility and observable contracts

**Player outcome:** none yet. This stage exists so every later playable result can be built and
measured repeatably.

**Deliverables:**

- independent ForgeGradle project, wrapper, Java 17 toolchain, mod/pack metadata and license;
- Forge-only hard dependency plus isolated optional-integration source boundaries;
- registries with no gameplay content beyond test fixtures;
- closed `Element`, `Disposition`, `OrderState`, `WorkStepType` and `FailureReason` enums;
- pure interfaces for endpoints, filters, reservations, transfers and machine adapters;
- versioned SavedData envelope with explicit schema version and empty migration registry;
- server configuration with bounds validation and safe defaults;
- `check_alfheim_golems` artifact/resource checker and a deterministic jar install/copy procedure;
- operator-only diagnostics returning scheduler counts, active orders, sleeping entities and last
  bounded failure reasons without dumping inventory contents.

**Slices:** G0.1 scaffold; G0.2 domain contracts; G0.3 persistence envelope; G0.4 diagnostics and
artifact checker.

**Exit gate:** U0-U3. Clean `test build`; the reobfuscated jar has `mods.toml`, `pack.mcmeta` and no
examplemod residue; an empty mod reaches `Done` in the full dedicated pack, saves/restarts cleanly and
loads with all optional adapter mods absent in a reduced test profile.

**Failure rule:** metadata, side-loading or persistence defects are repaired in G0. No entity or item
registration starts until this gate is green.

### G1 — trustworthy Fire Worker vertical slice

**Player outcome:** a player can create one small Fire Worker and order one real stack from one chest
to another, with understandable recovery when the route cannot finish.

**Deliverables:** Worker entity/inventory, provisional Fire model, Simple Fire Core and effigy,
Command Gem binding, follow/stay/pause/dismantle, server-ray-traced Take/Put endpoints, one-stack
route, status surface and ownership persistence.

**Slices:**

- G1.1 spawn/bind/follow/stay and owner rejection;
- G1.2 endpoint marking and preview without mutation;
- G1.3 single-stack transaction through the golem inventory;
- G1.4 repeated route, pause/resume and safe cancellation;
- G1.5 dismantle only when idle, healthy and empty.

**Exit gate:** U1-U5. The route passes success, destination-full, source-removed, chunk-unloaded,
permission-revoked-between-checks, restart-mid-step, death-while-carrying and two-golems-racing cases.
No case duplicates or deletes a stack. A second player cannot bind, edit, dismantle or inspect private
route details. GameTests prove the small hitbox can traverse one-block doors; an automated client
script captures binding, route preview and blocked status and asserts that labels remain inside the
screen at the supported GUI scales.

**Failure rule:** any duplication, loss or ownership breach disables work execution behind a config
kill switch and returns G1 to active. Later crafting work does not begin.

### G2 — complete Worker tier: four elements, furnaces and 2x2 craft

**Player outcome:** Workers can run a small early-game workshop: sort supplies, keep a furnace fueled,
collect outputs and batch simple recipes.

**Deliverables:** all four Worker alignments/models, shared element strategy, groups and filters,
quantity/stock policies, furnace/smoker/blast-furnace adapters, 2x2 shaped/shapeless crafting,
remainder handling, home/return endpoint and per-owner limits.

**Slices:** G2.1 four alignments with no behavior forks; G2.2 filters/stock policy; G2.3 furnace
input; G2.4 fuel and output; G2.5 2x2 craft once; G2.6 repeated batch craft and recovery.

**Exit gate:** U1-U5 and an early U7 sample. Every element completes chest -> furnace -> chest and
the same 2x2 recipe. Fuel containers, recipe remainders, mixed inputs, full outputs, hopper
competition and cancellation preserve exact accounting. Element bonuses change capacity/timing only,
never output count. Eight Workers run for thirty minutes without chunk tickets or log spam.

**Progression gate:** the Command Gem and Simple Core recipes are reachable in proposed Era III from
both spines; JEI shows the full path; no removed recipe is required.

### G3 — expensive core economy and recoverable construction

**Player outcome:** the player understands and can complete the prodigious deterministic route to all
Simple and Advanced cores before wild salvage is introduced as its alternative.

**Deliverables:** four aligned variants per core family, chassis parts/lattices, Botania and Ars
process stages, Worker/Artisan effigies, damaged-core data model, dismantling/death salvage and quest
cost exposition.

**Slices:** G3.1 recipe inventory audit; G3.2 Simple chain; G3.3 Advanced recursion; G3.4 effigy
lifecycle; G3.5 damage/salvage accounting; G3.6 quest and JEI teaching.

**Exit gate:** U1-U3 and progression simulation. Every ingredient ID exists, every transitive route is
reachable in its era, Advanced consumes Simple, and total costs are generated into a review table.
Create -> place -> save -> dismantle never multiplies cores or shells; death is strictly lossy and
cannot be used as a conversion exploit.

**Failure rule:** recipe costs are tuned at their manifest/generator authority. No hand-edited output
may diverge from the audited cost table.

### G4 — Artisan, 3x3 crafting and the first real machine adapter

**Player outcome:** one player-height Artisan can complete a multi-step workshop order involving a
3x3 recipe and at least one pack machine beyond vanilla storage.

**Deliverables:** Artisan entity/inventory/model, Advanced Core/effigy activation, 3x3 recipe executor,
bounded order graph, reservation contention, Manna Stone Storage regression adapter and one audited
modded processing adapter chosen after inspecting the installed version.

**Slices:** G4.1 Artisan lifecycle; G4.2 3x3 craft once/remainders; G4.3 bounded sequence; G4.4 Manna
Stone Storage capability case; G4.5 first modded adapter; G4.6 recovery and status UI.

**Exit gate:** U1-U5. A dedicated-server scenario performs source -> craft -> machine -> output with a
server restart at every state boundary. The adapter passes detection, wrong-side, input rejection,
completion evidence, unrelated-output protection and mod-absent tests. Two Artisans contending for
the same last ingredients produce one legal output, not two partial jobs.

**Adapter rule:** one machine family is one independently gated goal card. Adding five shallow
adapters does not advance G4 faster than proving one complete adapter.

### G5 — wild Deep ecology and salvage economy

**Player outcome:** a Deep expedition reliably encounters ancient golems and can trade danger/time
for a meaningful reduction in the resource burden of building owned golems.

**Deliverables:** WILD disposition and behaviors for all three chassis, four element presentations,
biome modifier, depth/floor/light/density/spawn-hub predicates, loot tables, damaged-core restoration,
spawn/loot survey tooling and discovery documentation. Wild versions remain uncommandable.

**Slices:** G5.1 wild Worker spawn/loot; G5.2 all Worker elements; G5.3 Artisan; G5.4 Sentinel; G5.5
restoration; G5.6 multi-seed ecology/economy tune.

**Exit gate:** U1-U7. Survey at least three fresh Alfheim seeds and multiple Deep origins. Report
attempts, successful spawns and living counts by chassis, element, Y band and floor tag. Surface,
Midgard, peaceful and spawn-hub exclusion counts are zero. A representative expedition saves a
defined fraction of one core's bulk inputs; pristine complete-core yield remains below the agreed
cap. A deliberately constructed farm cannot exceed the configured living/drops budget.

**Conflict gate:** update `THE_DEEP.md`'s former “No mobs authored in” statement when implementation
begins, not while this remains a plan. Natural danger, Mine and Slash rewards and structure density
must be measured together before admission.

### G6 — consumable elemental combat Sentinels

**Player outcome:** the player can spend one expensive vessel for a brief, comprehensible allied
combat intervention that cannot become permanent or refund itself.

**Deliverables:** four Combat Core chains recursively consuming Advanced cores; four Sentinel Vessel
recipes/items; safe placement preview; summoned ownership/team target selector; elemental attacks;
120-second configurable lifetime; final-ten-second warning; logout/death/dimension/restart cleanup;
no inventory/loot/XP path.

**Slices:** G6.1 one Earth vessel and timer; G6.2 target authority/friendly fire; G6.3 expiry matrix;
G6.4 four element strategies; G6.5 full recipes/effects/UI; G6.6 combat balance.

**Exit gate:** U1-U5, U7 and economy review. Successful placement consumes exactly one vessel;
blocked/invalid placement consumes none. Timeout, death, owner logout/death, dimension separation,
chunk unload and server restart cannot preserve or reward a summoned Sentinel. Team members are
never legal targets. Four variants are distinct but remain below the agreed boss/companion power
ceiling.

**Failure rule:** any persistence or reward leak disables vessel use globally until repaired. It is
not mitigated with a tooltip.

### G7 — adapter expansion as continuous independent goals

**Player outcome:** Artisans progressively understand the pack's machines without making the base
mod fragile when optional mods update or disappear.

Each adapter family follows: installed-jar/API audit -> written contract -> fixture -> one machine
vertical slice -> failure matrix -> dedicated-server scenario -> optional-dependency absence ->
admission. Priority is Create, Ars Nouveau, Botania/MythicBotany, Occultism, then remaining machines
ranked by campaign use rather than mod count.

**Exit gate per adapter:** U0-U5 and the six-point adapter contract above. Version fingerprints and
supported block IDs are recorded. A changed installed jar automatically returns the adapter to
**needs revalidation**; it does not silently inherit old evidence.

**No final adapter count is promised.** Unsupported machine is an acceptable explicit state. Unsafe
generic operation is not.

### G8 — scale, onboarding and production admission

**Player outcome:** the complete system is understandable in normal play, stable at workshop scale
and recoverable across updates.

**Deliverables:** final models/animations/sounds, command-gem UX and accessibility, Jade/JEI/quest
integration, configuration comments, operator recovery commands, SavedData migrations, scheduler
profiling, spawn/loot/combat balance, multiplayer soak and release/install procedure.

**Exit gate:** all U gates. Representative 32-Worker/8-Artisan workshops meet the recorded MSPT
budget against a no-golem baseline; no unexpected chunk tickets remain; two-team multiplayer soak
passes; all golem acquisition routes are taught; old saves migrate through every shipped schema;
client and server jars are byte-identical; automated client captures and assertions cover every
command state and elemental model; the full validation ladder records the highest gate actually
reached. The owner is not assigned a manual acceptance step.

Production admission is per capability. A new adapter or later element bonus can remain experimental
without downgrading already admitted chest/furnace behavior, provided it is disabled by default and
isolated behind its feature flag.

## Test matrix

Pure unit tests cover filters, quantities, reservations, crafting-grid fit, remainders, element
serialization, order transitions, expiry math and loot caps. GameTests cover handlers, furnaces,
claim denial, save/reload and blocked paths. Dedicated-server runs cover registration, natural
spawning, optional-dependency absence and side safety. Automated client scripts cover models,
hitboxes, gem workflow, status legibility and summon effects using captured-frame and UI-bound
assertions; they do not ask the owner to play or review the result.

Every inventory scenario is tested for success, destination full, source removed, target unloaded,
permission revoked between simulation and commit, golem killed while carrying, restart mid-step and
two golems racing for the last stack.

## Shipping and tracking

Source remains under `first_party_mods/alfheim_golems/`. A built artifact is copied to both `mods/`
and `server/mods/` only after that wave's build and jar-content gates pass; the two copies must be
byte-identical. Acceptance state and current artifact belong in this document, intent in
`BACKLOG.md` B-92, live evidence in `EXECUTION_STATE.md`, and completed changes in `CHANGELOG.md`.

Current acceptance: **planned only**. No IDs, recipes, entities, spawn rules or jar described above
are registered in the game.
