# Shore decoration development — 2026-10-14

Adds two small shoreline details and repairs fallen wood without changing density,
surface rules, biome selection or the accepted harbor placement policy.

| Detail | Placement and budget | Support |
|---|---|---|
| Mistbark stone scatter | Silvermist/frost stone, five single-block attempts forming low clusters up to two blocks high, rarity 9 | Soil, sand, gravel and the native Mistbark stone family |
| Void Shore wrack | Chalk/shale strips up to three blocks long, two attempts, rarity 13 | Sand, gravel and native Void Shore rock |
| Shore driftwood | Two fallen trunks up to four blocks long; existing rarity 4 retained | Soil, sand, gravel and native shore stone beneath every cell |

The previous driftwood configuration rejected beach sand/gravel and native shore
rock, mixed in dead bushes, and represented logs as isolated upright cubes.
The repair chooses one species per trunk, then an X or Z orientation. Its maximum
eight log blocks per patch matches the previous eight single-block attempts.
Columns stop when their per-cell air/support predicate fails, preventing bridges
across missing ground and replacement of occupied cells.

The existing Emberbark, Gloambark and Hushbark logs also need an axis property and
rotated column models. They keep their IDs, materials and vertical default; the
placement callback follows the clicked face. Both tree and shore generators use
the shared log-axis source so regeneration retains the repair.

Static validation passes source equality, native beach support, horizontal log
axes, two deliberately broken safety fixtures, effective biome injection and
feature ordering. All 39 protected terrain files remain unchanged.

Saved-world validation passes all 27 controlled cases covering grass, sand,
gravel, native stone, wrong stone, missing support, water, edges and occupied cells.
All 65 fallen log blocks retain horizontal axes (27 X, 38 Z); all 12 explicit
axis/default states across the three grove logs survive saving. Every decoration
has support, including the upper stones in two-block clusters, and occupied
test volumes remain intact. The sparse edge case uses 50 bounded calls per
feature; other cases use five. These are safety tests, not frequency samples.

Two untouched 64-chunk patches contain 128 fully generated saved chunks. Raw
natural stone or log counts cannot uniquely identify one decoration feature,
so they must not be reported as its observed frequency. Client appearance and
manual player-placement callbacks remain unreviewed. World:
`server/validation-shore-details-axes-20261014`; successful server console:
`server/console-20261014-180220.log`; hashed proof: `tools/shore_detail_runtime.json`.

The test launcher also now distinguishes this pack's Forge/Java runtime from an
unrelated NeoForge server. It waits for the dedicated-server ready signal before
queuing commands, with a 300-second bound. This repairs false process matches
and invalid command contexts when a slow boot exceeds the old fixed delay.
No other Java process was stopped. The final server run saved and exited with
code zero in 282.2 seconds; the read-only saved-world review passes separately.

Sources: `tools/gen_shore_details.py`, `tools/gen_grove_log_axes.py`.
Checks: `tools/check_shore_details.py`, `tools/run_shore_detail_validation.py`.
