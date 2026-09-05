# The Reclamation Trades

**Design specification with an implemented armory bridge — 2026-09-04.** Companion to [The Reclaimed Armory](CLASS_ARMORY.md). The full nine-trade production and multiplayer economy remains the governing specification. Its armory core is installed: 480 native Gear Crafting recipes consume the appropriate embedded frame material, tiered Mine and Slash mining material and salvage stone; era III+ pieces also consume their class crystal. Custom bloom mining XP, food, alchemy and broader Infusing extensions remain design work and are not claimed as installed.

The intended loop is **gather → prepare through Leaf and Song → craft through a native profession → equip and provision → explore → salvage → refine**. A combat player needs a functioning homeland; a crafter has useful customers and can progress without personally mastering every combat class.

## 1. Verified baseline and integration gaps

The installed Mine and Slash 6.4.7 jar defines **nine professions**, with separate combat and profession progression. Its data includes six gathering-material tiers (`TIER0`–`TIER5`) and **799 profession recipes**: 150 Gear Crafting, 145 Enchanting/Infusing, 216 Cooking, and 288 Alchemy. This is a shipped-data count, not proof that every recipe is reachable in this pack.

| Native ID | Player-facing trade | Elven title | Current evidence |
|---|---|---|---|
| `mining` | Mining | Bloom Delver | Explicit vanilla ore block-tag XP sources; six material-drop tiers |
| `farming` | Farming | Grove Tender | Explicit crop-item/growth requirements; six material-drop tiers |
| `fishing` | Fishing | Tidekeeper | Six material-drop tiers; event behavior must be checked in-game |
| `husbandry` | Animal Breeding | Wildward | Six meat-material tiers; native animal-breeding profession |
| `salvaging` | Salvaging | Memory Reclaimer | Native profession and salvage station; not an ordinary crafting recipe family |
| `gear_crafting` | Gear Crafting | Armsinger | Native souls and sharpening-stone recipes |
| `enchanting` | Infusing / Enchanting | Runeweaver | Native infusion recipes; internal ID remains `enchanting` |
| `cooking` | Cooking | Hearthkeeper | Native MMO food recipes |
| `alchemy` | Alchemy | Dewbrewer | Native buff and restoration recipes |

Use the mod's native stations for native crafting XP. A recipe run in Botania or Ars Nouveau does not inherently award Mine and Slash profession XP. The upstream profession guide describes that station-specific distinction and calls the enchanting trade **Infusing**. [Profession guide](https://moddedmc.wiki/en/project/mine-and-slash/latest/docs/professions/professions_intro).

There is no native Forestry, Tailoring, Jewelcrafting, or standalone Weaponsmith profession in the inspected profession registry. We can offer those **as specializations within the nine trades**, using patterns and commissions, without inventing native XP bars. MineColonies citizen jobs remain their own worker progression and never stand in for player Mine and Slash levels.

Observed gaps:

- The twelve custom blooms are tagged `forge:ores` and `alfheim:blooms`. Native mining XP explicitly names individual vanilla ore tags; no custom bloom entry is present. Default fallback/event behavior still needs runtime inspection. Do not report custom-ore XP as integrated merely because the blocks can be mined.
- The current `14_mmo_bridge.js` exchanges materials and currencies, but supplies neither a full class armory nor profession event/recipe integration.
- The installed Compatibility addon is present, while the inspected validation world's preset is `ORIGINAL_MODE`. Its configuration enforces weapon requirements and sets vanilla-to-MMO weapon damage conversion to zero. Installed Ars Nouveau and Iron's Spells therefore cannot simply be assumed to share the combat system.
- Existing bridge comments disagree with several inputs: galeglass says six shards but consumes one, rootglass says eight but consumes one, and dawnglass says eight but lists four. Several Ars exchanges put a copy on the reagent slot **and** extra copies on pedestals. Cost calculations must use actual inputs and station semantics, not comments. These are design audit findings; no unrelated recipes were changed.

Evidence is recorded in [installed_mns_evidence.json](armory/installed_mns_evidence.json). Material identities come from the existing bloom, crystal, grove, and item manifests and the exported runtime item registry.

## 2. Who produces what

| Trade | Gathering/preparation in this pack | Native profession output | Customers and continuing demand |
|---|---|---|---|
| Bloom Delver | Twelve blooms, natural geodes, appropriately tiered mining supplies | Native mining materials; raw inputs for Leaf processing | Armsingers and Runeweavers; continuous soul, infusion, and sharpening demand |
| Grove Tender | Mature food crops, renewable petal gardens, cultivated grove supplies | Native farming materials plus existing harvested items | Dewbrewers, Hearthkeepers, fibre/frame preparation |
| Tidekeeper | Player fishing in home waters and expedition waters | Native fishing materials and ordinary catch | Meals, restorative preparations; no mandatory rare fish for starter gear |
| Wildward | Player breeding of allowed animals; wool/hide supply chains | Native husbandry materials | Meals and armor bindings; breeding XP is distinct from slaughter/loot |
| Memory Reclaimer | Unwanted genuine MMO drops brought to salvage station | Native stones/materials from valid salvage | Every crafting profession; gear recycling without free rarity escalation |
| Armsinger | Spine-prepared frame materials plus native mining/salvage supplies | Targeted souls and sharpening stones; validated application to custom frames | All six combat traditions; reliable build foundations and upgrades |
| Runeweaver | Prepared crystal attunements plus native mining/salvage supplies | Native gear infusions; compatible socket/rune services | Build specialization, retuning, hybrid equipment |
| Hearthkeeper | Farmer's Delight/Miners Delight preparation plus native farming/fishing/husbandry supplies | Native MMO food families | Solo travel, party expeditions, gathering preparation |
| Dewbrewer | Botanical Brewery/Ars preparations plus native farming/salvage supplies | Native MMO restoration and buff potions | Field recovery and planned encounters |

Class and profession are independent. A Dawnsinger can forge plate for a Thornwarden; a Hunter can brew for a Warlock. No class-exclusive recipe knowledge and no extra profession tax for a dual-class character.

## 3. Craft specialties without parallel XP systems

| Specialty | Parent trade | Work and identity |
|---|---|---|
| Leafsmith | Gear Crafting | Swords, axes, tridents, plate-like bark frames |
| Bowyer | Gear Crafting | Bows/crossbows; Dreamwood shaping and Wildmarch bindings |
| Vestment Weaver | Gear Crafting | Cloth/leather-looking frames from the existing fibre/sinew ladder |
| Focus Carver | Gear Crafting | Staff bodies, tome shells, wards; separate casting and throwing designs |
| Crystal Lapidary | Infusing | Six crystal preparations that target existing MMO stats |
| Grove Steward | Farming | Forest/petal work and horticultural commissions; new harvest-event support only after verification |
| Expedition Provisioner | Cooking + Alchemy | Class-useful meals and restorative batches, each credited to its own native trade |
| Relic Conservator | Salvaging + Infusing | Salvage service and re-attunement; no duplication of the source soul |

A specialty is an optional recipe collection and visual identity, not a permanent mutually exclusive choice. Unlock patterns through the material eras and small work orders. Avoid a second reputation currency unless a later server design specifically requires one. All essential services remain obtainable solo or by trade.

## 4. Gatherer integration, explicitly mapped

### Mining

Use dedicated, non-overlapping custom bloom tags in the native mining definition. Keep the existing Midgard vanilla sources. Never add all blooms to `minecraft:iron_ores` just to obtain XP; that would misclassify recipes and native profession tiers.

Proposed assignment follows the pack's material access, not the vanilla metal a bloom eventually renders:

| Bloom | Manifest era | Proposed profession tier | Starting XP per eligible natural block |
|---|---:|---:|---:|
| Cinderbloom | I | 0 | 15 |
| Verdigris | I | 0 | 15 |
| Palebloom | I | 0 | 20 |
| Sparkroot | II | 0 | 20 |
| Duskbloom | II | 0 | 25 |
| Sunbloom | III | 1 | 35 |
| Cloudglass | III | 1 | 35 |
| Silverthorn | IV | 1 | 40 |
| Grievebloom | IV | 1 | 40 |
| Rimebloom | V | 2 | 55 |
| Emberwake | VII | 3 | 75 |
| Farbloom | VIII | 4 | 100 |

These are tuning proposals. Validate native level requirements and XP curves before committing them. The Era X crafting tier does not require inventing a thirteenth ore; native high-tier mining materials, existing blooms, and the Crown chain provide its inputs. No crafting route should require a gathering material whose acquisition is itself locked behind that route.

Natural crystal clusters can contribute to Mining after harvest behavior is verified. Keep six equal-value attunements: choose a provisional 10 XP for an eligible mature cluster; ordinary decorative blocks and budding blocks grant none. Re-grown clusters are a renewable resource and need an explicitly bounded XP policy rather than pretending to be a finite ore vein.

Anti-loop contract: one eligible natural block harvest, one base XP award; Fortune affects resources, not XP multiplication. Silk Touch awards no custom harvest XP; re-placing its block must not create a new eligible natural node. Player-placed ore, Orechid conversion, dimensional mining output, artificial growth, and quarries must not be silently treated as fresh exploration. Reliable origin tracking/event filtering is an integration requirement, not a capability the current JSON proves. Until that is reliable, enable only verified harvest sources and use finite work orders for unverified resource types.

### Farming and forestry

Keep native mature-crop rules. Map each additional crop to exactly one harvest route and validate right-click harvest from The Harvest separately from breaking the crop. Breaking an immature crop, taking from a chest, and replanting grant no harvest XP. A harvest event must not also receive a second scripted award for the same output.

Petals, Dreamwood, archwood, Emberbark, Hushbark, and Gloambark have real production value for frames and alchemy. Forestry starts as a Grove Steward commission specialization. The native farming definition does not prove it can treat a log break as a mature crop: do not fake that mapping. Only add personal forestry XP through a verified player-action hook with renewable-growth and placed-log protection. Retain existing leaf loot rather than replacing saplings or petals with profession currency.

### Fishing and husbandry

Native player fishing feeds the fishing trade. Use water-region flavor and food recipes to connect Tidewake waters to provisioners; avoid six nearly identical fish currencies. Automated fishers and colony workers supply items without granting the owner fishing XP. Validate catches from modded systems rather than assuming they emit the vanilla player event.

Native animal breeding feeds husbandry. Allow verified modded breedable animals deliberately. Breeding, shearing, and killing are distinct actions; shearing may supply wool without being an XP event, and killing animals must not be relabeled breeding. A living-material substitute for a binding is acceptable when it uses an era-equivalent spine product, so a particular animal species never becomes a hard class lock.

## 5. Production and XP architecture

### One transaction owns each reward

**Spine preparation:** Botania/MythicBotany provide awakened materials; Ars Nouveau provides source preparation and complex finishing. These operations consume power and produce components. They do not automatically award native crafting XP.

**Native profession finalization:** author recipes in `data/mmorpg/mmorpg_profession_recipe/` and craft them in their native stations. Installed recipes expose `profession`, `tier`, `exp`, `mats`, `result`, `result_num`, `set_tier_nbt`, and `requires_pinnacle_unlock`. This gives a concrete integration surface for prepared Alfheim components plus native profession supplies. Confirm reload behavior and custom inputs in a one-recipe prototype before generating families.

**Frame plus soul:** custom frame identity comes from the pack; the native Gear Crafting profession creates the corresponding soul. Native item recognition and the soul-application process must be proved for sword, bow, staff, each armor family, and offhands. Creating an ordinary item at an Ars station is not sufficient MMO integration.

**Infusing:** crystal preparation selects a native infusion recipe. Native profession tier/consumable data remains native. Do not use `set_tier_nbt` as a substitute for forging a complete arbitrary soul or assume its tier means campaign era.

**Commission rewards:** initial work orders grant patterns, supplies, or one-time quest rewards. They do not duplicate the native XP already earned crafting the submitted item. If cross-station personal XP is later added, designate one owner for that award and require a verified server-side hook.

### Era-to-profession recipe bands

| Era band | Proposed native recipe tier | Production requirement |
|---|---:|---|
| I–II | 0 | Beginner frames and provisions; renewable home materials |
| III–IV | 1 | Verdant/Gatewrought material chains |
| V–VI | 2 | Elementium/Wildmarch chains |
| VII | 3 | Emberbound chain |
| VIII–IX | 4 | Rimebound/Grave-Gilt chains |
| X | 5 | Crown chain and existing native pinnacle restrictions where applicable |

Profession level governs the artisan's mastery. Campaign materials govern what they can manufacture. Combat level governs use of a soul. These axes cooperate without forcing a combat level requirement on a spine milestone. A skilled crafter can buy missing ingredients; an adventurer can buy finished work.

Do not equate profession tier with rarity. Preserve native rarity and pinnacle conditions on the recipe families copied. A common high-tier provision and a rare low-tier item can both have legitimate uses.

### Concrete prototype recipes

The following are specifications, not generated game JSON. Quantities are starting costs. A “prepared component” below is a proposed functional intermediate produced from existing materials, not a new mined material set.

| Recipe | Preparation and final transaction | Native reward |
|---|---|---|
| Dreamwood beginner frame | Pure Daisy supplies Dreamwood/livingrock; frame assembly uses one log, two livingrock and two petals | Sword, bow or staff frame; no crafting XP outside its owning station |
| Common weapon soul | Gear station: three tier-0 native mining materials, one tier-0 salvage stone, one Leaf-prepared component | One native common weapon-family soul, level/tier restrictions retained; target 100 native recipe XP |
| Verdant focus | One Verdant Filament plus Dreamwood, with an Ars-prepared crystal fitting; one frame assembly | Refined staff-compatible frame; attach a legal soul separately |
| Rootglass infusion | Ars preparation consumes two Rootglass shards plus one Source Gem; native Infusing station consumes the prepared result plus native tier-matched supplies | One suitable native defense/totem infusion; target 100 native recipe XP |
| Expedition meal | Farmer's Delight prepares the dish; a Leaf-prepared garnish and native cooking materials finish it at the MMO Cooking station | One appropriate native MMO food, normal food-family restrictions; target 100 native recipe XP |
| Tidewake restorative | Botanical preparation consumes two Tidewake shards and botanical ingredients; MMO Alchemy station adds farming/salvage supplies | Native restorative with normal use rules; target 100 native recipe XP |

The beginner soul recipe may not be accepted until its mining and salvage inputs have a non-circular starter supply. Preserve existing starter supplies; provide a small, one-time training work order if needed. No map key, boss kill, advanced rune, or rare drop is allowed to be the only way to activate the first weapon.

The frame/soul distinction is for the design team. The player should see one concise guide entry showing the frame recipe, the correct native soul family, and the application step. Do not present empty frames as finished expedition gear.

## 6. Other installed systems

| Installed system | Intended integration | Boundary to prove |
|---|---|---|
| Botania / MythicBotany | Material preparation, crystal reagents, grade chains, mana cost | Botanically generated resources are renewable production, not automatically mining XP |
| Ars Nouveau | Source preparation, imbuement, apparatus finishing, utility and magical automation | Apparatus output does not imply native profession XP; combat/healing conversion must be tested separately |
| Farmer's Delight / Miners Delight | Real dishes and prepared ingredients feed native cooking recipes | Normal hunger effects can remain; MMO buffs must come from recognized native consumables |
| The Harvest | Convenient player crop harvest | Verify maturity, player attribution, and duplicate event handling |
| MineColonies | Workers cultivate, mine, cook, transport and make authorized intermediates; artisan shops support commissions | Citizen skill/research remains local to the colony. Workers confer no player combat/profession XP by ownership |
| Create and addons | Batch preparation and transport of already spine-gated materials | Automated throughput provides goods; no AFK personal profession XP. No new engine-based backbone is introduced |
| Nature's Aura | Ecological treatment and advanced preparation | Aura economy supports existing era recipes, not a duplicate MMO stat system |
| Occultism / Occult Engineering | Spirit processing, logistics and late remembrance materials | Miner/crusher output has explicit generated-resource origin; no exploration XP attribution |
| Feywild | Court preparation and specialty ingredients around Wildmarch | Court progression and player profession progression remain distinct |
| Iron's Spells | Selected alchemical inputs, utility, and candidate compatible combat paths | Its mana, healing and damage are not automatically the Mine and Slash versions |
| FTB Quests / Teams / Chunks | Lessons, collaborative progression, protected workshops | Team quest completion does not award every member personal harvest/crafting XP |
| Quest Giver | In-world trade introductions and work orders | Narrative orders first; a transactional player commission board would need a separate implementation |
| Knight Quest / existing combat equipment | Additional cosmetic/form references and compatible gear candidates | Original stats or visuals do not establish MMO power or class compatibility |

The player-operated native final craft can award XP even when inputs were bought or automated. This keeps automation and trade worthwhile. The distinction is who performs the profession action, not whether every ingredient was hand-gathered by that player.

### Profession equipment

Give each trade an elven tool identity using familiar items: Bloom Delver pickaxe, Grove Tender hoe, Tidekeeper rod, forestry axe, and an optional shepherd's utility tool. Tool grade follows the same material ladder and affects ordinary harvesting/durability only where the implemented tool supports it. A pickaxe is not a universal class weapon.

Trade aprons, hoods and badges are useful cosmetic sets. Any gathering-yield or XP bonus would require its own capped, verified adapter; do not invent native “Mining Power” or “Crafting Luck” stats. Keep combat armor and profession utility choices legible, and avoid requiring constant outfit swaps for routine crafting.

## 7. Trade, salvage and inflation controls

Use existing native supplies and currency. Gatherers sell resources, specialists sell preparation, Armsingers sell frames/souls, Runeweavers sell infusions, provisioners sell consumables, and adventurers sell salvage and expedition rewards. Every service consumes something other than time alone.

Recommended policies:

- Finished gear keeps its native level/attribute requirements when traded. The crafter's level does not become the buyer's level.
- Frame assembly, soul creation, and infusion each have one canonical production route. Refitting an existing item is a distinct, audited transfer operation, not a duplicate new-item recipe.
- Salvage preserves native behavior initially. If custom frame recovery is added, target at most 25% of the frame's material-equivalent cost on average, with no return of its unique finalization reagent. Fractional costs use scraps or lower intermediates, never a guaranteed full top-tier core back from a one-core recipe.
- Never refund a soul and also retain an equipped copy. Extractors, cleaners, salvagers, upgrades, death and disconnect paths are a single transaction audit surface.
- Rerolls and retuning consume native currency plus appropriate preparations. No reusable item may produce an unlimited currency or XP return.
- Basic crystals remain useful at endgame through consumable preparation. High-tier frames alone should not invalidate early gathering professions.
- Native food categories and potion rules control stacking. New preparation recipes must not create a second independent version of the same buff that stacks for free.

The existing reciprocal currency bridge needs a full input ledger before expansion. For example, Emberglass → chaos orb → Emberglass must be evaluated using all consumed copies, output counts, and station costs. Mana/source being renewable is not a sufficient safeguard against a net-positive material cycle. Every closed conversion cycle must have no positive material/currency profit; every repeatable salvage/craft cycle must also be checked for unbounded profession XP.

The inspected validation config already sets combat-to-profession rested-XP generation to **0.25** and profession-to-combat to **0.10**. Retain and measure that native connection first; do not add a second scripted rested-XP bridge. These are observed values from that world's config, not a guarantee that every save shares them.

## 8. Versatile combat integration

Keep Mine and Slash as the authority for gear power, classes and expedition difficulty. The installed Compatibility addon gives a candidate **Compatible mode** for later Ars/Iron's offensive spell integration while retaining the MMO damage framework. Upstream distinguishes that mode from Lite mode, which changes scaling and adds MMO damage on top of vanilla behavior. [Compatibility documentation](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/1.20-Forge/docs/modpack_dev/compatibility_addon.mdx).

Preferred full-integration target: test Compatible mode in an isolated validation world after the native armory works. Do not change production presets as part of a design document. Verify damage attribution, resource cost, cast rate, summons, multiple hits, environmental damage, PvP and low/high-level targets. The setting is not evidence that foreign healing, buffs, spell cooldowns, or profession XP are integrated.

Tune supported foreign attacks against comparable native damage per cast and sustained damage per second at the same soul level, including mana/source limits. Keep unsupported routes identified as utility until they pass. Do not grant every vanilla item `MAGE_WEAPON` or globally disable weapon requirements to hide incompatible equipment.

Party healing must respect teams, range and valid targets. Summons must not inherit duplicate damage scaling. Automated turrets, cannons or fake-player attacks cannot become a free profession/combat progression source without a deliberate design and attribution policy.

## 9. Implementation sequence and measurable acceptance

| Slice | Deliverable | Acceptance evidence |
|---|---|---|
| A — native foundation | One sword, bow, staff, armor-family sample, and correct soul recognition | Six classes can use their intended primary; wrong-weapon errors remain correct; no starter material cycle |
| B — gathering | Bloom mining entries, mature crops, fishing and breeding checks | Exact XP/drop count per event; natural versus placed/generated resources; Fortune/Silk Touch; no double award |
| C — production | One prepared-input recipe in each of four native crafting professions; native salvage | Inputs consumed once, proper output tier, XP awarded once, non-circular beginner access |
| D — economy | Era I–III equipment, meals, infusions and upgrade transfer | Singleplayer loop plus two-player trade; native level restrictions, no profitable conversion/salvage cycle |
| E — automation | Colony, Create, Ars and Occultism input supply | Materials produced correctly; no owner XP from unattended workers; player finishing still grants valid XP |
| F — full armory | Remaining grades, specialties, guides and optional sets | Six roles and all fifteen dual-class pairings; modifier cleanup; viable solo progression |
| G — compatible magic | Isolated addon-mode validation and selected foreign spells | Comparable damage/resource budgets at low/mid/high levels; no duplicate scaling; explicit healing results |

Before accepting numerical tuning, record time to activate the first weapon, time to a complete first armor set, profession XP per minute for representative actions, material cost per useful item, salvage recovery, and consumables used per expedition. Provisional targets: a first class-appropriate weapon within 15–25 minutes of normal play; first functional set within 45–75 minutes; a gatherer/crafter should be able to make useful saleable output in their first session. These are playtest goals, not measured results.

Verify offline/relog state, server restart, death, full inventory, failed craft, recipe reload and concurrent players. Runtime findings decide the next slice; static JSON validity alone cannot pass the economy or gameplay gates.

**Current acceptance:** design drafted. Installed classes, native profession IDs, recipe counts, selected gear/stat definitions, and existing frame materials have been inspected. Custom events, item activation, profession balance, player commissions and compatible magic remain implementation and gameplay-validation work, exactly as requested for design-first delivery.
