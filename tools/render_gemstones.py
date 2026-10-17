"""Actual gem sprites, source distribution table and representative host-matched ore views."""
import csv,io,json,math,textwrap,zipfile
from PIL import Image,ImageDraw,ImageFont
from gen_gemstones import ROOT,ASSET,DATA
from gemstone_catalog import GEMS,POOLS
from gemstone_art import rendered

def main():
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
    jar=zipfile.ZipFile('C:/Users/Admin/curseforge/minecraft/Install/versions/1.20.1/1.20.1.jar')
    rows=[]
    for number,start in enumerate(range(0,len(GEMS),116)):
        gems=GEMS[start:start+116];sheet=Image.new('RGB',(1600,math.ceil(len(gems)/10)*118+90),'#192630');d=ImageDraw.Draw(sheet)
        d.text((22,14),f'NATURAL GEM MATERIALS / {number+1} / actual inventory sprites',font=title,fill='white')
        for i,g in enumerate(gems):
            im=rendered(g,128).resize((80,80),Image.Resampling.LANCZOS);x=(i%10)*160+40;y=(i//10)*118+55;sheet.paste(im,(x,y),im)
            for j,line in enumerate(textwrap.wrap(g['name'],22)):d.text((x-32,y+66+j*17),line,font=font,fill='#d5e2eb')
        sheet.save(ROOT/f'tools/gemstones_review_{number+1}.png')
    jar.close()
    with (ROOT/'tools/gemstone_catalogue.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['Gem material','Item ID','Deposit / source','Minimum Y','Maximum Y','Source category','Aliases'])
        for g in GEMS:
            p=POOLS[g['pool']];w.writerow([g['name'],g['item'],p['label'],*p['y'],p['source'],'; '.join(g['aliases'])])
    # Cube preview uses the exact host texture with the original transparent gem overlay.
    from render_fey_sky_villages import texture
    from render_monstrosities import render
    import numpy as np
    sheet=Image.new('RGB',(1600,math.ceil(len(POOLS)/6)*250+70),'#192630');d=ImageDraw.Draw(sheet);d.text((22,15),'DEPOSIT COLOURS / original overlays on native host texture',font=title,fill='white')
    base=texture('alfheim:block/cracked_livingrock');assert base is not None
    for i,(key,pool) in enumerate(POOLS.items()):
        overlay=Image.open(ROOT/(ASSET+f'textures/block/gemstones/{key}.png')).convert('RGBA')
        composite=Image.alpha_composite(base.resize((16,16)),overlay).resize((64,64),Image.Resampling.NEAREST)
        tile=Image.new('RGBA',(160,160));td=ImageDraw.Draw(tile)
        tile.alpha_composite(composite,(48,40));tile=tile.resize((180,180),Image.Resampling.NEAREST)
        x=(i%6)*265+35;y=(i//6)*250+60;sheet.paste(tile,(x,y),tile);d.text((x,y+180),pool['label'],font=font,fill='white');d.text((x,y+201),f"Y {pool['y'][0]} to {pool['y'][1]} / {pool['source']}",font=font,fill='#a5c5d5')
    sheet.save(ROOT/'tools/gemstone_deposits_review.png')
    pedestal_review()
    print('Rendered all 232 gem materials, representative deposit textures and player catalogue CSV')

def pedestal_review():
    from render_fey_sky_villages import texture
    from render_monstrosities import render
    import numpy as np
    model=json.loads((ROOT/'first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion/models/block/geologist_pedestal.json').read_text())
    faces={'north':([(1,0,0),(0,0,0),(0,1,0),(1,1,0)],[0,0,-1]),'south':([(0,0,1),(1,0,1),(1,1,1),(0,1,1)],[0,0,1]),'west':([(0,0,0),(0,0,1),(0,1,1),(0,1,0)],[-1,0,0]),'east':([(1,0,1),(1,0,0),(1,1,0),(1,1,1)],[1,0,0]),'up':([(0,1,0),(0,1,1),(1,1,1),(1,1,0)],[0,1,0]),'down':([(0,0,1),(0,0,0),(1,0,0),(1,0,1)],[0,-1,0])}
    wanted=['ruby','sapphire','emerald','watermelon_tourmaline','ammolite','black_pearl'];sheet=Image.new('RGB',(1500,1100),'#192630');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
    d.text((25,15),'GEOLOGIST DISPLAYS / native model and revised gem material previews',font=font,fill='white')
    for i,key in enumerate(wanted):
        g=next(g for g in GEMS if g['id']==key);atlas=Image.new('RGBA',(512,512));keys=list(model['textures']);quads=[]
        for j,k in enumerate(keys):
            im=texture(model['textures'][k]);assert im is not None,model['textures'][k];atlas.paste(im.resize((128,128)),((j%4)*128,(j//4)*128))
        def uv(j):u,v=(j%4)/4,(j//4)/4;return [[u,v+1/4],[u+1/4,v+1/4],[u+1/4,v],[u,v]]
        for e in model['elements']:
            lo=np.array(e['from']);hi=np.array(e['to'])
            for side,f in e['faces'].items():
                vertices,normal=faces[side];j=keys.index(f['texture'][1:]);quads.append({'vertices':[(lo+(hi-lo)*p-[8,0,8]).tolist() for p in np.array(vertices)],'normal':normal,'uv':uv(j)})
        j=len(keys);atlas.paste(rendered(g,128),((j%4)*128,(j//4)*128));quads.append({'vertices':[[-4,15,-.1],[4,15,-.1],[4,24,-.1],[-4,24,-.1]],'normal':[0,0,-1],'uv':uv(j)})
        tile=render(quads,np.array(atlas),size=500,yaw=155,scale=14,center_y=12);x=(i%3)*500;y=(i//3)*500+55;sheet.paste(tile,(x,y),tile);d.text((x+45,y+435),g['name'],font=font,fill='white')
    d.text((25,1060),'Offline asset preview; live rotation, lighting and engraved labels require an in-game review.',font=font,fill='#9eb8c9');sheet.save(ROOT/'tools/geologist_pedestals_review.png')

if __name__=='__main__':main()
