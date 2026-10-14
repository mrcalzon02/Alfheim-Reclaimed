# Void formation support review

Controlled runtime review, 2026-10-14. Player saves and broad terrain were not modified.

Verge markers, Shatter anchors and mourning steles now require their native stone beneath the initial air cell. They retain one column per attempt, original height distributions and outer rarity. Previously their configured columns accepted air without checking the support below.

The nine newer formations are tested alongside those three repairs. Test-only selector wrappers preserve production offsets and environment scans. Hanging formations start above a five-block native shelf, scan down through it, and grow from its underside; a 37-block shelf exceeds the 32-step limit and rejects.

| Formation | Correct-host signature blocks | Wrong host | Unsupported air | Thick shelf or water | Attached columns |
|---|---:|---:|---:|---:|---:|
| verge_markers | 3 | 0 | 0 | 0 | 1 |
| shatter_anchors | 4 | 0 | 0 | 0 | 1 |
| mourning_steles | 2 | 0 | 0 | 0 | 1 |
| verge_shear_steps | 10 | 0 | 0 | 0 | 7 |
| shatter_fault_teeth | 7 | 0 | 0 | 0 | 7 |
| prism_split_inclusions | 8 | 0 | 0 | 0 | 0 |
| rootfall_fossil_knots | 9 | 0 | 0 | 0 | 0 |
| sepulchral_fallen_plates | 9 | 0 | 0 | 0 | 6 |
| starless_null_teeth | 7 | 0 | 0 | 0 | 6 |
| shatter_hanging_faults | 6 | 0 | 0 | 0 | 6 |
| prism_suspended_needles | 4 | 0 | 0 | 0 | 4 |
| rootfall_hanging_ribs | 49 | 0 | 0 | 0 | 7 |

Every upright and hanging column is continuous and touches its original native host. Ore inclusions replace only their matching host; ordinary host updates persist the manual ore edits before the saved-world census. Each case occupies four isolated 19×19 pads. The test forces 108 chunks once and performs no site search.

Rarity, in-square, heightmap and biome filters are omitted from these controlled wrappers. This establishes substrate behavior and bounded underside scanning, not natural frequency, landscape fit or client appearance. Existing bramble/thorn natural-sample evidence remains separate.

World: `server/validation-void-formations-20261014`. Console: `server/console-20261014-141944.log`. Machine-readable source and test-pack hashes: `tools/void_formation_runtime.json`.
