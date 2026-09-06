"""Deep terrain integration; keeps a single owner for Alfheim's final density.

The biome generator calls wrap_density(). This sibling emits only its own noise,
surface and ore files plus a narrowly amended copy of installed noise settings.
Both generators may run in either order without erasing the Deep/Void composition.
"""
from pathlib import Path
import argparse
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'kubejs/data/'


def config(): return json.loads((ROOT/'tools/deepworks_terrain.json').read_text())
def binary(kind, a, b): return {'type':'minecraft:'+kind,'argument1':a,'argument2':b}
def noise(name, y=1): return {'type':'minecraft:noise','noise':'alfheim:deepworks/'+name,'xz_scale':1.0,'y_scale':y}
def gradient(ys, a, b): return {'type':'minecraft:y_clamped_gradient','from_y':ys[0],'to_y':ys[1],'from_value':a,'to_value':b}
def choose(input, low, high, yes, no):
    return {'type':'minecraft:range_choice','input':input,'min_inclusive':low,'max_exclusive':high,
            'when_in_range':yes,'when_out_of_range':no}


def cavity_density():
    c=config()
    terms=[binary('add',noise('province',0),c['region_threshold']),
           binary('add',noise('chambers',1.25),c['chamber_threshold']),
           gradient(c['floor'],1,-1),gradient(c['roof'],-1,1),
           binary('add',c['minimum_initial_density'],binary('mul',-1,'mythicbotany:alfheim_initial'))]
    result=terms[0]
    for term in terms[1:]: result=binary('max',result,term)
    return {'type':'minecraft:interpolated','argument':result}


def wrap_density(normal):
    # Caller applies this only to the non-Void branch. Outside the Y envelope this
    # is literally the old expression, preserving bedrock and upper terrain density.
    return choose('minecraft:y',-60,28,
                  binary('min',normal,'alfheim:deepworks/cavities'),normal)


def block(name): return {'type':'minecraft:block','result_state':{'Name':name}}
def condition(test, rule): return {'type':'minecraft:condition','if_true':test,'then_run':rule}
def above(y): return {'type':'minecraft:y_above','anchor':{'absolute':y},'surface_depth_multiplier':0,'add_stone_depth':False}
def negate(test): return {'type':'minecraft:not','invert':test}
def threshold(name, low, high=100): return {'type':'minecraft:noise_threshold','noise':'alfheim:deepworks/'+name,'min_threshold':low,'max_threshold':high}
def sequence(rows): return {'type':'minecraft:sequence','sequence':rows}
def vertical_gradient(name, below, above):
    return {'type':'minecraft:vertical_gradient','random_name':'alfheim:'+name,
            'true_at_and_below':{'absolute':below},'false_at_and_above':{'absolute':above}}


def identity_surface_rule():
    """Biome-specific exposed floors, ahead of MythicBotany's grass/dirt rule."""
    floor={'type':'minecraft:stone_depth','offset':0,'add_surface_depth':False,
           'secondary_depth_range':0,'surface_type':'floor'}
    shallow={'type':'minecraft:stone_depth','offset':3,'add_surface_depth':True,
             'secondary_depth_range':0,'surface_type':'floor'}
    preliminary={'type':'minecraft:above_preliminary_surface'}
    mix=lambda low: {'type':'minecraft:noise_threshold','noise':'alfheim:deepworks/surface_mix',
                     'min_threshold':low,'max_threshold':100}
    def palette(biome, tops, fill):
        top=sequence([condition(mix(limit),block(name)) for limit,name in tops]+[block(fill)])
        return condition({'type':'minecraft:biome','biome_is':[biome]},
                         condition(preliminary,sequence([condition(floor,top),
                                                        condition(shallow,block(fill))])))
    return sequence([
        palette('alfheim:scorchfell',[(0.56,'minecraft:magma_block'),
                                      (0.12,'minecraft:blackstone'),
                                      (-0.30,'minecraft:coarse_dirt')],
                'minecraft:basalt'),
        palette('alfheim:starved_reach',[(0.58,'minecraft:blue_ice'),
                                         (0.18,'minecraft:packed_ice'),
                                         (-0.28,'minecraft:snow_block')],
                'minecraft:packed_ice'),
        palette('alfheim:alfheim_ocean',[(0.35,'minecraft:gravel'),
                                         (-0.35,'minecraft:sand')],
                'minecraft:sand'),
    ])


def build():
    from gen_void_worldgen import VOID_IDS, MASK, RIM, surface_rule, extra_files
    c=config()
    with zipfile.ZipFile(next((ROOT/'mods').glob('MythicBotany*.jar'))) as jar:
        settings=json.loads(jar.read('data/mythicbotany/worldgen/noise_settings/alfheim.json'))
        surface=json.loads(jar.read('data/mythicbotany/libx/surface_rule_set/alfheim_surface.json'))
    out={}
    def emit(path,obj): out[PREFIX+path]=(json.dumps(obj,indent=2)+'\n').encode()
    for name,value in c['noises'].items(): emit('alfheim/worldgen/noise/deepworks/'+name+'.json',value)
    emit('alfheim/worldgen/density_function/deepworks/cavities.json',cavity_density())

    # The dry Void needs all aquifer inputs to consume the same continentalness mask.
    # floodedness=-1 removes ordinary aquifer levels. initial_density=+1 is not terrain:
    # NoiseChunk uses it only for preliminary-surface estimation, and the high value stops
    # the aquifer's early surface shortcut from interpreting removed edge columns as ocean.
    # spread and lava are inert inside the same region. The separate basal final-density
    # guard in gen_void_worldgen handles the global Y<-54 lava picker before aquifer noise.
    old_floodedness=settings['noise_router']['fluid_level_floodedness']
    old_initial=settings['noise_router']['initial_density_without_jaggedness']
    old_spread=settings['noise_router']['fluid_level_spread']
    old_lava=settings['noise_router']['lava']
    deep_floodedness=choose('minecraft:y',-60,28,
        choose('alfheim:deepworks/cavities',-100,0,-1.0,old_floodedness),old_floodedness)
    settings['noise_router']['fluid_level_floodedness']=choose(MASK,-100,RIM,-1.0,deep_floodedness)
    settings['noise_router']['initial_density_without_jaggedness']=choose(MASK,-100,RIM,1.0,old_initial)
    settings['noise_router']['fluid_level_spread']=choose(MASK,-100,RIM,0.0,old_spread)
    settings['noise_router']['lava']=choose(MASK,-100,RIM,0.0,old_lava)

    # Keep MythicBotany's own vein_gap untouched. The retired custom helper used
    # this otherwise unrelated channel as an opt-in marker; the data-only repair
    # must not retain or reproduce that marker.
    expected_vein_gap={'type':'minecraft:noise','noise':'minecraft:ore_gap','xz_scale':1.0,'y_scale':1.0}
    if settings['noise_router']['vein_gap'] != expected_vein_gap:
        raise RuntimeError('Unexpected MythicBotany vein_gap; refusing to overwrite upstream noise settings')
    out.update(extra_files())
    emit('mythicbotany/worldgen/noise_settings/alfheim.json',settings)

    families=json.loads((ROOT/'tools/deepworks_manifest.json').read_text())['families']
    known={f['id'] for f in families}
    # Every land biome owns a recognisable five-stone geological family.  The old
    # four broad buckets made very different places share the same underground and
    # silently dropped every deficient biome into the generic Ley fallback.
    biome_palettes={
        'alfheim:ashen_grove':['cinder_livingrock','cracked_livingrock','embervein_livingrock','obsidian_livingrock','gloam_livingrock'],
        'alfheim:sundered_highlands':['cracked_livingrock','obsidian_livingrock','starfleck_livingrock','moonstone_livingrock','embervein_livingrock'],
        'alfheim:scorchfell':['magmatic_livingrock','embervein_livingrock','cinder_livingrock','obsidian_livingrock','cracked_livingrock'],
        'mythicbotany:dreamwood_forest':['rootbound_livingrock','moss_livingrock','petrified_livingrock','amber_livingrock','fern_livingrock'],
        'alfheim:silverbark_wood':['fern_livingrock','silvermist_livingrock','frost_livingrock','rootbound_livingrock','moonstone_livingrock'],
        'alfheim:bloomfall_vale':['moss_livingrock','amber_livingrock','rose_livingrock','fern_livingrock','leyline_livingrock'],
        'mythicbotany:alfheim_lakes':['tide_livingrock','abyssal_livingrock','storm_livingrock','gale_livingrock','frost_livingrock'],
        'alfheim:alfheim_ocean':['abyssal_livingrock','tide_livingrock','storm_livingrock','frost_livingrock','gale_livingrock'],
        'alfheim:mana_fen':['tide_livingrock','moss_livingrock','abyssal_livingrock','leyline_livingrock','fern_livingrock'],
        'mythicbotany:golden_fields':['dawn_livingrock','amber_livingrock','ivory_livingrock','starfleck_livingrock','rose_livingrock'],
        'mythicbotany:alfheim_plains':['ivory_livingrock','dawn_livingrock','silvermist_livingrock','moonstone_livingrock','leyline_livingrock'],
        'alfheim:starved_reach':['frost_livingrock','ivory_livingrock','moonstone_livingrock','gloam_livingrock','starfleck_livingrock'],
        'alfheim:hollow_marches':['gloam_livingrock','storm_livingrock','frost_livingrock','cracked_livingrock','abyssal_livingrock'],
        'alfheim:infested_warren':['rootbound_livingrock','gloam_livingrock','moss_livingrock','petrified_livingrock','amethyst_livingrock'],
        'alfheim:decayed_mire':['abyssal_livingrock','moss_livingrock','gloam_livingrock','tide_livingrock','amethyst_livingrock'],
        'mythicbotany:alfheim_hills':['cracked_livingrock','storm_livingrock','gale_livingrock','moonstone_livingrock','obsidian_livingrock'],
    }
    assert all(set(ids)<=known for ids in biome_palettes.values())
    palettes=[([biome],ids) for biome,ids in biome_palettes.items()]
    palettes.append(([],['amethyst_livingrock','leyline_livingrock','gloam_livingrock',
                         'starfleck_livingrock','moonstone_livingrock']))
    zones=[]
    for biomes,ids in palettes:
        def strata_rule(stones):
            step=1.35/max(1,len(stones)-1)
            rules=[condition(threshold('strata',-0.68+i*step),block('alfheim:'+id))
                   for i,id in reversed(list(enumerate(stones[1:])))]
            rules.append(block('alfheim:'+stones[0]))
            return sequence(rules)
        upper=strata_rule(ids[:3])
        lower=strata_rule(ids[2:]+ids[:2])
        rule=sequence([
            condition(threshold('inclusions',0.62),block('alfheim:'+ids[-1])),
            condition(negate(above(-34)),lower),
            condition(vertical_gradient('deepworks_lower_blend',-30,-8),lower),
            upper,
        ])
        zones.append(condition({'type':'minecraft:biome','biome_is':biomes},rule) if biomes else rule)
    floor={'type':'minecraft:stone_depth','offset':3,'add_surface_depth':False,'secondary_depth_range':0,'surface_type':'floor'}
    geology=sequence([
        condition(negate(above(-51)),condition(floor,sequence([
            condition(threshold('inclusions',0.30),block('alfheim:livingrock_slag')),
            block('alfheim:magmatic_livingrock')]))),
        condition(negate(above(-45)),condition(floor,block('alfheim:cracked_livingrock'))),
        sequence(zones)])
    geology=condition(above(c['geology_y'][0]),
        condition(vertical_gradient('deepworks_upper_contact',8,42),
        condition(negate({'type':'minecraft:biome','biome_is':VOID_IDS}),geology)))
    # Bedrock still runs first; biome and surface rules are otherwise retained.
    surface['before_biomes']=sequence([surface_rule(),identity_surface_rule(),
                                       surface['before_biomes'],geology])
    emit('mythicbotany/libx/surface_rule_set/alfheim_surface.json',surface)
    # Surface material replacement happens before underground_ores. The ordinary
    # features remain unchanged, while these additions can replace only library rock.
    placed=[]
    for bloom in c['blooms']:
        id='deepworks/ore_'+bloom
        ore_targets=[{'target':{'predicate_type':'minecraft:block_match',
                                'block':'alfheim:'+f['id']},
                      'state':{'Name':'alfheim:'+bloom+'_'+f['id'].removesuffix('_livingrock')+'_ore'}}
                     for f in families]
        ore_targets.append({'target':{'predicate_type':'minecraft:tag_match',
                                      'tag':'alfheim:livingrock_natural'},
                            'state':{'Name':'alfheim:'+bloom+'_ore'}})
        emit('alfheim/worldgen/configured_feature/'+id+'.json',{
            'type':'minecraft:ore','config':{'size':c['ore_size'],'discard_chance_on_air_exposure':0,
                'targets':ore_targets}})
        emit('alfheim/worldgen/placed_feature/'+id+'.json',{'feature':'alfheim:'+id,'placement':[
            {'type':'minecraft:count','count':c['ore_attempts']},{'type':'minecraft:in_square'},
            {'type':'minecraft:height_range','height':{'type':'minecraft:trapezoid',
                'min_inclusive':{'absolute':c['ore_y'][0]},'max_inclusive':{'absolute':c['ore_y'][1]},'plateau':16}},
            {'type':'minecraft:biome'}]})
        placed.append('alfheim:'+id)
    emit('alfheim/forge/biome_modifier/deepworks_ores.json',{'type':'forge:add_features',
        'biomes':'#alfheim:deepworks_land','features':placed,'step':'underground_ores'})
    # Explicitly exclude all Void Margin biomes; the home tag is shared with their islands.
    layer=json.loads((ROOT/(PREFIX+'mythicbotany/libx/biome_layer/alfheim.json')).read_text())
    land=sorted({r['biome'] for r in layer['biomes']} - set(VOID_IDS))
    emit('alfheim/tags/worldgen/biome/deepworks_land.json',{'replace':False,'values':land})
    # Preserve all existing native ore/bloom routes through the changed host rock.
    # This is MythicBotany's narrow native tag, never a vanilla replacement tag.
    emit('mythicbotany/tags/blocks/base_stone_alfheim.json',{'replace':False,'values':['#alfheim:livingrock_natural','#alfheim:void_natural']})
    return out


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    out=build()
    # Only ask the biome generator for its existing function; do not regenerate its
    # unrelated habitat/biome files, which may have work from other project tasks.
    from gen_alfheim_biomes import void_final_density
    out[PREFIX+'mythicbotany/worldgen/density_function/alfheim_final.json']=(json.dumps(void_final_density(),indent=2)+'\n').encode()
    for name,data in out.items():
        p=ROOT/name
        if args.check: assert p.read_bytes()==data, name
        else: p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
    print(f'{len(out)} Deep terrain files '+('byte-identical' if args.check else 'generated'))


if __name__=='__main__': main()
