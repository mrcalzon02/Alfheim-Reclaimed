'use strict'
// Source-level FTB ownership state-machine regression. This is NOT a Forge/FTB runtime test.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const vm = require('node:vm')

const shipping = fs.readFileSync('kubejs/server_scripts/04_spawn_hub.js', 'utf8')
const template = fs.readFileSync('tools/templates/spawn_hub_protection.js', 'utf8')
function value(name) {
    const match = shipping.match(new RegExp('const\\s+' + name + '\\s*=\\s*(-?\\d+)'))
    assert.ok(match, 'missing generated constant ' + name)
    return Number(match[1])
}
const dimensionMatch = shipping.match(/const\s+HUB_DIMENSION\s*=\s*'([^']+)'/)
assert.ok(dimensionMatch, 'missing generated dimension')
let rendered = template.replace('__HOME_DIMENSION__', dimensionMatch[1])
for (const name of ['HUB_MIN_X', 'HUB_MAX_X', 'HUB_MIN_Z', 'HUB_MAX_Z']) {
    rendered = rendered.replace('__' + name + '__', String(value(name)))
}
assert.equal(shipping, rendered, 'shipping KubeJS script must match generator template')

const first = Math.floor(value('HUB_MIN_X') / 16) + ',' + Math.floor(value('HUB_MIN_Z') / 16)
function scenario(mode) {
    let nowMs = 100000
    const messages = { info: [], warn: [], error: [] }
    const logs = Object.fromEntries(Object.keys(messages).map(kind =>
        [kind, line => messages[kind].push(String(line))]))
    const teamId = { id: 'admin', equals(other) { return !!other && other.id === this.id } }
    const foreignId = { id: 'foreign', equals(other) { return !!other && other.id === this.id } }
    const playerId = { id: 'player', equals(other) { return !!other && other.id === this.id } }
    function team(id, serverTeam) {
        return {
            isServerTeam: () => serverTeam,
            getId: () => id,
            getProperty: () => 'alfheim_hub',
            setProperty() {},
            markDirty() {}
        }
    }
    const admin = team(teamId, true)
    const foreign = team(foreignId, true)
    const player = team(playerId, false)
    const claims = new Map()
    if (mode === 'foreign') claims.set(first, foreign)
    let unclaims = 0
    let playerDataCalls = 0
    let attempts = 0
    let callback = null
    const queue = []
    const chunkManager = {
        getChunk(pos) {
            const owner = claims.get(pos.key)
            return owner ? {
                getTeamData: () => ({ getTeam: () => owner }),
                unclaim() { unclaims++; claims.delete(pos.key) }
            } : null
        },
        getOrCreateData(t) {
            if (!t.isServerTeam()) playerDataCalls++
            return {
                claim(_source, pos, checkOnly) {
                    assert.equal(checkOnly, false)
                    if (mode === 'deny' && pos.key === first) {
                        return { isSuccess: () => false, getResultId: () => 'DENIED' }
                    }
                    if (!claims.has(pos.key)) claims.set(pos.key, t)
                    return { isSuccess: () => true, getResultId: () => 'OK' }
                },
                saveNow() {},
                syncChunksToAll() {}
            }
        }
    }
    const manager = {
        getTeamByName() {
            attempts++
            return { orElse: () => mode === 'missing' ? null : mode === 'nonserver' ? player : admin }
        },
        getTeams() { return { toArray: () => (mode === 'missing' || mode === 'nonserver') ? [] : [admin] } },
        createServerTeam() { return null }
    }
    class ChunkDimPos {
        constructor(_dimension, x, z) { this.key = x + ',' + z }
    }
    const classes = {
        'dev.ftb.mods.ftbteams.api.FTBTeamsAPI': { api: () => ({ getManager: () => manager }) },
        'dev.ftb.mods.ftbchunks.data.ClaimedChunkManagerImpl': { getInstance: () => chunkManager },
        'dev.ftb.mods.ftblibrary.math.ChunkDimPos': ChunkDimPos,
        'dev.ftb.mods.ftbteams.api.property.TeamProperties': {
            DISPLAY_NAME: 'name', DESCRIPTION: 'description', COLOR: 'color'
        },
        'dev.ftb.mods.ftbchunks.api.FTBChunksProperties': {
            BLOCK_EDIT_MODE: 'block', BLOCK_INTERACT_MODE: 'interact',
            ENTITY_INTERACT_MODE: 'entity', NONLIVING_ENTITY_ATTACK_MODE: 'attack',
            ALLOW_EXPLOSIONS: 'explosions', ALLOW_MOB_GRIEFING: 'grief',
            ALLOW_PVP: 'pvp', CLAIM_VISIBILITY: 'visibility'
        },
        'dev.ftb.mods.ftbteams.api.property.PrivacyMode': { PRIVATE: 'private', PUBLIC: 'public' },
        'dev.ftb.mods.ftblibrary.icon.Color4I': { fromString: value => value },
        'net.minecraft.resources.ResourceKey': { create: (_registry, loc) => loc },
        'net.minecraft.resources.ResourceLocation': class ResourceLocation {
            constructor(value) { this.value = value }
        },
        'net.minecraft.core.registries.Registries': { DIMENSION: 'dimension' }
    }
    const state = {}
    const guards = {}
    const context = {
        global: state,
        console: logs,
        Date: { now: () => nowMs },
        Java: { loadClass: name => {
            assert.ok(Object.hasOwn(classes, name), 'unexpected Java class ' + name)
            return classes[name]
        } },
        EntityEvents: { checkSpawn(fn) { guards.spawn = fn } },
        LevelEvents: { beforeExplosion(fn) { guards.explosion = fn } },
        BlockEvents: {
            broken(fn) { guards.break = fn },
            placed(fn) { guards.place = fn }
        },
        ServerEvents: { loaded(fn) { callback = fn } }
    }
    vm.runInNewContext(shipping, context, { filename: '04_spawn_hub.js', timeout: 3000 })
    assert.equal(state.alfheimHubClaimReady, false, 'claim must start NOT READY')
    const server = {
        createCommandSourceStack: () => ({}),
        scheduleInTicks(ticks, fn) { assert.equal(ticks, 40); queue.push(fn) }
    }
    assert.ok(callback, 'server-load handler must register')
    callback({ server })
    let retries = 0
    while (queue.length) {
        assert.ok(retries++ < 6, 'bounded retries exceeded')
        queue.shift()({})
    }
    return { state, messages, attempts, unclaims, playerDataCalls, claims, guards,
             advanceTime(ms) { nowMs += ms } }
}

const happy = scenario('healthy')
assert.equal(happy.state.alfheimHubClaimReady, true, 'only complete admin claims may be ready')
assert.equal(happy.attempts, 1)
assert.match(happy.messages.info.join('\n'), /FTB ownership verified/)
assert.equal(happy.unclaims, 0)

// Exercise the actual registered KubeJS protection handlers, not a reimplemented predicate.
// Inclusive rectangle boundaries, other dimensions and operator exemptions matter as much
// as FTB ownership: a READY claim is not proof that edits/spawns/explosions are guarded.
for (const name of ['spawn', 'explosion', 'break', 'place']) {
    assert.equal(typeof happy.guards[name], 'function', name + ' handler not registered')
}
function probe(kind, x, z, options = {}) {
    const dimension = options.dimension ?? dimensionMatch[1]
    const messages = []
    let cancels = 0
    const event = {
        level: { dimension }, x, z, block: { x, z },
        player: options.noPlayer ? null : {
            username: options.username || 'visitor',
            op: !!options.op,
            tell(message) { messages.push(String(message)) }
        },
        entity: {
            level: { dimension }, x, z, living: options.living !== false,
            monster: options.monster !== false,
            type: options.woodElf ? 'richs_races_wood_elves:wood_elf' : 'minecraft:zombie'
        },
        cancel() { cancels++ }
    }
    happy.guards[kind](event)
    return { cancels, messages }
}
const minX = value('HUB_MIN_X')
const maxX = value('HUB_MAX_X')
const minZ = value('HUB_MIN_Z')
const maxZ = value('HUB_MAX_Z')
for (const kind of ['break', 'place']) {
    for (const [x, z] of [[minX, minZ], [maxX, maxZ], [0, 0]]) {
        const denied = probe(kind, x, z, { username: 'boundary_' + kind + '_' + x + '_' + z })
        assert.equal(denied.cancels, 1, kind + ' must reject non-op edit at ' + x + ',' + z)
        assert.match(denied.messages.join(' '), /Royal Elven Guard/)
        assert.equal(probe(kind, x, z, { op: true }).cancels, 0,
            'an operator may repair the protected hub')
        assert.equal(probe(kind, x, z, { noPlayer: true }).cancels, 1,
            'unattributed hub edits must not bypass the guard')
    }
    for (const [x, z] of [[minX - 1, 0], [maxX + 1, 0],
                          [0, minZ - 1], [0, maxZ + 1]]) {
        assert.equal(probe(kind, x, z).cancels, 0, kind + ' must not lock outside the hub')
    }
    assert.equal(probe(kind, 0, 0, { dimension: 'minecraft:overworld' }).cancels, 0,
        'hub protection must not lock Midgard')
}
for (const [x, z] of [[minX, minZ], [maxX, maxZ]]) {
    assert.equal(probe('explosion', x, z).cancels, 1, 'in-hub explosion must be blocked')
    assert.equal(probe('spawn', x, z).cancels, 1, 'in-hub hostile spawn must be blocked')
}
// Repeated breaking/placing must still be cancelled, without flooding the player chat.
const chatFirst = probe('break', 0, 0, { username: 'cooldown_player' })
assert.equal(chatFirst.cancels, 1)
assert.equal(chatFirst.messages.length, 1)
assert.match(chatFirst.messages[0], /Build outside its grounds/)
for (const kind of ['break', 'place']) {
    const repeat = probe(kind, 0, 0, { username: 'cooldown_player' })
    assert.equal(repeat.cancels, 1)
    assert.equal(repeat.messages.length, 0, 'notices share a per-player cooldown across actions')
}
const differentPlayer = probe('break', 0, 0, { username: 'another_player' })
assert.equal(differentPlayer.messages.length, 1, 'other players receive their own guidance')
happy.advanceTime(9999)
assert.equal(probe('place', 0, 0, { username: 'cooldown_player' }).messages.length, 0)
happy.advanceTime(1)
assert.equal(probe('place', 0, 0, { username: 'cooldown_player' }).messages.length, 1)
assert.equal(probe('break', 0, 0, { username: 'cooldown_player', op: true }).cancels, 0)
console.log('SPAWN_HUB_NOTICE_COOLDOWN_PASS: per-player guidance throttled without relaxing protection')

assert.equal(probe('explosion', maxX + 1, 0).cancels, 0)
assert.equal(probe('spawn', minX - 1, 0).cancels, 0)
assert.equal(probe('explosion', 0, 0, { dimension: 'minecraft:overworld' }).cancels, 0)
assert.equal(probe('spawn', 0, 0, { dimension: 'minecraft:overworld' }).cancels, 0)
assert.equal(probe('spawn', 0, 0, { woodElf: true }).cancels, 0,
    'native wood elves are explicitly permitted at the hub')
assert.equal(probe('spawn', 0, 0, { monster: false }).cancels, 0,
    'non-hostile living entities are permitted')
assert.equal(probe('spawn', 0, 0, { living: false }).cancels, 0,
    'nonliving entities are not hostile mobs')
console.log('SPAWN_HUB_GUARD_BOUNDARIES_PASS: registered edit, spawn and explosion handlers')

for (const mode of ['missing', 'nonserver', 'foreign', 'deny']) {
    const result = scenario(mode)
    assert.equal(result.state.alfheimHubClaimReady, false, mode + ' must fail closed')
    assert.equal(result.attempts, 5, mode + ' must exhaust exactly five attempts')
    assert.match(result.messages.error.join('\n'), /HUB CLAIM NOT READY/,
        mode + ' must emit an actionable terminal error')
    assert.equal(result.unclaims, 0, mode + ' must not seize another team claim')
    assert.equal(result.playerDataCalls, 0, mode + ' must never claim for a player team')
    if (mode === 'foreign') assert.equal(result.claims.get(first)?.getId().id, 'foreign')
}
console.log('SPAWN_HUB_CLAIM_READINESS_PASS: healthy ownership + missing admin + name collision + foreign owner + retry exhaustion')
