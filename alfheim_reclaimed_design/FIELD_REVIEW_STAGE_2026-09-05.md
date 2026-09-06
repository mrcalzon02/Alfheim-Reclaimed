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
- `16_wood_elf_skins.js` also throws `redeclaration of var nbt` whenever a wood elf spawns. This is
  a separate runtime defect and must be repaired before court/wild-elf skin acceptance.

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

Repair any runtime script fault affecting elf creation, then test wild, savage and demonic variants in
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

Acceptance when implemented: each pixie type has a valid settlement/spawner pairing, spawners remain
reachable for maintenance but not visually exposed, and settlements do not collide with major structures.

### I8 — giant trees and Jaffa orange trees (queued worldgen)

Inventory `TaxTreeGiant` configured features and Jaffabricate orange-tree blocks/features from their jars,
then add them through Forge biome modifiers rather than editing either mod. Giant trees belong sparsely in
Dreamwood Forest, Silverbark Wood and selected old-growth pockets; orange groves belong in warm living
biomes such as Bloomfall Vale and Golden Fields, never the deficiencies, ocean or Void Margins.

Acceptance when implemented: both tree families occur in new Alfheim chunks, giant trees remain landmarks
rather than canopy spam, oranges are renewable, feature ordering stays acyclic, and sapling/growth behavior
is verified separately from natural placement.

## Running completion record

| Increment | State | Evidence / completed work | Commit |
|---|---|---|---|
| I0 | authored | Screenshots and log translated into scope and acceptance gates; later tree request included. | pending |
| I1 | active | Root symptom proven: no baked anchor after 1,200 seconds in New World Gamma. | pending |
| I2 | queued | — | — |
| I3 | queued | — | — |
| I4 | active | Registration exists; runtime field acceptance did not occur. Skin reservation script fault found. | pending |
| I5 | queued | Screenshot proves a vertical ocean/Verge density contact. | — |
| I6 | deferred | Explicitly queued; no image generation authorized for this stage. | — |
| I7 | deferred | Pixie settlement/spawner brief captured. | — |
| I8 | deferred | TaxTreeGiant and Jaffabricate jars confirmed installed; registry inventory remains. | — |

