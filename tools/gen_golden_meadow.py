"""Replace the native floor-overwriting wheat decorator with soil-only meadow grass.

Worked crops remain in the existing bounded golden_field_dais structure. This
tool writes decoration only, never noise, biome selection or surface rules.
"""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def build():
    out={}
    def emit(path,value):out['kubejs/data/alfheim/'+path]=(json.dumps(value,indent=2)+'\n').encode()
    emit('forge/biome_modifier/golden_meadow_remove_wheat.json',{
        'type':'forge:remove_features','biomes':['mythicbotany:golden_fields'],
        'features':['mythicbotany:wheat_fields'],'steps':['vegetal_decoration']})
    emit('worldgen/configured_feature/golden_meadow_grass.json',{
        'type':'minecraft:random_patch','config':{'tries':24,'xz_spread':7,'y_spread':2,
            'feature':{'feature':{'type':'minecraft:simple_block','config':{'to_place':{
                'type':'minecraft:weighted_state_provider','entries':[
                    {'data':{'Name':name},'weight':weight} for name,weight in (
                        ('minecraft:grass',8),('minecraft:fern',1),('minecraft:dandelion',1))]}}},
                'placement':[{'type':'minecraft:block_predicate_filter','predicate':{
                    'type':'minecraft:all_of','predicates':[
                        {'type':'minecraft:matching_blocks','blocks':['minecraft:air']},
                        {'type':'minecraft:matching_blocks','blocks':['minecraft:grass_block','minecraft:dirt'],
                         'offset':[0,-1,0]}]}}]}}})
    emit('worldgen/placed_feature/golden_meadow_grass.json',{'feature':'alfheim:golden_meadow_grass','placement':[
        {'type':'minecraft:count','count':2},{'type':'minecraft:in_square'},
        {'type':'minecraft:heightmap','heightmap':'WORLD_SURFACE_WG'},{'type':'minecraft:biome'}]})
    emit('forge/biome_modifier/golden_meadow_grass.json',{'type':'forge:add_features',
        'biomes':['mythicbotany:golden_fields'],'features':'alfheim:golden_meadow_grass','step':'vegetal_decoration'})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    for relative,data in build().items():
        path=ROOT/relative
        if args.check:assert path.read_bytes()==data,relative
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print('GOLDEN MEADOW:',len(build()),'files', 'byte-identical' if args.check else 'generated')

if __name__=='__main__':main()
