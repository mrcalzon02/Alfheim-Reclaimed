# The Twelve Blooms — Alfheim's ore economy and the Rites that render it

**Role:** authoritative design record for Alfheim's native ore family and the magical processing
that turns it into base ingredients.
**Status:** `draft` — designed and evidenced, not yet implemented.
**Authority:** subordinate to `INSTRUCTIONS.md`. Supersedes the scarce-vanilla-ore approach
recorded in `EXECUTION_STATE.md` under "B-25 resolved by implementation, 2026-09-02".
**Decided by the user, 2026-09-03:** *"I don't want to use vanilla ores because that just reskins
Alfheim as the Overworld."*

---

## 1. The problem, measured

Two independent faults, both invisible to every static check the project currently runs.

### 1.1 Alfheim is a reskinned Overworld

Today Alfheim's mineral wealth is seven **vanilla** ores — copper, iron, coal, lapis, diamond,
redstone — injected by three `forge:add_features` biome modifiers, and made to place at all only
by force-adding `botania:livingrock` to `#minecraft:stone_ore_replaceables`. A player who tunnels
in Alfheim finds exactly what they would find in the Overworld, at a quarter the density. The
world's defining premise — a place where magic ate the geology — is contradicted by its own
stone.

### 1.2 The chains do not have roots

Measured across all thirteen of our server scripts, every ingredient our recipe chains consume:

| Ingredient | Uses | Reachable in Alfheim today? |
|---|---:|---|
| `minecraft:gunpowder` | 21 | **Witch drop only**, and witches spawn in 5 of 11 biomes. No creepers spawn anywhere in Alfheim. |
| `minecraft:blaze_powder` | 16 | **No.** Nether-only. |
| `minecraft:melon_slice` | 14 | No native melon. Seeds are loot/trade. |
| `minecraft:raw_iron` | 14 | Yes — scarce vanilla ore |
| `minecraft:raw_copper` | 13 | Yes — scarce vanilla ore |
| `occultism:raw_silver` | 11 | **No.** No silver feature reaches any Alfheim biome. |
| `minecraft:redstone` | 11 | Yes — scarce vanilla ore |
| `minecraft:raw_gold` | 9 | Yes — `mythicbotany:gold_ore`, all 11 biomes. *(Corrected 2026-09-03: an earlier draft of this table said 5 of 11. Our six biomes carry MythicBotany's ore set through the `ORES` constant in `gen_alfheim_biomes.py`, so gold reaches all eleven. Sunbloom is still worth building — it gives gold a **Rite** route and an era gate rather than leaving it to deep mining — but it closes a distribution gap, not an absence.)* |
| `minecraft:ghast_tear` | 8 | **No.** Nether-only. |
| `minecraft:glowstone_dust` | 8 | **Witch drop only**, as gunpowder. |
| `minecraft:quartz` | 1 | **No.** Nether-only. |
| `ars_nouveau:source_gem` | 22 | Yes — imbuement from lapis |
| `naturesaura:gold_leaf` | 3 | Depends on gold, above |

Three ingredients used 25 times are **Nether-only**, and the Nether is not known to be reachable:
portal linking is hardcoded Overworld↔Nether and Alfheim is not the Overworld. That risk is
recorded and still unverified. Two more used 29 times depend on a single mob that spawns in
under half the world.

> This is the same failure class as B-25 and B-41: every id exists, every static check passes,
> and the material does not. `check_era.py` proves a recipe is *reachable in the graph*. It has
> never proven the graph has a **root in the ground**.

### 1.3 There are no petals in Alfheim — found while validating this design

Checking Rite I's own reagent against the world turned up a defect larger than the ore gap.

**No Botania feature generates in any of the eleven Alfheim biomes.** Verified by reading the
feature lists of our six biome JSONs and MythicBotany's five from its jar: zero `botania:*`
entries at any generation step.

The near-miss that hides it is `mythicbotany:motif_flowers`, which appears in three Alfheim biomes
and looks like the flower source. It is not. `MotifFlowerFeature.class` places exactly two blocks —
`BotaniaBlocks.motifDaybloom` and `BotaniaBlocks.motifNightshade` — and **neither has a loot
table**, so both drop nothing. They are decoration.

Mystical flowers are the only source of petals; the 64 petal recipes in Botania's jar are all
petal↔petal-block storage conversions, not creation. Petals gate the Pure Daisy, every Petal
Apothecary recipe, the Wand of the Forest and the Mana Spreader — **the entire Spine of Leaf**,
which is half this pack. Era I's own authored quests already require a Pure Daisy and a Mana
Spreader.

**The pack is not quite hard-locked, but only by an undocumented accident.** Botania's Floral
Fertilizer is `minecraft:bone_meal + 4× #forge:dyes` — no petals — and applying it to grass spawns
mystical flowers. Bone meal is reachable from a composter, and four *white* dyes satisfy the four
tag slots. So the bootstrap is:

```
plant matter -> composter -> bone meal -> 4x white dye
             -> botania:fertilizer -> apply to grass -> mystical flowers -> petals
```

That route is non-obvious to an experienced Botania player, invisible to a new one, undocumented
anywhere in the pack, and the single point of failure for half the campaign.

**The fix is Botania's own mechanism, not a new one.** Botania injects flowers with
`add_mystical_flowers.json`, a `forge:add_features` modifier keyed on the biome tag
`#botania:mystical_flower_spawnlist`. Adding Alfheim to that tag is one datapack file:

```
kubejs/data/botania/tags/worldgen/biome/mystical_flower_spawnlist.json
  { "replace": false, "values": ["#mythicbotany:alfheim"] }
```

Mystical flowers then generate in Alfheim through Botania's own modifier and ordering, so no new
feature of ours enters the sort. Three layers, because this one must not fail:

1. **Worldgen** — the tag addition above. The elven homeland having no mystical flowers was always
   the anomaly.
2. **Taught** — Era I Guides cover the Floral Fertilizer route explicitly, so the renewable path is
   known even if a player strips their area bare.
3. **Starting kit** — `01_starting_kit.js` adds a small petal grant and one Floral Fertilizer, so
   minute zero is never a dead end.

This is tracked as **B-46** and it outranks the ore work: blooms are useless if the Apothecary that
renders them cannot be fed.

---

## 2. The premise, extended

Alfheim's ley-lines died. The mana that ran through the bedrock did not drain away — it
**crystallised**, and it took the metal with it.

> There is no ordinary metal in Alfheim because the magic ate it. What is left in the stone are
> **blooms**: mineral growths that hold the *pattern* of a metal without being one.

You cannot smelt a bloom. Heat alone does nothing to it — the pattern is magical, not chemical.
To make a bloom remember what it was, you give it **living things**: petals, seed, grain, sapling,
fruit. Life completes the pattern. That is **supplementation**, and it is the only metallurgy
Alfheim has.

This carries three consequences that the pack has needed and did not have:

1. **It explains the scarcity** the premise asserts, instead of merely asserting it.
2. **It makes botanical magic load-bearing.** Farming is not flavour; it is the smelter.
3. **It preserves the trade route.** Midgard has *finished* metal — already patterned, available
   in bulk, needing no garden. Alfheim's route is self-sufficient and slow; Midgard's is fast and
   large. The gate stays worth opening. `INSTRUCTIONS.md` §1 holds.

---

## 3. The Twelve Blooms

Twelve ore blocks, all native to Alfheim, all placed against `#mythicbotany:base_stone_alfheim` —
MythicBotany's own Alfheim stone tag (livingrock plus the seven metamorphic stones). This is the
tag the mod's own gold, elementium and dragonstone ores already use. Using it means:

- Alfheim's ores are Alfheim's, not vanilla's;
- **the global `#minecraft:stone_ore_replaceables` override is reverted** — the livingrock entry
  that currently reaches every dimension goes away;
- our features sit in the same namespace of intent as the mod's, which is what the deep-slate
  variant handling and the metamorphic stones already assume.

| # | Ore block | Raw drop | Renders into | Era | y-range | Rarity |
|--:|---|---|---|:--:|---|---|
| 1 | `alfheim:cinderbloom_ore` | `cinder_clump` | coal, charcoal | I | 0…96 | common, surface-exposed |
| 2 | `alfheim:verdigris_ore` | `verdigris_nodule` | copper | I | 8…112 | common |
| 3 | `alfheim:palebloom_ore` | `pale_nodule` | iron | I | −16…80 | common |
| 4 | `alfheim:sparkroot_ore` | `sparkroot_clump` | redstone, glowstone dust | II | −48…24 | uncommon |
| 5 | `alfheim:duskbloom_ore` | `dusk_shard` | lapis, source gem | II | −32…40 | uncommon |
| 6 | `alfheim:sunbloom_ore` | `sun_nodule` | gold, gold leaf | III | −32…32 | uncommon |
| 7 | `alfheim:cloudglass_ore` | `cloudglass_shard` | quartz, glass, amethyst | III | 16…96 | uncommon |
| 8 | `alfheim:silverthorn_ore` | `silverthorn_nodule` | silver (Occultism) | IV | −24…56 | uncommon |
| 9 | `alfheim:grievebloom_ore` | `grieve_dust` | gunpowder, ghast tear | IV | −64…−8 | rare, deep |
| 10 | `alfheim:rimebloom_ore` | `rime_shard` | diamond | V | −64…8 | rare |
| 11 | `alfheim:emberwake_ore` | `emberwake_ember` | blaze powder, magma cream | VII | −64…−16 | rare, deep |
| 12 | `alfheim:farbloom_ore` | `far_pearl` | ender pearl, chorus fruit | VIII | −64…0 | rarest |

**Every Nether-only and mob-only ingredient in §1.2 now has a ground root.** Blooms 9, 11 and 12
exist specifically to close gunpowder, ghast tear, blaze powder and the end-family — the four that
no amount of recipe re-pointing could have fixed, because the material was not in the world.

### 3.1 Block properties

All twelve share one shape so they read as a family:

- `hardness(3.0)`, `resistance(3.0)`, `requiresTool(true)`, stone sound;
- tagged `#minecraft:mineable/pickaxe` and `#forge:ores`, plus a family tag `#alfheim:blooms`;
- tier tag per era: blooms 1–3 need **stone**, 4–8 **iron**, 9–12 **diamond**. Era I must be
  minable with the first pickaxe the player can make, or the prologue stalls;
- loot drops the raw item, `silk_touch` drops the block, Fortune applies;
- emissive-ish palette derived from a vanilla ore base by `gen_items.py`'s existing tint path, so
  the roster stays reproducible rather than hand-drawn.

### 3.2 Worldgen and the feature-order invariant

Four `forge:add_features` biome modifiers, each on a disjoint biome tag:

| Modifier | Biome tag | Blooms |
|---|---|---|
| `blooms_common` | `#mythicbotany:alfheim` (all 11) | 1, 2, 3 |
| `blooms_veined` | `#alfheim:veined` | 4, 5, 6, 7 |
| `blooms_deep` | `#alfheim:deep` | 9, 10, 11, 12 |
| `blooms_drained` | `#alfheim:drained` | 8 |

> **Binding rule, from CW-4.** *Each bloom feature must appear in exactly one modifier.* Forge
> appends modifier features to the end of a step, and applies modifiers in `ResourceLocation` path
> order across **every mod**. Two modifiers adding the *same* feature under names that straddle a
> third hand two biomes contradictory orders, and `FeatureSorter` throws `Feature order cycle
> found` on world creation with every id valid. Disjoint feature sets make that impossible from
> our side by construction. `check_feature_order.py` must be extended to assert disjointness.

All twelve ids must be added to `FEATURE_ORDER` in `gen_alfheim_biomes.py`, ranked **after**
MythicBotany's `extra_gold_ore` in step 6, or `ordered()` will refuse them — which is the intended
behaviour, not an obstacle.

---

## 4. The Four Rites — magical processing

A raw bloom is inert. It becomes a base ingredient only through a **Rite**, and each Rite is a
station the era has just taught. This is the "one new process per era" rule from
`CAMPAIGN_ERAS.md` §1b applied to material acquisition rather than to a single tier item.

The same bloom is valid input to every Rite the player has unlocked. Later Rites do not obsolete
earlier ones — they pay better. That is what makes the ladder feel like progress instead of
replacement.

| Rite | Era | Station | Reagents beyond the bloom | Yield | Mana / Source |
|---|:--:|---|---|:--:|---|
| **I — The Steeping** | I | Petal Apothecary | 2 petals + 1 crop | 1× | none (water reagent) |
| **II — The Quickening** | II | Mana Pool infusion | — (consumes a Steeped intermediate) | 2× | 3 000–12 000 mana |
| **III — The Grafting** | III | Runic Altar | 3 plant reagents + 1 rune | 3× + byproduct | 8 000–24 000 mana |
| **IV — The Deepening** | V | MythicBotany Infuser | elven reagents | 4× + rare byproduct | 60 000+ mana |

### 4.1 The intermediate stage

Every bloom passes through a **Quickened** intermediate before it becomes a base ingredient. This
is deliberate: it gives each chain a visible middle, it is where the yield multiplier is applied,
and it is the hook the era quests hang their teaching on.

```
alfheim:pale_nodule                     mined from alfheim:palebloom_ore
        |
        |  RITE I — The Steeping   (botania:petal_apothecary)
        |     ingredients: pale_nodule, 2x #botania:petals/white, minecraft:wheat
        |     reagent:     #botania:seed_apothecary_reagent
        v
alfheim:quickened_pale_nodule           the intermediate stage
        |
        |  smelting  (or blasting)
        v
minecraft:iron_ingot                    the base ingredient every existing recipe wants
```

Rite II replaces the Steeping step for the same bloom at twice the yield:

```
alfheim:pale_nodule  --[ botania:mana_infusion, 4000 mana ]-->  2x alfheim:quickened_pale_nodule
```

### 4.2 Why the output is a vanilla ingredient, not a custom metal

The Rites emit `minecraft:iron_ingot`, `minecraft:gunpowder`, `minecraft:blaze_powder` and the
rest — the exact ids the existing chains already consume.

This is the single most important implementation decision in this document. Making custom elven
metals instead would require re-pointing every recipe in Botania, MythicBotany, Ars Nouveau,
Occultism, Create and eleven other mods that expects vanilla ingots — hundreds of recipes, each a
chance to soft-lock the pack, against `INSTRUCTIONS.md` §6.2's requirement that every gated item
keep exactly one reachable route.

**The ore is custom and elven. The product is standard.** We change where base ingredients come
from, not what they are. Existing recipe chains keep working untouched, and the ~500 recipes
already authored need no revision.

### 4.3 The plant reagents

Each bloom takes reagents that read as *why* that metal comes back. They are all obtainable in
Alfheim: Botania mystical petals grow from mystical flowers, wheat and saplings are native to
MythicBotany's biomes (`wheat_fields`, `dreamwood_trees`), and the rest are Farmer's Delight and
The Harvest crops.

| Bloom | Rite I reagents | Reads as |
|---|---|---|
| Cinderbloom | 2× black petal + charcoal-bearing sapling | burnt things remember fire |
| Verdigris | 2× green petal + wheat | green metal, green life |
| Palebloom | 2× white petal + wheat | the plainest bloom, the plainest grain |
| Sparkroot | 2× red petal + redstone-root or beetroot | a root that carries current |
| Duskbloom | 2× blue petal + sugar cane | deep water, deep colour |
| Sunbloom | 2× yellow petal + golden crop (wheat + apple) | the golden fields |
| Cloudglass | 2× light-blue petal + sapling | clarity grown, not blown |
| Silverthorn | 2× light-grey petal + bramble/thorn crop | it cuts |
| Grievebloom | 2× black petal + wither-touched flora | grown where things died |
| Rimebloom | 2× white petal + frost-tolerant crop | slow, cold, valuable |
| Emberwake | 2× orange petal + blazing archwood sapling | fire wood for fire metal |
| Farbloom | 2× purple petal + chorus-adjacent flora | it is not entirely here |

### 4.4 Verified recipe schemas

Read from the shipping jars on 2026-09-03, per B-41's requirement that schemas are never guessed:

| Type | Required shape |
|---|---|
| `botania:petal_apothecary` | `ingredients[]`, `output{item}`, `reagent{tag}` |
| `botania:mana_infusion` | `input{}`, `mana`, `output{item,count}`, optional `catalyst{type,block}` |
| `botania:runic_altar` | `ingredients[]`, `mana`, `output{item,count}` |
| `mythicbotany:infuser` | `ingredients[]`, `mana`, `output{}`, **`fromColor`**, **`toColor`**, `group` |
| `ars_nouveau:imbuement` | `input{}`, `output` (bare id string), `pedestalItems[{item:{item}}]`, `source`, `count` |
| `naturesaura:tree_ritual` | `sapling{}`, `ingredients[]`, `output{item,count}`, `time` |

`mythicbotany:infuser`'s `fromColor`/`toColor` are the exact fields whose absence silently killed
five recipes in B-41. Any generator emitting this type must supply both as integers.

---

## 5. What is removed

| Target | Action | Reason |
|---|---|---|
| `kubejs/data/alfheim/worldgen/{configured,placed}_feature/ore_*_scarce.json` (6) | delete | vanilla ore in Alfheim is the reskin the user rejected |
| `.../ore_iron_highland.json` (2 files) | delete | same |
| `kubejs/data/alfheim/forge/biome_modifier/{common_metals,highland_veins,arcane_strata}.json` | delete | replaced by the four bloom modifiers |
| `kubejs/data/minecraft/tags/blocks/stone_ore_replaceables.json` | delete | a global cross-dimension override no longer needed once blooms target `#mythicbotany:base_stone_alfheim` |
| `kubejs/data/alfheim/tags/worldgen/biome/{arcane_strata,highland_veins}.json` | replace | superseded by `veined` / `deep` / `drained` |

`kubejs/data/minecraft/tags/blocks/base_stone_overworld.json` is retained pending a separate check
— it is not part of this change.

> **`INSTRUCTIONS.md` §6.1 binds here.** Nothing above is deleted until the twelve blooms and
> their Rite I recipes exist and have been seen to generate and craft in a fresh world. The
> deletion and the replacement ship in the same change, or Alfheim briefly has no metal at all.

---

## 6. Coverage — every chain root, traced to ground

| Base ingredient | Old root | New root |
|---|---|---|
| coal / charcoal | vanilla coal ore | **Cinderbloom** → Rite I |
| copper | vanilla copper ore | **Verdigris** → Rite I |
| iron | vanilla iron ore | **Palebloom** → Rite I |
| redstone | vanilla redstone ore | **Sparkroot** → Rite I |
| glowstone dust | witch drop, 5/11 biomes | **Sparkroot** → Rite III |
| lapis | vanilla lapis ore | **Duskbloom** → Rite I |
| `ars_nouveau:source_gem` | lapis → imbuement | unchanged, now rooted |
| gold | `mythicbotany:gold_ore`, 5/11 biomes | **Sunbloom** → Rite I, all 11 |
| `naturesaura:gold_leaf` | depends on gold | rooted via Sunbloom |
| quartz | **nothing** — Nether-only | **Cloudglass** → Rite II |
| glass / amethyst | sand / geodes, neither native | **Cloudglass** → Rite I / III |
| `occultism:raw_silver` | **nothing** | **Silverthorn** → Rite I |
| gunpowder | witch drop, 5/11 biomes | **Grievebloom** → Rite I |
| ghast tear | **nothing** — Nether-only | **Grievebloom** → Rite III |
| diamond | vanilla diamond ore | **Rimebloom** → Rite I |
| blaze powder | **nothing** — Nether-only | **Emberwake** → Rite II |
| magma cream | **nothing** — Nether-only | **Emberwake** → Rite III |
| ender pearl | enderman, spawn unverified | **Farbloom** → Rite I |
| elementium / dragonstone | `mythicbotany:*_ore`, 5/11 biomes | unchanged — native elven metal, per premise |

Six ingredients move from **unreachable** to rooted. Three move from *one mob in under half the
world* to rooted. Nothing that worked stops working.

---

## 7. Implementation order

Sequential. Each step is validated before the next begins, per `INSTRUCTIONS.md` §7.

| # | Unit | Accept when |
|--:|---|---|
| 1 | `tools/blooms_manifest.json` — the twelve, as data | parses; twelve entries; ids unique |
| 2 | `tools/gen_blooms.py` — blocks, items, textures, models, tags | regenerates byte-identically from the manifest |
| 3 | Rite recipes I–IV in `kubejs/server_scripts/1x_rites_*.js` | schema-checked against §4.4 |
| 4 | Worldgen: 12 features ×2, 4 modifiers, 3 biome tags | `check_worldgen.py` resolves all |
| 5 | `FEATURE_ORDER` + disjointness assertion in `check_feature_order.py` | 0 cycles; synthetic overlap fails |
| 6 | `check_era.py` — new **R-invariant**: every chain root traces to a placed ore feature | fails on a deliberately unrooted chain |
| 7 | Remove §5's vanilla ore layer | `check_worldgen.py` reports no vanilla ore in Alfheim |
| 8 | Level 8 boot, then level 9 fresh world | blooms generate; Rite I crafts; 0 recipe-parse errors |

**Step 6 is the one that stops this recurring.** The project has now twice shipped a world where
every id resolved and the material was absent. A reachability checker that does not terminate at
the ground cannot catch that, and no amount of care substitutes for the invariant.

---

## 8. The Archive Groves — petals from leaves, and Alfheim's own trees

**User instruction, 2026-09-03:** *"We should add petal variety to the break block recipe of leaves
for all trees of Alfheim… certain types of leaves should have certain types of petals. We should
also include various types of trees of our own custom generation, to give randomized overworld
saplings so that we can get access to other types of trees."*

This is the **real** answer to B-46. The spawnlist fix in §1.3 makes mystical flowers *generate*;
this makes petals **renewable by an activity the player is already doing**, and ties the supply to
the trees that actually grow in Alfheim rather than to a flower patch they may strip bare.

Manifest `tools/groves_manifest.json`, generator `tools/gen_groves.py`.

### 8.1 Petals from the leaves already here

Five leaf types grow in Alfheim. Each now drops petals of its own colour.

| Leaf | Petals | Where |
|---|---|---|
| `mythicbotany:dreamwood_leaves` | white, light gray | almost every biome — the workhorse |
| `ars_nouveau:blue_archwood_leaves` | blue, light blue | bloomfall_vale |
| `ars_nouveau:red_archwood_leaves` | red, pink | bloomfall_vale |
| `ars_nouveau:green_archwood_leaves` | green, lime | bloomfall_vale |
| `ars_nouveau:purple_archwood_leaves` | purple, magenta | bloomfall_vale |

**These are mod-owned loot tables, so the generator copies them verbatim out of the jar and
appends one pool.** Nothing is retyped. That matters concretely: archwood leaves drop the archwood
saplings that Rite I uses as a reagent, and a hand-authored override would have silently deleted
them. Each generated table carries an `__alfheim` provenance block with the source jar's SHA-1, so
drift after a mod update is visible without diffing. Re-running the generator re-reads the jar and
re-syncs.

Drop rate 0.09 before Fortune, on vanilla's own apple-pool pattern: not on shears, not on silk
touch, survives explosion, scales with Fortune.

### 8.2 Three trees of our own

No vanilla tree generates in Alfheim. Without these there is no oak, no apple, no plank variety —
and `minecraft:apple` alone is used 13 times in the existing chains.

> **The fiction.** Before the devastation the elves kept a seed-archive of every forest in the Nine
> Realms. Three trees are what survived of it. Their leaves still carry other forests' seeds.

| Tree | Petals | Saplings its leaves drop | Biomes |
|---|---|---|---|
| **Emberbark** | orange, yellow | acacia, jungle, oak | sundered_highlands, ashen_grove, alfheim_hills |
| **Gloambark** | black, brown | dark oak, spruce, oak | hollow_marches, mana_fen, alfheim_lakes |
| **Hushbark** | gray, cyan | birch, cherry, spruce | silverbark_wood, bloomfall_vale, dreamwood_forest |

**All 16 petal colours now have a leaf source** — the five mod leaves cover ten, these three cover
the remaining six. **Seven vanilla saplings become reachable**, and they are plantable, so the
player bootstraps a normal wood economy from a foreign-seed drop.

### 8.3 Two constraints this design obeys

**They are worldgen-only, and cannot be replanted.** KubeJS 2001.6.5 ships no sapling builder and
no `TreeGrower` binding — verified against the jar, not assumed — so a plantable custom sapling is
not available without a Java mod. The *vanilla* saplings they drop are plantable, which is the
point of the feature; the custom trees themselves are a wild resource. Recorded in §9.

**One feature per modifier, `zz_`-prefixed.** Each tree is added by its own
`zz_grove_<id>.json`, carrying exactly one feature. Disjoint feature sets make a feature-order
cycle impossible from our side, and the `zz_` prefix sorts them after every vegetal modifier the
mods ship — the same discipline `gen_alfheim_biomes.py` uses for the archwood and cascading
features, and for the same reason. `check_feature_order.py` after this change: **0 cycles**, 63
modifiers applied.

## 9. Crystallised mana — six alignments, six bifurcated geodes

**User instruction, 2026-09-03:** *"a variety of crystals similar to the amethyst… crystallised
mana stones of various elemental alignments… no single geode should have just one type of crystal,
they should be bifurcated — half of a geode is one crystal and the other half another… much more
plentiful than the vanilla amethyst… some kind of surface feature to indicate that a geode is in
that chunk."*

Manifest `tools/crystals_manifest.json`, generator `tools/gen_crystals.py`.

> **The fiction.** The Blooms (§3) are what happened where mana crystallised into *stone*. Where
> the ley-lines ran hardest it did something else: it **separated by alignment** and set as gem. A
> geode is therefore never one crystal. It is the boundary between two, and you can see the seam.

### 9.1 The six

| Crystal | Alignment | Blocks | Item |
|---|---|---|---|
| **Emberglass** | Fire | block, budding, cluster | Emberglass Shard |
| **Tidewake** | Water | " | Tidewake Shard |
| **Rootglass** | Earth | " | Rootglass Shard |
| **Galeglass** | Air | " | Galeglass Shard |
| **Duskglass** | Shadow | " | Duskglass Shard |
| **Dawnglass** | Light | " | Dawnglass Shard |

Budding blocks **grow clusters on random tick**, so a deposit is renewable rather than finite.
Vanilla does this in `BuddingAmethystBlock`; KubeJS 2001.6.5 has no binding for it, so `randomTick`
picks a face and places a cluster if it is air — a 1-in-5 roll per face, deliberately slower than
vanilla. Budding blocks drop nothing without Silk Touch, so a deposit cannot be trivially moved.

### 9.2 Bifurcation is spatial, not statistical

The requirement was *halves*, not a mix — and vanilla's geode feature has no notion of sides.

The answer is **`minecraft:noise_threshold_provider`** on the inner layer. It picks each block from
`low_states` or `high_states` by sampling a noise field **at that block's position**. At
`scale: 0.08` the field is coherent over tens of blocks, so a geode 10–16 blocks across usually
straddles exactly one boundary: one half crystal A, the other crystal B, with a real seam. A
`weighted_state_provider` — the obvious first choice — would have given salt-and-pepper.

`inner_layer_provider` and `alternate_inner_layer_provider` **share one seed**, so the budding
blocks land on the correct side of the seam rather than in the wrong half.

| Geode | Pair | Rarity | Biomes |
|---|---|---|---|
| the Burning Dark | Emberglass ∣ Duskglass | 1 in 6 | sundered_highlands, ashen_grove |
| the Storm | Tidewake ∣ Galeglass | 1 in 6 | alfheim_lakes, mana_fen |
| the Greening | Rootglass ∣ Dawnglass | 1 in 5 | bloomfall_vale, alfheim_plains, golden_fields |
| the Forge | Emberglass ∣ Galeglass | 1 in 6 | alfheim_hills |
| the Drowned | Tidewake ∣ Duskglass | 1 in 5 | hollow_marches |
| the Quiet Fen | Rootglass ∣ Tidewake | 1 in 6 | silverbark_wood, dreamwood_forest |

Six pairs across eleven biomes is the "random distribution of what is where": which alignments a
region yields is a property of that region, so the map is worth reading.

### 9.3 Plentiful, and anchored to where the player is standing

Vanilla amethyst is `rarity_filter: 24` at **absolute** y 6–30 — rare, and unrelated to the surface
above it. Ours average **1 in 5.6 eligible chunks (4.3× vanilla)** and are anchored to the *local*
surface: `heightmap` then a negative `random_offset` of 14–28, so they sit just under the ground
being walked on rather than at a fixed depth.

That anchoring is not only for findability. It is what makes the surface marker possible at all.

### 9.4 The surface marker cannot lie

`minecraft:environment_scan` caps `max_steps` at **32**, so a marker can only verify a geode within
32 blocks below it — which the surface anchoring guarantees. The marker's placement chain:

```
count(2) → in_square → heightmap(OCEAN_FLOOR_WG)
         → environment_scan(down, target #alfheim:budding_crystals, max_steps 32)
         → heightmap(OCEAN_FLOOR_WG)      ← scan moved only Y, so this returns to the surface
         → biome
```

`environment_scan` **aborts the placement when it finds nothing**, so a marker never appears
without a geode beneath it. **Zero false positives** — that is the property that makes it a signal
a player can trust rather than noise they learn to ignore. False negatives (a geode with no marker)
are acceptable and expected at chunk edges.

The marker is itself a **small geode of the same two crystals**, so it tells the player *which*
pair is below, not merely that something is.

**Step ordering matters and is deliberate:** the geode is added in `local_modifications` and the
marker in `top_layer_modification`, so by the time the marker scans, the geode it is looking for
already exists.

## 10. Open

1. **Bloom textures.** `gen_items.py` tints vanilla bases. Ore blocks need a stone-plus-speckle
   base; the vanilla ore textures are the obvious source and are already the licence-safe path the
   project accepted for items.
2. **Deepslate variants.** Vanilla ores ship a deepslate twin. Alfheim's stone is livingrock and
   the seven metamorphic stones, which have no deepslate analogue, so the blooms ship as one block
   each. Revisit only if the metamorphic stones read badly at depth.
3. **Fortune and silk touch balance.** Specified in §3.1 but not tuned; tune after level 9 when
   real mining time exists to measure against.
4. **Whether Rite IV should exist at Era V or Era VII.** Era V is where the Infuser arrives, but
   Era V also brings native Elementium, which may make a 4× multiplier on common metals moot.
5. **The Archive Groves cannot be replanted** (§8.3). If wild Emberbark, Gloambark and Hushbark
   prove too scarce to be a comfortable petal source, the options are: raise `count`/`rarity` in
   `groves_manifest.json`; add a Rite that converts leaves to petals directly; or accept a Java
   mod for a real sapling. Decide after level 9, when there is a real world to walk.
6. **Petal drop rates are untuned.** 0.09 on mod leaves and 0.10 on grove leaves are first
   guesses. The right number is whatever makes a Petal Apothecary recipe feel like a morning's
   work rather than an afternoon's; measure it in a real world, not in a spreadsheet.
