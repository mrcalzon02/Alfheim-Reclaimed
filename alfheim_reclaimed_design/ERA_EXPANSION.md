# Era chapter expansion — 215 quests to 660

**Role:** authoritative design record for the campaign's three-fold expansion.
**Status:** `draft` — designed, not yet generated.
**Authority:** subordinate to `INSTRUCTIONS.md` and `CAMPAIGN_ERAS.md`. Extends the latter's
§2 quest budget; does not replace its era themes or rune capstones.
**Asked for by the user, 2026-09-03:** triple each era chapter using *"filler quests, intermediate
stages, guides on how various magical processes work, instructional guidance on how to use the
various magical systems, with a special focus on the early chapters."*

---

## 1. The gap this closes

The pack currently teaches nothing. 215 quests across ten eras name objectives — *make a Mana
Spreader*, *build a Runic Altar* — and assume the player already knows what those are and why
they behave the way they do.

That assumption fails badly here for a specific reason: **this pack inverts Botania.** A player
who has played Botania before is not merely un-helped by their experience, they are actively
misled — Livingwood is gone, the gate runs backwards, and metal comes out of a flower pot. A
player who has *not* played Botania has three unfamiliar magic systems, three different energy
types, and no in-game text explaining any of them.

The expansion is therefore not padding. The new quests are the manual.

---

## 2. Targets

Three times the current length, weighted toward the eras where the player knows least.

| Era | Now | New | × |
|:--:|--:|--:|--:|
| I — The Ashen Grove | 17 | **60** | 3.5 |
| II — The First Light | 22 | **70** | 3.2 |
| III — The Green Return | 22 | **68** | 3.1 |
| IV — The Long Silence | 22 | **66** | 3.0 |
| V — The Deep Forges | 22 | **66** | 3.0 |
| VI — The Wild Marches | 22 | **66** | 3.0 |
| VII — The Burning Cradle | 22 | **66** | 3.0 |
| VIII — The Frozen Archive | 22 | **66** | 3.0 |
| IX — The Debt | 22 | **66** | 3.0 |
| X — The Crown of Branches | 22 | **66** | 3.0 |
| **Total** | **215** | **660** | **3.07** |

> **Built 2026-09-04 — Eras I–III are done, and they were rebuilt around systems rather
> than around a number.** Actuals: **Era I 60** (target 60), **Era II 70** (target 70),
> **Era III 69** (target 68). 66 → 199 across the early game.
>
> The shape changed on the user's instruction — *"an indexing of all of our different
> magic mods, and how they all need their own sets of quest chains through all three
> early game eras."* Measuring that first found the real defect: **ten magic systems had
> zero quest coverage across all three eras.** See `MAGIC_SYSTEMS.md`, which is now the
> authority on what each chain teaches; this file remains the authority on the budget.
>
> Era II had **no Guides at all**, which meant §4.1's three-energies disambiguation — the
> pack's worst confusion, by this document's own assessment — was never taught anywhere.
> It now has 19.

Every existing quest is **retained** and its stable key is unchanged, so the generator emits the
same id it emitted before. Expansion is purely additive *in the source*.

> **⚠ CORRECTED 2026-09-03 — regeneration is NOT progress-safe, and this was measured.**
>
> An earlier version of this section claimed that a stable key means "in-progress player completion
> survives regeneration." **That is false**, and the evidence is direct.
>
> Comparing the chapter the game had normalised at session start against what `gen_quests.py`
> produces now:
>
> | Object | On disk (game's form) | Generator emits | |
> |---|---|---|---|
> | `era_1` chapter | `5F04313E8BBC9035` | `978E4F51D53B8576` | **differs** |
> | `shelter` quest | `29569136F0E03D89` | same | matches |
> | `shelter` task | `3C2CC4C0DA24E952` | `9D8955D226D47AC3` | **differs** |
> | `spiders` quest | `5E4E351D50C8970C` | `F922CD7718A5E39A` | **differs** |
> | `spiders` task | `5877BEC973773EAE` | same | matches |
>
> The divergence runs in both directions and is not explained by any key rename — `shelter` keeps
> its quest id but loses its task id; `spiders` does the reverse. Something in the load/normalise
> path reassigns a subset of ids, and our generator does not know which.
>
> **This is not hypothetical.** `saves/New World/ftbquests/<uuid>.snbt` records real progress keyed
> by id, and its `started` set contains `5F04313E8BBC9035` — the era_1 chapter. After regeneration
> that id exists nowhere in `config/ftbquests/`, so that progress is **orphaned**.
>
> **What it costs today: nothing.** Level 11 is deferred, the quests have never been played, and the
> affected save is a two-quest test world. **What it would cost after release: everything a player
> had done.**
>
> **B-55 must be settled before the expansion continues past Era I.** Authoring 660 quests on the
> assumption that regeneration is safe, and discovering otherwise after people have played, is the
> most expensive version of this mistake.

---

## 3. Quest taxonomy

Six kinds. The mix shifts across the campaign: teaching front-loaded, chain depth back-loaded.

| Kind | Task type | Purpose |
|---|---|---|
| **Guide** | `checkmark` | Pure instruction. No material cost. Explains one mechanic in Velrous's voice. |
| **Stage** | `item` | One intermediate step of a chain — the Rites' Quickened items, the tier ladder's steps. |
| **Practice** | `item` / `kill` | Apply what a Guide just taught, at trivial cost. Proves the lesson landed. |
| **Flavour** | mixed | Settlement, building, exploration, colony. The world made inhabited. |
| **Wound** | `kill` / `item` | Mine and Slash — combat, expedition, reward. |
| **Capstone** | `item` | The era's rune. Unchanged from `CAMPAIGN_ERAS.md`. |

| Era | Guide | Stage | Practice | Flavour | Wound | Cap | Total |
|:--:|--:|--:|--:|--:|--:|--:|--:|
| I | 20 | 12 | 9 | 12 | 7 | 0 | 60 |
| II | 19 | 16 | 11 | 14 | 9 | 1 | 70 |
| III | 17 | 16 | 11 | 14 | 9 | 1 | 68 |
| IV | 15 | 16 | 11 | 14 | 9 | 1 | 66 |
| V | 13 | 18 | 11 | 14 | 9 | 1 | 66 |
| VI | 12 | 18 | 12 | 14 | 9 | 1 | 66 |
| VII | 11 | 19 | 12 | 14 | 9 | 1 | 66 |
| VIII | 11 | 19 | 12 | 14 | 9 | 1 | 66 |
| IX | 10 | 20 | 12 | 14 | 9 | 1 | 66 |
| X | 9 | 20 | 13 | 14 | 9 | 1 | 66 |
| **Total** | **137** | **174** | **114** | **138** | **88** | **9** | **660** |

Guides fall 20 → 9 as the player stops needing them. Stages rise 12 → 20 as chains deepen. This
is the shape the user asked for, expressed as a curve rather than a slogan.

---

## 4. The curriculum — what the 137 Guides teach

Each Guide is one mechanic, one screen of text, one checkmark. They are ordered so that no Guide
depends on a concept a later Guide introduces.

### 4.1 The three energies — the pack's worst confusion, taught first

Alfheim Reclaimed runs **three** unrelated energy systems that look alike and behave nothing alike.
Nothing in any mod explains the difference, and every one of them is load-bearing here.

| Energy | Mod | Moves by | Stored in | Runs out? |
|---|---|---|---|---|
| **Mana** | Botania | Spreader bursts, line of sight | Pools, tablets | Generated by flowers, consumed |
| **Source** | Ars Nouveau | Relays, wireless within range | Source Jars | Generated by Sourcelinks |
| **Aura** | Nature's Aura | Ambient, per-chunk | The chunk itself | **Depletes the land** if overdrawn |

Three Guides in Era II do nothing but disambiguate these. The Aura entry matters most: it is the
only one of the three that *punishes* the player environmentally, and Era I's spawn zone is
already aura-depleted by design.

### 4.2 Spine of Leaf — Botania and MythicBotany (≈52 Guides)

*Era I:* what mana is and why it is a **fluid you move, not a number you have** · the Pure Daisy
transmutes blocks in place · petals, and where they come from · the Petal Apothecary is your first
station · **the Ashen Grove has no metal, and why** · reading a bloom in stone · **Rite I: the
Steeping** · why heat alone does nothing to a bloom · Dreamwood, and the thing this pack changed.

*Era II:* generating flowers versus functional flowers — the distinction that defeats most new
players · Mana Spreader line of sight, and why yours is not firing · burst mana loss over distance
· the Mana Pool, and the Diluted Pool trap · Mana Tablets · the Runic Altar · runes are catalysts,
not ingredients · **Rite II: the Quickening** · mana is now your smelter.

*Era III–V:* Agricarnation and passive growth · the Hydroangeas trap · Floral Fertilizer ·
**Rite III: the Grafting** · byproducts and why yield beats speed · the Mana Infuser · Alfsteel ·
**Rite IV: the Deepening** · Elementium is an *ore* here, not a trade good.

*Era VI–X:* Terrasteel needs three imports — the trade route explained as mechanics · the Terra
Plate · Gaia preparation · Manaweave · the rune rituals · Mjöllnir's true cost.

### 4.3 Spine of Song — Ars Nouveau (≈45 Guides)

*Era I–II:* what Source is · the Imbuement Chamber, your first Source work · Sourcelinks generate,
they do not store · the Agronomic Sourcelink eats your farm · Source Jars and Relays · **how a
spell is assembled: Form → Effect → Augment** · the Scribe's Table · your first three glyphs ·
casting, and spell mana cost.

*Era III–V:* the Ritual Brazier · Ritual of Growth · familiars, and what a Starbuncle actually does
· the Enchanting Apparatus · Arcane Pedestals and placement · Amplify and Pierce · the Wixie
Cauldron automates crafting · Warp Scrolls and the Relay: Warper.

*Era VI–X:* ritual chaining · Caster Tomes · Archmage progression · the full glyph library ·
automated enchanting · Scry rituals for lost sites.

### 4.4 The Wound — Mine and Slash (≈18 Guides)

Levels and why a mob two levels up will kill you · gear rarity and stat rolls · **currency orbs,
one Guide per orb that matters** · the talent tree, and committing to one · Adventure Maps as
instanced expeditions · map tiers and gear checks · gem socketing · uniques.

### 4.5 Support (≈22 Guides)

MineColonies: the builder loop, and why your builder is idle · request fulfilment · Farmer's
Delight cooking · The Harvest crops · Occultism ritual basics · Nature's Aura depletion and
recovery · Create, and the rule that every progression recipe in it routes through a spine ·
Domum Ornamentum · Structurize.

---

## 5. Layout

60–70 quests per chapter needs a deliberate arrangement or the map becomes unreadable.

**Lanes by track, columns by progression.** `x` advances with dependency depth; `y` is the track:

| `y` | Lane |
|--:|---|
| −6 … −5 | Guide (top band, visually separate — teaching sits above doing) |
| −4 … −2 | Spine of Leaf: Stage + Practice |
| −1 … +1 | Spine of Song: Stage + Practice |
| +2 … +3 | Support / Flavour |
| +4 … +5 | The Wound |
| centre-right | Capstone |

Guides carry `shape: "gear"` and are visually distinct from objective quests. Guides depend only
on the Guide before them, so the teaching band reads left-to-right as a syllabus and never blocks
material progress.

**Gate rule unchanged** (`CAMPAIGN_ERAS.md` §2): the Capstone requires both spine tracks complete.
Guides, Practice, Flavour and Wound quests never gate the Capstone — a player who wants to skip
the manual can.

---

## 6. Generation

`tools/gen_quests.py` currently hand-declares Eras I–III as Python tuples and
`gen_quests_bulk.py` emits IV–X. 660 quests will not be maintained as literal tuples.

**The change:** move era content into `tools/quests/era_N.py` declarative modules, and give the
generator a `guide()` helper so a Guide is one call:

```python
guide('mana_is_a_fluid', 'Mana Is Not A Number',
      "You will hear it called a resource. It is not...",
      after='what_the_grove_was')
```

Ids stay derived from `qid(era_key, stable_key)`, so the **generator** is deterministic: the same
key always produces the same id, and adding quests never disturbs the ids of existing ones.

**That is a property of the generator, not of the round trip.** See the correction in §2: the game
reassigns a subset of ids when it normalises the chapter files, so generator-determinism does not
by itself make regeneration progress-safe. Do not restore the stronger claim without evidence from
a booted game (B-55).

`check_era.py` gains three invariants:

- **E14** — every Guide's `after` resolves to a quest in the same chapter (no dangling syllabus).
- **E15** — no quest depends on an item whose chain root is not traceable to ground
  (`ORE_SUPPLEMENTATION.md` §7 step 6, shared implementation).
- **E16** — chapter totals match §2's table exactly, so drift is caught by the checker rather than
  by counting.

---

## 7. Authoring order

`INSTRUCTIONS.md` §6.4 binds: **one chapter at a time.** Author, load, verify in-game, then move
on. The schema is now known — the game has normalised all ten chapters once, so its canonical form
is established — but 660 quests against an unplayed layout is exactly the failure that rule exists
to prevent.

1. **Era I → 60.** Ships with the Rite I recipes and the three Era I blooms. This is the chapter
   that proves the whole design: if the Steeping does not teach itself here, nothing later will.
2. **Era II → 70.** The three-energies Guides, Rite II.
3. **Era III → 68.** Rite III, automation.
4. **Era IV → 66.** The gate chapter. The pack's biggest reveal, and `alfheim:gatewrought_cord`.
5. **Eras V–X.** Mechanical; the ladder already exists.

---

## 8. The gate decision — settled, nothing blocked

**Settled by the user 2026-09-03: the gate opens in Era IV.** *"Record the earlier gate as when
the gate opens."* The 2026-09-02 instruction that the portal is *"completable only in Era VI"* is
**withdrawn**. Full record and the six documents it corrects: `CAMPAIGN_ERAS.md` §3, Era IV.

Consequences for this document:

- **Nothing is blocked.** The 132 quests in Eras IV and VI are eligible, and §7's authoring order
  runs start to finish without a decision gate.
- **Era IV is the gate chapter.** Its Guides carry the pack's biggest reveal — that Botania's
  trade runs backwards here — and its capstone material is `alfheim:gatewrought_cord`.
- **Era VI is the frontier chapter.** Expeditions depart *through* a gate the player has used
  since Era IV. Its Guides teach expedition logistics, not portal construction.
- **§7 step 5 is deleted.** "Eras IV and VI last" was only ever a consequence of the block; they
  now author in their natural position.
