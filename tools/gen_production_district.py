"""Wave-2 botanical industry and salvage logistics; no working power machines."""
import argparse
import json
from pathlib import Path
import nbt
from district_refit import detail_nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,bed,elven_remains,stone_debris,HOME_BIOMES
from gen_elder_lineage import royal,bench,desk,mounted_banner,lift,STONE,CARVED,FLOOR,AIR,DEPTH

ROOT=Path(__file__).resolve().parents[1]
SIZES={'freight_yard':(47,24,47),'distribution_depot':(39,26,47),
       'resonance_foundry':(39,30,47),'mana_mill':(47,30,39),
       'dreamwood_shaping_court':(47,22,31),'glass_bloom_house':(39,26,31),
       'waterworks':(47,18,31),'worker_housing':(39,24,31),
       'guard_post':(31,22,31),'freight_approach':(23,14,32)}
LINKS={'freight_yard':{'east':'distribution_depot','west':'resonance_foundry','north':'mana_mill','south':'dreamwood_shaping_court'},
       'resonance_foundry':{'north':'glass_bloom_house'},
       'mana_mill':{'north':'waterworks'},
       'dreamwood_shaping_court':{'west':'worker_housing','east':'guard_post','north':'freight_approach'}}

def build(name):
    sx,sy,sz=SIZES[name];cx=sx//2;p=Piece(sx,sy,sz)
    box(p,0,1,0,sx-1,sy-1,sz-1,AIR);box(p,0,0,0,sx-1,0,sz-1,FLOOR)
    closed=name in ('distribution_depot','resonance_foundry','mana_mill','glass_bloom_house','worker_housing','guard_post')
    if closed:
        for x in (1,sx-2):box(p,x,1,1,x,13,sz-2,STONE)
        for z in (1,sz-2):box(p,1,1,z,sx-2,13,z,STONE)
        for z in range(7,sz-7,8):
            for x in (1,sx-2):box(p,x,5,z,x,9,z+1,B('botania:elf_glass'))
        for z in range(5,sz-3,8):
            for x in range(2,sx-2):
                if not (name=='glass_bloom_house' and z>=21 and x>cx):
                    p.set(x,15+min(6,x//3,(sx-1-x)//3),z,B('botania:dreamwood_log',axis='x'))
    if name=='freight_yard':
        # Paired timber gantries, repair benches and abandoned cart staging.
        for z in (8,36):
            for x in (7,16,30,39):box(p,x,1,z,x,11,z,B('botania:dreamwood_log',axis='y'))
            box(p,7,12,z,16,12,z,B('botania:dreamwood_log',axis='x'))
            box(p,30,12,z,39,12,z,B('botania:dreamwood_log',axis='x'))
        for x,z in ((8,13),(33,30)):
            box(p,x,1,z,x+4,1,z+5,B('botania:dreamwood_planks'))
            for dz in (0,5):p.set(x-1,1,z+dz,CARVED)
        desk(p,5,29);desk(p,35,13)
        elven_remains(p,12,1,34,20261240)
    elif name=='distribution_depot':
        for x in (5,29):
            for z in (7,15,31,39):
                box(p,x,1,z,x+4,2,z+2,B('botania:dreamwood_planks'))
        # Store subdivisions preserve a public aisle and a sealed inner reserve.
        for z in (18,35):box(p,3,1,z,13,5,z,STONE);box(p,25,1,z,35,5,z,STONE)
        desk(p,5,25);royal(p,30,1,25,'royal_tall_cabinet')
        mounted_banner(p,4,5,44,'north');elven_remains(p,31,1,42,20261241)
    elif name=='resonance_foundry':
        for x in (7,29):
            for z in (8,30):
                box(p,x-3,0,z-3,x+3,0,z+4,CARVED)
                for xx in (x-3,x+3):box(p,xx,1,z,xx,6,z,STONE)
                for xx in range(x-3,x+4):p.set(xx,7,z,CARVED)
                p.set(x,1,z,B('minecraft:furnace',facing='south',lit=False))
                box(p,x-1,1,z+3,x+1,1,z+3,B('minecraft:calcite'))
        desk(p,5,18);desk(p,28,40)
        # A cracked ritual bed and stripped work bay, with manual repair stock.
        box(p,27,1,17,35,1,17,B('minecraft:coal_block'))
        elven_remains(p,29,1,35,20261242)
    elif name=='mana_mill':
        for x in (8,36):
            box(p,x,1,7,x,10,7,CARVED);box(p,x,1,29,x,10,29,CARVED)
            # Fractured decorative channel and an incomplete bypass along its side.
            for z in range(9,28):
                if z not in (17,18):p.set(x,2,z,B('ars_nouveau:sourcestone'))
                if 14<=z<=22:p.set(x+2,1,z,CARVED)
            p.set(x,3,13,B('botania:elf_glass'))
        desk(p,6,31);royal(p,37,1,31,'royal_tall_cabinet')
        box(p,32,1,6,39,1,6,B('minecraft:coal_block'))
        elven_remains(p,10,1,28,20261243)
    elif name=='dreamwood_shaping_court':
        for x in (6,32):
            for z in (6,23):
                for xx in range(x,x+8):p.set(xx,1,z,B('botania:dreamwood_log',axis='x'))
                for xx in (x,x+7):box(p,xx,2,z,xx,6,z,CARVED)
                box(p,x,7,z,x+7,7,z,B('botania:dreamwood_log',axis='x'))
        box(p,5,1,11,11,1,11,B('botania:dreamwood_planks'))
        desk(p,33,10);elven_remains(p,8,1,26,20261244)
    elif name=='glass_bloom_house':
        for x in (7,28):
            for z in (7,22):
                box(p,x-2,0,z-2,x+2,0,z+2,CARVED)
                p.set(x,1,z,B('minecraft:furnace',facing='south',lit=False))
                for xx in (x-2,x+2):p.set(xx,1,z+1,B('botania:elf_glass'))
        # Freestanding growth beds and kiln residue, never crystals inside masonry.
        desk(p,5,15);stone_debris(p,29,1,25,20261245,3)
        elven_remains(p,9,1,24,20261246)
    elif name=='waterworks':
        # Dry settling tanks: no fluid sources or spill into adjacent rooms.
        for x in (6,30):
            box(p,x,0,5,x+10,0,23,CARVED)
            for xx in (x,x+10):box(p,xx,1,5,xx,2,23,STONE)
            for z in (5,23):box(p,x,1,z,x+10,2,z,STONE)
            p.set(x+5,1,24,B('botania:elf_glass'))
        desk(p,4,26);elven_remains(p,34,1,26,20261247)
    elif name=='worker_housing':
        for x in (5,11,27,33):
            for z in (6,15,24):bed(p,x,1,z,'brown')
        for z in (10,22):bench(p,5,z);royal(p,31,1,z,'royal_tall_cabinet')
        elven_remains(p,29,1,19,20261248)
    elif name=='guard_post':
        desk(p,5,7);bench(p,23,7);bed(p,5,1,23,'purple')
        mounted_banner(p,24,5,28,'north');elven_remains(p,23,1,24,20261249,role='warden')
    else:
        for z in range(sz):
            for x in (cx-2,cx+2):p.set(x,0,z,CARVED)
        for x in (4,18):box(p,x,1,5,x,7,5,STONE)
    box(p,cx-2,1,0,cx+2,4,sz-1,AIR)
    if name in ('freight_yard','dreamwood_shaping_court'):box(p,0,1,sz//2-2,sx-1,4,sz//2+2,AIR)
    p.set(7,1,10,B('minecraft:barrel',facing='up',open=False),{'id':'minecraft:barrel','CustomName':json.dumps({'text':'Production '+name}),'LootTable':'alfheim:chests/production/'+('records' if name in ('distribution_depot','mana_mill','guard_post') else 'stock')})
    def socket(face,target,child):
        x,z={'north':(cx,0),'south':(cx,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]
        p.jigsaw(x,1,z,'alfheim:'+target,'alfheim:'+target,'minecraft:empty' if child is None else 'alfheim:ancient/production_district/'+child,face+'_up',joint='aligned')
    if name!='freight_yard':socket('south',name+'_in',None)
    for face,child in LINKS.get(name,{}).items():socket(face,child+'_in',child)
    return lift(p)

def generate(root=ROOT):
    data=root/'kubejs/data/alfheim';files=[]
    def emit(path,value):
        p=data/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');files.append(p)
    for name in SIZES:
        p=data/'structures/ancient/production_district'/f'{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True);nbt.save(str(p),'',detail_nbt(build(name), 'production_district', name));files.append(p)
        emit(f'worldgen/template_pool/ancient/production_district/{name}.json',{'name':'alfheim:ancient/production_district/'+name,'fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'alfheim:ancient/production_district/'+name,'projection':'rigid','processors':'minecraft:empty'}}]})
    emit('worldgen/structure/production_district.json',{'type':'minecraft:jigsaw','biomes':'#alfheim:has_production_district','step':'surface_structures','terrain_adaptation':'beard_thin','spawn_overrides':{},'start_pool':'alfheim:ancient/production_district/freight_yard','size':3,'start_height':{'absolute':-DEPTH},'project_start_to_heightmap':'WORLD_SURFACE_WG','max_distance_from_center':116,'use_expansion_hack':False})
    emit('worldgen/structure_set/production_district.json',{'structures':[{'structure':'alfheim:production_district','weight':1}],'placement':{'type':'minecraft:random_spread','spacing':56,'separation':32,'salt':101220267}})
    emit('tags/worldgen/biome/has_production_district.json',{'replace':False,'values':HOME_BIOMES})
    for table,entries in {'records':[('minecraft:paper',6),('minecraft:book',4),('minecraft:ink_sac',2)],'stock':[('minecraft:paper',3),('minecraft:clay_ball',3),('minecraft:calcite',2),('minecraft:bread',2)]}.items():
        emit(f'loot_tables/chests/production/{table}.json',{'type':'minecraft:chest','pools':[{'rolls':{'type':'minecraft:uniform','min':2,'max':4},'entries':[{'type':'minecraft:item','name':item,'weight':weight,'functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':1,'max':3}}]} for item,weight in entries]}]})
    return files

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-root',default=str(ROOT));args=ap.parse_args();print(f'Production District: {len(generate(Path(args.output_root).resolve()))} files')
