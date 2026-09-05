# Process Index — every crafting method in the pack

**Status:** reference record. Extracted 2026-09-02 from 95 jars; **11 have since been removed**
(B-32, B-33). Rows for purged mods are struck through below — the counts in §1 and the ~95-station
figure predate the purge.
**Purpose:** the tier ladder (`CAMPAIGN_ERAS.md` §1b) needs up to **17 distinct processes** in one
Era X chain. This is the menu to draw from.

**171 distinct recipe types across 24 namespaces at time of extraction. Roughly 95 were
player-operated stations; the purge removed 14 types / 960 recipes, leaving ~81.**

The constraint is still not scarcity. Era X needs 17 distinct steps and the pack offers ~81 — this
remains a **curation** problem, not an availability one.

**Biggest single loss:** `bclib:alloying`, the Alloying Furnace. It was the one clean two-input metal
fusion station, and §2–§5 have no direct replacement. Nearest substitutes are `create:mixing` (heated,
multi-input) and `botania:terra_plate`. Worth noting when specing the metal tiers.

---

## 1. The step curve it has to serve

From `CAMPAIGN_ERAS.md` §1b: steps = **2n − 3**.

| Era | New steps | Transitive total |
|---:|---:|---:|
| 3 | 3 | 3 |
| 4 | 5 | 8 |
| 5 | 7 | 15 |
| 6 | 9 | 24 |
| 7 | 11 | 35 |
| 8 | 13 | 48 |
| 9 | 15 | 63 |
| 10 | 17 | **80** |

Each era's chain consumes the previous era's output, so depth accumulates. ~80 steps transitively for
the Era X tier material, and therefore roughly **80 intermediate items** to author.

## 2. Spine of Leaf — Botania / MythicBotany

The material spine. 11 stations.

| Process type | Station | Existing recipes | Ladder use |
|---|---|---:|---|
| `botania:pure_daisy` | Pure Daisy | 8 | Era I–II. Transmutation in-world. |
| `botania:petal_apothecary` | Petal Apothecary | 49 | Early. Flower creation. |
| `botania:mana_infusion` | Mana Pool | 140 | **Workhorse.** Any era. |
| `botania:runic_altar` | Runic Altar | 25 | Mid. Rune-gated. |
| `botania:terra_plate` | Terrestrial Agglomeration Plate | 1 | Late. Terrasteel. |
| `botania:elven_trade` | **Alfheim Portal** | 15 | **The gate.** See §7. |
| `botania:brew` | Botanical Brewery | 20 | Consumables, additives. |
| `botania:orechid` / `orechid_ignem` | Orechid | 19 | Ore conversion. |
| `botania:marimorphosis` | Marimorphosis | 8 | Stone variety. |
| `mythicbotany:infuser` | Mana Infuser | 4 | Late. Alfsteel tier. |
| `mythicbotany:rune_ritual` | Rune Ritual | 3 | **Era capstones.** The nine runes. |

Botania also ships ~25 single-purpose utility types (`mana_gun_add_clip`, `cosmetic_attach`,
`terra_pick_tipping`…). Not ladder material — listed in §9 for completeness.

## 3. Spine of Song — Ars Nouveau

The process spine. 7 stations.

| Process type | Station | Existing | Ladder use |
|---|---|---:|---|
| `ars_nouveau:imbuement` | Imbuement Chamber | 13 | Early Song. Entry tier. |
| `ars_nouveau:enchanting_apparatus` | Enchanting Apparatus | 75 | **Workhorse.** Mid–late. |
| `ars_nouveau:crush` | Crush | 26 | Reduction step. |
| `ars_nouveau:glyph` | Glyph Press | 81 | Knowledge gating. |
| `ars_nouveau:scry_ritual` | Scrying Ritual | 12 | **Gate attunement** — `TWIN_SPINES.md` §2.4. |
| `ars_nouveau:summon_ritual` | Ritual Brazier | 1 | Interlock — required by Alfsteel. |
| `ars_nouveau:potion_flask` | Potion Flask | 3 | Additives. |

## 4. Supporting magic — Nature's Aura, Occultism, BetterEnd, Feywild

Ecological and occult processes. Strong thematic fit as *additive* steps rather than spine steps.

| Process type | Station | Existing | Note |
|---|---|---:|---|
| `naturesaura:altar` | Natural Altar | 36 | Aura-gated — pairs with the drained-grove mechanic |
| `naturesaura:tree_ritual` | Ritual of the Forest | 17 | Multi-block, slow. Excellent late-era step. |
| `naturesaura:offering` | Offering Table | 7 | Consumes, does not return. Good sink. |
| `naturesaura:animal_spawner` | Animal Spawner | 60 | Living components |
| `occultism:crushing` | Crusher Spirit | 180 | Automatable reduction |
| `occultism:ritual` | Occultism Ritual | 69 | Era IX (`The Debt`) |
| `occultism:spirit_fire` | Spirit Fire | 16 | Cheap transmutation |
| `occultism:spirit_trade` | Spirit Trade | 3 | Exchange step |
| `occultism:miner` | Dimensional Mineshaft | 86 | Resource generation |
| ~~`betterend:infusion`~~ | ~~Infusion Ritual~~ | 46 | **REMOVED** — BetterEnd purged |
| ~~`bclib:alloying`~~ | ~~Alloying Furnace~~ | 8 | **REMOVED** — a genuine loss; it was the natural two-input tier step |
| ~~`bclib:smithing`~~ | — | 21 | **REMOVED** |
| `feywild:fey_altar` | Fey Altar | 29 | **Era VI, the Courts.** Perfect thematic fit. |
| `irons_spellbooks:alchemist_cauldron_brew` | Alchemist Cauldron | 15 | Additives |

## 5. Mechanical — Create and addons

23 process types. The industrial vocabulary, reframed as elven machinery
(`INSTRUCTIONS.md` §2.3 requires each to route through a spine).

| Process type | Existing | Ladder use |
|---|---:|---|
| **`create:sequenced_assembly`** | 83 | **The key one.** One recipe encodes N sequential passes on a belt — purpose-built for 11–17 step eras. |
| `create:mechanical_crafting` | 14 | Large multi-input assembly |
| `create:milling` / `crushing` | 470 | Reduction |
| `create:mixing` | 113 | Combination, heated variants |
| `create:deploying` | 157 | Applies an item to an item — ideal additive step |
| `create:filling` / `emptying` | 141 | Fluid stages |
| `create:pressing` / `compacting` | 75 | Shaping |
| `create:cutting` / `splashing` / `haunting` | 141 | Washing, soul-fire |
| `create:item_application` / `sandpaper_polishing` | 12 | Finishing |
| `createdieselgenerators:*` | 51 | wire_cutting, hammering, compression_molding, bulk/basin_fermenting, casting, distillation |
| `createbigcannons:melting` | 12 | Metal liquefaction |

## 6. Craft, trade and settlement

| Process type | Station | Existing |
|---|---|---:|
| ~~`hearthfire:*`~~ (woodcutting, woodworking, weaving, smithing) | ~~Hearthfire~~ | 626 | **REMOVED** |
| `farmersdelight:cutting` / `cooking` | Cutting Board, Cooking Pot | 156 |
| `refurbished_furniture:workbench_constructing` | Workbench | 446 |
| `refurbished_furniture:*` (oven, freezer, frying pan, toaster, microwave, cutting board) | Kitchen suite | 60 |
| ~~`conquest_armory:arms_station`~~ | ~~Arms Station~~ | 202 | **REMOVED** |
| `domum_ornamentum:architects_cutter` | Architect's Cutter | 80 |
| `framedblocks:frame` | Framing | 173 |
| ~~`twilightforest:uncrafting`~~ | ~~Uncrafting Table~~ | 2 | **REMOVED** |
| ~~`twilightforest:*`~~ | — | 52 | **REMOVED** |
| `minecolonies:composting` / `zero_waste` | Colony | 4 |

## 7. The gate as a process step

`botania:elven_trade` is not only a reward — it is a **station**, and under the reversal
(`GATE_REVERSAL.md`) it is an *export*. That means a mid or late chain can require passing an
intermediate **out through the gate and back**.

Doing that makes the pack's central premise mechanically compulsory rather than narrative: you cannot
build Era IV's material without a working trade route. Recommended as a mandatory link from Era IV
onward, and it pairs with `ars_nouveau:scry_ritual` for attunement.

## 8. Dead recipe types — do not plan steps around these

16 recipe types target mods that are **not installed**. Harmless (they simply never load), but they
appear in any naive scan of the jars.

| Type | Shipped by | Target mod |
|---|---|---|
| `immersiveengineering:crusher` / `cloche` / `squeezer` / `fermenter` / `metal_press` | Farmer's Delight | Immersive Engineering — absent |
| `jeed:effect_provider` / `potion_provider` | Supplementaries, Twilight Forest | JEED — absent |

## 9. Utility types — not ladder material

~50 single-purpose types exist for specific items rather than as stations: Botania's
`mana_gun_add_clip`, `cosmetic_attach`, `terra_pick_tipping`, `phantom_ink_apply`, `split_lens`,
`keep_ivy`, `merge_vial`…; Supplementaries' 17 one-off types (`antique_book`, `flag_from_banner`,
`weathered_map`…); Create Big Cannons' 11 munition types. Catalogued here so they are not
re-investigated; none are useful as tier steps.

---

## 10. Intermediate items — the 80-item roster

80 steps means roughly 80 intermediates. This is the largest content number in the project.

**Approach: generate them by tinting and compositing existing textures with PIL.** A 16×16 item
texture recoloured along a themed palette produces a coherent family cheaply — dusts, shards, ingots,
essences, filaments — and keeps the roster visually consistent in a way hand-drawing 80 icons would
not.

### 10.1 Licensing — read before choosing source textures

Deriving from third-party mod art and shipping it in a resource pack is **redistribution of a
derivative work**, and `INSTRUCTIONS.md` §5 forbids redistributing third-party assets without
compatible licensing. Several mods here are explicitly All Rights Reserved.

| Source | Safe to derive from |
|---|---|
| **Vanilla Minecraft textures** | **Yes** — resource packs are expressly permitted. Nuggets, ingots, dusts, gems, seeds, rods give a wide neutral shape vocabulary that tints well. |
| **Continuity Works assets** | Yes — ours |
| Permissively licensed mods (MIT / Apache / CC-BY) | Yes, with attribution as the licence requires |
| ARR mods (ForgeSkyboxes is explicitly ARR; others unverified) | **No**, without written permission |
| Procedurally generated from scratch | Yes |

**Recommendation:** build the pipeline on **vanilla bases**. They cover essentially every shape the
roster needs, they are unambiguously safe, and it removes a licence audit of 95 jars from the
critical path.

### 10.2 Pipeline sketch

A generator under `tools/` reading a manifest (`base texture, hue, saturation, overlay, output id`)
and emitting both the PNG and the KubeJS item registration, so the roster is reproducible from source
rather than hand-maintained — per `INSTRUCTIONS.md` §5, generated output must stay reproducible.

Not yet written. Backlog item to follow.

## 11. How to use this index

1. Give each era a **process signature** — which stations its chain uses, in order.
2. Introduce **at least one station the player has not used** per era (`CAMPAIGN_ERAS.md` §1b rule 2).
3. Alternate spines across the chain so neither completes alone (`TWIN_SPINES.md` §2).
4. Reserve `create:sequenced_assembly` for Eras VIII–X, where 13–17 steps need compressing into
   something a player can actually run.
5. Keep `botania:elven_trade` mandatory from Era IV (§7) — the gate opens there, settled 2026-09-03.
