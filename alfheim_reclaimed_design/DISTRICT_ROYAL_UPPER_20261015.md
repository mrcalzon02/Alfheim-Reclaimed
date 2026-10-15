# District spacing, royal citadel and upper-rock discoveries

## District placement

All twelve district definitions now use a shared 192/96-chunk candidate grid and
salt. A native, deterministic family selector admits exactly one family per cell;
the other families return before terrain sampling or jigsaw assembly. Different
families cannot independently claim the same position. Candidate spacing leaves a
conservative **1,024-block footprint gap**, allowing a 256-block reservation radius
per district, including harbor rotations. This exceeds the 500-block contract.

District starts are rejected within 6,000 blocks of the original spawn region and
within 4,096 blocks of the currently bound Alfheim world spawn. These checks use
squared distance and read the existing spawn position; they never load chunks.
The nine admitted families retain their natural sets. Sacred, Military/Warden and
Frontier definitions receive the same policy but remain disabled naturally.
Unused family selections are not replaced by a different district.

The harbor retains its accepted approximate fitter: 32 columns / 150 ms, no
additional shore search. Its spawn/grid guard runs first. Existing generated
districts are not relocated; this policy governs future generation.

## Royal castle

Continuity Works 0.3.2 `StructureCapability.generate`, using the registered
`CastleProvider`, emits six template types for a **235×235-block, 25-tile citadel**:
three-floor keep, four high corner towers, four gatehouses, curtain walls, four
court halls and four gardens. Templates fit the 48-block editing limit. There
are upper-floor stairs, battlement walks, royal furniture, archive shelving,
contained reflecting pools and flush magical lighting.

Three concentric-ring candidates are reserved near the original spawn region
(nominal radius 1,024–1,792 blocks, with vanilla preferred-biome adjustment).
It prefers plains, Golden Fields, Bloomfall, Silverbark and Alfheim Hills.
A fixed priority admits only the first suitable candidate, so at most one natural
castle wins. Each candidate uses nine terrain columns (27 maximum), allowing up to
80 blocks of relief; Void or build-height failures are rejected without region searches.
The platform stays above sea level, allowing a supported coastal/island citadel.
The start remains centred within vanilla's eight-chunk structure-reference reach.

A saved native foundation piece fills air, fluids and soft vegetation below the
citadel, stopping at solid ground, with a strict limit of 96 blocks below the tile origin (plus its eight-block plinth) and
chunk-local writes. It does not replace buried solid terrain with a massive
solid template. The complete site still requires visual terrain/approach review.
An already generated ring location in an existing world is not automatically rebuilt.

## Above the Deep

The documented Deep density envelope is Y=-60..27 (`DEEP_TERRAIN.md`). The new
upper-rock structures own **no blocks below Y=32**, start at Y=32..96 and retain
at least twelve blocks of surface cover. They do not edit density, surface rules,
bedrock or the existing Deep markers.

Twelve 31×20×31 discoveries are authored: Moss Grotto, Calcite Drapery, Root Vault,
Buried Cistern, Abandoned Gallery, Collapsed Archive, Silt Pool, Basalt Columns,
Fossil Pocket, Crystal Beds, Buried Bridge and Lithic Fault. They include supported
formations, discovery mouths, fossils, contained water, magical floor lights and
ordinary abandoned supplies. No entities, spawners or progression treasure are added.

Their shared 80/48-chunk grid permits only one variant per start. A 4,000-block
origin reservation protects the castle/hub region. Before terrain work, the native
adapter rejects candidates within 800 blocks on both axes of district reservations
and biome-eligible random-spread underground structure reservations. This covers
the existing quarries, tombs, Faultworks and ley corridors without recursive
structure/chunk lookups. Deep structures and upper discoveries remain separate.
Concentric underground placements from unrelated future mods need separate review.

## Evidence and limits

`tools/district_spacing_report.json`: shared data policy, spawn bounds, footprint
gap, installed first-party artifact hash and Java test results. All twelve existing
district source/layout checkers pass with the new definitions. The existing 39-file
terrain and 106-model regression guard passes. Broad historical audit findings from
the prior refit remain documented separately.

`tools/royal_castle_report.json` and `tools/upper_underworld_report.json` record actual
Continuity Works snapshots and emitted artifact hashes. The disposable runtime
runner is `tools/run_royal_upper_validation.py`; its final saved-world report is
`tools/royal_upper_runtime_report.json` when accepted. A forced complete-castle
placement and template gallery do not establish natural population density or
client visual quality. Upper-rock natural placement and client review remain
RUNTIME_TEST_REQUIRED until bounded field evidence exists.

Final local proof: Java17 build and 61 tests pass. All twelve district source/layout
checks pass. Source equality and orphan checks pass for all eighteen new template
types. Saved-world validation passes 25 complete castle tiles, nine foundation
columns and 7,819 geometry samples. Natural ring lookup locates [-1088, 1392],
1,766 blocks from the origin, on test seed 3536368297089363045. Runtime proof:
`tools/royal_upper_runtime_report.json`; console `server/console-20261015-101124.log`.
The district veto at the loaded origin passes; protected terrain/model gates pass.
Upper-rock natural population and client visuals still require field review.
