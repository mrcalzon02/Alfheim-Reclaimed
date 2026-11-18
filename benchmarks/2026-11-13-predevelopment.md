# Alfheim Reclaimed — 2026-11-13 pre-development benchmark

**Audit identifier:** `alfheim-benchmark-20261113-ba1b8e4` (source-audit identifier; **not** a GitHub release, tag, compiled build, or redistributable pack).
**Frozen implementation revision:** `ba1b8e4eab581947508e98605adc78398c0147c0` on `main`.
**Review date:** 2026-11-13.
**Result:** **SOURCE BENCHMARK RECORDED; RELEASE BUILD / RUNTIME ACCEPTANCE NOT ESTABLISHED.**

This document is an evidence-bound baseline before further implementation. The documentation-only commit which introduces this record is *not* the implementation SHA above. Do not replace that SHA with this documentation commit when comparing build outputs. No feature code, binaries, branches, tags, or published release assets were changed for this audit.

## Live repository and CI facts

- Public repository: https://github.com/mrcalzon02/Alfheim-Reclaimed
- The implementation revision was the HEAD of `main` at inspection; latest implementation commit dated 2026-11-01 21:29:11 UTC.
- GitHub Releases returned zero published or draft releases during this audit. No benchmark release assets exist.
- GitHub Actions lists three `Frontier shipping NBT source regression` runs; all three completed successfully. Latest is https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/41352242161 at the exact frozen implementation revision.
- That workflow runs three synthetic/shipping-NBT regression steps on `ubuntu-latest`. Its job uses `continue-on-error: true`: useful diagnostic proof, **not** a full Forge startup, Java compilation, complete modpack compatibility run, or hard release gate.
- No new runtime, ForgeGradle build, full source suite, or graphical-client run was executed in this audit. The audit environment lacks a working GitHub DNS clone route and is running Java 21, while the Forge projects require Java 17. Historical test successes must not be presented as tests run today.

## Version, build, and configuration inventory

| Item | Observed at frozen SHA | Interpretation |
| --- | --- | --- |
| Pack | Minecraft 1.20.1 / Forge 47.4.10 / Java 17 | All three first-party Forge Gradle projects target the profile |
| Latest named design version | `0.23.0-design` (CHANGELOG.md and INSTRUCTIONS.md) | Many October 17+ changes are not captured by a new numbered release |
| README declaration | `0.20.0-design` | Documentation is stale; reconcile before versioned packaging |
| Companion Forge mod | `0.2.0` | Installed JAR exists in root and server directories |
| Leyworks Forge mod | `0.1.0` | Installed JAR exists in root and server directories |
| Golems Forge mod | `0.1.0` | Installed JAR exists in server/mods, absent from root mods |
| Companion inference worker | `0.1.0`, separately built with Java 21 | Optional local process, not the Java 17 Forge runtime |
| Root `mods/` | **2 JARs** | Not a complete client modpack |
| `server/mods/` | **84 JARs** | Runtime mirror with 82 files not present in root mods |
| `config/mythicbotany.json5` | `lockAlfheim: false` | Matches required playable Alfheim configuration |

The two JARs common to root `mods/` and `server/mods/` have identical Git blob SHAs:
- `alfheim_companion-0.2.0.jar`: `32ac14aec28f4e1dea9b7ad980b35215f1c33631`.
- `alfheim_leyworks-0.1.0.jar`: `4a4ebccd9ddf42fa40246ab4978a6190510f66d9`.

These are Git object identities, not newly computed binary SHA-256 test results. The server mirror includes externally sourced jars. Follow project policy: **never alter or redistribute third-party jars** in a benchmark release.

## Proven historical evidence versus work still awaiting runtime admission

- October 17 execution/build reports record 72 Java tests passing, matching first-party built/installed/server artifacts, zero reported feature-order cycles, naturally generated Spring and Autumn fairy island samples, 24 saved randomized barrel inventories and 28 naturally placed district pieces. These are **historical recorded results**, not re-run during this benchmark.
- The existing NBT source regression at the frozen SHA passed on GitHub Actions. This verifies its scoped source assertions only. It does not verify four-rotation terrain fitting or client walking/visual acceptance.
- `server/manifest.json` contains an older run with `exit_code: 1`; `server/harness.out` contains a different historical `exit 0` run. Do not use these mixed historical records as a clean present-day end-to-end result.

## Monastery / five-Act labyrinth compatibility boundary

- First-party source contains shared `WorldSiteAllocation`, intercardinal `LabyrinthSiteAllocation`, `LabyrinthGraphPlan`, native `MonasteryLabyrinthStructure` and `MonasteryVillageGeometry`. It describes six strata, 54 rooms, six service stalls and radial Act I–V thresholds at 1,000 / 2,000 / 3,000 / 4,000 / 5,000 blocks.
- The monastery/labyrinth registration files remain under `alfheim_reclaimed_design/monastery_labyrinth/pending_worldgen/`, outside the active KubeJS worldgen data. Correctly **do not activate** those registrations against an unverified JAR.
- The current companion binaries were last committed 2026-10-18. Monastery/labyrinth implementation source changed again on 2026-10-28. Consequently the installed companion JAR is **not verified to implement the frozen source**; it must be rebuilt and compared before deployment.
- Direct JSON integrity audit on `monster_catalog.json` at frozen SHA passed **11/11 static invariants**: 130 unique monster designs, 26 per Act, one boss per Act, unique signature identifiers, 36 unique affixes, at least 10 roles (17 observed), counterplay descriptions, five distance-only encounter profiles. Every creature is still explicitly `design_only` with model `unassigned`. **No live monster spawning or gameplay has been proved.**
- Shared policy preserves Hollow Court, moved spawn, district and three castle candidate envelopes in Java source; this is not a fresh-world collision acceptance test.

## Release gate decision

**The frozen source is suitable as a comparison benchmark. It is not a verified runnable or publishable modpack release.**

Release-blocking evidence not yet available for this snapshot:
1. Java 17 clean build/test of current first-party source and matching deployed artifacts, including companion after October 28.
2. Full pack client and server launch/load (including required multiplayer behavior), with a final reproducible manifest and unmodified third-party dependencies.
3. Fresh-world generation, stability, save/reload and cross-system collision tests on the exact packaged binaries. Specific new monastery gameplay cannot be called a release feature while its active registration, vendors, creatures and runtime acceptance remain absent.

Visual polish, cosmetic balance, terrain aesthetics and nonfunctional diagnostics are recorded separately; they are not made release-blocking merely because they remain unfinished. For the monastery, activation before a matching build may cause actual codec/startup failures and is a functional gate, not a visual concern.

## Reproduction / next-stage checklist

- Freeze implementation SHA `ba1b8e4eab581947508e98605adc78398c0147c0` as the pre-development reference.
- On a Java 17 Forge-capable runner with the real dependencies installed, execute the existing first-party Gradle wrappers/tests; record commands, exact SHA, exit codes, artifact hashes, and logs. Do not assume historic results apply to the Oct 28 source.
- Validate build-to-installed and server mirror equality, manifest completeness, `lockAlfheim=false`, scripts/recipes, player arrival in `mythicbotany:alfheim`, and extended generation at distances beyond the previously observed ~625-chunk failure zone.
- Before admitting the five-Act monastery family, build the updated companion, activate the pending registrations in the same tested deployment, and verify actual placement at 999/1000/1999/2000/2999/3000/3999/4000/4999/5000 radial cases, negative coordinates, district-ring winners, castle candidates, moved spawn, supported surface elevation and bedrock approach.
- Do not conflate the design-only bestiary, model stubs, decorative vendor stalls or successful source parses with functional monsters, merchants, save persistence, or multiplayer acceptance.
- Once the package actually builds and runs, use a new version/tag/release record rather than retagging or rewriting the pre-development snapshot. Draft releases are excluded from the definition of latest; published prereleases count.

**No GitHub release was created, no tag was moved, no existing workflow was disabled or triggered, and no feature code was modified by this audit.**
