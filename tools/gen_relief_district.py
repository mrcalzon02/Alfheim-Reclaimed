"""Wave-1 relief precinct: controlled wards and burials beyond the checkpoint."""
import argparse
import json
from pathlib import Path
import nbt
from district_refit import detail_nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,bed,elven_remains,skeletal_remains,stone_debris,HOME_BIOMES
from gen_elder_lineage import royal,bench,desk,mounted_banner,lift,STONE,CARVED,FLOOR,AIR,DEPTH

ROOT=Path(__file__).resolve().parents[1]
SIZES={'triage_court':(47,24,47),'hospice_hall':(39,26,47),
       'healer_cloister':(39,24,47),'quarantine_checkpoint':(47,18,23),
       'mass_grave':(47,16,39),'supply_court':(47,18,31),
       'ration_hall':(39,24,31),'sealed_store':(39,22,31),
       'corpse_cart_way':(23,14,32),'ash_pits':(31,14,23),'digger_shelter':(31,18,23)}
LINKS={'triage_court':{'east':'hospice_hall','west':'healer_cloister','north':'quarantine_checkpoint','south':'supply_court'},
       'quarantine_checkpoint':{'north':'mass_grave'},
       'mass_grave':{'east':'ash_pits','west':'digger_shelter'},
       'supply_court':{'west':'ration_hall','east':'sealed_store','north':'corpse_cart_way'}}

def build(name):
    sx,sy,sz=SIZES[name];cx=sx//2;p=Piece(sx,sy,sz)
    box(p,0,1,0,sx-1,sy-1,sz-1,AIR);box(p,0,0,0,sx-1,0,sz-1,FLOOR)
    enclosed=name in ('hospice_hall','healer_cloister','ration_hall','sealed_store','digger_shelter')
    if enclosed or name=='triage_court':
        h=12 if enclosed else 6
        for x in (1,sx-2):box(p,x,1,1,x,h,sz-2,STONE)
        for z in (1,sz-2):box(p,1,1,z,sx-2,h,z,STONE)
        for z in range(7,sz-7,9):
            for x in (1,sx-2):box(p,x,5,z,x,7,z+1,B('botania:elf_glass'))
        if enclosed:
            for z in range(5,sz-3,8):
                for x in range(2,sx-2):
                    # A roof breach over the eastern ward has a matching debris fan.
                    if not (name=='hospice_hall' and z>=29 and x>cx):
                        p.set(x,14+min(5,x//4,(sx-1-x)//4),z,B('botania:dreamwood_log',axis='x'))
    if name in ('triage_court','hospice_hall'):
        xs=(6,13,31,38) if name=='triage_court' else (5,11,27,33)
        for x in xs:
            for z in (6,15,29,38):bed(p,x,1,z,'white')
        for x in ((17,29) if name=='triage_court' else (14,24)):
            for z in (5,28):box(p,x,1,z,x,3,z+11,B('minecraft:white_wool'))
        for x,z in ((8,12),(32,34),(12,40)):
            elven_remains(p,x,1,z,20261060+x+z)
        desk(p,4,26);royal(p,sx-5,1,26,'royal_tall_cabinet')
        if name=='hospice_hall':
            elven_remains(p,7,1,33,20261101,role='healer')
            stone_debris(p,30,1,41,20261102,3)
            box(p,29,1,27,35,1,27,B('minecraft:coal_block'))
    elif name=='healer_cloister':
        for z in (7,15,31,39):desk(p,5,z);royal(p,30,1,z,'royal_tall_cabinet')
        for z in (11,35):bed(p,9,1,z,'white')
        # Exhausted preparation counters and a failed, dry cleansing basin.
        box(p,26,0,18,34,0,25,CARVED)
        for x in (26,34):box(p,x,1,18,x,1,25,STONE)
        for z in (18,25):box(p,26,1,z,34,1,z,STONE)
        elven_remains(p,8,1,32,20261103,role='healer')
        mounted_banner(p,5,5,44,'north')
    elif name=='quarantine_checkpoint':
        for x in (3,15,31,43):
            box(p,x,1,4,x,8,4,CARVED);box(p,x,1,18,x,6,18,STONE)
        for x0,x1 in ((3,20),(26,43)):
            box(p,x0,1,11,x1,4,11,STONE)
        desk(p,5,7);desk(p,36,7)
        mounted_banner(p,8,5,18,'north');mounted_banner(p,38,5,18,'north')
        elven_remains(p,34,1,14,20261104,role='warden')
    elif name=='mass_grave':
        box(p,3,0,3,43,0,35,B('minecraft:coarse_dirt'))
        # Orderly, filled early rows: stone markers, individual shrouds and spoil.
        for z in (6,12,18):
            for x in (6,11,16):
                p.set(x,1,z,B('minecraft:chiseled_stone_bricks'))
                skeletal_remains(p,x,1,z+2,20261110+x+z,cloth=True)
        # Late crowded rows remain open; carve them after adding the buried base.
        for x in (31,39):
            for z in (6,14,22,30):p.set(x+2,1,z,CARVED)
        desk(p,5,31);elven_remains(p,11,1,32,20261105,role='warden')
    elif name=='ration_hall':
        for z in (7,15,25):
            box(p,4,1,z,11,1,z,B('botania:dreamwood_planks'))
            bench(p,29,z)
        # Queue rails show an organized service that later became overwhelmed.
        for x in (13,26):
            for z in (5,6,7,8,9,10,11,12,13):
                p.set(x,1,z,B('minecraft:oak_fence',north=z>5,south=z<13,east=False,west=False,waterlogged=False))
        for x,z in ((7,20),(30,11),(28,27)):elven_remains(p,x,1,z,20261120+x+z)
    elif name=='sealed_store':
        for z in (7,15,25):royal(p,5,1,z,'royal_tall_cabinet');royal(p,30,1,z,'royal_tall_cabinet')
        # Sealed depleted side bays leave the supply corridor open.
        for z in (5,23):box(p,3,1,z,12,5,z,STONE);box(p,26,1,z,35,5,z,STONE)
        desk(p,5,19);elven_remains(p,30,1,18,20261106)
    elif name=='ash_pits':
        for x in (5,22):
            box(p,x-2,0,5,x+2,0,16,B('minecraft:coal_block'))
            for z in (5,16):box(p,x-3,1,z,x+3,1,z,STONE)
            skeletal_remains(p,x,1,10,20261130+x,cloth=False)
        elven_remains(p,6,1,19,20261107)
    elif name=='digger_shelter':
        for z in (5,15):bed(p,5,1,z,'brown');bench(p,23,z)
        desk(p,5,19)
        # Grounded tool residue, a screened sleeping bay and abandoned burial rolls.
        p.set(24,1,18,B('minecraft:composter',level=0))
        elven_remains(p,23,1,9,20261108)
    elif name=='supply_court':
        for z in (6,25):bench(p,5,z);bench(p,36,z)
        for x in (4,42):box(p,x,1,7,x,7,7,CARVED)
        mounted_banner(p,8,4,4,'south')
    else:
        # Empty cart bed off the axis, with tracks continuing toward the checkpoint.
        for z in range(sz):
            for x in (cx-2,cx+2):p.set(x,0,z,CARVED)
        box(p,3,1,12,7,1,18,B('botania:dreamwood_planks'))
        for z in (12,18):p.set(2,1,z,B('minecraft:chiseled_stone_bricks'))
    box(p,cx-2,1,0,cx+2,4,sz-1,AIR)
    if name in ('triage_court','supply_court','mass_grave'):
        box(p,0,1,sz//2-2,sx-1,4,sz//2+2,AIR)
    p.set(7,1,10,B('minecraft:barrel',facing='up',open=False),
          {'id':'minecraft:barrel','CustomName':json.dumps({'text':'Relief '+name}),
           'LootTable':'alfheim:chests/relief/'+('records' if name in ('healer_cloister','quarantine_checkpoint','mass_grave','digger_shelter') else 'supplies')})
    def socket(face,target,child):
        x,z={'north':(cx,0),'south':(cx,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]
        p.jigsaw(x,1,z,'alfheim:'+target,'alfheim:'+target,
                 'minecraft:empty' if child is None else 'alfheim:ancient/relief_district/'+child,face+'_up',joint='aligned')
    if name!='triage_court':socket('south',name+'_in',None)
    for face,child in LINKS.get(name,{}).items():socket(face,child+'_in',child)
    out=lift(p)
    if name=='mass_grave':
        for x in (29,37):
            for z0,z1 in ((4,16),(23,34)):
                box(out,x,DEPTH-1,z0,x+2,DEPTH,z1,AIR)
                for z in range(z0+1,z1,3):skeletal_remains(out,x+1,DEPTH-1,z,20261200+x+z,cloth=True)
                # Stable spoil piles sit beside the excavations, outside clear axes.
                box(out,x+3,DEPTH+1,z0,x+3,DEPTH+2,z0+2,B('minecraft:coarse_dirt'))
    return out

def generate(root=ROOT):
    data=root/'kubejs/data/alfheim';files=[]
    def emit(path,value):
        p=data/path;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');files.append(p)
    for name in SIZES:
        p=data/'structures/ancient/relief_district'/f'{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True)
        nbt.save(str(p),'',detail_nbt(build(name), 'relief_district', name));files.append(p)
        emit(f'worldgen/template_pool/ancient/relief_district/{name}.json',{'name':'alfheim:ancient/relief_district/'+name,'fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'alfheim:ancient/relief_district/'+name,'projection':'rigid','processors':'minecraft:empty'}}]})
    emit('worldgen/structure/relief_district.json',{'type':'minecraft:jigsaw','biomes':'#alfheim:has_relief_district','step':'surface_structures','terrain_adaptation':'beard_thin','spawn_overrides':{},'start_pool':'alfheim:ancient/relief_district/triage_court','size':4,'start_height':{'absolute':-DEPTH},'project_start_to_heightmap':'WORLD_SURFACE_WG','max_distance_from_center':116,'use_expansion_hack':False})
    emit('worldgen/structure_set/relief_district.json',{'structures':[{'structure':'alfheim:relief_district','weight':1}],'placement':{'type':'minecraft:random_spread','spacing':56,'separation':32,'salt':101220265}})
    emit('tags/worldgen/biome/has_relief_district.json',{'replace':False,'values':HOME_BIOMES})
    for table,entries in {'records':[('minecraft:paper',6),('minecraft:book',3),('minecraft:ink_sac',1)],'supplies':[('minecraft:bread',3),('minecraft:white_wool',4),('minecraft:wheat_seeds',2)]}.items():
        emit(f'loot_tables/chests/relief/{table}.json',{'type':'minecraft:chest','pools':[{'rolls':{'type':'minecraft:uniform','min':1,'max':3},'entries':[{'type':'minecraft:item','name':item,'weight':weight,'functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':1,'max':2}}]} for item,weight in entries]}]})
    return files

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-root',default=str(ROOT));args=ap.parse_args()
    print(f'Relief District: {len(generate(Path(args.output_root).resolve()))} files')
