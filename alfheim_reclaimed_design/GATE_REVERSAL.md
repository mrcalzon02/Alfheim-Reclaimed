# The Gate Reversal

**Status:** design record — specification complete, implementation not yet written to `kubejs/`.
**Authority:** `INSTRUCTIONS.md` §1. Recipe data below verified by extraction from the pinned jars.

---

## 1. What is being reversed

Botania ships **15 functional elven trade recipes** in `data/botania/recipes/elven_trade/`. Verified
against `Botania-1.20.1-455-FORGE.jar`. Nine of them convert a mundane input into an elven output;
five are identity "returns" that exist so the portal does not eat mundane items; one is the lexicon.

### 1.1 The nine conversions, as shipped

| Recipe | Input (Midgard) | Output (elven) |
|---|---|---|
| `dreamwood` | `botania:livingwood` | `botania:dreamwood` |
| `dreamwood_log` | `botania:livingwood_log` | `botania:dreamwood_log` |
| `elementium` | 2 × `botania:manasteel_ingot` | `botania:elementium_ingot` |
| `elementium_block` | 2 × `botania:manasteel_block` | `botania:elementium_block` |
| `dragonstone` | `botania:mana_diamond` | `botania:dragonstone` |
| `dragonstone_block` | `botania:mana_diamond_block` | `botania:dragonstone_block` |
| `elf_glass` | `botania:mana_glass` | `botania:elf_glass` |
| `elf_quartz` | `minecraft:quartz` | `botania:quartz_elven` |
| `pixie_dust` | `botania:mana_pearl` | `botania:pixie_dust` |

Recipe schema, confirmed:

```json
{
  "type": "botania:elven_trade",
  "ingredients": [ { "item": "botania:livingwood" } ],
  "output":      [ { "item": "botania:dreamwood"  } ]
}
```

### 1.2 The reversal

Each conversion is inverted. You send elven goods out; Midgard goods come back.

| Recipe | Input (elven, native) | Output (Midgard, exotic) |
|---|---|---|
| `dreamwood` | `botania:dreamwood` | `botania:livingwood` |
| `dreamwood_log` | `botania:dreamwood_log` | `botania:livingwood_log` |
| `elementium` | `botania:elementium_ingot` | 2 × `botania:manasteel_ingot` |
| `elementium_block` | `botania:elementium_block` | 2 × `botania:manasteel_block` |
| `dragonstone` | `botania:dragonstone` | `botania:mana_diamond` |
| `dragonstone_block` | `botania:dragonstone_block` | `botania:mana_diamond_block` |
| `elf_glass` | `botania:elf_glass` | `botania:mana_glass` |
| `elf_quartz` | `botania:quartz_elven` | `minecraft:quartz` |
| `pixie_dust` | `botania:pixie_dust` | `botania:mana_pearl` |

The five identity returns (`iron`, `iron_block`, `diamond`, `diamond_block`, `ender_pearl`) stay
exactly as they are. They are safety valves, not progression.

## 2. The soft-lock this creates, and the fix

**This is the part that will break the pack if it is implemented carelessly.**

Botania's entire early game is built on Livingwood. The Wand of the Forest, the Mana Spreader, the
Petal Apothecary chain, the first Mana Pool — all of it. Under the reversal, Livingwood is now
obtainable *only* through a gate the player cannot open until mid-campaign.

Left unaddressed, the player reaches the first flower and stops forever.

### 2.1 Dreamwood becomes the elven starting wood

Botania already ships every part needed. Verified present:

| Midgard form | Elven form | Status |
|---|---|---|
| `botania:livingwood_twig` | `botania:dreamwood_twig` | exists |
| `botania:mana_spreader` | `botania:elven_spreader` | exists |
| `botania:mana_pylon` | `botania:natura_pylon` | exists |
| `botania:livingwood_log` | `botania:dreamwood_log` | exists |
| `botania:livingwood` | `botania:dreamwood` | exists |

So the fix is not to invent items. It is to **re-point the early recipes at the forms that already
exist**, and to give Dreamwood a native origin.

### 2.2 Required additions

**A. A Pure Daisy route to Dreamwood.** As shipped, `botania:pure_daisy/livingwood` turns
`#minecraft:logs` into `botania:livingwood_log`. On the elven side the Pure Daisy must instead
produce `botania:dreamwood_log`. The Livingwood route is removed — it is now a gate import.

**B. Dreamwood variants of the early chain.** Wand of the Forest from `dreamwood_twig`; the first
spreader is the `elven_spreader`; the apothecary and pool chains accept Dreamwood where they
required Livingwood.

**C. Elementium from ore, not from trade.** MythicBotany already ships
`mythicbotany:elementium_ore` and `mythicbotany:raw_elementium`, generating in the Alfheim dimension.
Under the reversal this is the *primary* Elementium source and needs no new recipe — only worldgen
confirmation and a smelting path. This is the single strongest piece of evidence that the reversal is
the mod stack's natural grain rather than a fight against it.

**D. Dragonstone, Elf Glass, Elven Quartz, Pixie Dust need native routes.** Each currently exists only
as a trade output. Proposed, in ascending era order:

| Item | Proposed native route | Era |
|---|---|---|
| `botania:quartz_elven` | Mana infusion from Alfheim-native quartz | III |
| `botania:elf_glass` | Mana infusion from sand + Pixie Dust | IV |
| `botania:pixie_dust` | Pixie mob drop (`mythicbotany:alf_pixie`) + infusion | IV |
| `botania:dragonstone` | Runic Altar, gated on Rune of Nidavellir | V |

## 3. What the inversion does to the milestone order

This is the elegant part, and it falls out of the data rather than being imposed.

**Terrasteel** requires `manasteel_ingot` + `mana_pearl` + `mana_diamond` at 500,000 mana. All three
are now **imports**. Terrasteel therefore becomes a *late* milestone that cannot be reached without a
working trade route.

**Alfsteel** requires 1,500,000 mana infusion and is otherwise elven-native. It becomes reachable
*earlier* than Terrasteel.

In unmodified MythicBotany the order is Terrasteel → open Alfheim → Alfsteel. Here it inverts to
**Alfsteel → open the gate → Terrasteel**, and Terrasteel stops being a tech tier and becomes what it
always should have been thematically: the alloy of two worlds, made only when the elves reach Midgard
again.

## 4. Implementation plan

Written as KubeJS in `kubejs/server_scripts/`, never by editing jars.

```
20_gate_reversal.js        remove the 9 conversions, add the 9 inversions
21_elven_early_game.js     dreamwood pure daisy, dreamwood twig/spreader chain
22_native_elven_goods.js   quartz, glass, pixie dust, dragonstone routes
```

Sequencing is mandatory and is not negotiable: **`21` must be loaded and verified in-game before `20`
is enabled.** Enabling the reversal before the Dreamwood early game exists produces a pack that boots
cleanly and is unplayable — the worst possible failure, because it passes every static check.

## 5. Validation

| Level | Condition |
|---|---|
| 4 | All 18 affected recipes appear correctly in JEI; no KubeJS errors in log |
| 8 | Pack boots with scripts loaded |
| 9 | Fresh world: Pure Daisy produces Dreamwood; `mythicbotany:elementium_ore` generates in Alfheim |
| 11 | A test player reaches the first Mana Pool using **only** elven-side materials |

Level 11 is the real gate. Until someone has played from spawn to first mana pool without touching
Livingwood, the reversal is `draft`.
