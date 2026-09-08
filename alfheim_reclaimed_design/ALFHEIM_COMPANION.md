# Alfheim Companion — Design and Implementation Plan

Status: **integration prototype / clean build and unit validation; updated dedicated-server boot validated**  
Current artifact: `alfheim_companion-0.2.0.jar`  
Mod ID: `alfheim_companion`  
Target: Minecraft 1.20.1, Forge 47.4.10, Java 17  
Continuity Works blueprint API: version 1

## Purpose

Alfheim Companion adds one persistent, summonable elven companion to a server. The companion is a
local Minecraft entity with its own identity, memory, inventory and state. Normal movement, combat,
defence, retreat, following and interaction mechanics are deterministic Minecraft/Forge routines.
A very small local language model is reserved for ambiguous construction planning and occasional
ambient dialogue; it never directly mutates the world.

## Non-negotiable rules

1. Exactly one companion may exist at a time across all dimensions on the server.
2. The companion is a real local mob, not a remote service, player subclass, or owner impersonation.
3. It is summoned or recalled with the craftable `companion_sigil`; crouch-use dismisses it.
4. Summoning and dismissal use Enderman teleport particles and sound.
5. Summoning chooses a safe location no farther than five blocks from the owner.
6. A name is selected from a bounded elven name list on first creation and persists with memory.
7. Rapid repeated summoning raises a persistent agitation counter. Agitation affects preset dialogue
   and decays by one point per five in-game minutes. It never weakens safety or obedience.
8. Commands are recognized only when prefaced with the companion's current name, for example
   `Aelara, follow`. Unaddressed chat is ignored.
9. Destructive actions obey FTB claims. When FTB Chunks is installed but no compatible claims adapter
   is registered, destructive actions fail closed.
10. The companion asks before accepting or equipping an offered item. A second matching offer within
    ten seconds confirms the transfer.
11. Items, ingredients and placed blocks must come from real inventories. Nothing may be created from
    nothing unless the requesting player is in creative mode.
12. The inference engine is inactive when the companion is dismissed. Routine commands and behaviors
    do not invoke inference.
13. Ownership is a renewable 30-minute lease, not a permanent monopoly. A valid token holder cannot
    displace an active lessee and receives the bounded reply “Sorry, I’m currently busy!” The lease
    expires after 36,000 server ticks without a successful interaction; dismissal releases it early.
    On transfer, owner-scoped task, guard and quest context is cleared and rebuilt for the new lessee;
    the elf's identity, agitation and non-private world/personality memory remain continuous.
    An expired lease can be acquired only through Summon/Recall, not by stale chat or arbitrary wheel
    packets. A failed entity creation releases the attempted lease rather than leaving a ghost lock.
14. The one active physical entity fronts a dormant per-player binding. First binding randomizes name/
    personality and outfit. `/alfheimcompanion profile list|set`, `outfit list|set`, and `reset`
    manage only the issuing player's binding. Death marks that binding fallen, releases its lease and
    blocks resummoning until a death-only reset creates a fresh randomized binding.

## Runtime layers

### Native behavior layer

Minecraft goals and later SmartBrainLib behaviors own navigation, following, guarding, defending,
retreating, pickup, delivery, interaction cooldowns and animation. Combat does not wait for inference.

### Programmatic task layer

Typed Java tasks cover:

- `follow`;
- `guard` at the current or named position;
- locate an item and either **show its location**, **fetch it**, or **lead the owner to it**;
- fetch a requested quantity for a quest or direct request;
- explain and assist with crafting an item using actual known recipes and inventories;
- request, preview and execute a named construction blueprint;
- resume, suspend, cancel and report task progress.

Searches are bounded and claim-aware. Container extraction requires permission and a real matching
stack. Crafting consumes real ingredients and uses registered recipes. Building consumes real blocks
and validates each operation immediately before execution.

### Tiny reasoning layer

Target model: `Qwen2.5-0.5B-Instruct` in Jlama Q4 form (about 316 MB of model files), or another
drop-in engine satisfying the same `TinyBrainEngine` contract. The inference subsystem target is less
than 1 GB of disk and working memory, with a 512-token context, at most 64 output tokens and one active
request globally.

Because current Jlama requires Java 21 preview features while Forge 1.20.1 officially targets Java 17,
Jlama cannot simply be shaded into the Forge mod. The adapter must either be a separately bundled local
Java 21 worker or be replaced by a verified Java-17-compatible engine. Until then, a deterministic rule
engine implements the interface.

The model receives candidate choices, not raw chunks or unrestricted control. A compact result names a
known task, template, site and parameters. Java parses, validates and executes it. Invalid, late or stale
results are discarded.

## Passive context and dialogue

Routine conversation comes from bounded preset banks of adjectives, summon/dismiss lines, activity
comments and interaction responses. This avoids spending inference on predictable speech.

Every selectable name has one explicit, stable `PersonalityProfile`: temperament, cadence, core
value, humor style, favorite terrain, food, color and activity, favored path adjective,
summon/follow/wait lines and acknowledgements. Profiles
never reroll and do not change permissions or competence. Routine chat reads them directly; compact
and safety-qualified profile summaries are included in complex/ambient inference snapshots so a future
tiny model preserves voice without being allowed to reinterpret rules.

The companion also has bounded persistent physiology: nutrition 0–20, stamina 0–100 and movement/
activity exhaustion. Survival difficulty drains nutrition and stamina in proportion to travel,
working, defending and retreating; Peaceful or a creative lessee suppresses that drain. Waiting and
guarding restore stamina when fed. At low nutrition the companion consumes real food from its own
18-slot inventory; below half health it may drink a real beneficial potion and retains the empty
bottle. It never takes these directly from a player—the existing confirm-twice trade is the supply
path. Mood is a persistent -100..100 index, shifts with hunger/rest/feeding, and decays slowly toward
neutral. Mood affects voice only, never claims, consent, lease rules or task safety.

An ambient reflection request may occur only when all of these are true:

- the companion is summoned and the owner is nearby;
- the area is calm and no urgent behavior is active;
- no task or inference request is running;
- the cooldown has elapsed (initial target: ten minutes);
- the server is not under measured tick pressure.

The ambient model input is a compact, immutable snapshot: dimension, biome, weather/time category,
current activity, a few nearby semantic features, one active quest summary and up to three relevant
memories. Its output is dialogue only. It cannot select or execute an action.

## Command wheel and state emotes

The `V` key (fully remappable in Minecraft Controls) opens an eight-segment radial command wheel.
The same wheel opens after holding the Sigil of the Hollow Court for eight ticks; releasing sooner
performs the ordinary summon/recall. Crouch-quick-use retains dismissal as an accessibility fallback.
The first wheel contains Summon/Recall, Follow, Wait Here, Guard Here, Defend Me, Status, Cancel Task
and Dismiss. Free-form item, quest, crafting and building targets remain name-addressed chat
because a wheel must not guess their arguments.

Wheel packets contain only a bounded enum. The server independently verifies sigil possession,
ownership and live companion identity, then runs the same authoritative services as chat/sigil
interactions. The client cannot send command strings, positions, item IDs or blueprint approvals
through this channel.
Wheel actions are rate-limited server-side to one accepted packet per player per four ticks. The
client also refuses to open the wheel without a sigil, but that convenience check is never trusted as
authority. Item tooltip text teaches quick, hold, crouch and hotkey paths without requiring a wiki.

While summoned, a small state emblem renders above the companion at up to 32 blocks: compass for
following, clock for waiting, shield for guarding, iron sword for defending, boots for retreating and
crafting table for working. These reference built-in Minecraft item renders and introduce no copied
third-party artwork. A later original icon atlas may replace them after accessibility testing.

## Original Hollow Court skin direction

The installed Rich's Races wood-elf sheets confirm the standard 64×64 player texture layout, but that
jar declares its license as “Not specified.” Its pixels must not be copied, traced, recolored or
redistributed. Alfheim Companion skins are original works using the normal player UV topology.

The persistent identity has a stable face/ears/hair seed; outfit variants change by role or biome
without making the companion look like a different person. Initial design families:

- **Wayfinder:** moss-green split travel coat, bark-brown leather, pale-gold stitching, compass clasp;
- **Hollow Court Warden:** deep plum and muted silver, leaf-scale shoulder panels, shield-shaped clasp;
- **Ley Gardener:** layered teal work robes, root-fiber apron, botanical tool loops, mana-blue accents;
- **Ashen Scout:** charcoal cloak, ember-red repairs, wrapped boots and a soot-muted silhouette;
- **Winter Envoy:** pale lichen, blue-grey wool and restrained iridescent trim rather than bright white.

Every sheet needs readable pointed ears, asymmetric elven tailoring, two-layer hair/garment depth,
glove and boot detail, no modern logos, no borrowed franchise heraldry, and an optional original
emissive mask limited to magical jewelry/eyes. Final admission requires front/back/side inspection on
both classic and slim player geometry, armor compatibility, mipmap/bleed inspection and in-game tests
under daylight, rain, caves, Nether-like light and the Alfheim palette.

The first original visual reference is `docs/art/hollow_court_skin_concepts_v1.png`. It is a concept
sheet, not a game-ready texture and must not be shipped as an entity UV map. Pixel-perfect 64×64 skins
will be authored from it as separate original assets.

Command-wheel acceptance is deliberately split by layer:

1. unit: exactly eight unique enum actions; malformed ordinals are ignored; name-chat behavior is unchanged;
2. protocol: client sends only action ordinals and the server rejects missing-sigil/non-owner requests;
3. dedicated server: channel registration is side-safe and the full pack reaches `Done`;
4. client: quick release summons once; hold at eight ticks opens once and does not also summon;
5. input: remapped hotkey, Escape/no-selection, mouse segment boundaries and GUI-scale 1–4;
6. state: every server mode synchronizes to its matching overhead emblem for two clients;
7. accessibility: labels remain readable without color, wheel does not pause, and keyboard/controller
   follow-up is scoped before production admission;
8. multiplayer abuse: packet spam, invalid ordinals, stolen sigil, non-owner and dismissed-state probes.

## Persistent memory and state

Authoritative memory lives in overworld `SavedData`, not large entity NBT or client-synced tags.
Entity NBT contains only immediate identity, mode, equipment and inventory state needed to restore the
mob. Current memory bounds are 50 episodic entries and 64 semantic facts.

Memory domains:

- identity: persistent name, owner UUID and companion UUID;
- relationship: familiarity, preferences, promises and boundaries;
- state: following, waiting, guarding, defending, retreating, working or dismissed;
- task: objective, requested quantity, approach, progress, failure and blueprint reference;
- episodic: bounded important events with type, subject, detail, time and importance;
- semantic: landmarks, known resources, machines, work sites and player preferences;
- quest: selected quest IDs, status transitions and notable objective progress;
- personality: agitation and dialogue variation state.
- lease: current lessee UUID and persisted expiry; expiration cancels unsafe work and leaves the
  companion waiting for the next token holder.

The model may propose a memory, but Java decides whether it is supported, safe, useful and within
bounds before saving it.

## Quest awareness

An optional, versioned FTB Quests adapter normalizes quests into:

- stable quest ID and display name;
- goal/description;
- status: not available, available, active or completed;
- objective descriptions and current/required counts;
- ingredient or tag requirements and known availability;
- completion criteria.

The companion can reference quests by name, goal, ingredient or criterion in addressed chat. Full quest
graphs are not copied into memory or prompts. The adapter supplies current views, while memory retains
only selected objectives and significant changes.

## Continuity Works integration

Continuity Works implements the versioned `BlueprintProvider` Java endpoint. Alfheim Companion submits
immutable requests containing purpose, maximum bounds, styles, available materials, preferred origin,
orientation and pre-scored candidate sites. Continuity Works returns a proposal containing an ID,
format version, integrity hash, origin, bounds, placements, material manifest and warnings.

Required flow:

1. addressed build request becomes a typed task;
2. deterministic code gathers materials and candidate sites;
3. tiny reasoning selects or clarifies purpose/style when necessary;
4. Continuity Works generates a proposal from the immutable request;
5. the server creates a fresh world snapshot and Continuity Works validates the proposal;
6. the owner receives a preview and explicitly approves destructive work;
7. a deterministic executor revalidates claims, chunks, reach, inventory and block state per step;
8. memory records only blueprint identity, location, decisions and progress—not the entire block list.

Only one blueprint request can exist for the singleton companion. Continuity Works is optional: without
it, only bundled static templates are available.

## Player-like capabilities and permissions

The entity owns a persistent, owner-interactable 36-slot carrying layout: 27 main slots and a 9-slot
hotbar, plus six directly interactable equipment/hand slots. Empty-hand interaction opens its
five-row combined equipment/container screen within eight blocks;
shift-click transfers work in both directions and the server closes access if owner, distance, entity
or lease validity changes. Eating, potions, crafting, fetching and building all use these same visible
slots. Validated block actions run through a
dedicated Forge `FakePlayer` identity so Forge events and protection hooks observe them. The fake player
never uses the owner's UUID or privileges. Claim checks occur before the vanilla/Forge action path and
again where needed at execution.

Player-like capability means using legitimate player interaction paths—not bypassing claims, commands,
recipes, inventories, reach, cooldowns or game mode. Direct command execution and arbitrary reflection
into other mods are prohibited.

Equipment is not cosmetic: understood armor, shields, swords and axes occupy real entity equipment
slots, so vanilla/Forge attribute modifiers, armor reduction, enchantments, durability and potion
effects participate in real combat. Native target/melee goals defend an attacked lessee and patrol a
guard radius; retreat navigation seeks distance from nearby monsters. Unknown or complex modded gear
is accepted into visible storage after confirmation but is not auto-equipped or activated—the elf
states that it does not know how to use it safely.

The version-2 `CombatProfileProvider` now has a direct, optional Mine and Slash adapter pinned to the
pack's Mine and Slash 6.4.7 and Library of Exile 2.1.11 APIs. When `mmorpg` is loaded it:

- synchronizes the companion to the active lessee's Mine and Slash level without granting XP or items;
- exposes the lessee's selected Mine and Slash class path plus the companion's live MMO resources and
  calculated modifiers to status responses and bounded inference snapshots;
- reads Mine and Slash `GearItemData`, maps it through the mod's own base-gear slot, enforces
  `canPlayerWear` and `canUseWeapon`, and invalidates the mod's equipment cache after real slot changes;
- leaves unmet-requirement gear and unsupported jewelry in ordinary visible storage with an explicit
  response instead of guessing how to activate it.

The adapter class remains cold when `mmorpg` is absent, and the mod then falls back to ordinary
vanilla/Forge equipment and combat. Damage execution stays with Mine and Slash/Forge hooks; the
companion adapter never fabricates damage, progression, gear, currency or resources.

Death inventory follows the world rule. With `keepInventory=true`, all 36 carrying/hotbar stacks and
six equipment/hand stacks are stored in the fallen player's binding and restored to the replacement
after `/alfheimcompanion reset`. With it false, those real stacks spawn at the death location and all
source slots are cleared to prevent duplication. An optional `GraveIntegrationBridge` can transfer the
same immutable stack list to a documented grave-mod API before ordinary drops. No grave mod is present
in the current pack, so no adapter is guessed and no fake player death is fabricated.

## Chunk loading

The companion will hold a small, moving, ticking Forge chunk ticket centered on its current chunk while
active. The initial cap is the current chunk plus the minimum neighboring radius required for safe
navigation. Old tickets are released before new tickets are acquired, and all tickets are released on
dismissal, death and server shutdown. It must not force-load arbitrary goals, entire paths or dimensions.

The 3×3 controller is implemented. Its exact Forge 47.4.10 behavior remains pending until verified
in a controlled server run.

## Implemented prototype

- official Forge 47.4.10 Gradle project and metadata;
- registered companion entity and temporary player-model renderer;
- craftable summoning sigil;
- server-wide singleton registration and recall service;
- persistent name, location, state, memory, task reference and agitation data;
- bounded episode/fact memory collections;
- owner following/waiting behavior;
- persistent 18-slot inventory and two-step item offer confirmation;
- Enderman-style teleport effect utility;
- deterministic tiny-brain interface and bounded single-request coordinator;
- fail-closed claims bridge;
- player-like break/place service and creative-only generation gate;
- versioned Continuity Works blueprint endpoint;
- versioned FTB Quests awareness endpoint;
- preset name and dialogue banks.
- name-prefixed chat parser for follow, guard, status, cancel, item, craft, build and quest requests;
- guard-anchor goal and bounded dropped-item show/fetch/lead routines;
- registered-recipe crafting advice with combined owner/companion material checks;
- bounded 3×3 moving ticking chunk ticket with dismissal, death and shutdown cleanup;
- low-frequency quest status memory refresh;
- ten-minute calm-state ambient reflection boundary with dialogue-only output.
- version-2 typed task persistence with bounded fields and safe migration from version-1 strings;
- exact installed-version FTB Chunks 2001.3.8 claim adapter using `shouldPreventInteraction`;
- exact installed-version FTB Quests 2001.4.22 adapter with team status, visibility, descriptions,
  criteria and live item counts;
- bounded Continuity Works generation lifecycle with one active request, timeout, proposal shape
  validation, a fresh world/claim snapshot, owner preview, addressed approve/reject commands and an
  audit ledger;
- deterministic blueprint execution capped at one placement per four ticks, with navigation,
  per-block reach/claim checks, actual inventory consumption and fail-safe pause behavior;
- restart behavior that converts non-persisted preview/execution lists to `PAUSED` rather than
  replaying stale destructive work;
- JUnit regression coverage for addressed parsing, command precedence/count bounds, task migration
  and blueprint-ledger restart safety.
- hold-versus-quick-use sigil interaction and remappable `V` command-wheel hotkey;
- eight bounded server-authoritative wheel actions over an enum-only network packet;
- client-synchronized companion mode plus built-in-item state emblems above the nameplate;
- original five-outfit Hollow Court concept sheet and license boundary for the installed elf mod.

## Next implementation order

1. Run controlled dedicated-server registration/boot tests with the exact modpack and repair any
   side-only, dependency, event-registration or runtime-mapping failures.
2. Add GameTests for singleton enforcement, summon/dismiss, inventory accounting, claim denial,
   chunk-ticket cleanup and blueprint interruption.
3. Extend item search from visible drops to remembered, permission-approved container indexes.
4. Add inventory-backed recipe execution after an explicit craft confirmation.
5. Add a property-aware block-state codec and explicit scaffold/obstruction policy to blueprint
   execution; the current executor resolves block IDs and uses default placement state.
6. Add an explicit resume/regenerate interaction for a `PAUSED` blueprint after restart.
7. Measure and tune the 3×3 chunk-ticket radius and blueprint placement cadence under representative
   server load.
8. Implement a Java-17-compatible tiny-model adapter or isolated bundled Jlama worker.
9. Replace the temporary player renderer with approved Hollow Court assets.
10. Add an explicit Curios-backed companion jewelry harness before enabling Mine and Slash rings or
    necklaces; they are recognized but safely stored in the current six-slot equipment model.

## Acceptance gates

Current automated status: clean Java 17 compilation, reobfuscated production jar build, and thirteen
unit tests passing. Compilation is only static validation. Production admission additionally requires a dedicated server
boot, singleton/dimension tests, claim tests, survival inventory accounting, quest compatibility,
Continuity Works contract tests, chunk-ticket cleanup tests, malformed/stale inference tests, and a
measured tick/RAM budget under representative modpack load.

## Validation evidence and current blockers

- Clean Java 17 `test build`: thirteen unit tests pass and the Forge production jar reobfuscates.
- Controlled full-pack dedicated boot `companion-boot-20260908a`: exit 0, reached `Done` in 18.503
  seconds, both FTB adapters connected, all dimensions saved on clean shutdown.
- A later singleton command-spawn probe did not reach command execution because concurrently changed
  pack data declared `alfheim:deepworks_headworks` with a value of 10 outside the allowed `[0:7]`
  range. That registry failure occurs after the companion and both FTB adapters load and is outside
  this mod; the singleton rejection still needs a rerun after that pack data stabilizes.
- Updated safe-mode full-pack boot `companion-wheel-safe-20260908b`: exit 0, reached `Done` in 18.770
  seconds, both FTB adapters connected, and shut down cleanly. Existing Fabric Connector/MMORPG
  client-mixin warnings and unrelated data/loot errors remained non-fatal and were not caused by the
  companion.
- The command wheel and overhead emotes are clean-build, unit, and dedicated-side validated. Client
  interaction/visual acceptance remains open after the implementation pass.
- MMO-enabled safe-mode full-pack boot `companion-mmo-safe-20260908c`: exit 0; FTB Chunks, FTB Quests,
  and the direct Mine and Slash 6.4.x adapter all connected before the server reached `Done` and shut
  down cleanly. Live-player acceptance for level synchronization, requirement-denied gear, calculated
  damage, resources, and the six equipment slots remains an explicit in-world test gate.
