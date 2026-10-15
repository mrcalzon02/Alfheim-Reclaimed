"""Guard a native feature's placement; keep its configured contents and rewards."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH='kubejs/data/mythicbotany/worldgen/placed_feature/abandoned_apothecaries.json'

def predicate():
    return {'type':'minecraft:all_of','predicates':[
        {'type':'minecraft:matching_blocks','blocks':['minecraft:air']},
        {'type':'minecraft:any_of','predicates':[
            {'type':'minecraft:matching_blocks','blocks':['minecraft:grass_block','minecraft:dirt',
                'minecraft:coarse_dirt','minecraft:podzol','minecraft:mycelium','minecraft:rooted_dirt',
                'minecraft:mud','minecraft:sand','minecraft:gravel','botania:livingrock'],'offset':[0,-1,0]},
            *[{'type':'minecraft:matching_block_tag','tag':'alfheim:'+tag,'offset':[0,-1,0]}
              for tag in ('livingrock_natural','void_natural')]]}]}

def placement():
    return {'feature':'mythicbotany:abandoned_apothecaries','placement':[
        {'type':'minecraft:count','count':1},{'type':'minecraft:rarity_filter','chance':20},
        {'type':'minecraft:in_square'},{'type':'mythicbotany:alfheim_ground'},
        {'type':'minecraft:block_predicate_filter','predicate':predicate()},{'type':'minecraft:biome'}]}

def build():return {PATH:(json.dumps(placement(),indent=2)+'\n').encode()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    for relative,data in build().items():
        path=ROOT/relative
        if args.check:assert path.read_bytes()==data,relative
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print('NATIVE FEATURE GUARD:', 'byte-identical' if args.check else 'generated; native configured feature unchanged')

if __name__=='__main__':main()
