"""Sacred-life roster: ritual courts repurposed as shelter, infirmary and mortuary."""
import argparse
import json
from pathlib import Path
import nbt
from district_refit import detail_nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,bed,elven_remains,stone_debris,HOME_BIOMES
from gen_elder_lineage import royal,bench,desk,mounted_banner,lift,STONE,CARVED,FLOOR,AIR,DEPTH

ROOT=Path(__file__).resolve().parents[1]
SIZES={'great_temple_court':(47,38,47),'root_star_shrine':(31,24,31),
       'ancestor_reflection_pool':(31,14,31),'pilgrim_chapel':(31,22,31),
       'rite_house':(39,26,31),'temple_reliquary':(39,24,31),'processional_approach':(23,14,32)}
LINKS={'great_temple_court':{'north':'ancestor_reflection_pool','east':'rite_house','west':'temple_reliquary','south':'processional_approach'},
       'processional_approach':{'east':'pilgrim_chapel','west':'root_star_shrine'}}

def build(name):
    sx,sy,sz=SIZES[name];cx=sx//2;p=Piece(sx,sy,sz)
    box(p,0,0,0,sx-1,0,sz-1,FLOOR);box(p,0,1,0,sx-1,sy-1,sz-1,AIR)
    enclosed=name not in ('ancestor_reflection_pool','processional_approach','root_star_shrine')
    if enclosed:
        for x in (1,sx-2):box(p,x,1,1,x,12,sz-2,STONE)
        for z in (1,sz-2):box(p,1,1,z,sx-2,12,z,STONE)
        for z in range(6,sz-5,8):
            for x in (1,sx-2):box(p,x,5,z,x,8,z+1,B('botania:elf_glass'))
            # Broken ribs and a deliberately missing roof, with no terrain-filled crown.
            for x in range(2,sx-2):
                if not(z>sz//2 and x>cx):p.set(x,15+min(6,x//3,(sx-1-x)//3),z,B('botania:dreamwood_log',axis='x'))
    else:
        for x in (3,sx-4):
            for z in (4,sz-5):box(p,x,1,z,x,7,z,CARVED)
    if name=='great_temple_court':
        for x in (7,39):
            for dy,part in enumerate(('base','mid','crown')):royal(p,x,1+dy,7,'royal_lineage_stele_'+part)
            mounted_banner(p,x,6,44,'north')
        for z in (14,32):bench(p,10,z);bench(p,32,z)
        for x in (5,38):
            for z in (10,36):bed(p,x,1,z,'white')
        box(p,4,1,28,11,1,28,B('botania:dreamwood_planks'))
        elven_remains(p,8,1,37,20261301,role='healer');stone_debris(p,35,1,38,20261302,3)
    elif name=='root_star_shrine':
        for x in (7,23):
            for dy,part in enumerate(('base','mid','crown')):royal(p,x,1+dy,8,'royal_lineage_stele_'+part)
        bench(p,5,23);bench(p,21,23);bed(p,5,1,16,'white')
        p.set(24,1,22,B('minecraft:flower_pot'));stone_debris(p,23,1,25,20261303,2)
    elif name=='ancestor_reflection_pool':
        for x in (4,26):
            for dy,part in enumerate(('base','mid','crown')):royal(p,x,1+dy,5,'royal_lineage_stele_'+part)
        bench(p,5,24);bench(p,21,24);desk(p,5,26)
        elven_remains(p,25,1,25,20261304)
    elif name=='pilgrim_chapel':
        for x in (5,23):
            for z in (7,24):bed(p,x,1,z,'white')
        bench(p,5,15);bench(p,21,15);desk(p,5,20)
        box(p,22,5,25,27,5,27,B('minecraft:white_wool'))
        for x in (22,27):box(p,x,1,27,x,4,27,B('botania:dreamwood_log',axis='y'))
        elven_remains(p,23,1,19,20261305)
    elif name=='rite_house':
        for z in (7,14,25):
            box(p,5,1,z,12,1,z+1,B('botania:dreamwood_planks'));desk(p,28,z)
        for z in (9,24):royal(p,33,1,z,'royal_tall_cabinet')
        elven_remains(p,8,2,25,20261306);stone_debris(p,30,1,25,20261307,2)
    elif name=='temple_reliquary':
        for z in (7,15):desk(p,5,z);royal(p,29,1,z,'royal_tall_cabinet')
        for x in (24,35):box(p,x,1,21,x,5,28,STONE)
        for z in (21,28):box(p,24,1,z,35,5,z,STONE)
        royal(p,28,1,24,'royal_tall_cabinet')
        # Emptied outer shelves and ordinary redistribution records; no powerful relic loot.
        p.set(7,1,24,B('minecraft:bookshelf'));elven_remains(p,31,1,17,20261308)
    else:
        for x in (4,sx-5):
            for z in (6,24):box(p,x,1,z,x,7,z,CARVED)
        for x in range(cx-2,cx+3):
            for z in range(sz):p.set(x,0,z,CARVED)
    box(p,cx-2,1,0,cx+2,4,sz-1,AIR)
    if name in ('great_temple_court','processional_approach'):box(p,0,1,sz//2-2,sx-1,4,sz//2+2,AIR)
    p.set(7,1,26 if name=='ancestor_reflection_pool' else 10,B('minecraft:barrel',facing='up',open=False),{'id':'minecraft:barrel',
        'CustomName':json.dumps({'text':'Sacred '+name}),'LootTable':'alfheim:chests/sacred/'+('records' if name in ('rite_house','temple_reliquary') else 'supplies')})
    def socket(face,target,child):
        x,z={'north':(cx,0),'south':(cx,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]
        p.jigsaw(x,1,z,'alfheim:'+target,'alfheim:'+target,'minecraft:empty' if child is None else 'alfheim:ancient/sacred_precinct/'+child,face+'_up',joint='aligned')
    if name!='great_temple_court':socket('south',name+'_in',None)
    for face,child in LINKS.get(name,{}).items():socket(face,child+'_in',child)
    # Author rubble in its settled position: loose gravel must not migrate into
    # an explicit air cell after the structure receives its first block updates.
    loose=[(point,idx) for point,(idx,_) in p.blocks.items() if p.palette[idx]['Name']=='minecraft:gravel']
    for (x,y,z),idx in sorted(loose,key=lambda item:item[0][1]):
        target=y
        while target>1:
            below=p.blocks.get((x,target-1,z))
            if below is not None and p.palette[below[0]]['Name'] not in ('minecraft:air','minecraft:water'):break
            target-=1
        if target!=y:
            state=p.palette[idx];p.set(x,y,z,AIR);p.set(x,target,z,(state['Name'],state.get('Properties')))
    out=lift(p)
    if name=='ancestor_reflection_pool':
        for x0,x1 in ((5,10),(20,25)):
            box(out,x0,DEPTH-2,8,x1,DEPTH-1,19,B('minecraft:water',level=0))
            box(out,x0,DEPTH,8,x1,DEPTH,19,AIR)
            for x in (x0-1,x1+1):
                for z in range(8,20):out.set(x,DEPTH+1,z,B('minecraft:oak_fence',north=z>8,south=z<19,east=False,west=False,waterlogged=False))
    return out

def generate(root=ROOT):
    data=root/'kubejs/data/alfheim';files=[]
    def emit(path,value):
        p=data/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');files.append(p)
    for name in SIZES:
        p=data/'structures/ancient/sacred_precinct'/f'{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True);nbt.save(str(p),'',detail_nbt(build(name), 'sacred_precinct', name));files.append(p)
        emit(f'worldgen/template_pool/ancient/sacred_precinct/{name}.json',{'name':'alfheim:ancient/sacred_precinct/'+name,'fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'alfheim:ancient/sacred_precinct/'+name,'projection':'rigid','processors':'minecraft:empty'}}]})
    emit('worldgen/structure/sacred_precinct.json',{'type':'minecraft:jigsaw','biomes':'#alfheim:has_sacred_precinct','step':'surface_structures','terrain_adaptation':'beard_thin','spawn_overrides':{},'start_pool':'alfheim:ancient/sacred_precinct/great_temple_court','size':3,'start_height':{'absolute':-DEPTH},'project_start_to_heightmap':'WORLD_SURFACE_WG','max_distance_from_center':116,'use_expansion_hack':False})
    emit('tags/worldgen/biome/has_sacred_precinct.json',{'replace':False,'values':HOME_BIOMES})
    for table,items in {'records':['minecraft:paper','minecraft:book','minecraft:ink_sac'],'supplies':['minecraft:bread','minecraft:white_wool','minecraft:glass_bottle']}.items():
        emit(f'loot_tables/chests/sacred/{table}.json',{'type':'minecraft:chest','pools':[{'rolls':2,'entries':[{'type':'minecraft:item','name':item} for item in items]}]})
    return files

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-root',default=str(ROOT));args=ap.parse_args()
    print('sacred_precinct:',len(generate(Path(args.output_root).resolve())),'files')
