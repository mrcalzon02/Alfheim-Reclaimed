# Alfheim Reclaimed

A Minecraft 1.20.1 Forge modpack. You are an elf of Alfheim, on the far side of the Alfheim Gate,
rebuilding a homeland that magic destroyed — with botanical magic, not engines. Alfheim is
magical, whimsical and deliberately metal-poor, and it is where you wake up. The gate leads outward
to Midgard, the industrial world that died — which is where the ordinary metals are.

Alfheim is **`mythicbotany:alfheim`**, the dimension MythicBotany ships; **`minecraft:overworld` is
Midgard**, left vanilla and populated by Continuity Works. The world-preset override was struck on
2026-09-02 — `INSTRUCTIONS.md` §1 records why.

**Version** 0.13.0-design · **Forge** 47.4.10 · **Mods** 83 jars in `mods/` · **Status** boots and
generates headlessly (levels 8–9); the newest work is `static validated`, not runtime

## Start here

| Read | For |
|---|---|
| [INSTRUCTIONS.md](INSTRUCTIONS.md) | Doctrine: the premise, the three systems, what must never be done |
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | **The build order** — 9 stages, each with a verification gate |
| [EXECUTION_STATE.md](EXECUTION_STATE.md) | Where the project is right now and the next exact action |
| [BACKLOG.md](BACKLOG.md) | What is eligible to work on, in dependency order |
| [CHANGELOG.md](CHANGELOG.md) | What has actually been done, with evidence |

## Design records

`alfheim_reclaimed_design/` — see its [README](alfheim_reclaimed_design/README.md) for the index.
The three that carry the design:

- **[GATE_REVERSAL.md](alfheim_reclaimed_design/GATE_REVERSAL.md)** — Botania's elven trade recipes
  run backwards here. Elven materials are native; human materials are the exotic imports.
- **[CAMPAIGN_ERAS.md](alfheim_reclaimed_design/CAMPAIGN_ERAS.md)** — ten eras, 215 quests, each era
  capped by one of MythicBotany's Nine Realm runes.
- **[TWIN_SPINES.md](alfheim_reclaimed_design/TWIN_SPINES.md)** — Botania and Ars Nouveau as two
  halves of one broken tradition; neither completes alone.
- **[WORLD_STRUCTURE.md](alfheim_reclaimed_design/WORLD_STRUCTURE.md)** — Alfheim as its own
  dimension, the verified biome injection point, and the cost of getting there.
- **[SPAWN_ZONE.md](alfheim_reclaimed_design/SPAWN_ZONE.md)** — the Greatbole arrival tree and the
  Hollow Court: a 1000-block drained elven city, and how to build one without authoring 3 million m².
- **[PROCESS_INDEX.md](alfheim_reclaimed_design/PROCESS_INDEX.md)** — all 171 crafting methods in the
  pack, ~95 of them usable stations; the menu the tier ladder draws from.

## The next thing to do

The pack **boots and generates**, headlessly — level 8 and level 9 both passed on 2026-09-04, and
the Greatbole spawn hub is runtime-proven. Since then three passes landed `static validated` and
have never been seen in a world: thirty-two surface structures and the Cartographer (B-73), the
Liquid Bifrost chain, and the Guild Regalia asset build (B-74). All 63 Regalia textures, models,
startup declarations and slot tags now exist; effects and recipes remain pending.

Next: restart the client, verify the Regalia items in JEI and probe Curios slot capacities, then
implement the Warrior/Mining effect slice (B-74). The wider quest-coverage backlog and a client
playtest of the surface structures also remain. Preview the [63-item review sheet](tools/curios_review.png).

Two items are **blocked on a user decision** — deer and toads both need an entity type that neither
KubeJS 2001.6.5 nor 1.20.1 can supply. One defect is still open: `alfheim:scorchfell` is unreachable
by `locate biome` on every run to date.

## Method

Managed under AI Project Manager v3.0 with the Repository Execution Protocol and the Minecraft Java
Profile. Practical consequences: static checks are never reported as runtime success, acceptance
states are named exactly, and no third-party jar is ever edited.
