"""Connected caravan/customs transport precinct, with an authored dry-cut bridge."""
import argparse
import json
from pathlib import Path
from district_policy import apply as district_policy
import nbt
from district_refit import detail_nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,bed,elven_remains,skeletal_remains,stone_debris,HOME_BIOMES
from gen_elder_lineage import royal,bench,desk,mounted_banner,lift,STONE,CARVED,FLOOR,AIR,DEPTH

ROOT=Path(__file__).resolve().parents[1]
SIZES={'caravan_court':(47,26,47),'processional_avenue':(47,20,39),
       'bridge_gate':(47,26,31),'freight_exchange':(39,26,47),
       'custom_house':(39,26,47),'bonded_store':(39,24,31),
       'road_checkpoint':(47,20,31),'wayshrine_rest':(31,24,31),
       'refugee_lodge':(39,24,31),'road_approach':(23,14,32)}
LINKS={'caravan_court':{'north':'processional_avenue','east':'freight_exchange','west':'custom_house','south':'road_checkpoint'},
       'processional_avenue':{'north':'bridge_gate'},
       'custom_house':{'north':'bonded_store'},
       'road_checkpoint':{'west':'wayshrine_rest','east':'refugee_lodge','north':'road_approach'}}

def cart(p,x,z):
    box(p,x,1,z,x+4,1,z+5,B('botania:dreamwood_planks'))
    for xx in (x-1,x+5):
        for zz in (z,z+5):p.set(xx,1,zz,CARVED)

def build(name):
    sx,sy,sz=SIZES[name];cx=sx//2;p=Piece(sx,sy,sz)
    box(p,0,1,0,sx-1,sy-1,sz-1,AIR);box(p,0,0,0,sx-1,0,sz-1,FLOOR)
    if name in ('freight_exchange','custom_house','bonded_store','wayshrine_rest','refugee_lodge'):
        for x in (1,sx-2):box(p,x,1,1,x,13,sz-2,STONE)
        for z in (1,sz-2):box(p,1,1,z,sx-2,13,z,STONE)
        for z in range(5,sz-3,8):
            for x in range(2,sx-2):
                if not (name=='freight_exchange' and z>29 and x>cx):p.set(x,15+min(5,x//3,(sx-1-x)//3),z,B('botania:dreamwood_log',axis='x'))
    if name=='caravan_court':
        for z in (7,36):
            for x in (5,16,30,41):box(p,x,1,z,x,9,z,STONE)
            box(p,5,10,z,16,10,z,B('botania:dreamwood_log',axis='x'))
            box(p,30,10,z,41,10,z,B('botania:dreamwood_log',axis='x'))
        cart(p,7,12);cart(p,33,28)
        desk(p,5,30);desk(p,35,14)
        for x in (8,36):bed(p,x,1,40,'brown')
        elven_remains(p,12,1,32,20261400)
    elif name=='processional_avenue':
        for z in (5,17,32):
            for x in (8,38):box(p,x,1,z,x,6,z,CARVED)
        cart(p,31,9)
        box(p,4,0,24,15,0,34,B('minecraft:coarse_dirt'))
        for z in (26,31):skeletal_remains(p,7,1,z,20261401+z,cloth=True)
        # Root damage beside the lane; the transport axis survives.
        box(p,36,1,29,41,1,29,B('botania:dreamwood_log',axis='x'))
    elif name=='bridge_gate':
        for x in (15,31):box(p,x,1,5,x,12,5,STONE)
        box(p,15,13,5,31,13,5,CARVED)
        mounted_banner(p,14,5,6,'south');mounted_banner(p,32,5,6,'south')
        desk(p,5,7);elven_remains(p,36,1,7,20261402,role='warden')
    elif name=='freight_exchange':
        for x in (5,27):
            for z in (7,31):
                box(p,x,1,z,x+6,2,z+3,B('botania:dreamwood_planks'))
                box(p,x,1,z+8,x,10,z+8,CARVED)
                box(p,x,11,z+8,x+5,11,z+8,B('botania:dreamwood_log',axis='x'))
        cart(p,5,21);desk(p,29,22)
        stone_debris(p,30,1,41,20261403,3);elven_remains(p,8,1,40,20261404)
    elif name=='custom_house':
        for z in (7,15,31,39):desk(p,5,z);royal(p,31,1,z,'royal_tall_cabinet')
        box(p,27,1,18,35,5,18,STONE)
        mounted_banner(p,5,5,44,'north');elven_remains(p,29,1,35,20261405)
    elif name=='bonded_store':
        for x in (5,27):
            for z in (7,22):box(p,x,1,z,x+6,2,z+3,B('botania:dreamwood_planks'))
        box(p,26,1,20,35,6,20,STONE)
        desk(p,5,15);elven_remains(p,29,1,17,20261406)
    elif name=='road_checkpoint':
        for x in (6,17,29,40):box(p,x,1,7,x,8,7,CARVED)
        for x0,x1 in ((4,20),(26,42)):box(p,x0,1,9,x1,3,9,STONE)
        mounted_banner(p,8,5,24,'north');mounted_banner(p,38,5,24,'north')
        desk(p,5,24);elven_remains(p,34,1,24,20261407,role='warden')
    elif name=='wayshrine_rest':
        for x in (5,24):
            for dy,part in enumerate(('base','mid','crown')):royal(p,x,1+dy,7,'royal_lineage_stele_'+part)
        bench(p,5,16);bench(p,23,16)
        for x in (5,24):bed(p,x,1,24,'brown')
        desk(p,5,21);elven_remains(p,23,1,21,20261408)
    elif name=='refugee_lodge':
        for x in (5,11,27,33):
            for z in (6,15,24):bed(p,x,1,z,'brown')
        for z in (10,22):bench(p,5,z);royal(p,31,1,z,'royal_tall_cabinet')
        elven_remains(p,29,1,19,20261409)
    else:
        for z in range(sz):
            for x in (cx-2,cx+2):p.set(x,0,z,CARVED)
        for x in (4,18):box(p,x,1,5,x,7,5,STONE)
    box(p,cx-2,1,0,cx+2,4,sz-1,AIR)
    if name in ('caravan_court','road_checkpoint'):box(p,0,1,sz//2-2,sx-1,4,sz//2+2,AIR)
    p.set(7,1,10,B('minecraft:barrel',facing='up',open=False),{'id':'minecraft:barrel','CustomName':json.dumps({'text':'Trade '+name}),'LootTable':'alfheim:chests/trade/'+('records' if name in ('custom_house','bonded_store','bridge_gate','road_checkpoint') else 'cargo')})
    def socket(face,target,child):
        x,z={'north':(cx,0),'south':(cx,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]
        p.jigsaw(x,1,z,'alfheim:'+target,'alfheim:'+target,'minecraft:empty' if child is None else 'alfheim:ancient/roads_trade/'+child,face+'_up',joint='aligned')
    if name!='caravan_court':socket('south',name+'_in',None)
    for face,child in LINKS.get(name,{}).items():socket(face,child+'_in',child)
    out=lift(p)
    if name=='bridge_gate':
        # Dry channel and ruined outer span are wholly authored, never a terrain carve.
        box(out,2,DEPTH-4,14,44,DEPTH+1,24,AIR)
        box(out,19,DEPTH,14,27,DEPTH,24,FLOOR)
        for x in (19,27):
            for z in (14,24):box(out,x,DEPTH-4,z,x,DEPTH-1,z,STONE)
        for x in (18,28):
            for z in range(14,25):
                out.set(x,DEPTH,z,CARVED)
                out.set(x,DEPTH+1,z,B('minecraft:oak_fence',north=z>14,south=z<24,east=False,west=False,waterlogged=False))
    return out

def generate(root=ROOT):
    data=root/'kubejs/data/alfheim';files=[]
    def emit(path,value):
        value=district_policy(path,value)
        p=data/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');files.append(p)
    for name in SIZES:
        p=data/'structures/ancient/roads_trade'/f'{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True);nbt.save(str(p),'',detail_nbt(build(name), 'roads_trade', name));files.append(p)
        emit(f'worldgen/template_pool/ancient/roads_trade/{name}.json',{'name':'alfheim:ancient/roads_trade/'+name,'fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'alfheim:ancient/roads_trade/'+name,'projection':'rigid','processors':'minecraft:empty'}}]})
    emit('worldgen/structure/roads_trade.json',{'type':'minecraft:jigsaw','biomes':'#alfheim:has_roads_trade','step':'surface_structures','terrain_adaptation':'beard_thin','spawn_overrides':{},'start_pool':'alfheim:ancient/roads_trade/caravan_court','size':3,'start_height':{'absolute':-DEPTH},'project_start_to_heightmap':'WORLD_SURFACE_WG','max_distance_from_center':116,'use_expansion_hack':False})
    emit('worldgen/structure_set/roads_trade.json',{'structures':[{'structure':'alfheim:roads_trade','weight':1}],'placement':{'type':'minecraft:random_spread','spacing':56,'separation':32,'salt':101220269}})
    emit('tags/worldgen/biome/has_roads_trade.json',{'replace':False,'values':HOME_BIOMES})
    for table,entries in {'records':[('minecraft:paper',6),('minecraft:book',4),('minecraft:ink_sac',2)],'cargo':[('minecraft:bread',3),('minecraft:white_wool',3),('minecraft:clay_ball',2),('minecraft:apple',2)]}.items():
        emit(f'loot_tables/chests/trade/{table}.json',{'type':'minecraft:chest','pools':[{'rolls':{'type':'minecraft:uniform','min':2,'max':4},'entries':[{'type':'minecraft:item','name':item,'weight':weight,'functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':1,'max':3}}]} for item,weight in entries]}]})
    return files

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-root',default=str(ROOT));args=ap.parse_args();print(f'Roads / Trade: {len(generate(Path(args.output_root).resolve()))} files')
