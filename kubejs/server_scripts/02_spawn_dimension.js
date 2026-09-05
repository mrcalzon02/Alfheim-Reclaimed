// Alfheim Reclaimed — the player wakes in Alfheim, not in the Overworld
//
// Alfheim is `mythicbotany:alfheim`, the dimension MythicBotany ships. The Overworld is Midgard,
// the dead industrial world the player is not supposed to see until the gate opens in Era VI.
// Vanilla has no notion of a spawn dimension: every player joins and respawns in the Overworld,
// and no datapack can change that. No dimension-management mod is installed, so this is the
// piece of the architecture that has to be script.
//
// ---------------------------------------------------------------------------------------------
// B-44 — WHY THIS WAS REWRITTEN. Read before changing it back.
//
// The first version ran:
//
//     execute in mythicbotany:alfheim run spreadplayers 0 0 1 2000 false <name>
//
// and it never moved anybody. `execute in <dim>` sets the *execution* dimension, so spreadplayers
// sampled ALFHEIM's terrain to choose a landing spot — which is why Alfheim generated exactly one
// region — and then placed the player at those coordinates in the dimension they were already in.
// The save told the story precisely: the player stood at Midgard (189, 64, -1319) while the only
// Alfheim region ever generated was r.0.-3, the region containing (189, -1319).
//
// It then ran `spawnpoint @s ~ ~ ~` and wrote SpawnForced=1 on **Midgard**, and set a persistent
// flag saying the job was done — so it never tried again. Three compounding faults:
//
//   1. the wrong command for the job;
//   2. recording success without observing it;
//   3. latching a flag on an unverified outcome, which turned a transient failure into a permanent
//      one.
//
// This version fixes all three. `execute in <dim> run tp` is the idiom that actually changes a
// player's dimension. Nothing is recorded until the game has been asked where the player is, and
// the flag is only latched once the answer is Alfheim.
// ---------------------------------------------------------------------------------------------
//
// See alfheim_reclaimed_design/WORLD_STRUCTURE.md §1 and §7, and BACKLOG B-44.

const HOME_DIMENSION = 'mythicbotany:alfheim'

// v2 deliberately. v1 means "we issued the commands"; v2 means "we watched the player arrive".
// Bumping it re-sends every character that v1 stranded in Midgard, so the fix is self-healing and
// needs no manual repair commands.
const SPAWN_FLAG = 'alfheim_home_spawn_v2'

// Set once Era VI opens the gate; after that Midgard is a legitimate place to come back to and
// this script stops interfering. Nothing sets it yet — that lands with B-36.
const MIDGARD_FLAG = 'alfheim_midgard_unlocked'

const LANDING_RANGE = 2000   // max blocks from (0,0) that spreadplayers may drop them
const VERIFY_DELAY = 20      // ticks to let the dimension change settle before asking

// `@e` is scoped to the execution dimension, so this is a dimension test written entirely in
// vanilla commands — no KubeJS level/dimension accessor, whose shape has moved between builds and
// whose failure mode last time was to silently skip the check.
function isHome(server, name) {
    try {
        return server.runCommandSilent(
            `execute in ${HOME_DIMENSION} if entity @e[type=minecraft:player,name=${name},limit=1]`
        ) > 0
    } catch (e) {
        console.warn(`[Alfheim Reclaimed] could not test ${name}'s dimension: ${e}`)
        return false
    }
}

// Move them, then place them. The teleport is what crosses the dimension boundary; spreadplayers
// then picks a non-liquid, non-fire surface spot — which it can now do correctly, because the
// player is already in the dimension whose terrain it is sampling.
// REWRITTEN 2026-09-04. The old body teleported to (0,320,0) and then spreadplayers-ed the
// player up to LANDING_RANGE blocks away, which meant every player landed somewhere different
// and nobody landed at the hub. The user's requirement is the opposite: a pre-made spawn that
// operators create before anyone joins, and that every player arrives at.
//
// The anchor is a marker entity placed by alfheim:hub/create, which #minecraft:load runs on
// world load with NO PLAYER PRESENT. This function is now only the delivery half -- vanilla has
// no cross-dimension world spawn, so something must still move a joining player across, but it
// moves them to a fixed known place instead of scattering them.
//
// Falls back to the old behaviour only if the anchor is genuinely missing, so a world that
// somehow has no hub still puts the player in Alfheim rather than leaving them in Midgard.
// REWRITTEN AGAIN 2026-09-04, after a live session left the player in Midgard for the whole
// session. Two faults, and the second is the one that made the first invisible:
//
//   1. The old body ran `hub/send` and returned early `if (placed > 0)`. `/function` reports
//      the number of commands it executed, NOT whether any of them did anything -- so a
//      hub/send whose every line was `at @e[...marker...]` with no marker in the world still
//      came back non-zero. The fallback never fired and the player never left Midgard.
//
//   2. It logged NOTHING on the success path. The session log therefore contained no evidence
//      either way, which is the same "recorded success without observing it" fault B-44 was
//      about. Every path here now logs.
//
// hub/send is now self-sufficient: it crosses into Alfheim unconditionally and only then
// refines onto the anchor, so this function no longer has a fallback to choose between. Its
// job is to invoke it and say what happened.
function sendHome(server, name) {
    try {
        server.runCommandSilent(`execute as ${name} at @s run function alfheim:hub/send`)
    } catch (e) {
        console.warn(`[Alfheim Reclaimed] hub/send threw for ${name}: ${e} -- falling back to ` +
                     'a direct teleport so they at least reach Alfheim.')
        server.runCommandSilent(`execute in ${HOME_DIMENSION} run tp ${name} 0 320 0`)
        server.runCommandSilent(
            `execute in ${HOME_DIMENSION} run spreadplayers 0 0 1 ${LANDING_RANGE} false ${name}`)
    }
    // Observed, not assumed. isHome() asks the game rather than trusting a command's return.
    console.info(`[Alfheim Reclaimed] hub/send run for ${name}; in ${HOME_DIMENSION} now: ` +
                 isHome(server, name))
}

// Ask the game where they ended up, and only then write anything down.
//
// The player object is passed in rather than looked up. `server.getPlayer(name)` has no precedent
// in this pack, and if it returned null the flag would never latch — which would re-spread the
// player across Alfheim on every single login. Every API touched here except the scheduler is one
// the previous version already proved works on this KubeJS build.
function confirmAndAnchor(server, player, why) {
    const name = player.username
    if (!isHome(server, name)) {
        console.warn(
            `[Alfheim Reclaimed] ${name} did NOT arrive in ${HOME_DIMENSION} (${why}). ` +
            'Nothing recorded, no spawnpoint set, flag left clear — it will try again on next ' +
            'login. If this repeats, the teleport itself is failing; check for a dimension or ' +
            'teleport-blocking mod before trusting any other spawn evidence.')
        return false
    }

    // Only now is it safe to anchor respawn here. /spawnpoint writes the respawn DIMENSION as
    // well as the position, so dying bedless returns them to Alfheim. A bed overrides it normally.
    server.runCommandSilent(`execute as ${name} at @s run spawnpoint @s ~ ~ ~`)
    player.persistentData.putBoolean(SPAWN_FLAG, true)

    console.info(`[Alfheim Reclaimed] ${name} confirmed in ${HOME_DIMENSION} (${why}); ` +
                 'spawnpoint anchored there.')
    return true
}

// Verification has to happen after the dimension change has settled, not in the same tick. If the
// scheduler is unavailable on this KubeJS build, fall back to checking immediately — a slightly
// flakier check is still better than the old behaviour of not checking at all.
function verifyLater(server, player, why) {
    // IMMEDIATE check first, always. In the 2026-09-04 session the scheduled callback produced
    // no log line at all -- neither "confirmed" nor "did NOT arrive" -- so whatever happened to
    // it, the delayed path cannot be the only thing that reports. This one costs a command and
    // guarantees the log says something.
    if (confirmAndAnchor(server, player, why + ', immediate')) return

    // Then the delayed one, which is the authoritative check: a dimension change can take a
    // tick or two to settle, and an immediate false is not proof of failure.
    try {
        server.scheduleInTicks(VERIFY_DELAY, () => confirmAndAnchor(server, player, why))
    } catch (e) {
        console.warn('[Alfheim Reclaimed] scheduleInTicks unavailable: ' + e +
                     ' -- the immediate check above is all the verification there is.')
    }
}

PlayerEvents.loggedIn(event => {
    const player = event.player

    // COLLECT A PLAYER WHO IS STILL OWED THE HUB, before anything else and regardless of the
    // spawn flag. hub/send tags anyone it had to place provisionally because the Greatbole had
    // not finished generating; hub/anchor collects them when it resolves -- but only the ones
    // who are ONLINE at that moment. Someone who logged out while tagged would otherwise keep
    // the tag forever and never be moved to the tree.
    //
    // hub/send is idempotent for this: with an anchor it moves them and clears the tag, without
    // one it re-tags them. So running it on every login of a tagged player is safe and is the
    // whole repair.
    try {
        event.server.runCommandSilent(
            `execute as ${player.username} at @s if entity @s[tag=alfheim_awaiting_hub] ` +
            'run function alfheim:hub/send')
    } catch (e) {
        console.warn('[Alfheim Reclaimed] awaiting-hub collection failed: ' + e)
    }

    if (player.persistentData.getBoolean(SPAWN_FLAG)) return
    if (player.persistentData.getBoolean(MIDGARD_FLAG)) return

    // The flag is NOT set here. It is set in confirmAndAnchor, and only on success.
    sendHome(event.server, player.username)
    verifyLater(event.server, player, 'first join')
})

// Respawn safety net. /spawnpoint should already cover it, but if the recorded spawn is obstructed
// or cleared, vanilla silently falls back to the Overworld world spawn — which is Midgard, and
// before Era VI that is a soft failure the player cannot read as intentional.
PlayerEvents.respawned(event => {
    const player = event.player
    if (player.persistentData.getBoolean(MIDGARD_FLAG)) return

    const name = player.username

    // Give the respawn a moment to land, then correct it only if they are genuinely not home.
    // A bed in Alfheim, or the anchored spawnpoint, should mean this never fires.
    const guard = () => {
        if (isHome(event.server, name)) return
        console.info(`[Alfheim Reclaimed] ${name} respawned outside ${HOME_DIMENSION}; ` +
                     'returning them before the gate is open.')
        sendHome(event.server, name)
        verifyLater(event.server, player, 'respawned in Midgard before the gate')
    }

    try {
        event.server.scheduleInTicks(VERIFY_DELAY, guard)
    } catch (e) {
        console.warn('[Alfheim Reclaimed] respawn guard could not schedule, checking now: ' + e)
        guard()
    }
})

console.info('[Alfheim Reclaimed] spawn dimension handler loaded - home is ' + HOME_DIMENSION +
             ' (v2: verifies arrival before recording anything)')
