# Five Descents asset batch 01 — 2026-10-18

**Acceptance: static validated prototypes. Staged outside the active pack.**

This begins the delivery order in `FIVE_ACT_LABYRINTHS_AND_SITE_ALLOCATION.md`.
Continuity Works' local `StructureCapability.plan` and `generate` executed with a
pack-authored provider. Creature art follows the existing monstrosity sculpture,
UV-island and material-painting workflow, using original geometry.

## Review the emitted assets

- [Creature sculptures: front, three-quarter and rear](creature_sculptures.png)
- [All nine creature appearances](creature_appearances.png)
- [Room geometry cutaways](room_cutaways.png)
- [All 25 family floor plans](room_floorplans.png)
- [Five-Act production queue](five_act_asset_queue.json)
- [Static validation evidence](static_validation.json)

The room cutaways use flat material colors and hide roofs/front walls for
inspection. Creature sheets render the actual model quads and their matching
512-pixel skins. These are offline artifact previews, not Minecraft screenshots.

## What exists

75 valid Minecraft 1.20.1 structure NBTs: 18 Act I dungeon room families, six
service interiors and one straight connector, in three conditions each. Ordinary
rooms are 29×15×29; the switchback is 29×18×29 and rises twelve blocks; the
rotatable passage is 7×8×29. Kept/weathered variants differ in masonry surfaces;
ruined variants also lose small internal fixtures while retaining containment.
The refuge rooms are **interior modules**, not fitted replacements for the native
13×19 service stalls. No functional economy is implied by their furniture.

The 95-part Ashen Novice, 87-part Lurking Silkmaw and 105-part Bell Warden each
have three material-painted skins, a detailed geometry export, an editable
Blockbench model with named articulation groups, and textured OBJ/MTL files
importable into Blender. There are no animation keyframes or native baked models
yet. The catalogue remains `design_only`; this adds zero implemented species.

`five_act_asset_queue.json` maps all 130 species to their existing signature and
counterplay, records 18 proposed room families per Act, gives distinct material
directions for Acts II–V and identifies the three art prototypes. Later Acts'
room names and material directions are plans, not generated geometry.

## Contracts and integration gates

- Seed `2026101801`; DataVersion `3465`; no template axis exceeds 48 blocks.
- Native room datum retained: floor layers 0/1, ordinary doorway feet at Y 2.
  Ordinary sockets are five blocks wide and five high, with a dry crossing.
- Stairs have north lower and south upper sockets. The native graph's actual
  stratum delta varies with surface height; this 12-block prototype needs an
  exact-height adapter and client movement tests before replacing ladder shafts.
- Passage length matches inclusive native connector endpoints at a 56-block
  room pitch. Rotation, door masks/caps and graph-to-template selection are pending.
- No room, vendor, portal, monster, loot table or structure is registered here.
  Natural placement still requires one shared family reservation, existing
  court/castle/district priorities, independent-structure clearance, terrain fit,
  a compatible rebuilt companion JAR and fresh-world evidence.
- No existing worlds, active `kubejs` resources, JARs or monster IDs are changed.

## Reproduce and validate

Run from the instance root using Python 3.11+; art/preview/check tools need Pillow
and NumPy. The desktop's bundled Python includes both.

```powershell
python -X utf8 -B tools/gen_labyrinth_asset_kit.py --cw-source C:/GITS/Structuresmith/StructureSmith
python -X utf8 -B tools/gen_labyrinth_creature_art.py
python -X utf8 -B tools/gen_labyrinth_creature_art.py --check
python -X utf8 -B tools/gen_labyrinth_asset_queue.py
python -X utf8 -B tools/check_labyrinth_asset_kit.py
python -X utf8 -B tools/render_labyrinth_asset_kit.py
python -X utf8 -B tools/check_labyrinth_bestiary.py
```

The structural provider probes actual block IDs, emits deterministic compressed
NBT, and records Continuity Works snapshot/source and registry hashes in
`structure_manifest.json`. Its snapshots are under `build/labyrinth-asset-kit/`.
The independent checker reloads NBT, compares source geometry, walks all sockets,
checks UV ownership, used texel opacity, export winding, group references and file
hashes. A standing-cell route is evidence of geometry connectivity, not proof of
Minecraft collision, animated movement, combat or server performance.

Executed on 2026-10-18: all 75 template and three-model artifact checks passed;
all creature outputs reproduced byte-for-byte; the existing 130-species bestiary
validator passed; the active pack feature-order check found zero cycles across
313 loaded biomes, including Forge biome modifiers. No game was booted for this
asset batch. Static validation is the current acceptance boundary.
