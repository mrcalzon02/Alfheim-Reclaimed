# The Deep — first terrain implementation

**2026-09-05 continuation of B-78.** The material library has a runtime-validated contract.
This pass adds natural geology, a cavern density field and native deep-bloom supplements.
Actual acceptance evidence belongs in `EXECUTION_STATE.md`; client review remains separate.

**Measured result:** three separate sites in paired fresh worlds; 112,230 block samples per world.
Open spans reached approximately 216 blocks, heights 68–84 blocks and lava spans up to 164 blocks.
Sampled ore density rose from 6.94 to 14.60 per thousand solid blocks. Cave-air samples rose from
2,085 to 29,848 and lava samples from 279 to 1,179. These are targeted section counts, not world-wide
frequency estimates. Upper density samples match exactly and bottom-block differences are zero.
Three heightmap readings differ at x=-1930/-1928/-1926, z=-960 because Gloambark leaves generated
at y=72..75 in the treatment; sampled ground and the terrain density there are unchanged.

Evidence: `tools/deep_terrain_summary.json`, the two complete sample reports beside it, and
`tools/deep_terrain_sections.png`. Runtime consoles:
`server/deep-terrain-treatment-20260905-130352.log` and
`server/deep-terrain-baseline-20260905-130620.log`; both harness runs exited 0 with audit=True.
The two matching test worlds are retained under `server/`.

## Space and lava

Alfheim retains its installed dimension, generator type, world height and default fluids.
The existing biome generator still owns `mythicbotany:alfheim_final`. Its normal land branch
now calls `wrap_density()` from `tools/gen_deep_terrain.py`. The Void Verge mask and island
expression are unchanged. Regenerating either tool preserves this composition.

The Deep field combines a broad province noise, a smaller chamber noise, bottom/top gradients
and a minimum solid-terrain density. It can only remove solid terrain, using a minimum with the
existing cave density. Outside y=-60..27 it returns the original density expression. The bottom
gradient closes the rooms near y=-57; the top gradient closes them near y=14, with the exact
shape also controlled by chamber noise. Dense roofs remain necessary for the added cavities.

The world already has a basal lava picker. New cavities reach that band, allowing broad connected
lava surfaces rather than placing many small lake features. Floodedness is reduced only inside
the actual deep cavity field below y=28, allowing air above those basins while retaining the
original aquifer expressions elsewhere. This is an initial basin mechanism. Hand-authored lava
terraces, old high-water shelves and shores that inspect nearby fluid are later refinements.

## Natural geology

Surface rules apply natural Livingrock masses from y=-59 through y=23, after the original bedrock
rule and before biome surface decoration. The original remaining surface rules are retained.
The Void Verge biome is excluded. Biome-associated palettes select coherent masses through a
low-frequency noise field: Furnace under hot/highland ground, Grove under forests, Water/Sky
under lakes/fens, Court under plains/golden fields and Ley in the remaining land biomes.

Five-family palettes have four thresholds; the four-family Ley palette has three. They generate
spatial regions, not a random 24-color block mixture. All 24 natural types have a geological home,
but a small test sample is not expected to contain every type. The shallowest natural deposits
stop at y=23; decoration and shaped variants are never geological host blocks.

Low floor surfaces gain Magmatic Livingrock and occasional slag below y=-51, with Cracked
Livingrock on floor surfaces below y=-45. These are depth/floor rules, not fluid-neighbor tests;
an existing cave in that band can therefore also have a heated floor. Detailed lake shore
gradients still need a later formation pass and client inspection.

The current top of the new geological mass is a deliberately bounded y=23 cutoff and can read
as a sharp contact in section. Feathering that contact is a later geology refinement; no claim
of final visual acceptance is made for this first terrain pass.

## Ore compatibility and abundance

The native `mythicbotany:base_stone_alfheim` tag additionally includes
`#alfheim:livingrock_natural`. This is necessary: otherwise changing livingrock walls would remove
the host that existing Elementium, Dragonstone and bloom features require. No broad vanilla ore
replacement tag is changed. Existing native ore and bloom recipes and feature counts are retained.

Four supplemental features place Grievebloom, Rimebloom, Emberwake and Farbloom into the new natural
host rock only, with size 12, five attempts per chunk, no air-exposure discard and a trapezoid
distribution from y=-54 to y=12. Their 16-block plateau centers the richer deposits underground.
They are confined to Alfheim's current land-biome roster, derived from the existing biome layer
and excluding the Void Verge. This is a geological host restriction, not an exact cavern-wall
distance test. Quarry-specific exposed seams belong to the archaeology pass.

## How this pass is measured

`tools/run_deep_terrain_validation.py` boots a separate fresh world for each run, using the same
seed for treatment and baseline. The treatment finds three widely separated candidate chambers
from the actual seeded density router. Each site then generates two perpendicular 256-block
sections, sampled every two blocks horizontally and every block vertically, from y=-64 to y=80.
That yields 112,230 actual block samples. Coordinates and block runs are saved with the console
and world names; no player save is modified.

The baseline uses the same sites and seed, restores the original density branch in the development
mirror, and removes this pass's other generated worldgen overrides in that mirror. The authoritative
instance keeps the treatment files. `tools/analyze_deep_terrain.py` compares upper density samples,
surface heights, open spans, lava, ores, natural stone diversity and the bedrock floor, and draws
the actual cross-sections. Measurements describe these targeted sections, not the frequency of
Deepworks complexes across the whole world.

## Remaining environmental work

The large-space pass must be judged before placing archaeology. Crystal chandeliers, paired
alignment scars, mineral columns, nuanced lava shores and slag terraces still need formation
generators. Quarries, sealed royal tombs and damaged Faultworks need supported entrances and
floors, plus validation of their entire required anchor volume. They are not added by this pass.
Client traversal and lighting review must include caves away from the measured seed and sites.
