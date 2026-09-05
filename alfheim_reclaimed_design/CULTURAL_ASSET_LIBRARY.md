# Cultural Asset Library — Alfheim Royal / Noble Foundation

**Role:** authoritative implementation record for the civilization-wide reusable asset system introduced by the September 5, 2026 Noble Houses / Fey Stones / Cultural Generation design record.

**Status:** first production slice implemented for static validation. This record adopts the new conversation design into repository authority; it does not claim runtime or fresh-world acceptance.

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

## 3. First implemented slice

`tools/royal_asset_manifest.json` defines the first reusable families:

- reliquary pedestal;
- oath memorial;
- monumental arch;
- grand column;
- processional stair;
- balcony/gallery bay;
- royal bench;
- ceremonial brazier;
- one ruined reliquary-core development prototype.

`tools/gen_royal_assets.py` emits block-built NBT fragments under `kubejs/data/alfheim/structures/royal_assets/`. They are inspectable with `/place template alfheim:royal_assets/<id>`. They have **no worldgen registration** in this slice.

The prototype reliquary does **not** fake a Fey Stone. Its center contains one mandatory jigsaw socket named `alfheim:fey_stone_socket`. The later house-specific stone implementation must satisfy that socket deterministically. No valid ruin derivative may remove the socket or all access to it.

## 4. Construction language

The initial royal grammar uses proven in-pack materials: elven quartz as the formal shell, living/magical stone accents, dreamwood as warm structural/furnishing material, and elf glass for translucent openings. The geometry favors tall narrow openings, layered frames, expressed bases/capitals, repeated vertical rhythm, axial processional routes, and visible magical-service elements.

Damage is causal. Failed arches throw debris toward the failed side; broken columns retain bases and fallen capitals; damaged stairs preserve a climbable spine; balcony failure proceeds from the exposed edge inward. Random block deletion is not a substitute for decline history.

## 5. Surface integration rules

The surface refinement pass is not allowed to decorate by density alone. Landmark upgrades should pull assets by historical function and condition:

- castles/halls/shrines: thresholds, columns, gallery bays, memorials and ceremonial lighting;
- quarries/infrastructure: derivative worksite/service families, broken mana/water infrastructure and discovery-value resources;
- shore/ocean ruins: drowned derivatives with waterline, silt, collapsed pier/seawall and salt-damage logic;
- all structures: human-scale residue, broken paving, railings, benches, work areas, storage and debris that explain function and failure.

The Starved Reach `starveling_pit` remains the terrain-integration calibration reference. Greatbole-to-ruin connection geometry and terrain-sensitive placement remain separate required repairs under `THE_SURFACE.md`.

## 6. Validation and acceptance

`tools/check_royal_assets.py` verifies metadata completeness, family condition coverage, 48-block piece limits, minimum geometry, no dropped out-of-bounds writes, NBT round-trip parsing, deterministic source metrics, and the required single Fey-Stone jigsaw socket in the reliquary prototype.

This slice may advance only to **static validated** until the generated templates are loaded in Minecraft and visually reviewed. Runtime acceptance must inspect scale, silhouettes, collision/traversal, broken-state readability, material substitutions and the reliquary route.

## 7. Deliberately unresolved

The first six house identities and exact six fixed bearings remain uncanonized because the source design did not finalize them. The concrete Fey Stone block/block-entity and persistence format also remain open. Neither uncertainty blocks building the reusable sacred/architectural vocabulary or a socketed reliquary prototype.

## 8. Next exact action

Load the Royal Asset review set in a client, reject/adjust weak silhouettes, then use the accepted families in the first surface refinement target and in one 3K near-ring ruin. After that, build the first house-specific reliquary antechamber kit and lock the six first-ring house identities/bearings before any mass manor generation.
