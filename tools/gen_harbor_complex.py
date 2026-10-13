"""Maritime complex with sparse, budget-limited approximate shore placement."""
import argparse
import json
from pathlib import Path
import nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,bed,elven_remains,stone_debris
from gen_elder_lineage import royal,bench,desk,mounted_banner,lift,STONE,CARVED,FLOOR,AIR,DEPTH

ROOT=Path(__file__).resolve().parents[1]
SIZES={'harbor_exchange':(47,30,47),'harbormaster_house':(39,26,47),
       'bonded_warehouse':(39,26,47),'wavebreak_pier':(47,20,39),
       'sunken_drydock':(47,24,31),'tide_temple':(39,28,31),
       'quay_court':(47,20,31),'signal_lighthouse':(31,38,31),
       'dockworker_housing':(39,24,31),'harbor_approach':(23,14,32)}
LINKS={'harbor_exchange':{'east':'harbormaster_house','west':'bonded_warehouse','north':'wavebreak_pier','south':'quay_court'},
       'wavebreak_pier':{'north':'sunken_drydock'},
       'bonded_warehouse':{'north':'tide_temple'},
       'quay_court':{'west':'signal_lighthouse','east':'dockworker_housing','north':'harbor_approach'}}

def build(name):
    sx,sy,sz=SIZES[name];cx=sx//2;p=Piece(sx,sy,sz)
    box(p,0,1,0,sx-1,sy-1,sz-1,AIR);box(p,0,0,0,sx-1,0,sz-1,FLOOR)
    if name not in ('wavebreak_pier','sunken_drydock','quay_court','harbor_approach'):
        for x in (1,sx-2):box(p,x,1,1,x,13,sz-2,STONE)
        for z in (1,sz-2):box(p,1,1,z,sx-2,13,z,STONE)
        for z in range(5,sz-3,8):
            for x in range(2,sx-2):
                if not (name=='harbor_exchange' and z>29 and x>cx):p.set(x,15+min(5,x//3,(sx-1-x)//3),z,B('botania:dreamwood_log',axis='x'))
    if name=='harbor_exchange':
        for z in (7,15,31,39):desk(p,5,z);bench(p,38,z)
        for x in (9,37):mounted_banner(p,x,5,44,'north')
        royal(p,40,1,10,'royal_tall_cabinet')
        stone_debris(p,32,1,39,20261500,3);elven_remains(p,9,1,34,20261501)
    elif name=='harbormaster_house':
        for z in (7,15,31,39):desk(p,5,z);royal(p,31,1,z,'royal_tall_cabinet')
        bed(p,29,1,24,'purple');mounted_banner(p,4,5,44,'north')
        elven_remains(p,29,1,35,20261502)
    elif name=='bonded_warehouse':
        for x in (5,27):
            for z in (7,31):box(p,x,1,z,x+6,2,z+3,B('botania:dreamwood_planks'))
        box(p,26,1,36,35,5,36,STONE);desk(p,5,23)
        elven_remains(p,29,1,40,20261503)
    elif name=='wavebreak_pier':
        for z in (7,30):
            for x in (5,16,30,41):box(p,x,1,z,x,7,z,CARVED)
        for x in (3,43):
            for z in range(4,35):
                if not (x==43 and 18<=z<=22):box(p,x,1,z,x,2,z,STONE)
        box(p,6,1,12,11,1,17,B('botania:dreamwood_planks'))
        elven_remains(p,35,1,29,20261504)
    elif name=='sunken_drydock':
        # Hull fragments stand beside the supported central maintenance causeway.
        for x in (7,33):
            for z in (7,13,20):box(p,x,1,z,x+5,1,z,B('botania:dreamwood_log',axis='x'))
        for x in (4,42):box(p,x,1,5,x,8,5,STONE)
        desk(p,5,26);elven_remains(p,35,1,26,20261505)
    elif name=='tide_temple':
        for x in (6,26):
            for z in (7,23):
                for dy,part in enumerate(('base','mid','crown')):royal(p,x,1+dy,z,'royal_lineage_stele_'+part)
        bench(p,5,16);bench(p,24,16)
        bed(p,5,1,11,'white');desk(p,5,24)
        elven_remains(p,29,1,25,20261506)
    elif name=='signal_lighthouse':
        # A walkable stair climbs to a surviving signal gallery beneath the broken crown.
        for x in (7,23):box(p,x,1,4,x,30,4,CARVED)
        box(p,5,12,5,12,12,24,FLOOR)
        for i in range(12):
            box(p,10,1,26-i,10,i+1,26-i,STONE)
            box(p,10,i+2,26-i,10,i+3,26-i,AIR)
            p.set(10,i+1,26-i,B('botania:dreamwood_stairs',facing='north',half='bottom',shape='straight',waterlogged=False))
        for z in range(5,15):p.set(12,13,z,B('minecraft:oak_fence',north=z>5,south=z<14,east=False,west=False,waterlogged=False))
        royal(p,7,13,7,'royal_mana_brazier')
        box(p,5,22,5,12,22,5,B('botania:elf_glass'))
        bed(p,23,1,23,'brown');desk(p,22,7)
        elven_remains(p,23,1,17,20261507)
    elif name=='dockworker_housing':
        for x in (5,11,27,33):
            for z in (6,15,24):bed(p,x,1,z,'brown')
        for z in (10,22):bench(p,5,z);royal(p,31,1,z,'royal_tall_cabinet')
        elven_remains(p,29,1,19,20261508)
    elif name=='quay_court':
        for z in (6,24):bench(p,5,z);bench(p,36,z)
        for x in (6,35):box(p,x,1,9,x+4,1,9,B('botania:dreamwood_planks'))
        mounted_banner(p,7,5,4,'south')
    else:
        for z in range(sz):
            for x in (cx-2,cx+2):p.set(x,0,z,CARVED)
    box(p,cx-2,1,0,cx+2,4,sz-1,AIR)
    if name in ('harbor_exchange','quay_court'):box(p,0,1,sz//2-2,sx-1,4,sz//2+2,AIR)
    p.set(7,1,10,B('minecraft:barrel',facing='up',open=False),{'id':'minecraft:barrel','CustomName':json.dumps({'text':'Harbor '+name}),'LootTable':'alfheim:chests/harbor/'+('records' if name in ('harbor_exchange','harbormaster_house','signal_lighthouse') else 'cargo')})
    def socket(face,target,child):
        x,z={'north':(cx,0),'south':(cx,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]
        p.jigsaw(x,1,z,'alfheim:'+target,'alfheim:'+target,'minecraft:empty' if child is None else 'alfheim:ancient/harbor_complex/'+child,face+'_up',joint='aligned')
    if name!='harbor_exchange':socket('south',name+'_in',None)
    for face,child in LINKS.get(name,{}).items():socket(face,child+'_in',child)
    out=lift(p)
    if name in ('harbor_exchange','sunken_drydock','tide_temple'):
        # Authored inundation is contained below the main quay, with a solid bed.
        for x0,x1 in ((10,17),(29,36)):
            z0,z1=(6,19)
            box(out,x0,DEPTH-2,z0,x1,DEPTH-1,z1,B('minecraft:water',level=0))
            box(out,x0,DEPTH,z0,x1,DEPTH,z1,AIR)
            for x in (x0-1,x1+1):
                for z in range(z0,z1+1):out.set(x,DEPTH+1,z,B('minecraft:oak_fence',north=z>z0,south=z<z1,east=False,west=False,waterlogged=False))
    return out

def generate(root=ROOT):
    data=root/'kubejs/data/alfheim';files=[]
    def emit(path,value):
        p=data/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');files.append(p)
    for name in SIZES:
        p=data/'structures/ancient/harbor_complex'/f'{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True);nbt.save(str(p),'',build(name).to_nbt());files.append(p)
        emit(f'worldgen/template_pool/ancient/harbor_complex/{name}.json',{'name':'alfheim:ancient/harbor_complex/'+name,'fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'alfheim:ancient/harbor_complex/'+name,'projection':'rigid','processors':'minecraft:empty'}}]})
    for sx,sz in sorted({(size[0],size[2]) for size in SIZES.values()}):
        for lift_by in (2,4,6):
            footer=Piece(sx,lift_by,sz);box(footer,0,0,0,sx-1,lift_by-1,sz-1,STONE)
            p=data/'structures/ancient/harbor_complex/foundations'/f'{sx}x{sz}_{lift_by}.nbt';p.parent.mkdir(parents=True,exist_ok=True)
            nbt.save(str(p),'',footer.to_nbt());files.append(p)
    emit('worldgen/structure/harbor_complex.json',{'type':'alfheim_companion:shoreline_harbor','biomes':'#alfheim:has_harbor_complex','step':'surface_structures','terrain_adaptation':'none','spawn_overrides':{}})
    emit('worldgen/structure_set/harbor_complex.json',{'structures':[{'structure':'alfheim:harbor_complex','weight':1}],
        'placement':{'type':'minecraft:random_spread','spacing':80,'separation':48,'salt':101320269}})
    emit('tags/worldgen/biome/has_harbor_complex.json',{'replace':False,'values':['alfheim:tidewood_shore','alfheim:mistbark_shore','alfheim:sporebank_shore']})
    for table,entries in {'records':[('minecraft:paper',6),('minecraft:book',4),('minecraft:ink_sac',2)],'cargo':[('minecraft:bread',3),('minecraft:white_wool',3),('minecraft:clay_ball',2),('minecraft:apple',2)]}.items():
        emit(f'loot_tables/chests/harbor/{table}.json',{'type':'minecraft:chest','pools':[{'rolls':{'type':'minecraft:uniform','min':2,'max':4},'entries':[{'type':'minecraft:item','name':item,'weight':weight,'functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':1,'max':3}}]} for item,weight in entries]}]})
    return files

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-root',default=str(ROOT));args=ap.parse_args();print(f'Harbor Complex: {len(generate(Path(args.output_root).resolve()))} files')
