# Liquid Bifrost — the bridge between the magic systems

**Role:** design record for `alfheim:liquid_bifrost`, its four-tier refinement chain, and the
conversions that connect the pack's magic systems to each other.
**Status:** `built` — generator, fluid, items, art, tags, recipes, worldgen, the Era VII
renewable route and nine quests all in place; runtime-verified on 2026-09-04.
**Authority:** subordinate to `INSTRUCTIONS.md`. Sits alongside `MAGIC_SYSTEMS.md` (which
indexes the systems this bridges) and `ORE_SUPPLEMENTATION.md` (which owns the blooms and
geodes this deliberately is *not*).
**Owner:** `tools/gen_liquid_bifrost.py`. Everything below is generated; nothing is hand-edited.

**Asked for by the user, 2026-09-04:**

> *"Let's call it 'liquid bifrost' pools as a new surface feature for the lakes, as a new liquid
> material. It should have the same similar colour tuning properties as the bifrost blocks, and
> it should have a crystallized form and a condensed form and a refined form and then a
> distilled form as the final product, and it should be useful for converting to the various
> types of mana essence from the different magical mods."*

---

## 1. The gap this closes

`MAGIC_SYSTEMS.md` indexes **thirteen** magic systems. Each has its own currency — Botania
mana, Ars source, Occultism essence, Iron's arcane, Nature's Aura — and **none of them talk to
each other**. A player forty hours into Botania who opens Ars Nouveau starts from nothing.

That is what makes a thirteen-system pack read as thirteen packs stapled together. Liquid
Bifrost is the one material every system will accept.

**It is deliberately a bad exchange rate.** It is not a way to skip a system; it is a way to
carry a little momentum into one. `INSTRUCTIONS.md` §2.3 keeps power on the spine, and a
universal currency is exactly the thing that could take it off.

---

## 2. Why a fluid, and why lakes

The user asked for pools, and that is the right shape.

`ORE_SUPPLEMENTATION.md` already owns twelve blooms and seven geodes, and **all of them are
dug**. Alfheim's entire resource vocabulary was one verb. A surface liquid is a different
verb — found by looking rather than by mining — and it gives the lake biomes and the Void Verge
something they are uniquely good at.

| | |
|---|---|
| **Feature** | `minecraft:lake`, the same one vanilla uses for water and lava lakes, so the pools carve a basin and sit in the terrain rather than being a disc pasted on top |
| **Barrier** | `botania:livingrock`, the dimension's own stone |
| **Rarity** | **1 in 40 chunks** — rarer than the geodes after their same-day retune (1 in 13–15) |
| **Biomes** | `alfheim_lakes`, `mana_fen`, `hollow_marches`, `void_verge`, `bloomfall_vale` |

Five biomes, not sixteen. A bridge material that turns up everywhere stops being a reason to go
anywhere.

### 2.1 The colour

Botania's bifrost cycles the rainbow **per frame**. A fluid tint is a single ARGB and cannot
cycle, so the fluid takes bifrost's *character* rather than its animation: a bright pale cyan
(`0xB4F0FF`) reading violet where it flows — bifrost at any one instant.

`luminosity 12`, not 15: bright enough to light its own pool and be visible across a lake at
night, dim enough that a player cannot farm it as free full-brightness lighting.

---

## 3. The chain

Four tiers, in the user's own words and order. **Each step uses a different method, and every
method is one the player has already been taught by that era** — the ordering standard the user
set on 2026-09-04: *"when a recipe requires a method it should verify that you have previously
unlocked that method in some preceding step"*. Nothing here introduces a new machine.

| Tier | Era | Station | Why that station |
|---|---|---|---|
| **Crystallized** | II | Petal apothecary | The first station the pack teaches, so a whole new material costs nothing not already built |
| **Condensed** | II | Mana infusion | Botania's own, already on the ladder |
| **Refined** | III | Alfheim infuser | MythicBotany's, and it sits **behind the gate** — so this tier is *unreachable* until Era III on the spine, not merely expensive |
| **Distilled** | III | Runic altar | The last station before Era IV |

The apothecary **consumes its reagent**, bucket and all, so tier 1 yields 4 to pay for the iron.
Pouring the pool in is also simply what the recipe should look like.

The chain is split across two **era-scoped** files, `18_era2_` and `19_era3_`, because
`check_coverage.py` reads a recipe's era from `_era<N>_` in its filename and can check nothing
without it. Shipping it as one un-scoped file made the coverage report say so directly: *"24
contributive step(s) belong to no era ... they cannot be checked until they are era-scoped."*

---

## 3.1 The renewable route — Era VII

**Asked for by the user, 2026-09-04:** *"We also need a high level renewable bifrost recipe. One
would think using the mixer, with say water and a renewable crystal based ingredient."*

Until this existed, Liquid Bifrost was strictly **finite**. Pools generate at 1-in-40 chunks and
do not come back, so the bridge between thirteen magic systems was a consumable that ran out — a
player who spent their last bucket on the wrong conversion had permanently lost access to a
system. That is a worse failure than a poor exchange rate, because it is **invisible until it
has already happened**.

```
create:mixing, heated
   2 x #alfheim:crystal_shards
   1 x botania:mana_powder
   500 mB minecraft:water
   -> 250 mB alfheim:liquid_bifrost
```

**Era VII is not arbitrary.** `cr_mix` (`create:basin`) is first taught by the Era VII ladder, so
this is the earliest era that can require a mixer without violating the ordering rule. It is also
the right *power* level: by Era VII the player has a working Create setup, and the renewable route
should be a reward for that infrastructure rather than a way around the pools in the early game.

**What makes it renewable.** `#alfheim:crystal_shards` holds exactly the six crystals that have a
budding block, so every shard in the tag regrows. `frost_shard` is deliberately **not** in that
tag — it has no budding form — which means the tag is already precisely *"renewable crystal"* and
this recipe inherits the guarantee instead of restating it. Water is water; mana powder is a
flower.

The mana powder is the third ingredient for a reason. Crystal and water alone make a slurry; what
makes bifrost is the *charge*. It also keeps this honest as a high-level recipe: it costs a mana
economy, not two rocks.

**It is not cheaper than finding a pool, and was never meant to be.** Four mixes to the bucket —
8 shards and 2 mana powder. It is only *endless*, which is a different and better property.

---

## 4. The conversions

One distilled bifrost into each system's **entry** currency, never its advanced one.

| System | Yields | Note |
|---|---|---|
| Botania | 6 × `mana_powder` | The cheapest thing mana buys — a starter, not a shortcut |
| Ars Nouveau | 3 × `source_gem` | Three is one spell, not a spellbook |
| Occultism | 2 × `otherworld_essence` | The one system that should stay expensive |
| Iron's Spellbooks | 4 × `arcane_essence` | |
| Nature's Aura | 4 × `gold_leaf` | The aura chain's first consumable |
| Botania (advanced) | 1 × `mana_pearl` | The single advanced conversion, and it costs **4** distilled |

Every id was checked against `tools/registry_items.json` — the ground-truth dump from a running
server — **not** against a lang file. That distinction has already cost this project eleven
recipes.

---

## 4.1 Quests

Nine, across three eras, meeting the user's coverage standard that *"every intended processing
step ... should have a quest covering the process by which that is created"*.

| Era | Quests |
|---|---|
| **II** | *The Bridge, Poured Out* (find a pool) → *Give It A Shape* → *Press Them Together* |
| **III** | *Take The Rest Out* → *The Last Step* → *One Material, Every Road* |
| **VII** | *A Crystal That Grows Back* → *Stop Going To The Lakes* → *Spend It Freely Now* |

Era II opens with a **find-it** quest because nothing else in the tree says the pools exist, and
a player who has never seen one cannot begin the chain.

The Era III exchange quest carries **six task items** on purpose. Coverage counts per output and
the six conversions produce six currencies, but the real reason is that the point of the chain is
that *one material reaches every system* — six separate quests would say the opposite.

Era VII's quests are attached through a new `extra` hook on `ERA_META`. `build_era` derives
everything else from the ladder, which is what keeps it honest and also what makes it unable to
express anything the ladder does not contain; the renewable route belongs to Era VII without ever
being a tier.

*A Crystal That Grows Back* uses a **checkmark**, not a tag task. FTB Quests takes a plain item id
there; a tag needs the `itemfilters:tag` wrapper, no other quest in this pack uses one, and the
format is client-side so nothing in headless validation could prove it fired. Naming a single
shard instead would force a specific geode type on a player who may never have found that biome.

---

## 5. Five things the checkers caught before the server did

Recorded because each was a live defect in the first draft, and each is the kind that fails
*silently* at runtime.

1. **`mythicbotany:mana_infusion` does not exist.** I guessed the type. MythicBotany ships
   exactly one recipe type for the Alfheim infuser — **`mythicbotany:infuser`** — and it takes
   an ingredient *list* plus `fromColor`/`toColor` for the beam, not a single `input`. Caught by
   **E13** against the jars.

2. **The fluid was registered unqualified.** `event.create('liquid_bifrost')` registers under
   **KubeJS's** namespace, giving `kubejs:liquid_bifrost_bucket` — while every recipe named
   `alfheim:*`. The whole chain would have failed to resolve, with no error. Every other startup
   script in the pack qualifies its ids for exactly this reason.

3. **`worldgen()` was silently deleted.** Splitting the recipe script into two era-scoped
   files replaced everything between two anchors — and `worldgen()` sat between them. The
   generator then failed with `NameError: name 'worldgen' is not defined` on its next run.
   Restored, with the pool feature's finiteness now documented in its own docstring.

4. **Fluids were being read as items.** `check_era.py` extracted `fluid: 'minecraft:water'` from
   the Create mixing recipe as an item id and reported water as unregistered — true of the item
   registry, irrelevant to the recipe. `fluid` and `fluidTag` are now in `NON_ITEM_KEYS`.

5. **The checker did not know the pack declares its own tags.** `#alfheim:crystal_shards` — the
   renewable-shard contract the whole Era VII recipe rests on — was reported as declared by no
   jar. It is declared by us, in `kubejs/data/`. Same class of mistake as reading lang files for
   registrations: right question, wrong source.

6. **E12 did not know a fluid creates a bucket.** `our_registrations()` scanned `event.create`
   calls for items and blocks, but KubeJS's `FluidBuilder` also builds a `FluidBlockBuilder` and
   a `FluidBucketItemBuilder` — none of which appear as their own call. It reported our own
   bucket as unregistered. Fixed in `check_era.py`, and the fix was proven by removing it and
   watching E12 fire.

---

## 6. Open

- **The Compendium has no Liquid Bifrost entry.** `check_coverage.py` reports Compendium
  documentation alongside quest coverage, and this system contributes nothing to it. Quests teach
  a player doing the chain; the Compendium is for a player who wants to look it up afterwards.
- **The mixing recipe is invisible to coverage.** It outputs a *fluid*, and `check_coverage.py`
  only counts item outputs, so the renewable route is unchecked by construction. The quests exist
  regardless — but a future recipe that produced only fluids would slip through silently.
- **Whether the Void Verge should be the richest source.** `THE_DEEP.md` §6 already argues the
  void islands are mana-rich by design, and the Rim geode is tuned that way. The pools currently
  use one rarity everywhere.
