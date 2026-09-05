# The Spawn Hub — the Greatbole, the Gate, and the Court

**Role:** authoritative design record for the pack's centrepiece: the arrival tree, the portal
built into its flank, the ruined amphitheatre outside it, and the protected admin zone around
all three.
**Status:** `runtime observed` 2026-09-04 — the Greatbole now generates with its crown, but the
first in-world design review exposed two open defects: unacceptable cliff/terrain integration
and incomplete circulation between the Greatbole interior and the ruined Court circle. The
repair pass is open.
**Authority:** subordinate to `INSTRUCTIONS.md`. Extends `SPAWN_ZONE.md`; see §1.2 for the
boundary between the two records. `SPAWN_HUB_PROTECTION.md` owns protection acceptance and
runtime claim proof.
**Asked for by the user, 2026-09-03. Runtime refinement added from the user's 2026-09-04 test.**

---

## 1. What is being built, and why it is the most important thing in the pack

> *"An absolutely massive oak tree with a huge intricate portal structure built into the side of
> the tree ... the ruins of a wide amphitheater of marble and stone immediately outside that
> portal ... a large protected area claimed by admins as a spawn hub."*

This is not a set piece the player walks past once. The user's own reasoning is the design
constraint, and it is worth quoting because it determines everything below:

> *"I can definitely anticipate the player setting up a base somewhere nearby, exploring the
> nearby abandoned elven ruins and village pieces, setting up their own base, but needing to
> return here on a number of occasions — for various reasons such as interacting with the wizard
> or the captain or the other court members and scouts."*

So the hub is a **destination the player returns to for the length of the campaign**, not a
spawn point they leave behind in the first hour. Three consequences follow, and they are the
reason this record exists separately from `SPAWN_ZONE.md`:

1. **It must survive.** A creeper crater in the amphitheatre on day 40 is not a war story, it is
   a broken quest hub. Hence §4.
2. **It must stay legible.** The player needs to find Velrous again without a map. A silhouette
   visible from a kilometre is the cheapest wayfinding in the game — hence a tree that is
   deliberately enormous even after the jigsaw-height correction.
3. **It will take many passes.** The user said so explicitly. The build is therefore
   **parametric and regenerable** — `tools/gen_spawn_hub.py` writes every `.nbt` from numbers, so
   the next pass is an edit and a re-run, not a rebuild. This is the single most important
   structural decision in this record.

### 1.1 The fiction it has to carry

Alfheim is a wasteland of collapsed tree-cities. The hub is the one place that is *not quite*
collapsed: the tree still stands, the gate is still there but sealed, and the court that used to
fill the amphitheatre is down to a magister, a captain, and six survivors. It should read as
**the last lit room in a dark house** — enough grandeur to say what was lost, enough ruin to say
it is gone.

### 1.2 Boundary with `SPAWN_ZONE.md`

| Record | Owns |
|---|---|
| **This file** | The Greatbole, the Gate, the amphitheatre, the protected hub, the court's placement |
| `SPAWN_ZONE.md` | The Hollow Court **city** — the ~1000-block ruin field, its 40–80 pieces, the decay processors, the Drained Grove biome |

They meet at the hub's edge. `SPAWN_ZONE.md` §3.1's `concentric_rings` mechanism and its §7.1
Continuity Works spawn-protection analysis both still govern; nothing here supersedes them.

---

## 2. The Greatbole

An oak, deliberately. The pack's own material is Dreamwood, and the arrival tree being **common
oak** is the point: it is the tree that was already here before the elves made anything, and it
outlived everything they made. Dreamwood and livingrock appear only as elven *work* applied to
it — the gate frame, the stairs, the court.

### 2.1 Why it is an assembly and not one structure

`SPAWN_ZONE.md` §2 established the three hard limits; they bind here too.

| Limit | Value | Consequence |
|---|---|---|
| Structure block save volume | **48 × 48 × 48** | No piece may exceed it. The tree is an assembly. |
| Jigsaw `size` (recursion depth) | 0–20 | Ample for the current stack. |
| Jigsaw `max_distance_from_center` | codec 1–128; **116 practical budget under `beard_thin`** | The assembled tree must fit the structure-plus-terrain-adaptation budget. It is now **112 blocks** tall. |

> **Corrected and runtime-proven 2026-09-04.**
>
> The old entry read: *"a 190-block tree centred on its base spans ±96 — inside the cap."* That is false. The tree is **not centred on its base** — it grows *upward* from it, so a 190-block tree spans **+190**, not ±95. Jigsaw placement culled the crown, and raising the nominal cap to 128 also failed because `JigsawStructure` validates the structure plus the 12-block terrain-adaptation margin. With `beard_thin`, the real usable budget is 116.
>
> The tree is now assembled at **112 blocks** (48 base + one 24-block trunk segment + 40 crown). `tools/gen_spawn_hub.py` and the S9 pool-graph check enforce that relationship. A crown probe in the validation world proved that the crown piece now places at runtime.

### 2.2 The pieces

| Piece | Size | Role |
|---|---|---|
| `greatbole/base` | 48³ | Root buttresses, the trunk foot, **the gate chamber cut into the north flank**, and the court jigsaw |
| `greatbole/trunk` | 32×24×32 | One current trunk segment. `rollable` joint so the trunk does not read as an extrusion |
| `greatbole/crown` | 48×40×48 | The canopy and the dead upper boughs |

Total current vertical assembly: **112 blocks**. Stacking through vertical jigsaws is what gets
past the 48-block ceiling without violating the real placement budget.

### 2.3 The Gate

Built **into the north flank**, not standing free — the user was specific, and it is the better
image: you walk *into the tree* to leave the world.

- Chamber roughly 12 wide × 13 tall × 12 deep, hollowed out of the trunk mass.
- The gate face itself is **8 × 10 of `alfheim:sealed_gate`** — the animated dormant block built
  for B-57. It is scenery: no teleport, no state change.
- Framed in livingrock bricks, chiseled quartz and gold, with elf glass in the arch.

**This is the seeing half of B-36.** That item asks for *"a multiblock the player can see from
Era I and cannot finish until Era IV"*, and notes the traversal already exists
(`botania:alfheim_portal` outward, `mythicbotany:return_portal` home). The gate here is the thing
seen. Era IV's opening, and whatever block actually carries the player, stay with B-36.

### 2.4 The Greatbole and the Court must be one piece of circulation

**Runtime design defect, observed 2026-09-04:** the Greatbole and the ruined circle are adjacent,
but they do not yet read or function as one connected place. The finished hub requires a
**continuous, deliberate, walkable route from inside the Greatbole/gate chamber through the base
and root mass into the amphitheatre/circle**. Proximity is not connection.

The route should read as the remains of the Court's original processional way: an interior
landing, threshold or root-vault, broad steps or ramps, broken paving, retaining masonry and
collapsed side elements that explain how the interior once opened into the circle. Ruin may
interrupt the edges and ornament, but the primary route cannot require the player to jump down a
natural slope, climb raw terrain, break blocks, or wander around the outside of the tree to find
the Court.

**Acceptance:** stand inside the gate chamber and walk into the Court circle without leaving the
intended architectural route. Looking back from the circle, the path must visibly terminate in
the Greatbole rather than merely disappearing beside it.

---

## 3. The Amphitheatre

Immediately outside the gate, to the north. Marble and stone, and thoroughly ruined.

**There is no marble block in the load path, and there is no longer one on disk.** Conquest
Reforged — 227 MB of exactly this material — was deleted with the rest of `quarantine/` on
2026-09-03, and Quark is not installed. The substitute palette is therefore the palette, not a
placeholder:

| Reads as | Block |
|---|---|
| White marble | `minecraft:calcite`, `minecraft:smooth_quartz` |
| Veined / cut marble | `minecraft:quartz_block`, `minecraft:chiseled_quartz_block` |
| Columns | `minecraft:quartz_pillar` |
| Elven marble | `feywild:elven_quartz_block` |
| The ruin | `minecraft:cracked_stone_bricks`, `minecraft:mossy_stone_bricks`, `minecraft:mossy_cobblestone` |

Restoring Conquest Reforged would improve this more than any other single change, but it is now
a fresh CurseForge install rather than a file move, and it is a 227 MB pack-weight decision. The
aesthetic passes proceed on calcite and quartz unless that is revisited.

Form: concentric seating tiers around a sunken circular stage, opening toward the gate. Broken
column stumps around the rim, tiers collapsed in places, the stage cracked. The court's NPCs
stand on it — Velrous and Orenvel flanking the gate mouth, the six ambient elves scattered
through the tiers.

**The NPCs stay fixed.** Confirmed by the user, and it is the better call: `NoAI` already removes
targeting, wandering and despawn in one flag, and a frozen court cannot drift out of the
protected zone or path itself into the stage wall. Roaming would have needed a tether loop and a
`follow_range` of 0 to stop them shooting the player, for no gain.

---

## 4. The protected hub

> *"claimed preserved and protected, to have no mobs spawn within the area, to have no damage
> occur, so that if somehow a creeper does spawn it's not able to destroy anything."*

### 4.1 Two layers: the claim, and the enforcement

**`ftb-chunks-forge-2001.3.8` is installed.** The claim and the KubeJS enforcement are separate
layers, and both are required. `SPAWN_HUB_PROTECTION.md` owns the detailed acceptance gate.

- **The claim** is runtime world data, but it is no longer a deferred manual setup step. The
  generated `kubejs/server_scripts/04_spawn_hub.js` creates/reuses the `alfheim_hub` server team
  and runs `ftbchunks admin claim_as` for the full §4.2 envelope on server load. Reconciliation
  is therefore automatic and idempotent from the pack's point of view.
- **Claim command return values are not proof of ownership.** `tools/run_server.py` probes the
  centre and all four corners with `ftbchunks info`; `tools/check_spawn_hub_claim.py` requires
  each read-back to name `alfheim_hub`. Runtime acceptance remains pending until that read-back,
  ordinary-player edit tests, and restart persistence are observed.
- **The enforcement** — hostile-spawn suppression, explosion protection, mob/mechanism block
  protection, and explicit non-op break/place rejection — stays in `04_spawn_hub.js` even when
  the FTB claim is healthy. The layers are additive rather than substitutes for one another.

Settings worth setting once the FTB Chunks server config exists:
`max_idle_days_before_unclaim = 0` (a hub must never auto-release) and
`force_load_mode` left at its default.

| Layer | Needs FTB Chunks? | Status |
|---|---|---|
| No hostile spawns in the hub | no | built; runtime acceptance pending |
| No explosion damage to blocks | no | built; runtime acceptance pending |
| No mob/mechanism block griefing | no | built; runtime acceptance pending |
| No fire spread | no | built; runtime acceptance pending |
| Non-op block breaking/placement rejected | no | built; ordinary-player acceptance pending |
| Visible claim on the FTB map, team semantics | **yes** | automated statically; ownership/restart read-back pending |

### 4.2 Shape

A square region centred on **the origin**, radius **192 blocks**. Alfheim only; Midgard is
unaffected.

**Centred on the origin, not on the tree**, because the tree may relocate. The claim therefore
has to be big enough to contain the tree wherever placement puts it:

|  | blocks | why |
|---|---|---|
| biome-search displacement | 112 | worst case `findBiomeHorizontal` relocation (see §4.3) |
| half the base piece | 48 | so the claim reaches the far side of the trunk |
| amphitheatre apron | 32 | the court sits outside the trunk |
| **total** | **192** | |

> **Corrected 2026-09-04.** This was **96 blocks centred on the origin**, on the false premise
> — recorded in `gen_spawn_hub.py` — that `concentric_rings` with `distance: 0` pins the
> structure to `0,0`. It does not; see §4.3. The user reported the consequence directly: *"the
> spawn area around the Great Tree was never claimed and we didn't spawn inside it."*

### 4.3 Why the tree moves, and what pins it

`concentric_rings` computes the ring-0 position — which for `distance: 0, spread: 0` really is
chunk `0,0` — and then **snaps it to a `preferred_biomes` match** via
`findBiomeHorizontal(..., radius 112, findClosest = true)`. The same tag is read a second time,
as the structure's own `biomes` field, where it is a **validity** test rather than a position
one.

That made a narrow tag two separate bugs:

| Field | Effect of a narrow tag |
|---|---|
| `structure.biomes` | The Greatbole **does not generate at all** unless the chosen chunk's biome is tagged. With 3 of 16 layer biomes tagged, most worlds had no tree anywhere — the user's *"No spawn structure on Fresh World."* |
| `structure_set.preferred_biomes` | The search is forced outward, **moving the tree up to 112 blocks** from the origin — away from the claim and away from the spawn anchor. |

`findClosest` returns the **centre** when the centre matches, so the fix for both is the same:
tag everything buildable. `#alfheim:has_greatbole` now holds **14 of the 16 biomes** in the
Alfheim layer, which normally pins the structure to chunk `0,0` and lets
`project_start_to_heightmap: WORLD_SURFACE_WG` with `terrain_adaptation: beard_thin` do the
final terrain snap.

Two biomes stay out, because the terrain snap cannot rescue either:

- **`alfheim:void_verge`** — floating islands over nothing; there is no ground for the roots.
- **`mythicbotany:alfheim_lakes`** — `WORLD_SURFACE_WG` counts fluids, so the trunk would
  stand on the water surface.

When the origin lands in one of those, the search relocates to the nearest of the other
fourteen. That is why the claim is still sized for displacement rather than assuming `0,0`.

### 4.3a Terrain suitability is a placement condition, not an aesthetic pass

**Runtime defect, observed 2026-09-04:** the generated hub could jut bodily out of the side of a
cliff with essentially no terrain incorporation. The structure existing at a legal height is not
enough. `WORLD_SURFACE_WG` plus `beard_thin` can blend a legal placement; it does not prove that
the chosen 48×48 base footprint is suitable for a monumental tree and court.

The generator/placement logic must therefore treat **local relief across the entire Greatbole
footprint as a candidate test**. At minimum it should sample the centre, corners and edge zones of
the base. A severe cliff or abrupt elevation delta must cause one of two deliberate outcomes:

1. **reject and relocate** to another buildable candidate inside the allowed search envelope; or
2. **author real terrain incorporation** — root buttresses descending to ground, stepped
   foundations, terraces, retaining walls, buried/collapsed lower masonry and approach stairs
   that visibly carry the mass into the slope.

What is forbidden is the current failure mode: a flat or square base visibly cantilevered from a
cliff because the terrain happened to meet one side of the template. A cliff placement is only
acceptable when the architecture is visibly designed as a cliff structure and carries its load
to terrain.

### 4.4 Chunk loading

**The hub keeps a 13 × 13 chunk region loaded** (`KEEP = 6`). This reverses an earlier
"deliberately not force-loaded" decision, which was right about the cost and wrong about the
requirement: `@e` selectors only see **loaded** chunks, so with the hub unloaded
`hub/send` finds no anchor and silently teleports the player nowhere, and `hub/status` reports
the anchor as missing. The NPCs are still `NoAI` and still simulate nothing; what is being
bought is selector reachability, not AI.

Generation uses a much larger 33 × 33 region, and `hub/anchor` **releases it** once the
anchor resolves. Leaving it in place would have cost the server 1,089 permanently ticking
chunks for the life of the world.

---

## 5. Build passes

Pass 1 is generated. Runtime has now done its job: it exposed defects that static validation
could not see. Those defects are now the next work, not optional polish.

| Pass | Work | State |
|---|---|---|
| **1** | Parametric generator; base, trunk, crown, amphitheatre; jigsaw wiring; protection; checker | **done (static)** |
| **2** | Runtime proof: whole tree/crown, placement, gate and court inspected in a fresh world | **partial 2026-09-04 — crown proven; terrain and circulation failed acceptance** |
| **3** | Terrain-fit repair — reject bad cliff candidates or build genuine root/terrace/foundation integration | **open, priority** |
| **4** | Greatbole-to-Court circulation — continuous interior processional route into the ruined circle (§2.4) | **open, priority** |
| 5 | Silhouette and proportion — trunk taper, root spread, canopy mass | |
| 6 | The gate chamber interior — the "intricate" pass. Detail work at the frame |
| 7 | Amphitheatre ruin quality — collapse that reads as causal, not as random block removal |
| 8 | Court dressing — braziers, banners, scattered apothecaries, the Guard's armoury |
| 9 | Approach and sightlines — how the tree first reads from 200 blocks out |
| 10 | Interaction — final NPC post positions against the finished geometry rather than temporary offsets | **structure-baked now; final geometry-relative refinement open** |

The Court no longer depends on a player-relative summon path. Its eight elves are baked into
`court/amphitheatre.nbt` by `tools/gen_spawn_hub.py`, with names sourced from the shared manifest;
that branch has already been observed in the runtime hub. Pass 10 now means moving those baked
post coordinates as the finished circulation and amphitheatre geometry change, not migrating
ownership from `03_hollow_court.js`.

---

## 6. Placement

`concentric_rings`, `distance: 0`, `spread: 0`, `count: 1` — the vanilla mechanism for "at world
spawn", the one strongholds use. It removes any need for spawn-forcing code.

`SPAWN_ZONE.md` §7.1 applies directly: the Greatbole should be tagged
`continuityworks_spawn_protection:protected`, which enforces a 500-block exclusion around it, so
nothing else generates through the roots. The Hollow Court's city pieces must stay `ignored`, or
they will exclude each other.

**Placement acceptance is now explicitly two-stage:** first find a legal biome/position; then
prove the local terrain is suitable for the complete base footprint. `terrain_adaptation` is a
finishing operation, not permission to place a monumental structure on any slope the heightmap
can name. The cliff case observed on 2026-09-04 is a failed placement even though Minecraft
successfully generated it.

---

## 7. What is not decided

- ~~**Conquest Reforged**~~ — **settled 2026-09-03: gone.** The user cleared `quarantine/`, so
  the 227 MB block set is no longer on disk and the calcite/quartz palette in §3 is the palette.
  Restoring it would now mean a fresh CurseForge install, not a file move.
- ~~**FTB Chunks**~~ — **settled 2026-09-03, installed; automatic reconciliation implemented.**
  The remaining work is runtime ownership read-back, non-op break/place proof, and restart
  persistence under `SPAWN_HUB_PROTECTION.md`, not a one-time manual claim.
- ~~**Where the player actually arrives**~~ — **implemented: the gate chamber.** A fast first join
  crosses into Alfheim without waiting for the tree; when the baked hub anchor resolves,
  `hub/anchor` collects awaiting players into the gate chamber and anchors their respawn there.
  Runtime acceptance of a joining client on the current flow remains separate from this design
  state.
- **Whether the tree is climbable** at all, or scenery from the ground up. Boughs and canopy
  platforms are in `SPAWN_ZONE.md`'s inventory but are not built.