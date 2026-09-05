// Development server only. Installed by run_fey_validation.py, never shipped.
const FeyAuditRegistries = Java.loadClass('net.minecraft.core.registries.Registries')
const FeyAuditForge = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
const FeyAuditCategory = Java.loadClass('net.minecraft.world.entity.MobCategory')
const FeyAuditSpawns = Java.loadClass('net.minecraft.world.entity.SpawnPlacements')
const FeyAuditReason = Java.loadClass('net.minecraft.world.entity.MobSpawnType')
const FeyAuditPos = Java.loadClass('net.minecraft.core.BlockPos')
const FeyAuditRandom = Java.loadClass('net.minecraft.util.RandomSource')

ServerEvents.loaded(event => {
    event.server.scheduleInTicks(100, callback => {
        const server = event.server
        const level = server.getLevel('mythicbotany:alfheim')
        const registry = level.registryAccess().registryOrThrow(FeyAuditRegistries.BIOME)
        const manifest = JSON.parse(String(JsonIO.readJson('kubejs/zombie_habitat_manifest.json')))
        const ids = manifest.natural.map(r => r.type).concat(manifest.variants)
            .concat(['minecraft:zombie','minecraft:husk','minecraft:drowned','minecraft:zombie_villager'])
        let missing = 0
        manifest.biomes.forEach(id => {
            const biome = registry.get(new ResourceLocation(id))
            if (!biome) throw new Error('Unknown biome ' + id)
            const found = []
            FeyAuditCategory.values().forEach(category => {
                biome.getMobSettings().getMobs(category).unwrap().forEach(s => found.push(String(FeyAuditForge.ENTITY_TYPES.getKey(s.type))))
            })
            ids.forEach(type => {
                if (!found.includes(type)) {
                    missing++
                    console.error('[FEY AUDIT] Missing ' + type + ' in ' + id)
                }
            })
        })
        console.info('[FEY AUDIT] Zombie coverage: ' + manifest.biomes.length + ' biomes; ' + ids.length + ' entries; missing=' + missing)
        const roster = JSON.parse(String(JsonIO.readJson('kubejs/fey_roster.json')))
        roster.forEach((r,i) => {
            const e = level.createEntity(r.id)
            if (!e) throw new Error('Failed to instantiate ' + r.id)
            e.setPosition(256 + (i%6)*4, 200, 256 + Math.floor(i/6)*4)
            e.mergeNbt({NoAI: true, Invulnerable: true, PersistenceRequired: true, Tags:['fey_validation']})
            e.spawn()
            if (Math.abs(e.maxHealth-r.health)>0.01) throw new Error('Health mismatch '+r.id+' '+e.maxHealth)
            console.info('[FEY AUDIT] Created ' + r.id + ' health=' + e.maxHealth + ' width=' + e.bbWidth + ' height=' + e.bbHeight)
        })
        console.info('[FEY AUDIT] COMPLETE creature construction and final biome tables')
    })
})
