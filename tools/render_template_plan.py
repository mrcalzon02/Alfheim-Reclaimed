"""Render a shipping structure template as floor plans, coloured by what a block IS.

`check_structure_detail.py` can say a piece carries a 12% detail share over 24 block ids. It
cannot say whether those blocks are in sensible places, and that is the question the September 9
field review actually asked: "podiums and crafting blocks and anvils and all kinds of blocks
added all over to all kinds of structures where they definitely do not belong". A census counts;
a plan shows.

Six classes, chosen so the failure mode is visible at a glance rather than legible only to
someone who knows the palette:

    red         the universal-catalogue furniture the detail pass used to scatter
    blue-grey   stair, slab, wall, fence, trapdoor, pane -- small-scale articulation
    yellow      light of any kind
    green       moss, root, vine, web -- what the decay pass let in
    grey        bulk mass
    near-black  air

Comparing a piece against its own history is the useful move, and git makes that cheap:

    git show <rev>:kubejs/data/alfheim/structures/<family>/<piece>.nbt > before.nbt
    python tools/render_template_plan.py before.nbt before.png "faultwork/wing before" 2,6,10,14
    python tools/render_template_plan.py \\
        kubejs/data/alfheim/structures/deepworks_archaeology/faultwork/wing.nbt \\
        after.png "faultwork/wing after" 2,6,10,14

It reports the furniture tally on stderr as well, so the picture and the number come from the
same read of the same file.
"""
import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402

try:
    from PIL import Image, ImageDraw
except ImportError:                                     # pragma: no cover
    sys.exit('Pillow is required: python -m pip install pillow')

# Kept in step with structure_detail.furnish()'s catalogue. Anything this pass can place
# without being told what the building is belongs here.
FURNITURE = {
    'minecraft:lectern', 'minecraft:bookshelf', 'minecraft:cauldron',
    'minecraft:decorated_pot', 'minecraft:barrel', 'minecraft:crafting_table',
    'minecraft:brewing_stand', 'minecraft:cartography_table', 'minecraft:anvil',
    'minecraft:smithing_table', 'minecraft:grindstone', 'minecraft:loom',
    'minecraft:composter',
}
LIGHT = ('torch', 'lantern', 'candle', 'glow', '_light', 'cluster', 'campfire', 'shroomlight')
DETAIL = ('_stairs', '_slab', '_wall', '_fence', '_fence_gate', '_trapdoor', '_pane',
          '_carpet', '_button', '_pressure_plate', '_sign', '_bars', '_chain', '_rod')
PLANT = ('moss', 'vine', 'root', 'sapling', 'flower', 'grass', 'fern', 'leaves',
         'wheat', 'web', 'drip', 'lichen')

C_BG, C_AIR = (16, 16, 20), (26, 26, 32)
C_MASS, C_DETAIL = (108, 104, 96), (150, 176, 196)
C_LIGHT, C_PLANT, C_FURN = (238, 206, 120), (104, 150, 96), (222, 74, 74)


def classify(name):
    if not name or name in ('minecraft:air', 'minecraft:cave_air'):
        return None
    if name in FURNITURE:
        return C_FURN
    low = name.lower()
    if any(k in low for k in LIGHT):
        return C_LIGHT
    if any(k in low for k in PLANT):
        return C_PLANT
    if any(low.endswith(k) for k in DETAIL):
        return C_DETAIL
    return C_MASS


def load(path):
    _name, root = nbt.load(path)
    pal = [b.get('Name', '') for b in (root.get('palette') or [])]
    size = root.get('size') or [0, 0, 0]
    cells = {}
    for blk in root.get('blocks') or []:
        pos, state = blk.get('pos'), blk.get('state')
        if pos is None or state is None or state >= len(pal):
            continue
        cells[(pos[0], pos[1], pos[2])] = pal[state]
    return cells, size


def render(cells, size, levels, out, title):
    sx, _sy, sz = size
    pad, gap, head = 14, 10, 16
    W = pad * 2 + len(levels) * sx + (len(levels) - 1) * gap
    H = pad * 2 + sz + head
    im = Image.new('RGB', (W, H), C_BG)
    px = im.load()
    for i, y in enumerate(levels):
        ox = pad + i * (sx + gap)
        for x in range(sx):
            for z in range(sz):
                c = classify(cells.get((x, y, z)))
                px[ox + x, pad + head + z] = c if c else C_AIR
    scale = max(1, min(4, 1400 // max(1, W)))
    im = im.resize((W * scale, H * scale), Image.NEAREST)
    d = ImageDraw.Draw(im)
    d.text((4, 3), title, fill=(235, 235, 235))
    for i, y in enumerate(levels):
        d.text(((pad + i * (sx + gap)) * scale, (pad + 4) * scale), f'y={y}',
               fill=(190, 190, 190))
    im.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('template')
    ap.add_argument('out')
    ap.add_argument('title')
    ap.add_argument('levels', help='comma-separated Y levels to plan, e.g. 2,6,10,14')
    a = ap.parse_args()

    cells, size = load(a.template)
    levels = [int(v) for v in a.levels.split(',')]
    bad = [y for y in levels if not 0 <= y < size[1]]
    if bad:
        sys.exit(f'Y level(s) {bad} outside the piece, which is {size[1]} tall')
    render(cells, size, levels, a.out, a.title)

    tally = collections.Counter(n for n in cells.values() if n in FURNITURE)
    print(f'{os.path.basename(a.template)}  size {size}  '
          f'furniture {sum(tally.values())}'
          + (f'  {dict(tally)}' if tally else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
