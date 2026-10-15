# Continuity Works district refit — 2026-10-15

The existing twelve district families receive an architectural detail pass; the purple
crying-obsidian/magmatic-livingrock formations are separated from Faultwork mine rooms.
Broad terrain, player worlds, natural district admission and the bounded harbor fitter
are outside this change.

## Executed capability and reproducibility

Actual local Python execution uses Continuity Works 0.3.2 from
`C:/GITS/Structuresmith/StructureSmith`, through `StructureCapability.inventory_project`,
`audit`, `plan`, `register_generator` and `generate`. Its published downstream provider
interface wraps the pack's original district authoring generators; the generic dungeon
generator does not replace these buildings. Grade 3 retains their envelopes and purpose.
The report records the capability source hash, actual returned artifact hashes and
snapshot identifiers. Working snapshots and emitted bytes reside under
`build/continuity-district-refit/`.

Minecraft 1.20.1, Forge 47.4.10, original deterministic authoring seeds, home dimension
`mythicbotany:alfheim`. Non-vanilla IDs are probed against the block registry exported by
a fresh dedicated server on this date. Namespace discovery alone is insufficient.

```
python -X utf8 -B tools/cw_district_refit.py --cw-source C:/GITS/Structuresmith/StructureSmith --include-anomaly --promote
python -X utf8 -B tools/check_district_refit.py
python -X utf8 -B tools/run_cw_refit_validation.py
```

## Eightfold target and architectural layers

The regression floor is **at least eight times the original detail-block count per
family**, using the pre-existing `structure_detail.is_detail` vocabulary. That is a
measurable content target, not a claim of eight times the visual quality or voxel resolution.
`ALFHEIM_DISTRICT_BASELINE=1` in isolated generator child processes reproduces the
original geometry for comparison. New fixtures, lamps or entities do not inflate the
count: the increase consists of supported upper-wall mouldings. Masonry treatments also
add plinth courses, bay pilasters, spandrels, window frames, friezes, coffer patterns,
paving inlays and beam joints. The tall Frontier survey tower carries upper-story courses.

All 109 district templates retain their original sizes, terrain ownership, block entities,
loot and socket NBT. New relief touches original masonry and stays four air blocks above
every original walking surface, including upper galleries. Hydraulic basin walls and
the conservatory observation walkway retain their required materials. No rubble,
lanterns, floating crystals, mobs or new block entities are added by the detail pass.

## Purple formation separation

Source inventory identifies the rings and fractured cavern lining in the Faultwork
centre and wing. They were built into those mine templates; they were not merely an
independent structure set choosing the same chunk. Those components and their loose
purple debris are removed from the mine builders. Survey gantries, stairs, arches,
salvage and supported flush mana-glass instrument channels remain.

`alfheim:ley_fracture` now owns its own circular, sealed cavern, supported annular
formations, central monolith, four clear aisles and salvage cache. It emits a 47×32×47
template, pool and separate structure definition. It intentionally emits **no natural
structure set**: independent placement requires a runtime adapter enforcing a 500-block
footprint/reservation gap. Manual review command, in a disposable test world:

```
/execute in mythicbotany:alfheim run place structure alfheim:ley_fracture
```

The bounded read-only sample of `New World staven` found no crying obsidian around
spawn; the precise photographed formation has not been located. This repair removes
the confirmed authored source from newly placed mine templates. It does not erase
blocks in already generated player-world chunks or prove that every other mod's
underground structure obeys the new exclusion contract.

## Acceptance boundaries

`tools/continuity_district_refit_report.json` records per-piece comparisons and per-family
detail ratios. Each family's existing static checker verifies source equality, spatial
layout, connected portals and functional fixtures. `check_field_review.py` guards the
39 protected terrain files and previous model/mount/lighting repairs.

The disposable template gallery tests all 109 district pieces, three Faultwork pieces
and the independent fracture, then reads the saved world to check every added relief
cell, fixture position and sampled geometry. This tests registration and materialization;
it does not validate natural terrain fit, district spacing or a new jigsaw assembly.
Previous assembly evidence remains historical until rerun against this corpus. Client
visual review and natural-world placement remain **RUNTIME_TEST_REQUIRED**. Sacred,
Military/Warden and Frontier natural sets remain disabled.

The broad historical checkers were also run and do **not** pass: `check_spawn_hub.py`
reports 51 findings (nine water-cauldron registry false negatives, a stale baked-guard
assertion and 41 templates with existing orphan fragments). `check_structure_detail.py`
reports 136 findings, principally missing coverage for the ancient/field-review families,
the new geological anomaly and older court/leyline thresholds. These are separate from
the focused refit gates; the refit checker explicitly rejects newly orphaned geometry
relative to the original corpus. Do not describe this release as a clean global audit.

## Measured family detail counts

| Family | Original | Refit | Ratio |
|---|---:|---:|---:|
| common residential | 148 | 1400 | 9.459× |
| elder lineage | 410 | 3937 | 9.602× |
| civic center | 320 | 3250 | 10.156× |
| relief district | 238 | 2686 | 11.286× |
| scholastic quarter | 360 | 2966 | 8.239× |
| production district | 74 | 3549 | 47.959× |
| agricultural estate | 194 | 2764 | 14.247× |
| harbor complex | 266 | 4087 | 15.365× |
| sacred precinct | 97 | 1838 | 18.948× |
| military warden | 142 | 2055 | 14.472× |
| frontier stewardship | 251 | 2289 | 9.12× |
| roads trade | 107 | 3231 | 30.196× |

## Final local acceptance evidence

All twelve family source/layout/functional checkers pass. `check_district_refit.py`
passes for 109 district templates: 122,361 changed cells and 31,445 supported relief
cells, with no newly orphaned geometry. Detail counts rise from 2,607 to 34,052.
The dedicated-server gallery passes 113 templates and 31,551 relief/fixture positions;
every recorded shipping artifact hash still matches (test seed `3536368297089363045`). Evidence:
`tools/continuity_refit_runtime_report.json`, console `server/console-20261015-013631.log`.
The 39 protected terrain files and 106 custom-model checks pass. No client visual or
natural-world acceptance is implied.
