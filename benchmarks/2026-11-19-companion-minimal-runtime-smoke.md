# Alfheim Reclaimed — first-party companion minimal Forge runtime smoke

**Date:** 2026-11-19.
**Acceptance:** Java 17 ForgeGradle compilation/tests **passed**; minimal Forge dedicated-server
startup, command registration and graceful shutdown **passed**. **Full modpack,
graphical client, save migration and multiplayer have not been tested.**

## Immutable candidate identity

| Field | Evidence |
|---|---|
| Candidate source commit | `f1a43100c45ba1efb52db673f624362774fa6f4f` |
| Build workflow | https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44626195977 |
| First-party JAR | `alfheim_companion-0.2.0.jar` |
| JAR SHA-256 | `f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246` |
| Built artifact ID | `14580075904` (expires November 26, 2026) |
| Minecraft / Forge / Java | Minecraft 1.20.1 / Forge 47.4.10 / Java 17 |
| Runtime source | Existing tracked Forge server libraries and the owner's accepted EULA |
| Staging | Temporary OS directory; no in-repository world or installed JAR changes |

## Executed runtime checks

| Run | Commit | Real result | Evidence artifact |
|---|---|---|---|
| Minimal startup/shutdown | [`c49530c3`](https://github.com/mrcalzon02/Alfheim-Reclaimed/commit/c49530c3d9867e42b4992e284d0fbbc7dca21ed7) | [Successful](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44628400029) | `14579768072` |
| Companion command registration | [`2bb3d568`](https://github.com/mrcalzon02/Alfheim-Reclaimed/commit/2bb3d5685792a2d7bcd8f6b54a66c22ff034970f) | [Successful](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44628910896) | `14580507607` |

Both workflows completed with successful single-job conclusions. The run log records
`COMPANION_SERVER_SMOKE_PASS` after verifying the exact candidate hash, booting
the Forge dedicated server and shutting it down with exit code 0.

The stricter second run additionally executed the real server console commands:

- `alfheimcompanion profile list` — required the actual `Companion profiles:` response
- `alfheimcompanion outfit list` — required the actual `Companion outfits:` response

The test fails if either response is missing, even if Minecraft otherwise boots.
The Python self-test, Node source regressions, Java 17 admission/landing/wheel/ticket
checks and inventory-retention test also passed on the stricter run.

## What was deliberately NOT tested

The smoke server loaded **only** Forge and the exact companion candidate. It was
bound to `127.0.0.1` with `online-mode=false`, a 4 GiB JVM heap and a hard
480-second startup budget. An identical binary was staged as a client-side copy
for hash comparison; **no graphical client was launched**. No third-party mods,
full original pack configs, quest hooks, new or existing player saves, or
real multiplayer clients were used in this smoke profile.

The tracked client `mods/alfheim_companion-0.2.0.jar` and
`server/mods/alfheim_companion-0.2.0.jar` remained untouched. Their earlier
different byte sizes mean they still must not be described as synchronized.

## Next release gates

1. Run the pinned candidate on a sufficiently provisioned full-modpack staging
   server, with the actual pack config/worldgen dependencies and an explicit
   source-to-binary hash read-back.
2. Boot a compatible graphical client with **that same** candidate JAR.
3. Test new-world entry, save/reload, companion first summon, refusal/retry, safe
   landing, dismissal/restore, realm transfer and two-player handoff.
4. Capture server/client logs, exact hashes, persisted UUIDs, cargo and equipment
   before/after tests. Admit the feature only after those functional gates pass.
5. Create a distinct version/release only after those gates; do not retag or
   redistribute third-party mod binaries.

**This is a minimal runtime acceptance milestone, not a pack release.** Source
commit `f1a43100` remains the immutable build target; the two smoke commits
change test infrastructure only.
