# From the installed foundation to usable golems

Updated plan: 2026-10-17. This is the current delivery order; retain the detailed invariants in
`ALFHEIM_GOLEMS_PLAN.md`. No new playable golems are claimed by this planning change.

## Product and ownership

**A player can craft an elven workshop assistant, give it a simple job, see why it pauses, and
recover its real inventory without loss.** A persistent Worker is the first release outcome.

MineColonies owns settlement construction, citizens, research, settlement growth and reclamation
of land. Golems own bounded inventory transport and workshop operations. They do not survey land,
build colony houses, staff colony jobs or claim territory. A colony may supply a workshop through
its normal systems, but a golem only touches an explicitly permitted endpoint. Companion tasks
retain their existing independent ownership and lifecycle.

## Actual starting point

The Java 17/Forge project, wrapper, installed `alfheim_golems-0.1.0.jar`, configuration,
diagnostics, domain enums/interfaces, transfer contracts and tests already exist. The SavedData
envelope currently records an empty versioned schema and zero network/order counts. The mod entry
point registers no items, entities or menus. There is no active scheduler, navigation, real
inventory executor, Command Gem, work-order UI or playable crafting/acquisition route.

Reuse that foundation. The next action is an evidence refresh of G0 followed by the first G1
slice, not scaffolding another project. Existing build reports are historical evidence; they do
not certify a new gameplay implementation.

## Delivery order

| Release | Usable result | First supported scope | Acceptance required before expanding |
|---|---|---|---|
| Worker courier | Craft/place one owned Fire Worker and move an exact amount between two bound containers | Same dimension, loaded chunks, explicit item filter, one source and one destination | Real transfer, ownership, pause/recovery, death, save/restart and client interaction |
| Workshop Worker | Repeat routes, tend a furnace, and perform a bounded 2x2 recipe | Vanilla furnace family; item-handler transport; selected ordinary recipes with exact remainders | Automated furnace cycle and repeat/shift/cancellation/concurrency cases; measured small-workshop load |
| Artisan | Perform 3x3 crafting and a short source/process/deliver sequence | Crafting table plus one specifically audited machine adapter | Valid recipe execution, container remainders, contention, restart at every committed state and visible status |
| Temporary Sentinel | Spend a vessel for a time-limited allied defender | One proved element first, then the other elements | Exactly-once consumption, friendly-fire rules, MMO combat path and zero expiry/reload rewards |
| Deep salvage and wider support | Encounter wild forms and recover useful parts; admit additional machine adapters | Bounded Deep-only habitats and adapter-specific support | Natural density/loot surveys, zero surface/Midgard spawns, cost balance and per-adapter evidence |

The first courier release is independently valuable. Wild spawns, four elemental bonuses, all
machine families and Sentinel combat are not prerequisites for shipping its accepted capability.
Keep G0–G8 identifiers for continuity; G5's broad wild ecology can follow the owned releases and G6.

## First Worker: exact player flow

1. Craft the Command Gem, Simple Fire Core and Worker Effigy through reachable pack recipes.
2. Use the effigy on a clear, supported location. The server validates placement; one successful
   creation consumes one effigy and binds one owner. Invalid placement consumes nothing.
3. Use the gem on the Worker to select it. Its name, owner, carried items, job and status are visible.
4. Mark a source container and a destination container using server-validated block interactions.
   The command interface labels each role explicitly; do not require the player to write a script
   or infer source/destination from an unexplained click combination.
5. Choose one item filter and either a quantity or repeat mode, then start. The Worker takes only
   permitted items it can carry, physically walks the route and inserts only what the destination
   can accept. It never teleports inventory between endpoints.
6. Follow, Stay, Start, Pause, Return Cargo and Dismantle are available as appropriate. Dismantling
   requires idle, healthy and empty state and returns one effigy. Return Cargo moves real carried
   items; a blocked return pauses and explains the obstruction.

Initial budgets: one active order per Worker, at most two endpoints for a courier order, 16-block
endpoint search from a selected Worker (explicit endpoints only), configured navigation limit up
to 64 blocks, and at most one inventory mutation per ten ticks. Search is not a container scan
through arbitrary claimed land. Global scheduling uses the existing bounded configuration. These
are initial implementation targets, to be measured before broad deployment.

## Implementable slices and dependencies

| Slice | Concrete implementation | Result to demonstrate |
|---|---|---|
| G0 refresh | Validate existing built/installed artifact and tests; record actual hashes, full-pack boot and empty schema reload evidence | Current foundation status is factual; missing gates stay named |
| G1.1 lifecycle | Entity/item registration, Fire Worker model, inventory, core/effigy, placement and owner UUID | One reachable creation route; invalid placement and non-owner commands reject |
| G1.2 command and endpoints | Command Gem, small menu, server-bound endpoint/filter records, bounded packet validation and FTB claims adapter | Select Worker, inspect cargo, bind two owned/permitted containers; reject spoofed or revoked access |
| G1.3 transfer executor | Implement the existing transfer interfaces against real sided item handlers; navigation and last-moment validation | Move a requested stack exactly once while conserving source + cargo + destination |
| G1.4 recovery and status | Persist endpoint IDs, order state, quantity remaining, entity cargo and owner; revalidate on load | Full, missing, inaccessible or unloaded destination pauses with the cargo intact |
| G1.5 usable acquisition | Finalize reachable core/gem/effigy recipes and reference instructions; capture normal command flow | A survival player creates and operates the Worker with no operator commands |
| G2 | Furnace input/fuel/output, repeating routes and real 2x2 recipe execution | Chest → furnace → chest and crafting-with-remainders work across interruption |
| G3/G4 | Recursive Advanced core, Artisan lifecycle, 3x3 executor and one admitted processing adapter | One complete delegated workshop sequence, with exact inventory accounting |
| G6 | Combat core/vessel, one Sentinel, expiry and MMO/team integration | A bounded allied summon cannot become permanent or refund its vessel |
| G5/G7/G8 | Wild salvage, later elements/adapters, teaching, migrations and scale | Broader features gain their own evidence without weakening accepted courier behavior |

Implementation remains in `com.continuityworks.alfheimgolems`: add `registry/`, `entity/`,
`brain/`, `menu/`, `network/` and `integration/ftb/`; turn the existing `inventory/`, `order/`,
`machine/` and `data/` contracts into executors. Do not import companion-private implementations.
Persist real jobs with an explicit schema migration; the present zero-count envelope is not an
order store.

## Acquisition and operating costs

Preserve the accepted layered core design: shaped chassis parts, Botania mana/runic binding and
Ars preparation produce a completed aligned core. Simple → Advanced → Combat consumes the prior
family recursively. Worker/Artisan shells are recoverable only through safe dismantling; death
returns bounded damaged parts. Command Gems are reusable.

The implementation must first audit exact installed item IDs, station formats and campaign
availability, then write explicit ingredient quantities and costs. Do not name unregistered
components as if they exist. Scratch crafting must be possible without wild salvage, so deferring
natural spawns cannot soft-lock acquisition. Salvage later reduces bulk costs while retaining
the appropriate magical preparation.

Keep item-backed crafting/placement costs in the first courier release. A running fuel or mana
drain requires an explicit implemented energy store, refill route and visible empty state; no
fictional mana consumption should be added as a tooltip. Any later operating cost must preserve
carried cargo on exhaustion.

## Inventory, claims and persistence invariants

- Every committed extraction puts the items in the real Worker inventory. That inventory is the
  recovery ledger; never also restore an invented copy to the source.
- Simulate insertion, then revalidate both access and actual acceptance at commit. Reservations
  coordinate golems but do not replace capability checks or promises of available space.
- After cancellation, death, unload or restart, source + cargo + destination + legitimate drops
  reconcile. Two Workers competing for the last stack cannot both obtain it.
- An inaccessible/unloaded chunk pauses work. Workers create no chunk tickets, operate across no
  dimension boundary and do not manipulate inventories while they are away from the endpoint.
- Non-owners need explicit team/claim permission; revoke access between selection and commit to
  verify that cached approval is not sufficient. Unsupported claims integration denies mutation.
- Ordinary golem work never grants a player personal Mine and Slash gathering/profession proof.
  A native machine produces its own output once; golems do not duplicate its XP or rewards.
- A future schema opens safely without deleting orders. Disabling work pauses orders and keeps
  cargo; it never deletes entities, records or inventory to make a diagnostic pass.

## Mandatory evidence for a usable release

Codex owns the checks. Do not ask the pack owner to launch a world or complete acceptance steps.
Use focused unit/transaction checks, GameTests/scripted dedicated servers and automated client
interaction/capture where appropriate; report any unavailable gate honestly.

The courier failure matrix covers destination full, removed source/destination, blocked route,
chunk unload, permission revoked before insertion, killed carrier, cancellation while carrying,
restart after extraction, two competing Workers and malformed/stale command requests. Each case
must preserve item counts and produce a comprehensible status.

Automated client evidence must show the recipe/acquisition route, successful effigy placement,
model and hitbox, source/destination labels, cargo display and the paused/full-destination state.
Native MMO item counting and FTB claims require full-pack scenarios. Later adapters receive an
explicit supported-block/version ledger. No client or server acceptance is claimed by this plan.

## Next exact action

Refresh G0 evidence for the existing artifact and schema, then implement **G1.1: one owned Fire
Worker with real inventory and a craftable effigy**. Keep the active slice on G1 until the
source → Worker → destination route, interruption recovery and player-facing command flow pass.
