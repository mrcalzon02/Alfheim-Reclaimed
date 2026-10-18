# Usable-state handoff — 2026-10-18

User explicitly stopped further tests/checking and requested an immediate commit.

Active: supported coastal castle spawning, unchanged three candidate positions,
one-block castle foundation apron with gate openings, all 89 terrain contracts,
and native pre-existing-host placement for the twelve Void ruins.

The castle naturally generated on New World raven's seed at X1312, Y78, Z-1840.
The final completed castle test verified all 25 tiles and 5,029 sampled blocks.
The player save was not edited; its castle start chunk was still ungenerated.

The broader ground-foundation adapter is **staged and inactive by default**.
Its representative test found an unsupported edge column, and its strict site
checks rejected all first-three-ring district sites on this seed. Keeping those
unaccepted changes active would regress the usable world. Existing district and
small-building generation therefore continues through the established layouts.
The staged adapter now opts out of duplicate Forge bearding, but that repair has
not been runtime tested. Individual families require an explicit
`activate_ground_adapter: true` policy after acceptance. Omitted means false.

The policy catalogue is complete; the broad new foundation treatment is not
accepted. The original design record's adapter descriptions document the staged
implementation. This handoff supersedes any implication that it is active.
Client terrain/entrance review and wider specialized-family sampling remain open.

Resume with an isolated test runtime: another chat used the shared server folder
during this work. Retain the complete original jigsaw layouts, prove real solid
contact below every exposed plate edge, and assess district availability before
activating a family. No further tests were run after the user's stop instruction.
