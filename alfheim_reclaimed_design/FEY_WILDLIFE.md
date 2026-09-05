# Fey wildlife, hostile elves and field supplies

Updated 2026-09-05. Scope: the 18 EntityJS creatures in `tools/fey_manifest.json`.
The separate zombie work is parked at the user's request. The Hollow Court's original
wood-elf entity and reserved skins are unchanged.

## The three elf variants

| Variant | Habitat | Combat identity | Player-kill drops |
|---|---|---|---|
| Wild elf | Ashen Grove, Silverbark Wood, Sundered Highlands | Swift melee fighter; 20 health, 3 base damage, movement speed 0.30 | 1–3 barkcloth scraps guaranteed; 35% chance of 1–2 dreamwood twigs |
| Savage elf | Infested Warren, Decayed Mire, Hollow Marches | Leaping bruiser; 28 health, 5 base damage, 2 armor, stronger knockback | One bone fetish guaranteed; 50% chance of 1–2 leather |
| Demonic elf | Scorchfell, Void Verge, Starved Reach | Fire-immune fighter; 36 health, 7 base damage, 4 armor, knockback resistance | One scorched sigil guaranteed; 50% chance of 1–2 charcoal |

These are separate creature variants, not an elf reproduction mechanic. Combat figures are
registration baselines; Mine and Slash may adjust encounters. No fire-spreading attack is added.
All three attack survival players, despawn in Peaceful and stay out of the protected spawn square.

## Wildlife

- Brown whitetail does and antlered bucks inhabit forests and fields. They flee players.
- Celestial does and bucks use Minecraft's End Portal render type. They spawn alone at weight 1
  with an additional 1-in-32 placement roll. They drop a celestial mote, never venison or hide.
- Moss, azure and amber frogs each have small and large forms. Bog and mossback toads have
  0.9 × 0.9 collision dimensions, matching a pig, with corresponding model scaling.
- Abyssal Watchers, Mire Tentacles and Drowned Maws use water navigation and swimming control.
  Their placement requires water above and below, and they target players who are in water.

The manifest owns all 53 species/habitat assignments. Wild animals do not currently breed;
slaughter does not masquerade as the native Husbandry profession's breeding XP.

## Drops that have somewhere to go

13 registered items, 18 loot tables and 14 recipes. Exact rates and counts are generated into
`tools/fey_drops_manifest.json` and the in-game **The Fey Bestiary** chapter.

| Material | Use |
|---|---|
| Raw venison | Roast at a campfire, furnace or smoker; roasted venison supplies 8 hunger and 12.8 saturation |
| Whitetail hide | One hide and one dreamwood twig make one leather |
| Hart antler | Three bone meal; only bucks drop antlers, at 50% on player kills |
| Celestial mote | Mana Pool: two Fey Dust for 500 mana |
| Frog gel | Two gel make one slimeball; large frogs yield more than small frogs |
| Toad gland | Mana Pool: two slimeballs for 500 mana |
| Abyssal eye | Mana Pool: two glow ink sacs for 1,000 mana |
| Mire tendril | Mana Pool: three string for 200 mana |
| Maw fang | Four bone meal |
| Barkcloth scraps | Three scraps make two string |
| Savage bone fetish | Mana Pool: four bone meal for 300 mana |
| Scorched elven sigil | Mana Pool: one Fey Dust for 1,500 mana |

Trophy quantities are bounded and receive no extra Looting roll. Elf trophies, celestial motes,
antlers, toad glands, abyssal eyes and maw fangs require a player kill. Existing global loot
modifiers remain active: the runtime loot evaluation also observed Knightlib's small and great
essences on elves. These are optional supply routes, never replacements for an era rune,
profession unlock, class gate, MMO currency or starter weapon. No custom XP is awarded.

## Source and regeneration

- `tools/gen_fey_wildlife.py`: creature models, animations, habitats, roster and generation entrypoint.
- `tools/fey_drops.py`: authoritative drop quantities, recipes, item declarations and bestiary prose.
- `kubejs/startup_scripts/08_fey_wildlife.js`: entity registration and spawn predicates.
- `kubejs/server_scripts/17_fey_wildlife.js`: goals and targets.
- Generated item declarations: `kubejs/startup_scripts/19_fey_drops.js`.
- Generated optional reference chapter: `config/ftbquests/quests/chapters/ref_fey_wildlife.snbt`.

Run `python tools/gen_fey_wildlife.py`, then `check_fey_wildlife.py` and `check_fey_drops.py`.
The bestiary uses the existing Compendium group and does not rewrite campaign chapters or groups.
Inventory items reuse installed vanilla art; the entity material atlas is the preserved built-in
ImageGen output at `kubejs/assets/alfheim/textures/entity/fey_materials.png`. UV sampling now scales
with model-face dimensions instead of stretching a whole square swatch over every limb.

EntityJS 0.7.3 is installed alongside the existing KubeJS and GeckoLib dependencies. Third-party
jars are unmodified. A full client restart is required after these registrations change.

## Acceptance

Static checks pass: creature/source synchronization, bounded loot and processing coverage,
script syntax, dependency ranges and world-generation feature ordering.

Acceptance: **runtime validated for registration, habitats and loot**. Evidence:
`server/fey-console-20260905-064250.log`, clean exit 0; no KubeJS startup/server errors.
All 18 entities instantiate with the expected health and dimensions. Minecraft's own codec
confirms all 53 species/habitat assignments in the final Forge spawn tables. All 13 items and
14 recipes resolve. The engine evaluated 128 player-kill and 128 non-player-kill loot rolls per
species (4,608 evaluations), with zero wrong quantities, missing outputs or violated player-kill
guards. Other mods' global loot additions are recorded separately and preserved.

Regeneration left all 3,551 checked shipping files byte-identical. These checks do not establish
natural encounter frequency or observe a player making the recipes. The optional bestiary is
instructional reference, not proof of completing a recipe.

Next client acceptance: inspect the three elves' movement and attack styles, the celestial
portal effect, material density on moving models, food consumption, Mana Pool processing and
natural encounter frequency. The headless server cannot verify client rendering or combat feel.
