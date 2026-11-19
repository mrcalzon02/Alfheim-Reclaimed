'use strict'
// Source-order safety checks, not Forge runtime acceptance.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const root = 'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/'
const ticket = fs.readFileSync(root + 'service/CompanionChunkTickets.java', 'utf8')
const summon = fs.readFileSync(root + 'service/CompanionSummonService.java', 'utf8')
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
console.log('COMPANION_LIFECYCLE_GUARDS_PASS: ticket delta wired; rejected spawn keeps inventory; failed cross-world recall aborts')
