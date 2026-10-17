"""Render actual installed elf skins (including pack overrides) with clothing and baked finery."""
import copy,io,json,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from render_fey_heads import render
ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion'

def main():
    catalogue=json.loads((ROOT/'tools/elven_society_geometry.json').read_text())
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15);title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',22)
    with zipfile.ZipFile(ROOT/'mods/richs_races_wood_elves-1.0.0-forge-1.20.1.jar') as archive:
        for page in range(3):
            sheet=Image.new('RGB',(1280,1430),'#1b2529');d=ImageDraw.Draw(sheet)
            d.text((22,16),['ELVEN WORKERS AND HOUSEHOLD','ELVEN NOBILITY','ELVEN ROYAL FAMILY'][page],font=title,fill='white')
            for row in range(4):
                role=catalogue['roles'][page*4+row];model=catalogue['bodies'][role['id']]
                for look in range(4):
                    ns,path=role['base_skins'][look].split(':');asset=f'assets/{ns}/textures/{path}.png'
                    override=ROOT/'kubejs'/asset
                    original=Image.open(override if override.exists() else io.BytesIO(archive.read(asset))).convert('RGBA')
                    cloth=Image.open(RES/f"textures/entity/society/{role['id']}_{look}.png").convert('RGBA')
                    original=Image.alpha_composite(original,cloth)
                    wardrobe=Image.open(RES/f"textures/entity/society/wardrobe/{role['id']}_{look}.png").convert('RGBA')
                    tile=render(model,280,{'base':np.array(original),'wardrobe':np.array(wardrobe)},directional_light=True)
                    x=look*320+20;y=row*335+55;sheet.paste(tile,(x,y),tile)
                    d.text((x+12,y+282),role['name']+' / '+str(look+1),font=font,fill='#dce6df')
            d.text((22,1397),'Installed wood-elf identity skins + role clothing/finery. Offline pose; client animation/lighting review pending.',font=font,fill='#99acb2')
            sheet.save(ROOT/f'tools/elven_society_review_{page+1}.png')
        detail=Image.new('RGB',(1200,650),'#1b2529');d=ImageDraw.Draw(detail)
        d.text((20,15),'UPWARD EARS / ORIGINAL SKINS / MODELED FINERY',font=title,fill='white')
        for row,role_index in enumerate((10,11)):
            role=catalogue['roles'][role_index];ns,path=role['base_skins'][0].split(':');asset=f'assets/{ns}/textures/{path}.png'
            override=ROOT/'kubejs'/asset
            original=Image.open(override if override.exists() else io.BytesIO(archive.read(asset))).convert('RGBA')
            wardrobe=Image.open(RES/f"textures/entity/society/wardrobe/{role['id']}_0.png").convert('RGBA')
            for col,angle in enumerate((180,90,0)):
                model=copy.deepcopy(catalogue['bodies'][role['id']]);model['display']['gui']['rotation']=[0,angle,0]
                tile=render(model,280,{'base':np.array(original),'wardrobe':np.array(wardrobe)},directional_light=True)
                detail.paste(tile,(col*400+60,row*290+45),tile)
                d.text((col*400+90,row*290+320),role['name']+' / '+['front','side','back'][col],font=font,fill='white')
        detail.save(ROOT/'tools/elven_society_detail.png')
    print('Rendered all 48 reference-faithful elven civilians')
if __name__=='__main__':main()
