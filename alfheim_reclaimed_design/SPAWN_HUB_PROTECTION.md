# Spawn Hub Protection — claim and anti-grief acceptance

**Role:** protection subrecord for `SPAWN_HUB.md` §4. It owns the runtime acceptance criteria for the Greatbole/Hollow Court protected zone, its FTB Chunks administrative claim, and player-edit protection.
**Status:** `static partially repaired; runtime validation pending` 2026-09-05 — the stale assumption that FTB Chunks was absent has been corrected in the authoritative generator and shipping script. The hub now attempts a server-team claim and independently rejects non-op breaking and placement. Post-reconciliation review also confirmed that the current shipping script still has **no fire-spread handler**, so fire protection remains an open implementation item rather than an accepted static capability.
**Authority:** subordinate to `INSTRUCTIONS.md`; extends `SPAWN_HUB.md`. `SPAWN_HUB.md` §4 was reconciled to the automatic FTB claim flow on 2026-09-05; this file remains the authority for protection acceptance. Where the parent record's summary table conflicts with the implementation-specific state here, this record controls until that row is corrected.

---

## 1. The failure

The Greatbole can generate, the hub can anchor to it, and the anti-explosion / anti-mob-grief scripts can exist while the actual spawn hub is still **unclaimed and player-destructible**. The 2026-09-04 runtime test demonstrated exactly that failure.

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

### 2.1 Static repair now implemented

`tools/gen_spawn_hub.py` remains the authority for `kubejs/server_scripts/04_spawn_hub.js`. Its protection generator now reflects the installed pack rather than the stale assumption that FTB Chunks was absent:

- FTB Chunks 2001.3.8 is treated as installed and the generated script creates/reuses the server team `alfheim_hub` and invokes `ftbchunks admin claim_as` for the hub envelope on server load;
- `PROTECT_FROM_PLAYERS` defaults to `true`;
- both `BlockEvents.broken` and `BlockEvents.placed` reject non-op edits in the protected zone;
- the existing hostile-spawn and explosion layers remain additive rather than being replaced by the claim;
- the script logs the FTB command return values but explicitly does **not** treat them as ownership read-back.

**Fire spread is not yet implemented in the current generated/shipping script.** The protection contract requires it, but inspection of `04_spawn_hub.js` shows no fire-spread event handler. That is an open implementation defect and must not be described as built merely because the acceptance list contains it.

This is a **partial static repair**, not runtime acceptance. A zero `claim_as` return can mean that no new chunks needed claiming or that no claim was established, so command return values alone cannot satisfy §4.

### 2.2 Ownership read-back is now machine-checked

`tools/run_server.py` issues `ftbchunks info` at the centre and all four corners of the configured protection envelope. `tools/check_spawn_hub_claim.py` turns those console replies into an acceptance gate instead of leaving them for manual interpretation. The checker reads `HUB_DIMENSION`, `HUB_FTB_TEAM`, and `HUB_RADIUS` directly from the generated shipping script, converts the probe block coordinates to the chunk coordinates FTB Chunks reports, and requires every location to name the expected `alfheim_hub` owner.

The checker fails on a missing probe, an unclaimed probe, or a different owner. Its built-in fault tests cover the complete claim, wrong-owner, missing-corner, and unclaimed-centre cases. This closes the evidence gap between “the claim command ran” and “FTB Chunks reported who owns the protected envelope,” but it still does **not** satisfy the non-op player or restart-persistence requirements in §4.

---

## 3. Claim lifecycle must follow the actual Greatbole

The Greatbole may relocate from the origin when the origin biome is unsuitable. Protection therefore cannot be based on a hard-coded assumption that the structure sits at 0,0.

The current static repair claims the complete 192-block relocation envelope already used by the hub protection logic. That envelope deliberately contains every allowed Greatbole relocation plus the structure footprint, so it does not leave a relocated hub outside protection. This is broader than resolving and claiming only the final marker-relative footprint; runtime validation must confirm that the resulting FTB claim is acceptable and persists correctly.

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
- explosion damage, **fire spread**, mob griefing and hostile spawning are tested separately and remain prevented as designed.

**Failure of any one is a failed hub-protection pass.** The Greatbole may not be described as claimed, protected, locked or production-ready until those runtime conditions have been observed.

---

## 5. Repair priority

This sits alongside the Greatbole terrain-fit and Greatbole-to-Court circulation defects, but it is not aesthetic work. Protection is a functional prerequisite for using the structure as the persistent campaign hub.

The next protection implementation action is to add fire-spread prevention at the authoritative `tools/gen_spawn_hub.py` protection generator and regenerate `kubejs/server_scripts/04_spawn_hub.js`, then prove source-to-shipping equality. After that, runtime validation remains: boot a fresh world with the regenerated script, read back the `alfheim_hub` server-team claim in FTB Chunks, run `python tools/check_spawn_hub_claim.py` against that run's console, test break and placement with a non-op survival player, restart and re-check ownership, then exercise the independent explosion/fire/mob-grief/hostile-spawn gates.

The wider structure repair ordering remains:

1. **placement:** the Greatbole belongs in and is supported by its terrain;
2. **circulation:** the interior connects deliberately to the Court;
3. **protection:** the actual generated hub is claimed and ordinary players cannot damage it;
4. **aesthetic refinement:** silhouette, ruin quality, dressing and detail follow once the first three are reliable.

That ordering prevents another visually improved hub from shipping while remaining mechanically destructible.
