# Elven Golems — workers, artisans, sentinels and Deep salvage

**Status:** approved direction; implementation planned, no mod scaffold or runtime content yet.  
**Owning mod:** future first-party `alfheim_golems`, independent of Alfheim Companion and Alfheim
Leyworks.  
**Target:** Minecraft 1.20.1, Forge 47.4.10, Java 17.  
**Implementation authority:** `../first_party_mods/alfheim_golems/docs/ALFHEIM_GOLEMS_PLAN.md`.

The canonical spelling in identifiers and player-facing English is **golem**. Existing **Manna
Stone** is deliberately spelled with two n's, so its command item is the **Manna Stone Command
Gem**.

## 1. Promise and boundary

Elven Golems is the pack's deterministic workshop-assistant system. Player-owned golems move real
items among real inventories, perform legal crafting recipes, tend furnaces and, at the advanced
tier, operate explicitly supported machines. They do not create items, load remote chunks, bypass
claims, impersonate players or ask a language model what to do.

This is a separate mod because it has a many-entity logistics scheduler, machine-adapter API,
work-order UI, natural spawning and a release cadence unrelated to the one persistent conversational
companion. The companion may eventually report golem-network status through a public read-only API,
but neither mod depends on the other.

## 2. The twelve forms

There are three chassis classes and four elemental alignments. The implementation registers one
entity type per chassis and synchronizes the alignment as bounded entity data; this gives twelve
playable forms without twelve copies of the same AI.

| Chassis | Scale | Persistent owned role | Wild Deep role |
|---|---|---|---|
| **Worker** | within one block, about 0.7 x 0.9 blocks | item transport, filters, furnace input/fuel/output, recipes fitting a 2x2 grid | common salvage carrier |
| **Artisan** | player-sized, about 0.8 x 1.9 blocks | larger inventory, 3x3 crafting, multi-step jobs and supported machine operation | uncommon ruined workshop keeper |
| **Sentinel** | player-sized and visually heavier | no permanent logistics role; temporary allied combat summon only | rare Deep guardian |

Every chassis has Fire, Water, Earth and Air versions. Alignment is a specialization, not a job
lock: every Worker can move items and tend a furnace, and every Artisan can craft and use every
adapter available to its tier.

| Element | Workshop identity | Combat identity | Deep salvage emphasis |
|---|---|---|---|
| Fire | furnace and heated-process efficiency | burning strikes without block ignition | emberglass, fuel, heat-worn plates |
| Water | washing/cooling and later fluid-machine aptitude | fire resistance and brief slowing | tidewake glass, vessels, cooled fittings |
| Earth | carry capacity, stability and shorter recovery after obstruction | armour and knockback resistance | rootglass, livingrock, heavy chassis plates |
| Air | travel speed, route recovery and lightweight sorting | speed, leap and evasive movement | galeglass, feathers/fibre, fine control vanes |

Numerical bonuses remain configuration values and must not multiply recipe outputs. The element
changes time, capacity or combat behavior; it never changes the registered result of a recipe.

## 3. Command language

The **Manna Stone Command Gem** is reusable. It binds to one owner and one golem network and stores
only compact identifiers; the server owns all positions, permissions and order data.

The minimum complete interaction is:

1. use the gem on a golem to select it, or select a named group in the gem screen;
2. crouch-use an inventory face and choose **Take**, **Put**, **Fuel**, **Craft at**, or **Operate**;
3. choose an item/tag filter, quantity policy and destination;
4. preview the resulting route, then confirm it;
5. inspect a plain-language state: working, waiting for input, output full, path blocked, unloaded,
   permission denied, unsupported machine or paused.

The first vertical slice needs five commands only: **follow**, **stay**, **work**, **pause** and
**dismantle**, plus a two-endpoint `take here -> put there` order. Furnace and crafting verbs extend
that same order graph rather than becoming unrelated AI modes.

Orders are explicit directed graphs of inventory endpoints and station steps. An endpoint is a
dimension, block position, face and filter. It is not a forced chunk ticket. A golem pauses when an
endpoint is unloaded and resumes only after ordinary chunk loading brings both it and the work area
back.

## 4. Inventory and crafting invariants

- All movement uses Forge item-handler simulation before extraction or insertion. Unsupported or
  ambiguous handlers fail closed.
- Extracted items enter the golem's visible internal inventory before another action occurs. If a
  destination disappears or fills, the golem keeps the stack and reports the blockage.
- No operation drops overflow into the world as its normal error path.
- Owned golems act only for their owner or an explicitly authorized FTB team. Container access and
  block interaction are rechecked at execution time; a missing claims adapter fails closed for
  protected interaction.
- Workers execute furnace-family cooking and registered shaped/shapeless recipes whose occupied grid
  fits 2x2. Artisans execute 3x3 recipes, legal remainders and bounded sequences.
- Crafting always asks the server RecipeManager, consumes exact ingredients, preserves recipe
  remainders and inserts output before beginning another craft.
- A machine is supported only through a named adapter with detection, input rules, completion
  evidence, output rules and tests. Merely having slots does not prove that a machine can be operated
  correctly.

Initial adapters are vanilla furnaces, generic sided item handlers and the pack's Manna Stone
Storage. Create, Botania/MythicBotany, Ars Nouveau, Occultism and other machines are audited and added
one adapter family at a time. Open-world processing such as throwing items into a mana pool is out of
scope until an adapter can prove ownership, consumption and output without guessing.

## 5. Cores, construction and the costly route

There are three core families, each with four aligned variants:

1. **Simple Golem Core** — powers a Worker.
2. **Advanced Golem Core** — consumes a Simple core inside a larger cognition, storage and movement
   lattice; powers an Artisan.
3. **Combat Golem Core** — consumes an Advanced core inside armour, target-binding and timed-mana
   layers; powers one combat summoning vessel.

Each family is a layered recipe chain, not a single nine-slot sink. The exact pack item IDs are fixed
only after the recipe/progression audit, but every chain must visibly cross both spines:

`aligned Deep salvage -> shaped chassis pieces -> Botania mana infusion/runic binding -> Ars
imbuement/enchanting apparatus -> completed aligned core`.

Making every precursor from raw materials is intentionally prodigious. Higher cores recursively
consume the previous family, so an Advanced or Combat core represents the earlier work rather than
sitting beside it. Recipes use the campaign's one-tier-material rule and must not introduce a second
independent exponential ladder.

A Worker or Artisan is made by combining its core with a recoverable shell to create an aligned
effigy. Using the effigy places and binds the persistent golem. Safe dismantling is allowed only
while the golem is idle, healthy and carrying nothing, and returns the effigy. Death returns damaged
components, not a free intact respawn.

## 6. Wild golems and the salvage route

All twelve forms have wild Deep counterparts. They are remnants of elven mines, workshops and
defences—not owned golems waiting to be claimed.

| Wild chassis | Habitat and frequency | Resource role |
|---|---|---|
| Worker | common, y -20 to -55, groups of 1-3 around ordinary Deepworks stone and quarry approaches | large amounts of basic aligned materials and Simple-core components |
| Artisan | uncommon, y -40 to -64, usually solitary near quarries, Faultworks and ley infrastructure | advanced lattice parts and a low chance of a damaged Advanced core |
| Sentinel | rare, y -48 to -64, solitary near high-mana geology and ruins | combat casing parts and a very low chance of a damaged Combat core |

Natural spawning is added to Alfheim biomes, then constrained by server-side placement rules for
dimension, depth, darkness, floor tags, local density and distance from the spawn hub. Wild golems
do not spawn in Midgard, on the surface, in peaceful difficulty, or from ordinary monster spawners.
Structure proximity may bias later waves but is not required for the first reliable spawn pass.

Wild units are wary-neutral until attacked or until a player violates a small guarded ruin radius;
they never join a player merely because the player holds a gem. Defeating one yields aligned raw
materials, chassis pieces and core fragments. Complete pristine cores are never common drops.
Damaged cores require an expensive restoration chain, so exploration removes much of the bulk cost
without removing the current era's processes or knowledge gate.

Spawn budgets and loot are tuned together. A per-chunk living cap, slow despawn rules, Looting caps
for core parts and no self-replicating golem drops prevent a dark-room farm from becoming an
unbounded finished-core factory. The acceptance target is that a real Deep expedition materially
accelerates one build while crafting from scratch always remains possible.

## 7. Combat summoning

The four **Sentinel Vessels** are consumable items, one per element. Crafting a vessel consumes the
matching Combat Golem Core plus its shell and temporal binding. Successful use consumes one vessel
and summons one allied Sentinel near the player; a failed placement consumes nothing.

The Sentinel:

- is allied to the summoning player and respects the player's scoreboard/FTB team;
- follows and defends that player, attacks only legal hostile targets and never breaks blocks;
- has no inventory, pickup, breeding, taming, portal travel or permanent-save path;
- expires after a configurable initial target of 120 seconds, with a visible warning in its final
  ten seconds;
- despawns early on owner logout, owner death, dimension separation or invalid ownership;
- drops no core, vessel, loot or experience, regardless of how it expires.

The short lifetime and full consumable cost make it an emergency power item comparable to a combat
summon, not a permanent replacement for the player or the companion.

## 8. Progression proposal

The campaign rule says automation must arrive before the Era V-VI material curve bites.

| Era | Unlock |
|---|---|
| III — Green Return | Manna Stone Command Gem, first Simple Core, Worker logistics and furnaces |
| IV — Long Silence | 2x2 batch crafting, filters, grouped routes and basic Deep salvage clues |
| V — Deep Forges | Advanced Core, Artisan, 3x3 crafting and first machine adapters |
| VI — Wild Marches | multi-step machine jobs and wider network limits |
| VII — Burning Cradle | Combat Core and four consumable Sentinel Vessels |

Wild encounters may occur before the player knows how to restore every part. Early salvage can be
stored, but the recipe process and era material still gate use.

## 9. Performance and safety budgets

- No forced chunk loading and no path search to an unloaded endpoint.
- A configurable global scheduler budget, default target 64 lightweight golem decisions per server
  tick and no more than one inventory mutation per golem per 10 ticks.
- Navigation range, network size, endpoints per order, filters and queued crafts are bounded.
- Golems sleep when idle, paused, ownerless or outside simulation distance.
- Work orders use SavedData; transient navigation and reservations do not.
- Server-authoritative packets carry bounded enums and IDs, never arbitrary class names, commands or
  client-supplied permission results.
- Every order exposes an audit trail of the last state change and failure reason without logging
  full player inventories.

## 10. Acceptance

Production admission requires more than a clean build:

1. all three entity types and four alignments save, load and synchronize on a dedicated server;
2. a Worker completes chest -> furnace -> chest and 2x2 craft loops without duplication or loss;
3. an Artisan completes a 3x3 recipe and each admitted machine adapter with correct remainder logic;
4. full, removed, unloaded and claim-denied endpoints pause safely and resume correctly;
5. two teams cannot command or extract from one another's golems or containers;
6. all twelve wild forms obey habitat, density and loot tables in fresh Alfheim worlds;
7. each Sentinel Vessel consumes exactly once on success, not on failure, and its summon leaves no
   drops or persistent entity after expiry;
8. a representative 32-Worker/8-Artisan workshop remains inside a measured tick budget;
9. automated client interaction/capture proves model and texture resolution, hitbox traversal,
   elemental state distinction and command-UI bounds at GUI scales 1-4; no owner playtest is a gate;
10. quest/JEI text teaches the expensive craft route, Deep salvage route and non-obvious pause
    states before the system is called progression-ready.
