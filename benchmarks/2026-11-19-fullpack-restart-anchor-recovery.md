# Full-pack Greatbole saved-world restart — anchor recovery

**Initial restart: FAIL** — full-pack CI
[44637365193](https://github.com/mrcalzon02/Alfheim-Reclaimed/actions/runs/44637365193).

The first boot successfully assembled all seven Greatbole/court parts,
anchored the hub and saved `level.dat`. On second boot all seven scores,
`#created=1`, `#final=1`, `#attempts=1` persisted and Forge exited
cleanly. However, `ALFHEIM_BAKED_ANCHOR_PRESENT` was missing; server
console reported `That position is not loaded` and
`WARNING: no anchor entity`. This is a **real recovery defect**,
not a failed Java build or missing scoreboard save.

Diagnostic artifact `14584384677` (expires November 26, 2026).
The exact pinned first-party companion JAR SHA-256 remained
`f88b8bbd746631cdbf9fb23575d335cfbe97259dde913d5840d55656cf7eb246`.

**Source correction:** In `tools/gen_world_hub.py` and emitted
`hub/autoload.mcfunction`, a completed hub now force-loads its
fixed origin envelope without first selecting the baked marker.
A source regression checks exact generator/command parity.

**Next acceptance:** The existing isolated two-boot full-modpack
test must pass loaded-marker, saved flags, no-second-assembly and
clean-shutdown checks. Neither a source test nor the successful
first boot substitutes for that evidence. Graphical client,
two-player gameplay and actual player inventory persistence
remain separate release gates.
