// Development server only. Installed by run_fey_validation.py, never shipped.
// Runtime acceptance for the generated fey roster: intended habitat tables + construction.
const FeyAuditRegistries = Java.loadClass('net.minecraft.core.registries.Registries')
const FeyAuditForge = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
const FeyAuditCategory = Java.loadClass('net.minecraft.world.entity.MobCategory')
const FeyMobSettings = Java.loadClass('net.minecraft.world.level.biome.MobSpawnSettings')
const FeyJsonOps = Java.loadClass('com.mojang.serialization.JsonOps')
const FeyLootParams = Java.loadClass('net.minecraft.world.level.storage.loot.LootParams$Builder')
const FeyLootKeys = Java.loadClass('net.minecraft.world.level.storage.loot.parameters.LootContextParams')
const FeyLootSets = Java.loadClass('net.minecraft.world.level.storage.loot.parameters.LootContextParamSets')
const FeyFakePlayers = Java.loadClass('net.minecraftforge.common.util.FakePlayerFactory')

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
                // Serialize final loaded settings with Mojang's codec: categories and entries
                // are explicit, and the output can be compared directly with the manifest.
                const encoded = FeyMobSettings.CODEC.codec().encodeStart(FeyJsonOps.INSTANCE, biome.getMobSettings()).result().get()
                const settings = JSON.parse(String(encoded))
                Object.keys(settings.spawners).forEach(key => settings.spawners[key].forEach(s => found.push(s.type)))
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
        let dropErrors = 0
        const additionalDrops = {}
        const dropManifest = JSON.parse(String(JsonIO.readJson('kubejs/fey_drops_manifest.json')))
        const fakePlayer = FeyFakePlayers.getMinecraft(level)
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
            // Evaluate the real loaded entity loot table, including player-kill conditions.
            const rows = dropManifest.creatures[r.id]
            const expected = rows.map(row => row[0].includes(':') ? row[0] : 'alfheim:' + row[0])
            const seen = []
            const table = server.getLootData().getLootTable(e.getLootTable())
            for (let playerKill = 0; playerKill <= 1; playerKill++) {
                let lootBuilder = new FeyLootParams(level)
                    .withParameter(FeyLootKeys.THIS_ENTITY, e)
                    .withParameter(FeyLootKeys.ORIGIN, e.position())
                    .withParameter(FeyLootKeys.DAMAGE_SOURCE, level.damageSources().generic())
                if (playerKill) lootBuilder.withParameter(FeyLootKeys.LAST_DAMAGE_PLAYER, fakePlayer)
                let lootParameters = lootBuilder.create(FeyLootSets.ENTITY)
                for (let roll = 0; roll < 128; roll++) {
                    table.getRandomItems(lootParameters).forEach(stack => {
                        const id = String(stack.id)
                        const index = expected.indexOf(id)
                        // Forge applies other mods' global loot modifiers here (Knightlib
                        // essence, for example). Record those independently; keep them intact.
                        if (index < 0) { additionalDrops[id] = true; return }
                        if ((!playerKill && rows[index][4]) ||
                            stack.count < rows[index][1] || stack.count > rows[index][2]) {
                            dropErrors++
                            console.error('[FEY AUDIT] Bad loot ' + r.id + ' -> ' + id + ' x' + stack.count)
                        }
                        if (playerKill && !seen.includes(id)) seen.push(id)
                    })
                }
            }
            expected.forEach(id => {
                if (!seen.includes(id)) {
                    dropErrors++
                    console.error('[FEY AUDIT] Loot never produced: ' + r.id + ' -> ' + id)
                }
            })
        })
        console.info('[FEY AUDIT] Creature construction: created=' + created +
            ' expected=' + roster.length + ' mismatches=' + creatureMismatches)
        Object.keys(dropManifest.items).forEach(name => {
            if (!FeyAuditForge.ITEMS.containsKey(new ResourceLocation('alfheim:' + name))) dropErrors++
        })
        const recipeIds = Object.keys(dropManifest.recipes).map(name => 'alfheim:fey/' + name)
            .concat(['smelting','smoking','campfire_cooking'].map(method => 'alfheim:fey/venison_' + method))
        recipeIds.forEach(id => {
            if (!server.getRecipeManager().byKey(new ResourceLocation(id)).isPresent()) {
                dropErrors++
                console.error('[FEY AUDIT] Missing recipe ' + id)
            }
        })
        console.info('[FEY AUDIT] Drops: items=' + Object.keys(dropManifest.items).length +
            ' recipes=' + recipeIds.length + ' errors=' + dropErrors)
        console.info('[FEY AUDIT] Preserved global drops: ' + Object.keys(additionalDrops).join(','))
        console.info('[FEY AUDIT] COMPLETE habitat_missing=' + habitatMissing +
            ' creature_mismatches=' + creatureMismatches)
    })
})
