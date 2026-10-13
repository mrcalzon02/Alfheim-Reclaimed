# Roads / Trade Support Precinct - Wave 2

Design authority: `ANCIENT_ELVEN_STRUCTURE_ROSTER.md` sections 6.10 and 11.

One caravan-court anchor assembles ten related transport and shelter sections.
The processional avenue leads to a bridge gate. Freight exchange and customs
house flank the court; a bonded store continues beyond customs. The road checkpoint
connects a wayshrine/rest station, refugee lodge and road approach. Nine supported
connections form one walking network. The local footprint is 172 by 180 blocks.

Caravan gantries, stranded carts and inspection desks explain normal transport.
Customs counters, depleted confiscated stores and bonded partitions retain the
administrative system. A damaged freight roof, fallen stone and broken handling
frames show salvage and abandonment. Emergency checkpoint walls preserve a
central passage. Refugee beds, roadside burials and memorial markers show travel
turning into attempted evacuation and shelter. All remains are decorative blocks,
without persistent template entities or fabricated movement-permit items.

The bridge spans a dry channel wholly contained inside its authored template.
Its nine-block-wide surviving deck has supported edge rails and four piers down
to the channel bed. Ruined outer spans leave the central route usable. Tests
require the route to reach the far bank, every deck/pier block and all guardrails.
This is an architectural crossing, not a terrain-aware river bridge or a road
network connecting independently generated settlements. Those remain separate
placement/design work. No broad terrain file is changed.

The precinct reuses 47 cultural furniture modules and has sixteen travel/refuge
beds. It adds no vanilla lanterns or soul lanterns, progression gear, powered
machinery or exotic-metal rewards. Caches hold ordinary food, wool, clay and
records. Individual templates stay within 48 blocks on every axis and own eight
buried foundation layers and their occupied air. The dry cut leaves a solid bed
and does not open a drop into the void. Authored bedding is not proof of natural
terrain integration.

`tools/gen_roads_trade.py` generates 25 shipping files: ten templates, ten pools,
one structure, one placement set, one biome tag and two loot tables.
`tools/check_roads_trade.py` verifies source/shipping equality, registration,
bounds, non-overlap, reach, connected circulation, beds, supported guardrails,
bridge clearance and piers. The isolated harness is `tools/run_roads_trade_validation.py`.
The shared saved-world checker verifies each reconstructed member marker,
connections, cultural furnishings, beds, remains, deck, piers, guardrails and
all authored air cells.

Acceptance: source checks and controlled saved-world assembly passed.
`server/console-20261012-163523.log` saved all dimensions; server and harness exited 0.
All ten members, nine connections, 47 cultural modules, beds, remains, bridge
deck, piers and rails matched the save. All 324,657 authored air cells
remained air, including bridge channel and passage headroom.
Evidence: `tools/roads_trade_manifest.json`; map: `roads_trade_layout.png`.
Client visual review, natural placement frequency and terrain-fit admission remain
pending. These transport pieces conclude the planned Wave 2 family sequence at
the controlled-assembly stage; no production admission is implied.

Next planned family: Wave 3 Harbor Complex.
