# The Five Deficiencies — Alfheim's damaged ground, and the rim of the world

**Role:** authoritative design record for the five negative biomes and the void terrain.
**Status:** `runtime rejected — repair designed` — the game boots and the Void Verge generates, but the generated rim is not accepted.
**2026-09-11:** the water-at-the-edge half of this rejection is addressed at the source — the sea
now ends against emerged land rather than against a dried band of sunken seabed — and the rim's
one-profile-everywhere geometry is broken up. Both are **static and analytic only**; §5's
acceptance list still governs and still requires a fresh world with eyes on it.
**Expanded definition, 2026-09-05:** `VOID_MARGINS.md` adds six environmental variants including
the existing Verge, 18 proposed stone families and concrete structure/traversal examples.
It preserves the dry-rim and terminal-empty-space contract below; it does not close this rejection.
**Authority:** subordinate to `INSTRUCTIONS.md` and `WORLD_STRUCTURE.md`.
**User instruction, 2026-09-03:** *"we need to add a number of negative biomes — Starved, Burned,
Infested, Decayed, and Void… Void biomes should just be small chunks of mana and mineral rich stone
floating in the void… random noise edge blending to just have the world come to an end in a
vaguely noisy cliff."*

**Runtime correction, 2026-09-04:** the first successful game run proved the current Void Verge
terrain wrong. The empty-density region is being occupied by water, with lava and obsidian pockets,
and the edge reads as a slow descent into an ocean rather than the end of the world. The intended
shape is now explicit: **a dry plains-like verge, then an abrupt broken rim, then open empty space,
with only diminishing fragments of stone beyond the cliff. No ocean. No lake floor. No lava sea.**

---

## 1. Why these belong

Alfheim's premise is a wasteland being repaired, but until now every biome was some shade of
*damaged but liveable* — grey grass, dead trees, fewer flowers. Nothing in the world said **this
place is finished**. The five deficiencies are the places the devastation actually completed, and
they give the campaign something it lacked: ground that is worse than where you started, so
progress can be measured by what you are able to walk into.

Four of them sit in **narrow corners of the climate space** — pockets to find, not terrain to
cross. The fifth is the edge of the world.

| Biome | What happened | Climate corner | Spawns |
|---|---|---|---|
| **Starved Reach** | Used up. Not poisoned, not burned — simply spent. No vegetation feature at all. | high continentalness, high erosion, cold and dry | spiders |
| **Scorchfell** | It burned, and kept burning. Standing dead wood, ash in the air. | mid continentalness, low erosion, hot and dry | spiders |
| **Infested Warren** | Something moved into the roots and never left. | low continentalness, low weirdness, warm and wet | cave spiders, silverfish, spiders |
| **Decayed Mire** | Rot, standing water, and what is still in it. | mid continentalness, low weirdness, cool and wet | zombies, husks |
| **Void Verge** | The world runs out. | the outer continentalness band | endermen, sparse winter fey |

Scorchfell and Decayed Mire carry ambient particles (`white_ash`, `ash`) so the damage reads
before the block palette does.

---

## 2. The Void Verge — corrected target

### 2.1 It is a rim biome, not an ocean biome

The Void Verge must be readable while the player is still standing safely on it. It is a **dry,
open, plains-like margin** where vegetation thins, the sky and fog darken, and the terrain becomes
unnaturally level before it simply stops.

The player experience is:

1. ordinary Alfheim terrain;
2. a visibly different but still walkable Verge plain;
3. a short fractured transition where the ground breaks into shelves and detached slabs;
4. a near-vertical drop into open space;
5. sparse mana-rich stone fragments that become smaller and rarer with distance;
6. finally, nothing at all except the world void below.

There is **no gradual bathymetric slope**. The edge must not resemble a coast. A player approaching
it should read "the world has been cut away", not "the land is descending into deep water".

### 2.2 One signal still owns both biome and terrain

A biome cannot directly choose a density function. The biome layer and the terrain therefore still
need a shared signal, and `mythicbotany:alfheim_continentalness` remains the correct one.

The previous design used one terrain threshold and then replaced everything outside it with floating
`cave_cheese` blobs. That solved the biome/terrain alignment problem but not the *shape* problem.
The corrected design uses **four bands driven by the same masked continentalness signal**:

| Band | Initial tuning target | Terrain role |
|---|---:|---|
| **Verge biome starts** | `< -0.80` | biome visuals change; terrain remains safe |
| **Verge plain** | `-0.86 .. -0.80` | low-relief, dry plateau with only small surface noise |
| **Breakline / debris** | `-0.94 .. -0.86` | hard cliff plus shelves, detached slabs and rubble |
| **Open void** | `< -0.94` | guaranteed empty air; no continuous terrain |

These are tuning values, not sacred constants. What is sacred is the ordering and the visual result:
**plain -> break -> fragments -> nothing**.

> **Revised 2026-09-11 — the ordering gained a band, and the numbers moved with it.**
>
> The table above assumed the sequence began at ordinary land. It does not: continentalness is
> the same axis that decides ocean, and the void sits at the bottom of the ocean basin, so the
> real sequence ran **land -> ocean -> verge -> debris** and the approach was made across water.
> Worse, the aquifer repair below dried everything under `-0.58` while leaving its terrain at
> seabed height, so the outer 42% of the ocean's own climate band generated as an ocean biome
> over an open dry basin: **123,145 of 348,224 ocean columns** in `saves/New World Ferngale`,
> measured 2026-09-11, with a seabed around Y 30 and nothing above it to the build limit.
>
> The shipped bands are now:
>
> | Band | Continentalness | Biome | Terrain role |
> |---|---:|---|---|
> | **Ocean** | `-0.55 .. -0.28` | `alfheim_ocean` | ordinary sea; wet everywhere it is claimed |
> | **Coast** | `-0.55 .. -0.46` | (inside the ocean claim) | sea floor rising to meet the shore |
> | **Void Shore** | `-0.72 .. -0.55` | `alfheim:void_shore` | emerged, dry, pale; the sea ends here |
> | **Verge plain** | `-0.86 .. -0.72` | `void_verge` | dry plateau, rooted to bedrock |
> | **Breakline** | `-0.86 .. -0.77` | `void_verge` | the eroded lip; the plain comes apart |
> | **Debris** | `-0.925 .. -0.86` | four debris biomes | shelves, slabs, rubble |
> | **Open void** | `< -0.925` | `starless_reach` | empty by construction below `-0.99` |
>
> **The dry-aquifer rim stays at `-0.58` and must not be pulled outward.** It is not a tuning
> value: `Aquifer.NoiseBasedAquifer` samples preliminary surface at chunk offsets spanning
> `-3..+1` and blends the three nearest cells, so a narrow shoulder floods the void to Y 64.
> What was wrong was never its width — it was that the band it dried was left below sea level.
> Making that band land is what lets the sea end against a coast instead of against a deletion,
> and it is what turns "no ocean at the margin" from a deletion into a geography.
>
> **The breakline is no longer a contour.** Measured over 900 columns in 30 rim segments, the
> outer edge of the plain sat at exactly `-0.8600` in every column — spread 0.0000 — with a
> face of 61..78 blocks, standard deviation 3.2. Every point at the same continentalness had
> the same profile, which is what a pure function of one smooth 2D scalar produces and why no
> amount of noise *inside* it could make it read as a coast. A broad appetite term, a 3D spall
> term and an interpolated underside now give a measured median face of **33 blocks**, 56% of
> the rim under 40, and a third of it still carrying a 60..78 block headland.

The mask keeps the existing small 2D perturbation so the rim is irregular in plan view rather than
a mathematically smooth contour. The important change is that the perturbation no longer drives a
whole field of cave-shaped islands. It perturbs the **breakline**.

### 2.3 The Verge plain is intentionally flat

The current implementation leaves ordinary terrain in the safety strip. That can still produce
hills, basins and coast-like descent immediately before the void, which undermines the silhouette.
The repaired Verge must instead suppress most large-scale relief inside the safety band.

Implementation target: construct a dedicated low-relief density branch for the Verge plain,
anchored around the normal Alfheim surface height and modulated only by low-amplitude 2D noise.
It should feel like a broad final shelf of land, not a copied Overworld plains biome and not a
perfect superflat plate.

Acceptance silhouette from a side view:

```text
ordinary land        verge plain            broken rim                open void
______/\____        _____________        ___      _
           \_______/             \______|   \__ _| \_       .   .
                                               \       .
                                                \
                                                 \
                                                  [void]
```

The cliff itself is produced by a **2D mask independent of Y**, so when the threshold is crossed the
terrain is removed through the full vertical column. That is what gives a hard wall instead of a
slow descent.

### 2.4 Debris must fade outward

The fragments beyond the rim are not a second floating-island biome. They are pieces of the edge
that have broken away.

Use the continentalness distance from the breakline as a probability envelope:

- nearest the cliff: attached shelves, long ledges, bridge-like remnants and large slabs;
- middle band: detached chunks large enough to land on and mine;
- outer band: isolated blocks, tiny clusters and occasional narrow pillars;
- beyond the debris band: no terrain at all.

`minecraft:cave_cheese` can still contribute **local fragment shape**, but it must not own fragment
frequency. Frequency is controlled by the edge-distance band, so material visibly fades away as the
player looks outward.

The fragments remain the dimension's base livingrock so the existing Alfheim ore/bloom/crystal
tags continue to work. Their value is the reason to risk the rim.

### 2.5 Why the current void fills with water

The successful run answered the open question from the previous version of this document.
`alfheim_final` can make density negative, but negative terrain density does **not** by itself mean
"air" below sea level. Alfheim's aquifer system still evaluates those empty cells and is free to
place its default fluid. That is why the current void becomes water and why lava/obsidian pockets
appear inside it.

This is not a cosmetic surface-rule defect. It is a **noise-router/aquifer defect**: the terrain
mask and the fluid decision are using different rules.

The repair therefore must make the aquifer router consume the **same void mask** as the terrain.
A post-generation water deletion pass is rejected: it would be a cleanup layer over the wrong
source behaviour and would leave fluid-update and chunk-boundary hazards.

### 2.6 Dry-void aquifer contract

The data-driven repair is to override the Alfheim noise settings/router narrowly enough that the
following channels share the rim mask:

- `final_density` — chooses Verge plain, debris branch, or empty void;
- `fluid_level_floodedness` — forced decisively into the **empty** state in the debris/open-void bands;
- `preliminary_surface_level` — masked with the same region so aquifer surface heuristics do not
  reinterpret the removed terrain as ocean floor;
- `fluid_level_spread` — retained outside the void and made inert inside it;
- `lava` — retained outside the void and made inert inside it.

Outside the Void Verge mask, every original MythicBotany value must be byte-for-byte or
structurally equivalent to the shipped setting. The correction is regional, not a global drying of
Alfheim.

If a pure datapack router cannot guarantee the empty state after runtime proof, the next step is a
small first-party worldgen hook that uses the same 2D mask to return air for aquifer fluid selection
inside the void region. That is the only acceptable code fallback because it repairs the source
fluid decision directly; it is not permission for a post-process scrubber.

### 2.7 The residue, measured 2026-09-11: a mask-keyed band cannot guarantee a distance

The dry-aquifer contract above is doing its job and there is still water in the void. Measured on
`server/void-margin-20260911-175908`, over 75,164 generated void columns:

| biome | columns | carrying water or lava | share |
|---|---:|---:|---:|
| `sepulchral_reach` | 2,494 | 228 | **9.1%** |
| `shatterfields` | 4,628 | 260 | 5.6% |
| `prism_drift` | 4,152 | 220 | 5.3% |
| `void_verge` | 56,244 | 793 | 1.4% |
| `starless_reach` | 5,486 | 18 | 0.3% |
| `rootfall` | 2,160 | 0 | 0.0% |
| **total** | **75,164** | **1,519** | **2.0%** |

**Proximity is the whole explanation, and it separates cleanly.** Distance to the nearest ocean or
lake column: wet void columns median **28 blocks, 100% within 60**; dry void columns median **84
blocks, only 22.9% within 60**. The water sits with its bottom around Y 25..49 and its top at
exactly Y 63 — a sea surface, not a spring.

The mechanism is the one shortcut in `Aquifer.NoiseBasedAquifer` that routed floodedness cannot
reach. Before consulting the floodedness noise it samples `preliminarySurfaceLevel` at chunk
offsets spanning `-3..+1` and, if any of those neighbours reports a surface at or below Y 56,
returns the global fluid status — water at sea level — for the block being decided. Our band
defeats that by pinning `initial_density_without_jaggedness` to 1.0 below `DRY_AQUIFER_RIM`, which
makes the preliminary surface resolve to the build limit. It works for every column whose
NEIGHBOURS are also inside the band.

**It cannot work where the band is narrower on the ground than the sampling reach.**
`alfheim_continentalness` is `1.7 x badlands_surface` and then clamped, and in its steepest
stretches it crosses the entire margin in a few tens of blocks. There the ocean comes within 28
blocks of a debris biome and the shortcut fires across the gap. No value of `DRY_AQUIFER_RIM`
fixes this: the requirement is a *distance*, the band is expressed as a *value*, and the field's
gradient is not ours to set. Widening the band far enough to cover the steepest stretches would
need more continentalness than the axis contains.

This is the sharpest argument for **B-96**, a dedicated void field whose gain we choose: a margin
that is a fixed width in blocks can hold the sampling reach open everywhere instead of only where
the terrain happens to be gentle. Until then the residue is 2.0% of void columns and it is
recorded here rather than tuned at.

### 2.7 No void sea

The former "maybe add a void-sea mod" branch is closed. The runtime result demonstrated exactly why
that visual language is wrong for this world edge. The design target is **open empty space**.
Falling past the fragments means falling into the dimension void.

---

## 3. Void resources and encounter grammar

The Void Verge is dangerous because footing disappears, not because it becomes another combat
biome. Resource density can therefore be somewhat higher than elsewhere without turning the area
into a dungeon.

The existing **Rim geode** remains Duskglass | Galeglass and is currently authored at **1 in 8
chunks** in `tools/crystals_manifest.json`. That value supersedes the older 1-in-3 prose that used
to be in this document.

Ore and bloom generation on detached fragments should be allowed only where the fragment has enough
solid volume to contain the feature. A geode intersecting a three-block shard would look like a
worldgen error. The implementation therefore needs either minimum-solid-volume placement checks or
an inner debris band reserved for full geodes, with only smaller ore/bloom features allowed farther
out.

No generated water source, lava source, obsidian patch or conventional shoreline feature is valid
inside the open-void band.

---

## 4. Implementation sequence

### Pass V1 — reproduce and instrument

Use the already successful fresh-world path and record the first Void Verge coordinates that show
the failure. Add a small debug sampler to `tools/gen_alfheim_biomes.py` or a sibling validation tool
that prints the continentalness/mask band expected at those coordinates. This gives the repair a
known runtime target rather than tuning blind.

### Pass V2 — plains rim and hard cut

Replace the current single `VOID_TERRAIN_MAX` branch with the four-band terrain contract. Preserve
normal terrain outside the biome, flatten only the Verge safety shelf, then remove the terrain as a
vertical cut at the breakline.

### Pass V3 — dry the void at the source

Override the aquifer-related noise-router channels with the same mask. Validate that chunks below sea
level inside the void contain air, not water or lava, before touching debris density.

### Pass V4 — debris falloff

Add the edge-weighted shelves/slabs/rubble field. Start with coarse fragments; tune frequency before
texture/detail. The outer band must converge to literal zero terrain.

### Pass V5 — resource compatibility

Re-enable/validate blooms, Rim geodes and mineral features on sufficiently large fragments. Verify
that no feature constructs a fake floor or bridges the open void unintentionally.

### Pass V6 — runtime acceptance

Fresh world only. Walk from ordinary Alfheim across the Verge and over the edge in spectator and
survival. Inspect at least three separated rim segments so one lucky contour cannot pass the test.

---

## 5. Acceptance criteria

The Void Verge remains **rejected** until all of these are seen in a fresh world:

1. the approach is dry, walkable and plains-like rather than descending toward water;
2. the land terminates in a visually abrupt cliff/breakline;
3. the void below and beyond the rim contains no generated water body;
4. no lava sea or routine lava/obsidian pockets occupy the void volume;
5. debris is densest near the rim and visibly fades to isolated pieces and then nothing;
6. the far field is genuinely empty space down to the world floor;
7. resources occur on substantial fragments without creating impossible hanging geodes;
8. ordinary Alfheim terrain and aquifers outside the Void Verge are unchanged;
9. the player can identify the world edge before accidentally walking off it;
10. all static worldgen/feature-order checks still pass before runtime admission.

The failure observed on 2026-09-04 is therefore useful evidence: the biome now exists and the game
can reach it, which means the remaining problem is no longer "does the system load?" It is the
specific terrain-and-fluid contract above.
