# Full-modpack dedicated-server first attempt — 2026-11-19

**Verdict: FAIL (shutdown acceptance), with startup and gameplay registrations observed.**

- Workflow: https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44631357459
- Source test commit: `3dd716a4e4b335d8a93901bb8c85a1a86af30e3a`
- Evidence artifact: `14580918589` (expires 2026-11-26)
- Candidate build SHA: `f1a43100c45ba1efb52db673f624362774fa6f4f`
- Candidate JAR SHA-256: `f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246`
- Source/staged server JAR counts: 84/84; only the first-party companion was replaced
  in temporary staging, current `config/`, `defaultconfigs/` and `kubejs/` were copied.

## Verified findings

- Forge `Done (48.267s)` on a newly staged Minecraft 1.20.1 / Forge 47.4.10
  dedicated server with 6 GiB heap.
- Companion profile and outfit commands returned their expected response lists.
- `execute in mythicbotany:alfheim run say ALFHEIM_DIMENSION_OK` succeeded.
- Spawn hub claim reconciliation said `FTB ownership verified 100/100 chunks`.
- FTB Quests reported 3 chapter groups, 19 chapters and 508 quests.
- Minecraft logged `Stopping the server`, then `All dimensions are saved`.
- The harness reached a 60-second process wait deadline measured from enqueuing
  `stop`, after the heavy world-generation tick work delayed command replies
  until nearly 60 seconds after `Done`. It then terminated Java (exit 143),
  so clean process exit was NOT proved.
- Runtime separately printed `deterministic Greatbole template assembly failed
  at the origin; one retry remains`. This requires diagnosis and cannot be
  counted as completed spawn construction.
- KubeJS reported one failed recipe; this is a diagnostic for investigation,
  not proof of an installation or launch failure.

## Next bounded test

The revised smoke harness measures command-response latency and shutdown timing
separately, with 210-second response and 180-second shutdown bounds in the full
profile; it probes read-only Greatbole per-piece scoreboard state on the
running server. It still runs in an isolated temporary directory, uploads only
bounded log/JSON evidence even on failure, and never replaces a tracked JAR.

**No client, save/reload, or multiplayer gameplay testing occurred.** This is
not a release-ready modpack result.
