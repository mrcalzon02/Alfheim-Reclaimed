# Structure terrain affordances — 2026-10-18

**Final activation state:** the general ground adapter below is staged and
inactive pending acceptance. The castle fix/apron, complete policy catalogue
and native Void host checks are active. See `CASTLE_TERRAIN_HANDOFF_20261018.md`.

User requirement: structures should belong to their terrain, normally resting on
a foundation plate with at least a one-block border. Bearding/feathering means
terrain blending; it does not by itself guarantee a footing or a traversable door.

## Scope and implementation

`tools/gen_terrain_affordances.py` inventories all 89 active Alfheim structure
registrations and emits a separate, explicit contract for each. Generated
contracts live in `kubejs/data/alfheim/terrain_affordances/`, with a complete
reviewable census in `tools/terrain_affordance_manifest.json`. A missing or
unclassified new family fails validation. Dormant designs and future monastery
families must satisfy this same standard before becoming active registrations.

The 36 ordinary ground-based registrations use a native saved foundation adapter
around their existing jigsaw members. Its default is a one-block perimeter edge,
two further blocks of descending soil transition, no more than 16 blocks of
underfill and no more than six blocks of uphill burial in the sampled envelope.
Nine noise-height probes per member, capped at 256 unique probes per assembly,
reject gross cliffs, open Void, overly deep foundations and disallowed water.
These are bounded sample checks, not an exhaustive terrain scan.

Each foundation piece is serialized with its actual member bounds, floor level,
material, edge, feather and depth. It fills missing contact before the original
templates are placed; original rooms, floors, irrigation, doors and jigsaw joins
remain authoritative. Writes stay in the current generation chunk. The adapter
stops at existing solid blocks and block entities, preserves buried ore/stone,
and does not edit existing worlds. Soil feathering never dams existing water.
The complete apron/transition envelope is included in district/hub/castle bounds.

## Distinct terrain forms

| Form | Terrain rule |
|---|---|
| Ordinary building/district | Supported plate, >=1-block edge, shallow soil feather; bounded relief and depth |
| Royal castle | Existing deep native foundation plus a one-block perimeter apron; lowered gate apron preserves the four original ramps |
| Harbor | Existing authored quay footers and wet/dry waterline checks; channels and drydock remain open |
| Bridge/span | Preserve open span and authored standing abutment; no solid rectangular fill below the crossing |
| Crater/quarry | Preserve authored bowl, benches and natural rim; no foundation that fills the excavation |
| Waterwork/wreck | Preserve intended waterline/seabed and open water; no manufactured dry island |
| Burial/underground | Preserve authored rooms, host cover, floor boundary and specialized native checks |
| Void ruin | All twelve now use `alfheim_companion:void_surface`: 7/9 or 8/9 solid host probes, bounded relief, 5- or 9-block backing; no rescue terrain |
| Greatbole | Existing authored root flare and Hollow Court foundation, rather than a rectangular tree platform |
| Floating island | Preserve authored floating shape and native terrain/neighbor clearance; no pillar to the ground |
| Mountain Worldstone | Existing native competent-host, roof-cover, floor and cavern-envelope checks |

Special-form classification preserves geometry and records its governing rule;
it does not claim that every specialized family's terrain predicate has newly
passed an exhaustive runtime survey. Client appearance and broader per-family
sampling remain separate acceptance gates.

## Castle spawn repair

On seed `-5876049240305171930` (New World raven), the old candidates were:

* (928, 2032): Hollow Marches, highest sample Y286; rejected.
* (-2112, -288): Hills, 129 blocks of relief; rejected.
* (1312, -1840): Tidewood Shore, sampled heights 40..69; acceptable support,
  but formerly excluded by the biome whitelist.

The supported coastal biome is now allowed. A separate preferred-biome tag keeps
the old five preference biomes unchanged, preserving the exact three reserved
ring candidates and their priorities. No candidate relocation or extra castle
rolls were introduced. The first suitable site still wins; this does not promise
a viable castle on every possible world seed.

An initial fresh-world natural test placed the full 235x235 castle at
(1312, Y78, -1840), with all 25 template members, nine foundation probes and 5,029
matching sampled blocks. Neither player save was edited. That candidate's start
chunk was absent from New World raven when inspected, so it remains eligible
for new generation after restarting the client. An already generated start
would require a separately reviewed migration; simply updating does not retrofit it.

## Repeatable gates

* `tools/check_terrain_affordances.py`: exact policy coverage and active native types.
* `tools/check_void_surface_support.py --complete`: all twelve sanctioned Void families.
* `alfheim_terrain_audit`: actual loaded registry versus terrain contracts and adapter coverage.
* `alfheim_castle_audit`: all three real ring candidates, terrain heights and biome acceptance.
* `tools/run_castle_natural_validation.py`: disposable natural castle and grounded-site generation.
* `tools/check_terrain_affordances.py --runtime`: saved member footings, complete exterior edge rings and support.
* `tools/castle_natural_runtime_report.json` and `tools/terrain_affordance_validation_report.json`: final test evidence.

No forced placement command is used for the natural castle proof. No visual
acceptance or all-seed guarantee should be inferred from the mechanical checks.
