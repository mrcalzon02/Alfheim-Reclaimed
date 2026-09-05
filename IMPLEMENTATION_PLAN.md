# Implementation Plan — Era by Era

**Shape:** lay the foundations out once, then build **one complete era at a time** — its items, its
recipes, its quests — and check that era hangs together before starting the next.

Not horizontal layers. A vertical slice per era. Each era's items get authored while its chain is
being built, because that is when you know what it actually needs.

**Doctrine:** `INSTRUCTIONS.md`. **Item detail:** `BACKLOG.md`. **Live state:** `EXECUTION_STATE.md`.

---

## Phase 0 — Laid out ahead of time

These are planned across all ten eras *before* any era is built, so each slice knows its targets and
nothing gets authored twice or contradicts a later era.

| | What | Status |
|---|---|---|
| **0a** | **Worldgen** — Alfheim is `mythicbotany:alfheim`; 6 new biomes, 13-entry layer, tags, spawn handler | ✅ **BUILT** |
| **0b** | **Ore & cave viability** — livingrock is not in `#stone_ore_replaceables`, so almost nothing generates; no vanilla cave noise either | to do |
| **0c** | **Ladder spec** — for all 10 eras: tier material, station chain, step count (2n−3) | to do |
| **0d** | **Item inventory** — every intermediate across all eras, named and tiered. Built per era, but *listed* now so ids and tiers do not collide | to do |
| **0e** | **Structure inventory** — Greatbole pieces, Hollow Court pools, decay processor. Listed now, authored later | to do |

Phase 0 produces **plans and one worldgen datapack**. It does not produce items or recipes.

---

## Then: one era per slice

Every era runs the same five steps, in this order:

1. **Items** — author only what this era's chain needs, from the 0d inventory.
2. **Recipes** — the era's tier chain plus any reworks it depends on.
3. **Quests** — 22 quests (17 for Era I), tasks naming only items and recipes that now exist.
4. **Structures** — any this era introduces.
5. **Check** — internal consistency for this era only:
   - every quest task names a real item
   - every recipe input resolves
   - the era's tier material is reachable from the previous era's output
   - no quest depends on something no recipe produces

Then the next era. An era is not revisited unless a later one proves it wrong.

---

## Era I — The Ashen Grove

*Steps: 0 (base tier). Question: can anything still grow here?*

| Step | Artifact | Status |
|---|---|---|
| Items | **none custom** — Era I runs entirely on Botania and vanilla | n/a |
| Recipes | Pure Daisy → Dreamwood; Dreamwood twig / elven spreader / apothecary chain → `kubejs/server_scripts/21_elven_early_game.js` | **next** |
| Quests | 17 quests, Velrous voice → `config/ftbquests/quests/chapters/era_1.snbt` | ✅ **BUILT** |
| Structures | none | n/a |
| Check | every Era I quest task obtainable from Era I recipes | pending |

Era I deliberately introduces no custom items. It teaches the reversal using material that already
exists, which is also why it is the safest place to prove the pipeline.

## Era II — The First Light
*`alfheim_rune`. 1 step. Mana pool, spreader network, first generating flower, Runic Altar.*

## Era III — The Green Return
*`vanaheim_rune`. **3 steps** — the ladder proper begins. First custom tier material.*

## Era IV — The Long Silence
*`midgard_rune`. 5 steps. The gate opens outward; the reversal becomes visible.*

## Era V — The Deep Forges
*`nidavellir_rune`. 7 steps. Elementium from ore, Alfsteel.*

## Era VI — The Wild Marches
*`joetunheim_rune`. 9 steps. The frontier taken back — expeditions depart through the gate that
opened in Era IV. (Retargeted 2026-09-03: the gate is no longer an Era VI milestone.)*

## Era VII — The Burning Cradle
*`muspelheim_rune`. 11 steps.*

## Era VIII — The Frozen Archive
*`niflheim_rune`. 13 steps. `create:sequenced_assembly` starts carrying the depth.*

## Era IX — The Debt
*`helheim_rune`. 15 steps.*

## Era X — The Crown of Branches
*`asgard_rune`. 17 steps. Terrasteel, Mjöllnir, the restored city.*

Each of these expands into the same five-step slice when it is reached. Detail lives in
`alfheim_reclaimed_design/CAMPAIGN_ERAS.md`; this file only sequences.

---

## Cross-era work, folded into whichever era needs it first

| Work | Lands in |
|---|---|
| Gate reversal (`20_gate_reversal.js`) | Era IV — but **only after** Era I's `21_elven_early_game.js` exists and works |
| Native elven goods (Quartz, Elf Glass, Pixie Dust, Dragonstone) | Eras III–V, per `GATE_REVERSAL.md` §2.2.D |
| Spine interlock (Sourcelinks need Livingrock; Alfsteel needs a Brazier) | Era II and Era V |
| Gaia Guardian bypass — craft `botania:life_essence`, skip the boss | Era IX or X |
| Feysythia repair — MythicBotany calls for `feywild:lesser_fey_gem`, which no longer exists | Era I, with the other recipe work |
| Pack-wide gating — every support mod routes through a spine | per era, one mod family at a time |
| Hollow Court structures | Era I placement, authored across the whole build |
| Mine and Slash onboarding, c_races, book unification | before Era I ships |

## Final verification — once, at the end

Static: dependency ranges, JSON/SNBT parse, recipe resolution, quest task resolution, NBT bounds,
reachability. Runtime: pack loads, world generates Alfheim, play to the first Mana Pool, Era I
completes.

## Position

**Updated 2026-09-02, after the era verification pass.**

Phase 0a built and extended. **0b (ore and cave viability) is now done** — scarce copper, iron,
coal, redstone, lapis and diamond generate via a Forge biome modifier; caves were already carved.
0c/0d are effectively built: the ladder spec and the 80-item inventory exist in
`tools/items_manifest.json` and are generated into `kubejs/`.

All ten eras have items, recipes and quests authored, and all ten pass the consistency check
(`python tools/check_era.py --all` → 0 problems, 376 recipes, 215 quests, 80 items). Three real
defect families were repaired at their generators during that pass, including a free Elementium
duplication loop — see `EXECUTION_STATE.md`.

Era I's own soft-lock is cleared: it asked for copper, iron and Manasteel that the world did not
generate. It does now.

Elven villages (0e, partly) are built: MythicBotany's houses are decayed and clustered by datapack
override rather than by authoring NBT.

**Architecture revised 2026-09-02 — Alfheim left the Overworld slot.** Alfheim is now
`mythicbotany:alfheim`, the dimension MythicBotany ships, and the player spawns there;
`minecraft:overworld` is Midgard and is left vanilla. The world-preset override is deleted.

That change **closed four backlog items without building anything**: B-12 (prove the override —
the assumption was dropped), B-05 (Regions Unexplored now generates, in Midgard, where lush Earth
biomes belong), B-14 (there is only one Alfheim), and three of the four Continuity Works
change-asks. B-35 (Midgard) went from "author a dimension" to "it already generates". Everything
built earlier in the day carried over untouched, because it was keyed to **biome tags** rather than
to the dimension slot.

**Everything above is static.** Nothing has been observed running.

**Next: a fresh world for level 9** — the player wakes in Alfheim, on Alfheim terrain; copper and
iron are findable; elven villages generate ruined and clustered; respawn returns home. Then the
`Level.OVERWORLD` sweep (MineColonies first) and whether a Nether portal lit in Alfheim links to
anything. Then the Era IV gate (B-36).

## Deferred

Continuity Works (quarantined, CW-1 worldgen crash), memory re-tune, vanilla asset repair,
JourneyMap and BuildCraft RF disposition.
