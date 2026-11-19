'use strict'
// Source-level KubeJS grant regression. Does not prove Forge inventory persistence.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const vm = require('node:vm')
const script = fs.readFileSync('kubejs/server_scripts/01_starting_kit.js', 'utf8')
const expected = [
    ['botania:lexicon', 1],
    ['ftbquests:book', 1],
    ['botania:fertilizer', 2],
    ['botania:white_petal', 4]
]

function scenario({ missing = [], failing = [], completed = false } = {}) {
    const flags = new Map(completed ? [['alfheim_starting_kit_v2', true]] : [])
    const granted = []
    const known = new Set(expected.map(([id]) => id).filter(id => !missing.includes(id)))
    const failures = new Set(failing)
    let login = null
    const player = {
        username: 'new_elf',
        persistentData: {
            getBoolean(key) { return flags.get(key) === true },
            putBoolean(key, value) { flags.set(key, !!value) }
        },
        give(stack) {
            if (failures.has(stack.id)) throw new Error('synthetic inventory failure')
            granted.push([stack.id, stack.count])
        }
    }
    const item = {
        of(id, count) {
            return { id, count, isEmpty() { return !known.has(id) } }
        }
    }
    const context = {
        Item: item,
        console: { warn() {}, info() {} },
        PlayerEvents: { loggedIn(callback) { login = callback } }
    }
    vm.runInNewContext(script, context, { filename: '01_starting_kit.js', timeout: 3000 })
    assert.equal(typeof login, 'function', 'login handler registered')
    return {
        login() { login({ player }) },
        flags, granted,
        register(id) { known.add(id) },
        restoreGrant(id) { failures.delete(id) }
    }
}
const fresh = scenario()
fresh.login()
assert.deepEqual(fresh.granted, expected, 'fresh kit includes the correct quantities')
assert.equal(fresh.flags.get('alfheim_starting_kit_v2'), true)
fresh.login()
assert.equal(fresh.granted.length, expected.length, 're-login never reissues completed kit')

const missing = scenario({ missing: ['botania:white_petal'] })
missing.login()
assert.equal(missing.granted.length, expected.length - 1)
assert.equal(missing.flags.get('alfheim_starting_kit_v2'), undefined,
    'missing item leaves the whole kit pending')
missing.register('botania:white_petal')
missing.login()
assert.deepEqual(missing.granted[missing.granted.length - 1], ['botania:white_petal', 4])
assert.equal(missing.granted.length, expected.length, 'prior successful entries are not duplicated')
assert.equal(missing.flags.get('alfheim_starting_kit_v2'), true)
missing.login()
assert.equal(missing.granted.length, expected.length)

const failed = scenario({ failing: ['ftbquests:book'] })
failed.login()
assert.equal(failed.granted.length, expected.length - 1)
assert.equal(failed.flags.get('alfheim_starting_kit_v2'), undefined)
failed.restoreGrant('ftbquests:book')
failed.login()
assert.deepEqual(failed.granted[failed.granted.length - 1], ['ftbquests:book', 1])
assert.equal(failed.granted.length, expected.length)
assert.equal(failed.flags.get('alfheim_starting_kit_v2'), true)

const legacy = scenario({ completed: true })
legacy.login()
assert.equal(legacy.granted.length, 0, 'legacy v2 completion must be honored')
console.log('STARTING_KIT_RECOVERY_PASS: first grant, quantities, partial retry, failure retry, no duplication, legacy v2')
