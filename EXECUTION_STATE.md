# Execution State

## Latest implementation — terrain authorities, stage 1 — 2026-09-12

The 2026-09-11/12 field review rejected the margin four times in one session, and the owner chose
a rebuild over further increments. Scope is the owner's own framing: *"this area is this biome,
this terrain generation takes predominant control of this area."* Design record:
`alfheim_reclaimed_design/TERRAIN_AUTHORITIES.md`. Backlog: **B-96**.

**Three symptoms, one root cause.** Void Shore prolific (every dip below −0.58 becomes land);
water standing in the void (2.5% of void columns, **100% within 60 blocks of an ocean**, dry ones
median 84); faces no carve could roughen (rugged plateaued at 0.53). All three come from
expressing every landform as a branch of one density keyed to a field whose gain is not ours —
`1.7 x badlands_surface`, clamped, which makes the Verge **sixteen columns wide** against a shelf
sixty blocks thick, and makes every band cost ocean at 1:1.

### The fact the architecture rests on

**The biome layer is a disjoint covering partition of axis-aligned boxes** — 44 entries, 0
overlapping pairs, 0.000% of climate space uncovered over 200,000 samples. Multi-noise selection
is nearest-neighbour, so with overlaps or gaps "which biome" is a distance computation no density
function can reproduce. **That is exactly how B-82 stamped Hills terrain into Plains and Silverbark
and had to be reverted.** With a disjoint covering partition every point lies in one box at
distance zero and membership is axis-aligned threshold tests, which `range_choice` reproduces
exactly. The defence is not better thresholds — the partition IS the selection.

### What stage 1 delivered

| target | state |
|---|---|
| `TERRAIN_AUTHORITIES.md` | architecture, contracts, staging, and the five proven constraints |
| `tools/gen_terrain_authorities.py` | selector emitted from the same CLAIMS list as the layer |
| `tools/check_terrain_authorities.py` | A1..A5; **60,000 climate points, 0 disagreements**; self-test **5/5 fire** |
| 46 shipped files | 44 named steps + 2 authority leaves, 31.6 KB, largest step 948 bytes |
| boot | pack loads with all 46 present, `Done (49.557s)`, zero density-function errors |

**The chain is named rather than inline, and that is arithmetic.** Each band's test is up to five
nested `range_choice`s and every false branch must reach the rest of the chain; inline the tail
repeats once per axis test and the document grows as 5^44.

**Stage 1 moves no terrain on purpose.** Both authorities carry the same expression — today's
whole `alfheim_final` body, inlined rather than referenced so that wiring `alfheim_final` to the
chain cannot close a cycle through itself. A5 asserts the leaves stay byte-identical. The
framework is proven before anything moves, so a later regression cannot be confused with the
migration.

### Two constraints now written down rather than rediscovered

**A carve expressed as a density offset is gradient-dependent.** It removes down to a fixed
density value, so how far that reaches in blocks is the local gradient's business: ~5 blocks on a
flat top, **~0.6 of a block on a sheer face**. Enough amplitude to move a vertical face shreds
every horizontal surface in the same breath. Regions wanting different terrain need different
*expressions*, not different constants — which is the formal reason the last four worlds hit a
ceiling at rugged 0.53.

**The aquifer collar cannot be removed by any architecture.** `Aquifer.NoiseBasedAquifer` samples
preliminary surface across chunk offsets −3..+1, so a ring of above-sea-level land is mandatory.
What a purpose-built field changes is that the ring becomes a fixed **width in blocks** instead of
a value band — which is both the plateau and the standing water, from one cause.

### Where the margin stands, measured

| | session start | now |
|---|---|---|
| walls per 1000 margin columns | 22.7 | **9.9** |
| solid runs per column | 1.26 | **2.04** |
| exposed faces per solid block | 0.46 | **0.53** |
| full-depth fins | 8.0% | **4.3%** |
| cliff-foot talus | — | **25.7%** |
| prism_drift empty | 7.6% (a regression of mine) | **73.6%** |
| ocean water-bearing | 60.3% | **100.0%** |
| Golden Fields terrace excess | +31.8 | **+22.1** |

### Next

**Stage 1b — wire `alfheim_final` through the selector.** Emit the chain's first step as
`alfheim_final`'s own body rather than a top-level reference, so the registry codec question does
not arise and no cycle is possible. Acceptance is a generated world block-identical to
`void-margin-20260912-072941` on the same seed, since both leaves are the same expression.

**It requires two guard repairs first, and neither should be skipped.** `check_worldgen` W7 reads
`alfheim_final` expecting a `range_choice` whose `max_exclusive` is the void terrain band; through
the selector it must follow the indirection to the void authority instead. `check_alfheim_hills`
asserts `actual == void_final_density()` and must compare against the authority leaf.

Then stage 2: the dedicated void field on the erosion axis, normalised to −1..1 so `CLIFF`,
`TERMINAL`, `FRINGE` and `check_void_surface_support`'s −0.94..−0.925 landing window keep their
meaning.

**Deferred, unchanged:** `libx:smash` removal (built, untested, awaiting a decision); the pixie
census (B-95); the residual 2.5% of void columns carrying water (DEFICIENT_BIOMES.md §2.7).


## Latest implementation — the sea had nowhere to stop — 2026-09-11

A client walk rejected three things at once: empty volumes with deep rock below them and nothing
above, the void edge still reading as a sheer cliff, and the ocean bleeding out over that edge.
All three were reproduced against `saves/New World Ferngale` before anything changed — 764,672
columns read out of the region files — and all three turned out to be the same defect seen from
different angles.

**`alfheim_ocean` claimed continentalness -0.80..-0.28 and the aquifer router dried everything
below -0.58.** The outer 42% of the ocean's own climate band was therefore an ocean biome, over an
ocean-shaped seabed, with the water suppressed: **123,145 of 348,224 ocean columns** carrying no
water and nothing above Y 40. At z=223 every ocean column from x -180 to -113 reads seabed
-53..29, water count zero. That is the "deeps below it but nothing above".

**And `DRY_AQUIFER_RIM` could not simply be pulled back.** `Aquifer.NoiseBasedAquifer` samples
preliminary surface at chunk offsets spanning -3..+1 and blends the three nearest cells, so a
narrow shoulder floods the whole void to Y 64. The shoulder's width was never the defect. Leaving
the band it dried at seabed height was.

### What was repaired

| target | repair |
|---|---|
| `gen_void_worldgen.density()` | the Verge plain runs on past `RIM` and only turns into sea floor between `COAST_RIM` -0.55 and `COAST_TOE` -0.46; the sea ends against land |
| `alfheim:void_shore` | new biome, -0.72..-0.55: the void's own coastline, emerged and dry, so the edge is three bands deep |
| `alfheim_ocean` claim | -0.55..-0.28; every band it gave up was dried basin, so no wet ocean was lost |
| `attach` / `UNDERCUT` | the undercut is local to the lip; the approach is rooted to bedrock where it is walked |
| breakline erosion | broad `appetite`, 3D `spall`, interpolated underside `lift` — the edge is a coast, not a contour |
| `void_shore` surface rule | in the un-gated void rule, not `identity_surface_rule()`, which cannot fire inside the dry band |
| `gen_spawn_hub.LAYER_BIOMES` | derived from the layer instead of transcribed |
| `surface_works_manifest` | Strandline Hulk and Edgewatch Beacon, so a 357k-column biome is not empty |

### The breakline was a contour line, and the control proves it

Measured over 900 columns in 30 rim segments against a control with the erosion terms zeroed:
the outer edge of the plain sat at **exactly -0.8600 in every single column, spread 0.0000**, with
a face of 61..78 blocks, standard deviation 3.2. Every point at the same continentalness had the
same profile, because the margin was a pure function of one smooth 2D scalar. Shipped: median face
**33 blocks**, 58% of the rim under 40, a third still carrying a 60..78 block headland.

### Two measurements that only the other one could make

**The analytic sweep passed the first shaped build and the generated world rejected it.**
`measure_void_edge.py` reported median face 69 -> 33 and 58% under 40 on code whose survivors were
**130-block fins**: at z=-704, x=-1711 is void_verge solid -53..76 with prism_drift carrying
nothing on either side. Erosion reached 0.09 inland while the undercut reached only 0.06, so
across the strip between them the break removed whole columns from a shelf that was still welded
to bedrock. The sweep samples one column at a time, and **from inside one column a fin and a butte
are the same measurement.** `UNDERCUT` is 0.12 now and VG8 asserts the containment; full-depth
fins at the break fell from **19.5% to 5.1%** of Verge columns, read out of generated chunks.

That is the 2026-09-09 lesson one level up. A density function can be correct at every sampled
point and still produce the wrong landform; a distribution can be correct at every column and
still describe the wrong landform.

**And the sweep caught what the world could not have explained.** Lifting the underside by
subtracting from its `y_clamped_gradient` drove the median face from 69 to 123 blocks, because the
gradient saturates at +/-1 outside its span and the `min()` went the other way entirely. In a
generated world that reads only as "the rim got worse". Both tools are in `tools/` now rather than
in a scratchpad, which is where the 2026-09-09 cross-section renderer was left and lost.

### Guards

VG6 capped relief at 0.18 and detail at 0.05. **That is a proxy** — a cap on each amplitude says
nothing about where the surface lands, because that depends on the gradient the amplitudes are
added to, which the rule never read. It now derives the plain's lowest possible surface from the
shipped density and requires it to clear sea level. VG7 asserts that every column the aquifer
dries stands on that plain and that the attach bias clears the underside floor. VG8 asserts the
erosion stops inside both the terrain band and the dry shoulder, is clamped at zero, varies along
the rim, has a three-dimensional term, and is contained by the undercut.
`check_void_geology --self-test`: **16/16 proven to fire.**

### Evidence

| | |
|---|---|
| Commits | `6902f101`, `1e85b8c2`, `4850825b`, `79cb1107`, `6428e785`, `db7889e7` — all local, **unpushed** |
| Worlds | `server/void-margin-20260911-171819` and `-172920`, both exit 0, audit true, KubeJS clean |
| Ocean | **100.0% of ocean columns at sea level, 0.0% bare** (was 39.7% below sea level with nothing on it) |
| Void Shore | 357,520 columns, minimum surface **Y 65** — emerged everywhere |
| Surface rule | Void Shore reads riftchalk 67%, sand 18%, gravel 12%; no bare Deepworks strata |
| Fins | 19.5% -> 5.1% of Verge columns at the break rooted to bedrock |
| Static | 13 guards pass, plus `check_spawn_hub`, `check_surface_works`, `check_feature_order` |
| Admission | **fresh-world validated** for the ocean and the approach; the rim's *read* is client-pending |

### Next

A client walk. Every number above is read from region files and nobody has stood in any of it.
Three things need eyes: whether the Void Shore reads as a coast or as a grey apron, whether the
eroded lip reads as the world coming apart or merely as a shorter wall, and whether the 5% of
rooted spurs read as headlands or as leftover fins.

**Deferred, with the test named.** The pixie hamlets do receive valid structure starts — three of
four cultures placed in 21,305 chunks of `void-margin-20260911-171819` — but **not one of their
chunks reached `minecraft:full` in any world generated so far**, so whether the islands actually
build has never been observed. The census needs a world centred on a pixie host biome with enough
radius to take the start chunks to `full`, then a block count at Y 208.
`PIXIE_SETTLEMENTS.md` already names the suspect: Continuity Works auto-enrols every registered
structure in a 500-block exclusion, `autoIncludeRegisteredStructures = true`.


## Latest implementation — the line endings were never this project's to choose — 2026-09-10

Three byte-equality guards were failing and none of them could say why. `check_deepworks`
reported 414 drifting models, `check_material_textures` a drifting texture, `check_fey_generation`
a drifting quest chapter. **Not one character of content had changed in any of them.**

Git's `core.autocrlf=true` is set in the *system* config — `C:/Program Files/Git/etc/gitconfig`,
not in this repository and not by anyone working on it — and there was no `.gitattributes` to
overrule it. Every commit stored LF; every checkout wrote CRLF; every generator under `tools/`
emits LF. So 8,786 tracked files differed from their own blobs by one byte per line and nothing
else, and level 6 of the ladder had been asserting against the wrong bytes for as long as that
was true.

**A byte-equality check cannot tell a re-encoded file from a re-authored one.** That is the point
of level 6 and also its blind spot, and the diagnosis had to come from outside the guards:
`git cat-file blob HEAD:<path>` against the worktree, for all 29,534 tracked files at once. It
separated cleanly — 8,786 CRLF-only, 45 genuinely different, and those 45 were exactly the staged
`server/` mirror and runtime-config churn that was already known about.

### What was repaired

| target | repair |
|---|---|
| `.gitattributes` | new; `* text=auto eol=lf`, `*.bat`/`*.cmd` pinned CRLF, 14 binary suffixes declared |
| repo-local git config | `core.autocrlf=false` |
| 8,782 worktree files | rewritten CRLF to LF, each only where the result provably equalled its blob |
| 63 call sites in 36 tools | `newline='\n'` pinned on every text-mode write |
| `tools/run_fey_validation.py` | unresolved merge-conflict markers removed, committed at HEAD |
| 16 void-material textures | regenerated; every one proven pixel-identical before writing |
| `tools/check_midgard_biomes.py` | M0 reads the harness's resolved commands, not its source text |
| `tools/check_ancient_districts.py` | A4 asserts the contract is stated, not one exact sentence |
| `tools/check_fey_generation.py` | `config/ftbquests/` excluded from byte comparison; reported paths made posix |

**The generators disagreed with each other, and the repository was hiding it.** `gen_deepworks`
and `gen_void_materials` build `bytes` and write LF. Thirty-six other tools used
`Path.write_text()` or a text-mode `open()`, which on Windows turns every LF into CRLF on the way
out. While the worktree was CRLF the second group matched and the first did not; normalising to LF
swapped which half was broken — `check_fey_generation` went from 1 problem to 106 — and proved the
real defect: **the same generator emitted different bytes on Windows than it would on Linux.**
Pinning `newline` at all 63 sites is what makes level 6 mean anything on more than one machine.

### Two guards that had never asserted their invariant

`check_midgard_biomes` M0 searched `run_server.py`'s **source text** for
`locate biome continuityworks_biomes:temperate_grove`. All six probes are written as two
implicitly concatenated string literals across two lines, so the substring was never present and
never could be, while the harness issued every probe correctly. It now reads
`run_server.DEFAULT_COMMANDS` — all six FOUND.

`check_ancient_districts` A4 required the generator to contain the sentence
*"subordinate homes, roads, cistern/trace edges"*. `git log -S` finds that string only in the
checker, on `b6c303c6`, and never once in `gen_ancient_districts.py`, which has said
*"subordinate members are jigsaw-only"* since `ed204d76`. **A4 could not pass on any commit in
this repository's history.** It now asserts that the contract is stated rather than how it is
worded.

That is the same defect shape B-93 recorded three times on 2026-09-09 — a guard measuring a proxy
instead of the invariant — found twice more, in guards nobody had reason to doubt because they had
simply always been red.

### The fey guard compared bytes against a file the game rewrites

`check_fey_generation` byte-compared `config/ftbquests/quests/chapters/ref_fey_wildlife.snbt`
against generator output. INSTRUCTIONS.md section 5 already states that FTB rewrites that
directory on every world load, and the shipping file is visibly the game's form: keys
alphabetised, `quest_links` added, IDs the game minted itself — `73373E92A355D7DC` on disk
against `C2FB7BDD0D32592A` from the generator — 433 lines against 363.

**Owner decision, 2026-09-10: exclude `config/ftbquests/` from the comparison.** Presence is still
required, so the chapter cannot silently disappear; only its bytes are no longer asserted. Every
other file this generator owns is still compared byte for byte, and the guard now passes at 107
files reconciled.

**Its self-test had never passed on this machine either.** The fixtures expect
`generator/source drift: out/000.json` while the message interpolated a `Path`, which renders a
Windows separator here. Green on Linux, red on this machine, for exactly the reason the generators
emitted different bytes on the two platforms. Reported paths now go through `as_posix()`, and the
self-test passes.

### Evidence

| field | value |
|---|---|
| Repository | `mrcalzon02/Alfheim-Reclaimed`, `main`, HEAD `e677905e` unchanged |
| Checker suite | **33 pass / 10 fail → 37 pass / 6 fail** |
| Repaired | `check_deepworks` (1,486 files byte-identical), `check_material_textures`, `check_ancient_districts`, `check_fey_generation` |
| Compilation | all 88 tools compile; 2 were failing, 1 from committed conflict markers |
| Conflict markers | none remain anywhere in the repository |
| Object store | `git fsck --connectivity-only` clean — dangling blobs only, no missing or broken objects |
| Worktree | 89 real changes (16 textures, 38 tools, 35 `.pyc`); staged churn of 64 untouched |
| Commit | **none — unstaged, uncommitted** |

### Deliberately not resolved

**`check_royal_assets` — a validator for content that does not exist.**
`kubejs/data/alfheim/structures/royal_assets/` has never been tracked, `tools/royal_asset_metrics.json`
is absent, and neither BACKLOG.md nor this document mentions the Royal / Noble Cultural Asset
Library anywhere. `tools/gen_royal_assets.py` and `tools/royal_asset_manifest.json` exist. Running
a generator that writes a structure library into `kubejs/` is not a repair, so it was not run.

**`check_midgard_biomes` M1 — deferred, not failing.** The static contract now passes. M1 wants a
console carrying the six probes; the newest, `server/console-20260909-140525.log`, has zero
`locate biome` lines because it came from a different harness. Resumption: one `tools/run_server.py`
run.

**The object store carries garbage from an interrupted `gc`.** Twelve `.pack` files have no `.idx`
and 17 `tmp_obj_*` files sit in `.git/objects/`, together about 260 MB. `fsck` proves nothing
depends on them. Left alone: `git gc` is the correct cleaner and is a long mutating operation on a
1.1 GB store.

## Latest implementation — the September 9 field review, three worldgen regressions — 2026-09-09

A client walk of `saves/New World Cherish` rejected three shipped systems at once. All three were
reproduced against that save before anything changed — 22,800 chunks read straight out of the
region files — so the diagnosis describes the world the reviewer was standing in. B-93 carries the
full record; this is the operational state.

**All three shared one shape of defect: a guard that measured a proxy instead of the invariant.**

| system | the guard said | what it did not assert |
|---|---|---|
| terraces | the sawtooth stays within ±0.5 (G5) | that it returns to **zero** outside its band — a saturated constant satisfies a bound |
| terraces | the weight is 0.0 outside the climate box (G3) | it swept continentalness and weirdness, the two axes Golden Fields and Silverbark Wood **share**, and not temperature, the one that separates them |
| void | the debris shaping noises are absent from final density (VG3) | that the far field is empty and fragments stay masked — the rule would have passed an unbounded field written from any other noise |
| structures | per-family detail floors (D1/D2) | *what* the detail was; 1,622 misplaced blocks raised the share it measures |

Each guard was repaired to assert the invariant directly, and each repair is proven to fire against
the pre-fix input: G7 catches the old saw at 290 block levels, VG3a/VG3b/VG3c are covered by
`check_void_geology --self-test` at 8/8, and G3 now sweeps temperature.

**Three commits, each a bounded unit.**

| commit | change |
|---|---|
| `7d591b12` | the debris belt gets terrain; the Verge gets its dry plain at Y 71 |
| `d8cdbf52` | `dress()` can no longer choose what a building contains; 1,622 → 150 blocks |
| `bca3c54e` | the saw returns to zero, the weight gains temperature, amplitude cut |
| `22ac3b9f` | the belt gets a skyline; two measurement tools the project lacked |
| *(head)* | the belt drops to shelf level, the Verge gets an underside, amplitude settled at 0.30 on four measured points |

**One premise unblocked another repair.** The debris field had been removed on the grounds that
cell interpolation could carry a splinter past its mask. B-86 disproved that on 2026-09-08 —
`alfheim_final` holds no `minecraft:interpolated`, the markers are inside `alfheim_height` and
`alfheim_caves`, so the branch is evaluated per block — but the finding was recorded only in
`gen_deep_terrain` and never carried back to `gen_void_worldgen`. Rebuilding the belt was possible
because a measurement from one target was applied to another.

**Current acceptance: fresh-world validated for the two terrain systems; static for the
structures.** 13 guards pass. Six server generations across four worlds.

**What the generated worlds added that static checking could not.** Three defects, all of them
invisible to a density-function reading and obvious in a cross-section:

1. *A flat lid on the debris belt.* The envelope's upper edge was steeper than the fragment noise
   and therefore decided every top — 74% of shatterfields columns at exactly Y 92.
2. *Islands in the sky.* The belt sat Y 85–110 above a Verge shelf at Y 71, so the fragments read
   as sky islands over intact ground rather than as land coming apart.
3. *The fins in the screenshots.* The Verge had no underside at all, solid from the basal guard at
   Y −54 to its surface, so a narrow continentalness footprint generated a 130-block curtain wall.

All three are repaired and re-measured. The lesson worth keeping: **a density function can be
correct at every sampled point and still produce the wrong landform.** The cross-section renderer
in the scratchpad found in one image what four static probes did not.

**And the terracing's dominant term was not the one the project thought.** Four fresh worlds on one
seed reading the same patch: amplitude 0.20 → 1.10×, 0.30 → 1.11×, 0.45 → 1.12×, against the
rejected 0.60-with-wide-ramps at 2.75×. More than doubling the amplitude moves the result by six
tenths of a point; the climate ramps decide almost everything. B-86 had the same measurement
("tripling the amplitude bought eight points") and read it as an interpolation-cell ceiling. It was
a coverage effect, and the 2026-09-08 ramp widening — not the amplitude — is what shipped the
stacked floors. Recorded in `gen_golden_terraces` so the next person widens the right knob.

**Second verification pass, 2026-09-09/10.** Six headless generations across five worlds, all
exit 0, KubeJS at zero errors. It overturned one of the claims above and confirmed the other two.

| claim | how it held up |
|---|---|
| terracing repaired | **overturned, then repaired properly.** A control world showed the addend was contributing nothing: treatment 27.7% on one residue against a baseline 27.8%, deep void 3.42% against 3.42%. The climate ramps carry the coverage and had been narrowed to zero effect; restored, the treatment now reads +4.0 points over its own control with Silverbark and Dreamwood unmoved and the deep band untouched. |
| detail pass repaired | **confirmed at runtime.** 8,040 generated chunks contain 94 bookshelves, 70 barrels, 3 cauldrons, 1 lectern and zero decorated pots — the hand-placed set exactly. 16 structure types placed across 40 starts. |
| debris belt built | **confirmed, then corrected.** Coverage said it worked; measuring it as landforms found 103,440 of 103,937 void columns in one mass welded to the Verge. Correlated noise percolates, so the cut moved and the belt came apart into a mainland plus 31–73 islands per rim segment. |

**The reusable lesson, and it cost two calibration cycles: a metric with no meaningful zero
cannot tell a working feature from an absent one.** On-tread share returns 27.8% on terrain that
was never touched, and terrain coverage returns 98% for a shelf and for a debris belt alike.
Both now have a stated control — `run_terrace_validation --mode baseline` for the first,
`probe_void_fragments` reading connected components for the second — and both controls found a
defect on their first run.

**Next gate: a client walk.** Every number in B-93 is read from region files; nobody has stood in
any of it. Three things need eyes rather than metrics:

1. Whether the terracing at 1.11× reads as "gradual laid out terraces" or as no terraces at all.
   It is deliberately subtle now, and the metric cannot make that call. The ramps are the knob.
2. The void margin as a place — cliff readability, whether the buttes read as a broken edge, and
   whether the debris is reachable and worth reaching.
3. The six structure families, which is the review B-91 was already waiting on.

**Known and deliberately out of scope.** The biome bands still run land → ocean → verge → debris,
so the void is reached across water rather than from a dry approach. That is the standing
`DEFICIENT_BIOMES.md` rejection; it needs the biome geography reordered and was not touched here.

## Latest planning — Alfheim Golems — 2026-09-09

B-92 now owns a separate planned first-party mod, `alfheim_golems`. No Gradle scaffold, registered
content or jar exists yet. The durable contract is `alfheim_reclaimed_design/ELVEN_GOLEMS.md` and the
implementation waves are in `first_party_mods/alfheim_golems/docs/ALFHEIM_GOLEMS_PLAN.md`.

Settled scope: Worker, Artisan and Sentinel chassis; Fire/Water/Earth/Air versions of each; Manna
Stone Command Gem orders; real inventory, furnace, crafting and audited machine work; recursive
Simple/Advanced/Combat cores; wild Deep variants providing costly-route salvage; and four consumed
Sentinel Vessels that summon owner-allied combat golems for an initial target of 120 seconds. Wild
salvage may remove bulk cost but does not commonly drop pristine cores or bypass era processes.

Current acceptance: **planned only**. Next gate is G0, the independent Java 17/Forge scaffold and
pure contracts; it must not inherit companion inference or claim implementation by copy. The owner
will not perform runtime validation: every golem gate must use automated tests, scripted servers,
fresh-world surveys or automated client interaction/capture.

## Latest implementation — the structure detail pass, all six families — 2026-09-08

`THE_SURFACE.md` pass 5 has been open since the first field review: *"the hero-detail/slow-decay
pass across every archetype."* It is now implemented for every structure set in the pack, not only
the surface one, because the census built to scope it found the same gap everywhere.

**The measurement came first, and it disagreed with the eye.** `structure_detail.census()` counts
what share of a piece's solid blocks are small-scale articulation rather than bulk mass. Over the
105 shipping templates at `9b393f2`: 29 pieces under a 4% detail share, `greatbole/trunk` built
from **three** block ids repeated 6,645 times, and every leyline bend, terminal and hub at a flat
**zero** — because all of the hanging light lived in `channel_line`, which only the straights call.

**One vocabulary, five generators, and it is never told where the rooms are.**
`tools/structure_detail.py` implements the five layers of `THE_SURFACE.md` §3.2 as passes over a
finished `Piece`, deriving every candidate from geometry: a wall face is a solid with a free cell
beside it, a floor is a solid with headroom over it, an overhang is a solid with nothing under it.
The same `sconces()` call therefore works on a castle keep, a mine drift and a pixie cottage. It
was extracted for the reason `structure_nbt.py` was — a second generator needed it, and copying it
would have made two divergent answers to one question.

**The order is the mechanism.** `dress()` runs before each builder's decay pass and `aftermath()`
after it: detail laid down first is what the building had, so decay eats it where it eats the
walls; detail added after is what the collapse did — debris heaped at the foot of the wall it fell
from, moss where the roof stopped keeping rain out, roots through the floor nobody sweeps.

**Measured, same metric on both trees:**

| Family | n | Worst share | Median share | Fewest ids |
|---|--:|---|---|---|
| surface | 50 | 0.0% -> 4.2% | 16.5% -> 27.5% | 7 -> 8 |
| deepworks_archaeology | 11 | 2.0% -> 5.1% | 5.8% -> 14.0% | 5 -> 13 |
| court | 4 | 1.3% -> 2.7% | 4.0% -> 7.2% | 16 -> 20 |
| greatbole | 3 | 0.0% -> 1.1% | 0.0% -> 1.3% | 3 -> 5 |
| leyline | 5 | 0.0% -> 3.2% | 0.0% -> 5.9% | 7 -> 13 |
| pixie | 32 | 1.2% -> 1.3% | 14.4% -> 20.8% | 6 -> 6 |

Detail blocks 22,891 -> 50,646 over 303,605 -> 336,689 solids; pieces under a 4% share 29 -> 9,
and the nine are the tree, the canopy, the pixie saplings and the open-air amphitheatre, which are
mass by nature.

**Four things the pass found rather than added.**

1. **A pixie house had no way in.** `house_3`, the leaf-capped tree home, put its doorway three
   blocks off the ground with no stair anywhere in the piece — and it was the only one of the four
   variants to measure a flat zero while its siblings ran 22 to 58 per cent. It now has a ladder up
   the trunk that comes through the deck, an eave course, and a balcony rail; 0.0% -> 18.0%.
2. **The metric was blind to plants.** A pixie kitchen garden scored zero because none of it is
   made of stone. In a botanical-magic pack the crop row, the sapling and the two flowers at a
   doorstep ARE the human-scale residue layer, so `is_detail` counts them. The pixie median moved
   14.4% -> 20.8% on that correction alone, which says how badly the first metric read that set.
3. **Two checkers disagreed about one palette.** `minecraft:wall_torch` has no item, so
   `check_spawn_hub.py` S2 called it unregistered while `check_surface_works.py` NO_ITEM had
   exempted it since it was written. S2's itemless-block list gained the two wall-torch variants;
   the same proxy had already hidden `minecraft:water` once.
4. **Debris carpeted the halls.** The first run placed one fragment per broken wall top at a 0.45
   rate and covered every hall floor evenly — the same failure `Noise3` exists to prevent one level
   up. It now drops heaps: a tenth of the tops, three or four blocks each, tapering outward.

**Two structures also got the discovery-value work `THE_SURFACE.md` §6.1 asked for.** Every quarry
now carries stockpiles of Era I-IV bloom ore and half-worked seams that stop mid-vein, so a player
who follows a map to a rare quarry leaves with a haul and still cannot skip an era. Every crater
carries a severed ley run coming in over the rim on a fixed bearing and stopping short of the
centre with its last node still lit — an answer to "what was here" that is geometry rather than a
chest.

**Validation.** `tools/check_structure_detail.py` is new and holds a floor per family, each set
below what the set measures so it fires on regression; `--self-test` proves 6/6 of its checks fire
on corrupted input. All structure-relevant checkers pass: `check_structure_detail`,
`check_surface_works`, `check_spawn_hub` (S1-S13, including the pack-wide S11 attachment sweep over
all 105 pieces), `check_deep_archaeology`, `check_hollow_court`, `check_pixie_settlements`,
`check_pixie_runtime`, `check_funerary_set`, `check_worldgen`, `check_feature_order`, `check_spawn`.
Reproducibility: all five generators re-run and all 105 decompressed payloads are identical
(`gzip` stamps the header clock, so the files never are).

**Acceptance: static validated. No piece in this pass has been seen in a client or a fresh world.**
That is the next gate and it is open for all six families.

## Latest implementation — the Ley Conduit Node — 2026-09-08

The last piece of `LEY_LINE_CHANNEL_CORRIDORS.md` that a datapack could not express. B-88 shipped
the corridors and recorded the node as deliberately absent because no mod in the pack owned
worldgen blocks; the client took that decision, so `first_party_mods/alfheim_leyworks` now exists
as a second first-party Gradle mod — its own project, one dependency, Forge.

**Two blocks, and only the inert one is generated.** `ley_conduit_node_dormant` has no block
entity; `ley_conduit_node` ticks. Thousands of corridors carrying zero tickers is the point:
the 2026-09-07 field report ended on the game bringing the machine to a crawl. Converting one is a
shapeless craft consuming `alfheim:elementium_core`, our own Era V component, so lighting a
network is a mid-game investment and a node found early is loot rather than a tool.

**The pyramid rules are vanilla's geometry with our masonry and a different meaning.** Course *n*
is a (2n+1) square at depth *n* up to four courses; anything in `alfheim_leyworks:pyramid_base`
counts; tier chooses reach (tier x 12 blocks), not an effect. Projection runs six axes through air
and `alfheim_leyworks:beam_transmits`. The aura resolves `alfheim:leyline_presence` by
ResourceLocation, so a missing effect degrades to projection-without-buff rather than a hard link.

**The runtime caught what static checking could not.** The first jar shipped without
`pack.mcmeta`. Forge logs one line — `Missing metadata in pack mod:alfheim_leyworks` — and then
declines to load the mod's `data/` tree. Blocks still register, the jar still builds, and the
pyramid tag, the beam tag and the block's own drop all silently do nothing. Fixed, and the warning
is gone from the log.

**Measured, fresh world.** A live node over two complete courses reports `Tier: 2`; remove one
corner of the lower 5x5 and it reports `Tier: 1`. That single moving number proves the block
entity ticks, the courses are counted from the node downward, and the `pyramid_base` tag actually
loaded. `alfheim:leyline_corridors` locates 293 blocks from spawn; the four Deepworks structures
locate at 386, 402, 1,173 and 386 blocks, with `deepworks_headworks` and `deep_quarry` sharing
[352, ~, 160] — the co-location B-87 built and had never demonstrated. Hub unchanged: anchor 1,
crown 1, court 8, FTB ownership 100/100.

**A stale probe was also fixed.** `run_server.py` was asking `locate structure` for
`alfheim:deepworks_archaeology`, a structure *set*. The server answers "there is no structure with
type", which reads exactly like absence. It now asks for the three member structures by name.

**Acceptance: runtime-verified for registration, datapack load and the pyramid rules. Client
visual review is open** on the node model, its light level and the particle density.
Node-to-node retransmission — a node inside another's projection coming up to that tier — is
specified in the design and is not built; each node reads only its own pyramid. Nothing in the
game points a player at the activation recipe yet.

## Latest implementation — biome distribution and the three thin biomes — 2026-09-08

The question was whether a given seed reliably puts every biome within a day's travel. It is now
measured rather than argued: `run_server.py --run --survey` runs `locate biome` for all 25 biomes
from five spread origins in one world, and `read_biome_survey.py` pools worlds and reports median
and worst case. Worst case is the gate — a biome 300 blocks from spawn and 5,000 from a point 3 km
east is not reliably reachable, and a single probe from the origin would have called it fine.

**The survey overturned the obvious fix.** Widening a biome's temperature or humidity slice moved
its median and barely touched its worst case. Grouping the same numbers by continentalness showed
why: seven biomes shared `cont 0.15..0.45` and every one came back 1,810-2,583 blocks, while bands
holding one or two came back 452-1,450. Reaching the continentalness region dominates; finding the
right climate inside it does not. The nominal share of the climate cube predicts almost nothing
here — `infested_warren` holds 0.72% of it and measured 24% of a real world.

**So the midland was split, geographically rather than arbitrarily:** the cool and the wet sit
lower (`0.15..0.30` — decayed_mire, silverbark_wood, dreamwood_forest, golden_fields), the burnt
and the bright sit higher (`0.30..0.45` — ashen_grove, bloomfall_vale, scorchfell). No band now
carries more than four biomes. Eight tail-gated thresholds were also widened, and
`infested_warren` was relaxed from three tight axes at once.

**Measured, one seed, same five origins:** median of all worst cases 1,917 -> 1,629; biomes worse
than 2,000 blocks 9 of 19 -> 6 of 19; none ever unfound. Typical travel roughly halved for the
redistributed biomes — bloomfall_vale median 1,142 -> 362, ashen_grove 1,631 -> 712,
dreamwood_forest 973 -> 390, golden_fields 1,350 -> 676, scorchfell 601 -> 394.

**Pooled over two seeds and eight origins, all 19 land biomes are found from every origin, worst
case 2,715 blocks against a 3,000 target, medians 48-880.** The one biome that failed an earlier
pooled run (`infested_warren`, 3,192 from one origin) is 1,632 after being relaxed.

**The three thin biomes now have ground, standing evidence and air.** Ashen Grove gets ash drifts,
cinder boulders, charred gloambark stumps and dead scrub under falling white ash at 0.006.
Sundered Highlands gets scree, torn obsidian boulders and hardy tufts under wind-borne grit at
0.004. Hollow Marches gets dead ground of gloam livingrock and soul soil, hollow boulders,
standing witherwood and bone fields under the heaviest ash fall in the pack outside Scorchfell —
precipitation is off there, so the air has to carry the biome. `BIOME_INDEX.md` §5 now reports no
land biome without vegetal decoration.

**Topography is done with features, not density.** B-82 removed a climate-stamped terrain branch
because climate thresholds and LibX's nearest-biome result do not coincide, so full columns were
replaced inside neighbouring biomes and the seams read as chunky walls. Boulders, scree patches
and re-floored ground are bounded, local and support-aware; a density branch is none of those.

**Validation.** Sixteen static checkers pass, and the biome index regenerates clean. The climate
cube remains exactly covered — 43 disjoint bands, total measure 1.000000, no gaps and no overlaps.
Four survey worlds exited 0.

**Acceptance: survey-measured across two seeds and eight origins. Client visual review is open on
all three biomes and on the redistributed geography.** The remaining six biomes over 2,000 blocks
are bounded by continentalness region size (1,422 blocks); tightening further means raising
`CONT_SCALE`, which shrinks continents — a trade against "large enough to feel significant", and a
decision rather than a defect.

## Latest implementation — wooded shores and the climate-scale correction — 2026-09-08

Field item 7 asked for the wooded shorelines. Doing it surfaced the cause of item 8, which turns
out to be one line, and the two are recorded together in `BACKLOG.md` B-84.

**Three coastal biomes** sit on continentalness -0.15..0.03, the strip where the lake and ocean
floor rises out of the water. The band straddles the waterline on purpose: trees need a dry
heightmap column and zero water depth, so the belt places itself along whatever part of the band
is land in a given chunk rather than following a guessed radius. `tidewood_shore` is the warm
Gloambark coast, `mistbark_shore` the pale Hushbark one, and `sporebank_shore` carries all six
Feywild cap colours as a real canopy over a mycelium bed. The band is taken from
`mythicbotany:alfheim_lakes`, which measured 44% and 77% of two field worlds. Six new coastal
structures keep the manifest's two-per-biome rule.

**The climate scale was one constant applied to four different noises.** `CLIMATE_SCALE = 0.0625`
fed `minecraft:temperature` (base period 1024), `vegetation` (256), `ridge` (128) and
`badlands_surface` (64). Region size is base period / xz_scale, so the axes came out at 16,384,
4,096, 2,048 and 1,422 blocks respectively. Continentalness at 1.4 km always worked; temperature
at 16 km meant a world held roughly one thermal band. That is B-83's monoculture, and it is also
why two earlier attempts failed: both moved a threshold or widened the tails, when the defect was
the period. Each axis now gets the scale its own base period needs — temperature 4,096, humidity
2,048, weirdness 1,024 — preserving the nesting vanilla intends instead of flattening it.
Weirdness also gained the 1.8 amplification it was the only axis to lack, which matters because
28 of the layer's 42 bands split on it.

**Measured on one seed across three worlds.** `locate biome` from the origin: scorchfell and
bloomfall_vale went from **not found at all** to 2,458 and 2,234 blocks; ashen_grove 5,376 ->
1,810; hollow_marches 5,077 -> 1,697; tidewood_shore 6,324 -> 2,013. The four
continentalness-driven biomes (starved_reach, void_verge, decayed_mire, infested_warren) are
byte-identical across all three worlds, exactly as predicted since that axis was not touched.
Full table in B-84.

**Validation.** All sixteen static checkers pass, including `check_surface_works` W10, which
caught the three new biomes having no structures and drove the six coastal additions, and the new
`check_spawn_hub` S13, which asserts `has_greatbole` covers every biome the layer can place.
Three fresh worlds on the reported seed exited 0 with zero far-chunk errors; run C reported 5/5
hub ownership probes. The mushroom canopy is in the ground: 457 blue, 433 purple and 387 pink cap
sections plus 525 mycelium sections in run B's 529 chunks.

**Acceptance: fresh-world runtime measured for reachability and for the shore features; client
visual review pending on all three shores and the six coastal structures.** One caveat worth a
second seed: `sporebank_shore` is 56% of the 529 chunks around this seed's spawn, which is one
humidity region rather than a defect, but the three-way split is not yet shown to be balanced.

## Latest implementation — September 7 twelve-item field review — 2026-09-07

Eight of the twelve reported items have an authoritative repair; four are diagnosed and scoped.
Five of the eight turned out to be a different defect from the one the symptom named, so the
diagnosis is recorded with each rather than only the fix. Full table in `BACKLOG.md` B-83.

**Spawn complex.** The amphitheatre had exactly one carved approach — south, to the Greatbole —
while the three civic wings each drove a seven-wide processional spine into the intact outer
seating bank. `AISLES` is now the single authority for where the court opens, and all four
approaches are paved, cheeked and cleared last. Vertical alignment was already correct and was
verified rather than assumed: the amphitheatre sits at placement -3 with its floor at local y3 and
the wings at -5 with theirs at local y5, so both land on the surface datum. Separately,
`courtyard_detail` was placing rubble, moss, drums and vines at computed tier heights with no
regard for whether the tier survived its collapse roll or had been cut away by an aisle. Every
scatter is now support-aware, court seats are built down to the tier base course, and vines must
name a solid neighbour. Blocks hanging at y>=4 in the amphitheatre: 3 before, **0** after.
Detached vines: 3 of 21 before, **0** of 18 after.

**Claim envelope.** `HUB_RADIUS = 128` was a square centred on the tree, sized for a placement
probe that no longer exists. The complex is not centred on the tree — it runs Z -120..23 — so the
claim covered a large empty apron south of it. Replaced by an explicit rectangle derived from the
placed templates and snapped to chunks: X -80..79, Z -128..31. **Runtime validated:** the fresh
server reports `FTB ownership verified 100/100 chunks for alfheim_hub`, down from 289.

**Deep geology.** Cave faces were reading as per-block speckle for three independent reasons, all
now corrected: `inclusions` moved from firstOctave -4 to -6 with a second octave so it forms pods
rather than confetti; the lower strata palette went from five stones to three so its band edges
coincide with the upper scheme's and one stone carries through the contact; and the dithered
upper/lower blend band narrowed from 22 blocks (Y -30..-8, squarely at cave height) to 10.

**Deepworks.** Two separate faults. `ley_scars` kept an `xz_radius` of 16 and produced 20
`Detected setBlock in a far chunk` errors in the field session; the <=15 reach bound that was
written for the slag terraces now covers every formation. And the families were undiscoverable
rather than absent — a save scan found the one `elder_kings_tomb` start the 96-grid predicted
across the area explored. The grid is now 48/24, and the checker's magic `>=96/>=48` floors are
replaced by the geometric condition they stood in for: `separation * 16 > 2 * reach` (384 > 232).

**Biome identity.** Infested Warren and Decayed Mire had no identity features whatsoever. A probe
of the reported save measured the result: 566 of 876 Warren surface samples were plain grass block,
and the Mire was 82% the same. Together they are a third of that world. Six Alfheim-owned features
now carry both — root mats, fungal blooms and web snares for the Warren; mud flats, water pools
and deadfall for the Mire — plus standing dead dreamwood in each.

**Not a pack defect.** The session ended in a system crawl with a clean log and no crash. Distant
Horizons runs distant generation across nine dimensions with 14 threads at full duty cycle, at the
same thread priority as the game, with a 256-chunk LOD radius. It left 1,917 chunks at
`structure_starts` status beside the game's own 3,085 full chunks in thirteen minutes. The client
config is the user's to change and has not been touched.

**Loose blocks, everywhere they were.** `Piece.prune_orphans` now sweeps anything left touching
nothing on any of six faces; the decay, collapse and rubble passes in every generator remove blocks
without asking what rested on them. 47 orphans across the 44 surface pieces. Two findings were real
geometry faults and were repaired rather than swept: the Elder King's Tomb approach ran its
corbelled cornice at x=3 with the shell at x=1, so the whole band — 28 walls and 28 slabs — floated,
and both Faultwork suspended bridges carried their railings one block off a two-wide deck. The
cornice now rises off the shell; the decks are four wide, two lanes plus a slab under each railing.

**S11's first form was too strict and was narrowed on evidence.** It began by demanding solid
support directly below and flagged 36 pieces. Inspecting the six-neighbour context showed most were
corbels hanging under an overhang and stepped debris joined only on a diagonal — both authored ruin
geometry, which this project builds on purpose. Narrowed to "touches nothing on any of six faces",
which is never intentional, it flagged 15 pieces; all 15 are now clean.

**Validation.** Static: fifteen checkers pass, including the new `check_spawn_hub` S9 (claim
envelope derived from `assemble.mcfunction`), S10 (each wing seam clear) and S11/S12 (no unattached
blocks, no unsupported dressing), plus the generalised `<=15` formation reach in
`check_deep_formations` and the derived non-overlap condition in `check_deep_archaeology`.

Runtime, three fresh disposable worlds, all exit 0 and all with **zero far-chunk errors**:
`validation-field-0907e` (seed `alfheim`, 304s), `validation-fellhammer-0907` and
`validation-fellhammer-0907b` (the reported seed, 304s). The hub assembles, anchors and claims
100/100 chunks; `check_spawn_hub_claim` reports **5/5 ownership probes returning `alfheim_hub`** at
the centre and all four corners of the new envelope. In the seed-matched worlds the Warren's new
features are in the ground: across 1,056 Warren sections, 61 rooted dirt, 58 podzol, 57 coarse dirt,
37 brown mushroom, 23 cobweb and 4 red mushroom.

Two validator defects were found and fixed while doing this, both of which had made their checks
unable to pass: `run_server.py` still probed the retired ±128 claim corners, and
`check_spawn_hub_claim` expected `Location: <dim> [x, z]` when FTB Chunks prints
`Location: [<dim>:x:z]`. The probe list is now derived from the generator and the parser matches
the real output; the self-test passes on all four fixtures.

**Acceptance: item 3 runtime validated (5/5 probes); items 1, 5, 12 runtime validated in part;
items 4, 9, 10 static validated with dedicated invariants; item 2 registered and parsed but its
biome lies 320 blocks outside the test radius, so its three features have not been observed
placing. Client visual review is open on all of them.** Items 6, 7 and 8 are diagnosed and scoped,
not built.

## Latest implementation — terrain smoothing and clean Void reset — 2026-09-07

The September 7 screenshots traced the general terrain regression to a climate-stamped Y=191 Hills
plateau. Because climate thresholds and LibX's nearest-biome result do not coincide exactly, that
branch replaced full columns inside neighboring Plains, Silverbark and Starved Reach and produced
the reported chunky walls. It is removed. Ordinary upper terrain now exactly preserves
MythicBotany's continuous base density, guarded by a dedicated static invariant.

The Void is reset to a quieter baseline: one continuous low-amplitude shore/Verge blend, then clean
air beyond the cliff. Independent pressure slabs, fault needles, prism cores, root ribs, burial beds
and terminal splinters no longer contribute to final density. Their future return must be through
bounded, support-aware configured features. The aquifer dry shoulder begins at continentalness
-0.58, using the exact unshifted-in-context terrain field, and the basal ten-block guard handles
Minecraft's global fluid picker before surface rules remove its temporary stone.

Acceptance is **fresh-world runtime validated; new-client visual review pending**. Disposable world
`void-margin-20260907-210920` exited 0 and audited 170 columns: all seven Void classifications had
zero fluid blocks and every continentalness-below--0.94 column had zero playable far-field solids.
The three Deep controls remained populated/wet as expected. All 126 Void/Deep material blocks and
126 recipes resolved, and the static terrain/geology/worldgen/reproducibility suites pass.

## Latest implementation — September 7 field repair — 2026-09-07

Fresh logs confirmed 241 `Detected setBlock in a far chunk` errors, all from the generated
Deepworks Slag Terraces. The patch radius plus random offset could reach 25 blocks; the generator
now caps total reach at 15 and its checker enforces that invariant. No KubeJS/EntityJS load error,
feature-order cycle, or Java crash exception was present in the supplied current logs; the stdout
session did end with code 1, so extended fresh-world runtime stability remains unaccepted.

The Greatbole/royal complex is rebuilt around X=0/Z=0: 112-block custom Elder-wood
tree, 20-block embed, eight descending root buttresses, level gate-to-Court procession, and three
new civic/palace wings. Seven templates totaling 95,354 source blocks are directly assembled on
one vertical terrain datum. The spawn-claim generator now owns the proven FTB API implementation,
including `claim(..., false)`, per-chunk read-back, persistence, sync and bounded retries over the
128-block envelope. Fresh disposable world `validation-field-repair-0907d` placed every one of the
seven pieces, found exactly one baked base marker, one crown marker and eight Court elves, and
verified all 289 required chunks as owned by `alfheim_hub`; independent `ftbchunks info` probes at
the centre and four corners agreed. `check_spawn_hub` reports zero problems. Fresh-client geometry,
ordinary-player edit denial and restart persistence remain pending.

All three Deep archaeology families now share one 96/48 random-spread grid, making their large
spawn zones mutually exclusive. Seven Elder Grave Doors have full nine-by-eight corridor-closing
masonry bays. The decoded-NBT/generator checker passes. Infectious' 99 natural spawn modifiers are
overridden at their original resource IDs to `#minecraft:is_overworld`, matching the mod's Java
predicate and removing impossible Alfheim pointers. Wild Elves now include Dreamwood Forest at
weight 12. Alfheim Hills' climate-owned density branch transitions terrain at Y=191–194. Each has
a passing dedicated static checker; all require fresh-world/client observation.

## Latest implementation — Deepworks Section 8 formations — 2026-09-07

D6 now decorates the existing colossal-cavern field with four terrain-aware formation systems.
Crystal chandeliers, ley scars and mineral columns each have Fire, Water, Earth, Air, Shadow and
Light variants derived from the existing crystal manifest. Chandeliers search real ceilings and
hang multiple 5–22-block branches; scars form broad fused floor bands; clustered mineral shafts
rise 12–36 blocks and truncate at cave roofs while carrying native Bloom inclusions. Slag terraces
first find basal lava, then spread the established lava → Magmatic → Cracked → ordinary Livingrock
grammar across nearby shelves. None of the features carves a substitute cavern.

Acceptance is **fresh-world load and natural-generation validated; client visual acceptance
pending**. Generator closure and the dedicated formation checker pass, as do full worldgen
resolution and global feature ordering. The first Forge run caught Minecraft 1.20.1's 32-block
`environment_scan` codec maximum; the generator and checker were corrected. The clean retry reached
Done, generated a new world and exited 0. Its 2,025 Alfheim chunks naturally contain Mana-glass from
four alignments, proving the new formation path executed without direct placement. Frequency,
silhouette, lava-shore readability and traversal still require client review before production
admission. D7 archaeology—Quarries, Tombs and Faultworks—remains next.

## Active implementation — September 5 field-review corrections

The durable plan and active work log are
`alfheim_reclaimed_design/FIELD_REVIEW_STAGE_2026-09-05.md` (B-80). Field evidence establishes
three visual corrections and one critical runtime failure: ocean vegetation is over-dense, the
ocean/Verge boundary is a vertical density cut, Scorchfell walls are repetitive, and New World
Gamma never generated a Great Bole or baked hub anchor despite 1,200 seconds of force-loading.

Work is ordered Great Bole → Scorchfell/ocean → custom elf runtime test → Void littoral prototype.
The stone-library texture pass is now statically implemented as recorded below; the NPC-art pass remains
deliberately deferred. The four seasonal pixie sky-island villages are now direct-assembly runtime-proven. Natural
giant-tree placement was declined because it would intrinsically alter
the world's silhouette. Sparse Jaffa orange and seasonal Feywild accents are now statically implemented.
I9 has a static repair: the carpet, balustrade and wall sconce no longer contain the reported same-facing
coplanar geometry, and the apparent pants/book offsets were identified as neighbouring atlas fragments crossing
cell cuts. The shared generator now removes only detached boundary spill before centering all 480 icons; rebuilt
review sheets pass, while restarted-client signoff remains. I11 now gives all twelve independent Knight Quest
creatures one climate-matched hostile-ruin encounter through bounded vanilla spawner NBT; no repeating spawn
script was added. Starfall precipitation is accepted and will not be changed.

Newly queued after the ore pass: multiple forest identities; two dense wooded-shoreline environments around
the large Alfheim Ocean footprint; climate-matched Feywild mushrooms across every non-Void biome; a custom
Bramble family using static behavior rather than repeating growth code; and additional local-stone crystal/
geode features for all six Void biomes. The Void's no-living-growth rule remains absolute.

I1 is runtime-proven and I2–I5 have a static implementation pass. Hub creation now checks a bounded
solid-surface lattice, assembles the trunk/crown/court/base exactly once, verifies its baked anchor,
retries only an explicit failure and reopens provisional worlds;
the natural duplicate placement source is removed. Scorchfell uses its native five-stone family at the
surface with 1-in-36 lava pools and six seep attempts. Alfheim Ocean has sparse independent vegetation
and its player-facing name. The Void shore blends continuously into a lower noisy shelf. The faulting
wood-elf cosmetic handler is deleted rather than replaced with more runtime logic.

Deep regeneration/invariants, worldgen, feature order, hub and wildlife static checks pass. After the
user cleared Java, `validation-hub-lattice-proof-0906` proved all four templates succeeded, one baked
anchor and one crown existed, the hub finalized on attempt one, and all eight tagged court NPCs were
present in the saved entity data. Client visual acceptance for Scorchfell/ocean/Void shore and natural
wild-elf spawn observation remain pending. Details and exact files are in the B-80 field-review log.

I8 uses six climate-specific biome modifiers and Alfheim-owned placed-feature wrappers that exactly mirror
Jaffabricate/Feywild rarity and survival rules. This keeps the additions sparse and eliminates the feature-
order cycles produced by directly sharing their vanilla-biome placed-feature identities. The dedicated tree
checker, full worldgen resolver and global feature-order checker pass; fresh-client visual acceptance remains.

I10 is runtime smoke-proven. Elementium uses size 12/count 6, Dragonstone size 7/count 2, and climate-limited
Fey Gem size 6/count 3. Each has 42 Deep/Void host variants with preserved source loot—126 startup-registered
blocks and no recurring hook. The fresh validation server exited 0; 639 full Alfheim chunks contain 26
distinct hosted IDs across all three ore families. Quantitative density and client appearance remain open.

I11 is runtime load-smoke-proven. Twelve hostile Surface Works templates contain one Knight Quest encounter
each, divided among skirmish, swarm and elite cooldown/population profiles. The checker validates exact NBT,
entity coverage, placement and protected-biome exclusions; all self-tests fire. Disposable world
`validation-knight-encounters-0906` reached Done and exited 0 with 17/17 startup and 26/26 server scripts clean.
Actual ruin placement, spawner activation and combat balance remain unclaimed client/gameplay checks.

I7 is direct-assembly runtime-proven. Four fixed-height, one-step jigsaw hamlets provide spring,
summer, autumn and winter pixies with culture-specific dew-well centres, three miniature houses,
functional vanilla crop gardens and complete matching Feywild trees on tapered 33×33 islands. A
clean Forge run directly placed all four at Y 208, and the saved-world audit found every required
piece, no residual jigsaw blocks and exactly one correct bounded pixie spawner beneath each centre.
Natural random placement is not yet claimed: Continuity Works auto-enrols registered structures in
its 500-block exclusion system, so a fresh-world census must measure actual rarity and clearance.
Spawner activation/escape and client silhouette, scale and fall-safety review also remain open.

**Role:** live operational state. Distinct from `BACKLOG.md`, which holds intent.

## Latest implementation — feature-bound Void Margin geology — 2026-09-06

The six Void biomes no longer share one fragment silhouette painted with a generic three-stone
noise wash. Their density branches now express separate landform vocabularies: Shatterfields has
pressure slabs and upright fault needles, Prism Drift has tall cores with bounded split seams,
Rootfall has shelves carried by elongated fossil ribs, and Sepulchral Reach has broad memorial
shelves with competent burial backing. Verge and Starless retain their distinct longitudinal jobs.

`void_catalog.json` schema 3 binds all eighteen stones to named roles. Broad surface rules cover
only the appropriate cap, shell, seam, core or backing. Signature materials such as Veilstone and
Epitaph remain formation-only. Rootfossil is selected by the same `root_ribs` noise that shapes the
roots, Resinshale forms its narrow halo, and Hollowheart remains the vanished-trunk host. The placed
Root Apron is now a set of 7–18-block downward fossil columns inside existing Void-natural support,
not another surface block pile.

Acceptance is **static validated and Forge load-smoke-proven; client visual acceptance pending**.
Generator closure, the new geology invariant checker and its four mutation tests, worldgen
resolution, feature order and complete structure-support checks pass. A fresh server generated all
audit sites and accepted the new codecs. Its full dry/far-field audit still failed with 91 errors
from the older aquifer spatial leak. Testing the opposite floodedness polarity increased that to
137 errors, so it was reverted. That water defect remains separate from this geology pass. Existing
chunks do not change.

## Latest implementation — stone textures and Continuity CTM — 2026-09-06

The uploaded texture archive is installed at its repository-relative destinations. It replaces
placeholder/recoloured art with native 32×32 material grammars for all 24 Deep and 18 Void stone
families, four texture variants per natural/polished/brick/carved form, four Y rotations for every
full cube, and transparent mana-glass/crystal assets.

The archive's 1,974 connected tiles were renderer-neutral source assets. The installed renderer is
Continuity 3.0.0 for Forge, so `tools/gen_connected_palette.py` now also emits 42 OptiFine-format
rules and 1,974 runtime tiles in Continuity's historical 0..46 order. The mapping is verified
against the installed jar rather than assuming that the source generator's compact state order is
the same as Continuity's sprite order.

Acceptance is **static validated; restarted-client visual acceptance pending**.
`tools/check_material_textures.py`, `tools/check_deepworks.py`,
`tools/check_connected_palette.py`, crystal regeneration, JSON parsing and asset-reference closure
pass. The uploaded PNGs were pixel-identical to their generator outputs but encoded by a different
Pillow build; local regeneration normalized compression without changing any pixels and restored
byte-for-byte generator closure. No player save or worldgen configuration was changed.

## Latest implementation — terrain-identity field review — 2026-09-05

The user's fourteen-point screenshot review is implemented for newly generated chunks. The Great
Bole has an eight-block root embed and a broad processional aisle through the stone circle. Frog
and toad heads, deer tails and antlers were separated to remove the reported coplanar geometry.

Deep geology is now biome-specific across sixteen non-Void biomes, with five-stone palettes,
upper/lower permutations, independent inclusions and a noisy y=8..42 surface transition. All 42
natural Deep/Void host stones have matching variants for all twelve blooms (504 new ore blocks).
Liquid Bifrost is 1-in-24 rather than 1-in-40 and includes the new ocean.

`alfheim:alfheim_ocean` is live with coral, seagrass, kelp, sea pickles, vanilla aquatic life and
Alfheim sea predators. Stormwreck and Tidal Arcade make it the twenty-second biome in the complete
44-structure Surface Works catalogue. Scorchfell now exposes volcanic materials/lava features;
Starved Reach exposes snow and ice and receives sparse glacial formations. Void precipitation
remains disabled and is represented by ambient End-rod star motes.

The Void density branch now uses 3-D fragment, fracture and shape fields, noisy Verge relief and
a narrow intact shore. It produces tapered, undercut floating masses instead of height-windowed
vertical extrusions. Six biome material formations and ten new Void sibling landmarks are live;
all twelve Void structures declare terrain-owned support and use no terrain adaptation. The old
Verge Spire self-generated island was removed.

Acceptance is **static complete; fresh-world/client acceptance pending**. Wildlife/drop equality,
spawn-hub, Deep, feature-order, climate/worldgen, Surface Works and complete Void-support checks
all pass. Forge loaded 16/16 startup scripts, including the expanded registry, with zero KubeJS
startup errors/warnings. The first fresh-world harness attempt reached that point but filesystem
access failed before datapack load. A permitted retry found an existing dedicated server process
holding the world lock, so it was not interrupted. Next exact action: restart that server or close
it, run a clean fresh world, then traverse the Bole/Court, ocean, three Deep sites and several
separated Void margins. Existing chunks do not change.

## Current priority — the Deep terrain — 2026-09-05

The next development pass is implemented: natural Livingrock masses, a dedicated deep cavern
field, initial basal lava basins and richer native deep-bloom deposits. `DEEP_TERRAIN.md` is the
design record; `tools/gen_deep_terrain.py` and `tools/deepworks_terrain.json` own this work.
The existing biome generator now composes the Deep only into its non-Void density branch.
The original Void density/aquifer branches, upper density, bedrock rule and unrelated settings
are preserved. New natural stone stops at y=23 and is excluded from the Void Verge biome.

Acceptance: **runtime validated for terrain generation and sampled geometry/ore contracts**.
Two isolated fresh worlds, same seed and sites, each sampled 112,230 actual blocks across six
sections. Both harness runs exited 0 with audit=True:

- Treatment: `server/deep-terrain-treatment-20260905-130352.log`.
- Baseline: `server/deep-terrain-baseline-20260905-130620.log`.
- Evidence: `tools/deep_terrain_summary.json`, complete treatment/baseline sample JSONs,
  and `tools/deep_terrain_sections.png`.

Measured open spans reach approximately 216 blocks, heights 68–84 blocks and lava spans 164 blocks.
Cave-air samples increased 2,085 → 29,848; lava 279 → 1,179; ore samples 476 → 586 despite much
less solid rock. Ore density in sampled solids increased 6.94 → 14.60 per thousand. Fifteen
natural library stones appeared in these sections. Upper density samples match; bottom-block
differences are zero; no sampled library stone appears above y=23. Three heightmap differences
are Gloambark leaves at y=72..75, not changed ground. These are targeted-site measurements, not
an unbiased census of world-wide cavern frequency or proof of a whole 3D complex's dimensions.

All 19 terrain files reproduce; feature ordering reports zero cycles; material checks still pass.
KubeJS startup/server logs have zero errors in the final two runs. Existing third-party console
diagnostics remain. The temporary baseline overrides and test probe were removed from the server
mirror after measurement; it again matches the authoritative treatment worldgen.

The probe initially deadlocked while generating chunks inside Rhino's lock and waiting for EntityJS
wildlife callbacks. The repaired harness requests chunks through console commands outside JS and
samples only loaded chunks. `tools/deep_terrain_threads.txt` retains the diagnostic evidence.

**Next exact action:** inspect/traverse the three sites in a client, then refine the sharp upper
geological contact and lava shores; build crystal chandeliers, ley scars and mineral columns;
finally add supported Quarries, Tombs and Faultworks. Review sites (x,z): (-864,-576),
(1824,-1632), (-2016,-960), around y=-20 in the retained treatment test world. Terrain affects
new chunks only. No player save was modified. No archaeology or bespoke formation generator is
claimed by this pass, and full client/gameplay acceptance remains pending.

## Livingrock material foundation — 2026-09-05

The user resumed the Deep and requested substantially more stones, including non-magmatic
palettes useful throughout Alfheim. This takes priority over the historical next actions below.
Design: `alfheim_reclaimed_design/LIVINGROCK_LIBRARY.md`; backlog B-78.

Implemented: 24 Livingrock families × 7 forms = 168 blocks, six aligned mana-glasses and slag;
175 blocks total, 103 textures and 174 decorative stonecutting recipes. Nineteen families are
non-volcanic. Natural, polished, brick, carved, slab, stair and wall forms all exist.
Authoritative generator: `tools/gen_deepworks.py`; source: `tools/deepworks_manifest.json`.
Generated startup: `kubejs/startup_scripts/20_deepworks.js`. The review atlas is
`tools/deepworks_review.png`.

Static validation passes: `tools/check_deepworks.py` verifies all 764 generated files byte-for-byte,
unique registration, texture/model contracts and recipe closure. `tools/check_feature_order.py`
reports 303 biomes and zero cycles. No density function, natural deposit feature, broad vanilla
replacement tag, player save or existing structure template was changed by this pass.

Acceptance: **runtime validated for the material contract; client visual acceptance pending**.
Evidence: `server/deepworks-console-20260905-071446.log`, with
`[DEEP AUDIT] COMPLETE blocks=175 recipes=174 loot=374 errors=0`.
All blocks and items exist, all blocks place, intended light levels and shape properties match,
all 174 recipes have correct inputs/results/counts, and all 374 loaded loot evaluations pass.
The generator compensates for the float-truncation defect found in the preceding run.
KubeJS startup and server logs have zero errors. The overall console still contains pre-existing
Moonlight/Connector, client-dist and Iron's Spellbooks loot diagnostics; the missing Feywild
Feysythia ingredient warning also predates this work, confirmed in the prior Fey validation log.
This is not a claim that the entire pack's console is clean.

**Next exact action:** client review of the 175-block library (restart required), especially
transparent glass adjacent to lava, stair/wall connections and hand-mining. Then D3/D4: controlled
natural stone deposits and the masked colossal-cavern volume. Lava basins, ore concentration,
crystal formations and supported Quarries/Tombs/Faultworks remain subsequent implementation.
The revised design carries the full cave objective; these terrain features are not yet built.

The following dated sections record earlier work and remain valid for their own scopes.
**Updated:** 2026-09-05. The Fey wildlife, elf variants and drops are runtime validated as
specified below. The zombie work is parked at the user's request. The preceding state was
2026-09-04, after repairing the boot crash in the zombie habitat spawn gate — the
pack boots again, verified by a full headless server run. The Guild Regalia asset build below is
unchanged by that repair. All 63 items now have generated
textures, models, startup registrations and slot tags. Acceptance: **static validated**.
Effects, recipes, profession proof, class gating and per-player slot behavior remain pending.
The six-class Reclaimed Armory remains runtime validated. Earlier session entries below are
historical; their claims that the Regalia has no registrations are superseded by this build.

## Fey wildlife and useful drops — 2026-09-05

User priority: continue the Fey creatures, especially the elf variants and creature drops;
leave the zombie work alone. B-77, design: `alfheim_reclaimed_design/FEY_WILDLIFE.md`.

- 18 creatures: whitetail and celestial does/bucks, six frogs, two pig-sized toads, three
  aquatic predators and three hostile elf variants. All 53 intended habitats resolve at runtime.
- Wild elves are fast melee fighters; savage elves have a leap and stronger knockback;
  demonic elves have fire immunity, armor and knockback resistance. Court elves are unchanged.
- 13 new supply/food items, 18 individual loot tables, 14 useful processing/cooking recipes,
  and one 18-page optional Fey Bestiary chapter. Rare trophies are not progression gates.
- Cube UVs now scale with face dimensions to reduce inconsistent texture density.

Evidence: `python tools/run_fey_validation.py` exited 0 with audit=True;
`server/fey-console-20260905-064250.log`. 18/18 entity constructions and dimensions/health,
53/53 habitats, 13/13 items, 14/14 recipes, 4,608 loot evaluations; zero audit errors.
Knightlib small/great essence additions remain active. KubeJS startup/server logs: zero errors.
Static checks pass; all 3,551 shipping files checked stayed byte-identical after regeneration.

Acceptance is runtime validation of registration, habitat tables and loot, not client visual or
combat acceptance. **Next exact action:** restart the client, inspect the three elf attack styles
and celestial portal rendering, sample natural encounters and make the Mana Pool and venison
recipes. Native Husbandry breeding and the Guild Regalia effect slice remain separate work.

## Boot restored — the zombie habitat spawn gate — 2026-09-04

The pack had not booted since the fey-wildlife and zombie-habitat generation run. Diagnosis and
repair are recorded in `CHANGELOG.md` 0.13.1-design; the surviving design gap is `BACKLOG.md` B-76.

Authoritative change: `kubejs/startup_scripts/09_zombie_habitats.js` — the 99-entry
`event.or(...)` loop over `kubejs/zombie_spawn_gates.json` removed. `server/kubejs/` is a run-time
mirror written by `tools/run_server.py`, not a second source; it re-synced on the verifying run.

Evidence:

- `python tools/run_server.py --run` → exit 0 after 315.1 s, `server/console-20260904-174418.log`.
- `Loaded 12/12 KubeJS startup scripts in 1.232 s with 0 errors and 0 warnings`.
- `alfheim validation: startup reached`; world generated; command script ran; clean stop.
- 0 `[ERROR]` lines in `server/logs/kubejs/startup.log`, `.../server.log`, `server/logs/latest.log`.
- No crash report written; newest remains `crash-2026-09-04_16.50.56-fml.txt`, from before the fix.
- The 15 `zombie_variants` ids verified present in
  `server/local/kubejs/export/registries/entity_type.json` before the edit.

Not claimed: that any zombie variant actually spawns. The placements register; no spawn was
observed. `kubejs/zombie_spawn_gates.json` is retained as generator evidence and is now unconsumed.

**Next exact action:** the same generation run's fey wildlife — 18 `alfheim:` species in
`08_fey_wildlife.js`, from `tools/gen_fey_wildlife.py`, with `tools/run_fey_validation.py`
alongside it — is undocumented in both `CHANGELOG.md` and this file. Reconcile it: confirm the 18
registrations and their habitats at runtime, then record acceptance, before starting new work.

---

## Guild Regalia asset build — 2026-09-04

Per the user's direction, presentation was brought forward from phase 6: derive the suite from
existing textures using PIL. `tools/gen_curios.py` reads the catalog and emits 36 class pieces
and 27 profession cuffs, in Apprentice/Guild/Master ranks. Vanilla eye, shard and lead textures
supply the forms; existing Alfheim frame materials supply the rank overlays. Signet openings are
literal transparency and all overlays stay inside the original silhouette.

`tools/curios_review.png` shows every item grouped by family and owner. Husbandry and Salvaging
colors were separated, guild brightness was adjusted to preserve the master step, and the sheet
now uses full labels, transparency backgrounds and integer 4x enlargement.

Evidence:

- `check_curios.py`: 0 problems; 18/18 fault-injection cases fire across C1–C16.
- 63 RGBA 16x16 textures, 63 models, 63 declarations; ring 18, necklace 9, charm 9, bracelet 27.
- 133 Curio outputs byte-identical across regeneration, including the review sheet and manifest.
- Shared `item_textures.py` extraction: all 83 earlier textures pixel-identical to the preserved
  pre-refactor generator; all 167 earlier item assets/registration byte-identical after rerunning.
- Era, surface, spawn-hub, worldgen and Hollow Court checks: 0 problems. Feature ordering: 0 cycles.
  Spawn-hub validation also parsed 37 KubeJS scripts with 0 syntax errors.
- Coverage is **not a clean pass**: 66 existing per-item gaps, 1 process gap, 14 unscoped steps,
  0 method-ordering violations. This asset-only build adds no recipes or quest requirements.

**Next exact action:** boot with these startup registrations and verify all 63 items in JEI;
probe ring/necklace/charm/bracelet capacities with a real player, then implement the Warrior/Mining
effect slice. Registration parsing and item tags do not prove equipping works or enforce class and
profession limits. A full client restart is needed to load new startup items.

---

## Reconciliation — the Guild Regalia numbers hold, four documents did not — 2026-09-04

No new gameplay content. This pass re-derived every claim from the planning pass against the
actual environment, per AI Project Manager §6, and repaired what disagreed.

### Reproduced, exactly

| Command | Observed | Exit |
|---|---|---|
| `python tools/build_curio_plan.py` | 6 class suites, 9 profession suites, 63 planned items, 46 installed functional anchors, 0 missing IDs | 0 |
| `python tools/build_curio_inventory.py` | 147 wearable IDs (114 functional, 33 cosmetic), 19 slot definitions, 14 live slot types | 0 |

The plan generator is **deterministic**: `SUITE_MATRIX.md` and `curio_suite_catalog.json` are
byte-identical across reruns by `sha256sum -c`. The "nothing is registered" claim is verified by
absence, not by assertion — `grep` over `kubejs/` returns **0** `curios:` references and **0**
signet/emblem/cuff/torque ids.

Full checker suite after the document edits: `check_era --all` 0 · `check_surface_works` 0 ·
`check_spawn_hub` 0 · `check_worldgen` 0 · `check_feature_order` 0 cycles · `check_coverage` 0 ·
`check_hollow_court` 0.

### Four documents disagreed with reality

| Document | Was | Now |
|---|---|---|
| `BACKLOG.md` | **no Curios item at all** — the pass existed in this file and in `CHANGELOG.md`, but nothing carried its intent or its next action | B-74, with the reproduction evidence and the accept criteria |
| `CHANGELOG.md` | two entries numbered `0.10.0-design` and two numbered `0.9.0-design`, all dated 2026-09-04 | surface → `0.12.0`, canopy → `0.11.0`; the Regalia keeps `0.10.0` and the Armory `0.9.0` |
| `README.md` | "Alfheim *is* the Overworld" (struck 2026-09-02), 95 mods, "boots to title screen", next action B-02/B-12 — B-12 closed | current premise, 83 jars, levels 8–9 passed, next action B-74 and the Bifrost quests |
| `INSTRUCTIONS.md` | 97 mods, pack version `0.2.0-design` | 83 jars counted on disk, `0.12.0-design` |

**The backlog gap is the one that mattered.** A planning pass whose only record is a narrative
section cannot be picked up by the next session as eligible work — §11 names "ending without a next
exact action" as a defect, and that is what had happened.

**The mod count is now a disk count, deliberately.** `mods/` holds 83 jars. Neither 97 nor 95 is
reproducible, and `logs/latest.log` does not print a loaded-mod total (its 149 "Found mod file"
lines include jar-in-jar libraries). `INSTRUCTIONS.md` now says so rather than quoting a number
nothing verifies.

### Next exact action

Unchanged by this pass, and now recorded in B-74: run the live per-player Curios slot/capacity
probe — the 14 live slot types came from a headless run with no player entity, so nothing yet
proves how many `ring` slots a real player has — then build the Warrior signet with its Greatbole
Torque anchor and all three Mining cuff ranks. Ahead of it in the queue sits the Liquid Bifrost
quest gap, which is a coverage-standard violation already recorded above.

---

## The surface has thirty-two things in it, and a shop that sells directions — 2026-09-04

**User:** *"a small subchapter of FTB quests that is explorers maps that are repeatable purchase
actions ... And I want at least two explorable interesting structures per Biome that we have.
These should be surface features castles ruined castles large craters a large quarry mine and so
on."*

Before this the surface held **one** structure of ours, the Greatbole at the origin, plus
MythicBotany's cottages. Sixteen biomes, one landmark. Design record:
`alfheim_reclaimed_design/THE_SURFACE.md`. B-73.

### Two deliverables

**Thirty-two structures**, exactly two per biome, from ten parametric archetypes — castle,
quarry, crater, tower, hall, aqueduct, span, barrow, wreck, shrine — across seven palettes.
Every biome gets one thing that was *built* and one thing that was *done to the land*.

**The Cartographer**, a new campaign chapter: ten repeatable purchases, one per archetype, paid
in petals and livingrock. Per TYPE, not per structure, which is what was asked for and what
`#minecraft:village` already does for five village types.

### The mechanisms, all read out of the jars rather than remembered

| | |
|---|---|
| A crater can exist | A template position set to `minecraft:air` **is placed** and overwrites terrain; a position never set is absent from the template and leaves terrain alone. Craters and quarries carve by writing air. |
| A map is a search, not an item | `minecraft:exploration_map` is a loot *function* that reads `LootContextParams.ORIGIN`. FTB Quests has nowhere to put a loot function, so the reward runs `/loot give {p} loot ...` and the command runs the table. `/loot ... loot <table>` builds its params with ORIGIN set to the source position and the **chest** param set — read out of `afd.class` in the 1.20.1 client jar. |
| `destination` takes no `#` | `readStructure` does `TagKey.create(Registries.STRUCTURE, new ResourceLocation(s))` on the raw string (`eat$b.class`). |
| Nobody buys by accident | `ItemTask.submitItemsOnInventoryChange()` returns `!consumesResources()`. A consuming task is never auto-submitted; the player must click to pay. |
| 1.20.1 map icons | `MapDecoration.Type` here has no `jungle_temple` and no `swamp_hut`. The legal set was read off `dyl$a.class`. |

### The bug class this pass added a counter for

**`Piece.set()` silently drops anything outside the piece.** The wreck's mast was twelve blocks
tall in a box with eight blocks of headroom; the Bloomfall Shrine's dome overshot its lid by
four courses; the Rotwood Barrow's outer menhirs stood at x=32 in a 32-wide box. All three
generated, validated and shipped a structure with a piece missing. `Piece` now counts every
dropped `set()` and the generator prints the ratio. Worst is now **0.02** — the legitimate
overdraw of scanning a bounding square to draw a circle.

The tower's spiral had the same shape of defect and no counter would have caught it: it stepped
a fixed twelfth of a turn per stair, which around a radius-4 ring puts consecutive treads two
blocks apart. A decorative helix nobody can climb. Rebuilt by walking the ring at fine angular
resolution, keeping each integer cell once and rising one block per cell; proven adjacent
(Chebyshev 1, including the wrap) for all three towers.

### One shared Piece, not two

`gen_surface_works.py` needed the same NBT builder `gen_spawn_hub.py` had. Copying it would
have been a parallel implementation of the primitive that decides whether a `.nbt` is placeable
at all, so it was extracted to `tools/structure_nbt.py` and both import it. Proven neutral by
regenerating the four spawn-hub pieces and comparing **decompressed** payloads — `gzip.compress`
stamps the current time into its header, so comparing the files directly proves nothing.

### check_era.py's E11 guard was wrong, and was repaired rather than worked around

E11 asks which generators write `chapter_groups.snbt`, and separated a write from a note by
testing whether the line started with `#`. `gen_cartographer.py`'s header says, correctly, that
it does **not** touch that file — and was reported as a second writer for saying so. The guard
now parses the module and looks only at non-docstring string literals, which is strictly more
precise; proven still to fire against a synthetic second writer.

### Validation

Fourteen checks in `tools/check_surface_works.py`, **all eleven self-tests fire** on synthetic
bad input. Full suite after the change: `check_surface_works` 0 · `check_spawn_hub` 0 ·
`check_worldgen` 0 · `check_feature_order` 0 cycles · `check_coverage` 0 · `check_hollow_court`
0 · `check_era --all` 0.

**Nothing here has been seen in a world.** `static validated`, not runtime. THE_SURFACE.md §7.1
lists what pass 1 cannot tell you.

### Noted, not mine

Regenerating the spawn hub flushed a pending change that was sitting on disk: `amphitheatre.nbt`
gained `DataSkinSwap` on its eight court entities, the output of `gen_court_skins.py` work that
landed in `gen_spawn_hub.py` at 08:26 and had never been regenerated. Verified to be **exactly**
that and nothing else — the two files are identical once `DataSkinSwap` is removed.

---

## Spawn hub — runtime-proven — 2026-09-04

The Greatbole generates, its canopy survives placement, and the world spawn is inside its gate
chamber. Last headless run: 298s, exit 0, no error in the `alfheim:` namespace.

```
The nearest alfheim:greatbole is at [96, ~, -96] (135 blocks away)
crown probe   [72.5d, 157.0d, -71.5d]     canopy generated
hub anchor    [78.5d,  66.0d, -71.5d]     gate chamber
Magister Velrous                          court branch placed
[Alfheim] world hub anchored to the Greatbole gate chamber.
```

The tree is 112 blocks against a budget of 116 — `max_distance_from_center` 116 plus the
12-block `beard_thin` margin makes 128, the vanilla ceiling. **Do not raise either number
without re-running `check_spawn_hub.py`; S9 and S5 both bind here.**

The 135-block displacement is the *designed* fallback, not a defect: the validation seed's
origin is `mythicbotany:alfheim_lakes`, one of the two biomes deliberately outside
`#alfheim:has_greatbole`. On a seed whose origin is buildable the tree pins to chunk `0,0`.
Because the spawn anchor is baked into `greatbole/base.nbt` and the claim is 192 blocks, neither
outcome needs the tree to be at the origin.

---

## Liquid Bifrost — integrated — 2026-09-04

Fluid, four-tier chain, six conversions into five magic systems, and the Era VII renewable
route all load clean on a headless run. Design record:
`alfheim_reclaimed_design/LIQUID_BIFROST.md`.

Integration completed this pass: derived art and models for all four tiers (they had been
rendering as the missing-texture checkerboard), `#alfheim:bifrost` and
`#alfheim:bifrost_distilled` item tags, era-scoped recipe files so coverage can see the chain,
**nine quests** across Eras II/III/VII, and a 7-entry Compendium chapter.

Coverage: per-item gap 74 → 65, every bifrost output covered, 0 ordering violations.

**The material is no longer finite.** A heated Create mixer makes it from
`#alfheim:crystal_shards` + mana powder + water, in Era VII because that is the first era to
teach `cr_mix`. The shard tag holds exactly the six crystals with a budding block, so the tag
*is* the renewability guarantee — do not add `frost_shard` to it.

**Two things this system still does not have:**
- The mixing recipe is **invisible to `check_coverage.py`**, which counts item outputs only.
  A future recipe producing nothing but fluids would slip through silently.
- No decision yet on whether the Void Verge should be the richest source of pools.

---

## Blocked on a user decision — 2026-09-04

Two items from the fey roster cannot be built with what is installed:

| Asked for | Blocker |
|---|---|
| **Deer** from the horse model, antlers on bucks | Needs a new entity type. KubeJS 2001.6.5 has no entity registry builder on Forge 1.20.1. Of 691 registered entities the only candidate is `occultism:deer_familiar` — a summoned familiar with no spawn placement. |
| **Toads** as larger frogs | 1.20.1 has no scale attribute; `minecraft:generic.scale` arrives in 1.20.5. |

Both need either a mod that ships them or a small Java entity. Recorded in `FEY_BACKLOG` inside
`tools/gen_alfheim_biomes.py` so the constraint is not rediscovered.

---

## Still open from earlier passes

- **`alfheim:scorchfell` remains unreachable.** `locate biome` reported *"Could not find a biome
  of type alfheim:scorchfell within reasonable distance"* on every run to date, while the other
  ten are found. Its temperature band is the suspect.

## Guild Regalia — planned and inventory-validated — 2026-09-04

The installed Curios scan records 147 wearable IDs: 114 functional items and 33 Botania cosmetics.
The last headless run loaded 14 slot types. `tools/build_curio_inventory.py` produces the evidence
in `alfheim_reclaimed_design/curios/installed_curios_inventory.json` and its readable inventory.

`tools/build_curio_plan.py` validates a 63-item plan: 36 class pieces for the six Mine and Slash
classes and 27 trade cuffs for all nine professions. It references 46 installed functional Curios
and currently reports zero missing IDs. All embedded rank materials resolve in the pack registry.

The plan adds no slot or capacity. It permits up to two class signets in existing ring slots, one
class emblem in necklace/charm, and one active profession cuff in bracelet. Ranks gate visibility,
cross-mod station handshakes and bounded master workflows at eras II, V and VIII. Profession proof
is server-owned player state, so crafted ranks remain tradeable but cannot transfer another
player's progression or bypass the buyer's native profession tier.

No Curio item, recipe, effect, slot modifier or proof capability has been installed. The first
implementation gate is a live per-player slot/capacity probe followed by a Warrior/Mining vertical
slice. Exact cooldowns, ranges, percentages and costs are deferred until event ownership and NBT
preservation pass at runtime.

---

## Reclaimed Armory — generated and runtime validated — 2026-09-04

The installed Mine and Slash base classes are Warrior, Hunter, Sorcerer, Shaman, Warlock and
Minstrel. They are expressed as Thornwarden, Waywatcher, Leyweaver, Rootspeaker, Duskkeeper and
Dawnsinger without replacing the native classes.

`tools/gen_armory.py` generates 480 registered equipment pieces across ten material eras: three
weapons, one offhand and four armor slots for each class. It also generates 480 inventory textures,
120 worn armor layers, 480 item models, 48 native Mine and Slash base gear types, 480 auto-item
mappings, 480 custom item generations and 480 Gear Crafting recipes.

### Transparency is measured, not inferred from the preview

All six source atlases run through an edge-connected Pillow flood fill, including sources that
already contain an alpha channel. Palette alpha 1–16 is explicitly rewritten to `(0,0,0,0)` after
resizing. The generator refuses nontransparent corners or nearly empty foreground/background.

| Class | Final icons | Literal alpha-zero range |
|---|---:|---:|
| Thornwarden | 80 | 36.9%–81.6% |
| Waywatcher | 80 | 43.5%–84.4% |
| Leyweaver | 80 | 42.8%–81.3% |
| Rootspeaker | 80 | 42.0%–78.1% |
| Duskkeeper | 80 | 38.2%–82.5% |
| Dawnsinger | 80 | 47.5%–79.8% |

All 120 worn layers use binary alpha and are 67.8%–86.3% transparent. Review sheets intentionally
draw a checkerboard behind the production sprites to expose halos; the item PNGs themselves have
literal transparent backgrounds.

The first review exposed one topology case the corner test could not catch: the closed bow and
string trapped an opaque background island inside the curve. Bow cells now receive a second
connected-component pass for large enclosed neutral regions. All 20 Hunter/Duskkeeper bows have a
26–59 pixel enclosed alpha-zero region after final 32×32 conversion; the generator requires at
least 20 pixels for every bow.

Crossbow frames and the Waywatcher necklace exposed the same issue at smaller scales. Crossbows
now use class-aware enclosed-component thresholds, preserving pale Dawnsinger limbs while opening
all 20 interiors (11–65 alpha-zero pixels). Necklace output keeps the largest connected foreground
silhouette, removing the stray atlas strip beside the chain; all ten loops retain 11–15 enclosed
alpha-zero pixels.

### Runtime proof

The dedicated Forge 47.4.10 run in `server/console-20260904-102701.log` reached `Done` and exited 0.
KubeJS loaded 9/9 startup scripts with zero errors and zero warnings. A temporary probe queried the
live Mine and Slash containers after datapack load:

```
[Armory Probe] gear_types=48 auto_items=480 custom_items=480 profession_recipes=480
[Armory Probe] representatives gear=true auto=true custom=true recipe=true
```

The probe was removed after validation. `tools/armory_manifest.json` preserves the log hash and the
hash of the generated MMO payload.

### Known presentation limits before client playtest

- Bows and crossbows have their native use behavior but currently use one static inventory model;
  draw-stage textures have not been authored.
- Thrown tridents use the vanilla trident entity renderer after leaving the hand; their custom item
  art covers inventory and held form.
- Dedicated-server validation cannot prove worn-model alignment or first-person transforms. The
  flat UV layers and item sheets are visually reviewed; a client equipment pass remains required.
- The Curios phase now has a validated design and installed-item inventory; gameplay registration
  and numerical balancing remain the next implementation work.

---

## The first play session — nine findings, five defects — 2026-09-04

The user played a fresh world and reported nine things. Screenshots settled three of them
immediately; the rest were measured.

### The big one: nine of eleven biomes could not exist

The player saw only MythicBotany's biomes, no Greatbole, and no void. All one root cause, in two
layers:

**1. The climate axes were dead.** MythicBotany ships Alfheim with

    alfheim_temperature = libx:clamp of density 0.0      <- a CONSTANT
    alfheim_humidity    = libx:clamp of density 0.0      <- a CONSTANT

Every sample reads temperature 0.0 and humidity 0.0. Any band constraining either away from zero
can never be selected — and nine of ours did, including all five deficiencies. This file's own
generator carried a comment saying those axes were "free"; they were not free, they were flat,
and that sentence is what caused the bug. It has been corrected in place.

**2. The layer was not a partition.** A LibX biome_layer entry is a vanilla
`Climate.ParameterPoint` and selection is NEAREST MATCH. Our biomes were declared as strict
SUBSETS of MythicBotany's full-span boxes, so a point inside both was distance 0 from both and
the tie went to the bigger, earlier entry every time. The void was the clearest case:
`alfheim_lakes` claimed continentalness [-1, 0] and was declared first, `void_verge` claimed
[-1, -0.8] and was declared last, so the void was unreachable by construction.

Fixed by giving Alfheim a real climate (`CLIMATE_OVERRIDES`) and resolving the layer into a
genuine disjoint partition — an n-dimensional box subtraction, most specific claims first.

**Measured on a live server with `locate biome`, which is the only honest test:**

| | before | after |
|---|--:|--:|
| biomes reachable | **0 of 11** | **10 of 11** |
| void_verge | never | 951 blocks |
| mana_fen | never | 160 blocks |
| silverbark_wood | never | 340 blocks |

`scorchfell` is the holdout: probed at temp 0.55, 0.45 and now 0.32. The noise reaches the low
0.4s in that continentalness band and no further, so the last threshold is untested.

Biomes were also enlarged on request — climate xz_scale 0.0625 (vanilla's large-biomes value)
and continentalness 0.045, roughly 2–4x larger regions.

### The other findings

| # | Finding | Cause |
|--:|---|---|
| 2 | "Petal apothecaries everywhere?" | MythicBotany's own default: 1–3 per **second** chunk. Overridden to 1 per 20. |
| 3 | Crystals render as cubes | `.textureAll()` builds a cube model. Vanilla amethyst uses `block/cross`; clusters now do too. Block and budding forms stay cubes, as vanilla's do. |
| 5 | Trees in open water | `heightmap: OCEAN_FLOOR` **unguarded**. Vanilla's own trees use it too, paired with `surface_water_depth_filter` and a `would_survive` sapling check. Both added. |
| 6 | Trees on top of trees | Same fix — `would_survive` rejects a log top. Probed with an oak sapling deliberately: our own saplings are KubeJS blocks whose `canSurvive` is permissive and would accept anything. |
| 8 | Ore distribution chart | `tools/ore_chart.py`, read from the placed features rather than the manifests. Also switched all 12 blooms from `uniform` to `trapezoid`, so each has a depth it is *most likely* at, as vanilla ores do. |

Coverage is y−64..112, 46% of the 384-block column; the 208 blocks above are sky.

### New guard

**W8** — the climate partition must be disjoint, and every biome with a definition must have a
band. Nothing looked wrong when this failed: the file parsed, every biome was present, and the
world contained none of them. Proven to fire by reinstating the old overlapping order, where it
correctly named `void_verge` and `alfheim_lakes`.

### Planned, not built

- `THE_DEEP.md` — quarries, tombs, faultworks, and **§5 the Deepworks**: a subterranean biome of
  lava lakes and magmatic livingrock, with its environmental pass deferred by the user.
- `SPAWN_ZONE.md` §11 — the village problem. `gen_elven_ruins.py` can only ever produce *decayed
  versions of the three cottages MythicBotany ships*; a canopy village needs bough and platform
  pieces and, above all, **bridges**, of which there are currently none.

**Validation:** all six checkers **0** · `check_coverage` 0 violations · **497 artifacts
byte-identical** across fourteen generators · live server: 10/11 biomes located, hub created with
no player, 0 recipe errors, 10 ERROR lines and none ours.


## The hub builds itself, with nobody logged in — 2026-09-04

**User:** *"We should have server side commands for a server operator to create the world spawn
and set player world spawning to the correct place ... So our correct world hub generation
should not depend on a player logging in."*

It did depend on it, in two places. `02_spawn_dimension.js` teleported each player on
`PlayerEvents.loggedIn` and then `spreadplayers`-ed them **up to 2000 blocks**, so a server
nobody had joined had no hub at all and two players could land a kilometre apart and a kilometre
from the Greatbole. `03_hollow_court.js` audited the court on login too.

### Vanilla functions, not a KubeJS command API

`ServerEvents.commandRegistry` exists and hands you a raw Brigadier dispatcher. It was the wrong
tool: this project has already been bitten twice by KubeJS APIs whose shape moved between builds
— `02_spawn_dimension.js` carries a standing refusal to use level accessors for that reason, and
`.tagItem()` cost a boot earlier the same day.

`#minecraft:load` runs a function on every world load **on the server with no player**, which is
the entire requirement, in vanilla, with no API risk. `tools/gen_world_hub.py` emits five:

| Command | |
|---|---|
| `/function alfheim:hub/create` | force-load, place the anchor, set Alfheim's default spawn. Idempotent. |
| `/function alfheim:hub/autoload` | wired to `#minecraft:load`; creates the hub once per world |
| `/function alfheim:hub/status` | **read-only**, console-safe |
| `/function alfheim:hub/send` | put the running player at the anchor |
| `/function alfheim:hub/reset` | drop the anchor and the flag so it can be rebuilt |

### The anchor trick

Finding a safe Y from a command is the hard part, and it is solved by not computing one. A
`minecraft:marker` is summoned at y=250 over the hub and `spreadplayers` drops it onto a legal
surface; the marker **is** the anchor from then on. Nothing has to read coordinates back out of
a command — which `runCommandSilent` cannot do anyway, since it returns a result count.

`02_spawn_dimension.js` now delivers to that anchor via `hub/send`, falling back to the old
spread landing only if the anchor is genuinely missing, and saying so in the log when it does.

**Vanilla limit, stated plainly:** there is no cross-dimension world spawn. Something must still
move a joining player into Alfheim. What changed is that it moves them to a fixed, pre-built
place instead of scattering them, and the place exists before anyone connects.

### Verified on a live server, with no client attached

```
[Alfheim] --- world hub status ---
[Alfheim] hub: created
25 force loaded chunks were found in mythicbotany:alfheim at: [0,-2] ... [-1,2]
```

Also fixed while there: two defects in my own first draft — `status` used `@s` (the console has
no entity) and it **set the caller's spawnpoint**, a mutation with no business in a command
called status.

And `/kubejs export` was removed from the default run sequence: it triggers a datapack reload
that fails on this build with `NoSuchMethodError: JsonObject.isEmpty()` — gson 2.10 on the
classpath, that method arriving in 2.10.1. It is now `--export`, for when a fresh registry dump
is actually wanted. `Reload failed` went 1 → 0 and total ERROR 12 → 10.

**Validation:** all six checkers **0** · `check_coverage` 0 violations · **486 artifacts
byte-identical** after re-running all fourteen generators · live server: hub created with no
player, 0 `Error parsing recipe alfheim:`, 0 reload failures.

**Still not observed:** that a *joining client* actually lands at the anchor. The hub half is
proven; the delivery half has never had a player through it, because no client has connected.

---

## LEVEL 8 AND 9 — the pack boots and generates, headlessly — 2026-09-04

**User:** *"Use a command based server side world generation."* That removed the one thing that
had deferred every runtime claim in this project: booting no longer means driving a GUI.

`tools/run_server.py` installs a Forge 1.20.1-47.4.10 dedicated server into `server/`, mirrors
the pack into it, launches it headless, feeds a command sequence on stdin, and captures the
console. **The Forge installer was downloaded and the Minecraft EULA accepted on explicit user
instruction**; the harness refuses to run without both and says so rather than assuming.

| | |
|---|---|
| Startup | `Done (19.440s)` |
| World | 20 region files, `level.dat`, **`dimensions/mythicbotany/alfheim/region`** |
| KubeJS | **6/6 startup, 22/22 server scripts, 0 errors** |
| `Error parsing recipe alfheim:` | **0** — B-41's acceptance condition, met in a running game |
| Quest lines | **0 failures** |
| Spawn protection | **2 profiles loaded**, ours accepted |
| Remaining ERROR | 12, **none ours** — Iron's Spellbooks loot ×4, dist cleaner ×2, hanging entities ×5, Moonlight notice ×1 |

### Eight defects only a boot could find

Every one passed every static check. Seven runs, each fixed at its generator.

| # | Defect | Why static checks could not see it |
|--:|---|---|
| 1 | `continuity` is a Fabric client mod loaded via Sinytra Connector; kills dependency resolution on a server | Declares nothing at Forge mod level |
| 2 | ETF puts a client-only handler in a **common** mixin, reaching `Screen` on a dedicated server | Mod defect, invisible in our tree |
| 3 | BetterGrassify + ForgeSkyboxes fail the dist cleaner | Same |
| 4 | **`.tagItem()` does not exist on an ItemBuilder** — only on BlockBuilder. 18 calls | The script parses perfectly |
| 5 | **`const HOME_DIMENSION` declared in three server scripts** — KubeJS shares one scope per directory | Each file parses fine alone; `node --check` cannot see it |
| 6 | Geode `random_offset.y_spread` of −28..−14 exceeds the codec's ±16 bound | Well-formed JSON, rejected by the codec |
| 7 | `concentric_rings` **requires `salt`**; the Greatbole structure_set omitted it | Same |
| 8 | **`quest_giver:grow_tree` is not a registered task type** — the class ships and is never registered. It aborted loading of **every quest line, both givers** | The id was derived from a class name |

Plus two of my own earlier "fixes" that the boot proved were not fixes at all:

- **B-43 was wrong.** The item tag I supplied listed the eight orange-leaf **blocks**, none of
  which has an item form, so the tag failed on its own contents and `minecraft:leaves` stayed
  broken. It has to be **empty** — that resolves the reference honestly, and now does.
- **The Greatbole had no spawn protection.** Continuity Works rejected the whole profile —
  *"attempts to lower the hard 500-block minimum"* — because `jigsaw_piece_exclusion_radius` was
  96. A static check saw a well-formed file and a present profile; the mod saw an invalid one.

### The finding that changes how this project validates anything

> **Lang keys are translations, not registrations.**

Eleven MMO-bridge recipes were rejected at every load with `Unknown item 'mmorpg:*'`. Those ids
came from lang keys — `item.mmorpg.currency.orb_of_quality` — and the **real registry path is
`mmorpg:currency/orb_of_quality`**, with slashes. `mmorpg:map` does not exist at all; the map you
carry is `dungeon_realm:dungeon_map`. Every static check in this project had been reading
translations and calling it verification.

`/kubejs export` now dumps the real registry, and **`tools/registry_items.json` holds all 8,257
registered item ids as ground truth**. `check_era.py` prefers it over the lang-derived set. The
moment it was wired in, a checker that had reported **0 problems** reported **20** — including
ids in quests I had written and verified the same day.

Two new checks close the gaps that let these through:

- **E12** — every item named by **any** recipe script. E2 only inspected era-scoped scripts, so
  `14_mmo_bridge.js`, `12_rites.js` and `30_item_uses.js` were never id-checked at all.
- **S8** — no top-level name declared twice across scripts in one KubeJS scope. Defect 5's class.

Both proven to fire on injected faults.

### Harness lessons, recorded because they cost three runs

A killed wrapper leaves the java child alive holding `session.lock`, and the next run dies with
an IOException that reads like a filesystem fault. The harness now detects running servers,
refuses to start, names the PIDs, clears stale locks, and writes a **per-run** timestamped
console log — three runs previously clobbered one file and I read a mix of them.

**Validation:** all six checkers **0** · `check_coverage` 0 violations · **480 artifacts
byte-identical** after re-running all thirteen generators.

**Level 9 is partially passed:** world creation, Alfheim generation and chunk save are observed.
Not yet observed: that the player wakes in Alfheim (no client joined), that the Greatbole
generates, that the court is seated, or that anything is survivable. `server.properties` is
generated with a fixed seed, so those are the next commands to add.

---

## Every step taught, every method unlocked first — 2026-09-04

**User set a standard in two halves**, both now measured by `tools/check_coverage.py`:

> Every intended processing step for an ore, a contributive item or a componentary item should
> have a quest covering the process by which it is created … and when a recipe requires a method,
> verify that the method was unlocked in some preceding step, so recipes are used consecutively
> rather than requiring methods you have not yet unlocked.

**Result: 39 → 0 coverage gap, 13 → 0 ordering violations, 0 unmapped methods.**

### Both gaps had one root, and it was in a generator

`gen_quests_bulk.py` **banded** the tier ladder — `band = len(chain)//5`, capped at six leaf
quests, then truncated the chapter at 22. Era X therefore named six of its seventeen steps and
eleven transformations had no quest at all. Replaced with one quest per step derived from
`gen_ladder.LADDER`, and the truncation removed. Chapters IV–X grew from 22 each to 23/25/28/31/
33/31/33.

Method teaching is derived the same way: each era emits a quest for every station it is the
**first** to use, so adding a station to an era's rotation now produces a teaching quest
automatically rather than a silent dead end.

### Three findings that were more than bookkeeping

**1. The Alfheim Gate could not be built by anyone, ever.** Botania crafts the portal from
livingwood logs and terrasteel nuggets. Livingwood is a gate-import the premise says you cannot
have — it is the entire reason Era I was re-pointed onto Dreamwood — and terrasteel is the Era X
capstone. Six eras of `elven_trade` recipes depended on a station requiring a material from the
last era and one the world does not contain. **No quest could have fixed that**; the recipe had
to change. `07_alfheim_gate.js` re-lays it on dreamwood framing `alfheim:gatewrought_cord`, which
is the material B-36 specified all along.

**2. `rite:render` — 12 recipes, 0 covered.** The payoff of the whole ore chain: quickened bloom
into metal. B-47 retired Alfheim's vanilla ore layer, so rendering is the **only** source of coal
or iron in the world, and the chain was taught right up to the final step and then stopped.

**3. `ars_nouveau:crush` is not a station.** It is a glyph — "turns stone into gravel". There is
no block to build, so the unlock is the Scribe's Table and a spell book. It had been the one
method the ordering check could not see.

### And a defect the reproducibility check caught

**Three generators were writing `chapter_groups.snbt`.** `gen_quests_bulk.py` wrote it with the
one-group version, so running it after `gen_compendium.py` **silently deleted the Compendium
group and all six reference chapters.** This was the second copy of a defect already fixed once in
`gen_quests.py` — the first fix did not find it because nothing checked. Now **E11** asserts that
exactly one generator writes each shared FTB Quests file, ignoring comment mentions. Proven to
fire, then restored.

> It only surfaced because a reproducibility run executed the generators in a different order than
> usual. Byte-identical checks are not ceremony; that one found a bug that would have deleted a
> whole chapter group in front of a player.

### The standard, as recorded

`MAGIC_SYSTEMS.md` §6 holds it. The rule is ambiguous by a factor of ten, so the tool reports
three readings and assumes none: **per item 106, per process 39, hybrid 39 (recommended)** — per
item for ladder steps, per process for the Rites, because the Rites are four *parallel* routes
from raw bloom to quickened bloom rather than a chain, and steeping a twelfth bloom teaches
nothing the first eleven did not.

**Validation:** all six checkers **0** · `check_coverage` 0 gap / 0 violations · **480 artifacts
byte-identical** after re-running all thirteen generators.

**Not run:** everything, still. Quest totals are now 61/71/69/23/25/28/31/33/31/33 = 405 across
ten chapters plus the 57-entry Compendium.

---

## The early game, rebuilt around systems — 2026-09-04

**User asked** to triple the quest count with the emphasis on the early game, then sharpened it
mid-work: *"an indexing of all of our different magic mods, and how they all need their own sets
of quest chains through all three early game eras."*

Measuring that before authoring is what made the work correct, because the measurement found a
worse problem than the count did.

### The finding

> **Ten magic or magic-adjacent systems had zero quest coverage across all three early eras.**

The 66 quests of Eras I–III named items from six namespaces. Nature's Aura, Occultism, Feywild,
Iron's Spellbooks, Create: Wizardry, Occult Engineering, Dungeon Realm, The Harvest, Ancient
Obelisks and Knight Quest were never mentioned — installed, working, and invisible.

**Era II had no Guides at all**, which meant `ERA_EXPANSION.md` §4.1's three-energies
disambiguation — that document's own nomination for the pack's worst confusion — was taught
nowhere. It now has 19.

### Built

New authority: `alfheim_reclaimed_design/MAGIC_SYSTEMS.md` — every magic system indexed from the
jars, with its verified entry items and the chain it runs through Eras I–III.

| Era | Was | Now | Budget | Guides |
|:--:|--:|--:|--:|--:|
| I | 29 | **60** | 60 | 20 |
| II | 22 | **70** | 70 | 19 |
| III | 22 | **69** | 68 | 17 |
| **Total** | **66** | **199** | 198 | **56** |

Every system now has coverage; none is at zero. Botania 27, Ars Nouveau 23, Nature's Aura 9,
Iron's Spellbooks 9, Occultism 8, Feywild 6, MythicBotany 4, Create: Wizardry 4, Mine and Slash 4,
Occult Engineering 2, Dungeon Realm 2, The Harvest 1, Ancient Obelisks 1.

The chains share one shape — **Era I introduces, Era II makes it produce, Era III makes it scale**
— and one rule that keeps six new traditions from diluting the Twin Spines into eight: a chain
teaches a system and ends in a capability, but **only a spine gates an era**, and every chain's
first real cost is paid in spine materials.

### A correction that changed a gate

B-57 claimed the Map Device was `mmorpg:teleporter` with no recipe anywhere, so expeditions were
unreachable. **Wrong on both counts.** `mmorpg:teleporter` is legacy and uncraftable; the working
block is `dungeon_realm:map_device`, and the jar crafts it from **one diamond over one stone at a
vanilla crafting table**. Expedition access — a major capability — cost less than a stone pickaxe
and touched no spine, in direct violation of §2.3. `06_expedition_gate.js` removes that recipe and
re-lays it on the Runic Altar in elven materials; Orenvel grants one outright as the second route.
Removal and replacement ship together, per §6.1.

> The error was checking the id I expected rather than the id the game uses. Two mods ship a block
> called "Map Device" and only one of them works.

### The checker learned two things it should always have known

Authoring surfaced three false E1s and one false E3 — all checker gaps, not content defects:

- **`our_registrations()`** — `check_era` knew only the 80 items in `items_manifest.json`, so the
  **153 `event.create` calls** across the startup scripts were invisible. Blooms, crystals, grove
  woods and the sealed gate all read as unregistered the moment a quest named one. Reading the
  registrations rather than three more manifests means one source that cannot drift.
- **`world_sourced()`** — E3 asked whether a *recipe* produces an item. A raw bloom is mined out
  of stone; no recipe makes one and none should. The honest fix was to teach the checker the other
  way of obtaining things rather than to author a fake recipe to satisfy it.

Both proven not to have blunted the check: injected nonsense ids still raise E1 and E3.

**Validation:** all six checkers **0** · **479 artifacts byte-identical** after re-running all
twelve generators.

**Not run:** everything. B-55 still governs — see its entry; the risk it names is regenerating
*after players have played*, not authoring before release, and authoring the early game now is the
"author once" step under either of its resolutions.

**Next:** MythicBotany at 4 task items is the thinnest real gap left — half the Spine of Leaf,
carried mostly by Rites taught through Botania stations rather than named directly. Then Eras
IV–X, which `gen_quests_bulk.py` owns rather than `gen_quests.py`.

---

## Chunks in, quarantine out, three items closed — 2026-09-03

**User:** installed FTB Chunks; instructed that the quarantined mods be removed; confirmed the
multi-pass structure approach ("automated structure generation typically needs multiple passes of
detailed improvement ... before the structures are actually usage acceptable"); and directed that
**pack design changes come before spawn checking**. Runtime work is therefore deferred by
instruction, not by blocker.

### `quarantine/` cleared — 361 MB to 513 KB, with two deliberate survivors

Seventeen rejected jars deleted, Conquest Reforged (227 MB) among them. **Two things were kept,
and the reasons are doctrinal rather than cautious:**

| Kept | Why |
|---|---|
| `ContinuityWorks-...-rc.2.jar` (459 KB) | §5.1 condition 2 requires the unmodified original be preserved, and `patch_continuity_works.py` takes it as its `src` argument. Delete it and the installed `+cw1cw3cw4patch` jar becomes **unreproducible**. |
| `vanilla_ore_layer_2026-09-03/` (21 files, 53 KB) | Retired ore-layer design history. Not a mod, so not in scope for "the quarantined mods should be removed". |

The two **superseded** Continuity Works chained jars were deleted — §5.1 says a further defect
does not get a further chained jar, so they had no role.

**Consequence to record:** Conquest Reforged is no longer on disk, so restoring the amphitheatre's
stone palette is now a fresh CurseForge install, not a file move. `SPAWN_HUB.md` §3 and §7 updated
— calcite and quartz are the palette, not a placeholder.

### FTB Chunks — the claim and the enforcement are separate layers

`ftb-chunks-forge-2001.3.8` installed, 82 jars, dependency check clean. It settles the claim
layer but does not replace `04_spawn_hub.js`, and the split matters: **a claim is runtime world
data**, stored per team, config written at first boot. No datapack can pre-claim a chunk, so the
hub claim is a one-time in-game admin action and belongs to pass 2.

Commands read off `FTBChunksCommands.class`: the admin subtree is `claim_as`, `unclaim_as`,
`bypass_protection`, `extra_claim_chunks`, `extra_force_load_chunks`, `unclaim_everything`,
`unload_everything`, and `claim` takes `radius_in_blocks`. `claim_as` requires a **team**, which
is exactly why it cannot be scripted blind.

### Three items closed

- **B-43** — `kubejs/data/jaffabricate/tags/items/orange_leaves.json`. Verified in the jar: it
  ships `data/minecraft/tags/items/leaves.json` pointing at `#jaffabricate:orange_leaves` and the
  **block** version of that tag, but no item version. Four ERROR lines a load, taking
  `minecraft:completes_find_tree_tutorial` and two MineColonies tags down with them.
- **B-24** — the Greatbole added to `continuityworks_spawn_protection:protected` plus a profile
  with a 500-block exclusion radius and `protect_jigsaw_pieces: true`. Format copied from the
  mod's own `abyssal_vents` profile. Per-piece protection is **required** here because the tree is
  four stacked pieces — and is the exact opposite of what the Hollow Court city will need.
- **B-30 was already fixed, and the entry was stale.** `21_era1_elven_early_game.js:77` already
  emits `alfheim:era1/feysythia_repair`. A second copy went into a new `05_upstream_repairs.js`
  and **`check_era.py` E7 rejected it as a duplicate before it shipped**; the script was deleted.

> That is the checker earning its keep in the least glamorous way possible: not by finding a
> subtle bug, but by stopping a competent-looking fix to a problem that no longer existed. Stale
> backlog state is a real defect class, and E7 is currently the only thing that detects it.

Confirmed against the jars while there: Feywild 5.5.5 ships only `feywild:fey_gem` and
`feywild:fey_dust`. MythicBotany's `feysythia_level_1`…`_4` tags all point at the removed
lesser/greater/shiny/brilliant gems, so Feysythia's upgrade tiers resolve empty and only level 0
works. Left alone — choosing one surviving item to stand in for four removed ones is a balance
decision, not a repair.

**Validation:** all six checkers **0** · **477 artifacts byte-identical** after re-running all
twelve generators.

**Not run:** everything. By instruction — pack design changes come before spawn checking.

---

## Spawn hub pass 1 — the Greatbole stands, on disk — 2026-09-03

**User asked** for the pack's centrepiece: a massive oak with an intricate portal built into its
flank, a ruined marble amphitheatre outside it for the court to occupy, and the whole thing an
admin-claimed protected hub — *"the proper central piece of the entire pack"*, anticipating that
the player bases nearby and **returns here all campaign**. Documented in full as
`alfheim_reclaimed_design/SPAWN_HUB.md`; built as pass 1 of eight.

### B-56 cleared

The user removed the YUNG chain deliberately. `betterarcheology` was the dependent left behind,
still declaring `yungsapi` `mandatory=true`, so the pack still would not boot. Quarantined with
its sha1 recorded; nothing of ours referenced it; `check_dependency_ranges.py` back to **0**.
`minecraftinstance.json` still lists it, so a CurseForge sync may restore it — that is the failure
to expect, and the manifest fix needs CurseForge closed.

### Built — four pieces, 60,077 blocks, ~184 blocks tall

Everything is written from numbers, because the user said this needs many passes. Pass 2 is an
edit to a constant and a re-run. That is the whole shape of `tools/gen_spawn_hub.py`.

| Piece | Size | Blocks |
|---|---|--:|
| `greatbole/base` | 48³ | 30,123 |
| `greatbole/trunk` | 32×48×32 | 13,096 |
| `greatbole/crown` | 48×40×48 | 12,371 |
| `court/amphitheatre` | 48×12×48 | 4,487 |

The gate chamber is a 22-block walk into the trunk to an **8×10 face of `alfheim:sealed_gate`**,
framed in livingrock bricks, chiseled quartz, gold and elf glass — B-57's block doing the job it
was built for, and the seeing half of B-36. NBT format read off MythicBotany's shipping
`house.nbt` rather than assumed: `size`/`entities`/`blocks`/`palette`, DataVersion 3465.

There is **no marble block in the load path** — Conquest Reforged is quarantined, Quark absent —
so calcite and the quartz family carry it, with `feywild:elven_quartz_block` as the elven accent.
Restoring Conquest Reforged would improve the amphitheatre more than any other single change.

### The contradiction this surfaced, and why it mattered

`03_hollow_court.js` summoned the eight elves **at the player's landing spot**. Correct when it
was written; wrong the moment the hub existed, because `02_spawn_dimension.js` spreads the player
up to **2000 blocks** from the origin where `concentric_rings` puts the tree. It would have built
a **second court with the same names in an empty field** — and quest_giver binds a quest line by
custom name, so the player's Velrous would have been whichever one they reached first.

The court is now **seated inside `court/amphitheatre.nbt`**, read from
`hollow_court_manifest.json` at generation time so seat names and quest-link names cannot drift.
The summon path survives behind `FALLBACK_SUMMON_AT_PLAYER`, default off, and says in the log
that it is placing them away from the amphitheatre when used.

**Still open, and it is the biggest one:** the player *still* does not arrive at the hub. Until
`02_spawn_dimension.js` places them against the structure, the centrepiece is 2000 blocks from
where the campaign starts. `SPAWN_HUB.md` §7 holds the decision; pass 2 settles it with a world open.

### The protection is real, but it is not FTB

`ftbchunks` **is not installed** — only `ftblibrary`, `ftbquests`, `ftbteams`, `ftbxmodcompat`.
The claim layer the user asked for by name needs a jar and a composition decision; the behaviour
it was wanted for does not, and is in `04_spawn_hub.js`: no hostile spawns, no explosions, no mob
block-breaking, 96-block radius, Alfheim only. Every handler arms in its own try/catch and the
startup line names which armed — a protection that silently failed to register is worse than none,
because it would be trusted.

### Two defects, both caught by checkers rather than by eye

- **`minecraft:empty_processor_list` does not exist.** The id is `minecraft:empty`. Six pools
  were wrong; `check_worldgen.py` W5 caught all six the moment they were written. Confirmed
  against MythicBotany's own pools.
- **A generated apostrophe** inside a single-quoted string made `04_spawn_hub.js` a syntax error
  — the whole file dead, silently. That produced the more valuable half of the new checker.

### `node --check` is available, and now runs over everything

The single most useful discovery of the session: node is on this machine, so **S7 syntax-checks
every KubeJS script**. All 27 parse. This closes a whole failure class the project had no cover
for — B-41 taught that a script which parses is not a script that works, but a script that does
not parse certainly does not.

`check_spawn_hub.py` also asserts **S4: every jigsaw `target` is answered by some piece's `name`**.
An unanswered target generates the base alone — no trunk, no crown, no court, no error. Proven to
fire, along with S7, on injected faults; restored by regenerating from the generator.

**Validation:** `check_spawn_hub` **0** · `check_hollow_court` **0** · `check_era --all` **0** ·
`check_worldgen` **0** · `check_feature_order` **0** · `check_dependency_ranges` **0** ·
**474 artifacts byte-identical** after re-running all twelve generators, NBT included.

**Not run: any of it.** Unproven: that the tree assembles whole; that `beard_thin` sits the root
flare in ground rather than on a pillar of air; that the gate chamber is reachable; that
structure-baked entities spawn with NBT intact; and that the three protection events exist under
those names on KubeJS 2001.6.5 — the startup log will say.

---

## The Hollow Court, and a boot blocker that arrived from outside — 2026-09-03

**User asked** whether the Quest Giver mod and the wood elf entity could put a court of NPCs at
spawn — Velrous giving quests, a captain of the Royal Elven Guard — plus a fake portal block for
the arrival chamber. Chosen: two named quest givers plus six ambient elves; the Captain **gates
expeditions**; the gate is a dormant face now, with B-36 keeping Era IV.

### ⚠ B-56 — the pack stopped booting, and nothing in this session caused it

`check_dependency_ranges.py` reported **0** early in the session and **1** later. That divergence
was investigated rather than accepted, and it is real:

| Evidence | |
|---|---|
| `minecraftinstance.json` | rewritten **21:30:52**, 468520 → 446348 bytes |
| `mods/` | directory mtime **21:30:52**, same second, no file inside newer |
| YUNG's API | **gone from the whole instance** — not in `mods/`, `quarantine/`, or the manifest |
| `betterarcheology` | there since Aug 31; declares `yungsapi` **`mandatory=true`** |

Forge hard-fails an unsatisfied mandatory dependency, so **level 8 cannot pass until this is
fixed**. This session only ever read from `mods/`, so the writer was CurseForge, syncing while
the instance was being edited. Deliberately not actioned: jars are pack composition, and §5 makes
the manifest CurseForge-owned and editable only while CurseForge is closed.

**The reusable lesson:** re-running a checker that was already green is not wasted work. The pack
is not a closed system while its launcher is open.

### Built — the court

No new mod. `quest_giver`'s `quest_line_links.json` binds a line to any `entity_id` + `name`, and
`QuestLinkManager.getMatchingLink` compares `getType()` against `getCustomName()`, so a nametagged
`richs_races_wood_elves:wood_elf` **is** a quest giver. Both mods carry CurseForge project ids, so
distribution stays clean.

| | |
|---|---|
| Magister Velrous | `the_reclaiming`, 6 quests — biome, item_stack, craft, grow_tree, gift. Gates nothing. |
| Captain Orenvel | `the_royal_guard`, 5 quests — kill, item_stack, craft. **Gates expeditions.** |
| Ambient | 6 named elves, no lines, set dressing |
| `alfheim:sealed_gate` | 12-frame animated block, `hardness(-1)`, no mineable tag |

**The Captain's gate needed no removal, which is the part worth recording.** `mmorpg:teleporter`
— the Map Device, the only entry to Mine and Slash's dungeon dimension — has **no recipe anywhere
in the pack**: 0 across all 133 mmorpg recipes and every other jar. Expeditions are presently
unreachable in survival. Orenvel's last quest grants one. So the gate both satisfies §6.1 by
adding a route rather than closing one, *and* opens content that was dead.

**The elves are hostile.** `WoodElfEntity extends Monster implements RangedAttackMob` and targets
`Player`. `NoAI:1b` kills targeting, wandering and despawn in one flag; each also gets a livingrock
plinth set under its feet, because NoAI mobs do not walk down onto terrain.

### The checker, and why H5 is the one that matters

quest_giver matches on **custom name**. A one-character drift between `quest_line_links.json` and
the summon in `03_hollow_court.js` yields an elf that stands there and gives nothing — no error,
no log line, no missing id. `check_hollow_court.py` **H5** asserts the two agree; H1–H7 also cover
line registration, parent resolution, task and reward ids, entity/biome ids, and **H6**, that an
item declared gated is actually granted where it is declared. Proven on injected faults — renamed
link, removed gate reward, broken parent, typo'd task id — then restored from snapshot.

One checker defect found and fixed while building it: the entity scan read only `mods/*.jar`, so
`minecraft:spider` looked unregistered. Vanilla entities live in the client jar.

**Validation:** `check_hollow_court.py` **0** · `check_era.py --all` **0** (459 recipes, 366
schema-checked) · `check_worldgen.py` **0** · `check_feature_order.py` **0** · **463 artifacts
byte-identical** after re-running all eleven generators. `check_dependency_ranges.py` **1** —
B-56, above.

**Not run:** all of it. Nothing here has been loaded, and it cannot be until B-56 clears.
Unproven in particular: that `NoAI` elves persist and render; that the quest GUI opens on
right-click with a Quest Scroll; that `biome`, `grow_tree` and `gift` tasks complete; that the
animated texture renders; and that `server.persistentData` and `scheduleInTicks` behave as assumed
on KubeJS 2001.6.5.

**Dependency worth stating plainly:** there is still **no spawn tree**. B-17 and B-18 are unbuilt
and `SPAWN_ZONE.md` says "No pieces built", so the court anchors to the player's landing spot, not
to a Greatbole. It moves into the jigsaw when one exists.

---

## B-41 repaired, B-42 inverted, and the checker taught to read schemas — 2026-09-03

**User asked** to examine the development goals, find the gaps in the next steps, and move forward.

### Two premises corrected before any work

**There is no git for this project**, stated by the user. The `.git/` directory in the instance
root is vestigial — created 2026-09-02, never used, `HEAD` malformed (`ref: refs/heads/`), zero
objects. It is not a defect and not a gap; do not propose version control. Work is purely local
files intended for **distribution on the CurseForge network**, which makes two things binding:
no third-party distribution, and everything shipped must either resolve to a CurseForge file ID
or be content the owner holds rights to.

> That has a consequence nobody has costed yet: the locally patched Continuity Works jar
> (`+cw1cw3cw4patch`) is first-party, so the rights are fine, but it is **not an official
> CurseForge build and cannot carry a file ID**. That is a distribution argument for **B-39**,
> on top of the maintenance one. Also unaudited: `gen_items.py` supports mod-art bases, and its
> own docstring flags that a public release should audit those licences. 83 items now exist.

### The gap that mattered most, quantified

**249 files under `kubejs/` and `config/ftbquests/` have changed since the game last ran** at
16:09 — 11 biome JSONs, 29 placed features, 29 configured features, 23 biome modifiers, the LibX
biome layer, and `alfheim_final.json`, the void density function this file already calls the
riskiest in the datapack. The Twelve Blooms, the six geodes, the Archive Groves, the five
deficiencies, the Void Verge, the Compendium and the MMO bridge have **never been loaded**.
Level 9's evidence describes a datapack that no longer exists.

### B-41 — all three families were still live, and the fix is at the generator

Verified rather than trusted: `fromColor` appeared **0 times** across all five ladder scripts that
emit `mythicbotany:infuser`, while `12_rites.js` had it. All three families repaired in
`tools/gen_ladder.py`, with every schema **read out of the shipping jar** rather than guessed:

| Family | Was | Jar says | Now |
|---|---|---|---|
| `mythicbotany:infuser` | `input:`, no colours | `ingredients`, `fromColor`, `toColor`, `group` — 2/2 recipes | all four emitted; beam runs dull→bright on the era's own hue |
| `create:sequenced_assembly` | `ingredients`/`processingTime`/`results` | `ingredient`, `transitionalItem`, `loops`, `results`, `sequence` | full shape, with 3 new `incomplete_*` items registered |
| `create:milling` | 2 ingredients | 1, in **231/231** recipes, always with `processingTime` | 1 |
| `create:pressing` | 2 ingredients + a duration | 1, in **39/39**, `processingTime` in **0** | 1, no duration |
| `create:mixing` | spurious `processingTime` | 1–5 ingredients, `processingTime` in **0/14** | dropped |
| `occultism:crushing` | no `ignore_crushing_multiplier` | present in **180/180** | emitted |

The root cause was structural, not incidental: `STATIONS` mapped `infuser` to the same `'infusion'`
emitter as Botania's `mana_pool`, which has no colour fields, and mapped all five Create types to
one generic `'shaped'` emitter that gave every one of them two ingredients and a `processingTime`.

### B-42 was backwards, and the jar says so

**All 29 `feywild:fey_altar` recipes in the jar use exactly 5 ingredients. None uses 4.** Our
generator emitted 4. `Index 4 out of bounds for length 4` in `FeyAltarRecipeCategory` is the
category reaching for a fifth slot our short array does not have — so we were **an ingredient
short, not one over**. B-42 proposed trimming to four, which would have preserved the crash.
Now padded to five.

### The checker that reported 0 while 11 recipes were rejected

`check_era.py` gained **E10**, and it does not hardcode a single schema. For each recipe type we
emit, it reads that mod's own recipes out of its jar and reduces them to: keys present in every
one (mandatory), keys present in any (permitted), and the ingredient counts actually observed.
366 recipes are now checked this way.

**Arity is asserted only from a sample of ≥20.** A profile is evidence about what shipping recipes
*do*, not a reading of the serialiser, and the two part company on small samples: MythicBotany
ships 2 infuser recipes, both with 3 ingredients, yet our own working Rites recipes use 4; Botania
ships exactly **1** terra_plate recipe. The observed sample sizes fall into two clean groups — 1
and 2, then 22 and up — so the floor sits in the gap, and it still keeps every arity rule the game
actually enforced on us: milling 231, pressing 39, deploying 112.

**Proven to fire.** A temporary fixture with one deliberately malformed recipe per family was run
and removed: E10 caught the missing `fromColor`/`toColor`, all four missing sequenced-assembly
keys plus the two fields that type does not have, and the 2-ingredient milling recipe. **9
problems on 3 bad recipes, 0 on the repaired pack.**

### One defect I introduced, caught by running the generators again

The three `incomplete_*` items went into the manifest as ordinary materials, so `gen_item_uses.py`
gave them **14 recipes** — including `shortcut` recipes that mint a half-finished assembler state
directly, and food/heal/enhance families that let the player trade one. They are progress states
that should never leave the machine. Fixed at both generators: `gen_ladder.py` marks them
`transitional`, `gen_item_uses.py` filters them out. Now 3 registered items, 0 uses, referenced
only by their own sequenced-assembly recipes.

> **Latent generator defect, noted not fixed:** `gen_ladder.py` appends to
> `items_manifest.json` only for ids not already present, so a *changed* definition of an existing
> item never propagates — the stale entries had to be deleted by hand before the flag would land.
> Worth repairing before the manifest is edited again.

**Validation:** `check_era.py --all` **0** (459 recipes parsed, 366 schema-checked) ·
`check_worldgen.py` **0** · `check_feature_order.py` **0 cycles** · `check_dependency_ranges.py`
**0** · **448 artifacts byte-identical** after re-running all ten generators.

**Not run:** any of it in a game. B-41 was found at runtime and its repair is **static only** —
level 4 stays `rejected at runtime` until a boot shows 0 `Error parsing recipe alfheim:` lines.
The Fey Altar correction and the sequenced-assembly recipes are the two most likely to need a
second pass, because both were diagnosed from a jar rather than observed working.

---

## Crafting-method audit, the MMO bridge, and Era I begun — 2026-09-03

**User asked** whether the recipe set actually uses all the pack's crafting methods, and to wire
the new ores and crystals into it, add Mine and Slash conversions, and begin the quest expansion.

### The audit — the answer was "partly", and the numbers say where

Not "only three": the era ladder proper already rotated **23 distinct methods across 86 recipes**,
nothing above 10.5%. That work was real. But pack-wide the picture was bad, and one file was why:

| | Before | After |
|---|--:|--:|
| distinct methods pack-wide | 20 | **30** |
| top single method | 56% (shapeless) | **16%** |
| top four combined | 82% | **54%** |
| `30_item_uses.js` methods | **1** | **13** |

`30_item_uses.js` emitted 238 shapeless recipes — 54% of everything the pack shipped, all one
method. It was the single thing flattening the pack's crafting variety.

### Ores and crystals now carry the recipes

They did not before: **crystal shards appeared in zero recipes** outside their own geodes, and
quickened blooms in none outside the Rites. The ladder predates both.

- `MULTIPLIER` retargeted off `minecraft:raw_*` onto **quickened blooms** — which also closes
  **B-48**, since raw ore stopped having an Alfheim source when the vanilla layer was retired.
- Crystal shards seeded into `ENHANCER` and `REAGENT`, each alignment feeding the economy it
  belongs to.
- Coverage is now **12/12 blooms and 6/6 crystals**, and it is structural: table selection was
  changed from hash-modulo to **round-robin**, because a hash is deterministic but not *covering* —
  it had left 7 blooms and 1 crystal unreachable no matter the seed.

### The Mine and Slash bridge — `14_mmo_bridge.js`

`INSTRUCTIONS.md` §2.2 says the Wound is not a side system, but its economy was sealed: 316 items
that never touched anything a spine produced. 12 conversions now bridge it — 6 outward (shards buy
orbs, all six alignments), 6 inward (essences pay out in Alfheim materials). **Every one runs
through a spine station**, never a crafting table, per §2.3.

### One regression I introduced, caught by the checker

Routing the `shortcut` family through the single-input helper silently dropped its 4× cost and its
mana powder, making it identical to the ladder step it exists to bypass. `check_era.py` **E7** flagged
two duplicates. Shortcut now has its own emitter that keeps the cost.

### Era I begun — 17 → 29 quests

`build_quest` gained a `guide` track (optional, gear-shaped, gates nothing). Twelve Guides authored
in Velrous's voice, covering the mechanics nothing else explains: why there is no metal · the
Steeping · where petals come from · three energies · the gate runs outward · reading a geode and
its surface sign · the Apothecary · why a spreader will not fire · generating vs functional flowers
· the Archive Groves · the five deficiencies · levels and orbs.

Target is 60. **Era I should stay the proving ground until B-55 is settled.**

### B-55 — and it blocks Eras II–X

Checking the id-stability claim rather than assuming it showed it is **false**. The generator is
deterministic, but the *round trip* is not: FTB reassigns a subset of ids on load, in both
directions — `shelter` keeps its quest id and loses its task id, `spiders` the reverse, and the
`era_1` **chapter id** changes outright.

Not hypothetical: `saves/New World/ftbquests/<uuid>.snbt` keys progress by id and its `started` set
holds `5F04313E8BBC9035`, which after regeneration exists nowhere in `config/ftbquests/`.

**Costs nothing today** — level 11 deferred, never played, two-quest test world. **Would cost a
player's whole run after release.** `ERA_EXPANSION.md` §2 and §6 corrected; the stronger claim must
not be restored without evidence from a booted game.

**Validation:** all four checkers **0**; **438 artifacts byte-identical** after re-running all
eight generators. **Not run:** any of it in a game.

---

## The Compendium, and the MineColonies plan — 2026-09-03

**User:** documentation for every custom feature inside the quest book, *"other than just looking at
JEI and hoping they can figure it out"* — and a **plan** (explicitly not an implementation) for
elven MineColonies theming.

### Built — the Compendium (B-53)

A second FTB Quests chapter group, **57 entries across 6 chapters**. Generator
`tools/gen_compendium.py`; design `COMPENDIUM.md`.

| Chapter | Entries |
|---|--:|
| How This Pack Works | 4 |
| The Twelve Blooms | 12 |
| The Four Rites | 4 |
| Crystallised Mana | 13 |
| The Archive Groves | 8 |
| The Sixteen Biomes | 16 |

**Facts generated, prose authored** — every number is read from the manifests the implementation is
generated from, so the docs cannot drift. All entries `optional: true`; the Compendium gates
nothing.

**Ownership change:** `chapter_groups.snbt` now belongs to `gen_compendium.py` (it declares both
groups); `gen_quests.py` no longer writes it. Two generators writing one file is how a group
disappears on whichever ran last.

**Two generator defects caught while building it:** the argparse namespace `a` was shadowed by a
geode-pair unpack (`a, b = g['pair']`), and the Rite numeral was derived from dict index, which
quietly depended on where the manifest's `_comment` key sat. Both fixed; numerals now explicit.

### Planned only — elven MineColonies (B-54)

`MINECOLONIES_ELVES.md`. Researched against the jars, and two brief assumptions did not survive:

- **`richs_races_wood_elves` is an MCreator mob entity**, not a race or citizen system. Six 64×64
  player-format skins against MineColonies' 128×64 citizens — a visual reference, not a template.
  `license="Not specified"`.
- **Pointed ears are model geometry.** No datapack or resource pack can produce them. Any promise
  of visibly elven citizens from data alone is a promise that cannot be kept.

Against that: **MineColonies already ships `citizennames/elf.json`** — 104 male, 110 female, 237
surnames. The most visible piece of theming is a setting, not a feature.

Four tiers: 0 name file (minutes) · 1 datapack visitors + research branch gated on spine materials
(a day, best value) · 2 programmatic citizen reskin (days, capped) · 3 Structurize building style
(weeks, deferred).

**Blocked ahead of all of it:** whether MineColonies functions in a non-Overworld dimension. It is
the mod flagged as most likely to hardcode `Level.OVERWORLD`. That sweep stays ahead of this plan.

**Validation:** `check_era.py --all` **0** with the six new chapters present; `gen_quests.py`
parses and still emits its 3 chapters / 61 quests.

---

## The Five Deficiencies and the Void Verge — 2026-09-03

**User:** negative biomes — Starved, Burned, Infested, Decayed — and a Void where the world ends in
a ragged cliff over floating mana-rich islands. Design: `DEFICIENT_BIOMES.md`.

Alfheim: **11 biomes → 16**, layer **13 bands → 18**. Four deficiencies in narrow climate corners;
the Void Verge claims the outer fifth of continentalness. Seventh geode **the Rim**
(Duskglass ∣ Galeglass) generates only in the void, 1 in 3 chunks — the richest ground in Alfheim
and the hardest to stand on.

### The void, and the one thing that makes it possible

Density functions **cannot read biomes**, so a "void biome" is two things that must be made to
agree. They are driven from the same signal: `mythicbotany:alfheim_continentalness`, which is what
the biome layer already selects on. The datapack overrides `mythicbotany:alfheim_final` — one file,
not the whole noise settings — wrapping `min(alfheim_initial, alfheim_caves)` in a `range_choice`.
Outside the void band nothing changes at all.

```
mask     = cache_2d( alfheim_continentalness + 0.035 * noise(surface) )   ← ragged, not contoured
islands  = 2.0 * noise(cave_cheese, xz 1.0, y 0.8) - 1.35                  ← sparse blobs
y_window = min( grad(y20→50: -1→1), grad(y110→150: 1→-1) )                 ← float y50..110
```

Islands are **livingrock**, the dimension's own `default_block`, so they are mana-bearing by
construction and every ore and geode feature targeting `#mythicbotany:base_stone_alfheim` works on
them unchanged — the "mana and mineral rich stone" obtained by not fighting the dimension.

### New guard — W7, and why it exists

`VOID_TERRAIN_MAX (-0.86)` must be strictly inside `VOID_BIOME_MAX (-0.80)`. That ordering means
all void terrain sits inside the void biome, leaving a 0.06 shore of void biome with ordinary
ground. **Reversed, the floor vanishes under a forest** — corruption rather than a view, invisible
until someone walks into it. `check_worldgen.py` W7 asserts the ordering and that the island window
is non-empty; both proven to fire on synthetic faults.

### Cleanup

69 lines of `SCARCE_ORES` / `ORE_DISTRIBUTION` / `ORE_BIOME_TAGS` removed from
`gen_alfheim_biomes.py` — dead tables describing the vanilla ore layer retired earlier today.

### Not built, deliberately — B-52

**Void structures** need an NBT pipeline and belong in their own unit. **A void sea** needs a mod:
**DNS resolves from this machine** (the "no network" note in project memory is stale), so the
environment does not block it — process does. A jar is a pack composition change and
`tools/check_incoming_mod.py` runs first. Name the mod and it proceeds.

**Validation:** `check_feature_order.py` **0 cycles**; `check_worldgen.py` **0** including the new
W7; `check_era.py --all` **0**; `check_dependency_ranges.py` **0**; **419 artifacts byte-identical**
after re-running all four generators.

**Not run:** everything. The void density function is the single riskiest file in the datapack — a
malformed one fails world creation outright, and no static check can prove the terrain it produces
is playable rather than merely legal.

---

## Crystallised mana, and the groves get saplings — 2026-09-03

**User:** bifurcated geodes of elementally-aligned mana crystals, far more plentiful than vanilla
amethyst, with a surface feature marking a geode below — plus *"do our custom trees have their own
saplings?"*

**They did not. Now they do (B-49 closed).** KubeJS 2001.6.5 has no `SaplingBlock` builder and no
`TreeGrower`, which was the original blocker — but `randomTick` plus
`BlockContainerJS.offset(Direction, int)`, both confirmed present in the jar, are enough to place a
trunk and canopy directly. `growGrove()` uses each tree's own worldgen numbers and checks headroom
before writing anything. Grove leaves drop their own sapling at 0.03, rarer than the foreign seeds
at 0.055.

**Six crystals, six bifurcated geodes.** Design `ORE_SUPPLEMENTATION.md` §9.

| Built | Detail |
|---|---|
| 6 crystals × 3 blocks + 6 shards | Emberglass, Tidewake, Rootglass, Galeglass, Duskglass, Dawnglass |
| Budding blocks | grow clusters on random tick; drop nothing without Silk Touch |
| 6 geodes, 12 features, 12 modifiers | deep in `local_modifications`, marker in `top_layer_modification` |
| Plenty | mean **1 in 5.6** eligible chunks — vanilla amethyst is 1 in 24 |

**Bifurcation is spatial, not statistical.** `minecraft:noise_threshold_provider` samples a noise
field *at each block position*, so at `scale: 0.08` a 10–16 block geode straddles one boundary and
comes out in halves with a seam. `weighted_state_provider` — the obvious first choice — would have
given salt-and-pepper. Inner and alternate-inner layers share one seed so budding blocks land on
the correct side.

**The surface marker cannot produce a false positive.** `environment_scan` caps `max_steps` at 32,
which is why the geodes are anchored to the *local surface* (`heightmap` + negative
`random_offset` of 14–28) rather than to absolute depth. The chain is heightmap → scan down for
`#alfheim:budding_crystals` → heightmap again; the scan moves only Y, so the second heightmap
returns to the surface at the same x/z, and a failed scan aborts the placement entirely.

### Two defects in my own generator, caught before they shipped

1. **`hash()` is salted per process in Python**, so the geode noise seeds would have differed on
   every run and the generator would have stopped being reproducible. Replaced with a SHA-1
   derivation; verified stable across two runs.
2. **An empty `LootBuilder` consumer was an API guess.** The budding blocks' drops-nothing tables
   are now written as plain datapack files (`{"type":"minecraft:block","pools":[]}`), which is
   unambiguous.

**Validation:** `check_feature_order.py` **0 cycles** (924 edges over 590 placed features);
`check_worldgen.py` **0**; `check_era.py --all` **0**; `node --check` clean on all scripts;
**403 generated artifacts byte-identical** after re-running all four generators.
**Not run:** any of it in a game.

---

## The Archive Groves — petals from leaves, and three trees, 2026-09-03

**User:** *"We should add petal variety to the break block recipe of leaves for all trees of
Alfheim… We should also include various types of trees of our own custom generation, to give
randomized overworld saplings."*

This is the real fix for B-46. The spawnlist tag makes mystical flowers *generate*; this makes
petals **renewable by an activity the player is already doing**. Design: `ORE_SUPPLEMENTATION.md`
§8. Manifest `tools/groves_manifest.json`, generator `tools/gen_groves.py`.

| Built | Detail |
|---|---|
| 5 mod leaf tables extended | dreamwood + 4 archwood, each dropping its own two petal colours |
| 3 trees | Emberbark, Gloambark, Hushbark — 6 blocks, 9 textures |
| Petal coverage | **16/16 colours** now have a leaf source |
| Vanilla saplings reachable | **7** — acacia, birch, cherry, dark oak, jungle, oak, spruce |
| Worldgen | 3 tree features ×2 + 3 `zz_grove_*` modifiers, one feature each |

**The mod loot tables are copied verbatim out of their jars and appended to, never retyped.**
Proven on `blue_archwood_leaves`: 2 original pools kept, drops now
`blue_archwood_leaves, blue_archwood_sapling, blue_petal, light_blue_petal, stick`. Retyping would
have deleted the archwood sapling — a Rite I reagent. Each table carries an `__alfheim` provenance
block with the source jar's SHA-1 so drift after a mod update is visible without diffing.

**Why the trees matter beyond petals:** no vanilla tree generates in Alfheim, so before this there
was no oak, no apple and no plank variety at all — and `minecraft:apple` alone is used 13 times in
the existing chains. The grove leaves drop *plantable* vanilla saplings, so the player bootstraps a
normal wood economy from a foreign-seed drop.

**Constraint accepted, recorded as B-49:** the groves cannot be replanted. KubeJS 2001.6.5 has no
sapling builder and no `TreeGrower` binding — verified against the jar, not assumed.

**Validation:** `check_feature_order.py` **0 cycles** (63 modifiers, up from 60);
`check_worldgen.py` **0**; `check_era.py --all` **0**; 68 datapack JSON files parse; `node --check`
clean. **Not run:** any of it in a game.

---

## DECIDED — the Alfheim Gate opens in Era IV, 2026-09-03

**User:** *"Yeah I changed my mind there. Record the earlier gate as when the gate opens."*

The longest-standing open question in the project is closed. Of the two candidate eras the
**earlier** one wins: the gate is built, lit and traversable in **Era IV**, and the 2026-09-02
instruction that it is "completable only in Era VI" is **withdrawn**. It must not be reinstated
from the older record — three documents carried the Era VI reading and all three are now corrected.

**Propagated to six documents,** so no reader can pick up the retired version:

| Document | Change |
|---|---|
| `CAMPAIGN_ERAS.md` §3 Era IV | ⚠ UNRESOLVED block replaced with the decision record |
| `ERA_EXPANSION.md` §7, §8 | blocking decision removed; authoring order renumbered |
| `BACKLOG.md` B-36 | retitled to Era IV; gating material and accept criteria retargeted |
| `IMPLEMENTATION_PLAN.md` | Era VI re-themed to the frontier; "Era VI gate" → "Era IV gate" |
| `WORLD_STRUCTURE.md` | Midgard reachable Era IV+, in two places |
| `PROCESS_INDEX.md` | `botania:elven_trade` mandatory from Era IV |

**The gating material moved with it,** and the roster had already anticipated this: B-36 keyed the
final component to Era VI's capstone `alfheim:wildmarch_sinew`; it is now Era IV's capstone
**`alfheim:gatewrought_cord`**, whose tooltip has read *"Era IV. Elven work, finished on the far
side of the gate"* since `items_manifest.json` was authored.

**What it unblocks:** 132 quests. `ERA_EXPANSION.md` §7 now runs Era I → X with no decision gate,
and Eras IV and VI author in their natural position instead of last.

---

## Ore economy redesigned — the Twelve Blooms, 2026-09-03

**User instruction:** *"I want custom ores that are then magically converted into base ingredients
for all of our industrial and elf projects… I don't want to use vanilla ores because that just
reskins Alfheim as the Overworld."*

Design records written: `alfheim_reclaimed_design/ORE_SUPPLEMENTATION.md` (the twelve blooms, the
four Rites, coverage, implementation order) and `ERA_EXPANSION.md` (215 → 660 quests, the taxonomy,
the curriculum). Implementation begun and statically clean.

### What was built

| Artifact | State |
|---|---|
| `tools/blooms_manifest.json` | 12 blooms, source of truth |
| `tools/gen_blooms.py` | regenerates every artifact below from the manifest |
| 12 ore blocks, 24 items, 36 textures, 24 item models | worktree |
| `kubejs/startup_scripts/11_blooms.js` | worktree |
| `kubejs/server_scripts/11_bloom_loot.js` | `addSimpleBlock`, API confirmed in the KubeJS jar |
| `kubejs/server_scripts/12_rites.js` | 4 Rites × 12 blooms + rendering = 62 recipes |
| 24 worldgen features, 4 biome modifiers, 4 tags | worktree |
| Vanilla ore layer | **retired** — 20 files preserved with md5s in `quarantine/vanilla_ore_layer_2026-09-03/` |
| `tools/gen_alfheim_biomes.py` | `ore_files()` repaired so it no longer *regenerates* the retired layer |

### Two defects found by building it

**B-46 — no petals in Alfheim.** No `botania:*` feature generates in any of the eleven biomes.
`mythicbotany:motif_flowers` places only `motifDaybloom` and `motifNightshade`, and neither has a
loot table. Petals gate the Pure Daisy, the Apothecary, the twig wand and the Mana Spreader — the
whole Spine of Leaf — and Era I's authored quests already require them. Fixed by adding
`#mythicbotany:alfheim` to `#botania:mystical_flower_spawnlist`, which is the tag Botania's own
modifier keys off, plus a starting-kit safety net (`KIT_FLAG` → `v2`).

**A feature-order cycle, introduced by that very fix, caught before boot.** Adding mystical flowers
to Alfheim made `alfheim:bloomfall_vale` assert `placed_mixed_archwoods → mystical_flowers` while
125 other biomes asserted the reverse chain. Cause: Ars Nouveau's `rare_archwood_mix` and Nature's
Aura's `aura_bloom` both target `#minecraft:is_overworld`, which Alfheim is not in, so our biomes
listed those features **inline** — and an inline feature sorts before every modifier-appended one.
Repaired at the generator: the two tree features moved out of the biome JSONs into `zz_`-prefixed
modifiers of our own, which sort after `rare_archwood_mix` and land in the position the rest of the
world agrees on. `check_feature_order.py`: 1 cycle → **0**.

### `check_worldgen.py` W4 rewritten — the invariant that should have existed

W4 checked for `minecraft:copper_ore` and friends *generating*. After the retirement that invariant
would have failed a perfectly playable world, and — worse — it would pass a world where the ore
generates but nothing can process it. It now checks **reachability**: base ingredient → bloom →
ore block → does that block generate in an Alfheim biome. Proven to fail on synthetic bad input
(`palebloom` reassigned to a non-existent biome group → `W4 minecraft:iron_ingot is unreachable`).

### Validation run

| Check | Result |
|---|---|
| `check_feature_order.py` | **0 cycles**, 298 biomes, 903 edges, 60 modifiers applied |
| `check_worldgen.py` | **0 problems**; all 12 blooms place; 3 early essentials reachable |
| `check_era.py --all` | **0 problems**; 215 quests, 10 eras |
| JSON parse | 58 datapack files, 0 bad |
| `node --check` | 4 scripts, all clean |
| Recipe schemas | all 6 types read from the shipping jars before emission (B-41 discipline) |

**Not run:** levels 8–12. No boot since these changes. The blooms have never generated, no Rite has
ever been crafted, and no bloom texture has been seen in-game.

---

## B-44 PROVEN — the player wakes in Alfheim, 2026-09-03 16:07

**Read from the save, not from a log line:**

```
Dimension        mythicbotany:alfheim
Pos              [-688, 118, 766]
SpawnDimension   mythicbotany:alfheim     SpawnForced 1
spawn flags      {'alfheim_home_spawn_v2': 1}
chunks           mythicbotany:alfheim -> 12 region files, minecraft:overworld -> 11
```

`python tools/check_spawn.py` → **0 problems** (before S5 was added). The `_v2` flag is present,
which by construction can only have been written after `confirmAndAnchor` observed the arrival:

```
[16:07:59] 02_spawn_dimension.js#96: [Alfheim Reclaimed] mrcalzon02 confirmed in
  mythicbotany:alfheim (first join); spawnpoint anchored there.
```

`execute in <dim> run tp` does cross dimensions on this build, and `scheduleInTicks` exists —
both previously unproven. **Level 9 check 9 passes, and 9e is anchored** (`SpawnDimension` is
Alfheim, so dying bedless returns home). The premise of the pack works.

## The lock that blinds the player for doing the intended thing — 2026-09-03 16:11

The spawn fix worked and the player was **permanently blinded** the moment they arrived.

```json5
// Whether players that manage to get to alfheim via another mod but have not drunk the mead
// of kvasir should get a blindness effect.
"lockAlfheim": true,
```

MythicBotany ships that guard to stop people skipping progression to reach Alfheim early. **This
pack puts the player there on first join by design**, so the guard fires on the *intended* path.

The signature in the save is why it reads as a rendering fault rather than a config toggle:

```
{'forge:id': 'minecraft:blindness', 'Ambient': 1, 'ShowIcon': 1,
 'ShowParticles': 0, 'Duration': 59, 'Amplifier': 0}
```

`Duration: 59` — under three seconds, reapplied forever. `Ambient: 1` and `ShowParticles: 0` —
environmental, no visual source. Nothing in the log mentions it at all.

**Set to `false`.** Original preserved in the session scratchpad. `check_spawn.py` grew an **S5**
that fails on both the config key and a blinded player, so a config reset or a MythicBotany update
that restores the default cannot silently make the pack unplayable again. Validated both ways: with
the key flipped back it reports the config problem, with it off it does not.

**The residual blindness on the existing character is stale save data**, written while the lock was
live. It stops being reapplied on restart and expires in about three seconds.

**This is now doctrine** — `INSTRUCTIONS.md` §6 — because it is one key, it is shipped `true`, and
its failure mode is a player who cannot see and a log that says nothing.

## B-44 rewritten — the spawn now verifies before it records, 2026-09-03 15:20

`kubejs/server_scripts/02_spawn_dimension.js` v2. Three faults, three fixes:

1. **`execute in <dim> run tp <name> 0 320 0` first**, then `spreadplayers` *within* Alfheim for a
   safe surface landing. `spreadplayers` alone never crossed the dimension boundary — it sampled
   Alfheim's terrain and dropped the player at those coordinates in Midgard.
2. **Arrival is observed, not assumed.**
   `execute in mythicbotany:alfheim if entity @e[type=minecraft:player,name=<name>,limit=1]` — `@e`
   is scoped to the execution dimension, so this is a dimension test written entirely in vanilla
   commands, with no KubeJS accessor whose shape has moved between builds.
3. **The flag latches only on success**, inside `confirmAndAnchor`. A failure leaves it clear, logs
   loudly, and retries on next login rather than stranding the player forever.

Renamed to `alfheim_home_spawn_v2` — v1 meant "commands issued", v2 means "arrival observed" — so
any character v1 stranded is re-sent automatically. `server.getPlayer` was removed from a first
draft: no precedent in this pack, and a null return would have re-spread the player every login.

**New checker: `tools/check_spawn.py`.** Reads the save rather than the log — S1 current dimension,
S2 respawn dimension, S3 Alfheim generated chunks, S4 the verifying flag latched. Validated in the
failing direction against `saves/New World (1)`:

```
S1  f1457c43 is in minecraft:overworld, not mythicbotany:alfheim
S2  f1457c43 respawns into minecraft:overworld ... dying bedless drops them in Midgard
S4  f1457c43 carries only alfheim_home_spawn_v1 -- set by the old script, which recorded
    success it never observed (B-44)
```

That is the answer to "how would we have caught this": by asking the save. The project now does.

**Static only.** `execute in <dim> run tp` is standard vanilla and `node --check` passes the script,
but neither the teleport nor `scheduleInTicks` has been observed on this KubeJS build. Both fail
safe. A fresh world is the acceptance.

| Check | Result |
|---|---:|
| `node --check 02_spawn_dimension.js` | OK |
| `check_spawn.py` vs the broken save | **3 problems** — fires correctly |
| `check_feature_order` / `check_dependency_ranges` / `check_worldgen` / `check_era --all` | 0 / 0 / 0 / 0 |
| kubejs datapack JSON | 114 files parsed, 0 bad |

## The game rewrites our quest source — found 2026-09-03 15:00

Running the validators after the Midgard change turned `check_era.py --all` from **0 problems to
42**, all `E9 quest has no id`. Nothing about the quests had changed; the config edit was unrelated.

**FTB Quests rewrites `config/ftbquests/quests/chapters/*.snbt` every time a world loads.** All ten
chapter files carry mtime 14:18 — world creation. It reorders every object's keys **alphabetically**
and expands minified objects across lines. Our generator wrote `title:` before `id:`; FTB writes
`description`, `id`, `rewards`, `shape`, `subtitle`, `tasks`, `title`.

**No content was lost.** `id: "062824AAEB36EF43"` is present on the quest the checker called
id-less. This was a **parser defect in `check_era.py`**, exposed rather than caused by the rewrite:
it opened a new quest record at every `title:` line and then claimed the next `id:`. With `id`
now preceding `title`, every quest's id was already gone by the time its record existed — and a
task's `title:` opened phantom quest records of its own.

Repaired with structural parsing: `lines_with_depth()` tracks brace depth outside string
literals, a quest is one balanced object directly inside `quests: [`, and `id`/`title` are read
only at the quest's own top level. Item and entity extraction now accepts both the minified form
our generator emits and the expanded form FTB rewrites it into.

| | Before the fix | After |
|---|---:|---:|
| Problems | 42 (all E9, all false) | **0** |
| Quests parsed | 24/era, inflated by task titles | **22/era, 215 total** |
| Quests with no id | 42 | **0** |

215 is exactly the figure this project recorded before the game had ever run, which is the
independent check that the parser is now right rather than merely quiet.

**The boundary this exposes.** `config/ftbquests/` is authored by `tools/gen_quests.py` and then
**owned and normalised by the game**. Anything reading it must read the game's form, not the
generator's. Regenerating quests will overwrite FTB's formatting, and launching will restore it —
that churn is expected and is not a defect.

## Midgard is Continuity Works only — user decision, 2026-09-03 14:57

**Why the anthology was invisible: arithmetic, not a defect.** Continuity Works was loaded,
patched, and registering its TerraBlender region correctly —
`Registered region continuityworks_biomes:overworld_templates to index 1 for type OVERWORLD` at
14:31:15 — with all 144 biomes enabled in `config/continuityworks-biomes-common.toml`, and its
`BiomeTemplateRegion` class does carry the anthology (`AnthologyBiomeCatalog`, `isAnthologyEnabled`,
`ENABLE_ABYSSAL_FAMILY`). It simply had **9%** of Midgard shared across ~144 biomes — about 0.06%
each — and the player had travelled ~2 km.

| Region | Was | Now |
|---|---:|---:|
| `minecraft:overworld` | 10 | **0** |
| `regions_unexplored:primary` | 11 | **0** |
| `regions_unexplored:secondary` | 8 | **0** |
| `regions_unexplored:rare` | 1 | **0** |
| `continuityworks_biomes:overworld_templates` | 3 | **20** |
| `ars_nouveau:overworld` | code | **code — cannot be weighted** |

CW share: 9% → **100%** of the configurable weight.

**Owned by `tools/set_midgard_biomes.py`** (`--show`, `--mode cw-only`, `--mode mixed`). It is a
tool and not a datapack because TerraBlender reads these weights from TOML at mod load; no datapack
can reach them. It rewrites one key per file in place, preserving comments, and reads back.

**Three consequences, all real:**

1. **Regions Unexplored now generates nothing** — 170 biomes loaded for no world content. B-05 is
   reopened with the opposite disposition: remove it, or accept it as inert.
2. **Ars Nouveau archwood stays.** `ArchwoodRegion` registers in code with no config key, so
   "CW only" means *CW plus archwood*. Removing Ars is not an option — Spine of Song.
3. **Unverified and the real risk:** with vanilla's region at 0, whether Midgard still gets oceans,
   rivers and beaches depends on whether TerraBlender backfills the parameter space vanilla was
   covering. This can only be settled by generating a world. Check with
   `/locate biome minecraft:ocean` before trusting the switch.

Generation only, and only for chunks not yet generated — `saves/New World (1)` keeps what it has.

## LEVEL 9 — WORLD GENERATED, 2026-09-03 14:18

**The pack generates a world.** First time in five attempts, and the first runtime evidence the
project has ever had about world generation. The player did **not** wake in Alfheim — that claim
was made here in error and is corrected below. See B-44.

| | |
|---|---|
| Save | `saves/New World (1)` |
| Created | 14:18:04; start region prepared 14:18:08–14:18:29, **20.5 s** |
| Crash reports | **0** — newest on disk is 13:57, the CW-4 crash |
| Midgard | `minecraft:overworld` — **13 region files, 18 MB** |
| Alfheim | `dimensions/mythicbotany/alfheim/region` — **1 region file, 2.2 MB** |
| Player | `mrcalzon02`, playerdata written, advancements earned 14:19–14:20 |
| Session | still running at 14:20:31, two clean `Saving and pausing` cycles |

> ### CORRECTION, 2026-09-03 14:40 — the home-dimension check did NOT pass
>
> This entry originally read "the player woke in Alfheim", citing:
>
> ```
> [14:18:39] 02_spawn_dimension.js#36: mrcalzon02 sent to mythicbotany:alfheim (first join)
> ```
>
> **That line is not evidence.** It is our own `console.info`, printed unconditionally after the
> commands are issued, and it says nothing about whether they succeeded. Reading the save says the
> opposite — see **B-44** below. The claim was wrong and the check is `rejected`, not `passed`.
>
> The lesson is the one this project keeps relearning in a new costume: a log line a script writes
> about itself is a statement of intent, not of outcome. Verify at the destination.

### What that settles, and what it does not

| Check | State |
|---|---|
| World creation completes | **PASSED** |
| Midgard generates | **PASSED** |
| Alfheim generates | **PASSED** — but as a side effect of the failed spawn, not because the player went there |
| 9 — player wakes in Alfheim | **REJECTED — B-44** |
| 9d — copper/iron actually findable | not verified — needs mining in-game |
| 9e — respawn returns home | not verified — needs dying bedless |
| 9f — Nether portal lit in Alfheim links to anything | not verified |
| 10 — villages generate ruined and clustered | not verified |
| Fly out and hold | not verified — **both earlier crashes landed ~625 chunks from spawn** |

Level 9 is therefore **partially passed**, not passed. The part that blocked everything else is
done; the substantive gameplay checks inside it are still open.

### The five attempts

| Attempt | Result | Cause |
|---|---|---|
| 1 | crashed | CW-1 — `minecraft:ore_diamond_medium` does not exist |
| 2 | crashed | CW-3 + ours — 5 feature order cycles in biome JSON |
| 3, 4 | crashed | CW-4 — two biome modifiers, one feature, inconsistent sort |
| **5** | **world generated** | — |

Each fault hid the next; `FeatureSorter` stops at the first one it reaches. That is why the
modifier-aware `check_feature_order.py` mattered more than any individual fix.

## Level 8 — PASSED at 14:18, one jar behind since 14:26

Previously `stale`. The same run booted **85** jars to the title screen and into a world with
**0 crash reports** and **27 ERROR lines**, none load-blocking: 16 `Invalid path in pack` from
mods shipping illegally-named files, 2 unparseable Iron's Spellbooks loot tables, 4 tag-loading
failures from one upstream defect (below), 2 JEI layout failures in **our** recipes, 2 hanging
entities at invalid positions, 1 Moonlight notice about Fabric API.

**JourneyMap 5.9.20 was installed at 14:26**, after that boot, so the load path is now 86 jars and
this evidence is one jar behind. Re-confirm on the next launch. Static checks on the new load path
are clean: 0 blocking dependency issues, 0 feature order cycles.

## Runtime found what static checks could not — 2026-09-03

`check_era.py --all` reports **0 problems**, and the game rejected **11 of our recipes at load.**
Level 4 is therefore `rejected at runtime`, not `passed (static)`. The checker validates that ids
exist and are reachable; it does not validate each recipe type's **schema**, and every failure
here is a schema failure.

| Family | Count | Message | Recipes |
|---|---:|---|---|
| `mythicbotany:infuser` | 5 | `Missing fromColor, expected to find a Int` | `era5/elementium_drawn`, `era7/emberbound_quenched`, `era8/rimebound_quenched`, `era9/gravegilt_quenched`, `era10/branch_cord` |
| `create:sequenced_assembly` | 3 | `Item cannot be null` | `era8/rimebound_rebound`, `era9/gravegilt_stilled`, `era10/crown_rebound` |
| `create:milling` / `create:pressing` | 2 | more item inputs (2) than supported (1); pressing also given a meaningless duration | `era5/annealed_plate`, `era8/frost_shard` |
| Feywild Fey Altar | 2 | `ArrayIndexOutOfBoundsException: Index 4 out of bounds for length 4` in `FeyAltarRecipeCategory` | `era6/march_hide`, `era10/crown_drawn` |

The Fey Altar pair is arity, not schema: ours pass 5 ingredients and Feywild's category indexes 4.
JEI catches it, so it is a display failure — but whether the altar itself accepts a fifth
ingredient has not been tested.

Also confirmed at runtime: **B-30**, `mythicbotany:feysythia` is uncraftable because its recipe
calls for `feywild:lesser_fey_gem`, which Feywild 5.5.5 does not ship.

### One upstream defect worth fixing locally

`jaffabricate` ships `data/minecraft/tags/items/leaves.json` pointing at `#jaffabricate:orange_leaves`
and **never ships that item tag** — only the block version. So the **item** tag `minecraft:leaves`
fails to load, and takes `minecraft:completes_find_tree_tutorial`, `minecolonies:fletcher_ingredient`
and `minecolonies:compostables` down with it. One datapack file fixes it. B-43.

## Level 9, attempts three and four — crashed on CW-4, 2026-09-03 13:55 and 13:57

```
Description: Exception generating new chunk
java.lang.IllegalStateException: Feature order cycle found, involved sources:
  [continuityworks_biomes:ash_wastes, continuityworks_biomes:quarry_megaplex]
    at FeatureSorter.m_220603_(FeatureSorter.java:100) -> ChunkGenerator.m_223094_
```

Reports: `crash-reports/crash-2026-09-03_13.55.59-server.txt`, `…_13.57.22-server.txt`.

**The two named biomes have byte-identical `features` arrays.** The contradiction was not in the
files at all — it was in the Forge biome modifiers applied on top of them.

| Modifier (sorted by file path) | Adds | To |
|---|---|---|
| `anthology_land_topology` | `land/topology` | `#anthology` — 128 biomes |
| `biome_cave_networks` | `caves/biome_network` | `#all_primary_biomes` — all |
| `foundation_land_topology` | `land/topology` | `#templates` — 8 biomes |

`forge:add_features` **appends** to the end of a step, and Forge applies modifiers in order of
**file path across every mod** — `RegistryDataLoader` reads a `TreeMap` over `ResourceLocation`,
and `ResourceLocation.compareTo` compares path first, namespace second. So an anthology biome gets
`land/topology` before `caves/biome_network` and a template biome gets the reverse. 128 biomes
assert one order, 8 assert the other.

**Fixed** by renaming both `land/topology` modifiers to a shared `land_topology_` prefix, making
them adjacent in the global sort. No byte of content changed — only the zip entry name, which is
the registry key that decides order. Recorded as **CW-4**;
`…+cw1patch+cw3patch+cw4patch.jar`, md5 `b2c6e3bf9ab2045410007ac15ba83720`, built from the
pristine original.

### The checker was wrong, and that is the more important finding

`tools/check_feature_order.py` reported **0 cycles** on the jar that then crashed twice. It read
biome JSON and nothing else, so the entire biome-modifier layer — 57 feature-affecting modifiers
across 20 mods, 2,667 biome-steps — was invisible to it. The static claim in the previous entry
was honestly labelled static, but the *model behind it was incomplete*, which is worse than a
missing check because it reads as coverage.

It now applies `forge:add_features`, `forge:remove_features` and
`farmersdelight:add_features_by_filter` in the game's own path-sorted order before running the
sort, and it **reproduces this crash exactly** from the unpatched jar: one cycle, step 2, the same
two features, `ash_wastes` among the 8 and `quarry_megaplex` among the 128.

That reproduction is the validation that counts. A synthetic self-test proves the graph code
works; predicting the crash the game actually threw proves the model is right. Both are kept.

It also now parses commented JSON (Forge reads these files leniently;
`irons_spellbooks:necromancer_spawns` ships `//` comments), so no modifier is skipped silently.
Every one of the 194 modifiers in the load path is now read and classified.

### Evidence

| Check | Result |
|---|---:|
| `check_feature_order.py` against the **pre-CW-4** jar | **1 cycle** — reproduces the crash |
| `check_feature_order.py` against the installed jar | **0 cycles** |
| `check_feature_order.py --self-test` | PASSED |
| Modifiers read | 194 total, 57 affect features, **0 unmodelled** |
| `check_incoming_mod.py <jar>` | 0 fail, 0 warn, 6 pass |
| `check_dependency_ranges.py` | 0 blocking, 0 quarantine conflicts |
| `check_worldgen.py`, `check_era.py --all` | 0 problems |
| Jar patch | 307 entries, 2 renamed byte-identical, 0 unintended byte changes, reproducible |

**Static only.** Level 9 remains `not run`.

## Level 9, attempt two — crashed on feature order in biome JSON, 2026-09-03 13:18

```
Description: Exception generating new chunk
java.lang.IllegalStateException: Feature order cycle found, involved sources:
  [continuityworks_biomes:terraced_vineyard, ars_nouveau:archwood_forest]
    at FeatureSorter.m_220603_(FeatureSorter.java:100) -> ChunkGenerator.m_223094_
```

`minecraft:overworld`, stock `NoiseBasedChunkGenerator`, chunk −1/−1, 625 chunks, level "New World".
Report: `crash-reports/crash-2026-09-03_13.18.07-server.txt`.

**Root cause.** `FeatureSorter` does not generate a biome's features in the order that biome lists
them. It flattens every loaded biome into ONE global order per generation step, by topologically
sorting the "A immediately before B" constraints each biome asserts. Two biomes naming the same
pair in opposite orders make that order impossible. Like CW-1 it throws lazily from
`ChunkGenerator`, so it lands on world creation with every static check green; unlike CW-1 it is
not seed-dependent.

**The crash report names only the first cycle.** Simulating the sorter over the whole load path
found **five** — four in Continuity Works, one ours:

| Cycle | Deviant | Consensus |
|---|---|---|
| `patch_sugar_cane` ↔ `patch_pumpkin` | 41 CW biomes, pumpkin first | vanilla ×41, Regions Unexplored ×52, CW's own ×22, Ars Nouveau ×1 |
| badlands trio | CW `rocky_badlands` | `minecraft:badlands` ×3 |
| `flower_meadow` ↔ `patch_grass_plain` | CW `flowering_meadow` | `minecraft:meadow` |
| savanna trio | 25 CW biomes | `minecraft:savanna` ×2 |
| `loose_dreamwood_trees` ↔ `motif_flowers` | **`alfheim:bloomfall_vale` — ours** | `mythicbotany:alfheim_plains` |

**The fifth is the one that mattered most.** It is in Alfheim's own biome layer, so it would have
crashed the dimension the player wakes in. It stayed invisible because the Overworld generates
first and crashed first — patching Continuity Works alone would have moved the crash, not removed
it. Both had to be found together, which is why the fix was a whole-load-path simulation rather
than a reading of the crash report.

### Ours — repaired at the generator

`tools/gen_alfheim_biomes.py` now carries a `FEATURE_ORDER` table read off MythicBotany's five
jar-owned biomes (`alfheim_grass` first; `loose_dreamwood_trees` before `motif_flowers`;
`extra_gold_ore` last in the ore step) and sorts every step through it. A feature with no declared
rank is a hard error rather than a silent cycle. Regenerating changed **two lines in one file**,
`kubejs/data/alfheim/worldgen/biome/bloomfall_vale.json`.

### Continuity Works — CW-3, patched locally

| | |
|---|---|
| Scope | **67** of 146 biomes, 67 step lists reordered (plus CW-1's 136) |
| Tool | `tools/patch_continuity_works.py`, now applying CW-1 and CW-3 in one pass |
| Input | the **pristine** original in `quarantine/`, md5 `32b6003bf04692f09708415442c85547` — not a patch chained onto a patch |
| Output | `mods/ContinuityWorks-Forge-1.20.1-0.3.0-rc.2+cw1patch+cw3patch.jar`, md5 `063438d8b41444be295b0284d051aad4` |
| Reference order | derived at patch time from every biome source except that jar — 152 biomes, acyclic on its own, so adopting it cannot introduce a new contradiction |
| Method | permuted ids written back into the **same quote slots**; no whitespace, comma or line break moves |
| Verify | 307 entries, **0** unintended byte changes; blanking every feature string leaves before and after byte-identical; a second run reproduces the jar with 0 differing entries |

Numbered CW-3 because CW-2 is a withdrawn architecture ask and numbers are not reused. The
superseded `+cw1patch` jar was moved to `quarantine/`; it is not a defective original and may be
deleted. **Backport pending — B-39.**

### Guard added — `tools/check_feature_order.py`

Simulates `FeatureSorter` over the vanilla client jar, all 85 mod jars and our datapack: 298
biomes, 789 constraints over 516 placed features. Reports each cycle with the step, the features,
and how many biomes assert each edge, so the deviant side is evident rather than arguable.
Validated both ways — `--self-test` fires on a synthetic contradicting pair; the real run went
**5 → 0**.

**Why no existing checker caught it.** `check_worldgen.py` resolves ids, and every id here is
valid; it is their *sequence* that is impossible. `check_incoming_mod.py` reads one jar, and a
cycle is a property of the whole load path — four of these five needed vanilla's own biomes in
the comparison to appear at all.

### Evidence

| Check | Result |
|---|---:|
| `python tools/check_feature_order.py` | **0 cycles** (was 5) |
| `python tools/check_feature_order.py --self-test` | PASSED — fires on a known cycle |
| `python tools/check_incoming_mod.py <patched jar>` | 0 fail, 0 warn, 6 pass |
| `python tools/check_dependency_ranges.py` | 0 blocking, 0 quarantine conflicts |
| `python tools/check_worldgen.py` | 0 problems |
| `python tools/check_era.py --all` | 0 problems |

**Static only.** Nothing here has been seen running. Level 9 remains `not run`, not `passed`.

## CW-1 root-caused and patched — 2026-09-03

**It was one bad string.** `minecraft:ore_diamond_medium` does not exist in Minecraft 1.20.1.
Vanilla ships exactly `ore_diamond`, `ore_diamond_large` and `ore_diamond_buried` — all three
already present in the same list, either side of the invented one.

A datapack biome naming a `placed_feature` nothing provides gets an unbound `Holder.Reference`.
Nothing complains at load; `FeatureSorter` throws the first time a chunk resolves that biome. Hence
625 chunks out, and seed-dependent.

Measured rather than assumed: **5,219** feature references across the 146 biomes, checked against
vanilla + 84 mods + CW itself. **Exactly one** id resolved against nothing, in 136 biomes.

**The prior diagnosis in this project was wrong** — it speculated about code-side holder
construction via `AnthologyBiomeCatalog` and a captured `BuiltinRegistries` snapshot. The biomes are
ordinary datapack JSON; the mod's Java is not implicated. Recorded rather than deleted, because the
symptom convincingly imitates a registry-lifecycle bug.

**Patched at the owner's instruction** — Continuity Works is their own mod, so `INSTRUCTIONS.md`
§5.1 was added to draw the first-party / third-party line rather than quietly breaking §6.5.

| | |
|---|---|
| Tool | `tools/patch_continuity_works.py` — re-runnable, not a hand edit |
| Method | entry **deleted**, not substituted — substituting would double diamond generation |
| Installed | `mods/ContinuityWorks-Forge-1.20.1-0.3.0-rc.2+cw1patch.jar` |
| Original | preserved in `quarantine/`, md5 `32b6003bf04692f09708415442c85547` |
| Verify | 307 entries, **0** unintended byte changes, 5,219 → 5,083 refs, 0 unresolvable |
| Acceptance | `check_incoming_mod.py` → 0 fail / 0 warn / 6 pass; original → 1 fail |

**Backport pending.** The fix belongs in Continuity Works' source; drop the local patch the moment
an upstream build carries it, so the two cannot diverge.

**Guard added:** `check_incoming_mod.py` now fails any jar whose biomes reference a
`placed_feature` nothing provides — the check that would have caught this before install. It also
now counts biome *definitions* rather than definitions plus tag files, which is where the wrong
"176 biomes" figure came from. Its obsolete `#mythicbotany:alfheim` warning was removed: CW's
biomes belong in Midgard, so appending to Alfheim's tag would now be the defect.

## Architecture revised — Alfheim is no longer the Overworld

Authorised by the user 2026-09-02, and it is doctrine, so `INSTRUCTIONS.md` §1 and §4 were changed.

| | Was | Now |
|---|---|---|
| Alfheim | `minecraft:overworld`, via a world-preset override | **`mythicbotany:alfheim`** — the mod's own dimension |
| Midgard | A new dimension to be authored, from Continuity Works | **`minecraft:overworld`** — vanilla, left alone |
| Player spawn | Vanilla | `02_spawn_dimension.js` places and re-spawns them in Alfheim |

**Why.** The override was duplicating `data/mythicbotany/dimension/alfheim.json`, which already
carries the identical generator block — verified. It was also the project's riskiest unproven
assumption, and it occupied the slot every TerraBlender mod injects into, which was the single
cause of both the Continuity Works mismatch and Regions Unexplored generating nowhere.

**What it closed without building anything:**

| Item | Disposition |
|---|---|
| B-12 prove the Overworld override | **Retired** — the assumption was dropped, not proved |
| B-05 Regions Unexplored | **Closed** — it generates again, in Midgard, where lush Earth biomes belong |
| B-14 Alfheim Unbroken | **Dissolved** — there is only one Alfheim and the player lives in it |
| B-35 Midgard | **Mostly built** — the Overworld already generates; only CW's anthology is outstanding |
| CW asks 2, 3, 4 | **Withdrawn** — only CW-1 remains |

**What it cost.** Mods that hardcode `Level.OVERWORLD` in Java now see the home world as "not the
overworld", and no datapack reaches that. Alfheim's dimension type is otherwise an Overworld clone
(`bed_works`, `natural`, `has_skylight`, `effects: minecraft:overworld`, 384/−64, scale 1.0; only
`has_raids` differs). MineColonies is the one to watch. Also unresolved: a Nether portal lit in
Alfheim probably will not link, since portal linking is hardcoded Overworld↔Nether.

**Everything built earlier in the day carried over untouched** — the ore modifier keys off the
`#mythicbotany:alfheim` *biome tag* and the ruins off MythicBotany's pools, neither of which cares
which dimension the biomes back. One file was deleted; one was added.

## Boot blocker — found and cleared, 2026-09-02

`journeymap-forge-1.20.1-6.0.4.jar` had been restored to `mods/` at 18:09, after the run that
recorded B-27, leaving it in **both** `mods/` and `quarantine/`. MineColonies declares
`journeymap` optional at `versionRange="[5.9.8,)"`; JourneyMap declares
`version = "1.20.1-6.0.4"`, which Maven tokenises from **1**, so Forge halted in `ModSorter`
before any mod loaded. Both strings read directly from the jars' `mods.toml`.

**Cleared.** The two copies were verified byte-identical (md5 `4dee6648…`) and the `mods/` copy
removed; the quarantine copy is preserved. Load path is 84 jars, 130 mod IDs,
`check_dependency_ranges.py` → **0 blocking issues**.

**User's decision — back-date JourneyMap to the minimum viable version.** Not yet actionable
here: no JourneyMap 5.9.x jar exists anywhere on this machine, and this sandbox has no network.
**The exact requirement:** a JourneyMap build for 1.20.1 whose `mods.toml` declares a bare
`5.9.x` version (≥ `5.9.8`) rather than the MC-prefixed `1.20.1-…` form — the prefix is the
whole fault, so a 6.x jar cannot satisfy the range no matter how new. Filenames look like
`journeymap-1.20.1-5.9.18-forge.jar`. Drop it in `mods/` and re-run the checker.

**New guard:** `check_dependency_ranges.py` now reports any jar present in both `mods/` and
`quarantine/`. This regression was invisible between two recorded sessions precisely because a
quarantine decision had been undone silently.

## Project position

| Field | Value |
|---|---|
| Pack version | 0.2.0-design |
| Minecraft / loader | 1.20.1 / Forge 47.4.10 |
| Mods in load path | **86** (17 quarantined) — Continuity Works patched for CW-1/3/4; JourneyMap 5.9.20 installed 2026-09-03 (B-27 resolved) |
| Mod IDs resolved | 133 |
| Missing mandatory deps | 0 |
| Version range violations | **0** |
| Feature order cycles | **0** — with biome modifiers applied (was 5 in JSON, then 1 from modifiers) |
| Times launched | 5 in the attempt table below, **plus five level 9 attempts — four crashed, the fifth generated a world** |
| Admission state | `runtime validated` on the current load path; level 9 **partially** fresh-world validated. Level 4 **rejected at runtime** — 11 recipes. Not `production admitted`. |

> **Recorded inconsistency, not resolved here:** `INSTRUCTIONS.md` §4 and this table say pack
> version `0.2.0-design`; `CHANGELOG.md` has been running `0.3.x`/`0.4.x-design`. One of the two is
> wrong. Doctrine is not changed on the way past a crash fix — decide it deliberately.

## Verified this session

| Step | Evidence |
|---|---|
| All 98 jars parsed | 146 mod IDs resolved; every `mods.toml` valid TOML |
| Two boot blockers identified | `mh_automated` missing `meds_and_herbs`; `create_sophback_compat` is a NeoForge 1.21 jar with no Forge `mods.toml` |
| Both blockers removed from load path | Moved to `quarantine/`; re-scan shows 96 jars, 144 IDs, **0 missing mandatory dependencies** |
| Pinned matrix reconciled | All 26 pinned mods present at exact pinned file IDs — zero drift |
| Botania elven trade extracted | 15 recipes; 9 conversions, 5 identity returns, 1 lexicon. Schema confirmed. |
| Dreamwood early-game parts confirmed | `dreamwood_twig`, `elven_spreader`, `natura_pylon`, `dreamwood_log` all exist |
| MythicBotany Alfheim confirmed | Real dimension, 5 biomes, `elementium_ore` + `raw_elementium` native |
| Milestone inversion confirmed | Terrasteel needs 3 imports; Alfsteel is elven-native at 1,500,000 mana |
| Design set authored | `INSTRUCTIONS.md`, `GATE_REVERSAL.md`, `CAMPAIGN_ERAS.md`, `TWIN_SPINES.md`, `BACKLOG.md`, this file |

## Validation ladder

| Level | State | Note |
|---|---|---|
| 1 Syntax & schema | passed | All jars parse; 34 datapack JSON files parse |
| 2 Java & Gradle | N/A | No source project |
| 3 Registration & metadata | **passed** | 85 jars, 132 IDs, 0 missing deps, 0 range violations, 0 quarantine conflicts |
| 4 Scripts & gameplay data | **REJECTED at runtime** | `check_era.py --all` → 0 problems, but the game refused **11** of our recipes at load. Static passes; schemas were never checked. |
| 5 Structure & NBT | **passed (static)** | `check_worldgen.py` W5/W6 — pools, processor lists, and the home dimension's biome source all resolve; `check_feature_order.py` F1 — **0 cycles** over 298 biomes |
| 6 Source-to-shipping | **passed** | 4 generators; every generated artifact reproduced from its manifest |
| 7 Packaging boundary | passed | No strays; `tools/` and design docs outside the load path |
| 8 Controlled startup | **passed, now one jar stale** | 2026-09-03 14:11–14:18 on the then-current **85**-jar load path; 0 crash reports, 27 ERROR lines, none load-blocking. JourneyMap was added at 14:26, so the next boot re-confirms it on 86. |
| 9 Fresh world | **partially passed** | Attempt five, 2026-09-03 14:18: world creates, Midgard and Alfheim both generate, **player wakes in Alfheim**. Outstanding inside level 9: 9d ore findable, 9e respawn, 9f Nether portal, and flying out past ~625 chunks. |
| 10 Compatibility | **eligible** | Level 9 no longer blocks it. Villages ruined and clustered; Lost Cities/RU/CW coexistence in Midgard. |
| 11 Gameplay integration | deferred | Quests authored (215) but never played |
| 12 Production admission | `draft` | Levels 8-11 outstanding |

## Worktree

Design and management documents written this session; no third-party jar modified; two jars moved to
`quarantine/` and preserved. `minecraftinstance.json` deliberately **not** edited — CurseForge is
running and would overwrite the change.

## First launch attempt — 2026-09-02 13:44 — did NOT reach the game

**The pack was never tested. Level 8 remains `not run`, not `failed`.** No mod was loaded, so no
conclusion about the modpack can be drawn from this attempt.

**Evidence of absence, in the instance:** no `logs/latest.log`, no `crash-reports/`, no `config/`,
no `options.txt`. Nothing was written, because the JVM never started.

**Cause — DNS failure in the launcher, not a modpack fault.** From
`%APPDATA%/CurseForge/logs/2026-09-02_12-45-41/main-2026-09-02_12-45-41.log`:

```
13:44:42  [CurseForgeLauncher] launching modpack ... Id: b76c4165-0d11-4068-9d80-c035b1b09494
13:44:44  [VerifyAndRepairModsAction] Skipping verify/repair for unlocked modpack
13:44:44  [DownloadGameVersionManifestAction] Downloading game version 1.20.1 manifest file....
13:44:44  [error] get request .../v1/minecraft/version #1 failed - getaddrinfo ENOTFOUND api.curseforge.com
13:44:52  [error] ... #2 failed        13:44:53  [error] ... #3 failed
13:44:54  [OperationCompletedEventHandler] Outcome: Failed.
```

CurseForge fetches the 1.20.1 version manifest *before* launching. DNS for `api.curseforge.com`
failed three times and it aborted. DNS errors in that log run from 13:15 onward; `tracking.overwolf.com`
failed too, and the Electron updater reported `ERR_NAME_NOT_RESOLVED`.

**Recovered.** `api.curseforge.com` resolves now (CNAME to CloudFront). The condition was transient.

## Blocking risk found — no Java 17 is installed

Verified, and independent of the DNS failure:

| | |
|---|---|
| `versions/1.20.1/1.20.1.json` requires | `java-runtime-gamma`, **majorVersion 17** |
| Installed: `java/java-runtime-delta` | **21.0.12** |
| Installed: `java/Jre_21` | **21.0.4** |
| System `java` on PATH | **26.0.1** |

There is no Java 17 on this machine. CurseForge must download `java-runtime-gamma` on the next
launch — which needs the same network that just failed, so the two problems are linked.

If it instead falls back to Java 21, Forge 47.4.10 with 97 mods is an unsupported configuration, and
Sinytra Connector rewrites bytecode at load time. That combination fails in ways that are hard to
attribute. **Confirm Java 17 is actually fetched before trusting any subsequent crash.**

## LEVEL 8 PASSED — 2026-09-02 15:58

**The pack reaches the title screen and holds there.** Five attempts; the fifth succeeded.

| | |
|---|---|
| Mods in load path | 95 (4 quarantined) |
| Valid mod files loaded | **403** including JarJar-nested |
| Heap | 13 GB |
| Java | 21.0.4 Eclipse Adoptium |
| Load time | ~95 s launch to idle |
| Crash reports | **0** |
| FATAL lines | **0** |
| `config/` | 77 entries written |
| Resident | 16.3 GB |

**How idle was confirmed:** two `Sound engine started` markers, meaning both resource reloads
completed; final log lines are texture-atlas and shader loading; log growth then stopped entirely
while the process stayed alive. `Sound engine started` alone is *not* a success marker — it fires
during the loading overlay. The quiet log after the second reload is.

**FIRST_BOOT_VALIDATION step 9 satisfied:**
`[KubeJS Startup]: 00_alfheim_reclaimed_bootstrap.js#3: [Alfheim Reclaimed] Startup KubeJS scaffold loaded.`

Core mods confirmed by their written configs: botania, mythicbotany, ars_nouveau, naturesaura,
feywild, jei, jade, curios, patchouli, terrablender, continuityworks. FTB Quests, FTB Library and
KubeJS confirmed from log output (they do not write to `config/` at client start).

**Caveat on method:** launched from a hand-assembled Forge command against the existing install, not
through CurseForge. This validates the **mod stack**. The CurseForge launch path is still unproven
and needs working DNS, its own Java runtime (B-26), and repaired assets (B-28).

### The five attempts

| # | Heap | Outcome |
|---|---|---|
| 1 | — | CurseForge aborted: DNS failure fetching the 1.20.1 manifest. No JVM. |
| 2 | 8 GB | `ModSorter`: JourneyMap x MineColonies optional range violation (B-27). |
| 3 | 8 GB | Module `ResolutionException` — a fault in my launch harness, not the pack. |
| 4 | 8 GB | `OutOfMemoryError` in `ModelBakery`. 8 GB was my test choice, not the pack's need. |
| 5 | 13 GB | **Title screen.** After quarantining BuildCraft RF (B-29). |

Attempt 4 vindicates the instance's 14 GB setting and the original F-05 finding: this pack genuinely
needs a large heap, and 8 GB is not enough to bake its models.

### Fourth blocker — BuildCraft RF has no BuildCraft


```
java.lang.OutOfMemoryError: Java heap space
  at com.google.common.collect.Maps.newHashMap
  at net.minecraft.client.resources.model.ModelBakery.m_119362_(ModelBakery.java:336)
  Overlay name: net.minecraft.client.gui.screens.LoadingOverlay
```

The heap was **8 GB** — a value chosen for the test because only 13.5 GB was free, not one the pack
asked for. **This vindicates the instance's 14 GB setting and the earlier F-05 finding.** Conquest
Reforged alone is 227 MB of block models; with 95 mods, 8 GB is not enough. 13 GB succeeds.

Crash report preserved outside the instance at `scratchpad/crash-oom-8gb.txt`.

**Caveat on method:** launched from a hand-assembled Forge command against the existing install, not
through CurseForge. This validates the **mod stack**; it does not validate the CurseForge launch
path, which still needs working DNS, its own Java runtime, and repaired assets.

### Fourth blocker — BuildCraft RF has no BuildCraft

The 13 GB heap got past the OOM and immediately hit a harder fault:

```
java.lang.NoClassDefFoundError: buildcraft/lib/tile/TileBC_Neptune
  at dev.jackraidenph.buildcraftrf.util.CapabilityEvents.onCapability(CapabilityEvents.java:18)
    ~[buildcraftrf-3.0.0.jar]
```

`buildcraftrf-3.0.0.jar` is an addon for BuildCraft; BuildCraft is not installed. It crashes on
capability-attach for the first BlockEntity — any chest. Quarantined. See B-29.

**This one no static scan could have caught.** It declares no dependency on buildcraft; the
requirement exists only as a hard class reference. Metadata analysis is blind to it. Only running
the game finds this class of fault — which is the argument for doing level 8 early and often.

### Third blocker found and cleared — JourneyMap x MineColonies

MineColonies declares `journeymap` **optional** at `[5.9.8,)`. JourneyMap's version string
`1.20.1-6.0.4` tokenises from **1**, below the bound. Forge halts: an optional dependency may be
*absent*, but if present it must satisfy the range.

```
[15:43:49] [main/ERROR] [net.minecraftforge.fml.loading.ModSorter/LOADING]:
    Unsupported installed optional dependencies:
    Mod ID: 'journeymap', Requested by: 'minecolonies',
    Expected range: '[5.9.8,)', Actual version: '1.20.1-6.0.4'
```

Quarantined; mod loading then completed. Disposition is B-27.

**Method gap exposed:** the earlier scan checked only *mandatory* dependencies and passed the pack
clean, so this reached first boot. `tools/check_dependency_ranges.py` now checks both kinds using
Maven `ComparableVersion` tokenisation, and is verified in both directions.

### Runtime errors — 1264 lines, none load-blocking

| Count | Source | Assessment |
|---:|---|---|
| 864 | Conquest Reforged models — `JsonSyntaxException: Missing axis` | Malformed model JSON **inside the mod**. Cosmetic. |
| 384 | `PalettedPermutations: unable to apply palette` | Same family. Cosmetic. |
| 4 | `FilePackResources: Failed to open pack .../assets/objects/...` | **Real** — assets incomplete after the DNS outage. B-28. |
| ~14 | `Invalid path in pack` | Mod-authoring sloppiness. Cosmetic. |

864 malformed models and a heap ceiling in the model baker are not unrelated: model loading is where
this pack is heaviest, and where both its bugs and its memory pressure land.

### Java 21

It loads, but LWJGL logs `Unsupported JNI version detected, this may result in a crash`. Java 17
remains the supported runtime; B-26 is downgraded from blocker to correctness item.

## Datapack layer validated — 91-minute session, clean exit

The successful run stayed up **5,482 s (91 min)** and exited normally (`Stopping!`, rc 0, no crash
report). Before shutdown it loaded the datapack layer, which is stronger evidence than the title
screen alone:

| | |
|---|---|
| Recipes parsed | **30,960** in 179 ms |
| Advancements | **9,320** |
| MineColonies crafters | 161 recipes across 16 crafters |
| KubeJS server scripts | 1/1 loaded, **0 errors, 0 warnings** |
| KubeJS recipe pass | added 0, removed 0, modified 0 — correctly inert by design |

`[KubeJS Server]: 00_alfheim_reclaimed_recipes.js#3: [Alfheim Reclaimed] Server recipe scaffold
loaded.` — the server half of FIRST_BOOT_VALIDATION step 9.

**One real defect surfaced (B-30):** `mythicbotany:feysythia` is uncraftable. MythicBotany's
conditional Petal Apothecary recipe calls for `feywild:lesser_fey_gem`, which Feywild 5.5.5 no longer
ships. Fixable in a few lines of KubeJS, and a good first exercise of that path.

Also 5 Conquest Reforged stonecutting recipes with empty results — they fall back to vanilla.
Cosmetic.

## Purge executed — 2026-09-02 17:48

Conquest, Twilight Forest and BetterEnd removed (B-32), then Continuity Works quarantined after it
crashed world generation (B-33). **11 jars out, 84 remain.**

| Measure | Before | After |
|---|---:|---:|
| Jars in load path | 95 | **84** |
| `mods/` on disk | 674 MB | **320 MB** |
| Runtime ERROR lines | 1270 | **17** |
| Peak resident memory | 16.3 GB | **8.8 GB** |
| Crash reports | — | **0** |

**The 17 remaining errors are all trivial** and none are ours: 16 are `Invalid path in pack` from
mods shipping files with illegal names — `miners_delight` ships both `Lunchbox.png` and a misspelled
`Launchbox.png`, `mmorpg` ships `question - Copy.png`, `cozyhome` ships uppercase `.ogg` filenames —
plus one informational Moonlight notice about Fabric API being present.

Conquest Reforged alone accounted for **98%** of the pack's error output and roughly half its memory.

**Memory finding (B-34):** the 14 GB instance setting was justified while Conquest was loaded — 8 GB
OOMed in `ModelBakery`. At 8.8 GB peak it is now over-provisioned; 8 GB is worth retesting.

## Level 9 — attempted, failed, cause identified

First world-generation attempt crashed:

```
Description: Exception generating new chunk
IllegalStateException: Trying to access unbound value
  'ResourceKey[minecraft:worldgen/placed_feature / minecraft:ore_diamond_medium]'
    at FeatureSorter.m_220603_ -> ChunkGenerator.m_223094_
```

`minecraft:overworld`, stock `NoiseBasedChunkGenerator`, chunk −26/−6, **625 chunks in** — the fault
does not appear at spawn, so a spawn-only test would have passed falsely.

Cause is Continuity Works (B-33). 136 of its 176 biomes reference vanilla ore placed-features — which
is *not* wrong in itself; Regions Unexplored does the same in 71 of its 170 and works. The difference
is that CW builds biomes code-side and hands them unbound feature holders. Report written to
`alfheim_reclaimed_design/CONTINUITY_WORKS_DEFECTS.md`; jar quarantined, reversibly.

## Next exact action

1. **Create a fresh world and run `python tools/check_spawn.py`.** This is the top item: B-44's
   fix is written and statically clean but has never run. Expect 0 problems — current dimension,
   respawn dimension, Alfheim chunks and the `_v2` flag all confirmed **from the save**. If it
   reports S1, the teleport itself is failing and nothing else about spawn should be trusted.
   The same world settles the Midgard switch: `/locate biome minecraft:ocean` and
   `/locate biome continuityworks_biomes:terraced_vineyard`.
2. **Fix the 11 recipes the game rejected (B-41, B-42).** They are ours, they are silently absent
   from a running world, and `check_era.py` passes them. Repair the generators, then teach the
   checker each recipe type's schema so the same class cannot pass again — the checker gap matters
   more than the eleven recipes.
2. **Finish level 9 in the world that is already open.** Cheap, and it needs no new run:
   mine for copper/iron (9d), die bedless and confirm respawn returns to Alfheim (9e), light a
   Nether portal in Alfheim and see whether it links (9f), and **fly out several thousand blocks** —
   both earlier crashes landed ~625 chunks from spawn, so a world that creates has proved nothing
   about the rest of the map yet.
4. **Level 10** is now eligible: villages ruined and clustered, and Midgard's three worldgen mods
   coexisting without destructive overlap.
5. **B-43** — one datapack file restores the `minecraft:leaves` item tag that `jaffabricate` breaks.
5. **`Level.OVERWORLD` sweep** (10b) — MineColonies colonies first, then Botania flower mechanics
   and Mine and Slash. This is the cost of the architecture change and the only way to price it.
6. Then the **Era IV gate** (B-36) — retargeted 2026-09-03, see `CAMPAIGN_ERAS.md` §3.
7. ~~Install a JourneyMap 5.9.x build~~ — **done 2026-09-03**, `journeymap-1.20.1-5.9.20-forge.jar`,
   declared version `5.9.20` (bare), 0 blocking issues. Needs a launch to accept.
8. **Backport CW-1, CW-3 and CW-4** to Continuity Works (B-39) and drop the local patch when an
   upstream build carries all three.
3. **`Level.OVERWORLD` sweep** (10b) — MineColonies colonies first, then Botania flower mechanics
   and Mine and Slash. This is the cost of the architecture change and the only way to price it.
3. Then the **Era IV gate** (B-36). Midgard itself already generates.
4. Install a JourneyMap **5.9.x** build when one is available; the pack boots without it.
5. **Backport CW-1 and CW-3** to Continuity Works (B-39) and drop the local patch when an upstream
   build carries both.

**Run before any launch, after any jar or datapack change:**

```
python tools/check_feature_order.py
python tools/check_dependency_ranges.py
```

Both are cheap and both catch a class of fault that only appears after the title screen.

## Open decisions

1. **Regions Unexplored** (B-05) — still generates nowhere. Re-home its biomes into Midgard, or
   remove the mod. Midgard work forces this decision.
2. **Midgard's generator** — Continuity Works is quarantined on CW-1. Midgard either waits for a
   fixed CW jar, or ships first with a smaller hand-built biome source.

**Resolved 2026-09-02:** Ars Nouveau confirmed as the Spine of Song (B-04). Anthology-fit question
dissolved (B-23). **B-25 (Alfheim ore viability) — resolved by implementation**, see below.

---

## Session — era verification and Alfheim viability, 2026-09-02

### Era-by-era verification: 10 eras, 0 problems

`tools/check_era.py` was rewritten from an existence check into a playability check. The prior
version verified that quest items and recipe ids were registered somewhere; it passed on a pack
whose custom items no recipe could make. It now runs ten invariants (E1–E13) and validates
**376 recipes, 215 quests and 80 custom items** across all ten eras.

Two defects in the tool itself were repaired first, because both produced false results:

| Defect | Effect |
|---|---|
| Era script glob was `*era{n}*.js` | `210_era10_tier_ladder.js` matched **era 1** — Era I was silently validated against Era X's ladder |
| `.id(...)` was searched in a 240-char tail | An `event.remove({...})`, which has no `.id()`, adopted the id of the next recipe — one false duplicate |

**Three real defect families were then found and fixed at their generator, not in the output:**

1. **53 "uses" that used nothing** (E5). `tools/gen_item_uses.py` emitted the `multiplier` family
   as `occultism:crushing` naming only the ore — the custom item it was filed under never
   appeared in the recipe. The docstring said `ore/raw + item -> extra ingots`; the code dropped
   the item.
2. **5 duplicated recipes covering 53 ids** (E7). Because the item was absent, all 53 collapsed
   into 5 distinct crushing recipes — 14 identical copies of raw iron → 2 iron, and so on.
3. **17 free duplication loops** (E8). Two `MULTIPLIER` rows were ingot → *the same ingot*, x2,
   with no other input: `botania:manasteel_ingot` → 2 manasteel, `botania:elementium_ingot` → 2
   elementium, repeatable forever. Infinite Elementium destroys the trade premise outright.

The repair changed `MULTIPLIER` to genuine raw→ingot rows (adding `mythicbotany:raw_elementium`,
the native elven metal) and made the intermediate the catalyst consumed with the ore. One
root-cause change cleared all three families. Regenerated: 286 use-recipes.

E8 was then narrowed to fail only on *free* duplication. The 48 `reagent` recipes it also flagged
consume an intermediate and are deliberate; failing them would have buried the 17 real exploits.

### Alfheim was not completable — worldgen, not scripts

The verification passed, and the pack was still unplayable. `tools/check_worldgen.py` (new)
resolves preset → layer → biomes → Forge biome modifiers and reports what actually generates:

> **Copper, iron, coal, redstone, lapis and diamond generated in none of Alfheim's 11 biomes.**
> MythicBotany places only gold, elementium and dragonstone.

Era I's own quest chain asks for a Mana Spreader (**copper ingot**), an iron ingot, and a
Manasteel ingot (**infused iron**). No static check on scripts could see this: every id existed
and every recipe resolved. The material simply did not exist in the world.

This settles **B-25** by implementation, taking the guard rail the backlog asked for rather than
the pure-scarcity option:

| | |
|---|---|
| Everywhere (`#mythicbotany:alfheim`, 11 biomes) | copper ×4, iron ×3, coal ×6 — about a quarter of vanilla counts, smaller veins |
| `#alfheim:highland_veins` (3 biomes) | richer iron ×6, redstone ×2 |
| `#alfheim:arcane_strata` (3 biomes) | lapis ×1, diamond ×2 |

Delivered as a **Forge `add_features` biome modifier**, which reaches MythicBotany's five biomes
as well as our six without overriding a single jar-owned biome. Ore is scarce enough that trading
through the gate still pays, and the early chain can now be finished.

Also fixed: **Ashen Grove generated no trees at all**, while Velrous's opening line is "The trees
you see standing are dead." Spawn could strand a player with no wood and a first quest asking for
a crafting table. Loose dreamwood at low density is now the standing dead the script describes.

### Abandoned elven villages — B-19, without authoring an NBT

MythicBotany ships `elven_house`: three buildings and two gardens, generating **pristine and
alone**, one per ~24 chunks. `tools/gen_elven_ruins.py` fixes both, entirely by datapack override:

- `alfheim:elven_ruin` — a `block_rot` (integrity 0.88) plus rule processor: elf glass shatters,
  livingrock goes mossy then cracked, dreamwood floors fall in, cobwebs fill the gaps. Applied to
  every pool element, so one intact piece yields both an intact and a ruined state.
- `house` and `tower` each carry a jigsaw block **named** `mythicbotany:entrance`, and the entrance
  connector targets the `gardens` pool. Putting the buildings into that pool makes buildings chain
  to buildings — a site grows into a cluster instead of a lone cottage. The structure's own
  `size: 5` bounds the spread.

Only full blocks are swapped by name: `output_state` sets `Name` alone, so converting a stair or
slab would reset its facing. The generator asserts this rather than trusting the author.

### Evidence

| | |
|---|---|
| `python tools/check_era.py --all` | 0 problems; E1–E13 over 10 eras, 376 recipes |
| `python tools/check_worldgen.py` | 0 problems; W1–W5; copper/iron/coal each in 11 biomes |
| `python tools/check_dependency_ranges.py` | **0 blocking issues** after clearing JourneyMap 6.0.4 |
| Datapack JSON | 34 files parse (preset override removed) |
| Both new checkers | Validated in **both** directions — each fires on synthetic bad input |
| Worktree | Changed: `tools/check_era.py`, `tools/gen_item_uses.py`, `tools/gen_alfheim_biomes.py`, `tools/check_worldgen.py` (new), `tools/gen_elven_ruins.py` (new), regenerated `kubejs/` output |
| Git | Not in use per user direction; nothing committed |

**Static only.** Nothing here has been seen running. Levels 8–12 remain outstanding; level 3 now
passes and level 9 is unblocked.

**Waiting on Continuity Works:** four asks in `WORLD_STRUCTURE.md` §6 — move the anthology to Midgard,
add an Alfheim biome layer, address terrain viability, keep spawn protection.

Nothing blocks B-01, B-02, B-03, B-06, B-12 or B-17.

## Continuity Works 0.3.0-rc.2 — received and checked

Arrived and installed 2026-09-02. `ContinuityWorks-Forge-1.20.1-0.3.0-rc.2.jar`, 459 KB.

| Check | Result |
|---|---|
| Acceptance scan | **0 fail, 1 warn, 5 pass** |
| Mod IDs | `continuityworks_biomes`, `continuityworks_spawn_protection` — unique, no `continuity` collision |
| Loader | Forge `[47.4.10,)`, MC `[1.20.1,1.20.2)` — correct |
| Full pack re-scan | 97 jars, 146 mod IDs, **0 missing dependencies** |
| Content | 176 biomes, 11 convention tag files, 2 abyssal structures |

**It is pointed at the wrong dimension.** The mod requires TerraBlender and injects into the
Overworld — the slot Alfheim now occupies. Nothing in the jar is broken; it needs re-aiming at
Midgard. Four asks are written up in `WORLD_STRUCTURE.md` §6.

Static acceptance only. Level 9 still requires a fresh world.

## Architecture settled — two worlds

Clarified by the user 2026-09-02, after two wrong turns in this file's history.

| | Alfheim | Midgard |
|---|---|---|
| Dimension | `minecraft:overworld` | new, from Continuity Works |
| Role | Home. Elven, magical, **metal-poor**. | The industrial world that died. Era IV+. |
| Biomes | MythicBotany's 5 + a Continuity Works elven layer | the 176 anthology biomes |

Alfheim takes the Overworld slot for a technical reason as well as a thematic one: a great many mods
gate behaviour on `Level.OVERWORLD`, and the player's home world should be the one where the mod stack
behaves normally.

**Injection point corrected.** Earlier revisions of `WORLD_STRUCTURE.md` named
`tags/worldgen/biome/alfheim.json`. The real extension point is
`data/mythicbotany/tags/libx/biome_layer/alfheim.json` — a tag of **LibX `biome_layer`** entries, each
a full climate map like vanilla multi-noise. Enriching Alfheim is a datapack append of new layers, no
TerraBlender and no Java.

**New risk found — Alfheim is not campaign-viable as shipped.** Its terrain is `botania:livingrock`,
not stone; `ore_veins_enabled` is false; there is no vanilla cave noise. Almost no ore generates.
That scarcity is arguably the premise rather than a bug (B-25), but it needs a deliberate decision and
a guard rail that Era I is completable without iron.

The pre-written checker (`tools/check_incoming_mod.py`) was built before the jar arrived and caught
the TerraBlender dependency on first run. It is validated against a known-bad jar
(`quarantine/create_sophback_compat-1.0.jar` → 3 fail) and a known-good one.

## Scope note — 2026-09-02, second session

Direction expanded materially. Three changes, all doctrine-level:

- The magic spines now govern the **whole pack**, not just the Botania tree. Pack-wide recipe gating
  (B-16) is now the largest body of implementation work in the project.
- Mine and Slash is upgraded from reward economy to the **primary world-interaction layer**.
- **Alfheim is the Overworld.** Originally planned as a `#mythicbotany:alfheim` tag append with the
  Alfheim generator overriding the Overworld preset. **Superseded the same day** — Continuity Works
  requires TerraBlender, so the design moved to a vanilla multi-noise Overworld with Alfheim injected
  as a TerraBlender region. See the Continuity Works section above and `WORLD_STRUCTURE.md` §3.
# Session — Royal Wave A completion and Manna Stone Storage, 2026-09-09

Royal Tile Set I Wave A now covers all 17 planned semantics as 30 registered custom-model blocks. The deterministic generator emits 34 files and its checker passes. The review function places the complete gallery, including all six multi-block assemblies.

`alfheim_leyworks:manna_stone_storage` is the first functional elven furnishing. It stores 27 slots at base and consumes up to three items in `alfheim_leyworks:manna_storage_gems`, adding 27 slots per gem to a 108-slot maximum. Contents and installed gems persist separately; breaking returns both. The custom 18×6 interface visibly locks unavailable capacity. Comparator output and Spine-of-Leaf crafting are present.

Evidence: Royal checker `PASS semantics=17 blocks=30 generated=34`; Alfheim Leyworks `gradlew test build` passes on Java 17; installed client/server jars are byte-identical; dependency-range and feature-order checkers both report zero blocking issues. Static only: client rendering, interaction, save/reload, shift-click, comparator and multiplayer synchronization remain runtime-pending.

Expansion in the same session: seven fixed-capacity functional containers now share the Manna storage screen and persistence foundation—Royal Chest 54, Gemstone Coffer 18, Dreamwood/Provision/Scroll Crates 27 each, Tall Vase 9 and Memorial Urn 9. `tools/check_functional_elven_containers.py` passes over 38 deterministic resources, including a complete review function. The sculptural-detail generator adds 12 physical blocks for Ancestor/Oathkeeper/Mourning statues, Large Crystal Plinth, Observatory Prism Stand and three gemstone embellishments; its 16 outputs reproduce byte-for-byte and its startup script passes Node syntax. Runtime status is unchanged: pending client restart and field review.

Further household expansion: Royal Wave B now implements all 19 catalogued room-completion semantics as 28 physical blocks; its checker passes over 32 deterministic outputs. A new 32-object exotic-home catalog supplies seven families of specifically non-human domestic design. Eight pilot objects are registered in 12 deterministic outputs: Starbell Chandelier, Moonpool Lamp, Whisper Harp, Moonmirror, Levitating Planter, Nectar Fountain, Bottled Aurora and Miniature Ley Garden. Total new decorative/functional physical blocks across the current furnishing pass: 86. Runtime status remains pending restart and gallery inspection.
