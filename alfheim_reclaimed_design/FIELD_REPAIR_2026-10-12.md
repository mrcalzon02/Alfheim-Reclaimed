# Field repair and structure development — 2026-10-12

Player evidence: the three screenshots preserved under
`screenshots/field-review-2026-10-12/`; read-only inspection of `saves/New World beta`.
Seed: `3536368297089363045`. No player region files or player NBT were edited.

## Scope and results

| Finding | Cause and repair |
|---|---|
| Grave-door reverse-side Z fighting; similar custom models | Overlaid cuboids draw coincident faces. `model_geometry.py` clips hidden and overlapping face areas while preserving texture coordinates. Applied to funerary, sculptural, royal, exotic-home and functional-container generators. Transparent shells retain their visible contents. All 103 checked custom cuboid models have zero coincident face overlaps; the original KubeJS models contained 291 pairs. Collision bounds and registrations remain as authored. |
| Excessive ley-line lanterns | Both channel collars and the generic sconce pass supplied lights. Collar lamps now occur every 16 blocks; additional lights have spacing and hard budgets. A long straight falls from 26 lamps to 6; the hub from 8 to 2. |
| Walls appearing as separate posts | Templates stored default wall states without connected arms. `Piece.to_nbt()` now bakes local north/south/east/west connections and the central post state. The exact connected-rail state passed a game placement probe. |
| Excessive tomb soul lanterns | The generic dressing pass filled a light lattice repeatedly across floors. Tomb lighting now has wider spacing and a maximum of 12 additional sconces per piece. Final centre/approach/wing/gallery counts: 12/4/11/12, down from 69/11/26/86. Across the thirteen-piece tomb: **561 to 120 soul lanterns**. |
| Memorial carvings inset into masonry | Registration bands replaced wall blocks with shallow relief models. Bands now retain their masonry backing and mount carvings in adjacent empty interior cells, with inward orientation. Backing is checked in every tomb role. |
| Terrain filling the rotunda's upper interior | Corbel courses only wrote their boundary rings; unspecified cells retain native terrain. The crown now explicitly owns its air volume and closes the final cross-section with a continuous roof. A runtime probe verified the upper air volume and roof. |
| Crystal clusters buried in walls or floors | The shared detail pass replaced supporting masonry with the cluster itself. Wall sockets now mount outside the backing, and floor-channel nodes stand above a retained channel block. Tomb machinery dressing was removed from the funerary rooms. Affected structure templates were regenerated. |
| Brown-mushroom monoculture | Ground-bed vegetation defaulted to brown mushrooms, and scatter excluded mycelium. Both now support the two vanilla and six Feywild mushrooms. A controlled mycelium-bed placement produced all eight kinds. |
| Insufficient trees | Doubled custom-grove attempts and wooded-shore canopy attempts, and halved the rarity gates of the six modded tree accents. Source survival filters remain intact. Giant-tree placement remains unchanged. |
| Golden Fields dirt paths/coarse dirt underground | A floor-only surface rule also matched cave floors. Golden Fields now paints ordinary grass and shallow dirt only above the preliminary surface. Worked soil is confined to bounded raised-field structures. The terrain-density terrace term was deliberately preserved. |
| Spawn over the void | Removed the random/airborne delivery path. A supported provisional platform is prepared before any delivery, and the landing floor/headroom are ensured before teleportation. New hub assembly uses a bounded height when the sampled origin is unsuitable. |
| Spawn structures without ground support | Added stepped stone underfill beneath the Greatbole and court footprints, replacing only air and fluids. Existing hubs receive a one-time, delayed, bounded-retry underfill upgrade using the baked anchor; buildings are not moved. The old-hub upgrade passed a restart test. |
| Mistbark Shore lacks dense fog | Added a client-only Forge fog handler: approximately 4–56 blocks at full strength, with a gradual transition across the biome boundary. Underwater/status-effect fog is retained when shorter. The rebuilt companion mod contains the handler; interactive client rendering remains unverified. |

## New structures

- **Golden Field Dais** — a circular, raised stone plinth with divided wheat beds,
  worked-soil paths and four stair approaches. Only Golden Fields; 10/5 placement grid.
- **Thorn Gate** — a ruined procession of arches, low connected walls and bramble,
  available on the Void Verge and Void Shore.
- **Shore Memorial Court** — a low ring, eight memorial stones and a central urn,
  available on the Void Verge and Void Shore. The two void courts share a 12/6 grid.

Generator: `tools/gen_field_review_features.py`. Each template is under the 48-block
editing limit. Single-piece jigsaw structures use `size: 1`, matching the pack's
established surface structures; their pools contain no expansion sockets.

## Terrain protection and paired soil check

All **39** density-function, noise, noise-setting and biome-layer files remain
byte-identical to the starting snapshot. Baseline:
`tools/field_review_terrain_baseline.json`; guard: `tools/check_field_review.py`.
No broad terrain, climate partition, aquifer or void-density repair was changed.

At sample centre **X -1443, Z 654**, 25 same-seed chunks were inspected below Y=64:

| Material | Player world before | Fresh test generation after |
|---|---:|---:|
| Dirt path | 670 | 0 |
| Coarse dirt | 591 | 0 |

Evidence: `tools/field_review_soil_validation.json`. This comparison was recorded
before manually placing the raised field at that location.

Controlled mushroom counts: brown 4, red 7, purple 12, blue 7, pink 6,
orange 5, yellow 5, green 6. This proves all eight blocks can place on the
mycelium bed; it is not a whole-biome distribution survey.
Evidence: `tools/field_review_mushroom_validation.json`.

## Verification and acceptance boundary

- Both first-party mod builds passed with their wrappers and Java 17. Installed
  Leyworks block models match source resources; the companion jar contains the fog handler.
- Funerary, sculpture, both royal waves, exotic-home and functional-container outputs
  match their generators. Archaeology and ley-line NBT match decoded source output.
- Spawn hub, archaeology, surface works, pixie settlements, funerary and container
  checks passed. Worldgen and biome feature ordering passed with zero problems/cycles.
- Fresh world `validation-field-review-bounded-20261012`:
  `server/console-20261012-122258.log` — all eight landing/foundation/crown/rail/template
  probes passed, the screenshot area generated, all dimensions saved, exit 0.
- Restart and vegetation check: `server/console-20261012-123153.log` — existing-hub
  underfill upgrade passed, eight mushroom varieties placed, save/shutdown exit 0.
  The new-field world-placement probe failed in this attempt and was repaired next.
- Final biome/heightmap structure placement:
  `server/console-20261012-123847.log` — Golden Field Dais, Thorn Gate and Shore Memorial
  Court all generated through `/place structure`, all three probes passed,
  all dimensions saved, exit 0.

The first broad `/locate` attempt stalled while sampling density for candidates;
the zero-depth setting of the new structures did not yield a usable start. Only the
development test process was stopped. The rejected attempt is preserved as
`server/console-20261012-121424.log`; thread evidence is in
`quarantine/field-review-20261012/locate-thread.txt`. No terrain formula was changed
to work around the search. Normal placement was subsequently verified with the
corrected one-piece setting and bounded generation.

Acceptance: **structure/spawn repairs runtime validated**, paired Golden Fields
generation validated, model geometry and fog build validated. **Client visual
acceptance remains outstanding**, including shaders and perceived fog density.
Other pre-existing third-party asset/integration warnings remain outside this pass.

Model changes affect existing blocks after restarting the client. Rebuilt structure
layouts, lamp counts, mushroom/tree placement and corrected cave painting apply
to newly generated chunks or a fresh world. The existing-hub underfill upgrade
runs once on load; existing tombs and cave material are not overwritten.

## Backups

Previous installed companion and Leyworks jars, representative original tomb/ley-line
templates, and the original terrain hash snapshot are preserved under
`quarantine/field-review-20261012/`. The development server's pre-test properties
were restored after every run. Player worlds were inspected only.
