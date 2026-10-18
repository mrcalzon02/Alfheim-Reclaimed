# Test-run repairs and district rings — 2026-10-17

Minecraft 1.20.1, Forge 47.4.10. These changes are installed in the local instance.

## District placement

The user's revised placement is concentric rings at 1,000, 2,000, 3,000 blocks and
onward around the fixed Greatbole starting hub at X=0, Z=0. Four deterministic
candidate sites occupy each ring; successive rings turn 45 degrees. Chunk
alignment moves a candidate by at most approximately 12 blocks from its nominal
radius. Each site selects one of the nine enabled district families. Biome, harbor,
hub, moved-spawn and castle checks can reject unsuitable candidates. Sacred,
Military/Warden and Frontier remain unadmitted prototypes.

The former 6,000-block origin and 4,096-block spawn exclusions are superseded.
District-to-district spacing retains at least 500 blocks between conservative
256-block-radius footprints. The existing hub claim fits within radius 152;
the new 908-block hub reservation therefore leaves 500 blocks. All three natural
castle candidates receive a conservative 960-block reservation, covering its
167-block radius, the district footprint and 500-block clearance. Upper-rock
discoveries now reserve the ring nodes rather than the obsolete district grid.
This is a scoped district/hub/castle spacing proof; unrelated third-party surface
placement is not globally admitted by it.

The native placement extends the vanilla random-spread locator interface while
admitting only exact ring nodes. Nine structure sets use the registered
`alfheim_companion:district_rings` placement. Existing templates, loot, furnishings
and terrain definitions are unchanged. `tools/district_policy.py` preserves this
placement when the district generators run again.

Search all enabled families with:

```mcfunction
/execute in mythicbotany:alfheim run locate structure #alfheim:districts
```

This changes new generation. Already generated chunks in player saves are not
rebuilt. A fresh test world is the reliable way to inspect the inner rings.

## Crown and creature display textures

The reported client log contains 439 distinct missing companion textures: 390
themed creature skins, 48 citizen wardrobe skins and the Crown palette. Their
item models reference `entity/` or `models/armor/`, which the default block/item
atlas does not scan. An additive atlas definition now explicitly includes those
439 textures. It does not load every installed mod's entity textures. The native
entity and armor texture paths and all texture images remain intact.

`tools/check_display_atlas.py --write` refreshes the list after model generation;
`--jar` checks the installed artifact. The original installed companion jar is
preserved in `quarantine/alfheim_companion-before-test-run-fixes-20261017.jar`.

## JourneyMap tree colors

Emberbark, Gloambark and Hushbark logs, leaves and saplings now have explicit map
colors sampled from their visible texture pixels. Transparent leaf holes do not
darken the averages. The generator owns these changes, and the native audit checks
that all nine registered blocks have a map color other than `MapColor.NONE`.
Existing JourneyMap cache files and player saves were not changed.

## Validation and evidence

The final build passes 72 Java tests, including ring geometry across 51 seeds and
100 rings per seed. Natural saved-block checks pass 28 pieces: Production at
X=128, Z=-992 (radius 1,000.22), Civic Center at X=-1584, Z=1232 (radius 2,006.71),
and Scholastic Quarter at X=368, Z=-2976 (radius 2,998.67). All 495 real creature
selections pass spawning and saved-appearance checks: 390 themed enemies, 48
citizens and 57 monstrosity appearances across 19 species. All nine grove map
colors pass in the actual registry. Feature ordering has zero cycles.

`tools/test_run_fixes_build.json` records the final jar, backup hashes and static
checks. `tools/district_ring_runtime_report.json` records the disposable world,
native candidate audit, actual egg spawns, persisted appearances and placed-block
census. The runtime tool is `tools/run_district_ring_validation.py`, using the
existing Forge server harness and seed **-5876049240305171930**, read without
modifying the newest test save, **New World raven**. No `/place structure` command
is used. Joined templates deliberately share cells; the census checks each
piece's remaining owned solid cells after later joined pieces take precedence.

The preliminary old-grid probe and its daylight monstrosity-test failure remain
in `tools/test_run_runtime_report.json`; they do not describe final ring acceptance.
The older manifest checker still reports incomplete historical family metadata,
and the production/relief source checkers encounter obsolete exported block
registries that omit later Leyworks furnishings. These are separate from the
current native registration and ring-placement tests.

Full client restart is required for the rebuilt mod and startup block colors.
Client inventory, worn Crown and JourneyMap visual acceptance remains pending;
previously cached black map tiles may require remapping. This is a bounded
one-seed runtime test, not production admission of every biome, terrain fit or
unrelated structure overlap. No new structure geometry was generated with
Continuity Works; the existing generated district corpus is reused.
