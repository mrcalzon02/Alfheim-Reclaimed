"""Six military/civil-order archetypes in one connected ruined command precinct."""
import json
from pathlib import Path
import nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,bed,elven_remains,HOME_BIOMES
from gen_elder_lineage import royal,bench,desk,mounted_banner,lift,STONE,CARVED,FLOOR,AIR,DEPTH

ROOT=Path(__file__).resolve().parents[1]
SIZES={'border_keep':(47,38,47),'warden_tower':(31,38,31),
       'watch_captain_house':(39,26,31),'gate_barracks':(39,26,31),
       'discipline_guard_court':(39,20,39),'last_muster_ground':(47,18,39)}
LINKS={'border_keep':{'north':'warden_tower','east':'watch_captain_house',
                     'west':'gate_barracks','south':'discipline_guard_court'},
       'discipline_guard_court':{'north':'last_muster_ground'}}

def build(name):
    sx,sy,sz=SIZES[name];cx=sx//2;p=Piece(sx,sy,sz)
    box(p,0,0,0,sx-1,0,sz-1,FLOOR);box(p,0,1,0,sx-1,sy-1,sz-1,AIR)
    enclosed=name not in ('discipline_guard_court','last_muster_ground')
    height=25 if name=='warden_tower' else 14 if name=='border_keep' else 10
    for x in (1,sx-2):box(p,x,1,1,x,height if enclosed else 3,sz-2,STONE)
    for z in (1,sz-2):box(p,1,1,z,sx-2,height if enclosed else 3,z,STONE)
    if enclosed:
        for z in range(7,sz-5,9):
            for x in (1,sx-2):box(p,x,5,z,x,7,z,B('botania:elf_glass'))
        # Interrupted roof ribs expose deliberately authored air above the ruin.
        for z in range(6,sz-5,9):
            for x in range(2,sx-2):
                if x<cx or z<sz//2:p.set(x,height+1,z,B('botania:dreamwood_log',axis='x'))
    if name=='border_keep':
        # Inner court, patched breach, sealed ordinary supply magazine.
        for x in (11,35):box(p,x,1,9,x,6,35,CARVED)
        box(p,35,1,27,35,4,32,AIR)
        box(p,1,1,31,1,5,37,AIR)
        box(p,2,1,33,2,3,36,B('botania:dreamwood_planks'))
        for z in (7,16):royal(p,39,1,z,'royal_tall_cabinet')
        royal(p,16,1,34,'royal_weapon_rack_left');royal(p,17,1,34,'royal_weapon_rack_right')
        box(p,37,1,4,37,5,20,STONE);box(p,37,1,4,43,5,4,STONE)
        box(p,37,1,20,43,5,20,STONE)
        desk(p,16,8);mounted_banner(p,23,7,2,'south')
        elven_remains(p,8,1,34,20261321)
    elif name=='warden_tower':
        # A supported stair reaches the surviving signal platform; missing far corner.
        for k in range(14):
            z=7+k
            box(p,4,1,z,6,k+1,z,STONE)
            for x in range(4,7):p.set(x,k+1,z,B('alfheim:ivory_livingrock_stairs',facing='south',half='bottom',shape='straight',waterlogged=False))
        box(p,4,15,21,22,15,25,FLOOR)
        for x in (4,22):box(p,x,16,21,x,18,25,CARVED)
        box(p,21,16,23,21,20,23,B('botania:dreamwood_log',axis='y'))
        p.set(21,21,23,B('botania:elf_glass'));desk(p,19,8)
        elven_remains(p,20,1,18,20261322)
    elif name=='watch_captain_house':
        desk(p,9,8);royal(p,30,1,8,'royal_tall_cabinet')
        royal(p,28,1,5,'royal_weapon_rack_left');royal(p,29,1,5,'royal_weapon_rack_right')
        bed(p,29,1,21,'gray');bench(p,7,22)
        box(p,27,1,18,33,1,18,B('botania:dreamwood_planks'))
        for k in range(6):
            box(p,4,1,13+k,6,k+1,13+k,STONE)
        box(p,4,7,19,12,7,24,FLOOR)
        elven_remains(p,10,1,23,20261323)
    elif name=='gate_barracks':
        for x in (5,29):
            for z in (7,15,23):bed(p,x,1,z,'gray')
        for z in (7,23):desk(p,10,z)
        for x in (cx-4,cx+4):box(p,x,1,4,x,5,8,CARVED)
        for x in (cx-3,cx+3):
            for dy,half in enumerate(('lower','upper')):p.set(x,1+dy,5,B('minecraft:iron_door',facing='south',half=half,hinge='left',open=False,powered=False))
        elven_remains(p,13,1,5,20261324);elven_remains(p,25,1,5,20261325)
    elif name=='discipline_guard_court':
        for x in (5,29):
            for z in (8,25):bed(p,x,1,z,'white')
        for x in range(4,13):box(p,x,1,15,x,3,15,B('minecraft:iron_bars',north=False,south=False,east=x<12,west=x>4,waterlogged=False))
        box(p,26,1,15,33,1,16,B('botania:dreamwood_planks'));desk(p,26,21)
        bench(p,6,32);elven_remains(p,30,1,30,20261326,role='healer')
    else:
        for x in (8,16,30,38):
            for z in (8,16):p.set(x,1,z,CARVED)
        for x in (5,35):
            box(p,x,1,5,x+5,1,6,B('botania:dreamwood_planks'))
            bed(p,x,1,20,'white');bed(p,x,1,24,'white')
        # Two shallow, contained burial trenches beside the roll-call lanes.
        for x in (6,35):
            box(p,x,0,29,x+4,0,33,AIR)
            elven_remains(p,x+2,0,31,20261327+x)
        bench(p,20,26)
    # Every join has a broad, level passage. Upper stair routes are separate.
    box(p,cx-2,1,0,cx+2,4,sz-1,AIR)
    if name=='border_keep':box(p,0,1,sz//2-2,sx-1,4,sz//2+2,AIR)
    p.set(7,1,10,B('minecraft:barrel',facing='up',open=False),{'id':'minecraft:barrel',
        'CustomName':json.dumps({'text':'Warden '+name}),
        'LootTable':'alfheim:chests/warden/'+('records' if name in ('border_keep','warden_tower','watch_captain_house') else 'supplies')})
    def socket(face,child,incoming=False):
        x,z={'north':(cx,0),'south':(cx,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]
        target=(name if incoming else child)+'_in'
        p.jigsaw(x,1,z,'alfheim:'+target,'alfheim:'+target,'minecraft:empty' if incoming else 'alfheim:ancient/military_warden/'+child,face+'_up',joint='aligned')
    if name!='border_keep':socket('south',None,True)
    for face,child in LINKS.get(name,{}).items():socket(face,child)
    return lift(p)

def generate(root=ROOT):
    data=root/'kubejs/data/alfheim';files=[]
    def emit(path,value):
        p=data/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');files.append(p)
    for name in SIZES:
        p=data/'structures/ancient/military_warden'/f'{name}.nbt';p.parent.mkdir(parents=True,exist_ok=True);nbt.save(str(p),'',build(name).to_nbt());files.append(p)
        emit(f'worldgen/template_pool/ancient/military_warden/{name}.json',{'name':'alfheim:ancient/military_warden/'+name,'fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'alfheim:ancient/military_warden/'+name,'projection':'rigid','processors':'minecraft:empty'}}]})
    emit('worldgen/structure/military_warden.json',{'type':'minecraft:jigsaw','biomes':'#alfheim:has_military_warden','step':'surface_structures','terrain_adaptation':'beard_thin','spawn_overrides':{},'start_pool':'alfheim:ancient/military_warden/border_keep','size':3,'start_height':{'absolute':-DEPTH},'project_start_to_heightmap':'WORLD_SURFACE_WG','max_distance_from_center':116,'use_expansion_hack':False})
    emit('tags/worldgen/biome/has_military_warden.json',{'replace':False,'values':HOME_BIOMES})
    for table,items in {'records':['minecraft:paper','minecraft:book','minecraft:ink_sac'],'supplies':['minecraft:bread','minecraft:white_wool','minecraft:string']}.items():
        emit(f'loot_tables/chests/warden/{table}.json',{'type':'minecraft:chest','pools':[{'rolls':2,'entries':[{'type':'minecraft:item','name':item} for item in items]}]})
    return files

if __name__=='__main__':print('Military/Warden:',len(generate()),'files')
