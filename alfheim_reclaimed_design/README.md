# Alfheim Reclaimed — Design Records

**Minecraft:** 1.20.1 · **Loader:** Forge 47.4.10 · **Pack version:** 0.2.0-design

Project doctrine lives in `../INSTRUCTIONS.md`. This directory holds design records — what is true
about the pack's design and why.

## Core premise

You are an elf of Alfheim, on **the far side of the Alfheim Gate**, rebuilding a homeland that magic
destroyed.

**Plants are the machines. Gardens are the factories. Groves are the industrial districts. Mana is
the power grid.**

**Alfheim is where you wake up** — not a dimension you travel to, the ground you start on. It is
`mythicbotany:alfheim`, the dimension MythicBotany ships; `minecraft:overworld` is **Midgard**, the
world that died. Revised 2026-09-02 — see `WORLD_STRUCTURE.md` §1.

Because you stand on the elven side of the gate, the trade relationship Botania assumes is inverted.
Dreamwood grows in your forests and Elementium is an ore you mine; Livingwood and Manasteel are
exotic goods that arrive from a Midgard the elves no longer reach freely. The gate is a trade route,
and it runs outward.

The two magic spines govern the **whole** pack: every progression-relevant recipe in every support
mod is re-gated to route through Botania, MythicBotany or Ars Nouveau. Mine and Slash is how the
player touches the world — combat, expedition, gear and reward.

## The documents

| File | Role |
|---|---|
| `CLASS_ARMORY.md` | **Implemented 2026-09-04:** six verified Mine and Slash base classes, elven weapon suites, ten material grades, armor sets and dual-class builds. |
| `PROFESSIONS_AND_MMO.md` | **Design-first, armory bridge implemented 2026-09-04:** all nine native professions; 480 armory recipes now connect Gear Crafting to tiered mining, salvage and embedded frame materials. The wider trade overhaul remains specified. |
| `CURIOS_AND_PROFESSIONS.md` | **Planned 2026-09-04:** 63-piece Guild Regalia system for six classes and nine professions, using established slots, verified native actions, tradeable ranks and 46 installed Curio anchors. |
| `curios/INSTALLED_CURIOS.md` | Reproducible installed-jar inventory: 147 wearable IDs, recipe presence, eligible slots and the 14 live slot types reported by the last headless run. |
| `curios/SUITE_MATRIX.md` | Compact class/profession-to-anchor matrix; `curios/curio_suite_catalog.json` contains the validated 63-item plan. |
| `armory/WEAPON_FAMILIES.md` | Full simple-to-intricate weapon/offhand naming table; `armory/equipment_catalog.json` maps the 480 registered variants. Texture prompts, alpha evidence and review sheets live beside it. |
| `GATE_REVERSAL.md` | The recipe inversion, its soft-lock risk, and the fix |
| `CAMPAIGN_ERAS.md` | Ten eras, 215 quests, capped by the Nine Realm runes |
| `TWIN_SPINES.md` | How Botania and Ars Nouveau interlock as one tradition |
| `WORLD_STRUCTURE.md` | The two worlds — Alfheim as the Overworld, Midgard as the dead industrial dimension |
| `SPAWN_ZONE.md` | The Greatbole and the Hollow Court — the drained city the player wakes in |
| `PROCESS_INDEX.md` | Every crafting method in the pack — the menu the tier ladder draws from |
| `CONTINUITY_WORKS_DEFECTS.md` | Defect report for our own mod — CW-1 blocks worldgen |
| `PINNED_MOD_MATRIX.md` | The 26 pinned core mods. Accurate but incomplete — 95 are installed |
| `CUSTOM_RECIPE_PLAN.md` | Original recipe doctrine. Still valid; `GATE_REVERSAL.md` supersedes its scope |
| `FIRST_BOOT_VALIDATION.md` | The first-boot checklist. Still the correct procedure |
| `FTB_QUEST_AUTHORING_NOTE.md` | Why no quest SNBT ships yet. Now more important, not less |
| `PROGRESSION_BLUEPRINT.md` | **Superseded** by `CAMPAIGN_ERAS.md`. Kept for provenance |
| `BUILD_METADATA.json` | Pack identity and counts |

## What this pack does not yet do

- ship any FTB Quest data — the schema has not been captured from a running game;
- implement the gate reversal — specified in full, not yet written to `kubejs/`;
- remove any vanilla or mod recipe;
- include performance mods.

The order is deliberate. Boot first, capture the quest schema second, build the elven early game
third, and only then reverse the gate. Reversing it earlier produces a pack that passes every
automated check and cannot be played.

## Java

Forge 1.20.1 uses Java 17. Let the CurseForge launcher manage its runtime unless there is a specific
reason to override it.
