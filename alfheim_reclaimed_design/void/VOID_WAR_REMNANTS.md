# The war at the end of the world

## Intent

These are the remnants of a magical civilization locked in a war it could neither
win nor retreat from. Its crystalline defenders lie gutted at the feet of the dead
biomass titans they fought. Extracted cores, torn conduits, dismembered armor, broken
ribs, collapsed organs and sloughed hide tell the encounter without a living boss.
The final defensive works continue beneath the battlefield: broken wards, medical
stations, deserted barracks, magazines, ossuaries and labyrinths of abandoned orders.

User-confirmed habitats are **only `alfheim:void_verge` and `alfheim:void_shore`**.
The five other Void Margin sibling biomes are outside this family's tag. Broad
terrain, biome masks, density, aquifers, bedrock and player saves are not edited.

## Eight sites

| Family | Surface identity | Underground | Footprint |
|---|---|---|---|
| Last Bulwark | breached gate, keeps, barracks and failed artillery wards | magazines and defensive labyrinth | 141×141 |
| Abandoned War Encampment | ruined tents, supplies, field hospital and shattered limbs | deserted barracks and medical passages | 141×141 |
| Shattered Ward Fortress | broken fortified perimeter, empty conduits and artillery scars | ward vaults, ossuary and linked military maze | 141×141 |
| Titanfall Battlefield | a hollow crystal golem immediately beside its dead biomass adversary | dissection galleries and war hospital | 141×141 |
| Crystal Execution Ground | two gutted crystal hulks flanking a desiccated titan | severed ward chambers and salvage magazines | 141×141 |
| Rotting Colossus Redoubt | ossified and desiccated titans around a defeated crystal chassis | anatomical galleries and bone vaults | 141×141 |
| War Rift Redoubt | compact, breached surviving outpost | connected muster atrium and descent | 47×47 |
| Buried War Bastion | compact ossuary outpost with a dead-core reliquary | bone-lined muster atrium and descent | 47×47 |

Each large site is one coherent **18-piece family**, not eighteen independent
structure starts: nine surface modules and nine basement modules. Eight maze tiles
provide 200 reachable chambers around one shared stair atrium. Small sites use two
pieces. The adjacent golem/titan modules are parts of the same battlefield and
intentionally share its reservation; the corpse components do not receive scatter sets.

Twenty-five templates stay inside Minecraft's 48-block editing envelope. Four
aligned floor-level portals connect every basement tile. A continuous 24-step,
three-block-wide descent joins the surface opening to the atrium, with three blocks
of headroom and a restored bridge carrying the surface crossroads over the shaft.
The native piece order is surface first, basement second, so the stair landing and
bridge survive placement. Functional routes are reserved before furnishings.

## Material library

`kubejs/war_remains_catalog.json` inventories **32 actual registered blocks**, each
with three deterministic 32×32 pixel texture variants (96 textures total):

- Five sludge states: saturated, coagulated, putrefied, desiccated and mineralized.
- Four flesh states: fibrous, necrotic, putrescent and desiccated.
- Three organ materials: exposed, liquefied and calcified.
- Five hides: pallid, bruised, charred, sloughed and petrified.
- Four skeletal materials: bone, fractured bone, exposed marrow and ossified cartilage.
- Sinew and torn ligaments.
- Six dead-crystal materials: fractured, scorched and Void-scarred crystal, lattice
  fragments, an empty core socket and severed conduits.
- Bulwark masonry, fractured ward plates and scorched masonry.

Sludge and decay states are stable decorative blocks without fluid or decay ticks.
Ordinary harvesting returns their block items. The cube models inherit vanilla
geometry, avoiding overlapping custom-model faces. The crystal torsos own explicit
air cavities where active cores were ripped out; salvage contains no active cores.
Titan bodies have ruptured flanks, irregular broken ribs, curved spines, exposed
organs and detached limbs. Desiccated and ossified versions use distinct palettes
and tear patterns rather than merely renaming the same template.

The two encounter-room modules use the existing biome skeleton and biome endermite
types. Each spawner produces two at a time, caps four nearby, waits 400–800 ticks,
and activates within twelve blocks. No creepers are added. Corner wards are spent
non-emissive plates; the remaining central floor light is sufficiently far away
to leave encounter rooms dark. Combat balancing and client inspection remain gates.
Caches return small quantities of decorative war salvage, not progression items.

## Placement and support

The eight registrations share one **192/128-chunk grid**, salt 202610153, with a
5,000-block origin exclusion. A deterministic seed/cell selector admits one family
before terrain probing. Wide biome corners select the six large profiles; narrower
sites select one of the two compact profiles. There is no relocation search or
fallback to another terrain region. Other family entries reject before height work.

The accepted profile samples **25 fixed terrain columns**, with surface Y60–160,
at most six blocks of relief, dry surface, dry solid floor and roof bands, and at
least 23 solid blocks in the measured 28-block host. Basement origins remain Y>=32,
above the documented Deep density envelope. The entire horizontal noise-biome
footprint is checked at both occupied strata: 2,592 footprint cells for a large
site, plus the bounded center and family-selection queries. The operator's
`biome_queries` counter counts its center/footprint checks; selection is separate.
Empty, steep, water-covered, insufficiently backed and biome-crossing sites fail.
Templates add local foundations on existing hosts; they do not create rescue islands.

Six existing frontier neighbors retain their vanilla layouts under a reservation
wrapper: Verge Spire, Severed Span, Edgewatch Beacon, Strandline Hulk, Thorn Gate
and Shore Memorial Court. Those and the pack's allocated archaeology/ley corridors
yield to an eligible war-grid reservation within 900 blocks on both axes. A 256-block
legacy reservation plus a 70-block war radius leaves a conservative **574-block gap**.
War sites themselves have at least 1,907 blocks between footprints. Other independent
Void-eligible sets retain conservative reservations. Unrelated non-Void surface
structures across biome boundaries need broader compatibility review; this scoped
adapter does not establish universal pack-wide spacing.

Reservations may remain empty when the host fails, bounding work and avoiding
generation-order dependencies. The inverse guards protect future generation;
previously generated neighboring ruins are not retroactively moved. Mixed old/new
chunk boundaries require a separate audit. The approved bounded harbor fitter is
unchanged, and the upper-rock adapter only reserves eligible Void war candidates.

## Reproducibility and evidence

- `tools/gen_war_remains_materials.py`: material registry/assets and review sheet.
- `tools/gen_void_war.py`: actual Continuity Works 0.3.2 provider, snapshots, exact
  registry probes, deterministic templates, family matrices and native layout source.
- `tools/void_war_registry_report.json`: real Forge registry evidence for all 32 IDs.
- `tools/void_war_generation_report.json`: emitted hashes, templates, matrices and CW snapshot.
- `tools/check_void_war.py`: room/portal graph, stair/bridge joins, empty cores,
  fixture/entity/loot IDs, material models, registration and source/layout gates.
- `tools/run_void_war_validation.py`: disposable registry, bounded survey, gallery
  and natural-start proof. It never edits a player world.
- `tools/void_war_runtime_report.json`: authoritative final runtime results and hashes.

The source voxel previews in `tools/void_war_colossi_review.png` and material sheet
are design renders, not Minecraft screenshots. Native/gallery acceptance is separate
from client rendering, traversal and combat acceptance. No successful generator or
preview is presented as proof that every family has been naturally observed.

## Accepted bounded runtime sample

Minecraft 1.20.1 / Forge 47.4.10, seed 3536368297089363045, disposable world
`validation-void-war-final-20261015`:

- Shattered Ward Fortress: full 18-piece natural start at surface origin
  [-12270,76,-27022], in saved Void Shore biome data.
- War Rift Redoubt: two-piece natural start at [52657,84,-36511], in saved Void Verge.
- All 2,880 occupied-stratum biome cells across both footprints belong to the
  allowed biomes. Native origins/bounds, two continuous 24-step stairways, headroom
  and bridges pass; two spawners and eight cache records retain their intended data.
- Natural samples: 3,619/3,629 exact block matches. All ten remaining samples are
  expected native Cinderbloom/Verdigris ores replacing Riftshale foundation cells
  during the subsequent ore-feature pass. Unexpected substitutions fail the validator.
- Gallery: all 25 templates, 4,534/4,534 sampled blocks, two spawner records and eleven
  unopened salvage-cache tables pass. A loaded far-Overworld wrong-biome placement
  and a protected home-origin placement both explicitly fail.
- Native population console: `server/console-20261015-164630.log`; gallery:
  `server/console-20261015-165139.log`. Both stop cleanly. Runtime evidence binds
  the final built, installed and mirrored jar hashes, CW snapshot and all 25 template
  hashes. No player world is used.

Java17 build and 66 tests pass. All emitted NBT equals its generator source; all
32 registered material IDs, 96 generated textures, navigation graphs, empty cores,
stair/bridge joins, encounter darkness and loot references pass. The 39-file terrain,
106-model and bounded harbor guards pass; existing archaeology and ley-line generator
closures pass; the final feature-order check has zero cycles. These facts establish
the sampled native integration, not client rendering, combat balance or observation
of every family in the wild. Those and the compatibility limits above remain open.
