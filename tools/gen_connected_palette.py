"""Generate 47-state connected texture palettes for all Deep + Void stones.

The 47 states are the complete valid cardinal/diagonal adjacency space used by classic CTM:
cardinal connections N/E/S/W plus only those diagonal corners whose two adjacent cardinals exist.
The authored, renderer-neutral tiles remain under textures/block/connected. A second, remapped copy
and one rule per family are emitted under optifine/ctm for the installed Continuity renderer.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import io
import json
import random
from PIL import Image, ImageDraw, ImageFont

from material_texture import OUTPUT_SIZE, VARIANT_COUNT, render_texture
from gen_deepworks import ROOT, png

OUT_ROOT='kubejs/assets/alfheim/textures/block/connected'
CONTINUITY_ROOT='kubejs/assets/alfheim/optifine/ctm/alfheim'
CATALOG='tools/connected_palette_catalog.json'
REVIEW='tools/connected_palette_review.png'

DIRS=('n','e','s','w')
CORNERS=(('ne','n','e'),('se','s','e'),('sw','s','w'),('nw','n','w'))

# Source states are generated in compact cardinal-mask/corner-mask order. Continuity's classic
# CTM processor expects OptiFine's historical 0..46 tile order, which is not that same order.
# This permutation was verified against SPRITE_INDEX_MAP in the installed Continuity 3.0.0 jar.
SOURCE_TO_CONTINUITY=(
    0,3,12,5,15,1,2,4,13,7,29,31,14,36,17,39,24,19,43,41,27,16,37,18,
    40,42,38,6,28,30,25,46,21,9,22,8,34,23,45,20,10,35,44,11,32,33,26,
)
assert sorted(SOURCE_TO_CONTINUITY)==list(range(47))


def states47():
    states=[]
    for cards in range(16):
        c={d:bool(cards&(1<<i)) for i,d in enumerate(DIRS)}
        allowed=[name for name,a,b in CORNERS if c[a] and c[b]]
        for corner_mask in range(1<<len(allowed)):
            row=dict(c)
            for name,_,_ in CORNERS:
                row[name]=name in allowed and bool(corner_mask&(1<<allowed.index(name)))
            states.append(row)
    assert len(states)==47
    return states


def _rgb(value):
    return tuple(bytes.fromhex(value)) if isinstance(value,str) else tuple(value[:3])


def _mix(a,b,t):
    return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))


def _seed(text):
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8],'big')


def _edge_line(im,side,dark,light,rng):
    """Irregular exposed geological edge, never a continuous UI-like frame."""
    px=im.load(); S=OUTPUT_SIZE
    def blend_at(x,y,target,t):
        r,g,b,a=px[x,y]; px[x,y]=(_mix((r,g,b),target,t)+(255,))
    for t in range(S):
        # Edge depth wanders between 1-3 pixels in coherent short runs.
        depth=1 + (1 if ((t//3)+rng.randrange(3))%4==0 else 0) + (1 if ((t//7)+rng.randrange(5))%7==0 else 0)
        for d in range(depth):
            if side=='n': x,y=t,d
            elif side=='s': x,y=t,S-1-d
            elif side=='w': x,y=d,t
            else: x,y=S-1-d,t
            blend_at(x,y,dark,.20+.10*(depth-d))
        # Sparse mineral catch on the inner lip; discontinuous by design.
        if t%3!=1:
            d=min(S-1,depth)
            if side=='n': x,y=t,d
            elif side=='s': x,y=t,S-1-d
            elif side=='w': x,y=d,t
            else: x,y=S-1-d,t
            blend_at(x,y,light,.10)


def render_connected(spec,state,index,base_variants=None):
    # State chooses an authored base variant deterministically. CTM removes random seams while
    # still drawing from the same four geological compositions used by ordinary blocks.
    variant=(_seed(spec['id']+'|ctm|'+str(index)) % VARIANT_COUNT)
    if base_variants is None:
        base_variants=[render_texture(spec,'raw',v) for v in range(VARIANT_COUNT)]
    out=base_variants[variant].copy()
    base=_rgb(spec['color']); accent=_rgb(spec['accent'])
    dark=_mix(base,(3,5,8),.62); light=_mix(base,accent,.32)
    rng=random.Random(_seed(spec['id']+f'|ctm-edge|{index}'))
    draw=ImageDraw.Draw(out)

    # Missing cardinal neighbor = visible exposed block boundary. Connected edges stay clean,
    # allowing the geological texture to flow to the next tile without an artificial block line.
    for side in DIRS:
        if not state[side]:
            _edge_line(out,side,dark,light,rng)

    # If both cardinals connect but the diagonal does not, cut a small re-entrant corner notch.
    S=OUTPUT_SIZE-1
    corner_xy={'ne':(S-2,2),'se':(S-2,S-2),'sw':(2,S-2),'nw':(2,2)}
    px=out.load()
    for name,a,b in CORNERS:
        if state[a] and state[b] and not state[name]:
            cx,cy=corner_xy[name]
            # Re-entrant fractured corner: irregular wedge, not a circular marker.
            for dy in range(-3,4):
                for dx in range(-3,4):
                    man=abs(dx)+abs(dy)
                    if man>4 or rng.random()<.20: continue
                    x=max(0,min(S,cx+dx)); y=max(0,min(S,cy+dy))
                    c=px[x,y][:3]
                    px[x,y]=_mix(c,dark,.18+.05*(4-man))+(255,)
            c=px[cx,cy][:3]; px[cx,cy]=_mix(c,light,.12)+(255,)
    return out


def _font(size,bold=False):
    candidates=[
        Path('/usr/share/fonts/truetype/dejavu')/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'),
        Path('C:/Windows/Fonts')/('segoeuib.ttf' if bold else 'segoeui.ttf')]
    for p in candidates:
        if p.exists(): return ImageFont.truetype(str(p),size)
    return ImageFont.load_default()


def _families():
    deep=json.loads((ROOT/'tools/deepworks_manifest.json').read_text())['families']
    void=json.loads((ROOT/'alfheim_reclaimed_design/void/void_catalog.json').read_text())
    vf=[]
    for biome in void['biomes']:
        for stone in biome['stones']:
            f=dict(stone); f['id']=stone['id'].split(':',1)[1]; f['group']='Void / '+biome['name']; vf.append(f)
    return [dict(f) for f in deep]+vf


def build():
    states=states47(); families=_families(); out={}; catalog={'schema':2,'resolution':OUTPUT_SIZE,'states':[],'families':[]}
    for i,state in enumerate(states):
        catalog['states'].append({'index':i,**state})
    previews={}
    for f in families:
        stem=f['id']; paths=[]; images=[]
        base_variants=[render_texture(f,'raw',v) for v in range(VARIANT_COUNT)]
        for i,state in enumerate(states):
            image=render_connected(f,state,i,base_variants); images.append(image)
            rel=f'{OUT_ROOT}/{stem}/{i:02}.png'; out[rel]=png(image); paths.append(rel)
        continuity_paths=['']*len(states)
        for source_index,continuity_index in enumerate(SOURCE_TO_CONTINUITY):
            rel=f'{CONTINUITY_ROOT}/{stem}/{continuity_index}.png'
            out[rel]=png(images[source_index]); continuity_paths[continuity_index]=rel
        rule=f'{CONTINUITY_ROOT}/{stem}/{stem}.properties'
        out[rule]=(
            'method=ctm\n'
            f'matchBlocks=alfheim:{stem}\n'
            'tiles=0-46\n'
            'connect=block\n'
            f'resourceCondition=textures/block/{stem}.png\n'
        ).encode()
        previews[stem]=images
        catalog['families'].append({
            'id':'alfheim:'+stem,'name':f['name'],'group':f.get('group','Void'),
            'tiles':paths,
            'continuity':{'rule':rule,'tiles':continuity_paths},
        })
    out[CATALOG]=(json.dumps(catalog,indent=2)+'\n').encode()

    # Review six topology archetypes for every family.
    def find(**wanted):
        for i,s in enumerate(states):
            if all(s[k]==v for k,v in wanted.items()) and all((k in wanted) or not s[k] for k in s if k in ('ne','se','sw','nw')):
                return i
        raise KeyError(wanted)
    sample=[
        ('Isolated',0),
        ('E-W',next(i for i,s in enumerate(states) if s['e'] and s['w'] and not s['n'] and not s['s'])),
        ('N-S',next(i for i,s in enumerate(states) if s['n'] and s['s'] and not s['e'] and not s['w'])),
        ('Corner',next(i for i,s in enumerate(states) if s['n'] and s['e'] and not s['s'] and not s['w'] and not s['ne'])),
        ('Cross',next(i for i,s in enumerate(states) if all(s[d] for d in DIRS) and not any(s[c] for c,_,_ in CORNERS))),
        ('Filled',next(i for i,s in enumerate(states) if all(s.values()))),
    ]
    width=930; rowh=74; height=92+len(families)*rowh
    sheet=Image.new('RGB',(width,height),'#181e26'); d=ImageDraw.Draw(sheet); font=_font(13); bold=_font(22,True)
    d.text((18,14),'CONNECTED STONE PALETTE / 47-STATE CTM SOURCE',font=bold,fill='#f2e3c8')
    for col,(label,_) in enumerate(sample): d.text((260+col*108,58),label,font=font,fill='#cbd9da')
    for r,f in enumerate(families):
        y=86+r*rowh; stem=f['id']; d.text((18,y+18),f['name'],font=font,fill='#eee3d2')
        for col,(_,idx) in enumerate(sample):
            tile=previews[stem][idx].convert('RGB').resize((64,64),Image.Resampling.NEAREST)
            sheet.paste(tile,(260+col*108,y))
    out[REVIEW]=png(sheet)
    return out


def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
    out=build(); bad=[]
    for rel,data in out.items():
        p=ROOT/rel
        if args.check:
            if not p.exists() or p.read_bytes()!=data: bad.append(rel)
        else:
            p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
    if bad: raise SystemExit('Generated output mismatch:\n'+'\n'.join(bad))
    print(f'{len(out)} connected-palette files '+('verified' if args.check else 'generated'))

if __name__=='__main__': main()
