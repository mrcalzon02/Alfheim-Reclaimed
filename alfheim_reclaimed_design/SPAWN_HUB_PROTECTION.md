# Spawn Hub Protection — claim and anti-grief acceptance

**Role:** protection subrecord for `SPAWN_HUB.md` §4. It owns the runtime acceptance criteria for the Greatbole/Hollow Court protected zone, its FTB Chunks administrative claim, and player-edit protection.
**Status:** `runtime failed` 2026-09-04 — the Greatbole and spawn structure were again observed without the intended admin-team claim, and blocks could be destroyed. The hub is **not protection-complete**.
**Authority:** subordinate to `INSTRUCTIONS.md`; extends `SPAWN_HUB.md`. Where the older §4 status says player-edit protection is built or treats the FTB claim as a later manual administrative step, this later runtime evidence controls until the two records are reconciled.

---

## 1. The failure

The Greatbole can generate, the hub can anchor to it, and the anti-explosion / anti-mob-grief scripts can exist while the actual spawn hub is still **unclaimed and player-destructible**. The latest runtime test demonstrated exactly that failure again.

This matters because the protected hub is not decorative scenery. It is a persistent campaign location containing the Greatbole, gate, Court and recurring NPC interactions. A player being able to remove its blocks means the core quest hub can be permanently damaged through ordinary play.

The previous treatment of the FTB Chunks claim as a one-time admin action to perform later is no longer an acceptable delivery assumption. A required protection step that is repeatedly absent in fresh-world testing is an unresolved implementation defect, not documentation trivia.

**A hub is not ready merely because it generated. It is not ready until its protection state is observed.**

---

## 2. Two protection layers, neither substitutes for the other

The hub deliberately has two independent protection mechanisms and both must pass.

| Layer | Responsibility | Runtime requirement |
|---|---|---|
| **FTB Chunks admin-team claim** | Player block-edit ownership, team semantics, visible claimed territory, normal survival protection | The full hub footprint is actually claimed by the intended administrative/server team. |
| **KubeJS/server enforcement** | Hostile-spawn suppression, explosion damage, fire spread, mob griefing and other world-event protections | Each prevention rule works independently even if a claim is temporarily absent. |

The KubeJS protections do **not** prove the FTB claim exists. Conversely, an FTB claim does not by itself prove creepers, fire or other scripted hazards are handled exactly as designed.

The live observation that blocks could be destroyed also means the prior `SPAWN_HUB.md` table entry stating that player edits were already restricted must be treated as **failed/unproven**, regardless of what the script intended to do.

---

## 3. Claim lifecycle must follow the actual Greatbole

The Greatbole may relocate from the origin when the origin biome is unsuitable. Protection therefore cannot be based on a hard-coded assumption that the structure sits at 0,0.

The desired lifecycle is:

1. Generate/resolve the Greatbole and obtain the authoritative hub anchor.
2. Resolve the intended administrative/server FTB team.
3. Reconcile the team's claimed area against the actual Greatbole/Hollow Court footprint, including the processional approach and any allowed relocation envelope.
4. Observe that the required chunks are claimed before reporting the hub as protection-ready.
5. Re-check or reconcile protection on subsequent server/world loads so a missing, released or stale claim cannot silently persist.

If the installed FTB Chunks version or available scripting APIs make automatic claim reconciliation impossible, the fallback is **not** silent manual debt. The pack must expose a loud, specific readiness failure/instruction until an operator completes the claim, and validation must remain failed until read-back confirms it.

A message such as "claim this later" is not completion evidence.

---

## 4. Acceptance must use an ordinary player

An operator is a poor protection test because operator/bypass permissions can intentionally defeat the exact restrictions being tested. Player-edit acceptance therefore uses a **non-op survival player**.

The finished hub must pass all of the following in a fresh test world:

- the intended admin/server team owns the FTB Chunks claim covering the full Greatbole, Court and protected approach;
- a non-op survival player cannot break a Greatbole, gate, amphitheatre or protected-zone block;
- the same player cannot place arbitrary blocks inside the protected zone unless the final design explicitly grants a build area;
- the protection follows a Greatbole that relocated away from 0,0 rather than protecting empty origin chunks;
- the claim survives a player relog and server/world restart;
- protection status can be inspected/read back rather than inferred from a command return code;
- explosion damage, fire spread, mob griefing and hostile spawning are tested separately and remain prevented as designed.

**Failure of any one is a failed hub-protection pass.** The Greatbole may not be described as claimed, protected, locked or production-ready until those runtime conditions have been observed.

---

## 5. Repair priority

This sits alongside the Greatbole terrain-fit and Greatbole-to-Court circulation defects, but it is not aesthetic work. Protection is a functional prerequisite for using the structure as the persistent campaign hub.

The next repair pass should therefore treat these as separate gates:

1. **placement:** the Greatbole belongs in and is supported by its terrain;
2. **circulation:** the interior connects deliberately to the Court;
3. **protection:** the actual generated hub is claimed and ordinary players cannot damage it;
4. **aesthetic refinement:** silhouette, ruin quality, dressing and detail follow once the first three are reliable.

That ordering prevents another visually improved hub from shipping while remaining mechanically destructible.
