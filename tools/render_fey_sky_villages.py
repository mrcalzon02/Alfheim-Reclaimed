"""Offline voxel silhouettes from actual emitted NBT, colored by installed block textures."""
import io,json,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from check_fey_sky_villages import read_village
from gen_fey_sky_villages import ROOT,CULTURES,THEMES

ARCHIVES={}
for p in (ROOT/'mods').glob('*.jar'):
    if any(s in p.name.lower() for s in ('feywild','botania')):
        z=zipfile.ZipFile(p)
        for n in z.namelist():
            if n.startswith('assets/') and '/textures/block/' in n and n.endswith('.png'):ARCHIVES[n]=z
client=zipfile.ZipFile('C:/Users/Admin/curseforge/minecraft/Install/versions/1.20.1/1.20.1.jar')
for n in client.namelist():
    if n.startswith('assets/minecraft/textures/block/') and n.endswith('.png'):ARCHIVES[n]=client
CACHE={}
def texture(rid):
    ns,key=rid.split(':');path=f'assets/{ns}/textures/{key}.png'
    for base in (ROOT/'kubejs',ROOT/'first_party_mods/alfheim_companion/src/main/resources'):
        if (base/path).exists():return Image.open(base/path).convert('RGBA')
    if path in ARCHIVES:return Image.open(io.BytesIO(ARCHIVES[path].read(path))).convert('RGBA')
    return None
def color(name):
    if name in CACHE:return CACHE[name]
    ns,key=name.split(':');mapped={'grass_block':'grass_block_top','podzol':'podzol_top','farmland':'farmland_moist','water':'water_still','lantern':'lantern','soul_lantern':'soul_lantern','barrel':'barrel_side','oak_fence':'oak_planks','red_carpet':'red_wool','yellow_carpet':'yellow_wool','light_blue_carpet':'light_blue_wool','snow_block':'snow','chain':'chain','campfire':'campfire_log','carrots':'carrots_stage3','potatoes':'potatoes_stage3','beetroots':'beetroots_stage3','wheat':'wheat_stage7','melon_stem':'melon_stem','pumpkin_stem':'pumpkin_stem'}
    if key.endswith('_fey_apartment'):ns='feywild';key=key.replace('_fey_apartment','_tree_log')
    if key.endswith(('_stairs','_slab','_fence')):key=key.rsplit('_',1)[0]
    im=texture(ns+':block/'+mapped.get(key,key))
    if im is not None:
        a=np.array(im);a=a[a[:,:,3]>100,:3];c=tuple(map(int,a.mean(axis=0))) if len(a) else (100,130,100)
    else:c=(125,115,100)
    if name=='minecraft:grass_block':c=(91,143,64)
    elif 'leaves' in name and ns=='minecraft':c=(80,132,58)
    elif name=='minecraft:water':c=(66,135,180)
    CACHE[name]=c;return c

def render(kind,variant):
    grid,_=read_village(kind,variant);solid={p:s for p,s in grid.items() if s['Name']!='minecraft:air'}
    scale=7;im=Image.new('RGB',(1400,1100),'#17232d');d=ImageDraw.Draw(im)
    def xy(x,y,z):return (700+(x-z)*scale,140+(x+z)*scale*.5-y*scale)
    def face(vertices,c):d.polygon([xy(*p) for p in vertices],fill=c)
    for (x,y,z),s in sorted(solid.items(),key=lambda p:sum(p[0])):
        c=color(s['Name']);top=c;left=tuple(int(v*.72) for v in c);right=tuple(int(v*.88) for v in c)
        if (x,y,z+1) not in solid:face([(x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1)],left)
        if (x+1,y,z) not in solid:face([(x+1,y,z),(x+1,y,z+1),(x+1,y+1,z+1),(x+1,y+1,z)],right)
        if (x,y+1,z) not in solid:face([(x,y+1,z),(x+1,y+1,z),(x+1,y+1,z+1),(x,y+1,z+1)],top)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
    d.text((25,25),THEMES[kind]+' / layout '+str(variant+1),font=title,fill='white')
    d.text((25,1045),'Actual emitted NBT / texture-derived voxel preview. Fine block models and in-game lighting are not shown.',font=font,fill='#adbfcc')
    im.save(ROOT/f'tools/fey_sky_{kind}_{variant}.png');return im

def homes():
    from render_monstrosities import render
    sheet=Image.new('RGB',(1600,520),'#17232d');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
    coords={'north':([(1,0,0),(0,0,0),(0,1,0),(1,1,0)],[0,0,-1]),'south':([(0,0,1),(1,0,1),(1,1,1),(0,1,1)],[0,0,1]),'west':([(0,0,0),(0,0,1),(0,1,1),(0,1,0)],[-1,0,0]),'east':([(1,0,1),(1,0,0),(1,1,0),(1,1,1)],[1,0,0]),'up':([(0,1,0),(0,1,1),(1,1,1),(1,1,0)],[0,1,0]),'down':([(0,0,1),(0,0,0),(1,0,0),(1,0,1)],[0,-1,0])}
    for i,kind in enumerate(CULTURES):
        model=json.loads((ROOT/f'first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion/models/block/{kind}_fey_apartment.json').read_text());atlas=Image.new('RGBA',(256,256));quads=[];names=list(model['textures'])
        for j,key in enumerate(names):
            tex=texture(model['textures'][key]);assert tex is not None,model['textures'][key]
            atlas.paste(tex.resize((32,32)),((j%8)*32,(j//8)*32))
        for e in model['elements']:
            lo=np.array(e['from']);hi=np.array(e['to'])
            for side,face in e['faces'].items():
                vertices,normal=coords[side];j=names.index(face['texture'][1:]);u,v=(j%8)/8,(j//8)/8
                quads.append({'vertices':[(lo+(hi-lo)*p-np.array([8,0,8])).tolist() for p in np.array(vertices)],'normal':normal,'uv':[[u,v+1/8],[u+1/8,v+1/8],[u+1/8,v],[u,v]]})
        tile=render(quads,np.array(atlas),size=400,yaw=155,scale=16,center_y=8);sheet.paste(tile,(i*400,50),tile);d.text((i*400+25,465),kind.title()+' log apartments',font=font,fill='white')
    d.text((25,10),'Native block models, recessed windows, doors and balconies / actual installed textures',font=font,fill='white');sheet.save(ROOT/'tools/fey_home_models.png')

def main():
    rows=[]
    for kind in CULTURES:
        row=Image.new('RGB',(1400,550))
        for v in range(2):row.paste(render(kind,v).resize((700,550)),(v*700,0))
        rows.append(row)
    overview=Image.new('RGB',(1400,2200))
    for i,row in enumerate(rows):overview.paste(row,(0,i*550))
    overview.save(ROOT/'tools/fey_sky_villages_review.png');homes();print('Rendered eight emitted islands and four actual native apartment block models')

if __name__=='__main__':main()
