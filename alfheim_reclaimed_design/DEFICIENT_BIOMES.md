# The Five Deficiencies — Alfheim's damaged ground, and the rim of the world

**Role:** authoritative design record for the five negative biomes and the void terrain.
**Status:** `runtime rejected — repair designed` — the game boots and the Void Verge generates, but the generated rim is not accepted.
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
