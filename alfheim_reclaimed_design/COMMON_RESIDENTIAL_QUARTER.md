# Common Residential Quarter — Wave 1

Authority: `ANCIENT_ELVEN_STRUCTURE_ROSTER.md`, especially sections 7.3, 9 and 11.
Implementation date: 2026-10-12. Acceptance: **runtime validated for assembly**;
client terrain-fit, architecture and gameplay review remain outstanding.

## Implemented district

One district anchor assembles a connected place. Individual homes, streets, cisterns
and graves have no independent structure sets.

| Member | Count | Purpose and decline evidence |
|---|---:|---|
| Neighborhood Common Hall | 1 | Shared kitchen and public hall converted to ration distribution; queue rails, exhausted stores, remains and roof loss |
| Common Row House | 6 | Two family rooms sharing a partition; beds, household stores, damaged roof timbers and civilian remains |
| Courtyard Home | 4 | Water court and garden converted to subsistence use; sleeping space, sealed sick-room partition and household burial evidence |
| Artisan House-Shop | 4 | Living space with work benches, unfinished repair infrastructure and an exchange counter |
| Extended Kin Hall | 2 | Compact two-storey member with six beds in upper sleeping galleries, a shared work/eating room and accessible stairs |
| Avenue | 4 | Seven-block public street, paved house approaches, runic wayfinding and clogged water infrastructure |
| District Cistern | 1 | Contained reservoir, dark filter bed, failed valve and emergency-use traces |
| Mass Grave of the Last Order | 1 | Four ordered trench rows, a crowded late pit, corpse-cart approach, digger camp and a connected trace edge |
| Collapsed Trace Field | 3 | Foundation fragments, broken services and directional masonry/timber residue |
| **Total** | **26** | **16 inhabited members plus the common hall** |

The 20-block house frontage and 22-block socket spacing are intentional. The earlier
32–48-block plots overlapped adjacent sockets and district corners. The pilot uses
compact, functionally different street buildings; this is not the roster's eventual
monumental kin-estate form. Street-specific pools guarantee six row houses, four
garden homes, four workshops and two kin halls rather than leaving required social
functions to weighted chance.

Every template stays inside the 48-block boundary. Six courses of bedding lie beneath
authored floors and paths. The start datum embeds that bedding below the sampled
surface. Rooms and paths explicitly clear their occupied air volume, so native
terrain cannot fill their interiors or doorway headroom. The district uses a single
engineered terrace; contour-stepping and severe-relief admission remain review gates.
Do not treat `beard_thin` alone as proof of terrain integration.

Water courts and the cistern have retaining rims. Failed water-service valves use
clogged glass fittings, which cannot create uncontrolled perpetual water sources.
Floor-level paths are reserved before connector placement; their clearing cannot
erase the opposing house socket.

## Discovery value

Seventeen governed cache barrels mark the hall and inhabited members. Household
caches contain food, seeds and paper; public stores preserve basic crop leads;
workshops contain sticks, paper, string and limited decorative elven quartz.
No end-tier gear, progression token, magic station or spine milestone is awarded.
There are no persistent decorative entities or authored spawners.

## Evidence

- Authoritative generator: `tools/gen_ancient_districts.py`.
- Manifest: `tools/ancient_district_manifest.json`.
- Shipping corpus: **31 files** — 12 templates, 13 pools, 3 placement/tag files,
  and 3 loot tables. An isolated rebuild reproduces JSON bytes and decoded NBT.
- `check_ancient_districts.py` verifies the corpus, registered block names,
  legal bounds, four surviving house sockets per avenue, doorway headroom and
  doorway support.
- Feature ordering: zero cycles. All 39 protected broad terrain/climate files
  remain byte-identical to the October 12 baseline.
- Final test world: `server/validation-residential-quarter-complete-20261012`.
  Seed `3536368297089363045`; placement requested at X -1443, Z 654 in Alfheim.
- Console: `server/console-20261012-132531.log`; generated through
  `/place structure`, all dimensions saved, process exit 0.
- `check_ancient_assembly.py` reconstructed the actual saved layout from its
  hall cache and connector geometry. All 26 members match source geometry;
  all 25 joins have a solid floor and two blocks of clear air. The saved cache
  census proves the exact 6/4/4/2 inhabited mix.
- Layout evidence: `tools/ancient_district_runtime_census.json` and
  `common_residential_quarter_layout.png`.

Earlier attempts are retained. They exposed unowned road headroom, unowned side
paths and a clearing pass that erased the opposite house connector. These failed
the acceptance checks and were repaired before the final census passed.

This establishes controlled fresh-world assembly and saving, not an unbiased
natural-spawn survey or client visual admission. Player saves were not edited.
The development server properties were restored after each run.

## Next gate and sequencing

Walk the retained district in a client: assess the single terrace against local
relief, readable household/workshop differences, roof collapse, cistern containment,
grave chronology and indoor/upper-gallery circulation. Record this separately from
the automated bounds and connector evidence.

The next roster family is the **Elder Lineage Precinct**: Elder Lineage Palace or
High Noble Hall, Noble Retainer Hall, Private Ancestor Court, and Family Mausoleum.
Its design and terrain-fit review must retain the same settlement-family approach.
