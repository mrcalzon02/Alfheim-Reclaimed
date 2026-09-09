# Backlog

### B-90 — Crystal clusters had no orientation state — **REPAIRED (static) 2026-09-08**

User report, from a geode screenshot: *"our custom crystals do not correctly have orientation
states. They have a correct model, they do not have correct orientations."* Exactly right, and the
model was never the problem — `minecraft:block/cross` is what vanilla's own `amethyst_cluster`
uses too. The six cluster blocks simply had **no blockstate properties at all**, so each had
exactly one state and every cluster rendered upright whichever face it grew from.

Two callers had been addressing a property that did not exist, and both failed silently:

| Caller | Asked for | What happened |
|---|---|---|
| `growCluster` in `13_crystals.js` | `{ facing: face }` on the grown cluster | dropped — the bud's chosen face never reached the block |
| 28 `inner_placements` across 14 geode features | `facing` + `waterlogged` | dropped — for a propertyless block `StateHolder`'s codec is `Codec.unit`, which ignores `Properties` without logging |

**Repaired at `tools/gen_crystals.py`, not in its output.** Three coordinated changes:

1. cluster blocks declare `BlockProperties.FACING` and `BlockProperties.WATERLOGGED`. Verified
   against KubeJS 2001.6.5, where `BlockBuilder.property` feeds
   `BasicBlockJS.createBlockStateDefinition` and `BasicBlockJS` already implements
   `SimpleWaterloggedBlock` — the property was the only missing piece.
2. a six-facing blockstate per cluster, rotations taken from vanilla's
   `assets/minecraft/blockstates/amethyst_cluster.json` in the 1.20.1 client jar. Real files under
   `kubejs/assets/` overwrite the builder's generated simple variant, because
   `GeneratedResourcePack` walks that folder *after* `generate()` — the same mechanism the block
   and budding cube variants already depend on.
3. `placementState(orientCluster)`, so a hand-placed cluster points out of the face it was placed
   against. It sets waterlogged as well, because `getStateForPlacement` skips its automatic
   waterlogging as soon as a placement callback exists.

`waterlogged` is deliberately absent from the blockstate keys: a variant key matches any state
whose listed properties agree, so six entries cover all twelve states — which is exactly what
vanilla ships.

**Evidence.** `gen_crystals.py --check` reproduces. The cross-artifact check reads 6 blocks
declaring no properties, 28 geode placements asserting properties the block did not have, and 0
cluster blockstate files at `HEAD`; after the change, 6 blocks declaring both, 28 placements
satisfied, and 6 blockstates of exactly six facings each whose models resolve. `node --check`
parses the generated script.

**Deferred to runtime:** that a geode now shows clusters on walls, floor and ceiling in their own
orientations. Blockstate rotation is client-side and cannot be read from a dedicated server. The
server half is provable without a client — `setblock ... alfheim:emberglass_cluster[facing=north]`
followed by `data get block` fails to parse outright if the property is missing.

### B-89 — The Ley Conduit Node — **PYRAMID RULES RUNTIME-PROVEN; CLIENT REVIEW PENDING**

B-88 shipped the corridors and recorded the node as deliberately absent, because "a block entity
that projects and retransmits a beacon payload is Java, and this pack has no mod that owns
worldgen blocks." That was true when it was written and is no longer true. The decision B-88 said
a worldgen block should not be taken without has now been taken by the client: build it, make
dormant nodes need a crafting operation that consumes a mid-tier item, and use the modified
beacon-pyramid rules.

#### A second first-party mod, not an extension of the first

`first_party_mods/alfheim_leyworks/` is its own Gradle project rather than another package inside
`alfheim_companion`. The companion is scoped to one summonable entity and carries an FTB
integration layer and optional compile-time adapters; the node needs none of that and should not
inherit its dependency surface or its release cadence. Its build declares exactly one dependency,
Forge itself. Built with the project's own wrapper under JDK 17 — the default `java` on this
machine is 26, which Gradle 8.8 cannot run on at all.

#### Two blocks, not one blockstate

| block | ticks | where it comes from |
|---|---|---|
| `alfheim_leyworks:ley_conduit_node_dormant` | no block entity at all | placed by worldgen, light 3 |
| `alfheim_leyworks:ley_conduit_node` | block entity, 80-tick recheck | crafted only, light 12 |

This is a performance decision before it is a design one. A size-6 corridor network places roughly
a dozen nodes and there are thousands of these structures in a world; a single blockstate with one
ticking block entity would mean every generated corridor everywhere carries live tickers. The
2026-09-07 field report already ended with "the game brought my system to a crawl." **Nothing in a
generated corridor ticks until a player converts a node by hand.**

It is also exactly what the design asks for. `LEY_LINE_CHANNEL_CORRIDORS.md`: *"The network begins
as archaeology rather than infrastructure. Most nodes are dormant or disconnected."* Worldgen seeds
inert nodes; the player lights them.

#### The crafting operation, and why elementium core

Shapeless: `ley_conduit_node_dormant` + `alfheim:elementium_core` -> `ley_conduit_node`.

`alfheim:elementium_core` is the Era V component — `10_items.js` registers it,
`25_era5_tier_ladder.js` crafts it from `alfheim:elementium_stilled` + `botania:livingrock`, and
`26_era6_tier_ladder.js` already consumes it. It is genuinely mid-tier on our own ladder rather
than borrowed from a mod's, so lighting a network is a real mid-game investment and a node found
in Era II is a thing to carry home rather than a thing to use.

#### Modified beacon-pyramid rules

Vanilla reads a four-tier pyramid of a fixed block list and grants an effect globally. This reads
the same shape and changes what it is for, per the design: **tier chooses reach, not effect.**

- Course *n* is a (2n+1) square at depth *n*, up to four courses — vanilla's geometry exactly.
- Any block in `alfheim_leyworks:pyramid_base` counts, so the pack picks its own masonry
  (leyline/moonstone livingrock, `botania:livingrock`) instead of inheriting iron and diamond.
- Reach = tier x 12 blocks, applied to both node-to-node projection and aura radius.
- Projection runs all six cardinal axes through air and anything in
  `alfheim_leyworks:beam_transmits` — that is what lets architecture mask unused faces instead of
  needing a different block per shape.
- The aura applies `alfheim:leyline_presence`, looked up **by ResourceLocation** rather than
  compiled against KubeJS, so the two stay decoupled: if the effect is not registered the node
  still projects, it just cannot buff.

Particles are the visible channel: END_ROD motes travelling outward along every open axis, at the
measured projection length, client-side only. A beacon-style rendered light column is a separate
client renderer and is not claimed here.

#### Worldgen now places them

`gen_leyline_corridors.py` seats a dormant node at the points the geometry already made
significant: the relay housing every twelve blocks of straight run, the centre of every four-way
junction, the sealed face of every terminal (*"or disconnected"*), and the crown of the hub
distributor — which is itself three courses of relay masonry, so the hub silently shows the player
the shape a pyramid wants to be. Bends get none; a corner is not a place.

Node counts per piece: hub 1, junction 1, straight 1, terminal 1, bend 0.

A datapack cannot declare a dependency on a mod's block, so the generator gained check **L1**: it
fails if no `alfheim_leyworks-*.jar` is in `mods/`. Without the jar the palette entries do not
resolve and corridors generate with holes where the nodes belong — a failure that is invisible
until someone walks one.

#### Measured

Fresh world `leyworks02`, seed `alfheim`, two runs.

**The pyramid rules read the world.** A live node over two complete courses of
`alfheim:leyline_livingrock_bricks` reports `Tier: 2`. Knock one corner out of the lower 5x5 and
it reports `Tier: 1`. That one moving number is four proofs at once: the block entity ticks, the
courses are counted from the node downward and stop at the first gap, the reading is not a
constant, and `alfheim_leyworks:pyramid_base` actually loaded — which only happens if the jar's
`pack.mcmeta` is present.

**The nodes are in the ground, not just in the palette.** Force-generating a 320x320-block box
around the located corridor gave 1,042 full chunks holding **36 dormant nodes**, all at Y -7, the
channel height — alongside 550 luminous channel blocks, 5,202 relay blocks and 11,512 shell
bricks. Both node blocks also place and read back by command.

**Everything underground locates.** `alfheim:leyline_corridors` 293 blocks from spawn;
`deep_quarry` 386, `elder_kings_tomb` 402, `faultwork` 1,173, `deepworks_headworks` 386 — the last
two at the same [352, ~, 160], which is the co-location B-87 built and had never demonstrated.

**Nothing regressed.** Same run: hub anchor 1, crown 1, court 8, FTB ownership 100/100 chunks.
Static: `check_surface_works`, `check_deep_archaeology`, `check_worldgen`, `check_golden_terraces`
and `gen_leyline_corridors --check` all clean.

#### Two defects this pass found, both invisible to static checking

**The jar had no `pack.mcmeta`.** Forge logs exactly one line — `Missing metadata in pack
mod:alfheim_leyworks` — and then declines to load the mod's `data/` tree. The jar builds, the
blocks register, and the pyramid tag, the beam tag and the block's own `mineable/pickaxe` entry
all silently do nothing; with `requiresCorrectToolForDrops()` set, the node would not even have
dropped. `processResources` now expands `pack.mcmeta` alongside `mods.toml`, and the warning is
gone from the log. `gradle.properties` also still carried the companion's description verbatim,
and `mods.toml` was unedited MDK boilerplate carrying an irrelevant optional dependency on
`continuityworks`; both are now this mod's own.

**The Deepworks probe was asking for a structure set.** `run_server.py` ran `locate structure
alfheim:deepworks_archaeology`, which is a *set* holding three structures. The server answers
"there is no structure with type", which reads exactly like the structure being absent — the same
sentence field item 12 was about. It now asks for `deep_quarry`, `elder_kings_tomb` and
`faultwork` by name, and all three answer.

#### Open

- Client visual review of the node model, its light level and the particle density.
- Node-to-node **retransmission** — a node inside another node's projection coming up to that
  node's tier — is specified in the design and is not built. Each node currently reads only its
  own pyramid. That is a chained-network mechanic and wants its own pass.
- No advancement, quest or recipe book entry points at the activation recipe yet, so a player has
  no in-game way to learn it exists.
- **`tools/registry_items.json` is stale** — dumped 2026-09-04, so it predates both first-party
  mods. `check_era.scan_jars` now carves our own namespaces out of the dump's replacement, which
  is the durable fix and is why every checker passes, but the dump itself is still four days
  behind. Refresh it with `tools/run_server.py --run --export`, then copy
  `server/local/kubejs/export/registries/item.json` into it. Not done here: seven tools read that
  file as ground truth, and the export runs on a build whose datapack reload is known to fail, so
  replacing it deserves its own verified pass rather than a drive-by.

### B-88 — Ley line corridors, worldgen half — **RUNTIME PLACED AND ASSEMBLED**

Field item 6: "I still haven't seen the Ley line conduit shafts spawning. They may be missing a
spawn criteria or Biome." They were missing neither. **The worldgen half did not exist.** Only
Phase 1 was built — the status-effect registry and its icons. There was no block, no structure,
no template pool and no NBT anywhere in the pack, so there was nothing for a spawn criterion to
fail. B-83 recorded that diagnosis; this builds the missing half.

#### What shipped

Five jigsaw pieces on the design's fixed geometry — five-by-five clear interior, one-block shell
for a seven-by-seven envelope, channel on the exact horizontal and vertical centre, two-block
maintenance lanes either side:

| piece | size | role |
|---|---|---|
| `hub` | 17×12×17 | start piece; round distributor chamber, four spoke mouths |
| `straight` | 7×7×16 | arterial run; collars every 4, a solid relay every 12 |
| `bend` | 7×7×7 | right-angle knee |
| `junction` | 7×7×7 | four-way crossing |
| `terminal` | 7×7×7 | sealed dead relay face — **also the pool fallback** |

The terminal doubling as fallback is what stops a branch that hits the depth limit from ending in
an open hole. Weights favour straights 8:3:2:2 so the network reads as long arterial runs rather
than a knot. Its own grid at 40/18 with its own salt, deliberately *not* the archaeology salt, so
the two networks are independent finds.

#### What deliberately did not ship, and why that is not a gap — **SUPERSEDED 2026-09-08 by B-89**

> The reasoning below was correct on 2026-09-07 and the constraint it rests on is gone: `first_party_mods/alfheim_leyworks` now owns the block, and the corridors place the dormant variant. The starting state it describes still holds — worldgen still places *only* dormant nodes, and lighting one is a crafting operation. Left in place because it records why the node was absent rather than missed.

`alfheim:ley_conduit_node` — the six-direction beam block — is **not** here. A block entity that
projects and retransmits a beacon payload is Java, and this pack has no mod that owns worldgen
blocks. That is the intended starting state rather than a shortfall:
`LEY_LINE_CHANNEL_CORRIDORS.md` says so directly — *"The network begins as archaeology rather
than infrastructure. Most nodes are dormant or disconnected."* So the channel is static and
roughly one length in six has gone out, reading as leyline stone. A dormant network is the thing
the player finds and repairs; the live beam is the later mechanic, not a missing half of this one.

#### Measured

Fresh world, 512-block patch: **`alfheim:leyline_corridors` placed twice**, and the pieces
assembled rather than merely recording a start — 22 sections of shell brick, 21 of polished deck,
14 of carved collar, 18 of lane rail, 16 of relay node, 41 carrying the luminous channel, plus
chains and lanterns. All five piece types are represented in the ground.

#### Open

- Client visual review of corridor scale, the relay pinch points and the hub silhouette.
- ~~The conduit block and the beacon-pyramid transmission network remain Phase 3.~~ **Closed by
  B-89 2026-09-08.** The decision was taken: the block lives in a second first-party mod,
  `first_party_mods/alfheim_leyworks`, not in the companion. Node-to-node retransmission is still
  outstanding and is now tracked under B-89.

### B-87 — Deepworks surface entrance — **RUNTIME PLACED AND CO-LOCATION PROVEN**

Field item 12's second half. B-83 fixed the grid pitch, but the complexes stayed invisible: all
three families sit at absolute Y -58..-10 with `terrain_adaptation: none`, and every jigsaw in
the chain is at local y=3. They are entirely horizontal. A player standing directly on one sees
ordinary ground.

#### The headworks

A surface winding-gear landmark — spoil apron, broken head frame, open shaft mouth, ladder,
a lantern still burning — over a timbered shaft that chains downward.

**One generic head, not three matched ones.** The archaeology set picks a family with its own
weighted roll; a second set would roll independently and a Tomb portal would stand over a Quarry
a third of the time. A neutral elven mine head is correct over all three and cannot desynchronise.

**Co-located by construction.** `RandomSpreadStructurePlacement` derives its chunk from spacing,
separation and salt plus the world seed — nothing else. The headworks set uses **identical**
values to `deepworks_archaeology`, so both resolve to the same chunk.

**The shaft chains rather than being one piece,** because the gap is 50-130 blocks and varies with
both terrain and the family's own depth roll. No fixed-length piece spans that. Six 24-block
segments give 144 blocks of reach; an overshoot is a shaft that passes through the complex, which
is the outcome we want.

#### A codec cap found the hard way

The first attempt used `size: 10` and **failed world load outright** —
`Value 10 outside of range [0:7]`. A datapack that fails to load takes the dimension with it, so
the segments were deepened from 16 to 24 blocks to keep the reach at 144 with `size: 7`, and
`check_deep_archaeology` now asserts the cap, the heightmap projection and the co-location keys
rather than relying on memory.

#### Measured

Fresh world, 640-block patch around the origin: **`alfheim:deepworks_headworks` placed twice**.
One at chunk (19, 21) sits **exactly on the `faultwork` complex** — co-location confirmed against
the real generator, not just against the JSON.

The second, at chunk (15, -30), had no archaeology start recorded. That chunk was only generated
to `structure_starts` status — its biome array still reads the `minecraft:plains` placeholder — so
it is not a clean observation either way.

#### Open

A real asymmetry remains: the archaeology structures test `#alfheim:deepworks_land` at their own
depth (Y -58..-10) while the headworks tests it at the surface. Alfheim's biomes are three
dimensional, so the two checks can in principle disagree and leave a mine head over nothing.
Whether that actually happens needs a wider sample than two placements. Client visual review of
the head, the shaft descent and the junction with the complex is also open.

### B-86 — Golden Fields terracing — **CALIBRATED IN FRESH WORLDS; CLIENT REVIEW PENDING**

Asked 2026-09-08, via a design brief: rework Golden Fields from "a vaguely hilly biome with
random stamps of wheat smashed into the surface" into terraced, organised fields integrated with
the terrain, using layered Voronoi/Worley for plot mapping, following the heightmap without
overwriting world generation.

#### Two premises in the brief did not hold, and both changed the build

1. **There is no Forge mod to write logic in.** `INSTRUCTIONS.md` §7 line 201 — "Java & Gradle |
   N/A — no source project". No `build.gradle`, no `gradlew`, no `src/`. Everything below is
   data-driven density functions instead.
2. **Alfheim does not use TerraBlender.** Its biome source is `libx:layered`; TerraBlender governs
   Midgard. So "multiply by the TerraBlender biome edge weight" has nothing to read here.

#### And 1.20.1 has neither Voronoi nor floor()

Verified by enumerating every density-function type used across all 35 vanilla density functions
and noise settings. No `voronoi`, no `worley`, no `cellular`, no `floor`, no modulo.

Two substitutions carry the algorithm across:

- **Quantization without `floor`.** A staircase is a SUM OF UNIT STEPS, and a unit step is one
  `y_clamped_gradient`. 22 of them cover Y 56..144 at N=4. Subtracting that staircase from `y`
  gives a sawtooth, and adding a sawtooth to a density that falls with height cancels the fall
  across a tread, so the iso-surface pins to the tread and drops at the riser.
- **Voronoi is not needed for the terracing at all.** Quantizing the height field produces
  contour-following terraces on its own — the plateau boundaries *are* the contours of the base
  height, which is where terrace walls belong on a hillside. Cell structure is only needed for
  plot identity in the decoration, and `|ridge|` supplies both a tiling partition and an
  edge-distance proxy.

#### Measured in a standalone prototype before any datapack edit

420-block cross-section, comparing surface heights column by column:

| | flat-run share | max 1-block rise | columns exactly on a tread |
|---|---:|---:|---:|
| control | 75.4% | 1 | 46.0% |
| terracing at full strength | 94.3% | 4 (= N) | **100.0%** |
| edge-blend × biome-fade | 82.3% | 4 | 68.1% |

Residues 1, 2 and 3 are eliminated entirely at full strength. Two errors were found and fixed by
measurement: the riser must span `k..k+1` (at `k-1..k` it terraces just as hard but leaves every
flat one block below the tread — 73% of columns on the wrong residue), and the sign/phase decides
whether the surface is pulled onto treads or pushed off them.

#### Shipped assets

| Asset | Role |
|---|---|
| `alfheim:fields/terrace_saw` | 22 summed risers + bare `y`; clamped to ±0.5 |
| `alfheim:fields/plot_edge` | `\|ridge\|` cell proxy, `flat_cache` |
| `alfheim:fields/terrace_weight` | edge blend × continentalness window × weirdness ramp, all `flat_cache` |
| `mythicbotany:alfheim_final` | `add(<untouched density>, mul(weight, mul(0.22, saw)))` |
| `alfheim_surface` rule set | `steep` → retaining wall; plot interior → farmland; verge → path |

The weight is full only inside continentalness 0.19‥0.235 — the lower, flatter part of Golden
Fields' 0.15‥0.30 band, leaving the higher ground continuous and wild — and is exactly zero at or
below weirdness 0.03, so it cannot bleed into Dreamwood across the weirdness-0 split.

**A surface rule may test the biome; a density function may not.** A surface rule only chooses
which block to paint on a column that already exists, so a biome test there costs at worst a
colour seam. A density branch keyed on biome *moves terrain*, and where the climate threshold and
LibX's nearest-biome result disagree the result is the sheer wall B-82 had to revert.

#### Guards

`check_golden_terraces.py` asserts six invariants, G1–G6: files match their generator; the
injection is an `add` whose first argument is the untouched density unchanged; the weight is
**exactly** 0.0 outside the biome box across a 7,200-sample sweep; the weight never steps by more
than 0.05 between adjacent samples; the sawtooth stays within ±0.5 across the whole world height
and peaks on every tread line; and the surface rule is gated to Golden Fields.

Three existing guards navigated `alfheim_final` assuming the void `range_choice` sat at the top.
Rather than loosen them — they are the ones that caught B-82 — `gen_golden_terraces.strip()` peels
the addend off and each keeps asserting exactly what it asserted before, now on the base, plus
that what was stripped is the known terrace term. `check_deep_terrain`'s upstream-surface-rule
assertion was also made position-independent, because indexing it broke the moment a rule was
prepended.

#### Measured in fresh worlds — and the ceiling is not the amplitude

`locate` puts Golden Fields ~1,300 blocks from spawn and the spawn area contains none of it, so
`run_server.py --forceload X Z R` was added to generate a real patch where a probe can read it.
Three worlds, same seed, same patch:

| | on-tread share | uniform baseline | enrichment |
|---|---:|---:|---:|
| N=4, amplitude 0.22 | 42.0% | 25% | 1.7× |
| N=4, amplitude 0.60 | 49.9% | 25% | 2.0× |
| N=8, amplitude 0.60 | 36.0% | 12.5% | **2.9×** |

Tripling the amplitude bought eight points. That is a resolution limit, not a tuning problem, and
the cause is in the noise settings: `size_vertical: 2` means Minecraft samples `final_density` on
an **8-block-tall grid** and interpolates linearly between samples. A 4-block sawtooth is a
half-cell signal the interpolator cannot represent, so most of it is averaged away. N=8 matches
the cell and pins relatively harder, but its absolute flatness is worse and an 8-block riser is
not a walkable agricultural step, so N=4 is kept at amplitude 0.60.

**The decoration works fully.** Surface samples in the generated patch: 40.6% farmland, 9.5%
dirt path, 8.2% moonstone retaining-wall brick on `steep` risers, 6.2% coarse dirt, plus wheat
planting on the flats.

#### `size_vertical: 1` was authorised, tried, measured and reverted

The theory was that 8-block density sampling averaged a 4-block sawtooth away. It was wrong twice
over, and measuring it said so:

- `alfheim_final` contains **no `minecraft:interpolated`**, so it is evaluated per block at full
  resolution. The cell grid never touched the sawtooth.
- The probe returned **49.8%** on-tread at `size_vertical: 1` against **49.9%** at 2, with
  generation time 14,221 ms against a five-run 14,395 ms baseline. Both inside noise.

A `sea_level: 64 → 100` probe confirmed the override mechanism itself works — water moved from
Y 63 to Y 99 — so the setting was genuinely applied and genuinely did nothing. Reverted to
upstream, with the measurement recorded in `gen_deep_terrain` so it is not retried blind.

#### What the ceiling actually was: coverage, not resolution

Splitting the probe by surface block made it obvious, because the surface block *is* a readout of
the terrace weight:

| surface | n | on-tread |
|---|---:|---:|
| retaining wall (on `steep` risers) | 506 | **83.0%** |
| dirt path (verge) | 411 | 63.0% |
| farmland (plot interior) | 1,779 | 59.5% |
| grass block (low weight) | 916 | 32.9% |
| wheat (sits one block *above* farmland) | 239 | 13.4% |

The terracing was already sharp where the weight was high. The soft aggregate was dilution by
low-weight columns. Widening every ramp to saturate sooner — `cont` full across 0.175‥0.265
instead of 0.19‥0.235, weirdness from 0.02, plot edge from 0.12 — moved the aggregate from
**49.8% to 59.7%** on-tread and retaining walls from 11.0% to 14.0%, at no global cost.

`check_golden_terraces` G4 was rewritten while doing this: it compared against a fixed 0.05 step
and fired on a legitimately narrower ramp. It now derives the expected per-sample rise from the
ramp widths, so it still catches a step function but not a steeper continuous fade.

#### Open

Client visual review of the shelved fields, retaining walls and plot verges. The remaining
softness is the deliberate edge blend between plots and at the biome margin; tightening it
further trades away the smooth transition that keeps this out of B-82 territory.

Client visual review of the shelved fields, the retaining walls and the plot verges is open.

### B-85 — biome distribution, and the three thin biomes — **SURVEY-MEASURED; CLIENT REVIEW PENDING**

Asked 2026-09-08: distribute the biomes better so a given seed is likelier to put all of them
within one day's travel, keep them large enough to feel significant, and give Ashen Grove,
Sundered Highlands and Hollow Marches real depth. Void biomes are excluded from the travel
target — they need flight.

#### A measurement, not a model

`tools/run_server.py --run --survey` runs `locate biome` for all 25 biomes from five spread
origins in one world; `tools/read_biome_survey.py` pools several worlds and reports median and
**worst case** per biome. Worst case is the gate: a biome 300 blocks from spawn and 5,000 from a
point 3 km east is not reliably within a day's walk, and a single probe from the origin would
have called it fine.

A day of sprinting is about 6,700 blocks, so the target is 3,000 out with time to look around.

#### What the survey found

Widening a biome's temperature or humidity slice moved its **median** but barely touched its
**worst case**. The reason is visible when the same numbers are grouped by continentalness
instead: seven biomes shared `cont 0.15..0.45` and every one came back 1,810–2,583 blocks, while
bands holding one or two came back 452–1,450. The journey is dominated by reaching that
continentalness region at all, not by finding the right climate inside it.

The nominal share of the climate cube predicts almost nothing here — `infested_warren` holds
0.72% of it and measured 24% of a real world — so this had to be measured.

#### What changed

The midland was split in two, geographically rather than arbitrarily: the cool and the wet sit
lower, nearer the water they need, and the burnt and the bright sit higher.

| Band | Before | After |
|---|---|---|
| `cont 0.15‥0.45` | 7 biomes | *(split)* |
| `cont 0.15‥0.30` | — | decayed_mire, silverbark_wood, dreamwood_forest, golden_fields |
| `cont 0.30‥0.45` | — | ashen_grove, bloomfall_vale, scorchfell |

Eight tail-gated bands were also widened: `starved_reach` −0.45→−0.35 temperature,
`decayed_mire` 0.5→0.42 humidity, `ashen_grove` −0.4→0.0, `bloomfall_vale` 0.2→0.05 then freed
entirely, `hollow_marches` −0.3→−0.2, the shore belt −0.15..0.03→−0.18..0.05, and
`infested_warren` relaxed from three tight axes to `cont 0..0.18, weird ≤ −0.2, hum ≥ 0.42`.

#### Measured result, one seed, same five origins

| | before | after |
|---|---|---|
| median of all worst cases | 1,917 | **1,629** |
| biomes worse than 2,000 blocks | 9 of 19 | **6 of 19** |
| biomes never found | 0 | 0 |

Typical travel roughly halved for the redistributed biomes: `bloomfall_vale` median 1,142→362,
`ashen_grove` 1,631→712, `dreamwood_forest` 973→390, `golden_fields` 1,350→676,
`decayed_mire` 1,174→770, `scorchfell` 601→394.

Pooled over two seeds and ten origins, all 19 land biomes were found from every origin, with
medians of 90–880 blocks.

#### The three thin biomes

`BIOME_INDEX.md` §5 now reports no land biome without vegetal decoration. Each got ground,
standing evidence and air:

- **Ashen Grove** — ash drifts of gravel and cinder livingrock, cinder boulders, charred
  gloambark stumps, dead scrub; white ash falling at 0.006, a fraction of Scorchfell's.
- **Sundered Highlands** — scree of cracked and starfleck livingrock, torn obsidian boulders,
  hardy tufts; wind-borne grit at 0.004.
- **Hollow Marches** — dead ground of gloam livingrock and soul soil, hollow boulders, standing
  witherwood, bone fields; the heaviest ash fall in the pack outside Scorchfell at 0.011,
  because precipitation is off here and the air has to carry the biome.

**Topography is done with features, not density.** B-82 removed a climate-stamped terrain branch
because thresholds and LibX's nearest-biome result do not coincide, so full columns were replaced
inside neighbouring biomes and the seams read as chunky walls. Boulders, scree patches and
re-floored ground are bounded, local and support-aware; a density branch is none of those.

#### Open

- Client visual review of all three, and of the redistributed geography.
- `mythicbotany:golden_fields` is the last biome with a single vegetal feature. It is the mod's
  own and may be right as shipped; it needs a decision rather than a fix.
- The remaining six biomes over 2,000 blocks are all bounded by continentalness region size
  (1,422 blocks). Tightening further means raising `CONT_SCALE`, which shrinks continents — a
  direct trade against "large enough to feel significant" and a decision, not a defect.

### B-84 — wooded shores and the climate-scale correction — **RUNTIME MEASURED; CLIENT REVIEW PENDING**

Two pieces of work, the second discovered while doing the first.

#### The wooded shores (field item 7, design item I12)

Three coastal biomes on continentalness -0.15..0.03, the strip where the lake and ocean floor
rises out of the water. The band deliberately straddles the waterline: trees require a dry
heightmap column and zero water depth, so the belt places itself along whatever part of the band
is land in a given chunk. It follows the coast because the coast is what defines it.

| Biome | Split on | Canopy | Floor |
|---|---|---|---|
| `alfheim:tidewood_shore` | temperature >= -0.15 | Gloambark, dense | undergrowth, driftwood, motif flowers |
| `alfheim:mistbark_shore` | the remainder | Hushbark, pale | undergrowth, driftwood, ferns |
| `alfheim:sporebank_shore` | humidity >= 0.4 | six Feywild cap colours as a real canopy | mycelium/podzol bed, spore scatter |

The band is taken from `mythicbotany:alfheim_lakes`, which measured 44% of one field world and
77% of another. Six new coastal structures keep the two-per-biome rule: Tidewatch and the
Driftwood Span, the Mistfall Shrine and Hushbark Causeway, the Sporebank Hall and Capfall Barrow.

#### The climate-scale correction (field item 8)

One constant, `CLIMATE_SCALE = 0.0625`, was applied to four vanilla noises whose base periods
span a 16x range. Region size is base period / xz_scale, so the four axes came out wildly
different:

| Axis | Noise | Base | Region produced |
|---|---|---|---|
| temperature | `minecraft:temperature` | 1024 | **16,384 blocks** |
| humidity | `minecraft:vegetation` | 256 | 4,096 blocks |
| weirdness | `minecraft:ridge` | 128 | 2,048 blocks |
| continentalness | `minecraft:badlands_surface` | 64 | 1,422 blocks |

That single fact explains B-83's monoculture. Continentalness varies on a 1.4 km scale, so ocean,
land and the Void rim always worked. Temperature varied on a 16 km scale, so a world contained
about one thermal band.

It also explains why two earlier attempts failed: both moved a *threshold* (scorchfell's floor
0.55 -> 0.45 -> 0.32) and `CLIMATE_AMPLIFY` widened the *tails*. Amplitude was never the problem.
A 16 km period means few independent samples per world, so widening a rare band does not make it
less rare.

Each axis now gets the scale its own base period needs, keeping the nesting vanilla intends —
broad thermal zones, humidity variation inside them, weirdness variants inside that:
temperature 4,096, humidity 2,048, weirdness 1,024 blocks. Weirdness also gained the 1.8
amplification it was the only axis to lack, which matters because 28 of the layer's 42 bands
split on it at -0.3, 0.0 and +0.3.

#### Measured, three worlds, one seed (-6479222785550481610)

`locate biome` from the origin. A is the old shared 0.0625; B a uniform 2,048-block target;
C the shipped hierarchy.

| Biome | A | B | C |
|---|---|---|---|
| scorchfell | **not found** | 1,324 | **2,458** |
| bloomfall_vale | **not found** | 1,154 | **2,234** |
| tidewood_shore | 6,324 | 1,024 | 2,013 |
| ashen_grove | 5,376 | 2,492 | 1,810 |
| hollow_marches | 5,077 | 1,831 | 1,697 |
| sundered_highlands | 2,805 | 1,131 | 1,154 |
| starved_reach | 618 | 618 | 618 |
| mistbark_shore | 659 | 484 | 484 |
| void_verge / decayed_mire / infested_warren | 389 / 320 / 101 | unchanged | unchanged |

The four continentalness-driven biomes are identical across all three, exactly as predicted:
continentalness was not touched. Every temperature- or humidity-driven biome improved, and the
two that could not be found at all now exist.

#### Open

- Client visual review of all three shores, and of the six new coastal structures in place.
- The shore band is 56% `sporebank_shore` within 529 chunks of this seed's spawn. That is one
  humidity region, not a bug, but it is worth a second seed before calling the three-way split
  balanced.
- `CLIMATE_AMPLIFY = 1.8` predates this analysis and may now be doing less work than it was;
  worth re-measuring once the period is right.

### B-83 — September 7 field review, twelve items — **PARTIALLY IMPLEMENTED; SEE PER-ITEM STATE**

Twelve field observations from the 22:08 session on `New World-fellhammer`. Each is recorded with
its diagnosed root cause, because five of the twelve turned out to be a different defect from the
one the symptom suggested.

| # | Item | Root cause | State |
|---|---|---|---|
| 1 | Infested Warren reads as gently rolling hills | Biome had no identity features at all: ores plus `mythicbotany:alfheim_grass`. Save probe: 566 of 876 surface samples were plain grass block | **static implemented** |
| 2 | Decayed Mire, likewise | Same. Ores, apothecaries, alfheim_grass. 76 of 93 samples plain grass block | **static implemented** |
| 3 | Claim far too large | `HUB_RADIUS = 128` square centred on the tree, sized for a placement probe retired in an earlier pass. The complex spans X -72..71, Z -120..23 and is centred at Z = -48, so the claim over-reached south and barely cleared the north wing | **runtime validated** — console reports 100/100 chunks, down from 289 |
| 4 | Boundary caves full of noise blocks | Three causes: `inclusions` noise at firstOctave -4 sprayed single blocks; upper 3-stone and lower 5-stone strata schemes banded at different widths so no edge lined up; and a 22-block randomly dithered blend band sat at Y -30..-8, exactly cave height | **static implemented** |
| 5 | Surface structures need a high-detail pass | The decay/collapse passes delete blocks without asking what rested on them. S11 found wholly unattached blocks in 15 pieces — floating lanterns in four keeps, detached stairs in several towers, 318 in `faultwork/wing` | **loose blocks repaired; the wider detail pass is still open** |
| 6 | Ley line conduit shafts never seen | Not a spawn-criteria fault. The worldgen half does not exist: no `alfheim:ley_conduit_node`, no structure, no template pool, no NBT. Only Phase 1 — the status effects and their icons — is built, exactly as `LEY_LINE_CHANNEL_CORRIDORS.md` states | **diagnosed; unbuilt** |
| 7 | Wooded shoreline biomes, incl. mushroom forests | Not started. Already queued in B-80's later list | **not started** |
| 8 | Remaining development gaps | See "climate monoculture" below — the largest open gap, and it is upstream of items 1, 2 and 7 | **evidenced** |
| 9 | Wings do not connect to the central area | The amphitheatre had one carved aisle, south to the Greatbole. The three wings each drive a seven-wide spine at the right elevation into the *intact* outer seating bank: five to six blocks of marble, with a two-block void at the seam | **static implemented, geometry verified** |
| 10 | Noise blocks hovering over the main dais | `courtyard_detail` ran after the aisle carve and placed rubble, moss and marble at *computed* tier heights whether or not that tier survived the collapse roll or had been cut away. Rim columns, colonnade columns, court seats and vines had the same defect | **static implemented, verified 0 floating** |
| 11 | System crawled to a halt; no crash | Not a pack error — the log is clean and the single tick overload is world-join. Distant Horizons runs distant generation across **nine dimensions** with 14 threads at `threadRunTimeRatio = 1.0`, `threadPriority = 5` and a 256-chunk LOD radius. In 13 minutes it left **1,917 chunks at `structure_starts` status** beside the game's own 3,085 full chunks | **diagnosed; config change offered, not applied** |
| 12 | No Deepworks structure found | Not runaway world generation. `alfheim:elder_kings_tomb` did place, at chunk (19, 45), with 126 chunk references. Over the 77x91 chunks explored, a 96-spacing grid predicts 0.76 starts and exactly 1 was found. Every piece is within the 48-block limit. The real causes are the grid pitch and the total absence of a surface entrance | **spacing 48/24; ley_scars far-chunk writes fixed; surface entrance open** |

#### The climate monoculture — item 8's headline

Alfheim's temperature and humidity are `minecraft:temperature` and `minecraft:vegetation` at
`xz_scale` 0.0625, which stretches them roughly sixteenfold. The consequence is measurable rather
than theoretical:

- `New World-fellhammer`, 3,085 fully generated chunks: **six** biomes, and `alfheim_lakes` alone
  is 44.4%. Infested Warren and Decayed Mire are another 34.3% between them, which is why two
  featureless biomes dominated the whole field session.
- Seed `alfheim`, headless locate from the origin: `mana_fen` 160 blocks, `silverbark_wood` 340,
  `sundered_highlands` 891, `void_verge` 951, `hollow_marches` 1,569, `starved_reach` 1,790,
  `ashen_grove` 1,814, `infested_warren` 2,849, `decayed_mire` 3,106, `bloomfall_vale` **7,178**,
  and `scorchfell` **not found within locate range at all**.

Eleven authored biomes are not eleven reachable places. This is upstream of items 1, 2 and 7: new
shoreline forests added to the current climate field would be just as unreachable as Scorchfell.
Decide the climate scale before authoring more biomes.

#### Open, in priority order

1. Climate scale for temperature/humidity — the decision that gates items 7 and 8.
2. Surface-structure detail pass. The loose-block sweep is done and S11 is clean; what remains is
   the actual quality pass on the 44 surface pieces — silhouette, interior legibility, materials.
3. A surface entrance for the Deepworks families, so a player can find one without caving to Y -40.
4. Ley line corridors Phase 2: the conduit block, then the jigsaw network.
5. Wooded shoreline biomes and mushroom forests.

### B-82 — terrain smoothing and clean Void reset — **FRESH-WORLD RUNTIME VALIDATED; CLIENT VISUAL PENDING**

The screenshot-driven smoothing pass is implemented. The erroneous Y=191 climate plateau is gone,
so Hills, Plains, Silverbark and Starved Reach again share continuous upstream terrain. The Void's
interpolated multi-noise debris and terminal fields are also removed from final density: one quiet,
supported shore blend now ends at the cliff, with clean empty space beyond it. A broad aquifer dry
shoulder and basal picker guard prevent water from cascading into the Void.

Fresh world `void-margin-20260907-210920` passed 170 sampled columns with zero Void fluids and zero
far-field terrain overflow; all static gates pass. Remaining acceptance is a flight through newly
generated client chunks. After that, resume the user's next priority: reintroduce each Void biome's
identity as sparse, bounded, support-aware landmarks and formations, never as unbounded 3-D density
noise. B-82 supersedes B-81's rejected Hills plateau and B-79's rejected procedural debris field.

### B-81 — September 7 field repair — **STATIC IMPLEMENTED; FRESH-WORLD ACCEPTANCE PENDING**

The current generator pass addresses the screenshot/log report: exact-origin Greatbole and expanded
royal complex, API-owned automatic spawn claim, custom Elder-wood roots and shared circulation,
the now-superseded Hills terrain experiment, normal Wild Elf habitat, one mutually exclusive Deep archaeology grid,
scaled tomb-door bays, and bounded Slag Terraces. Dedicated static checks pass. Highest-priority
remaining gate is one extended fresh-world client run proving no far-chunk errors, exact origin
geometry/terrain fit, FTB ownership/restart persistence, natural Wild Elves, Hills elevation and
natural archaeology separation.

### B-80 — September 5 field-review corrections — **I1 + I10 RUNTIME-PROVEN; I7 DIRECT-ASSEMBLY-PROVEN; I11 LOAD-SMOKE; I2–I5 + I8–I9 STATIC 2026-09-07**

The full ordered plan, screenshot evidence, acceptance gates and running completion record live in
`alfheim_reclaimed_design/FIELD_REVIEW_STAGE_2026-09-05.md`. Immediate work is the failed Great
Bole spawn system, Scorchfell's native hot-stone surface/features, ocean density/name, custom elf
runtime spawning and the ocean-to-Void-Verge transition. Starfall rain is accepted unchanged.

Deferred but explicitly queued: one coordinated custom-block and Hollow Court NPC texture run. Natural TaxTreeGiant placement was removed
from the plan by later field-review decision because it would intrinsically alter Alfheim's silhouette.
Sparse Jaffabricate orange and normal-size seasonal Feywild trees are now statically implemented. I9 rebuilds
the carpet/balustrade/wall-sconce geometry and removes vertical source-atlas bleed before centering all 480
armory icons; restarted-client signoff remains. I11 places the twelve independent Knight Quest creatures
once each in climate-matched hostile ruins using bounded vanilla spawner profiles; static checks and a fresh
Forge load pass, while placement/combat review remains. I7 now implements four climate-matched pixie
hamlets on small organic sky islands, each with a seasonal tree, functional vanilla food garden and
buried bounded spawner beneath its culture-specific dew well.

The later queue adds multiple distinct forest identities, at least two dense wooded-shoreline environments
around Alfheim's large ocean footprint, climate-matched Feywild mushrooms in every non-Void biome, a custom
Bramble family without repeating growth logic, and more local-stone crystalline/geode features throughout
the six Void biomes. The Void remains absolutely vegetation-free.

I1–I5 now have an implementation pass: deterministic Great Bole placement, native Scorchfell
surface/lava features, sparse named ocean vegetation, removal of the wood-elf skin handler, and a
continuous low littoral density blend at the Void Verge. Static checks pass. After Java was cleared,
a fresh headless world proved the final bounded-lattice hub path: trunk, crown, court and base each
returned success; the baked anchor and crown marker were unique; the world hub anchored on its first
attempt; and all eight tagged court NPCs persisted in their authored seats. I2–I5 still need visual
acceptance in newly generated client chunks, and natural wild-elf spawning still needs field proof.

I8 now adds six restrained climate accents through Alfheim-owned wrappers around the installed
Jaffabricate/Feywild placement rules. The wrappers retain the source rarity and ground-safety predicates
while avoiding cross-mod feature-order cycles. Giant-tree world placement remains disabled, and denser
Feywild tree groupings remain reserved for the deliberately shaped pixie sky islands.

I7 is direct-assembly runtime-proven. Spring, summer, autumn and winter each own a fixed-height
one-step jigsaw hamlet: one 33×33 tapered island, a seasonal dew well, three houses selected from
four forms, a functional vanilla garden and one complete matching Feywild tree. A saved-world audit
of one directly placed hamlet per culture found all six children, no exposed jigsaw blocks and one
correct bounded seasonal-pixie spawner beneath every centre. Natural random placement, interaction
with Continuity Works' automatic 500-block structure exclusion, spawner activation/escape and client
appearance remain open.

I10 is runtime smoke-proven. Elementium is now size 12/count 6, Dragonstone size 7/count 2, and the new
climate-limited Fey Gem feature size 6/count 3. All three have variants for the 42 natural Deep/Void hosts
(126 blocks total) with source-equivalent loot and startup-only registration. A clean fresh server generated
639 full Alfheim chunks containing 26 naturally selected hosted IDs from all three families. Wider density
sampling and client texture review remain.

I11 is load-smoke-proven. Twelve Surface Works templates now contain one intentional Knight Quest encounter
each. The generator uses baked vanilla spawner block entities and three bounded profiles rather than a
recurring script. The NBT coverage/profile checker and its self-tests pass; a fresh dedicated Forge world
reached Done and exited 0. Natural placement, activation and combat balance remain a client gate.

### B-79 — Void Margins definition and dedicated stone classes — **FEATURE-BOUND GEOLOGY STATIC IMPLEMENTED 2026-09-06**

Requested examples/extended definition are recorded in `alfheim_reclaimed_design/VOID_MARGINS.md`:
six environments including the existing Verge, 18 proposed stone families, 126 planned block
forms, concrete building/exploration examples and a generated concept board. The companion JSON
catalog is valid and its proposed stone IDs do not collide with live content.

The 18 families and six environments are live. The density repair now gives the Verge noisy
relief and an intact shore, then uses 3-D body/fracture/shape noise to taper and undercut outer
masses before the terminal empty field. Six mineral formations and all twelve Void structure
families are generated with terrain-owned support contracts and no terrain adaptation. The old
Verge Spire self-generated island is removed. Static worldgen, feature-order, structure and
complete Void-support checks pass. Fresh-world/client traversal remains the acceptance gate.

The follow-up geology pass removes the shared random three-stone wall wash. All eighteen materials
are now bound to named feature roles in catalog schema 3: caps, cliff backing, pressure-slab rind,
fault cores, split seams, prism cores/crowns, fossil ribs and resin halos, burial faces/shelves/
backing, terminal cores/shells and tiny Astralite indications. Each lateral biome also has a
distinct density composition rather than a different height window over one common blob. Rootfall
is the key regression guard: its geometry and Rootfossil surface both consume `root_ribs`, while
its placed Root Aprons descend 7–18 blocks through existing Void-natural support. The new checker
and four mutation tests pass; a fresh Forge server accepts every codec. Client legibility remains
open. The pre-existing aquifer spatial leak still fails the full dry/far-field audit and remains a
separate repair item; the tested opposite polarity was worse and was reverted.

### B-78 — The Deep: expanded Livingrock library and colossal cavern province — 2026-09-05

User priority: resume the Deep and grow the former small stone set into a broad Alfheim building
library, including many non-magmatic varieties. Design: `alfheim_reclaimed_design/LIVINGROCK_LIBRARY.md`.

Material foundation implemented: 24 families with seven forms each, plus six mana-glasses and
slag; 175 blocks and 174 decorative stonecutting recipes. **Material contract runtime validated**:
175 placements, 174 recipes, 374 loot checks, zero audit errors. See `EXECUTION_STATE.md` for
evidence. Visual review remains a client gate.

D3/D4 and initial D5 are now **runtime validated for sampled terrain**: natural geological masses,
masked colossal cave volumes, basal lava and four richer native bloom features. Paired fresh worlds
show 216-block open spans, 164-block lava spans and roughly twice the ore density in sampled solid
rock. See `DEEP_TERRAIN.md` and `EXECUTION_STATE.md` for exact evidence and limits.

The sharp y=23 contact is replaced by a noisy y=8..42 blend. Sixteen biomes now have individual
five-stone geological palettes with two vertical permutations and inclusions. All twelve blooms
have matching variants for all 24 Deep and 18 Void host stones. **D6 is fresh-world load and
natural-generation validated:** six aligned chandelier, ley-scar and mineral-column variants plus
lava-anchored slag terraces decorate existing cavern faces. A 2,025-chunk Alfheim sample naturally
contained four Mana-glass alignments. Client traversal/rarity tuning remains. Continuation: D7
anchored underground quarries, tombs and faultworks. Existing native ore routes and processing are
preserved; Midgard ore replacement tags remain untouched.

**Role:** intent and sequencing. A backlog item is not evidence that work began.
**Live state:** `EXECUTION_STATE.md`. **Doctrine:** `INSTRUCTIONS.md`.

Eligibility is strict: an item is eligible only when every dependency listed is `complete`.

---

## Now eligible

### B-77 — Fey wildlife, elf variants and useful drops — **RUNTIME VALIDATED 2026-09-05**

User priority: Fey creatures and the elf variants/drops; zombie work parked. Details and sources:
`alfheim_reclaimed_design/FEY_WILDLIFE.md`. 18 registered species, 53 habitat assignments,
13 new items, 14 recipes and one optional bestiary chapter. Wild/savage/demonic elves now have
distinct stats/traits and trophies; every trophy has an existing-supply use.

`tools/run_fey_validation.py`: exit 0, `server/fey-console-20260905-064250.log`, zero habitat,
entity or loot errors. 4,608 engine loot evaluations cover player-kill restrictions and counts.
Static and regeneration checks pass. Next: client visual/combat/recipe acceptance. No native
Husbandry XP or new breeding mechanics were added. B-70's old deer/toad blockers are superseded.

### B-76 — Infectious zombies cannot reach Alfheim; the placement gate crashed the boot — **PARKED BY USER 2026-09-05; GAP OPEN**
User: *"A previous generation run has introduced a new spawn bug. It crashes on boot."*

`09_zombie_habitats.js` gated 99 `infectious:*` entities with `event.or(id, predicate)`. It threw
on the first iteration, and the whole handler aborted:

```
[16:50:55] [ERROR] ! Error in 'EntityJSEvents.spawnPlacement':
  Registering a new Spawn Predicate requires a nonnull placement type! Entity Type: infectious:acid_zombie
```

`or` maps to Forge's 3-arg `register(type, predicate, Operation.OR)`, which passes a null
placement type and heightmap. `SpawnPlacementRegisterEvent.register` (47.4.10, lines 78-82)
accepts that **only if the entity already has an entry**. No Infectious entity does at that point:
`AcidZombieEntity.init()` calls `SpawnPlacements.register(...)`, and it is invoked from
`InfectiousModEntities.init(FMLCommonSetupEvent)` — which fires *after* `SpawnPlacementRegisterEvent`.
The mod is not late; the hook is early. This is structural, so all 99 gates were unreachable, and
the `zombie_variants` block below them never ran either.

**`replace` is not the fix.** It would insert an entry, `fireSpawnPlacementEvent` would write it
into `DATA_BY_TYPE`, and the mod's own later `SpawnPlacements.register` would throw
`IllegalStateException: Duplicate registration for type infectious:acid_zombie`. The same crash,
one phase later, ninety-nine times.

**Unblocked** by removing the loop. Retained and unaffected: `alfheim:populated_biomes`, every
biome-modifier extension, and the 15 `zombie_variants` placements — that mod registers none of its
own (it gates spawning with a `checkSpawnRules` mixin), so `replace` is the correct operation
there, and those 15 ids were checked against the registry export.

**The open gap.** `AcidZombieNaturalEntitySpawningConditionProcedure` compares `Level.dimension()`
against `Level.OVERWORLD`. So Infectious reaches Midgard through the biome modifiers with no
override at all, and can never spawn in `mythicbotany:alfheim`. Forcing it requires
`MobSpawnEvent.SpawnPlacementCheck` with `Result.ALLOW`, fired from the patched
`SpawnPlacements.checkSpawnRules` via `ForgeEventFactory.checkSpawnPlacements`. Neither KubeJS nor
EntityJS exposes it — `EntityEvents.checkSpawn` receives an already-constructed `LivingEntity`, so
it can deny a spawn but never allow one the placement check has already rejected. Closing this
needs Java: a listener in Continuity Works. Until then it stands as a design choice — Alfheim is
free of Midgard's plague.

`kubejs/zombie_spawn_gates.json` and the gate derivation in `tools/gen_zombie_habitats.py` are kept
as evidence. The JSON is currently unconsumed.

---

### B-74 — The player spent the whole session in Midgard — **FIXED 2026-09-04**
User: *"On world spawn, spawned in an Overworld instead of Alfheim."* and *"Chat text was
logged that said the hub hadn't spawned!"*

Both are the same failure. Reconstructed from `logs/latest.log`:

```
12:47:52  world load -> hub/create -> forceload -> resolve begins retrying
12:48:23  player logs in AT (-8.5, 65.0, 0.5) in minecraft:overworld   <- 31s after load
12:48:24  03_hollow_court.js: "8/8 missing ... the Greatbole has not generated"
12:50:20  hub/fallback: "provisional origin spawn set"                 <- 2m28s after load
12:50:42  session ends
```

The hub needs **441 chunks to generate** before its baked anchor exists. The player joined in
**31 seconds**. Everything downstream was built on an anchor that did not exist yet.

Three separate defects, and the second is what made the first invisible:

1. **`hub/send` did nothing and reported success.** Both its commands were anchored on
   `at @e[...marker...]`; with no marker, both no-oped. But `sendHome` gated on
   `if (placed > 0) return`, and `/function` reports *how many commands it executed*, not
   whether any did anything — so it came back non-zero, the fallback never fired, and the
   player never left Midgard.

2. **The success path logged nothing.** The session log contained no evidence either way. That
   is the identical "recorded success without observing it" fault B-44 was about, in a
   different function.

3. **The delayed verification never reported.** `confirmAndAnchor` prints on *both* branches
   and printed neither, so the scheduled callback did not run. `scheduleInTicks` does exist on
   this build (`MinecraftEnvironmentKJS`), so the cause is unresolved — which is why the fix
   does not depend on knowing it.

**Fixed so that crossing into Alfheim never depends on the hub:**

- `hub/send` now **crosses first, unconditionally**, then refines onto the anchor if one
  exists. With no anchor it lands the player on legal ground within 160 blocks of the origin
  and tags them `alfheim_awaiting_hub`.
- `hub/anchor` **collects** those players when the tree finally resolves — teleports them to the
  gate chamber, re-anchors their spawnpoint, and tells them. A fast join is now self-healing
  instead of permanent.
- `sendHome` logs on every path, and asks the game where the player is rather than trusting a
  return value.
- Verification runs **immediately as well as** on the delay, so the log always says something.
- Force-load is now **two-stage**: 81 chunks first (the disc the tree occupies when it pins to
  chunk 0,0, which is the normal case), widening to 441 only at attempt 6 if the tree really is
  not there.

---

### B-75 — Midgard showed vanilla biomes, not Continuity Works — **UNDER MEASUREMENT 2026-09-04**
User: *"Overall still had vanilla biomes not continuity works."*

Everything upstream of the world looks correct, and none of it is evidence:

```
Registered region continuityworks_biomes:overworld_templates to index 1 for type OVERWORLD
Initialized TerraBlender biomes for level stem minecraft:overworld
```

`config/continuityworks-biomes-common.toml` has every family enabled — 8 templates, 8 abyssal,
128 anthology — and `regionWeight = 20`, its maximum. The jar ships 146 biome definitions.

So the question is whether any of it *generates*, and `locate biome` is the instrument that
answers it — the same one that proved nine of eleven Alfheim biomes unreachable earlier the
same day. Six probes added to `tools/run_server.py`: two CW templates, two CW anthology, one
Regions Unexplored, and `minecraft:plains` as the control.

**Note the confound:** the player was in Midgard for only ~2 minutes and part of that in
spectator. A small sample of a weighted region mix is not evidence of absence. The probes are.

---

### B-73 — Liquid Bifrost was finite — **FIXED 2026-09-04**
User: *"We also need a high level renewable bifrost recipe. One would think using the mixer,
with say water and a renewable crystal based ingredient... and the correct quests explaining how
this process works."*

Pools generate at 1-in-40 chunks and do not come back. The bridge between thirteen magic systems
was a **consumable that ran out**, so a player who spent their last bucket on the wrong
conversion had permanently lost access to a system — a failure that is invisible until it has
already happened.

```
create:mixing, heated
   2 x #alfheim:crystal_shards
   1 x botania:mana_powder
   500 mB minecraft:water
   -> 250 mB alfheim:liquid_bifrost
```

**Era VII**, because `cr_mix` (`create:basin`) is first taught by the Era VII ladder — the
earliest era that can require a mixer without breaking the ordering rule.
`#alfheim:crystal_shards` already held exactly the six crystals with a budding block, so the tag
*is* the renewability guarantee; `frost_shard` has no budding form and is already excluded.

Three quests on a new `extra` hook: *A Crystal That Grows Back* → *Stop Going To The Lakes* →
*Spend It Freely Now*.

**Also integrated this pass:** textures and models for all four tiers (they were rendering as
the missing-texture checkerboard), `#alfheim:bifrost` and `#alfheim:bifrost_distilled` item
tags, the chain split into era-scoped files so coverage can see it, and six quests in Eras II
and III. Coverage gap fell 74 → 65 with every bifrost output covered and zero ordering
violations.

---

### B-74 — The Guild Regalia: 63 elven Curios for six classes and nine professions — **ASSETS STATIC VALIDATED 2026-09-04**
Design: `alfheim_reclaimed_design/CURIOS_AND_PROFESSIONS.md`. Matrix `curios/SUITE_MATRIX.md`,
inventory `curios/INSTALLED_CURIOS.md`, catalog `curios/curio_suite_catalog.json`. Generators
`tools/build_curio_inventory.py` and `tools/build_curio_plan.py`.

| Planned | Detail |
|---|---|
| 36 class pieces | signet and emblem, three ranks, six Mine and Slash base classes |
| 27 profession cuffs | three ranks, all nine native professions |
| 46 anchors | existing installed functional Curios, referenced as optional, never required |
| 3 ranks | Apprentice (Era II), Guild (Era V), Master (Era VIII) |
| 0 new slots | signets use `ring`, emblems `necklace`/`charm`, one active cuff `bracelet` |

**Asset build exists:** 63 textures, models and startup declarations, with four additive Curios
slot tags. `tools/gen_curios.py` derives art from existing vanilla textures and Alfheim materials
using PIL; `tools/check_curios.py` reports 0 problems and 18/18 fault-injection cases fire.
Review: `tools/curios_review.png`. Effects, recipes and player proof remain unimplemented, and
runtime registration/equipping has not been verified for this build.

**The rule the system rests on:** one transaction per reward. A Curio reacts only after the owning
system accepts the native action — it may display state, route a result, or open an explicit station
operation. It never repeats XP, drops, class access, station authority or mod resources. Crafted
rank stays tradeable; profession proof is server-owned player state and every effect is capped by
the wearer's own native profession tier, so a bought cuff cannot carry the seller's progression.
Automation may prepare materials but cannot generate personal proof.

**Reproduction, verified 2026-09-04:** `python tools/build_curio_plan.py` → *6 class suites, 9
profession suites, 63 planned items, 46 installed functional anchors, 0 missing IDs*, exit 0, and
the generator is deterministic — `SUITE_MATRIX.md` and `curio_suite_catalog.json` are hash-identical
across reruns. `python tools/build_curio_inventory.py` → *147 wearable IDs (114 functional, 33
cosmetic), 19 slot definitions, 14 live slot types*, exit 0.

**Depends on:** a live per-player slot/capacity probe. The 14 live slot types come from a headless
run, not from a player entity; nothing yet proves how many `ring` slots a real player actually has.

**Next exact action:** restart the client and check the new items in JEI, run the slot/capacity
probe, then implement the effect slice — the Warrior signet with its Greatbole Torque emblem,
and all three Mining cuff ranks. Numbers (cooldowns,
ranges, percentages, costs) stay deferred until event ownership and NBT preservation are observed
at runtime.

**Accept:** level 4 — the slice registers and appears in JEI with no script error; level 11 — a
Warrior equips the signet, a miner earns a rank, and neither doubles a native reward.


### B-73 — Thirty-two surface structures and the Cartographer — **BUILT (static) 2026-09-04**
User instruction: *"a small subchapter of FTB quests that is explorers maps that are repeatable
purchase actions ... And I want at least two explorable interesting structures per Biome that we
have. These should be surface features castles ruined castles large craters a large quarry mine
and so on."*

Design: `alfheim_reclaimed_design/THE_SURFACE.md`. Manifest `tools/surface_works_manifest.json`,
generators `tools/gen_surface_works.py` and `tools/gen_cartographer.py`, checker
`tools/check_surface_works.py`.

| Built | Detail |
|---|---|
| 32 structures | exactly two in each of the sixteen biomes in the Alfheim layer |
| 10 archetypes | castle, quarry, crater, tower, hall, aqueduct, span, barrow, wreck, shrine |
| 7 palettes | elven marble, livingrock, sourcestone, burnt, drowned, bone, void |
| 183 files | nbt, template pools, structures, structure sets, 32 biome tags, 10 structure tags |
| 10 maps | one `exploration_map` loot table per archetype, pointed at that archetype's tag |
| 3 chest tables | common / uncommon / rare, commodities only — no runes, no tier materials |
| 1 chapter | `cartographer.snbt`, 10 repeatable purchases and 2 guides, campaign group |

**The maps are per TYPE, not per structure**, which is what "different types of structures" asks
for and what `#minecraft:village` already does for five village types.

**A map is bought, not earned.** An `ItemTask` with `consume_items` is never submitted by an
inventory change (`submitItemsOnInventoryChange()` returns `!consumesResources()`), so the
player must click to pay — without that a repeatable shop would drain their petals in a loop.
Payment is petals plus the dimension's own stone, both renewable from the first hour, and
nothing on the price list is a spine material or a ladder intermediate.

**Deferred to runtime (nothing here has been seen in a world):** that any of the thirty-two
generates; that `start_height: {absolute: -ground}` puts the crater bowl and the quarry floor at
the right depth; that the two `OCEAN_FLOOR_WG` structures sit on the lake bed; that
`verge_spire` finds ground on the floating islands; that a purchased chart fills rather than
returning blank; and what thirty-two extra `random_spread` sets cost at chunk generation.
**Accept:** level 9 — `locate structure` finds each of the thirty-two in a fresh world; level 11
— one chart of each of the ten bought and confirmed filled.

### B-67 — The canopy never generated — **FIXED 2026-09-04**
User: *"The Great tree doesn't seem to actually spawn its canopy."*

Every piece was individually legal, the pools paired, the structure loaded without error, and
the crown was **culled at placement** every time. Jigsaw rejects any piece landing further than
`max_distance_from_center` from the structure start, and the tree was 184 blocks tall.

The cause was a wrong sentence in `SPAWN_HUB.md` §2.1: *"a 190-block tree centred on its base
spans ±96 — inside the cap."* A tree grows **upward** from its base, so its span is its full
height, not half of it.

Raising the cap to 128 to fit it made things worse: world creation then refused the structure
outright with `Structure size including terrain adaptation must not exceed 128`, because
`JigsawStructure`'s codec validates `max_distance_from_center + margin <= 128` and the margin is
**12** for every `terrain_adaptation` except `none`. The real budget with `beard_thin` is **116**
— which is where the original 116 came from.

Tree rebuilt at **112** blocks (48 base + 1 × 24 trunk + 40 crown). Guarded by **S9**, which
walks the pool graph upward from `start_pool` and measures against the real budget rather than
trusting a constant, and by an assertion in the generator.

**Runtime-proven.** A probe marker baked into `greatbole/crown` — the piece that was being
culled — reports its own world position:
```
The nearest alfheim:greatbole is at [96, ~, -96] (135 blocks away)
crown probe   [72.5d, 157.0d, -71.5d]
hub anchor    [78.5d,  66.0d, -71.5d]
```
Base origin 65 + 72 (base + trunk) + 20 (probe offset within the crown) = 157, exactly.

---

### B-68 — The claim and the spawn were pinned to the origin; the tree was not — **FIXED 2026-09-04**
User: *"the spawn area around the Great Tree was never claimed by admin team and we didn't spawn
inside it, which we should."*

One root cause, two symptoms. `concentric_rings` does **not** pin a structure to `0,0`. It
computes the ring-0 position — which for `distance: 0` really is the origin — and then snaps it
to a `preferred_biomes` match via `findBiomeHorizontal(..., radius 112, findClosest = true)`.
The claim was a hardcoded ±96 box at the origin and the spawn anchor was a marker summoned at
`0 250 0` and dropped by `spreadplayers`. Tree in one place, claim and spawn in another.

`#alfheim:has_greatbole` held **3 of the 16** biomes in the layer, and it is read in two places
doing two different jobs:

| Field | Effect of a narrow tag |
|---|---|
| `structure.biomes` | **Validity.** The Greatbole does not generate *at all* off-tag — the earlier *"No spawn structure on Fresh World"* |
| `structure_set.preferred_biomes` | **Position.** Forces the search outward, moving the tree up to 112 blocks |

Fixed three ways, because the anchor must not depend on the position being right:

- **Tag widened to 14 of 16.** `findClosest` returns the centre when the centre matches, so this
  pins the tree to chunk `0,0` whenever the origin is buildable. Only `void_verge` (no ground)
  and `alfheim_lakes` (`WORLD_SURFACE_WG` counts fluids, so the trunk would stand on water) stay
  out. Guarded by **S10**.
- **The spawn anchor is baked into `greatbole/base.nbt`** as a marker standing in the gate
  chamber, four blocks in front of the gate and facing it. It lands wherever the structure lands
  and cannot desynchronise from the tree. Same reasoning as the court.
- **Claim widened to 192** — 112 worst-case displacement + 48 half-structure + 32 court apron —
  so it contains the tree even when the fallback fires.

**Runtime-proven.** On the validation seed the origin *is* a lake, so the designed fallback ran
and the tree landed 135 blocks out — and the hub still anchored to it:
```
[Alfheim] provisional origin spawn set; still waiting for the Greatbole.
[Alfheim] world hub anchored to the Greatbole gate chamber.     (5s later)
```

The two-deadline resolve loop is part of the fix. `forceload add` only *marks* chunks; the
server generates them over the following ticks, so the anchor does not exist on the tick
`hub/create` runs. A single 2-minute deadline fired the fallback at 125s and the anchor appeared
at ~145s, permanently stranding the world at the origin. The fallback is now **provisional** and
`hub/resolve` keeps going, upgrading to the real anchor in the same session.

---

### B-69 — Geodes overlapping; bifrost and diluted pools everywhere — **FIXED 2026-09-04**
User: *"The Crystal Geodes seem just a little bit too frequent, I've seen a couple of examples of
Geodes overlapping"* and *"The Bifrost blocks and diluted mana pools are too common."*

**Geodes.** The reported statistic was wrong and hid the problem. `gen_crystals.py` printed the
*mean* rarity across geode types — a number no player experiences, because a player stands in one
biome and meets only the types valid there. Per biome the density was **4× to 8× vanilla
amethyst**, and at 1-in-5 two adjacent chunks rolling puts geodes inside overlap range. Retuned
to 1-in-13/15 (1-in-8 in the void), and the generator now reports **per biome**, naming the
densest.

**Bifrost and diluted pools.** Not ours: `mythicbotany:mana_crystals`, whose feature class
references `bifrost`, `bifrostPerm` and `dilutedPool`, ships at `count` uniform 1–4 with
`rarity_filter` 2 — 1–4 formations in every *second* chunk. Overridden to 1 per 12 chunks, the
same treatment the apothecaries got.

---

### B-70 — One fey creature in a fey world — **FIXED 2026-09-04**
User: *"We definitely need more fey creatures"*, then *"deer based off the Minecraft horse ...
frogs, toads (larger frogs) of kinds and varieties, and of course the various hostile elves."*

Exactly **one** fey creature spawned anywhere: `mythicbotany:alf_pixie`, weight 5, in the three
biomes carrying `PASSIVE`. Now **15 species across all 11 biomes**, each with its own roster so
the fey read as native to the place rather than as ambient decoration. `feywild:mab` and
`feywild:titania` stay out — they are ritual bosses, and world-spawning them would hand the
player an Era-IV fight in Era I.

From the user's roster: **hostile elves** (`richs_races_wood_elves:wood_elf` already extends
`Monster` and targets players — the court's own entity with its AI left on) in the five biomes
where the fall went worst, and **frogs**, whose temperate/warm/cold variants come free from our
own climate work.

The original deer/toad blockers are **superseded by B-77 (2026-09-05)**. EntityJS now supplies
proper custom animal types, antler geometry, separate collision dimensions and model scaling.
Four deer forms and two toads are registered and runtime-tested; no familiar is being repurposed.

---

### B-71 — Liquid Bifrost — **BUILT 2026-09-04**
User: *"Let's call it 'liquid bifrost' pools as a new surface feature for the lakes ..."*

A real flowing fluid with a four-tier chain and conversions into five magic systems. Design
record: `alfheim_reclaimed_design/LIQUID_BIFROST.md`. Owner: `tools/gen_liquid_bifrost.py`.

**Open:** the four tiers and the conversions have **no quests yet**, which the user's own
coverage standard requires.

---

### B-72 — Custom skins for the Magister and the Captain — **BUILT 2026-09-04**
User: *"we need custom textures for the mage and the captain."*

The court are all one entity type separated only by a custom name. Entity Texture Features is
installed and is the obvious tool — and the wrong one, because ETF matches through
OptiFine-style `.properties` read entirely on the **client**, so nothing in headless validation
could prove a rule ever fired. This project has already shipped two silent no-ops that looked
correct on disk.

The mod offers something verifiable instead. It is MCreator-generated: the renderer picks among
six textures from a synched int persisted to NBT as **`DataSkinSwap`**, and `IsSkin1Procedure`
through `IsSkin6Procedure` compare it against 1..6 — confirmed by decoding the `if_icmpne`
operand in each class, not assumed. So slots **5 and 6 are reserved**, their textures overridden
with recoloured art, and `16_wood_elf_skins.js` forces every wild elf back into 1–4. Plain NBT,
server-verifiable.

---

### B-66 — Hub creation depended on a player logging in — **FIXED 2026-09-04**
User: *"server side commands for a server operator to create the world spawn ... our correct
world hub generation should not depend on a player logging in."*

It did, in two places, and the consequence was worse than "no hub on an empty server":
`02_spawn_dimension.js` `spreadplayers`-ed each joining player **up to 2000 blocks**, so players
landed in different places and none of them landed at the Greatbole.

Fixed with **vanilla datapack functions**, not `ServerEvents.commandRegistry` — that hands you a
raw Brigadier dispatcher, and this project has been bitten twice by KubeJS APIs whose shape moved
between builds. `#minecraft:load` runs a function on world load with **no player present**, which
is the whole requirement, in vanilla, with no API risk.

`tools/gen_world_hub.py` emits `create` / `autoload` / `status` / `send` / `reset` under
`/function alfheim:hub/`. The anchor is a `minecraft:marker` summoned at y=250 and dropped onto a
legal surface by `spreadplayers` — so no coordinate is ever computed or parsed back out of a
command, which `runCommandSilent` cannot do anyway.

**Verified live with no client attached:** `[Alfheim] hub: created`, 25 force-loaded chunks in
`mythicbotany:alfheim`.

**Vanilla limit, recorded:** there is no cross-dimension world spawn, so something must still
move a joining player into Alfheim. `hub/send` is that something; it goes to a fixed anchor
instead of scattering, and the anchor exists before anyone connects.

**Deferred:** no client has ever joined, so the delivery half is unproven end to end.

**Also fixed:** `/kubejs export` left the default run sequence — it triggers a reload that fails
with `NoSuchMethodError: JsonObject.isEmpty()` (gson 2.10 present, method added in 2.10.1). Now
`--export`. `Reload failed` 1 → 0, total ERROR 12 → 10.


### B-64 — Headless server harness, and the eight defects it found — **LEVEL 8 PASSED 2026-09-04**
User instruction: *"Use a command based server side world generation."* `tools/run_server.py`.
Forge installer downloaded and the Minecraft EULA accepted on explicit user instruction; the
harness refuses to run without either.

**The pack boots and generates a world.** `Done (19.440s)`, 20 region files, `level.dat`,
`dimensions/mythicbotany/alfheim/region`, 6/6 startup and 22/22 server scripts with **0 errors**,
**0** `Error parsing recipe alfheim:`, 0 quest-line failures, 2 spawn-protection profiles loaded.
12 ERROR lines remain and **none is ours**.

Eight runtime-only defects, each fixed at its generator, each of which passed every static check:
`continuity` (Fabric client mod via Connector) · ETF's client handler in a common mixin ·
BetterGrassify and ForgeSkyboxes failing the dist cleaner · **`.tagItem()` does not exist on an
ItemBuilder** (18 calls, killed all bloom and crystal registration) · **`const HOME_DIMENSION` in
three scripts** (KubeJS shares one scope per directory) · geode `y_spread` outside the codec's
±16 · `concentric_rings` missing its mandatory `salt` · **`quest_giver:grow_tree` is not a
registered task type**, which aborted loading of every quest line and both givers.

**Two earlier "fixes" of mine were proven not to be fixes.** B-43's item tag listed eight blocks
with no item form, so it failed on its own contents — it has to be empty. And the Greatbole had
**no** spawn protection: Continuity Works rejected the profile for lowering its hard 500-block
minimum, while a static check saw a well-formed file.

**Deferred:** level 9 is only partially passed. World creation, Alfheim generation and chunk save
are observed; that the player wakes in Alfheim, that the Greatbole generates, that the court is
seated and that any of it is survivable are not. No client has joined.

### B-65 — Static checks were reading translations, not registrations — **FIXED 2026-09-04**
The most consequential finding of the boot.

Eleven MMO-bridge recipes were rejected at every load with `Unknown item 'mmorpg:*'`. Those ids
came from **lang keys** — `item.mmorpg.currency.orb_of_quality` — and the real registry path is
**`mmorpg:currency/orb_of_quality`**, with slashes. `mmorpg:map` does not exist at all; the map
you carry into a dungeon is `dungeon_realm:dungeon_map`.

Every id check in this project had been reading `item.<ns>.<path>` out of lang files and treating
it as proof of registration. It is proof of a *translation*.

`/kubejs export` now dumps the real registry; **`tools/registry_items.json` holds all 8,257
registered ids** and `check_era.py` prefers it. On being wired in, a checker reporting **0
problems** reported **20** — including ids in quests written and "verified" the same day.

Two new checks close the gaps that admitted them:
- **E12** — every item named by **any** recipe script. E2 only saw era-scoped scripts, so
  `14_mmo_bridge.js`, `12_rites.js` and `30_item_uses.js` were never id-checked at all.
- **S8** — no top-level name declared twice in one KubeJS scope; `node --check` cannot see this
  by construction, because each file parses correctly on its own.

Both proven to fire on injected faults.
**Do:** re-dump `registry_items.json` whenever the mod list changes — it is ground truth and it
goes stale.


### B-63 — Three generators wrote `chapter_groups.snbt` — **FIXED 2026-09-04**
Found by a reproducibility run that happened to execute the generator set in a different order.

`chapter_groups.snbt` declares **both** chapter groups. `gen_quests_bulk.py` was writing it with
`gen_quests.CHAPTER_GROUPS`, which declares only one — so running the bulk generator after
`gen_compendium.py` **silently deleted the Compendium group and all six reference chapters**.

This is the second copy of a defect already fixed once in `gen_quests.py`; the fix there did not
find this one because nothing checked for it. Now guarded: **`check_era.py` E11** asserts that
exactly one generator writes each shared FTB Quests file, ignoring mentions inside comments.
Proven to fire by reinstating the offending line, then restored.

**480 artifacts byte-identical** after re-running all thirteen generators — the drift that
exposed this is gone.


### ~~B-62 — Recipes require methods the player was never given~~ — **CLOSED 2026-09-04, 13 → 0**
Every era now teaches the stations it is the first to use, before it uses them.
`gen_quests_bulk.py` derives them from `gen_ladder.LADDER`, so a station added to an era's
rotation gets a teaching quest automatically and cannot be forgotten.

**The Alfheim Gate needed a recipe change, not just a quest.** Botania crafts the portal from
**livingwood logs + terrasteel nuggets** — livingwood is a gate-import the premise says you cannot
have (§1, and the whole reason Era I was re-pointed onto Dreamwood), terrasteel is the Era X
capstone. So the station for six eras of `elven_trade` recipes could not be built at all, and no
quest could have fixed that. `07_alfheim_gate.js` re-lays it on dreamwood framing
`alfheim:gatewrought_cord`, which is exactly the material B-36 always specified. Removal and
replacement in one change, per §6.1.

**`ars_nouveau:crush` was not a station at all** — it is a *glyph*
(`ars_nouveau.glyph_name.glyph_crush`, "turns stone into gravel"). There is no block to build, so
the unlock is the Scribe's Table and a spell book. It was the one method the checker could not
see; now mapped, and the blind spot is closed.

`check_coverage.py`: **0 ordering violations, 0 unmapped methods.**

<details><summary>Original entry — found 2026-09-04, 13 violations</summary>
User requirement: *"when a recipe requires a method it should verify that you have previously
unlocked that method in some preceding step, so that the recipes are used consecutively in a
proceeding manner rather than requiring crashing methods you have not yet unlocked."*

Implemented as the METHOD ORDERING section of `tools/check_coverage.py`, which maps each recipe
type to the set of station items that prove it is available and asserts the station is taught in
that era or earlier. **13 violations, two families, both real:**

| Method | Eras | Station | |
|---|---|---|---|
| `botania:elven_trade` | 4, 6, 7, 8, 9, 10 | `botania:alfheim_portal` | **never taught** |
| `create:milling`/`mixing`/`pressing`/`sequenced_assembly` | 5, 7, 8, 9, 10 | millstone, basin, press, deployer | **never taught** |

1. **Every elven trade in the pack is unreachable.** Six eras of recipes depend on the Alfheim
   Portal and B-36 is unbuilt, so nothing ever grants it. This is the strongest argument yet for
   B-36's priority: it is not one era's feature, it is a dependency of six.
2. **No Create machine is taught in any quest**, while the ladder uses Create stations from Era V.
   `MAGIC_SYSTEMS.md` §4.5 anticipated this — Create: Wizardry must be taught before B-16's
   pack-wide gating lands, or the gating reads as a tax on machines nobody was handed.

**Do:** grant or gate the Alfheim Portal in Era IV (B-36), and add a Create introduction chain
before Era V. **Accept:** `check_coverage.py` reports 0 ordering violations.
**Caveat:** `ars_nouveau:crush` has no station mapped and is unchecked.

</details>

### ~~B-61 — Instructional depth: 39 processing steps have no quest~~ — **CLOSED 2026-09-04, 39 → 0**
The root cause was in `gen_quests_bulk.py`, not in the authoring: it **banded** the tier ladder —
`band = len(chain)//5`, capped at six leaf quests — so Era X named six of its seventeen steps and
eleven transformations had no quest at all. The banding was replaced with one quest per step,
derived from `gen_ladder.LADDER`, and the 22-quest truncation removed.

Two Rite processes were also uncovered, and one of them mattered a great deal: **`rite:render`,
12 recipes and 0 covered.** That is the payoff of the entire ore chain — quickened bloom into
metal — and since B-47 retired Alfheim's vanilla ore layer, rendering is the *only* source of
coal or iron in the world. The chain was taught right up to the last step and then stopped.

| Era | I | II | III | IV | V | VI | VII | VIII | IX | X |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Was | 1 | 1 | 0 | 0 | 1 | 3 | 5 | 7 | 10 | 11 |
| **Now** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Chapters grew: IV 23, V 25, VI 28, VII 31, VIII 33, IX 31, X 33 — from 22 each.

<details><summary>Original entry — measured 2026-09-04</summary>
User standard: *"every intended processing step for an ore, a contributive item or a componentary
item should have a quest covering the process by which it is created."* Measured by
`tools/check_coverage.py`: **164 contributive steps, 286 alternate uses.**

The standard is ambiguous by a factor of ten, so the tool reports three readings and does not
assume one: **per item 106**, **per process 39**, **hybrid 39 (recommended)** — per item for
ladder steps, per process for the Rites.

The Rites are four *parallel* routes from raw bloom to quickened bloom at improving yields, not a
chain, so steeping a twelfth bloom teaches nothing the first eleven did not; the Compendium's
*Twelve Blooms* chapter already introduces each one.

| Era | I | II | III | IV | V | VI | VII | VIII | IX | X |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Quests to add | 1 | 1 | 0 | 0 | 1 | 3 | 5 | 7 | 10 | 11 |

**36 of the 39 are in Eras VI–X** — the late tier ladder, where every 2n−3 step exists as a recipe
and has no quest. Eras I–III are effectively complete, having just been rebuilt to this standard.

**By mod, the honest gaps are MythicBotany (12) and Occultism (5, with zero coverage of any of its
five steps).** Botania's headline 53 is Rites inflation and collapses under the hybrid reading.

**Depends on:** Eras IV–X are `gen_quests_bulk.py`'s 22-quest chapters, not `gen_quests.py`'s
hand-authored ones. Closing this means expanding those chapters, which is the same work as the
rest of `ERA_EXPANSION.md`'s budget.


</details>

### B-59 — Magic-system quest chains, Eras I–III — **BUILT (static) 2026-09-04**
User instruction: triple the quest count, weighted to the early game, then *"an indexing of all of
our different magic mods, and how they all need their own sets of quest chains through all three
early game eras."* New authority: `alfheim_reclaimed_design/MAGIC_SYSTEMS.md`.

**Indexing first found a worse problem than the count did: ten magic or magic-adjacent systems
had zero quest coverage across all three early eras.** Nature's Aura, Occultism, Feywild, Iron's
Spellbooks, Create: Wizardry, Occult Engineering, Dungeon Realm, The Harvest, Ancient Obelisks and
Knight Quest were installed, working, and never mentioned. **Era II had no Guides at all**, so
`ERA_EXPANSION.md` §4.1's three-energies disambiguation was taught nowhere.

| Era | Was | Now | Budget | Guides |
|:--:|--:|--:|--:|--:|
| I | 29 | **60** | 60 | 20 |
| II | 22 | **70** | 70 | 19 |
| III | 22 | **69** | 68 | 17 |

Every system now has coverage. Chains share one shape — introduce, produce, scale — and one rule
that stops six traditions becoming six spines: a chain ends in a capability, **only a spine gates
an era**, and every chain's first real cost is paid in spine materials (§2.3 applied to teaching).

**Deferred to runtime:** that 199 quests render in a readable layout at these coordinates; that
`shape: "gear"` reads as distinct across 56 Guides; that every task completes.

**Next gap:** MythicBotany at 4 task items — half the Spine of Leaf, carried mostly by Rites
taught through Botania stations rather than named directly.

### B-60 — `check_era.py` did not know about the pack's own registrations — **FIXED 2026-09-04**
Found while authoring B-59: three false E1s and one false E3 on items that plainly exist.

`check_era` built its id universe from mod lang files plus `items_manifest.json` — the 80 tier
ladder intermediates. The **153 `event.create` calls** across `kubejs/startup_scripts/` were
invisible, so blooms, crystals, grove woods and `alfheim:sealed_gate` all read as unregistered the
moment a quest named one. Our own content was the part the checker was least sure about, which is
exactly backwards.

- **`our_registrations()`** reads the `event.create` calls themselves, plus our resource-pack lang
  files — one source, and it cannot drift from what the game registers. Chosen over reading the
  three extra manifests for that reason.
- **`world_sourced()`** teaches E3 that block drops are a way of obtaining things. A raw bloom is
  mined out of stone; no recipe makes one and none should. The alternative was authoring a fake
  recipe to satisfy a checker, which is the failure mode §7 of the profile names outright.

Proven not to have blunted the checks: injected nonsense ids still raise E1 and E3.


### B-58 — The spawn hub: the Greatbole, the Gate, the amphitheatre, the protected court — **PASS 1 BUILT (static) 2026-09-03**
User instruction: a massive oak with an intricate portal built into its flank, a ruined marble
amphitheatre outside it holding the court, and the whole thing an admin-claimed protected hub —
*"the proper central piece of the entire pack"*, returned to all campaign long. Design:
`alfheim_reclaimed_design/SPAWN_HUB.md`. Generator `tools/gen_spawn_hub.py`, checker
`tools/check_spawn_hub.py`.

**Parametric, because the user said it will take many passes.** Every `.nbt` is written from
numbers, so pass 2 is an edit to a constant and a re-run rather than a rebuild. That is the
single most important structural decision in the item.

| Piece | Size | Blocks |
|---|---|--:|
| `greatbole/base` | 48³ | 30,123 — roots, trunk foot, gate chamber, court socket |
| `greatbole/trunk` | 32×48×32 | 13,096 — stackable, `rollable` so segments do not look extruded |
| `greatbole/crown` | 48×40×48 | 12,371 — boughs and a half-gone canopy |
| `court/amphitheatre` | 48×12×48 | 4,487 — ruined tiers, sunken stage, 8 seated NPCs |

Tree ~184 blocks. The gate chamber is a 22-block walk into the trunk to an **8×10 face of
`alfheim:sealed_gate`** framed in livingrock, chiseled quartz, gold and elf glass — the seeing
half of B-36. The NBT format was read off MythicBotany's shipping `house.nbt`, not assumed.

**The court is seated in the structure, not summoned at the player — and that fixed a live
contradiction.** `03_hollow_court.js` placed the eight elves at the player's landing spot, which
`02_spawn_dimension.js` puts up to **2000 blocks** from the origin where the hub generates. It
would have built a *second* court, with the same names, in an empty field — and quest_giver binds
by name, so the player's quest giver would have been whichever they reached first. The roster is
now read from `hollow_court_manifest.json` at generation time, so seat names and quest-link names
cannot drift. The old summon path survives behind `FALLBACK_SUMMON_AT_PLAYER`, default **off**.

**The protection is real but it is not FTB.** `ftbchunks` is **not installed** — the pack has
`ftblibrary`, `ftbquests`, `ftbteams`, `ftbxmodcompat` only. The behaviour asked for does not need
it and is in `kubejs/server_scripts/04_spawn_hub.js`: no hostile spawns, no explosions, no mob
block-breaking, 96-block radius, Alfheim only. Each handler arms inside its own try/catch and the
startup log names which armed, because a protection that silently failed to register is worse than
none — it would be trusted. `PROTECT_FROM_PLAYERS` (default off) locks edits to operators.
**Open decision:** add FTB Chunks for the claim/map/team layer, or accept this.

**Two defects found while building, both by checkers rather than by eye:**
- `minecraft:empty_processor_list` does not exist; the id is `minecraft:empty`. Six pools were
  wrong and `check_worldgen.py` **W5** caught all six. Confirmed against MythicBotany's own pools.
- A generated apostrophe inside a single-quoted string made `04_spawn_hub.js` a syntax error.
  Which produced the more valuable half of the new checker: **S7 runs `node --check` over every
  KubeJS script.** All 27 parse.

**New checker.** S1 the 48-block limit, S2 palette ids, S3 pools exist and their elements resolve,
**S4 every jigsaw `target` is answered by some piece's `name`** — an unanswered target generates
the base alone with no trunk, no crown and no court, silently — S5 structure/placement legality,
S6 seated names match the quest links, S7 script syntax. S4 and S7 both proven to fire on injected
faults, then restored by regenerating from the generator.

**Validation:** `check_spawn_hub` **0** · `check_hollow_court` **0** · `check_era --all` **0** ·
`check_worldgen` **0** · `check_feature_order` **0** · `check_dependency_ranges` **0** ·
**474 artifacts byte-identical** after re-running all twelve generators.

**Not run: any of it.** Pass 2 is a fresh world. Unproven: that the tree assembles whole rather
than as an orphaned base; that `beard_thin` sits the root flare in the ground instead of on a
pillar; that the gate chamber is reachable and not buried; that structure-baked entities spawn
with their NBT intact; and that the three KubeJS protection events exist under those names on
2001.6.5 — the startup log will say.

**The largest open item is arrival.** `02_spawn_dimension.js` still `spreadplayers`-es the player
up to 2000 blocks from the hub. Until that changes the player does not start at the centrepiece.
`SPAWN_HUB.md` §7 holds the decision; it should be settled in pass 2 with the world open.

### B-56 — CurseForge deleted YUNG's API mid-session; the pack will not boot — **CLEARED 2026-09-03**
> **Resolved.** The user removed the YUNG dependency chain deliberately — *"I found them counter
> to purpose."* `betterarcheology-1.2.1-1.20.1.jar` was the one dependent left behind and still
> declared `yungsapi` `mandatory=true`, so the pack still would not boot. Moved to `quarantine/`
> (sha1 `c2cb928bef1c1aa89e90e72b8544b885aceb5d01`), which is reversible per §5. Nothing in
> `kubejs/`, `tools/` or the quest chapters referenced it. `check_dependency_ranges.py` now
> reports **0 blocking issues**.
>
> `minecraftinstance.json` still lists it, so **CurseForge may restore it on the next sync** —
> if the dependency error returns, that is why, and the manifest needs editing with CurseForge
> closed. The original finding is kept below because the concurrency lesson stands.


Found 2026-09-03 by `check_dependency_ranges.py`, which had reported **0** earlier the same
session and then **1**. The pack changed underneath the work.

| Evidence | |
|---|---|
| `minecraftinstance.json` | rewritten **21:30:52**, 468520 → 446348 bytes |
| `mods/` directory | mtime **21:30:52** — same second |
| YUNG's API | **absent from the entire instance** — not in `mods/`, not in `quarantine/`, not in the manifest |
| `betterarcheology-1.2.1-1.20.1.jar` | present since Aug 31, declares `yungsapi` **`mandatory=true`**, range `[1.20-Forge-4.0.2,)` |

Forge hard-fails on an unsatisfied mandatory dependency, so **this is a boot blocker**: level 8
cannot pass until it is resolved. Nothing in this session wrote to `mods/` — the work only read
jars — so the writer was CurseForge itself, running while the instance was being edited.

**Not actioned deliberately.** Installing or removing a jar is a pack composition change:
`INSTRUCTIONS.md` §5 makes `minecraftinstance.json` CurseForge-owned and editable only while
CurseForge is **closed**, and `tools/check_incoming_mod.py` runs before any incoming jar.
**Do:** close CurseForge, then either (a) reinstall YUNG's API at `[1.20-Forge-4.0.2,)` and
re-run the dependency check, or (b) move `betterarcheology` to `quarantine/` if it is not
wanted — it is not referenced by any of our recipes or quests.
**Accept:** `check_dependency_ranges.py` back to **0 blocking issues**.
**Also worth deciding:** whether CurseForge should be closed during authoring sessions as
standing practice. This is the first observed instance of it mutating the pack mid-work, and it
silently introduced a boot blocker into a tree that had passed every check twenty minutes earlier.

### B-57 — The Hollow Court: quest-giving elves at spawn, and the sealed gate — **BUILT (static) 2026-09-03**
User instruction: *"a bevy of entities around our spawn tree, namely the wizard ... giving us our
quests and the captain of the Royal Elven Guard? Along with a fake portal block for the inside of
our portal tree?"* Generator `tools/gen_hollow_court.py`, checker `tools/check_hollow_court.py`.

**No new mod.** `quest_giver` does not require its own villager: `quest_line_links.json` binds a
quest line to any `entity_id` plus a `name`, and `QuestLinkManager.getMatchingLink` compares
`getType()` against `getCustomName()`. A nametagged `richs_races_wood_elves:wood_elf` is a quest
giver. Both mods carry CurseForge project ids (618562, 1342078), so distribution is clean.

**Magister Velrous** — already the pack's narrator, the voice of all twelve Era I Guides — takes
`the_reclaiming`, 6 quests, flavour only. **Captain Orenvel** of the Royal Elven Guard takes
`the_royal_guard`, 5 quests, and it **gates expeditions**. Plus 6 ambient elves with no lines.

**The gate is real, and it required no removal.** `mmorpg:teleporter`, the Map Device that is the
only entry to Mine and Slash's dungeon dimension, has **no recipe anywhere in the pack** — 0
across all 133 mmorpg recipes and every other jar. Expeditions are currently unreachable in
survival. Orenvel's final quest grants one, so the Wound's content becomes something the Guard
dispatches the player to, satisfying §6.1 by adding a route rather than closing one.

**The elves are hostile archers and must be neutralised.** `WoodElfEntity extends Monster
implements RangedAttackMob`, and its `NearestAttackableTargetGoal` list includes `Player`.
`NoAI:1b` removes targeting, wandering and despawn together; `PersistenceRequired`, `Invulnerable`
and `Silent` finish the job. Each gets a livingrock plinth set under its feet first, because NoAI
mobs do not walk down onto terrain.

**`alfheim:sealed_gate`** — a 12-frame animated block, `hardness(-1)`, in no mineable tag. Scenery
only: the seeing half of B-36's *"a multiblock the player can see from Era I and cannot finish
until Era IV"*. Era IV gating stays with B-36.

**New checker, and it exists for one specific silent failure.** quest_giver matches on custom
name, so a one-character drift between the links file and the summon produces an elf that stands
there and gives nothing — no error, no missing id. **H5** asserts the two agree. H1–H7 also cover
line registration, parent resolution, task/reward ids, entity and biome ids, and **H6**: that the
item declared gated is actually granted where it is declared. All proven to fire on injected
faults, then restored.

**Deferred to runtime — and this is the largest deferment in the item.** Nothing here has been
loaded. Specifically unproven: that `NoAI` elves render and persist as intended; that the quest
GUI opens on right-click with a Quest Scroll; that `quest_giver:biome`, `grow_tree` and `gift`
complete; that the animated gate texture renders; and that `server.persistentData` and
`scheduleInTicks` behave as assumed on KubeJS 2001.6.5. **Blocked behind B-56.**

**Known cosmetic defect, upstream:** `quest_giver` ships `quest_scroll` with **no lang entry**, so
the interaction item is nameless in-game. One line in a resource pack fixes it; not done here.

### B-46 — There are no petals in Alfheim — **FOUND AND FIXED (static) 2026-09-03**
**Severity: this blocked the entire Spine of Leaf, and every static check passed.**

No `botania:*` feature generates in any of the eleven Alfheim biomes — verified across our six
biome JSONs and MythicBotany's five from its jar. `mythicbotany:motif_flowers` looks like the
flower source and is not: `MotifFlowerFeature.class` places only `motifDaybloom` and
`motifNightshade`, **neither of which has a loot table**, so both drop nothing.

Mystical flowers are the only source of petals — Botania's 64 petal recipes are all
petal↔petal-block storage conversions. Petals gate the Pure Daisy, every Petal Apothecary recipe,
the Wand of the Forest and the Mana Spreader, all of which Era I's authored quests already require.

The pack was saved only by an undocumented accident: `botania:fertilizer` is `bone_meal +
4× #forge:dyes` (no petals), and four *white* dyes satisfy the four tag slots, so
composter → bone meal → dye → Fertilizer → grass → flowers is technically reachable. Invisible to
a new player and non-obvious to a veteran.

**Fixed with Botania's own mechanism, in four layers:**
1. `kubejs/data/botania/tags/worldgen/biome/mystical_flower_spawnlist.json` adds
   `#mythicbotany:alfheim` to the tag Botania's `add_mystical_flowers` modifier already keys off.
   No new feature of ours enters the sort.
2. **Petals drop from leaves — the Archive Groves, the user's own instruction and the real fix.**
   `ORE_SUPPLEMENTATION.md` §8. Five Alfheim leaf types drop petals of their own colour, and three
   trees of our own cover the remaining six colours. **All 16 colours now have a leaf source**, so
   petals are renewable by an activity the player is already doing rather than by a flower patch
   they can strip bare. The mod loot tables are copied *verbatim from their jars* and appended to,
   with the source SHA-1 recorded — a hand-authored override would have deleted the archwood
   saplings Rite I depends on.
3. Era I Guides will teach the Floral Fertilizer route (`ERA_EXPANSION.md` §4.2).
4. `01_starting_kit.js` grants 2 Floral Fertilizer + 4 white petals; `KIT_FLAG` bumped to `v2`
   so players who already joined receive it.

**Deferred to runtime:** that mystical flowers actually place in Alfheim's biomes, that the leaf
overrides load without a datapack conflict, and that the grove trees generate. Level 9.

### ~~B-49 — The Archive Groves cannot be replanted~~ — **CLOSED 2026-09-03, they can**
The user asked directly whether the grove trees have their own saplings. They did not; now they do.

KubeJS 2001.6.5 ships no `SaplingBlock` builder and no `TreeGrower` binding — that part was
correct. But `BlockBuilder.randomTick(Consumer<RandomTickCallbackJS>)` exists, and
`BlockContainerJS.offset(Direction, int)` is confirmed present in the jar, which is enough to place
a trunk and canopy directly. `growGrove()` in `12_groves.js` does exactly that, using each tree's
own worldgen trunk/foliage numbers so a grown tree matches a generated one. It checks headroom
before writing a single block, so a sapling under a ceiling stays a sapling.

Grove leaves now drop the tree's own sapling at 0.03 — rarer than the foreign vanilla seeds at
0.055, on purpose: the archive is the point of the tree, the tree itself is the bonus.

**Deferred to runtime:** that `randomTick` fires on these blocks, that `offset(...).set(...)` writes
as expected, and that a grown tree looks like a generated one.

### B-55 — Quest ids churn across a regenerate → play → regenerate cycle — **BLOCKS the expansion**
Found 2026-09-03 while starting the Era I expansion, by checking a claim rather than assuming it.

`ERA_EXPANSION.md` §2 asserted that a stable quest key means player progress survives
regeneration. **It does not.** Measured against the chapter the game had normalised:

| Object | On disk | Generator emits | |
|---|---|---|---|
| `era_1` chapter | `5F04313E8BBC9035` | `978E4F51D53B8576` | **differs** |
| `shelter` quest | `29569136F0E03D89` | same | matches |
| `shelter` task | `3C2CC4C0DA24E952` | `9D8955D226D47AC3` | **differs** |
| `spiders` quest | `5E4E351D50C8970C` | `F922CD7718A5E39A` | **differs** |
| `spiders` task | `5877BEC973773EAE` | same | matches |

Divergence runs both ways and is not a key rename — `shelter` keeps its quest id and loses its
task id, `spiders` the reverse. Something in FTB's load/normalise path reassigns a subset.

**Concrete, not theoretical:** `saves/New World/ftbquests/<uuid>.snbt` keys progress by id and its
`started` set holds `5F04313E8BBC9035`, which after regeneration exists nowhere in
`config/ftbquests/`. That progress is orphaned.

**Cost today: nil** — level 11 deferred, quests never played, and the affected save is a two-quest
test world. **Cost after release: a player's entire run.**

**Do:** boot, load a world, and diff `config/ftbquests/quests/chapters/*.snbt` before and after, to
establish exactly which ids FTB rewrites and why. Then either (a) make the generator adopt the
game's ids by reading them back before regenerating, or (b) accept that quests are authored once
and edited in-game thereafter, and say so in `INSTRUCTIONS.md`.
**Accept:** a regenerate → load → regenerate cycle leaves every id in the save's `started` and
`completed` sets still present in `config/ftbquests/`.
**Why it blocks:** authoring 660 quests on a false safety assumption, and finding out after people
have played, is the most expensive version of this mistake. Era I may proceed as a proving ground;
Eras II–X should wait.

### B-53 — The Compendium: in-game documentation — **BUILT (static) 2026-09-03**
User instruction: documentation for every custom feature, inside the quest book, *"other than just
looking at JEI and hoping they can figure it out."* Design:
`alfheim_reclaimed_design/COMPENDIUM.md`. Generator `tools/gen_compendium.py`.

A second FTB Quests chapter group, **57 entries across 6 chapters**: How This Pack Works (4), the
Twelve Blooms (12), the Four Rites (4), Crystallised Mana (13), the Archive Groves (8), the Sixteen
Biomes (16). Every entry is `optional: true` so the Compendium gates nothing.

**Facts generated, prose authored.** Every y-range, tool tier, drop rate, geode rarity, reagent
list and spawn list is read at generation time from the same manifests the implementation comes
from, so the documentation cannot drift. Change a number in `blooms_manifest.json`, re-run, and the
Compendium already says the new one.

**Ownership change:** `chapter_groups.snbt` now belongs to `gen_compendium.py`, which declares both
groups; `gen_quests.py` no longer writes it. Two generators writing one file is how a chapter group
silently disappears on whichever ran last.

**Deferred to runtime:** that `optional: true`, `shape: "gear"` and a second chapter group render
as intended; that 16 entries fit a readable chapter layout.

### B-54 — Elven MineColonies — **PLAN ONLY, not implemented**
`alfheim_reclaimed_design/MINECOLONIES_ELVES.md`. Four tiers, costed against the installed jars.

Two brief assumptions did not survive research: `richs_races_wood_elves` is an **MCreator mob
entity**, not a race or citizen system, and its textures are 64×64 player format against
MineColonies' 128×64 — a visual reference at best, and `license="Not specified"`. **Pointed ears
are model geometry and cannot be done from a datapack or resource pack at all.**

Against that, MineColonies **already ships `citizennames/elf.json`** — 104 male, 110 female, 237
surnames. Tier 0 is a setting, not a feature.

| Tier | Effort | Content |
|---|---|---|
| 0 | minutes | switch colonies to the `elf` name file |
| 1 | a day | elven visitors (recruit cost in our crystals), an elven research branch gated on spine materials, crafter recipes, study items |
| 2 | days | programmatic citizen reskin — capped at skin/hair/clothing |
| 3 | weeks | a Structurize elven building style. **Defer.** |

**Blocked ahead of all of it:** whether MineColonies works in a non-Overworld dimension. It is the
mod `WORLD_STRUCTURE.md` flags as most likely to hardcode `Level.OVERWORLD`. The sweep stays ahead
of this plan — if colonies do not function in Alfheim, every tier is moot.

### B-51 — The Five Deficiencies and the Void Verge — **BUILT (static) 2026-09-03**
User instruction: negative biomes — Starved, Burned, Infested, Decayed — plus a Void where the
world ends in a ragged cliff over floating mana-rich islands. Design:
`alfheim_reclaimed_design/DEFICIENT_BIOMES.md`.

Alfheim goes from 11 biomes to **16**, the layer from 13 bands to 18. Four deficiencies sit in
narrow climate corners (pockets to find); the Void Verge claims the outer fifth of continentalness.
A seventh geode, **the Rim** (Duskglass ∣ Galeglass), generates only in the void at 1 in 3 chunks.

**The void needed terrain surgery, and it is the riskiest file in the datapack.** Density functions
cannot read biomes, so biome and terrain are made to agree by driving both from
`alfheim_continentalness`. The datapack overrides `mythicbotany:alfheim_final` — one file, not the
whole noise settings — wrapping the original in a `range_choice`: outside the void band nothing
changes, inside it terrain is replaced by sparse `cave_cheese` blobs inside a y50–110 window.
Islands are livingrock, the dimension's own default block, so every ore and geode feature targeting
`#mythicbotany:base_stone_alfheim` works on them unchanged.

**New guard — `check_worldgen.py` W7.** The terrain band must be strictly *inside* the biome band
(−0.86 vs −0.80). Reversed, the floor vanishes under a forest — corruption rather than a view, and
invisible until someone walks into it. W7 asserts the ordering and the island window is non-empty;
both verified to fire on synthetic faults.

**Also removed:** 69 lines of dead `SCARCE_ORES`/`ORE_DISTRIBUTION`/`ORE_BIOME_TAGS` tables left in
`gen_alfheim_biomes.py` by the vanilla-ore retirement — data describing a system that no longer
exists is worse than no data.

**Deferred to runtime:** that the density function loads at all; that the cliff reads as ragged
rather than as a clean circle; that islands generate in the intended band; whether aquifers make
floating water; whether surface rules cap the islands with grass.

### B-52 — Void structures, and the void sea
Two things asked for on 2026-09-03 and deliberately not built.

**Void structures** need an NBT pipeline (`SPAWN_ZONE.md`, B-19 territory) and belong in their own
unit of work rather than bolted onto a terrain change.

**A void sea** — a surface at the bottom of the void — needs a mod. **DNS resolves from this
machine**, so the environment does not block it; process does. Installing a jar is a pack
composition change touching `minecraftinstance.json`, the pinned matrix and the dependency graph,
and `tools/check_incoming_mod.py` must run on it first. **Name the mod and it can proceed.**

### B-50 — Crystallised mana: six alignments, six bifurcated geodes — **BUILT (static) 2026-09-03**
User instruction: bifurcated geodes of elementally-aligned mana crystals, far more plentiful than
vanilla amethyst, with a surface feature marking a geode below. Design:
`ORE_SUPPLEMENTATION.md` §9. Manifest `tools/crystals_manifest.json`, generator
`tools/gen_crystals.py`.

| Built | Detail |
|---|---|
| 6 crystals | Emberglass, Tidewake, Rootglass, Galeglass, Duskglass, Dawnglass |
| 18 blocks + 6 shards | block / budding / cluster each; budding grows clusters on random tick |
| 6 geodes | each a **noise-split** pair — spatial halves, not a random mix |
| 12 features, 12 modifiers | deep geode in `local_modifications`, marker in `top_layer_modification` |
| Plenty | mean **1 in 5.6** eligible chunks vs vanilla amethyst's 1 in 24 |
| Marker | `environment_scan` verifies a budding crystal within 32 blocks below, so **zero false positives** |

**Deferred to runtime:** that `noise_threshold_provider` splits a geode into visible halves at
`scale: 0.08` rather than banding oddly; that `environment_scan` + a second `heightmap` returns to
the surface as intended; that markers actually appear; that budding blocks tick and grow.

### B-47 — The Twelve Blooms replace Alfheim's vanilla ore — **BUILT (static) 2026-09-03**
User instruction: *"I don't want to use vanilla ores because that just reskins Alfheim as the
Overworld."* Design: `alfheim_reclaimed_design/ORE_SUPPLEMENTATION.md`.

Twelve custom ore blocks native to Alfheim, placed against `#mythicbotany:base_stone_alfheim`
(the mod's own Alfheim stone tag), each rendered into a standard base ingredient by one of four
Rites — botanical processing with petal, grain, seed and sapling reagents.

| Built | Detail |
|---|---|
| `tools/blooms_manifest.json` | 12 blooms, source of truth |
| `tools/gen_blooms.py` | textures, blocks, items, loot, Rites, worldgen — all reproducible |
| 12 ore blocks + 24 items | raw + quickened intermediate per bloom |
| 4 Rites × 12 | Steeping (Apothecary), Quickening (Mana Pool), Grafting (Runic Altar), Deepening (Infuser) |
| 24 worldgen features, 4 modifiers | disjoint feature sets, so no cycle is possible from our side |
| Retired | 7 vanilla scarce-ore features, 3 modifiers, 2 biome tags, and the global `stone_ore_replaceables` override — preserved with hashes in `quarantine/vanilla_ore_layer_2026-09-03/` |

**Six ingredients moved from unreachable to rooted:** quartz, ghast tear, blaze powder, magma
cream, glass/amethyst and Occultism silver. Three moved off a single mob in under half the world.

**Deferred to runtime:** blooms generate; textures render; Rite recipes are accepted at load;
`mythicbotany:infuser` `fromColor`/`toColor` are emitted (B-41's exact failure) but unproven.

### B-48 — `30_item_uses.js` multipliers still take vanilla raw ore
The 48 cost-bearing multiplier recipes consume `minecraft:raw_iron`, `raw_copper`, `raw_gold` and
`occultism:raw_silver`. With the vanilla ore layer retired those are Midgard-only materials, so
those recipes silently become Era IV+ content. Not a soft-lock and not urgent — but it should be a
decision rather than a side effect. Either accept it (Midgard has real ore; that is the premise)
or teach `gen_item_uses.py` to accept the Quickened blooms as equivalent inputs.

### ~~B-01 — First boot~~ — **COMPLETE 2026-09-02 15:58**
The pack reaches the title screen and holds. 95 mods, **403** valid mod files including
JarJar-nested, 13 GB heap, ~95 s load, **0 crash reports, 0 FATAL lines**, 77 config files written.
KubeJS baseline script logged — FIRST_BOOT_VALIDATION step 9 satisfied.
Five attempts: DNS abort; JourneyMap (B-27); a fault in the test harness; an 8 GB OOM in ModelBakery;
then success at 13 GB with BuildCraft RF quarantined (B-29).
1270 runtime ERROR lines, all cosmetic — see `EXECUTION_STATE.md`.
**Caveat:** launched from a hand-assembled Forge command, not through CurseForge. The mod stack is
validated; the CurseForge launch path is not — it still needs B-26 and B-28.

### B-26 — Install Java 17 — **downgraded from blocker 2026-09-02**
`versions/1.20.1/1.20.1.json` requires `java-runtime-gamma` major **17**; the machine has only
Java 21 (`java-runtime-delta` 21.0.12, `Jre_21` 21.0.4) and a system Java 26.0.1.
**No longer blocking:** the pack demonstrably loads on Java 21. But LWJGL logs
`Unsupported JNI version detected, this may result in a crash`, and 17 is the supported runtime.
**Do:** let CurseForge fetch `java-runtime-gamma` now that DNS works.
**Accept:** the launch uses Java 17 — confirmed, not assumed.

### B-28 — Repair the vanilla asset download
**Found by:** the successful boot. Four `FilePackResources: Failed to open pack` errors against
`Install/assets/objects/...` — files the DNS outage prevented CurseForge from downloading.
**Do:** let CurseForge validate/repair the 1.20.1 assets.
**Accept:** no `NoSuchFileException` on assets in `logs/latest.log`.
**Impact if skipped:** missing sounds and textures. Not load-blocking.

### ~~B-27 — JourneyMap x MineColonies~~ — **RESOLVED 2026-09-03. Option (b) taken.**
`journeymap-1.20.1-5.9.20-forge.jar` installed by the user from CurseForge, 14:26. It is the
oldest 1.20.1 build the listing offers, and it satisfies the range for the reason that matters:

```
modId="journeymap"   version="5.9.20"        <- bare, not "1.20.1-5.9.20"
[[dependencies.journeymap]]  modId="forge"  versionRange="[44.0.0,)"
```

Maven tokenises `5.9.20` from **5**, so it clears MineColonies' `[5.9.8,)`. The 6.x line declares
`1.20.1-6.0.4`, which tokenises from **1** — the prefix was the entire fault, and no 6.x build can
ever satisfy the bound. It also drops the 6.x hard dependency on `commonnetworking`, which is not
in this load path, so a 6.x jar would have failed twice over.

| Check | Result |
|---|---:|
| `check_dependency_ranges.py` | **0 blocking** — 133 mod IDs, 416 declared deps, 0 missing, 0 range violations, 0 quarantine conflicts |
| `check_incoming_mod.py` | 0 fail, 0 warn, 3 pass — unique mod ID, Forge-readable, claims no worldgen |
| `check_feature_order.py` | 0 cycles — it ships no biomes |
| Load path | 85 → **86** jars |

**Headroom, if 5.9.20 misbehaves:** anything up to `5.10.3` (the newest Release in the listing)
also satisfies `[5.9.8,)`. Only the `6.0.0-beta.x` builds are excluded, and by the version string
rather than by the number.
**Still to accept:** a real launch. Static checks pass; the pack has not booted with this jar.
The quarantined `journeymap-forge-1.20.1-6.0.4.jar` stays quarantined — do not restore it.

<details><summary>Original entry, kept for history</summary>

**REGRESSED, THEN CLEARED 2026-09-02. Decision made.**
`journeymap-forge-1.20.1-6.0.4.jar` was restored to `mods/` at 18:09, putting it in **both**
`mods/` and `quarantine/` and re-breaking `ModSorter` — the pack stopped booting between two
recorded sessions and nothing said so. Copies verified byte-identical; the `mods/` copy removed,
quarantine copy preserved. `check_dependency_ranges.py` → **0 blocking issues**, 84 jars.

**Decided by the user: back-date to the minimum viable version.** Outstanding, and not doable
from here — no JourneyMap 5.9.x jar exists on this machine and the sandbox has no network.
**Spec:** a 1.20.1 build whose `mods.toml` declares a bare `5.9.x` version (≥ `5.9.8`), *not*
the MC-prefixed `1.20.1-…` form. The prefix is the entire fault — Maven tokenises `1.20.1-6.0.4`
from **1**, below the bound — so no 6.x build can ever satisfy it. Drop it in `mods/`, re-run
the checker, expect 0.

**Guard added:** the checker now fails on any jar present in both `mods/` and `quarantine/`,
so an undone quarantine decision can no longer pass silently.

**Found by:** first successful mod-loading run, 2026-09-02.
**The defect:** MineColonies declares `journeymap` as an **optional** dependency with range
`[5.9.8,)`. JourneyMap declares its version as `1.20.1-6.0.4`, which Maven parses as major version
**1** — so it is below 5.9.8 and outside the range. Forge halts: an optional dependency may be
*absent*, but if present it must satisfy the range.
**Interim action:** `journeymap-forge-1.20.1-6.0.4.jar` moved to `quarantine/` to unblock testing.
**Decide:** (a) leave it out — it is a convenience map mod, not in the pinned core; or (b) install a
JourneyMap **5.9.x** build, whose version string satisfies the range. MineColonies is core to the
settlement track and cannot be the one to go.
**Accept:** the pack loads with the chosen option, verified by `tools/check_dependency_ranges.py`
and a real launch.
</details>

### B-29 — BuildCraft RF has no BuildCraft — **quarantined 2026-09-02**
**Found by:** the 13 GB run, once a larger heap got past the OOM that was masking it.
**The defect:** `buildcraftrf-3.0.0.jar` ("BuildCraft RF: ReFluxified") is an addon for BuildCraft,
and BuildCraft is not installed. It throws `NoClassDefFoundError: buildcraft/lib/tile/TileBC_Neptune`
from `CapabilityEvents.onCapability` — fired on capability-attach for the first BlockEntity created,
i.e. any chest. Fatal.
**Why no scan caught it:** it declares no mod dependency on buildcraft. The requirement exists only
as a hard class reference. Static metadata analysis cannot see this class of fault — only a run can.
**Action taken:** moved to `quarantine/`.
**Decide:** it stays out. It is one of the 72 undocumented additions, it is a redundant tech mod
under `INSTRUCTIONS.md` §2.3, and installing BuildCraft to satisfy it would add a second industrial
tech tree the design does not want. Confirm and it can be deleted from the manifest.

### ~~B-30 — Feysythia is uncraftable~~ — **ALREADY FIXED; entry was stale. Closed 2026-09-03**
Found while attempting the fix: `21_era1_elven_early_game.js:77` already emits
`alfheim:era1/feysythia_repair`, a `botania:petal_apothecary` recipe with `feywild:fey_gem`
substituted. A second copy was written into a new `05_upstream_repairs.js` and `check_era.py`
**E7** rejected it as a duplicate before it could ship. The script was deleted; the Era I fix
stands. Confirmed against the jars: Feywild 5.5.5 ships only `feywild:fey_gem` and
`feywild:fey_dust`, and the whole lesser/greater/shiny/brilliant ladder MythicBotany references
was removed upstream.

**Still open, deliberately not acted on:** MythicBotany's `feysythia_level_1` … `_4` item tags
point at those same removed gems, so Feysythia's upgrade tiers resolve empty and only level 0
(`fey_dust`) works. Restoring them means choosing which surviving item stands in for four removed
ones — a balance decision, not a repair.

<details><summary>Original entry</summary>
**Found by:** the 91-minute run, during datapack/recipe load.
**The defect:** MythicBotany ships `feysythia_petal_apothecary.json` as a `forge:conditional` recipe
gated on `forge:mod_loaded: feywild`. Feywild **is** loaded, so the recipe activates — and then fails,
because it calls for `feywild:lesser_fey_gem`, which Feywild 5.5.5 does not have. It ships only
`feywild:fey_gem`; the "lesser" variant was removed upstream.

```
[KubeJS Server/WARN]: Error parsing recipe mythicbotany:feysythia_petal_apothecary
  ... {"item":"feywild:lesser_fey_gem"} ... : Unknown item 'feywild:lesser_fey_gem'
```

**Effect:** `mythicbotany:feysythia` — one of MythicBotany's mystical flowers — cannot be made.
Progression-relevant, and it will silently bite whichever era wants that flower.
**Fix:** a few lines of KubeJS re-adding the Petal Apothecary recipe with `feywild:fey_gem`
substituted. Cannot be fixed by editing the jar (doctrine §6.5).
**Why this one first:** it is the smallest possible real recipe change — one recipe, verifiable in
JEI, fixes an actual defect. A good shakedown of the KubeJS path before `20_gate_reversal.js`.

</details>

### B-31 — Intermediate item roster and texture generator
**Depends on:** the era chains being specced (which stations, in what order).
**Do:** ~80 intermediate items are needed for the tier ladder — see `PROCESS_INDEX.md` §10. Build a
generator under `tools/` that reads a manifest (base texture, hue, saturation, overlay, output id)
and emits both the PNG and the KubeJS item registration, so the roster is reproducible from source
rather than hand-maintained.
**Accept:** regenerating from the manifest reproduces the roster byte-identically; items appear in
JEI with correct names and textures.
**Constraint — licensing:** derive from **vanilla** textures. Redistributing derivatives of
third-party mod art is forbidden by `INSTRUCTIONS.md` §5 without compatible licensing, and several
mods here are All Rights Reserved. Vanilla bases cover the shape vocabulary and remove a 95-jar
licence audit from the critical path.
**Size:** largest content item in the project after the spawn-zone NBTs.

### ~~B-32 — Purge Conquest, Twilight Forest and BetterEnd~~ — **EXECUTED 2026-09-02 17:48**
All 10 jars moved to `quarantine/`, verified, relaunched. **ERROR lines fell from 1270 to 17** and
peak memory from 16.3 GB to 8.8 GB. Details below; result in `EXECUTION_STATE.md`.

**The full closure — 10 jars, 353 MB, verified clean:**

| Family | Jars | Size |
|---|---|---:|
| Conquest | `ConquestReforged-forge-1.20.1-1.7.0.jar`, `Hearthfire-1.0.4-1.20.1.jar`, `MedievalArmsCR-1.0.0.jar` | 234 MB |
| Twilight Forest | `twilightforest-...-universal.jar`, `tf_dnv-1.2.3.jar`, `TwilightTreehouses-...jar` | 23 MB |
| BetterEnd | `BetterEnd-20.0.11.jar`, `BCLib-20.0.13.jar`, `WunderLib-20.0.1.jar`, `better-cities-better-end-1.16-1.20.jar` | 97 MB |

**Dependency check: nothing outside the set requires any of them** — no mandatory dependencies, and
no optional ones either. BCLib and WunderLib exist solely for BetterEnd; nothing else touches them.
The cut is clean, which is unusual and worth having verified.

**What it also removes (update `PROCESS_INDEX.md` when executed):** 960 recipes across **14 process
types**, including four Hearthfire stations (woodcutting, woodworking, weaving, smithing — 626
recipes), `conquest_armory:arms_station` (202), `betterend:infusion` (46), and `bclib:alloying` (8).
The alloying furnace was flagged in `PROCESS_INDEX.md` §4 as a natural two-input tier step; that
option goes with it.

**Also resolves:** the 864 malformed Conquest model errors and 384 palette errors disappear — roughly
**98% of the pack's 1270 runtime ERROR lines** are Conquest's. And it removes two worldgen systems,
which simplifies B-12 and B-13.

**Before executing, confirm:** which specific Twilight Forest blocks were wanted for variety, in case
any are genuinely unique. Conquest Reforged, Domum Ornamentum, FramedBlocks and Supplementaries
between them should cover the elven palette, but name the gap before closing it.

**Method:** move to `quarantine/`, re-run `tools/check_dependency_ranges.py`, relaunch, then remove
the entries via the CurseForge UI while CurseForge is closed.

### ~~B-33 — Continuity Works CW-1~~ — **ROOT CAUSE FOUND AND PATCHED 2026-09-03**
**It was one bad string.** `minecraft:ore_diamond_medium` does not exist in 1.20.1 — vanilla ships
`ore_diamond`, `ore_diamond_large` and `ore_diamond_buried`, and all three were already in the list
beside it. A datapack biome naming a non-existent `placed_feature` gets an unbound
`Holder.Reference` that nothing complains about until `FeatureSorter` dereferences it mid-chunk-gen,
which is why it appeared 625 chunks out and was seed-dependent.

Of 5,219 feature references across the 146 biomes, that id was **the only one** that resolved
against nothing. The earlier diagnosis on this page — code-side holder construction via
`AnthologyBiomeCatalog` — was wrong; the mod's Java is not implicated.

**Patched** at the owner's instruction (their mod, `INSTRUCTIONS.md` §5.1) via
`tools/patch_continuity_works.py`: entry deleted, not substituted — substituting would double
diamond generation. `mods/ContinuityWorks-Forge-1.20.1-0.3.0-rc.2+cw1patch.jar` is installed; the
defective original is preserved in `quarantine/`. 307 entries, 0 unintended byte changes.
**Backport pending** — the fix belongs in Continuity Works' source; drop the local patch when an
upstream build carries it.
**Guard added:** `check_incoming_mod.py` now fails any jar whose biomes reference a
`placed_feature` nothing provides. Validated both ways — patched jar 0 fail, original 1 fail.
**Still unverified at runtime.** Level 9 is the acceptance condition.

<details><summary>Original blocker entry, kept for history</summary>

**Found:** 2026-09-02 17:46, first world-generation attempt. Full report in
`alfheim_reclaimed_design/CONTINUITY_WORKS_DEFECTS.md`.
**Symptom:** `IllegalStateException: Trying to access unbound value 'minecraft:ore_diamond_medium'`
in `FeatureSorter` during chunk generation. `minecraft:overworld`, stock `NoiseBasedChunkGenerator`,
625 chunks in — **not** at spawn, so a spawn-only test gives a false pass.
**Cause:** 136 of Continuity Works' 176 biomes reference vanilla ore placed-features. That is not
itself wrong — Regions Unexplored does the same in 71 of its 170 biomes and works. The difference is
registration: CW builds biomes code-side (`AnthologyBiomeCatalog`, `BiomeCaveFeatures`) and appears to
hand unbound feature holders to them.
**Action taken:** `ContinuityWorks-Forge-1.20.1-0.3.0-rc.2.jar` quarantined. **Reversible** — restore
it as soon as CW-1 is fixed. This also removes spawn protection and the custom biomes in the meantime.
**Blocks:** B-12 (Overworld override) cannot be meaningfully tested while worldgen crashes.
**Next:** hand `CONTINUITY_WORKS_DEFECTS.md` to the Continuity Works project. It carries CW-1 plus the
four CW-2 architecture asks so both are fixed in one pass.
</details>

### ~~B-44 — The player never reaches Alfheim~~ — **FIXED AND PROVEN 2026-09-03 16:07**
A fresh world, read back from the save: `Dimension = mythicbotany:alfheim`, `SpawnDimension = mythicbotany:alfheim`, `alfheim_home_spawn_v2` latched, 12 Alfheim region files. `python tools/check_spawn.py` → 0 problems. `execute in <dim> run tp` does cross dimensions on this build and `scheduleInTicks` exists — both previously unproven.
**Level 9 check 9 passes and 9e is anchored.** The original diagnosis and fix follow.

### B-45 — `lockAlfheim` blinds the player for doing the intended thing — **FIXED 2026-09-03 16:11**
The spawn fix worked and the player was blinded the instant they arrived.
`config/mythicbotany.json5` ships `"lockAlfheim": true` — "players that manage to get to alfheim via another mod but have not drunk the mead of kvasir should get a blindness effect". The guard exists to stop progression-skipping; this pack spawns the player there by design, so it fires on the intended path.
The save signature is why it reads as a rendering fault: `minecraft:blindness`, `Duration: 59` reapplied forever, `Ambient: 1`, `ShowParticles: 0`, and nothing in the log.
**Set to `false`;** now doctrine in `INSTRUCTIONS.md` §6 and guarded by `check_spawn.py` S5, which fails on both the config key and a blinded player, and is validated in both directions. A config reset or a MythicBotany update restoring the default cannot silently make the pack unplayable again.
**Residual blindness on an existing character is stale save data** — it stops being reapplied on restart and expires in ~3 seconds.

<details><summary>B-44 original diagnosis, kept for history</summary>

**FOUND 2026-09-03**
The premise of the pack does not work. Read from `saves/New World (1)/playerdata/*.dat`:

```
Dimension        minecraft:overworld
Pos              [-751.1, 95.5, -1878.5]
SpawnDimension   minecraft:overworld
SpawnX/Y/Z       189 / 64 / -1319      SpawnForced 1
KubeJS persist   alfheim_home_spawn_v1 = 1
```

**The mechanism, and the coordinates prove it.** `02_spawn_dimension.js` runs
`execute in mythicbotany:alfheim run spreadplayers 0 0 1 2000 false <name>`. The `in` clause makes
Alfheim the *execution* dimension, so `spreadplayers` samples **Alfheim's** terrain to pick a safe
landing spot — which is why Alfheim generated exactly one region, `r.0.-3` (blocks x 0–511,
z −1536…−1025). It then placed the player at those coordinates **in the dimension they were already
in**. `189, -1319` sits inside that Alfheim region, and the player is standing at it in the
Overworld. The follow-up `spawnpoint @s ~ ~ ~` then wrote `SpawnForced=1` on the **Overworld**,
cementing the failure into the save.

**The script's success line is not evidence.** `console.info('... sent to ...')` is printed
unconditionally after `runCommandSilent` and reports intent, not outcome. It caused a false
`PASSED` in `EXECUTION_STATE.md`, now corrected.

**REWRITTEN 2026-09-03 15:20 — static only, needs a fresh world.** `02_spawn_dimension.js` v2 fixes
all three faults:

| Fault | v1 | v2 |
|---|---|---|
| Wrong command | `execute in <dim> run spreadplayers` — never crosses dimensions | `execute in <dim> run tp <name> 0 320 0` **first**, then `spreadplayers` *within* Alfheim for a safe surface landing |
| Recorded without observing | `console.info` fired unconditionally | `execute in <dim> if entity @e[type=player,name=…]` asks the game where the player is — `@e` is dimension-scoped, so this is a dimension test in pure vanilla commands, with no KubeJS accessor whose shape has moved between builds |
| Latched an unverified flag | flag set on the login event | flag set **only** inside `confirmAndAnchor`, after arrival is confirmed. A failure leaves it clear and retries next login instead of stranding the player permanently |

Verification is scheduled `VERIFY_DELAY` ticks later so the dimension change settles;
`scheduleInTicks` is guarded and falls back to checking immediately. The flag is renamed to
`alfheim_home_spawn_v2` — v1 meant "commands issued", v2 means "arrival observed" — so the fix is
**self-healing**: any character v1 stranded in Midgard is re-sent on next login, no repair commands
needed. `server.getPlayer` was deliberately removed after a first draft used it: it has no
precedent in this pack, and if it returned null the flag would never latch and the player would be
re-spread across Alfheim on every login.

**Accept:** `python tools/check_spawn.py` on a fresh, joined world → 0 problems. It reads the save,
not the log: S1 current dimension, S2 respawn dimension, S3 Alfheim generated chunks, S4 the
verifying flag latched. Validated in the failing direction against `saves/New World (1)`, where it
reports exactly the three faults above.
**Still unproven:** `execute in <dim> run tp` moving a player across dimensions is standard vanilla,
but it has not been observed *in this pack*, and neither has `scheduleInTicks` on this KubeJS build.
Both fail safe — the flag stays clear and the warning is loud — but a fresh world is the only
acceptance.
**Note:** this is B-37's acceptance condition 9/9e, which was recorded as built-and-untested. It was
untested for a reason.

</details>

### B-41 — 11 of our recipes are rejected at load — **REPAIRED (static) 2026-09-03**
All three families repaired in `tools/gen_ladder.py`, at the generator rather than in its output.
Every schema was **read out of the shipping jar**, never guessed: the infuser wants `ingredients`
(not `input`), `fromColor`, `toColor` and `group`; sequenced assembly wants `ingredient`,
`transitionalItem`, `loops`, `results` and `sequence`; milling takes 1 ingredient in 231/231
shipping recipes and pressing 1 in 39/39, with `processingTime` in 231/231 and 0/39 respectively.

The root cause was structural: `STATIONS` gave the infuser the same emitter as Botania's
`mana_pool`, which has no colour fields, and gave all five Create types one generic emitter that
handed every one of them two ingredients and a `processingTime`. Three `alfheim:incomplete_*`
items were added to carry sequenced-assembly progress, marked `transitional` so
`gen_item_uses.py` does not give a half-finished assembler state its own recipes.

`check_era.py` gained **E10**, which profiles each type from its mod's own jar recipes and checks
mandatory keys, unknown keys, and ingredient arity — the latter only from a sample of ≥20, because
2 infuser recipes agreeing is coincidence and 231 milling recipes agreeing is not. 366 recipes are
now schema-checked. Proven to fire: a fixture with one malformed recipe per family produced 9
problems and was removed.

**Still open — this is the half that needs a boot.** The defect was found at runtime and the repair
is static only. Level 4 stays `rejected at runtime` until a booted game shows **0**
`Error parsing recipe alfheim:` lines. The sequenced-assembly recipes and the Fey Altar change are
the likeliest to need a second pass, both having been diagnosed from a jar rather than observed.

<details><summary>Original entry — found at runtime 2026-09-03</summary>
`check_era.py --all` reports 0 problems and the game refuses eleven `alfheim:` recipes at load.
They are simply absent from the running world: no error the player sees, no route to the item.
Three schema families, all in generated output:

| Type | Message | Recipes |
|---|---|---|
| `mythicbotany:infuser` | `Missing fromColor, expected to find a Int` | `era5/elementium_drawn`, `era7/emberbound_quenched`, `era8/rimebound_quenched`, `era9/gravegilt_quenched`, `era10/branch_cord` |
| `create:sequenced_assembly` | `Item cannot be null` — it wants `transitionalItem` and a `sequence`, not `ingredients`/`results` | `era8/rimebound_rebound`, `era9/gravegilt_stilled`, `era10/crown_rebound` |
| `create:milling`, `create:pressing` | more item inputs (2) than supported (1); pressing also given a duration it ignores | `era5/annealed_plate`, `era8/frost_shard` |

**Do:** repair the generators that emit these, not the output. Then extend `check_era.py` with a
per-type **schema** check — required fields, input arity, field types — because the current
invariants only prove ids exist and are reachable, which is why 376 recipes passed with eleven
broken. Cross-check each type against the shipping mod's own recipes in its jar rather than
guessing the schema.
**Accept:** the pack loads with **0** `Error parsing recipe alfheim:` lines, and `check_era.py`
fails on a deliberately malformed recipe of each of the three types.
**Why it matters:** this is the exact failure INSTRUCTIONS §6.3 names — a script that parses is not
a script that works. It is also the first real proof that level 4's static pass was not enough.

</details>

### B-42 — Fey Altar — **THE PREMISE WAS BACKWARDS. Corrected (static) 2026-09-03**
This entry had it the wrong way round, and the jar settles it. **All 29 `feywild:fey_altar`
recipes in feywild-1.20.1-5.5.5.jar use exactly 5 ingredients. None uses 4.** Our generator was
emitting **4**, not 5 — so `Index 4 out of bounds for length 4` in `FeyAltarRecipeCategory` is
the category reaching for a fifth slot that our short array does not have. We were an ingredient
**short**, not one over.

The fix below — "if the altar caps at four, drop to four ingredients" — would have preserved the
crash. `gen_ladder.py` now pads to five, matching every shipping recipe. Found by E10's arity
check, which is exactly the class of question it was built to answer.

**Deferred to runtime:** that the altar accepts our five-ingredient recipes and that JEI renders
them without throwing.

<details><summary>Original entry — the inverted reading</summary>
`alfheim:era6/march_hide` and `alfheim:era10/crown_drawn` throw
`ArrayIndexOutOfBoundsException: Index 4 out of bounds for length 4` in
`com.saphienyako.feywild.compat.FeyAltarRecipeCategory.setRecipe`. JEI catches it, so it is a
display failure today.
**Unknown and worth establishing first:** whether the altar block itself accepts a fifth
ingredient, or whether these two recipes are also uncraftable. Test in the open world before
deciding.
**Do:** if the altar caps at four, drop to four ingredients in `26_era6_tier_ladder.js` and
`210_era10_tier_ladder.js`; if it accepts five, the JEI category is a Feywild defect and the
recipes stay, with the display failure recorded and accepted.

</details>

### ~~B-43 — `jaffabricate` breaks the `minecraft:leaves` item tag~~ — **FIXED (static) 2026-09-03**
`kubejs/data/jaffabricate/tags/items/orange_leaves.json` supplies the missing item tag, mirroring
the eight values of the mod's own block tag verbatim. Verified in the jar: it ships
`data/minecraft/tags/items/leaves.json` pointing at `#jaffabricate:orange_leaves` and
`data/jaffabricate/tags/blocks/orange_leaves.json`, but **no** item version. The jar is
untouched — a datapack addition, not a patch.
**Deferred to runtime:** that the four `Couldn't load tag` ERROR lines are gone and
`minecraft:leaves` resolves as an item tag.

<details><summary>Original entry</summary>
The jar ships `data/minecraft/tags/items/leaves.json` pointing at `#jaffabricate:orange_leaves`
but ships **only the block** version of that tag — no `data/jaffabricate/tags/items/orange_leaves.json`.
The item tag `minecraft:leaves` therefore fails to load, and takes
`minecraft:completes_find_tree_tutorial`, `minecolonies:fletcher_ingredient` and
`minecolonies:compostables` with it. Four ERROR lines at every load.
**Do:** add `kubejs/data/jaffabricate/tags/items/orange_leaves.json` mirroring the block tag's
eight values. Third-party jar stays untouched — this is a datapack addition, not a patch.
**Accept:** those four `Couldn't load tag` lines are gone, and `minecraft:leaves` resolves as an
item tag.

</details>

### ~~B-40 — Feature order cycles from biome modifiers~~ — **FIXED 2026-09-03**
Attempts three and four crashed the same way as attempt two, now between
`continuityworks_biomes:ash_wastes` and `continuityworks_biomes:quarry_megaplex` — **two biomes
whose `features` arrays are byte-identical.** B-38's fix was correct and incomplete: a biome's
JSON is not its final feature list, because `forge:add_features` biome modifiers append to a step
at runtime.

Continuity Works ships two modifiers adding the same feature (`land/topology`) to different biome
sets, under names that sort on opposite sides of a third (`biome_cave_networks`). Forge applies
modifiers in order of **file path across every mod** — `RegistryDataLoader` reads a `TreeMap` over
`ResourceLocation`, whose `compareTo` compares path first, namespace second — so 128 anthology
biomes get one order and 8 template biomes the reverse. Recorded as **CW-4**, fixed by renaming
both to a shared `land_topology_` prefix. No content changed, only the zip entry names.

**The checker was fixed first, and that is the durable part.**
`tools/check_feature_order.py` had reported 0 cycles on the jar that then crashed twice: it read
biome JSON and nothing else, so 57 feature-affecting modifiers and 2,667 biome-step changes were
invisible to it. It now applies `forge:add_features`, `forge:remove_features` and
`farmersdelight:add_features_by_filter` in the game's own order, parses commented JSON, and reads
all 194 modifiers in the load path with none skipped.
**Validated against the real defect:** it reproduces this exact crash from the unpatched jar and
reports 0 against the patched one.
**Still unverified at runtime.** Level 9 is the acceptance condition.

### ~~B-38 — Feature order cycles crash world creation~~ — **FIXED 2026-09-03, but incomplete — see B-40**
The second world-generation attempt crashed with `IllegalStateException: Feature order cycle
found`, naming `continuityworks_biomes:terraced_vineyard` and `ars_nouveau:archwood_forest`.
`FeatureSorter` flattens every loaded biome into one global order per generation step; two biomes
that name the same pair in opposite orders make that order impossible. It throws lazily, from
`ChunkGenerator`, so it lands on world creation with every static check already green.

**Five cycles, in two authorities.** Four were Continuity Works contradicting vanilla in 67 of its
146 biomes — recorded as **CW-3**, patched locally, backport pending (see below). The fifth was
**ours**: `alfheim:bloomfall_vale` put `motif_flowers` before `loose_dreamwood_trees`, while
`mythicbotany:alfheim_plains` has the reverse. That one would have crashed **Alfheim itself** — the
dimension the player wakes in — and nothing had found it because the first crash happened in the
Overworld first.

**Fixed at the generator, not the output.** `tools/gen_alfheim_biomes.py` now carries a
`FEATURE_ORDER` table read off MythicBotany's five jar-owned biomes and sorts every step through
it, refusing any feature with no declared rank. Regenerating changed exactly two lines in one file.
**Guard added:** `tools/check_feature_order.py` simulates `FeatureSorter` over the vanilla client
jar, all 85 mod jars and our datapack. Validated both ways — `--self-test` fires on a synthetic
cycle; the real run went 5 → 0.
**Still unverified at runtime.** Level 9 is the acceptance condition.

### B-39 — Backport CW-1, CW-3 and CW-4 to Continuity Works
`tools/patch_continuity_works.py` now fixes three defects in a jar the pack does not own the source
of. All three belong upstream: CW-1 (`minecraft:ore_diamond_medium`, one bad string), CW-3 (67
biome feature lists contradicting vanilla's order) and CW-4 (two biome modifiers adding one feature
under names that sort inconsistently). Report is
`alfheim_reclaimed_design/CONTINUITY_WORKS_DEFECTS.md`.
**CW-4 is worth fixing properly upstream rather than by rename:** the durable rule is *one feature,
one insertion point*. A union biome tag covering `#anthology` and `#templates` with a single
modifier removes the whole class; a list of tags is not a valid `HolderSet`, which is why the local
patch renames instead.
**Do:** hand the report to the Continuity Works project; when a build carries both fixes, drop the
local patch and install the upstream jar.
**Accept:** `python tools/check_incoming_mod.py <new jar>` clean, then
`python tools/check_feature_order.py` → 0 cycles with the unpatched jar in `mods/`.
**Note:** a local patch and its source must never silently diverge — this is the item that closes
that gap. Blocked only on an upstream build; this sandbox has no network.

### B-34 — Re-tune the memory allocation
The instance is set to 14 GB. That was justified when Conquest Reforged was loaded — an 8 GB heap
OOMed in `ModelBakery`. **After the purge, peak resident is 8.8 GB, down from 16.3 GB.**
**Do:** retest at 8 GB. If it holds, drop the instance setting and reclaim 6 GB.
**Accept:** a full load and a generated world at the chosen heap with no OOM.

### B-02 — Capture the FTB Quests schema — **NOW ELIGIBLE**
**Depends on:** B-01 — complete.
**Do:** author one throwaway quest chapter in-game, then read what FTB Quests writes to
`config/ftbquests/`. Record the exact SNBT shape as a design record.
**Accept:** a documented schema that a generator can target, verified by round-tripping one
hand-edited quest back into the game.
**Why first:** 215 quests cannot be authored by hand. Everything downstream needs a generator, and a
generator needs a verified schema. This is the highest-leverage item in the backlog.

### B-03 — Reconcile pack metadata
**Depends on:** nothing.
**Do:** extend `alfheim_reclaimed_design/PINNED_MOD_MATRIX.md` to all 97 installed mods; keep
`BUILD_METADATA.json` counts in step.
**Accept:** matrix rows equal jars on disk; metadata counts match.

---

## Blocked on a decision

### ~~B-04 — Resolve Ars Nouveau vs. Ars Magica~~ — **RESOLVED 2026-09-02**
Ars Nouveau confirmed by the user. The Spine of Song is Ars Nouveau; ~100 quests unblocked.
See `INSTRUCTIONS.md` §2.1.

### B-05 — Regions Unexplored: remove or accept as dead weight — **REOPENED 2026-09-03**
**The user's decision, 2026-09-03: Midgard is Continuity Works only.** `tools/set_midgard_biomes.py
--mode cw-only` sets `vanilla_overworld_region_weight`, `primary_region_weight`,
`secondary_region_weight` and `rare_region_weight` to **0**, and CW's `regionWeight` to **20**.
Continuity Works now holds 100% of the configurable Overworld weight, up from 9%.

That leaves Regions Unexplored installed and generating **nothing** — 170 biomes, ~30 MB of jar,
loaded every launch for no world content. Its items, blocks and recipes still exist, so removing it
is not free: anything gating on RU content breaks.

**Decide:** (a) leave it installed and inert — its blocks stay craftable/obtainable through other
routes; or (b) remove it, and sweep `kubejs/` for any recipe or quest that references
`regions_unexplored:` first.
**Do first:** `grep -r "regions_unexplored" kubejs/` to price option (b) before choosing.
**Note:** `ars_nouveau:overworld` cannot be zeroed — `ArchwoodRegion` registers in code with no
config key. Midgard therefore means *Continuity Works plus Ars Nouveau archwood*. Removing Ars is
not an option; it is the Spine of Song.

<details><summary>Previous disposition, superseded</summary>

**CLOSED 2026-09-02. It stays.**
Closed by the architecture change rather than by a decision. Alfheim vacated the Overworld slot, so
the Overworld is vanilla multi-noise again, TerraBlender injects into it as designed, and Regions
Unexplored 0.5.6 generates normally. Its 170 lush Earth biomes were said to suit "neither an elven
world nor a dead industrial one" — but the Overworld is now **Midgard**, and a dead *Earth* is
exactly what they are. It populates Midgard until Continuity Works' anthology can join it.
</details>

### ~~B-23 — Which Continuity Works anthologies belong in this pack~~ — **DISSOLVED 2026-09-02**
The two-world split answers it. The anthologies are not competing with Alfheim for the Overworld —
they populate **Midgard**, the dead industrial world. A neon-virtual biome there is correct, not
off-premise. See `WORLD_STRUCTURE.md` §4.

### ~~B-25 — Alfheim ore and cave viability~~ — **RESOLVED BY IMPLEMENTATION 2026-09-02**
The guard rail failed, so the trickle was taken. `tools/check_worldgen.py` proved that copper,
iron, coal, redstone, lapis and diamond generated in **none** of Alfheim's 11 biomes, while Era I
quests ask for a Mana Spreader (copper), an iron ingot and a Manasteel ingot (infused iron) — the
campaign could not be finished.

Scarce ores now generate everywhere via a Forge `add_features` biome modifier on
`#mythicbotany:alfheim` (copper ×4, iron ×3, coal ×6, roughly a quarter of vanilla counts in
smaller veins), with richer seams on `#alfheim:highland_veins` and `#alfheim:arcane_strata` so the
map is worth exploring. Caves were already present via `mythicbotany:cave`/`canyon` carvers.
**Static only** — level 9 still needs a fresh world. See `EXECUTION_STATE.md`.

---

## Sequenced after first boot

### B-06 — Elven early game (`21_elven_early_game.js`)
**Depends on:** B-01.
Pure Daisy → Dreamwood; Dreamwood twig/spreader/apothecary chain. See `GATE_REVERSAL.md` §2.
**Accept:** level 11 — a player reaches the first Mana Pool using only elven-side materials.
**Must precede B-07.** Reversing the gate before this exists produces a pack that passes every static
check and is unplayable.

### B-07 — Gate reversal (`20_gate_reversal.js`)
**Depends on:** B-06 at level 11.
Remove the 9 elven trade conversions, add the 9 inversions. See `GATE_REVERSAL.md` §1.2.
**Accept:** all 18 recipes correct in JEI; a test trade returns Livingwood for Dreamwood.

### B-08 — Native elven goods (`22_native_elven_goods.js`)
**Depends on:** B-07.
Native routes for Elven Quartz, Elf Glass, Pixie Dust, Dragonstone. See `GATE_REVERSAL.md` §2.2.D.

### B-09 — Era I quest chapter
**Depends on:** B-02, B-06.
17 quests. The prologue teaches the reversal. See `CAMPAIGN_ERAS.md` §3.
**Accept:** level 11 — completed start to finish in a fresh world.

### B-10 — Spine interlock recipes
**Depends on:** B-09.
The four hard dependencies in `TWIN_SPINES.md` §2. Verify era ordering in-game before committing —
§5 names a near-circular dependency that no static check will catch.

### B-11 — Eras II–X
**Depends on:** B-09 complete and admitted.
One era at a time, each reaching level 11 before the next is authored.

---

## Worldgen — Alfheim as the Overworld

### ~~B-12 — Prove the Overworld override~~ — **RETIRED 2026-09-02. The assumption was dropped.**
Closed by ceasing to make the assumption rather than by proving it. The override duplicated
`data/mythicbotany/dimension/alfheim.json`, which already carries the identical generator block, and
it occupied the slot every TerraBlender mod injects into — the single cause of both the Continuity
Works mismatch and B-05.

`kubejs/data/minecraft/worldgen/world_preset/normal.json` is **deleted** (archived to the session
scratchpad). Alfheim is now `mythicbotany:alfheim`, the mod's own tested dimension, and the player is
placed there by `kubejs/server_scripts/02_spawn_dimension.js`.
**Guard:** `check_worldgen.py` W6 fails if the override reappears, and asserts that the home
dimension's `biome_source` really reads the layer the tool validates.

### B-37 — Spawn and respawn into Alfheim — **BUILT (static) 2026-09-02**
Vanilla has no spawn dimension: every player joins and respawns in the Overworld, and no datapack
changes that. No dimension-management mod is installed, so this is script.
**Built:** `02_spawn_dimension.js` — `spreadplayers` for a safe first-join landing in Alfheim, then
`spawnpoint` at that spot, which is what carries respawn (`/spawnpoint` writes the respawn
*dimension*, so dying bedless returns the player to Alfheim, not Midgard). A guarded `respawned`
handler is a safety net only, and no-ops if it cannot read the dimension.
**Accept:** level 9e — fresh world, player wakes in Alfheim; dies without a bed and wakes in Alfheim.
**Untested.** Commands were chosen over the KubeJS teleport API because `execute in <dim> run` has
been stable across KubeJS builds and the teleport signatures have not.

### B-13 — Convention tags and structure placement in Alfheim
**Depends on:** B-12.
**Do:** MythicBotany's biomes carry **no** `minecraft:` or `forge:` convention tags — confirmed by
scan. Add them, then extend the placement tags of whatever structures should appear in Alfheim.
**Accept:** level 10 — the intended structures observed generating in Alfheim.
**Narrowed by the two-world split:** anything that belongs to the dead industrial world moves to
Midgard instead of being re-tagged into Alfheim. Decide per structure family which world it belongs
to — that decision removes most of the work.

### ~~B-14 — Alfheim Unbroken~~ — **DISSOLVED 2026-09-02**
It proposed keeping `mythicbotany:alfheim` as a separate late-game fragment alongside an Overworld
Alfheim. There is now only one Alfheim, it *is* `mythicbotany:alfheim`, and the player lives in it
from the first minute. Nothing left to build.

### B-35 — Midgard — **MOSTLY BUILT BY DOING NOTHING 2026-09-02**
**Midgard is `minecraft:overworld`.** No dimension is registered and no generator is authored: the
Overworld is left exactly as vanilla ships it, and **Regions Unexplored** populates it through
TerraBlender. The dead industrial world already generates.
**Continuity Works is installed** as of 2026-09-03: CW-1 was patched locally (B-33), the jar passes
acceptance 0 fail / 0 warn / 6 pass, and its TerraBlender Overworld injection is correct as shipped.
Midgard therefore carries **Regions Unexplored + the 146-biome anthology**, with no integration work
beyond the patch.
**Accept:** level 9c — the Overworld generates and carries RU's biomes; level 10 — CW's anthology
joins them without a crash.
**Boundary:** Continuity Works is a separate repository consumed as a built jar. Defects go upward
as reports, never patched here.
**Note:** the four CW change-asks are withdrawn — see `CONTINUITY_WORKS_DEFECTS.md`. Only CW-1
remains.

### B-36 — The Alfheim Gate: a custom portal, completable in Era IV
> **Retargeted from Era VI to Era IV, 2026-09-03, by the user:** *"Record the earlier gate as when
> the gate opens."* The 2026-09-02 "completable only in Era VI" instruction is withdrawn. Full
> record: `CAMPAIGN_ERAS.md` §3, Era IV.

**Depends on:** B-35, and Era IV's chain existing.
**Do:** the gate is a **trade route, not a reward** (`INSTRUCTIONS.md` §1) and it runs outward to
Midgard. Build it as a multiblock the player can *see* from Era I and cannot *finish* until Era IV,
so it reads as a goal for the opening third of the campaign.
**Gating material:** the final component must come from the Era IV tier chain —
**`alfheim:gatewrought_cord`**, the era's capstone, whose tooltip has read *"Era IV. Elven work,
finished on the far side of the gate"* since the roster was authored. The name was pointing here
all along.
**Accept:** level 11 — the portal cannot be completed before Era IV, does complete in Era IV, and
lands the player in Midgard.

**Simplified by the architecture change 2026-09-02 — the traversal already exists.** Midgard is
`minecraft:overworld`, and two vanilla-path portals already connect the two worlds:

| Block | Direction | Note |
|---|---|---|
| `botania:alfheim_portal` | Overworld → Alfheim | Botania's own, built in the Overworld |
| `mythicbotany:return_portal` | Alfheim → Overworld | "Alfheim Return Portal", MythicBotany's |

So the work is **not building a portal** — it is *gating* one. The remaining job is to make the
outward route unreachable before Era IV and require the era's capstone material
(`alfheim:gatewrought_cord`) to open it, then set the `alfheim_midgard_unlocked` flag that
`02_spawn_dimension.js` already reads so respawn stops forcing the player home.
**Open:** whether to gate `mythicbotany:return_portal`'s recipe/activation, or to require a new
keystone block alongside it. Investigate how the return portal is obtained before choosing.

### ~~B-15 — Custom mod integration~~ — **DONE (static) 2026-09-02**
Continuity Works 0.3.0-rc.2 installed. Acceptance check **0 fail, 1 warn, 5 pass**; full pack
re-scan 97 jars / 146 mod IDs / 0 missing dependencies. Mod IDs unique, Forge 1.20.1 correct,
Overworld generator not claimed, 176 biomes with 11 convention tag files.
**Static only.** Level 9 acceptance still requires a fresh world — carried by B-12.
The single warning (does not reference `#mythicbotany:alfheim`) is now B-12's scope, not a defect.

### ~~B-24 — Spawn protection tag configuration~~ — **DONE (static) 2026-09-03**
Two files, both `replace: false` so they extend Continuity Works rather than displace it:
`kubejs/data/continuityworks_spawn_protection/tags/worldgen/structure/protected.json` adds
`alfheim:greatbole`, and `kubejs/data/alfheim/continuityworks_spawn_protection/profiles/greatbole.json`
gives it a 500-block exclusion radius with `protect_jigsaw_pieces: true`. Format copied from the
mod's own `abyssal_vents` profile, not guessed.

Per-piece protection is **required** here, not optional: the tree is four pieces stacked
vertically with the amphitheatre alongside, so without it something can generate between trunk
segments. That is the exact opposite of the Hollow Court **city**, whose 40–80 pieces must be
allowed to crowd and therefore belong in `ignored` — never in `protected`. SPAWN_ZONE.md §7.1.
**Deferred to runtime:** that nothing generates within 500 blocks of the hub, and that the four
Greatbole pieces are not excluded from each other.

<details><summary>Original entry</summary>
**Depends on:** B-18, B-20.
**Do:** add the Greatbole to `#continuityworks_spawn_protection:protected` (500-block exclusion keeps
the arrival zone clean) and the Hollow Court pieces to `ignored` (they must be allowed to crowd).
Keep Hollow Court pieces out of `jigsaw_piece_protected`.
**Accept:** level 10 — the city generates dense, and nothing foreign spawns within 500 blocks of the
Greatbole.
**Note:** all three tags are `replace: false`, so this is pure datapack work. See `SPAWN_ZONE.md` §7.1.

---

## Spawn zone — the Hollow Court

Design record: `alfheim_reclaimed_design/SPAWN_ZONE.md`.

</details>

### B-17 — Calibrate the spawn ring before authoring
**Depends on:** B-01. **Not** blocked by B-12.
**Do:** build three throwaway pieces, wire them into a `concentric_rings` structure set, generate a
world, and **measure the actual radius**. Tune `distance`, `spread` and `count` against the real
1000-block target.
**Accept:** measured extent within tolerance of 1000 blocks, recorded with the parameter values used.
**Why first:** `concentric_rings` distances are in chunks and the relationship to a felt radius is not
obvious. Getting this wrong after authoring 80 pieces is expensive; getting it wrong after three is
free.

### B-18 — The Greatbole
**Depends on:** B-17.
**Do:** the arrival tree as a vertical jigsaw assembly — base with portal chamber, stackable trunk
segments, boughs, canopy platforms, dead crown. Each piece ≤ 48³.
**Accept:** level 9 — generates at spawn, player arrives inside it, no floating or buried geometry.

### ~~B-19 — Decay processor list~~ — **BUILT (static) 2026-09-02**
`alfheim:elven_ruin` — `block_rot` at integrity 0.88 plus a rule processor: elf glass shatters,
livingrock goes mossy then cracked, dreamwood floors fall in, cobwebs fill interior air. Emitted by
`tools/gen_elven_ruins.py` and applied to every MythicBotany elven-house pool element by datapack
override, so no third-party NBT is modified.

It also delivers the **villages**: `house` and `tower` each carry a jigsaw named
`mythicbotany:entrance` whose connector targets the `gardens` pool, so adding the buildings to that
pool makes buildings chain into clusters instead of lone cottages, bounded by the structure's
`size: 5`. Era X's restoration is now a processor swap, as intended.
**Accept:** level 9/10 — observed generating ruined and clustered in a fresh world. **Not yet run.**

### B-20 — Hollow Court piece authoring
**Depends on:** B-17, B-19.
**Do:** 40–80 NBT pieces across the pools in `SPAWN_ZONE.md` §5. Extend MythicBotany's existing
`elven_houses` pools rather than replacing them.
**Accept:** level 5 per piece, level 10 for the assembled city.
**Size:** the single largest labour item in the project — larger than the 215 quests. Needs a plan and
probably a dedicated builder.

### B-21 — Drained Grove biome
**Depends on:** B-12.
**Do:** the biome itself — dead trees, cobwebs, dead bushes, debris; spider-weighted spawners;
mystical flowers and mana crystals deliberately **omitted**. Raise `abandoned_apothecaries` rarity.
**Accept:** level 9 — the biome generates at spawn and reads as drained.

### B-22 — Nature's Aura depletion at spawn
**Depends on:** B-21. **Investigation first.**
**Do:** determine whether initial per-chunk aura is datapack-reachable or needs KubeJS, then set the
spawn region near zero so the drain is a mechanic the player reverses.
**Accept:** aura reads as depleted in-game and can be restored.
**Note:** do **not** extend this to suppressing Botania mana generation — that risks soft-locking
Era I. See `SPAWN_ZONE.md` §7.

### B-16 — Pack-wide recipe gating
**Depends on:** B-07, B-09.
**Do:** re-gate every progression-relevant recipe in every support mod so its unlock or its materials
come from a spine. `INSTRUCTIONS.md` §2.3. Starts with the Create family — twelve mods.
**Accept:** level 11 per mod family. No support mod yields progression power without spine input.
**Size:** the largest body of implementation work in the project. Break into one mod family per unit.

---

## Deferred

- **Performance mods.** B-01 gave the baseline: ~95 s to title screen, 13 GB heap. 95 mods including a 227 MB Conquest
  Reforged, currently with no rendering optimiser.
- **Worldgen validation.** Seven mods write to generation; needs a fresh world. Audit finding F-09.
- **Sinytra Connector removal.** Connector and Forgified Fabric API serve only BetterGrassify and
  Continuity. Drop all four if either misbehaves. Audit finding F-10.
- **Manifest cleanup.** The two quarantined jars still have entries in `minecraftinstance.json`.
  Remove them through the CurseForge UI, or edit the file only while CurseForge is closed.
- **Git.** Per user direction this is a file-based project; the repository is not in use. `.git/HEAD`
  is malformed if that ever changes.
