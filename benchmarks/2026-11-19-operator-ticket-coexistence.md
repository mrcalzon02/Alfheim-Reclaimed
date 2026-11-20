# External operator chunk-ticket regression — 2026-11-19

## Problem
Previous Greatbole functions used `forceload remove all`, clearing unrelated operators' and
mods' forced chunks. Commits `47b2d82` and `972214b1` corrected the generated functions
and player delivery scopes, but had only source-level acceptance.

## Verification protocol
A disposable, loopback-bound, 84-JAR Forge server creates a fresh world on seed `alfheim`.
Once the seven-part Greatbole is confirmed, the harness performs real console commands:

1. Query X192/Z192 in `mythicbotany:alfheim` — require not forced (0).
2. Force-load the external chunk; query again — require 1.
3. Invoke real `function alfheim:hub/anchor` and query again — require 1.
4. Query distinct X192/Z224, which must remain unforced (0).
5. Save and cleanly stop, restart the exact same temporary world/JARs,
   and require X192/Z192 to still be forced (1), negative to be 0.

All query results are captured via `execute store success score` and verified from
actual scoreboard output, not command text. A bounded 120-second response window
fails closed. The existing 100/100 FTB-claim, seven-stage marker and clean-restart
gates remain in force. No player worlds or installed JARs are touched.

**Acceptance on this source commit: pending CI.** Even a green result will not prove
operator-ticket ownership overlap *inside* the hub region or joined-player behavior.

## 2026-11-19 runtime failure and MC-143952 hypothesis

Full 84-JAR run [44662546115](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44662546115)
at `96399f5` had a clean first boot, 7/7 Greatbole stages, 100/100 FTB claims
on both boots, no duplicate generation or claim warnings, and clean saved-world
restart. The independent chunk at (192,192) was unforced, then forced, then still
forced after manually replaying `hub/anchor` (scoreboard 0→1→1). **After restart
it was absent (0)**. The failed gate exposed a real persistence regression
missed by source CI.

Minecraft issue [MC-143952](https://mojira.dev/MC-143952) affects Minecraft
1.20.1: a redundant/failed `/forceload add` can reset `chunks.dat` dirty
state, discarding new forced tickets at save. The re-run `hub/anchor` tried
to add an already-forced 11×11 footprint after adding the external ticket.
The next source revision skips that redundant command once `#final=1`.
Autoload now probes the corners and origin and re-adds the footprint only if
a probe is missing. Provisional fallback also probes before re-adding.

**Hypothesis pending re-test.** The five autoload probes are not exhaustive
for individually cleared interior chunks; a future per-chunk or native
ticket-set check is needed if partial-footprint repair is observed.
