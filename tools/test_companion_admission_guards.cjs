'use strict'
// Test production source admission ordering, not a Minecraft runtime.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const root = 'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/'
const summon = fs.readFileSync(root + 'service/CompanionSummonService.java', 'utf8')
const events = fs.readFileSync(root + 'CompanionEvents.java', 'utf8')
const data = fs.readFileSync(root + 'memory/CompanionSavedData.java', 'utf8')

const join = events.slice(events.indexOf('public static void onEntityJoin('),
    events.indexOf('public static void onCompanionDeath('))
assert.match(join, /!data\.allowsCompanionJoin\(companion\.getUUID\(\), companion\.ownerUuid\(\)\)/,
    'entity join must verify committed identity or an ephemeral reservation')
assert.doesNotMatch(join, /data\.bind\(/, 'join event must not commit unverified entity identity')
assert.match(data, /private final CompanionAdmissionGate admissionGate = new CompanionAdmissionGate\(\)/,
    'saved companion state needs one transient admission gate')
assert.match(data, /admissionGate\.allows\(entity, owner, companionUuid, ownerUuid\)/,
    'admission must check both UUID and owner against the committed state')
assert.doesNotMatch(data.slice(data.indexOf('public CompoundTag save(')),
    /pendingEntity|pendingOwner|admissionGate\./,
    'pending admission must not be serialized')
const summonBegin = summon.indexOf('if (companion == null) {')
const summonEnd = summon.indexOf('        } else {', summonBegin)
const fresh = summon.slice(summonBegin, summonEnd)
const begin = fresh.indexOf('data.beginCompanionAdmission(candidateId, owner.getUUID())')
const add = fresh.indexOf('owner.serverLevel().addFreshEntity(companion)')
const finish = fresh.indexOf('data.endCompanionAdmission(candidateId, owner.getUUID())')
const reject = fresh.indexOf('if (!admitted) {')
assert.ok(begin > 0 && add > begin && finish > add && reject > finish,
    'reserve, call Forge, release reservation in finally, then inspect actual result')
assert.match(fresh, /finally \{\s*data\.endCompanionAdmission\(candidateId, owner\.getUUID\(\)\)/,
    'failed or throwing admission must always release its reservation')
assert.doesNotMatch(fresh, /data\.bind\(|data\.claimOrRefreshLease\(|data\.releaseLease\(|data\.dismiss\(/,
    'no successful Forge insertion must mean no persistent identity or lease changes')
const commit = summon.indexOf('data.bind(companion.getUUID(), owner.getUUID()')
const activate = summon.indexOf('data.activatePlayerBinding(owner.getUUID(), now)')
const lease = summon.indexOf('data.claimOrRefreshLease(owner.getUUID(), now)')
const gear = summon.indexOf('data.restoreFallenInventory(owner.getUUID(), companion)')
const transfer = summon.indexOf('Entity moved = companion.changeDimension(owner.serverLevel())')
const transferReject = summon.indexOf('Cross-dimensional companion recall failed')
const entityRebind = summon.indexOf('companion.bindOwner(owner.getUUID());', summonEnd)
assert.ok(transfer > add && transferReject > transfer && entityRebind > transferReject,
    'failed dimension change must not change the loaded companion owner')
assert.ok(commit > add && activate > add && lease > activate && gear > commit,
    'persistent admission, lease and inventory restoration must follow successful spawn')
console.log('COMPANION_ADMISSION_SOURCE_PASS: reserved new join, fail-safe cleanup, committed reload and deferred owner/gear persistence')
