"""Deep terrain integration; keeps a single owner for Alfheim's final density.

The biome generator calls wrap_density(). This sibling emits only its own noise,
surface and ore files plus a narrowly amended copy of installed noise settings.
Both generators may run in either order without erasing the Deep/Void composition.
"""
from pathlib import Path
import argparse
import copy
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


def build():
    from gen_void_worldgen import VOID_IDS, FLUID_MARKER, surface_rule, extra_files
    c=config()
    with zipfile.ZipFile(next((ROOT/'mods').glob('MythicBotany*.jar'))) as jar:
        settings=json.loads(jar.read('data/mythicbotany/worldgen/noise_settings/alfheim.json'))
        surface=json.loads(jar.read('data/mythicbotany/libx/surface_rule_set/alfheim_surface.json'))
    out={}
    def emit(path,obj): out[PREFIX+path]=(json.dumps(obj,indent=2)+'\n').encode()
    for name,value in c['noises'].items(): emit('alfheim/worldgen/noise/deepworks/'+name+'.json',value)
    emit('alfheim/worldgen/density_function/deepworks/cavities.json',cavity_density())
    # Aquifers stay vanilla outside the actual cavern field. Dry cavern air above
    # the vanilla basal lava picker avoids turning giant chambers into water tanks.
    old=settings['noise_router']['fluid_level_floodedness']
    from gen_alfheim_biomes import void_final_density
    original_final=void_final_density(False)
    deep_floodedness=choose('minecraft:y',-60,28,
        choose('alfheim:deepworks/cavities',-100,0,-1.0,old),old)
    settings['noise_router']['fluid_level_floodedness']=choose(original_final['input'],
        original_final['min_inclusive'],original_final['max_exclusive'],-1.0,deep_floodedness)
    settings['noise_router']['vein_gap']=FLUID_MARKER
    out.update(extra_files())
    emit('mythicbotany/worldgen/noise_settings/alfheim.json',settings)

    families=json.loads((ROOT/'tools/deepworks_manifest.json').read_text())['families']
    # Biome palettes create geographic associations; one low-frequency field then
    # selects coherent masses within each palette. All 24 natural stones have a home.
    palettes=[
        (['alfheim:ashen_grove','alfheim:sundered_highlands','alfheim:scorchfell'],[f['id'] for f in families if f['group']=='Furnace']),
        (['mythicbotany:dreamwood_forest','alfheim:silverbark_wood','alfheim:bloomfall_vale'],[f['id'] for f in families if f['group']=='Grove']),
        (['mythicbotany:alfheim_lakes','alfheim:mana_fen'],[f['id'] for f in families if f['group']=='Water and sky']),
        (['mythicbotany:golden_fields','mythicbotany:alfheim_plains'],[f['id'] for f in families if f['group']=='Court']),
        ([],[f['id'] for f in families if f['group']=='Ley'])]
    zones=[]
    for biomes,ids in palettes:
        rules=[condition(threshold('strata', -0.30+i*0.20),block('alfheim:'+id))
               for i,id in reversed(list(enumerate(ids[1:])))]
        rules.append(block('alfheim:'+ids[0]))
        rule=sequence(rules)
        zones.append(condition({'type':'minecraft:biome','biome_is':biomes},rule) if biomes else rule)
    floor={'type':'minecraft:stone_depth','offset':3,'add_surface_depth':False,'secondary_depth_range':0,'surface_type':'floor'}
    geology=sequence([
        condition(negate(above(-51)),condition(floor,sequence([
            condition(threshold('inclusions',0.30),block('alfheim:livingrock_slag')),
            block('alfheim:magmatic_livingrock')]))),
        condition(negate(above(-45)),condition(floor,block('alfheim:cracked_livingrock'))),
        sequence(zones)])
    geology=condition(above(c['geology_y'][0]),condition(negate(above(c['geology_y'][1])),
        condition(negate({'type':'minecraft:biome','biome_is':VOID_IDS}),geology)))
    # Bedrock still runs first; biome and surface rules are byte-for-byte retained.
    surface['before_biomes']=sequence([surface_rule(),surface['before_biomes'],geology])
    emit('mythicbotany/libx/surface_rule_set/alfheim_surface.json',surface)
    # Surface material replacement happens before underground_ores. The ordinary
    # features remain unchanged, while these additions can replace only library rock.
    placed=[]
    for bloom in c['blooms']:
        id='deepworks/ore_'+bloom
        emit('alfheim/worldgen/configured_feature/'+id+'.json',{
            'type':'minecraft:ore','config':{'size':c['ore_size'],'discard_chance_on_air_exposure':0,
                'targets':[{'target':{'predicate_type':'minecraft:tag_match','tag':'alfheim:livingrock_natural'},
                            'state':{'Name':'alfheim:'+bloom+'_ore'}}]}})
        emit('alfheim/worldgen/placed_feature/'+id+'.json',{'feature':'alfheim:'+id,'placement':[
            {'type':'minecraft:count','count':c['ore_attempts']},{'type':'minecraft:in_square'},
            {'type':'minecraft:height_range','height':{'type':'minecraft:trapezoid',
                'min_inclusive':{'absolute':c['ore_y'][0]},'max_inclusive':{'absolute':c['ore_y'][1]},'plateau':16}},
            {'type':'minecraft:biome'}]})
        placed.append('alfheim:'+id)
    emit('alfheim/forge/biome_modifier/deepworks_ores.json',{'type':'forge:add_features',
        'biomes':'#alfheim:deepworks_land','features':placed,'step':'underground_ores'})
    # Explicitly exclude the Void Verge; the home tag is shared with its islands.
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
