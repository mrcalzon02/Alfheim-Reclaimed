# Full-modpack Greatbole runtime result — seed alfheim, 2026-11-19

**Overall smoke: PASSED (full dedicated-server startup, commands and clean shutdown).**
**Greatbole: PASSED for seed `alfheim`, not yet proven across random seeds.**
**Graphical client, multiplayer and player save/reload: NOT TESTED.**

| Metric | Verified result |
|---|---|
| GitHub run | https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44634440976 |
| Code/data commit | `9a85992433f7e79b7a27222a3d5c002036a525ca` |
| Companion candidate source | `f1a43100c45ba1efb52db673f624362774fa6f4f` |
| Candidate JAR SHA-256 | `f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246` |
| Full-pack mods staged | 84 JARs, no third-party changes |
| Pack data | current root `config/`, `defaultconfigs/`, `kubejs/` |
| Stage | temporary Linux Forge 1.20.1 / 47.4.10, Java 17, 6 GiB heap |
| World seed | `alfheim` |
| Source origin surface height | Y=159 (runtime marker position) |
| Forge-ready time | 36.855 seconds (Forge log) |
| Command-response latency | 43.3 seconds |
| Stop-to-exit time | 47.7 seconds |
| Process | exit 0, all dimensions saved |
| Final hub state | `#final = 1`, `#created = 1`, `#attempts = 1` |
| Template stages | base, trunk, crown, court, west, east, north = **1** each |
| Terrain predicate | `ALFHEIM_GROUND_HEIGHT_OK` |
| Evidence artifact | `14581604446` (expires November 26, 2026) |

## Confirmed gameplay infrastructure

- The full tracked mod set reached dedicated-server readiness and processed
  the real companion profile and outfit commands.
- The `mythicbotany:alfheim` dimension accepted an execution command.
- Greatbole and all six surrounding authored pieces placed at origin.
- The baked marker successfully anchored the hub.
- The spawn protection check reported all 100/100 FTB chunks owned by
  the `alfheim_hub` server team.
- The server reported successful world save and clean exit, with no change
  to installed client or server JARs.

## Open runtime findings

1. **Not an isolated A/B proof of the height fix:** The deterministic seed
   `alfheim` yielded Y=159, which met the *previous* Y64..200 predicate.
   The widened Y32..200 guard addresses possible low-origin failures, but
   that specific mechanism remains unproven until a verified low-Y seed
   and repeated launch/reload test are executed.
2. **Initial-world performance:** The server logged `Can't keep up! ...
   Running 40376ms or 807 ticks behind` after assembly. This major
   one-time startup stall requires profiling; do not call the game smooth
   based on successful boot alone.
3. **One failed native recipe:** KubeJS rejected
   `mythicbotany:feysythia_petal_apothecary` because the third-party
   item `feywild:lesser_fey_gem` was not registered. Do not remove the
   recipe until a valid replacement ingredient is verified in-game.
4. **Client and multiplayer acceptance:** No graphical client, saved
   player/reconnect, 2-player handoff, inventory persistence, or companion
   AI movement took place.

**Release disposition:** full-pack dedicated-server boot and Greatbole
construction passed on this seed; the overall playable release remains
pending client and multiplayer gates.
