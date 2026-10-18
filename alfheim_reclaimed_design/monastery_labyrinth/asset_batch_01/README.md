# Five Descents asset batch 01 — 2026-10-18

**Acceptance: static validated prototypes. Staged outside the active pack.**

This begins the delivery order in `FIVE_ACT_LABYRINTHS_AND_SITE_ALLOCATION.md`.
Continuity Works' local `StructureCapability.plan` and `generate` executed with a
pack-authored provider. Creature art follows the existing monstrosity sculpture,
UV-island and material-painting workflow, using original geometry.

## Review the emitted assets

- [Creature sculptures: front, three-quarter and rear](creature_sculptures.png)
- [All thirty-six creature appearances](creature_appearances.png)
- [Wave 02 sculptures](creature_wave_02_sculptures.png)
- [Wave 02 action preview](creature_wave_02_signature_motion.gif)
- [Wave 02 action still](creature_wave_02_signature_poses.png)
- [Magnified rat details](creature_wave_02_small_details.png)
- [Signature-action motion preview](creature_signature_motion.gif)
- [Signature-action pose still](creature_signature_poses.png)
- [Art motion and future combat contracts](art_motion_contracts.json)
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

Twelve original sculptures now have three material-painted skins each. The first
six are the 95-part
Ashen Novice, 87-part Lurking Silkmaw, 105-part Bell Warden, 113-part Ossuary
Bowyer, 103-part Reliquary Sentinel and 116-part Ossuary Prior. Each includes a
detailed geometry export, an editable Blockbench model, and textured OBJ/MTL
files importable into Blender. The Bowyer carries a segmented bone bow and
independently posed string/arrow. The Sentinel has a broad frontal bulwark and
exposed rear reliquary. The Prior has a rib halo, ceremonial mitre and bell staff.

The second wave adds six original anatomies:

| Creature | Sculpted parts | Readable visual cue |
|---|---:|---|
| Hollow Veil | 89 | Empty veiled face and contracting cloak |
| Lantern Ghoul | 91 | Exposed hanging lantern outside its shoulder silhouette |
| Corvid Undertaker | 87 | Hooked avian beak, talons and feathered calling wings |
| Rotmilk Ratpack | 89 | One 0.443-block-high rat member, whiskers and segmented tail |
| Grave Thorn | 100 | Rooted grave marker and four spreading barb fans |
| Mourning Matron | 96 | Empty rib cradle, open palms and wound-silk tassels |

The rat model is one pack member, not a giant combined swarm entity. Pack
composition and grate travel remain runtime work. The Grave Thorn stays rooted;
its `walk` slot is a root-settling reference, not locomotion. It has a separate
stationary trap design, not a recolor of the installed mobile Thorn Infestor.

All twelve now include a root hierarchy, named articulation groups, anatomical
pivots, and editable idle, walk and signature-action clips: 36 clips total.
Jaws, bowstrings, arrows, clappers, lanterns and tails inherit their attachment's
motion; offline pose evaluation follows the same exported group hierarchy.
Signature clips show a bell-triggered stagger, silk ambush descent, rally toll,
marked bow shot, bulwark slam and the Prior's convergence gesture. These are
**art-motion prototypes**, not native game animation or functioning combat.
The new six add phase-slip, lantern-charge, scavenger-call, grate-rush, rooted
snare and wound-transfer gestures. Creature appearance and animation do not
substitute for distinct server-authoritative behavior implementations.
Markers identify visual timing only; no hit, sound, projectile, summon or damage
event executes. Original sound production and native animation remain pending.
The catalogue remains `design_only`; this adds zero implemented species.

`five_act_asset_queue.json` maps all 130 species to their existing signature and
counterplay, records 18 proposed room families per Act, gives distinct material
directions for Acts II–V and identifies the twelve art prototypes. Later Acts'
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
hashes. It also checks all clip group references, finite sampled poses and exact
loop endpoints. The animation save representation was inspected in the installed
Blockbench 4.12.4 source; `art_motion_contracts.json` records source entry hashes.
Actual editor import remains pending. A standing-cell route is evidence of
geometry connectivity, not proof of Minecraft collision, animated movement,
combat or server performance.

Executed on 2026-10-18: all 75 template and twelve-model artifact checks passed;
all creature outputs reproduced byte-for-byte; the existing 130-species bestiary
validator passed; the active pack feature-order check found zero cycles across
313 loaded biomes, including Forge biome modifiers. No game was booted for this
asset batch. Static validation is the current acceptance boundary.
