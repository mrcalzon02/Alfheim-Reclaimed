# Functional objects in district rooms

The utility furnishings now appear in **55 existing templates across all twelve
district families**: 109 objects total, at most two per template. All eleven object
types are used. The other 54 templates retain their prior furnishing layout.
This pass edits template interiors, not district placement, rarity, terrain or
independent structure reservations. The 500-block independent-structure contract
does not create a separation requirement between a district room and its own desk.

| District family | Furnished templates | Main room fittings |
|---|---:|---|
| Agriculture | 4 | Seed cabinets, workdesks |
| Civic | 5 | Service counters, archive cabinets |
| Residential | 5 | Provision hutches, weaving frames |
| Elder lineage | 1 | Archive cabinets, weaving frames |
| Frontier | 3 | Cartography tables, provision hutches |
| Harbor | 6 | Service counters, cartography tables |
| Military | 4 | Armory lockers, mending benches |
| Production | 6 | Mason's benches, workdesks |
| Relief | 6 | Apothecary cabinets, provision hutches |
| Roads and trade | 6 | Service counters, cartography tables |
| Sacred | 4 | Archive cabinets, weaving frames |
| Scholastic | 5 | Archive cabinets, workdesks |

## What is preserved

All 310 original block-entity records across the 109 source templates remain
unchanged, including unopened loot and jigsaw metadata. A newly placed fixed
container starts empty. It does not replace a loot barrel or acquire a guaranteed
progression reward. Existing crafting tables and other original utility fixtures
are retained, so a specialized new station cannot remove an existing crafting route.

These are ordinary storage and vanilla workstation conveniences. Salvaging one
does not refund the crafted object's resin/lattice ingredients or produce tier
materials, runes or magical power.

Every new object occupies an existing explicit air cell. The template's size,
cell ownership, entities, terrain foundations, floors, walls, stairs and ceilings
remain unchanged. No air cell outside the existing template footprint is claimed.
Previously generated player rooms are not rewritten.

## Bounded placement contract

`tools/district_furnishing_placement.py` makes deterministic choices from each
authored room, rather than searching a live world. An eligible spot has a full
floor, two perpendicular backing walls, overhead cover, and a clear two-wide,
two-deep approach. Candidate cells near jigsaws, block entities, beds, ladders and
stairs are excluded. Nearby wall blocks are excluded to avoid changing wall joins.
Furnishings on one level are separated by at least seven cells of Manhattan
distance. At most two objects are placed in each template.

The supported two-high walking graph is built from the original template. Removing
the occupied furniture cells must leave every remaining node of every original
component connected. This is a conservative cell graph, not a simulation of every
Minecraft movement edge or furniture hitbox. The models themselves remain inside
their cell and use the already validated native collision and menu behavior.

## Source and Continuity Works

The shared district detail hook applies the same furnishing mutator in normal
generation. `ALFHEIM_DISTRICT_FURNISHINGS=0` produces an unfurnished architectural
baseline without disabling the earlier eight architectural detail layers.

`tools/cw_furnish_districts.py` invokes the installed Continuity Works
`StructureCapability.generate` adapter for all twelve families. Only emitted,
exact-ID-probed NBT is promoted. Baselines are checked against shipping cells before
promotion; reuse of local baselines still requires this comparison. Registry
evidence comes from the previous real-game eleven-object interaction/reload audit,
with the installed Leyworks jar hash checked before authoring.

The older eightfold architectural audit first runs the furnishing audit, then
normalizes only the new furniture cells to their original air for its original
architectural metrics. This keeps room furnishing separate from masonry detail
counts while preserving the original gate. The old refit generator uses the same
normalization and verified registry IDs for future regeneration.

## Evidence

- `tools/district_furnishing_placement_report.json`: twelve actual Continuity Works
  snapshots, exact block-ID probes, all 109 placement coordinates and template hashes.
- `tools/district_furnishing_placement_static_report.json`: every shipping template
  reproduced from baseline plus the deterministic mutator; all other cells and
  original block entities unchanged; connected routes and full eleven-role coverage.
- The common-residential source generator was independently rerun; every emitted
  template matches the shipping NBT, including the new furnishings.
- `tools/run_furnished_district_validation.py`: disposable-world materialization of
  all 55 changed templates, checking saved facing, empty storage block entities and
  retained unopened loot IDs/tables. Vanilla StructureTemplate assigns a random
  loot seed during placement; the verifier records those assigned seeds separately
  rather than confusing them with a change to the original template NBT. Results are in
  `tools/furnished_district_runtime_report.json`.

Final gallery: `server/console-20261015-221145.log`, isolated world
`validation-furnished-districts-20261015`: 55/55 templates, 60 correctly facing empty
storage inventories, 49 correctly facing workstations, and 55 retained unopened
loot records pass. The source and server-mirror template hashes match. The earlier
native Leyworks interaction/reload jar remains unchanged.

The template gallery does not re-prove natural district site selection or old/new
chunk boundaries. Client presentation and live exploration remain play-review
tasks. New furnishing layouts appear when updated templates generate in new chunks;
restart the game to refresh loaded structure templates.
