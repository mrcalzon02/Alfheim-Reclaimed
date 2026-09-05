"""Shared item-texture primitives: recolour, composite, and load a base texture.

Extracted from `tools/gen_items.py` so `gen_curios.py` can derive its icons the same way rather
than growing a second copy of the primitive that decides what every generated item looks like.
Both generators import from here; neither owns it.

**Licence boundary.** `load_base` will read from three places, and they are not equal:

  * the vanilla client jar   — safe to derive from, and the default for anything shipped;
  * `kubejs/assets/<ns>/`    — our own generated art, safe by definition;
  * an installed mod jar     — a third-party work. `INSTRUCTIONS.md` §5 forbids editing or
                               redistributing those jars, and a recoloured copy of a mod's
                               texture in our asset tree is redistribution of a derivative.
                               Reading one is therefore opt-in per call (`allow_mod=True`) and
                               `gen_curios.py` never asks for it.
"""
import colorsys
import glob
import os
import zipfile

from PIL import Image

CLIENT_JAR = (r'C:\Users\Admin\curseforge\minecraft\Install\versions'
              r'\1.20.1\1.20.1.jar')


def tint(img, hue_deg, sat_mul, val_mul, sat_floor=0.0, absolute_hue=True):
    """Recolour a texture, preserving alpha and per-pixel shading.

    `sat_floor` matters more than it looks. Many vanilla bases (string, sugar, bone meal) are
    near-white, so their saturation is ~0 — multiplying that by anything is still ~0 and the
    hue rotation has no visible effect. Raising saturation to a floor first is what lets a
    white texture actually take a colour.

    `absolute_hue` sets the hue outright rather than rotating from the base's own hue, so the
    result does not depend on what colour the base happened to be.
    """
    img = img.convert('RGBA')
    out = Image.new('RGBA', img.size)
    src, dst = img.load(), out.load()
    target = (hue_deg % 360) / 360.0
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = src[x, y]
            if a == 0:
                dst[x, y] = (0, 0, 0, 0)
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            h = target if absolute_hue else (h + target) % 1.0
            s = max(s, sat_floor)
            s = max(0.0, min(1.0, s * sat_mul))
            v = max(0.0, min(1.0, v * val_mul))
            nr, ng, nb = colorsys.hsv_to_rgb(h, s, v)
            dst[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)
    return out


def overlay(base, top, alpha=0.55):
    """Composite a second texture over the base, for two-part items."""
    top = top.convert('RGBA').resize(base.size)
    faded = Image.new('RGBA', base.size)
    tp, fp = top.load(), faded.load()
    for y in range(base.height):
        for x in range(base.width):
            r, g, b, a = tp[x, y]
            fp[x, y] = (r, g, b, int(a * alpha))
    return Image.alpha_composite(base.convert('RGBA'), faded)


def mask_to(base, stencil):
    """Keep only the pixels of `base` that `stencil` also paints.

    Used to press a material's colour into a silhouette that already reads as jewellery: the
    stencil supplies the shape, the base supplies the surface. Without this an overlay spills
    outside the form and the icon stops looking like a ring.
    """
    base = base.convert('RGBA')
    stencil = stencil.convert('RGBA').resize(base.size)
    out = Image.new('RGBA', base.size)
    bp, sp, op = base.load(), stencil.load(), out.load()
    for y in range(base.height):
        for x in range(base.width):
            sa = sp[x, y][3]
            if sa == 0:
                op[x, y] = (0, 0, 0, 0)
            else:
                r, g, b, a = bp[x, y]
                op[x, y] = (r, g, b, min(a, sa))
    return out


_MOD_JARS = None


def _mod_jars():
    global _MOD_JARS
    if _MOD_JARS is None:
        _MOD_JARS = sorted(glob.glob(os.path.join('mods', '*.jar')))
    return _MOD_JARS


def load_base(jar, name, allow_mod=True, own_assets='kubejs/assets'):
    """Load a base texture.

    "string.png"                   -> vanilla assets/minecraft/textures/item/string.png
    "alfheim:elementium_core.png"  -> our own generated art under kubejs/assets/
    "botania:mana_powder.png"      -> that namespace's item texture, from whichever mod jar has
                                      it. Requires allow_mod=True; see the licence note above.
    "botania:block/livingwood.png" -> an explicit subpath under textures/
    """
    ns, rest = name.split(':', 1) if ':' in name else ('minecraft', name)

    if ns == 'minecraft':
        # Vanilla lives in the client jar, not in any mod jar.
        sub = rest if '/' in rest else f'item/{rest}'
        with jar.open(f'assets/minecraft/textures/{sub}') as f:
            return Image.open(f).convert('RGBA').copy()

    sub = rest if '/' in rest else f'item/{rest}'

    # Our own asset tree wins over a mod jar of the same namespace: if we generated it, that is
    # the art we mean, and it is the copy we are allowed to derive from.
    own = os.path.join(own_assets, ns, 'textures', *sub.split('/'))
    if os.path.exists(own):
        return Image.open(own).convert('RGBA').copy()

    if not allow_mod:
        raise FileNotFoundError(
            f'{name}: not found under {own_assets}/{ns}/textures/, and mod jars are not '
            f'permitted for this generator (see the licence note in tools/item_textures.py)')

    for mj in _mod_jars():
        try:
            with zipfile.ZipFile(mj) as z:
                if sub and f'assets/{ns}/textures/{sub}' in set(z.namelist()):
                    with z.open(f'assets/{ns}/textures/{sub}') as f:
                        return Image.open(f).convert('RGBA').copy()
        except Exception:
            continue
    raise FileNotFoundError(f'texture not found in any mod jar: {name}')
