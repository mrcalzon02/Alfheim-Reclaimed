# Natural gems and geologist displays — 2026-10-17

The first catalogue contains **232 natural gem materials**: mineral species and
varieties, ornamental rocks, organic materials and gem-bearing fossils. It
includes common jewellery stones and rare collector materials. It is a broad
working baseline, not an assertion that every historic trade name or every
mineral ever faceted has been exhausted. Synthetic products and duplicate
synonyms are not added as separate natural deposits.

Five existing item identities are reused: diamond, emerald, amethyst shard,
quartz (rock crystal) and lapis lazuli. The other 227 gem items are additive.
The authored catalogue and aliases live in `tools/gemstone_catalog.py`;
`tools/gemstone_catalogue.csv` lists all items and their sources. Naming follows
the [GIA Gem Encyclopedia](https://www.gia.edu/gem-encyclopedia), its collector
gem studies, and the natural-material distinctions in the
[CIBJO Gemstone Book](https://cibjo.org/wp-content/uploads/2023/01/22-12-22-Official-Gemstone-Book.pdf).
No source's treatment charts, images or prose are reproduced.

## Distribution

Alfheim's home-world biomes receive 28 source pools across Y −60 through 280.
These are authored game altitude bands and weighted discovery pools, not
claims that real-world geological formation obeys Minecraft Y coordinates or
that all gems sharing a pool actually co-occur in nature.

| Source | Example finds | Search area |
|---|---|---|
| Deep seams | Diamond varieties, garnets, peridot, corundum | Deep and lower-middle rock |
| Crystal pockets | Beryl, quartz, tourmaline, topaz, spodumene | Middle-depth and upper rock |
| Highland deposits | Feldspar, collector crystals, phenomenal quartz | High exposed terrain and high stone |
| Woodland soil/fossils | Amber, copal, jet, petrified wood | Forest soil, buried wood and coal-bearing beds |
| Mineralized fossil beds | Ammolite, agatized coral, fossil ivory/bone | Buried rock |
| Marine beds/growth | Marine pearls, nacre and precious coral | Underwater ocean/shore beds |
| Freshwater mussel beds | White, cream and pink pearls, nacre | Underwater lakes and wetland beds |

There are 1,040 deposit blocks, mostly host-matched variants covering all 42
authored natural stones plus Livingrock, stone and deepslate. Original
transparent gem overlays reference each host texture without copying or
recolouring third-party stone art. Replacements target listed natural hosts;
crafted bricks, tiles and Titan flesh are not targets. Organic deposits have
their own soil/fossil or modelled shell/coral sources. Aquatic placement checks
both water and a solid seabed. Coral and marine-specific pearls are not placed
in the freshwater biome group.

Mineral veins are small, with rarity filters rather than dozens of attempts per
chunk. Weighted positive loot entries make every catalogue item reachable.
Silk Touch retains the exact deposit block; Fortune affects the gem yield.
Iron-level pickaxes are required for rock deposits. Existing ores, recipes and
their registration logic are retained. No new gem tools, jewellery recipes,
magical powers or trade conversion rates are implied by this resource pass.

## Rebuilt art

The rejected flat icon generator was removed. A new original master atlas was
generated with the built-in **image_gen** tool, using 32 detailed gem forms:
cut facets, raw crystals, cabochons, chatoyancy/asterism, pearls, fossils,
resin, coral and metallic specimens. The unmodified source is
`tools/art/gemstone_masters.png`; the exact prompt is
`tools/art/gemstone_masters_prompt.txt`. The tool returned 1792 × 896 artwork,
despite the requested 2048 × 1024 canvas. The compiler uses its actual 8 × 4
cell dimensions, crops and resizes into 128 × 128 transparent material sprites.

Minecraft's item-colour renderer supplies each gem's palette. Additional
material masks provide ametrine's yellow/purple split, watermelon tourmaline's
green/pink zoning, ruby/bloodstone inclusions, and opal colour flecks. The same
native shading is reproduced in the offline review sheets. The five reused
vanilla gem items retain their IDs and receive the new art as well. These are
static material illustrations, not physically simulated optical phenomena.

## Geologist displays

Added one functional glass-topped stone-and-gold pedestal with a name plaque,
blue display lining and a rotating gem sample. All 232 catalogue materials
have named, preloaded display selections in the Functional Blocks creative tab.
The common empty pedestal is craftable using three glass, five smooth stone
and a gold nugget. Preloaded selections are creative curator conveniences;
there are no survival recipes that conjure their gems.

Right-click an empty pedestal with a catalogue gem to insert one. Crouch with
an empty hand to retrieve it. Ordinary survival breaking returns the empty
pedestal and its sample. Sample NBT and display updates persist across reloads
and synchronize to clients. The plaque uses the catalogue's real-world name,
so a reused quartz item is labelled Rock Crystal. Labels render at close range
to limit exhibition rendering cost.

An optional operator function, `alfheim:debug/gemstone_gallery`, places all 232
displays in a 16-column grid. It replaces the chosen base blocks in a roughly
46 × 43-block area: invoke only in a prepared empty exhibition space. It is not
scheduled, auto-run, or executed by this change.

## Generation, evidence and limits

Executed the existing local Continuity Works `StructureCapability.generate`
through provider `alfheim_real_gemstones_v1` in `tools/gen_gemstones.py`, with
Java 1.20.1/Forge as target and deterministic icon/source generation. Actual
snapshot, output hashes and existing-registry probes are in
`tools/gemstone_generation.json`. These are small worldgen features, not
independent structures; no structure reservation/exclusion policy is changed.
New KubeJS IDs are source declarations pending actual startup registration.

Static checks resolve all biome, texture, reused-item and host references,
unique registrations, loot reachability, Silk Touch/Fortune, display roster,
placement bounds and exact generated-source equality. The merged pack-wide
feature-order check found **zero cycles**, including Forge modifiers. Java 17
offline compilation and packaging passed with tests excluded. The startup
script also passed JavaScript syntax checking. Native models and revised art
were reviewed in offline previews, not screenshots from Minecraft.

Build/install hash and source evidence: `tools/gemstone_build.json`.
Full startup, mining drops, natural density, live tint/rotation/labels and
multiplayer item interactions still require an in-game check. This is locally
validated, not production admitted. Restart Minecraft to register the new
items, blocks and native renderer. Explore newly generated chunks for deposits;
existing chunks are not retrofitted. No third-party mod jar was changed.
