# Terrain Authorities — one density, many owners

**Role:** authoritative design record for Alfheim's terrain architecture.
**Status:** `stage 1 built and wired 2026-09-12` — `alfheim_final` is the selector and the
expressions live in the authority leaves. **No terrain has moved:** both leaves carry the same
expression, A5 asserts they stay byte-identical, and a generated world matches the pre-wiring
run column for column. Stage 2 onward is unstarted.
**Authority:** subordinate to `INSTRUCTIONS.md` and `WORLD_STRUCTURE.md`. Supersedes the terrain
half of `DEFICIENT_BIOMES.md` §2.2 when built; that record keeps the dry-rim contract.
**Owner direction, 2026-09-11:** *"creating an alternative mapping function like continentalness,
for all of these different highly terrain modifying biomes to apply their own definitive and
distinct terrain altering features … that bleed over point where stop, this area is this biome,
this terrain generation takes predominant control of this area."*

---

## 1. Why

Three separate rejections in one session turned out to be one root cause.

| symptom | measured | what it actually is |
|---|---|---|
| Void Shore "far too prolific", a plateau for a tiny void | 357,680 columns, every dip below −0.58 becomes land | the aquifer collar is a *value* band, so it appears wherever the field dips, not where void is |
| water standing in the void | 2.5% of void columns, **100% within 60 blocks of an ocean**, dry ones median 84 | the collar has to be a *width*; keyed to a value it pinches wherever the field is steep |
| sheer faces that no carve could roughen | rugged 0.46 → 0.53 at the limit of tuning; a carve reaches ~5 blocks on a flat top and **0.6 of a block** on a vertical face | one global density shaped by mask ramps cannot give a region its own vocabulary |

All three are consequences of expressing every landform as a branch of one density function keyed
to `mythicbotany:alfheim_continentalness` — a field whose gain is not ours. It is
`1.7 × badlands_surface` at `xz_scale 0.045`, then clamped, which makes it steep exactly where the
margin lives: the Void Verge biome measured **sixteen columns wide** at z=223 while its shelf was
sixty blocks thick. Widening any band costs ocean at 1:1, because ocean and void share the axis.

## 2. What is proven, and therefore what may be built on

These are measurements from 2026-09-11/12, not assumptions. Each is cheap to re-run.

**2.1 The biome layer is a disjoint, covering partition of axis-aligned boxes.**
44 entries, **0 overlapping pairs, 0.000% of climate space uncovered** (200,000 samples).
`gen_alfheim_biomes.partition()` produces it and `assert_disjoint()` already guards it.

This is the load-bearing fact. Multi-noise selection is nearest-neighbour in climate space; with
overlapping or gappy claims, "which biome" is a distance computation no density function can
reproduce. **With a disjoint covering partition every point lies in exactly one box at distance
zero, so membership reduces to axis-aligned threshold tests — which `minecraft:range_choice` on
the same climate functions reproduces exactly.**

That is precisely what B-82 failed at. It thresholded climate independently of the biome source,
the two disagreed at the edges, and Hills terrain was stamped into Plains and Silverbark. The
difference here is not better thresholds; it is that **the partition IS the selection**.

**2.2 There is exactly one `final_density`.** Authorities are branches of it, not separate
functions the game chooses between. Nothing in a datapack can give a biome its own generator.

**2.3 Biomes are sampled at quart resolution; density is evaluated per block.** So an authority
boundary carries roughly two to three blocks of slop against its biome boundary. Harmless if every
handover is continuous, ugly the moment one steps.

**2.4 The aquifer collar cannot be designed away.** `Aquifer.NoiseBasedAquifer` samples
preliminary surface at chunk offsets spanning −3..+1 and blends the three nearest cells, so any
void air below Y 64 within roughly 48..80 blocks of a sub-sea-level seabed is filled to sea level,
whatever `final_density` said. A ring of above-sea-level land is mandatory under any architecture.

**What changes is that a purpose-built field can make that ring a fixed width in blocks.** Today
it is a continentalness band, so it balloons where the field is flat — the plateau — and pinches
below the sampling reach where the field is steep — the standing water. Both failure modes at
once, from one cause.

**2.5 A carve expressed as a density offset is gradient-dependent.** It removes down to a fixed
density value; how far that reaches in blocks is the local gradient's business. Measured: ~5
blocks on a flat top, ~0.6 of a block on a sheer face. No amount of amplitude fixes this — enough
to move a vertical face shreds every horizontal surface in the same breath. A region that wants
sheer faces and a region that wants rolling ground need different *expressions*, not different
constants.

## 3. The architecture

### 3.1 One partition, two consumers

`CLAIMS` already exists and is already priority-ordered and resolved into a disjoint partition.
It becomes the single source for **both** the biome layer and the terrain selector. A checker
asserts the two are generated from one list, so they cannot drift — the failure mode that
`gen_spawn_hub.LAYER_BIOMES` demonstrated by drifting the moment a biome was added.

### 3.2 An authority owns biomes, not thresholds

```
authority := { id, biomes[], density, handover{} }
```

The selector is emitted as a chain of **named** density functions — `alfheim:authority/step_N` —
so each step's false branches reference the next by name. Written inline the chain would repeat
its own tail once per axis test and blow up exponentially; by name it is linear.

**And there is one test per merged authority region, not per biome band.** Emitted per band it was
44 steps, and a 44-deep reference chain as `final_density` **killed the dedicated server twice**
during level preparation — no exception, no crash report, no JVM dump. Bands belonging to one
authority are fused wherever they differ on a single axis and are adjacent on it, so the void's
seven biomes become one contiguous continentalness range and the whole selector is a single
`range_choice` at −0.55. Depth is capped by a guard, because that failure had no diagnostic
signature at all.

Each leaf is that authority's complete expression for its own region. **Not an addend on a global
field.** That distinction is the whole point: a Golden Fields terrace cannot appear in Silverbark
Wood because the expression is never evaluated there — not because a weight ramps to zero, which
is a thing that has to be measured and can be got wrong.

### 3.3 The handover contract

Every authority declares, for each neighbour it touches, either

- **equal** — the two expressions agree at the shared boundary, or
- **blended** — a declared width over which one becomes the other.

A blend must interpolate **surfaces, not densities**. Interpolating two densities that both
saturate produces a step function, not a slope: measured on the old coast, where
`coast*normal + (1-coast)*plain` evaluated to `1 − 2*coast` with no Y dependence at all, and the
surface jumped when `coast` passed 0.5 instead of travelling. The same trap deleted all terrain
between continentalness −0.52 and −0.48 when an elevation offset was applied to a single
`y_clamped_gradient`, which saturates outside its span. **Interpolate between gradients; never
offset one, and never blend two saturated densities.**

### 3.4 The void field

A dedicated 2D field, normalised to −1..1 so `CLIFF`, `TERMINAL`, `FRINGE` and
`check_void_surface_support`'s −0.94..−0.925 landing window keep their meaning and the migration
is an input swap per branch plus a re-tune.

Its gain is authored, not inherited. That is what buys:

- a collar of **fixed width in blocks** around actual void, instead of a value band;
- a margin wide enough in plan that a cliff is not taller than its own biome;
- void placed where the design wants it, rather than at the bottom of every ocean basin.

**Erosion is the axis to carry it.** Of 44 claims, continentalness constrains all 44, humidity 31,
weirdness 28, temperature 26 — and **erosion only 6**, `depth` none. Erosion is already routed and
doing almost nothing. Void biomes claim low erosion; every other biome keeps spanning the full
range; `partition()` gives the void claims priority because they are listed first.

## 4. What this does not fix

- **The collar still exists** (§2.4). It becomes proportionate, not optional.
- **`libx:smash`.** MythicBotany's own `alfheim_height` is `libx:smash{axis:"y"}`, a quantiser
  upstream of every column in Alfheim. Removing it is a separate one-file override, still untested
  and still awaiting a decision.
- **It is not a licence to re-tune everything at once.** Each authority migrates with its own
  measurement and its own control world.

## 5. Staging

| stage | delivers | proof |
|---|---|---|
| **1** | one partition source; authority registry; selector emitted as named density functions; `upstream` and `void` authorities whose expressions are exactly today's | selector reproduces biome membership on N random climate points; a generated world matches the current one |
| **2** | the dedicated void field, normalised; collar as a fixed width | the three measurements in §1, re-run |
| **3** | Golden Fields becomes an authority; terracing moves inside it | `probe_terraces.py --pin` against a control |
| **4** | further authorities as biomes want distinct terrain | per-authority |

Stage 1 changes no terrain. That is deliberate: the framework is proven before anything moves,
so a later regression cannot be confused with the migration.

## 6. Measurements this architecture is accountable to

Every one has a control and a tool, and all of them exist today.

| what | tool | reading at 2026-09-12 |
|---|---|---|
| walls at the break | `probe_void_margin --edge-quality` | 9.9 per 1000 margin columns |
| face roughness | same, `RUGGED` | 0.53 exposed faces per solid block |
| internal structure | same, `RUNS` | 2.04 runs per column |
| cliff-foot talus | same, `FEET` | 25.7% |
| void that is actually void | `probe_void_margin --census` | prism_drift 73.6% empty |
| ocean that is actually wet | same | 100.0% |
| standing water in the void | ad hoc, §1 | 2.5% of void columns |
| terrace severity | `probe_terraces --pin` | +22.1 points over control |
