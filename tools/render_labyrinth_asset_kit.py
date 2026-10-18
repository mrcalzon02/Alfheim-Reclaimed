"""Review the emitted NBT and the original textured creature surfaces, offline."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import nbt
from gen_labyrinth_asset_kit import OUT
from render_monstrosities import render as render_creature
from render_template_plan import classify

FONT = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 17)
SMALL = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 14)
TITLE = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 27)
BG = '#171f27'


def room_cells(path):
    root = nbt.load(path)[1]
    palette = root['palette']
    return {tuple(b['pos']): palette[int(b['state'])]['Name'] for b in root['blocks']}, root['size']


def plans(manifest):
    rows = [r for r in manifest['pieces'] if r['condition'] == 'weathered']
    out = Image.new('RGB', (1500, 1290), BG)
    d = ImageDraw.Draw(out)
    d.text((24, 16), 'ASHEN CLOISTER / FIRST MODULAR ASSET KIT', font=TITLE, fill='white')
    d.text((24, 54), 'Actual NBT floor slices at feet height. Blue lines mark reserved routes; cyan marks water.', font=FONT, fill='#acbecb')
    for i, row in enumerate(rows):
        cells, size = room_cells(OUT / row['path'])
        tile = Image.new('RGB', (29, 29), '#222a32')
        for x in range(size[0]):
            for z in range(size[2]):
                name = cells.get((x, 2, z), 'minecraft:air')
                color = (36, 44, 51) if name == 'minecraft:air' else classify(name)
                if name == 'minecraft:water':
                    color = (56, 138, 163)
                if name == 'minecraft:air' and ((12 <= x <= 16 or 12 <= z <= 16) if size[0] == 29 else 1 <= x <= 5):
                    color = (42, 69, 85)
                tile.putpixel((x, z), color or (36, 44, 51))
        x, y = (i % 5) * 296 + 17, (i // 5) * 235 + 94
        out.paste(tile.resize((174, 174), Image.Resampling.NEAREST), (x + 47, y))
        d.text((x + 8, y + 179), row['family'].replace('_', ' ').title(), font=SMALL, fill='white')
        d.text((x + 8, y + 199), ' × '.join(map(str, size)) + ' blocks', font=SMALL, fill='#91a5b3')
    d.text((24, 1260), 'Staged art and geometry. Refuge services, encounters, portals and natural placement remain pending.', font=FONT, fill='#adc0cd')
    out.save(OUT / 'room_floorplans.png')


def material(name):
    if 'water' in name: return (47, 117, 144)
    if 'copper' in name: return (155, 108, 67)
    if 'sea_lantern' in name: return (170, 223, 207)
    if 'glass' in name: return (101, 155, 151)
    if 'bone' in name: return (199, 188, 151)
    if 'moss' in name: return (93, 113, 88)
    if any(k in name for k in ('spruce', 'bookshelf', 'hay')): return (118, 87, 61)
    if 'chiseled' in name: return (152, 151, 139)
    if 'cracked' in name: return (104, 106, 105)
    if 'cobweb' in name: return (177, 185, 168)
    return (124, 127, 125)


def cutaway(cells, size, tile_size=650):
    # Remove the front two walls and roof *in this preview only*.
    cells = {p: n for p, n in cells.items() if n != 'minecraft:air' and p[1] <= 10 and p[0] < size[0]-2 and p[2] < size[2]-2}
    out = Image.new('RGBA', (tile_size, 520))
    d = ImageDraw.Draw(out)
    s = 9
    def project(p):
        x, y, z = p
        return (tile_size/2 + (x-z)*s, 160 + (x+z)*s*.48 - y*s)
    for (x, y, z), name in sorted(cells.items(), key=lambda row: (sum(row[0][::2]), row[0][1])):
        c = material(name)
        faces = [((1, 0, 0), [(x+1,y,z),(x+1,y,z+1),(x+1,y+1,z+1),(x+1,y+1,z)], .70),
                 ((0, 0, 1), [(x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1)], .88),
                 ((0, 1, 0), [(x,y+1,z),(x+1,y+1,z),(x+1,y+1,z+1),(x,y+1,z+1)], 1.1)]
        for (dx, dy, dz), verts, light in faces:
            if (x+dx,y+dy,z+dz) not in cells:
                d.polygon([project(v) for v in verts], fill=tuple(min(255, round(a*light)) for a in c), outline=tuple(round(a*.63) for a in c))
    bbox = out.getbbox()
    if bbox:
        crop = out.crop(bbox)
        out = Image.new('RGBA', (tile_size, 520))
        out.paste(crop, ((tile_size-crop.width)//2, max(0,(520-crop.height)//2)))
    return out


def rooms(manifest):
    names = ['ruined_nave', 'ossuary', 'bell_chamber', 'cistern', 'boss_sanctuary', 'switchback_stair']
    sheet = Image.new('RGB', (1400, 1740), BG)
    d = ImageDraw.Draw(sheet)
    d.text((24, 15), 'ASHEN CLOISTER / GEOMETRY CUTAWAYS', font=TITLE, fill='white')
    d.text((24, 53), 'Flat material colors; roof and front walls hidden for inspection. Authored NBT remains sealed.', font=FONT, fill='#a9becb')
    for i, family in enumerate(names):
        row = next(r for r in manifest['pieces'] if r['family'] == family and r['condition'] == 'weathered')
        tile = cutaway(*room_cells(OUT / row['path']))
        x, y = (i % 2) * 700 + 25, (i // 2) * 540 + 80
        sheet.paste(tile, (x, y), tile)
        d.text((x+25, y+496), family.replace('_', ' ').title(), font=FONT, fill='white')
    d.text((24, 1704), 'Offline artifact preview. Template placement, stair movement and client visual acceptance remain pending.', font=FONT, fill='#a9becb')
    sheet.save(OUT / 'room_cutaways.png')


def creatures(manifest):
    sheet = Image.new('RGB', (1440, 1600), BG)
    d = ImageDraw.Draw(sheet)
    d.text((24, 14), 'ASHEN CLOISTER / ORIGINAL CREATURE SCULPTURES', font=TITLE, fill='white')
    d.text((24, 54), 'Textured art prototypes at shared scale. Front, three-quarter and rear views.', font=FONT, fill='#acc1cb')
    for i, row in enumerate(manifest['models']):
        g = json.loads((OUT / row['geometry']).read_text())
        texpath = (OUT / row['geometry']).parent / (row['catalog_id'] + '_cloister_ash.png')
        texture = np.array(Image.open(texpath).convert('RGBA'))
        vertices = np.array([v for q in g['quads'] for v in q['vertices']])
        center_y = (vertices[:,1].min() + vertices[:,1].max()) / 2
        for j, yaw in enumerate((180, 145, 25)):
            tile = render_creature(g['quads'], texture, size=440, yaw=yaw, scale=7, center_y=center_y)
            x, y = j*480+20, i*490+95
            sheet.paste(tile, (x,y), tile)
            d.text((x+18,y+411), ['Front','Three-quarter','Rear'][j], font=SMALL, fill='#8fa5b3')
        d.text((24, i*490+529), row['catalog_id'].replace('_',' ').title() + f" / {row['part_count']} sculpted parts / 512px atlas / {row['role']}", font=FONT, fill='white')
    d.text((24,1560),'Original model surfaces with the existing material painter. Creature behaviors, animation and in-game acceptance remain pending.',font=SMALL,fill='#a9becb')
    sheet.save(OUT / 'creature_sculptures.png')
    looks = Image.new('RGB',(1440,1530),BG)
    ld = ImageDraw.Draw(looks)
    ld.text((24,14),'THREE APPEARANCES / SHARED ANATOMIES',font=TITLE,fill='white')
    for i,row in enumerate(manifest['models']):
        g=json.loads((OUT/row['geometry']).read_text())
        vertices=np.array([v for q in g['quads'] for v in q['vertices']])
        for j,look in enumerate(row['looks']):
            texpath=(OUT/row['geometry']).parent/(row['catalog_id']+'_'+look+'.png')
            tile=render_creature(g['quads'],np.array(Image.open(texpath).convert('RGBA')),size=440,yaw=145,scale=7,center_y=float((vertices[:,1].max()+vertices[:,1].min())/2))
            x,y=j*480+20,i*485+60
            looks.paste(tile,(x,y),tile)
            ld.text((x+18,y+414),look.replace('_',' ').title(),font=FONT,fill='#c4d3dc')
    looks.save(OUT/'creature_appearances.png')


def main():
    structures = json.loads((OUT / 'structure_manifest.json').read_text())
    art = json.loads((OUT / 'creature_art_manifest.json').read_text())
    plans(structures)
    rooms(structures)
    creatures(art)
    print('Rendered emitted NBT floor plans/cutaways and all nine textured creature looks.')


if __name__ == '__main__':
    main()
