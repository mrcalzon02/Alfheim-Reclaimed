# Cultural Asset Library — Alfheim Royal / Noble Foundation

**Role:** authoritative implementation record for the civilization-wide reusable asset system introduced by the September 5, 2026 Noble Houses / Fey Stones / Cultural Generation design record.

**Status:** the first Royal macro-asset source slice exists but has not completed repository/runtime acceptance. Royal Tile Set I — Court & Residence is now the authoritative first decorative-object design set; it is design only until its registered models/textures are built and reviewed.

**Extends:** `THE_SURFACE.md`, `ANCIENT_ELVEN_STRUCTURE_ROSTER.md`, `LIVINGROCK_LIBRARY.md`.

## 1. Binding thesis

Structures are downstream products of a civilization definition. Alfheim therefore develops in this order: civilization language -> reusable asset families -> environment relationships -> room/structure modules -> generation grammar -> progression/narrative -> individual instantiations.

The existing 32 surface landmarks are retained as the first landmark layer. Their refinement pass must consume this shared vocabulary instead of becoming 32 unrelated detail passes. The 3K near ring will introduce degraded versions of the same language before players reach the monumental 6K great houses.

## 2. Asset contract

Every asset family records purpose, family, construction logic, approved materials, scale, condition, room compatibility, house affinity, placement rules, storytelling tags and generator weight. Families require intact and damaged/ruined derivatives where damage is meaningful. A single decorative object with no family, no placement logic and no story is not an accepted cultural asset.

Royal work begins sacred and structural before miscellaneous furniture:

1. sacred/reliquary pieces;
2. monumental royal architecture;
3. noble furnishings;
4. ceremonial/representational pieces;
5. household/service pieces;
6. damaged, burned, overgrown, stripped or repurposed derivatives.

## 3. First macro-asset source slice

`tools/royal_asset_manifest.json` defines the first reusable macro families:

- reliquary pedestal;
- oath memorial;
- monumental arch;
- grand column;
- processional stair;
- balcony/gallery bay;
- royal bench;
- ceremonial brazier;
- one ruined reliquary-core development prototype.

`tools/gen_royal_assets.py` is the authoritative generator source for block-built NBT fragments intended for `kubejs/data/alfheim/structures/royal_assets/`. The generator/checker sources exist, but generated NBT was deliberately not committed through the GitHub connector because binary transfer was not trustworthy. Therefore this source slice is not claimed static-validated or present in-game until the generator is executed in an actual repository environment and its outputs are checked.

The prototype reliquary does **not** fake a Fey Stone. Its center contains one mandatory jigsaw socket named `alfheim:fey_stone_socket`. The later house-specific stone implementation must satisfy that socket deterministically. No valid ruin derivative may remove the socket or all access to it.

## 3.1 Royal Tile Set I — Court & Residence

`alfheim_reclaimed_design/ROYAL_TILESET_I.md` and `tools/royal_tileset_catalog.json` define the first object-scale Royal/Noble furnishing library: **48 semantic assets in 12 four-member families** covering ceremonial objects, seating, tables/desks, storage/display, sleeping/personal furniture, lighting, heraldry/textiles, vessels/tableware, scholarly objects, architectural ornament, botanical/conservatory pieces and guard accoutrements.

This layer is intentionally different from the macro NBT fragments above. Chairs, cabinets, vessels, sconces, banners, balustrades, planters, instruments and similar human-scale details need custom or modular block models when ordinary full blocks cannot express their silhouette. Large architectural pieces remain block-built structure fragments. Multi-block furniture is assembled only where its visible size genuinely requires it.

The set also formalizes house substitution slots for color, heraldry, metal, wood/stone inlay, textile borders, glass tint and magical glow. The first six houses therefore do not require six copied furniture namespaces: they share the same elven civilization language and differentiate through weighting, materials, heraldry and room program.

Generic rubble, splintered debris, remains and anonymous abandoned-object scatter continue to belong to `tools/ancient_set_dressing_manifest.json`. Tile Set I owns the recognizable cultural object and its meaningful decline state; the set-dressing system owns the surrounding residue.

## 4. Construction language

The initial royal grammar uses proven in-pack materials: elven quartz as the formal shell, living/magical stone accents, Dreamwood as warm structural/furnishing material, Elementium for refined metalwork, and elf glass for translucent openings and instruments. The geometry favors tall narrow openings, layered frames, expressed bases/capitals, repeated vertical rhythm, axial processional routes, open negative space and visible magical-service elements.

Damage is causal. Failed arches throw debris toward the failed side; broken columns retain bases and fallen capitals; damaged stairs preserve a climbable spine; balcony failure proceeds from the exposed edge inward. Furniture follows the same rule: legs/joints fail, glass shatters locally, textiles tear from supports, cabinets lose doors/shelves, and botanical pieces crack and overgrow. Random block deletion is not a substitute for decline history.

## 5. Surface integration rules

The surface refinement pass is not allowed to decorate by density alone. Landmark upgrades should pull assets by historical function and condition:

- castles/halls/shrines: thresholds, columns, gallery bays, memorials, heraldry, furniture and ceremonial lighting;
- quarries/infrastructure: derivative worksite/service families, broken mana/water infrastructure and discovery-value resources;
- shore/ocean ruins: drowned derivatives with waterline, silt, collapsed pier/seawall and salt-damage logic;
- all structures: human-scale residue, broken paving, railings, seating, work areas, storage and debris that explain function and failure.

The Starved Reach `starveling_pit` remains the terrain-integration calibration reference. Greatbole-to-ruin connection geometry and terrain-sensitive placement remain separate required repairs under `THE_SURFACE.md`; once the Tile Set I pilot is accepted, those repairs should consume the shared Royal vocabulary rather than inventing one-off decoration.

## 6. Validation and acceptance

`tools/check_royal_assets.py` is intended to verify macro-asset metadata completeness, family condition coverage, 48-block piece limits, minimum geometry, no dropped out-of-bounds writes, NBT round-trip parsing, deterministic source metrics, and the required single Fey-Stone jigsaw socket in the reliquary prototype. It must still be executed against generated repository outputs before that slice advances.

Royal Tile Set I design acceptance requires exactly 12 four-member families / 48 unique semantic assets, only canonical condition states, explicit placement/room/house metadata, no progression objects, no default inventory behavior and no persistent entity-based display props. Static implementation acceptance additionally requires registered model/block validity, correct rotation/collision, deterministic material substitutions, condition variants and a generated review atlas. Runtime acceptance requires client placement and inspection.

## 7. Deliberately unresolved

The first six house identities and exact six fixed bearings remain uncanonized because the source design did not finalize them. The concrete Fey Stone block/block-entity and persistence format also remain open. Neither uncertainty blocks building the shared Royal tile vocabulary because house identity is represented through substitution hooks rather than copied geometry.

## 8. Next exact action

Implement the Royal Tile Set I **Wave A pipeline pilot**: Highback Chair, Wall Sconce, Carpet Runner, Balustrade Segment, Lidded Amphora, Canopy Bed, Wall Banner and Astrolabe. Those eight deliberately exercise the major representation problems—single custom furniture, wall lighting, connectable floor tiles, connectable architecture, small props, multi-block furniture, house-substitution textiles and complex hero geometry. Register, texture, generate a review atlas and validate those eight before completing the remaining Wave A families or consuming them in the Greatbole/court refinement pass.
