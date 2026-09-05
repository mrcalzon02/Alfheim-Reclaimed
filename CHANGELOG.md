# Changelog

Completed changes with evidence. Intent lives in `BACKLOG.md`; live state in `EXECUTION_STATE.md`.

---

## 0.13.1-design — 2026-09-04 — the boot crash in the zombie habitat gate

Every boot since the habitat pass died in FML:

```
KubeJS (kubejs) encountered an error during the complete event phase
  There were KubeJS startup script syntax errors!
```

One error stood behind it:

```
Error in 'EntityJSEvents.spawnPlacement': Registering a new Spawn Predicate requires a
nonnull placement type! Entity Type: infectious:acid_zombie
```

Not the fey wildlife generated in the same run — that script registered its 18 species without a
single warning. `acid_zombie` is index 0 of 99 gates, so the first `event.or(...)` threw and took
the whole handler with it, including the `zombie_variants` block underneath.

**Why `or` cannot work here.** It maps to Forge's 3-arg `register(type, predicate, Operation.OR)`,
which passes a null placement type. `SpawnPlacementRegisterEvent.register` accepts null only when
the entity already has an entry — and no Infectious entity does, because MCreator registers
placements in `FMLCommonSetupEvent`, which fires *after* `SpawnPlacementRegisterEvent`. Structural,
not incidental: all 99 gates were unreachable.

**Why `replace` is not the repair.** It would insert the entry, `fireSpawnPlacementEvent` would
write it into `DATA_BY_TYPE`, and the mod's own later `SpawnPlacements.register` would throw
`IllegalStateException: Duplicate registration`. The same boot failure, one phase later.

The loop is removed. The 15 `zombie_variants` placements stay — that mod registers none of its own
(it gates spawning with a `checkSpawnRules` mixin), so `replace` is the correct operation there,
and the ids were checked against `entity_type.json` before the change. `alfheim:populated_biomes`
and every biome modifier are untouched, and Infectious still reaches Midgard through them — the
only dimension its Overworld-gated condition accepts. Alfheim gets no Infectious spawns; that gap,
and the Java-side hook it would take to close, are B-76.

Acceptance: **runtime validated**, ladder level 8. `python tools/run_server.py --run` exited 0
after 315.1 s (`server/console-20260904-174418.log`): 12/12 startup scripts with 0 errors and 0
warnings, `alfheim validation: startup reached`, world generated, command script run, clean stop,
no crash report. Zero `[ERROR]` lines in `logs/kubejs/startup.log`, `logs/kubejs/server.log` and
`logs/latest.log`. Whether the variant placements actually yield spawns is **not** claimed — no
spawn was observed.

---

## 0.13.0-design — 2026-09-04 — Guild Regalia assets and registration

Built all 63 catalog items: 36 class signets/emblems and 27 profession cuffs across three ranks.
Each has a 16x16 RGBA icon, generated model, display name, rank rarity, unstackable registration
and one additive slot tag. Textures use PIL edits of vanilla bases plus existing Alfheim rank
materials. Signets have transparent openings; family silhouettes, owner hues and rank brightness
are checked. The full review sheet is `tools/curios_review.png`.

`tools/check_curios.py`: 0 problems, 18/18 injected faults detected. All 133 Curio outputs are
byte-identical across reruns. Shared texture primitives preserve all 83 earlier item textures
against the pre-refactor generator; regenerating the 167 earlier assets/registration changes no
bytes. Era, surface, spawn-hub, worldgen and Hollow Court checks pass; feature ordering has no
cycles. Coverage separately reports 66 per-item gaps, 1 process gap and 14 unscoped steps, with
no ordering violations; it must not be reported as zero gaps merely because the tool exits 0.

Acceptance: **static validated**. No new effects, recipes, native gear behavior, proof ledger or
slot-capacity changes. Client registration, rendering and equipping still require runtime checks.

---

## 0.9.1-design — 2026-09-04 — **Liquid Bifrost, integrated**

The fluid registered and the recipes loaded in 0.9.0, but the material was not yet *part of the
pack*. This pass connects it.

### What "registered" was hiding

| | before | after |
|---|---|---|
| Tier textures | none — four missing-texture checkerboards | derived art, four distinct silhouettes |
| Item tags | none | `#alfheim:bifrost`, `#alfheim:bifrost_distilled` |
| Era scoping | one un-scoped file; coverage could check *nothing* | `18_era2_`, `19_era3_`, `20_era7_` |
| Quests | none | nine, across three eras |
| Compendium | no entry | 7-entry chapter |
| Renewability | **finite** | Era VII Create mixing route |

KubeJS registers an item happily with no model at all, and no registry or recipe check notices.
The four tiers had been loading cleanly and rendering as the checkerboard.

### The finiteness problem — B-73

Pools are 1-in-40 chunks and do not come back, so a bridge between thirteen magic systems was a
consumable that ran out. A player who spent their last bucket on the wrong conversion had
permanently lost access to a system — a failure invisible until it has already happened.

```
create:mixing, heated
   2 x #alfheim:crystal_shards + 1 x botania:mana_powder + 500 mB water
   -> 250 mB alfheim:liquid_bifrost
```

Era VII because `cr_mix` is first taught by the Era VII ladder — the earliest era that can
require a mixer without breaking the ordering rule. `#alfheim:crystal_shards` already held
exactly the six crystals with a budding block, so **the tag is the renewability guarantee**;
`frost_shard` has no budding form and was already excluded.

### Coverage

```
                    before    after
per-item gap          74        65
bifrost outputs    uncovered   all covered
ordering violations    0          0
Compendium items      50         57
```

### Caught by the checkers

1. **`worldgen()` was silently deleted.** Splitting the recipe script replaced everything
   between two anchors, and `worldgen()` sat between them. `NameError` on the next run.
2. **Fluids were read as items.** `fluid: 'minecraft:water'` was extracted as an item id and
   reported unregistered — true of the item registry, irrelevant to the recipe.
   `fluid`/`fluidTag` now in `NON_ITEM_KEYS`.
3. **The pack's own tags were not counted.** `#alfheim:crystal_shards` — the contract the whole
   Era VII recipe rests on — was reported as declared by no jar. It is declared by us.
4. **The filled bucket had no source.** E3 was right that nothing *crafts* it; it is filled from
   a pool. `world_sourced()` now knows a fluid registration implies a fillable bucket. (An empty
   bucket is vanilla-craftable and was never the question.)

Each fix proven by fault injection, then restored.

### Final state

```
check_era.py --all        RESULT: 0 problem(s)
check_spawn_hub.py        RESULT: 0 problem(s)
check_worldgen.py         RESULT: 0 problem(s)
check_hollow_court.py     RESULT: 0 problem(s)
```

414 quests across 10 chapters, 7 reference chapters, 64 Compendium entries.

---

## 0.12.1-design — 2026-09-04 — the state documents catch up to the state

No gameplay change. A reconciliation pass re-derived the Guild Regalia planning claims from the
tools and repaired four documents that disagreed with the project.

**Reproduced exactly.** `tools/build_curio_plan.py` reports 6 class suites, 9 profession suites, 63
planned items, 46 installed functional anchors and 0 missing IDs; `tools/build_curio_inventory.py`
reports 147 wearable IDs (114 functional, 33 cosmetic), 19 slot definitions and 14 live slot types.
Both exit 0. The plan generator is deterministic — `SUITE_MATRIX.md` and `curio_suite_catalog.json`
verify byte-identical across reruns. The claim that no Curio is registered is confirmed by absence:
`kubejs/` contains zero `curios:` references and zero signet/emblem/cuff/torque ids. All seven
project checkers report 0 problems.

**Fixed — `BACKLOG.md` had no Curios item.** The planning pass was recorded in `EXECUTION_STATE.md`
and here, but nothing in the backlog carried its intent, its dependency or its next action, so the
next session had no eligible item to pick up. Added as B-74 with reproduction evidence and accept
criteria at levels 4 and 11.

**Fixed — duplicate version numbers.** Two entries claimed `0.10.0-design` and two claimed
`0.9.0-design`, all dated 2026-09-04. The surface pass is renumbered `0.12.0` and the canopy pass
`0.11.0`; the Guild Regalia keeps `0.10.0` and the Reclaimed Armory `0.9.0`, matching the order the
four passes actually ran.

**Fixed — `README.md` was four things stale.** It still described Alfheim as the Overworld, a
premise struck on 2026-09-02; it claimed 95 mods and "boots to title screen" when levels 8 and 9
have both passed headlessly; and it named B-02 and B-12 as next, B-12 having been closed when the
world-preset override was dropped.

**Fixed — `INSTRUCTIONS.md` profile table.** Pack version `0.2.0-design` → `0.12.0-design`. Mod
count 97 → 83 jars counted on disk, with a note that no loaded-mod total should be quoted until a
run prints one: `logs/latest.log` does not, and its 149 "Found mod file" lines count jar-in-jar
libraries rather than mods.

---

## 0.12.0-design — 2026-09-04 — **the surface is no longer empty**

Alfheim had one landmark of ours across sixteen biomes. It now has thirty-three, and a shop
that sells directions to them. B-73; design `alfheim_reclaimed_design/THE_SURFACE.md`.

### Thirty-two structures, two per biome

Ten parametric archetypes across seven palettes:

| Archetype | Count | Where |
|---|--:|---|
| castle | 5 | Ashwatch Keep, Riven Hold, the Hollow Bastion, the Warren Gate, Hillcrown Keep |
| barrow | 4 | the Grey Barrow, the Garland Stones, the Rotwood Barrow, the Waystone Ring |
| hall | 4 | the Silver Moot, the Pyre Hall, the Open Moot, the Grange |
| quarry | 3 | the Sundered Quarry, the Starveling Pit, the Hillcut |
| crater | 3 | the Marchfall, the Cinderglass, the Harvest Crater |
| tower | 3 | Frostwatch Spire, the Verge Spire, Boughwatch |
| span | 3 | the Broken Causeway, the Severed Span, the Canopy Span |
| shrine | 3 | the Sunken Wayshrine, the Bloomfall Shrine, the Lake Shrine |
| aqueduct | 2 | the Drowned Arcade, the Lake Arcade |
| wreck | 2 | the Boneyard Hulk, the Mire Hulk |

Every biome gets one thing that was **built** and one thing that was **done to the land**.
Rarity runs in three bands — shrines and waystones are common, keeps and craters and quarries
are rare — and every `structure_set` carries its own salt, because two `random_spread` sets
sharing spacing and salt do not become neighbours, they generate in the same chunk.

### The Cartographer

A new campaign chapter. Loremistress Anwe of the Hollow Court sells one Explorer's Map per
archetype — ten purchases, each repeatable as often as you can pay:

| Chart | Price |
|---|---|
| The Wayshrines | 6 white petals |
| The Waystones | 6 light gray petals |
| The Moot Halls | 8 yellow petals + 2 dreamwood |
| The Watchtowers | 8 cyan petals + 4 livingrock |
| The Aqueducts | 8 blue petals + 4 livingrock |
| The Broken Spans | 8 brown petals + 4 livingrock |
| The Wrecks | 10 purple petals + 4 dreamwood |
| The Quarries | 12 orange petals + 8 livingrock |
| The Craters | 12 red petals + 8 livingrock |
| The Keeps | 16 magenta petals + 12 livingrock |

Petals and the dimension's own stone, both renewable from the first hour. Nothing on that list
is a spine material or a ladder intermediate: a chart is knowledge, and `INSTRUCTIONS.md` §6.3
puts convenience outside the gating doctrine. What a chart cannot do is make the place
survivable, and the chapter says so in its own words.

An Explorer's Map is not an item, it is an item plus a search performed at the moment of
handing it over, so the reward runs `/loot give {p} loot alfheim:explorer_maps/<type>` and the
loot table carries the `exploration_map` function. The chart finds the nearest structure of that
TYPE — the same way `#minecraft:village` covers five village types.

### Also

- `Piece` moved to `tools/structure_nbt.py` and is now shared by both structure generators
  rather than copied. Proven neutral by decompressed-payload comparison of all four spawn-hub
  pieces.
- `Piece` counts blocks placed outside its own box. Three structures were shipping with a
  piece silently missing — a mast, a dome, a ring of standing stones.
- The tower stair is now provably climbable rather than decorative.
- `check_era.py`'s E11 single-writer guard was reading docstrings as writes. It parses now.

### Validation

`tools/check_surface_works.py`, fourteen checks, **all eleven self-tests fire** on synthetic bad
input. Suite: check_surface_works 0 · check_spawn_hub 0 · check_worldgen 0 ·
check_feature_order 0 cycles · check_coverage 0 · check_hollow_court 0 · check_era --all 0.

**`static validated`. Nothing here has been generated in a world.** THE_SURFACE.md §7.1 lists
exactly what that leaves unproven.

---

## 0.11.0-design — 2026-09-04 — **the tree has a canopy, and the hub knows where it is**

Nine items reported from a live world. Seven fixed and runtime-proven; two blocked on a
decision only the user can make.

### The canopy — B-67

The crown was **culled at placement**, every time, silently. Jigsaw rejects any piece landing
further than `max_distance_from_center` from the structure start, and the tree was 184 blocks.

Raising the cap to 128 made it worse — world creation refused the structure outright:

```
Caused by: java.lang.RuntimeException: Structure size including terrain adaptation
                                       must not exceed 128
```

`JigsawStructure`'s codec validates `max_distance_from_center + margin <= 128`, and the margin
is **12** for every `terrain_adaptation` except `none`. With `beard_thin` the real budget is
**116**, which is exactly where the original 116 came from. Tree rebuilt at **112**.

Proven by a probe marker baked into `greatbole/crown` — the piece that was being culled:

```
The nearest alfheim:greatbole is at [96, ~, -96] (135 blocks away)
crown probe   [72.5d, 157.0d, -71.5d]
hub anchor    [78.5d,  66.0d, -71.5d]
```

Base origin 65 + 72 (base + trunk) + 20 (probe offset) = **157**, exactly.

### The claim and the spawn — B-68

`concentric_rings` does not pin a structure to `0,0`; it snaps ring 0 to a `preferred_biomes`
match up to 112 blocks away. The claim was a hardcoded ±96 box at the origin and the spawn was a
marker `spreadplayers`-dropped at the origin. The tag held **3 of 16** biomes and is read twice —
as a *validity* test (off-tag, the tree does not generate at all) and as a *position* test.

Tag widened to 14 of 16; the spawn anchor is now **baked into `greatbole/base.nbt`** so it lands
with the structure; claim widened to 192.

The two-deadline resolve loop is part of the fix. `forceload add` only *marks* chunks, so the
anchor does not exist on the tick `hub/create` runs. A single 2-minute deadline fired the
fallback at 125s and the anchor appeared at ~145s — stranding the world at the origin
permanently. The fallback is now provisional:

```
[Alfheim] provisional origin spawn set; still waiting for the Greatbole.
[Alfheim] world hub anchored to the Greatbole gate chamber.        (5s later)
[Alfheim] hub: created
```

On the validation seed the origin *is* a lake, so the designed fallback ran, the tree landed 135
blocks out — and the hub still found it.

### Density — B-69

| | before | after |
|---|---|---|
| Geodes, densest biome | 8.0× vanilla amethyst | 3.0× |
| Geodes, median biome | 4.8× | 1.6× |
| Bifrost / diluted pools | 1–4 per 2 chunks | 1 per 12 chunks |

The geode statistic was the bug's accomplice: `gen_crystals.py` printed the *mean* across geode
types, which no player experiences — a player stands in one biome and meets only the types valid
there. It now reports per biome and names the densest.

The bifrost and diluted pools were never ours: `mythicbotany:mana_crystals`, whose feature class
references `bifrost`, `bifrostPerm` and `dilutedPool`.

### Population — B-70

**1 → 15 fey species**, across all 11 biomes, each with its own roster. Plus hostile wood elves
in the five worst-hit biomes and frogs in the wet ones.

### New systems

- **Liquid Bifrost** (B-71) — a real flowing fluid, four-tier chain, conversions into five magic
  systems. `alfheim_reclaimed_design/LIQUID_BIFROST.md`.
- **Court skins** (B-72) — the Magister and the Captain, via reserved `DataSkinSwap` slots.
- **Courtyard** — fountain with a running spout, colonnade, vines, rubble.
- **The gate** — recessed one block behind its frame, confirmed at z=23 against a chamber wall
  at z=22.

### Checks added

| | |
|---|---|
| **S5** | enforces the `terrain_adaptation` margin — the failure that aborted world creation |
| **S9** | walks the pool graph and measures the assembled tree against the real budget |
| **S10** | `#alfheim:has_greatbole` must cover the layer, minus the two unbuildable biomes |
| **E12** | now knows a KubeJS fluid registration also creates a bucket |

Each was proven by fault injection and restored. S9 reproduces the exact historical numbers
(120 vs 116).

### Final state

```
check_era.py --all        RESULT: 0 problem(s)
check_spawn_hub.py        RESULT: 0 problem(s)
check_worldgen.py         RESULT: 0 problem(s)
check_hollow_court.py     RESULT: 0 problem(s)
```

Headless run, 298s, exit 0. No error in the `alfheim:` namespace.
`[minecraft:fluid] Found 36 tags, added 2 objects` — the fluid registered.

### Caught by the checkers before the server saw them

1. `mythicbotany:mana_infusion` does not exist — the type is **`mythicbotany:infuser`**, and it
   takes an ingredient *list* plus `fromColor`/`toColor`, not a single `input` (**E13**).
2. The fluid was registered **unqualified**, which would have given
   `kubejs:liquid_bifrost_bucket` while every recipe named `alfheim:*` — a silent total failure.
3. `execute if biome` does **not** exist in 1.20.1; Brigadier parses `if b` as `if blocks`.

---

## 0.10.0-design — 2026-09-04 — the Guild Regalia plan

Specified the Curios integration phase without registering gameplay content yet. The installed-jar
inventory identifies 147 wearable IDs, 114 functional items, 33 Botania cosmetics and 14 slot
types loaded by the last headless run. The plan maps 46 functional installed Curios into optional
class and profession workflows.

The catalog defines 63 new elven pieces: 36 class items from a signet and emblem at three ranks for
each of six native classes, plus 27 profession cuffs at three ranks for all nine native
professions. It adds no slot types and changes no slot capacity. Class signets use `ring`, class
emblems use `necklace` or `charm`, and one active trade cuff uses `bracelet`.

The central rule is one transaction per reward. A Curio reacts only after the owning system accepts
the native action; it may display state, route the actual result, or open an explicit station
operation. It does not repeat XP, drops, class access, station authority or mod resources. Crafted
rank remains tradeable while profession proof is player-owned and every effect is capped by the
wearer's native profession tier.

`tools/build_curio_inventory.py` and `tools/build_curio_plan.py` reproduce and validate the
inventory and suite catalog. The current build reports 6 class suites, 9 profession suites, 63
planned items, 46 installed anchors and 0 missing IDs. Runtime implementation begins with a slot
capability probe and a Warrior/Mining vertical slice; exact numerical balance follows event-path
validation.

---

## 0.9.0-design — 2026-09-04 — the Reclaimed Armory

Implemented the six-class elven armory from the approved design:

| Delivered | Count |
|---|---:|
| Registered equipment | 480 |
| Weapon/offhand families | 24 across 10 material eras |
| Four-piece armor sets | 60 |
| Inventory textures | 480 |
| Worn armor layer textures | 120 |
| Mine and Slash gear types | 48 |
| Auto-item and custom-soul mappings | 480 each |
| Native Gear Crafting profession recipes | 480 |

The recipes bind the armory to the pack economy: every piece consumes its embedded era material,
the matching Mine and Slash mining tier and salvage stone; era III+ pieces also consume a class
crystal. Crown-era recipes require the native pinnacle unlock.

The image generator returned fake checkerboard/white backgrounds for several class atlases. The
production pipeline now ignores apparent transparency and runs every class through Pillow
edge-connected background removal. It also strips palette-quantization alpha haze at 16 or below
to literal RGBA `(0,0,0,0)`. All 480 item textures have four alpha-zero corners and 36.9%–84.4%
literal transparent area. All 120 worn layers use binary alpha with 67.8%–86.3% transparent area.
Six class review sheets and a combined overview make edge residue visible over a drawn QA
checkerboard; production textures contain no checkerboard.

A visual pass then caught background islands trapped inside the Hunter and Duskkeeper bow curves.
The cleaner now removes large enclosed neutral components specifically from bow source cells. All
20 bow variants contain a measured enclosed alpha-zero region of 26–59 pixels at 32×32, and the
generator treats less than 20 as a build failure.

The same review found smaller islands inside crossbow frames and an atlas fragment beside the
Waywatcher necklace chain. Family-specific cleanup now opens all 20 Waywatcher/Dawnsinger
crossbows without erasing the Dawnsinger ivory limbs. Their enclosed alpha-zero openings measure
11–65 pixels. All ten necklaces retain an 11–15 pixel transparent loop, and detached side spill is
removed before recoloring.

Runtime evidence: Forge 47.4.10 loaded 9/9 startup scripts with zero errors and zero warnings. A
temporary live-registry probe reported exactly 48 armory gear types and 480 each of auto items,
custom item generations and profession recipes; representative lookups all returned true. The
server reached `Done`, saved its worlds, and exited 0. Evidence and payload hash are in
`tools/armory_manifest.json`.

The wider profession plan remains scoped in `PROFESSIONS_AND_MMO.md`: custom-bloom mining XP,
expanded Infusing, cooking and alchemy are not included in this armory pass. Curios and numerical
balance are intentionally the next phase.

---

## 0.8.0-design — 2026-09-03 — **the player wakes in Alfheim**

### B-44 proven

A fresh world, read from the save rather than a log line:

```
Dimension        mythicbotany:alfheim
SpawnDimension   mythicbotany:alfheim     SpawnForced 1
spawn flags      {'alfheim_home_spawn_v2': 1}
chunks           mythicbotany:alfheim -> 12 region files
```

`python tools/check_spawn.py` → 0 problems. The `_v2` flag can only have been written after
`confirmAndAnchor` observed the arrival. `execute in <dim> run tp` does cross dimensions on this
build and `scheduleInTicks` exists — both previously unproven. **Level 9 check 9 passes, 9e is
anchored.**

### Fixed — B-45, `lockAlfheim` blinded the player for doing the intended thing

The spawn fix worked and the player was blinded on arrival. `config/mythicbotany.json5` ships
`"lockAlfheim": true` — "players that manage to get to alfheim via another mod but have not drunk
the mead of kvasir should get a blindness effect". It exists to stop progression-skipping; this
pack spawns the player there by design, so it fires on the intended path.

Why it read as a rendering fault: `minecraft:blindness`, `Duration: 59` reapplied forever,
`Ambient: 1`, `ShowParticles: 0`, and not one line in the log.

**Fixed by setting it `false`.** That is the whole fix — one key, no code. `check_spawn.py` grew a
20-line S5 that reports the key and a blinded player, so a config regeneration or mod update
restoring the default is visible rather than silent; it is a detector, not a workaround, and can be
dropped if unwanted. Residual blindness on an existing character is stale save data and expires
about three seconds after restart.

---

## 0.7.0-design — 2026-09-03 — the spawn verifies before it records

### Fixed — B-44, the player never reached Alfheim

The premise of the pack did not work, and the project had recorded it as working. Three
compounding faults in `02_spawn_dimension.js`, all now fixed:

| Fault | v1 | v2 |
|---|---|---|
| Wrong command | `execute in <dim> run spreadplayers` never crosses a dimension boundary. It sampled **Alfheim's** terrain to choose a landing spot — generating exactly one Alfheim region — then placed the player at those coordinates in **Midgard** | `execute in <dim> run tp <name> 0 320 0` first, then `spreadplayers` *within* Alfheim for a safe surface landing |
| Recorded without observing | `console.info('... sent to ...')`, fired unconditionally after the commands | `execute in <dim> if entity @e[type=minecraft:player,name=…,limit=1]` — `@e` is dimension-scoped, so the game is asked where the player is, in pure vanilla commands |
| Latched an unverified flag | set on the login event, turning a transient failure into a permanent one | set only inside `confirmAndAnchor`, after arrival is confirmed; a failure retries next login |

The save had recorded the failure precisely all along: the player stood at Midgard
`(189, 64, -1319)` with `SpawnForced=1`, while the only Alfheim region ever generated was
`r.0.-3` — the region containing `(189, -1319)`.

Flag renamed `alfheim_home_spawn_v1` → `_v2`. v1 meant "commands issued"; v2 means "arrival
observed". Any character v1 stranded in Midgard is re-sent on next login, so the fix is
self-healing and needs no repair commands.

### Added — `tools/check_spawn.py`

Asks the **save**, not the log: S1 current dimension, S2 respawn dimension, S3 Alfheim generated
chunks, S4 the verifying flag latched. Validated in the failing direction against
`saves/New World (1)`, where it reports exactly the three faults above.

This is the direct answer to how the original error slipped through: a script's own log line is a
statement of intent, and nothing was reading the destination.

**Static only.** `execute in <dim> run tp` is standard vanilla and `node --check` passes, but
neither it nor `scheduleInTicks` has been observed on this KubeJS build. Both fail safe — the flag
stays clear and the warning is loud. A fresh world is the acceptance.

---

## 0.6.0-design — 2026-09-03 — Midgard is Continuity Works only

### Changed — vanilla and Regions Unexplored silenced in the Overworld

At the user's direction. Continuity Works was never quarantined or disabled: it loaded, registered
its TerraBlender region at 14:31:15, and had all 144 biomes enabled. It simply held **9%** of
Midgard shared across ~144 biomes — roughly 0.06% each — which is why walking 2 km found none.
Arithmetic, not a defect.

| Region | Was | Now |
|---|---:|---:|
| `minecraft:overworld` | 10 | **0** |
| `regions_unexplored:primary` / `:secondary` / `:rare` | 11 / 8 / 1 | **0 / 0 / 0** |
| `continuityworks_biomes:overworld_templates` | 3 | **20** |
| `ars_nouveau:overworld` | code | **code — no config key, cannot be zeroed** |

New tool `tools/set_midgard_biomes.py` (`--show`, `--mode cw-only`, `--mode mixed`) owns these.
It is a tool rather than a datapack because TerraBlender reads the weights from TOML at mod load;
no datapack can reach them. It rewrites one key per file in place, preserving comments, and reads
back.

**Consequences, all real:** Regions Unexplored now generates nothing (B-05 reopened with the
opposite disposition — nothing in `kubejs/` references it, so removal is cheap); Ars Nouveau
archwood stays because `ArchwoodRegion` is hardcoded; and whether Midgard keeps oceans and rivers
with vanilla's region at 0 is **unverified** — it depends on TerraBlender backfilling the parameter
space, and only a new world settles it.

### Fixed — `check_era.py` counted task titles as quests

The validator sweep after that change went from 0 problems to **42**, all `E9 quest has no id`.
The cause was neither the config change nor the quests: **FTB Quests rewrites
`config/ftbquests/quests/chapters/*.snbt` on every world load**, alphabetising every object's keys.
Our generator wrote `title:` before `id:`; FTB writes `id` first.

`check_era.py` opened a new quest record at each `title:` line and then claimed the next `id:` — so
once `id` preceded `title`, every quest's id was gone before its record existed, and task titles
opened phantom quests. Replaced with structural parsing: brace depth tracked outside string
literals, a quest is one balanced object directly inside `quests: [`, and `id`/`title` are read only
at the quest's own top level.

| | Before | After |
|---|---:|---:|
| Problems | 42, all false | **0** |
| Quests parsed | 24/era, inflated | **22/era, 215 total, 0 without an id** |

215 is exactly the figure recorded before the game had ever run — the independent check that the
parser is right rather than merely quiet. `INSTRUCTIONS.md` §5 now records that `config/ftbquests/`
is generator-authored but game-normalised.

### Fixed — `tools/read_player_inventory.py` NBT reader

`out[self.string()] = self.payload(nt)` evaluates the right-hand side first, so it read each tag's
payload from the bytes holding its name and desynced the stream — surfacing later as a bogus
`unknown tag 95` that looked like an unsupported modded tag. Two statements instead of one. This is
what made B-44 diagnosable.

---

## 0.5.0-design — 2026-09-03 — **the pack generates a world**

Attempt five created a world. First runtime evidence the project has ever had about world
generation, after four crashes and three distinct causes.

> **Corrected in 0.7.0:** this entry originally said the player woke in Alfheim. They did not — the
> claim rested on the spawn script's own log line. See B-44.

### Level 9 — world generated

| | |
|---|---|
| Save | `saves/New World (1)`, created 14:18:04 |
| Start region | prepared in **20.5 s** |
| Crash reports | **0** |
| Midgard `minecraft:overworld` | 13 region files, 18 MB |
| Alfheim `mythicbotany:alfheim` | 1 region file, 2.2 MB |

```
[14:18:39] [Server thread/INFO]: 02_spawn_dimension.js#36:
  [Alfheim Reclaimed] mrcalzon02 sent to mythicbotany:alfheim (first join)
```

That is B-37 satisfied at runtime, and it is the first confirmation that the two-world architecture
adopted on 2026-09-02 — Alfheim as MythicBotany's own dimension, the Overworld left vanilla as
Midgard — actually works in a running game rather than only on paper.

**Level 9 is partially passed, not passed.** World creation, both dimensions generating, and the
home-dimension spawn are confirmed. Ore findability (9d), respawn (9e), Nether portal linking (9f),
ruined villages (10) and holding up thousands of blocks out are all still unverified — and both
earlier crashes landed ~625 chunks from spawn, so a world that creates has proved nothing yet about
the rest of the map.

**Level 8 passes on the current load path.** 85 jars, 0 crash reports, 27 ERROR lines, none
load-blocking.

### Runtime found eleven recipes that every static check passed

`check_era.py --all` reports 0 problems across 376 recipes. The game refused **eleven** of ours at
load — three schema families in `mythicbotany:infuser`, `create:sequenced_assembly` and
`create:milling`/`create:pressing`, plus two Fey Altar recipes that hand Feywild's JEI category a
fifth ingredient it indexes only four of. They are simply absent from the running world: no error
the player sees, no route to the item.

Level 4 is therefore **rejected at runtime**, not `passed (static)`. The checker proves ids exist
and are reachable; it never checked each recipe type's schema. Recorded as B-41 and B-42 — and the
checker gap matters more than the eleven recipes.

This is exactly the failure `INSTRUCTIONS.md` §6.3 names: a script that parses is not a script that
works.

### Also surfaced

- **B-43** — `jaffabricate` ships `minecraft:leaves` (items) pointing at `#jaffabricate:orange_leaves`
  and never ships that item tag, only the block one. The `minecraft:leaves` item tag fails to load
  and takes `completes_find_tree_tutorial`, `minecolonies:fletcher_ingredient` and
  `minecolonies:compostables` with it. One datapack file fixes it.
- **B-30 confirmed at runtime** — `mythicbotany:feysythia` is uncraftable; its recipe calls for
  `feywild:lesser_fey_gem`, which Feywild 5.5.5 does not ship.
- `tools/read_player_inventory.py` cannot parse a modded player `.dat` (`unknown tag 95`). A reader
  limitation, not a save problem; repair it when the inventory question next matters.

---

## 0.4.2-design — 2026-09-03

Third and fourth world-creation crashes, same exception, different cause. Fixed — and the checker
that missed it was fixed first. Still static only; no world has been generated.

### The checker was wrong

`tools/check_feature_order.py` reported **0 cycles**, and the very next launch crashed with
`Feature order cycle found` between `continuityworks_biomes:ash_wastes` and
`continuityworks_biomes:quarry_megaplex` — **two biomes whose `features` arrays are byte-identical.**

A biome's JSON is not its final feature list. Forge applies `forge:add_features` biome modifiers at
runtime, and they **append** to the end of a step. The checker read files and nothing else, so all
57 feature-affecting modifiers in the pack — 2,667 biome-step changes across 20 mods — were
invisible to it. The previous entry's claim was correctly labelled static, but the model behind it
was incomplete, which is worse than a missing check because it reads as coverage.

It now applies `forge:add_features`, `forge:remove_features` and
`farmersdelight:add_features_by_filter` in the game's own order before running the sort. That order
is not obvious: Forge loads modifiers through `RegistryDataLoader`, whose `ResourceManager` listing
is a `TreeMap` over `ResourceLocation`, and `ResourceLocation.compareTo` compares **path first,
namespace second** — so modifiers apply by file path across every mod, not grouped by mod.

It also parses commented JSON now, because Forge reads these files leniently and
`irons_spellbooks:necromancer_spawns` ships `//` comments. All 194 modifiers in the load path are
read and classified; none is skipped silently.

**Validated against the real defect, not just a synthetic one:** run against the pre-CW-4 jar it
reports exactly one cycle, in step 2, between the same two features, with `ash_wastes` among the 8
biomes on one side and `quarry_megaplex` among the 128 on the other. Predicting the crash the game
actually threw is what proves the model; the synthetic `--self-test` only proves the graph code.

### Fixed — CW-4, one feature with two insertion points

| Modifier (sorted by file path) | Adds | To |
|---|---|---|
| `anthology_land_topology` | `land/topology` | `#anthology` — 128 biomes |
| `biome_cave_networks` | `caves/biome_network` | `#all_primary_biomes` — all of them |
| `foundation_land_topology` | `land/topology` | `#templates` — 8 biomes |

The same feature is added by two modifiers whose names sort on opposite sides of a third. An
anthology biome gets `land/topology` before `caves/biome_network`; a template biome gets the
reverse. 128 biomes assert one order, 8 the other, and no global order satisfies both.

**Fixed by renaming** both to a shared `land_topology_` prefix — `land_topology_anthology` and
`land_topology_templates` — so they are adjacent in the global sort and every biome receives the
two features in the same sequence. No byte of content changed; only the zip entry name, which is
the registry key that decides order. Verified that no other modifier in the pack sorts between the
two new names, and that nothing in the jar references either old name.

`tools/patch_continuity_works.py` now carries CW-1, CW-3 and CW-4, still building from the pristine
original: 307 entries, 2 renamed with byte-identical contents, **0** unintended byte changes,
reproducible on a re-run. Installed as
`ContinuityWorks-Forge-1.20.1-0.3.0-rc.2+cw1patch+cw3patch+cw4patch.jar`
(md5 `b2c6e3bf9ab2045410007ac15ba83720`). **Backport pending — B-39.**

| Check | Result |
|---|---:|
| `check_feature_order.py` vs the pre-CW-4 jar | **1 cycle** — reproduces the crash |
| `check_feature_order.py` vs the installed jar | **0 cycles** |
| `check_feature_order.py --self-test` | PASSED |
| `check_incoming_mod.py` | 0 fail, 0 warn, 6 pass |
| `check_dependency_ranges.py` | 0 blocking, 0 quarantine conflicts |
| `check_worldgen.py`, `check_era.py --all` | 0 problems |

---

## 0.4.1-design — 2026-09-03

Second world-creation crash root-caused. Five feature order cycles found; all five fixed. Still
static only — no world has been generated.

### Fixed — five impossible feature orders, in two authorities

A new world crashed on creation with `IllegalStateException: Feature order cycle found`, naming
`continuityworks_biomes:terraced_vineyard` and `ars_nouveau:archwood_forest`.

`FeatureSorter` does not generate a biome's features in the order that biome lists them. It
flattens every loaded biome into **one** global order per generation step, by topologically
sorting the "A immediately before B" constraints each biome asserts. Two biomes naming the same
pair in opposite orders make that order impossible. Like CW-1 it throws lazily, from
`ChunkGenerator`, so it lands on world creation with every static check already green — and, unlike
CW-1, it is not seed-dependent.

The crash report names only the first cycle it finds. Simulating the sorter over the whole load
path found **five**:

| Cycle | Where | Verdict |
|---|---|---|
| `patch_sugar_cane` ↔ `patch_pumpkin` | 41 CW biomes vs vanilla ×41, Regions Unexplored ×52, CW's own ×22, Ars Nouveau ×1 | CW deviant, and inconsistent with itself |
| badlands trio | CW `rocky_badlands` vs `minecraft:badlands` ×3 | CW deviant |
| `flower_meadow` ↔ `patch_grass_plain` | CW `flowering_meadow` vs `minecraft:meadow` | CW deviant |
| savanna trio | 25 CW biomes vs `minecraft:savanna` ×2 | CW deviant |
| `loose_dreamwood_trees` ↔ `motif_flowers` | `alfheim:bloomfall_vale` vs `mythicbotany:alfheim_plains` | **ours** |

**The fifth one is the important one.** It is in Alfheim's own biome layer, so it would have
crashed the dimension the player wakes in. It was invisible because the Overworld generates first
and crashed first — fixing Continuity Works alone would have moved the crash, not removed it.

### Ours — repaired at the generator

`tools/gen_alfheim_biomes.py` now carries a `FEATURE_ORDER` table read off MythicBotany's five
jar-owned biomes — `alfheim_grass` first, `loose_dreamwood_trees` before `motif_flowers`,
`extra_gold_ore` last in the ore step — and sorts every generation step through it. A feature with
no declared rank is a hard error rather than a silent cycle, which is exactly how `bloomfall_vale`
came to contradict `alfheim_plains` in the first place.

Regenerating changed **two lines in one file**, `kubejs/data/alfheim/worldgen/biome/bloomfall_vale.json`.
`check_worldgen.py` and `check_era.py` still report 0 problems.

### Continuity Works — CW-3, patched locally

67 of CW's 146 biomes had at least one step out of order. Sorted into the order the rest of the
pack already agrees on, derived at patch time by topologically sorting every biome source **except**
that jar — vanilla, the other 84 mods, our datapack — which is acyclic on its own (152 biomes,
0 cycles), so adopting it cannot introduce a new contradiction. Nothing added, nothing removed.

`tools/patch_continuity_works.py` now applies CW-1 and CW-3 together, from the **pristine** original
in `quarantine/` (md5 `32b6003bf04692f09708415442c85547`) rather than chaining a patch onto a patch.
The permuted ids are written back into the same quote slots, so no whitespace, comma or line break
moves: 307 entries, **0** unintended byte changes, and blanking every feature string leaves the
before and after texts byte-identical. A second run reproduces the jar with 0 differing entries.

Installed as `ContinuityWorks-Forge-1.20.1-0.3.0-rc.2+cw1patch+cw3patch.jar`
(md5 `063438d8b41444be295b0284d051aad4`). The superseded `+cw1patch` jar moved to `quarantine/`.
Numbered CW-3 because CW-2 is a withdrawn architecture ask and numbers are not reused.
**Backport pending** — B-39.

### Added — `tools/check_feature_order.py`

Simulates `FeatureSorter` over the vanilla client jar, all 85 mod jars and our datapack: 298
biomes, 789 ordering constraints over 516 placed features. Reports each cycle with the step, the
features, and how many biomes assert each edge, so the deviant side is obvious rather than argued.

Validated in both directions — `--self-test` fires on a synthetic pair of contradicting biomes, and
the real run went **5 cycles → 0**. This is the check `check_worldgen.py` structurally could not
make: every id it resolves is valid; it is their *sequence* that was impossible.

| Check | Result |
|---|---:|
| `check_feature_order.py` | **0 cycles** (was 5) |
| `check_incoming_mod.py` on the patched jar | 0 fail, 0 warn, 6 pass |
| `check_dependency_ranges.py` | 0 blocking, 0 quarantine conflicts |
| `check_worldgen.py` | 0 problems |
| `check_era.py --all` | 0 problems |

---

## 0.4.0-design — 2026-09-03

CW-1 root-caused and patched. Continuity Works is back in the load path, so Midgard now carries the
full anthology. Static only — still nothing has been run.

### Fixed — CW-1 was one bad string

**`minecraft:ore_diamond_medium` does not exist in Minecraft 1.20.1.** Verified against the pinned
client jar: of its 231 placed features the diamond ones are exactly `ore_diamond`,
`ore_diamond_large` and `ore_diamond_buried` — and all three were already in the same list, either
side of the invented fourth entry. 136 of Continuity Works' 146 biomes carried it.

A datapack biome naming a `placed_feature` nothing provides gets a `Holder.Reference` that is never
bound. Nothing complains at load. `FeatureSorter` throws the first time a chunk resolves that biome,
which is why the crash landed 625 chunks out and was seed-dependent rather than reproducible at
spawn.

Measured rather than assumed: **5,219** feature references across the 146 biomes, resolved against
vanilla, all 84 installed mods and CW itself. **Exactly one** failed. Nothing else was wrong.

**The project's earlier diagnosis was wrong** and is corrected in
`CONTINUITY_WORKS_DEFECTS.md` rather than deleted. It had speculated about code-side holder
construction through `AnthologyBiomeCatalog` and a captured `BuiltinRegistries` snapshot — a
plausible story that the class names supported and that the symptom convincingly imitates. The
biomes are ordinary datapack JSON; the mod's Java is not implicated at all.

**The fix is deletion, not substitution.** `ore_diamond` and `ore_diamond_large` are already
present, so swapping in a real feature would double diamond generation instead of restoring vanilla
behaviour.

Applied at the owner's instruction via `tools/patch_continuity_works.py` — a re-runnable tool rather
than a hand edit, so the change is exactly reproducible for the backport. Surgical text deletion,
no JSON reserialisation: **307 entries, 0 unintended byte changes**, 5,219 → 5,083 references, 0
unresolvable. Installed as `ContinuityWorks-Forge-1.20.1-0.3.0-rc.2+cw1patch.jar`; the defective
original is preserved in `quarantine/` (md5 `32b6003b…`).

**This is a stopgap.** The fix belongs in Continuity Works' source, and the local patch must be
dropped the moment an upstream build carries it.

### Changed — doctrine now distinguishes first-party from third-party jars

`INSTRUCTIONS.md` gained **§5.1**. Continuity Works is the owner's own mod, so the blanket
"third-party jars are read-only" rule in §6.5 did not actually cover it — patching it silently would
have left the repo contradicting itself. A first-party jar may now be patched as a stopgap under six
conditions: the owner asks, the original is preserved with its hash, the patch is a re-runnable tool
under `tools/`, the artifact is renamed `+<fix>patch`, the change is minimal and byte-verified, and
it is recorded as a stopgap to be dropped on the next upstream build.

### Added — the guard that would have caught it

`check_incoming_mod.py` now fails any incoming jar whose biomes reference a `placed_feature` that
nothing provides. Validated both directions: the patched jar passes 0 fail / 0 warn / 6 pass, the
original fails on exactly that clause.

Two further corrections to the same tool: it now counts biome **definitions** rather than
definitions plus tag files — the source of the wrong "176 biomes" figure, which is really 146
definitions and 30 tag files — and its `#mythicbotany:alfheim` warning was removed as obsolete,
since CW's biomes belong in Midgard and appending them to Alfheim's tag would now be the defect.

## 0.3.0-design — 2026-09-02

Every era verified end to end, three generator defect families repaired, the two worldgen faults
that made Alfheim unplayable fixed, and the world architecture simplified. All static; nothing here
has been seen running.

### Changed — Alfheim left the Overworld slot

**Alfheim is now `mythicbotany:alfheim`**, the dimension MythicBotany already ships and tests, and
the player spawns there. **`minecraft:overworld` is Midgard** and is left exactly as vanilla ships
it. `kubejs/data/minecraft/worldgen/world_preset/normal.json` is deleted.

The override was **duplicating the mod's own work**: `data/mythicbotany/dimension/alfheim.json`
already carries the identical generator block — same `libx:noise`, same `libx:layered` on
`#mythicbotany:alfheim`, same noise settings and surface override. It was also the project's
riskiest unproven assumption, and it sat in the slot every TerraBlender mod injects into, which was
the single cause of both the Continuity Works mismatch and Regions Unexplored generating nowhere.

Vacating the slot closed five items **without building anything**:

| Item | Disposition |
|---|---|
| B-12 prove the Overworld override | Retired — the assumption was dropped rather than proved |
| B-05 Regions Unexplored | Closed — generates again, in Midgard, where lush Earth biomes belong |
| B-14 Alfheim Unbroken | Dissolved — there is one Alfheim and the player lives in it |
| B-35 Midgard | Mostly built — the Overworld already generates; only CW's anthology is left |
| Continuity Works asks 2–4 | Withdrawn — CW was already pointed at the right dimension |

Everything built earlier the same day carried over untouched, because it was keyed to **biome tags**
rather than to the dimension slot. One file deleted, one added.

**The cost, recorded rather than glossed:** mods that hardcode `Level.OVERWORLD` in Java now see the
home world as "not the overworld", and no datapack reaches that — MineColonies is the one to watch.
A Nether portal lit in Alfheim probably will not link, since portal linking is hardcoded
Overworld↔Nether; the route out likely runs through Midgard. Both are level-9/10 questions.

### Added — spawn handling

`kubejs/server_scripts/02_spawn_dimension.js`. Vanilla has no spawn dimension and no
dimension-management mod is installed, so this is script: `spreadplayers` for a safe first-join
landing in Alfheim, then `spawnpoint` at that spot — which is what carries respawn, because
`/spawnpoint` writes the respawn *dimension*, so dying bedless returns the player to Alfheim rather
than to Midgard. Commands rather than the KubeJS teleport API, because `execute in <dim> run` has
been stable across KubeJS builds and the teleport signatures have not.

`check_worldgen.py` gained **W6**: the home dimension must exist and its `biome_source` must
actually read the layer the tool validates — otherwise a clean run proves nothing — and it fails if
the deleted world-preset override ever reappears.

### Fixed — Continuity Works report corrected

`CONTINUITY_WORKS_DEFECTS.md` said "176 biomes". Verified against the jar: **146 biome definitions**
plus 30 tag files. The 136-biome ore-reference figure is unchanged but is 136 **of 146**, and all
136 reference `minecraft:ore_diamond_medium` — the exact key in the crash. CW-2 is withdrawn; CW-1
is now the only outstanding item and the sole reason the jar is quarantined.

### Fixed — the pack could not be finished

- **Alfheim generated no copper, iron or coal.** MythicBotany places only gold, elementium and
  dragonstone across all 11 biomes. Era I's own quests ask for a Mana Spreader (copper ingot), an
  iron ingot and a Manasteel ingot (infused iron), so the campaign soft-locked in its first
  chapter. No script check could see it: every id existed and every recipe resolved — the
  material simply was not in the world.

  Scarce ores now generate through a Forge `add_features` biome modifier on
  `#mythicbotany:alfheim`, which reaches MythicBotany's five biomes as well as our six without
  overriding a jar-owned biome. Copper ×4, iron ×3, coal ×6 everywhere at roughly a quarter of
  vanilla counts in smaller veins; richer iron and redstone on `#alfheim:highland_veins`; lapis
  and diamond on `#alfheim:arcane_strata`. Scarce enough that gate trade still pays. Settles B-25.

  *Evidence:* `python tools/check_worldgen.py` → 0 problems, copper/iron/coal each in 11 biomes.

- **A free Elementium duplication loop.** `tools/gen_item_uses.py` emitted its `multiplier` family
  as an `occultism:crushing` recipe naming only the ore — the custom item it was filed under never
  appeared. Two rows were ingot → *the same ingot* ×2 with no other input:
  `botania:manasteel_ingot` → 2 manasteel and `botania:elementium_ingot` → 2 elementium,
  repeatable forever. Infinite Elementium destroys the trade premise the pack is built on.

  17 such loops, plus 53 "uses" that used nothing, plus 5 duplicated recipes covering all 53 ids —
  all three families were one generator defect and were fixed there, not in the output. The
  intermediate is now the catalyst consumed with the ore, and `mythicbotany:raw_elementium` (the
  native elven metal) replaced the ingot rows.

- **Ashen Grove had no trees**, while Velrous's opening line is "The trees you see standing are
  dead." Spawn could strand a player with no wood and a first quest asking for a crafting table.
  Loose dreamwood at low density is now the standing dead the script already describes.

- **Two validator defects** that produced false results: the era script glob `*era{n}*.js` matched
  `210_era10_tier_ladder.js` for **era 1**, so Era I was validated against Era X's ladder; and
  `.id(...)` was searched in a trailing window, letting an `event.remove({...})` adopt the id of
  the next recipe.

### Added

- **Abandoned elven villages, without authoring an NBT.** MythicBotany's elven houses generated
  pristine and alone. `alfheim:elven_ruin` — `block_rot` at integrity 0.88 plus a rule processor —
  shatters elf glass, weathers livingrock to mossy then cracked, drops dreamwood floors and fills
  interior air with cobwebs. And because `house` and `tower` each carry a jigsaw named
  `mythicbotany:entrance` whose connector targets the `gardens` pool, putting the buildings into
  that pool makes buildings chain into clusters. Both by datapack override, so no third-party art
  is modified. Delivers B-19.

- **`tools/check_era.py`, rewritten** from an existence check into a playability check. The old
  version verified ids were registered somewhere and passed on a pack whose custom items no recipe
  could make. Thirteen invariants now cover obtainability, cross-era ordering, duplicate and
  self-multiplying recipes, quest structure, and — against the jars — that every `event.remove`
  target, tag and recipe serialiser actually exists. A remove that matches nothing is the failure
  doctrine warns about most: it passes every check and leaves the closed route open.

- **`tools/check_worldgen.py`** — a static level-9 pre-check. It resolves preset → biome layer →
  biomes → Forge biome modifiers across datapack, mod jars and the vanilla client jar, and would
  have caught the unbound `placed_feature` that crashed world generation 625 chunks out (B-33).

  Both new checkers are validated in **both** directions: they pass on the pack and fire on
  synthetic bad input.

- **A boot regression nobody had noticed.** `journeymap-forge-1.20.1-6.0.4.jar` had been restored
  to `mods/` after the run that recorded B-27, leaving it in both `mods/` and `quarantine/`.
  MineColonies declares it optional at `[5.9.8,)`; JourneyMap declares `version = "1.20.1-6.0.4"`,
  which Maven tokenises from **1**, so Forge halted in `ModSorter` before any mod loaded. The pack
  had stopped booting between two recorded sessions and nothing said so.

  Copies verified byte-identical, the `mods/` copy removed, quarantine copy preserved. Load path
  84 jars, 130 mod IDs, **0 blocking issues**. `check_dependency_ranges.py` now also fails on any
  jar present in both `mods/` and `quarantine/`, so an undone quarantine decision cannot pass
  quietly again.

### Known state

Level 3 passes; level 9 is unblocked. All ten eras pass their consistency check — 376 recipes,
215 quests, 80 custom items, 0 problems. Generators reproduce their output byte-identically.

**None of it has been played.** Level 8 last passed on a 95-jar load path that has since changed
twice, so it is stale rather than current. Outstanding: a JourneyMap **5.9.x** build to restore
the minimap (spec in B-27), then a fresh world for level 9.

---

## 0.2.0-design — 2026-09-02

The pack's premise was settled, the campaign structured, and the two jars that prevented it from
booting were removed. No quest or recipe implementation yet.

### Fixed

- **Removed two boot blockers.** `mh_automated-1.2.2.jar` declared a mandatory dependency on
  `meds_and_herbs`, which was not installed. `create_sophback_compat-1.0.jar` was a NeoForge 1.21
  artifact carrying only `META-INF/neoforge.mods.toml`, unreadable by Forge 1.20.1, and additionally
  required an uninstalled `sophisticatedbackpacks`. Both moved to `quarantine/` rather than deleted.

  *Evidence:* dependency re-scan after removal — 96 jars, 144 mod IDs resolved including
  JarJar-nested, **0 missing mandatory dependencies**. Validation level 3 moved from failed to passed.

### Added

- `INSTRUCTIONS.md` — project doctrine: premise, the three systems, authority hierarchy, source
  boundaries, validation ladder, acceptance states.
- `BACKLOG.md` — eleven sequenced items with explicit dependencies and acceptance conditions.
- `EXECUTION_STATE.md` — live position, verified steps, ladder status, next exact action.
- `alfheim_reclaimed_design/GATE_REVERSAL.md` — the recipe inversion specified against extracted
  recipe data, including the soft-lock it creates and the Dreamwood early game that prevents it.
- `alfheim_reclaimed_design/CAMPAIGN_ERAS.md` — ten eras budgeted at 215 quests, each capped by one
  of MythicBotany's Nine Realm runes.
- `alfheim_reclaimed_design/TWIN_SPINES.md` — the four hard dependencies binding Botania and Ars
  Nouveau into one tradition.

### Changed

- `alfheim_reclaimed_design/README.md` — rewritten for the far-side-of-the-gate premise and to index
  the design records.
- `BUILD_METADATA.json` — `manifest_mod_entries` corrected from 26 to 96; version to `0.2.0-design`;
  pinned-core and quarantine counts added.
- `alfheim_reclaimed_design/PROGRESSION_BLUEPRINT.md` — marked superseded by `CAMPAIGN_ERAS.md`,
  content preserved for provenance.

### Verified, unchanged

- All 26 mods in `PINNED_MOD_MATRIX.md` are present at exactly their pinned file IDs. Zero drift.
- MythicBotany ships a real `mythicbotany:alfheim` dimension with five biomes, plus
  `elementium_ore` and `raw_elementium` — the gate reversal runs with the mod stack's grain, not
  against it.
- Botania ships every part the elven early game needs: `dreamwood_twig`, `elven_spreader`,
  `natura_pylon`, `dreamwood_log`. No new items required.

### Direction expanded — second session, same day

Three doctrine-level changes on user direction, and one design record added.

- **The magic spines govern the whole pack.** Every progression-relevant recipe in every support mod
  is re-gated to route through a spine (`INSTRUCTIONS.md` §2.3). Pack-wide recipe work — backlog
  B-16 — is now the largest single body of implementation work in the project.
- **Mine and Slash upgraded** from reward economy to the primary world-interaction layer.
- **Alfheim is the Overworld**, not a dimension to travel to. New record
  `alfheim_reclaimed_design/WORLD_STRUCTURE.md`; backlog B-12 through B-15.

  *Evidence:* MythicBotany's Alfheim uses a `libx:layered` biome source reading the biome **tag**
  `#mythicbotany:alfheim` (5 values). Biome injection is therefore a datapack tag append, not code —
  the hook the Continuity Works custom mod should use. The Overworld preset override that would make
  this the actual Overworld is reasoned but **unverified**; it needs level 9 evidence.

  *Cost identified:* a `libx:layered` Overworld ignores TerraBlender, so all 170 Regions Unexplored
  biomes stop generating, and every biome-tagged structure needs re-tagging. Both surfaced now rather
  than at world generation.

### Spawn zone specified — third session, same day

- **Ars Nouveau confirmed** as the Spine of Song. B-04 closed; ~100 quests unblocked.
- New record `alfheim_reclaimed_design/SPAWN_ZONE.md` — the Greatbole arrival tree and the Hollow
  Court, a 1000-block-radius drained elven city as the start area. Backlog B-17 through B-22.

  *Constraint established:* a 1000-block radius cannot be one structure. Vanilla caps structure-block
  saves at 48³, jigsaw `size` at 20, and `max_distance_from_center` at **128** — eight times too small.
  The zone is therefore five layers, only two hand-built; the rest is biome features.

  *Reuse found:* MythicBotany already ships a working elven-village jigsaw — `elven_house` structure,
  structure set, three template pools and five NBT pieces, with `beard_thin` terrain adaptation — plus
  an `abandoned_apothecaries` feature that already scatters empty apothecaries and spilled petals. The
  Hollow Court extends this rather than starting over.

  *Method decided:* buildings are authored **intact once** and decayed by a `processor_list`, not
  rebuilt as ruins. Halves the build, and makes Era X's restoration a processor swap rather than a
  second city.

  *Flagged:* "Lothlórien" is Tolkien's and cannot ship in content. Working names are descriptive and
  IP-clean.

### Continuity Works received — fourth session, same day

`ContinuityWorks-Forge-1.20.1-0.3.0-rc.2.jar` installed. Acceptance scan **0 fail, 1 warn, 5 pass**;
full pack re-scan **97 jars, 146 mod IDs, 0 missing dependencies**. Two mods —
`continuityworks_biomes` (176 biomes, 11 convention tag files) and `continuityworks_spawn_protection`
(500-block structure exclusion). Mod IDs unique; no collision with the installed `continuity`
connected-textures mod.

**The jar corrected the worldgen design before a world was ever generated.**

`continuityworks_biomes` requires TerraBlender and places biomes through it. The plan recorded hours
earlier in `WORLD_STRUCTURE.md` §3 — overriding the Overworld preset with MythicBotany's
`libx:noise`/`libx:layered` generator — bypasses TerraBlender entirely. Had it been implemented, all
**176** Continuity Works biomes and all **170** Regions Unexplored biomes would have silently failed
to generate, with no error in any log.

- `WORLD_STRUCTURE.md` rewritten: Path A rejected, **Path B** adopted — vanilla multi-noise Overworld
  with Alfheim injected as a TerraBlender region. Accepted loss: Alfheim's own terrain shape and
  surface rules do not come along.
- B-05 (Regions Unexplored: rebuild or remove) **dissolved** — the question only existed under Path A.
- B-13 (structure re-tagging) **shrank** from a programme to a handful of tag files.
- B-15 **closed** at static acceptance.
- B-23 added: 168 of the 176 biomes are genre anthologies — sci-fi, neon virtual, atomic
  post-collapse, industrial. Decide which belong in an elven botanical pack.
- B-24 added: spawn-protection tag configuration. `SPAWN_ZONE.md` §7.1 — protect the Greatbole with
  the 500-block exclusion, exempt the Hollow Court pieces so the city can crowd.

### Two-world architecture — fifth session, same day

**Supersedes the Path A / Path B framing recorded above.** Both were arguing about which biomes get
the single Overworld. The answer is that there are two worlds.

- **Alfheim takes the `minecraft:overworld` slot** — elven, magical, and deliberately metal-poor.
  Also the technically correct choice: a great many mods gate behaviour on `Level.OVERWORLD`, so the
  player's home world should be the one where the mod stack behaves normally.
- **Midgard becomes a new dimension** carrying Continuity Works' 176 anthology biomes — the industrial
  world that died, reached through the gate from Era IV.
- B-23 (anthology fit) **dissolved** — sci-fi and neon biomes are correct in a dead industrial world;
  they were only wrong when they were going to generate around the Hollow Court.
- B-05 (Regions Unexplored) **reopened** — with the Overworld off vanilla multi-noise, TerraBlender
  injects into nothing and RU now generates nowhere at all.
- B-12 **reinstated**: the Overworld preset override is back, and bypassing TerraBlender there is now
  the intent rather than the hazard. Still unverified; now the riskiest assumption in the project.

**Correction — the injection point was documented wrongly, twice.** Earlier revisions named
`data/mythicbotany/tags/worldgen/biome/alfheim.json`. The real extension point is
`data/mythicbotany/tags/libx/biome_layer/alfheim.json`: a tag of **LibX `biome_layer`** entries, each
a full climate map over continentalness, erosion, weirdness, humidity, temperature, depth and offset.
Enriching Alfheim means defining new layers and appending their IDs — still a datapack append, still
no TerraBlender and no Java, but a different registry than recorded.

**New risk — Alfheim is not campaign-viable as shipped (B-25).** Its terrain is `botania:livingrock`
rather than stone, `ore_veins_enabled` is false, and there is no vanilla cave noise. Vanilla and
modded ores place against `#minecraft:stone_ore_replaceables`, which livingrock is not in, so almost
no ore generates. Curated scarcity is the recommendation — it makes the trade premise real — but it
needs a guard rail that Era I is completable without iron, and caves are needed regardless.

Four asks recorded for Continuity Works in `WORLD_STRUCTURE.md` §6.

### Added — tooling

- `tools/check_incoming_mod.py` — acceptance checker for incoming jars, written **before** delivery
  against the integration contract. Validated against a known-bad jar
  (`quarantine/create_sophback_compat-1.0.jar` → 3 fail) and a known-good one. It caught the
  TerraBlender dependency on first run. Development tooling; never packaged, never placed in `mods/`.

### First launch attempted — 2026-09-02 13:44

**It did not reach the game, and the modpack was not the cause.** Recording this precisely because
"it crashed" and "the launcher aborted" are different facts with different next actions.

- **No JVM started.** No `logs/latest.log`, no `crash-reports/`, no `config/`, no `options.txt` —
  nothing was written to the instance at all.
- **Cause: DNS.** CurseForge fetches the 1.20.1 version manifest before launching. `api.curseforge.com`
  failed to resolve three times (`getaddrinfo ENOTFOUND`) and the launch aborted with
  `Outcome: Failed`. Errors in that launcher log run from 13:15 onward and also hit
  `tracking.overwolf.com`. DNS has since recovered.
- **Validation level 8 remains `not run`, not `failed`.** No mod was loaded, so nothing was learned
  about the pack. The distinction matters: a failed boot would send us hunting mod conflicts that no
  evidence supports.

**Separate blocking risk found — no Java 17 (B-26).** `versions/1.20.1/1.20.1.json` requires
`java-runtime-gamma` majorVersion **17**. The machine has `java-runtime-delta` 21.0.12, `Jre_21`
21.0.4, and a system Java 26.0.1. Nothing at 17. CurseForge must download the correct runtime on the
next launch — which needs the same network that just failed, linking the two problems. If it falls
back to Java 21 instead, Forge 47.4.10 with 97 mods is unsupported and Sinytra Connector rewrites
bytecode at load time; a crash from that is very hard to attribute. Confirm the runtime before
diagnosing anything else.

### THE PACK BOOTS — 2026-09-02 15:58

Validation **level 8 passed**. The pack reaches the title screen and holds there: 95 mods, **403**
valid mod files including JarJar-nested, 13 GB heap, ~95 s load, **0 crash reports, 0 FATAL lines**,
77 config files written. The KubeJS baseline script logged, satisfying FIRST_BOOT_VALIDATION step 9.

Launched from a hand-assembled Forge command against the existing install, not through CurseForge.
That validates the **mod stack**; the CurseForge launch path still needs working DNS, its own Java
runtime (B-26) and repaired assets (B-28).

#### Five attempts, and what each one taught

| # | Heap | Outcome |
|---|---|---|
| 1 | — | CurseForge aborted before the JVM: DNS failure fetching the 1.20.1 manifest. |
| 2 | 8 GB | JourneyMap x MineColonies optional version-range violation (B-27). |
| 3 | 8 GB | Module `ResolutionException` — a fault in the test harness, not the pack. |
| 4 | 8 GB | `OutOfMemoryError` in `ModelBakery`. |
| 5 | 13 GB | **Title screen**, after quarantining BuildCraft RF (B-29). |

Attempt 4 vindicates the instance's 14 GB memory setting and the original F-05 audit finding: this
pack genuinely needs a large heap, and 8 GB cannot bake its models.

A note on evidence: an earlier revision of this entry claimed success at attempt 3. It was wrong.
`Sound engine started` fires *during* the loading overlay, not at the title screen. The real marker
is the second resource reload completing and the log going quiet with the process alive.

#### Two more blockers, both found by running rather than scanning

- **JourneyMap x MineColonies (B-27).** MineColonies declares `journeymap` **optional** at
  `[5.9.8,)`; JourneyMap's version string `1.20.1-6.0.4` tokenises from **1**, below the bound.
  Forge halts — an optional dependency may be *absent*, but if present it must satisfy the range.
- **BuildCraft RF (B-29).** `buildcraftrf-3.0.0.jar` is an addon for BuildCraft, which is not
  installed. `NoClassDefFoundError: buildcraft/lib/tile/TileBC_Neptune` on capability-attach for the
  first BlockEntity. It declares **no** mod dependency — the requirement exists only as a hard class
  reference, so no metadata scan can see it.

Both quarantined; neither is in the pinned core. Four jars are now in `quarantine/`.

#### Added — `tools/check_dependency_ranges.py`

The earlier scan checked only *mandatory* dependencies, which is how B-27 reached first boot. The new
tool checks mandatory **and** optional dependencies and evaluates ranges with Maven
`ComparableVersion` tokenisation rather than naive field comparison — the distinction that decides
whether `1.20.1-85-FORGE` sorts above `1.20.1-83`.

A first cut using field comparison reported 62 issues against a pack that demonstrably loads. Three
defects were fixed before it was trustworthy: `${file.jarVersion}` now resolves from the jar
manifest, duplicate mod IDs resolve to the highest version (JarJar semantics) rather than the first
seen, and semver `+build` metadata is stripped. It reports **0** against the current mods folder and
correctly flags JourneyMap when restored. Twelve comparison cases are asserted.

#### Runtime errors — 1270 lines, none load-blocking

- **864** Conquest Reforged model failures, `JsonSyntaxException: Missing axis` — malformed model
  JSON inside the mod. Affected blocks render untextured.
- **384** `PalettedPermutations: unable to apply palette` — same family.
- **4** missing vanilla assets (B-28) — a direct consequence of the earlier DNS outage.
- **~18** `Invalid path in pack` — mod-authoring sloppiness: `miners_delight` ships both
  `Lunchbox.png` and a misspelled `Launchbox.png`; `mmorpg` ships `question - Copy.png`.

#### The datapack layer, validated by a 91-minute session

The successful run stayed up **5,482 s** and exited normally (`Stopping!`, rc 0, no crash report).
Before shutdown it loaded the full datapack layer: **30,960 recipes** parsed in 179 ms, **9,320
advancements**, 161 MineColonies crafter recipes. KubeJS server scripts loaded 1/1 with **0 errors,
0 warnings**, and the recipe pass reported added 0 / removed 0 / modified 0 — correctly inert, as the
scaffolds are designed to be. Both halves of FIRST_BOOT_VALIDATION step 9 are now satisfied.

**One real defect surfaced (B-30):** `mythicbotany:feysythia` is uncraftable. MythicBotany ships its
Petal Apothecary recipe as a `forge:conditional` gated on Feywild being loaded; Feywild *is* loaded,
so the recipe activates and then fails, because it calls for `feywild:lesser_fey_gem` and Feywild
5.5.5 ships only `feywild:fey_gem`. Upstream version drift between two mods that are both current.
Fixable in a few lines of KubeJS — and a good shakedown of that path before the gate reversal.

#### Java 21

It loads, but LWJGL logs `Unsupported JNI version detected, this may result in a crash`. Java 17
remains the supported runtime; B-26 is downgraded from blocker to correctness item.
### Known state

Boots to the title screen. Admission state: **static validated + runtime validated (level 8)**.
Levels 9–12 remain unrun — no world generated, no quest authored. Next: B-02 (capture the FTB Quests
schema) and B-12 (prove the Overworld override), which are independent of each other.

Continuity Works 0.3.0-rc.2 is installed and loads. It needs re-aiming at Midgard — four asks in
`WORLD_STRUCTURE.md` §6.

---

## 0.1.0-prototype — 2026-09-01

Initial instance assembly. 26 pinned core mods, design documents, inert KubeJS scaffolds. A further
70 mods were added on 1–2 September without documentation; reconciling them is backlog item B-03.
