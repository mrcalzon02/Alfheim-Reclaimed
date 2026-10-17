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
also reserves 900 blocks from potential biome-eligible independent structure
centers, rejects unsupported neighbor placements, terrain intrusion and
sampled biome-edge clipping. This deliberately conservative guard may reduce
eligible sites; natural-world placement density still needs a runtime check.
The related tiles are one structure family, rather than independent placements.

Existing non-vanilla materials were probed against the exported registry.
The four new home blocks have compiled native declarations; runtime admission
for those IDs remains pending. Existing structures, other mods' registries and
unrelated placement policies were not modified.

## Evidence and remaining review

Offline compilation/package build passed with tests excluded. Actual emitted
NBT readback checks 32 tiles, eight different landforms, source equality,
seasonal homes, clear entrances and connected terraced surface approaches.
All model texture paths resolved against installed assets. Offline previews
were inspected; village previews show voxel geometry and texture-derived
colors, while the home sheet renders the actual native block models/textures.
These are not Minecraft screenshots.

Reports: `tools/fey_sky_villages_static.json` and
`tools/fey_sky_villages_build.json`. The former 33-block jigsaw pieces and their
historical saved-world checks are retained as history; their earlier runtime
success does not validate the new structure type or home behavior. The current
generation/check entry points forward to the new provider/checker.

Fresh-world placement, actual neighbor-guard density, client lighting, home
entry/release across reloads, ownership protection and garden behavior still
require in-game validation. This addition is locally validated, not certified
production-ready. Restart to load the companion jar; explore new chunks for
the enlarged villages. Already placed hamlets are not rewritten.
