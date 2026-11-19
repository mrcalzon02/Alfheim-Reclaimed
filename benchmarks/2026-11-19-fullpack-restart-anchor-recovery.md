# Full-pack Greatbole saved-world restart — anchor recovery

## Accepted full-modpack saved-world restart — 2026-11-19

**PASS: GitHub Actions run [44640185308](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44640185308).** First world assembly and the reload of the **same temporary saved world** both succeeded using the exact candidate JAR from source `f1a43100`.

| Measure | Verified result |
|---|---|
| World and code under test | Seed `alfheim`, 84 server mod JARs; smoke source commit `3d73de84735ad0fe670214576b712a6aaef27066` |
| First Forge readiness | `Done (49.774s)` |
| First server total runtime | 240.2 s; shutdown wait 65.6 s; exit 0 |
| First hub construction | All 7 part scores = 1, `#place_result=#created=#final=1`, `#attempts=1`; baked anchor present |
| Persisted world | `level.dat` existed and its SHA-256 changed across the restart save, confirming two distinct saves |
| Second Forge readiness | `Done (14.883s)` |
| Second server total runtime | 113.0 s; shutdown wait 21.5 s; exit 0 |
| Second hub state | All seven part scores and completion flags remained 1; `#attempts` remained 1 |
| Baked marker on second boot | Found by read-only probe after **2 attempts / 6.0 s** of bounded grace |
| Duplicate hub construction | None; `hub_assembled_this_boot=false` on restart |
| Companion commands and Alfheim dimension | Both passed on each boot |
| Installed modpack | Untouched; staged client and server candidate SHA-256 equal |
| Binary SHA-256 | `f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246` |
| Runtime evidence artifact | `14585578917`, expires November 26, 2026 at 23:51 UTC |

**Why two earlier attempts failed:** At `9344d827`, the hub's saved marker could not load because autoload depended on selecting the unloaded marker before force-loading its chunk. `fc498ee7` fixed this cycle using the deterministic origin force-load; that run still queried the marker too soon after readiness. `3d73de84` retried the existing marker for a bounded 60 seconds without creating any entity. The marker appeared after 6.0 seconds; the server then exited normally.

This **accepts the dedicated-server Greatbole save/restart behavior for seed `alfheim`**, not player-save persistence, client startup, graphical controls, companion movement, performance across other seeds, or multiplayer inventory/lease behavior. The ~40s first-world tick spike remains a profiling diagnostic, and the missing native Feywild ingredient remains unresolved. No release was created.

---
**Historical initial restart: FAIL** — full-pack CI
[44637365193](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44637365193).

The first boot successfully assembled all seven Greatbole/court parts,
anchored the hub and saved `level.dat`. On second boot all seven scores,
`#created=1`, `#final=1`, `#attempts=1` persisted and Forge exited
cleanly. However, `ALFHEIM_BAKED_ANCHOR_PRESENT` was missing; server
console reported `That position is not loaded` and
`WARNING: no anchor entity`. This is a **real recovery defect**,
not a failed Java build or missing scoreboard save.

Diagnostic artifact `14584384677` (expires November 26, 2026).
The exact pinned first-party companion JAR SHA-256 remained
`f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246`.

**Source correction:** In `tools/gen_world_hub.py` and emitted
`hub/autoload.mcfunction`, a completed hub now force-loads its
fixed origin envelope without first selecting the baked marker.
A source regression checks exact generator/command parity.

**Acceptance achieved:** The later isolated two-boot full-modpack
test passed loaded-marker, saved flags, no-second-assembly and
clean-shutdown checks at seed `alfheim`. Neither a source test nor the successful
first boot substitutes for that evidence. Graphical client,
two-player gameplay and actual player inventory persistence
remain separate release gates.

## Second restart result and follow-up

The second run, [GitHub Actions 44638990830](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44638990830),
also **FAILED** strict loaded-marker acceptance (artifact
`14586200557`). The second boot again retained `#place_result=1`,
`#created=1`, `#final=1`, `#attempts=1` and 7/7 template
results, with no duplicate construction and clean Forge exit.
Unlike the initial test, the origin was now **loaded**, so the
absolute forceload change solved part of the problem. A saved
marker still was not selectable immediately after startup.

The next strictly bounded check waits for normal entity admission
after chunk loading, issuing only repeated queries of the existing
baked tag for up to 60 seconds. No marker is manufactured or world
data edited to obtain a passing result. A failure remains a failure.
