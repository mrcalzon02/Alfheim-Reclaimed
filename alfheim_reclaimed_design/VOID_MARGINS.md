# The Void Margins — environments, stone classes and examples

**Design expansion, 2026-09-05. Status: draft, ready for material prototyping.**
Requested scope: extend the definition of the Void Verge and related void biomes, give concrete
examples, and define their own custom stone classes. This record and its companion catalog are
design artifacts; they do not register new biomes, blocks or mechanics.

Companion concept board: `void/void_margins_concepts.png`, generated with the built-in image tool.
The exact saved prompt is `void/concept_prompt.txt`. Swatches run left-to-right in the same
order as the three stones in each environment's table row. They are visual direction, not final
16-pixel block textures; the Oathstone swatch illustrates its carved finish.

`DEFICIENT_BIOMES.md` retains authority over the dry-rim repair. Its current **runtime rejected**
status remains: preserving the Void branch during Deep development did not repair the rejected
water-filled edge. This expansion must be built on that repair, not on an ocean disguised by fog.

## 1. What the void means in Alfheim

The Deep is where the lost mana accumulated. At the Void Margins, the connections that held the
world together failed. What remains is unusually dense material stranded at the edge of absence:
stone with compressed seams, exposed mineral cores, petrified roots and fragments of elven works.

The player should understand the danger before reaching it. Ordinary country becomes a dry,
open Verge plain; its last solid ground ends in a fractured cliff. Attached shelves give way to
detached blocks, smaller fragments and finally empty space. Distance removes footing. Mineral
richness rewards careful expeditions into the remaining rock, not an endless supply of islands.

The six environments below are **regional variants along that boundary**. They are not six
consecutive rings that stretch the debris belt indefinitely. Rootfall and Sepulchral Reach can
occupy different stretches of the same rim; Prism Drift can be a small mineral pocket within it.
Starless Reach is the terminal fringe and empty far field. Beyond the debris limit, every variant
must converge to zero terrain and zero generated structures.

Shared invariants:

- Dry approach, abrupt cliff, no ocean, lava sea, submerged floor or routine obsidian patches.
- Broad safe approach land; open space dominates beyond the breakline.
- Fragments become smaller and rarer outward. Their disappearance is part of the landscape.
- Existing native ore and crystal processing remain authoritative. Decorative stones do not
  become interchangeable sources of Elementium, shards, quartz, mana or progression materials.
- The main danger is footing. Sparse existing encounters can inhabit adequate ground; do not
  fill tiny landing fragments with unavoidable combat or introduce new mobs for this pass.

## 2. Six environments

| Environment | Dominant silhouette | Stone signature | Example worth finding |
|---|---|---|---|
| **Void Verge** | Broad dry plain ending at a broken wall of land | Riftchalk, Riftshale, Veilstone | A survey stair and shattered parapet overlooking the first detached slabs |
| **Shatterfields** | Angular slabs and pressure-fractured remnants close to the rim | Shardbreccia, Anchorstone, Seamstone | A Severed Span anchored in a surviving abutment |
| **Prism Drift** | Sparse mineral-rich remnants with small rooted crystal crowns | Prismstone, Aetherquartzite, Glintschist | A Duskglass–Galeglass seam exposed through a split fragment |
| **Rootfall** | Petrified root undersides and broken woodland ledges | Rootfossil, Resinshale, Hollowheart | The stone roots of a vanished garden beneath a collapsed arch |
| **Sepulchral Reach** | Quiet stable shelves with cut burial faces and fallen memorial slabs | Epitaph Marble, Mourning Slate, Oathstone | A sealed royal tomb still embedded in the cliff |
| **Starless Reach** | Last tiny fragments disappearing into almost entirely empty space | Nightmantle, Nullstone, Astralite | A final exposed mineral fleck visible from the last substantial landing |

### Void Verge — the readable edge

**Terrain:** the existing `alfheim:void_verge` ID remains the safe rim biome. Its land is
plains-like, gently uneven and visibly dry, with sparse ground cover and occasional exposed stone.
Near the edge, shallow shear cracks reveal layered stone without turning the approach into a
maze of concealed pits. The last cliff face is steep, broken and unmistakable.

**Material balance:** Riftchalk supplies the pale bulk, Riftshale marks shear faces, and Veilstone
appears as restrained grey seams and architectural trim. The darker void remains readable behind
the pale lip. Avoid a fully black approach that conceals where the ground ends.

**Example:** a player crosses a pale clearing and reaches an old survey stair. Its last landing
is intact; beyond a broken parapet, a familiar Livingrock seam continues across three detached
slabs. The first slab is substantial. The third is visibly too small to carry a building.

**Structures:** approach markers, survey steps and supported abutments. No structure should
project a complete new island into the empty band simply because its template includes a floor.

### Shatterfields — the rock remembers the break

**Terrain:** the inner debris belt has angular wedges, exposed fault faces, split slabs and a few
short attached shelves. Most fragment volume stays close to the cliff. Broad horizontal slabs and
narrow upright remnants should coexist, but the field must not form an accidental walkable road.

**Material balance:** Shardbreccia is visibly made of interlocked broken pieces. Anchorstone forms
dark competent cores and structural bases. Seamstone traces the edges where mana rejoined cracks.
The differences are fracture size and layering as much as color.

**Example:** the existing Severed Span becomes a scene with a reason: its surviving approach sits
on Anchorstone, then the bridge ends where a Shardbreccia shear plane removed the far abutment.
A seam is visible on a nearby landing, giving the player a concrete expedition target.

**Traversal:** visible gaps, predictable solid landings, routes the player builds. The name
Anchorstone does not imply a gravity anchor, fall protection or automatic structural stability.

### Prism Drift — mineral interiors laid open

**Terrain:** an uncommon pocket in the inner/middle debris band, with a few intact mineral
remnants separated by conspicuous empty gaps. Crystals grow from surviving cores. Crowns stay
smaller than their host rock; tiny fragments can carry exposed inclusions, not full geodes.

**Material balance:** Prismstone has fine pale mineral boundaries with occasional spectral seams;
Aetherquartzite is a denser frosted blue-white fabric; Glintschist has directional mica-like flakes.
Color must not turn every rock face into a luminous crystal block.

**Example:** a split remnant exposes the boundary between Duskglass and Galeglass. The player can
see both alignments from the rim. One face offers an ore seam; the substantial rear core supports
a small crystal pocket. Mining the decorative host does not yield crystal shards.

**Resources:** preserve the authored Rim pairing, Duskglass | Galeglass. Its currently configured
1-in-8-chunk attempt rate is historical placement data, not a guarantee of eight-chunk spacing or
proof of suitable host volume. New placement must check the supporting solid volume first.

### Rootfall — the underside of a lost woodland

**Terrain:** broken forest shelves with petrified root forms exposed beneath them. Roots belong
to the surviving rock, with tapering ends where the rest was lost. They must not generate as an
independent hanging forest across open void. Occasional trunk sockets tell where a tree once stood.

**Material balance:** Rootfossil follows grain and growth rings; Resinshale carries small amber
lenses inside laminated grey stone; Hollowheart has visible pores and root cavities. They remain
stone to mine, not free wood, resin or sapling sources.

**Example:** a garden arch stands on the last broad shelf. Looking underneath reveals enormous
stone roots ending in empty space. An old irrigation channel is dry. A broken root cross-section
contains a mineral seam, connecting the botanical history to an ordinary mining reward.

**Structures:** fragments of root shrines, garden supports and archive terraces. Preserve enough
ground for an intentional path; ornate structure detail cannot substitute for a valid anchor.

### Sepulchral Reach — the kings at the world's edge

**Terrain:** stable inner shelves, ledges with intact backing rock and occasional fallen memorial
slabs. This is a quiet lateral pocket of the rim, not a city of tomb islands. Burial chambers remain
inside the land. A cliff-facing entrance may overlook the void while its chamber stays supported.

**Material balance:** Epitaph Marble provides ivory walls with hairline grey-violet veining;
Mourning Slate gives dark layered floors and borders; Oathstone is competent grey stone whose
crafted form carries interlaced elven carving. Raw Oathstone must not look naturally engraved.

**Example:** a sealed burial facade faces the absent homeland. One intact memorial records a
king's name; two matching memorial slabs lie on a lower shelf. The open view provides atmosphere,
while the sealed room and its single significant, era-appropriate reward preserve the Tomb design.

**Structures:** integrate with the existing Tomb family rather than inventing a parallel dungeon
system. Decorative masonry may be collected; special tomb rewards must still obey spine gating.

### Starless Reach — the end of the material field

**Terrain:** at the terminal debris fringe, only isolated small pieces remain. Farther out, there
is no rock at all. This region can be visually distinct without producing terrain: sparse ambient
particles and restrained sky/fog establish it. Avoid particles so dense they resemble a floor.

**Material balance:** matte Nightmantle, porous Nullstone and sparse pinpoint Astralite inclusions
occur only in the last surviving fragments, preferentially on faces exposed toward the void.
There are no deposits, ore features, geodes or structures in the guaranteed-empty far field.

**Example:** from the last substantial landing, the player sees a dim Astralite fleck in a small
fragment. Beyond it, there is visibly no next landing. This is a readable endpoint, not bait for
a procedural island that the player assumes must exist farther away.

**Mechanics:** Nullstone is a material name, not implemented anti-magic. Astralite does not negate
gravity. No arbitrary random teleportation, inventory loss or hidden debuffs belong to this pass.

## 3. Eighteen custom stone classes

Here **class** means a material family: its natural texture, geological role and matching masonry.
It does not mean eighteen new Java block implementations. The existing KubeJS stone/shape builders
should handle the initial mechanics. The source catalog is `void/void_catalog.json`.

| Stone family | Texture and structure | Building example |
|---|---|---|
| Riftchalk | Pale granular stone, broken edges rather than large cracks | Bright rim parapets and survey stairs |
| Riftshale | Thin grey lamination and offset shear faces | Layered bridge abutments and roof slabs |
| Veilstone | Mist-grey fine fabric with sparse lilac seams | Observatory trim and quiet sanctuary walls |
| Shardbreccia | Angular light fragments in a darker matrix | Rough ruin walls and heavy retaining faces |
| Anchorstone | Dense dark grey fabric with broad pressure folds | Tower bases, piers and robust-looking columns |
| Seamstone | Fine repaired seams across cracked grey-lilac rock | Restrained glowing joints and carved boundary markers |
| Prismstone | Pale interlocking mineral boundaries with spectral seams | Crystal-gallery floors and patterned inlay |
| Aetherquartzite | Frosted blue-white interlocked grains, low porosity | Pale lintels and scholar-hall columns |
| Glintschist | Directional silver flakes in cool grey layers | Roofs, steps and softly reflective wall panels |
| Rootfossil | Petrified branching grain and distinct end-grain rings | Root-shrine pillars and botanical arch bases |
| Resinshale | Thin amber lenses within grey-brown lamination | Warm archive trim and memorial bands |
| Hollowheart | Pale porous stone with occasional larger root cavities | Weathered garden walls and grotto masonry |
| Epitaph Marble | Ivory matrix with fine grey-violet veins | Royal burial vaults and civic memorials |
| Mourning Slate | Blue-charcoal layered stone with clean cut edges | Tomb floors, borders and dark roofwork |
| Oathstone | Competent cool grey natural stone; interlace only when carved | Seals, ceremonial doorframes and civic lintels |
| Nightmantle | Matte black-blue stone with broad subdued fractures | Observatory backs and dark contrast walls |
| Nullstone | Porous charcoal fabric with discontinuous pale inclusions | Ruined foundations and weathered accent masonry |
| Astralite | Indigo-grey matrix with sparse pinpoint silver inclusions | Star-vault ceilings and fine border inlay |

Each family is planned to have natural, polished, bricks, carved, slab, stair and wall forms:
**18 families × 7 forms = 126 proposed blocks**, separate from the existing 175-block Deep library.
Slabs, stairs and walls initially use the matching brick fabric. Rootfossil's raw growth direction
may justify an axis-aware block later; that is a separate model/placement task, not assumed here.

First-pass mechanics: pickaxe mining, self-drop, two drops for a double slab, no gravity, random
ticks, fluid emission, contact damage or passive resource production. Most light levels are zero;
the catalog proposes low light only for sparse seam/inclusion families. A pale or reflective stone
need not emit light. Polishing removes roughness without erasing material identity.

For decorative availability outside the void, follow the current Livingrock-library convention:
stonecut native Livingrock into natural family blocks, then cut their masonry forms. This is a
proposed 126-recipe catalog, including 1:2 slabs, not shipped recipes. It intentionally makes
ordinary building access independent of surviving the rim. Rare exploration rewards must be actual
native deposits, crystal finds and era-appropriate archaeology, not inaccessible basic building colors.

## 4. Practical example palettes

**A Verge Spire:** Anchorstone foundations, Riftchalk walls, Glintschist roof and a few carved
Veilstone bands. One substantial inner remnant supports the whole footprint. The tower does not
spawn a replacement island. Keep its silhouette slender enough to preserve the scale of the void.

**A Rootfall garden:** Rootfossil supports, Hollowheart retaining walls, Resinshale edging and
existing Moss/Fern Livingrock from the Deep library. This is a shared elven material culture, with
the void's fossil textures adding history rather than replacing every familiar stone.

**A king's cliff tomb:** Epitaph Marble and existing Ivory Livingrock walls, Mourning Slate floors,
Oathstone carved door, a very narrow Astralite border. The tomb is sealed into the cliff; a small
lookout landing provides the view. The reward design stays with the existing Tomb progression.

**A restored surface observatory:** ordinary Moonstone masonry, Aetherquartzite columns,
Nightmantle instrument backing and Astralite ceiling inlays. These stones remain useful back in
the homeland, which is the reason to author complete construction families.

## 5. Implementation boundaries and order

1. Prototype the 18 raw stones and four full-block finishes; inspect grain, contrast and tile seams.
   Reuse proven shape builders for the remaining forms, with registration/loot/recipe tests.
2. Repair the current dry Verge: safe shelf, hard cut, matching fluid mask and debris that fades
   to zero. Do not propagate the currently rejected wet rim into five additional biome IDs.
3. Introduce shared `alfheim:void_biomes` membership before adding sub-biomes. Existing Deep
   exclusions currently name `alfheim:void_verge`; they must exclude every new void member.
   Terrain and aquifers must still share one rim signal, with the Deep restricted to surviving land.
4. Allocate the variants laterally with coherent region noise inside the existing rim/debris
   envelope. Reuse `alfheim:void_verge`; the five other IDs in the catalog are proposals, not live.
5. Add geology to surviving solids only. Use narrow void-host tags and preserve native ore routes;
   do not broaden vanilla replacement tags or generate block masses to support a failed ore feature.
6. Enable volume-checked resource formations and then supported structures. The existing Verge
   Spire and Severed Span are design anchors, not evidence that void placement is already accepted.
7. Sample at least three separated rim segments in fresh worlds. Check dry space below sea level,
   cliff readability, outward falloff, terminal zero terrain, support volumes and Deep compatibility.
   Client traversal and visibility remain required alongside headless block measurements.

The four-band values in `DEFICIENT_BIOMES.md` remain the initial tuning reference. They are climate
signal bands, not fixed distances in blocks; do not promise a particular walk or gap length from
those numbers alone. No extra dimension, world-height change or far-field island generator is
authorized by this design expansion.
