# Agricultural Estate / Food Belt - Wave 2

Design authority: `ANCIENT_ELVEN_STRUCTURE_ROSTER.md` sections 6.9, 7.8 and 11.

The Water Garden anchors ten connected food-production and keeper sections.
The terraced orchard continues into survival vegetable terraces. The root granary
leads to a seed vault; the fungus conservatory occupies the other principal wing.
A harvest court connects keeper housing, pollinator sanctuary and farm approach.
Nine supported connections form one walking network. The local footprint is
172 by 180 blocks.

Four bounded irrigation basins retain water around silted clay filter columns.
Every basin has a solid floor, sealed sides and walls above water level; glass
marks closed junctions rather than allowing an uncontrolled outlet. Orchard beds
step upward behind authored retaining walls, with four native Dreamwood trees.
Emergency wheat and carrot beds reuse matching ornamental terraces. A broken
outer retaining wall and adjacent debris show one source of structural failure.
Terrace stairs have solid supports and clear headroom.

The granary has emptied bins, stripped bays and a sealed reserve. Seed cabinets
survive beside evidence of late withdrawals. The conservatory contains four
supported mycelium beds, with both vanilla mushrooms and all six colored Feywild
varieties. Broken upper framing and a staff bed show cultivation overtaking its
managed space. Flower beds, four empty beehives and a keeper station form the
pollinator sanctuary. Keeper housing contains twelve beds; the conservatory adds
one staff bed. Remains mark the final work and shelter areas without persistent
template entities.

The estate reuses 41 cultural furniture modules. It adds no vanilla lanterns or
soul lanterns, powered machinery, progression gear, exotic metals or credential
substitutes. Ordinary seed and food caches support discovery without granting
magical unlocks. Each template owns eight buried foundation layers, its occupied
air and all soil/crop supports, and stays within 48 blocks on every axis. The
planted terraces are structure geometry; broad terrain generation is unchanged.

`tools/gen_agricultural_estate.py` generates 25 shipping files: ten templates,
ten pools, a structure, a placement set, a biome tag and two loot tables.
`tools/check_agricultural_estate.py` verifies source/shipping equality, registration,
piece limits, non-overlap, reach, internal circulation, terrace stairs, basin
containment, beds, hives and eight fungus varieties. The isolated live harness is
`tools/run_agricultural_estate_validation.py`.

For the saved geometry census, random growth is paused in the disposable test
world. Fluid ticks remain enabled, allowing leaks to fail the authored-air check.
Crop growth, irrigation yield and pollination behavior are separate pending
gameplay checks; empty hives do not establish a bee population. The shared saved
checker verifies every member, connection, furnishing, bed, water cell, crop,
soil support, tree foliage, mushroom and authored air cell.

Acceptance: source checks and controlled saved-world assembly passed.
`server/console-20261012-162742.log` saved all dimensions and exited 0; the harness
and saved census also exited 0. All ten members, nine connections, 41 cultural
modules, beds, planted features, supports and water cells matched the save. All
312,717 authored air cells remained air, with no irrigation leakage.
Random growth was paused; fluid ticks remained enabled.
Evidence: `tools/agricultural_estate_manifest.json`; map: `agricultural_estate_layout.png`.
Client visual review, natural placement frequency and terrain-fit admission remain
pending. Authored foundation thickness is not proof of terrain integration.

Next planned work: Roads / Trade support pieces.
