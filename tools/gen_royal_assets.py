"""Generate the first Royal / Noble Cultural Asset Library.

Authority: alfheim_reclaimed_design/CULTURAL_ASSET_LIBRARY.md
Manifest: tools/royal_asset_manifest.json

The outputs are reusable structure-template fragments, not independently placed worldgen
structures. They deliberately have no random-spread structure sets in this slice.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, random, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt
from structure_nbt import Piece, MAX_AXIS

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "royal_asset_manifest.json"
OUT = ROOT / "kubejs" / "data" / "alfheim" / "structures" / "royal_assets"
METRICS = ROOT / "tools" / "royal_asset_metrics.json"
REVIEW = ROOT / "tools" / "royal_asset_review.png"
SEED = 20260905

def B(name, **props):
    if not props: return (name, None)
    return (name, {k: ("true" if v is True else "false" if v is False else str(v)) for k,v in props.items()})

def box(p,x0,y0,z0,x1,y1,z1,block):
    for x in range(min(x0,x1),max(x0,x1)+1):
        for y in range(min(y0,y1),max(y0,y1)+1):
            for z in range(min(z0,z1),max(z0,z1)+1):
                p.set(x,y,z,block)

def line(p,a,b,block):
    x0,y0,z0=a; x1,y1,z1=b
    n=max(abs(x1-x0),abs(y1-y0),abs(z1-z0))
    for i in range(n+1):
        t=0 if n==0 else i/n
        p.set(round(x0+(x1-x0)*t),round(y0+(y1-y0)*t),round(z0+(z1-z0)*t),block)

def stair(name,facing,half="bottom",shape="straight"):
    return B(name,facing=facing,half=half,shape=shape,waterlogged=False)
def slab(name,kind="bottom"):
    return B(name,type=kind,waterlogged=False)
def pillar(name,axis="y"):
    return B(name,axis=axis)

def mats(m):
    return {k:(v,None) for k,v in m.items()}

def add_rubble(p, positions, m, seed):
    rng=random.Random(seed)
    rubble=[m["cracked"],m["mossy"],("minecraft:calcite",None),("minecraft:gravel",None)]
    for x,y,z in positions:
        p.set(x,y,z,rng.choice(rubble))

def reliquary_pedestal(a,m):
    p=Piece(*a["size"]); damaged=a["condition"]=="damaged"
    cx,cz=p.size[0]//2,p.size[2]//2
    box(p,cx-4,0,cz-4,cx+4,0,cz+4,m["polished"])
    box(p,cx-3,1,cz-3,cx+3,1,cz+3,m["structural"])
    box(p,cx-2,2,cz-2,cx+2,2,cz+2,m["accent"])
    box(p,cx-1,3,cz-1,cx+1,4,cz+1,m["pillar"])
    # sacred framing posts and small lamps
    for dx,dz in [(-4,-4),(4,-4),(-4,4),(4,4)]:
        box(p,cx+dx,1,cz+dz,cx+dx,6,cz+dz,m["pillar"])
        p.set(cx+dx,7,cz+dz,m["light"])
    # socket is a jigsaw, not a fake progression object
    p.jigsaw(cx,5,cz,"alfheim:fey_stone_socket","alfheim:fey_stone_piece",
             "alfheim:royal/fey_stones","up_north",joint="aligned")
    if damaged:
        # fail the east flank but never the center/socket
        for pos in list(p.blocks):
            x,y,z=pos
            if x>=cx+3 and y>=3 and (x+y+z)%3:
                del p.blocks[pos]
        add_rubble(p,[(cx+4,1,cz-2),(cx+4,1,cz-1),(cx+4,1,cz),(cx+3,1,cz+2),
                      (cx+2,1,cz+4),(cx+4,2,cz+3)],m,SEED+11)
    return p

def oath_memorial(a,m):
    p=Piece(*a["size"]); damaged=a["condition"]=="damaged"
    sx,sy,sz=p.size; cx=sx//2
    box(p,1,0,1,sx-2,0,sz-2,m["polished"])
    for x in range(1,sx-1):
        box(p,x,1,2,x,7,2,m["structural"])
    for x in (1,sx-2):
        box(p,x,1,1,x,8,3,m["pillar"])
    box(p,cx-2,2,1,cx+2,6,1,m["accent"])
    # oath line and memorial lights
    for x in (cx-3,cx+3):
        p.set(x,5,1,m["light"])
    if damaged:
        for pos in list(p.blocks):
            x,y,z=pos
            if x>cx and y>4 and (x+y)%2:
                del p.blocks[pos]
        add_rubble(p,[(cx+2,1,3),(cx+3,1,3),(cx+1,1,2),(sx-2,1,2)],m,SEED+21)
    return p

def monumental_arch(a,m):
    p=Piece(*a["size"]); damaged=a["condition"]=="damaged"
    sx,sy,sz=p.size; cx=sx//2
    # deep threshold base
    box(p,0,0,0,sx-1,0,sz-1,m["polished"])
    for z in range(1,sz-1):
        # piers
        box(p,1,1,z,4,10,z,m["structural"])
        box(p,sx-5,1,z,sx-2,10,z,m["structural"])
        # expressed outer columns
        box(p,2,1,z,2,11,z,m["pillar"])
        box(p,sx-3,1,z,sx-3,11,z,m["pillar"])
        # spring blocks
        box(p,4,8,z,5,10,z,m["accent"])
        box(p,sx-6,8,z,sx-5,10,z,m["accent"])
        # stepped arch crown around 7-wide opening
        box(p,5,10,z,sx-6,11,z,m["structural"])
        box(p,6,12,z,sx-7,12,z,m["structural"])
        box(p,7,13,z,sx-8,13,z,m["accent"])
    if damaged:
        # directional failure on east crown; passage remains
        for pos in list(p.blocks):
            x,y,z=pos
            if x>=cx+2 and y>=9 and (x+y+z)%4 != 0:
                del p.blocks[pos]
        add_rubble(p,[(cx+4,1,1),(cx+5,1,2),(cx+6,1,3),(cx+5,2,4),
                      (cx+7,1,5),(cx+3,1,5),(cx+6,2,1)],m,SEED+31)
    return p

def grand_column(a,m):
    p=Piece(*a["size"]); damaged=a["condition"]=="damaged"
    sx,sy,sz=p.size; cx,cz=sx//2,sz//2
    if not damaged:
        box(p,cx-3,0,cz-3,cx+3,0,cz+3,m["polished"])
        box(p,cx-2,1,cz-2,cx+2,2,cz+2,m["accent"])
        box(p,cx-1,3,cz-1,cx+1,sy-5,cz+1,m["pillar"])
        box(p,cx-2,sy-4,cz-2,cx+2,sy-3,cz+2,m["accent"])
        box(p,cx-3,sy-2,cz-3,cx+3,sy-1,cz+3,m["structural"])
    else:
        # intact base and stump, shaft fallen east
        box(p,1,0,2,7,0,6,m["polished"])
        box(p,2,1,3,6,2,5,m["accent"])
        box(p,3,3,3,5,6,5,m["pillar"])
        for x in range(6,12):
            box(p,x,1,3,x,3,5,pillar(m["pillar"][0],"x"))
        box(p,10,1,2,12,3,6,m["accent"])
        add_rubble(p,[(8,1,1),(9,1,6),(11,1,1),(12,1,7),(7,1,7)],m,SEED+41)
    return p

def procession_stair(a,m):
    p=Piece(*a["size"]); damaged=a["condition"]=="damaged"
    sx,sy,sz=p.size; cx=sx//2
    # 9 steps, 11-wide, with wide landings
    for step in range(9):
        z0=1+step*2
        y=step
        for z in (z0,z0+1):
            for x in range(cx-5,cx+6):
                p.set(x,y,z,m["polished"])
        # side balustrade/pillars
        for x in (cx-7,cx+7):
            for z in (z0,z0+1):
                p.set(x,y,z,m["structural"])
                if step%2==0:p.set(x,y+1,z,m["pillar"])
    box(p,cx-7,8,19,cx+7,8,20,m["polished"])
    if damaged:
        # east rail and outer stair edge have collapsed, leave central 7-wide route
        for pos in list(p.blocks):
            x,y,z=pos
            if x>cx+4 and z>7:
                del p.blocks[pos]
        add_rubble(p,[(cx+6,1,9),(cx+7,1,11),(cx+8,1,13),(cx+6,2,15),(cx+8,1,17)],m,SEED+51)
    return p

def balcony_bay(a,m):
    p=Piece(*a["size"]); damaged=a["condition"]=="damaged"
    sx,sy,sz=p.size; cx=sx//2
    # back wall and tall glazed opening
    box(p,0,0,0,sx-1,0,sz-1,m["polished"])
    for x in range(sx):
        box(p,x,1,1,x,10,1,m["structural"])
    box(p,5,3,1,11,9,1,m["glass"])
    for x in (1,4,12,15):
        box(p,x,1,1,x,11,1,m["pillar"])
    # balcony floor
    box(p,2,5,2,sx-3,5,7,m["polished"])
    # rail
    for x in range(2,sx-2):
        p.set(x,6,7,m["fence"])
    for z in range(2,8):
        p.set(2,6,z,m["fence"]); p.set(sx-3,6,z,m["fence"])
    if damaged:
        for pos in list(p.blocks):
            x,y,z=pos
            if z>=5 and x>cx and y>=5 and (x+z)%3:
                del p.blocks[pos]
        add_rubble(p,[(cx+3,1,5),(cx+4,1,6),(cx+5,1,7),(cx+2,1,7)],m,SEED+61)
    return p

def royal_bench(a,m):
    p=Piece(*a["size"]); damaged=a["condition"]=="damaged"
    sx,sy,sz=p.size
    for x in range(1,sx-1):
        p.set(x,1,2,slab(m["plank"][0],"bottom"))
        p.set(x,2,3,B(m["fence"][0],north=False,south=False,east=False,west=False,waterlogged=False))
    for x in (1,sx-2):
        p.set(x,0,2,m["timber"])
        p.set(x,1,3,m["timber"])
    if damaged:
        for pos in [(sx-2,0,2),(sx-2,1,2),(sx-2,1,3),(sx-2,2,3),(sx-3,2,3)]:
            p.blocks.pop(pos,None)
        p.set(sx-2,0,1,m["plank"]); p.set(sx-3,0,1,m["cracked"])
    return p

def ceremonial_brazier(a,m):
    p=Piece(*a["size"]); damaged=a["condition"]=="damaged"
    cx,cz=p.size[0]//2,p.size[2]//2
    box(p,cx-1,0,cz-1,cx+1,0,cz+1,m["polished"])
    p.set(cx,1,cz,m["pillar"]); p.set(cx,2,cz,m["pillar"])
    for dx,dz in [(-1,0),(1,0),(0,-1),(0,1)]:
        p.set(cx+dx,3,cz+dz,m["accent"])
    p.set(cx,3,cz,m["light"] if not damaged else m["cracked"])
    if not damaged:
        p.set(cx,4,cz,B("minecraft:soul_lantern",hanging=False,waterlogged=False))
    else:
        p.set(cx+1,0,cz+1,m["cracked"]); p.set(cx-1,0,cz+1,("minecraft:gravel",None))
    return p

def reliquary_core(a,m):
    p=Piece(*a["size"]); sx,sy,sz=p.size; cx,cz=sx//2,sz//2
    # terraced sacred chamber
    box(p,2,0,2,sx-3,0,sz-3,m["polished"])
    # outer walls with four axial entrances
    for x in range(3,sx-3):
        for y in range(1,12):
            for z in (3,sz-4):
                if not (cx-3<=x<=cx+3 and y<=6):
                    p.set(x,y,z,m["structural"])
    for z in range(4,sz-4):
        for y in range(1,12):
            for x in (3,sx-4):
                if not (cz-3<=z<=cz+3 and y<=6):
                    p.set(x,y,z,m["structural"])
    # tall corner/side columns
    for x,z in [(5,5),(sx-6,5),(5,sz-6),(sx-6,sz-6),(cx,5),(cx,sz-6),(5,cz),(sx-6,cz)]:
        box(p,x,1,z,x,16,z,m["pillar"])
        box(p,x-1,0,z-1,x+1,0,z+1,m["accent"])
        box(p,x-1,17,z-1,x+1,18,z+1,m["accent"])
    # inner processional ring
    for x in range(cx-10,cx+11):
        for z in (cz-10,cz+10):
            p.set(x,1,z,m["structural"])
            if x%4==0:p.set(x,2,z,m["light"])
    for z in range(cz-9,cz+10):
        for x in (cx-10,cx+10):
            p.set(x,1,z,m["structural"])
            if z%4==0:p.set(x,2,z,m["light"])
    # central stepped dais
    box(p,cx-6,1,cz-6,cx+6,1,cz+6,m["structural"])
    box(p,cx-4,2,cz-4,cx+4,2,cz+4,m["polished"])
    box(p,cx-2,3,cz-2,cx+2,3,cz+2,m["accent"])
    box(p,cx-1,4,cz-1,cx+1,5,cz+1,m["pillar"])
    p.jigsaw(cx,6,cz,"alfheim:fey_stone_socket","alfheim:fey_stone_piece",
             "alfheim:royal/fey_stones","up_north",joint="aligned")
    # overhead broken vault ribs
    for d in (-10,-5,0,5,10):
        for y in range(12,23):
            spread=max(0,10-(y-12)//2)
            for x in (cx-spread,cx+spread):
                z=cz+d
                if 0<=x<sx and 0<=z<sz:
                    p.set(x,y,z,m["structural"] if y%3 else m["accent"])
    # galleries/benches and ritual lights
    for z in (8,sz-9):
        for x in range(9,sx-9,6):
            box(p,x,1,z,x+3,1,z+1,m["plank"])
            p.set(x,2,z+1,m["timber"]); p.set(x+3,2,z+1,m["timber"])
    for x,z in [(cx-13,cz-13),(cx+13,cz-13),(cx-13,cz+13),(cx+13,cz+13)]:
        box(p,x-1,1,z-1,x+1,1,z+1,m["polished"]); p.set(x,2,z,m["pillar"]); p.set(x,3,z,m["light"])
    # causal east/northeast roof collapse + debris, but center and route survive
    for pos in list(p.blocks):
        x,y,z=pos
        if x>cx+6 and z<cz-4 and y>8 and ((x*3+y+z)%5)!=0:
            del p.blocks[pos]
    rubble=[]
    for i in range(34):
        rubble.append((min(sx-4,cx+8+(i%9)),1,max(4,cz-13+(i*3)%12)))
    add_rubble(p,rubble,m,SEED+77)
    # clear 5-wide axial routes after debris
    AIR=("minecraft:air",None)
    for z in range(3,cz-6):
        for x in range(cx-2,cx+3):
            for y in range(1,5): p.set(x,y,z,AIR)
    for z in range(cz+7,sz-3):
        for x in range(cx-2,cx+3):
            for y in range(1,5): p.set(x,y,z,AIR)
    for x in range(3,cx-6):
        for z in range(cz-2,cz+3):
            for y in range(1,5): p.set(x,y,z,AIR)
    for x in range(cx+7,sx-3):
        for z in range(cz-2,cz+3):
            for y in range(1,5): p.set(x,y,z,AIR)
    # restore socket if any route clear write touched it (it should not)
    p.jigsaw(cx,6,cz,"alfheim:fey_stone_socket","alfheim:fey_stone_piece",
             "alfheim:royal/fey_stones","up_north",joint="aligned")
    return p

BUILDERS={
 "reliquary_pedestal":reliquary_pedestal, "oath_memorial":oath_memorial,
 "monumental_arch":monumental_arch, "grand_column":grand_column,
 "procession_stair":procession_stair, "balcony_bay":balcony_bay,
 "royal_bench":royal_bench, "ceremonial_brazier":ceremonial_brazier,
 "reliquary_core":reliquary_core
}

def canonical_digest(root):
    # repr is stable because Piece writes blocks/palette in deterministic insertion/sorted order
    def normal(v):
        if isinstance(v,dict): return {k:normal(v[k]) for k in sorted(v)}
        if isinstance(v,list): return [normal(x) for x in v]
        if isinstance(v,(int,float,str)) or v is None:return v
        return int(v) if isinstance(v,int) else str(v)
    raw=json.dumps(normal(root),sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()

def make_review(records):
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return
    tiles=[]
    for rec in records:
        _,root=nbt.load(OUT/f"{rec['id']}.nbt")
        sx,sy,sz=[int(v) for v in root["size"]]
        # top projection by highest occupied non-air block
        palette=root["palette"]; cols={}
        for b in root["blocks"]:
            x,y,z=map(int,b["pos"]); name=palette[int(b["state"])]["Name"]
            if name=="minecraft:air": continue
            if (x,z) not in cols or y>cols[(x,z)][0]: cols[(x,z)]=(y,name)
        scale=max(1,128//max(sx,sz))
        im=Image.new("RGB",(sx*scale,sz*scale),(20,20,24)); d=ImageDraw.Draw(im)
        for (x,z),(y,name) in cols.items():
            # stable color from block id
            h=hashlib.sha1(name.encode()).digest()
            col=(70+h[0]//2,70+h[1]//2,70+h[2]//2)
            d.rectangle((x*scale,z*scale,(x+1)*scale-1,(z+1)*scale-1),fill=col)
        tiles.append((rec["id"],im))
    w=600; rowh=170; h=rowh*len(tiles)
    atlas=Image.new("RGB",(w,h),(245,245,245)); d=ImageDraw.Draw(atlas)
    y=0
    for name,im in tiles:
        d.text((10,y+8),name,fill=(0,0,0))
        im.thumbnail((150,145))
        atlas.paste(im,(10,y+25))
        y+=rowh
    atlas.save(REVIEW)

def generate(only=None):
    data=json.loads(MANIFEST.read_text())
    m=mats(data["materials"]); OUT.mkdir(parents=True,exist_ok=True)
    records=[]
    for a in data["assets"]:
        if only and a["id"]!=only: continue
        p=BUILDERS[a["builder"]](a,m)
        if any(v>MAX_AXIS for v in p.size): raise ValueError(f"{a['id']}: piece exceeds {MAX_AXIS}")
        out=OUT/f"{a['id']}.nbt"
        nbt.save(out,"",p.to_nbt())
        _,loaded=nbt.load(out)
        records.append({"id":a["id"],"family":a["family"],"condition":a["condition"],
                        "size":list(p.size),"blocks":len(p.blocks),"palette":len(p.palette),
                        "dropped":p.dropped,"sha256_decompressed":canonical_digest(loaded)})
        print(f"{a['id']}: blocks={len(p.blocks)} palette={len(p.palette)} dropped={p.dropped}")
    if not only:
        METRICS.write_text(json.dumps({"schema":"alfheim:royal_asset_metrics/v1","assets":records},indent=2)+"\n")
        make_review(records)
    return records

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--only"); args=ap.parse_args()
    generate(args.only)
