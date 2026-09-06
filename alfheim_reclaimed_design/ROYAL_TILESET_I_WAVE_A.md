# Royal Tile Set I — Wave A implementation

**Role:** implementation record for the first eight-object pilot selected by `ROYAL_TILESET_I.md`.

**Status:** **static source/generated validated**. Registration and model source exists and reproduces byte-for-byte. Minecraft/KubeJS startup, client rendering, collision, rotation, seams, and visual acceptance are still pending.

**Manifest:** `tools/royal_tileset_wave_a_manifest.json`  
**Generator:** `tools/gen_royal_tileset_wave_a.py`  
**Checker:** `tools/check_royal_tileset_wave_a.py`

## 1. Implemented semantic assets

The pilot implements the eight deliberately different Wave A test cases selected by the parent design:

- Royal Highback Chair — single-block directional furniture;
- Royal Wall Sconce — wall-mounted directional light with glass/glow geometry;
- Royal Carpet Runner — low directional textile tile;
- Royal Balustrade Segment — directional architectural ornament intended for repeated runs;
- Royal Lidded Amphora — small freestanding household/ceremonial vessel;
- Royal Canopy Bed — six-module 2x3 furniture assembly;
- Royal Wall Banner — directional heraldic textile;
- Royal Astrolabe — four-module 2x2 scholarly hero object.

These eight semantics compile into **16 physical block registrations** because the bed and astrolabe are deliberately modular. Internal assembly modules have no item form and exist for structure/room assembly, not creative-tab clutter.

## 2. Model and material contract

Wave A uses custom JSON block geometry rather than pretending full cubes are furniture. All model elements remain inside the legal local 0..16 block-model volume. The pilot deliberately reuses already-installed material textures so geometry can be admitted independently of a later bespoke texture pass:

- Botania Dreamwood planks/log for Royal timber;
- Botania Elementium block for refined metalwork;
- Botania elf-glass frame 0 for magical glass;
- vanilla quartz faces for pale stone/ceramic;
- purple/magenta textile stand-ins for the house-substitution layer;
- sea lantern for contained luminous cores.

Those texture choices are a **pilot skin**, not the final six-house palette. The permanent house system remains substitution-driven: accepted geometry is reused while heraldry, textile borders, inlays, glass tint and glow tint differentiate houses.

No new PNG is required for this pass. That is intentional: the model pipeline and silhouette can be accepted or rejected before bespoke art multiplies the cost of revision.

## 3. Rotation and structure safety

Every physical Wave A block uses KubeJS's `cardinal` builder and an explicit shared `royalOrient` callback. The callback updates horizontal facing on both structure rotation and mirror operations. This is required because future jigsaw/NBT placement can rotate room pieces; decorative blocks must rotate their visible model and collision with the room rather than retaining authoring orientation.

Directional collision boxes are authored in the north-facing local frame and are rotated by the cardinal block implementation. The checker requires every physical registration to remain cardinal and requires both rotate and mirror callbacks to remain present.

## 4. Gameplay boundary

Wave A is scenery infrastructure, not progression:

- no Fey Stone or progression object;
- no recipes in the pilot;
- no block entities;
- no inventories;
- no persistent display entities;
- no loot ownership;
- no quest completion behavior.

The visible storage/display language remains decorative until a structure explicitly places a separately governed loot or interaction point.

## 5. Generated review surface

`alfheim:royal_tileset_wave_a/review` is a disposable review function that places the six stand-alone examples, the complete 2x3 canopy bed and the complete 2x2 astrolabe. It is not worldgen and is not called automatically.

After a client restart, run:

`/function alfheim:royal_tileset_wave_a/review`

in a disposable flat review area. Inspect silhouette, scale, texture mapping, facing, collision, wall attachment, repeated balustrade/carpet seams, six-piece bed continuity, four-piece astrolabe continuity and lighting. Rotate/mirror through structure placement before runtime acceptance so the jigsaw use case is tested rather than assumed.

## 6. Static evidence

Observed in the source workspace before repository admission:

- `python tools/check_royal_tileset_wave_a.py` -> `ROYAL TILESET WAVE A: PASS semantics=8 blocks=16 generated=20`;
- `python tools/gen_royal_tileset_wave_a.py --check` -> `20 files byte-identical`;
- Python compilation of generator/checker -> pass;
- Node syntax check of `21_royal_tileset_wave_a.js` -> pass;
- all generated model/tag JSON parses -> pass.

These checks establish the **static source/generated contract only**. They do not prove KubeJS accepts the registrations on this installed build or that Minecraft renders/collides with them correctly.

## 7. Next exact action

Restart the client and inspect the Wave A review grid. Reject or revise weak geometry before producing bespoke Royal textures or expanding the remaining 40 semantic assets. Once these eight are visually accepted, apply the same pipeline to the rest of Wave A and begin using accepted Royal tiles in the Greatbole/court refinement rather than creating one-off decoration there.
