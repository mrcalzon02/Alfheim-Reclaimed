"""Show proposed footprint changes over measured saved terrain, without editing saves."""
import json
import argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageColor
from survey_saved_harbor_coasts import load_columns,rotate

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--core',action='store_true');args=ap.parse_args()
    screen=json.loads((ROOT/'tools/harbor_adaptation_screen.json').read_text(encoding='utf-8'))
    grid,_=load_columns(screen['world'])
    site=screen['variants']['core_with_approach' if args.core else 'narrow_docks_inland_temple']['best_candidates'][0]
    x,z,r=site['x'],site['z'],site['rotation']
    font=lambda size:ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',size)
    variants=[(name,v) for name,v in screen['variants'].items() if (name in ('shipping','core_with_approach') if args.core else name!='core_with_approach')]
    rows=(len(variants)+1)//2;legend_top=115+rows*680+10
    out=Image.new('RGB',(1280,115+rows*680+155),'#151c27');d=ImageDraw.Draw(out)
    d.text((30,20),'Harbor footprint studies',font=font(32),fill='white')
    d.text((30,70),f'Saved coast at X={x}, Z={z}; orientation {r}. Footprints only.',font=font(20),fill='#c5cfdf')
    colors={'reachable water':'#569ed6','water beyond footing':'#254676','supported land':'#577d61',
            'land above quay':'#b37a4c','low unsupported ground':'#b45493','unknown / decorated':'#394353'}
    names={'shipping':'Current harbor','narrow_docks':'Narrower, shorter docks',
           'inland_temple':'Temple moved inland','narrow_docks_inland_temple':'Narrow docks + inland temple',
           'core_with_approach':'Required core + inland access'}
    for index,(name,v) in enumerate(variants):
        ox=30+(index%2)*630;oy=115+(index//2)*680
        d.text((ox,oy),names[name],font=font(24),fill='white')
        terrain=Image.new('RGB',(200,200),colors['unknown / decorated'])
        for px in range(200):
            for pz in range(200):
                lx,lz=px-85,pz-75;dx,dz=rotate(lx,lz,r);c=grid.get((x+dx,z+dz))
                if not c:continue
                s,f=c
                if s==64 and f<64:color=colors['reachable water' if f>=58 else 'water beyond footing']
                elif s!=f:color=colors['unknown / decorated']
                elif s>73:color=colors['land above quay']
                elif f<58:color=colors['low unsupported ground']
                else:color=colors['supported land']
                terrain.putpixel((px,pz),ImageColor.getrgb(color))
        top=oy+40;out.paste(terrain.resize((600,600),Image.Resampling.NEAREST),(ox,top))
        for part in v['layout']:
            x0,z0,x1,z1=part['bounds']
            box=(ox+(x0+85)*3,top+(z0+75)*3,ox+(x1+86)*3,top+(z1+76)*3)
            d.rectangle(box,outline='#fff2ac',width=2)
            label=part['name'].replace('harbor_','').replace('sunken_','').replace('signal_','').replace('_',' ')
            if label=='dockworker housing':label='housing'
            if label=='harbormaster house':label='master'
            if label=='bonded warehouse':label='warehouse'
            if label=='wavebreak pier':label='pier'
            if label=='tide temple':label='temple'
            d.text((box[0]+3,box[1]+4),label,font=font(13),fill='white',stroke_width=1,stroke_fill='#101821')
        d.text((ox,top+610),f"{v['fully_covered_candidates']} sites fully covered by saved data; {v['coarse_passes']} coarse passes",font=font(17),fill='#c5cfdf')
    for i,(name,color) in enumerate(colors.items()):
        px=30+(i%3)*420;py=legend_top+(i//3)*36
        d.rectangle((px,py,px+22,py+22),fill=color)
        d.text((px+32,py-2),name,font=font(18),fill='white')
    d.text((30,legend_top+90),'Decoration affects saved heights. These studies do not establish native terrain fit.',font=font(19),fill='#c5cfdf')
    path=ROOT/'alfheim_reclaimed_design'/('harbor_required_core_study.png' if args.core else 'harbor_adaptation_studies.png');out.save(path)
    print(path)

if __name__=='__main__':main()
