# Instance repair — 2026-10-12

## Diagnosed faults and repairs

- The latest client log (September 30) ends in Library of Exile's expedition
  startup wipe. The October 1 config repair remains installed and was rechecked:
  all 18 applicable defaults and existing-world configs disable
  `WIPE_DIMENSION_ON_LOAD`. No player worlds were loaded or changed in this repair.
- The companion sigil texture reference used `minecraft:item:amethyst_shard`,
  which is an invalid resource location. Corrected the source to
  `minecraft:item/amethyst_shard`, rebuilt with the project's Gradle wrapper and
  Java 17 (`build` passed), and installed the rebuilt jar. Both companion models'
  resource references and the installed sigil resource were checked.
- Iron's Spellbooks 3.16.3 ships two loot tables using fields incompatible with
  this Minecraft 1.20.1 runtime. `citadel_tomes` uses the unsupported
  `set_written_book_pages`; `crypt_loot` uses `value` instead of `name` for a
  loot-table reference. Added KubeJS data overrides preserving the pools,
  probabilities, items and translated lore pages. Book pages now use `set_nbt`
  with the title and author required by written books. The third-party jar is
  untouched. `tools/repair_spellbook_loot.py` reproduces these overrides;
  running it twice produces identical files.

## Validation

- Feature ordering: 313 loaded biomes, zero cycles with biome modifiers applied.
- Worldgen checks: zero problems.
- Fresh dedicated test world: `validation-repair-fixed-20261012`.
  Console: `server/console-20261012-105230.log`.
- Startup completed: `Done (17.358s)`; 22/22 startup scripts and 26/26 server
  scripts loaded with zero errors and warnings. Hub reported `created`.
- Both repaired loot tables loaded with no parsing failures. Explicit loot
  commands produced one Citadel Tome and 13 crypt items.
- All three fresh-world expedition configs inherited the disabled wipe setting.
- Additional Alfheim terrain was requested through a 64-chunk forceload area.
  Save and shutdown completed with all dimensions saved and process exit 0.
  The development server's prior properties were restored after the test.

The first sandboxed test could not establish Java's local loopback connection
and was excluded from runtime acceptance. Its failed test-server process was
identified and stopped before retrying with the required access.

Client rendering and an interactive client world-load have not been verified.
Existing third-party asset paths, optional integration mixins, update-check
failures, loot-modifier warnings and structure hanging-entity warnings remain;
they did not prevent the dedicated test from starting. A headless server does
not exercise client-only mods.

## Backup

Original companion jar: `quarantine/repair-20261012/alfheim_companion-0.2.0.jar`.
SHA256: `cd11b90c19bd8884c1eabbf68d84ffaa9db5c7e1817be429a60f1bf8bdfbbcd8`.
Rebuilt jar SHA256:
`609964196869f19febe13447299be6e5c5377f6cacb8174965cb1ecffe8a28b6`.
