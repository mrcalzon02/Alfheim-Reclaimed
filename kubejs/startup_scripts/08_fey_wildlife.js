// EntityJS 0.7.3 / Forge 1.20.1. Restart the client after changing registrations.
// Models, atlas, habitats and roster: tools/gen_fey_wildlife.py.
global.ALFHEIM_FEY = JSON.parse(String(JsonIO.readJson('kubejs/fey_roster.json')))
const FeyMonster = Java.loadClass('net.minecraft.world.entity.monster.Monster')
const FeyFluidRegistry = Java.loadClass('net.minecraftforge.registries.ForgeRegistries').FLUIDS
const FeySwimControl = Java.loadClass('net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl')

function feyOutsideHub(level, pos) {
    return String(level.getLevel().dimension) !== 'mythicbotany:alfheim' ||
        Math.abs(pos.x) > 192 || Math.abs(pos.z) > 192
}

// Do not call FluidState.is(TagKey) from Rhino here. On this Forge/KubeJS mapping both
// FluidState.is(Fluid) and FluidState.is(TagKey<Fluid>) are exposed under the same JavaScript
// method name, and Rhino cannot disambiguate them at natural-spawn time. That fault crashed the
// integrated server on the first aquatic spawn check. Resolve the registry key instead; this
// preserves the vanilla WATER tag's two members without touching the overloaded method.
function feyIsWater(level, pos) {
    const key = FeyFluidRegistry.getKey(level.getFluidState(pos).getType())
    if (key === null) return false
    const id = String(key)
    return id === 'minecraft:water' || id === 'minecraft:flowing_water'
}

StartupEvents.registry('entity_type', event => {
    global.ALFHEIM_FEY.forEach(r => {
        const name = String(r.id).split(':')[1]
        const water = r.family === 'sea'
        const hostile = r.family === 'elf' || water
        const b = event.create(r.id, water ? 'entityjs:watercreature' :
            r.family === 'elf' ? 'entityjs:mob' : 'entityjs:animal')
            .sized(r.width, r.height)
            .mobCategory(water ? 'water_creature' : hostile ? 'monster' : 'creature')
            .modelResource(e => 'alfheim:geo/entity/' + name + '.geo.json')
            .textureResource(e => 'alfheim:textures/entity/fey_materials.png')
            .animationResource(e => 'alfheim:animations/entity/' + name + '.animation.json')
            .attributes(a => {
                a.add('minecraft:generic.max_health', r.health)
                a.add('minecraft:generic.movement_speed', r.speed)
                a.add('minecraft:generic.follow_range', hostile ? 20 : 12)
                a.add('minecraft:generic.attack_damage', r.damage)
            })
            .addAnimationController('movement', 4, state => {
                state.thenLoop(state.isMoving() ? 'move' : 'idle')
                return true
            })
            .scaleModelForRender(ctx => {
                if (r.family === 'toad') ctx.poseStack.scale(r.width / 0.875, r.height / 0.5625, 1.1)
                else ctx.poseStack.scale(r.scale, r.scale, r.scale)
            })
            .spawnPlacement(water ? 'in_water' : 'on_ground', 'motion_blocking_no_leaves',
                (type, level, reason, pos, random) => {
                    if (water) return feyOutsideHub(level, pos) &&
                        String(level.getDifficulty()) !== 'PEACEFUL' &&
                        feyIsWater(level, pos) &&
                        feyIsWater(level, pos.above()) &&
                        feyIsWater(level, pos.below())
                    if (hostile) return feyOutsideHub(level, pos) &&
                        FeyMonster.checkMonsterSpawnRules(type, level, reason, pos, random)
                    if (r.celestial && random.nextInt(32) !== 0) return false
                    return level.getRawBrightness(pos, 0) > 8 &&
                        level.getBlockState(pos.below()).isSolid() &&
                        level.getFluidState(pos).isEmpty()
                })
        if (r.celestial) {
            // This callback runs in the client renderer only; no client class loads on server.
            b.renderType(e => Java.loadClass('net.minecraft.client.renderer.RenderType').endPortal())
        }
        if (hostile) b.shouldDespawnInPeaceful(true).removeWhenFarAway(ctx => true)
        else b.canBreed(e => false) // Wild populations; no accidental same-sex breeding or familiar AI.
        if (water) {
            b.setDefaultGoals(false)
                .createNavigation(ctx => EntityJSUtils.createWaterBoundPathNavigation(ctx.entity, ctx.level))
                .setMoveControl(e => new FeySwimControl(e, 85, 10, 0.1, 0.5, false))
                .setAmbientSound('minecraft:entity.squid.ambient')
                .setHurtSound(ctx => 'minecraft:entity.squid.hurt')
                .setDeathSound('minecraft:entity.squid.death')
        } else if (r.family === 'frog' || r.family === 'toad') {
            b.canBreatheUnderwater(true)
                .createNavigation(ctx => EntityJSUtils.createAmphibiousPathNavigation(ctx.entity, ctx.level))
                .setAmbientSound('minecraft:entity.frog.ambient')
                .setHurtSound(ctx => 'minecraft:entity.frog.hurt')
                .setDeathSound('minecraft:entity.frog.death')
                .tick(e => {
                    if (!e.level.isClientSide() && e.onGround() && !e.navigation.isDone() && e.tickCount % 20 === 0) {
                        const motion = e.deltaMovement
                        e.setDeltaMovement(motion.x, 0.24, motion.z)
                    }
                })
        } else if (r.family === 'deer') {
            b.setHurtSound(ctx => 'minecraft:entity.goat.hurt').setDeathSound('minecraft:entity.goat.death')
        }
    })
})
