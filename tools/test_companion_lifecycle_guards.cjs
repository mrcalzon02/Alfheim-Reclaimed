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
const reservation = fresh.indexOf('data.beginCompanionAdmission(candidateId, owner.getUUID())')
const admission = fresh.indexOf('owner.serverLevel().addFreshEntity(companion)')
const release = fresh.indexOf('data.endCompanionAdmission(candidateId, owner.getUUID())')
const committedName = summon.indexOf('data.activatePlayerBinding(owner.getUUID(), now)')
const restore = summon.indexOf('if (newlyCreated || changingLessee) data.restoreFallenInventory(owner.getUUID(), companion)')
assert.ok(reservation >= 0 && admission > reservation && release > admission,
    'admission must be staged, attempted and cleared in that order')
assert.ok(restore > committedName && committedName > admission,
    'gear restoration and owner activation must follow successful entity admission')
assert.doesNotMatch(fresh, /data\.bind\(|data\.dismiss\(|data\.releaseLease\(/,
    'rejected spawn must not modify the committed companion identity or release a lease')
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
const aliveCheck = summon.indexOf('if (!data.getOrCreatePlayerBinding(owner.getUUID(), now).alive())')
const handoff = summon.indexOf('boolean changingLessee =')
const previousStash = summon.indexOf('CompanionDeathInventoryService.retainForDismiss(companion, data, previousOwner)')
const activeName = summon.indexOf('data.activatePlayerBinding(owner.getUUID(), now)')
const transferred = summon.indexOf('Entity moved = companion.changeDimension(owner.serverLevel())')
assert.ok(aliveCheck >= 0 && handoff > aliveCheck && previousStash > transferred && activeName > previousStash,
    'reject dead bindings and verify dimension transfers before saving old cargo or switching owners')
const handoffBranch = summon.slice(handoff, activeName)
const presenceDecision = handoffBranch.indexOf('CompanionHandoffRules.evaluate(')
const missingActiveGuard = handoffBranch.indexOf('if (decision == CompanionHandoffRules.Decision.BLOCK_UNLOADED_ACTIVE)')
const mismatchGuard = handoffBranch.indexOf('if (decision == CompanionHandoffRules.Decision.BLOCK_OWNER_MISMATCH)')
const ownerChange = handoffBranch.indexOf('if (changingLessee) {')
assert.ok(presenceDecision >= 0 && missingActiveGuard > presenceDecision
    && mismatchGuard > missingActiveGuard && ownerChange > mismatchGuard,
    'both presence guards must execute for same-owner and cross-owner requests before handoff')
assert.match(handoffBranch.slice(missingActiveGuard, mismatchGuard),
    /lastKnown\.getX\(\)[\s\S]*?lastKnown\.getY\(\)[\s\S]*?lastKnown\.getZ\(\)[\s\S]*?return;/,
    'blocked summon must give the player the last recorded coordinates and abort')
assert.match(handoffBranch.slice(mismatchGuard, ownerChange), /operator investigation required\."\)\);\s*return;/,
    'entity-owner mismatch must refuse every request, not just transfers')
assert.match(handoffBranch, /Decision\.SAVE_LOADED_COMPANION[\s\S]*?retainForDismiss\(companion, data, previousOwner\)/,
    'verified old cargo must be saved under its original owner')
assert.match(summon, /if \(newlyCreated \|\| changingLessee\) data\.restoreFallenInventory\(owner\.getUUID\(\), companion\)/,
    'only newly admitted or successfully transferred companions restore the requester cargo')
console.log('COMPANION_LIFECYCLE_GUARDS_PASS: transient spawn admission, cross-world handoff order, owner integrity and inventory isolation')
