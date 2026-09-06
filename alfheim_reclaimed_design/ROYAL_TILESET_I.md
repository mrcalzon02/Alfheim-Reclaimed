# Royal Tile Set I — Court & Residence

**Role:** first implementation-facing design catalog for reusable Royal/Noble objects, decoratives, furniture, household goods, architectural ornaments and court accoutrements.

**Status:** design specification. No block/model registration, textures, recipes, generated structure outputs, or runtime acceptance are claimed by this record.

**Authority:** extends `alfheim_reclaimed_design/CULTURAL_ASSET_LIBRARY.md` and the September 5, 2026 Noble Houses / Fey Stones / Cultural Generation design. Generic rubble and decay remain owned by `tools/ancient_set_dressing_manifest.json`.

**Catalog:** `tools/royal_tileset_catalog.json`.

## 1. Purpose

Royal Tile Set I is the first concrete furnishing vocabulary for Alfheim's lost high-status civilization. It exists so the Greatbole court, 3K near-ring estates, later 6K great houses, castles, halls, shrines, observatories, conservatories and noble residential wings can draw from the same civilization rather than being decorated as unrelated one-off builds.

This is deliberately a **tile set**, not a bag of props. Every semantic asset declares a footprint, anchor, room compatibility, condition states, house-affinity hooks, material-substitution profile and production wave. Structure generators can therefore reserve furnishing sockets and choose coherent objects by room function instead of scattering decoration randomly.

The first set contains **48 semantic assets in 12 families**. "48 assets" does not mean 48 final block IDs. Intact/worn/damaged states may be expressed with model variants, blockstates, material substitutions, multi-block assemblies or separate registered blocks depending on what is mechanically cleanest. The catalog owns semantic identity; implementation chooses the smallest stable representation.

## 2. Visual language

Royal Alfheim should read as advanced, old, botanical and deliberate without becoming mechanically industrial.

Forms favor tall and slender proportions, leaf/seed/flame curves, expressed ribs, elevated legs, open negative space, inset glass, shallow relief carving, layered borders and repeated vertical rhythm. Furniture should look lighter and more engineered than human medieval furniture. It should not look dwarven, rustic, blocky, mass-produced or modern-minimalist.

The base material language is native Alfheim: Dreamwood, elven quartz, Elementium, elf glass, Livingrock/Sourcestone where magical service is visible, and house-colored textiles/inlays. Livingwood is not treated as the default Royal timber because the pack's governing premise makes human/Midgard materials exotic and elven materials native.

Magic appears as integrated craft: contained luminous cores, thin glass channels, inlaid runic or botanical lines, suspended or balanced forms, and instruments that imply magical knowledge. The set does not add generic glowing cubes merely to signal "magic."

## 3. Relationship to existing asset systems

The existing Royal structure-fragment manifest already contains macro pieces such as the Royal bench and ceremonial brazier. Those are retained as prototypes. Tile Set I supplies the reusable object vocabulary beneath them. When the custom-object implementation exists, macro structure generators should consume the accepted tile family rather than keeping duplicate hand-built furniture forever.

`tools/ancient_set_dressing_manifest.json` remains authoritative for generic rubble fans, fallen masonry, splintered beams, broken-furnishing debris, remains, abandoned generic objects and failed infrastructure. Royal Tile Set I owns the **recognizable intact object and its culturally specific damaged form**. The set-dressing system owns the anonymous residue around that failure.

No Tile Set I object is a Fey Stone, progression token, quest gate, mana source or guaranteed loot container. Decorative storage is decorative by default. If a room needs actual loot, the structure generator places a separately governed loot container or interaction point.

Persistent display entities are forbidden as the baseline. Armor displays, goblet groups, table settings, banners and similar details are modeled as blocks/assemblies so ruins do not fill the world with armor stands, item frames or loose item entities.

## 4. Tile and placement grammar

The catalog uses a small placement vocabulary:

- **T1** — 1×1 small floor or tabletop object.
- **T2** — 1×2 / 2×1 furniture or linear object.
- **T4** — 2×2 medium furniture or instrument.
- **T6** — 2×3 large furniture assembly.
- **T9** — 3×3 hero furniture/technical assembly.
- **W1** — one-block-wide wall-mounted ornament, textile or light.
- **W2** — wide wall-mounted feature.
- **C1** — ceiling-mounted feature.

Every floor tile needs an explicit facing and clearance envelope. A room generator must reserve circulation first, then furnishing sockets. Furnishings may not block the required route from entry to room purpose, and ruined variants may not turn a previously valid route into an accidental puzzle.

Furniture placement is contextual. A bed implies a bedchamber or guest suite; a council map table implies governance, strategy or surveying; an astrolabe implies scholarly/observatory culture; a weapon rack implies guard or armory use. A room may use sparse secondary props, but the primary tiles must explain its function before debris is added.

## 5. The twelve Royal families

| Family | Four base assets | What the family communicates |
| --- | --- | --- |
| Ceremonial & sacred | Oath Basin, Offering Stand, Lineage Stele, Crown Display Dais | lineage, ritual, remembrance, controlled presentation of authority |
| Seating | Highback Chair, Audience Bench, Crescent Settee, Kneeling Stool | court hierarchy, waiting, leisure, domestic ritual |
| Tables & desks | Banquet Table, Salon Table, Writing Desk, Council Map Table | feasting, administration, planning, social life |
| Storage & display | Tall Cabinet, Glass Display Case, Wardrobe, Jewel Coffer | wealth, routine, clothing, records, preserved/removed valuables |
| Sleeping & personal | Canopy Bed, Washstand, Vanity, Privacy Screen | lived-in noble residence rather than empty monumental shell |
| Lighting | Wall Sconce, Floor Candelabrum, Hanging Lantern Cluster, Mana Brazier | integrated magical lighting and ceremonial rhythm |
| Heraldry & textiles | Wall Banner, Ceiling Pennant, Carpet Runner, Ceremonial Drape | house identity, procession, soft materials, decay by tearing/fading |
| Vessels & tableware | Lidded Amphora, Goblet Service, Tea Service, Ceremonial Bowl | hospitality, storage, food/drink culture, household routine |
| Scholarly court | Scroll Rack, Book Lectern, Astrolabe, Map Case | literacy, administration, astronomy, advanced magical scholarship |
| Architectural ornament | Balustrade Segment, Finial, Carved Wall Panel, Window Lattice | reusable architectural language below full structure-piece scale |
| Botanical & conservatory | Pedestal Planter, Trough Planter, Trellis Panel, Conservatory Stand | trained growth, horticulture, domestic use of magical plants |
| Guard accoutrements | Weapon Rack, Shield Display, Armor Display, Command Standard | military presence, ceremony, readiness and stripped/abandoned authority |

The catalog carries exact footprint, anchor, model strategy, room list and condition policy for each of the 48 entries.

## 6. Model strategy

The implementation should use four representation classes rather than forcing everything into one technique.

**Custom model blocks** are the default for chairs, cabinets, small tables, lights, vessels, display objects, planters, instruments and guard fittings. These are the places where vanilla block assemblies look oversized or crude.

**Modular block sets** are used where connection matters: banquet tables, carpet runners, balustrades, carved panels, trellises, privacy screens and other pieces that need ends, middles, corners or repeatable spans.

**Multi-block assemblies** are reserved for objects whose silhouette genuinely exceeds one block and benefits from composition: canopy beds, crescent settees, council map tables, large hanging-light clusters and display daises. These assemblies may combine custom model blocks with existing structural materials.

**Existing-block structure fragments** remain valid for large architectural elements already handled well by the Royal Asset Library—monumental arches, columns, processional stairs, gallery bays and the reliquary prototype. Tile Set I does not turn those into arbitrary single-block models.

Custom geometry must have deliberate collision. Tiny tabletop goods and wall reliefs should not create invisible full-cube collision. Chairs, beds, tables and cabinets need collision that broadly matches the visible object without becoming a maze of micro-boxes. Decorative lights and hanging textiles should be non-obstructive unless the visible geometry clearly occupies walking space.

## 7. House variation without asset duplication

The first six great houses are not yet canonized, so Tile Set I does not hard-code six separate furniture libraries. Instead, each family exposes substitution slots such as house primary and secondary colors, heraldic metal, emblem/crest, Dreamwood tone or carved pattern, quartz/stone inlay, textile border, and glass or magical glow tint.

A militant house can weight weapon displays, command standards, map tables and harder geometric inlays. A scholarly house can weight astrolabes, map cases, lecterns and glass display cases. A botanical house can weight planters, trellises, offering stands and conservatory pieces. The geometry stays recognizably Alfheim; house identity appears through weighting, materials, heraldry and room program.

If a later house genuinely requires a unique cultural object, it extends the shared family instead of copying the entire set under a new namespace.

## 8. Condition and decay contract

Canonical condition vocabulary is: **intact, worn, damaged, collapsed, overgrown, burned, repaired, repurposed**. Not every object needs all eight. Every implemented family must have at least intact plus one meaningful decline state before it is considered useful for ruins.

Damage follows construction and use: chairs break at legs, arms and joints rather than losing random voxels; beds sag, lose canopy rails, tear textiles and collapse posts; cabinets hang or lose doors and shelves; ceramic and glass pieces crack or shatter locally; banners fade, tear downward or detach from one support; balustrades fail from an edge or impact point; lights lose glass, arms or magical cores; planters crack, spill soil and become overgrown; weapon/armor displays may remain intact but visibly empty; scholarly instruments bend, lose rings/lenses, or collapse around a surviving base.

Generic surrounding rubble is then supplied by the existing ancient set-dressing system according to collapse direction and historical context.

## 9. Furnishing density and storytelling

Royal does not mean cluttered. High-status rooms should use deliberate composition: strong axial pieces, paired or mirrored secondary furniture, controlled empty floor, and detail concentrated near use zones.

A good furnished room answers several questions without text: what happened here, who used it, what status they had, what activity the room supported, and what changed during decline. If an object answers none of those questions and contributes no useful silhouette/composition, it is decoration noise and should not be selected by the generator.

Conversely, domestic residue is required. A great house containing only thrones, banners and braziers would still feel like a theme park. Beds, washstands, tea services, wardrobes, writing desks, planters, cabinets and ordinary seating are what make the monumental architecture read as a place people actually lived.

## 10. Production waves

**Wave A — identity primitives** builds the highest-reuse pieces first: lineage stele, highback chair, audience bench, writing desk, tall cabinet, canopy bed, wall sconce, mana brazier, wall banner, carpet runner, lidded amphora, goblet service, astrolabe, balustrade, finial, pedestal planter and weapon rack. These are enough to materially improve the Greatbole court and the first near-ring ruin while proving the model pipeline.

**Wave B — room completion** adds the majority of dining, salon, wardrobe, vanity, candelabrum, pennant, tea, scholarly, architectural and botanical pieces so full rooms can be furnished coherently rather than by repeating Wave A.

**Wave C — hero/detail** adds the largest or most specialized compositions: crown display dais, kneeling stool, council map table, jewel coffer, privacy screen, hanging lantern cluster, ceremonial drape, ceremonial bowl, map case, window lattice, conservatory stand and command standard.

Implementation proceeds family-by-family inside a wave. A family is not accepted because one attractive intact model exists; its placement metadata and decline state must exist with it.

## 11. Validation gates

Design acceptance requires the catalog to parse, contain exactly 12 four-member families / 48 unique semantic assets, use only the canonical condition vocabulary, declare room compatibility and house affinity for every asset, keep progression objects and persistent-entity props out, and bridge rather than duplicate the existing Royal bench/brazier prototypes.

Static implementation acceptance will require registration and model JSON validity, four-way orientation where applicable, source-to-generated equality, deliberate collision/occlusion, no missing-texture references, intact plus meaningful decline coverage, an atlas/review sheet, deterministic house-material substitutions, and no inventory or progression behavior unless separately authorized.

Runtime acceptance requires placing the Wave A review set in a client and inspecting scale, texture density, lighting, collision, rotation, transparency, adjacency, condition readability and performance. Only then should a structure generator consume those tiles.

## 12. First structural consumers

The first consumers should be the Greatbole / ruined court connection and court detail pass, one 3K near-ring noble ruin used as the furnishing grammar prototype, and the first full great-house reliquary antechamber with adjacent public/residential rooms.

The existing 32 surface structures may then adopt relevant subsets by function. Quarries do not get royal beds because the asset library exists; they receive work/service derivatives. Shore structures receive drowned/salt-damaged derivatives. Castles, halls and shrines consume the Royal vocabulary where their historical function justifies it.

## 13. Next exact action

Implement **Wave A** as the first registered decorative/model slice, beginning with one representative object from each major representation problem: Highback Chair (custom furniture model), Wall Sconce (wall/light model), Carpet Runner (connectable modular floor tile), Balustrade Segment (connectable architectural tile), Lidded Amphora (small prop), Canopy Bed (multi-block assembly), Wall Banner (house-substitution textile), and Astrolabe (complex hero model). Validate those eight as a pipeline pilot, then complete the remaining Wave A families using the same proven model/texture/registration machinery.
