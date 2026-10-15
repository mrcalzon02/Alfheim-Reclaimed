# Terrain and structure audit closeout — 2026-10-14

Two native decoration defects received source repairs. Frontier's first normal
generation trial remains rejected, with the next obstruction recorded below.
No production structure family was enabled by this checkpoint.

## Repairs and evidence

| Finding | Repair / result |
|---|---|
| Golden Fields wheat decoration converted polished floors into farmland | Remove native `mythicbotany:wheat_fields` from Golden Fields. Add grass, fern and dandelion patches restricted to air over grass/dirt. Existing bounded golden-field dais structures retain worked crops. |
| Native abandoned apothecaries could occupy architectural floors and rooms | Require target air and natural ground below. Preserve native configured contents and the pack's count 1 / rarity 20. The main biome generator uses the same placement definition. |
| Assembly review previously checked doorway support without exact floor identity | Compare both sides of every join against authored floor blocks. The failed wheat trial is now rejected for its replaced floor. |

The wheat witness is `[-1456,74,617]` farmland under wheat in
`server/validation-frontier-natural-20261014`, where the authored floor is ivory
polished livingrock. The following meadow-repaired trial found an apothecary at
`[-1445,75,640]` in the lodge's reserved air. Local inspection of the native
feature implementations identified the missing soil/target restrictions; no jar
was edited.

The final guarded trial saved and exited successfully in 151.4 seconds:
`server/console-20261014-192626.log`. It generated all 256 requested chunks and
exactly one natural Frontier start with six members. No manual structure or
feature placement was used. The test-only structure set selects one bounded
Golden Fields locality; it is absent from shipping data.

**Runtime gate rejected:** the census passed assembly and join checks, then
found dreamwood leaves at `[-1340,94,621]` in the wild ward shrine's authored air.
This is the next repair target. A complete room/foundation census and natural
terrain-fit acceptance were not reached. Do not treat a clean server exit as a
structure pass. Machine-readable rejection: `tools/frontier_natural_runtime.json`.

The final trial used a deliberately denser apothecary placement (uniform 1–3
attempts, rarity 2), while published data retains count 1 / rarity 20. Its target
and support predicates are identical. The report records both source hashes and
this difference; it does not establish final sparse frequency or complete
absence of decoration intrusions. The general source generator was corrected
before closeout to preserve the authored sparse setting.

## Inventory and retained boundaries

- All 26 home biomes have configured vegetation; no configuration coverage gaps.
  This is a feature inventory, not measured density or visual acceptance.
- All 12 sequencing structure families have implementations: nine natural sets
  enabled; Sacred, Military/Warden and Frontier remain disabled prototypes.
- Void Shore and Void Verge both have bramble/thorn patches, Thorn Gate and Shore
  Memorial Court. Earlier substrate repairs and their runtime evidence remain
  recorded in `BIOME_FEATURE_COVERAGE.md`.
- The 39 protected broad-terrain files remain unchanged. The bounded,
  approximate harbor policy remains unchanged. Player saves were not edited.
- Current static checks retain 106 custom models without coplanar faces and zero
  feature-order cycles. Meadow generator equality and mutation fixtures pass.

Next work: isolate the shrine leaf intrusion without changing broad terrain,
then repeat a finite natural trial. Client review, other terrain/biome sites,
natural frequency and production admission remain pending. Known unrelated
startup log warnings are not certified repaired by this checkpoint.
