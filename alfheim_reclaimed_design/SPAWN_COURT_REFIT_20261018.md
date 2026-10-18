# Spawn court repair — 2026-10-18

Continuity Works `StructureCapability.plan / generate` executed locally from
`C:/GITS/Structuresmith/StructureSmith`, Minecraft 1.20.1, seed 20260903.
The pack-authored provider is `tools/refit_spawn_court.py`; emitted artifacts and
source hash are recorded in `tools/spawn_court_refit_report.json`.

The latest saved client world, New World raven, contains all eight court NPCs.
Decoration occupies Loremistress Anwe's and Warden Ilesh's feet, and Vaal's head
space. The final decoration pass ran after the original NPC clearance pass.
The protection script also sets entity interaction to PRIVATE, and the quest
links require a Petition Scroll absent from the starting kit. The client log
confirms both existing quest lines loaded; they were not deleted.

The revised generator reserves three-block headroom and three-wide approaches
after every decoration pass. Velrous and Orenvel remain at opposite sides of
the stage. Anwe and Nyre move into the northern archive rooms; Sethyr into the
western steward's room; Ilesh to the western approach; Faelan to eastern stores;
Vaal to the kitchen. Normal right-click opens the two existing quest lines.
Entity interaction is PUBLIC; block edits remain PRIVATE. The six supporting
NPCs have no authored quest lines in the original implementation; this revision
does not invent missing historical quests for them.

On the next world load, a bounded scheduled migration updates only blocks that
match the archived original template, verifies station clearance, and moves
exactly one existing NPC per name. It preserves UUIDs, quests, player state,
inventories, foundations, and the Greatbole. Conflicting stations or duplicate
NPCs are reported and skipped. A completion marker prevents repeated movement.
No saved world has been edited offline. No independent structure or reservation
is added; these are interiors of the existing Greatbole family.

Validation: `check_spawn_court_refit.py` passes all eight stations and guarded
migration assertions; `check_hollow_court.py` passes both lines, 11 quests and two
links. All 55 KubeJS scripts parse. The broader `check_spawn_hub.py` still reports
51 issues in unchanged ancient district assets and a stale baked-anchor selector
expectation. Those are outside this revision. Minecraft command execution,
client dialogue/gift turn-ins and visual review remain unverified; acceptance
is static validated. Commit requested before an additional game boot.
