"""Rasterize the complete SVG to one PNG using installed librsvg/Cairo.

Streams 256-row stripes into PNG, keeping memory bounded for the poster-sized image.
No game files are changed and no extra Python packages are required.
"""
import argparse
import ctypes as c
import json
import math
import os
from pathlib import Path
import struct
import zlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/recipe-tree'
DLL=Path(r'C:\Program Files\GIMP 3\bin')
os.add_dll_directory(str(DLL))
cairo=c.CDLL(str(DLL/'libcairo-2.dll'))
rsvg=c.CDLL(str(DLL/'librsvg-2-2.dll'))
def bind(lib,name,args,ret):
    fn=getattr(lib,name);fn.argtypes=args;fn.restype=ret;return fn
ptr=c.c_void_p;double=c.c_double;integer=c.c_int
new=bind(rsvg,'rsvg_handle_new_from_file',[c.c_char_p,ptr],ptr)
render=bind(rsvg,'rsvg_handle_render_cairo',[ptr,ptr],integer)
record=bind(cairo,'cairo_recording_surface_create',[integer,ptr],ptr)
create=bind(cairo,'cairo_create',[ptr],ptr)
image=bind(cairo,'cairo_image_surface_create',[integer,integer,integer],ptr)
scale=bind(cairo,'cairo_scale',[ptr,double,double],None)
translate=bind(cairo,'cairo_translate',[ptr,double,double],None)
source=bind(cairo,'cairo_set_source_surface',[ptr,ptr,double,double],None)
paint=bind(cairo,'cairo_paint',[ptr],None)
flush=bind(cairo,'cairo_surface_flush',[ptr],None)
data=bind(cairo,'cairo_image_surface_get_data',[ptr],ptr)
stride=bind(cairo,'cairo_image_surface_get_stride',[ptr],integer)
destroy=bind(cairo,'cairo_destroy',[ptr],None)
destroy_surface=bind(cairo,'cairo_surface_destroy',[ptr],None)
status=bind(cairo,'cairo_surface_status',[ptr],integer)
write_png=bind(cairo,'cairo_surface_write_to_png',[ptr,c.c_char_p],integer)

def chunk(f,kind,payload):
    f.write(struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--width',type=int,default=24000);ap.add_argument('--name',default='alfheim-recipe-tech-tree.png');ap.add_argument('--crop',nargs=4,type=float)
    a=ap.parse_args();coverage=json.loads((OUT/'coverage.json').read_text())
    x,y,w,h=a.crop or (0,0,coverage['svg_width'],coverage['svg_height'])
    factor=a.width/w;W=a.width;H=math.ceil(h*factor)
    handle=new(str(OUT/'alfheim-recipe-tech-tree.svg').encode('utf-8'),None)
    assert handle,'SVG parse failed'
    target=OUT/a.name
    if W*H*4 < 2_000_000_000:
        print(f'Rendering {W} x {H} pixels',flush=True)
        surface=image(0,W,H);assert status(surface)==0,'Cairo allocation failed'
        ctx=create(surface);translate(ctx,-x*factor,-y*factor);scale(ctx,factor,factor)
        assert render(handle,ctx),'SVG render failed'
        print('Writing PNG',flush=True)
        assert write_png(surface,str(target).encode('utf-8'))==0,'PNG write failed'
        destroy(ctx);destroy_surface(surface)
        print(f'Rendered {target.name}: {W} x {H}, {target.stat().st_size:,} bytes',flush=True)
        return
    compressor=zlib.compressobj(6)
    with target.open('wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n');chunk(f,b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))
        for top in range(0,H,256):
            rows=min(256,H-top)
            tile=image(0,W,rows);assert status(tile)==0,'Cairo allocation failed'
            ctx=create(tile);translate(ctx,-x*factor,-y*factor-top);scale(ctx,factor,factor);assert render(handle,ctx);flush(tile)
            raw=c.string_at(data(tile),stride(tile)*rows)
            for row in range(rows):
                pixels=raw[row*stride(tile):row*stride(tile)+W*4]
                rgb=bytearray(W*3);rgb[0::3]=pixels[2::4];rgb[1::3]=pixels[1::4];rgb[2::3]=pixels[0::4]
                encoded=compressor.compress(b'\0'+rgb)
                if encoded:chunk(f,b'IDAT',encoded)
            destroy(ctx);destroy_surface(tile)
            if top%2560==0:print(f'{top}/{H} rows',flush=True)
        chunk(f,b'IDAT',compressor.flush());chunk(f,b'IEND',b'')
    print(f'Rendered {target.name}: {W} x {H}, {target.stat().st_size:,} bytes',flush=True)

if __name__=='__main__':main()
