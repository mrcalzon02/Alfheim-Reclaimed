# World creation stall — 2026-10-01

## Evidence and diagnosis

The September 30 client log starts the integrated server at 22:18:09 and ends
at 22:19:03 in Library of Exile's `WipeDimensionFeature`, wiping the Harvest
folder in **New World burnshire**, although the world being created was
**New World blober**. Spawn preparation never appears. The launcher records
`code=0, terminatedByApp=false`; there is no new crash report or fatal exception.
The user confirmed they closed the client after it froze for over a minute.

Read-only inspection of Library of Exile 2.1.11's bytecode confirms that
`OnStartResetMap` recursively enumerates **FMLPaths.GAMEDIR**, then deletes every
directory whose suffix matches the expedition dimension. This includes other
saves and the development server tree. It runs synchronously during startup,
once per enabled map dimension. A config boolean gates the entire operation.
The last client log establishes at least 54 seconds before the first wipe;
it does not prove a feature-order cycle or chunk-generator exception.

## Repair

Set `WIPE_DIMENSION_ON_LOAD = false` in the Forge defaults for Harvest, Ancient
Obelisks and Dungeon Realm. `tools/repair_expedition_boot.py` also changes the
same setting in existing client saves, preserving all other parsed settings
and retaining a `.boot-repair.bak` alongside each changed config. Run it with
Minecraft closed. New worlds inherit the defaults; existing worlds do not
automatically inherit Forge defaults.

This disables automatic expedition-folder deletion on startup. Normal in-game
instance cleanup remains enabled. Expedition folders persist across restarts;
if a map needs a reset, use that mod's maintenance workflow deliberately.
No jars, terrain rules, dimensions, or saved map data are patched or deleted
by this repair.

## Verification

- Feature ordering: 313 loaded biomes, **0 cycles**.
- Worldgen reference/schema/material checks: **0 problems**.
- Baseline fresh dedicated world `validation-boot-repair-20261001`: generation
  completed, hub pieces and ownership probes succeeded, all dimensions saved,
  process exit 0. Console: `server/console-20261001-114450.log`.
- The first sandboxed attempt failed Minecraft's save-path access check and is
  excluded from runtime acceptance; the baseline ran with approved access.
- Repaired fresh dedicated world `validation-boot-fixed-20261001`: all three
  generated server configs read back `false`; no startup wipe or sweep warning;
  spawn preparation completed (`Done (16.771s)`), all eight placement scores
  were 1, all 5 ownership probes passed, all dimensions saved and exit 0.
  Console: `server/console-20261001-114756.log`. This timing is the server's
  preparation measurement, not a promise about total client launch time.
- Re-running the repair is idempotent. All 15 existing configs have backups;
  parsed before/after comparison confirms only the wipe boolean changed.

Dedicated-server verification covers generation, scripts, hub assembly and
saving. It does not cover the client renderer or an interactive client retry.
Existing unrelated asset/loot warnings remain outside this fix.
