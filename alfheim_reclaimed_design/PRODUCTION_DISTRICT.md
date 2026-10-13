# Production District - Wave 2

Design authority: `ANCIENT_ELVEN_STRUCTURE_ROSTER.md` sections 6.8, 7.7 and 11.

One freight-yard anchor assembles ten connected sections. Distribution depot and
Resonance Foundry flank the yard; the foundry leads outward to the Glass Bloom
House. The Mana Mill connects to dry waterworks. The Dreamwood shaping court
connects worker housing, a guard post and the freight approach. Nine supported
connections form one walking network. The local footprint is 172 by 180 blocks.

Paired timber gantries, cart staging and work desks explain material movement.
The depot retains partitioned stock bays and a sealed inner reserve. The foundry
has unlit ordinary kilns, work beds, unfinished stone stock and a stripped bay.
Fractured mana channels have an incomplete bypass beside them; the regulator bay
is burned out. Dreamwood curing racks and unfinished timber survive beside the
worker route. Freestanding glass beds, unlit kilns, a breached roof and debris
show the Glass Bloom House's failure. Settling tanks are dry, with blocked outlets.
Workers and guards remain beside their final workplaces and shelter areas.

This is botanical and magical industry, with no added engines or functional mana
production machinery. Ordinary vanilla furnace blocks are unlit and retain their
ordinary behavior. The magical channels and regulators are inert architecture.
The family reuses 32 cultural furniture modules and contains twelve worker beds
plus a guard bed. It adds no vanilla lanterns or soul lanterns and no persistent
template entities. Stock caches contain small quantities of clay, calcite, food
and paper; record caches contain ordinary books, paper and ink. There are no
progression gear rewards, exotic metals, credentials or Fey Stone substitutes.

Every member owns eight buried foundation layers, its interior air and its route
headroom. Individual templates stay within 48 blocks on all axes, and the assembly
stays within adapted jigsaw reach. Glass occurs in authored windows and freestanding
work beds, without custom crystals embedded into walls. The waterworks introduce
no water or lava sources. Broad terrain generation is unchanged. Natural terrain
fit and placement frequency are pending; fixed bedding is not proof of terrain
admission. The Stone-Song Quarry remains a separate planned archetype.

`tools/gen_production_district.py` generates 25 shipping files: ten templates,
ten pools, one structure, one placement set, one biome tag and two loot tables.
`tools/check_production_district.py` verifies source/shipping equality, registration,
piece limits, non-overlap, reach, supported ports, internal circulation, eight
kilns, worker beds and absence of fluid sources. The isolated runtime harness is
`tools/run_production_district_validation.py`. The shared saved-world checker
verifies every member, connection, cultural module, bed, kiln, glass block, channel
and authored air cell.

Acceptance: source checks and controlled saved-world assembly passed.
`server/console-20261012-152612.log` saved all dimensions and the server exited 0.
The initial harness census failed because it counted unrelated natural edge
fragments as duplicate controlled members. The audit now requires each declared
member marker at its exact reconstructed position, plus every geometry/fixture
and air-volume check. Rechecking the same save exited 0: all ten members, nine
connections, 32 cultural modules, workshop fixtures and 333,148
authored air cells passed. A separate natural start at chunk (-92, 56) declares
ten members; only two labeled edge fragments were loaded in this test area.
That metadata is not a full natural-placement or terrain-fit admission.
Evidence: `tools/production_district_manifest.json`; map: `production_district_layout.png`.
Client visual review, terrain-fit and natural placement frequency remain pending.

Next planned family: Agricultural Estate / Food Belt.
