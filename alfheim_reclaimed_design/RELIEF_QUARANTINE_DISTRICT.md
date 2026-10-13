# Relief / Quarantine District - Wave 1

Design authority: `ANCIENT_ELVEN_STRUCTURE_ROSTER.md` sections 5, 6.6, 7.5 and 11.

One district anchor assembles eleven members rather than scattering independent
medical buildings and graves. The walled triage court connects the hospice and
healer cloister; a marked quarantine checkpoint separates treatment from the
burial ground. The Last Order mass grave branches into ash pits and a digger
shelter. On the public side, a supply court connects the ration hall, depleted
sealed store and cart approach. Ten supported connections form a single walking
network. The local footprint is 141 by 172 blocks.

The clinical court has divided patient lanes, privacy screens and dense ward
bedding. The hospice has a broken eastern roof with associated fallen stone,
burned bedding residue and staff remains. The healer cloister retains preparation
desks, emptied cabinets and a failed dry cleansing basin. The checkpoint shows
records, markers and a final guard station. Ration queues and civilian remains
show public care continuing until it was overwhelmed.

Burial order changes across the Last Order ground. Early marked rows retain
shrouded remains; later crowded trenches are excavated into the authored bedding,
with spoil heaps, open ends and unfinished work. Ash pits, a record desk and the
digger shelter extend the mortuary system beyond a simple collection of bones.
All remains are block-based: there are no persistent template entities. The
quarantine boundary is architectural; no disease gameplay system is introduced.

The family reuses 56 cultural furniture modules. It adds no lanterns or soul
lanterns, new models, credentials or progression rewards. Surviving caches contain
small quantities of ordinary paper, books, ink, food, wool and seeds. Supplies are
deliberately thinner than in the civic or household families.

Each piece has eight authored foundation layers and stays within the 48-block
template limit. Ward interiors, roof breaches and late trenches own their air
explicitly. Main routes remain level and clear, with trenches off the circulation
axes. Broad density, noise and biome-layer generation remains unchanged. Natural
terrain fit, visual presentation and placement frequency still require review.

`tools/gen_relief_district.py` generates 27 shipping files: eleven templates,
eleven pools, one structure, one placement set, one biome tag and two loot tables.
`tools/check_relief_district.py` checks decoded source/shipping equality, block
registration, template limits, non-overlap, reach, socket support, internal walking
connectivity, ward fixtures and open burial trenches. The separate disposable
world harness is `tools/run_relief_district_validation.py`. The shared saved-world
checker checks all members, connections, furniture, beds, bones, skulls, queue
rails and authored air volumes.

Acceptance: source checks and controlled saved-world assembly passed.
`server/console-20261012-144246.log` saved all dimensions and exited 0.
The save contains all eleven members, ten supported connections, all 56 cultural
modules and every declared ward bed, skull, bone block and queue rail. All
283,206 authored air cells remained air, including late trenches.
Evidence: `tools/relief_district_manifest.json`; map: `relief_district_layout.png`.
Client visual and terrain-fit admission remain pending.

This is the fourth Wave 1 family. Next planned family: Wave 2 Scholastic Quarter.
