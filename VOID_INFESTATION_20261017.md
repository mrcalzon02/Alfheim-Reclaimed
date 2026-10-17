# Void Verge and Titan infestation — 2026-10-17

Added seven authored native creature anatomies with three appearances each:
Corrupted Crystal Colossus, Shard Reaver, Prism Warden, Marrow Tick,
Rib Burrower, Sinew Leech and Parasite Maw. The complete menagerie now has
19 species, 57 skins and matching skinned-head spawn selections.

The three golems spawn as low-weight singleton hostiles in Void Verge and
Void Shore. Their spawn rule permits the Verge's luminous terrain; normal
ground and body clearance still apply. Crystal core UV islands have a
fullbright layer, rather than emitting terrain light. The existing twelve
species have broader regional habitat tags. All natural tags are listed in
`tools/void_infestation_static_report.json` (74 entries across 15 species).

Four parasites are spawner-only. Each fresh, desiccated or ossified Titan
corpse template has four hollow nests, one cage per parasite species and
four maggot mounds per nest. Cages spawn one creature at a time at 500–1000
tick intervals, with a local population limit of two Maws or three smaller
parasites. The corpse's decay selects the matching skin and mound state.
Parasite Maw is a large grounded maggot with a radial tooth mouth, pustules,
prolegs and vestigial fly wings. Burrowers do not excavate terrain.

Maggot mounds are modeled blocks with curled larvae, egg sacs, fleshy sludge,
three decay states, inventory display, map color and quiet wet/skitter sounds.
Breaking one yields rotten flesh. Creature loot uses existing vanilla items.

All nineteen species have registered ambient, hurt, death, movement, attack
windup and successful-impact sounds, plus mound ambience: 115 events with
subtitles. These are creature-specific pitched native Minecraft sound
palettes, with weighted ambient alternatives and occasional quiet secondary
rustles. They are not newly recorded audio. References were checked against
the installed Minecraft 1.20.1 asset index (5).

## Continuity Works provenance

Used the existing local Continuity Works provider `tools/gen_void_war.py`,
backed by `C:/GITS/Structuresmith/StructureSmith/src/structure_capability`,
with its deterministic name-derived seeds and existing Minecraft 1.20.1
target, template names, registry inventory and Void War placement policy.
The current snapshot, seeds, registry probes and all 25 template hashes are
in `tools/void_war_generation_report.json`. Only the three Titan NBT files
changed. Corpse footprints remain 47 × 48 × 47, with open approach axes;
no independent structure placement or exclusion-distance settings changed.
The new mound ID is verified from its native source declaration; actual
runtime registry confirmation remains pending as recorded by the provider.

## Build and limitations

Native model export, generated asset/source checks, Void War structure checks,
Titan NBT readback and offline packaging passed. Tests were excluded from
the final package build. The native preview was inspected. Installed jar
matches the built jar and all 1,205 packaged asset/data files match source.
Previous installed jar was preserved in quarantine. Exact hash and evidence:
`tools/void_infestation_build.json`.

No live server/client or listening review was performed for this addition.
Historical six-species gameplay evidence does not cover these new species.
Restart Minecraft to load the replacement companion jar. Newly generated
Titans get the infestation; already placed corpse structures are not changed.
