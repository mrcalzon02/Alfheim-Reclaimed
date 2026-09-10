# The Void Margins — environments, stone classes and examples

**Design expansion, 2026-09-05. Status: draft for materials; the debris terrain of §2 is built and fresh-world verified as of 2026-09-09 — see §6.**
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

## 6. Build status — the debris belt, 2026-09-09

**The margin had no debris at all, and the record above did not say so.** A client walk on
2026-09-09 reported the void generating wrongly, and the region files of the world it was walked
in said exactly how much: `shatterfields`, `prism_drift`, `rootfall` and `sepulchral_reach` had
82%, 79%, 81% and 66% of their columns with a surface at or below Y −54 — the bedrock guard slab.
Four of the six environments described in §2 were registered, given surface grammars in §3 and
given placed features, over open air. `void_verge` was no better off in kind: 75% of its columns
generated at Y 1–40, so the "broad dry plain" of §2 was a sunken basin.

### Why it was empty

`gen_void_worldgen.density()` returned a literal −1.0 for everything beyond `CLIFF`, under a note
that a 3-D debris field was unsafe because "Minecraft's cell interpolation could carry an entire
jagged splinter far beyond its pointwise mask". That premise was disproved on 2026-09-08 while
calibrating the Golden Fields terraces, and the disproof was recorded in `gen_deep_terrain` and
nowhere else: `alfheim_final` contains no `minecraft:interpolated` — the markers live inside
`alfheim_height` and `alfheim_caves` — so an expression written at that level is evaluated per
block at full resolution. The mask and the shape are read at the same block, and a fragment
cannot outrun its own mask.

### What §2's shared invariants became, in numbers

"Fragments become smaller and rarer outward. Their disappearance is part of the landscape" is now
a single ramp that every outward property derives from, so the belt cannot drift out of step with
itself. Measured statically at Y 78:

| continentalness | solid | reads as |
|---|--:|---|
| −0.865 | 59% | the attached shelves of §2, welded to the cliff |
| −0.900 | 35% | the inner debris belt |
| −0.925 | 18% | Starless Reach begins |
| −0.940 | 10% | the terminal-landing strip |
| −0.950 | 4% | last fragments |
| −0.990 | **literal −1.0** | "beyond the debris limit, zero terrain" |

The far-field guarantee is structural rather than a tuning outcome: a range choice returns −1.0,
and `check_void_geology` VG3a fails if that literal is absent or its bound moves outward.

"Regional variants along that boundary ... not six consecutive rings" is honoured by taking
character from **temperature and humidity** — the same two fields `claims()` already uses to
allocate the four laterally — rather than from distance out. Prism Drift reads sparsest at 22%
solid, Sepulchral Reach most continuous at 41%, with Shatterfields and Rootfall between them.

"Dry approach, abrupt cliff, no ocean, lava sea or submerged floor" required moving the shore
blend off `CLIFF`: the Verge shelf now holds Y 71 across its whole band and descends into the sea
only in the last sliver of its own biome, with the terrain band still strictly inside the biome
band so no ordinary biome sits over void-shaped ground.

### Verified in a fresh world

`tools/run_void_validation.py`, seed `alfheim-deep-terrain-20260905`, sites located by the probe
and force-generated. Share of columns with terrain in the debris band, against the same
measurement on the rejected world:

| environment | before | after |
|---|--:|--:|
| shatterfields | 18% | **91%** |
| rootfall | 19% | **96%** |
| prism_drift | 21% | **91%** |
| sepulchral_reach | 34% | **74%** |
| void_verge (Y 70–95) | 13% | **86%**, median Y 71 |

One defect the first fresh world found and the static model could not: with the envelope's upper
edge spanning only 14 blocks it was far steeper than the fragment noise and therefore decided
every top — 74% of Shatterfields columns came back at exactly Y 92. A belt planed to one height
is a table, not a break. The fall now spans 40 blocks and carries a bounded low-frequency offset,
so the belt has a skyline; `CEILING_WANDER` is declared and VG3c fails if any offset exceeds it.

### The belt as landforms, and the threshold that had to move

Terrain coverage alone said the belt was working. Measuring it as *landforms* said it was not.
`tools/probe_void_fragments.py` reads generated chunks as 4-connected patches, and at the first
tuning it found **103,440 of 103,937 void columns in a single connected mass welded to the
Verge**, against 413 columns of detached debris in 23 specks, none more than 31 blocks from
solid ground. That is a shelf with a ragged edge, not §1's "attached shelves give way to
detached blocks, smaller fragments and finally empty space".

The cause was the solidity threshold. Correlated noise percolates far more readily than an
uncorrelated fraction suggests, so a belt that is 35–60% solid is simply one landmass with
holes. `CUT_INNER` went from −0.18 to 0.30 and `CUT_TERM` from 0.46 to 0.62, and the belt came
apart. Coverage at the settled values, over a 384-block patch at each located site:

| biome | columns | with terrain | median surface |
|---|--:|--:|--:|
| void_verge | 76,146 | **98%** | Y 71 |
| sepulchral_reach | 3,295 | 65% | Y 68 |
| shatterfields | 4,080 | 48% | Y 63 |
| prism_drift | 4,127 | 45% | Y 63 |
| rootfall | 1,901 | 36% | Y 74 |
| starless_reach | 143 | 69% | Y 63 |

### Three separated rim segments, as §5.7 asks

| segment | mainland | islands | clearing 14×14 | furthest island |
|---|--:|--:|--:|--:|
| shatterfields | 5,295 cols, 93×124 | 31, median 32, largest 4,230 | 2 | 156 blocks |
| prism drift / verge | 15,913 cols, 272×252 | 39, median 16, largest 13,989 | 2 | 161 blocks |
| rootfall / starless | 11,101 cols, 216×176 | 73, median 33, largest 5,541 | 4 | 264 blocks |

Each segment is one broad landmass with a scatter of detached islands around it, several of
them large enough to carry a structure. No segment is a single fragment spanning the sampled
region, so the "accidental walkable road" §2 warns about has not appeared.

### Still open

### The terminal landing: surveyed, and the contract is the thing that does not fit

**Asked and answered 2026-09-10.** `check_void_surface_support` reserves continentalness
−0.94…−0.925 for `last_watch` and `starless_orrery` at 1,800 solid blocks and 14×8×14. The first
verification pass could not tell whether that was satisfiable, because Starless Reach occupied
143 columns of a 384-block patch against the Verge's 76,146. A density edit cannot answer it —
that is a property of the continentalness field — so `tools/void_landing_probe.js` asks the
field directly, over a 24,576 × 24,576 block survey:

| | |
|---|--:|
| lattice points sampled | 148,225 |
| inside the reserved band | 309 — **0.21%** |
| with a 15×15 neighbourhood ≥72% in band | **10** |

So the band exists and occasionally widens. The six best were force-generated and measured:

| candidate | continentalness | persistence | terrain found | 14×14 landing touching the band |
|---|--:|--:|---|---|
| 6144, −7680 | −0.9335 | 86% | 603-col mainland, 10 islands | none |
| −5568, 4608 | −0.9344 | 83% | 3,241-col mainland, island of 906 | none |
| 576, −2112 | −0.9310 | 83% | 1,103-col mainland, 26 islands | none |
| 64, −6016 | −0.9270 | 81% | 1,259-col mainland, island of 1,161 | none |
| 3200, 1984 | −0.9305 | 75% | — | **2,691 cols, a 16×16 square, touching by 5 columns** |

**There is substantial ground out there — mainlands of 600 to 3,200 columns and islands past
1,100 — but a 14×14 landing lying WHOLLY inside −0.94…−0.925 did not occur at any of the six.**
That is not a failure of the belt. Terrain that far out is sparse because §2 requires it to be:
"only isolated small pieces remain", "no deposits, ore features, geodes or structures in the
guaranteed-empty far field". A 1,800-block landing needs exactly the density the design forbids
there, so the requirement and the design pull against each other.

**And §2's own wording suggests the contract is what is mis-set.** It says the player sees a
final Astralite fleck *"from the last substantial landing"* — the landing is the last solid
ground, and the fleck is what lies beyond it. That places the landing at the INNER edge of
Starless Reach, around −0.930…−0.925, with the empty field outward of it. The 2,691-column
fragment at (3200, 1984) with a 16×16 buildable square, touching the band at continentalness
−0.9305, is a good description of that scene.

**This needs a decision, not a tune.** Either `check_void_surface_support`'s host contract for
those two structures changes from "wholly inside −0.94…−0.925" to "clears 14×14 and touches the
band", or the two structures move to the inner debris belt where hosts are plentiful — the
shatterfields and rootfall segments each carry two to four fragments clearing 14×14. Making the
terminal band dense enough to satisfy the contract as written would contradict §2, and no
density edit should be attempted for it. A `landing_swell` term tried on 2026-09-09 for exactly
that purpose measured as a no-op and was removed the same day.
- The eighteen stone classes of §3 remain a proposal; the belt currently wears the grammars in
  `void_catalog.json` over existing Livingrock.
- Client traversal: nobody has walked any of this.
- **The approach is still across water.** The biome bands run land → ocean → verge → debris, so
  the Verge is reached by sea rather than by the dry country §1 describes. That is the standing
  `DEFICIENT_BIOMES.md` rejection, it needs the biome geography reordered rather than the density
  adjusted, and nothing in this build addresses it.

The four-band values in `DEFICIENT_BIOMES.md` remain the initial tuning reference. They are climate
signal bands, not fixed distances in blocks; do not promise a particular walk or gap length from
those numbers alone. No extra dimension, world-height change or far-field island generator is
authorized by this design expansion.
