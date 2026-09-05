// Development-only fresh-world audit. Chunk requests are issued outside Rhino.
var VoidContext=Java.loadClass('net.minecraft.world.level.levelgen.DensityFunction$SinglePointContext')
var VoidPos=Java.loadClass('net.minecraft.core.BlockPos')
var VoidForge=Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
ServerEvents.loaded(event => {
  var server=event.server
  server.scheduleInTicks(40, callback => {
    var level=server.getLevel('mythicbotany:alfheim'), state=level.getChunkSource().randomState(), router=state.router()
    function value(df,x,y,z) {return Number(df.compute(new VoidContext(x,y,z)))}
    function kind(c,t,h) {
      if(c < -0.94) return 'empty'
      if(c < -0.925) return 'starless_reach'
      if(c < -0.86) return t<0 ? (h<0?'shatterfields':'prism_drift') : (h<0?'rootfall':'sepulchral_reach')
      if(c < -0.80) return 'void_verge'
      return 'land'
    }
    var found={},sites=[],names=['void_verge','shatterfields','prism_drift','rootfall','sepulchral_reach','starless_reach','empty']
    for(var radius=2048;radius<=16384 && sites.length<7;radius*=2) {
      for(var x=-radius;x<=radius;x+=64) for(var z=-radius;z<=radius;z+=64) {
        var c=value(router.continents(),x,64,z)
        if(c>=-0.805) continue
        var k=kind(c,value(router.temperature(),x,64,z),value(router.vegetation(),x,64,z))
        if(found[k] || k==='land') continue
        // Stay well inside each band for material/fluid checks; separate crossing
        // transects below measure the transition itself.
        if(k==='void_verge' && (c<-.85 || c>-.815)) continue
        if(k==='empty' && c>-.975) continue
        if(k==='starless_reach' && (c<-.938 || c>-.927)) continue
        if(k!=='void_verge' && k!=='empty' && k!=='starless_reach' && (c<-.915 || c>-.88)) continue
        if(k!=='empty' && k!=='void_verge' && value(router.finalDensity(),x,64,z)<=0) continue
        found[k]=true;sites.push({x:x,z:z,kind:k,continentalness:c})
      }
    }
    if(sites.length!==7) throw new Error('Missing Void sites: '+JSON.stringify(sites))
    // Known Deep cavern centers from the previous accepted density experiment.
    var prior=JSON.parse(String(JsonIO.readJson('kubejs/void_prior_deep.json')))
    prior.centers.forEach(p=>sites.push({x:p.x,z:p.z,kind:'deep'}))
    console.info('[VOID AUDIT] SITES '+JSON.stringify(sites))
    var report={sites:sites,columns:[],counts:{},biomes:{},errors:[],materialBlocks:0,materialRecipes:0},site=0,offset=-16
    var catalog=JSON.parse(String(JsonIO.readJson('kubejs/void_stones_catalog.json')))
    catalog.blocks.forEach(row=>{
      var key=new ResourceLocation(row.id),block=VoidForge.BLOCKS.getValue(key)
      if(!VoidForge.BLOCKS.containsKey(key) || !VoidForge.ITEMS.containsKey(key)) report.errors.push('Missing '+row.id)
      if(Number(block.defaultBlockState().getLightEmission())!==row.light) report.errors.push('Light '+row.id)
      if(!block.defaultBlockState().requiresCorrectToolForDrops()) report.errors.push('Tool '+row.id)
      report.materialBlocks++
    })
    catalog.recipes.forEach(row=>{
      var recipe=server.getRecipeManager().byKey(new ResourceLocation(row.id))
      if(!recipe.isPresent()) report.errors.push('Recipe '+row.id)
      else {
        var result=recipe.get().getResultItem(level.registryAccess())
        if(String(result.id)!==row.output || Number(result.count)!==row.count || !recipe.get().getIngredients().get(0).test(Item.of(row.input))) report.errors.push('Recipe result '+row.id)
      }
      report.materialRecipes++
    })
    function tick() {
      var p=sites[site],x=p.x+offset,z=p.z
      if(level.getChunkSource().getChunkNow(Math.floor(x/16),Math.floor(z/16))===null) {server.scheduleInTicks(20,tick);return}
      var c=value(router.continents(),x,64,z),blocks={},runs=[],last='',count=0,solid=0,fluids=0
      var biome=String(level.getBiome(new VoidPos(x,64,z)).unwrapKey().get().location())
      report.biomes[biome]=(report.biomes[biome]||0)+1
      for(var y=-64;y<320;y++) {
        var bs=level.getBlockState(new VoidPos(x,y,z)),id=String(VoidForge.BLOCKS.getKey(bs.getBlock()))
        if(!bs.isAir()) solid++
        if(!bs.getFluidState().isEmpty()) fluids++
        blocks[id]=(blocks[id]||0)+1;report.counts[id]=(report.counts[id]||0)+1
        if(id!==last) {if(count)runs.push([last,count]);last=id;count=1}else count++
      }
      runs.push([last,count])
      if(c<-.80 && fluids) report.errors.push('Void fluid '+x+','+z+': '+fluids)
      if(c<-.94 && solid) report.errors.push('Far-field blocks '+x+','+z+': '+solid)
      report.columns.push({site:site,x:x,z:z,c:c,biome:biome,solid:solid,fluids:fluids,runs:runs})
      offset+=2
      if(offset>16){console.info('[VOID AUDIT] SITE '+p.kind);offset=-16;site++}
      if(site<sites.length)server.scheduleInTicks(1,tick)
      else {JsonIO.write('kubejs/void_terrain_result.json',report);console.info('[VOID AUDIT] COMPLETE errors='+report.errors.length)}
    }
    tick()
  })
})
