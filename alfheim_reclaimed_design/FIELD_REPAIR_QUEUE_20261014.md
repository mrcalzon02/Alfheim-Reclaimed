# New field report — 2026-10-14

This supersedes assumptions of satisfactory terrain fit or district quality.
Reference save: `New World staven`, seed `-3282135118187884121`.
Screenshot reference: `codex-clipboard-f5dc3c85-97db-41e8-a51e-6160b0d5ed5f.png`.

## Reproduced and changed

- **Buried hub:** saved baked anchor `[0.5,81,-5.5]`; sampled ground around the
  footprint is Y245–268. The hub allows a heightmap datum only through Y200,
  then previously assembled at fixed Y80. Removed that full-hub fallback.
  Emergency platforms now use the actual surface through Y315; otherwise a
  supported platform at Y315 keeps all headroom within the build limit.
  This prevents a new fixed-Y buried hub; it does not relocate an existing
  buried hub or produce a complete tree on an unsuitable mountain.
  A legacy-anchor evacuation path now detects natural rock at all three probes
  100/110/120 blocks above the anchor, beyond the authored canopy. All three
  probes match livingrock in this save. It preserves the old tree, rejects its
  spawn anchor and creates a safe platform; nearby players and personal respawns
  are redirected. The final login/respawn hooks have static checks only; client
  evacuation review remains pending.
- **World floor:** four origin regions contain 3,836 fully generated chunks,
  982,016 non-Void columns and 17,547 columns without bedrock at Y−64.
  First recorded witnesses contain lava. No saved structure bounding box in
  this sample reaches the floor, so structure carving is not established as
  their cause. Machine evidence: `tools/staven_field_audit.json`.
  The first-party bedrock guard repairs only the minimum layer on chunk load,
  including existing chunks, excluding `#alfheim:void_margins` columns sampled
  at Y64. It uses 256 bounded column checks with no neighbour chunk requests.
  Java 17 build and existing tests pass. Runtime results are recorded separately
  in `tools/bedrock_guard_runtime.json` when the disposable-copy trial passes.
  Two successful copied-save trials each repaired all 22 holes in 40 chunks
  (10,240 columns), with no remaining missing floor blocks. The emergency marker
  was observed at Y222, following the actual surface rather than fixed Y100.
  The final landing X/Z was then moved from the old Z64 platform to the origin
  so it stays inside existing protection bounds; final origin delivery and
  legacy evacuation still require client/runtime review.
- **Conduits:** straight-run trim moved from walking lanes into the shell.
  Dripstone attempt rate reduced from 0.10 to 0.025; moss seepage increased
  from 0.07 to 0.14, with attached wall vines added. Five templates regenerated;
  source equality and lane regression checks pass. Client walking review pending.
- **Void crowding:** twelve independent Void ruin grids changed from spacing
  7 / separation 2 to 18 / 7 in both the manifest and shipping sets. Candidate
  density is about 85% lower per grid; observed density remains uncalibrated.
  Void-edge courts changed from 12 / 6 to 28 / 14. Existing chunks retain their
  structures. No broad terrain expression changed.

## Required next repairs, in order

1. **Complete spawn placement:** fixed, finite nearby-site probes, footprint-wide
   height/relief checks and canopy build-limit clearance. Move protection claims,
   suppression bounds and reload force-load state with the chosen anchor. Do not
   ship relocation while claims still protect the origin. Existing buried-hub
   recovery must preserve player builds and avoid duplicate baked anchors.
2. **Bottom-floor acceptance:** verify the Void branch remains open in a runtime
   sample, and identify the original floor-overwriting stage. The repair guard is
   a bounded containment measure, not proof of the originating cause.
3. **Districts:** shared placement/exclusion policy, spawn setback, foundation
   affordance and explicit exterior approach grades. Each family needs a detail
   and scale redesign; source existence and assembly joins do not establish
   acceptable architecture. Do not admit Sacred/Warden/Frontier yet. Preserve the
   accepted approximate, bounded harbor policy.
4. **Underground connections:** identify the crying-obsidian/magmatic-livingrock
   intrusion in the save. These materials appear in Faultwork templates; this is
   a candidate identity, not proof of an independent overlapping structure.
   Shared headworks/dungeon grid coordinates do not guarantee connected sockets:
   verify actual rotation, shaft termination, depth and entrance attachment.
5. **Void island foundations:** add bounded, tapered native geological undersides
   to ruins, with distinct silhouettes and roots where appropriate. Preserve
   broken-span gaps and fit to the structure datum. These have not been added by
   the frequency change; new terrain density searches are unnecessary.
6. **Frontier decorator obstruction:** remove dreamwood leaf intrusion in the wild
   ward shrine, then repeat a bounded normal-generation trial.

## Enemy roster requirement

At least three biome-specific appearances for each of zombie, skeleton,
pillager, enderman and endermite. For 26 home biomes this is **390 appearances**
(26 × 5 × 3), with no creeper variants. Preserve each species' recognizable
silhouette and behaviour; adapt materials, wounds, clothing and botanical growth
to the biome. Three recoloured names alone do not satisfy the visual request.

The user's request includes natural Overworld spawning. Implementation must
explicitly cover `minecraft:overworld` as well as the Alfheim home-biome roster;
do not silently interpret Overworld as only `mythicbotany:alfheim`. Define a
matching palette for Midgard biomes and avoid introducing duplicate vanilla
spawn entries or excessive pillager/endermite groups. Validate spawn caps,
despawning, loot and Mine and Slash integration on one species/biome slice before
expanding the roster. This roster is implemented in the 2026-10-15 checkpoint;
see `THEMED_ENEMIES.md` for its 390 appearance combinations, spawn integration
and bounded runtime evidence. Client appearance and combat/frequency review
remain pending. Structure repairs are held until Continuity Works completes its
skill conversion, per the user's latest instruction.
