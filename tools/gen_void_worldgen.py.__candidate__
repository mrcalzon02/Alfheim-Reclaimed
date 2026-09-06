"""Shared dry-margin density, lateral biome claims, and natural stone palettes.

All generation uses unperturbed 2D Alfheim continentalness for membership. Noise
inside the debris band varies shape; it cannot escape the empty far-field cutoff.

The dry-void contract stays entirely data-driven. Minecraft's aquifer picker hardcodes
lava below Y=-54 before floodedness noise can veto it, so the void branch uses a
temporary positive default-block density below that boundary. The existing surface
rule stage then converts that temporary Livingrock to literal air only in debris/terminal
void biomes. The safe Void Verge shelf remains solid, and ordinary Alfheim is untouched.
"""
import json
from gen_deep_terrain import ROOT, binary, choose, gradient, condition, block, sequence, above, negate

MASK='mythicbotany:alfheim_continentalness'
RIM=-0.80
CLIFF=-0.86
TERMINAL=-0.925
EMPTY=-0.94
BASAL_LAVA_Y=-54
CATALOG=json.loads((ROOT/'alfheim_reclaimed_design/void/void_catalog.json').read_text())
VOID_IDS=[b['id'] for b in CATALOG['biomes']]
DEBRIS_IDS=[id for id in VOID_IDS if id != 'alfheim:void_verge']

def noise(name,y=0):
    return {'type':'minecraft:noise','noise':'alfheim:void/'+name,'xz_scale':1.0,'y_scale':y}

def density(normal):
    # Safe rim: gently uneven, solid ground with a top around Y=80; no caves
    # undermine the approach. The continent's original terrain remains outside.
    rim=binary('add',gradient((72,88),1,-1),binary('mul',0.18,noise('relief')))
    # Progressive loss of footprint toward the void. Clamped continentalness
    # makes the taper seed-independent; the hard cutoff guarantees termination.
    taper=binary('add',binary('mul',8,MASK),7.18)
    footprint=binary('add',binary('mul',1.8,noise('fragments')),taper)
    window=binary('min',gradient((28,52),-1,1),gradient((70,92),1,-1))
    slabs=binary('min',footprint,window)
    # Rootfall extends tapered ribs beneath a shared slab crown; Sepulchral
    # shelves use flatter, thicker fragments. Both remain bounded by footprint.
    roots=binary('min',footprint,binary('min',gradient((4,46),-1,1),gradient((70,88),1,-1)))
    prisms=binary('min',footprint,binary('min',gradient((24,60),-1,1),gradient((74,112),1,-1)))
    shelves=binary('min',footprint,binary('min',gradient((34,48),-1,1),gradient((76,84),1,-1)))
    fragments=choose('mythicbotany:alfheim_temperature',-100,0,
        choose('mythicbotany:alfheim_humidity',-100,0,slabs,prisms),
        choose('mythicbotany:alfheim_humidity',-100,0,roots,shelves))
    terminal=binary('min',binary('add',footprint,-0.30),binary('min',gradient((46,60),-1,1),gradient((66,76),1,-1)))
    void=choose(MASK,-100,EMPTY,-1.0,choose(MASK,-100,TERMINAL,terminal,choose(MASK,-100,CLIFF,fragments,rim)))
    # NoiseBasedChunkGenerator hardcodes lava below Y=-54. Negative density there
    # would therefore become lava before floodedness can suppress it. Build temporary
    # default Livingrock instead; surface_rule() turns it back into air in the five
    # debris/terminal biomes, while Void Verge intentionally keeps its deep support.
    void=choose('minecraft:y',-64,BASAL_LAVA_Y,1.0,void)
    return choose(MASK,-100,RIM,void,normal)

def claims(pt):
    return [('alfheim:starless_reach',pt((-1,TERMINAL))),
            ('alfheim:shatterfields',pt((TERMINAL,CLIFF),temp=(-1,0),hum=(-1,0))),
            ('alfheim:prism_drift',pt((TERMINAL,CLIFF),temp=(-1,0),hum=(0,1))),
            ('alfheim:rootfall',pt((TERMINAL,CLIFF),temp=(0,1),hum=(-1,0))),
            ('alfheim:sepulchral_reach',pt((TERMINAL,CLIFF),temp=(0,1),hum=(0,1))),
            ('alfheim:void_verge',pt((CLIFF,RIM)))]

def surface_rule():
    # This is the second half of the data-only basal-void contract above. Surface
    # rules run over default stone through the full build height, so sacrificial
    # Livingrock below the hardcoded lava picker becomes literal air before features.
    # Void Verge is excluded because its safe approach shelf is intentionally solid.
    rules=[condition({'type':'minecraft:biome','biome_is':DEBRIS_IDS},
                     condition(negate(above(BASAL_LAVA_Y)),block('minecraft:air')))]
    for biome in CATALOG['biomes']:
        stones=biome['stones']
        palette=sequence([condition({'type':'minecraft:noise_threshold','noise':'alfheim:void/strata','min_threshold':0.22,'max_threshold':100},block(stones[2]['id'])),
                          condition({'type':'minecraft:noise_threshold','noise':'alfheim:void/strata','min_threshold':-0.18,'max_threshold':100},block(stones[1]['id'])),block(stones[0]['id'])])
        rules.append(condition({'type':'minecraft:biome','biome_is':[biome['id']]},palette))
    return sequence(rules)

def extra_files():
    out={}
    def emit(path,value):out['kubejs/data/'+path]=(json.dumps(value,indent=2)+'\n').encode()
    for name,octave,amps in [('relief',-5,[1,0.5]),('fragments',-5,[1,0.6,0.3]),('strata',-4,[1,0.5,0.25])]:
        emit('alfheim/worldgen/noise/void/'+name+'.json',{'firstOctave':octave,'amplitudes':amps})
    emit('alfheim/tags/worldgen/biome/void_margins.json',{'replace':False,'values':VOID_IDS})
    # REMOVE phase runs after all ADD modifiers. Conventional liquid pools must
    # not refill the dry margin. Keep the authored Rim geode/marker until their
    # volume-checked replacement exists; removing them here silently deletes the
    # existing exploration route before that replacement is implemented.
    emit('alfheim/forge/biome_modifier/void_no_pools_geodes.json',{'type':'forge:remove_features','biomes':'#alfheim:void_margins','features':['alfheim:liquid_bifrost_pool'],'steps':['lakes','local_modifications','top_layer_modification']})
    return out
