"""Geometry contact sheet from the authored collision/model manifest; not a screenshot."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from gen_war_remains_materials import SPECS
ROOT=Path(__file__).resolve().parents[1]

def main():
    m=json.loads((ROOT/'tools/war_salvage_manifest.json').read_text())
    colors={n:c for n,_,c in SPECS}
    im=Image.new('RGB',(1080,680),(20,24,31));d=ImageDraw.Draw(im)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',21)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
    d.text((20,14),'WAR SALVAGE / RECOVERED OBJECTS',font=title,fill='white')
    for i,(name,(tex,light,boxes)) in enumerate(m['objects'].items()):
        cx=180+(i%3)*360;cy=175+(i//3)*280
        grid={(x,y,z) for a,b in boxes for x in range(a[0],b[0]) for y in range(a[1],b[1]) for z in range(a[2],b[2])}
        def proj(x,y,z):return cx+(x-z)*6,cy+(x+z)*3-y*6
        for x,y,z in sorted(grid,key=lambda p:sum(p)):
            faces=[((0,1,0),[(x,y+1,z),(x+1,y+1,z),(x+1,y+1,z+1),(x,y+1,z+1)],1.15),
                ((1,0,0),[(x+1,y,z),(x+1,y,z+1),(x+1,y+1,z+1),(x+1,y+1,z)],.82),
                ((0,0,1),[(x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1)],.62)]
            for (dx,dy,dz),points,shade in faces:
                if (x+dx,y+dy,z+dz) not in grid:d.polygon([proj(*p) for p in points],fill=tuple(min(255,int(c*shade)) for c in colors[tex]))
        d.text((cx-155,cy+105),name.replace('_',' ').title(),font=small,fill='#e2e8ed')
        d.text((cx-155,cy+127),f'Light {light}/15' if light else 'Salvage display / no active core',font=small,fill='#9babbc')
    d.text((20,650),'Geometry preview; Minecraft textures, lighting and item display require client review.',font=small,fill='#a3b0bc')
    im.save(ROOT/'tools/war_salvage_models_review.png')

if __name__=='__main__':main()
