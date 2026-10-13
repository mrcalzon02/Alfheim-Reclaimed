# Scholastic Quarter - Wave 2

Design authority: `ANCIENT_ELVEN_STRUCTURE_ROSTER.md` sections 6.4, 7.4 and 11.

The Lore College anchors a single nine-member research and teaching precinct.
Its wings are the Archive Cloister and Runic Engineering Hall. The Philosopher
Court leads to an Astral Conservatory; the entry court connects student residence,
botanical research garden and scholars' avenue. Eight supported connections join
the family. The local footprint is 141 by 181 blocks.

Lecture benches survive around emergency planning tables and storage. The archive
combines copying stations with sealed manuscript storage, stripped or burned
stacks and a breached roof with associated debris. Inert test rigs and containment
partitions show engineers attempting repair. The conservatory has calendar marks,
an interrupted observing axis, a northeast dome breach and an accessible upper
gallery. Its stairwell is explicitly cut through the gallery platform. Student
bedding, botanical beds and staff remains show the population behind the college.

The botanical garden's raised grass beds own their support and contain ferns,
grasses and flowers. Its channels are dry. Glass occurs in authored windows,
conservatory rings and freestanding test rigs; custom crystal clusters are not
embedded in walls. All occupied volumes, roof breaches and stair headroom are
explicit air. Each template has eight buried foundation layers and remains within
48 blocks on every axis. Broad terrain generation is unchanged.

The quarter reuses 89 cultural furniture modules, with twelve student beds and
four end rods on inert test rigs. It adds no vanilla lanterns or soul lanterns,
persistent template entities, functional research machines or progression rewards.
Loot contains ordinary paper, books, ink, food, seeds and dye. Fey Stone and
credential systems are neither introduced nor represented by substitute items.

`tools/gen_scholastic_quarter.py` generates 23 shipping files: nine templates,
nine pools, one structure, one placement set, one biome tag and two loot tables.
`tools/check_scholastic_quarter.py` checks source equality, registration, limits,
non-overlap, reach, internal circulation, archives, beds and observation stair
clearance. The controlled test harness is `tools/run_scholastic_quarter_validation.py`.
The saved-world checker verifies all members and connections, every cultural
module, beds, archive shelves, inert rig rods, stairs and all authored air cells.

Acceptance: source checks and controlled saved-world assembly passed.
`server/console-20261012-151403.log` saved all dimensions and exited 0.
All nine members, eight connections, 89 furnishings, archive shelves, student
beds, inert rods and observation stairs matched the save. All
324,738 authored air cells remained air, including stair headroom.
Evidence: `tools/scholastic_quarter_manifest.json`; map: `scholastic_quarter_layout.png`.
Client visual review, natural placement frequency and terrain-fit admission remain
pending. The isolated placement test does not establish those gates.

Next planned family: Production District.
