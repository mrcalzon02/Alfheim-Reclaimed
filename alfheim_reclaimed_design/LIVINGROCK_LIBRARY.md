# The Deep and the Alfheim Livingrock library

**Terrain continuation:** `DEEP_TERRAIN.md` records the subsequently implemented natural stone
masses, cavern density field, initial lava basins and deep-bloom supplements. The material-pass
sequencing statements below describe the point at which this library was first delivered.

**User revision, 2026-09-05:** resume the Deep; expand the former three-stone foundation into a
large library, with many non-magmatic stones useful in other Alfheim structures. Livingstone in
conversation refers to the Livingrock family; IDs retain Botania's established spelling.

## Implemented material scope

24 families, each with natural, polished, brick, carved, slab, stair and wall forms: 168 blocks.
Six aligned mana-glasses and cooled, non-dropping slag bring the library to **175 blocks**.
Slabs, stairs and walls use the brick texture. The carved diamond-and-leaf device ties the
architectural sets together. These are decorative stones, with no passive mana production,
ore drops, combat bonuses or crystal conversion.

| Palette | Families | Architectural purpose |
|---|---|---|
| Furnace | Cracked, Magmatic, Embervein, Cinder, Obsidian | Lava shores, furnace walls, forge terraces, quarry transitions |
| Court | Moonstone, Dawn, Rose, Ivory, Silvermist | Tombs, royal halls, memorials, civic arcades and archives |
| Grove | Moss, Rootbound, Fern, Amber, Petrified | Greatbole foundations, garden cloisters, reclaimed ruins and root columns |
| Water and sky | Tide, Abyssal, Frost, Gale, Storm | Aqueducts, cold grottoes, drowned temples, bridges and watchtowers |
| Ley | Amethyst, Leyline, Gloam, Starfleck | Crystal chambers, observatories, quiet sanctuaries and mana channels |

Nineteen families are outside the Furnace palette. Most stones do not emit light. Cracked emits
1, Magmatic 10, Embervein 4, Leyline 3 and Starfleck 2, on Minecraft's 0–15 scale. Light applies
to each family's building forms. This is block light; shader-independent emissive texture masks
are not implemented. Magmatic stone does not currently inflict contact damage.

The source catalog is `tools/deepworks_manifest.json`; `tools/gen_deepworks.py` emits registrations,
103 textures, item models, cube models, loot tables, narrow Alfheim tags and 174 stonecutting recipes.
The installed KubeJS shape builders generate slab/stair/wall models and states. Textures extend the
existing local pipeline, using the first frame of Botania's animated Livingrock as their relief.
The source asset hash is recorded in `tools/deepworks_source.json`.

## Acquisition and building

Use a stonecutter: ordinary Botania Livingrock yields any natural family at 1:1. A natural family
cuts into its six architectural forms, at 1:1 except slabs at 1:2. Vanilla glass cuts into each
aligned mana-glass at 1:1. These ungated decorative routes make the library usable for construction
before natural deposits exist; no rare crystal is consumed or created. They also avoid making
access to a lava chamber mandatory for building a woodland pavilion.

Stones require a pickaxe and drop themselves. Double slabs drop two. Glass requires Silk Touch to
recover; ordinary mining drops nothing. Slag drops nothing, including with Silk Touch, and has no
resource recipe. Natural deposit placement is still part of the terrain pass.

Restart the client for registration, then search JEI for the family names. The review atlas is
`tools/deepworks_review.png`. The dedicated test world contains every block at a spaced review grid
near x=0..39, y=160, z=0..36 in Alfheim; this is development evidence, not a player-world structure.

## The Deep's environmental target

The requested Nether-like scale and lava abundance remain the target: an underground province of
linked colossal caves, with surviving elven works built into its shelves and walls. The surface's
lost mana accumulated here. Lava, cool mana channels and mineral diversity can coexist.

Retain the target of chambers 48–160 blocks across, linked complexes 200–400 blocks long and
25–70 blocks of interior height where terrain allows. The floor limit is still y=-64, so tall
chambers must rise above the old -20 ceiling rather than pretending 70 blocks fit in a 32-block
band. Cavern ceilings must retain a solid roof beneath the local surface. No dimension-height
change is implied. A masked deep density field must coexist with the existing Void Verge terrain.

| Environment | Geology and formations | Structures it supports |
|---|---|---|
| Furnace basins | Lava → Magmatic/Embervein shore → Cracked shell; Cinder/slag high-water shelves | Damaged forge galleries and hot Faultworks |
| Root vaults | Petrified columns, Rootbound and Moss walls; cooler upper connections | Old extraction halls and botanical galleries |
| Crystal reaches | Amethyst/Starfleck masses, paired crystal chandeliers and aligned mana-glass | Mineral quarries and observatory ruins |
| Stillwater reaches | Tide/Abyssal walls, pale Frost and Silvermist shelves; isolated from lava basins | Cisterns, aqueducts and drowned galleries |
| Crown shelves | Stable Ivory/Moonstone/Dawn masonry above the hot floor | Sealed elder-king tombs with marble/quartz accents |
| Ley wounds | Cool Leyline channels meeting hot fissures, Gloam borders and vitrified bands | Faultworks carrying the failed-working story |

These are planned environmental assemblages, not six newly registered biomes. Material zoning
must follow coherent masses and formations, with transitions; it must not scatter all 24 stones
uniformly through every cave.

## Ore abundance and archaeology

Richness means visible native elven ore and bloom seams, concentrated in quarry faces, cavern
walls and mineral columns. Ore-bearing blocks must be placed after geological replacement, or
target the narrow `alfheim:deepworks_replaceable` tag in Deep-specific features. Do not add the
library to vanilla ore-replaceable tags. Do not blanket-increase ordinary Midgard metals.
Existing bloom processing and the Spine of Leaf remain the route from deposits to useful metals.
Exact vein counts need a before/after fresh-world census and are not claimed by this material pass.

Quarries should open into the large caves with exposed seams and supported gallery floors. Tombs
use the cool Court palette on stable dry shelves, with their sealed burial rooms behind the rock
face. Faultworks terminate on visible ley scars. Entries, floors and supports need actual solid-rock
anchor checks; a random Y coordinate alone does not qualify a site. Tomb loot cannot skip eras.

## Acceptance and continuation

The library is the implemented D1 foundation. The headless D2 audit checks registration, placement,
light, shape state properties, recipes and real loaded loot tables. It cannot accept client models,
glass sorting against lava, hand-mining feel or the visual result of connected stairs and walls.
Those remain client review items. Cavern generation, natural stone deposits, rich ore distribution,
lava formations and the three archaeological families remain subsequent implementation passes.

Checks: `python tools/check_deepworks.py`, `python tools/check_feature_order.py`, and
`python tools/run_deepworks_validation.py`. The harness uses a separate development world and
does not edit player saves. See `EXECUTION_STATE.md` for actual runtime results.
