"""Render all 390 exported head models with native materials and their actual biome tints."""
import io,json,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from gen_themed_enemies import ROOT,RES,profiles,SPECIES
from render_fey_heads import render

def main():
    jar=ROOT.parent.parent/'Install/versions/1.20.1/1.20.1.jar'
    cache={}; rows=profiles();font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',12)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',21)
    with zipfile.ZipFile(jar) as archive:
        def texture(key):
            if key not in cache:
                namespace,name=key.split(':');path=f'assets/{namespace}/textures/{name}.png'
                im=Image.open(ROOT/RES/path).convert('RGBA') if namespace=='alfheim_companion' else Image.open(io.BytesIO(archive.read(path))).convert('RGBA')
                if path+'.mcmeta' in archive.namelist():
                    # Native animated block sprite: show its first frame, not the vertical strip.
                    meta=json.loads(archive.read(path+'.mcmeta')).get('animation',{})
                    width=meta.get('width',im.width);height=meta.get('height',width)
                    im=im.crop((0,0,width,height))
                cache[key]=np.array(im)
            return cache[key]
        for _,_,species,label in SPECIES:
            sheet=Image.new('RGB',(960,1950),'#171d27');draw=ImageDraw.Draw(sheet)
            draw.text((20,15),f'{label.upper()} / 26 BIOMES × 3 COLOR STYLES',font=title,fill='white')
            for p,row in enumerate(rows):
                for style in range(3):
                    path=ROOT/RES/f'assets/alfheim_companion/models/item/enemy_heads/{species}_{p}_{style}.json'
                    model=json.loads(path.read_text());images={k:texture(v) for k,v in model['textures'].items()}
                    tints=[int(row['body'],16),int(row['accent'],16)]
                    tile=render(model,112,images,tints)
                    col=(p%2)*3+style;x=col*160+24;y=(p//2)*143+52
                    sheet.paste(tile,(x,y),tile)
                    draw.text((col*160+8,y+112),row['title']+' '+['Bound','Shrouded','Crowned'][style],font=font,fill='#d9e2ef')
            draw.text((20,1924),'Offline textured models; actual client lighting and animation review pending.',font=font,fill='#9cabc0')
            sheet.save(ROOT/f'tools/themed_heads_{species}_review.png')
    print('Rendered all 390 head selections across five species sheets')

if __name__=='__main__':main()
