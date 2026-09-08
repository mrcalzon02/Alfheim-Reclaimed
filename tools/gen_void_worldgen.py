"""Shared dry-margin density, lateral biome claims, and natural stone palettes.

All generation uses unperturbed 2D Alfheim continentalness for membership. Noise
inside the debris band varies shape; it cannot escape the empty far-field cutoff.

The dry-void contract stays entirely data-driven. Detached debris is kept above the
global water table. A sacrificial solid guard covers Minecraft's hardcoded lowest fluid
band and is stripped by Void surface rules; the safe Void Verge shelf remains solid.
"""
import json
from gen_deep_terrain import ROOT, binary, choose, gradient, condition, block, sequence, above, negate

MASK='mythicbotany:alfheim_continentalness'
# Leave a narrow intact shore inside the biome transition. If terrain and biome ended
# on the same continentalness value, interpolation could expose holes beneath the ocean.
RIM=-0.82
# Dry the inward shoulder as well as the visible margin so neighbouring water
# centres cannot bleed through the breakline. Floodedness is evaluated at block
# coordinates, so it must use the exact shifted continentalness field.
DRY_AQUIFER_RIM=-0.58
BIOME_RIM=-0.80
CLIFF=-0.86
TERMINAL=-0.925
BASAL_LAVA_Y=-54
CATALOG=json.loads((ROOT/'alfheim_reclaimed_design/void/void_catalog.json').read_text())
VOID_IDS=[b['id'] for b in CATALOG['biomes']]
DEBRIS_IDS=[id for id in VOID_IDS if id != 'alfheim:void_verge']

def noise(name,y=0,xz=1.0):
    return {'type':'minecraft:noise','noise':'alfheim:void/'+name,'xz_scale':xz,'y_scale':y}

def clamp(value, low, high):
    return {'type':'minecraft:clamp','input':value,'min':low,'max':high}

def density(normal, shore_normal=None):
    # Deepworks wraps ordinary Alfheim density with cavern carving. The littoral blend needs
    # the original surface density, otherwise those unrelated deep cavities leak into the
    # Void branch and defeat the guarantee that this transition remains supported.
    if shore_normal is None:
        shore_normal=normal
    # Safe rim: a quiet, continuous shelf whose lowest noise displacement remains
    # above sea level. The former 0.62 combined amplitude moved the nominal Y=68
    # surface down into the global water table and exposed flowing water at the
    # breakline. Keep only broad, low-amplitude relief around a Y=72 median.
    rim_relief=binary('add',binary('mul',0.18,noise('relief',0,xz=0.72)),
                      binary('mul',0.05,noise('detail',0,xz=0.62)))
    rim=binary('add',gradient((62,82),1,-1),rim_relief)

    # The previous final range_choice jumped directly from `normal` density to `rim`
    # at RIM. That discontinuity is the vertical wall in the September field screenshot:
    # punching noise holes into it cannot turn it into a coast. Blend the complete normal
    # density into the low rim across CLIFF..RIM instead. Continentalness already has broad,
    # curved contours; relief/detail give the target shore local ledges and inlets.
    shore_t=clamp(binary('mul',1.0/(RIM-CLIFF),binary('add',MASK,-CLIFF)),0.0,1.0)
    shoreline=binary('add',binary('mul',shore_t,shore_normal),
                     binary('mul',binary('add',1.0,binary('mul',-1.0,shore_t)),rim))
    # The old four-way 3-D debris field is deliberately absent. Even with amplitude
    # caps, Minecraft's cell interpolation could carry an entire jagged splinter far
    # beyond its pointwise mask. Keep one continuous, supported shore and clean air
    # beyond CLIFF; biome-specific forms return later as bounded configured features.
    void=choose(MASK,-100,CLIFF,-1.0,shoreline)
    # NoiseBasedChunkGenerator consults its global fluid picker at the lowest ten
    # levels before routed floodedness can return air. Temporary default stone blocks
    # that picker; surface_rule() removes it in debris/terminal Void biomes.
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
