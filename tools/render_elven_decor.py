"""Catalog diagrams from emitted model faces; these are not Minecraft screenshots."""
import json
from PIL import Image,ImageDraw,ImageFont
from gen_elven_decor import ROOT,RES

COLORS={'wood':(162,139,99),'log':(111,95,76),'gold':(219,179,75),'gem':(156,117,190),'quartz':(219,216,201),
    'paper':(209,196,162),'green':(89,129,94),'purple':(101,71,139),'blue':(107,160,187),'dark':(61,64,76),'leaf':(89,123,67),'glass':(147,204,208)}

def render(filename,categories,title):
    manifest=json.loads((ROOT/'tools/elven_decor_manifest.json').read_text())['objects']
    entries=[(k,o) for k,o in manifest.items() if o['category'] in categories]
    rows=(len(entries)+3)//4;im=Image.new('RGB',(1440,rows*320+100),(19,23,30));d=ImageDraw.Draw(im)
    large=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',23);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
    d.text((22,14),title,font=large,fill='white')
    for i,(key,o) in enumerate(entries):
        cx=180+(i%4)*360;cy=220+(i//4)*320;faces=[];scale=4.5
        def p(x,y,z):return cx+(x+z-16)*scale,cy+(x+16-z)*scale*.5-y*scale
        for part_index,part in enumerate(o['parts']):
            model=json.loads((RES/f'assets/alfheim_leyworks/models/block/{part["model"]}.json').read_text())
            dx=16*part_index if o['kind']=='SOFA' else 0;dy=16*part_index if o['kind']=='TALL' else 0
            for e in model['elements']:
                x,y,z=e['from'];X,Y,Z=e['to'];x+=dx;X+=dx;y+=dy;Y+=dy
                points={'up':[(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],'north':[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z)],'east':[(X,y,z),(X,y,Z),(X,Y,Z),(X,Y,z)]}
                for f,poly in points.items():
                    if f not in e['faces']:continue
                    tex=e['faces'][f]['texture'].lstrip('#');c=COLORS[tex];shade={'up':1.12,'north':.81,'east':.65}[f]
                    depth=sum(a+16-c+b*.08 for a,b,c in poly)/4
                    faces.append((depth,[p(*v) for v in poly],tuple(min(255,int(v*shade)) for v in c),tex))
        for _,poly,color,texture in sorted(faces,key=lambda f:f[0]):
            if texture=='glass':d.line(poly+[poly[0]],fill='#a1c4cc',width=1)
            else:d.polygon(poly,fill=color)
        d.text((cx-160,cy+70),o['name'],font=small,fill='#e2e8ed')
        label='Two-block sofa' if o['kind']=='SOFA' else 'Two-block figure' if o['category']=='statue' else 'Fixed display' if o['category']=='display' else 'Wall ornament' if o['kind']=='WALL' else 'Decorative furnishing'
        d.text((cx-160,cy+94),label,font=small,fill='#9cabbc')
    d.text((22,im.height-28),'Geometry diagram from authored models. Glass shown as outlines; in-game textures and lighting require client review.',font=small,fill='#9cabbc')
    im.save(ROOT/'tools'/filename)

if __name__=='__main__':
    render('elven_decor_interiors.png',{'seating','display'},'ELVEN DECOR / SEATING AND FIXED DISPLAY CABINETS')
    render('elven_decor_honors.png',{'honors','arms','trophy'},'ELVEN DECOR / HONORS, TROPHIES AND WALL ARMS')
    render('elven_decor_statues.png',{'statue','ornament'},'ELVEN DECOR / KNIGHTS, GODDESS FIGURES AND ORNAMENTS')
