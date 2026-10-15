"""Authored farm terraces and bounded irrigation, without broad terrain edits."""
import argparse
import json
from pathlib import Path
import nbt
from district_refit import detail_nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,bed,elven_remains,stone_debris,HOME_BIOMES
from gen_elder_lineage import royal,bench,desk,mounted_banner,lift,STONE,CARVED,FLOOR,AIR,DEPTH

ROOT=Path(__file__).resolve().parents[1]
SIZES={'water_garden':(47,22,47),'terraced_orchard':(47,24,39),
       'survival_terraces':(47,20,31),'root_granary':(39,26,47),
       'seed_vault':(39,24,31),'fungus_conservatory':(39,26,47),
       'harvest_court':(47,18,31),'keeper_housing':(39,24,31),
       'pollinator_sanctuary':(39,24,31),'farm_approach':(23,14,32)}
LINKS={'water_garden':{'north':'terraced_orchard','west':'root_granary','east':'fungus_conservatory','south':'harvest_court'},
       'terraced_orchard':{'north':'survival_terraces'},
       'root_granary':{'north':'seed_vault'},
       'harvest_court':{'west':'keeper_housing','east':'pollinator_sanctuary','north':'farm_approach'}}
MUSHROOMS=['minecraft:brown_mushroom','minecraft:red_mushroom']+['feywild:'+c+'_mushroom' for c in ('purple','blue','pink','orange','yellow','green')]

def tank(p,x,z,w=8,d=14):
    box(p,x,0,z,x+w,0,z+d,CARVED)
    box(p,x,1,z,x+w,1,z+d,STONE)
    box(p,x+1,1,z+1,x+w-1,1,z+d-1,B('minecraft:water',level=0))
    # Walls reach a full block above water, with a solid floor and no open outlet.
    for xx in (x,x+w):box(p,xx,2,z,xx,2,z+d,STONE)
    for zz in (z,z+d):box(p,x,2,zz,x+w,2,zz,STONE)

def tree(p,x,y,z):
    box(p,x,y,z,x,y+5,z,B('botania:dreamwood_log',axis='y'))
    for yy,r in ((y+4,2),(y+5,2),(y+6,1)):
        for dx in range(-r,r+1):
            for dz in range(-r,r+1):
                if dx or dz or yy==y+6:p.set(x+dx,yy,z+dz,B('mythicbotany:dreamwood_leaves',distance=1,persistent=True,waterlogged=False))

def build(name):
    sx,sy,sz=SIZES[name];cx=sx//2;p=Piece(sx,sy,sz)
    box(p,0,1,0,sx-1,sy-1,sz-1,AIR);box(p,0,0,0,sx-1,0,sz-1,FLOOR)
    if name in ('root_granary','seed_vault','fungus_conservatory','keeper_housing'):
        for x in (1,sx-2):box(p,x,1,1,x,13,sz-2,STONE)
        for z in (1,sz-2):box(p,1,1,z,sx-2,13,z,STONE)
        for z in range(5,sz-3,8):
            for x in range(2,sx-2):
                if not (name=='fungus_conservatory' and z>28 and x>cx):p.set(x,15+min(5,x//3,(sx-1-x)//3),z,B('botania:dreamwood_log',axis='x'))
    if name=='water_garden':
        for x in (10,30):
            for z in (5,27):tank(p,x,z,8,14)
        for x in (4,38):desk(p,x,26)
        # Silted filter media and a visibly patched, closed distribution junction.
        for x in (15,31):box(p,x,1,7,x,1,17,B('minecraft:clay'))
        for x in (14,32):p.set(x,1,25,B('botania:elf_glass'))
        elven_remains(p,4,1,32,20261300)
    elif name in ('terraced_orchard','survival_terraces'):
        for x in (4,30):
            for z,h in ((4,1),(17,3)):
                box(p,x,1,z,x+12,h,z+10,STONE)
                box(p,x,h,z,x+12,h,z+10,B('minecraft:grass_block',snowy=False))
                for xx in (x,x+12):box(p,xx,1,z,xx,h,z+10,CARVED)
                for i in range(h):
                    box(p,x+5,1,z+11+h-1-i,x+5,1+i,z+11+h-1-i,STONE)
                    p.set(x+5,1+i,z+11+h-1-i,B('botania:dreamwood_stairs',facing='north',half='bottom',shape='straight',waterlogged=False))
                if name=='terraced_orchard':tree(p,x+6,h+1,z+5)
                else:
                    # Emergency crops reuse the ornamental terraces; each row has support.
                    for dx in (2,4,7,9):
                        for dz in (2,4,6,8):
                            p.set(x+dx,h,z+dz,B('minecraft:farmland',moisture=7))
                            p.set(x+dx,h+1,z+dz,B('minecraft:wheat' if dx%2==0 else 'minecraft:carrots',age=7))
        if name=='terraced_orchard':
            # Retaining-wall break and fallen stone occur on one outer side, off route.
            box(p,42,1,22,42,3,25,AIR);stone_debris(p,43,1,28,20261301,2)
        desk(p,5,16);elven_remains(p,35,1,16,20261302)
    elif name=='root_granary':
        for x in (5,27):
            for z in (6,15,31,39):
                box(p,x,1,z,x+6,3,z+3,B('botania:dreamwood_planks'))
                box(p,x+1,2,z+1,x+5,3,z+2,AIR)
        # Empty bins, stripped side bays and a sealed ration reserve.
        box(p,26,1,35,35,5,35,STONE)
        desk(p,5,25);royal(p,31,1,25,'royal_tall_cabinet')
        mounted_banner(p,4,5,44,'north');elven_remains(p,29,1,42,20261303)
    elif name=='seed_vault':
        for z in (7,15,24):
            for x in (5,30):royal(p,x,1,z,'royal_tall_cabinet')
        box(p,26,1,23,35,6,23,STONE);desk(p,5,20)
        elven_remains(p,29,1,20,20261304)
    elif name=='fungus_conservatory':
        for x in (4,26):
            for z in (5,27):
                box(p,x,1,z,x+8,1,z+12,B('minecraft:mycelium',snowy=False))
                for i,mushroom in enumerate(MUSHROOMS):p.set(x+1+(i%2)*5,2,z+1+(i//2)*3,B(mushroom))
        for z in (18,41):desk(p,5,z)
        bed(p,29,1,19,'brown');elven_remains(p,31,1,42,20261305)
    elif name=='keeper_housing':
        for x in (5,11,27,33):
            for z in (6,15,24):bed(p,x,1,z,'brown')
        for z in (10,22):bench(p,5,z);royal(p,31,1,z,'royal_tall_cabinet')
        elven_remains(p,29,1,19,20261306)
    elif name=='pollinator_sanctuary':
        for x in (4,26):
            box(p,x,1,5,x+8,1,24,B('minecraft:grass_block',snowy=False))
            for i,flower in enumerate(('dandelion','poppy','blue_orchid','allium','azure_bluet','oxeye_daisy')):
                p.set(x+2+(i%2)*4,2,7+(i//2)*6,B('minecraft:'+flower))
            for z in (10,22):p.set(x+8,2,z,B('minecraft:beehive',facing='west',honey_level=0))
        for x in (3,35):
            for z in (4,26):box(p,x,1,z,x,8,z,STONE)
            box(p,x,9,4,x,9,26,B('botania:dreamwood_log',axis='z'))
        desk(p,4,26);elven_remains(p,30,1,26,20261307)
    elif name=='harvest_court':
        for z in (6,24):bench(p,5,z);bench(p,36,z)
        for x in (6,35):box(p,x,1,9,x+4,1,9,B('botania:dreamwood_planks'))
        mounted_banner(p,7,5,4,'south')
    else:
        for z in range(sz):
            for x in (cx-2,cx+2):p.set(x,0,z,CARVED)
        for x in (4,18):box(p,x,1,5,x,7,5,STONE)
    box(p,cx-2,1,0,cx+2,4,sz-1,AIR)
    if name in ('water_garden','harvest_court'):box(p,0,1,sz//2-2,sx-1,4,sz//2+2,AIR)
    p.set(7,1,10,B('minecraft:barrel',facing='up',open=False),{'id':'minecraft:barrel','CustomName':json.dumps({'text':'Agricultural '+name}),'LootTable':'alfheim:chests/agricultural/'+('seeds' if name in ('seed_vault','survival_terraces','pollinator_sanctuary','fungus_conservatory') else 'stores')})
    def socket(face,target,child):
        x,z={'north':(cx,0),'south':(cx,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]
        p.jigsaw(x,1,z,'alfheim:'+target,'alfheim:'+target,'minecraft:empty' if child is None else 'alfheim:ancient/agricultural_estate/'+child,face+'_up',joint='aligned')
    if name!='water_garden':socket('south',name+'_in',None)
    for face,child in LINKS.get(name,{}).items():socket(face,child+'_in',child)
    return lift(p)

def generate(root=ROOT):
    data=root/'kubejs/data/alfheim';files=[]
    def emit(path,value):
        p=data/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');files.append(p)
    for name in SIZES:
        p=data/'structures/ancient/agricultural_estate'/f'{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True);nbt.save(str(p),'',detail_nbt(build(name), 'agricultural_estate', name));files.append(p)
        emit(f'worldgen/template_pool/ancient/agricultural_estate/{name}.json',{'name':'alfheim:ancient/agricultural_estate/'+name,'fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'alfheim:ancient/agricultural_estate/'+name,'projection':'rigid','processors':'minecraft:empty'}}]})
    emit('worldgen/structure/agricultural_estate.json',{'type':'minecraft:jigsaw','biomes':'#alfheim:has_agricultural_estate','step':'surface_structures','terrain_adaptation':'beard_thin','spawn_overrides':{},'start_pool':'alfheim:ancient/agricultural_estate/water_garden','size':3,'start_height':{'absolute':-DEPTH},'project_start_to_heightmap':'WORLD_SURFACE_WG','max_distance_from_center':116,'use_expansion_hack':False})
    emit('worldgen/structure_set/agricultural_estate.json',{'structures':[{'structure':'alfheim:agricultural_estate','weight':1}],'placement':{'type':'minecraft:random_spread','spacing':56,'separation':32,'salt':101220268}})
    emit('tags/worldgen/biome/has_agricultural_estate.json',{'replace':False,'values':HOME_BIOMES})
    for table,entries in {'seeds':[('minecraft:wheat_seeds',4),('minecraft:beetroot_seeds',3),('minecraft:pumpkin_seeds',2),('minecraft:melon_seeds',2)],'stores':[('minecraft:bread',4),('minecraft:apple',3),('minecraft:paper',2)]}.items():
        emit(f'loot_tables/chests/agricultural/{table}.json',{'type':'minecraft:chest','pools':[{'rolls':{'type':'minecraft:uniform','min':2,'max':4},'entries':[{'type':'minecraft:item','name':item,'weight':weight,'functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':1,'max':3}}]} for item,weight in entries]}]})
    return files

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-root',default=str(ROOT));args=ap.parse_args();print(f'Agricultural Estate: {len(generate(Path(args.output_root).resolve()))} files')
