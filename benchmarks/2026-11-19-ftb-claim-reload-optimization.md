# Alfheim Reclaimed — FTB claim reload optimization acceptance

**ACCEPTED in full-modpack dedicated-server runtime on seed `alfheim` — 2026-11-19.**

The real two-boot [GitHub Actions run #44651235333](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44651235333) passed, and its
[diagnostic artifact](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44651235333/artifacts)
(ID `14590494230`, expires November 27, 2026 at 01:13 UTC) contains the
JSON report and two console logs.

| Measured field | Previous first boot | Previous restart | New first boot | New restart |
|---|---:|---:|---:|---:|
| Protected FTB ownership | 100/100 | 100/100 | 100/100 | 100/100 |
| `already_claimed` warnings | 0 | **100** | 0 | **0** |
| Foreign ownership conflicts | — | — | 0 | 0 |
| Maximum reported tick-lag (ms) | 54,058 | 3,677 | 35,824 | 2,094 |

The prior test is [run #44640185308](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44640185308)
(artifact `14585578917`); the new test is source commit
`f7bb120a5ab63a1cbdc59c7622524b85addfe5a2`.
All 84 mod JARs were staged in isolation. Only the staged companion JAR was
replaced by the previously validated candidate with SHA-256
`f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246`.

The new first Forge boot completed in **178.8s**, restarted server in **105.2s**.
Both exited 0; the Greatbole's seven placement scores and completion flags
remained 1 across restart; baked marker recovered after two read-only probes
over 6 seconds, and no second construction occurred. The exact command
registration and Alfheim dimension checks also passed.

**Measured result:** 100 fewer redundant warnings and zero redundant claim
attempts in the source's saved 100/100 ownership path. The full runtime
readback verifies zero warnings, not direct call counts. First-world lag
remains material; no causal improvement in rendering/simulation performance
is claimed from different run timings. The next profiling focus is
synchronous Greatbole footprint generation/placement and tick duration,
**not** throttling player/AI simulation.

**Scope:** dedicated-server startup and save/restart on one deterministic
seed. No graphical client, real player connection/reconnect, multiplayer
lease/inventory transfer, multiple-seed coverage, or performance-smoothness
acceptance has been established. No installed mod, saved player world or
third-party binary was modified.

---

## Original rationale

## Grounded before/after criterion

The actual GitHub Actions artifact `14585578917` from
[run 44640185308](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44640185308)
contains two server logs from the **same saved 84-mod world**. Before the
idempotent claim improvement (later commit `cc1bee27`):

| Baseline event | First boot | Restart |
|---|---:|---:|
| FTB admin claim ownership | 100/100 | 100/100 |
| `already_claimed` warnings produced by `04_spawn_hub.js` | 0 | **100** |
| Successful Greatbole state | 7/7 | 7/7 |
| Server process exit | 0 | 0 |

The old reload code called `chunkData.claim()` for all 100 already-owned
chunks and emitted one warning per `already_claimed` response. The revised
KubeJS generator template and shipping script skip those redundant mutations
but still validate every owner's team UUID and fail on foreign-owned chunks.

## New runtime acceptance

The updated full-pack smoke harness measures these fields in **each boot**:
`ftb_claims_owned`, `ftb_claims_expected`,
`ftb_redundant_claim_warnings`, `ftb_foreign_claim_conflicts`,
`server_tick_lag_max_ms`, and `server_tick_lag_events`.

A complete two-boot pass now requires **100/100 ownership on both boots,
zero foreign-claim conflicts, and zero `already_claimed` warnings on the
second**. It also retains the previous Greatbole no-duplicate/reload and
clean shutdown conditions. The saved-world comparison uses the same
SHA-256-pinned companion candidate as earlier runs.

Lag values are diagnostic only, not artificial performance improvements
or a release block. Full graphical client and two-player testing remain
unperformed. The repository's tracked/installed JARs and player worlds are
never overwritten by this test.

**Candidate companion SHA-256:**
`f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246`.
