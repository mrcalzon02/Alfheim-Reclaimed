# The Compendium — in-game documentation for everything this pack adds

**Role:** authoritative design record for the reference chapters.
**Status:** `draft` — generated and statically clean, never opened in a running game.
**Generator:** `tools/gen_compendium.py`.
**User instruction, 2026-09-03:** *"we need to make sure that we add documentation for each of all
of our custom features in our quests so that there's somewhere to look at to find all of the
various mechanics, ores, biomes and behaviors that we've been adding, other than just looking at
JEI and hoping they can figure it out."*

---

## 1. What JEI cannot tell you

JEI shows recipes. It is very good at that and it is blind to everything else this pack does.

It cannot say **where a bloom generates**, or that Palebloom needs only a stone pickaxe while
Rimebloom needs diamond. It cannot say that a raw bloom **will not smelt** until a Rite has closed
its pattern — a player will try, watch the furnace refuse, and conclude the pack is broken. It
cannot say that a small geode on the surface means a full one is **within 32 blocks below**, which
is the single most useful piece of knowledge in the crystal system. It cannot explain that mana,
Source and Aura are three unrelated systems, or that Aura is the one that punishes you.

None of that is recipe data. All of it is the pack.

---

## 2. Shape

A second FTB Quests **chapter group**, `Compendium`, sitting beside `Alfheim Reclaimed`. Six
chapters, 57 entries:

| Chapter | Entries | Covers |
|---|--:|---|
| **How This Pack Works** | 4 | Three energies · the reversal · why there is no metal · where petals come from |
| **The Twelve Blooms** | 12 | Depth, tier, reagents, what each renders into |
| **The Four Rites** | 4 | Station, mana cost, return, and that later Rites do not replace earlier ones |
| **Crystallised Mana** | 13 | Six crystals, seven geodes, rarities, and the surface-marker rule |
| **The Archive Groves** | 8 | Five petal-bearing leaves, three archive trees, drop rates |
| **The Sixteen Biomes** | 16 | What each place is, and what lives there |

Every entry is `optional: true` with a `checkmark` task and `shape: "gear"`, so the Compendium is
visually distinct from the campaign and **gates nothing**. A player who wants no manual can ignore
it entirely; the campaign does not notice.

`How This Pack Works` is `order_index: 5` in the file but is the chapter to read first — its four
entries are the ones that prevent wasted weeks.

---

## 3. The property that matters: facts are generated, prose is authored

Documentation rots because it is written once and the code moves. This cannot.

**Every number in the Compendium is read at generation time from the same manifest the
implementation is generated from** — `blooms_manifest.json`, `crystals_manifest.json`,
`groves_manifest.json`, and the generated biome JSONs and biome layer. Y-ranges, tool tiers, drop
rates, geode rarities, Rite reagents, spawn lists, biome counts: all of it is derived.

What is hand-written is the *explanation* — the sentences saying what a number means, why a bloom
resists heat, what to do when a spreader will not fire. A generator cannot supply those and should
not pretend to.

The consequence is concrete: **change a y-range in `blooms_manifest.json`, re-run the generators,
and the Compendium already says the new number.** There is no second place to remember to update,
because there is no second source.

---

## 4. Ownership

`config/ftbquests/quests/chapter_groups.snbt` is now owned by **`gen_compendium.py`**, which
declares both groups. `gen_quests.py` no longer writes it.

One file, one owner. Two generators writing one file is how a group silently disappears on
whichever ran last.

Note the standing boundary from `INSTRUCTIONS.md` §5: `config/ftbquests/` is authored by our
generators and then **normalised by the game**, which alphabetises keys and expands minified
objects on every world load. That churn is expected. Anything reading these files must read the
game's form, not the generator's — the lesson that cost 42 false failures in `check_era.py`.

---

## 5. Open

1. **Never opened in game.** `optional: true`, `shape: "gear"` and a second chapter group are all
   used from the schema FTB normalised for us, but no Compendium page has been rendered.
2. **57 entries is a first pass, not coverage.** The Rites, blooms, crystals, groves and biomes are
   documented; the tier ladder, the 80 intermediate items, Mine and Slash, and the colony are not.
3. **No entry explains the Void Verge's terrain**, only the biome. Whether that needs saying in
   game or is better discovered is a judgment to make after walking it.
4. **The Compendium and the Guide quests overlap by design.** `ERA_EXPANSION.md` §4 puts 137
   teaching quests *in* the campaign, timed to when a mechanic first matters; the Compendium is the
   same knowledge available *out* of sequence, for lookup. Keep the campaign Guides short and
   situational, and let the Compendium carry the full detail — if they start duplicating verbatim,
   the Guides should link rather than repeat.
