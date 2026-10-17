"""Offline orthographic review of the emitted native mesh, not an in-game screenshot."""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion'
mesh=json.loads((ASSET/'crown_geometry.json').read_text())
gems=json.loads((ASSET/'gemstone_displays.json').read_text())
font_path='C:/Windows/Fonts/segoeui.ttf'
image=Image.new('RGB',(1500,760),(17,22,33));d=ImageDraw.Draw(image)
title=ImageFont.truetype(font_path,32);small=ImageFont.truetype(font_path,19)
d.text((42,24),'CROWN OF ETERNITY',font=title,fill=(246,222,160))
d.text((42,69),'Native model review • gold, platinum and 232 individual gem settings',font=small,fill=(173,189,211))

def draw_crown(cx,cy,scale,progress):
    # View the front and right sides from above. Depth-sort all visible exterior cube faces.
    faces=[];angle=.55;c=math.cos(angle);s=math.sin(angle)
    def project(p):
        x,y,z=p;x-=8;z-=8
        rx=x*c-z*s;rz=x*s+z*c
        return (cx+rx*scale,cy-y*scale*.94+rz*scale*.38)
    for e in mesh:
        if 'gem' in e and e['gem']>=progress*8:continue
        x,y,z=e['from'];X,Y,Z=e['to']
        color=(219,168,58) if e['material']=='gold' else (204,222,233)
        if 'gem' in e:color=tuple(bytes.fromhex(gems[e['gem']]['color']))
        for pts,light in [([(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],.85), ([(X,y,z),(X,y,Z),(X,Y,Z),(X,Y,z)],.66), ([(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],1.14)]:
            depth=sum(p[0]*s+p[2]*c for p in pts)/4
            faces.append((depth,[project(p) for p in pts],tuple(min(255,int(v*light)) for v in color), 'gem' in e))
    for _,points,color,gem in sorted(faces,key=lambda f:f[0]):
        d.polygon(points,fill=color)
        if gem:d.line(points[:2],fill=tuple(min(255,int(v*1.35+18)) for v in color),width=1)
        else:d.line(points+[points[0]],fill=tuple(int(v*.68) for v in color),width=1)

for cx,count,label in [(275,0,'Forged crown'),(750,14,'112 gems inset'),(1225,29,'All 232 gems inset')]:
    draw_crown(cx,617,36,count)
    d.text((cx-110,650),label,font=small,fill=(227,228,233))
d.text((42,718),'Offline geometry preview; crafting, equipment rendering and multiplayer still need an in-game check.',font=small,fill=(137,155,178))
target=ROOT/'tools/eternity_crown_review.png';image.save(target);print(target)
