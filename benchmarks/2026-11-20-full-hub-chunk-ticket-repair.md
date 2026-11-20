# Full 121-chunk Greatbole persistence repair — 2026-11-20

## Admission

**ACCEPTED for an isolated 84-mod Forge 1.20.1 dedicated server and saved-world
restart.** Source `49288d7ab7a2336ce00e0cea1ae3a05d9da9293e`;
[CI #44790630724](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44790630724),
evidence artifact `14657525105` (seven-day retention).

The temporary server uses seed `alfheim`, pinned first-party companion JAR
SHA-256 `f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246`,
the complete staged 84-mod pack, and the same saved world for two boots.
There are no connected players and no production save/JAR changes.

## Live and saved-state acceptance

| Gate | First saved world | Second saved world |
|---|---|---|
| Greatbole parts and baked marker | 7/7, accepted | 7/7, no duplicate assembly |
| Persisted hub force-load tickets | **120/121** (deliberate hole) | **121/121** (repaired) |
| Interior chunk [1,-1], block (16,-16) | not forced (saved NBT) | forced (saved NBT) |
| Separate operator ticket [12,12], block (192,192) | forced | forced |
| Negative control [12,14], block (192,224) | not forced | not forced |
| FTB protected spawn chunks | 100/100 | 100/100 |
| Foreign claim conflicts / redundant warnings | 0 / 0 | 0 / 0 |
| Clean stop, saved dimensions | pass | pass |
| Total boot/test duration | 187.1s | 103.0s |
| Max logged tick lag (diagnostic, not controlled comparison) | 39,362ms | 2,781ms |

Actual NBT parsed with `tools/nbt.py` from the disposable world's
`dimensions/mythicbotany/alfheim/data/chunks.dat`, checking the `data.Forced`
long array and Mojang packed signed chunk coordinates. Both saves passed
strict membership gates, not merely the live `/forceload query` command.

The first saved file was 330 bytes with SHA-256
`43ba8b773cdd1fe10adcc0dfffab767e5f7e324477e5b7f9a2fc0292675dff51`.
The restarted/saved file was 336 bytes with SHA-256
`de571a2667e25288eef76350a69db51d160550adf0dbb5ccc63b5a268cad9577`.
Different content verifies that the absent chunk was actually persisted after
the repair.

## Defect reproduction and correction

The old five-probe autoload missed interior holes. Source `851ff8f` expanded
read-only coverage to all 121 chunks, and live run `44787524650` passed
console-level restoration. That was insufficient proof of *saved* recovery.

At source `3c1206d`, run
[44789431936](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44789431936)
added a fail-closed, binary NBT membership gate and exposed the real defect:
first save 120/121, live restart 121/121, **second save still 120/121**.
The mixed `/forceload add -80 -128 80 32` touched 120 already-forced
chunks as well as the missing one; the desired state did not persist.

The final correction in `49288d7` retains the entire 121-chunk read-only
survey but issues a *single-chunk* `/forceload add X Z` only where that exact
chunk is missing. No bulk re-add is performed on reload. The repaired live
test now passes on disk as well as through the command interface.

## Scope and open boundaries

- This is dedicated-server and saved-NBT acceptance only. Graphical client,
  player login/respawn, multiplayer, and inventory persistence remain separate.
- The long first-world tick stall remains a profiling target. Do not
  lower player or simulation tick frequency to hide it.
- The earlier failure-path cleanup can still intersect an independently
  forced chunk *inside* the initial hub candidate rectangle; that is not
  a ticket-ownership isolation guarantee.
- No user world, installed first-party/third-party binary, release or
  tag was altered. Evidence uploads contain logs/JSON only.
