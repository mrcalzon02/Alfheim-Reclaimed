"""Small supported shore decorations; never writes density, surfaces or biomes."""
import argparse,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GROUND=['minecraft:grass_block','minecraft:dirt','minecraft:coarse_dirt','minecraft:podzol',
        'minecraft:mycelium','minecraft:rooted_dirt','minecraft:sand','minecraft:gravel',
        'botania:livingrock']+['alfheim:'+n+'_livingrock' for n in (
        'tide','storm','rootbound','moss','amber','fern','frost','silvermist','moonstone',
        'amethyst','gloam','ivory','abyssal','riftchalk','riftshale')]
SPECS={
    'mistbark_stone_scatter':('alfheim:mistbark_shore',9),
    'void_shore_wrack':('alfheim:void_shore',13),
}

def supported(hosts):
    return {'type':'minecraft:all_of','predicates':[
        {'type':'minecraft:matching_blocks','blocks':['minecraft:air']},
        {'type':'minecraft:matching_blocks','blocks':hosts,'offset':[0,-1,0]}]}

def weighted(states):
    return {'type':'minecraft:weighted_state_provider','entries':[
        {'data':state,'weight':weight} for state,weight in states]}

def patch(feature,hosts,tries,spread,y=0):
    return {'type':'minecraft:random_patch','config':{'tries':tries,'xz_spread':spread,'y_spread':y,
        'feature':{'feature':feature,'placement':[
            {'type':'minecraft:block_predicate_filter','predicate':supported(hosts)}]}}}

def horizontal(materials,hosts,lo,hi):
    """Every cell, not just the origin, requires air over native support."""
    options=[]
    for direction,axis in (('east','x'),('south','z')):
        states=[({'Name':name,**({'Properties':{'axis':axis}} if name.endswith('_log') else {})},weight)
                for name,weight in materials]
        options.append({'feature':{'type':'minecraft:block_column','config':{
            'direction':direction,'allowed_placement':supported(hosts),'prioritize_tip':False,
            'layers':[{'height':{'type':'minecraft:uniform','value':{'min_inclusive':lo,'max_inclusive':hi}},
                       'provider':weighted(states)}]}},'placement':[]})
    return {'type':'minecraft:simple_random_selector','config':{'features':options}}

def driftwood():
    # Select a whole trunk's species first; a single fallen trunk cannot alternate woods.
    options=[]
    for log,weight in (('alfheim:gloambark_log',4),('alfheim:hushbark_log',3)):
        choice={'feature':horizontal([(log,1)],GROUND,2,4),'placement':[]}
        options.extend([choice]*weight)
    return patch({'type':'minecraft:simple_random_selector','config':{'features':options}},GROUND,2,5,1)

def build():
    coast=['minecraft:sand','minecraft:gravel']+['alfheim:'+n+'_livingrock' for n in (
        'riftchalk','riftshale','tide','ivory','frost','gloam','abyssal')]
    mist=['minecraft:grass_block','minecraft:dirt','minecraft:podzol','minecraft:sand','minecraft:gravel']+[
        'alfheim:'+n+'_livingrock' for n in ('tide','frost','silvermist','fern','moonstone')]
    configured={
        'shore_driftwood':driftwood(),
        'mistbark_stone_scatter':patch({'type':'minecraft:simple_block','config':{'to_place':weighted([
            ({'Name':'alfheim:silvermist_livingrock'},3),({'Name':'alfheim:frost_livingrock'},2)])}},mist,5,3,1),
        'void_shore_wrack':patch(horizontal([('alfheim:riftchalk_livingrock',2),
                                           ('alfheim:riftshale_livingrock',3)],coast,1,3),coast,2,3),
    }
    out={}
    def emit(relative,doc):out['kubejs/data/alfheim/'+relative]=(json.dumps(doc,indent=2)+'\n').encode()
    for name,doc in configured.items():emit(f'worldgen/configured_feature/{name}.json',doc)
    for name,(biome,chance) in SPECS.items():
        emit(f'worldgen/placed_feature/{name}.json',{'feature':'alfheim:'+name,'placement':[
            {'type':'minecraft:rarity_filter','chance':chance},{'type':'minecraft:in_square'},
            {'type':'minecraft:heightmap','heightmap':'WORLD_SURFACE_WG'},{'type':'minecraft:biome'}]})
        emit(f'forge/biome_modifier/shore_{name}.json',{'type':'forge:add_features',
            'biomes':[biome],'features':'alfheim:'+name,'step':'vegetal_decoration'})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    for relative,content in build().items():
        path=ROOT/relative
        if args.check:assert path.read_bytes()==content,relative
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
    print('SHORE DETAILS:',len(build()),'files', 'byte-identical' if args.check else 'generated')

if __name__=='__main__':main()
