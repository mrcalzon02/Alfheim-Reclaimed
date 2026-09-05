// Spawn placements for zombie mods that register none of their own.
//
// Infectious is deliberately NOT handled here — see B-76. Its entities register their placements
// in FMLCommonSetupEvent, which runs *after* SpawnPlacementRegisterEvent, so at this point they
// have no entry to extend: `or`/`and` throw (nonnull placement type required) and `replace` would
// collide with the mod's own later SpawnPlacements.register (duplicate registration). Infectious
// reaches Midgard through the biome modifiers alone, which is all its Overworld-gated spawn
// condition will accept anyway. `kubejs/zombie_spawn_gates.json` is retained as generator
// evidence and is currently unconsumed.
const ZombieMonster = Java.loadClass('net.minecraft.world.entity.monster.Monster')

EntityJSEvents.spawnPlacement(event => {
    // The conversion mod ships no placements at all; it gates spawning with a checkSpawnRules
    // mixin instead. These entries are genuinely new, so `replace` is the correct operation.
    const variants = ['badlands','bamboo','cave','cherry','deep_dark','desert','dripstone',
        'frozen','jungle','lush','mangrove','pale_garden','savanna','swamp','mushroom']
    variants.forEach(name => event.replace('zombie_variants:' + name + '_zombie',
        'on_ground', 'motion_blocking_no_leaves',
        (type, level, reason, pos, random) => ZombieMonster.checkMonsterSpawnRules(type, level, reason, pos, random)))
})
