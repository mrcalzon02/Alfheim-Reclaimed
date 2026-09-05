// Custom fauna AI. Court elves have separate IDs and their reserved skins stay untouched.
const FeyPlayer = Java.loadClass('net.minecraft.world.entity.player.Player')
global.ALFHEIM_FEY.forEach(r => {
    EntityJSEvents.addGoalSelectors(r.id, goals => {
        if (r.family === 'sea') {
            goals.meleeAttack(1, 1.1, false)
            goals.randomSwimming(4, 0.8, 40)
        } else {
            goals.floatSwim(0)
            if (r.family === 'elf') goals.meleeAttack(1, 1.1, false)
            else {
                goals.panic(1, 1.4)
                if (r.family === 'deer') goals.avoidEntity(2, FeyPlayer, e => true, 7, 1, 1.4, e => true)
            }
            goals.randomStroll(5, 0.8, 80, false)
            goals.randomLookAround(6)
        }
    })
    if (r.family === 'elf' || r.family === 'sea') {
        EntityJSEvents.addGoals(r.id, goals => {
            goals.nearestAttackableTarget(1, FeyPlayer, 10, true, false,
                p => !p.isCreative() && !p.isSpectator() && (r.family !== 'sea' || p.isInWater()))
        })
    }
})
console.info('[Alfheim Fey] AI registered for ' + global.ALFHEIM_FEY.length + ' creatures')
