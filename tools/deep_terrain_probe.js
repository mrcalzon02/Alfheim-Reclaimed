// Development-only density search and measurements of actual generated terrain.
var TerrainContext = Java.loadClass('net.minecraft.world.level.levelgen.DensityFunction$SinglePointContext')
var TerrainPos = Java.loadClass('net.minecraft.core.BlockPos')
var TerrainForge = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
var TerrainHeight = Java.loadClass('net.minecraft.world.level.levelgen.Heightmap$Types')

ServerEvents.loaded(event => {
  var server=event.server
  server.scheduleInTicks(60, callback => {
    var level=server.getLevel('mythicbotany:alfheim')
    var router=level.getChunkSource().randomState().router()
    var density=router.finalDensity(), continents=router.continents()
    var options=JSON.parse(String(JsonIO.readJson('kubejs/deep_terrain_options.json')))
    function sample(x,y,z) { return Number(density.compute(new TerrainContext(x,y,z))) }
    var centers=options.centers
    if (!centers || !centers.length) {
      var candidates=[]
      for (var x=-3072;x<=3072;x+=96) for (var z=-3072;z<=3072;z+=96) {
        if (Number(continents.compute(new TerrainContext(x,-24,z))) < -0.6) continue
        if (sample(x,-55,z)>=0 || sample(x,-24,z)>=0 || sample(x,0,z)>=0) continue
        var score=0
        for (var dx=-48;dx<=48;dx+=24) for (var dz=-48;dz<=48;dz+=24) {
          if(sample(x+dx,-24,z+dz)<0) score++
          if(sample(x+dx,0,z+dz)<0) score++
        }
        candidates.push({x:x,z:z,score:score})
      }
      candidates.sort((a,b) => b.score-a.score)
      centers=[]
      candidates.forEach(p => {
        if(centers.length>=3) return
        if(centers.every(q => Math.abs(p.x-q.x)+Math.abs(p.z-q.z)>1024)) centers.push(p)
      })
      if(centers.length!==3) throw new Error('Could not find three cavern test sites: '+JSON.stringify(centers))
    }
    console.info('[TERRAIN AUDIT] SITES '+JSON.stringify(centers))
    var report={mode:options.mode,centers:centers,palette:[],sections:[],density_upper:[],counts:{},surface:[]}
    var index={}
    function idAt(x,y,z) {
      var state=level.getBlockState(new TerrainPos(x,y,z))
      var id=String(TerrainForge.BLOCKS.getKey(state.getBlock()))
      if(index[id]===undefined) { index[id]=report.palette.length; report.palette.push(id) }
      report.counts[id]=(report.counts[id]||0)+1
      return index[id]
    }
    var site=0,axis=0,offset=-128,section={site:0,axis:0,columns:[]}
    function tick() {
      var p=centers[site], x=p.x+(axis===0 ? offset:0), z=p.z+(axis===1 ? offset:0)
      // Never request synchronous generation while holding Rhino's context lock:
      // EntityJS animal construction on a generation worker needs the same lock.
      // The Python harness requests chunks through console commands outside JS.
      if(level.getChunkSource().getChunkNow(Math.floor(x/16),Math.floor(z/16))===null) {
        server.scheduleInTicks(20,tick)
        return
      }
      var runs=[]
      var last=-1,count=0
      for(var y=-64;y<=80;y++) {
        var id=idAt(x,y,z)
        if(id!==last) { if(count) runs.push([last,count]); last=id; count=1 }
        else count++
      }
      runs.push([last,count]); section.columns.push(runs)
      report.density_upper.push([x,z,sample(x,32,z),sample(x,64,z),sample(x,96,z)])
      report.surface.push([x,z,Number(level.getHeight(TerrainHeight.OCEAN_FLOOR_WG,x,z))])
      offset+=2
      if(offset>128) {
        report.sections.push(section)
        console.info('[TERRAIN AUDIT] SECTION site='+site+' axis='+axis+' columns='+section.columns.length)
        offset=-128; axis++
        if(axis>1) {axis=0;site++}
        section={site:site,axis:axis,columns:[]}
      }
      if(site<centers.length) server.scheduleInTicks(1,tick)
      else {
        JsonIO.write('kubejs/deep_terrain_result.json',report)
        console.info('[TERRAIN AUDIT] COMPLETE sections='+report.sections.length+' samples='+Object.values(report.counts).reduce((a,b)=>a+b,0))
      }
    }
    tick()
  })
})
