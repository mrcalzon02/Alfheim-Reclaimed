# The Five Deficiencies — Alfheim's damaged ground, and the rim of the world

**Role:** authoritative design record for the five negative biomes and the void terrain.
**Status:** `draft` — statically validated, never generated in a running game.
**Authority:** subordinate to `INSTRUCTIONS.md` and `WORLD_STRUCTURE.md`.
**User instruction, 2026-09-03:** *"we need to add a number of negative biomes — Starved, Burned,
Infested, Decayed, and Void… Void biomes should just be small chunks of mana and mineral rich stone
floating in the void… random noise edge blending to just have the world come to an end in a
vaguely noisy cliff."*

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
| **Void Verge** | The world runs out. | the outer fifth of continentalness | endermen |

Scorchfell and Decayed Mire carry ambient particles (`white_ash`, `ash`) so the damage reads
before the block palette does.

---

## 2. The Void Verge

### 2.1 The problem the vanilla toolkit does not solve

A biome cannot change terrain. Density functions are dimension-wide and **cannot read biomes** —
there is no `if (biome == void) return air`. So a "void biome" is not one thing; it is two things
that have to be made to agree:

- a **biome** that says *this is the rim*, chosen by the LibX biome layer from climate parameters;
- **terrain** that actually stops, produced by a density function that knows nothing about biomes.

The only way to make them agree is to drive both from the **same signal**.
`mythicbotany:alfheim_continentalness` is what the biome layer already selects on, so the terrain
mask reads that same function. Continentalness is, definitionally, *how much continent is here* —
so the world ending where it runs out of continent is the honest reading of the parameter, not a
trick played on it.

### 2.2 Two numbers, and the order that matters

```
VOID_BIOME_MAX   = -0.80     the biome claims continentalness below this
VOID_TERRAIN_MAX = -0.86     the floor disappears below this
```

**The terrain band is deliberately narrower than the biome band.** Every piece of void terrain then
falls inside the void biome, and the 0.06 strip between them is void *biome* with ordinary
ground — a shore, where the sky goes black and the fog closes in before the floor runs out.

Reversed, the floor would vanish under a forest. That reads as corruption, not as the edge of the
world, and it is invisible until someone walks into it. **`check_worldgen.py` W7 asserts the
ordering** and fails on reversal; verified against a synthetic flip.

### 2.3 The density function

`mythicbotany:alfheim_final` ships as `min(alfheim_initial, alfheim_caves)`. The datapack
overrides that one file — not the whole noise settings — and wraps it:

```
range_choice(
  input:             cache_2d( alfheim_continentalness + 0.035 * noise(surface) )
  [-2.0 .. -0.86):   min( islands, y_window )        ← the void
  otherwise:         min( alfheim_initial, alfheim_caves )   ← untouched
)

islands   = 2.0 * noise(cave_cheese, xz 1.0, y 0.8) - 1.35
y_window  = min( gradient(y20→50: -1→1), gradient(y110→150: 1→-1) )
```

- **The cliff is ragged** because the mask is continentalness *plus a small high-frequency
  perturbation*. Continentalness alone contours too smoothly to read as a broken edge. `cache_2d`
  keeps the mask a 2D lookup rather than a per-block 3D sample.
- **Islands are sparse** because only the top slice of `cave_cheese` clears zero after the −1.35
  offset.
- **They float in a band**, y 50–110, because a single `y_clamped_gradient` is monotonic; two of
  them under a `min` make a window. Below the band is open air to the world floor.
- **Islands are livingrock**, the dimension's own `default_block` — so they are mana-bearing by
  construction, and every ore and geode feature that targets `#mythicbotany:base_stone_alfheim`
  works on them unchanged. That is the "mana and mineral rich stone" the instruction asked for,
  obtained by not fighting the dimension.

### 2.4 Crystals in the void

A seventh geode, **the Rim** (Duskglass ∣ Galeglass), generates only in the Void Verge at
**1 in 3 chunks** — the most common of the seven. The rim is the richest ground in Alfheim and the
hardest to stand on, which is the trade the biome exists to offer.

---

## 3. The void sea — not built, and why

The instruction asked whether a void-sea mod could give the empty biomes a bottom.

**DNS resolves from this machine** (an earlier project note saying the sandbox had no network is
stale). So fetching a mod is not blocked by the environment. It is blocked by process, and
deliberately:

1. Installing a jar is a **pack composition change**, not a datapack change. It touches
   `minecraftinstance.json`, the pinned mod matrix, and the dependency graph.
2. The project has its own intake protocol — `tools/check_incoming_mod.py` must run on any jar
   before it goes near `mods/` (loader format, mod-ID collisions, dependency resolution,
   Overworld-generator ownership, convention tags).
3. It needs the pack owner's explicit say-so on *which* mod, since this is a distributed pack.

**What exists without a new mod:** the Void Verge already has no floor — below the islands is open
air to y −64 and then the world's bottom, which is the vanilla void. What a void-sea mod would add
is a *surface* down there to fall onto or swim in. That is a genuine gap and it is a reasonable
thing to want; it is simply not something to install unilaterally.

**If it is wanted:** name the mod, and the intake check runs first.

---

## 4. Open

1. **Nothing here has generated.** The void density function is the single riskiest file in the
   datapack: a malformed density function fails world creation outright, and no static check can
   prove the terrain it produces is *playable* rather than merely legal.
2. **Surface rules still apply in the void.** Alfheim's surface rule will cap the floating islands
   with whatever it caps ordinary ground with, probably grass. Cosmetic, and fixable with a
   surface-rule override — a larger and riskier change than this one, so deliberately deferred.
3. **Aquifers are enabled dimension-wide** (`aquifers_enabled: true`). Whether they produce
   floating water in the void band is unknown until it generates.
4. **Void structures** were asked for and are not built. Structures need an NBT pipeline
   (`SPAWN_ZONE.md`, B-19 territory) and belong in their own unit of work.
5. **The four deficient biomes are untuned.** Their climate corners were chosen to be narrow; if
   they turn out too rare to ever meet, widen the bands rather than adding more of them.
