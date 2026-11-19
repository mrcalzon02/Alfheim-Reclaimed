'use strict'
// Source-level KubeJS login/respawn recovery regression. NOT a full Forge runtime test.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const vm = require('node:vm')

const script = fs.readFileSync('kubejs/server_scripts/02_spawn_dimension.js', 'utf8')
const SEND = 'execute as TestElf at @s run function alfheim:hub/send'
const HOME = 'mythicbotany:alfheim'

function scenario({ atHome = false, confirmed = false, unlocked = false,
                    awaiting = false, buried = false, deliveryWorks = true } = {}) {
    let isInHome = atHome
    let works = deliveryWorks
    const flags = new Map()
    if (confirmed) flags.set('alfheim_home_spawn_v2', true)
    if (unlocked) flags.set('alfheim_midgard_unlocked', true)
    const commands = []
    const queue = []
    const warnings = []
    const loginHandlers = []
    const respawnHandlers = []
    const player = {
        username: 'TestElf',
        persistentData: {
            getBoolean(key) { return flags.get(key) === true },
            putBoolean(key, value) { flags.set(key, !!value) }
        }
    }
    const server = {
        runCommandSilent(command) {
            commands.push(command)
            if (command.includes('if entity @e[type=minecraft:player,name=TestElf,limit=1]'))
                return isInHome ? 1 : 0
            if (command.includes('if entity @s[tag=alfheim_awaiting_hub]')) {
                if (awaiting && works) isInHome = true
                return awaiting ? 1 : 0
            }
            if (command.includes('if entity @s[distance=..16]')) {
                if (buried && works) isInHome = true
                return buried ? 1 : 0
            }
            if (command === SEND) {
                if (works) isInHome = true
                return works ? 1 : 0
            }
            return 1
        },
        scheduleInTicks(ticks, fn) {
            assert.equal(ticks, 20, 'dimension recovery uses the fixed verify delay')
            queue.push(fn)
        }
    }
    const context = {
        console: { info() {}, warn(value) { warnings.push(String(value)) } },
        PlayerEvents: {
            loggedIn(handler) { loginHandlers.push(handler) },
            respawned(handler) { respawnHandlers.push(handler) }
        }
    }
    vm.runInNewContext(script, context, { filename: '02_spawn_dimension.js', timeout: 3000 })
    assert.equal(loginHandlers.length, 1, 'exactly one player-login handler')
    assert.equal(respawnHandlers.length, 1, 'exactly one respawn guard')
    return {
        login() { loginHandlers[0]({ server, player }) },
        respawn() { respawnHandlers[0]({ server, player }) },
        tick() { while (queue.length) queue.shift()() },
        get atHome() { return isInHome },
        get mainSends() { return commands.filter(c => c === SEND).length },
        get respawnWrites() { return commands.filter(c => c.includes('run spawnpoint @s')).length },
        get queued() { return queue.length },
        setDeliveryWorks(value) { works = value },
        flags, commands, warnings
    }
}

const established = scenario({ atHome: true, confirmed: true })
established.login()
assert.equal(established.mainSends, 0, 'returning Alfheim player keeps their exact location')
assert.equal(established.respawnWrites, 0, 'returning player does not lose a bed/respawn point')
assert.equal(established.queued, 0)

const rescued = scenario({ atHome: false, confirmed: true })
rescued.login()
assert.equal(rescued.mainSends, 1, 'previously confirmed player stranded in Midgard is recovered')
assert.equal(rescued.atHome, true)
assert.equal(rescued.flags.get('alfheim_home_spawn_v2'), true)
assert.match(rescued.warnings.join(' '), /before unlocking Midgard; recovering/)
rescued.login()
assert.equal(rescued.mainSends, 1, 'subsequent normal login does not repeat teleport')

const blocked = scenario({ atHome: false, confirmed: true, deliveryWorks: false })
blocked.login()
assert.equal(blocked.atHome, false, 'a failed move never counts as an arrival')
assert.equal(blocked.queued, 1, 'failed move is rechecked after delay')
blocked.tick()
assert.equal(blocked.atHome, false)
blocked.setDeliveryWorks(true)
blocked.login()
assert.equal(blocked.mainSends, 2, 'stale v2 flag does not block later recovery')
assert.equal(blocked.atHome, true)
assert.equal(blocked.flags.get('alfheim_home_spawn_v2'), true)

const newcomer = scenario()
newcomer.login()
assert.equal(newcomer.mainSends, 1, 'new player still receives hub delivery')
assert.equal(newcomer.atHome, true)
assert.equal(newcomer.flags.get('alfheim_home_spawn_v2'), true)

const allowed = scenario({ atHome: false, confirmed: true, unlocked: true, awaiting: true })
allowed.login()
assert.equal(allowed.commands.length, 0,
    'gate-unlocked returning player must not even attempt provisional-hub correction')
assert.equal(allowed.mainSends, 0)
allowed.respawn()
assert.equal(allowed.commands.length, 0, 'gate-unlocked respawn is never forcibly recalled')

const awaitingHome = scenario({ atHome: true, confirmed: true, awaiting: true })
awaitingHome.login()
assert.ok(awaitingHome.commands.some(c => c.includes('if entity @s[tag=alfheim_awaiting_hub]')),
    'locked player still receives provisional-hub reconciliation')

const respawn = scenario({ atHome: false, confirmed: true })
respawn.respawn()
assert.equal(respawn.queued, 1)
respawn.tick()
assert.equal(respawn.mainSends, 1, 'stranded locked respawn still repaired')
assert.equal(respawn.atHome, true)

const safeRespawn = scenario({ atHome: true, confirmed: true })
safeRespawn.respawn()
safeRespawn.tick()
assert.equal(safeRespawn.mainSends, 0, 'Alfheim bed respawn should remain untouched')

console.log('SPAWN_DIMENSION_RECOVERY_PASS: confirmed-home, stranded-login, failed delivery/retry, new player, unlocked Midgard, awaiting hub, respawn and bed safety')
