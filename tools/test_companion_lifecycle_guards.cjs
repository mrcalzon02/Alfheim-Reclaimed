'use strict'
// Source-order safety checks, not Forge runtime acceptance.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const root = 'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/'
const ticket = fs.readFileSync(root + 'service/CompanionChunkTickets.java', 'utf8')
const summon = fs.readFileSync(root + 'service/CompanionSummonService.java', 'utf8')
const death = fs.readFileSync(root + 'service/CompanionDeathInventoryService.java', 'utf8')
assert.match(ticket, /for\s*\(ChunkTicketDelta\.Change change : ChunkTicketDelta\.moving\(/,
    'production ticket transition must use tested difference planner')
assert.match(ticket, /else if \(existing\.level\(\) != level\)/,
    'cross-dimensional tickets must remain handled separately')
assert.doesNotMatch(ticket, /force\(level, companion\.getUUID\(\), center, true\);\s*if \(existing != null\) force\(/,
    'stale algorithm may remove overlapping forced chunks')
const first = summon.indexOf('if (companion == null) {')
const last = summon.indexOf('        } else {', first)
assert.ok(first >= 0 && last > first, 'fresh summon branch not found')
const fresh = summon.slice(first, last)
const admission = fresh.indexOf('if (!owner.serverLevel().addFreshEntity(companion)) {')
const restore = fresh.indexOf('data.restoreFallenInventory(owner.getUUID(), companion);')
assert.ok(admission >= 0 && restore > admission, 'gear restored before entity admission')
assert.match(fresh.slice(admission, restore), /return;/,
    'failed admission must exit without consuming saved gear')
assert.equal((fresh.match(/restoreFallenInventory/g) || []).length, 1, 'gear restored twice')
assert.match(summon, /if \(!\(moved instanceof ElvenCompanionEntity movedCompanion\)[\s\S]*?return;\s*\}\s*companion = movedCompanion/,
    'failed cross-world recall must not report a successful new position')
const dismiss = summon.slice(summon.indexOf('    public static void dismiss('))
const storeCall = dismiss.indexOf('CompanionDeathInventoryService.retainForDismiss(companion, data, owner.getUUID())')
const discardCall = dismiss.indexOf('companion.discard()')
const releaseCall = dismiss.indexOf('data.releaseLease()')
assert.ok(storeCall >= 0 && discardCall > storeCall,
    'dismiss must persist carried items before discarding the entity')
assert.ok(releaseCall > discardCall, 'owner mismatch must not release an active lease')
assert.match(dismiss.slice(storeCall, discardCall), /return;/,
    'inventory ownership mismatch must abort dismissal')
const retain = death.slice(death.indexOf('    public static boolean retainForDismiss('),
    death.indexOf('    public static void handle('))
assert.match(retain, /expectedOwner == null \|\| !expectedOwner\.equals\(companion\.ownerUuid\(\)\)/,
    'never save another player\'s carried items under the requester')
const saved = retain.indexOf('data.storeFallenInventory(expectedOwner, carried, equipment)')
const cleared = retain.indexOf('companion.inventory().clearContent()')
assert.ok(saved >= 0 && cleared > saved,
    'all carried items must be persisted before clearing live inventory')
assert.match(retain.slice(saved), /companion\.setItemSlot\(slot, ItemStack\.EMPTY\)/,
    'equipped items must be cleared only after saving')
console.log('COMPANION_LIFECYCLE_GUARDS_PASS: chunk delta wired, summon admission protected, cross-world transfer guarded, dismiss inventory persisted before discard')
