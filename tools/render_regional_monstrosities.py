"""Offline full-body review from actual baked model exports and shipped UV skins."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from render_fey_heads import render
from regional_monstrosity_skins import REGIONS
ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion'

def main():
    models=json.loads((ROOT/'tools/regional_monster_review_models.json').read_text())
    sheet=Image.new('RGB',(1080,1250),'#192127');d=ImageDraw.Draw(sheet)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',22)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
    d.text((22,16),'REGIONAL MONSTROSITIES / THREE RIGS, NINE SKINS',font=title,fill='white')
    labels={'zombie':'Ashen Revenant','pillager':'Rime Outcast','enderman':'Verge Riftwalker'}
    for column,(species,profile) in enumerate(REGIONS.items()):
        for style in range(3):
            skin=Image.open(RES/f'textures/entity/themed/{species}_{profile}_{style}.png').convert('RGBA')
            tile=render(models[species],330,{'base':np.array(skin)},directional_light=True)
            x=column*360+15;y=style*385+60;sheet.paste(tile,(x,y),tile)
            d.text((x+12,y+330),labels[species]+' / '+['Bound','Shrouded','Crowned'][style],font=font,fill='#dce5e4')
    d.text((22,1222),'Baked geometry / actual skins. Offline neutral pose; client animation and lighting review pending.',font=font,fill='#9baeb4')
    sheet.save(ROOT/'tools/regional_monstrosities_review.png')
    print('Rendered nine full-body regional appearances')
if __name__=='__main__':main()
