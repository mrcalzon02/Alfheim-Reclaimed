# The Surface — what is worth finding above ground

**Role:** design record for Alfheim's surface structures and the map shop that sells directions
to them.
**Status:** `static validated` 2026-09-04 — all thirty-two structures and the shop are built and pass fourteen checks; **nothing has been seen in a world.** See
`EXECUTION_STATE.md` for current status.
**Authority:** subordinate to `INSTRUCTIONS.md`. Sits opposite `THE_DEEP.md` (which owns the
quarries, tombs and faultworks *below* ground) and beside `SPAWN_HUB.md` (which owns the single
centrepiece at the origin).
**Asked for by the user, 2026-09-04:** *"a small subchapter of FTB quests that is explorers maps
that are repeatable purchase actions … And I want at least two explorable interesting structures
per Biome that we have. These should be surface features castles ruined castles large craters a
large quarry mine and so on."*

---

## 1. The gap this closes

Alfheim's surface currently contains **one** structure of ours — the Greatbole at the origin —
plus MythicBotany's elven houses. Sixteen biomes, one landmark. A player who walks out of the
Hollow Court in any direction walks through scenery.

That is worse here than it would be in an ordinary pack, because the premise is *a civilisation
that stopped*. A dead world with nothing built in it is not a dead world; it is an empty one.
The ruins are the evidence.

Two deliverables, and they are separable:

1. **Thirty-two surface structures**, two in every one of the sixteen biomes in the Alfheim
   layer, drawn from ten parametric archetypes.
2. **The Cartographer** — a repeatable FTB Quests shop that sells one Explorer's Map per
   *archetype*, not per structure. Ten purchases, endlessly repeatable.

The second is small on purpose. "Different **types** of structures" is what was asked for, and a
map that finds the nearest Keep of any kind is both the vanilla idiom (`#minecraft:village`
covers five village types) and the one that stays useful after the first purchase.

---

## 2. Ten archetypes

Each archetype is a Python builder taking a parameter block. A castle is not authored five
times; it is authored once and asked for five different castles. That is the same reasoning
`SPAWN_HUB.md` §1 gives — the user's own observation that *"automated structure generation
typically needs multiple passes of detailed improvement"*, and a pass is only cheap if pass 2 is
an edit to a constant.

| Archetype | Footprint | Ground | What it is | Map icon |
|---|---|--:|---|---|
| `castle` | 48×34×48 | 1 | Curtain wall, corner towers, gatehouse, inner keep | `mansion` |
| `quarry` | 48×34×48 | 22 | Terraced open pit, benches, ramp, headframe, spoil | `target_x` |
| `crater` | 48×26×48 | 14 | Blast bowl, fused floor, rim debris, shattered strata | `red_x` |
| `tower` | 24×48×24 | 1 | A solitary watch-spire | `target_point` |
| `hall` | 40×26×28 | 1 | One long roofed room; the roof is usually gone | `banner_yellow` |
| `aqueduct` | 48×26×16 | 1 | An arcade of arches, broken mid-span | `monument` |
| `span` | 48×24×16 | 1 | A bridge that stops | `banner_brown` |
| `barrow` | 40×18×40 | 4 | Mound, menhir ring, sealed door | `banner_gray` |
| `wreck` | 40×28×24 | 2 | A grounded elven sky-barge | `banner_purple` |
| `shrine` | 28×26×28 | 1 | A small domed shrine on a plinth | `banner_white` |

Five of those boxes are bigger than the first draft's, and the reason is worth keeping.
**`Piece.set()` silently drops anything outside the piece.** The wreck's mast was twelve blocks
tall in a box with eight blocks of headroom, the dome of the Bloomfall Shrine overshot its lid
by four courses, and the Rotwood Barrow's outermost menhirs stood at x=32 in a 32-wide box. All
three generated, validated and shipped a structure with a piece missing, and nothing anywhere
said so. `Piece` now counts every dropped `set()` and the generator prints the ratio; anything
over 0.60 is flagged CLIPPED. The current worst is **0.02**, which is the legitimate overdraw
of scanning a bounding square to draw a circle.

Ten icons, all distinct, all legal in 1.20.1. **`MapDecoration.Type` in 1.20.1 has no
`jungle_temple` or `swamp_hut`** — those arrived later. The legal set was read out of the
shipping client jar (`dyl$a.class`), not assumed: `player`, `frame`, `red_marker`,
`blue_marker`, `target_x`, `target_point`, `player_off_map`, `player_off_limits`, `mansion`,
`monument`, the sixteen `banner_*`, and `red_x`.

### 2.1 The carve, and why craters are possible at all

A crater is a hole. Structure templates place blocks; they do not normally remove them.

They do, and this is the mechanism the crater and the quarry both stand on: **a template
position set to `minecraft:air` is placed like any other block and overwrites the terrain, while
a position absent from the template's block list is not touched at all.** `structure_void` is
stripped by `BlockIgnoreProcessor.STRUCTURE_BLOCK`; plain air is not. So the builders carve by
writing air and leave terrain alone by writing nothing.

`Piece.set()` only records what it is given, so "leave the ground" is already the default and
the crater's bowl is an explicit air fill. This is the single most important fact in the file
for anyone extending it.

---

## 3. Two per biome, and they are not the same two

Every biome gets one thing that was **built** and one thing that was **done to the land**, so
finding both teaches the biome twice.

| Biome | Built | Scar |
|---|---|---|
| `ashen_grove` | `ashwatch_keep` — castle, worst decay | `grey_barrow` — barrow |
| `silverbark_wood` | `frostwatch_spire` — tower | `silver_moot` — hall |
| `mana_fen` | `drowned_arcade` — aqueduct | `fen_shrine` — shrine |
| `sundered_highlands` | `riven_hold` — castle | `sundered_quarry` — quarry |
| `bloomfall_vale` | `bloomfall_shrine` — shrine | `garland_menhirs` — barrow |
| `hollow_marches` | `hollow_bastion` — castle | `marchfall_crater` — crater |
| `starved_reach` | `boneyard_wreck` — wreck | `starveling_pit` — quarry |
| `scorchfell` | `pyre_hall` — hall | `cinderglass_crater` — crater |
| `infested_warren` | `warren_gate` — castle | `broken_causeway` — span |
| `decayed_mire` | `mire_hulk` — wreck | `rotwood_barrow` — barrow |
| `void_verge` | `verge_spire` — tower | `severed_span` — span |
| `mythicbotany:alfheim_plains` | `plains_moot` — hall | `waystone_ring` — barrow |
| `mythicbotany:alfheim_hills` | `hillcrown_keep` — castle | `hillcut_quarry` — quarry |
| `mythicbotany:alfheim_lakes` | `lake_shrine` — shrine | `lake_arcade` — aqueduct |
| `mythicbotany:dreamwood_forest` | `boughwatch_tower` — tower | `canopy_span` — span |
| `mythicbotany:golden_fields` | `grange_hall` — hall | `harvest_crater` — crater |

Sixteen biomes, thirty-two structures, ten archetypes. MythicBotany's five biomes are included
because they are Alfheim: they are in the same `libx:biome_layer` and the player crosses them on
the same walk. `tools/surface_works_manifest.json` is the source of truth for this table; the
table above is a copy and the manifest wins.

### 3.1 Palettes carry the biome, not the archetype

Two castles built from the same generator must not look like the same castle. Each structure
names a palette, and the palettes are keyed to the land rather than to the shape:

- **Elven marble** — `feywild:elven_quartz_*` (block, brick, cracked brick, mossy brick,
  pillar, polished, stairs, slab). The Court's own stone, and the only family in the load path
  that ships pre-cracked and pre-mossed. Used where the elves built to last.
- **Livingrock** — `botania:livingrock`, `_bricks`, `_slate`, and the stair/slab/wall set. The
  dimension's own stone (`default_block` in `mythicbotany:alfheim`'s noise settings), so a
  livingrock ruin reads as *quarried here*.
- **Sourcestone** — `ars_nouveau:sourcestone_*`. The Spine of Song's masonry; used where the
  building was magical rather than military.
- **Burnt** — blackstone, basalt, magma, `occultism:burnt_otherstone`. Scorchfell and the
  craters.
- **Drowned** — prismarine, dark prismarine, mossy cobble. The fen and the lakes.
- **Dreamwood** — `botania:dreamwood_*` for every timber. There is no oak civilisation here.

---

## 4. Placement

Each structure is its own `worldgen/structure` and its own `worldgen/structure_set`, placed by
`minecraft:random_spread`. Three rarity bands:

| Band | Spacing | Separation | Archetypes |
|---|--:|--:|---|
| common | 20 | 6 | shrine, barrow |
| uncommon | 28 | 9 | tower, hall, span, aqueduct, wreck |
| rare | 40 | 13 | castle, quarry, crater |

**Every set carries a unique `salt`.** Two `random_spread` sets sharing spacing and salt pick
*the same chunk in every cell*, so a shared salt does not make two structures neighbours — it
makes them occupy the same block. Salts are derived from a SHA-1 of the structure id in
`gen_surface_works.py`, which makes them unique by construction and stable across regeneration.

`terrain_adaptation` is `beard_thin` for everything that stands on the ground and `none` for
the crater and the quarry, which supply their own ground.

`max_distance_from_center` is **116** on every structure, not the codec maximum. The codec
validates `max_distance_from_center + margin <= 128` and **refuses world creation** when it
does not hold — `SPAWN_HUB.md` §2.1 paid for that at runtime. 116 clears the budget under both
adaptations, it is the value the Greatbole has already been proven on, and no single 48-block
piece comes anywhere near needing it. There is no upside to taking the last twelve.

**Not joined to the hub's exclusion family.** `THE_DEEP.md` §6 records the reason and it applies
here unchanged: `continuityworks_spawn_protection` carries a 500-block exclusion, and thirty-two
families all claiming it would sterilise each other.

### 4.1 The `#alfheim:has_<id>` biome tag is validity, not preference

`SPAWN_HUB.md` paid for this lesson twice and it is written down here so a third payment is not
needed. A structure whose `biomes` tag does not contain the biome at the chosen chunk **does not
generate at all** — silently, with no log line. Each structure therefore emits its own biome tag
listing exactly the biomes it is allowed in, and `check_surface_works.py` asserts that every
listed biome exists in the layer.

---

## 5. The Cartographer — ten maps, bought with flowers

A new FTB Quests chapter, `cartographer`, in the campaign group, after the eras.

**Mechanism, verified against the shipping jars rather than assumed:**

| Piece | Evidence |
|---|---|
| A quest may repeat | `Quest.canRepeat` is a `Tristate`; `Tristate.read` maps a present boolean to TRUE/FALSE, so `can_repeat: true` is the SNBT. `repeat_cooldown` is an `int` and is written only when > 0. |
| A purchase consumes | `ItemTask.consumeItems`, SNBT `consume_items: true`. |
| It does **not** auto-buy | `ItemTask.submitItemsOnInventoryChange()` returns `!consumesResources()`. A consuming task is never submitted from inventory changes — the player must click it. Without this the shop would silently drain a player's petals in a loop. |
| The reward can run a command | `CommandReward`, type `command`, keys `command`, `elevate_perms`, `silent`. It builds `player.createCommandSourceStack()`, so the command runs **at the player, in the player's dimension**. |
| Placeholders | `Pattern.compile("[{](\\w+)}")` — `{p}`, `{x}`, `{y}`, `{z}`, `{team}`. A vanilla `@s` passes through untouched. |
| The reward auto-delivers | `Reward.autoclaim`, NBT key `auto`, values `default`/`disabled`/`enabled`/`no_toast`/`invisible`. |

So one purchase is:

```
tasks:   [{ type: "item", item: "botania:magenta_petal", count: 16L, consume_items: true }, …]
rewards: [{ type: "command", auto: "enabled", elevate_perms: true, silent: true,
            command: "/loot give {p} loot alfheim:explorer_maps/castle" }]
can_repeat: true
```

### 5.1 Why `/loot give` and not an item reward

An Explorer's Map is not an item; it is an item **plus a search performed at the moment of
handing it over**. `minecraft:exploration_map` is a loot *function*: it reads
`LootContextParams.ORIGIN`, calls `ServerLevel.findNearestMapStructure(tag, origin, radius,
skipKnown)` and writes the result into the map's NBT. There is nowhere in FTB Quests to put a
loot function, so the reward runs a command and the command runs a loot table.

`/loot give <players> loot <table>` was checked in the 1.20.1 client jar (`afd.class`) rather
than trusted: it builds `LootParams.Builder(source.getLevel())`, sets `ORIGIN` to the source
position, sets `THIS_ENTITY` optionally, and creates the params with the **`chest`** param set —
which is exactly the context `exploration_map` requires.

The `destination` field is **a structure tag written without a leading `#`**. `readStructure`
does `TagKey.create(Registries.STRUCTURE, new ResourceLocation(s))` on the raw string
(`eat$b.class`). So `"destination": "alfheim:castle"` resolves to
`data/alfheim/tags/worldgen/structure/castle.json`, and that file lists the five castles.

### 5.2 Price list

Costs are **petals plus the dimension's own stone**, and nothing else. Both are renewable from
the first hour: livingrock is Alfheim's `default_block`, and petals come from every tree's
leaves (`ref_groves`), from wild mystical flowers, and from Floral Fertilizer.

Nothing here costs a tier-ladder intermediate or a spine material. That is deliberate — a map is
*knowledge*, and `INSTRUCTIONS.md` §6.3 puts convenience outside the gating doctrine. What the
map cannot do is make the place survivable.

| Map | Archetype | Petal | Petals | Stone |
|---|---|---|--:|--:|
| The Wayshrines | shrine | white | 6 | — |
| The Waystones | barrow | light gray | 6 | — |
| The Moot Halls | hall | yellow | 8 | 2 dreamwood |
| The Watchtowers | tower | cyan | 8 | 4 livingrock |
| The Aqueducts | aqueduct | blue | 8 | 4 livingrock |
| The Broken Spans | span | brown | 8 | 4 livingrock |
| The Wrecks | wreck | purple | 10 | 4 dreamwood |
| The Quarries | quarry | orange | 12 | 8 livingrock |
| The Craters | crater | red | 12 | 8 livingrock |
| The Keeps | castle | magenta | 16 | 12 livingrock |

`search_radius` is 100 chunks for the common and uncommon bands and 150 for the rare one, in
chunks, because a rare structure restricted to one biome may genuinely be far away.

### 5.3 The failure mode this shop has, stated before it happens

**If the search finds nothing, the player pays and receives a blank map.** `exploration_map`
returns the stack unchanged when `findNearestMapStructure` comes back null; there is no error
and no refund. The mitigations are the generous radius above and a warning in the chapter's own
text. The real fix, if it proves to bite, is a Guide quest that names which biome each map
wants — the information exists in this file and in `ref_biomes`.

This is a **runtime** question. It cannot be settled statically and is recorded as deferred.

---

## 6. What this must not become

`THE_DEEP.md` §3 named three failure modes for the underground. Two of them apply here
unchanged, and there is a third that is specific to the surface.

1. **A loot pinata.** Chests carry commodities, ruin-appropriate tools and petals. They do not
   carry runes, tier materials, or anything that shortens an era.
2. **Another thing that generates everywhere.** The apothecary lesson: 1-in-2 chunks is scenery.
   The rarity bands in §4 exist to keep a keep a genuine find.
3. **Thirty-two identical buildings with different palettes.** This is the one the parametric
   approach makes easy to fail. Every archetype takes a *shape* parameter block as well as a
   palette — tower count, wall length, ruin integrity, collapse direction — and two structures
   from the same archetype must differ in at least two of them. The manifest is the place that
   is checked.

---

## 7. Build order

| Pass | Work | State |
|---|---|---|
| 1 | Extract the shared NBT `Piece`; manifest; ten builders; datapack; loot; the Cartographer chapter; checker | **done 2026-09-04, static** |
| 2 | Prove it: fresh world, `locate structure` each of the thirty-two | deferred, runtime |
| 3 | Buy one map of each of the ten and confirm it fills rather than coming back blank | deferred, runtime |
| 4 | Interiors — spawners, named rooms, the one thing worth taking per archetype | not started |
| 5 | Terrain seams: the crater rim and the quarry bench against real ground; the lake pair against real water | not started |
| 6 | Density tuning against a real walk | not started |

### 7.1 What pass 1 cannot tell you

Fourteen static checks pass and the self-test proves all of them can fail. None of that is
runtime acceptance. Specifically **unproven**:

- that any of the thirty-two actually generates — `INSTRUCTIONS.md` §7 level 9;
- that `start_height: {absolute: -ground}` lands the crater bowl and the quarry floor where
  the arithmetic says. A one-block error is cosmetic; a sign error is not;
- that the two `OCEAN_FLOOR_WG` structures sit on the lake bed rather than under the surface;
- that `verge_spire`'s plinth is enough ground on the Void Verge's floating islands;
- that a purchased chart fills in rather than coming back blank (§5.3);
- that thirty-two extra `random_spread` sets cost nothing measurable at chunk generation.
  They are excluded from Midgard by biome tag — `ChunkGeneratorStructureState` drops a set
  whose biomes the generator cannot produce — so the cost should fall on Alfheim alone.

Pass 1 depends on nothing that does not already exist. `tools/gen_spawn_hub.py` proved the NBT
pipeline and `tools/nbt.py` writes the files; this is the same machinery pointed outward.
