# Field Review Stage — 2026-09-05

**Role:** the durable plan and running completion record for the September 5 client review.
**Evidence:** `screenshots/2026-09-05_23.23.39.png`, `2026-09-05_23.24.22.png`,
`2026-09-05_23.31.08.png`, and `logs/latest.log` from *New World Gamma*.
**Status:** active. Nothing in this record is production-admitted until its named acceptance gate passes.

## Field evidence

- The ocean is alive, but one reef/vegetation mass occupies too much of the visible sea. Kelp,
  coral, sea pickles and seagrass need independent sparse placement rather than the complete
  vanilla warm-ocean vegetation bundle.
- The ocean biome is exposed as the internal `alfheim_ocean` identifier in player-facing map UI.
- Water meets the Void Verge at a high, nearly vertical wall. The stone variation is useful, but
  punched-out pockets do not read as erosion or a shore transition.
- Scorchfell's large exposed walls repeat one surface too continuously. It needs Alfheim-native
  hot stone at the surface, localized fire/lava punctuation, and later texture variants.
- Starfall precipitation is accepted without changes.
- No wild, savage or demonic custom elf was observed. Spectator mode suppresses the player-driven
  natural-spawn test after 23:18, but the preceding normal-play interval was also inconclusive.
- The Great Bole did not generate. The log records 8/8 court NPCs absent, an empty 64-block search,
  an empty 160-block search, a provisional origin spawn, and final timeout after 1,200 seconds.
  Waiting longer is therefore not an acceptable repair.
- `16_wood_elf_skins.js` also threw `redeclaration of var nbt` whenever a wood elf spawned. The
  handler is unnecessary runtime skin-slot policing and is retired rather than repaired.

## Ordered increments

### I0 — plan and evidence capture

Record every requested item, its scope and its acceptance gate before changing implementation.
This document is the running dialog: append the files, checks, runtime evidence and commit for each
completed increment rather than relying on conversation context.

### I1 — Great Bole spawn system (P0)

Replace passive dependence on a concentric-ring structure eventually generating with a deterministic,
idempotent hub-placement command. Creation must verify the structure-carried anchor, retry boundedly,
retain the provisional safe spawn, never duplicate an existing Bole, and expose command-result evidence.
The natural structure set must not create a second Bole after the explicit placement.

Acceptance: a fresh world produces exactly one baked hub anchor, anchors world/player spawn inside the
gate chamber, loads all eight court NPCs, and reaches the success line without the provisional path.

### I2 — Scorchfell identity (P1)

Replace magma/blackstone/basalt surface strata with the native magmatic, embervein, cinder, obsidian and
cracked Livingrock family. Add sparse, independently controlled fire, lava seep and lava-pool features;
large connected lava fields are not the goal.

Acceptance: new Scorchfell chunks contain no ordinary Overworld stone in the authored surface palette,
show several recognizable heat features per traversal area, and retain walkable routes.

### I3 — living ocean correction (P1)

Give `alfheim:alfheim_ocean` a player-facing name and replace the all-at-once warm-ocean feature bundle
with low-count coral, kelp, seagrass and sea-pickle placements. Keep vanilla aquatic spawning and the
custom sea creatures.

Acceptance: the map says **Alfheim Ocean**; a wide ocean has visible life with substantial clear water
between gardens, and no single reef carpet dominates the view.

### I4 — custom elf spawning (P1)

Avoid runtime skin-policing scripts, then test wild, savage and demonic variants in
their named biomes while a non-spectator survival/creative player is present. Measure attempts and actual
entities rather than treating biome-modifier registration as proof. Tune weights or light rules only from
that evidence.

Acceptance: each of the three variants naturally spawns in at least one intended biome, none spawns in
the protected hub, and no EntityJS/KubeJS error is emitted.

### I5 — Void Verge littoral transition (P1 prototype)

Replace the hard normal-density-to-Verge branch with a noisy horizontal blend band. The water side should
step through submerged shelves, talus/ledges and occasional coves before reaching tall cliffs; the outer
side keeps the undercut floating-island language. Features may decorate the result, but cannot disguise a
vertical density discontinuity.

Acceptance: inspect at least three widely separated ocean/Verge contacts. No sampled shoreline may remain
a continuous flat wall for more than roughly two chunks, and at least two of shelf, slope, cove and detached
islet should appear at each site.

### I6 — deferred texture production run (queued, do not run now)

Queue one coordinated texture pass for every custom block family, explicitly including multi-tile/color
variation for broad walls and the Hollow Court Magister/Captain quest NPC skins. Build an asset manifest
first, group shared material languages, generate small contact sheets, choose a direction, then render the
full set. Do not spend image-generation capacity until this stage is deliberately resumed.

Acceptance when resumed: every custom block and court NPC is represented in the manifest; repeated walls
are reviewed at 8×8 and 16×8 scales; variants preserve block-edge tiling and remain distinguishable in JEI.

### I7 — pixie settlements (queued design)

Design tiny biome-specific villages for the installed Feywild pixie types: two to four miniature buildings,
paths/props readable at player scale, and a concealed, protected spawner chamber beneath each settlement.
Use separate palettes and structure pools by pixie culture; keep placement rare enough to feel discovered.
Each settlement should occupy its own small, intentionally shaped sky island, carry the Feywild tree species
whose climate matches the host biome, and include miniature but functional vanilla food gardens/crop plots.
The island silhouette, roots and support fragments must read as a floating landform rather than a structure
placed on a rectangular pad.

Acceptance when implemented: each pixie type has a valid settlement/spawner pairing, spawners remain
reachable for maintenance but not visually exposed, crops provide renewable vanilla food, the expected
Feywild tree grows on each cultural island, and settlements do not collide with major structures.

### I8 — restrained Jaffa orange and Feywild trees (static implemented)

The installed-jar inventory found Jaffabricate's normal/rare orange placements and Feywild's autumn,
spring, summer and winter trees. The later field-review decision explicitly declines natural TaxTreeGiant
placement: even sparse giant structures would intrinsically change Alfheim's world silhouette. The checker
therefore treats any Alfheim-owned giant-tree placement as a regression.

Six climate-aligned modifiers now add isolated tree accents only. Warm Bloomfall/Golden country receives
the normal orange feature; Silverbark/Dreamwood receives its rarer form. Autumn trees are confined to Ashen
Grove/Silverbark, spring to Bloomfall/Alfheim Plains, summer to Golden Fields, and winter to Starved Reach/
Alfheim Hills. Each uses an Alfheim-owned placed-feature wrapper that exactly mirrors the installed source
feature's rarity, biome, dry-surface and survival predicates. The separate identities prevent cross-mod
feature-order cycles without changing density. Dense Feywild groupings remain reserved for I7's pixie
sky islands.

Acceptance: a fresh server loads and generates chunks without a feature-order failure; the six accents occur
only in their assigned new Alfheim chunks; oranges remain renewable; and sapling/growth behavior is verified
separately from natural placement. No natural TaxTreeGiant structures are enabled.

### I9 — model and display alignment repair (static implemented)

The custom carpet now uses three adjacent base strips instead of coplanar trim over a full-width slab, and
its inlays sit above the textile. Balustrade posts, caps and rails no longer occupy the same volumes. The wall
sconce's backplate, mount and arm are separated, while its glow is inset from every glass face plane. A
static model check rejects same-facing coplanar rectangles on all three repaired models.

The apparent rightward display offset was traced to neighbouring source-atlas fragments crossing vertical
cell cuts. The shared armory generator now removes only non-principal foreground components that touch those
cut lines before all 480 item sprites are resized and centered. The principal silhouette and detached
interior decoration remain intact. Regenerated six-class review sheets show the reported left-edge fragments
removed from pants and books, along with sibling equipment affected by the same source fault.

Acceptance: the three blocks remain stable at near/mid/far camera distances; pants and books are centered in
inventory, hand and item frame; generated siblings pass the same crop rule. Static generation/checks and the
review atlas pass; an actual restarted client is still required for depth stability and display-frame signoff.

### I10 — native and compatibility ore tuning (runtime smoke-proven)

Elementium is increased from size 9/count 5 to size 12/count 6; Dragonstone from size 4/count 1 to size
7/count 2. This deliberately increases both deposit presence and useful deposit size without multiplying
either into ordinary-ore abundance. Fey Gem now has its own climate-limited Alfheim feature at size 6/count
3 across seven living/fey biomes.

Elementium, Dragonstone and Fey Gem each have 42 host-matched variants covering every authored Deep and
Void natural stone. Exact host predicates are evaluated before the broad Livingrock fallback, so authored
stone walls no longer receive a conspicuous foreign-rock square. Source Silk Touch, Fortune, count and
explosion behavior are retained. The 126 blocks register once at startup; there is no polling or tick script.

Acceptance: quantitative blocks-per-chunk sampling still needs a wider fixed-seed census and the textures
need client inspection. The fresh headless smoke world did load cleanly and its 639 full Alfheim chunks
contained 26 distinct naturally generated hosted IDs, including Fey Gem, Elementium and Dragonstone.
Progression and feature-order checks remain valid.

### I11 — structure encounter spawners (queued)

Inventory the creatures required by the knight quest line and assign them to appropriate ruin/fortress
families. Add protected, bounded spawners inside those structures with encounter-specific counts, activation
ranges and cooldowns; never substitute arbitrary hostile mobs merely because they fit a room.

Acceptance: every named knight-quest creature has at least one discoverable structure encounter, spawners do
not leak into the Hollow Court or peaceful settlements, and quest kill/encounter credit works end to end.

### I12 — forest, wooded-shore and living undergrowth expansion (queued)

Add several recognizably different forest identities rather than treating every wooded biome as a different
leaf color over the same spacing. At minimum, design two dense wooded shoreline environments around the large
Alfheim Ocean footprint: one warm/lush coast and one cool or misted coast. Their biome/density bands must
follow the actual littoral instead of dropping generic trees into every inland chunk; trunks, fallen wood,
roots and understory should make both read as forests while retaining navigable openings and views to water.

Inventory the installed Feywild mushroom features and distribute climate-suitable families through every
non-Void biome. “Nothing grows” remains an absolute Void rule: no mushrooms, brambles, trees, grass or other
living ground cover may target Void Verge, Prism Drift, Rootfall, Sepulchral Reach, Shatterfields or Starless
Reach. Add an Alfheim Bramble block/family for thickets, hedges and ruins; prefer static block behavior and
worldgen predicates over any repeating growth script. Bramble density, collision/damage behavior, drops and
renewability require a separate design gate before implementation.

Acceptance: at least two shore forest types form dense, irregular coastal belts in new chunks; inland forest
types remain visually distinct; mushroom families are climate-aligned and absent from every Void biome; and
brambles enrich paths/edges without turning normal travel into constant chip damage or a performance cost.

### I13 — Void crystal and local-stone geode expansion (queued)

Expand the crystalline feature vocabulary of Void Verge and all associated Void biomes. New geodes, crystal
seams, exposed nodules, broken crowns and suspended shard clusters must use each host biome's local stone
types for shells, anchors and debris instead of falling back to generic Livingrock. Give related environments
shared mineral logic but different silhouettes and exposure levels, so the features help explain the geology
rather than reading as randomly pasted decorations.

Acceptance: every Void biome gains at least two suitable crystalline/structural feature families; shells and
supports match the local stone palette; features never introduce living vegetation; placements preserve the
intentional floating-island silhouette and stay clear of major authored structures.

## Running completion record

| Increment | State | Evidence / completed work | Commit |
|---|---|---|---|
| I0 | committed | Screenshots and log translated into scope and acceptance gates; all later additions captured. | `d865f28` |
| I1 | runtime-proven | Bounded solid-surface lattice; deterministic trunk/crown/court/base template assembly; base-last commit marker; exact footprint loading; provisional-state self-repair; natural duplicate source removed. Fresh proof succeeded on attempt one with one anchor, one crown and all eight tagged court NPCs persisted. | `70d2fa8` |
| I2 | static implemented | Surface rule now uses magmatic/embervein/cinder/obsidian/cracked Livingrock; lava pool 1/36 chunks plus six native-rock seep attempts. | `70d2fa8` |
| I3 | static implemented | Name is “Alfheim Ocean”; coral 1/5 chunks, kelp 1/3, six seagrass attempts, pickles 1/32. Fish/custom sea life retained. | `70d2fa8` |
| I4 | partial | Registration remains; runtime field acceptance did not occur. Faulting skin handler deleted instead of expanded; natural-spawn proof remains. | `70d2fa8` |
| I5 | static prototype | CLIFF..RIM now continuously blends ordinary density into a lower noisy shore; Deep density is explicitly excluded from that blend. | `70d2fa8` |
| I6 | deferred | Explicitly queued; no image generation authorized for this stage. | — |
| I7 | deferred | Pixie settlement/spawner brief captured. | — |
| I8 | static implemented | Six sparse climate accents use Alfheim-owned wrappers around Jaffabricate/Feywild placement rules. Cross-mod feature ordering is acyclic. TaxTreeGiant world placement is explicitly disabled by later field-review decision. | `7348eed` |
| I9 | static implemented | Three model sources rebuilt without same-facing coplanar overlaps; all 480 armory source cells receive bounded edge-spill cleanup before centering. Review sheets and static checks pass; restarted-client signoff remains. | pending |
| I10 | runtime smoke-proven | Elementium 12×6, Dragonstone 7×2, climate-limited Fey Gem 6×3; 126 host-matched variants. Fresh server exit 0; 639 full chunks contain 26 hosted IDs from all three ores. Wider density/client review remains. | `566e11d` |
| I11 | queued | Knight-quest creature spawners in suitable structures recorded. | — |
| I12 | queued | Distinct forests, two dense wooded shore types, non-Void Feywild mushrooms, and static-behavior Bramble family recorded. | — |
| I13 | queued | More local-stone geodes/crystal structures across all six Void biomes recorded. | — |

## Implementation log

### 2026-09-05 / 2026-09-06 — I1 runtime proof and I2 through I5 static pass

- Great Bole: `tools/gen_world_hub.py`, `tools/gen_spawn_hub.py`, generated hub functions,
  protection script and biome tag changed. `worldgen/structure_set/greatbole.json` removed.
- Scorchfell/ocean: `tools/gen_alfheim_biomes.py` owns the new placed/configured features and
  ocean name; `tools/gen_deep_terrain.py` owns the native surface palette.
- Void shore: `tools/gen_void_worldgen.py` owns the continuous shoreline blend. The blend consumes
  original Alfheim surface density rather than Deepworks-wrapped density, preserving the Deep/Void
  separation contract.

### 2026-09-06 — I8 restrained tree pass

- User decision: natural TaxTreeGiant landmarks are declined because they would change the intrinsic
  character and silhouette of the world. No giant-tree structure or biome modifier was added.
- `tools/gen_tree_worldgen.py` generates six sparse climate-aligned accents from the installed
  Jaffabricate and Feywild placed features. Alfheim-owned wrappers preserve every source placement
  predicate while isolating the registry identities from the source mods' vanilla-biome order graph.
- `tools/check_tree_worldgen.py`, the full worldgen resolver and the global feature-order checker pass.
  Natural placement still needs new-chunk visual acceptance; dense Feywild groves remain part of I7.

### 2026-09-06 — I10 native ore pass and I12–I13 plan expansion

- `tools/gen_native_ores.py` and `tools/native_ores_manifest.json` own three ore families, 126 hosted
  blocks/textures/loot tables, measured density settings and the climate-limited Fey Gem modifier.
- `tools/check_native_ores.py` proves the complete host mapping, source-equivalent loot, animation
  metadata, configured/placed feature contract and absence of repeating runtime hooks. Full worldgen,
  global feature order and all KubeJS syntax checks pass.
- `validation-native-ores-0906` exited cleanly. Its 639 full Alfheim chunks contain 5,024 section-palette
  references across 26 hosted ore IDs, including all three families. This proves natural selection and
  registration, not the final blocks-per-chunk balance or client appearance.
- Later field-review additions are queued as I12 (multiple forest identities, two dense wooded shores,
  non-Void Feywild mushrooms and a Bramble family) and I13 (more local-stone Void geodes/crystals).
- Runtime script policy: `kubejs/server_scripts/16_wood_elf_skins.js` removed. Its legacy generator
  is prevented from recreating it. Dedicated court NPC assets remain I6 scope.
- Passing checks: Deep regeneration, Deep invariants, worldgen/climate, feature order (961 edges,
  611 placed features), spawn-hub structure/wiring, and 18-entity wildlife synchronization.
- Runtime proof: after Java was cleared, the final fresh `validation-hub-lattice-proof-0906` run
  loaded all scripts, found a solid candidate, placed trunk/crown/court/base with result 1, anchored
  on attempt one, and saved exactly one baked anchor, one crown marker and all eight tagged court
  NPCs. The early live court query saw seven because one entity chunk had not ticked in; saved entity
  data contains the complete eight-member manifest.

### 2026-09-06 — I9 model and armory crop repair

- `tools/gen_royal_tileset_wave_a.py` now owns non-coplanar carpet, balustrade and wall-sconce geometry;
  `tools/check_royal_tileset_wave_a.py` rejects a recurrence of overlapping same-facing planes on them.
- `tools/gen_armory.py` now strips only detached art crossing a source cell's vertical boundary before
  resizing and centering every item icon. This repairs the reported pants/books and the same visible fault
  in sibling equipment without adding model transforms or runtime code.
- All 480 item and 120 worn textures regenerate and pass the armory audit. The six rebuilt review sheets
  have clean cell margins. Minecraft client inspection is still required before calling I9 visually proven.
