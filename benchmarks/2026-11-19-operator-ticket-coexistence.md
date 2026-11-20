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
