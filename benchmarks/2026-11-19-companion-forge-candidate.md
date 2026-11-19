# Companion first-party Forge candidate — 2026-11-19

**Status: candidate built and unit/source checks passed; runtime admission pending.**
This is an evidence record, not a shipped release or a retagged version.

| Field | Verified value |
|---|---|
| Project | Alfheim Reclaimed, Minecraft 1.20.1 / Forge 47.4.10 |
| First-party source commit | `f1a43100c45ba1efb52db673f624362774fa6f4f` |
| Source URL | https://github.com/mrcalzon02/Alfheim-Reclaimed/commit/f1a43100c45ba1efb52db673f624362774fa6f4f |
| CI workflow | https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44626195977 |
| CI job | `135920561346` — success |
| Toolchain | GitHub Actions Ubuntu; Temurin Java 17; Gradle 8.8 wrapper |
| Command | `./gradlew --no-daemon --stacktrace clean test build -Pinstance_mods_dir=../../server/mods` |
| Build result | `BUILD SUCCESSFUL in 2m 44s`; `compileJava`, `reobfJar`, `compileTestJava`, `test`, `check`, `build` completed |
| Candidate binary | `build/libs/alfheim_companion-0.2.0.jar` |
| Candidate SHA-256 | `f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246` |
| Artifact ID | `14580075904` |
| Artifact name | `alfheim-companion-candidate-f1a43100c45ba1efb52db673f624362774fa6f4f` |
| Artifact archive size | 4,232,700 bytes (ZIP archive, **not** JAR size) |
| Artifact retention | Expires November 26, 2026 at 22:14 UTC |

## Verified checks

- Node 22: syntax, original Greatbole claims, spawn protections, player-login,
  starting-kit recovery, companion lifecycle and admission source assertions.
- Python 3: full spawn ownership negative controls.
- Java 17: wheel selection, ticket delta, handoff rules, landing plan, admission
  reservation, and production inventory-retention service against test doubles.
- ForgeGradle: clean current first-party source compilation, tests, reobfuscated
  candidate JAR, and successful build checks.
- Existing Java deprecation warnings (e.g. `ResourceLocation` constructors) are
  diagnostics, not build/test failures. No blocking failure was reported.

## Boundaries and next gates

The candidate is **not** installed to the client or server. At the time of inspection
the tracked root and server `alfheim_companion-0.2.0.jar` files were different
(5,161,333 versus 5,013,072 bytes) and not equivalent to a verified fresh build.
Do not replace either binary until the candidate is checked on a complete instance.

1. On a clean staging copy, install the same verified candidate binary into both
   client and dedicated server; preserve old copies for rollback.
2. Verify full game startup with pinned dependencies, one fresh world and one
   existing-save load/reload, no release-blocking startup errors.
3. Test first summon, rejected admission and retry, regular dismissal/restore,
   loaded and unloaded recall, cross-dimensional failure, item retention,
   two-player handoff, and mid-session reconnect.
4. Record exact startup logs, binary hashes, player inventory and world persistence,
   and multiplayer results for the **same** candidate before any promotion.
5. Only after full functional acceptance should a new distinct version and release
   be assigned. Do not retag any existing version, and do not redistribute
   third-party jars.

The build/run is evidence for source commit `f1a43100`, **not** for the
documentation-only commit that records it. All testing claims are bounded to
the successful GitHub workflow and its exact source revision.
