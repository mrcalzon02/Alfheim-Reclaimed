'use strict'
// Verify that the real source refuses unsafe summon/recall and unloaded dismissal.
// These are source-level contract checks; only the separate Java 17 test executes
// candidate generation and only a booted Forge runtime can validate world collision.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const root = 'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/service/'
const summon = fs.readFileSync(root + 'CompanionSummonService.java', 'utf8')

const preflight = summon.indexOf('Vec3 loadedDestination = loadedCompanion == null')
const handoff = summon.indexOf('boolean changingLessee =')
const firstMutation = summon.indexOf('data.activatePlayerBinding(owner.getUUID(), now)')
assert.ok(preflight >= 0 && handoff > preflight && firstMutation > handoff,
    'validate loaded recall landing before storing previous owner inventory or changing lease')
const loadedFail = summon.slice(preflight, handoff)
assert.match(loadedFail, /loadedCompanion != null && loadedDestination == null/)
assert.match(loadedFail, /return;/)

const fresh = summon.slice(summon.indexOf('if (companion == null) {'), summon.indexOf('        } else {', summon.indexOf('if (companion == null) {')))
const find = fresh.indexOf('Vec3 destination = findSafeSummonPosition(owner, companion)')
const initialBind = fresh.indexOf('data.bind(companion.getUUID(), owner.getUUID()')
const admission = fresh.indexOf('addFreshEntity(companion)')
assert.ok(find >= 0 && find < initialBind && initialBind < admission,
    'new summon must find a valid position before saving a new companion identity')
assert.match(fresh.slice(find, initialBind), /if \(destination == null\)[\s\S]*?data\.releaseLease\(\);[\s\S]*?return;/,
    'no valid new spawn must fail without creating or binding an entity')

const method = summon.slice(summon.indexOf('private static Vec3 findSafeSummonPosition('))
assert.match(method, /CompanionLandingPlan\.candidates\(\)/, 'use tested exhaustive candidate planner')
assert.match(method, /if \(level\.noCollision\(companion\)\) return companion\.position\(\)/)
assert.match(method, /return null;\s*\} finally \{[\s\S]*?companion\.setPos\(original\.x, original\.y, original\.z\)/,
    'a failed collision scan must restore original entity coordinates')
assert.doesNotMatch(method, /owner\.position\(\)\.add\(1\.0D/,
    'never put companion at an unchecked fallback position')
assert.match(method, /floor\.isFaceSturdy/, 'require a supporting floor')
assert.match(method, /unsafeLandingBlock\(level\.getBlockState\(candidate\)\)/,
    'reject harmful floor-space blocks')
assert.match(method, /unsafeLandingBlock\(level\.getBlockState\(candidate\.above\(\)\)\)/,
    'reject harmful head-space blocks')

const dismiss = summon.slice(summon.indexOf('public static void dismiss('))
const unloadedGuard = dismiss.indexOf('if (companion == null')
const release = dismiss.indexOf('data.releaseLease()')
const discard = dismiss.indexOf('companion.discard()')
assert.ok(unloadedGuard >= 0 && unloadedGuard < discard && discard < release,
    'unloaded active companion must not be dismissed without retaining its inventory')
assert.match(dismiss.slice(unloadedGuard, discard), /data\.mode\(\) != [\s\S]*?CompanionMode\.DISMISSED[\s\S]*?return;/,
    'unloaded active companion must keep its lease and mode unchanged')
console.log('COMPANION_LANDING_SAFETY_PASS: validated-only summon/recall, state-safe probing, and unloaded-dismiss guard')
