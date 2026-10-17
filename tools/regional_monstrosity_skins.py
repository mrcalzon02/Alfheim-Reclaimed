"""Authored UV skins for three regional native rigs; three restrained color variations each."""
import io
from PIL import Image,ImageDraw

REGIONS={'zombie':1,'pillager':16,'enderman':20}
PALETTES={
 'zombie':[(74,70,65),(91,74,63),(61,65,68)],
 'pillager':[(161,181,187),(145,166,185),(181,191,182)],
 'enderman':[(39,37,55),(47,38,59),(31,43,56)],
}

def skin(species,style):
    color=PALETTES[species][style]
    def shade(f):return tuple(min(255,round(c*f)) for c in color)+(255,)
    im=Image.new('RGBA',(64,64),shade(1));d=ImageDraw.Draw(im)
    for x,y,w,h in [(0,0,32,20),(0,24,32,18),(40,24,16,19),(0,44,16,18),(32,0,24,12),(48,48,8,8)]:
        d.rectangle((x,y,x+w-1,y+h-1),fill=shade(1))
        d.line((x,y,x+w-1,y),fill=shade(1.24))
        d.line((x,y+h-1,x+w-1,y+h-1),fill=shade(.65))
        for k in range(3,w,7):d.line((x+k,y+2,x+k,y+min(5,h-2)),fill=shade(.82))
    if species=='zombie':
        # Charcoal face: hollow sockets and sparse ember fissures, rather than magma blocks.
        d.rectangle((6,6,12,13),fill=shade(1.15))
        d.rectangle((6,9,7,10),fill='#24272a');d.rectangle((11,9,12,10),fill='#24272a')
        d.point((7,10),fill='#e1a15e');d.point((11,10),fill='#e1a15e')
        d.line((9,6,9,8),fill='#bb8054');d.line((8,12,11,12),fill='#282a29')
        d.line((8,30,9,35),fill='#b47d50');d.line((45,30,45,33),fill='#9e7251')
    elif species=='pillager':
        d.rectangle((6,6,11,15),fill=shade(1.13))
        d.rectangle((6,9,7,9),fill='#465b64');d.rectangle((10,9,11,9),fill='#465b64')
        d.point((7,9),fill='#d3e4df');d.point((10,9),fill='#d3e4df')
        d.line((6,7,11,7),fill=shade(.8));d.line((8,14,10,14),fill=shade(.6))
        # Worn coat panel and pale seam lines are painted into the body UVs.
        d.rectangle((5,29,11,40),fill='#516b78');d.line((8,29,8,40),fill='#9eb4b8')
        d.line((43,29,43,39),fill='#69808b')
    else:
        # Retain vanilla 8x8 head UV layout so the native eye-glow layer still aligns.
        d.rectangle((8,8,15,15),fill=shade(1.2))
        d.line((8,12,10,12),fill='#b6abd8');d.line((13,12,15,12),fill='#b6abd8')
        d.line((11,8,11,10),fill='#7f789d');d.line((12,14,12,15),fill='#716c91')
        d.line((3,29,3,37),fill='#6e6789');d.line((45,30,45,41),fill='#575471')
    stream=io.BytesIO();im.save(stream,format='PNG');return stream.getvalue()

def verge_eyes():
    im=Image.new('RGBA',(64,64),(0,0,0,0));d=ImageDraw.Draw(im)
    d.line((8,12,10,12),fill='#b6abd8');d.line((13,12,15,12),fill='#b6abd8')
    stream=io.BytesIO();im.save(stream,format='PNG');return stream.getvalue()
