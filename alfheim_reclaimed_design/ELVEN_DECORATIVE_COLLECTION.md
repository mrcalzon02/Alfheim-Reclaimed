# Elven decorative collection — 2026-10-15

38 craftable scenery objects, 52 block-model parts and 14 complete assembled item
models in the owned Alfheim Leyworks mod, Java 1.20.1 / Forge 47.4.10.

## Collection

### Seating (8)

- **Dreamwood Side Chair** — `alfheim_leyworks:decor_dreamwood_side_chair` (floor).
- **Moonvelvet Armchair** — `alfheim_leyworks:decor_moonvelvet_armchair` (floor).
- **Leafback High Chair** — `alfheim_leyworks:decor_leafback_high_chair` (floor).
- **Royal Audience Chair** — `alfheim_leyworks:decor_royal_audience_chair` (floor).
- **Moonvelvet Ottoman** — `alfheim_leyworks:decor_moonvelvet_ottoman` (floor).
- **Braided Reed Ottoman** — `alfheim_leyworks:decor_braided_reed_ottoman` (floor).
- **Spring Silk Sofa** — `alfheim_leyworks:decor_spring_silk_sofa` (sofa).
- **Twilight Velvet Sofa** — `alfheim_leyworks:decor_twilight_velvet_sofa` (sofa).

### Display (4)

- **Relic Display Cabinet** — `alfheim_leyworks:decor_relic_display_cabinet` (tall).
- **Ceremonial Arms Cabinet** — `alfheim_leyworks:decor_arms_display_cabinet` (tall).
- **Crystal Display Cabinet** — `alfheim_leyworks:decor_crystal_display_cabinet` (tall).
- **Court Regalia Cabinet** — `alfheim_leyworks:decor_ceremonial_display_cabinet` (tall).

### Honors (6)

- **Sunleaf Medallion** — `alfheim_leyworks:decor_sunleaf_medallion` (wall).
- **Moonbranch Medallion** — `alfheim_leyworks:decor_moonbranch_medallion` (wall).
- **Warden Service Medal** — `alfheim_leyworks:decor_warden_service_medal` (wall).
- **Grovekeeper Medal** — `alfheim_leyworks:decor_grovekeeper_medal` (wall).
- **Fallen Star Medal** — `alfheim_leyworks:decor_fallen_star_medal` (wall).
- **Royal Honors Plaque** — `alfheim_leyworks:decor_royal_honors_plaque` (wall).

### Trophy (4)

- **Crystal Stag Trophy** — `alfheim_leyworks:decor_crystal_stag_trophy` (floor).
- **Fallen Golem Trophy** — `alfheim_leyworks:decor_fallen_golem_trophy` (floor).
- **Silverleaf Laurel Trophy** — `alfheim_leyworks:decor_silverleaf_laurel_trophy` (floor).
- **Regatta Sail Trophy** — `alfheim_leyworks:decor_regatta_sail_trophy` (floor).

### Arms (4)

- **Leafguard Shield Display** — `alfheim_leyworks:decor_leafguard_shield_display` (wall).
- **Moonward Shield Display** — `alfheim_leyworks:decor_moonward_shield_display` (wall).
- **Sunblade Sword Display** — `alfheim_leyworks:decor_sunblade_sword_display` (wall).
- **Crossed Elven Blades** — `alfheim_leyworks:decor_crossed_elven_blades` (wall).

### Statue (6)

- **Elven Knight of the Watch** — `alfheim_leyworks:decor_elven_knight_watch` (tall).
- **Elven Knight of the Oath** — `alfheim_leyworks:decor_elven_knight_oath` (tall).
- **Mourning Elven Knight** — `alfheim_leyworks:decor_elven_knight_mourning` (tall).
- **Goddess of Renewal** — `alfheim_leyworks:decor_goddess_renewal` (tall).
- **Goddess of Moonlight** — `alfheim_leyworks:decor_goddess_moonlight` (tall).
- **Goddess of Remembrance** — `alfheim_leyworks:decor_goddess_remembrance` (tall).

### Ornament (6)

- **Ancestral Wall Relief** — `alfheim_leyworks:decor_ancestral_wall_relief` (wall).
- **Sunburst Wall Rosette** — `alfheim_leyworks:decor_sunburst_wall_rosette` (wall).
- **Moonwind Windchime** — `alfheim_leyworks:decor_moonwind_windchime` (wall).
- **Ceremonial Incense Stand** — `alfheim_leyworks:decor_ceremonial_incense_stand` (floor).
- **Elven Floor Harp** — `alfheim_leyworks:decor_elven_floor_harp` (tall).
- **Leafwoven Privacy Screen** — `alfheim_leyworks:decor_leafwoven_privacy_screen` (tall).

## Placement and purpose

These are purely decorative: fixed cabinet contents, ornamental weapons and
medals, and static furniture/sculpture. They have no inventory, interface, sitting
entity, combat effect, light effect, music or ticking behavior. The incense and
wind chime are visual ornaments. Goddess subjects are artistic motifs of Renewal,
Moonlight and Remembrance; they do not establish a named canonical pantheon.

Find them in the Building Blocks creative tab or through their 38 crafting recipes.
Recipes use Dreamwood or Livingrock, Elven Quartz, paired dyes, and wool, glass or a
gold nugget. This follows the project's ungated-decoration allowance. Each recipe
produces one complete object. Four chairs, two ottomans and two sofas provide the
seating family; cabinet silhouettes display relics, arms, crystals and court regalia.

Wall ornaments mount on a solid vertical face and recover as an item when their
backing is removed. Floor pieces require solid support. Tall pieces automatically
place their upper half; sofas automatically place their adjacent half to the right
of their facing. Both occupied cells must be available, and both sofa halves need
support. Breaking either half in survival recovers one complete item. Creative
removal of either half leaves no orphan or dropped item. All objects rotate to four
horizontal facings; collision follows the authored geometry. Mirroring a sofa
reverses its part ownership to preserve the assembly relationship.

## Review and validation

`/function alfheim_leyworks:elven_decor/review` builds a relative supported gallery
in a clear 30 by 18 area, with two blocks of object height. This is a deliberate
world-changing review command: use an empty test area. No automatic decoration
placements or structure/worldgen rules are introduced by this collection.

The deterministic generator calls the actual installed Continuity Works 0.3.2
`minecraft_recipe_generate` capability for all 38 recipes. Namespace-policy authoring
is followed by native Forge recipe and registry checks; the namespace gate alone
is not treated as registry proof. Twelve texture references resolve in installed
Botania or cached Minecraft assets. Source checks cover recipe uniqueness, complete
item models, model bounds and zero coplanar face overlap. The protected 39-file
terrain baseline and all 175 custom block-model face checks pass.

The isolated `validation-elven-decor-20261015` world checks actual BlockItem
placement and stack consumption, all 152 object/facing combinations, 14 assemblies,
13 wall mounts, blocked assembly rejection, survival and creative recovery, no
inventories/menu providers, and all 38 native recipes. A separate server restart
checks all 38 objects / 52 saved parts. Previous utility furnishings are tested on
the same installed jar: six storage profiles, five station transactions, six hopper
routes, and six saved inventory checks. Reports pin the exact installed jar hash:

- `tools/elven_decor_manifest.json` — inventory, source cuboids, recipes and CW gates.
- `tools/elven_decor_static_report.json` — independent static model/recipe checks.
- `tools/elven_decor_runtime_report.json` — native placement and restart evidence.
- `tools/district_furnishings_runtime_report.json` — existing utility regression.

Geometry contact sheets are `tools/elven_decor_interiors.png`,
`tools/elven_decor_honors.png` and `tools/elven_decor_statues.png`. They visualize
emitted model faces using flat colors, with glass outlined for inspection; they are
not game screenshots. Client texture, cutout-glass, item presentation and multiplayer
visual acceptance remain pending. Restart Minecraft fully to load the rebuilt mod.
No player saves were edited by the test harness.
