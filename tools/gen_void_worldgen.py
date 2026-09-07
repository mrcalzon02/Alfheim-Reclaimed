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
# Leave a narrow intact shore inside the biome transition. If terrain and biome ended
# on the same continentalness value, interpolation could expose holes beneath the ocean.
RIM=-0.82
BIOME_RIM=-0.80
CLIFF=-0.86
TERMINAL=-0.925
EMPTY=-0.94
BASAL_LAVA_Y=-54
CATALOG=json.loads((ROOT/'alfheim_reclaimed_design/void/void_catalog.json').read_text())
VOID_IDS=[b['id'] for b in CATALOG['biomes']]
DEBRIS_IDS=[id for id in VOID_IDS if id != 'alfheim:void_verge']

def noise(name,y=0,xz=1.0):
    return {'type':'minecraft:noise','noise':'alfheim:void/'+name,'xz_scale':xz,'y_scale':y}

def unary(kind,value):
    return {'type':'minecraft:'+kind,'argument':value}

def maximum(*values):
    result=values[0]
    for value in values[1:]:result=binary('max',result,value)
    return result

def clamp(value, low, high):
    return {'type':'minecraft:clamp','input':value,'min':low,'max':high}

def density(normal, shore_normal=None):
    # Deepworks wraps ordinary Alfheim density with cavern carving. The littoral blend needs
    # the original surface density, otherwise those unrelated deep cavities leak into the
    # Void branch and defeat the guarantee that this transition remains supported.
    if shore_normal is None:
        shore_normal=normal
    # Safe rim: continuous footing, but no longer a slab cut with a ruler. Two
    # horizontal scales displace the top by several blocks while preserving the
    # guaranteed solid approach. Its median surface is only a few blocks above sea
    # level so the transition can make shelves, low slopes and coves before the tall
    # detached margins begin.
    rim_relief=binary('add',binary('mul',0.46,noise('relief')),
                      binary('mul',0.16,noise('detail')))
    rim=binary('add',gradient((53,83),1,-1),rim_relief)

    # The previous final range_choice jumped directly from `normal` density to `rim`
    # at RIM. That discontinuity is the vertical wall in the September field screenshot:
    # punching noise holes into it cannot turn it into a coast. Blend the complete normal
    # density into the low rim across CLIFF..RIM instead. Continentalness already has broad,
    # curved contours; relief/detail give the target shore local ledges and inlets.
    shore_t=clamp(binary('mul',1.0/(RIM-CLIFF),binary('add',MASK,-CLIFF)),0.0,1.0)
    shoreline=binary('add',binary('mul',shore_t,shore_normal),
                     binary('mul',binary('add',1.0,binary('mul',-1.0,shore_t)),rim))
    # Progressive loss of footprint toward the void. Clamped continentalness
    # makes the taper seed-independent; the hard cutoff guarantees termination.
    taper=binary('add',binary('mul',8,MASK),7.18)
    # Shared edge envelope. It controls *where* surviving material is possible, but no
    # longer supplies one interchangeable blob silhouette to all four lateral biomes.
    # Each branch below composes its own named landforms inside this envelope.
    footprint=binary('add',
        binary('add',binary('mul',1.55,noise('fragments',0.62)),taper),
        binary('mul',0.34,noise('fracture',1.35)))
    lower=binary('add',gradient((24,54),-1,1),binary('mul',0.25,noise('shape',0.55)))
    upper=binary('add',gradient((68,98),1,-1),binary('mul',0.28,noise('shape',0.55)))
    window=binary('min',lower,upper)
    # SHATTERFIELDS: broad pressure plates plus sparse, narrow vertical remnants.
    # The needles have their own elongated 3-D field instead of inheriting the slab
    # footprint, which makes the horizon vocabulary visibly different from Rootfall.
    pressure_slabs=binary('min',
        binary('add',footprint,binary('mul',0.30,noise('pressure_plates',2.4))),window)
    needle_footprint=binary('add',binary('add',taper,binary('mul',1.75,noise('fault_needles',0.14))),-0.48)
    needle_window=binary('min',
        binary('add',gradient((10,48),-1,1),binary('mul',0.12,noise('detail',0.5))),
        binary('add',gradient((78,126),1,-1),binary('mul',0.14,noise('detail',0.5))))
    shatter=maximum(pressure_slabs,binary('min',needle_footprint,needle_window))

    # PRISM DRIFT: taller competent cores cut by a separate thin seam field. The
    # subtraction is bounded, so a seam reads as a split rather than deleting a host.
    prism_footprint=binary('add',binary('add',taper,binary('mul',1.48,noise('prism_cores',0.32))),-0.20)
    prism_window=binary('min',
        binary('add',gradient((12,58),-1,1),binary('mul',0.20,noise('shape',0.42))),
        binary('add',gradient((82,120),1,-1),binary('mul',0.18,noise('detail',0.62))))
    seam_distance=unary('abs',noise('split_seams',0.20))
    seam_cut=clamp(binary('mul',2.5,binary('add',seam_distance,-0.045)),0.0,0.24)
    prisms=binary('add',binary('min',prism_footprint,prism_window),binary('add',seam_cut,-0.24))

    # ROOTFALL: a surviving crown/shelf is explicitly supported by elongated fossil
    # ribs. The same root_ribs field owns the Rootfossil material rule below, so the
    # named stone and the geometry cannot drift back into unrelated random blobs.
    root_crown=binary('min',footprint,binary('min',
        binary('add',gradient((38,58),-1,1),binary('mul',0.16,noise('shape',0.65))),
        binary('add',gradient((76,96),1,-1),binary('mul',0.16,noise('detail',0.85)))))
    rib_footprint=binary('add',binary('add',taper,binary('mul',1.90,noise('root_ribs',0.10))),-0.42)
    rib_window=binary('min',
        binary('add',gradient((-2,46),-1,1),binary('mul',0.10,noise('detail',0.45))),
        binary('add',gradient((72,96),1,-1),binary('mul',0.12,noise('shape',0.40))))
    roots=maximum(root_crown,binary('min',rib_footprint,rib_window))

    # SEPULCHRAL REACH: unusually broad, quiet shelves and thick backing volumes.
    # High vertical frequency is deliberately restrained to shallow bed offsets.
    memorial_shelf=binary('min',
        binary('add',footprint,binary('mul',0.18,noise('burial_beds',2.0))),
        binary('min',
            binary('add',gradient((28,52),-1,1),binary('mul',0.10,noise('fracture',0.9))),
            binary('add',gradient((76,92),1,-1),binary('mul',0.10,noise('detail',0.8)))))
    burial_backing=binary('min',binary('add',footprint,-0.08),binary('min',
        gradient((18,54),-1,1),gradient((72,106),1,-1)))
    shelves=maximum(memorial_shelf,burial_backing)
    fragments=choose('mythicbotany:alfheim_temperature',-100,0,
        choose('mythicbotany:alfheim_humidity',-100,0,shatter,prisms),
        choose('mythicbotany:alfheim_humidity',-100,0,roots,shelves))
    terminal=binary('min',binary('add',footprint,-0.30),binary('min',
        binary('add',gradient((42,62),-1,1),binary('mul',0.18,noise('shape',0.8))),
        binary('add',gradient((65,80),1,-1),binary('mul',0.16,noise('detail',1.0)))))
    void=choose(MASK,-100,EMPTY,-1.0,choose(MASK,-100,TERMINAL,terminal,
                choose(MASK,-100,CLIFF,fragments,shoreline)))
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
            ('alfheim:void_verge',pt((CLIFF,BIOME_RIM)))]

def surface_rule():
    # This is the second half of the data-only basal-void contract above. Surface
    # rules run over default stone through the full build height, so sacrificial
    # Livingrock below the hardcoded lava picker becomes literal air before features.
    # Void Verge is excluded because its safe approach shelf is intentionally solid.
    rules=[condition({'type':'minecraft:biome','biome_is':DEBRIS_IDS},
                     condition(negate(above(BASAL_LAVA_Y)),block('minecraft:air')))]
    floor={'type':'minecraft:stone_depth','offset':3,'add_surface_depth':False,
           'secondary_depth_range':0,'surface_type':'floor'}
    def threshold(name,low,high=100):
        return {'type':'minecraft:noise_threshold','noise':'alfheim:void/'+name,
                'min_threshold':low,'max_threshold':high}
    grammar={b['id']:{r['feature']:r['material'] for r in b['terrain_grammar']}
             for b in CATALOG['biomes']}
    # These are feature grammars, not palettes. A material is selected because the
    # block belongs to a recognisable landform or structural role. Signature stones
    # that are absent here are emitted only by the matching configured feature below.
    palettes={
        'alfheim:void_verge':sequence([
            condition(floor,block(grammar['alfheim:void_verge']['verge_table'])),
            block(grammar['alfheim:void_verge']['breakline_scar'])]),
        'alfheim:shatterfields':sequence([
            condition(threshold('split_seams',-0.035,0.035),block(grammar['alfheim:shatterfields']['split_seam'])),
            condition(floor,block(grammar['alfheim:shatterfields']['pressure_slab'])),
            block(grammar['alfheim:shatterfields']['fault_needle'])]),
        'alfheim:prism_drift':sequence([
            condition(threshold('split_seams',-0.055,0.055),block(grammar['alfheim:prism_drift']['split_seam'])),
            condition(floor,block(grammar['alfheim:prism_drift']['crystal_crown'])),
            block(grammar['alfheim:prism_drift']['prism_core'])]),
        'alfheim:rootfall':sequence([
            condition(threshold('root_ribs',0.12),block(grammar['alfheim:rootfall']['root_apron'])),
            condition(threshold('root_ribs',-0.10,0.12),block(grammar['alfheim:rootfall']['resin_halo'])),
            block(grammar['alfheim:rootfall']['trunk_socket'])]),
        'alfheim:sepulchral_reach':sequence([
            condition(floor,block(grammar['alfheim:sepulchral_reach']['memorial_shelf'])),
            block(grammar['alfheim:sepulchral_reach']['competent_backing'])]),
        'alfheim:starless_reach':sequence([
            condition(threshold('astralite_flecks',0.72),block(grammar['alfheim:starless_reach']['astralite_fleck'])),
            condition(floor,block(grammar['alfheim:starless_reach']['hollow_splinter'])),
            block(grammar['alfheim:starless_reach']['terminal_landing'])]),
    }
    for biome,palette in palettes.items():
        rules.append(condition({'type':'minecraft:biome','biome_is':[biome]},palette))
    return sequence(rules)

def extra_files():
    out={}
    def emit(path,value):out['kubejs/data/'+path]=(json.dumps(value,indent=2)+'\n').encode()
    for name,octave,amps in [('relief',-5,[1,0.5]),('detail',-3,[1,0.5]),
                             ('fragments',-5,[1,0.6,0.3]),('fracture',-3,[1,0.45]),
                             ('shape',-4,[1,0.5]),('pressure_plates',-4,[1,0.5]),
                             ('fault_needles',-3,[1,0.45]),('prism_cores',-4,[1,0.55]),
                             ('split_seams',-3,[1,0.5]),('root_ribs',-3,[1,0.48]),
                             ('burial_beds',-5,[1,0.45]),('astralite_flecks',-2,[1,0.35])]:
        emit('alfheim/worldgen/noise/void/'+name+'.json',{'firstOctave':octave,'amplitudes':amps})
    emit('alfheim/tags/worldgen/biome/void_margins.json',{'replace':False,'values':VOID_IDS})
    # REMOVE phase runs after all ADD modifiers. Conventional liquid pools must
    # not refill the dry margin. Keep the authored Rim geode/marker until their
    # volume-checked replacement exists; removing them here silently deletes the
    # existing exploration route before that replacement is implemented.
    emit('alfheim/forge/biome_modifier/void_no_pools_geodes.json',{'type':'forge:remove_features','biomes':'#alfheim:void_margins','features':['alfheim:liquid_bifrost_pool'],'steps':['lakes','local_modifications','top_layer_modification']})

    # Small material formations make each margin legible before its full landmark
    # pair is found.  They use the pre-existing surface mass and never manufacture
    # support beneath themselves.
    air={'type':'minecraft:matching_blocks','blocks':'minecraft:air'}
    natural={'type':'minecraft:matching_block_tag','tag':'alfheim:void_natural'}
    def provider(entries):
        if len(entries)==1:return {'type':'minecraft:simple_state_provider','state':{'Name':entries[0][0]}}
        return {'type':'minecraft:weighted_state_provider','entries':[
            {'data':{'Name':state},'weight':weight} for state,weight in entries]}
    def column(direction,layers,allowed):
        return {'type':'minecraft:block_column','config':{'direction':direction,
            'allowed_placement':allowed,'prioritize_tip':True,'layers':[
                {'height':height,'provider':provider(states)} for height,states in layers]}}
    uniform=lambda lo,hi:{'type':'minecraft:uniform','value':{'min_inclusive':lo,'max_inclusive':hi}}

    # Upright markers/steles are columns; the Rootfall formation is a patch of long
    # downward columns inside existing support; crystal crowns remain low hosted piles;
    # Astralite is a tiny replacement fleck. Distinct reads now use distinct codecs.
    formations={
        'verge_markers':('alfheim:void_verge',14,column('up',[(uniform(2,4),[('alfheim:veilstone_livingrock',1)]),(1,[('minecraft:amethyst_block',1)])],air),[]),
        'shatter_anchors':('alfheim:shatterfields',12,column('up',[(uniform(4,9),[('alfheim:anchorstone_livingrock',4),('alfheim:seamstone_livingrock',1)])],air),[]),
        'prism_crowns':('alfheim:prism_drift',8,{'type':'minecraft:block_pile','config':{'state_provider':provider([('alfheim:prismstone_livingrock',4),('minecraft:amethyst_block',2),('minecraft:budding_amethyst',1)])}},[]),
        'root_aprons':('alfheim:rootfall',11,{'type':'minecraft:random_patch','config':{
            'tries':14,'xz_spread':6,'y_spread':0,'feature':{'feature':column('down',[
                (uniform(7,18),[('alfheim:rootfossil_livingrock',5),('alfheim:resinshale_livingrock',1)])],natural),
                'placement':[{'type':'minecraft:random_offset','xz_spread':0,'y_spread':-1},
                             {'type':'minecraft:block_predicate_filter','predicate':natural}]}}},[]),
        'mourning_steles':('alfheim:sepulchral_reach',13,column('up',[(uniform(2,5),[('alfheim:epitaph_livingrock',5)]),(1,[('alfheim:oathstone_livingrock',1)])],air),[]),
        'astralite_flecks':('alfheim:starless_reach',18,{'type':'minecraft:ore','config':{
            'size':3,'discard_chance_on_air_exposure':0.0,'targets':[
                {'target':{'predicate_type':'minecraft:block_match','block':state},
                 'state':{'Name':'alfheim:astralite_livingrock'}}
                for state in ('alfheim:nightmantle_livingrock','alfheim:nullstone_livingrock')]}},
            [{'type':'minecraft:random_offset','xz_spread':0,'y_spread':-2}]),
    }
    for name,(biome,chance,configured,extra_placement) in formations.items():
        emit('alfheim/worldgen/configured_feature/void/'+name+'.json',configured)
        emit('alfheim/worldgen/placed_feature/void/'+name+'.json',{'feature':'alfheim:void/'+name,'placement':[
            {'type':'minecraft:rarity_filter','chance':chance},{'type':'minecraft:in_square'},
            {'type':'minecraft:heightmap','heightmap':'MOTION_BLOCKING_NO_LEAVES'},
            *extra_placement,{'type':'minecraft:biome'}]})
        emit('alfheim/forge/biome_modifier/void_'+name+'.json',{'type':'forge:add_features',
            'biomes':[biome],'features':'alfheim:void/'+name,'step':'local_modifications'})
    return out
