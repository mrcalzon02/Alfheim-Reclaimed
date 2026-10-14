"""Bounded worked fields, void-edge courts and thorny undergrowth.

Changes decoration and structure placement only. No terrain density, climate,
aquifer or biome-selection file is written.
"""
import json
import math
from pathlib import Path
from structure_nbt import Piece
import nbt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'kubejs/data/alfheim'


def B(name, **props):
    return name, {k: str(v).lower() for k,v in props.items()} or None


def emit(path, obj):
    target = DATA / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def golden_field():
    p = Piece(39, 10, 39)
    c = 19
    for x in range(39):
        for z in range(39):
            d = math.hypot(x-c,z-c)
            if d > 18: continue
            for y in range(4):
                if d <= 17 + y/3:
                    p.set(x,y,z,B('alfheim:ivory_livingrock_bricks' if y==3 else 'alfheim:rootbound_livingrock'))
            if d > 16.5:
                p.set(x,4,z,B('alfheim:ivory_livingrock_slab',type='bottom',waterlogged=False))
            elif abs(x-c)<=1 or abs(z-c)<=1:
                p.set(x,4,z,B('minecraft:dirt_path'))
            elif d < 15 and (x//5+z//5)%3 != 0:
                p.set(x,4,z,B('minecraft:farmland',moisture=7))
                p.set(x,5,z,B('minecraft:wheat',age=7))
            else:
                p.set(x,4,z,B('minecraft:coarse_dirt' if (x+z)%7==0 else 'minecraft:dirt_path'))
    for dx,dz,facing in ((0,-1,'south'),(0,1,'north'),(-1,0,'east'),(1,0,'west')):
        for step in range(4):
            for width in (-1,0,1):
                x=c+dx*(18-step)+(width if dz else 0)
                z=c+dz*(18-step)+(width if dx else 0)
                p.set(x,step+1,z,B('alfheim:ivory_livingrock_stairs',facing=facing,half='bottom',shape='straight',waterlogged=False))
                for yy in range(step+2,7): p.set(x,yy,z,B('minecraft:air'))
    return p


def edge_court(kind):
    p = Piece(31, 20, 31)
    c = 15
    for x in range(31):
        for z in range(31):
            d = math.hypot(x-c,z-c)
            if d > 13: continue
            p.set(x,0,z,B('alfheim:abyssal_livingrock'))
            p.set(x,1,z,B('alfheim:gloam_livingrock_polished'))
            if d > 11.5 and (x+z)%5:
                p.set(x,2,z,B('alfheim:gloam_livingrock_wall'))
    if kind == 'thorn_gate':
        for z in (8,15,22):
            for x in (10,20):
                for y in range(2,10): p.set(x,y,z,B('alfheim:gloam_livingrock_bricks'))
            for x in range(10,21):
                p.set(x,10+min(x-10,20-x)//2,z,B('alfheim:gloam_livingrock_bricks'))
        for x,z in ((7,6),(23,7),(7,23),(23,24),(5,15),(25,15)):
            p.set(x,2,z,B('alfheim:bramble'))
    else:
        for k in range(8):
            a=k*math.tau/8
            x,z=round(c+math.cos(a)*8),round(c+math.sin(a)*8)
            for y in range(2,5+k%3):p.set(x,y,z,B('alfheim:ivory_livingrock_carved'))
        for x in range(13,18):
            for z in range(13,18):p.set(x,2,z,B('alfheim:moonstone_livingrock_polished'))
        p.set(c,3,c,B('alfheim_leyworks:memorial_urn',facing='north'))
    return p


def structure(name, piece, biomes):
    path=DATA/'structures/field_review'/f'{name}.nbt'
    path.parent.mkdir(parents=True, exist_ok=True)
    nbt.save(str(path), '', piece.to_nbt())
    emit(f'worldgen/template_pool/field_review/{name}.json', {
        'name':f'alfheim:field_review/{name}','fallback':'minecraft:empty',
        'elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element',
            'location':f'alfheim:field_review/{name}','projection':'rigid','processors':'minecraft:empty'}}]})
    emit(f'worldgen/structure/{name}.json', {
        'type':'minecraft:jigsaw','biomes':biomes,'step':'surface_structures',
        'terrain_adaptation':'beard_thin','spawn_overrides':{},
        'start_pool':f'alfheim:field_review/{name}','size':1,
        'start_height':{'absolute':-2},'project_start_to_heightmap':'WORLD_SURFACE_WG',
        'max_distance_from_center':40,'use_expansion_hack':False})


def main():
    structure('golden_field_dais', golden_field(), ['mythicbotany:golden_fields'])
    emit('worldgen/structure_set/golden_field_dais.json', {
        'structures':[{'structure':'alfheim:golden_field_dais','weight':1}],
        'placement':{'type':'minecraft:random_spread','spacing':10,'separation':5,'salt':101220261}})
    for name in ('thorn_gate','shore_memorial_court'):
        structure(name,edge_court(name),['alfheim:void_verge','alfheim:void_shore'])
    emit('worldgen/structure_set/void_edge_courts.json',{
        'structures':[{'structure':f'alfheim:{name}','weight':1}
                      for name in ('thorn_gate','shore_memorial_court')],
        'placement':{'type':'minecraft:random_spread','spacing':12,'separation':6,'salt':101220262}})
    predicate={'type':'minecraft:all_of','predicates':[
        {'type':'minecraft:matching_blocks','blocks':['minecraft:air']},
        {'type':'minecraft:matching_blocks','blocks':['minecraft:grass_block','minecraft:dirt',
            'minecraft:coarse_dirt','alfheim:abyssal_livingrock','alfheim:gloam_livingrock',
            'alfheim:ivory_livingrock','alfheim:tide_livingrock','alfheim:cracked_livingrock',
            'alfheim:riftchalk_livingrock','alfheim:riftshale_livingrock',
            'minecraft:sand','minecraft:gravel'],
         'offset':[0,-1,0]}]}
    for name,block in (('void_bramble','alfheim:bramble'),('void_thornbush','mmorpg:thorn_bush')):
        emit(f'worldgen/configured_feature/{name}.json',{
            'type':'minecraft:random_patch','config':{'tries':20,'xz_spread':6,'y_spread':2,
                'feature':{'feature':{'type':'minecraft:simple_block','config':{'to_place':{
                    'type':'minecraft:simple_state_provider','state':{'Name':block}}}},
                    'placement':[{'type':'minecraft:block_predicate_filter','predicate':predicate}]}}})
        emit(f'worldgen/placed_feature/{name}.json',{'feature':f'alfheim:{name}', 'placement':[
            {'type':'minecraft:count','count':3},{'type':'minecraft:in_square'},
            {'type':'minecraft:heightmap','heightmap':'WORLD_SURFACE_WG'},{'type':'minecraft:biome'}]})
        emit(f'forge/biome_modifier/zz_void_{name}.json',{'type':'forge:add_features',
            'biomes':['alfheim:void_verge','alfheim:void_shore'],'features':f'alfheim:{name}',
            'step':'vegetal_decoration'})
    asset=ROOT/'kubejs/assets/alfheim/models/block/bramble.json'
    asset.parent.mkdir(parents=True,exist_ok=True)
    asset.write_text(json.dumps({'parent':'minecraft:block/cross',
        'textures':{'cross':'minecraft:block/sweet_berry_bush_stage2'}})+'\n')
    startup=ROOT/'kubejs/startup_scripts/28_field_review_plants.js'
    startup.write_text("// GENERATED by tools/gen_field_review_features.py\n"
        "StartupEvents.registry('block', event => {\n"
        "  event.create('alfheim:bramble').displayName('Bramble Thicket')\n"
        "    .model('alfheim:block/bramble').renderType('cutout').soundType('grass')\n"
        "    .fullBlock(false).notSolid().hardness(0.4).box(2, 0, 2, 14, 12, 14)\n"
        "    .tagBlock('minecraft:mineable/axe')\n"
        "})\n",encoding='utf-8')
    print('Generated three bounded structures and two void-edge plant features')


if __name__=='__main__': main()
