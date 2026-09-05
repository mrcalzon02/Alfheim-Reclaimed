// Development server only. Installed by run_fey_validation.py, never shipped.
// Runtime acceptance for the generated fey roster: intended habitat tables + construction.
const FeyAuditRegistries = Java.loadClass('net.minecraft.core.registries.Registries')
const FeyAuditForge = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
const FeyAuditCategory = Java.loadClass('net.minecraft.world.entity.MobCategory')

ServerEvents.loaded(event => {
    event.server.scheduleInTicks(100, callback => {
        const server = event.server
        const level = server.getLevel('mythicbotany:alfheim')
        if (!level) throw new Error('Alfheim level is not loaded')
        const registry = level.registryAccess().registryOrThrow(FeyAuditRegistries.BIOME)
        const roster = JSON.parse(String(JsonIO.readJson('kubejs/fey_roster.json')))

        // The static checker proves the biome modifiers match the roster. This runtime probe
        // proves Forge actually applied those modifiers to the final biome mob tables.
        let expectedHabitats = 0
        let habitatMissing = 0
        roster.forEach(r => {
            r.biomes.forEach(id => {
                expectedHabitats++
                const biome = registry.get(new ResourceLocation(id))
                if (!biome) {
                    habitatMissing++
                    console.error('[FEY AUDIT] Unknown habitat ' + id + ' for ' + r.id)
                    return
                }
                const found = []
                FeyAuditCategory.values().forEach(category => {
                    biome.getMobSettings().getMobs(category).unwrap().forEach(s => {
                        found.push(String(FeyAuditForge.ENTITY_TYPES.getKey(s.type)))
                    })
                })
                if (!found.includes(r.id)) {
                    habitatMissing++
                    console.error('[FEY AUDIT] Missing ' + r.id + ' from final mob table for ' + id)
                }
            })
        })
        console.info('[FEY AUDIT] Habitat coverage: species=' + roster.length +
            ' placements=' + expectedHabitats + ' missing=' + habitatMissing)

        // Registration is not proven by source text. Instantiate every registered type and verify
        // the dimensions and max health that EntityJS was instructed to register.
        let created = 0
        let creatureMismatches = 0
        roster.forEach((r, i) => {
            const e = level.createEntity(r.id)
            if (!e) {
                creatureMismatches++
                console.error('[FEY AUDIT] Failed to instantiate ' + r.id)
                return
            }
            e.setPosition(256 + (i % 6) * 4, 200, 256 + Math.floor(i / 6) * 4)
            e.mergeNbt({NoAI: true, Invulnerable: true, PersistenceRequired: true, Tags: ['fey_validation']})
            e.spawn()
            created++

            const health = Number(e.maxHealth)
            const width = Number(e.bbWidth)
            const height = Number(e.bbHeight)
            const badHealth = Math.abs(health - Number(r.health)) > 0.01
            const badWidth = Math.abs(width - Number(r.width)) > 0.01
            const badHeight = Math.abs(height - Number(r.height)) > 0.01
            if (badHealth || badWidth || badHeight) {
                creatureMismatches++
                console.error('[FEY AUDIT] Attribute mismatch ' + r.id +
                    ' health=' + health + '/' + r.health +
                    ' width=' + width + '/' + r.width +
                    ' height=' + height + '/' + r.height)
            }
            console.info('[FEY AUDIT] Created ' + r.id + ' health=' + health +
                ' width=' + width + ' height=' + height)
        })
        console.info('[FEY AUDIT] Creature construction: created=' + created +
            ' expected=' + roster.length + ' mismatches=' + creatureMismatches)
        console.info('[FEY AUDIT] COMPLETE habitat_missing=' + habitatMissing +
            ' creature_mismatches=' + creatureMismatches)
    })
})
