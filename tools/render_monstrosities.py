"""Faithful quad previews of baked native models at one shared world scale."""
import copy,io,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion'

def render(quads,texture,size=440,yaw=155,scale=4.6,center_y=10):
    ax=math.radians(8);ay=math.radians(yaw)
    rx=np.array([[1,0,0],[0,math.cos(ax),-math.sin(ax)],[0,math.sin(ax),math.cos(ax)]])
    ry=np.array([[math.cos(ay),0,math.sin(ay)],[0,1,0],[-math.sin(ay),0,math.cos(ay)]])
    rot=ry@rx;pixels=np.zeros((size,size,4),dtype=np.uint8);depth=np.full((size,size),-np.inf)
    for q in quads:
        normal=np.array(q['normal']);n=rot@normal
        if n[2]<=0:continue
        v=(np.array(q['vertices'])-[0,center_y,0])@rot.T
        v[:,:2]*=[scale,-scale];v[:,:2]+=[size/2,size/2]
        uv=np.array(q['uv'])*texture.shape[0]
        for idx in ((0,1,2),(0,2,3)):
            p=v[list(idx)];t=uv[list(idx)];lo=np.maximum(0,np.floor(p[:,:2].min(axis=0)).astype(int));hi=np.minimum(size-1,np.ceil(p[:,:2].max(axis=0)).astype(int))
            if (hi<lo).any():continue
            gx,gy=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5)
            matrix=np.vstack([p[:,:2].T,np.ones(3)])
            if abs(np.linalg.det(matrix))<1e-8:continue
            weights=np.linalg.inv(matrix)@np.array([gx.ravel(),gy.ravel(),np.ones(gx.size)])
            z=(weights.T@p[:,2]).reshape(gx.shape);local=depth[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
            mask=((weights>=-1e-8).all(axis=0)).reshape(gx.shape)&(z>local)
            coords=weights.T@t;tx=np.clip(coords[:,0].astype(int),0,texture.shape[1]-1);ty=np.clip(coords[:,1].astype(int),0,texture.shape[0]-1)
            colors=texture[ty,tx].reshape(*gx.shape,4).copy();light=.88+.12*max(0,float(np.dot(normal,np.array([-.35,.65,-.7]))))
            colors[:,:,:3]=np.clip(colors[:,:,:3].astype(float)*light,0,255).astype(np.uint8);mask&=colors[:,:,3]>0
            pixels[lo[1]:hi[1]+1,lo[0]:hi[0]+1][mask]=colors[mask];local[mask]=z[mask]
    return Image.fromarray(pixels)

def head_icon(quads,texture_bytes):
    quads=copy.deepcopy(quads);vertices=np.array([v for q in quads for v in q['vertices']])
    low=vertices.min(axis=0);high=vertices.max(axis=0);center=(low+high)/2
    for q in quads:q['vertices']=(np.array(q['vertices'])-center+[0,5,0]).tolist()
    texture=np.array(Image.open(io.BytesIO(texture_bytes)).convert('RGBA'))
    return render(quads,texture,size=128,yaw=155,scale=110/(max(high-low)*1.35),center_y=5)

def main():
    g=json.loads((ROOT/'tools/monstrosity_geometry.json').read_text());font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18);title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25)
    def texture(row,look=0):return np.array(Image.open(RES/f"textures/entity/monstrosities/{row['id']}_{look}.png").convert('RGBA'))
    def overview(rows,name,heading):
        height=math.ceil(len(rows)/3)*500+80
        sheet=Image.new('RGB',(1440,height),'#1b242a');d=ImageDraw.Draw(sheet);d.text((24,15),heading,font=title,fill='white')
        for i,row in enumerate(rows):
            tile=render(g['models'][row['id']],texture(row));x=(i%3)*480+20;y=(i//3)*500+45;sheet.paste(tile,(x,y),tile)
            d.text((x+20,y+400),row['label']+f" / {row['height']:.2f} blocks tall",font=font,fill='white')
            px=x+395;floor=y+376;h=round(1.8*16*4.6)
            d.rectangle((px-7,floor-h,px+7,floor-h+23),fill='#647986');d.rectangle((px-9,floor-h+25,px+9,floor-48),fill='#526877')
            d.rectangle((px-9,floor-46,px-2,floor),fill='#46596c');d.rectangle((px+2,floor-46,px+9,floor),fill='#46596c');d.text((px-27,floor+8),'1.8',font=font,fill='#91a3ad')
        d.text((24,height-35),'Actual native models and UV skins. Shared scale; labels give collision height. Client motion and lighting review pending.',font=font,fill='#a8b6bd')
        sheet.save(ROOT/'tools'/name)
    def details(rows,name):
        detail=Image.new('RGB',(1800,len(rows)*650+70),'#1b242a');dd=ImageDraw.Draw(detail)
        dd.text((24,15),'NATIVE SCULPTURE AND MATERIAL DETAILS / FRONT, THREE-QUARTER, REAR',font=title,fill='white')
        for i,row in enumerate(rows):
            for j,angle in enumerate((180,135,35)):
                tile=render(g['models'][row['id']],texture(row),size=600,yaw=angle,scale=6.7,center_y=11)
                detail.paste(tile,(j*600,70+i*650),tile)
            dd.text((24,70+i*650+602),row['label'],font=font,fill='white')
        detail.save(ROOT/'tools'/name)
    overview(g['species'],'monstrosities_review.png','ALFHEIM MONSTROSITIES / TWELVE DISTINCT SPECIES')
    overview(g['species'][6:],'fey_nightmares_review.png','FEY WILDS NIGHTMARES / SIX NEW SPECIES')
    details(g['species'],'monstrosities_detail.png');details(g['species'][6:],'fey_nightmares_detail.png')
    variants=Image.new('RGB',(1440,len(g['species'])*440+70),'#1b242a');vd=ImageDraw.Draw(variants);vd.text((24,15),'REGIONAL APPEARANCES / SHARED WORLD SCALE',font=title,fill='white')
    for i,row in enumerate(g['species']):
        for look in range(3):
            tile=render(g['models'][row['id']],texture(row,look));x=look*480+20;y=i*440+35;variants.paste(tile,(x,y),tile)
            vd.text((x+20,y+405),row['variants'][look]+' '+row['label'],font=font,fill='white')
    variants.save(ROOT/'tools/monstrosities_variants.png');print('Rendered 12 anatomies, 36 regional skins and the new Fey nightmare review sheets')
if __name__=='__main__':main()
