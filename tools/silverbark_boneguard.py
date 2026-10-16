"""Authored 64px UV skin for the native elven Boneguard model. No sampled block materials."""
import io
from PIL import Image,ImageDraw

def skin():
    image=Image.new('RGBA',(64,64),'#c8c7b4');d=ImageDraw.Draw(image)
    bone='#d9d8c4';shadow='#979e8a';dark='#353f3b';moss='#73866b';light='#f0edda'
    # All regions have intentional pixel-scale shading; unused texels stay neutral.
    for x,y,w,h in [(0,0,24,15),(32,0,6,5),(0,16,8,14),(40,16,8,15),(0,32,18,4),(16,32,16,5)]:
        d.rectangle((x,y,x+w-1,y+h-1),fill=bone)
        d.line((x,y+h-1,x+w-1,y+h-1),fill=shadow)
        d.line((x,y,x+w-1,y),fill=light)
        for step in range(3,w,6):d.line((x+step,y+2,x+step,y+min(h-2,4)),fill=shadow)
    # Front skull face at UV 6,6: deep sockets, small cool eyes and a restrained jaw.
    d.rectangle((6,6,11,14),fill=bone)
    d.line((6,6,11,6),fill=light);d.line((6,7,6,13),fill=shadow)
    d.rectangle((6,9,7,10),fill=dark);d.rectangle((10,9,11,10),fill=dark)
    d.point((7,10),fill='#a1d3c7');d.point((10,10),fill='#a1d3c7')
    d.line((8,12,9,12),fill=dark);d.line((7,14,10,14),fill=shadow)
    d.line((9,6,9,7),fill=shadow);d.point((10,8),fill=shadow)
    # Moss at the temples and joint recesses; no ornamental hats or floating detail.
    d.rectangle((18,7,19,10),fill=moss);d.line((1,8,2,11),fill=moss)
    d.rectangle((24,16,31,29),fill='#697b66');d.line((27,18,27,27),fill=shadow)
    d.line((2,23,3,25),fill=moss);d.line((43,23,44,25),fill=moss)
    stream=io.BytesIO();image.save(stream,format='PNG');return stream.getvalue()
