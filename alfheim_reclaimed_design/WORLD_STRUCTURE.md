# World Structure — Two Worlds

**Status:** design record. **Revised three times on 2026-09-02** — when Continuity Works arrived,
when the two-world architecture was clarified, and finally when Alfheim was moved **out of the
Overworld slot**. This version supersedes all three. Prior revision archived in the session
scratchpad before replacement.

**Correction carried forward:** earlier versions of this file named
`data/mythicbotany/tags/worldgen/biome/alfheim.json` as the biome injection point. **That was wrong.**
The correct path is `data/mythicbotany/tags/libx/biome_layer/alfheim.json` — a tag in LibX's
`biome_layer` registry, not a biome tag. See §2.

---

## 1. The architecture

Two worlds, and the whole pack is the relationship between them.

| | **Alfheim** | **Midgard** |
|---|---|---|
| Dimension | **`mythicbotany:alfheim`** — the mod's own | **`minecraft:overworld`** |
| What it is | Elven, magical, whimsical. Ruined but alive. | The industrial world that died. |
| The player | Wakes here. Lives here. Rebuilds here. | Visits, from **Era IV**. |
| Biomes | MythicBotany's 5 + our 6 = **11** | Vanilla + Regions Unexplored; Continuity Works' anthology when CW-1 is fixed |
| Rich in | Mana, Elementium, gold, dragonstone, dreamwood | Iron, coal, redstone, ruins, salvage |
| Poor in | **Ordinary metals — this is the point** | Life, mana, growth |
| Generator | `libx:noise` + `libx:layered` (MythicBotany's, unmodified) | vanilla multi-noise + TerraBlender |

**Alfheim is no longer in the Overworld slot.** The earlier design overrode
`minecraft:worldgen/world_preset/normal` so the Overworld ran MythicBotany's Alfheim generator.
That is struck. Three reasons:

1. **It duplicated the mod's own work.** `data/mythicbotany/dimension/alfheim.json` already carries
   the exact generator block the override copied — same `libx:noise`, same `libx:layered` on
   `#mythicbotany:alfheim`, same noise settings, same surface override. The override bought a
   hand-maintained copy of a dimension the mod ships and tests.
2. **It was the riskiest unproven assumption in the project** (former B-12) and was never verified
   in a fresh world.
3. **It occupied the slot every TerraBlender mod injects into.** That is the single cause of both
   the Continuity Works mismatch and Regions Unexplored generating nowhere. Leaving the Overworld
   vanilla makes both work exactly as shipped, and their content lands in Midgard — where an
   industrial anthology and a set of lush Earth biomes belonged from the start.

**The cost, stated plainly.** The Overworld slot was originally chosen because a great many mods
gate behaviour on `Level.OVERWORLD`, and a home world that is not the Overworld will misfire for
any of them that hardcode that check in Java. No datapack can reach a hardcoded check.

What makes it survivable is that Alfheim's *dimension type* is an Overworld clone — verified from
`data/mythicbotany/dimension_type/alfheim.json`:

| Property | Value | Consequence |
|---|---|---|
| `bed_works` | `true` | beds set spawn and pass the night |
| `natural` | `true` | compasses work, no piglin zombification quirks |
| `has_skylight` | `true` | normal light, crops, solar behaviour |
| `effects` | `minecraft:overworld` | normal sky and fog |
| `height` / `min_y` | 384 / −64 | identical build range |
| `coordinate_scale` | 1.0 | no Nether-style scaling |
| `has_raids` | **`false`** | the one real difference — no village raids |

So the exposure is hardcoded `Level.OVERWORLD` checks, not dimension properties. **MineColonies is
the one to watch.** Finding them costs one boot, which is cheaper than proving the preset override
worked.

The scarcity in the Alfheim row is not a defect to fix. It is the engine of the entire pack: the
elves lack ordinary metals, so they must trade through the gate, so the gate reversal matters.
Ordinary metal now exists in Alfheim as a deliberate **trickle** (§3), not as absence — absence
made Era I uncompletable.

## 2. The injection point — corrected

MythicBotany's Alfheim generator:

```json
// data/mythicbotany/dimension/alfheim.json
"generator": {
  "type": "libx:noise",
  "biome_source": { "type": "libx:layered", "layers": "#mythicbotany:alfheim" },
  "settings": "mythicbotany:alfheim",
  "surface_override": "mythicbotany:alfheim_surface"
}
```

`"layers"` resolves to **`data/mythicbotany/tags/libx/biome_layer/alfheim.json`**:

```json
{ "values": [ "mythicbotany:alfheim" ] }
```

— a tag of **`libx:biome_layer`** entries. Each layer is a full climate map, in
`data/mythicbotany/libx/biome_layer/alfheim.json`, with seven entries keyed on
`continentalness`, `erosion`, `weirdness`, `humidity`, `temperature`, `depth` and `offset` — the same
climate space vanilla multi-noise uses. The layer also carries `density` and `range`, which is what
makes layers stack.

LibX also provides `libx:biome_surface` (per-biome surface rules) and `libx:surface_rule_set`.
MythicBotany ships surfaces for `golden_fields` and `alfheim_lakes`.

### 2.1 Therefore: enriching Alfheim is a datapack append

To add elven biomes to Alfheim, Continuity Works needs only to:

1. define one or more `libx:biome_layer` JSONs with its own biomes and climate parameters;
2. append those layer IDs to `#mythicbotany:alfheim` with `replace: false`.

No TerraBlender. No mixin. No Java. The layers stack over MythicBotany's, and `density`/`range` tune
how much of the world each layer claims.

This is the clean, supported extension point, and it is what the pack needs.

## 3. Alfheim's terrain — what has to change

Verified from `data/mythicbotany/worldgen/noise_settings/alfheim.json`:

| Setting | Value | Consequence |
|---|---|---|
| `default_block` | **`botania:livingrock`** | The world is not made of stone |
| `ore_veins_enabled` | **`false`** | No vanilla ore veins |
| Cave noise | **absent** — no `entrance`, `noodle` or `pillar` density functions | No vanilla cave systems; only MythicBotany's `cave`/`canyon` carvers |
| `sea_level` | 64 | Normal |
| `aquifers_enabled` | true | Normal |

Alfheim was built as a place you *visit* late. As a home world for ten eras it needs work.

**The livingrock problem is the important one.** Vanilla and modded ore features place against
`#minecraft:stone_ore_replaceables` — stone, deepslate, granite, andesite, diorite. Livingrock is in
none of them, so **almost no ore generates in Alfheim at all.** MythicBotany compensates with four of
its own features: `elementium_ore`, `dragonstone_ore`, `gold_ore`, `extra_gold_ore`.

Two ways forward, and they are a design choice rather than a bug fix:

**Option A — add `botania:livingrock` to `#minecraft:stone_ore_replaceables`.** One small datapack
file. Every vanilla and modded ore then generates in Alfheim normally. Cheap, and it makes Alfheim a
conventional home world.

**Option B — curate the ore table deliberately.** Leave livingrock out of the replaceables tag and
author exactly the ores Alfheim should have. Elementium, gold, dragonstone and mana crystals stay;
iron, coal, redstone and diamond are scarce or absent, and must come through the gate.

**Option B is the pack.** It converts a worldgen limitation into the premise, and MythicBotany's
existing ore set is already most of the way there. It needs one guard rail: the player must be able to
reach the first Mana Pool and the gate itself without iron. Verify that in Era I before committing —
if a hard iron requirement sits in the early chain, allow a small trickle rather than redesigning.

Caves still need adding either way. A world with no caves and no mining is a poor place to spend ten
eras.

## 4. Midgard

**Midgard is `minecraft:overworld`.** No new dimension is registered, and nothing has to be built:
the Overworld is left exactly as vanilla ships it, and every TerraBlender mod injects into it the
way its author intended.

In fiction it is the world that died — the elves' trading partner, then their expedition ground.
The player never starts there; they arrive through the gate.

**This is what the earlier design was fighting.** The previous revision of this section said
"TerraBlender cannot deliver this… Midgard therefore needs its own biome source", and listed four
change requests to Continuity Works. All of that existed only because Alfheim was sitting in the
Overworld slot. Vacate the slot and the problem is not solved so much as **deleted**:

| Was | Now |
|---|---|
| CW must move its anthology into a custom dimension | CW injects into the Overworld — already correct |
| Midgard needs a bespoke biome source | Vanilla multi-noise, unmodified |
| Regions Unexplored generates nowhere (B-05) | Generates in Midgard. Its lush Earth biomes suit a dead *Earth*. |
| CW must author an Alfheim biome layer | Ours already exists — 6 biomes, `libx/biome_layer/alfheim.json` |

**What Midgard ships on today:** vanilla multi-noise plus **Regions Unexplored 0.5.6** (installed,
TerraBlender-injected, working). Continuity Works' 146 anthology biomes land on top when **CW-1** is
fixed — see `CONTINUITY_WORKS_DEFECTS.md`. Until then the jar stays quarantined, because it now
generates the Overworld and an unbound feature holder there is a crash risk from world creation
onward, not something deferred until the player first uses the gate.

This also settles B-23 without a decision. A neon-virtual biome in a dead industrial world is
*right*; the anthologies were only ever wrong when they were going to generate around the Hollow
Court.

## 5. Realm layout

| Realm | Dimension | Role |
|---|---|---|
| **Alfheim** | `mythicbotany:alfheim` | Home. Elven, magical, metal-poor. Where the campaign happens and where the player spawns. |
| **Midgard** | `minecraft:overworld` | The dead industrial world. Trade partner, then expedition ground. **Era IV+** (gate settled 2026-09-03; see `CAMPAIGN_ERAS.md` §3). |
| The Nether | `minecraft:the_nether` | Vanilla. **Reached from Midgard** — portal linking is hardcoded Overworld↔Nether, so it is not directly reachable from Alfheim. Verify at level 9. |
| The End | `minecraft:the_end` | Vanilla, late-game. |
| Further realms | Continuity Works | The remaining Nine Realms as the campaign needs them |

**B-14 "Alfheim Unbroken" is dissolved.** It proposed keeping `mythicbotany:alfheim` as a separate
late-game fragment alongside an Overworld Alfheim. There is now only one Alfheim and the player
lives in it.

## 6. What Continuity Works needs to change — **one thing**

**Ask 1 — fix CW-1.** An unbound `placed_feature` holder crashes chunk generation. Full report and
reproduction in `CONTINUITY_WORKS_DEFECTS.md`. This is the only outstanding item, and the only
reason the jar is quarantined.

**Asks 2–4 are withdrawn.** They existed because Alfheim held the Overworld slot. It no longer does:

| Withdrawn ask | Why it is void |
|---|---|
| Move the anthology into a custom Midgard dimension | The Overworld *is* Midgard. TerraBlender injection is correct as shipped. |
| Author an Alfheim biome layer | Ours exists — 6 biomes in `kubejs/data/mythicbotany/libx/biome_layer/alfheim.json`. |
| Alfheim terrain viability | Solved in this pack (§3). Nothing needed from CW. |

**Still wanted, unchanged:** `continuityworks_spawn_protection`, for the Greatbole —
`SPAWN_ZONE.md` §7.1.

**Unchanged and correct:** Forge 1.20.1 targeting, unique mod IDs, convention tags on its biomes,
not claiming the Overworld generator.

## 7. Consequences elsewhere

- **Regions Unexplored works again, and has a home.** B-05 is closed. Its 170 biomes reach the world
  through TerraBlender's Overworld injection, which now exists again — and the Overworld is Midgard,
  so lush Earth biomes are exactly right for a dead *Earth*. It stays.
- **The preset override is deleted, not deferred.** `kubejs/data/minecraft/worldgen/world_preset/normal.json`
  is removed. B-12 — "the single riskiest unproven assumption in the project" — is closed by ceasing
  to make the assumption.
- **Spawn and respawn need handling.** No dimension-management mod is installed, so first-join
  placement and respawn-before-Midgard are KubeJS work (`02_spawn_dimension.js`). Vanilla would
  otherwise start and respawn the player in the Overworld — i.e. in Midgard, before the gate exists.
- **Nether access moves behind the gate.** Nether portal linking is hardcoded Overworld↔Nether, so a
  portal lit in Alfheim is unlikely to link. Blaze powder and ghast tears are already referenced by
  the Era chains, so the route to the Nether probably runs *through* Midgard. Narratively fine;
  **must be verified at level 9, not assumed.**
- **Structure re-tagging, narrowed further.** MythicBotany's biomes carry no `minecraft:` or `forge:`
  convention tags — confirmed by scan. Anything that should appear in Alfheim needs its placement
  tags extended; anything belonging to the dead world now needs no work at all, because Midgard is
  the Overworld and vanilla placement already finds it.
- **`Level.OVERWORLD` is the new risk surface.** See §1. MineColonies is the one to watch.

## 8. Validation

| Level | Condition |
|---|---|
| 1 | Datapack JSON parses; `pack.mcmeta` `pack_format` 15 |
| 3 | **passed** — 84 jars, 130 mod IDs, 0 missing deps, 0 range violations |
| 8 | Pack boots |
| **9** | **Fresh world: the player wakes in Alfheim, on Alfheim terrain, and survives** |
| 9b | Alfheim biome variety is adequate — 11 biomes; measure, do not assume |
| 9c | Midgard (the Overworld) generates and carries Regions Unexplored's biomes |
| 9d | Copper, iron and coal are findable; the Era I chain is completable — `tools/check_worldgen.py` passes statically |
| 9e | Respawn returns the player to Alfheim, not Midgard |
| 9f | **Whether a Nether portal lit in Alfheim links to anything** |
| 10 | Elven villages generate ruined and clustered; spawn protection behaves per `SPAWN_ZONE.md` §7.1 |
| 10b | `Level.OVERWORLD` sweep — MineColonies colonies, Botania flower mechanics, Mine and Slash |

Level 9 is still the gate for everything, but it is now a *cheaper* gate: it tests a dimension the
mod author already ships rather than an override this project invented.
