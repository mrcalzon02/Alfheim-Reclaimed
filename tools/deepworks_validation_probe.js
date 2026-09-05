// Development world only; installed by run_deepworks_validation.py.
const DeepForge = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
const DeepPos = Java.loadClass('net.minecraft.core.BlockPos')
const DeepVec = Java.loadClass('net.minecraft.world.phys.Vec3')
const DeepLoot = Java.loadClass('net.minecraft.world.level.storage.loot.LootParams$Builder')
const DeepKeys = Java.loadClass('net.minecraft.world.level.storage.loot.parameters.LootContextParams')
const DeepSets = Java.loadClass('net.minecraft.world.level.storage.loot.parameters.LootContextParamSets')
const DeepProps = Java.loadClass('net.minecraft.world.level.block.state.properties.BlockStateProperties')
const DeepSlab = Java.loadClass('net.minecraft.world.level.block.state.properties.SlabType')

ServerEvents.loaded(event => {
  event.server.scheduleInTicks(100, callback => {
    const server = event.server
    const level = server.getLevel('mythicbotany:alfheim')
    const catalog = JSON.parse(String(JsonIO.readJson('kubejs/deepworks_catalog.json')))
    let errors = 0, lootChecks = 0, placed = 0
    function check(ok, message) {
      if (!ok) { errors++; console.error('[DEEP AUDIT] ' + message) }
    }
    const pick = Item.of('minecraft:diamond_pickaxe')
    const silk = Item.of('minecraft:diamond_pickaxe', '{Enchantments:[{id:"minecraft:silk_touch",lvl:1s}]}')
    catalog.blocks.forEach((row, index) => {
      const key = new ResourceLocation(row.id)
      check(DeepForge.BLOCKS.containsKey(key) && DeepForge.ITEMS.containsKey(key), 'Missing block/item '+row.id)
      const block = DeepForge.BLOCKS.getValue(key)
      const state = block.defaultBlockState()
      check(Number(state.getLightEmission()) === row.light, 'Light mismatch '+row.id)
      check(state.requiresCorrectToolForDrops(), 'Tool requirement missing '+row.id)
      const pos = new DeepPos((index % 14)*3, 160, Math.floor(index/14)*3)
      level.setBlock(pos, state, 3)
      check(level.getBlockState(pos).getBlock() === block, 'Placement failed '+row.id)
      placed++
      if (row.form === 'stairs') check(state.hasProperty(DeepProps.STAIRS_SHAPE), 'Stair state missing '+row.id)
      if (row.form === 'wall') check(state.hasProperty(DeepProps.EAST_WALL), 'Wall state missing '+row.id)
      function lootTest(testState, tool, expected) {
        const params = new DeepLoot(level).withParameter(DeepKeys.BLOCK_STATE, testState)
          .withParameter(DeepKeys.ORIGIN, new DeepVec(pos.getX(), pos.getY(), pos.getZ()))
          .withParameter(DeepKeys.TOOL, tool).create(DeepSets.BLOCK)
        const table = server.getLootData().getLootTable(block.getLootTable())
        let count = 0
        table.getRandomItems(params).forEach(stack => {
          check(String(stack.id) === row.id, 'Unexpected block drop '+row.id+' -> '+stack.id)
          count += Number(stack.count)
        })
        check(count === expected, 'Drop count '+row.id+' expected='+expected+' got='+count)
        lootChecks++
      }
      lootTest(state, pick, row.glass || row.slag ? 0 : 1)
      lootTest(state, silk, row.slag ? 0 : 1)
      if (row.form === 'slab') {
        check(state.hasProperty(DeepProps.SLAB_TYPE), 'Slab state missing '+row.id)
        lootTest(state.setValue(DeepProps.SLAB_TYPE, DeepSlab.DOUBLE), pick, 2)
      }
    })
    catalog.recipes.forEach(row => {
      const found = server.getRecipeManager().byKey(new ResourceLocation(row.id))
      check(found.isPresent(), 'Missing recipe '+row.id)
      if (found.isPresent()) {
        const recipe = found.get()
        const result = recipe.getResultItem(level.registryAccess())
        check(String(result.id) === row.output && Number(result.count) === row.count, 'Recipe output '+row.id)
        check(recipe.getIngredients().get(0).test(Item.of(row.input)), 'Recipe input '+row.id)
      }
    })
    console.info('[DEEP AUDIT] COMPLETE blocks='+placed+' recipes='+catalog.recipes.length+' loot='+lootChecks+' errors='+errors)
  })
})
