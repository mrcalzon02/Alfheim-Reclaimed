# Alfheim Reclaimed — FTB claim reload optimization acceptance

**Status at authoring:** full-pack runtime retest pending. Prior source-only CI passed.

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
