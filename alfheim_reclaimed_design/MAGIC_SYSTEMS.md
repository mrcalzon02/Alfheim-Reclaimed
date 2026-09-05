# The Magic Systems Index — and a quest chain for each, Eras I–III

**Role:** authoritative index of every magic system in the pack, its entry point, its current
quest coverage, and the chain it needs through the early game.
**Status:** Eras I–III authored 2026-09-04. Every system below now has quest coverage;
none remains at zero. Eras IV–X not started.
**Authority:** subordinate to `INSTRUCTIONS.md`. Implements §2.3 (everything routes through the
spines) at the level of *teaching*. Extends `ERA_EXPANSION.md`, which sets the quest budget.
**Asked for by the user, 2026-09-03:** *"an indexing of all of our different magic mods, and how
they all need their own sets of quest chains through all three early game eras."*

---

## 1. The finding this index exists to record

Every id below was read out of the installed jars. The coverage numbers were measured by walking
`ERA_I`, `ERA_II` and `ERA_III` in `tools/gen_quests.py` and counting task items by namespace.

> **Ten magic or magic-adjacent systems had zero quest coverage across all three early
> eras.** Measured 2026-09-03, closed 2026-09-04. §5 has the after figures.

The 66 quests of Eras I–III named items from six namespaces: Botania (17), Ars Nouveau (15),
MineColonies (5), MythicBotany (2), Mine and Slash (3), Farmer's Delight (1), plus vanilla and
three of our own. Everything else in the pack was unmentioned — a player was never told it
existed, never given a reason to open it, and never shown how it connected to the spines.

That is a teaching failure, not a content failure: the mods are installed and working. It is also
the direct cause of the problem `ERA_EXPANSION.md` §1 names — *"the pack currently teaches
nothing"* — being worse than that section estimated, because it counted quests rather than
systems.

---

## 2. The index

82 mods are installed. These are the ones that are magic, or that gate magic.

### 2.1 The load-bearing three (INSTRUCTIONS.md §2)

| System | Mod id | Entry point | Era I–III coverage |
|---|---|---|--:|
| **Spine of Leaf** | `botania` | `botania:apothecary_livingrock`, petals | 17 → **27** |
| **Spine of Leaf** | `mythicbotany` | the Rites, `mythicbotany:alfheim_rune` | 2 → **4** — still thin, see §5 |
| **Spine of Song** | `ars_nouveau` | `ars_nouveau:novice_spell_book`, Source | 15 → **23** |
| **The Wound** | `mmorpg` + 3 | levels, orbs, gear, maps | 3 → **8** across the family |

### 2.2 The traditions that had no chain — all now authored, Eras I–III

| System | Mod id | Verified entry items | Character |
|---|---|---|---|
| **Nature's Aura** | `naturesaura` | `naturesaura:eye`, `gold_fiber`, `nature_altar`, `ancient_sapling`, `aura_cache` | Ambient, per-chunk, and the only system that **punishes the land** |
| **Occultism** | `occultism` | `occultism:chalk_white`, `candle_white`, `burnt_otherstone`, `taboo_book`, `book_of_binding_foliot` | Summoning, pentacles, bound spirits doing work |
| **Feywild** | `feywild` | `feywild:feywild_lexicon`, `fey_dust`, `fey_gem`, `fey_altar`, `empty_summoning_scroll`, `pixie_orb` | Bargains with pixies; courts and seasons |
| **Iron's Spells** | `irons_spellbooks` | `irons_spellbooks:arcane_debris`, `arcane_essence`, `copper_spell_book`, `common_ink`, `blank_rune`, `arcane_anvil` | Classic schools-and-scrolls casting |
| **Create: Wizardry** | `create_wizardry` | `create_wizardry:mana_bottle`, `mana_bucket`, `channeler`, `mithril_nugget` | **The Botania-mana ↔ Create bridge** |
| **Occult Engineering** | `occultengineering` | `occultengineering:copper_chalk`, `pentacle_altar`, `otherworld_detector` | **The Occultism ↔ Create bridge** |

### 2.3 The Wound is four mods, not one

Measured while indexing: `mmorpg`, `dungeon_realm`, `the_harvest` and `ancient_obelisks` all
ship a "Dungeon Relic" and all feed one expedition economy, with `library_of_exile` underneath.
Treating Mine and Slash as a single mod is why its coverage looked thin rather than absent.

| Mod | Provides |
|---|---|
| `mmorpg` | Levels, gear, talents, currency orbs, `mmorpg:map`, `mmorpg:map_bag` |
| `dungeon_realm` | **`dungeon_realm:map_device`** — the block that opens the dungeon dimension — plus `home_pearl`, `relic_key` |
| `the_harvest` | `the_harvest:harvest_map`, a distinct expedition type |
| `ancient_obelisks` | `ancient_obelisks:obelisk_map`, wave-defence encounters |

> **Correction recorded here because it changed a gate.** B-57 originally stated that the Map
> Device was `mmorpg:teleporter` and had no recipe anywhere, making expeditions unreachable.
> Wrong on both counts. `mmorpg:teleporter` is legacy and uncraftable; the working block is
> `dungeon_realm:map_device`, and the jar crafts it from **one diamond over one stone at a
> vanilla crafting table**. Expedition access — a major capability — cost less than a stone
> pickaxe and touched no spine at all, in direct violation of §2.3. Re-laid on the Runic Altar
> in `06_expedition_gate.js`, with Captain Orenvel granting one outright as the second route.

### 2.4 Adjacent, deliberately not given chains

| Mod | Why not |
|---|---|
| `knightquest` | 201 items of gear, bosses and essences. RPG combat content, not a magic system; it belongs to the Wound's reward vocabulary. |
| `infectious`, `zombie_variants`, `eggszombies` | Mob content. No player-facing system to teach. |
| `create_*` (cannons, tubes, diesel, cola) | Industry. Routes through a spine per §2.3, but that is recipe gating (B-16), not a magic chain. |
| `modonomicon`, `patchouli` | Book engines other mods render into. No content of their own. |

---

## 3. The doctrine question this raises, and its answer

`INSTRUCTIONS.md` §2 is explicit that the pack has **exactly three** load-bearing systems and
"every other mod is support". Giving six more systems their own quest chains could look like
promoting them to spines. It is not, and the distinction has to hold in the authoring:

- A spine **gates eras**. Nothing else does, and none of these chains may.
- A tradition chain **teaches a system and routes its entry cost through a spine**. It ends in a
  capability, never in an era advance.

So every chain below obeys one rule: **its first real cost is paid in spine materials.** You do
not get a Fey Altar without petals; you do not get chalk without mana-worked metal. That is §2.3
applied to teaching rather than to recipes, and it is what keeps six new chains from diluting the
Twin Spines into eight.

---

## 4. The chains, Era by Era

Each chain is 3–5 quests per era. The shape is deliberate and identical across systems:
**Era I introduces and gives one artifact · Era II makes it produce · Era III makes it automate
or deepen.**

### 4.1 Nature's Aura — *the land is not a resource*

| Era | Chain |
|---|---|
| **I** | The **Environmental Eye** (`naturesaura:eye`) — craft it and *look*. The spawn zone reads as depleted, which is the point: the Ashen Grove is not flavour text, it is a measurable state. Ties to B-22. |
| **II** | Gold Fiber and the **Natural Altar** — the first infusion. Aura is spent from the chunk you stand in, and it does not come back on its own. |
| **III** | The **Aura Cache**, ancient saplings, and recovery — planting to restore what you drew down. The only system in the pack where overuse degrades the world. |

**Spine cost:** the Eye's first use is taught alongside Era I's mana lesson; the Altar's first
infusion requires a Botania petal.

### 4.2 Occultism — *someone else can do the work*

| Era | Chain |
|---|---|
| **I** | Otherstone and the taboo book — find the residue of something that was summoned here before. Reading, not doing. |
| **II** | **Chalk** and the first pentacle. White chalk, one glyph, one candle. Spirit Fire. |
| **III** | A bound **Foliot** — the first spirit that works for you. Crushing, and the beginning of automation that is not a machine. |

**Spine cost:** chalk needs mana-worked metal, so the pentacle is downstream of a working Mana Pool.

### 4.3 Feywild — *everything here is a bargain*

| Era | Chain |
|---|---|
| **I** | **Fey Dust** — offer cookies to a pixie. The cheapest magic in the pack and the one that teaches the pack's tone: you ask, you do not take. |
| **II** | The **Fey Altar** and the Fey Gem. Five ingredients, always five — see B-42. |
| **III** | Summoning scrolls and the courts; **Feysythia**, which is where Feywild and MythicBotany meet. |

**Spine cost:** the Altar's recipes are petal-fed; Feysythia is a Petal Apothecary flower.

### 4.4 Iron's Spells 'n Spellbooks — *the human tradition*

| Era | Chain |
|---|---|
| **I** | **Arcane Debris** in stone, and Arcane Essence from it. Found, not made — this is Midgard's magic, and it is lying in the ground here as wreckage. |
| **II** | The **Copper Spell Book**, common ink, a first scroll. Schools and cooldowns. |
| **III** | The **Arcane Anvil**, blank runes, upgrading. |

**Narrative weight:** this is the *human* system in an elven pack. Its Guides should say so — the
player is learning the magic of the world that died, which is exactly the pack's premise inverted.

### 4.5 Create: Wizardry — *the bridge, and the §2.3 keystone*

| Era | Chain |
|---|---|
| **II** | **Bottle of Mana** (`create_wizardry:mana_bottle`) — Botania mana made portable, and the moment Create stops being a separate world. |
| **III** | The **Channeler** and Bucket of Mana; Mithril. Mana as a Create fluid. |

**Why this matters more than its size:** §2.3 requires every progression-relevant Create recipe to
route through a spine. This mod is the *mechanical* means to do that, not just the narrative one.
It should be taught before B-16's pack-wide gating lands, so the gating reads as a system rather
than as an arbitrary tax.

### 4.6 Occult Engineering — *the second bridge*

| Era | Chain |
|---|---|
| **III** | The **Otherworld Detector** and the **Pentacle Altar** — Occultism's rituals mechanised. Depends on 4.2 reaching a bound spirit first. |

Era III only. It has no meaning until Occultism works.

### 4.7 The Wound — *four mods, one economy*

| Era | Chain |
|---|---|
| **I** | Levels, the first orb, the first rolled gear. Why a mob two levels up is not "harder". |
| **II** | The talent tree and the commitment it demands; the first `mmorpg:map`. |
| **III** | The **Map Device**, now Runic-Altar-gated (§2.3); the first expedition; `the_harvest` and `ancient_obelisks` as distinct expedition types. |

---

## 5. What this costs in quests

`ERA_EXPANSION.md` §3 budgets 60 / 70 / 68 for Eras I–III. These chains fit inside that budget
rather than adding to it, because they are what the Stage, Practice and Guide slots were always
meant to contain:

| Era | Chains active | Authored | Budget |
|:--:|---|--:|--:|
| I | Leaf, Song, Aura, Occultism, Feywild, Iron's, Wound | **60** | 60 |
| II | + Create: Wizardry | **70** | 70 |
| III | + Occult Engineering | **69** | 68 |

**Measured coverage after authoring** — task items naming each system across Eras I–III:

| System | Tasks | | System | Tasks |
|---|--:|---|---|--:|
| Botania | 27 | | Iron's Spellbooks | 9 |
| Ars Nouveau | 23 | | Occultism | 8 |
| Nature's Aura | 9 | | Feywild | 6 |
| MythicBotany | 4 | | Create: Wizardry | 4 |
| Mine and Slash | 4 | | Occult Engineering | 2 |
| Dungeon Realm | 2 | | The Harvest | 1 |
| Ancient Obelisks | 1 | | | |

**MythicBotany at 4 is the thinnest real gap left.** It is half the Spine of Leaf and is carried
mostly by the Rites, which are taught through Botania stations rather than named directly. Worth
a pass before Era IV.

---

## 6. Instructional depth — the coverage standard

Set by the user 2026-09-04, in two halves. Both are measured by `tools/check_coverage.py`.

**Coverage.** *Every intended processing step for an ore, a contributive item or a componentary
item should have a quest covering the process by which it is created, so that every contributive
processing step has a quest charting progress from a raw ingredient to a useful component or a
useful output.*

**Ordering.** *When a recipe requires a method, verify that the method was unlocked in some
preceding step — so recipes are used consecutively rather than requiring methods you have not yet
unlocked.*

### 6.1 What the pack actually contains

164 contributive processing steps; 286 alternate uses, counted separately because a use is not a
step on the way to anything.

The standard is ambiguous by a factor of ten and the difference is worth ~70 quests, so the tool
reports three readings rather than assuming one:

| Reading | Rule | Gap |
|---|---|--:|
| Per item | Every output of every step gets a quest | **106** |
| Per process | One quest per named process, however many materials | **39** |
| **Hybrid** *(recommended)* | Per item for ladder steps, per process for the Rites | **39** |

**Why hybrid.** A ladder step is a genuinely distinct transformation with its own output, so it
earns a quest. The Rites are not a chain — steeping, quickening, grafting and deepening are four
*parallel* routes from raw bloom to quickened bloom at improving yields, and applying the Steeping
to a twelfth bloom teaches nothing the first eleven did not. The blooms want an introduction each,
which the Compendium's *Twelve Blooms* chapter already provides; they do not want a process quest
each.

### 6.2 Where the gap is

| Era | I | II | III | IV | V | VI | VII | VIII | IX | X |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Ladder steps | 0 | 0 | 3 | 5 | 7 | 9 | 11 | 13 | 15 | 17 |
| **Quests to add** | 1 | 1 | 0 | 0 | 1 | 3 | 5 | 7 | 10 | 11 |

**36 of the 39 sit in Eras VI–X.** Eras I–III are effectively complete against this standard —
they were rebuilt around it. The gap is the late-game tier ladder: every 2n−3 step exists as a
recipe and has no quest, because Eras IV–X are still the 22-quest chapters `gen_quests_bulk.py`
emitted before the expansion.

### 6.3 Which mods need depth

Steps whose station belongs to each mod, and how many are quest-covered:

| Station namespace | Steps | Quested | Gap |
|---|--:|--:|--:|
| Botania | 76 | 23 | **53** |
| vanilla | 29 | 11 | 18 |
| MythicBotany | 17 | 5 | **12** |
| Ars Nouveau | 13 | 7 | 6 |
| Occultism | 5 | 0 | **5** |
| Nature's Aura | 7 | 3 | 4 |
| Create | 7 | 4 | 3 |
| Feywild | 2 | 2 | 0 |

Botania's 53 is inflated by the Rites (12 blooms × 4 routes all run on Botania stations) and
mostly collapses under the hybrid reading. **The honest gaps are MythicBotany and Occultism**:
MythicBotany is half a spine and is the station for the Deepening and the whole late ladder;
Occultism has five steps and **zero** quest coverage of any of them.

### 6.4 Method ordering — 13 violations, two families

| Method | Eras | Station | Status |
|---|---|---|---|
| `botania:elven_trade` | 4, 6, 7, 8, 9, 10 | `botania:alfheim_portal` | **never taught** |
| `create:milling` / `mixing` / `pressing` / `sequenced_assembly` | 5, 7, 8, 9, 10 | millstone, basin, press, deployer | **never taught** |

Both are exactly the failure the user named: recipes requiring a method the player has not
unlocked.

1. **The Alfheim Portal is never granted.** Six eras of `elven_trade` recipes depend on it and
   B-36 — the Era IV gate — is unbuilt. Every elven trade in the pack is currently unreachable.
2. **No Create machine is taught in any quest.** The ladder uses Create stations from Era V
   onward and Create is never introduced. This is what `MAGIC_SYSTEMS.md` §4.5 anticipated:
   Create: Wizardry should be taught *before* B-16's pack-wide gating lands, or the gating reads
   as an arbitrary tax on machines the player was never handed.

`ars_nouveau:crush` has no station mapped and is unchecked — one method's worth of blind spot.

---

## 7. Open

- **B-55 still governs regeneration, not authoring.** See its entry: the risk is regenerating
  *after players have played*, not authoring before release. Authoring the early game now is the
  "author once" step under either of B-55's two resolutions.
- **Knight Quest** has 201 items and no chain. If it is staying, it needs a disposition — reward
  vocabulary for the Wound, or removal per §2.3's "candidate for removal, not for an exception".
- **Iron's Spellbooks vs Ars Nouveau** overlap as casting systems. The fiction separates them
  (elven Song vs human wreckage) but the mechanics compete. Worth a decision before Era IV.
