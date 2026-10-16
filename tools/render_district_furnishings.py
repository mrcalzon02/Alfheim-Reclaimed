"""Offline geometry contact sheet from the actual emitted models, not a game screenshot."""
import json
from PIL import Image,ImageDraw,ImageFont
from gen_district_furnishings import ROOT,RES

def main():
    m=json.loads((ROOT/'tools/district_furnishings_manifest.json').read_text())
    colors={'wood':(159,135,91),'log':(117,102,77),'gold':(211,175,77),'gem':(153,120,193),'quartz':(212,208,188),'paper':(206,194,151),'green':(92,126,87),'dark':(68,68,79)}
    im=Image.new('RGB',(1400,1030),(19,23,30));d=ImageDraw.Draw(im)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',24);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
    d.text((24,15),'ALFHEIM DISTRICT FURNISHINGS / WORK, STORAGE AND REPAIR',font=title,fill='white')
    for i,(key,e) in enumerate(m['objects'].items()):
        cx=175+(i%4)*350;cy=165+(i//4)*300
        model=json.loads((RES/f'assets/alfheim_leyworks/models/block/{key}.json').read_text());faces=[]
        def p(x,y,z):return cx+(x+z-16)*6.2,cy+(x+16-z)*3.1-y*6.2
        for elem in model['elements']:
            x,y,z=elem['from'];X,Y,Z=elem['to']
            points={'up':[(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],'north':[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z)],'east':[(X,y,z),(X,y,Z),(X,Y,Z),(X,Y,z)]}
            for f,poly in points.items():
                if f not in elem['faces']:continue
                c=colors.get(elem['faces'][f]['texture'].lstrip('#'),(145,147,155));shade={'up':1.12,'north':.8,'east':.64}[f]
                depth=sum(a+16-c+b*.05 for a,b,c in poly)/4
                faces.append((depth,[p(*v) for v in poly],tuple(min(255,int(v*shade)) for v in c)))
        for _,poly,color in sorted(faces,key=lambda f:f[0]):d.polygon(poly,fill=color)
        d.text((cx-155,cy+115),e['title'],font=small,fill='#e2e8ed')
        label=f"{e['utility']} persistent slots" if isinstance(e['utility'],int) else e['utility'].title()+' workstation'
        d.text((cx-155,cy+140),label,font=small,fill='#9eafbe')
    d.text((24,1000),'Geometry diagram from emitted model faces; client textures, lighting and interfaces require visual play review.',font=small,fill='#9eafbe')
    im.save(ROOT/'tools/district_furnishings_review.png')

if __name__=='__main__':main()
