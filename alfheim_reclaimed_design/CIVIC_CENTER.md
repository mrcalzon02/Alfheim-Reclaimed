# Civic Center — Wave 1

Design authority: `ANCIENT_ELVEN_STRUCTURE_ROSTER.md` §§6.1, 7.2 and 11.

The family is one connected civic precinct, with one placement set rather than
independent building placements. The assembly hall anchors the record house and
provincial council house. A public forum leads to a market court; the opposite
service court connects the census hall, public kitchen and processional avenue.
Nine deterministic members meet at eight five-block-wide public connections.

The ceremonial hall has benches, speaker desks, interrupted high roof beams,
side shelter beds and a broken dais barricade. Records survive beside stripped
shelves and burned stacks. The council retains administrative desks, a sealed
office and a guard station. Census desks and ration-kitchen counters show the
government continuing its work during decline. Market stalls and sheltered
public waiting spaces surround the institutions. Civilian, clerk and guard
remains and fallen stone carry the final abandonment into the present ruin.

The local footprint is 141 × 183 blocks. Individual templates remain within
48 × 48 × 48. Eight layers of authored foundation support every member;
occupied volumes, including the broken upper roof, are explicit air. This is
an engineered platform, with visual terrain integration still requiring client
review. Broad terrain density, noise and biome-layer generation is untouched.

The precinct contains 101 existing cultural furniture modules and no vanilla
lanterns or soul lanterns. Furnishings use the registered royal cultural library
as durable ceremonial desks, benches, cabinets and banners. No new models,
credentials or magical capabilities are introduced. Loot consists of mundane
paper, books, ink, food, seeds and wool; there are no progression rewards or
Fey Stone substitutes.

Implementation: `tools/gen_civic_center.py` generates 23 shipping files:
nine templates, nine pools, a structure, a structure set, a biome tag and two
loot tables. `tools/check_civic_center.py` verifies source/shipping equality,
registrations, piece limits, non-overlap, reach, supported sockets, archive
shelves and kitchen fixtures. `tools/run_civic_center_validation.py` creates a
separate disposable test world. The shared saved-assembly checker verifies all
nine members, eight doorways, every cultural module and every authored air cell.

Acceptance: source checks and saved-world runtime assembly passed.
`server/console-20261012-143111.log` saved all dimensions and exited 0.
The save contains all nine sections, eight clear supported connections and all
101 cultural modules. All 288,636 authored air cells remained air.
Evidence: `tools/civic_center_manifest.json`; map: `civic_center_layout.png`. Client visual review,
natural placement frequency and terrain-fit admission remain pending.

Next planned family: Relief / Quarantine District and Mass Grave of the Last Order.
