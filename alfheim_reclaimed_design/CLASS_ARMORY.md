# The Reclaimed Armory

**Design specification and implemented armory — 2026-09-04.** Requested scope: identify the installed Mine and Slash base classes; develop elven weapons from familiar vanilla forms, class armor, material progression, and deep profession integration. The design was approved first, then implemented through the reproducible `tools/gen_armory.py` pipeline.

**Delivered:** six elven combat traditions, each with three weapon families and an offhand, plus a four-piece armor collection. All use the pack's ten material grades. This is **18 weapon families, six offhand families, and 60 armor sets**: 480 registered equipment variants, 480 item textures, 120 worn armor textures, 48 Mine and Slash gear types, 480 auto-soul mappings and 480 Gear Crafting recipes. A dedicated Forge 47.4.10 server loaded every live Mine and Slash registry count and exited normally. `tools/armory_manifest.json` records the exact evidence.

Read alongside [the profession specification](PROFESSIONS_AND_MMO.md), the [complete weapon naming table](armory/WEAPON_FAMILIES.md), and the [machine-readable catalog](armory/equipment_catalog.json).

## 1. What the installed mod actually provides

The source of version-specific facts is `mods/Mine_and_Slash-1.20.1-6.4.7.jar`, particularly `data/mmorpg/mmorpg_spell_school/`. Its hash, class definitions, gear types, selected spell requirements, profession definitions, and recipe examples are captured in [the evidence snapshot](armory/installed_mns_evidence.json).

| Base class | Elven tradition | Native gameplay to build around | Intended party contribution |
|---|---|---|---|
| Warrior | **Thornwarden** | Melee attacks, Taunt, Charge, Whirlwind, defensive passives | Frontline, threat control, melee damage |
| Hunter | **Waywatcher** | Arrows, traps, movement, spirit wolf | Ranged damage, scouting, battlefield control |
| Sorcerer | **Leyweaver** | Fire and frost spells, golems, teleportation | Elemental damage and control |
| Shaman | **Rootspeaker** | Lightning, summoned totems, healing, thorn gardens | Area support, healing, elemental damage |
| Warlock | **Duskkeeper** | Curses, chaos/poison-themed spells, undead and spider summons | Attrition, debuffs, summon damage |
| Minstrel | **Dawnsinger** | Songs, Power Chord, healing, resource support | Party sustain and offensive support |

These are flavor titles for the existing classes, not six replacement classes. Ascendancies such as Guardian, Elementalist, and Necromancer remain a separate system. Hunter exists as both a base-school name and an ascendancy name; the catalog uses the base school.

The mod supports learning two base classes, subject to its normal rules. Equipment affinities are recommendations, not class locks. Spells still require the appropriate weapon and a Mine and Slash soul/stat profile. [Upstream casting guide](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/1.20-Forge/docs/newbie_guide/how_to_cast_spells.mdx).

## 2. Vanilla ancestry and actual behavior

The supported design vocabulary starts with **sword, axe, bow, crossbow, trident, and shield**. A knife, sabre, rapier, or falchion is a sword variation; a hatchet or crescent cleaver is an axe variation; a spear or glaive is a trident variation. Minecraft 1.20.1 has no vanilla mace, so none is assumed.

Casters need one explicit addition: Mine and Slash's **staff**. Its elven models borrow the shaft and fork of the vanilla trident, forming crystal spires, root crooks, and tuning forks. They remain mage weapons. Their appearance does not grant throwing, Loyalty, Riptide, or Channeling. Books become native tome offhands. A Hunter charm uses the native dodge totem category, not the vanilla Totem of Undying.

| Equipment | Integration contract |
|---|---|
| Sword families | Native `sword` base. Recognizable melee fallback for any class. Do not promise vanilla sweeping will match MMO area damage. |
| Axe families | The jar contains an `axe` weapon type, but no `axe` base-gear definition. Author an explicit base using the existing sword gear slot with axe weapon type, corrected tags and requirements; prove recognition before release. Do not map an axe to sword and call the behavior verified. |
| Bow/crossbow | Native bases and real projectile behavior. A different silhouette does not add repeat fire, multishot, or piercing. Those remain native enchants, skills, or budgeted MMO modifiers. |
| Trident families | Native `trident`; melee plus throw. A longer model does not automatically add reach. Test damage attribution and return/enchantment behavior. |
| Staff families | Native `staff`, including `mage_weapon`; spear-like appearance with staff handling. |
| Shield | Native shield, actual blocking. |
| Tome / dodge totem | Native passive offhand profiles. They do not block or enable main-hand spell requirements. The native dodge totem requires DEX; Rootspeaker uses an INT tome-shaped wooden tablet instead. |

Installed examples matter: Fire Ball, Lightning Spear, Acid Blast, and Power Chord require `MAGE_WEAPON`; Arrow Barrage requires `RANGED`; Gong Strike and Taunt require `MELEE_WEAPON`. Healing Aria is `ANY_WEAPON`. A martial sidearm therefore offers a real secondary playstyle, but does not cast all of its owner's spells.

Keep visible wording clear: **“Casting focus”**, **“Thrown spear”**, **“Blocking shield”**, and **“Passive ward.”** Reserve the same distinction in item icons and tooltips.

## 3. Weapon suites, simple to intricate

Every family has three silhouette stages: **simple, eras I–II; refined, III–VI; intricate, VII–X**. Material grade changes every era; silhouettes change only twice. Intricacy represents additional crafting work and build choices, not automatic extra attacks.

| Tradition | Primary progression | Alternative weapons | Offhand progression |
|---|---|---|---|
| Thornwarden | Leafknife → Boughblade → Crownleaf Falchion | Root Hatchet → Thorncleaver → Greatbole Crescent; Reed Spear → Branchguard Trident → Ninebough Glaive | Bark Buckler → Leafguard Shield → Hollow Court Aegis |
| Waywatcher | Twig Bow → Grove Recurve → Wildmarch Greatbow | Bough Crossbow → Thornstock Arbalest → Galeglass Windlass; Trailknife → Briar Sabre → Moonbranch Fang | Leaf Charm → Waywatcher Ward → Spiritwolf Crest |
| Leyweaver | Leybranch → Crystal Spire → Sixfold Conductor | Rune Knife → Ley Sabre → Starfall Falchion; Glass Spear → Prism Trident → Comet Fork | Bark Folio → Ley Atlas → Archive of Returning Stars |
| Rootspeaker | Rainbranch → Stormroot Crook → Worldroot Conductor | Tide Spear → Raincaller Trident → Stormtide Glaive; Grove Hatchet → Rootwarden Crescent → Tempest Boughcleaver | Root Tablet → Rainward Tablet → Memory of the First Grove |
| Duskkeeper | Hushbranch → Mourning Crook → Ancestor Reliquary | Dusk Knife → Grief Sabre → Last-Oath Falchion; Gloam Bow → Widow Recurve → Pale Procession Greatbow | Nameleaf Folio → Mourning Ledger → Book of Unforgotten Names |
| Dawnsinger | Tuning Branch → Chorus Fork → Greatbole Resonator | Danceknife → Ribbon Rapier → Dawncourt Estoc; Chord Crossbow → Harpstock Arbalest → Dawnchorus Ballista | Songleaf → Court Songbook → Canticle of the Reclaimed |

The catalog prepends the current material grade: **Verdant Grove Recurve**, **Elementium Crystal Spire**, **Rimebound Worldroot Conductor**, **Grave-Gilt Book of Unforgotten Names**. Names describe elven craft and memory rather than unrelated fantasy metals.

Three specialization choices per class shape targeted soul/infusion recipes:

| Tradition | Specialization A | Specialization B | Specialization C |
|---|---|---|---|
| Thornwarden | Bastion: shield and threat | Reclaimer: sword/axe damage | Tideguard: trident and repositioning |
| Waywatcher | Marksman: sustained bow damage | Trapper: crossbow and trap control | Packwarden: spirit wolf and mobility |
| Leyweaver | Ember: fire | Rime: frost | Confluence: mixed elements and golems |
| Rootspeaker | Storm: lightning | Grove: totems and thorns | Renewal: restoration |
| Duskkeeper | Hex: curse effect | Procession: summons | Wither: damage over time |
| Dawnsinger | Cantor: healing | Herald: offensive songs | Dancer: mobility and martial secondary |

These are recipe/affix preferences inside native classes, not additional talent trees. A specialist crafts a suitable profile; the player still spends their own skill and ascendancy points.

The combat learning curve has three parallel stages. A **simple** loadout teaches one dependable attack and a defensive/resource action. A **refined** loadout adds one deliberate interaction: Warrior threat plus positioning, Hunter trap plus shot, Sorcerer elemental control plus damage, Shaman totem plus restoration, Warlock curse plus summon, or Minstrel song plus healing. An **intricate** loadout coordinates those interactions with native support gems, specialization and a second class if chosen. Unlock skills at their actual native levels, independently of the frame's era; possessing an ornate weapon never grants an unlearned spell.

## 4. Ten grades using embedded materials

Era denotes **production access**, not a forced combat level. Suggested profession tiers below are pack recipe assignments within the mod's six existing tiers, not six newly defined levels. Exact MMO item level and rarity remain controlled by the soul and native requirements.

| Era | Grade | Required frame material | Additional material emphasis | Crafting complexity |
|---|---|---|---|---|
| I | Dreamwood | `botania:dreamwood_log` | Livingrock, petals; no imported metal | Basic frame after Pure Daisy; beginner soul route |
| II | Quickened | `alfheim:quickened_palebloom` | Quickened verdigris, sparkroot/duskbloom; Source Gem | Leaf-prepared frame plus Song preparation |
| III | Verdant | `alfheim:verdant_filament` | Living/charged fibre, sunbloom, cloudglass | Refined profile; existing three-step material chain |
| IV | Gatewrought | `alfheim:gatewrought_cord` | Silverthorn, grievebloom | Existing five-step material chain; traded components |
| V | Elementium | `alfheim:elementium_core` | Native Elementium, rimebloom | Existing seven-step chain; precise component shaping |
| VI | Wildmarch | `alfheim:wildmarch_sinew` | March hide, warded sinew | Existing nine-step chain; court craft and durable bindings |
| VII | Emberbound | `alfheim:emberbound_weave` | Emberwake, emberglass | Intricate profiles; existing eleven-step chain |
| VIII | Rimebound | `alfheim:rimebound_lattice` | Farbloom, tidewake | Existing thirteen-step chain; layered lattice |
| IX | Grave-Gilt | `alfheim:gravegilt_thread` | Grievebloom, duskglass | Existing fifteen-step chain; preserved memories |
| X | Crown | `alfheim:crown_filament` | Dawnglass, world-tree intermediates | Existing seventeen-step chain; masterwork finish |

An ore's manifest era is a design placement, not proof that its blocks are physically inaccessible earlier. Recipe inputs and completed material chains enforce production progression. Elementium gear requires the Era V core even if a player finds Elementium ore sooner.

**Early reachability:** Era I frames consume renewable dreamwood/livingrock/petals, not later fibre or ore. A usable, level-appropriate common soul must be obtainable without maps, rare loot, or an advanced station. Preserve the native starter route until the replacement is played. Era II may require the first Source preparation; Era I may not quietly require it.

Each era's material chain already contains the intended production depth. Add at most one frame assembly and one soul/infusion action; do not repeat the entire chain for every decorative fitting. Proposed base costs: one grade unit per weapon/offhand/helmet/boots, two per chest/leggings. This makes a four-piece suit six grade units. Verify late-era throughput before accepting those costs.

### Crystal attunements

| Existing crystal | Intended role | MMO interpretation |
|---|---|---|
| Emberglass | Fire, pressure | Fire damage preferences |
| Tidewake | Water, frost, restoration | Native water/cold profiles; healing only where explicitly chosen |
| Rootglass | Earth, living defense | Physical/defensive/totem preferences; no invented earth damage stat |
| Galeglass | Air, movement | Projectile/movement or lightning preferences; no invented air damage stat |
| Duskglass | Shadow, remembrance | Chaos, curses, summons; no new shadow resistance |
| Dawnglass | Light, renewal | Healing and songs; no invented holy damage school |

Crystals select an infusion/profile; they are not automatically native socket gems. Keep native gems, support gems, runes, and runewords distinct. A “Sixfold” staff does not receive six free sockets or six simultaneous damage conversions.

## 5. Class armor

All sets use the four vanilla slots. Shared elven design: tapered leaf plates, exposed wood grain, woven bindings, narrow crystal seams, and silhouettes that leave the face and ears readable. Era I looks repaired; III–VI looks cultivated; VII–X looks ritually grown. Armor colors communicate material and class through small accents rather than whole-body recolors.

| Collection | Native armor | Four pieces | Visual character | Stat direction |
|---|---|---|---|---|
| Boughguard | Plate | Leaf Helm, Bark Cuirass, Root Tassets, March Sabatons | Broad overlapping bark plates, thorn ridge, rootglass | STR, armor, melee, threat |
| Waywatcher | Leather | Trail Hood, Leaf Jerkin, Briar Leggings, Silent Boots | Layered leaves, fitted joints, galeglass clasp | DEX, dodge, projectiles, traps |
| Leyweaver | Cloth | Prism Circlet, Ley Robe, Starweave Leggings, Glassstep Boots | Forked crystal crown, fine ley-line embroidery | INT, magic shield, elemental spells, casting |
| Rootspeaker | Cloth | Antler Crown, Rain Mantle, Rootweave Leggings, Fenwalk Boots | Living roots, rain beads, small antler silhouette | INT, restoration, totems, lightning |
| Duskkeeper | Cloth | Mourning Veil, Memory Vestment, Graveweave Leggings, Hushstep Boots | Pale bark, named ribbons, recessed duskglass | INT, curses, summons, damage over time |
| Dawnsinger | Cloth | Laurel Circlet, Chorus Coat, Ribbon Leggings, Courtstep Boots | Open laurel, layered ribbons, dawn-colored seams | INT, healing, song duration/effect |

The armor categories describe Mine and Slash defenses, not necessarily vanilla material rendering. Native cloth uses magic shield, leather uses dodge, and plate uses armor. Attribute requirements are real; a Rootspeaker cannot obtain free plate defenses merely because roots look heavy.

### Proposed set identity, with mixed builds preserved

Era I–II pieces stand on their ordinary stats. From III, two eligible pieces can form a small specialization bonus; from VII, four can form a second bonus. Initial balance targets below are **increased-stat percentages**, not multiplicative “more” damage, and remain untested. Charge their value against the normal affix budget; do not add them above a full-strength soul for free.

| Set | Two pieces, initial target | Four pieces, initial target |
|---|---|---|
| Boughguard | +5% `melee_spell_dmg` | +8% `threat_generated` — tank specialization only |
| Waywatcher | +5% `projectile_damage` | +8% `trap_cdr` |
| Leyweaver | +5% `spell_elemental_damage` | +8% `cast_speed` |
| Rootspeaker | +5% `totem_spell_dmg` | +8% `totem_resto` |
| Duskkeeper | +5% `damage_to_cursed` | +8% `summon_damage` |
| Dawnsinger | +5% `increase_healing` | +8% `song_eff_dur_u_cast` |

These stat IDs exist in the installed data. Their existence does not prove a set-bonus implementation. No native set registry was found in the inspected datapack directories: implementation needs a server-side equipment modifier integration, or must ship only equivalent per-piece native infusions until that adapter is proven. The latter must be described as infusions, not an active set bonus.

Two plus two is an intentional hybrid option. Mixed grades qualify using the lowest grade among the pieces counted for that bonus. Each physical armor slot counts once; skins and vanity slots never count. Boughguard's damage specialization should substitute a budget-equivalent offensive four-piece choice rather than forcing extra threat on a damage player. Cap stacking through native stat rules and test equips, death, relogging, and swaps for lingering modifiers.

## 6. All fifteen dual-class pairings

These are suggested loadouts, not new classes. Weapon swaps remain necessary when a skill's requirement changes; dual-classing does not bypass it.

| Pair | Elven build | Equipment plan |
|---|---|---|
| Warrior + Hunter | Briar Outrider | Sword/shield and bow; Boughguard/Waywatcher mix |
| Warrior + Sorcerer | Spellthorn | Sword and staff; plate/cloth mix, meet both attributes |
| Warrior + Shaman | Stormwarden | Trident and staff; frontline with restoration |
| Warrior + Warlock | Oath-Reclaimer | Sword and staff; curses supporting melee |
| Warrior + Minstrel | Court Herald | Sword/shield and tuning focus; songs and frontline |
| Hunter + Sorcerer | Prism Stalker | Bow and staff; ranged skills and elemental control |
| Hunter + Shaman | Wildcall Ranger | Bow and root focus; traps, wolf, totems |
| Hunter + Warlock | Gloamstalker | Gloam bow and mourning focus; ranged attrition |
| Hunter + Minstrel | Wind Cantor | Harpstock crossbow and tuning focus; ranged support |
| Sorcerer + Shaman | Ley Tempest | One staff-compatible focus; elemental/totem profiles |
| Sorcerer + Warlock | Eclipse Weaver | One focus; elemental spells, curses, summons |
| Sorcerer + Minstrel | Star Cantor | Focus/tome; spell damage and healing |
| Shaman + Warlock | Ancestor Gardener | Root or mourning focus; summoned support and curses |
| Shaman + Minstrel | Grove Chorus | Focus/tome; restoration and songs |
| Warlock + Minstrel | Elegist | Mourning/tuning focus; remembrance, debuffs, sustain |

Do not require a tank/healer party to complete the campaign. Party specialization should improve coordination and efficiency; solo players retain a practical native class route and can commission equipment from others without leveling every profession themselves.

## 7. MMO power and ownership

Separate four things: **material grade** unlocks the frame; **soul level** sets MMO scaling; **rarity** sets native power/affix structure; **specialization** targets a build. An Era X frame must not turn a level-one soul into a level-100 item. A rarity upgrade must not skip the material chain. Preserve native level and attribute requirements on trade.

Targeted crafts provide reliable build foundations. Expeditions remain attractive for stronger souls, currencies, runes, gems, and rare rewards. Late materials buy precise frames and bounded specialization; they do not grant guaranteed maximum rarity or every best modifier.

A material upgrade must retain valid soul data, rolls, sockets, quality, and other applicable progression without duplication. Do not implement it as a recipe with a fresh output stack that silently deletes NBT. Prove a native transfer route first; otherwise design a dedicated validated transfer operation. No guessed NBT keys appear in this catalog.

Frames, components, and consumables are tradable by default. Retain native restrictions on individual items. No new auction house, global currency, soulbinding rule, or mail system is assumed. Those would be separate features.

## 8. Delivery and acceptance

1. Prove one Dreamwood sword, bow, staff, and each native armor family with genuine souls; include an axe recognition probe and an offhand probe.
2. Prove Era I–III production and professions end to end, including the class that cannot yet use its signature later-level spell.
3. Verify all six class primary weapons, dual-class swaps, ranged/trident damage attribution, crafting and salvage economics.
4. Build the remaining form stages and grades from the same definitions; validate native names and IDs against the installed version.
5. Add optional set mechanics only after stat application/removal is reliable. Validate in multiplayer and singleplayer before expansion.

Present acceptance is **design drafted; catalog reference checks passed**. This is not runtime-validated gear. Reproduce the evidence and 480-item catalog with `python tools/build_armory_design.py`; it writes only this design's `armory/` directory.
