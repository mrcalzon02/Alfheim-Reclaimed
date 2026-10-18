# Seasonal fey sky villages — 2026-10-17

Replaces the four tiny optional-jigsaw hamlet definitions with larger native
sky villages, retaining their existing structure IDs and seasonal biome tags.
Eight deterministic layouts span a 96 × 96 template envelope. The occupied
land is elongated and asymmetric, with uneven shores, deeper tapered livingrock
undersides, roots, raised soil and flattened building terraces. Cottages form
small neighborhoods beside a winding main street and short branch paths.
They do not occupy a perimeter circle or radiate around a central plaza.

Each layout has ten tiny cottages, two hollow apartment trees, two gardens and
a seasonal landmark. Spring uses blossom roofs and gardens; summer uses
suncomb pods, verandahs, sail roofs and small windmills; autumn uses mushroom
cottages, fallen-log annexes and a lanterncap market; winter uses snow lodges,
ice bell turrets and lit glass gardens. The two street arrangements and island
orientations per season replace the old three-house lottery. Three cottage
forms per season add variety within a settlement.

## Added seasonal vegetation

Each layout now includes ten additional branching seasonal trees, beyond the
two apartment trees, and roughly 1,000 flowers across the open land. Trees
use seasonal Feywild logs/leaves with broad summer crowns and tapered winter
crowns. Snow islands expose grass flower beds for blue orchids and cornflowers
to survive block updates. Streets, gardens, cottage approaches and home exits
remain clear in the emitted-layout checks. The structure templates are updated
in the active KubeJS data pack; the companion jar is unchanged for this foliage
pass.

## Inhabitable homes

Four native seasonal log-apartment blocks use the installed Feywild bark and
plank textures. Their beveled casings contain recessed windows and doors,
balconies and warm window details. They are available in Natural Blocks.
Each apartment tree contains three functioning home blocks; autumn log annexes
also accept residents but do not generate additional pixies.

The bee-style routine applies to the four existing Feywild seasonal pixies,
verified in the installed 5.5.5 mod and exported registry. No replacement pixie
entity or third-party jar modification is involved. A home accepts only its
matching seasonal type, up to three residents. Complete entity NBT, including
UUID and custom state, is saved inside the block. Residents are released during
clear daytime after resting; blocked exits retain the resident and retry later.
Wild pixies visit flowers, saplings and crops, linger with particles, and return
after several visits or for rain/night shelter. Owned, following, leashed,
mounted and fighting pixies are excluded. Native higher-priority goals remain.

Crop visits can add one growth stage, with a one-minute cooldown per pixie and
the Forge mob-griefing permission respected. There is no harvesting, item
duplication, forced sapling growth or terrain excavation. Apartment nurseries
create one matching resident at a time, checking nearby active and stored
populations within 48 blocks against a cap of eight, and waiting 120–180 seconds
between attempts. They require a nearby player and loaded chunks; they do not
force-load chunks. Picked-up home items preserve resident NBT, including a
creative-break drop when occupied.

## Pixie dust harvesting

Apartments now accumulate one dust level when a matching wild resident returns
after at least three plant visits. Those visits are consumed on admission;
nursery creation and shelter without visits do not produce dust. At level five,
right-click with shears to receive three existing Botania Pixie Dust items
(`botania:pixie_dust`), consume one shear durability and reset the supply to
zero. Residents remain inside. Full homes sparkle; empty-hand interaction
shows readiness/progress, and comparators output the current level (0�5).
Dust is saved with resident NBT and retained in picked-up home items.
No honey, bottles or new dust item is introduced. Existing apartments start
at zero on upgrade. This is manual harvesting; dispenser harvesting is not
implemented. Build/install evidence: `tools/fey_dust_harvest_build.json`;
the actual in-game production/harvest cycle remains pending review.

## World generation and provenance

Executed local `StructureCapability.generate` from the installed Continuity
Works implementation at `C:/GITS/Structuresmith/StructureSmith/src`, through
provider `alfheim_fey_sky_villages_v2` in `tools/gen_fey_sky_villages.py`.
Target: Java 1.20.1 / Forge, dimension mythicbotany:alfheim. Stable seeds are
2026101700 + season-index × 10 + layout-index. Actual snapshot, generation
result, registry probes and 32 emitted template hashes are recorded in
`tools/fey_sky_villages_generation.json`.

Four fixed-offset related 48 × 48 × 48 tiles assemble each island at base
Y 192. There are no optional children to omit buildings. Existing biome tags
remain unchanged. All seasonal sets share a 96-chunk/48-separation grid:
the minimum inter-island footprint gap exceeds 500 blocks. The native adapter
reserves a conservative 900-block center gap from independent structures,
checks actual viable neighbor starts, supports concentric castle reservations,
and filters phantom district-grid cells. A seasonal anchor may cross ordinary
biome boundaries; its sampled footprint must avoid the Void and high terrain.
Pack-owned standalone works, allocated underground structures and upper-rock
structures yield to valid island-grid reservations. This one-way policy uses
terrain/biome probes without recursively invoking neighbor guards or loading chunks.
Other mods retain their existing placement logic and take precedence in island checks.
The related tiles are one structure family, rather than independent placements.

Existing non-vanilla materials were probed against the exported registry.
The four home blocks have native declarations. Island template geometry and all
home metadata are preserved in the loot follow-up; the 49 standalone jigsaw
definitions keep their original layouts, terrain projection and biome settings.
Their two generators retain the reservation wrapper on regeneration. Commanded
Greatbole and disabled ley fracture definitions keep their existing behavior.

## Randomized island loot follow-up

The former cottage barrels had no loot data. Each now references a seasonal
`alfheim:chests/fairy_island_<season>` table, with no fixed seed or prefilled items.
There are ten loot barrels per island, or fourteen for autumn with its market.
Two weighted pools roll food, seeds, simple supplies, seasonal flowers and the
matching Feywild sapling, with randomized counts. No progression power is added.
Vanilla container opening generates the inventory once and saves it.

Continuity Works was actually rerun through the same v2 provider; snapshot
`20261018T073037Z-alfheim_seasonal_fey_sky_villages-generate-be66f46b` records
the emitted templates and tables. `tools/fairy_island_template_audit.json`
proves all 32 templates match their previous block/state/home geometry, with
only the new barrel loot metadata differing.

## Evidence and remaining review

The follow-up build passes all 72 Java tests. Built, installed and isolated-server
jars match SHA-256 `3e2abc9483fa5282313a5878e038f7450061e4edcf43a6d24b25f6393aa0dca0`.
The pre-repair artifact is preserved in
`quarantine/alfheim_companion-before-fairy-island-runtime-fix-20261017.jar`.
All 1,834 packaged resources match source or Gradle-expanded metadata. Feature
ordering has zero cycles; prior atlas and grove map-color checks still pass.

Fresh disposable world `validation-fairy-islands-allocated-20261017`, seed
`-5876049240305171930`, naturally generated these two islands in Alfheim:

| Season | Start chunk minimum block X/Z | Layout | Pieces | Homes | Loot barrels |
|---|---|---|---|---|---|
| Spring | -10576, -4288 | 1 | 4 | 6 | 10 |
| Autumn | -13360, 12912 | 1 | 4 | 10 | 14 |

No `/place`, template placement or biome editing was used. The bounded native
survey accepted one site in each of two 64-candidate samples, with other sites
rejected by terrain, seasonal biome restrictions or MythicBotany's elven houses.
Forced chunk loading then exercised ordinary natural structure generation.
Saved natural starts have all four children per island; all 1,615 sampled solid
blocks match the emitted templates. Every expected home has its registered native
block entity. Spring and Autumn are verified; Summer/Winter layout and loot
checks pass statically, with natural sampling still pending.

The native container-opening probe found all 24 expected loot barrels, each with
a different nonzero placement seed and different inventory. Repeated item access
kept the inventory stable. Saved chunk NBT contains the exact opened slot/item/count
contents and no remaining loot-table reference. Their 24 inventories include actual
seasonal supplies rather than empty barrels. This verifies one-time randomized
loot that persists; it is not a claim of renewable or rerolling treasure.

Reports: `tools/fairy_island_runtime_report.json`, `tools/fairy_island_build.json`,
`tools/fairy_island_template_audit.json`, and `tools/fey_sky_villages_static.json`.
`tools/fey_sky_villages_build.json` retains the earlier unvalidated artifact's
history; this follow-up supersedes its placement-pending state. The initial,
boundary, coordinated and cross-biome diagnostic survey reports are retained under
`tools/fairy_island_*_survey.json` with their actual failures/limits.

Client lighting/rendering, live home entry/release across reloads, ownership
protection, gardens and dust-harvest gameplay still require in-game review. Offline
previews are not Minecraft screenshots. Restart to load the installed companion
jar and explore new chunks; already placed hamlets and player saves are not rewritten.
