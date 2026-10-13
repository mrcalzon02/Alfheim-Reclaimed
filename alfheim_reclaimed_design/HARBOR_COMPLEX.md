# Harbor Complex Prototype - Wave 3

Design authority: `ANCIENT_ELVEN_STRUCTURE_ROSTER.md` sections 6.11, 7.6 and 11.

The maritime prototype links ten sections around a Harbor Exchange Hall.
Harbormaster House and bonded warehouse flank the exchange; the warehouse leads
to a Tide Temple. Wavebreak pier and partially inundated drydock extend seaward
in the authored layout. A quay court connects the signal lighthouse, dockworker
housing and harbor approach. Nine supported connections form one walking network.
The local footprint is 172 by 180 blocks.

Inspection desks, bonded stock and ship-record cabinets show the original port.
The exchange's broken roof and stranded cargo show trade ending; side storage
areas, the drydock and temple undercroft retain contained shallow inundation.
Pier protection has a broken outer segment. Hull fragments remain beside a dry
maintenance causeway. The temple has shelter bedding, and worker homes show the
last dock population. The lighthouse has keeper quarters, a supported twelve-step
stair to its signal gallery and a single surviving ceremonial brazier beneath a
broken upper crown. Existing furniture supplies 72 cultural modules; no persistent
template entities or new custom models are added.

Flooded areas occupy two bounded subfloor basins per affected member. Their floors
and sides remain solid, water stays below the primary walking level and side rails
protect the openings. Routes and stairs retain explicit air. All templates stay
within 48 blocks per axis, including foundation bedding. Broad terrain is unchanged.
No natural shoreline fit or waterline alignment is established by this geometry.

Natural placement is deliberately withheld: the generator emits no structure set.
The structure and pools are available for command placement and review. The biome
tag lists Tidewood, Mistbark and Sporebank shores, but a shore biome alone cannot
guarantee a usable coast. The dedicated shoreline guard is now implemented and validated on a synthetic
coast. It checks every footprint column in four orientations, ground support,
waterline, seabed depth and relief, rejecting unsafe sites without terrain
adjustment. Natural placement still awaits a real generated coast, performance
and visual admission. See `HARBOR_PLACEMENT_GUARD.md`. Void Shore is not an eligible prototype shore.

Loot is ordinary paper, books, ink, food, wool and clay. No progression gear,
exotic-metal rewards, credentials or Fey Stone substitutes are introduced. The
prototype adds no vanilla lanterns or soul lanterns. Its contained water represents
authored decline, not a functioning ocean connection.

`tools/gen_harbor_complex.py` generates 45 shipping files: ten architecture templates, twenty-one
optional foundation templates, ten pools, a structure, a biome tag and two loot
tables. `tools/check_harbor_complex.py` checks
source/shipping equality, registration, bounds, non-overlap, reach, internal routes,
lighthouse stair supports/headroom, basin floors/walls and the absence of a natural
placement set. The isolated live harness is `tools/run_harbor_complex_validation.py`.
The saved checker verifies all members, joins, furniture, bedding, stairs, water,
glass, rails and every authored air cell, with fluid ticks running.

Acceptance: revised source checks and controlled saved-world assembly passed.
The initial save comparison was invalidated by furniture revisions. Tide-temple
monuments/benches and exchange benches/cabinet were moved onto supported dry floor,
and a non-floating furniture gate was added. A fresh revised test passed all ten
members, nine connections, 72 cultural modules, stairs, rails, beds and water.
All 345,003 authored air cells remained air with fluid ticks running.
`server/console-20261012-175714.log` saved all dimensions; server and harness exited 0.
Evidence: `tools/harbor_complex_manifest.json`; map: `harbor_complex_layout.png`.
Client visual review, real-coast acceptance and terrain-fit admission remain pending.

Next harbor work: repair layout/foundation fit on real coasts, then native placement, performance and visual tests.
Next roster family after harbor development: Sacred precincts.

Real-coast validation did not find a safe fit for the current flat footprint.
The shore-apron rule was corrected, but four eligible Mistbark rechecks still
rejected it. See `HARBOR_REAL_COAST_VALIDATION.md`; natural generation stays held.

The 2026-10-13 adaptation adds selectable quay heights and matched physical
foundations. A raised-bank assembly passed, while two native island tips remain
rejected for lacking the required landward connection. See `HARBOR_ADAPTIVE_QUAY.md`.
