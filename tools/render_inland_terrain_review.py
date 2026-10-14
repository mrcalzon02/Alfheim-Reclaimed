"""Render measured saved-foundation gaps, without inventing a terrain screenshot."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import nbt
from check_ancient_assembly import world_pos

ROOT=Path(__file__).resolve().parents[1]

def main():
    data=json.loads((ROOT/'tools/inland_terrain_review.json').read_text(encoding='utf-8'))
    scale=3;panel=510;pad=26;top=145
    im=Image.new('RGB',(panel*3,650),'#f1efe8');draw=ImageDraw.Draw(im)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',27)
    sub=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',12)
    draw.text((pad,20),'Inland prototype foundation review',fill='#273630',font=title)
    draw.text((pad,60),'Saved forced placements at one Golden Fields locality; normal terrain adaptation is not tested.',fill='#425249',font=sub)
    names={'sacred_precinct':'Sacred Precinct','military_warden':'Military / Warden','frontier_stewardship':'Frontier / Wilderness'}
    for index,family in enumerate(data['families']):
        rects=[]
        for p in family['pieces']:
            path=ROOT/f'kubejs/data/alfheim/structures/ancient/{family["family"]}/{p["name"]}.nbt'
            raw=nbt.load(str(path))[1];sx,_,sz=map(int,raw['size'])
            pts=[world_pos(v,p['origin'],p['rotation']) for v in ((0,0,0),(sx-1,0,sz-1),(0,0,sz-1),(sx-1,0,0))]
            rects.append((p,[min(v[0] for v in pts),min(v[2] for v in pts),max(v[0] for v in pts)+1,max(v[2] for v in pts)+1]))
        x0=min(r[0] for p,r in rects);z0=min(r[1] for p,r in rects)
        width=max(r[2] for p,r in rects)-x0
        ox=index*panel+(panel-width*scale)//2
        def point(x,z):return ox+(x-x0)*scale,top+(z-z0)*scale
        draw.text((index*panel+pad,102),names[family['family']],fill='#273630',font=sub)
        for piece,r in rects:
            a,b=point(r[0],r[1]);c,d=point(r[2],r[3]);draw.rectangle((a,b,c,d),fill='#b9c9b4',outline='#526056',width=1)
            for xmin,xmax,z,ymin,ymax in piece['supplemental_footing_plan']['runs']:
                depth=ymax-ymin+1;color='#e0b557' if depth<=3 else '#c66e4f' if depth<=6 else '#8e3946'
                x1,z1=point(xmin,z);x2,z2=point(xmax+1,z+1);draw.rectangle((x1,z1,x2-1,z2-1),fill=color)
            for item in piece['supplemental_footing_plan']['obstructed_columns']:
                x,y,z=item['position'];px,pz=point(x,z);draw.rectangle((px,pz,px+2,pz+2),fill='#343946')
            label=piece['name'].replace('_',' ');words=label.split();lines=[];line=''
            for word in words:
                trial=(line+' '+word).strip()
                if line and draw.textlength(trial,font=font)>c-a-10:lines.append(line);line=word
                else:line=trial
            lines.append(line)
            draw.multiline_text(((a+c)/2,(b+d)/2),'\n'.join(lines),font=font,fill='#25352d',anchor='mm',align='center')
        s=family['actual_saved_native_contact']
        draw.text((index*panel+pad,535),f"Native contact: {s['contact_fraction']:.1%}; largest gap: {s['max_gap_below_base']} blocks",fill='#425249',font=sub)
    legend=[('#b9c9b4','Native ground contact'),('#e0b557','1-3 block gap'),('#c66e4f','4-6 block gap'),('#8e3946','7+ block gap'),('#343946','Other blocks: review')]
    x=pad
    for color,label in legend:
        draw.rectangle((x,585,x+18,603),fill=color);draw.text((x+26,582),label,font=sub,fill='#425249');x+=int(draw.textlength(label,font=sub))+65
    draw.text((pad,618),'North is up. Gap-only repair estimates are not applied; approaches, excavation and natural placement still need review.',font=sub,fill='#425249')
    out=ROOT/'alfheim_reclaimed_design/inland_terrain_review.png';im.save(out);print(out)

if __name__=='__main__':main()
