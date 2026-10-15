"""Wave-1 Elder Lineage Precinct: one connected estate, no member structure sets."""
import argparse
import json
from pathlib import Path
import nbt
from district_refit import detail_nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,bed,elven_remains,skeletal_remains,stone_debris,HOME_BIOMES

ROOT=Path(__file__).resolve().parents[1]
DEPTH=8
STONE=B('alfheim:ivory_livingrock_bricks')
CARVED=B('alfheim:moonstone_livingrock_carved')
FLOOR=B('alfheim:ivory_livingrock_polished')
WOOD=B('botania:dreamwood_planks')
AIR=B('minecraft:air')
SIZES={'palace_center':(47,32,47),'ancestral_gallery':(31,30,47),
       'family_residence':(31,30,47),'ancestor_court':(47,18,40),
       'family_mausoleum':(47,30,40),'gate_court':(47,22,32),
       'retainer_house':(39,25,31),'household_service':(39,25,31),
       'processional_entry':(23,14,32)}
# face -> child; every pool has exactly one choice and incoming sockets face south.
LINKS={'palace_center':{'east':'ancestral_gallery','west':'family_residence',
                      'north':'ancestor_court','south':'gate_court'},
       'ancestor_court':{'north':'family_mausoleum'},
       'gate_court':{'west':'retainer_house','east':'household_service','north':'processional_entry'}}
# Gate court arrives turned through 180 degrees: its local north points outward south.


def royal(p,x,y,z,name,facing='north'):
    p.set(x,y,z,B('alfheim:'+name,facing=facing))


def cache(p,name):
    p.set(7,1,10,B('minecraft:barrel',facing='up',open=False),
          {'id':'minecraft:barrel','CustomName':json.dumps({'text':'Lineage '+name}),
           'LootTable':f'alfheim:chests/lineage/{"records" if name in ("palace_center","ancestral_gallery","family_mausoleum") else "household"}'})


def shell(name,closed=True,eave=13):
    sx,sy,sz=SIZES[name];p=Piece(sx,sy,sz)
    # Entire occupied volume is explicit, including destroyed roof and edge ports.
    box(p,0,1,0,sx-1,sy-1,sz-1,AIR)
    box(p,0,0,0,sx-1,0,sz-1,FLOOR)
    for x in range(sx):
        for z in (0,sz-1):p.set(x,0,z,CARVED)
    for z in range(sz):
        for x in (0,sx-1):p.set(x,0,z,CARVED)
    if closed:
        for x in range(1,sx-1):
            for z in (1,sz-2):box(p,x,1,z,x,eave,z,STONE)
        for z in range(2,sz-2):
            for x in (1,sx-2):box(p,x,1,z,x,eave,z,STONE)
        for x in (2,sx-3):
            for z in (2,sz-3):
                box(p,x,1,z,x,eave+1,z,B('feywild:elven_quartz_pillar',axis='y'))
                p.set(x,eave+2,z,CARVED)
        # Tall, layered windows and an interrupted cornice/roof skirt.
        for z in range(7,sz-6,9):
            for x in (1,sx-2):
                box(p,x,4,z,x,8,z+1,B('botania:elf_glass'))
                for zz in (z-1,z+2):box(p,x,3,zz,x,9,zz,CARVED)
        for x in range(2,sx-2):
            for z in (2,sz-3):
                if (x*7+z*3)%11>2:
                    p.set(x,eave+1,z,B('alfheim:ivory_livingrock_slab',type='top',waterlogged=False))
    return p


def stele(p,x,z):
    for dy,part in enumerate(('base','mid','crown')):
        royal(p,x,1+dy,z,'royal_lineage_stele_'+part)


def bench(p,x,z,facing='north'):
    for dx,part in enumerate(('left','right')):royal(p,x+dx,1,z,'royal_audience_bench_'+part,facing)


def desk(p,x,z):
    royal(p,x,1,z,'royal_writing_desk_left');royal(p,x+1,1,z,'royal_writing_desk_right')


def canopy_bed(p,x,z):
    for dz,part in enumerate(('head','middle','foot')):
        for dx,side in enumerate(('left','right')):
            royal(p,x+dx,1,z+dz,f'royal_canopy_bed_{part}_{side}')


def mounted_banner(p,x,y,z,facing):
    dx,dz={'north':(0,-1),'south':(0,1),'east':(1,0),'west':(-1,0)}[facing]
    p.set(x-dx,y,z-dz,STONE)
    royal(p,x,y,z,'royal_wall_banner',facing)


def build(name):
    p=shell(name,closed=name not in ('ancestor_court','gate_court','processional_entry'))
    sx,sy,sz=p.size;cx=sx//2
    if name=='palace_center':
        for z in (8,18,28,38):
            for x in (12,34):
                box(p,x,1,z,x,16,z,B('feywild:elven_quartz_pillar',axis='y'))
                p.set(x,17,z,CARVED)
            for x in range(12,35):
                y=18+min(6,x-12,34-x)
                p.set(x,y,z,B('botania:dreamwood_log',axis='x'))
        for x0,x1 in ((4,9),(37,42)):
            box(p,x0,8,4,x1,8,42,WOOD)
            for z in (5,15,25,35):box(p,(x0+x1)//2,1,z,(x0+x1)//2,7,z,STONE)
        for x in (10,36):
            for i in range(8):p.set(x,1+i,12+i,B('botania:dreamwood_stairs',facing='south',half='bottom',shape='straight',waterlogged=False))
            box(p,min(x,4 if x==10 else 37),8,20,max(x,9 if x==10 else 42),8,22,WOOD)
        for x in (8,36):
            for z in (8,34):stele(p,x,z)
        bench(p,14,14);bench(p,30,14)
        desk(p,6,8);royal(p,38,1,8,'royal_tall_cabinet')
        royal(p,9,1,30,'royal_mana_brazier');royal(p,37,1,30,'royal_mana_brazier')
        for x in (8,37):mounted_banner(p,x,5,44,'north')
        # Shelter conversion occupies side galleries; ceremonial cross remains open.
        for x in (6,39):
            for z in (13,30):bed(p,x,1,z,'purple')
        elven_remains(p,15,1,34,20261012)
    elif name=='ancestral_gallery':
        for z in (7,17,27,37):
            stele(p,5,z);stele(p,25,z)
            bench(p,8,z)
        for z in (12,32):mounted_banner(p,2,5,z,'east')
        desk(p,6,41);royal(p,25,1,40,'royal_tall_cabinet')
        royal(p,4,1,22,'royal_mana_brazier')
        stone_debris(p,24,1,12,20261013,3)
    elif name=='family_residence':
        for z in (6,24):
            for x in (5,22):canopy_bed(p,x,z)
        for z in (14,34):
            box(p,2,1,z,11,7,z,STONE);box(p,19,1,z,28,7,z,STONE)
            mounted_banner(p,4,5,z-1,'north');mounted_banner(p,26,5,z-1,'north')
        box(p,11,1,2,11,7,14,STONE)
        desk(p,4,40);royal(p,24,1,40,'royal_tall_cabinet')
        # One inner family room is deliberately sealed; the estate link remains open.
        for dy,part in enumerate(('base','middle','crown')):
            royal(p,7,1+dy,14,'elder_grave_door_left_'+part)
            royal(p,8,1+dy,14,'elder_grave_door_right_'+part)
        elven_remains(p,21,1,35,20261014)
    elif name=='ancestor_court':
        box(p,5,0,7,18,0,28,STONE)
        box(p,6,1,8,17,1,27,B('minecraft:water',level=0))
        for x in range(5,19):
            for z in (7,28):p.set(x,1,z,CARVED)
        for z in range(8,28):
            for x in (5,18):p.set(x,1,z,CARVED)
        for z in (5,15,25):stele(p,3,z)
        # Common emergency burials intrude on the formal eastern garden, not the axis.
        box(p,31,0,8,42,0,30,B('minecraft:coarse_dirt'))
        for z in (11,20,28):skeletal_remains(p,34,1,z,20261020+z,cloth=True)
        bench(p,29,34);royal(p,8,1,33,'royal_pedestal_planter')
    elif name=='family_mausoleum':
        for x in (10,34):
            for z in (9,23):
                box(p,x-2,0,z-1,x+2,0,z+3,CARVED)
                for dz,part in enumerate(('head','middle','foot')):
                    royal(p,x,1,z+dz,'elder_sarcophagus_'+part)
        for x in (5,17,29,41):
            for z in (7,19,31):box(p,x,1,z,x,14,z,B('feywild:elven_quartz_pillar',axis='y'))
        for x in (18,28):
            for dy,part in enumerate(('base','body','crown')):royal(p,x,1+dy,30,'elder_statue_'+part)
        for z in (12,22,32):
            mounted_banner(p,2,5,z,'east');mounted_banner(p,44,5,z,'west')
        royal(p,8,1,33,'royal_mana_brazier');royal(p,36,1,33,'royal_mana_brazier')
    elif name=='gate_court':
        for x in (6,40):
            for z in (6,25):
                box(p,x,1,z,x,10,z,STONE);p.set(x,11,z,CARVED)
        for x in range(6,41):p.set(x,12,6,WOOD)
        for x in (10,34):bench(p,x,10)
        royal(p,6,1,19,'royal_weapon_rack_left');royal(p,7,1,19,'royal_weapon_rack_right')
        elven_remains(p,35,1,22,20261030,role='warden')
        p.set(34,1,24,CARVED)  # the north-facing abandoned guard hook has a backing
    elif name=='retainer_house':
        for x in (5,11,27,33):
            for z in (6,17):bed(p,x,1,z,'green')
        desk(p,7,24);royal(p,28,1,24,'royal_tall_cabinet')
        elven_remains(p,27,1,22,20261031)
        royal(p,3,1,14,'royal_mana_brazier')
    elif name=='household_service':
        for x in (5,11,27,33):p.set(x,1,7,B('minecraft:campfire',lit=False,signal_fire=False,waterlogged=False))
        for x0,x1 in ((4,15),(23,34)):box(p,x0,1,17,x1,1,17,WOOD)
        desk(p,5,24);royal(p,28,1,23,'royal_lidded_amphora')
        elven_remains(p,25,1,19,20261032,role='healer')
    else:
        for z in (6,24):
            for x in (4,18):box(p,x,1,z,x,7,z,STONE)
            for x in range(4,19):p.set(x,8,z,CARVED)
        royal(p,4,1,15,'royal_lineage_stele_base')
        royal(p,4,2,15,'royal_lineage_stele_mid');royal(p,4,3,15,'royal_lineage_stele_crown')
    # Reserve a full processional route before placing sockets; never clear another socket.
    box(p,cx-2,1,0,cx+2,4,sz-1,AIR)
    if name in ('palace_center','gate_court'):
        box(p,0,1,sz//2-2,sx-1,4,sz//2+2,AIR)
    cache(p,name)
    if name!='palace_center':socket(p,'south',name+'_in','minecraft:empty')
    for face,child in LINKS.get(name,{}).items():socket(p,face,child+'_in',child)
    return lift(p)


def socket(p,face,target,child):
    sx,_,sz=p.size
    x,z={'north':(sx//2,0),'south':(sx//2,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]
    # Axis already reserved. Local ports are always on explicit floor/headroom.
    p.jigsaw(x,1,z,'alfheim:'+target,'alfheim:'+target,
             'minecraft:empty' if child=='minecraft:empty' else 'alfheim:ancient/elder_lineage/'+child,
             face+'_up',joint='aligned')


def lift(p):
    assert p.dropped==0,p.dropped
    out=Piece(p.size[0],p.size[1]+DEPTH,p.size[2])
    for (x,y,z),(idx,be) in p.blocks.items():
        state=p.palette[idx];out.set(x,y+DEPTH,z,(state['Name'],state.get('Properties')),be)
    for x in range(p.size[0]):
        for z in range(p.size[2]):
            for y in range(DEPTH):out.set(x,y,z,STONE if y<DEPTH-2 else CARVED)
    assert max(out.size)<=48 and out.dropped==0,out.size
    return out


def generate(root=ROOT):
    data=root/'kubejs/data/alfheim';files=[]
    def emit(path,value):
        p=data/path;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');files.append(p)
    for name in SIZES:
        p=data/'structures/ancient/elder_lineage'/f'{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True)
        nbt.save(str(p),'',detail_nbt(build(name), 'elder_lineage', name));files.append(p)
        emit(f'worldgen/template_pool/ancient/elder_lineage/{name}.json',{
            'name':'alfheim:ancient/elder_lineage/'+name,'fallback':'minecraft:empty',
            'elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element',
                'location':'alfheim:ancient/elder_lineage/'+name,'projection':'rigid','processors':'minecraft:empty'}}]})
    emit('worldgen/structure/elder_lineage_precinct.json',{
        'type':'minecraft:jigsaw','biomes':'#alfheim:has_elder_lineage_precinct',
        'step':'surface_structures','terrain_adaptation':'beard_thin','spawn_overrides':{},
        'start_pool':'alfheim:ancient/elder_lineage/palace_center','size':3,
        'start_height':{'absolute':-DEPTH},'project_start_to_heightmap':'WORLD_SURFACE_WG',
        'max_distance_from_center':116,'use_expansion_hack':False})
    emit('worldgen/structure_set/elder_lineage_precinct.json',{
        'structures':[{'structure':'alfheim:elder_lineage_precinct','weight':1}],
        'placement':{'type':'minecraft:random_spread','spacing':56,'separation':32,'salt':101220263}})
    emit('tags/worldgen/biome/has_elder_lineage_precinct.json',{'replace':False,'values':HOME_BIOMES})
    for table,entries in {'household':[('minecraft:bread',4),('minecraft:paper',4),('minecraft:apple',3),('minecraft:wheat_seeds',2)],
                          'records':[('minecraft:book',4),('minecraft:paper',6),('botania:elf_quartz',2),('minecraft:purple_dye',2)]}.items():
        emit(f'loot_tables/chests/lineage/{table}.json',{'type':'minecraft:chest','pools':[
            {'rolls':{'type':'minecraft:uniform','min':2,'max':4},'entries':[
             {'type':'minecraft:item','name':item,'weight':weight,'functions':[
              {'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':1,'max':3}}]} for item,weight in entries]}]})
    return files


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-root',default=str(ROOT));args=ap.parse_args()
    files=generate(Path(args.output_root).resolve());print(f'Elder Lineage Precinct: 9 pieces, 9 pools, {len(files)} generated files')
