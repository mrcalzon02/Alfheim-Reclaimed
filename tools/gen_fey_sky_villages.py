"""Continuity Works provider for eight substantial, inhabitable seasonal sky villages."""
import gzip,hashlib,json,math,random,sys
from pathlib import Path
import nbt
from structure_nbt import Piece
from gen_pixie_settlements import CULTURES,B,box,salt_for

ROOT=Path(__file__).resolve().parents[1]
SURFACE=14
THEMES={'spring':'Blossom bough courts','summer':'Suncomb terraces','autumn':'Lanterncap log borough','winter':'Frostbell glass gardens'}
HOUSES=[[(29,25),(45,20),(61,25),(74,36),(76,52),(66,73),(49,77),(30,72),(20,57),(19,39)],
        [(26,31),(38,24),(56,22),(70,29),(77,45),(73,63),(60,74),(43,76),(25,66),(19,48)]]
LOGS=[[(34,43),(64,58)],[(33,56),(63,40)]]
AIR=B('minecraft:air')


def loot_barrel(p,kind,x,y,z):
    p.set(x,y,z,B('minecraft:barrel',facing='up',open=False),
          {'id':'minecraft:barrel','LootTable':f'alfheim:chests/fairy_island_{kind}'})


def island_loot(kind,c):
    def item(name,weight,lo,hi):
        return {'type':'minecraft:item','name':name,'weight':weight,
                'functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':lo,'max':hi}}]}
    return {'type':'minecraft:chest','pools':[
        {'rolls':{'type':'minecraft:uniform','min':2,'max':4},'entries':[
            item('minecraft:bread',5,1,3),item('minecraft:apple',4,1,3),
            item('minecraft:sugar',3,1,5),item('minecraft:wheat_seeds',4,2,7),
            item('minecraft:stick',3,2,6),item('minecraft:honey_bottle',1,1,2)]},
        {'rolls':{'type':'minecraft:uniform','min':1,'max':3},'entries':[
            *(item(f,3,1,4) for f in c['flowers']),item(c['sapling'],1,1,1)]}]}

def plan(kind,variant):
    if kind=='summer':
        houses=[(20,43),(27,33),(35,42),(37,61),(46,69),(55,59),(62,39),(72,45),(72,59),(53,27)]
        logs=[(42,34),(59,51)];gardens=[(25,55),(61,68)]
    elif kind=='autumn':
        houses=[(21,41),(30,31),(35,43),(34,62),(45,68),(53,60),(65,36),(75,46),(70,60),(52,26)]
        logs=[(43,35),(60,52)];gardens=[(25,54),(59,70)]
    elif kind=='winter':
        houses=[(21,43),(30,32),(35,45),(37,63),(46,71),(54,61),(65,38),(74,47),(70,61),(53,27)]
        logs=[(42,36),(59,51)];gardens=[(26,56),(61,70)]
    else:
        houses=[(23,43),(29,33),(36,45),(38,62),(46,70),(53,59),(64,40),(73,48),(66,60),(52,28)]
        logs=[(40,35),(59,51)];gardens=[(28,55),(60,71)]
    if variant:
        # A genuine alternative street plan, rather than another roll of the same house pool.
        offsets=[(0,2),(-1,0),(1,1),(-2,0),(1,-1),(1,0),(1,-2),(-2,1),(2,0),(0,2)]
        houses=[(96-z-dz,x+dx) for (x,z),(dx,dz) in zip(houses,offsets)]
        logs=[(96-z-1,x-1) if i==0 else (96-z,x+1) for i,(x,z) in enumerate(logs)]
        gardens=[(96-z+1,x-1) if i==0 else (96-z+2,x+1) for i,(x,z) in enumerate(gardens)]
    return houses,logs,gardens

def leaves(c,i=0):return B(c['leaves'][i%len(c['leaves'])],persistent=True,distance=1)
def lantern(p,c,x,y,z):p.set(x,y,z,B(c['light'],hanging=False,waterlogged=False))
def disk(p,x,y,z,r,block):
    for dx in range(-math.ceil(r),math.ceil(r)+1):
        for dz in range(-math.ceil(r),math.ceil(r)+1):
            if dx*dx+dz*dz<=r*r:p.set(x+dx,y,z+dz,block)

def land(kind,variant,c):
    p=Piece(96,48,96);ground={};phase=variant*.8
    for x in range(2,94):
        for z in range(2,94):
            xx,zz=(z,96-x) if variant else (x,z)
            dx,dz=xx-47.5,zz-47.5;a=math.atan2(dz,dx)
            season=list(CULTURES).index(kind)
            # An elongated, asymmetric natural landform with coves and promontories.
            # No rotational flower, crescent, peanut or circular settlement outline.
            d=math.hypot(dx/1.05,dz/.77)
            edge=40+2.5*math.sin(a*3+season*.7)+1.4*math.sin(a*7+1.1)+1.5*math.cos(a+season)
            if d>edge:continue
            height=16+round(1.5*math.sin(xx*.07+season)+1.2*math.cos(zz*.10)+1.5)
            ground[(x,z)]=height;bottom=max(0,height-int(3+(edge-d)*.65+1.5*math.sin(x*.21+z*.13)))
            for y in range(bottom,height+1):
                block=B(c['surface']) if y==height else B(c['soil']) if y>=height-2 else B('botania:livingrock')
                if y<6 and (x+z)%11==0:block=B(c['accent'])
                p.set(x,y,z,block)
    rng=random.Random(2026101700+list(CULTURES).index(kind)*10+variant)
    # Connected branching root pendants, rather than a thin circular plate.
    for i in range(25):
        a=rng.random()*math.tau;r=rng.uniform(17,35);x,z=round(48+math.cos(a)*r),round(48+math.sin(a)*r)
        if (x,z) not in ground:continue
        for y in range(rng.randrange(3),ground[(x,z)]):p.set(x,y,z,B(c['log'],axis='y'))
        for j in range(4):p.set(x+j*(1 if i%2 else -1),9+j//2,z,B(c['log'],axis='x'))
    return p,ground,rng

class Raised:
    def __init__(self,p,offset):self.p=p;self.offset=offset
    def set(self,x,y,z,block,be=None):return self.p.set(x,y+self.offset,z,block,be)

def terrace(p,c,ground,x,z,r):
    height=ground.get((x,z),17)
    for dx in range(-r,r+1):
        for dz in range(-r,r+1):
            xx,zz=x+dx,z+dz
            if not (0<=xx<96 and 0<=zz<96):continue
            old=ground.get((xx,zz),height)
            for y in range(max(0,min(old,height)-3),max(old,height)+1):
                p.set(xx,y,zz,AIR if y>height else B(c['surface']) if y==height else B(c['soil']))
            ground[(xx,zz)]=height
    return height

def path(p,c,ground,a,b):
    length=max(abs(b[0]-a[0]),abs(b[1]-a[1]));points=[]
    for t in range(length+1):
        x=round(a[0]+(b[0]-a[0])*t/max(1,length));z=round(a[1]+(b[1]-a[1])*t/max(1,length))
        for dx,dz in ((0,0),(1,0),(0,1)):
            xx,zz=x+dx,z+dz;height=ground.get((xx,zz),17)
            p.set(xx,height,zz,B(c['wood']));ground[(xx,zz)]=height
            for h in (height+1,height+2):p.set(xx,h,zz,AIR)
        points.append((x,z))
    return points

def cottage(p,kind,c,x,z,index):
    y=15;wood=B(c['wood']);log=B(c['log'],axis='y');roof=B(c['roof']);wall=wood
    if kind=='autumn':wall=B('minecraft:mushroom_stem')
    if kind=='winter':wall=B('minecraft:snow_block')
    box(p,x-2,y,z-2,x+2,y,z+2,wood)
    for h in range(1,4):
        for dx in range(-2,3):
            for dz in range(-2,3):
                p.set(x+dx,y+h,z+dz,log if abs(dx)==2 and abs(dz)==2 else wall if abs(dx)==2 or abs(dz)==2 else AIR)
    # Tiny fey doorway, recessed windows, porch and shutters.
    for h in (1,2):p.set(x,y+h,z-2,AIR)
    p.set(x,y+3,z-2,B(c['wood']+'_slab',type='top',waterlogged=False))
    for dx in (-2,2):
        p.set(x+dx,y+2,z,B('minecraft:yellow_stained_glass' if kind!='winter' else 'minecraft:light_blue_stained_glass'))
        p.set(x+dx,y+1,z,wood)
    box(p,x-1,y,z-4,x+1,y,z-3,wood);lantern(p,c,x-1,y+1,z-3)
    loot_barrel(p,kind,x-1,y+1,z+1)
    p.set(x+1,y+1,z+1,B('minecraft:red_carpet' if kind=='autumn' else 'minecraft:light_blue_carpet' if kind=='winter' else 'minecraft:yellow_carpet'))
    if kind=='spring':
        for h,r in ((4,3.5),(5,2.6),(6,1.6)):disk(p,x,y+h,z,r,leaves(c,index+h))
        p.set(x,y+7,z,B('minecraft:flowering_azalea'));p.set(x+2,y+5,z,B(c['flowers'][index%3]))
        if index%3==1:
            for h,r in ((7,1.5),(8,1.2),(9,.5)):disk(p,x,y+h,z,r,leaves(c,index))
            p.set(x,y+10,z,B('minecraft:pink_wool'))
        elif index%3==2:
            for dx,dz in ((-3,0),(3,0),(0,3)):disk(p,x+dx,y+4,z+dz,1.5,leaves(c,index))
    elif kind=='summer':
        # Honeycomb hexagonal sun pod with an open timber verandah.
        for h,r in ((4,3.5),(5,2.4),(6,1.2)):disk(p,x,y+h,z,r,roof)
        box(p,x-3,y,z-3,x+3,y,z-3,wood)
        for dx in (-3,3):box(p,x+dx,y+1,z-3,x+dx,y+4,z-3,log)
        box(p,x-3,y+4,z-3,x+3,y+4,z-3,B('minecraft:yellow_wool'))
        if index%3==1:
            box(p,x,y+6,z,x,y+10,z,log)
            for k in range(-3,4):
                if abs(k)>1:p.set(x+k,y+10,z,B('minecraft:white_wool'));p.set(x,y+10+k,z,B('minecraft:yellow_wool'))
        elif index%3==2:
            for h in range(4):box(p,x-2+h//2,y+6+h,z-2,x+2-h//2,y+6+h,z+2,B('minecraft:orange_wool'))
    elif kind=='autumn':
        # Broad toadstool caps, alternating red and brown village roofs.
        cap=B('minecraft:red_mushroom_block' if index%2 else 'minecraft:brown_mushroom_block')
        for h,r in ((4,3.6),(5,3),(6,1.7)):disk(p,x,y+h,z,r,cap)
        box(p,x+2,y+1,z+1,x+2,y+7,z+1,B('minecraft:bricks'));p.set(x+2,y+8,z+1,B('minecraft:campfire',lit=False,signal_fire=False,waterlogged=False,facing='north'))
        if index%3==1:
            # Fallen-log annexes are visibly different from mushroom cottages.
            for yy in range(y+1,y+5):
                for dx in range(-2,3):
                    for dz in range(3,8):
                        if (dx/2.5)**2+((yy-y-2.5)/2.5)**2<=1:p.set(x+dx,yy,z+dz,B(c['log'],axis='z') if abs(dx)==2 or yy in (y+1,y+4) else AIR)
            p.set(x,y+2,z+7,B('alfheim_companion:autumn_fey_apartment',facing='south'),{'id':'alfheim_companion:fey_home','Nursery':nbt.Byte(0)})
    else:
        for h in range(4):
            w=3-h
            for dx in range(-w,w+1):box(p,x+dx,y+4+h,z-3,x+dx,y+4+h,z+3,roof if h%2 else B('minecraft:snow_block'))
        p.set(x,y+8,z,B('minecraft:end_rod',facing='up'))
        for dx in (-3,3):p.set(x+dx,y+3,z-2,B('minecraft:chain',axis='y',waterlogged=False));lantern(p,c,x+dx,y+2,z-2)
        if index%3==1:
            for h,r in ((8,1.5),(9,1.2),(10,.6)):disk(p,x,y+h,z,r,B('minecraft:packed_ice'))
            lantern(p,c,x,y+11,z)
        elif index%3==2:
            for dx in (-2,2):
                for h in (1,2,3):box(p,x+dx,y+h,z-1,x+dx,y+h,z+1,B('minecraft:light_blue_stained_glass'))

def apartment_tree(p,kind,c,x,z):
    # Full-size hollow tree stump, with three tiny modeled apartments in its bark.
    for y in range(15,31):
        for dx in range(-3,4):
            for dz in range(-3,4):
                r=math.hypot(dx,dz)
                if r<=3.35:p.set(x+dx,y,z+dz,B(c['log'],axis='y') if r>=2.1 else AIR)
    for y in (15,20,25):
        disk(p,x,y,z,2.2,B(c['wood']))
        p.set(x,y+1,z-3,B('alfheim_companion:'+kind+'_fey_apartment',facing='north'),{'id':'alfheim_companion:fey_home','Nursery':nbt.Byte(1)})
        box(p,x-1,y,z-5,x+1,y,z-3,B(c['wood']))
        for dx in (-1,1):p.set(x+dx,y+1,z-5,B(c['wood']+'_fence',north=False,south=False,east=False,west=False,waterlogged=False))
        lantern(p,c,x+2,y+1,z-3)
        for dx in (-3,3):p.set(x+dx,y+2,z,B('minecraft:yellow_stained_glass'))
    for h,r in ((29,5.2),(30,5.8),(31,5.1),(32,4),(33,2.8),(34,1.4)):disk(p,x,h,z,r,leaves(c,h))
    for dx,dz in ((-5,0),(5,0),(0,5)):
        for i in range(4):p.set(x+round(dx*i/4),28+i//3,z+round(dz*i/4),B(c['log'],axis='x' if dx else 'z'))

def garden(p,kind,c,x,z):
    for dx in range(-4,5):
        for dz in range(-4,5):
            xx,zz=x+dx,z+dz
            if abs(dx)==4 or abs(dz)==4:p.set(xx,14,zz,B(c['wood']))
            elif dx==0:p.set(xx,14,zz,B('minecraft:water',level=0))
            else:
                p.set(xx,14,zz,B('minecraft:farmland',moisture=7));crop,age=c['crops'][(dx+dz)%2];p.set(xx,15,zz,B(crop,age=age))
    if kind=='winter':
        # The frost climate gets a functional, lit greenhouse with open fey entrances.
        for dx in range(-4,5):
            for dz in range(-4,5):
                p.set(x+dx,19,z+dz,B('minecraft:glass'))
                if abs(dx)==4 or abs(dz)==4:
                    for y in (15,16,17,18):p.set(x+dx,y,z+dz,B('minecraft:glass'))
        for y in (15,16):p.set(x,y,z-4,AIR);p.set(x,y,z+4,AIR)
    for dx,dz in ((-4,-4),(4,4)):
        p.set(x+dx,15,z+dz,B('minecraft:oak_fence'));lantern(p,c,x+dx,16,z+dz)

def landmark(p,kind,c):
    x=z=48
    disk(p,x,14,z,7,B(c['accent']));disk(p,x,15,z,4,B(c['wood']))
    if kind=='spring':
        disk(p,x,15,z,3,B('minecraft:water',level=0))
        for a in range(0,360,60):
            dx,dz=round(math.cos(math.radians(a))*5),round(math.sin(math.radians(a))*5)
            box(p,x+dx,15,z+dz,x+dx,21,z+dz,B(c['log'],axis='y'));disk(p,x+dx,22,z+dz,2.5,leaves(c,a));lantern(p,c,x+dx,20,z+dz-1)
    elif kind=='summer':
        for i in range(8):
            a=i*math.tau/8;dx,dz=round(math.cos(a)*5),round(math.sin(a)*5)
            box(p,x+dx,15,z+dz,x+dx,19,z+dz,B(c['log'],axis='y'));disk(p,x+dx,20,z+dz,1.6,B('minecraft:yellow_wool' if i%2 else 'minecraft:orange_wool'));lantern(p,c,x+dx,18,z+dz)
        box(p,47,15,47,49,22,49,B('minecraft:honeycomb_block'));p.set(48,23,48,B('minecraft:gold_block'))
    elif kind=='autumn':
        box(p,47,15,47,49,24,49,B('minecraft:mushroom_stem'))
        for h,r in ((24,7),(25,6),(26,4)):disk(p,x,h,z,r,B('minecraft:red_mushroom_block'))
        for dx,dz in ((-4,0),(4,0),(0,-4),(0,4)):loot_barrel(p,kind,x+dx,15,z+dz);lantern(p,c,x+dx,16,z+dz)
    else:
        for h in range(16):disk(p,x,15+h,z,max(.6,3-h*.16),B('minecraft:packed_ice') if h%3 else B(c['wood']))
        for dx,dz in ((-4,0),(4,0),(0,-4),(0,4)):
            box(p,x+dx,15,z+dz,x+dx,22,z+dz,B(c['log'],axis='y'));lantern(p,c,x+dx,23,z+dz)
        p.set(48,31,48,B('minecraft:end_rod',facing='up'))

def village(kind,variant):
    c=CULTURES[kind];p,ground,rng=land(kind,variant,c);center=(48,48)
    houses,logs,gardens=plan(kind,variant)
    heights={}
    for x,z in houses:heights[(x,z)]=terrace(p,c,ground,x,z,4)
    for x,z in logs:heights[(x,z)]=terrace(p,c,ground,x,z,6)
    for x,z in gardens:heights[(x,z)]=terrace(p,c,ground,x,z,4)
    civic=terrace(p,c,ground,48,48,7)
    street=[(13,48),(24,49),(38,53),(49,45),(64,48),(80,44)]
    if variant:street=[(96-z,x) for x,z in [(13,48),(25,47),(37,50),(49,49),(65,46),(80,44)]]
    street_cells=[]
    for a,b in zip(street,street[1:]):street_cells+=path(p,c,ground,a,b)
    for x,z in houses+logs+gardens:
        entrance=(x,z-5);nearest=min(street_cells,key=lambda a:(a[0]-entrance[0])**2+(a[1]-entrance[1])**2)
        path(p,c,ground,nearest,entrance)
    for i,(x,z) in enumerate(houses):cottage(Raised(p,heights[(x,z)]-14),kind,c,x,z,i+variant)
    for x,z in logs:apartment_tree(Raised(p,heights[(x,z)]-14),kind,c,x,z)
    for x,z in gardens:garden(Raised(p,heights[(x,z)]-14),kind,c,x,z)
    landmark(Raised(p,civic-14),kind,c)
    # Seasonal groves fill the open land without swallowing streets or home fronts.
    occupied=houses+logs+[(48,48)]+gardens
    tree_positions=[]
    road_cells={(x,z) for (x,y,z),(state,be) in p.blocks.items() if
                ground.get((x,z))==y and p.palette[state]['Name']==c['wood']}
    for _ in range(6000):
        if len(tree_positions)>=10:break
        x,z=rng.randrange(7,89),rng.randrange(7,89)
        if (x,z) not in ground or any(math.hypot(x-a,z-b)<8 for a,b in occupied+tree_positions):continue
        if any((x+dx,z+dz) in road_cells for dx in range(-4,5) for dz in range(-4,5)):continue
        if any((x+dx,z+dz) not in ground for dx in (-3,0,3) for dz in (-3,0,3)):continue
        height=ground[(x,z)];tall=rng.randrange(6,10)
        if any(p.palette[state]['Name']!='minecraft:air' for (xx,yy,zz),(state,be) in p.blocks.items()
               if abs(xx-x)<=3 and abs(zz-z)<=3 and height+2<=yy<=height+tall+3):continue
        for y in range(height+1,height+tall+1):p.set(x,y,z,B(c['log'],axis='y'))
        if kind=='winter':layers=[(tall-3,3),(tall-2,2.6),(tall-1,2),(tall,1.4),(tall+1,.7)]
        elif kind=='summer':layers=[(tall-2,3.5),(tall-1,3.8),(tall,3),(tall+1,1.8)]
        else:layers=[(tall-2,2.8),(tall-1,3.2),(tall,2.8),(tall+1,1.8),(tall+2,.7)]
        for dy,radius in layers:
            for dx in range(-4,5):
                for dz in range(-4,5):
                    if dx*dx+dz*dz<=radius*radius and (dx or dz or dy>tall):p.set(x+dx,height+dy,z+dz,leaves(c,len(tree_positions)+dy))
        for dx in (-2,2):
            for k in range(1,abs(dx)+1):p.set(x+(k if dx>0 else -k),height+tall-3+k//2,z,B(c['log'],axis='x'))
        tree_positions.append((x,z))
    flowers=0
    for _ in range(4000):
        x,z=rng.randrange(8,88),rng.randrange(8,88)
        if (x,z) not in ground or any(math.hypot(x-a,z-b)<5.5 for a,b in occupied):continue
        height=ground[(x,z)];current=p.blocks.get((x,height,z));above=p.blocks.get((x,height+1,z))
        if current is None or p.palette[current[0]]['Name']!=c['surface'] or above is not None:continue
        # Snowy islands get exposed grass beds so actual flowers survive block updates.
        if kind=='winter':p.set(x,height,z,B('minecraft:grass_block'))
        p.set(x,height+1,z,B(c['flowers'][rng.randrange(len(c['flowers']))]));flowers+=1
    assert p.dropped==0,(kind,variant,p.dropped)
    homes=sum(1 for state,be in p.blocks.values() if p.palette[state]['Name'].endswith('_fey_apartment'))
    return p,{'season':kind,'variant':variant,'theme':THEMES[kind],'width':96,'surface_cells':len(ground),'cottages':10,'apartment_trees':2,'home_blocks':homes,'gardens':2,'decorative_trees':len(tree_positions),'flowers':flowers,'cottage_positions':houses,'log_positions':logs,'garden_positions':gardens,'seed':2026101700+list(CULTURES).index(kind)*10+variant}

def home_resources():
    out={};prefix='first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion/'
    for kind,c in CULTURES.items():
        elements=[]
        def cube(lo,hi,tex):elements.append({'from':lo,'to':hi,'faces':{f:{'texture':'#'+tex,'uv':[0,0,16,16]} for f in ('north','south','east','west','up','down')}})
        # Bark shell and recessed black openings; doors and six windows have real depth.
        # Beveled octagonal bark casing reads as a hollow trunk, rather than a crate.
        cube([2,0,3],[14,16,15],'bark');cube([0,0,5],[2,16,11],'bark');cube([14,0,5],[16,16,11],'bark')
        cube([1,0,3],[3,16,13],'bark');cube([13,0,3],[15,16,13],'bark');cube([4,0,14],[12,16,16],'bark')
        cube([1,0,1],[2,16,5],'bark');cube([14,0,1],[15,16,5],'bark')
        cube([2,0,0],[14,2,3],'end');cube([2,7,0],[14,9,3],'wood');cube([2,14,0],[14,16,3],'end')
        for y in (2,9):
            cube([2,y,2],[14,y+5,3],'dark')
            for x in (2,6,10,13):cube([x,y,0],[x+.6,y+5,2],'wood')
            cube([2,y+2.2,.5],[14,y+2.7,2],'wood')
            cube([1,y-1,0],[15,y,5],'wood')
            cube([3,y+.5,1],[5,y+1,2],'glow');cube([11,y+.5,1],[13,y+1,2],'glow')
        for y in (3,10):
            cube([7,y,1],[9,y+3,2],'dark');cube([6.5,y-1,0],[9.5,y,3],'wood')
        for x in (0,14):cube([x,14,0],[x+2,16,5],'leaf')
        model={'parent':'minecraft:block/block','textures':{'particle':f'feywild:block/{kind}_tree_log','bark':f'feywild:block/{kind}_tree_log','end':f'feywild:block/{kind}_tree_log_top','wood':f'feywild:block/{kind}_tree_planks','dark':'minecraft:block/black_terracotta','glow':'minecraft:block/glowstone','leaf':'minecraft:block/hay_block_top' if kind=='autumn' else c['roof'].replace(':',':block/')},'elements':elements}
        rid=kind+'_fey_apartment'
        out[prefix+f'models/block/{rid}.json']=model
        out[prefix+f'models/item/{rid}.json']={'parent':'alfheim_companion:block/'+rid}
        out[prefix+f'blockstates/{rid}.json']={'variants':{f'facing={d}':{'model':'alfheim_companion:block/'+rid,'y':a} for d,a in [('north',0),('east',90),('south',180),('west',270)]}}
    return out

class Provider:
    provider_id='alfheim_fey_sky_villages_v2';aliases=('alfheim_fey_sky_villages',)
    def __init__(self,stage):self.stage=stage
    def describe(self):return {'provider_id':self.provider_id,'aliases':list(self.aliases)}
    def generate(self,request,resolver):
        files={};records=[];layouts=[];probes={};definitions=home_resources()
        for season,(kind,c) in enumerate(CULTURES.items()):
            for variant in range(2):
                whole,layout=village(kind,variant);layouts.append(layout)
                for state in whole.palette:
                    rid=state['Name']
                    if rid not in probes:probes[rid]=resolver.probe(rid,kind='block');assert probes[rid]['level'] in ('exact','vanilla'),probes[rid]
                for gx in range(2):
                    for gz in range(2):
                        tile=Piece(48,48,48)
                        for (x,y,z),(state,be) in whole.blocks.items():
                            if x//48==gx and z//48==gz:
                                s=whole.palette[state];tile.set(x%48,y,z%48,B(s['Name'],**s.get('Properties',{})),be)
                        name=f'village_{variant}_{gx}_{gz}';rel=f'kubejs/data/alfheim/structures/pixie/{kind}/{name}.nbt';path=self.stage/rel;path.parent.mkdir(parents=True,exist_ok=True);nbt.save(path,'',tile.to_nbt());data=gzip.compress(gzip.decompress(path.read_bytes()),mtime=0);path.write_bytes(data)
                        files[f'{kind}_{name}.nbt']=data;records.append({'file':rel,'season':kind,'variant':variant,'tile':[gx,gz],'size':[48,48,48],'sha256':hashlib.sha256(data).hexdigest()})
            sid=f'pixie_{kind}_hamlet'
            definitions[f'kubejs/data/alfheim/loot_tables/chests/fairy_island_{kind}.json']=island_loot(kind,c)
            definitions[f'kubejs/data/alfheim/worldgen/structure/{sid}.json']={'type':'alfheim_companion:fey_sky_village','season':season,'biomes':f'#alfheim:has_{sid}','step':'surface_structures','terrain_adaptation':'none','spawn_overrides':{}}
            # All four seasons share a grid. Their disjoint biome hosts choose the culture.
            definitions[f'kubejs/data/alfheim/worldgen/structure_set/{sid}.json']={'structures':[{'structure':'alfheim:'+sid,'weight':1}],'placement':{'type':'minecraft:random_spread','spacing':96,'separation':48,'spread_type':'linear','salt':202610174}}
        for rel,body in definitions.items():
            path=self.stage/rel;path.parent.mkdir(parents=True,exist_ok=True);data=(json.dumps(body,indent=2)+'\n').encode();path.write_bytes(data);files[rel.replace('/','_')]=data
        return {'provider_id':self.provider_id,'status':'GENERATED_NOT_VALIDATED','generated_layout':{'templates':records,'json':list(definitions),'layouts':layouts,'registry_probes':probes,'minimum_independent_gap':500,'runtime_neighbor_reservation':900,'base_y':192,'maximum_y':239,'pieces_per_village':4},'structure_artifact':{'format':'minecraft_structure_nbt','piece_count':32},'artifact_bytes':files}

def main():
    sys.path.insert(0,'C:/GITS/Structuresmith/StructureSmith/src')
    from structure_capability import StructureCapability
    stage=ROOT/'build/fey-sky-villages/generated';cap=StructureCapability(project_root=ROOT,state_root=stage/'snapshots')
    cap.inventory.add_registry_ids(json.loads((ROOT/'server/local/kubejs/export/registries/block.json').read_text()),kind='block')
    custom=['alfheim_companion:'+k+'_fey_apartment' for k in CULTURES]
    source=(ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/fey/ModFeyHomes.java').read_text();assert 'season+"_fey_apartment"' in source
    cap.inventory.add_registry_ids(custom,kind='block');cap.register_generator(Provider(stage))
    result=cap.generate({'structure_id':'alfheim:seasonal_fey_sky_villages','target_version':'1.20.1','grade':3,'purpose':{'kind':'inhabited_fey_sky_villages','required_zones':['seasonal landmark','ten tiny cottages','two hollow apartment trees','two pollination gardens','connected paths']},'context':{'dimension':'mythicbotany:alfheim','biomes':sorted({b for c in CULTURES.values() for b in c['biomes']})},'integration_contracts':{'minimum_independent_gap':500},'generation':{'kind':'alfheim_fey_sky_villages','materialize_nbt':True}})
    layout=result['generated_layout']
    for rel in [r['file'] for r in layout['templates']]+layout['json']:
        path=ROOT/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((stage/rel).read_bytes())
    langpath=ROOT/'first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion/lang/en_us.json';lang=json.loads(langpath.read_text())
    for k in CULTURES:lang['block.alfheim_companion.'+k+'_fey_apartment']=k.title()+' Fey Log Apartments'
    langpath.write_text(json.dumps(lang,indent=2)+'\n')
    (ROOT/'tools/fey_sky_villages_generation.json').write_text(json.dumps({'capability':'Continuity Works','snapshot_id':result['snapshot']['snapshot_id'],'generation':result['generation'],'layout':layout,'source_declared_new_ids':custom,'runtime_registry_pending':custom,'status':'GENERATED_NOT_VALIDATED'},indent=2)+'\n')
    print('CW emitted 8 villages / 32 related tiles / four modeled inhabitable log blocks; runtime validation required')

if __name__=='__main__':main()
