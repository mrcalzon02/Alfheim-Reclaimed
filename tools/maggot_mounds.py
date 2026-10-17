"""Detailed native block-model nest covers: sludge, egg sacs, and curled segmented maggots."""
import io,json,math
from PIL import Image,ImageDraw
BASE='assets/alfheim_companion/'
def build_mounds():
    out={}
    def js(p,v):out[p]=(json.dumps(v,indent=2)+'\n').encode()
    for variant,base in enumerate(((191,177,137),(153,120,105),(180,187,162))):
        im=Image.new('RGBA',(32,32));pix=im.load()
        for y in range(32):
            for x in range(32):
                fold=.78+.21*math.cos(y*.65)+.08*math.sin(x*.25)
                pix[x,y]=tuple(max(0,min(255,round(c*fold))) for c in base)+(255,)
        d=ImageDraw.Draw(im)
        for y in range(2,32,5):d.line((1,y,30,y),fill=tuple(int(c*.55) for c in base)+(255,));d.line((1,y-1,30,y-1),fill=tuple(min(255,int(c*1.1)) for c in base)+(255,))
        stream=io.BytesIO();im.save(stream,format='PNG');out[BASE+f'textures/block/maggot_skin_{variant}.png']=stream.getvalue()
        mouth=Image.new('RGBA',(16,16),(80,43,42,255));md=ImageDraw.Draw(mouth);md.ellipse((1,1,14,14),fill=base+(255,));md.ellipse((4,3,12,13),fill=(36,22,29,255));md.line((5,5,7,7),fill=(220,203,163,255));md.line((11,6,9,8),fill=(220,203,163,255))
        stream=io.BytesIO();mouth.save(stream,format='PNG');out[BASE+f'textures/block/maggot_mouth_{variant}.png']=stream.getvalue()
        elems=[]
        def box(lo,hi,tex,rotation=None):
            e={'from':lo,'to':hi,'faces':{side:{'texture':'#'+tex,'uv':[0,0,16,16]} for side in ['north','south','east','west','up','down']}}
            if rotation:e['rotation']=rotation
            elems.append(e)
        box([0,0,0],[16,3,16],'sludge');box([1,2,1],[15,6,15],'flesh');box([3,5,3],[13,8,13],'flesh')
        for i,(x,z) in enumerate(((2,3),(9,2),(4,7),(9,7),(6,5))):
            y=6+(i%2);rot={'origin':[x+1.5,y,z+1.5],'axis':'y','angle':22.5 if i%2 else -22.5}
            box([x,y,z],[x+3,y+3,z+3],'skin',rot);box([x+.5,y+1,z+2],[x+3.5,y+4,z+5],'skin',rot);box([x+1,y+1,z+4],[x+4,y+4,z+7],'skin',rot)
            box([x+1,y+1.5,z+6.7],[x+4,y+3.6,z+7.1],'mouth',rot)
        for x,z in ((2,12),(12,2),(12,12)):box([x,3,z],[x+2.5,7,z+2.5],'skin')
        js(BASE+f'models/block/maggot_mound_{variant}.json',{'parent':'minecraft:block/block','textures':{'particle':f'alfheim_companion:block/maggot_skin_{variant}','skin':f'alfheim_companion:block/maggot_skin_{variant}','mouth':f'alfheim_companion:block/maggot_mouth_{variant}','sludge':'alfheim:block/bio_sludge_coagulated','flesh':'alfheim:block/titan_flesh_putrescent'},'elements':elems})
    js(BASE+'blockstates/maggot_mound.json',{'variants':{f'decay={v}':[{'model':f'alfheim_companion:block/maggot_mound_{v}','y':a} for a in (0,90,180,270)] for v in range(3)}})
    js(BASE+'models/item/maggot_mound.json',{'parent':'alfheim_companion:block/maggot_mound_0'})
    js('data/alfheim_companion/loot_tables/blocks/maggot_mound.json',{'type':'minecraft:block','pools':[{'rolls':1,'conditions':[{'condition':'minecraft:survives_explosion'}],'entries':[{'type':'minecraft:item','name':'minecraft:rotten_flesh'}]}]})
    return out
