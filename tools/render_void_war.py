"""Voxel previews of the actual NBT assets, not Minecraft screenshots."""
from PIL import Image,ImageDraw,ImageFont
import nbt
from gen_void_war import ROOT
from gen_war_remains_materials import SPECS

def main():
    colors={'alfheim:'+n:c for n,_,c in SPECS}
    colors.update({'alfheim:riftshale_livingrock':(79,84,94),'alfheim:mana_glass_light':(110,195,185)})
    im=Image.new('RGB',(1200,610),(19,23,30));d=ImageDraw.Draw(im)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',21);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
    for panel,(name,label) in enumerate((('crystal_hulk','CRYSTAL HULK / CORE EXTRACTED'),('bio_titan','BIOMASS TITAN / RUPTURED FLANK'))):
        root=nbt.load(ROOT/f'kubejs/data/alfheim/structures/void_war/{name}.nbt')[1]
        grid={(int(b['pos'][0]),int(b['pos'][1]),46-int(b['pos'][2])):root['palette'][int(b['state'])]['Name'] for b in root['blocks'] if root['palette'][int(b['state'])]['Name'] not in ('minecraft:air','minecraft:cave_air')}
        cx,cy=300+panel*600,210
        def project(x,y,z):return cx+(x-z)*5,cy+(x+z)*2.5-y*5
        for (x,y,z),rid in sorted(grid.items(),key=lambda p:sum(p[0])):
            if y<4:continue
            c=colors.get(rid,(110,116,128))
            faces=[((0,1,0),[(x,y+1,z),(x+1,y+1,z),(x+1,y+1,z+1),(x,y+1,z+1)],1.12),
                   ((1,0,0),[(x+1,y,z),(x+1,y,z+1),(x+1,y+1,z+1),(x+1,y+1,z)],.82),
                   ((0,0,1),[(x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1)],.62)]
            for (dx,dy,dz),points,shade in faces:
                if (x+dx,y+dy,z+dz) in grid:continue
                d.polygon([project(*p) for p in points],fill=tuple(min(255,int(v*shade)) for v in c))
        d.text((panel*600+20,22),label,font=title,fill='#e2e8ed')
        d.text((panel*600+20,535),'47-block module • rendered from emitted structure NBT',font=small,fill='#a9b6c3')
    d.text((20,580),'Design preview only. Textures, lighting and terrain integration require Minecraft client review.',font=small,fill='#94a4b6')
    im.save(ROOT/'tools/void_war_colossi_review.png')
    print('Rendered two actual colossus templates')
if __name__=='__main__':main()
