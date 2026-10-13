# Elder Lineage Precinct — Wave 1

Authority: `ANCIENT_ELVEN_STRUCTURE_ROSTER.md` sections 6.2, 7.1 and 11;
furnishing vocabulary: `CULTURAL_ASSET_LIBRARY.md` and `ROYAL_TILESET_I.md`.
Implemented 2026-10-12. Acceptance: **runtime assembled and verified**;
client architecture, terrain-fit and gameplay acceptance remain outstanding.

## Estate programme

This is one estate anchor with eight connected members. It has one structure set,
not nine independent landmarks. The three-part palace spans approximately 141
blocks; the complete local footprint is 141 × 191 blocks before rotation.

| Member | Programme and decline evidence |
|---|---|
| Palace audience hall | Tall double colonnade, surviving roof ribs, two accessible upper galleries, lineage monuments and formal seating. Side spaces became shelter beds and an emergency record office. |
| Ancestral gallery | Eight lineage monuments, audience seating, hanging heraldry, cabinets and a writing desk; damaged masonry beside surviving records. |
| Family residence | Four assembled canopy beds, household rooms, a deliberately sealed inner bay and abandoned household remains. The main estate route remains open. |
| Ancestor reflection court | Contained water garden, formal memorials and common emergency burials intruding into the eastern ornamental beds. |
| Family mausoleum | Four dynastic sarcophagi, paired guardians, framed columns, mounted heraldry and sparse ceremonial light. |
| Entrance court | Processional columns, a surviving ceremonial span, waiting benches, empty weapon racks and a fallen warden at the service boundary. |
| Retainer house | Eight crowded beds, an accounting desk, stores and household remains; an official residence repurposed to shelter dependents. |
| Household service | Unlit cooking stations, counters, household vessels and exhausted medical/service residue. |
| Processional gate | Two ceremonial arch traces and a surviving lineage monument at the formal approach. |

These rooms consume the existing Royal Tile Set and Elder Kings funerary blocks:
**152 cultural modules** are present at their expected positions in the saved world.
No new decorative entities, custom block registrations or third-party jar edits
were introduced. The family has **zero vanilla lanterns/soul lanterns**; ceremonial
illumination uses sparse existing mana-brazier modules.

All occupied air is authored, including open roof volume and port headroom.
Eight courses of buried bedding support the floor datum. Wall banners occupy
adjacent air cells with masonry behind them. The reflection pool has a continuous
rim; skeletal traces are placed outside the processional axis. None of the new
work changes broad terrain, climate partition or aquifer functions.

## Culture and progression boundary

The estate is an unassigned lineage prototype. It does not impersonate a named
great house, create a Fey Stone, grant a house/profession credential, or award
progression-locked equipment. Nine cache barrels preserve ordinary food, seeds,
paper, books, dye and limited decorative elven quartz. Their inventory vocabulary
follows household or record-room function.

House affinity, a proper reliquary/Fey-Stone relationship and named 3K/6K house
variants remain later cultural/progression work. The reusable macro-asset library's
development reliquary was not silently installed or substituted for a real stone.

## Evidence

- Source: `tools/gen_elder_lineage.py`; contract: `tools/elder_lineage_manifest.json`.
- Shipping corpus: **23 files** — nine NBT templates, nine pools, structure,
  structure set, biome tag and two loot tables.
- `check_elder_lineage.py`: isolated source/shipping reproduction; legal 48-block
  template bounds; nine non-overlapping members inside the adapted 116-block reach;
  eight supported ports with authored headroom; block registration declarations;
  four dynastic burials; no persistent template entities; cultural/light budget.
- Feature ordering: zero cycles. `check_field_review.py`: all 39 protected terrain
  and climate files remain byte-identical, and earlier repair guards still pass.
- Test world: `server/validation-elder-lineage-20261012`, seed
  `3536368297089363045`, placement requested at X -1443, Z 654 in Alfheim.
- Console: `server/console-20261012-134655.log`. Structure generated through the
  biome/heightmap placement path; all dimensions saved; process exit 0.
- `check_ancient_assembly.py --family elder_lineage`: all nine members present,
  all eight joins have a solid floor and two blocks of clear air, member geometry
  matches source, and every one of the 152 royal/funerary block modules exists
  at the expected saved-world position.
- Captured layout: `tools/elder_lineage_runtime_census.json` and
  `elder_lineage_precinct_layout.png`.

Player saves were not edited. Development-server properties were restored.
This is controlled assembly validation, not a natural-placement frequency survey
or a claim of client visual admission. Terrain fit across different relief,
upper-gallery use, heraldry orientation and appearance under shaders need a client
walk before production admission.

## Next roster family

**Civic Center**: High Assembly Hall or District Forum, Record House and Provincial
Council House, with emergency administration, shelter conversion and surviving
public circulation. Retain family-linked placement rather than independent sets.
