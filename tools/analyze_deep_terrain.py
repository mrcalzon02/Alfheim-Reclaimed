"""Read actual in-world cross-sections; compare the same seed/sites and draw evidence."""
from pathlib import Path
import collections
import json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
AIR={'minecraft:air','minecraft:cave_air','minecraft:void_air'}
CAVITY=AIR|{'minecraft:lava'}


def expand(section,palette):
    result=[]
    for runs in section['columns']:
        col=[]
        for i,n in runs: col.extend([palette[int(i)]]*int(n))
        assert len(col)==145
        result.append(col)
    assert len(result)==129
    return result


def longest(values):
    best=run=0
    for value in values:
        run=run+1 if value else 0; best=max(best,run)
    return best


def metrics(columns):
    # Only the designed underground envelope counts; surface sky is excluded.
    heights=[longest([col[y+64] in CAVITY for y in range(-59,28)]) for col in columns]
    widths=[2*longest([col[y+64] in CAVITY for col in columns]) for y in range(-56,15)]
    lava=[2*longest([col[y+64]=='minecraft:lava' for col in columns]) for y in range(-59,-48)]
    count=collections.Counter(block for col in columns for block in col[:92])
    solid=sum(n for b,n in count.items() if b not in CAVITY and b!='minecraft:water')
    ores=sum(n for b,n in count.items() if b.endswith('_ore'))
    return dict(max_open_height=max(heights),max_open_width=max(widths),max_lava_width=max(lava),
                lava_samples=count['minecraft:lava'],air_samples=sum(count[b] for b in AIR),
                ore_samples=ores,solid_samples=solid,ores_per_thousand_solid=round(1000*ores/max(1,solid),2),
                native_stones=sorted(b for b in count if b.startswith('alfheim:') and b.endswith('_livingrock')),
                bedrock_floor=all(col[0]=='minecraft:bedrock' for col in columns),
                stone_above_limit=sum(b.startswith('alfheim:') and b.endswith('_livingrock') for col in columns for b in col[88:]))


def main():
    treatment=json.loads((ROOT/'tools/deep_terrain_treatment.json').read_text())
    basefile=ROOT/'tools/deep_terrain_baseline.json'
    baseline=json.loads(basefile.read_text()) if basefile.exists() else None
    documents=[baseline,treatment] if baseline else [treatment]
    families=json.loads((ROOT/'tools/deepworks_manifest.json').read_text())['families']
    colors={'alfheim:'+f['id']:tuple(bytes.fromhex(f['color'])) for f in families}
    colors.update({'minecraft:air':(15,19,27),'minecraft:cave_air':(15,19,27),'minecraft:void_air':(15,19,27),
        'minecraft:lava':(255,115,32),'minecraft:water':(43,99,153),'minecraft:bedrock':(57,58,64),
        'botania:livingrock':(174,166,148),'alfheim:livingrock_slag':(79,74,83),
        'minecraft:dirt':(106,80,61),'minecraft:grass_block':(95,121,68)})
    results=[]
    width=1120 if baseline else 620
    sheet=Image.new('RGB',(width,190+6*260),(22,28,36)); draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25)
    draw.text((24,18),'THE DEEP / GENERATED TERRAIN',font=title,fill='#eee3cd')
    draw.text((24,58),'Actual blocks from three sites; two perpendicular sections each.',font=font,fill='#bccdd1')
    draw.text((24,82),'Samples: 2 blocks across / 1 block high. Orange: lava. Gold: ore.',font=font,fill='#bccdd1')
    for k,doc in enumerate(documents):
        draw.text((70+k*530,123),doc['mode'].upper(),font=title,fill='#e6d6b6')
        for i,section in enumerate(doc['sections']):
            cols=expand(section,doc['palette']); m=metrics(cols)
            results.append(dict(mode=doc['mode'],site=section['site'],axis=section['axis'],**m))
            tile=Image.new('RGB',(258,145))
            for x,col in enumerate(cols):
                for y,block in enumerate(col):
                    color=colors.get(block,(233,198,81) if block.endswith('_ore') else (114,110,112))
                    tile.putpixel((x*2,144-y),color); tile.putpixel((x*2+1,144-y),color)
            x=70+k*530; y=190+i*260
            # Uniform scale preserves physical aspect ratio: x pixels already span 2 blocks.
            tile=tile.resize((464,261),Image.Resampling.NEAREST)
            # Display the underground portion y=-64..40, preserving the same aspect ratio.
            tile=tile.crop((0,72,464,261))
            sheet.paste(tile,(x,y))
            p=doc['centers'][int(section['site'])]
            draw.text((x,y-27),f"Site {section['site']+1} | {'X' if section['axis']==0 else 'Z'} cut | {p['x']}, {p['z']}",font=font,fill='#d9e0df')
            draw.text((x,y+192),f"Open: {m['max_open_width']}w / {m['max_open_height']}h | Lava span: {m['max_lava_width']}",font=font,fill='#c4d1ce')
            for label,offset in [('40',0),('0',72),('-32',130),('-64',188)]:
                draw.text((x-36,y+offset-8),label,font=font,fill='#a4b7bd')
    summary={'sections':results,'treatment_world':treatment['world'],'treatment_console':treatment['console']}
    if baseline:
        assert baseline['centers']==treatment['centers'], 'Sites differ'
        summary['upper_density_equal']=baseline['density_upper']==treatment['density_upper']
        summary['surface_height_differences']=sum(a!=b for a,b in zip(baseline['surface'],treatment['surface']))
        summary['surface_height_details']=[{'baseline':a,'treatment':b} for a,b in
            zip(baseline['surface'],treatment['surface']) if a!=b]
        summary['bottom_block_differences']=sum(
            a[0]!=b[0] for sa,sb in zip(baseline['sections'],treatment['sections'])
            for a,b in zip(expand(sa,baseline['palette']),expand(sb,treatment['palette'])))
        summary['baseline_world']=baseline['world']
        summary['totals']={}
        for mode in ['baseline','treatment']:
            group=[r for r in results if r['mode']==mode]
            totals={key:sum(r[key] for r in group) for key in ['lava_samples','air_samples','ore_samples','solid_samples']}
            totals['ores_per_thousand_solid']=round(1000*totals['ore_samples']/max(1,totals['solid_samples']),2)
            summary['totals'][mode]=totals
    summary['unique_natural_stones']=sorted(set(s for r in results if r['mode']=='treatment' for s in r['native_stones']))
    if baseline:
        treated=[r for r in results if r['mode']=='treatment']
        summary['checks']={
            'upper_density_preserved':summary['upper_density_equal'],
            'bottom_blocks_preserved':summary['bottom_block_differences']==0,
            'no_library_stone_above_y23':all(r['stone_above_limit']==0 for r in treated),
            'three_large_lava_sites':all(any(r['site']==site and r['max_open_width']>=96
                and r['max_open_height']>=25 and r['max_lava_width']>=32 for r in treated) for site in range(3)),
            'added_cavity_samples':summary['totals']['treatment']['air_samples']>summary['totals']['baseline']['air_samples'],
            'richer_ore_in_solid_rock':summary['totals']['treatment']['ores_per_thousand_solid']>
                                    summary['totals']['baseline']['ores_per_thousand_solid']}
    path=ROOT/'tools/deep_terrain_summary.json'; path.write_text(json.dumps(summary,indent=2)+'\n')
    sheet.save(ROOT/'tools/deep_terrain_sections.png')
    print(json.dumps(summary,indent=2))
    if baseline and not all(summary['checks'].values()): raise SystemExit(1)


if __name__=='__main__': main()
