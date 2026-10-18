# Monastery of the Five Descents — full-depth act dungeons and shared placement

**Project:** Alfheim Reclaimed — Minecraft 1.20.1 Forge, MythicBotany Alfheim dimension, Mine and Slash scaling.
**Status 2026-10-18:** Shared site policy and regression tests authored in Java source; dungeon structures, vendors, monster roster and runtime remain planned. Requires rebuilding and installing first-party companion JAR and saved-world validation. Never represent the planning text as shipped content.

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
