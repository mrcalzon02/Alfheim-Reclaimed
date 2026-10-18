"""Render all thirty saved crown states from the native mesh, with a depth buffer.

Offline model previews only. Opposite views expose every side of the circlet.
"""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion'
MESH=json.loads((ASSET/'crown_geometry.json').read_text())
PALETTE=np.asarray(Image.open(ASSET/'textures/models/armor/eternity_crown.png').convert('RGB'))
OUT=ROOT/'tools/crown_states'
FONT='C:/Windows/Fonts/segoeui.ttf'

def render(progress,angle):
    width,height=234,280;scale=17
    rgb=np.zeros((height,width,3),dtype=np.uint8);rgb[:]=(21,29,43)
    zbuffer=np.full((height,width),-np.inf)
    c,s=math.cos(angle),math.sin(angle)
    def project(p):
        x,y,z=p;x-=8;z-=8
        depth=x*s+z*c
        return [width/2+(x*c-z*s)*scale,244-y*scale*.94+depth*scale*.38,depth]
    def triangle(vertices,uv,light):
        v=np.array(vertices);t=np.array(uv)
        x0=max(0,int(np.floor(v[:,0].min())));x1=min(width-1,int(np.ceil(v[:,0].max())))
        y0=max(0,int(np.floor(v[:,1].min())));y1=min(height-1,int(np.ceil(v[:,1].max())))
        if x0>x1 or y0>y1:return
        xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
        den=(v[1,1]-v[2,1])*(v[0,0]-v[2,0])+(v[2,0]-v[1,0])*(v[0,1]-v[2,1])
        if abs(den)<1e-8:return
        a=((v[1,1]-v[2,1])*(xx-v[2,0])+(v[2,0]-v[1,0])*(yy-v[2,1]))/den
        b=((v[2,1]-v[0,1])*(xx-v[2,0])+(v[0,0]-v[2,0])*(yy-v[2,1]))/den
        q=1-a-b;depth=a*v[0,2]+b*v[1,2]+q*v[2,2]
        view=zbuffer[y0:y1+1,x0:x1+1]
        mask=(a>=-1e-7)&(b>=-1e-7)&(q>=-1e-7)&(depth>view)
        u=np.clip((a*t[0,0]+b*t[1,0]+q*t[2,0]).astype(int),0,255)
        w=np.clip((a*t[0,1]+b*t[1,1]+q*t[2,1]).astype(int),0,255)
        pixels=np.clip(PALETTE[w,u]*light,0,255).astype(np.uint8)
        rgb[y0:y1+1,x0:x1+1][mask]=pixels[mask];view[mask]=depth[mask]
    for e in MESH:
        if 'gem' in e and e['gem']>=progress*8:continue
        x,y,z=e['from'];X,Y,Z=e['to'];u,v=e['uv'];size=4 if 'gem' in e else 12
        texture=[(u,v+size),(u+size,v+size),(u+size,v),(u,v)]
        sides=[]
        if c>=0:sides.append(([(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],.86))
        else:sides.append(([(X,y,z),(x,y,z),(x,Y,z),(X,Y,z)],.86))
        if s>=0:sides.append(([(X,y,Z),(X,y,z),(X,Y,z),(X,Y,Z)],.72))
        else:sides.append(([(x,y,z),(x,y,Z),(x,Y,Z),(x,Y,z)],.72))
        sides.append(([(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],1.08))
        for points,light in sides:
            projected=[project(p) for p in points]
            for indexes in [(0,1,2),(0,2,3)]:triangle([projected[i] for i in indexes],[texture[i] for i in indexes],light)
    return Image.fromarray(rgb)

def main():
    OUT.mkdir(exist_ok=True)
    title=ImageFont.truetype(FONT,28);label=ImageFont.truetype(FONT,22);small=ImageFont.truetype(FONT,16)
    for page in range(5):
        image=Image.new('RGB',(1500,940),(13,19,29));draw=ImageDraw.Draw(image)
        first=page*6;last=first+5
        draw.text((28,20),f'CROWN OF ETERNITY  /  STATES {first}–{last}',font=title,fill=(244,219,157))
        draw.text((28,60),'Two opposite views per state • actual native geometry and texture • offline preview',font=small,fill=(162,181,205))
        for cell,state in enumerate(range(first,last+1)):
            left=(cell%3)*500+12;top=(cell//3)*410+98
            draw.rounded_rectangle((left,top,left+476,top+392),radius=12,fill=(21,29,43),outline=(47,63,84),width=1)
            name='Forged crown' if state==0 else 'Crown of Eternity' if state==29 else f'Inlay {state} complete'
            draw.text((left+16,top+12),name,font=label,fill=(244,219,157))
            draw.text((left+16,top+44),f'{state*8} / 232 gems  •  {state} / 29 inlays',font=small,fill=(191,208,226))
            for view,angle in enumerate((2.59,2.59+math.pi)):
                image.paste(render(state,angle),(left+4+view*234,top+72))
            draw.text((left+76,top+359),'Front / right',font=small,fill=(147,171,196))
            draw.text((left+302,top+359),'Back / left',font=small,fill=(147,171,196))
        path=OUT/f'crown_states_{page+1}.png';image.save(path);print(path)

if __name__=='__main__':main()
