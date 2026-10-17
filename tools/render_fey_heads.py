"""Offline textured review of native spawn-egg head models; not a game screenshot."""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT/'kubejs/assets/alfheim'


def render(model, size=160, texture_images=None, tints=None, directional_light=False):
    if texture_images is None:
        texture_images={'skin':np.asarray(Image.open(ASSETS/'textures/entity/fey_materials.png').convert('RGBA'))}
    ax, ay, az = [math.radians(a) for a in model['display']['gui']['rotation']]
    assert az == 0
    rx = np.array([[1,0,0],[0,math.cos(ax),-math.sin(ax)],[0,math.sin(ax),math.cos(ax)]])
    ry = np.array([[math.cos(ay),0,math.sin(ay)],[0,1,0],[-math.sin(ay),0,math.cos(ay)]])
    rot = ry @ rx
    scale = size/16*model['display']['gui']['scale'][0]
    pixels = np.zeros((size,size,4),dtype=np.uint8)
    depth = np.full((size,size),-np.inf)
    normals = {'north':(0,0,-1),'south':(0,0,1),'east':(1,0,0),
               'west':(-1,0,0),'up':(0,1,0),'down':(0,-1,0)}
    for e in model['elements']:
        x,y,z=e['from']; X,Y,Z=e['to']
        faces = {
            'north':[(X,Y,z),(x,Y,z),(x,y,z),(X,y,z)],
            'south':[(x,Y,Z),(X,Y,Z),(X,y,Z),(x,y,Z)],
            'east':[(X,Y,Z),(X,Y,z),(X,y,z),(X,y,Z)],
            'west':[(x,Y,z),(x,Y,Z),(x,y,Z),(x,y,z)],
            'up':[(x,Y,Z),(X,Y,Z),(X,Y,z),(x,Y,z)],
            'down':[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z)],
        }
        for face, vertices in faces.items():
            if face not in e['faces'] or (rot @ normals[face])[2] <= 0:
                continue
            v = (np.array(vertices)-8) @ rot.T
            v[:,:2] *= [scale,-scale]; v[:,:2] += size/2
            face_info=e['faces'][face]
            skin=texture_images[face_info['texture'].lstrip('#')]
            u0,v0,u1,v1 = np.array(face_info['uv'])*np.array([skin.shape[1],skin.shape[0],skin.shape[1],skin.shape[0]])/16
            uv = np.array([(u0,v0),(u1,v0),(u1,v1),(u0,v1)])
            for indices in ((0,1,2),(0,2,3)):
                p=v[list(indices)]; t=uv[list(indices)]
                lo=np.maximum(0,np.floor(p[:,:2].min(axis=0)).astype(int))
                hi=np.minimum(size-1,np.ceil(p[:,:2].max(axis=0)).astype(int))
                if (hi<lo).any(): continue
                gx,gy=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5)
                matrix=np.vstack([p[:,:2].T,np.ones(3)])
                if abs(np.linalg.det(matrix))<1e-8: continue
                weights=np.linalg.inv(matrix) @ np.array([gx.ravel(),gy.ravel(),np.ones(gx.size)])
                depths=(weights.T @ p[:,2]).reshape(gx.shape)
                local=depth[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
                mask=((weights>=-1e-8).all(axis=0)).reshape(gx.shape) & (depths>local)
                coords=weights.T @ t
                tx=np.clip(coords[:,0].astype(int),0,skin.shape[1]-1)
                ty=np.clip(coords[:,1].astype(int),0,skin.shape[0]-1)
                colors=skin[ty,tx].reshape(*gx.shape,4)
                if directional_light:
                    colors=colors.copy()
                    light={'north':1,'south':.86,'east':.74,'west':.74,'up':1.1,'down':.62}[face]
                    colors[:,:,:3]=np.clip(colors[:,:,:3].astype(float)*light,0,255).astype(np.uint8)
                if tints is not None and 'tintindex' in face_info:
                    colors=colors.copy()
                    tint=tints[face_info['tintindex']]
                    colors[:,:,:3]=(colors[:,:,:3].astype(float)*np.array([(tint>>16)&255,(tint>>8)&255,tint&255])/255).astype(np.uint8)
                mask &= colors[:,:,3]>0
                pixels[lo[1]:hi[1]+1,lo[0]:hi[0]+1][mask]=colors[mask]
                local[mask]=depths[mask]
    return Image.fromarray(pixels)


def main():
    roster=json.loads((ROOT/'kubejs/fey_roster.json').read_text())
    sheet=Image.new('RGB',(1200,830),'#171d27'); d=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',24)
    d.text((24,18),'CUSTOM CREATURE SPAWN ITEMS / SKINNED HEADS',font=title,fill='white')
    for i,r in enumerate(roster):
        model=json.loads((ASSETS/f"models/item/{r['id'].split(':')[1]}_spawn_egg.json").read_text())
        assert model['textures']['skin']=='alfheim:entity/fey_materials'
        for e in model['elements']:
            assert all(0<=a<b<=16 for a,b in zip(e['from'],e['to'])), r['id']
            assert all('tintindex' not in f for f in e['faces'].values()), r['id']
            assert all(0<=n<=16 for f in e['faces'].values() for n in f['uv']), r['id']
        tile=render(model)
        assert tile.getbbox(),r['id']
        x=(i%6)*200+20;y=(i//6)*240+65
        sheet.paste(tile,(x,y),tile)
        d.text((x,y+170),r['name'],font=font,fill='#dae2ee')
        tiny=render(model,16).resize((32,32),Image.Resampling.NEAREST)
        sheet.paste(tiny,(x+140,y+195),tiny)
    d.text((24,796),'Offline model render using the original skin UVs. Small inset: 16px inventory view. Client review pending.',
           font=font,fill='#98a8bd')
    sheet.save(ROOT/'tools/fey_spawn_heads_review.png')
    print(f'PASS: {len(roster)} bounded, textured, untinted head models rendered')


if __name__=='__main__':
    main()
