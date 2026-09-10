# The Surface — what is worth finding above ground

**Role:** design record for Alfheim's surface structures and the map shop that sells directions
to them.
**Status:** `static validated` 2026-09-08 for the detail pass (§3.3); `runtime sampled`
2026-09-04 for placement — the fifty-structure set is built and statically
validated, and representative structures have now been seen in a real world. The first field
review confirms the concepts but opens a **terrain-integration, detail-density and discovery-value
refinement pass** before the set can be considered production quality.
**Authority:** subordinate to `INSTRUCTIONS.md`. Sits opposite `THE_DEEP.md` (which owns the
quarries, tombs and faultworks *below* ground) and beside `SPAWN_HUB.md` (which owns the single
centrepiece at the origin).
**Asked for by the user, 2026-09-04:** *"a small subchapter of FTB quests that is explorers maps
that are repeatable purchase actions … And I want at least two explorable interesting structures
per Biome that we have. These should be surface features castles ruined castles large craters a
large quarry mine and so on."* Runtime refinement recorded from the user's first in-world review
later the same day.

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

### 3.2 The visual bar — grand civilisation, slow decay

**Runtime review, 2026-09-04:** the current structures generally succeed as *concept builds*.
They establish the right themes, especially the water/shore finds, but they are not yet detailed
enough to sell Alfheim's central premise. They need to read as the collapsed remains of an
**advanced elven civilisation that was grand in scale and decayed slowly**, not as small ruins
placed into a fantasy biome.

Every hero structure therefore needs multiple readable layers at once:

| Layer | Required read |
|---|---|
| **Monumental massing** | The ruin implies a larger original whole: tall walls, broad platforms, large spans, terraces, towers, docks, processional spaces or infrastructure sized for a civilisation rather than a campsite. |
| **Architectural logic** | Rooms, circulation, stairs, bridges, buttresses, foundations, drainage, retaining walls and structural frames explain how the place functioned before it failed. |
| **Elven technology and magic** | Mana conduits, crystal sockets, ritual machinery, rune channels, broken mechanisms, light wells or other remnants show that this was an advanced society, not merely medieval masonry with a different palette. |
| **Causal decay** | Collapse has direction and history: failed supports, water ingress, root pressure, storm damage, fire, subsidence, missing roofs, repaired sections and later collapses. Random block removal is not enough. |
| **Human-scale residue** | Broken paving, railings, benches, work areas, storage, debris, furnishings, loading points and other traces make the grand architecture feel inhabited rather than sculptural. |

### 3.3 The detail pass, and the number that made it checkable

**Implemented 2026-09-08.** The five layers above were a standard nothing measured, so the first
thing this pass built was the measurement: `structure_detail.census()` counts the share of a
piece's solid blocks that are small-scale articulation — stair, slab, wall, fence, pane, carpet,
chain, lantern, cluster, pot, crop, flower, sapling — rather than bulk mass. Run over the shipping
templates at `9b393f2` it said plainly what the field review had said in words:

| Family | Pieces | Worst share | Median | Fewest block ids |
|---|--:|--:|--:|--:|
| surface | 50 | 0.0% | 16.5% | 7 |
| deepworks_archaeology | 11 | 2.0% | 5.8% | 5 |
| court | 4 | 1.3% | 4.0% | 16 |
| greatbole | 3 | **0.0%** | **0.0%** | **3** |
| leyline | 5 | **0.0%** | **0.0%** | 7 |
| pixie | 32 | 1.2% | 14.4% | 6 |

Twenty-nine of the hundred and five shipping pieces carried under a four per cent detail share.
`greatbole/trunk` was three block ids repeated 6,645 times.

**The vocabulary is shared, and it reads the piece rather than being told about it.**
`tools/structure_detail.py` implements the five layers as passes over a finished `Piece`, and no
pass is ever handed a floor plan: a wall face is a solid with a free cell beside it, a floor is a
solid with headroom over it, an overhang is a solid with nothing under it. That is why one
`sconces()` call works on a keep, a mine drift and a pixie cottage, and why the same module
serves five generators instead of five divergent copies.

**The order is causal, and it is the point.** `dress()` runs *before* the decay pass and
`aftermath()` runs *after* it. Detail laid down first is what the building **had**, so the decay
gradient eats it in the same places it eats the walls and what survives reads as residue rather
than as decoration. Detail added afterwards is what the collapse **did** — debris heaped at the
foot of the wall it fell from, moss on the floors the roof stopped covering, roots through what
nobody sweeps any more.

Three invariants hold by construction, because checkers assert them: nothing is placed that
touches nothing (`check_spawn_hub.py` S11), nothing overwrites a block entity or a jigsaw, and
nothing replaces anything but plain masonry — which is what keeps a crystal socket from eating the
carved frame `check_deep_archaeology.py` counts around every grave door.

After the pass, over the same hundred and five pieces: detail blocks 22,891 → 50,646, pieces under
a four per cent share 29 → 9, and the nine are the tree, the canopy, the pixie saplings and the
open-air amphitheatre — mass by nature. `tools/check_structure_detail.py` now holds a floor per
family, set below what the set measures so it fires on regression, with a self-test proving all
six of its checks can fail.

**What it is not.** It is not a runtime claim. Every number above is read off the `.nbt` on disk;
no structure in this pass has been walked in a client. That gate is open.

### 3.4 Geometry may choose where. It may not choose what.

**Corrected 2026-09-09, after the client review §3.3 said was open.** The review rejected the
fifth layer and named the failure exactly: "podiums and crafting blocks and anvils and all kinds
of blocks added all over to all kinds of structures where they definitely do not belong ... making
all of the structures much much just noisier not necessarily more detailed."

The cause is a good idea applied one step too far. §3.3's central property — *no pass is ever
handed a floor plan* — is what lets one implementation serve five generators, and it is right for
**candidates**: a wall face is a wall face in a keep and in a mine drift. It is wrong for
**vocabulary**. `furnish()` carried a single fixed catalogue — bench, table, pot, cauldron, shelf,
lectern, crate — and took an `allow` filter that sixteen of its eighteen call sites never passed.
Censused over the 105 shipping templates:

| block | placed |
|---|--:|
| bookshelf | 496 |
| decorated pot | 432 |
| cauldron | 333 |
| lectern | 309 |
| everything else | 52 |
| **total** | **1,622, in 48 of 105 templates** |

A quarry with 150 bookshelves. A fault working with 157 pieces of furniture. 147 lecterns
distributed through the royal tombs. `floor_litter` compounded it by dropping one loose block per
floor cell at a flat rate — the same even scatter that §3.3's own account of `debris()` records
being corrected one level up, because *damage is contiguous* and a uniform sprinkle reads as
texture rather than as a building that fell over.

**The rule this adds to §3.2.** The five layers describe what a ruin must *read* as. Four of them
are properties of the structure's own fabric and geometry — massing, logic, technology, decay —
and a geometric pass can supply them anywhere. The fifth is not. Human-scale residue is a claim
about *who used this room and for what*, and that is knowledge only the generator that built the
room has. A layer that asserts occupancy must be told the occupancy.

So: `dress()` now refuses `furniture` unless the caller also names `furniture_allow`, and
`floor_litter` is gone from the orchestrator entirely. The blind default is unrepresentable rather
than merely unused. After the change, 150 blocks in 23 templates, all of them hand-placed by a
generator that meant them — the hub library's bookshelves, the loot barrels, one deliberate
lectern.

`debris()` is untouched and belongs where it is. It walks the broken wall tops the decay pass
left, drops heaps at the foot of the wall they fell from in the collapse direction, and draws from
the piece's own rubble palette. It never had to be told anything, because a collapse is a fact
about the fabric.

**A floor is not a target, and three pieces proved it.** Removing the furniture dropped
`leyline/hub`, `surface/harvest_crater` and `headworks/shaft` below their family detail floors —
they had been meeting them on the misplaced blocks. No floor was lowered. Each was given detail
its own geometry can actually carry, and finding it exposed a real defect in two of the three:

| piece | | |
|---|---|---|
| `leyline/hub` | 2.5% → 3.0% | `LEY_KIT` declared no `crystal` role, so `conduits()` and `crystal_sockets()` returned 0 on sight — in the one family whose entire premise is a mana channel |
| `surface/harvest_crater` | 3.7% → 6.0% | corbels on a shattered rim; the builder's own comment already said the detail here is geological |
| `headworks/shaft` | 4.3% → 5.5% | a 4×4 chimney has no floor to furnish, no overhang to corbel and no wall run long enough for a conduit — what three centuries leave inside an abandoned shaft is root, drip and web |

Pass 6 (named interior rooms) is where the fifth layer properly belongs: once a generator knows a
room is a kitchen, it can furnish it as one.

The **ocean and shore structures are specifically retained as concepts** — the first field review
liked them as thematic finds. Their next pass is depth, not replacement: layered waterlines,
eroded foundations, drowned lower rooms, silt/debris, collapsed piers or seawalls, storm-broken
upper works and enough surviving high architecture that the player can infer what stood there
before the coast reclaimed it.

This standard applies to the entire surface catalogue. The weaker structures are not allowed to
remain "good enough" because one quarry or one shoreline ruin works; the set must establish a
consistent civilisation-wide visual language.

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

### 4.2 Terrain incorporation is an acceptance gate

**Runtime defect, observed 2026-09-04:** several structures could generate as if the template had
simply been stamped onto the heightmap, including structures projecting from cliffs with no
credible foundation, earthwork or terrain transition. `beard_thin` is not enough by itself.
A structure that technically generates but visibly ignores the land has failed placement.

The **Starved Reach `starveling_pit` quarry is the positive reference** from this test. It read as
an excavation cut *into* the landscape rather than a box placed on it. That is the baseline the
rest of the set needs to reach by whatever method fits the archetype.

For ordinary buildings, the generator should inspect local relief across the footprint before
accepting a candidate. Mild slopes may be blended. Severe slopes/cliffs should either cause
relocation or trigger authored terrain geometry: stepped foundations, retaining walls,
buttresses, buried lower courses, approach stairs, collapsed substructures or deliberate cliff
architecture with visible support. A naked cantilevered template is never acceptable merely
because the structure system placed it successfully.

For **shore, lake and ocean structures**, the terrain contract includes the waterline. Foundations
must meet the bed or bank, lower work should show inundation/erosion, and transitions from dry
architecture to drowned architecture must be intentional. If a pier, arcade or wreck is partly
submerged, the placement should explain why rather than leaving half the build hovering beside a
random shoreline.

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

### 6.1 A genuine find must still be worth the walk

"Not a loot pinata" does **not** mean "materially empty." The first runtime review found the
Starved Reach quarry to be one of the strongest structures in placement and concept, but also
found that it needs **more resources to make discovery worthwhile**.

For `starveling_pit` and the other quarry variants, the reward should live primarily in the
**world geometry**, not a progression-skipping chest: more exposed ore/bloom faces, richer visible
strata, abandoned stockpiles of ordinary materials, half-worked seams and recoverable mundane
supplies appropriate to the biome. A player who deliberately follows a map or detours to a rare
quarry should leave with a meaningful haul, while still being unable to skip an era or obtain a
spine-gated material early.

That gives the quarry the right economic story as well: it was built because there was something
worth extracting there. A visually impressive empty quarry contradicts its own history.

---

## 7. Build order

The first runtime sample has moved the project out of pure proof-of-generation and into quality
repair. The highest-priority passes are now terrain incorporation and hero-level detail.

| Pass | Work | State |
|---|---|---|
| 1 | Extract the shared NBT `Piece`; manifest; ten builders; datapack; loot; the Cartographer chapter; checker | **done 2026-09-04, static** |
| 2 | Fresh-world proof: `locate structure` each of the thirty-two and inspect representative examples | **in progress — representative structures observed 2026-09-04** |
| 3 | Buy one map of each of the ten and confirm it fills rather than coming back blank | deferred, runtime |
| **4** | **Terrain-integration repair across the whole set (§4.2), using `starveling_pit` as the positive reference** | **open, priority** |
| **5** | **Hero-detail/slow-decay pass across every archetype (§3.2), with shore/ocean/water-edge structures explicitly included** | **layers 1-4 static implemented 2026-09-08 (§3.3); layer 5 rejected at client review 2026-09-09 and gated behind an explicit per-structure vocabulary (§3.4); client walk still open** |
| 6 | Interiors — named rooms, spawners where appropriate, circulation and the one thing worth taking per archetype | encounter slice: 12 bounded Knight Quest spawners; furniture, light and floor residue now generated per §3.3; named rooms still open |
| 7 | Quarry discovery-value pass — increase era-safe exposed resources and useful material yield (§6.1) | **static implemented 2026-09-08** — stockpiles and half-worked seams in every quarry |
| 8 | Density tuning against a real walk | not started |

### 7.1 What the first runtime sample changed

Static validation remains necessary, but "the file generated" and "the structure looks like it
belongs in the world" are now explicitly separate acceptance levels.

**Proven by the first field review:** at least representative members of the surface catalogue do
generate in Alfheim; the Starved Reach quarry can integrate into terrain convincingly; and the
shore/water concepts are thematically sound enough to keep.

**Still to prove or repair:**

- locate and inspect **all thirty-two**, not only the sample encountered in the test run;
- repair structures that ignore relief or jut from cliffs (§4.2);
- prove `start_height: {absolute: -ground}` for every crater/quarry variant rather than relying on
  the one successful quarry;
- verify the two `OCEAN_FLOOR_WG` structures against real water depth and shore transitions;
- verify `verge_spire` on the Void Verge's floating islands;
- perform the hero-detail pass so each ruin carries architecture, technology, inhabitation and
  causal decay rather than merely a silhouette (§3.2);
- confirm a purchased chart fills in rather than coming back blank (§5.3);
- measure what thirty-two extra `random_spread` sets cost at chunk generation. They are excluded
  from Midgard by biome tag — `ChunkGeneratorStructureState` drops a set whose biomes the
generator cannot produce — so the cost should fall on Alfheim alone.

The current implementation is therefore **concept-proven but not production-ready**. The next
pass is not "add more structures"; it is to make the structures already present look as though
Alfheim actually built, used, maintained and then slowly lost them.
