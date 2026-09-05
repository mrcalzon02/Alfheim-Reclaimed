# Continuity Works — defect report

**Version tested:** `ContinuityWorks-Forge-1.20.1-0.3.0-rc.2.jar` (459 KB, 78 class files)
**Found:** 2026-09-02, Alfheim Reclaimed instance, Forge 47.4.10 / MC 1.20.1
**Status of the jar in this pack:** CW-1, CW-3 and CW-4 **patched locally and installed** as
`mods/ContinuityWorks-Forge-1.20.1-0.3.0-rc.2+cw1patch+cw3patch+cw4patch.jar`. The defective
original is preserved unmodified in `quarantine/`, md5 `32b6003bf04692f09708415442c85547`.
Static only — no world has been generated with it.
**Re-verified against the jar 2026-09-02** after the two-world architecture was revised.
**CW-3 found 2026-09-03**, on the second world-generation attempt, after CW-1 was cleared.
**CW-4 found 2026-09-03**, on the third and fourth attempts, after CW-3 was cleared.

> **All four defects crash world generation and none is visible before it.** They were found one
> at a time because each one hides the next: the sorter stops at the first fault it reaches. Do
> not read "CW-1 fixed" as "world generation works" — that inference has now been wrong twice.

> **Count correction.** Earlier revisions of this report and of `EXECUTION_STATE.md` said "176
> biomes". That figure counted **tag files alongside biome definitions**. Verified directly:
>
> | | |
> |---|---:|
> | Biome definitions (`data/continuityworks_biomes/worldgen/biome/`) | **146** |
> | Biome tag files (19 CW-namespace + 5 `forge` + 6 `minecraft`) | **30** |
> | Total JSON paths under any `/worldgen/biome/` | 176 |
>
> The 136 figure below is unchanged and is **136 of 146**, not of 176.

This is a report *to* the Continuity Works project — it remains a separate repository, and the fix
belongs in its source.

**Superseded 2026-09-03:** the line that stood here said the jar is consumed and never patched
locally. Continuity Works is the pack owner's **own** mod, not third-party, and they instructed that
the jar be patched in place pending a source fix. `INSTRUCTIONS.md` §5 and §6.5 were amended to draw
that first-party / third-party line explicitly. The patch is recorded under CW-1 below.

---

## CW-1 — Unbound placed_feature crashes chunk generation — **ROOT CAUSE FOUND, PATCHED LOCALLY**

### Symptom

Any new world crashes during chunk generation, typically a few hundred chunks in.

```
Description: Exception generating new chunk
java.lang.IllegalStateException: Trying to access unbound value
  'ResourceKey[minecraft:worldgen/placed_feature / minecraft:ore_diamond_medium]'
  from registry net.minecraft.core.MappedRegistry$1
    at net.minecraft.core.Holder$Reference.m_203334_(Holder.java:147)
    at net.minecraft.world.level.biome.FeatureSorter.m_220603_(FeatureSorter.java:55)
    at net.minecraft.world.level.chunk.ChunkGenerator.m_223094_(ChunkGenerator.java:102)
```

Context from the crash report:

| | |
|---|---|
| Dimension | `minecraft:overworld` |
| Generator | `NoiseBasedChunkGenerator` (stock — no override applied) |
| Chunk | −26, −6 |
| Chunks generated before crash | 625 |
| Mixins on `ChunkGenerator` | `continuityworks_spawn_protection.mixins.json:ChunkGeneratorMixin` (from `continuityworks_biomes`), plus bclib and YUNG's |

Full report preserved at `scratchpad/crash-worldgen-continuityworks.txt`.

### Evidence pointing at Continuity Works

**136 of its 146 biome definitions reference vanilla ore placed-features**, and all 136 reference `minecraft:ore_diamond_medium` specifically — the exact key in the crash. Sampling
`data/continuityworks_biomes/worldgen/biome/academy_grove.json`, the features array has the correct
11 `GenerationStep.Decoration` steps, and step 6 (`UNDERGROUND_ORES`) lists vanilla keys as plain
strings — `minecraft:ore_dirt`, `minecraft:ore_gravel`, `minecraft:ore_granite_upper`, … and
`minecraft:ore_diamond_medium`.

### ROOT CAUSE — found 2026-09-03. The earlier diagnosis on this page was wrong.

> **`minecraft:ore_diamond_medium` does not exist in Minecraft 1.20.1.**

That is the entire bug. Verified against the pinned client jar: of its 231 placed features, the
diamond ones are exactly **`ore_diamond`, `ore_diamond_large`, `ore_diamond_buried`**. There is no
`ore_diamond_medium`, and there is no `ore_diamond_small` either.

The UNDERGROUND_ORES step in the affected biomes is a verbatim copy of the vanilla overworld ore
list, and **all three real diamond features are already present in it**, sitting immediately either
side of the invented one:

```
"minecraft:ore_diamond", "minecraft:ore_diamond_medium",
"minecraft:ore_diamond_large", "minecraft:ore_diamond_buried",
```

So `ore_diamond_medium` is a spurious fourth entry — most likely a hand-written or generated
addition that was never checked against the real registry.

**Why it presents as "unbound" rather than "unknown".** When a datapack biome names a
`placed_feature` that no pack provides, the registry still creates a `Holder.Reference` for the key
and simply never binds it. Nothing complains at load. `FeatureSorter` dereferences it the first time
a chunk resolves a biome carrying it — which is why the crash appeared 625 chunks out, and why it is
seed-dependent rather than reliably reproducible at spawn.

**The previous entry on this page speculated about code-side holder construction through
`AnthologyBiomeCatalog` / `BiomeCaveFeatures` and a captured `BuiltinRegistries` snapshot. That was
wrong**, and it is recorded here rather than deleted because it is the kind of wrong that costs a
day: the symptom *looks* like a registry-lifecycle bug, and the class names made a plausible story.
The biomes are ordinary datapack JSON. The mod's Java is not implicated at all.

**Scope, measured rather than assumed.** Across the 146 biome definitions there are **5,219**
`placed_feature` references. Checked against vanilla, all 84 installed mods, and Continuity Works
itself: **exactly one id fails to resolve**, in 136 biomes. Nothing else is wrong.

### THE FIX — delete the entry. Do not substitute.

`ore_diamond` and `ore_diamond_large` are already in the list, so replacing `ore_diamond_medium`
with a real feature would **double diamond generation** rather than restore vanilla behaviour.
Removing it leaves exactly the vanilla three.

**For the backport**, in the source that emits these biome JSONs: find where the overworld ore list
is defined and drop `ore_diamond_medium` from it. It is one entry in one shared list — the 136
biomes almost certainly derive from a single template, since 128 are pretty-printed and 8 minified,
which suggests two emission paths over one list.

**Recommended alongside it:** validate emitted feature ids against the real registry at build time.
This bug is invisible to every static check that does not resolve ids, and invisible at runtime
until a specific biome generates.

### Applied locally — 2026-09-03, at the owner's instruction

The pack owner owns this mod and asked for the jar to be patched in place pending a proper source
fix. Done, reproducibly:

    python tools/patch_continuity_works.py <in.jar> <out.jar>

| | |
|---|---|
| Patched artifact | `mods/ContinuityWorks-Forge-1.20.1-0.3.0-rc.2+cw1patch.jar` |
| Defective original | preserved unmodified in `quarantine/` (md5 `32b6003bf04692f09708415442c85547`) |
| Method | surgical text deletion of the array entry — JSON is not reserialised |
| Result | 307 entries, **0** unintended byte changes, 5,219 → 5,083 feature refs, 0 unresolvable |
| Acceptance | `check_incoming_mod.py` → **0 fail, 0 warn, 6 pass** (original now → 1 fail) |

The `+cw1patch` filename suffix marks it as a locally-patched artifact so it cannot be mistaken for
an official rc.2 build. The in-jar version string is untouched at `0.3.0-rc.2`.

**This is a stopgap. The fix belongs in the Continuity Works source**, and the local patch should be
dropped the moment a build carrying it arrives — the two must not silently diverge.

**Still unverified at runtime.** The patch is proven correct on disk; no world has been generated
with it. Level 9 remains the acceptance condition below.

### How to verify a fix

1. Fresh world, default settings.
2. Fly or `/tp` outward at least 2,000 blocks in one axis to force several hundred chunk generations.
3. Pass condition: no `IllegalStateException: Trying to access unbound value` in `logs/latest.log`,
   and no `crash-*-server.txt` written.

The failure appears a few hundred chunks in, not at spawn — testing only the spawn chunks will produce
a false pass.

---

## CW-3 — Biome feature lists contradict vanilla's order — **PATCHED LOCALLY 2026-09-03**

> Numbered CW-3, not CW-2: that number belongs to the withdrawn architecture ask below and is
> not reused.

### Symptom

A new world crashes on creation — earlier than CW-1 did, and not seed-dependent.

```
Description: Exception generating new chunk
java.lang.IllegalStateException: Feature order cycle found, involved sources:
  [Reference{...continuityworks_biomes:terraced_vineyard},
   Reference{...ars_nouveau:archwood_forest}]
    at net.minecraft.world.level.biome.FeatureSorter.m_220603_(FeatureSorter.java:100)
    at net.minecraft.world.level.chunk.ChunkGenerator.m_223094_(ChunkGenerator.java:102)
```

`minecraft:overworld`, stock `NoiseBasedChunkGenerator`, chunk −1/−1, 625 chunks in.
Full report: `crash-reports/crash-2026-09-03_13.18.07-server.txt`.

### Root cause

**Minecraft does not generate a biome's features in the order that biome lists them.**
`FeatureSorter.buildFeaturesPerStep` flattens every loaded biome's list and topologically sorts
the "A immediately before B" constraints each one asserts, producing a single global order per
generation step. Two biomes that name the same pair of features in opposite orders make that
order impossible.

Continuity Works authors its vegetal lists thematically, without reference to vanilla's fixed
order. In 67 of its 146 biomes the result contradicts the rest of the pack — and, in the
sugar-cane case, contradicts **itself**: 41 CW biomes say pumpkin first, 22 say sugar cane first.

Four independent cycles exist against a stock 1.20.1 pack:

| Cycle | CW says | Everyone else says |
|---|---|---|
| `patch_sugar_cane` ↔ `patch_pumpkin` | pumpkin first (41 biomes) | cane first — vanilla ×41, Regions Unexplored ×52, CW's own ×22, Ars Nouveau ×1 |
| badlands trio | `cactus_decorated` → `sugar_cane_badlands` (`rocky_badlands`) | `sugar_cane_badlands` → `pumpkin` → `cactus_decorated` (vanilla ×3) |
| `flower_meadow` ↔ `patch_grass_plain` | flowers first (`flowering_meadow`) | grass first (`minecraft:meadow`) |
| savanna trio | `trees_savanna` → `patch_grass_savanna` → `patch_tall_grass` (25 biomes) | `patch_tall_grass` → `trees_savanna` (vanilla ×2) |

Vanilla's order is not a convention that can be argued with: `BiomeDefaultFeatures` fixes it, and
64 vanilla biomes in the client jar assert it. Any mod that disagrees makes world generation
impossible for the whole pack, not just for its own biomes.

**This is why CW-1's fix did not produce a working world.** The two defects are unrelated and
sequential — clearing the unbound holder simply let `FeatureSorter` get far enough to find the
cycle.

### The fix

Sort each affected step into the order the rest of the pack already agrees on. The reference is
derived at patch time by topologically sorting every biome source **except** this jar — the
vanilla client jar, the other 84 mods and this pack's datapack. That reference is acyclic on its
own (152 biomes, 0 cycles), so adopting it cannot introduce a new contradiction.

Nothing is added or removed. The same features generate in the same biomes; only the sequence
within a step changes, and the game was going to impose its own global sequence regardless.

### Applied locally — 2026-09-03, at the owner's instruction

`INSTRUCTIONS.md` §5.1, all six conditions:

| | |
|---|---|
| Tool | `tools/patch_continuity_works.py` — re-runnable, now carries CW-1 and CW-3 |
| Input | the **pristine original** in `quarantine/`, md5 `32b6003bf04692f09708415442c85547` |
| Output | `mods/ContinuityWorks-Forge-1.20.1-0.3.0-rc.2+cw1patch+cw3patch.jar`, md5 `063438d8b41444be295b0284d051aad4` |
| Scope | 136 biomes for CW-1, **67** biomes / 67 step lists for CW-3 |
| Method | the permuted ids are written back into the **same quote slots**, so no whitespace, indent, comma or line break moves |
| Verify | 307 entries, **0** unintended byte changes; blanking every feature string leaves the two texts byte-identical; a second run from the original reproduces the jar with 0 differing entries |
| Acceptance | `check_feature_order.py` → **0 cycles** (was 5); `check_incoming_mod.py` → 0 fail / 0 warn / 6 pass |

The superseded `+cw1patch` jar was moved to `quarantine/`; it is not a defective original and can
be deleted whenever convenient.

**Backport pending.** The fix belongs in Continuity Works' source. Drop the local patch the moment
an upstream build carries it — a local patch and its source must never silently diverge.

### How to verify a fix upstream

`python tools/check_feature_order.py` — it simulates `FeatureSorter` over the vanilla client jar,
every mod jar and this pack's datapack, and reports each cycle with the biomes asserting each edge.
It self-tests with `--self-test`. A clean run means the ladder's level 9 will not fail *this way*;
it is not a substitute for generating a world.

---

## CW-4 — Two biome modifiers add one feature under names that sort inconsistently — **PATCHED LOCALLY 2026-09-03**

### Symptom

A new world crashes on creation, again, with CW-3 already fixed — and this time between two
Continuity Works biomes.

```
Description: Exception generating new chunk
java.lang.IllegalStateException: Feature order cycle found, involved sources:
  [continuityworks_biomes:ash_wastes, continuityworks_biomes:quarry_megaplex]
    at FeatureSorter.m_220603_(FeatureSorter.java:100) -> ChunkGenerator.m_223094_
```

Reports: `crash-reports/crash-2026-09-03_13.55.59-server.txt` and `…_13.57.22-server.txt`.

**Those two biomes' `features` arrays are byte-identical.** The contradiction is not in the files.

### Root cause

A biome's JSON is not its final feature list. Forge applies `forge:add_features` biome modifiers
at runtime, and each one **appends** to the end of a step. Three Continuity Works modifiers are
involved:

| Modifier | Adds | To |
|---|---|---|
| `anthology_land_topology` | `continuityworks_biomes:land/topology` | `#continuityworks_biomes:anthology` — 128 biomes |
| `biome_cave_networks` | `continuityworks_biomes:caves/biome_network` | `#continuityworks_biomes:all_primary_biomes` — all of them |
| `foundation_land_topology` | `continuityworks_biomes:land/topology` | `#continuityworks_biomes:templates` — 8 biomes |

**One feature, two insertion points, and a third modifier sorting between them.** Forge loads
biome modifiers through `RegistryDataLoader`, whose `ResourceManager` listing is a `TreeMap` over
`ResourceLocation` — and `ResourceLocation.compareTo` compares **path first, namespace second**.
So the application order is by file path across every mod in the pack, and
`anthology_… < biome_cave_networks < foundation_…`. Therefore:

```
quarry_megaplex (#anthology)  ->  land/topology, caves/biome_network, caves/literal_hex_lattice
ash_wastes      (#templates)  ->  caves/biome_network, land/topology, caves/literal_hex_lattice
```

A direct two-cycle, asserted by 128 biomes one way and 8 the other.

**This is a structural bug, not a typo.** Any third modifier landing alphabetically between the
two `land/topology` modifiers reintroduces it. The underlying rule: *one feature should have one
insertion point*, or every modifier that inserts it must be adjacent in the global sort.

### The fix

Rename both `land/topology` modifiers to a shared prefix so they are adjacent in the global sort:

```
anthology_land_topology.json   ->  land_topology_anthology.json
foundation_land_topology.json  ->  land_topology_templates.json
```

Every biome then receives `caves/biome_network`, then `land/topology`, then
`caves/literal_hex_lattice`. Verified: no other modifier in the pack sorts between the two new
names, and nothing in the jar — JSON, class files or metadata — references either old name.

Upstream the better fix is to give `land/topology` a single modifier over a union tag, since a
list of tags is not a valid `HolderSet`. The rename is the minimal change that removes the crash
without inventing a tag in someone else's namespace.

### Applied locally — 2026-09-03

| | |
|---|---|
| Tool | `tools/patch_continuity_works.py`, now carrying CW-1, CW-3 and CW-4 |
| Input | the **pristine original**, md5 `32b6003bf04692f09708415442c85547` |
| Output | `…+cw1patch+cw3patch+cw4patch.jar`, md5 `b2c6e3bf9ab2045410007ac15ba83720` |
| Method | zip entry renamed; **no byte of content changed** |
| Verify | 307 entries, 2 renamed with byte-identical contents, 0 unintended byte changes; a second run reproduces the jar with 0 differing entries |
| Acceptance | `check_feature_order.py` → 1 cycle before, **0** after; `check_incoming_mod.py` → 0 fail / 0 warn / 6 pass |

**Backport pending — B-39**, together with CW-1 and CW-3.

### The checker had to be fixed first

`tools/check_feature_order.py` reported **0 cycles** on the jar that then crashed. It read biome
JSON and nothing else, so the entire biome-modifier layer was invisible to it. It now applies
`forge:add_features`, `forge:remove_features` and `farmersdelight:add_features_by_filter` in the
game's own path-sorted order before running the sort — 57 feature-affecting modifiers, 2,667
biome-steps changed — and it reproduces this crash exactly from the unpatched jar.

That reproduction is the validation that matters: a synthetic self-test only proves the graph
code works, whereas predicting the crash the game actually threw proves the *model* is right.

---

## ~~CW-2 — Aimed at the wrong dimension~~ — **WITHDRAWN 2026-09-02. Do not action.**

This ask no longer exists. It was never a defect in the jar, and the architecture that made it a
mismatch has been replaced.

**What changed.** Alfheim no longer occupies the `minecraft:overworld` slot. The player now spawns
in MythicBotany's own `mythicbotany:alfheim` dimension, and **`minecraft:overworld` *is* Midgard** —
the dead industrial world. See `WORLD_STRUCTURE.md` and `INSTRUCTIONS.md` §1.

**Consequence for Continuity Works: it was already pointed at the right dimension.**
`continuityworks_biomes` requires TerraBlender and injects into the Overworld, which is exactly
where the anthology now belongs. Three of the four asks are void and one was solved in this pack:

| Original ask | Disposition |
|---|---|
| 1. Move the anthology into a `continuityworks:midgard` dimension | **Void.** The Overworld is Midgard. TerraBlender injection is correct as shipped. |
| 2. Add an Alfheim biome layer | **Void.** Alfheim's biome layer is this pack's own work, not CW's — six biomes in `kubejs/data/mythicbotany/libx/biome_layer/alfheim.json`. |
| 3. Alfheim terrain viability | **Solved here.** Scarce ores via a Forge biome modifier on `#mythicbotany:alfheim`; caves already existed via `mythicbotany:cave`/`canyon`. Nothing needed from CW. |
| 4. Keep `continuityworks_spawn_protection` | **Still wanted** — `SPAWN_ZONE.md` §7.1. Unchanged. |

**CW-1 is therefore the only outstanding item, and it is the sole reason the jar is quarantined.**

### The jar is back in the load path

CW-1 is patched, so the reason for quarantine is gone. Continuity Works generates
`minecraft:overworld` — which is now **Midgard** — alongside **Regions Unexplored** 0.5.6, and both
inject through TerraBlender exactly as their authors intended. No architecture work was required:
the mod was already pointed at the right dimension the moment Alfheim left the Overworld slot.

Note why the crash was dangerous rather than merely annoying: the Overworld level is created and its
spawn chunks load whenever the world runs, even though the player wakes in Alfheim. An unbound
holder there was a crash risk from world creation onward, not something deferred until the player
first used the gate — and because `FeatureSorter` only throws once a chunk resolves an affected
biome, whether it appeared at all depended on the seed.

## What was already correct

Recorded so it is not changed by accident: Forge 1.20.1 targeting, `[47.4.10,)` / `[1.20.1,1.20.2)`
ranges, unique mod IDs with no collision against the installed `continuity` connected-textures mod,
convention tags on its biomes, and not claiming the Overworld generator outright. The acceptance scan
passed 0 fail / 1 warn / 5 pass, and the mod loads cleanly — the failure is at world generation only.
