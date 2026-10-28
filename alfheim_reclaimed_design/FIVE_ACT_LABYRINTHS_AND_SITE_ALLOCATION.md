# Monastery of the Five Descents — full-depth act dungeons and shared placement

**Project:** Alfheim Reclaimed — Minecraft 1.20.1 Forge, MythicBotany Alfheim dimension, Mine and Slash scaling.
**Status 2026-10-18:** Shared site policy, tests and a first-party native monastery/village/54-room labyrinth geometry implementation committed as SOURCE ONLY. Registration JSON remains staged outside the active pack until a compatible companion JAR is built. Vendor trading, real monster entities, original assets, multiplayer validation and fresh-world deployment remain pending. Never report source-only content as shipped.

## Corrected authority: one allocator, no arbitrary 4,000-block no-build circle

The authoritative repository evolved to `DistrictRings` (four deterministic site candidates every kilometre, a winning family per site). Do not replace it with its superseded 192/96 grid. `DistrictPolicy` already has more nuanced near-origin protection, and the castle uses a vanilla concentric-ring structure set with three potential candidate starts. Older archaeology, Void War, and Worldstone systems still had independent 4,000, 5,000 and 6,000 block origin exclusions. Those were unrelated to actual building footprints and barred large exploration regions.

`WorldSiteAllocation` centralizes 1) a reserved 1,024-block Hollow Court radius, 2) 128 blocks around a relocated spawn plus caller footprint, 3) the *real* three candidate castle-ring positions, 4) coherent `DistrictRings` footprints, and 5) 1,000-block Act thresholds. Adjacent first-party underground, Void War, and Worldstone paths use this protected footprint policy before expensive terrain probes. District ring selection is unchanged. All numbers are policy constants, not user-visible prohibitions. Exact castle position must be audited against the saved world's actual palace; a candidate ring is a conservative pre-generation reservation.

**Important implementation boundary:** Source-only until the companion JAR is rebuilt; the monastery–labyrinth family is not registered yet. The old `DistrictPolicy` retains its already-accepted kilometre-ring, 908-block hub and 756-block moved-spawn checks. A future single allocator service should replace the remaining distinct wrappers only after proving unchanged district and castle acceptance, and should reserve *all* future monastery and vendor pieces before any place operation. The absence of a dungeon family today must not be hidden by an empty placeholder registration.

## One allocated destination: monastery + vendor village + labyrinth

The dungeon is one **coherent reservation**. Never create an independently rolled monastery, independently rolled trader village, and separately rolled dungeon under the same biome; they would overlap, fail to connect, or starve one another. Candidate selection reserves **the full horizontal footprint and every vertical occupied interval**: roughly 224–320 blocks width in X/Z to support a 96–144-block surface monastery, 48–96-block connected village, 16–32-block staircase approach, and 160–256-block underground wings. Exact dimensions are data-driven and must be measured before accepting a site.

The monastery entrance should be near existing terrain at roughly sea-level elevation when geography permits; sample the actual bounded terrain profile via `ChunkGenerator.getBaseHeight` and `getBaseColumn` without loading chunks. Reject a wet, unsupported, cliff-edge or void site rather than dropping the monastery to Y -64, filling an enormous foundation, or generating an artificial island. Village stalls must have natural ground, paths and safe spawn positions. Entrance, monastery nave and descent shaft share a single authored elevation datum and connected walkable route.

The dungeon extends from surface entrance to just above the world's natural bedrock layer (for Alfheim approximately Y -59, but derive this from dimension build height and actual bedrock). Multiple vertical strata connect through intentional shafts, stairs, lifts and loops. The player must be able to clear the full descent, with optional shortcuts opening after checkpoints. Generate in <=48-block template chunks or first-party bounded structure pieces. A single vanilla jigsaw with 128-block max reach cannot carry a 250-block complex; use a deterministic shared room graph with *chunk-local* placement and stable edge connectors. The generated graph is stored by site ID and version. Changes must not rewrite explored chunks.

The village is a functional **RPG service refuge** with weapon/armor merchant, potions and food, enchanting/repair, reagents, salvage/buyback, portal return and a quest giver. Vendors use real compatible trading systems and persistent identity, no decorative empty villagers; each offers act-specific inventory but does not bypass normal era resource gates. Site entry is safe from dungeon mob waves; monsters cannot wander into the protected vendor square, and traders are persistent and multiplayer safe.

## Radial Act classification — theme, not gating

| Radius from origin | Act | Monastery style | Labyrinth theme |
|---|---|---|---|
| 1,000–1,999 | I — Ashen Cloister | Ruined elven abbey and forest hamlet | Crypts, old cells, bone cloisters, spider galleries |
| 2,000–2,999 | II — Buried Covenant | Sandstone abbey and caravan bazaar | Sand tombs, cisterns, vault traps, scarab catacombs |
| 3,000–3,999 | III — Verdant Blight | Rooted, flooded cloister and marsh settlement | Choked sewers, fever fungus, corrupted temples |
| 4,000–4,999 | IV — Cinder Testament | Burned fortress-monastery and forge refuge | Infernal forges, blood chapels, ash barracks |
| 5,000 onward | V — Winter Crown | Besieged snow monastery and survivor village | Ice prisons, burial holds, glacial abyss, war citadel |

The distance determines act/theme and is **not** an exclusion. Players may fight through many sites, including repeat acts. Enemy level and reward level obey existing Mine and Slash distance-from-spawn mechanics, **not descent depth**. Per-room difficulty derives from local enemy archetype, affix, party and encounter type; no artificial vertical level multipliers. Encounters need bounded simultaneous mobs, pathing budgets, anti-camping and server-authoritative spawn controllers.

## Full Diablo-II-scale bestiary, original content

This is a *monster-alike breadth and encounter grammar* target, **not** a dozen reskinned vanilla mobs and not redistribution of copyrighted Diablo art/audio. Build 120+ mechanically distinct base monsters, 250+ visual/behavior variants, 30+ elite modifiers and at least five deep end-boss families. Make original textures/models/names, preserving familiar action-RPG roles. Inventory existing custom mobs and 390 regional variants before introducing duplicate registrations.

- **Act I:** swarming bone soldiers, shielded revenants, grave archers, wraiths, burrowers, cursed monks, carrion insects, spider broodmothers, chapel zealots, crypt sentinels.
- **Act II:** scarab swarms, sand phantoms, funerary guardians, necromantic wardens, mummified pikemen, bone mages, dart traps, animated urns, revenant pharaohs.
- **Act III:** fetid shamblers, fungal chargers, vine lashers, drowned marauders, bog hexers, insect swarms, poison spitters, rootbound behemoths, cult magi.
- **Act IV:** ash imps, furnace brutes, burning knights, flame casters, chain wardens, infernal hounds, winged attackers, soul leeches, magma revenants.
- **Act V:** frost dead, tundra beasts, ice magi, avalanche shamblers, siege golems, horned chargers, spirit wolves, cold wyverns, warlord champions.

Use defined combat roles (frontliner, flanker, ranged pressure, caster, summoner, healer, commander, trapper, siege and boss) and visually recognizable telegraphs. Include distinct AI state machines, element resistances/weaknesses, summon caps and anti-cheese behavior. Reuse suitable existing creatures only when the gameplay genuinely fits; cosmetic recolors do not count toward mechanical species targets. Champions and unique monsters use affix composition and clear damage source attribution; spawn/difficulty and loot scale through the existing pack's RPG system.

## Dungeon layout grammar and play progression

Build a deterministic **connected graph** with seeded branches, alternate routes and clear returns. Surface gate -> vestibule -> upper ossuary -> habitation wing -> flooded/broken service zone -> transition keep -> lower labyrinth -> elite arena -> bedrock-adjacent sanctuary -> boss and exit. Each act owns 15–25 large modular room families, connectors and vertical stairs with three levels of ruin/detail. Not all modules should be exposed in every run: repeated dungeons remain surprising. Mandatory graph traversal must be provably connected; locks must have reachable keys and cannot require digging through unbreakable rock. Loot is useful but must not short-circuit progression; boss caches should contain act-specific rewards and collectible lore.

## Allocation priority and collision requirements

The **Greatbole/Hollow Court and castle remain higher priority** than new destinations. Existing populated district-ring winners and their full footprints stay next; a monastery complex reserves a single unified envelope only on an otherwise unclaimed candidate; large Worldstone/Deep/war sites and small upper discoveries are checked against the same reservation before placement. Avoid independent salted random_spread sets for individual sub-buildings. Candidate rejection leaves a gap instead of searching or loading chunks recursively. Existing-world constructs are not rewritten to conform retroactively.

Acceptance for allocation requires tests using positive and negative coordinates, exactly 999/1000/1999/2000/2999/3000/3999/4000/4999/5000 boundary cases, three castle candidates, district ring 1 conflicts, moved spawn, neighboring candidate collisions, and at least 100 seeds. Runtime tests must include fresh placement near each Act threshold and against known valid/invalid terrain hosts. A source-only Java change without a matching rebuilt JAR and fresh-world evidence is NOT a shipped worldgen fix.

## Delivery order

1. Unified no-dead-zone allocation and tests, retain district kilometre rings and castle positions.
2. Registrations and generation plan for one real Act I monastery/village/descent complex, with correct surface and natural bedrock fit.
3. Construct 15–25 real modular pieces and proof of graph connectivity and multi-chunk boundaries.
4. Wire an initial functional merchant roster and at least 12 mechanically distinct Act I monsters; loot and encounter control.
5. Expand 120+ monster species and the Act II–V visual/gameplay families with original assets and affix systems.
6. Repeatable raid, checkpoint, boss, multiplayer and performance acceptance on saved new worlds. No GitHub Actions added.

## Implementation follow-up — reserved interleaved monastery candidates

The October 18 allocator baseline still had no monastery generator. We now define
a **pure deterministic candidate series** sharing `DistrictRings`' seed and
orientation without changing any existing district winner, family ID, ring spacing,
or castle candidate. Each ring offers four *additional* intercardinal monastery
candidates at radius `ring × 1000 + 340` blocks. The exact band is taken from
the final world-space coordinates. These are potential sites, not guaranteed
structures: castle, hub, moved spawn, district, terrain, water, and biome checks
must still accept them. There is no 4,000-block exclusion.

The earlier proposal with a 500-block radial midpoint was tested and rejected:
with a 160-block monastery half-footprint, 256-block district half-footprint,
and 128-block spacing, adjacent rings' district sites starved **all** monastery
candidates. The shifted intercardinal approach creates eligible candidates
without reallocating the already selected district winners.

`DistrictRings.nearEnvelope` repairs a previous real collision error:
circular proximity could admit intersecting diagonal square footprints.
`WorldSiteAllocation.clearDistricts` now uses full axis-aligned envelope
checks with the same 128-block gap convention. The ring itself and its
cardinal family selection remain unchanged.

`LabyrinthGraphPlan` introduces a reproducible six-stratum, 54-room graph with
positive-path connectivity, side loops, five anchored vertical transitions and
a lowest boss hub eight blocks above the minimum build height. This is a
**topological plan**, not authored placed geometry. Room, connector, elevation,
vendor, mob and tile construction are still necessary before registering the
full monastery site. Do not start reserving these candidate sites against other
live structures until the dungeon structure exists: otherwise unused phantom
sites could starve real settlements. No new JAR has been built by this commit.

## Monster source of truth — 130 authored species

The machine-readable catalogue lives at
`alfheim_reclaimed_design/monastery_labyrinth/monster_catalog.json`.
It enumerates **25 ordinary/elite original species plus one boss per Act**,
130 genuinely named and individually telegraphed monster designs; 36
independently keyed elite affixes and five bounded encounter pool profiles per
Act. Every creature identifies a distinct signature attack, a response behavior,
combat role, counterplay, elemental envelope, and content implementation state.
This is a design/implementation contract, not a declaration of spawned mobs.
All 130 models and sound sets still require original production or an
approved suitably licensed asset. Existing mod mobs can only be mapped to
entries with a matching mechanical profile, not blindly renamed.

`python tools/check_labyrinth_bestiary.py` checks registry ID uniqueness, Act
coverage, boss distribution, signature keys, affix identifiers, and
non-depth scaling. It intentionally **rejects counting proposed entries
as live entities** by asserting `implementation: design_only`. A future
runtime acceptance test must enumerate registry IDs, inspect actual actor
behavior, and confirm spawner budget/performance in naturally generated
complexes before switching any entry to `implemented`.

## October 18 implementation slice — native monastery structure and bounded dungeon geometry

The first-party companion source now contains a **registered native structure type**
(`alfheim_companion:monastery_labyrinth`), a matching placement type
(`alfheim_companion:labyrinth_rings`), and a serializable native structure
piece. The structure, structure-set and biome-tag definitions are prepared under
`alfheim_reclaimed_design/monastery_labyrinth/pending_worldgen/`, NOT active
`kubejs/data`. The Java source is a real native implementation awaiting build,
not an independently salted jigsaw.

Each accepted kilometre intercardinal slot first passes the same court, moved
spawn, castle and district exclusion policy; the surface has 18 bounded
terrain/solid-fluid samples across the monastery and village. Rejected
terrain simply means no dungeon at that candidate: no bottom-of-world
heightmap fallback, no rescue island, and no replacement site search.

A single native start now assembles a 65-wide monastery, six separate service
stalls in an adjacent village, a joining route, six layers × nine individual
29×15×29 rooms, horizontal corridors and full-depth connected ladder shafts.
The lowest boss chamber follows the existing graph's natural bedrock-relative
Y coordinate. Every Act chooses its masonry palette from world-space radius;
none modifies Mine and Slash level calculation with depth.

**Strict implementation claims:** this is first-pass procedural shell geometry,
not a visually finished monastery, completed village economy or a finished
encounter dungeon. The service stalls do not yet spawn NPCs or offer trades,
the 130 catalogued creatures remain design-only, and the boss chamber has no
boss entity. No generated world, Java build, installed companion JAR, natural
placement, traversability or multiuser acceptance has yet been evidenced.
These are required before describing this as shipped, fully playable content.
Dungeon shafts presently use ladders; the graph retains vertical-stair semantics
for subsequent proper switchback stairs.

Because the definitions use new registry IDs, deploying them without a companion
JAR rebuilt from this source would cause datapack codec load failure. They are
therefore held under pending_worldgen and must only be moved to kubejs/data in
the same verified deployment as a compatible, rebuilt companion JAR.
No GitHub Actions or unrelated repository workflow changes are introduced.


## October 28 source-only circulation repair — six stalls, service road, apron

The previously authored village placed paving at local Y=4 but returned `null`
for Y=0–3 under **road and lane** cells. A candidate surface could pass the
existing ±4-height terrain probes while leaving paved routes unsupported.
The short monastery-to-village apron similarly had only a one-block lower
surface. This was a real block-state gap, not a missing decorative path.

`MonasteryVillageGeometry` is now the Minecraft-free authoritative cell plan
called by `MonasteryLabyrinthPiece` when placing village and apron blocks.
It retains the six 13×19 stall footprints, three-wide inward-facing doors,
three-wide lanes, central road, lights, barrels and Act-specific palette. It
places four bounded layers of existing Act masonry below paved village paths,
and the apron now starts at `base-4` with its walkable surface still at
`base`. No district ring, reservation, terrain-probe threshold, spawn
registration, merchant or progression rule changed.

`MonasteryVillageGeometryTest` is the first-party JUnit 5 regression:
a two-block-headroom flood-fill from all six stall interiors must reach the
central road and monastery-facing west edge; every route cell must have
foundation blocks; door apertures must remain three wide; path behavior must
remain coordinate-independent across 16 chunk alignments. Negative cases
cover solid stall walls, the existing barrel, untouched terrain, submerged,
void/unsupported and cliff sample rejection. The production structure's
18 terrain probes call the same pure height/footing predicates as the tests.

**Evidence boundary:** the pure geometry and JUnit-shaped assertions passed
a local Java 17 source-level smoke using minimal JUnit API stand-ins, not a
ForgeGradle build. The committed JUnit tests still need a real `./gradlew test`
run in the first-party companion project; there is no repository GitHub
Actions workflow. No companion JAR was rebuilt or installed, and no fresh-world
chunk-seam, natural terrain or player pathing acceptance has been performed.
The existing 18 sparse terrain probes do not guarantee every intervening
road column has natural support; the new bounded foundations close the known
paving-underlay gap but are not proof of full terrain incorporation. Pending
worldgen definitions remain staged and should not be enabled on this evidence.
