"""Wave-2 connected teaching, preservation and failed research precinct."""
import argparse
import json
from pathlib import Path
import nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,bed,elven_remains,stone_debris,HOME_BIOMES
from gen_elder_lineage import royal,bench,desk,mounted_banner,lift,STONE,CARVED,FLOOR,AIR,DEPTH

ROOT=Path(__file__).resolve().parents[1]
SIZES={'lore_college':(47,32,47),'archive_cloister':(39,26,47),
       'runic_engineering_hall':(39,28,47),'philosopher_court':(47,18,32),
       'astral_conservatory':(47,32,39),'entry_court':(47,18,31),
       'student_residence':(39,24,31),'botanical_research_garden':(39,24,31),
       'scholars_avenue':(23,14,32)}
LINKS={'lore_college':{'east':'archive_cloister','west':'runic_engineering_hall',
                     'north':'philosopher_court','south':'entry_court'},
       'philosopher_court':{'north':'astral_conservatory'},
       'entry_court':{'west':'student_residence','east':'botanical_research_garden','north':'scholars_avenue'}}

def build(name):
    sx,sy,sz=SIZES[name];cx=sx//2;p=Piece(sx,sy,sz)
    box(p,0,1,0,sx-1,sy-1,sz-1,AIR);box(p,0,0,0,sx-1,0,sz-1,FLOOR)
    closed=name in ('lore_college','archive_cloister','runic_engineering_hall','student_residence')
    if closed:
        for x in (1,sx-2):box(p,x,1,1,x,13,sz-2,STONE)
        for z in (1,sz-2):box(p,1,1,z,sx-2,13,z,STONE)
        for z in range(7,sz-7,8):
            for x in (1,sx-2):box(p,x,5,z,x,9,z+1,B('botania:elf_glass'))
        for z in range(5,sz-3,8):
            for x in range(2,sx-2):
                if not (name=='archive_cloister' and z>=29 and x>cx):
                    p.set(x,15+min(6,x//3,(sx-1-x)//3),z,B('botania:dreamwood_log',axis='x'))
    if name=='lore_college':
        for z in (8,14,30,36):
            for x in (7,13,31,37):bench(p,x,z)
        for x in (8,34):desk(p,x,6);desk(p,x,40)
        # Emergency planning tables replace the side lecture bays.
        for x in (6,35):
            box(p,x,1,18,x+4,1,18,B('botania:dreamwood_planks'))
            royal(p,x,1,27,'royal_tall_cabinet')
        mounted_banner(p,6,6,44,'north');mounted_banner(p,40,6,44,'north')
        elven_remains(p,10,1,33,20261210)
    elif name=='archive_cloister':
        for x in (5,10,28,33):
            for z in range(5,39,4):
                if not (x==33 and z>24):box(p,x,1,z,x,4,z+1,B('minecraft:bookshelf'))
        for z in (9,25,40):desk(p,13,z)
        # Sealed surviving manuscript bay, copying stations and a burned wet-roof side.
        box(p,27,1,39,35,6,39,STONE)
        royal(p,30,1,42,'royal_tall_cabinet')
        for z in (29,33,37):p.set(33,1,z,B('minecraft:coal_block'))
        stone_debris(p,30,1,35,20261211,3)
        elven_remains(p,12,1,31,20261212)
    elif name=='runic_engineering_hall':
        for z in (8,30):
            for x in (7,29):
                box(p,x-2,0,z-2,x+3,0,z+4,CARVED)
                for xx in (x-2,x+3):box(p,xx,1,z,xx,4,z,STONE)
                # Inert fractured test rig; no functional progression machinery.
                p.set(x,1,z,B('botania:elf_glass'));p.set(x+1,1,z,CARVED)
                p.set(x,2,z,B('minecraft:end_rod',facing='up'))
        for z in (13,35):desk(p,5,z)
        box(p,27,1,17,35,5,17,STONE)
        elven_remains(p,29,1,38,20261213)
    elif name=='astral_conservatory':
        # Layered dome rings with a directional northeast collapse, not random holes.
        for y in range(4,27):
            radius=16 if y<=14 else max(4,16-(y-14))
            for x in range(cx-radius,cx+radius+1):
                for z in range(19-radius,20+radius):
                    d=(x-cx)**2+(z-19)**2
                    if (radius-1)**2<=d<=radius**2 and not (x>cx+3 and z<19 and y>11):
                        p.set(x,y,z,CARVED if y%4==0 else B('botania:elf_glass'))
        # Accessible observation gallery: east stairs, upper landing and guarded edge.
        box(p,30,8,10,35,8,29,FLOOR)
        for i in range(8):
            box(p,33,2+i,30-i,33,3+i,30-i,AIR)
            p.set(33,1+i,30-i,B('botania:dreamwood_stairs',facing='north',half='bottom',shape='straight',waterlogged=False))
        for z in range(10,23):p.set(30,9,z,B('minecraft:oak_fence',north=z>10,south=z<22,east=False,west=False,waterlogged=False))
        royal(p,31,9,12,'royal_writing_desk_left');royal(p,32,9,12,'royal_writing_desk_right');desk(p,9,26)
        for x,z in ((7,19),(39,19),(13,7),(33,7),(13,31),(33,31)):box(p,x,1,z,x,3,z,CARVED)
        for x in (9,36):box(p,x,1,17,x,4,17,CARVED)
        # Frozen calendar markers and an interrupted observing axis.
        for z in (9,29):box(p,14,0,z,32,0,z,CARVED)
        stone_debris(p,29,1,9,20261214,3)
        elven_remains(p,9,1,29,20261215)
    elif name=='student_residence':
        for x in (5,11,27,33):
            for z in (6,15,24):bed(p,x,1,z,'purple')
        for z in (10,22):desk(p,5,z);royal(p,31,1,z,'royal_tall_cabinet')
        elven_remains(p,29,1,19,20261216)
    elif name=='botanical_research_garden':
        for x in (5,27):
            for z in (6,17):
                box(p,x,1,z,x+5,1,z+7,B('minecraft:grass_block',snowy=False))
                for dx,dz,plant in ((1,1,'fern'),(3,2,'dandelion'),(2,5,'poppy'),(4,6,'grass')):
                    p.set(x+dx,2,z+dz,B('minecraft:'+plant))
                # Dry containment borders keep research beds away from circulation.
                for zz in (z-1,z+8):box(p,x-1,1,zz,x+6,1,zz,CARVED)
        for x in (3,35):
            for z in (4,26):box(p,x,1,z,x,9,z,STONE)
            box(p,x,10,4,x,10,26,B('botania:dreamwood_log',axis='z'))
        desk(p,4,26);elven_remains(p,30,1,26,20261217,role='healer')
    elif name=='philosopher_court':
        for z in (7,24):bench(p,8,z);bench(p,35,z)
        for x in (6,40):
            box(p,x,1,13,x,7,13,CARVED)
            mounted_banner(p,x,4,28,'north')
        desk(p,7,16);elven_remains(p,36,1,18,20261218)
    elif name=='entry_court':
        for z in (7,24):bench(p,6,z);bench(p,35,z)
        mounted_banner(p,7,5,4,'south');mounted_banner(p,39,5,4,'south')
    else:
        for z in (6,24):
            for x in (4,18):box(p,x,1,z,x,7,z,STONE)
            box(p,4,8,z,18,8,z,CARVED)
    box(p,cx-2,1,0,cx+2,4,sz-1,AIR)
    if name in ('lore_college','entry_court'):box(p,0,1,sz//2-2,sx-1,4,sz//2+2,AIR)
    p.set(7,1,10,B('minecraft:barrel',facing='up',open=False),{'id':'minecraft:barrel','CustomName':json.dumps({'text':'Scholastic '+name}),'LootTable':'alfheim:chests/scholastic/'+('supplies' if name in ('student_residence','botanical_research_garden','entry_court','scholars_avenue') else 'records')})
    def socket(face,target,child):
        x,z={'north':(cx,0),'south':(cx,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]
        p.jigsaw(x,1,z,'alfheim:'+target,'alfheim:'+target,'minecraft:empty' if child is None else 'alfheim:ancient/scholastic_quarter/'+child,face+'_up',joint='aligned')
    if name!='lore_college':socket('south',name+'_in',None)
    for face,child in LINKS.get(name,{}).items():socket(face,child+'_in',child)
    return lift(p)

def generate(root=ROOT):
    data=root/'kubejs/data/alfheim';files=[]
    def emit(path,value):
        p=data/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');files.append(p)
    for name in SIZES:
        p=data/'structures/ancient/scholastic_quarter'/f'{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True);nbt.save(str(p),'',build(name).to_nbt());files.append(p)
        emit(f'worldgen/template_pool/ancient/scholastic_quarter/{name}.json',{'name':'alfheim:ancient/scholastic_quarter/'+name,'fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'alfheim:ancient/scholastic_quarter/'+name,'projection':'rigid','processors':'minecraft:empty'}}]})
    emit('worldgen/structure/scholastic_quarter.json',{'type':'minecraft:jigsaw','biomes':'#alfheim:has_scholastic_quarter','step':'surface_structures','terrain_adaptation':'beard_thin','spawn_overrides':{},'start_pool':'alfheim:ancient/scholastic_quarter/lore_college','size':3,'start_height':{'absolute':-DEPTH},'project_start_to_heightmap':'WORLD_SURFACE_WG','max_distance_from_center':116,'use_expansion_hack':False})
    emit('worldgen/structure_set/scholastic_quarter.json',{'structures':[{'structure':'alfheim:scholastic_quarter','weight':1}],'placement':{'type':'minecraft:random_spread','spacing':56,'separation':32,'salt':101220266}})
    emit('tags/worldgen/biome/has_scholastic_quarter.json',{'replace':False,'values':HOME_BIOMES})
    for table,entries in {'records':[('minecraft:paper',6),('minecraft:book',4),('minecraft:ink_sac',2)],'supplies':[('minecraft:bread',3),('minecraft:wheat_seeds',3),('minecraft:purple_dye',2)]}.items():
        emit(f'loot_tables/chests/scholastic/{table}.json',{'type':'minecraft:chest','pools':[{'rolls':{'type':'minecraft:uniform','min':2,'max':4},'entries':[{'type':'minecraft:item','name':item,'weight':weight,'functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':1,'max':3}}]} for item,weight in entries]}]})
    return files

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-root',default=str(ROOT));args=ap.parse_args();print(f'Scholastic Quarter: {len(generate(Path(args.output_root).resolve()))} files')
