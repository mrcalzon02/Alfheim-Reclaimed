# Alfheim monstrosities — 2026-10-16

Six new hostile entity types with authored native models, three stored regional
skins each and 18 individually selectable skinned-head spawn items. These are
new anatomies and combat behaviors alongside the existing enemy catalogue.

## Art revision — 2026-10-17

Rebuilt the six sculptures after visual rejection of the first preview. Each
now has 86–120 individually sculpted pieces with dedicated UV islands in a
512-pixel atlas. Materials use separate shaded ramps, creases, grain, cracks,
stitching and trim rather than one shared noise texture. All 18 regional skins
were regenerated from the revised surfaces. Inventory heads are transparent
renders of the actual native head geometry and its matching skin, retaining
angled tusks, horns and facial plates.

- Troll: sloped spinal hump, sunken eyes and scars, curved tusks, layered
  musculature, fingers and nails, moss growths, one carved ruin pauldron and
  stitched hide panels.
- Cyclops: recessed single eye and eyelid, broken teeth, beard locks, diagonal
  harness, contrasting bracers and greave, bound stone maul and carved markings.
- Briar Beast: exposed heartwood and root ribs, layered bark, antlers, a
  toothed predatory jaw, reverse hocks, root claws, lichen and seed pods.
- Thorn Infestor: split seed-pod maw, offset spore eye, uneven fungal growths,
  rib cage, curved barbed lashes and spreading root feet.
- Gargoyle: angular carved chest and face, swept horns, scalloped bat membranes
  with separate finger bones, talons, digitigrade legs and a curved tail.
- Hag: gaunt asymmetrical face, hair strands, antler circlet, layered robe
  panels, embroidered hems, torn shawl, bottles and charms, long claws and a
  forked skull staff.

`tools/monstrosities_detail.png` contains larger front, three-quarter and rear
views; `tools/monstrosities_review.png` is the common-scale overview. These
are faithful offline previews, not client screenshots or an artistic sign-off.

| Creature | Physical height | Base health | Attack |
|---|---:|---:|---|
| Hulking Troll | 3.6 blocks | 90 | Telegraphed heavy punch and strong knockback |
| Cyclops | 3.2 blocks | 76 | Single-eyed giant with a club and knockback |
| Briar Beast | 1.9 blocks | 52 | Thorn-armored quadruped; claws slow victims |
| Thorn Infestor | 2.25 blocks | 42 | Articulated vine whips; poison and slowing, reach 4 blocks |
| Stone Gargoyle | 2.1 blocks | 60 | Armored winged predator with leaping melee strikes |
| Hag | 2.35 blocks | 38 | Visible poison-hex windup and a 6.5-block magic attack |

The troll's collision height is exactly twice the player's 1.8-block height;
the renderer uses matching world scale. Models have separate flesh, eye, horn,
cloth, bark and membrane UV materials, plus anatomical details such as tusks,
brow ridges, fingers, roots, bark plates and segmented whips. Gargoyles leap;
they do not have continuous flight AI.

All attacks recheck reach and line of sight at impact. Escaping or breaking
sight interrupts a windup. Thorn whips poison for three seconds and slow for
two; briar claws slow for three; hag hexes poison for four. These are base
combat values, subject to the pack's normal combat scaling. Replaced hits are
confirmed from health, absorption and Mine and Slash shield changes without
issuing duplicate damage. No block breaking,
terrain infestation, player equipment replacement or new progression material
is introduced. Existing vanilla ingredients make up the small loot tables.

## Regional appearances

- Hulking Troll: Mossback, Granite, Rime.
- Cyclops: Highland, Ashen, Sepulchral.
- Briar Beast: Rootbound, Withered, Bloomthorn.
- Thorn Infestor: Thornlash, Sporethorn, Frostthorn.
- Stone Gargoyle: Basalt, Prism, Grave.
- Hag: Fen, Mire, Rime.

## Natural spawning

There are 29 explicit habitat entries across the six types in Alfheim.
Each spawn is a single creature, with weights 2–4. Normal hostile darkness and
ground requirements apply, plus body clearance and an Alfheim dimension check.
Existing biome enemies, monster caps, terrain and structures are retained.
Skins are selected from the actual spawn biome; spawn-item selections override
that choice and survive saves. Creatures can also be summoned or spawned with
their 18 named inventory selections.

## Verification

Java17 build and 72 tests; six distinct baked anatomies, finite native animation
channels, UV/head-source checks and all 18 resource sets. Feature ordering has
no cycles. The review sheets render actual baked textured surfaces at a shared
world scale; height markers represent a 1.8-block player. They are offline
previews, not game screenshots.

`tools/run_monstrosity_validation.py` checks 18 actual egg spawns, physical
sizes, damage, effects, blocked sight, out-of-range attacks, saved appearances,
six simulated native goal attack cycles, all 29 loaded habitat entries and natural spawn rules.
The command advances full entity age and explicitly primes the native goal
selector because its synchronous simulation holds the server clock fixed.
The server audit passed on 2026-10-17; its report is
`tools/monstrosities_build.json`. Client motion/lighting
review and long-run natural density tuning remain pending. Restart Minecraft
to load the installed companion build.
