# Elven MineColonies — a plan

**Role:** plan record. **Nothing here is implemented.**
**Status:** `draft` — researched against the installed jars, costed, not built.
**User instruction, 2026-09-03:** *"a plan… to add some custom villager theming for MineColonies in
our data pack, for creating a villager elf preset. We do have the mod that adds the race of elves
as our template — but that's planning."*

---

## 1. What the research changed

Two assumptions in the brief did not survive contact with the jars, and both change the plan.

**`richs_races_wood_elves` is not a race system.** It is an MCreator mod containing a single
`WoodElfEntity` — a mob, with a renderer and six skin textures. It has no citizen integration, no
player-race hook, and no MineColonies awareness. It is a **visual reference**, not a template to
build on.

It is also **`license="Not specified"`**. `gen_items.py` already treats third-party art as
licence-sensitive; the same caution applies here. Use it to look at, not to copy from.

**The textures are the wrong shape anyway.** Wood elf skins are **64×64** (player format).
MineColonies citizens are **128×64** — a different, larger layout with 220 textures per skin-tone
suffix (`_a`, `_b`, `_d`, `_w`), across 43 job bases. Nothing is drop-in.

**And the thing that most says "elf" cannot be done in a texture at all.** Pointed ears are model
geometry. A resource pack can change skin tone, hair and clothing; it cannot change a silhouette.
Any plan that promises visibly elven citizens from a datapack is promising something it cannot
deliver.

**The good news is larger than the bad.** MineColonies already ships
`data/minecolonies/citizennames/elf.json` — **104 male given names, 110 female, 237 surnames**,
two-part Western order. The single most visible piece of elf theming is already in the pack and
costs nothing to switch on.

---

## 2. What MineColonies actually exposes

Verified against `minecolonies-1.20.1-1.1.1276.jar`:

| Hook | Path | What it gives us |
|---|---|---|
| Citizen names | `data/minecolonies/citizennames/` | **`elf.json` already exists.** Per-colony setting. |
| Visitors | `data/minecolonies/visitors/` | Fully datapack-definable recruitable NPCs |
| Research | `data/minecolonies/researches/` | 315 files; `branch`/`costs`/`effects`/`parentResearch` |
| Crafter recipes | `data/minecolonies/crafterrecipes/` | Per-worker recipe injection |
| Study items | `data/minecolonies/study_items/` | What the Library consumes |
| Citizen textures | `assets/.../entity/citizen/default/` | 880 files; resource pack territory |
| Building styles | Structurize blueprint packs | The largest lever, and the largest cost |

A visitor is this small:

```json
{ "texture": "<player-skin UUID>", "citizensuffix": "_w", "name": "Circinus Coranus",
  "chance": 0.001, "storylangkey": "…", "recruitcost": "minecraft:amethyst_block",
  "recruitcostcount": 13, "gender": "female",
  "primaryskill": "Mana", "secondaryskill": "Knowledge" }
```

`recruitcost` takes any item id — including ours. An elven wanderer recruited for **Dawnglass
Shards** is three lines of JSON and reads as pure theme.

---

## 3. The plan, in four tiers

Ordered by return per unit of effort. Each tier is independently shippable; stopping after any of
them leaves the pack coherent.

### Tier 0 — Switch the name file. *Effort: minutes.*

Set colonies to the `elf` name style. Every citizen the colony ever produces is named from
MythicBotany-adjacent elven stock instead of "Bob Smith".

**Open:** whether this is a per-colony Town Hall setting, a world default, or a config key. It is
not in `minecolonies-common.toml`, so it is most likely the in-game Town Hall selector. **Verify at
first boot** — if it is player-facing only, Era II's colony quest text tells the player to pick it,
which is a one-line fix rather than a feature.

### Tier 1 — Datapack theming. *Effort: a day. Highest value per hour.*

1. **Elven visitors.** Six to ten, in `kubejs/data/minecolonies/visitors/`. Names drawn from
   `elf.json`'s own lists so they sit alongside the citizens. `recruitcost` set to Alfheim
   materials — Dawnglass Shards, Quickened blooms, crystal clusters — which quietly teaches the
   player what those items are worth. `primaryskill: "Mana"` where it fits the fiction.
   **Their story text is the real payload:** `storylangkey` points at our lang file, so each
   wanderer can carry a line about what they walked out of. That is worldbuilding for the price of
   a JSON file.
2. **An elven research branch.** A new `branch` under `researches/`, gated on **spine materials**
   rather than vanilla ones — Manasteel, Elementium, crystal shards. This is where
   `INSTRUCTIONS.md` §2.3 gets enforced for MineColonies: the colony's power curve routes through
   the spines like everything else.
3. **Crafter recipes** for elven-appropriate goods, so colony workers can make pack materials.
4. **Study items** — the Library consumes our lore items, tying the colony to the campaign.

### Tier 2 — Citizen appearance. *Effort: days. Capped by what textures can do.*

Programmatic recolour of the 880 citizen textures, in the style `gen_items.py` already uses:
palette-shift skin toward pale/ashen, hair toward silver and copper, clothing toward the pack's
greens and violets. A `tools/gen_citizen_skins.py` reading a small manifest, so the result is
reproducible rather than hand-painted.

**Scope it down first.** 880 files is the whole set; the visible subset is the ~12 jobs a player
actually sees early. Do those, look at it, then decide whether the rest is worth it.

**Two hard limits to state up front:** no pointed ears without a model, and MineColonies ships only
a `default` style folder — whether it supports *selecting* an alternate folder is unverified, so
the fallback is overriding `default` directly in a resource pack, which affects every colony.

### Tier 3 — An elven building style. *Effort: weeks. Defer.*

A Structurize blueprint pack: every hut, in dreamwood and living rock, with Domum Ornamentum
trim. This is what would make a colony *look* elven, and it is the only tier that fully delivers
the brief.

It is also weeks of in-game building, and it is the one tier that cannot be generated. **Defer it
until the pack is play-tested.** A beautiful colony in an unplayable pack is worth nothing, and
Tier 1 buys most of the felt theming for a fraction of the cost.

---

## 4. Sequencing, and one honest caveat

Do **Tier 0 at first boot**, **Tier 1 alongside the Era II colony quests** (they are the quests
that introduce the colony, so the theming and the teaching land together), **Tier 2 when the pack
is otherwise stable**, and **Tier 3 only if the pack ships and wants a second act**.

The caveat: MineColonies is the mod most exposed by the architecture change. It is the one flagged
in `WORLD_STRUCTURE.md` as likely to hardcode `Level.OVERWORLD`, and Alfheim is not the Overworld.
**If colonies do not function in Alfheim at all, every tier above is moot.** That check —
the `Level.OVERWORLD` sweep, MineColonies first — is already the recorded next action after level
9, and it should stay ahead of this plan.

---

## 5. Open

1. How the citizen name style is selected. Config, world setting, or Town Hall UI.
2. Whether MineColonies can select a citizen texture *style* folder other than `default`.
3. Whether colonies work in a non-Overworld dimension at all — the blocker above.
4. Whether the wood-elf mod is worth keeping at all once it is established that it contributes a
   mob and nothing else. It is 1 of 86 jars; if it earns no place in the design, `INSTRUCTIONS.md`
   §2.3's rule applies to it as much as anything else.
