"""Remote elven stewardship retreat, adapted into a final wilderness refuge."""
import argparse
import json
from pathlib import Path
import nbt
from district_refit import detail_nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,bed,elven_remains,HOME_BIOMES
from gen_elder_lineage import royal,bench,desk,canopy_bed,lift,STONE,CARVED,FLOOR,AIR,DEPTH

ROOT=Path(__file__).resolve().parents[1]
SIZES={'green_noble_lodge':(47,30,47),'surveyor_tower':(31,38,31),
       'forest_waystation':(39,24,31),'outlying_retreat_hall':(39,28,39),
       'moon_pool_sanctuary':(39,18,39),'wild_ward_shrine':(31,22,31)}
LINKS={'green_noble_lodge':{'north':'surveyor_tower','west':'forest_waystation',
                         'east':'outlying_retreat_hall','south':'moon_pool_sanctuary'},
       'moon_pool_sanctuary':{'north':'wild_ward_shrine'}}

def build(name):
    sx,sy,sz=SIZES[name];cx=sx//2;p=Piece(sx,sy,sz)
    box(p,0,0,0,sx-1,0,sz-1,FLOOR);box(p,0,1,0,sx-1,sy-1,sz-1,AIR)
    enclosed=name in ('green_noble_lodge','surveyor_tower','outlying_retreat_hall')
    height=25 if name=='surveyor_tower' else 11
    if enclosed:
        for x in (1,sx-2):box(p,x,1,1,x,height,sz-2,STONE)
        for z in (1,sz-2):box(p,1,1,z,sx-2,height,z,STONE)
        for z in range(7,sz-5,8):
            for x in (1,sx-2):box(p,x,4,z,x,7,z+1,B('botania:elf_glass'))
        # Long-lived modular timber ribs; the far canopy has fallen away.
        for z in range(5,sz-4,8):
            for x in range(2,sx-2):
                if z<sz//2 or x<cx:p.set(x,13+min(6,x//3,(sx-1-x)//3),z,B('botania:dreamwood_log',axis='x'))
    else:
        for x in (2,sx-3):
            for z in (4,sz-5):box(p,x,1,z,x,6,z,CARVED)
    # Paired inactive mana/source service channels beside the main walking lane.
    for z in range(3,sz-3):
        p.set(cx-4,0,z,B('alfheim:moonstone_livingrock_polished'))
        p.set(cx+4,0,z,B('ars_nouveau:sourcestone'))
    if name=='green_noble_lodge':
        canopy_bed(p,6,7);desk(p,34,8)
        for x in (5,11,34,40):
            for z in (29,37):bed(p,x,1,z,'green')
        for z in (17,25):bench(p,7,z);royal(p,37,1,z,'royal_tall_cabinet')
        # Broken service partition and sheltered last meal, not a ceremonial empty hall.
        box(p,4,1,23,15,1,23,B('botania:dreamwood_planks'))
        elven_remains(p,11,1,20,20261341,role='healer')
    elif name=='surveyor_tower':
        for k in range(14):
            box(p,4,1,7+k,6,k+1,7+k,STONE)
            for x in range(4,7):p.set(x,k+1,7+k,B('alfheim:ivory_livingrock_stairs',facing='south',half='bottom',shape='straight',waterlogged=False))
        box(p,4,15,21,24,15,26,FLOOR)
        for x in (4,24):box(p,x,16,21,x,18,26,CARVED)
        # Unpowered weather/survey instrument in the surviving part of the platform.
        box(p,21,16,24,21,20,24,B('botania:dreamwood_log',axis='y'))
        p.set(21,21,24,B('botania:elf_glass'));desk(p,19,8)
        elven_remains(p,20,1,18,20261342)
    elif name=='forest_waystation':
        for x in (4,13,25,34):box(p,x,1,5,x,8,5,B('botania:dreamwood_log',axis='y'))
        box(p,4,9,4,34,9,10,B('botania:dreamwood_planks'))
        for x in (5,29):bed(p,x,1,7,'green');desk(p,x,14)
        for x in (6,29):
            p.set(x,0,24,AIR);p.set(x,1,25,CARVED)
            elven_remains(p,x,0,24,20261343+x)
        p.set(5,1,20,B('minecraft:moss_carpet'));p.set(33,1,19,B('minecraft:moss_carpet'))
    elif name=='outlying_retreat_hall':
        for x in (5,11):
            for z in (7,15,27):bed(p,x,1,z,'white')
        for z in range(5,20):p.set(34,1,z,B('minecraft:bookshelf'))
        box(p,32,1,4,32,5,20,STONE)
        desk(p,27,7);royal(p,28,1,18,'royal_tall_cabinet')
        for x in range(27,34):
            for z in range(24,31):
                p.set(x,0,z,B('minecraft:farmland',moisture=7));p.set(x,1,z,B('minecraft:wheat',age=7))
        p.set(30,0,27,B('minecraft:water',level=0));p.set(30,1,27,AIR)
        elven_remains(p,7,1,31,20261344)
    elif name=='moon_pool_sanctuary':
        for x in (4,33):bed(p,x,1,5,'white')
        bench(p,5,33);bench(p,29,33)
        for x in (4,34):
            box(p,x,1,30,x,5,30,B('botania:dreamwood_log',axis='y'))
    else:
        for x,z in ((6,7),(24,7),(6,23),(24,23)):
            for dy,part in enumerate(('base','mid','crown')):
                if (x,z)!=(24,23) or dy<1:royal(p,x,1+dy,z,'royal_lineage_stele_'+part)
        for x in (8,20):bed(p,x,1,15,'green')
        desk(p,5,19);elven_remains(p,23,1,18,20261345)
        p.set(25,1,24,B('alfheim:moonstone_livingrock_carved'))
    box(p,cx-2,1,0,cx+2,4,sz-1,AIR)
    if name=='green_noble_lodge':box(p,0,1,sz//2-2,sx-1,4,sz//2+2,AIR)
    p.set(7,1,10,B('minecraft:barrel',facing='up',open=False),{'id':'minecraft:barrel',
        'CustomName':json.dumps({'text':'Frontier '+name}),
        'LootTable':'alfheim:chests/frontier/'+('records' if name in ('surveyor_tower','outlying_retreat_hall') else 'supplies')})
    def socket(face,child,incoming=False):
        x,z={'north':(cx,0),'south':(cx,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]
        target=(name if incoming else child)+'_in'
        p.jigsaw(x,1,z,'alfheim:'+target,'alfheim:'+target,'minecraft:empty' if incoming else 'alfheim:ancient/frontier_stewardship/'+child,face+'_up',joint='aligned')
    if name!='green_noble_lodge':socket('south',None,True)
    for face,child in LINKS.get(name,{}).items():socket(face,child)
    out=lift(p)
    if name=='moon_pool_sanctuary':
        for x0,x1 in ((6,12),(26,32)):
            box(out,x0,6,11,x1,7,27,B('minecraft:water',level=0))
            box(out,x0,8,11,x1,8,27,AIR)
            for x in (x0-1,x1+1):
                for z in range(10,29):out.set(x,9,z,B('minecraft:oak_fence',north=z>10,south=z<28,east=False,west=False,waterlogged=False))
    return out

def generate(root=ROOT):
    data=root/'kubejs/data/alfheim';files=[]
    def emit(path,value):
        p=data/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');files.append(p)
    for name in SIZES:
        p=data/'structures/ancient/frontier_stewardship'/f'{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True);nbt.save(str(p),'',detail_nbt(build(name), 'frontier_stewardship', name));files.append(p)
        emit(f'worldgen/template_pool/ancient/frontier_stewardship/{name}.json',{'name':'alfheim:ancient/frontier_stewardship/'+name,'fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'alfheim:ancient/frontier_stewardship/'+name,'projection':'rigid','processors':'minecraft:empty'}}]})
    emit('worldgen/structure/frontier_stewardship.json',{'type':'minecraft:jigsaw','biomes':'#alfheim:has_frontier_stewardship','step':'surface_structures','terrain_adaptation':'beard_thin','spawn_overrides':{},'start_pool':'alfheim:ancient/frontier_stewardship/green_noble_lodge','size':3,'start_height':{'absolute':-DEPTH},'project_start_to_heightmap':'WORLD_SURFACE_WG','max_distance_from_center':116,'use_expansion_hack':False})
    emit('tags/worldgen/biome/has_frontier_stewardship.json',{'replace':False,'values':HOME_BIOMES})
    for table,items in {'records':['minecraft:paper','minecraft:book','minecraft:ink_sac'],'supplies':['minecraft:bread','minecraft:white_wool','minecraft:wheat_seeds']}.items():
        emit(f'loot_tables/chests/frontier/{table}.json',{'type':'minecraft:chest','pools':[{'rolls':2,'entries':[{'type':'minecraft:item','name':item} for item in items]}]})
    return files

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-root',default=str(ROOT));args=ap.parse_args()
    print('frontier_stewardship:',len(generate(Path(args.output_root).resolve())),'files')
