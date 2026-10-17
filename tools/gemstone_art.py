"""Compile tintable inventory sprites from the generated 32-form gemstone master atlas.

The source image remains unmodified. Cropping/resizing prepares game sprites;
colour is applied by Minecraft's item renderer, preserving the master shading.
"""
import hashlib
from functools import lru_cache
from PIL import Image
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'tools/art/gemstone_masters.png'

@lru_cache(maxsize=1)
def atlas_image():return Image.open(ATLAS).convert('RGBA')

def form(g):
    key=g['id'];habit=g['habit'];n=int(hashlib.sha256(key.encode()).hexdigest()[:8],16)
    if key in ('star_ruby','star_sapphire','star_quartz'):return 19
    if key in ('tiger_eye','hawk_eye','chrysoberyl_catseye','phenomenal_quartz','sphene_catseye'):return 18
    if key in ('moss_agate','dendritic_agate','bloodstone','dalmatian_stone'):return 17 if n%2 else 31
    if key in ('labradorite','spectrolite','rainbow_moonstone','sunstone'):return 21
    if key in ('jadeite','nephrite','maw_sit_sit'):return 22
    if key in ('moonstone','orthoclase','sanidine','chrysoberyl'):return 23
    if key=='mother_of_pearl':return 26
    if habit=='pearl':return 23
    if habit=='coral':return 27
    if habit=='amber':return 25
    if key=='ammolite':return 24
    if habit=='fossil':return 28 if n%2 else 31
    if habit=='banded':return 16 if n%3 else 31
    if habit=='opal':return 20
    if habit=='metallic':return 29
    if habit=='cabochon':return (22,21,31)[n%3]
    if habit=='crystal':
        if g['pool']=='tourmaline':return 10
        if key in ('selenite','scolecite','natrolite','gypsum'):return 30
        return (8,9,11,14,15)[n%5]
    if g['pool']=='garnet':return 13
    if g['pool']=='spinel':return 12
    return n%8

def master(g,size=128):
    atlas=atlas_image();w,h=atlas.width//8,atlas.height//4;i=form(g)
    crop=atlas.crop(((i%8)*w,(i//8)*h,(i%8+1)*w,(i//8+1)*h));bounds=crop.getbbox()
    assert bounds is not None
    crop=crop.crop(bounds);crop.thumbnail((size-16,size-16),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(size,size));canvas.alpha_composite(crop,((size-crop.width)//2,(size-crop.height)//2));return canvas

def accent_color(g):
    if g['id']=='ametrine':return 'e6bd65'
    if g['id']=='watermelon_tourmaline':return '67b983'
    if g['id']=='bicolor_tourmaline':return 'c786b7'
    if g['id'] in ('bloodstone','ruby_in_zoisite'):return 'd35675'
    if g['id']=='dalmatian_stone':return '474038'
    if g['habit']=='opal':return '74e0cc'
    return g['color']

def accent(g,size=128):
    """Neutral second material mask; native rendering supplies the accent colour."""
    im=master(g,size);pixels=im.load();key=g['id'];seed=int(hashlib.sha256(key.encode()).hexdigest()[:8],16)
    for y in range(size):
        for x in range(size):
            selected=(key in ('ametrine','bicolor_tourmaline') and x>=size//2) or (key=='watermelon_tourmaline' and (abs(x-size/2)>size*.12 or y<size*.2 or y>size*.78))
            if key in ('bloodstone','ruby_in_zoisite','dalmatian_stone') or g['habit']=='opal':selected=((x//3*71+y//3*37+seed)%31)<(4 if g['habit']=='opal' else 2)
            if not selected:pixels[x,y]=(0,0,0,0)
    return im

def rendered(g,size=128):
    """Offline equivalent of the native item-colour shader, for review only."""
    import numpy as np
    im=master(g,size);pixels=np.array(im).astype(float);tint=np.array(list(bytes.fromhex(g['color'])))/255
    pixels[:,:,:3]*=tint
    base=Image.fromarray(pixels.clip(0,255).astype('uint8'))
    if accent_color(g)!=g['color']:
        layer=np.array(accent(g,size)).astype(float);layer[:,:,:3]*=np.array(list(bytes.fromhex(accent_color(g))))/255
        base.alpha_composite(Image.fromarray(layer.clip(0,255).astype('uint8')))
    return base
