# Alfheim Reclaimed — Project Instructions

**Role:** Stable project doctrine. Authority hierarchy, premise, scope, boundaries, validation philosophy.
**Change:** deliberately and infrequently. Volatile state belongs in `EXECUTION_STATE.md`, intent in `BACKLOG.md`.
**Method:** AI Project Manager v3.0, plus the Repository Execution Protocol and the Minecraft Java Profile.

---

## 1. Premise

You are an elf of Alfheim, on **the far side of the Alfheim Gate**.

Magic devastated the world. The elven homeland is a wasteland of collapsed tree-cities, drowned
gardens, dead ley-lines and silent shrines. You rebuild it with botanical magic — not with engines.

**Alfheim is where you wake up.** Not a dimension you travel to; the ground you start on. It is
magical, whimsical, and deliberately **poor in ordinary metals** — that scarcity is what forces the
trade. The gate leads *outward* to **Midgard**, the industrial world that died.

> **Revised 2026-09-02 — Alfheim is no longer the Overworld *slot*.** Alfheim is
> **`mythicbotany:alfheim`**, the dimension MythicBotany already ships, and the player spawns there.
> **`minecraft:overworld` is Midgard.** See `alfheim_reclaimed_design/WORLD_STRUCTURE.md`.
>
> The previous design overrode the Overworld world preset to run MythicBotany's Alfheim generator.
> That was struck for three reasons, none of them cosmetic:
>
> 1. The override was **duplicating the mod's own dimension**. `data/mythicbotany/dimension/alfheim.json`
>    already contains the exact generator block the preset was copying, so the override bought a
>    hand-maintained copy of something the mod ships and tests.
> 2. It was **the riskiest unproven assumption in the project** (former B-12), and it was never
>    verified in a fresh world.
> 3. It put Alfheim in the slot every TerraBlender mod injects into, which is why Continuity Works
>    and Regions Unexplored both had nowhere to generate. With the Overworld left vanilla, both
>    work as shipped and populate Midgard — which is where their content belonged all along.
>
> **The cost, stated plainly:** mods that hardcode `Level.OVERWORLD` in Java now see the player's
> home world as "not the overworld", and no datapack can reach that. Alfheim's dimension type is
> otherwise an Overworld clone — `bed_works`, `natural`, `has_skylight`, `effects: minecraft:overworld`,
> height 384 / min_y −64, coordinate scale 1.0, normal day cycle; only `has_raids` differs — so the
> exposure is hardcoded checks, not dimension properties. Finding them requires booting, which is
> cheaper than proving the preset override worked.

The single most important consequence of standing on the far side of the gate is this:

> **Elven materials are native. Human materials are exotic.**

In unmodified Botania the player is a human who feeds mundane goods into the Alfheim Portal and
receives elven goods back. Here that relationship is inverted. Dreamwood grows in your forests.
Elementium is an ore you mine. What you *cannot* easily get is Livingwood, Manasteel, Mana Diamonds
— the products of a Midgard the elves no longer reach freely.

The gate is therefore not a reward for progression. It is a **trade route**, and it runs the other way.

## 2. The three systems

The pack has exactly three load-bearing systems. Every other mod is support.

### 2.1 The Twin Spines

Two magical traditions develop in parallel across the whole campaign. Neither is optional, and
neither completes without the other.

| Spine | Mods | Character | Supplies |
|---|---|---|---|
| **Spine of Leaf** | Botania, MythicBotany | Growth, mana, material transmutation | Power, metals, infrastructure |
| **Spine of Song** | Ars Nouveau | Source, glyphs, ritual, familiars | Knowledge, automation, utility |

Leaf is what you build *with*. Song is what you build *through*. Era gates require progress on both;
neither spine may be completed alone.

> **Settled 2026-09-02.** The brief originally named *Ars Magica*; the user confirmed **Ars Nouveau**
> is intended. Ars Magica has no 1.20.1 Forge build and its lineage (*Mana and Artifice*) is not
> installed. Ars Nouveau is installed, pinned, and already assigned "elven sorcery, rituals, magical
> automation" by the original design matrix. The Spine of Song is Ars Nouveau. Closed.

### 2.2 The Wound (Mine and Slash) — the world interaction layer

Mine and Slash is **how the player touches the world**. It is not a side system and not merely a
reward economy: combat, exploration, expedition, gear and personal power all run through it. Every
other mod feeds *into* it, routes *through* it, or draws *out* of it.

- combat difficulty, and the reason ruins are dangerous at all;
- Adventure Maps as instanced expeditions into what magic destroyed;
- currency orbs, gear, gems and uniques as the reward vocabulary the whole pack pays out in;
- levels and talent trees as the player's personal power curve, parallel to the material curve.

It remains true that Mine and Slash never *gates a spine milestone directly* — the spines govern what
can be made, and the Wound governs what can be reached and survived. But the two are not separable in
practice: an era's materials are gathered on expeditions, and expeditions are survivable only with
what the spines produced.

### 2.3 The gating doctrine — everything routes through the spines

The magic spines are the spine of the **entire pack**. Nothing meaningful is obtained outside them.

1. Every progression-relevant recipe in every support mod is re-gated so its unlock, its materials,
   or both come from Botania, MythicBotany or Ars Nouveau.
2. A support mod that cannot be routed through a spine is a candidate for removal, not a candidate
   for an exception.
3. Convenience and decoration may stay ungated. Power, capability and progression may not.
4. Recipe work is therefore **pack-wide**, not confined to the Botania tree. This is the largest
   single body of implementation work in the project.

The rule in §6.1 still binds: nothing is removed before its replacement exists and has been played.

## 3. Authority hierarchy

1. User instruction and granted scope.
2. Platform safety and permission boundaries.
3. This document.
4. Design records under `alfheim_reclaimed_design/`.
5. `EXECUTION_STATE.md`, then `BACKLOG.md`.
6. Conversation and session context.

Where a design record contradicts this document, this document wins and the record is corrected.

## 4. Project profile

Establish from here, never from memory of another version.

| Fact | Value |
|---|---|
| Minecraft | 1.20.1 |
| Loader | Forge 47.4.10 |
| Java | 17 (launcher-managed) |
| Mods installed | 84 jars in `mods/` (counted 2026-09-05, including EntityJS). The loaded-mod total is not stated plainly in `logs/latest.log`; do not quote one until a run reports it. |
| Pack version | 0.18.0-design — `CHANGELOG.md` is the authority for this number |
| Quest engine | FTB Quests 2001.4.22 |
| Scripting | KubeJS 2001.6.5 (Rhino 2001.2.3) |
| Home dimension | **`mythicbotany:alfheim`** — the mod's own dimension. No preset override. |
| Spawn | Player is placed in Alfheim on first join; respawn returns there until Midgard is unlocked |
| Biome injection point | `mythicbotany/libx/biome_layer/alfheim.json` — a LibX **biome_layer**, verified |
| Alfheim biomes | 11 — MythicBotany's 5 plus 6 of ours, with scarce ores via a Forge biome modifier |
| Midgard | **`minecraft:overworld`** — vanilla multi-noise + TerraBlender, **populated by Continuity Works alone**. Revised 2026-09-03: vanilla and Regions Unexplored region weights set to 0, CW to 20. Toggle: `tools/set_midgard_biomes.py`. |
| Custom worldgen mod | Continuity Works 0.3.0-rc.2 — **installed**, locally patched for CW-1, CW-3 and CW-4 (§5.1). Populates Midgard. Backport pending, B-39. |

## 5. Source and artifact boundaries

| Path | Role |
|---|---|
| `INSTRUCTIONS.md`, `BACKLOG.md`, `EXECUTION_STATE.md`, `CHANGELOG.md` | Authoritative project management |
| `alfheim_reclaimed_design/` | Authoritative design records |
| `kubejs/` | Authoritative implementation — recipes, progression hooks |
| `config/` | Runtime configuration; authoritative once tuned, absent until first boot. **`config/ftbquests/` is authored by `tools/gen_quests.py` but normalised by the game** — FTB rewrites it on every world load, alphabetising keys. Read the game's form. **TerraBlender region weights live here, not in a datapack** — `tools/set_midgard_biomes.py` owns them. |
| `mods/` | Runtime artifacts. **Third-party jars: never edit, never redistribute.** First-party jars (Continuity Works) may be patched — see §5.1. |
| `tools/` | Development tooling. Never packaged, never placed in `mods/`. |
| `quarantine/` | Jars removed from the load path, preserved for reversibility |
| `saves/`, `logs/`, `crash-reports/` | Runtime evidence, not source |
| `minecraftinstance.json` | CurseForge-owned manifest. Edit only while CurseForge is closed. |

### 5.1 First-party jars — Continuity Works

**Continuity Works is the pack owner's own mod.** It is developed in a separate repository and
reaches this pack as a built jar, so the separation of *authority* stands: bugs are reported upward
and the real fix belongs in its source. But it is not third-party, and the read-only rule in §6.5
does not apply to it.

A first-party jar may be patched locally **as a stopgap**, on these conditions:

1. **The owner asks for it.** Not a default.
2. **The defective original is preserved** unmodified in `quarantine/`, with its hash recorded.
3. **The patch is a re-runnable tool under `tools/`**, not a hand edit — so the change is exactly
   reproducible and reviewable for the backport.
4. **The patched artifact is renamed** with a `+<fix>patch` suffix, so it cannot be mistaken for an
   official build of that version.
5. **The change is minimal and verified** — the tool proves every entry it did not intend to touch
   is byte-identical.
6. **It is recorded as a stopgap** in the defect report, and dropped the moment an upstream build
   carries the fix. A local patch and its source must never silently diverge.

Precedent: CW-1, CW-3 and CW-4, all patched 2026-09-03 —
`alfheim_reclaimed_design/CONTINUITY_WORKS_DEFECTS.md`. A further defect does not get a further
chained jar: `tools/patch_continuity_works.py` always runs from the **preserved original**, so the
installed artifact is reproducible in one step and cannot drift from the recorded input hash.

## 6. Non-negotiable behaviour

1. **Do not purge recipes before replacements exist and are tested.** The reversal removes the
   player's normal route to Botania's early game; the replacement route must be in place in the same
   change, or the pack soft-locks at first flower.
2. **Every gated item must have exactly one reachable route.** Before any recipe is removed, name the
   replacement and the era that unlocks it.
3. **Static validation is not runtime acceptance.** A KubeJS script that parses is not a script that
   works. Levels 8–12 of the validation ladder require a booted game.
4. **One quest chapter at a time.** Author, load, verify in-game, then move on. Do not generate ten
   eras of SNBT against an unverified schema.
5. **`lockAlfheim` must stay `false`** in `config/mythicbotany.json5`. It ships `true` and blinds
   any player who reaches Alfheim without the Mead of Kvasir — which, in this pack, is every player
   on the intended path. One key; the default is simply wrong for us.
6. **Third-party jars are read-only.** All behaviour changes go through KubeJS, datapacks or config.
   **First-party jars (Continuity Works) are the one exception** — patchable as a stopgap under the
   six conditions in §5.1, never as a substitute for fixing the source.

## 7. Validation ladder

Applies per change, not once per project. A lower level never implies a higher one.

| Level | Check | How |
|---|---|---|
| 1 | Syntax & schema | JSON/TOML/SNBT parses |
| 2 | Java & Gradle | N/A — no source project |
| 3 | Registration & metadata | All mandatory dependencies resolve |
| 4 | Scripts & gameplay data | KubeJS loads without error; recipes appear in JEI |
| 5 | Structure & NBT | Only if custom structures are added. **Always:** `check_feature_order.py` — no two loaded biomes may assert contradictory feature orders, **with Forge biome modifiers applied**. A biome's JSON is not its final feature list. |
| 6 | Source-to-shipping equality | Only if generators are added |
| 7 | Packaging boundary | Disk matches manifest |
| 8 | Controlled startup | Reaches title screen, no errors in log |
| 9 | Fresh-world generation | New world; `mythicbotany:alfheim` generates, the player wakes there, and it is survivable. **Both crashes so far landed ~625 chunks out, not at spawn — a world that creates successfully is not yet a pass.** |
| 10 | Compatibility placement | Worldgen mods coexist; no destructive overlap |
| 11 | Gameplay integration | Quest chapter completes end to end in-game |
| 12 | Production admission | All governing gates passed or formally deferred |

## 8. Acceptance states

`draft` → `static validated` → `runtime validated` → `fresh-world validated` → `production admitted`

Also valid: `deferred` (with named reason and resumption condition) and `rejected` (repair the same
target; do not advance to the next).

Never write "done." Never write "production ready" for something that has only passed static checks.

## 9. Genuine blockers

Stop only for: missing authorization, a decision only the user can make, destructive ambiguity, or a
capability that cannot be recovered. A failed command, an empty directory, or an untested script is
not a blocker — it is the next piece of work.
