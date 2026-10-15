"""Connected civic government, archives and emergency public services."""
import argparse
import json
from pathlib import Path
import nbt
from district_refit import detail_nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,bed,elven_remains,stone_debris,HOME_BIOMES
from gen_elder_lineage import royal,bench,desk,mounted_banner,lift,STONE,CARVED,FLOOR,AIR,DEPTH

ROOT=Path(__file__).resolve().parents[1]
SIZES={'assembly_hall':(47,32,47),'record_house':(39,25,47),
       'council_house':(39,25,47),'public_forum':(47,18,40),
       'market_court':(47,18,32),'service_court':(47,18,32),
       'census_hall':(39,22,31),'public_kitchen':(39,22,31),
       'processional_avenue':(23,14,32)}
LINKS={'assembly_hall':{'east':'record_house','west':'council_house',
                      'north':'public_forum','south':'service_court'},
       'public_forum':{'north':'market_court'},
       'service_court':{'west':'census_hall','east':'public_kitchen','north':'processional_avenue'}}

def build(name):
    sx,sy,sz=SIZES[name];cx=sx//2;p=Piece(sx,sy,sz)
    box(p,0,1,0,sx-1,sy-1,sz-1,AIR)
    box(p,0,0,0,sx-1,0,sz-1,FLOOR)
    enclosed=name in ('assembly_hall','record_house','council_house','census_hall','public_kitchen')
    if enclosed:
        for x in (1,sx-2):box(p,x,1,1,x,13,sz-2,STONE)
        for z in (1,sz-2):box(p,1,1,z,sx-2,13,z,STONE)
        for z in range(7,sz-7,8):
            for x in (1,sx-2):box(p,x,5,z,x,9,z+2,B('botania:elf_glass'))
        # Interrupted roof beams leave deliberate air above the usable rooms.
        for z in range(5,sz-4,8):
            for x in range(2,sx-2):
                if not (z==21 and x>sx//2):p.set(x,15+min(7,x//3,(sx-1-x)//3),z,B('botania:dreamwood_log',axis='x'))
    else:
        for x in (3,sx-4):
            for z in (5,sz-6):box(p,x,1,z,x,8,z,CARVED)
    if name=='assembly_hall':
        for z in (9,15,29,35):
            for x in (7,12,32,37):bench(p,x,z)
        box(p,15,0,5,31,0,7,CARVED)
        desk(p,17,6);desk(p,28,6)
        for x in (7,38):
            mounted_banner(p,x,6,44,'north')
            for z in (18,32):bed(p,x,1,z,'purple')
        # Broken barricade on the speaker dais, with a surviving central opening.
        for x in (15,16,17,29,30,31):p.set(x,1,8,B('botania:dreamwood_planks'))
        elven_remains(p,11,1,11,20261040)
        stone_debris(p,35,1,39,20261041,3)
    elif name=='record_house':
        for x in (5,10,28,33):
            for z in range(5,39,4):
                if not (x==10 and z>24):box(p,x,1,z,x,4,z+1,B('minecraft:bookshelf'))
        desk(p,6,40);desk(p,29,40)
        for z in (9,29):royal(p,3,1,z,'royal_tall_cabinet')
        # Shelves stripped for fuel and burned stacks, beside death-register desks.
        for z in (29,33,37):p.set(10,1,z,B('minecraft:coal_block'))
        elven_remains(p,30,1,35,20261042)
    elif name=='council_house':
        for z in (8,14,30,36):desk(p,6,z);bench(p,29,z,'west')
        box(p,3,1,39,13,6,39,STONE)
        mounted_banner(p,4,4,38,'north')
        royal(p,31,1,39,'royal_tall_cabinet')
        # Emergency guard station, backed hooks and a sealed records office.
        box(p,28,1,5,35,2,5,B('botania:dreamwood_planks'))
        p.set(34,2,6,B('minecraft:tripwire_hook',facing='south',attached=False,powered=False))
        elven_remains(p,32,1,32,20261043,role='warden')
    elif name=='census_hall':
        for z in (7,13,24):desk(p,5,z);desk(p,29,z)
        for x in (8,29):
            p.set(x,1,18,B('minecraft:chiseled_stone_bricks'))
            mounted_banner(p,x,5,28,'north')
        elven_remains(p,30,1,25,20261044)
    elif name=='public_kitchen':
        for z in (7,13,24):
            box(p,4,1,z,10,1,z,B('botania:dreamwood_planks'))
            p.set(6,2,z,B('minecraft:campfire',facing='north',lit=False,signal_fire=False,waterlogged=False))
            bench(p,29,z)
        for z in (9,19):bed(p,32,1,z,'white')
        elven_remains(p,9,1,25,20261045,role='healer')
    elif name=='market_court':
        for x in (6,31):
            for z in (7,21):
                box(p,x,1,z,x+8,1,z+2,B('botania:dreamwood_planks'))
                for xx in (x,x+8):box(p,xx,2,z,xx,5,z,B('botania:dreamwood_log',axis='y'))
                box(p,x,6,z,x+8,6,z+3,B('minecraft:purple_wool'))
        elven_remains(p,34,1,15,20261046)
    elif name=='public_forum':
        for z in (8,28):bench(p,7,z);bench(p,35,z)
        for x in (8,36):
            mounted_banner(p,x,5,sz-3,'north')
            bed(p,x,1,17,'white')
        elven_remains(p,34,1,23,20261047)
    elif name=='service_court':
        for z in (8,24):
            for x in (7,35):bench(p,x,z)
        box(p,7,1,6,14,1,6,B('botania:dreamwood_planks'))
        mounted_banner(p,9,4,4,'south')
    else:
        for z in (6,24):
            for x in (4,18):box(p,x,1,z,x,7,z,STONE)
            box(p,4,8,z,18,8,z,CARVED)
    # Keep the public axes clear; furnish their sides, never the junctions.
    box(p,cx-2,1,0,cx+2,4,sz-1,AIR)
    if name in ('assembly_hall','service_court'):
        box(p,0,1,sz//2-2,sx-1,4,sz//2+2,AIR)
    p.set(7,1,10,B('minecraft:barrel',facing='up',open=False),
          {'id':'minecraft:barrel','CustomName':json.dumps({'text':'Civic '+name}),
           'LootTable':'alfheim:chests/civic/'+('records' if name in ('assembly_hall','record_house','council_house','census_hall') else 'supplies')})
    def socket(face,target,child):
        x,z={'north':(cx,0),'south':(cx,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]
        p.jigsaw(x,1,z,'alfheim:'+target,'alfheim:'+target,
                 'minecraft:empty' if child is None else 'alfheim:ancient/civic_center/'+child,face+'_up',joint='aligned')
    if name!='assembly_hall':socket('south',name+'_in',None)
    for face,child in LINKS.get(name,{}).items():socket(face,child+'_in',child)
    return lift(p)

def generate(root=ROOT):
    data=root/'kubejs/data/alfheim';files=[]
    def emit(path,value):
        p=data/path;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');files.append(p)
    for name in SIZES:
        p=data/'structures/ancient/civic_center'/f'{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True)
        nbt.save(str(p),'',detail_nbt(build(name), 'civic_center', name));files.append(p)
        emit(f'worldgen/template_pool/ancient/civic_center/{name}.json',{'name':'alfheim:ancient/civic_center/'+name,'fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'alfheim:ancient/civic_center/'+name,'projection':'rigid','processors':'minecraft:empty'}}]})
    emit('worldgen/structure/civic_center.json',{'type':'minecraft:jigsaw','biomes':'#alfheim:has_civic_center','step':'surface_structures','terrain_adaptation':'beard_thin','spawn_overrides':{},'start_pool':'alfheim:ancient/civic_center/assembly_hall','size':3,'start_height':{'absolute':-DEPTH},'project_start_to_heightmap':'WORLD_SURFACE_WG','max_distance_from_center':116,'use_expansion_hack':False})
    emit('worldgen/structure_set/civic_center.json',{'structures':[{'structure':'alfheim:civic_center','weight':1}],'placement':{'type':'minecraft:random_spread','spacing':56,'separation':32,'salt':101220264}})
    emit('tags/worldgen/biome/has_civic_center.json',{'replace':False,'values':HOME_BIOMES})
    for table,entries in {'records':[('minecraft:paper',6),('minecraft:book',4),('minecraft:ink_sac',2)],'supplies':[('minecraft:bread',4),('minecraft:apple',3),('minecraft:wheat_seeds',2),('minecraft:white_wool',2)]}.items():
        emit(f'loot_tables/chests/civic/{table}.json',{'type':'minecraft:chest','pools':[{'rolls':{'type':'minecraft:uniform','min':2,'max':4},'entries':[{'type':'minecraft:item','name':item,'weight':weight,'functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':1,'max':3}}]} for item,weight in entries]}]})
    return files

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-root',default=str(ROOT));args=ap.parse_args()
    print(f'Civic Center: {len(generate(Path(args.output_root).resolve()))} files')
