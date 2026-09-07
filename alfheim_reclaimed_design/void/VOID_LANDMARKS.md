# Void Margins — additive landmark family

**Role:** implementation-facing extension of `TERRAIN_AND_STRUCTURES.md` for floating geodes, astral towers and ley-line focus nodes.
**Status:** placement contract defined; generated structures and fresh-world placement still require proof.
**Source:** `tools/void_landmarks_manifest.json`.

## Authority and scope

The twelve structures in `TERRAIN_AND_STRUCTURES.md` remain the biome-core coverage set. This landmark family is additive and does not replace or satisfy those twelve slots.

The additive landmarks are **Void-space structures**, not ordinary surface structures. Empty Void columns do not provide a meaningful `WORLD_SURFACE_WG` result. Heightmap projection can therefore collapse a jigsaw start toward the dimension floor instead of placing the object in the intended Void volume.

## Fixed-height rule

For additive Void landmarks the default registration contract is:

- `start_height: {"absolute": 0}`
- **no `project_start_to_heightmap` field**
- `terrain_adaptation: "none"`

Y=0 is the structure start plane, not a request to locate terrain at Y=0. The structure begins there even when the entire column is empty.

This applies by default to the requested floating geodes, astral towers and ley-line focus nodes. A future landmark may use another explicit absolute height only when its design deliberately calls for another vertical band. It may not silently fall back to surface projection.

The biome-core Void ruins are different: Anchor Bastions, Root Shrines, cliff tombs and similar ruins explicitly depend on real terrain support and may use their own support/placement logic. Their surface behavior must not be generalized to the additive landmark layer.

## Floating geodes

**Prism Drift Geode** and **Starfall Geode** are suspended formations. They contain no generated foundation or hidden rescue island and never ask Minecraft to locate a surface beneath an empty Void column.

Prism Drift Geode uses Prismstone and Aetherquartzite with luminous Seamstone ribs. Starfall Geode uses Nightmantle, Astralite and Veilstone. Each is hollow, visibly fractured and opened on at least one face, with an internal crystalline axis so it reads as a geological/magical formation rather than a stone sphere.

## Astral towers

**Astral Watchtower** and **Nightglass Spire** are free-standing Void observatories. They start from the fixed Y=0 plane and do not query a surface heightmap. Their lowest platform is architecture, not generated terrain, and may not expand into an island merely to support the tower.

Astral Watchtower uses Anchorstone, Veilstone, Astralite and Seamstone around an orrery crown. Nightglass Spire uses Nightmantle, Aetherquartzite and Glintschist around a dark astronomical lens. Both require readable interior decks, a continuous climb path and cardinal observing geometry.

## Ley-line focus nodes

**Ley Focus Ring** and **Fractured Ley Focus** are compact ruined infrastructure in Void space. They use the fixed Y=0 start contract, do not project to a surface and do not manufacture a rescue island.

The intact ring uses Anchorstone, Seamstone, Veilstone and Astralite. The fractured node uses Shardbreccia, Glintschist, Riftshale and Seamstone. They are focusing infrastructure remnants, not new functional mana generators.

## Placement and overlap

The six templates are grouped into three families: floating geodes, astral towers and ley-focus nodes. The families should share one weighted `random_spread` structure set so a candidate cell selects one family instead of stacking several independent sets in the same cell.

Initial biome admission remains conservative. Distribution across sibling Void biomes is separate from vertical placement. Expanding a biome tag must never reintroduce heightmap projection as a substitute for a real Void-space placement rule.

## Acceptance contract

Static acceptance requires every additive landmark registration to use an explicit absolute start height; the current default is exactly Y=0; `project_start_to_heightmap` is absent; `terrain_adaptation` is `none`; no template creates a replacement island or broad terrain footing; templates remain at or below the 48-block inspection limit; and source-to-shipping equality is proven before claiming implementation.

Fresh-world acceptance must inspect at least three separated placements and reject immediately if any landmark appears at the bottom of the dimension, attempts to hug a nonexistent surface, or creates an artificial terrain mass merely to remain supported.
