# Void Margins — terrain and supported structure contract

**Role:** implementation-facing extension of `../VOID_MARGINS.md`.
**Status:** statically implemented 2026-09-05; fresh-world and client traversal acceptance remain pending.
**Authority:** subordinate to `INSTRUCTIONS.md`, `../VOID_MARGINS.md`, `../DEFICIENT_BIOMES.md`, `../THE_SURFACE.md`, and `../THE_DEEP.md`.

## 1. Live-state correction

The five Void Margin siblings are no longer merely proposals. The generated Alfheim layer already contains `alfheim:shatterfields`, `alfheim:prism_drift`, `alfheim:rootfall`, `alfheim:sepulchral_reach`, and `alfheim:starless_reach` alongside `alfheim:void_verge`. That makes twenty-one live Alfheim biome IDs: the sixteen biomes covered by the existing thirty-two Surface Works structures plus these five additional Void Margin biomes.

The original Surface Works rule remains useful: every live Alfheim biome should have two meaningful surface structures. `void_verge` already has `verge_spire` and `severed_span`, and the extension adds ten structures for the five sibling biomes. With the separately added Alfheim Ocean pair, the live catalogue is forty-four surface structures across twenty-two biomes. The twelve Void structures are generated; runtime placement and client support review remain open.

The rejected terrain state also remains rejected. The custom aquifer helper does not become the foundation for this work. Terrain must be repaired in the existing density/noise/surface data first, and every structure below is conditional on terrain support that already exists before structure placement.

## 2. One terrain system, four longitudinal bands

The Void Margins are not six concentric rings. Environment identity varies laterally, while one continentalness signal still controls how much world remains longitudinally.

| Band | Continentalness tuning | Physical meaning | Structure policy |
|---|---:|---|---|
| Safe rim | `-0.86 .. -0.80` | continuous, dry, low-relief final shelf | normal supported structures |
| Inner debris | `-0.925 .. -0.86` | attached shelves and substantial detached fragments | support-volume structures only |
| Terminal debris | `-0.94 .. -0.925` | last substantial landings tapering into shards | only small terminal structures |
| Far field | `< -0.94` | guaranteed empty air | no terrain, structures, fluids, or resources |

The important distinction is between **shape** and **frequency**. Local noise may sculpt the silhouette of a shelf or fragment, but the distance-to-edge envelope owns whether a fragment exists at all. That preserves the required visual sequence: broad land, hard break, diminishing debris, then nothing.

No structure template is allowed to manufacture the missing terrain. If its selected host does not satisfy the support class required by the structure, placement relocates or fails.

## 3. Support classes

Support is a generation input, not a visual afterthought. The existing Surface Works field review already rejected structures that projected from cliffs without credible foundations. The Void makes that failure much more obvious, so every structure here declares one of five support classes.

### Rim-backed

For ordinary structures on the safe Verge shelf. At least 82% of the structural footprint must already contact solid terrain, the supporting material must remain at least eight blocks deep below the main footprint, local relief across the footprint must remain within eight blocks, and unexplained cantilever may not exceed three blocks.

### Attached shelf

For structures on shelves that remain physically connected to the main rim. At least 76% of the footprint must be supported, shelf thickness must reach eight blocks, and the shelf must connect to the rim through at least a six-block-wide root of continuous stone. Decorative balconies may project, but the primary building mass may not.

### Fragment core

For substantial detached masses in Shatterfields or Prism Drift. A candidate host must contain at least 2,400 solid blocks inside the measured host volume and be at least 16×10×16 before a structure is considered. At least 80% of the structure footprint must sit on the host. The structure may decorate a fragment; it may not be the reason the fragment has enough blocks to exist.

### Embedded cliff

For galleries and tombs whose rooms belong inside surviving land. The facade requires 85% support and at least sixteen blocks of competent backing depth behind the entrance. External projections are limited to five blocks. A failed backing-depth probe rejects the placement rather than allowing a chamber to open directly into the void.

### Terminal landing

For Starless Reach only, and only in the surviving `-0.94 .. -0.925` strip. The host needs at least 1,800 solid blocks, minimum dimensions of 14×8×14 and 86% footprint support. Any candidate below `-0.94` fails unconditionally. Nothing in the far field may become structure-capable merely because a structure wants somewhere to stand.

## 4. Terrain feature grammar

Each environment gets three terrain features. These are not eighteen independent scatter features; they are named shapes and placement contracts that the terrain generator can compose.

| Environment | Feature | Read |
|---|---|---|
| Void Verge | **Verge Table** | broad final shelf with low relief and continuous footing |
| Void Verge | **Shear Crack** | shallow warning fracture that ends visibly before becoming a lethal hidden pit |
| Void Verge | **Breakline Scar** | exposed vertical rupture and layered cliff face at the world edge |
| Shatterfields | **Pressure Slab** | large angular detached or partly attached landing |
| Shatterfields | **Fault Needle** | narrow upright pressure remnant that interrupts the horizon |
| Shatterfields | **Talus Shelf** | thick attached wedge under a visible shear plane |
| Prism Drift | **Prism Core** | substantial fragment with a mineral interior laid open |
| Prism Drift | **Split Seam** | discontinuous fracture tracing a mineral boundary without bisecting the whole landing |
| Prism Drift | **Crystal Crown** | small crystal growth placed only on a host much larger than the formation |
| Rootfall | **Root Apron** | tapered petrified ribs beneath a surviving shelf |
| Rootfall | **Trunk Socket** | negative imprint of a vanished giant tree, with radial fossil grain |
| Rootfall | **Dry Irrigation Channel** | shallow civilized drainage scar that ends at the broken edge |
| Sepulchral Reach | **Burial Face** | stable cliff wall with reserved backing volume for a sealed facade |
| Sepulchral Reach | **Memorial Shelf** | unusually broad and quiet ledge beneath burial faces |
| Sepulchral Reach | **Fallen Slab Field** | a few monumental plates collapsed onto existing shelf mass |
| Starless Reach | **Terminal Landing** | last structure-capable mass before guaranteed emptiness |
| Starless Reach | **Hollow Splinter** | small non-anchorable shard with internal voids |
| Starless Reach | **Astralite Fleck** | tiny outward-facing visual reward on the final surviving rock |

The dimensions will be recorded in the machine-readable terrain/structure catalog during implementation. Their purpose is to stop scale drift: a Fault Needle must not become a new cliff wall, and a Crystal Crown must not become a geode larger than the fragment supporting it.

## 5. Structure coverage

The two existing `void_verge` structures remain and are refined rather than replaced.

### Void Verge

**Verge Spire** stays a watch/survey tower, but its next pass must make the relationship with the edge legible. The landward stair belongs on the Verge Table, the tower core must remain fully rim-backed, and the crown should carry broken survey fittings and mana sockets rather than simply being a generic tower. Decay variants are an intact lower core with a sheared crown, a collapsed outer stair, and a broken parapet. It should help the player see the world edge from inland.

**Severed Span** is the physical explanation of a route that no longer exists. The landward abutment and approach paving remain supported; the arch ribs and deck fail toward the void. It must never accidentally bridge to another fragment or create a convenient generated crossing. Its far side is absence.

### Shatterfields

**Anchor Bastion** is a compact strongpoint built around one competent Pressure Slab. A buttressed base, two-level watch chamber, mana-clamp sockets and a damaged landing explain that the elves were trying to stabilize and observe a failing edge. It uses the Fragment Core support class. The upper tower may split or lose a stair, but the base cannot float.

**Fracture Gate** is a roadhead or gatehouse where a civic route was severed. One supported gate pier survives on a Talus Shelf, with a short processional deck, maintenance room and drainage slot. The opposing side survives only as a visible architectural trace; the structure does not rebuild the missing route.

### Prism Drift

**Prism Observatory** is an open scientific structure built on a large Prism Core. It has an instrument dais, partial dome ribs, crystal sockets, a view platform and a small service niche. It does not spawn its own crystal island. A Crystal Crown may decorate the host only after both the structure host and the crystal host-volume checks succeed.

**Split Gallery** is a mineral inspection and extraction hall embedded into a surviving core. The entrance opens onto a supported face, then an inspection corridor reaches two sample alcoves, a broken mana conduit and a sealed rear niche. It is not a quarry full of free ore. Any mineral samples must come from already-valid resource families and remain modest.

### Rootfall

**Root Shrine** is a botanical shrine on an Attached Shelf whose foundations are visibly wrapped by Root Apron ribs. Its program is a processional step, open altar, root-column ring, dry basin and collapsed canopy. Root pressure should explain cracked floors and missing roof sections.

**Garden Archive Terrace** is larger but remains shelf-backed: archive hall, retaining wall, dry irrigation run, root observation bay and a damaged garden stair. This is one of the strongest places to show that the lost civilization managed forests as infrastructure rather than merely living among trees.

### Sepulchral Reach

**King's Cliff Tomb** is not a second dungeon system. It is the surface-facing entrance to the Elder King tomb grammar already owned by `THE_DEEP.md`: memorial facade, sealed door, antechamber, burial chamber and one reward plinth. The placement probe reserves at least sixteen blocks of backing rock before generation. Loot remains exactly one era-appropriate significant tomb reward under the existing Tomb rules.

**Mourning Court** is the companion surface find and deliberately less rewarding: colonnade, memorial slabs, central dry basin, processional edge and a collapsed side chapel. It provides lore and decorative salvage, not a second major tomb reward.

### Starless Reach

**Last Watch** sits only on a valid Terminal Landing. It is compact: one stair, watch chamber, open rail, broken survey arm and a return-facing beacon socket. Its purpose is psychological as much as architectural — this is the last place where someone once expected to stand and look outward.

**Starless Orrery** is rare and also restricted to a Terminal Landing. A low ring platform, three instrument piers, central socket and incomplete outer arc frame the guaranteed empty far field. The ruin may lose one pier or part of the ring, but the remaining platform must still be safe enough to read as intentional architecture rather than a random lethal gap. Its reward is lore or a cosmetic Astralite accent, not progression.

## 6. Resource and structure interaction

Terrain first, resources second, structures third. This order matters.

A Prism Core may qualify for a volume-checked Duskglass/Galeglass formation. A structure may then qualify on the remaining host. Neither feature is allowed to add blocks merely to rescue the next placement. Rootfall may expose ordinary ore seams in broken root cross-sections, but Rootfossil and Resinshale remain decorative host stone. Sepulchral Reach reserves tomb backing volume so a geode cannot later hollow the chamber out. Starless Reach allows only small exposed mineral indications; full geodes and large ore features stop before the terminal strip.

Conventional pools remain forbidden throughout the Void Margins. No terrain or structure pass adds water, lava, obsidian flooring or a replacement island under a failed placement.

## 7. Structure pipeline rule

These structures extend the existing Surface Works implementation. They do not get a second structure generator, second placement registry or parallel map system. The intended source owner is `tools/gen_surface_works.py` plus `tools/surface_works_manifest.json`, with any genuinely necessary new parametric archetype added there.

The King's Cliff Tomb is the only hybrid: its **surface placement and facade** belong to Surface Works, while its sealed-room grammar and reward policy belong to the Tomb family in `THE_DEEP.md`. The two systems share pieces or generation helpers rather than independently implementing two tomb types.

The existing Cartographer model should gain maps only when the new structures are built and locatable. A design entry does not get a purchasable map.

## 8. Decay and architectural quality

The Surface Works runtime review already established the visual bar: grand advanced elven construction under slow causal decay. Void structures follow the same rule but expose more of their structural logic because the ground itself is missing.

Every hero build needs a visible load path: buttress into stone, wall into backing rock, root into shelf, pier into competent core. Damage then follows that load path. A tower may shear above a pressure fracture; a garden wall may bow under petrified roots; a cliff tomb may lose outer memorial masonry while its buried chamber remains intact. Randomly deleting blocks is not an acceptable decay system.

Mana conduits, crystal sockets, survey arms, rune channels, drainage, retaining works and maintenance spaces should show how the elves used the site. They are evidence of technology and civil engineering, not additional magic systems.

## 9. Validation contract

Static acceptance requires exactly six Void Margin biome IDs, exactly eighteen terrain-feature definitions and exactly twelve structure definitions: two structures per environment. The five new sibling biomes therefore account for exactly ten planned new structure IDs. No structure may use the far field as an allowed placement band.

Generation acceptance requires every candidate structure to expose the host class and support measurements used to accept it. Rejected support must result in relocation or no placement, not hidden terrain fill.

Fresh-world acceptance requires at least three separated rim segments. For each, observe the dry shelf, cliff, debris falloff, far-field zero terrain, supported structures and absence of fake foundations. Starless structures must be proven to disappear entirely below the `-0.94` threshold. Client traversal remains mandatory because a numerical support ratio cannot prove that an approach, drop or broken stair reads correctly to a player.

## 10. Implementation order

1. Finish the data-only dry-void repair and remove the custom helper layer.
2. Reconcile the six live Void Margin biome IDs in the existing design/state records.
3. Add support-volume probing to the Surface Works generator before adding any new Void structure.
4. Refine the existing Verge Spire and Severed Span against the support contract.
5. Implement one biome pair at a time: Shatterfields, Prism Drift, Rootfall, Sepulchral Reach, then Starless Reach.
6. Add terrain formations before structures that depend on them; add resources only after host-volume checks exist.
7. Run structure/static checks, then controlled startup, `locate structure`, fresh-world placement and client traversal.
