"""Authored moss/peat arthropod UV skin, 64x32, for the four-segment native rig."""
import io
from PIL import Image,ImageDraw

def skin():
    image=Image.new('RGBA',(64,32),'#46584b');d=ImageDraw.Draw(image)
    for x,y,w,h in [(0,0,16,6),(0,8,20,8),(24,8,14,6),(24,16,8,4)]:
        d.rectangle((x,y,x+w-1,y+h-1),fill='#667a5d')
        d.line((x,y,x+w-1,y),fill='#9ba783')
        d.line((x,y+h-1,x+w-1,y+h-1),fill='#33483f')
        d.line((x+w//2,y+1,x+w//2,y+h-2),fill='#53684f')
    # Five-wide front face: tiny amber eyes separated by a dark central mouth.
    d.rectangle((3,3,7,5),fill='#5c7055')
    d.point((3,4),fill='#e4c17a');d.point((7,4),fill='#e4c17a')
    d.line((4,5,6,5),fill='#263b34')
    d.rectangle((40,0,47,3),fill='#b4aa86')
    d.line((40,3,47,3),fill='#756f54')
    d.rectangle((40,8,47,10),fill='#384a3e')
    d.line((40,8,47,8),fill='#7d8b68')
    out=io.BytesIO();image.save(out,format='PNG');return out.getvalue()
