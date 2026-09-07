"""Deterministic 32px geological texture engine for Alfheim's Deep and Void stones.

Each family owns a geological grammar rather than inheriting Botania Livingrock.  A compact
16-unit composition guide controls the large geological silhouette; the final 32x32 synthesis
adds native micro-relief, directional shading, bevels and finish-specific surface response.
"""
from __future__ import annotations
import colorsys
import hashlib
import math
import random
from PIL import Image, ImageDraw

GUIDE_SIZE = 16
SIZE = GUIDE_SIZE
OUTPUT_SIZE = 32
VARIANT_COUNT = 4
ROTATIONS = (0, 90, 180, 270)
ENGINE_VERSION = 4

# Stable material grammars.  These are silhouette/structure choices, not palette names.
STYLE_BY_ID = {
    # Deep — Furnace
    "cracked_livingrock": "pressure_cracks",
    "magmatic_livingrock": "magma_plates",
    "embervein_livingrock": "ember_vein",
    "cinder_livingrock": "cinder_pores",
    "obsidian_livingrock": "obsidian_shards",
    # Deep — Court
    "moonstone_livingrock": "clouded_grain",
    "dawn_livingrock": "warm_bands",
    "rose_livingrock": "marble_veins",
    "ivory_livingrock": "fine_grain",
    "silvermist_livingrock": "mist_bands",
    # Deep — Grove
    "moss_livingrock": "moss_clusters",
    "rootbound_livingrock": "root_inclusions",
    "fern_livingrock": "fern_fossils",
    "amber_livingrock": "amber_lenses",
    "petrified_livingrock": "petrified_grain",
    # Deep — Water and sky
    "tide_livingrock": "wave_laminae",
    "abyssal_livingrock": "abyssal_dense",
    "frost_livingrock": "frost_facets",
    "gale_livingrock": "wind_laminae",
    "storm_livingrock": "storm_faults",
    # Deep — Ley
    "amethyst_livingrock": "crystal_facets",
    "leyline_livingrock": "ley_channels",
    "gloam_livingrock": "gloam_clouds",
    "starfleck_livingrock": "star_flecks",
    # Void Verge
    "riftchalk_livingrock": "chalk_granular",
    "riftshale_livingrock": "offset_laminae",
    "veilstone_livingrock": "veil_seams",
    # Shatterfields
    "shardbreccia_livingrock": "breccia",
    "anchorstone_livingrock": "pressure_folds",
    "seamstone_livingrock": "rejoined_fractures",
    # Prism Drift
    "prismstone_livingrock": "prism_boundaries",
    "aetherquartzite_livingrock": "quartz_grains",
    "glintschist_livingrock": "schist_flakes",
    # Rootfall
    "rootfossil_livingrock": "root_fossil",
    "resinshale_livingrock": "resin_laminae",
    "hollowheart_livingrock": "root_cavities",
    # Sepulchral Reach
    "epitaph_livingrock": "epitaph_marble",
    "mourning_livingrock": "mourning_slate",
    "oathstone_livingrock": "competent_stone",
    # Starless Reach
    "nightmantle_livingrock": "night_fractures",
    "nullstone_livingrock": "null_pores",
    "astralite_livingrock": "astral_flecks",
}

def _rgb(value):
    if isinstance(value, (tuple, list)):
        return tuple(value[:3])
    return tuple(bytes.fromhex(value))

def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(max(0, min(255, round(a[i] * (1-t) + b[i] * t))) for i in range(3))

def _mul(a, f):
    return tuple(max(0, min(255, round(c*f))) for c in a)

def _seed(text):
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")

def _noise(x, y, seed, octave=0):
    """Small periodic field: all frequencies are integer cycles across the composition guide, so it tiles."""
    r = random.Random(seed + octave * 0x9E3779B1)
    v = 0.0
    norm = 0.0
    for k, amp in ((1, 1.0), (2, .52), (3, .24), (5, .12)):
        p1 = r.random() * math.tau
        p2 = r.random() * math.tau
        v += amp * math.sin(math.tau * k * x / SIZE + p1) * math.cos(math.tau * (k+octave%2) * y / SIZE + p2)
        norm += amp
    return v / norm

def _base_field(spec, form):
    base, accent = _rgb(spec["color"]), _rgb(spec["accent"])
    seed = _seed(spec["id"] + "|" + form + f"|v{spec.get('_variant',0)}")
    im = Image.new("RGBA", (SIZE, SIZE))
    smooth = form == "polished"
    for y in range(SIZE):
        for x in range(SIZE):
            n = _noise(x, y, seed)
            # Quantize into a Minecraft-like hand-pixelled value ladder.
            steps = 5 if smooth else 7
            q = round((n + 1) * .5 * (steps-1)) / (steps-1)
            # Polished stone has narrower relief but does not lose its material fabric.
            span = .13 if smooth else .24
            factor = 1 - span/2 + q*span
            c = _mul(base, factor)
            im.putpixel((x, y), c + (255,))
    return im

def _draw_wrapped_line(im, pts, color, width=1):
    """Draw a line in a 3×3 tiled canvas then crop center, making edge crossings seamless."""
    big = Image.new("RGBA", (SIZE*3, SIZE*3))
    draw = ImageDraw.Draw(big)
    for ox in (0, SIZE, SIZE*2):
        for oy in (0, SIZE, SIZE*2):
            draw.line([(x+ox, y+oy) for x,y in pts], fill=color+(255,), width=width)
    patch = big.crop((SIZE, SIZE, SIZE*2, SIZE*2))
    im.alpha_composite(patch)

def _scatter(im, rng, color, count, radius=0):
    px = im.load()
    for _ in range(count):
        cx, cy = rng.randrange(SIZE), rng.randrange(SIZE)
        if radius <= 0:
            px[cx, cy] = color + (255,)
        else:
            for dy in range(-radius, radius+1):
                for dx in range(-radius, radius+1):
                    if dx*dx+dy*dy <= radius*radius + (radius == 1):
                        px[(cx+dx)%SIZE, (cy+dy)%SIZE] = color + (255,)

def _material_overlay(im, spec, form):
    style = STYLE_BY_ID.get(spec["id"], "fine_grain")
    base, accent = _rgb(spec["color"]), _rgb(spec["accent"])
    dark = _mix(base, (8, 10, 14), .48)
    light = _mix(accent, (245, 247, 242), .18)
    rng = random.Random(_seed(spec["id"] + f"|geology|v{spec.get('_variant',0)}"))
    draw = ImageDraw.Draw(im)
    smooth = form == "polished"
    strength = .72 if smooth else 1.0
    a = _mix(base, accent, .74 * strength)
    d = _mix(base, dark, .72 * strength)

    # helpers
    def wandering(x0, slant=0, jitter=(-1,0,0,1), branch=False, col=None, width=1):
        x = x0
        pts=[]
        for y in range(-2, 19):
            x = (x + slant + rng.choice(jitter)) % SIZE
            pts.append((x, y))
        _draw_wrapped_line(im, pts, col or a, width)
        if branch:
            for by in (3, 9, 14):
                bx = pts[by+2][0]
                direction = rng.choice((-1,1))
                _draw_wrapped_line(im, [(bx,by),(bx+direction*2,by+2),(bx+direction*4,by+3)], col or a, width)

    if style == "pressure_cracks":
        wandering(rng.randrange(SIZE), branch=True, col=d)
        wandering((rng.randrange(SIZE)+8)%SIZE, branch=True, col=a)
    elif style == "magma_plates":
        # Broad cooled plates with sparse hot interior seams.
        for x0 in (2, 10):
            wandering(x0, branch=True, col=dark, width=2)
            wandering(x0, branch=True, col=accent, width=1)
        _scatter(im, rng, _mix(base, dark, .65), 9)
    elif style == "ember_vein":
        wandering(4, slant=0, branch=True, col=accent)
        wandering(12, slant=0, branch=False, col=_mix(base, accent, .45))
    elif style == "cinder_pores":
        _scatter(im, rng, dark, 18 if not smooth else 10)
        _scatter(im, rng, _mix(base, accent, .50), 7)
    elif style == "obsidian_shards":
        for pts in ([(0,5),(5,1),(10,4),(16,0)],[(1,14),(6,9),(11,12),(15,7)],[(3,0),(1,6),(4,11),(2,16)]):
            _draw_wrapped_line(im, pts, d)
        _draw_wrapped_line(im, [(0,6),(5,2),(10,5),(16,1)], light)
    elif style == "clouded_grain":
        _scatter(im, rng, light, 12 if not smooth else 7)
        _scatter(im, rng, _mix(base, accent, .4), 22 if not smooth else 12)
    elif style in ("warm_bands","mist_bands","wave_laminae"):
        phase = rng.random()*math.tau
        for band in (2,7,12):
            pts=[(x,(band+round(math.sin(x*.55+phase)*1.4))%SIZE) for x in range(17)]
            _draw_wrapped_line(im, pts, a if band != 7 else d)
    elif style in ("marble_veins","epitaph_marble"):
        wandering(3, branch=True, col=d)
        wandering(11, branch=False, col=_mix(base, accent, .55))
    elif style == "fine_grain":
        _scatter(im, rng, _mix(base, accent, .45), 24 if not smooth else 12)
        _scatter(im, rng, _mix(base, dark, .45), 14 if not smooth else 6)
    elif style == "moss_clusters":
        moss = _mix(accent, (68,96,54), .35)
        for _ in range(8 if not smooth else 5):
            cx,cy=rng.randrange(SIZE),rng.randrange(SIZE)
            for dx,dy in ((0,0),(1,0),(0,1),(-1,0),(1,1)):
                if rng.random()<.78: im.putpixel(((cx+dx)%SIZE,(cy+dy)%SIZE),moss+(255,))
    elif style in ("root_inclusions","root_fossil"):
        wandering(5, branch=True, col=d)
        wandering(13, branch=True, col=a)
        if style == "root_fossil":
            # small mineralised ring cross-section
            for r in (2,4):
                for deg in range(0,360,20):
                    x=(8+round(math.cos(math.radians(deg))*r))%SIZE
                    y=(8+round(math.sin(math.radians(deg))*r))%SIZE
                    im.putpixel((x,y),a+(255,))
    elif style == "fern_fossils":
        for x0,y0,sgn in ((4,2,1),(12,10,-1)):
            _draw_wrapped_line(im, [(x0,y0),(x0+sgn*2,y0+6)], d)
            for j in range(1,6):
                x=x0+round(sgn*2*j/6); y=y0+j
                _draw_wrapped_line(im, [(x,y),(x+sgn*(1+j%2),y-1)], a)
    elif style in ("amber_lenses","resin_laminae"):
        # host lamination plus elliptical inclusions
        for y in (3,8,13):
            _draw_wrapped_line(im, [(0,y),(5,y+1),(11,y),(16,y+1)], d)
        for _ in range(4):
            cx,cy=rng.randrange(SIZE),rng.randrange(SIZE)
            for dx,dy in ((-1,0),(0,0),(1,0),(0,1)):
                im.putpixel(((cx+dx)%SIZE,(cy+dy)%SIZE),accent+(255,))
    elif style == "petrified_grain":
        for x in (2,6,11,15):
            pts=[(x+round(math.sin(y*.7+x)*1.2),y) for y in range(17)]
            _draw_wrapped_line(im, pts, a if x%2 else d)
        for r in (2,5):
            for deg in range(0,360,30):
                im.putpixel(((8+round(math.cos(math.radians(deg))*r))%SIZE,(8+round(math.sin(math.radians(deg))*r))%SIZE),a+(255,))
    elif style == "abyssal_dense":
        _scatter(im, rng, d, 25 if not smooth else 12)
        wandering(9, branch=False, col=_mix(base, accent, .35))
    elif style == "frost_facets":
        for pts in ([(0,4),(4,0),(8,4),(4,8),(0,4)],[(9,16),(13,11),(16,14)],[(8,4),(12,8),(8,12),(4,8)]):
            _draw_wrapped_line(im, pts, a)
        _scatter(im, rng, light, 8)
    elif style == "wind_laminae":
        for y in (2,6,11,15):
            _draw_wrapped_line(im, [(-2,y+3),(5,y),(12,y-2),(18,y-4)], a if y%3 else d)
    elif style == "storm_faults":
        _draw_wrapped_line(im,[(-1,2),(3,5),(1,8),(7,10),(5,14),(10,17)],a)
        _draw_wrapped_line(im,[(8,-1),(11,3),(9,7),(15,11),(13,16)],d)
    elif style in ("crystal_facets","prism_boundaries","quartz_grains"):
        cells=[[(0,0),(5,1),(7,6),(2,8),(0,0)],[(5,1),(12,0),(14,5),(7,6),(5,1)],[(2,8),(7,6),(12,10),(9,16)],[(14,5),(16,8),(12,10),(7,6)]]
        for i,pts in enumerate(cells):
            _draw_wrapped_line(im,pts,a if i%2 else d)
        if style=="crystal_facets": _scatter(im,rng,light,7)
        if style=="quartz_grains": _scatter(im,rng,_mix(base,accent,.35),16)
    elif style in ("ley_channels","veil_seams","rejoined_fractures"):
        wandering(6, branch=True, col=accent)
        wandering(13, branch=False, col=d)
        if style=="rejoined_fractures":
            # dark shoulders around the healed line
            wandering(5, branch=True, col=dark)
    elif style == "gloam_clouds":
        for _ in range(5):
            cx,cy=rng.randrange(SIZE),rng.randrange(SIZE)
            for dy in range(-2,3):
                for dx in range(-2,3):
                    if dx*dx+dy*dy<6 and rng.random()<.75:
                        im.putpixel(((cx+dx)%SIZE,(cy+dy)%SIZE),_mix(base,d,.65)+(255,))
    elif style in ("star_flecks","astral_flecks"):
        _scatter(im,rng,light,13 if style=="star_flecks" else 8)
        for _ in range(2):
            x,y=rng.randrange(SIZE),rng.randrange(SIZE)
            for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
                im.putpixel(((x+dx)%SIZE,(y+dy)%SIZE),accent+(255,))
    elif style == "chalk_granular":
        _scatter(im,rng,_mix(base,dark,.38),38 if not smooth else 18)
        _scatter(im,rng,light,18 if not smooth else 9)
    elif style in ("offset_laminae","mourning_slate"):
        for i,y in enumerate((1,4,7,10,13)):
            shift = (i%2)*3
            _draw_wrapped_line(im,[(-2+shift,y),(5+shift,y+1),(10+shift,y),(18+shift,y+1)],d if i%2 else a)
    elif style == "breccia":
        polygons=[[(0,1),(4,0),(6,4),(3,7),(0,5)],[(7,0),(13,1),(15,5),(10,7),(6,4)],[(1,9),(5,7),(9,11),(6,16),(1,15)],[(10,8),(16,6),(16,14),(12,16),(8,12)]]
        for i,p in enumerate(polygons):
            draw.polygon(p, outline=(a if i%2 else d)+(255,))
            if not smooth and i%2==0: draw.line(p+[p[0]],fill=dark+(255,))
    elif style == "pressure_folds":
        for x in range(0,16,4):
            pts=[(x+round(math.sin(y*.55+x)*1.7),y) for y in range(17)]
            _draw_wrapped_line(im,pts,a if x%8 else d)
    elif style == "schist_flakes":
        for _ in range(28 if not smooth else 16):
            x,y=rng.randrange(SIZE),rng.randrange(SIZE)
            col=light if rng.random()<.25 else a
            _draw_wrapped_line(im,[(x-1,y),(x+2,y-1)],col)
    elif style == "root_cavities":
        _scatter(im,rng,d,10 if not smooth else 6,radius=1)
        wandering(4,branch=True,col=a)
    elif style == "competent_stone":
        # Intentionally restrained: Oathstone's interlace appears only in carved form.
        _scatter(im,rng,_mix(base,dark,.33),18 if not smooth else 8)
        _scatter(im,rng,_mix(base,accent,.30),10 if not smooth else 5)
    elif style == "night_fractures":
        _draw_wrapped_line(im,[(-1,5),(4,3),(8,6),(13,4),(17,7)],d,width=2)
        _draw_wrapped_line(im,[(3,-1),(5,4),(4,9),(7,13),(6,17)],a)
    elif style == "null_pores":
        _scatter(im,rng,d,22 if not smooth else 12)
        for _ in range(6):
            x,y=rng.randrange(SIZE),rng.randrange(SIZE)
            _draw_wrapped_line(im,[(x,y),(x+2,y),(x+3,y+1)],a)
    else:
        _scatter(im,rng,a,16)

def _finish_polished(im, spec):
    """Polish highlights broad planes; no blur, so pixel edges stay crisp."""
    px = im.load()
    base = _rgb(spec["color"])
    for y in range(SIZE):
        for x in range(SIZE):
            if (x + 2*y + _seed(spec["id"] + f"|polish|v{spec.get('_variant',0)}")//31) % 11 == 0:
                c=px[x,y][:3]
                px[x,y]=_mix(c,base,.22)+(255,)
    return im

def _brickify(material, spec):
    """Staggered elven ashlar; geology continues inside individual stones."""
    out=material.copy()
    draw=ImageDraw.Draw(out)
    base, accent=_rgb(spec["color"]),_rgb(spec["accent"])
    mortar=_mix(base,(6,8,10),.55)
    highlight=_mix(base,accent,.30)
    # 4px courses. Horizontal recess followed by a one-pixel upper highlight.
    for y in (0,4,8,12):
        draw.line((0,y,15,y),fill=mortar+(255,))
        if y+1<16: draw.line((0,y+1,15,y+1),fill=highlight+(255,))
    # 7/9px alternating blocks; no Livingrock 8x8 motif.
    for course,y0 in enumerate((0,4,8,12)):
        joints=(2,9) if course%2 else (6,13)
        for x in joints:
            draw.line((x,y0,x,min(15,y0+3)),fill=mortar+(255,))
            if x+1<16: draw.point((x+1,min(15,y0+2)),fill=highlight+(255,))
    return out

def _carve(material, spec):
    """Unified elven lens/interlace mark cut into the family's own polished stone."""
    out=material.copy()
    draw=ImageDraw.Draw(out)
    base,accent=_rgb(spec["color"]),_rgb(spec["accent"])
    shadow=_mix(base,(4,6,8),.60)
    edge=_mix(base,accent,.44)
    # border is broken at midpoints to avoid a generic square frame
    for a,b in [((2,2),(6,2)),((10,2),(13,2)),((13,2),(13,6)),((13,10),(13,13)),
                ((10,13),(13,13)),((2,13),(6,13)),((2,10),(2,13)),((2,2),(2,6))]:
        draw.line((a,b),fill=shadow+(255,))
    # central leaf/lens plus crossing interlace
    shadow_pts=[(8,2),(12,8),(8,14),(4,8),(8,2)]
    edge_pts=[(8,3),(11,8),(8,13),(5,8),(8,3)]
    draw.line(shadow_pts,fill=shadow+(255,))
    draw.line(edge_pts,fill=edge+(255,))
    draw.line((3,8,6,8),fill=shadow+(255,))
    draw.line((10,8,13,8),fill=shadow+(255,))
    draw.line((8,5,8,11),fill=edge+(255,))
    draw.point((7,8),fill=edge+(255,))
    draw.point((9,8),fill=edge+(255,))
    return out


def _periodic32(x, y, seed):
    """Native 32px periodic micro-height field. Frequencies tile exactly at the texture edge."""
    r = random.Random(seed)
    value = 0.0
    norm = 0.0
    for fx, fy, amp in ((1,2,.52),(2,3,.28),(5,4,.13),(7,9,.07)):
        p1, p2 = r.random()*math.tau, r.random()*math.tau
        value += amp * math.sin(math.tau*fx*x/OUTPUT_SIZE+p1) * math.cos(math.tau*fy*y/OUTPUT_SIZE+p2)
        norm += amp
    return value / norm


def _luma(c):
    return (c[0]*3 + c[1]*6 + c[2]) / 10.0


def _native32(guide, spec, form):
    """Turn the 16-unit geology composition into a genuine 32px material surface.

    This is not an image resize pass: the guide controls macro-material boundaries only.  The
    32px result receives an independent height field, upper-left lighting, edge bevel response,
    deterministic microchips/grain, and form-specific polish/ashlar treatment.
    """
    nearest = guide.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.NEAREST).convert('RGBA')
    src = nearest.load()
    base = _rgb(spec['color'])
    accent = _rgb(spec['accent'])
    seed = _seed(spec['id'] + '|native32|' + form + f"|v{spec.get('_variant',0)}")
    rng = random.Random(seed)

    # Build a periodic height map from macro value structure + native 32px relief.
    heights = [[0.0]*OUTPUT_SIZE for _ in range(OUTPUT_SIZE)]
    base_l = max(1.0, _luma(base))
    polished = form in ('polished','carved')
    for y in range(OUTPUT_SIZE):
        for x in range(OUTPUT_SIZE):
            c = src[x,y][:3]
            macro = (_luma(c) - base_l) / 92.0
            micro = _periodic32(x,y,seed)
            fine = _periodic32(x,y,seed ^ 0x6A09E667)
            heights[y][x] = macro*.78 + micro*(.15 if polished else .24) + fine*(.045 if polished else .08)

    out = Image.new('RGBA',(OUTPUT_SIZE,OUTPUT_SIZE))
    px = out.load()
    for y in range(OUTPUT_SIZE):
        for x in range(OUTPUT_SIZE):
            c = src[x,y][:3]
            h = heights[y][x]
            left = heights[y][(x-1)%OUTPUT_SIZE]
            right = heights[y][(x+1)%OUTPUT_SIZE]
            up = heights[(y-1)%OUTPUT_SIZE][x]
            down = heights[(y+1)%OUTPUT_SIZE][x]
            # Upper-left directional light. Raised NW-facing edges catch light; SE faces recede.
            slope = (left-right)*.62 + (up-down)*.78
            relief = slope*(.28 if polished else .40)
            broad = h*(.08 if polished else .13)
            factor = max(.72, min(1.24, 1.0 + relief + broad))

            # Strongly accented luminous seams should glow through their surface relief.
            dist_acc = sum(abs(c[i]-accent[i]) for i in range(3))
            if spec.get('light',0) and dist_acc < 70:
                factor = max(.94, factor)
            px[x,y] = _mul(c, factor) + (255,)

    # Micro-surface clusters: one-pixel information that did not exist in the 16-unit guide.
    # Keep this sparse and material-coloured rather than salt-and-pepper noise.
    draw = ImageDraw.Draw(out)
    hi = _mix(base, accent, .34)
    shadow = _mix(base,(5,7,9),.48)
    grain_count = 26 if polished else 58
    for _ in range(grain_count):
        x,y=rng.randrange(OUTPUT_SIZE),rng.randrange(OUTPUT_SIZE)
        if rng.random() < .58:
            draw.point((x,y), fill=_mix(out.getpixel((x,y))[:3],hi,.22)+(255,))
        else:
            draw.point((x,y), fill=_mix(out.getpixel((x,y))[:3],shadow,.20)+(255,))

    # Bevel abrupt macro boundaries with a one-pixel light/shadow pair.  This turns cracks,
    # pores, clasts and carved lines into recesses/raised lips rather than flat colour marks.
    src_l=[[ _luma(src[x,y][:3]) for x in range(OUTPUT_SIZE)] for y in range(OUTPUT_SIZE)]
    bevel=Image.new('RGBA',(OUTPUT_SIZE,OUTPUT_SIZE),(0,0,0,0))
    bd=ImageDraw.Draw(bevel)
    for y in range(OUTPUT_SIZE):
        for x in range(OUTPUT_SIZE):
            here=src_l[y][x]
            nw=(src_l[(y-1)%OUTPUT_SIZE][x]+src_l[y][(x-1)%OUTPUT_SIZE])*.5
            se=(src_l[(y+1)%OUTPUT_SIZE][x]+src_l[y][(x+1)%OUTPUT_SIZE])*.5
            delta=nw-se
            if abs(delta)>16:
                current=out.getpixel((x,y))[:3]
                if delta>0:
                    bd.point((x,y),fill=_mix(current,(255,255,250),.14)+(150,))
                else:
                    bd.point((x,y),fill=_mix(current,(4,5,7),.19)+(170,))
    out=Image.alpha_composite(out,bevel)

    if polished:
        # Restrained specular catches on broad planes; never a uniform plastic gloss.
        draw=ImageDraw.Draw(out)
        for y in range(2,OUTPUT_SIZE,7):
            offset=(seed//(y+11))%6
            for x in range(offset,OUTPUT_SIZE,11):
                if abs(heights[y][x]) < .22:
                    c=out.getpixel((x,y))[:3]
                    draw.line((x,y,min(OUTPUT_SIZE-1,x+2),y),fill=_mix(c,(250,252,248),.16)+(255,))

    if form == 'bricks':
        # Extra face-depth at native resolution: ashlar upper/left edges catch light and
        # lower/right interiors are fractionally darker, so courses no longer read as a grid.
        draw=ImageDraw.Draw(out)
        course=8
        mortar=_mix(base,(4,5,7),.62)
        lip=_mix(base,accent,.34)
        for y in range(0,OUTPUT_SIZE,course):
            draw.line((0,y,OUTPUT_SIZE-1,y),fill=mortar+(255,),width=2)
            if y+2<OUTPUT_SIZE: draw.line((0,y+2,OUTPUT_SIZE-1,y+2),fill=lip+(255,))
        for ci,y0 in enumerate(range(0,OUTPUT_SIZE,course)):
            joints=(12,26) if ci%2==0 else (4,18)
            for x in joints:
                draw.line((x,y0,x,min(OUTPUT_SIZE-1,y0+course-1)),fill=mortar+(255,),width=2)
                if x+2<OUTPUT_SIZE: draw.line((x+2,y0+1,x+2,min(OUTPUT_SIZE-1,y0+course-3)),fill=lip+(255,))

    return out

def render_texture(spec, form, variant=0):
    """Render one native 32x32 material tile variant.

    Variants keep the same geological grammar and palette while changing the macro seed,
    fracture/grain placement and native micro-relief. Shape blocks continue to reuse bricks.
    """
    if not 0 <= variant < VARIANT_COUNT:
        raise ValueError(f"variant {variant} outside 0..{VARIANT_COUNT-1}")
    if form in ("slab","stairs","wall"):
        form="bricks"
    if form not in ("raw","polished","bricks","carved"):
        raise ValueError(form)
    work=dict(spec)
    work['_variant']=variant
    geological_form = "polished" if form in ("polished","carved") else "raw"
    guide=_base_field(work, geological_form)
    _material_overlay(guide,work,geological_form)
    if form=="polished":
        guide=_finish_polished(guide,work)
    elif form=="bricks":
        guide=_brickify(guide,work)
    elif form=="carved":
        guide=_carve(_finish_polished(guide,work),work)
    return _native32(guide,work,form)

def render_slag(variant=0):
    if not 0 <= variant < VARIANT_COUNT:
        raise ValueError(variant)
    spec={"id":"livingrock_slag","color":"56525b","accent":"857b80","light":0,"_variant":variant}
    guide=_base_field(spec,"raw")
    rng=random.Random(_seed(f"livingrock_slag|geology|v{variant}"))
    base,accent=_rgb(spec["color"]),_rgb(spec["accent"])
    dark=_mix(base,(4,5,7),.62)
    _scatter(guide,rng,dark,24)
    _scatter(guide,rng,_mix(base,accent,.45),9,radius=1)
    draw=ImageDraw.Draw(guide)
    sockets=[((3+variant*2)%16,4),((12+variant)%16,10),((7+variant*3)%16,14)]
    for cx,cy in sockets:
        draw.ellipse((cx-1,cy-1,cx+1,cy+1),outline=dark+(255,))
    return _native32(guide,spec,"raw")

def _crystal_color(crystal):
    return tuple(int(c*255) for c in colorsys.hsv_to_rgb(
        crystal['hue']/360, min(.88, crystal['sat']*.55), min(1.0, crystal['val']*.88)))

def render_mana_glass(crystal, variant=0):
    """Transparent 32px vitrified mana-glass, with real clear pixels and depth-varying alpha.

    The old pass was a translucent coloured pane. This one behaves like irregular fused crystal:
    broad transparent windows, denser facet edges, internal colour planes and hairline clear breaks.
    """
    if not 0 <= variant < VARIANT_COUNT:
        raise ValueError(variant)
    col=_crystal_color(crystal)
    seed=_seed(f"mana_glass|{crystal['element']}|v{variant}")
    rng=random.Random(seed)
    im=Image.new('RGBA',(OUTPUT_SIZE,OUTPUT_SIZE),(0,0,0,0))
    px=im.load()
    for y in range(OUTPUT_SIZE):
        for x in range(OUTPUT_SIZE):
            n=_periodic32(x,y,seed)
            n2=_periodic32(x,y,seed^0xA54FF53A)
            light=1.0 + n*.10 + n2*.045 + ((x-y)/(OUTPUT_SIZE-1))*.035
            rgb=_mul(col,light)
            # Wide clear windows and translucent dense glass. Some pixels are genuinely empty.
            if n+n2*.55 > .56:
                alpha=0
            else:
                alpha=max(18,min(112,round(54 + n*24 + abs(n2)*31)))
            px[x,y]=rgb+(alpha,)
    draw=ImageDraw.Draw(im)
    edge_dark=_mix(col,(3,5,8),.38)
    edge_light=_mix(col,(245,250,248),.28)
    draw.rectangle((0,0,OUTPUT_SIZE-1,OUTPUT_SIZE-1),outline=edge_dark+(176,),width=2)
    draw.rectangle((2,2,OUTPUT_SIZE-3,OUTPUT_SIZE-3),outline=edge_light+(112,))
    # Four deterministic facet families; variant changes the crossings rather than recolouring them.
    shift=(variant*5 + seed%7)%OUTPUT_SIZE
    facets=[
        ((3+shift)%OUTPUT_SIZE, 25, (13+shift)%OUTPUT_SIZE, 4),
        ((10+shift)%OUTPUT_SIZE, 31, (21+shift)%OUTPUT_SIZE, 8),
        ((17+shift)%OUTPUT_SIZE, 27, (31+shift)%OUTPUT_SIZE, 13),
    ]
    for x0,y0,x1,y1 in facets:
        draw.line((x0,y0,x1,y1),fill=edge_dark+(130,),width=3)
        draw.line(((x0+1)%OUTPUT_SIZE,y0,(x1+1)%OUTPUT_SIZE,y1),fill=edge_light+(150,),width=1)
    # Fine clear fractures punch all the way through the pane.
    for _ in range(3):
        x=rng.randrange(OUTPUT_SIZE)
        pts=[]
        for y in range(-2,OUTPUT_SIZE+2,3):
            x=(x+rng.choice((-2,-1,0,1,2)))%OUTPUT_SIZE
            pts.append((x,y))
        _draw_wrapped_line_alpha(im,pts,(0,0,0,0),1,OUTPUT_SIZE)
    return im

def _draw_wrapped_line_alpha(im, pts, rgba, width, size):
    big=Image.new('RGBA',(size*3,size*3),(0,0,0,0))
    d=ImageDraw.Draw(big)
    for ox in (0,size,size*2):
        for oy in (0,size,size*2):
            d.line([(x+ox,y+oy) for x,y in pts],fill=rgba,width=width)
    patch=big.crop((size,size,size*2,size*2))
    # Replace rather than alpha-composite when drawing clear fractures.
    mask=patch.getchannel('A')
    if rgba[3]==0:
        # mask is zero for clear pixels, so derive a geometric mask from RGB-independent draw.
        marker=Image.new('L',(size*3,size*3),0); md=ImageDraw.Draw(marker)
        for ox in (0,size,size*2):
            for oy in (0,size,size*2):
                md.line([(x+ox,y+oy) for x,y in pts],fill=255,width=width)
        m=marker.crop((size,size,size*2,size*2))
        transparent=Image.new('RGBA',(size,size),(0,0,0,0))
        im.paste(transparent,(0,0),m)
    else:
        im.alpha_composite(patch)

def structural_signature(image):
    """Palette-independent luminance/edge signature used by static visual checks."""
    width,height=image.size
    vals=[]
    for y in range(height):
        for x in range(width):
            r,g,b,_=image.getpixel((x,y))
            vals.append((r*3+g*6+b)//10)
    edges=0
    for y in range(height):
        for x in range(width):
            v=vals[y*width+x]
            if abs(v-vals[y*width+(x+1)%width])>14: edges+=1
            if abs(v-vals[((y+1)%height)*width+x])>14: edges+=1
    return (len(set(vals)),edges)


def render_crystal_texture(crystal, kind='block', variant=0):
    """Native transparent crystal material for geode blocks, budding faces, clusters and shards.

    Crystal surfaces intentionally contain clear pixels. Block/budding faces use translucent
    faceted cells with void seams; cluster/shard textures are mostly transparent silhouette masks.
    """
    if kind not in ('block','budding','cluster','shard'):
        raise ValueError(kind)
    if not 0 <= variant < VARIANT_COUNT:
        raise ValueError(variant)
    col=_crystal_color(crystal)
    seed=_seed(f"crystal|{crystal['id']}|{kind}|v{variant}")
    rng=random.Random(seed)
    light=_mix(col,(255,255,250),.42)
    mid=_mix(col,(238,246,250),.14)
    dark=_mix(col,(4,6,10),.38)

    if kind in ('cluster','shard'):
        im=Image.new('RGBA',(OUTPUT_SIZE,OUTPUT_SIZE),(0,0,0,0))
        d=ImageDraw.Draw(im)
        if kind=='cluster':
            # Several overlapping tapered prisms.  Broad transparent background is deliberate.
            spikes=[(5,29,11,8),(12,31,17,3),(18,29,24,11),(23,30,29,16)]
            shift=(variant*3)%5
            for i,(x0,y0,x1,y1) in enumerate(spikes):
                x0=(x0+shift+i)%OUTPUT_SIZE; x1=(x1+shift+i)%OUTPUT_SIZE
                w=3+(i%2)
                poly=[(x0-w,y0),(x0+w,y0),(x1+1,y1+3),(x1,y1),(x1-1,y1+3)]
                d.polygon(poly,fill=mid+(185+i*10,))
                d.line((x0-w,y0,x1-1,y1+3),fill=dark+(210,),width=1)
                d.line((x0+w-1,y0-1,x1,y1+1),fill=light+(225,),width=1)
        else:
            # Item shard: three splinters, enough transparency to read as crystal rather than stone.
            pieces=[[(9,27),(12,8),(15,4),(16,11),(14,27)],
                    [(15,28),(20,13),(23,10),(22,19),(19,29)],
                    [(6,29),(8,17),(10,15),(10,24),(9,30)]]
            for i,p in enumerate(pieces):
                dx=(variant*2+i)%4-1
                pp=[(x+dx,y) for x,y in p]
                d.polygon(pp,fill=mid+(205,))
                d.line(pp+[pp[0]],fill=dark+(220,),width=1)
                d.line((pp[1],pp[2]),fill=light+(245,),width=1)
        return im

    # Full crystal/budding faces.
    im=Image.new('RGBA',(OUTPUT_SIZE,OUTPUT_SIZE),(0,0,0,0))
    px=im.load()
    for y in range(OUTPUT_SIZE):
        for x in range(OUTPUT_SIZE):
            n=_periodic32(x,y,seed)
            n2=_periodic32(x,y,seed^0x3C6EF372)
            # Crystal body is translucent, but coherent void seams cut through it completely.
            seam=abs(math.sin((x*0.31+y*0.17)+(variant*.9)+n*1.8))
            if seam < .075 and n2 > -.25:
                alpha=0
            else:
                alpha=max(72,min(202,round(142+n*38+n2*26)))
            tone=1.0+n*.10+n2*.06
            px[x,y]=_mul(col,tone)+(alpha,)
    d=ImageDraw.Draw(im)
    # Polygonal facet network with shadow/highlight lips.
    nodes=[(2,5),(10,1),(18,6),(29,3),(6,15),(15,12),(25,17),(2,26),(13,29),(23,25),(31,30)]
    off=(variant*4)%7
    nodes=[((x+off)%OUTPUT_SIZE,y) for x,y in nodes]
    edges=((0,1),(1,2),(2,3),(0,4),(1,5),(2,5),(2,6),(4,5),(5,6),(4,7),(5,8),(6,9),(7,8),(8,9),(9,10))
    for a,b in edges:
        p0,p1=nodes[a],nodes[b]
        d.line((p0,p1),fill=dark+(165,),width=2)
        d.line(((p0[0]+1)%OUTPUT_SIZE,p0[1],(p1[0]+1)%OUTPUT_SIZE,p1[1]),fill=light+(190,),width=1)
    if kind=='budding':
        for _ in range(9):
            cx,cy=rng.randrange(3,OUTPUT_SIZE-3),rng.randrange(3,OUTPUT_SIZE-3)
            d.polygon([(cx,cy-3),(cx+3,cy),(cx,cy+2),(cx-2,cy)],fill=light+(220,))
            d.line((cx-2,cy,cx,cy+2,cx+3,cy),fill=dark+(190,),width=1)
    return im
