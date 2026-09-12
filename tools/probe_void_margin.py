#!/usr/bin/env python3
"""Read the margin as a cross-section, because a density function can be correct at every
sampled point and still produce the wrong landform.

Three defects on 2026-09-11 were invisible to thirteen passing static guards and obvious in one
column table:

  THE OCEAN WAS DRY          alfheim_ocean claimed continentalness out to -0.80 while the
                             aquifer dried everything below -0.58, so 123,145 of 348,224 ocean
                             columns generated with a seabed at Y 30 and open air above it.
                             --census is the number that says so: water-bearing share, per biome.

  THE VERGE STOOD FREE       rim_base cut the shelf's landward face too. At z=223 the seabed at
                             x=-113 is solid -53..28 and the Verge at x=-112 is solid 11..34.
                             The base column is where that shows: a base far above its inland
                             neighbour's means the approach is not attached to anything.

  THE BREAK HAD NO WIDTH     x=-77 solid 12..72, x=-76 zero solid blocks in the entire column.
                             The runs column and the section image show whether the drop has any
                             steps in it or is one face.

    python tools/probe_void_margin.py <region_dir> --census
    python tools/probe_void_margin.py <region_dir> --transect z=223 --x -180,40
    python tools/probe_void_margin.py <region_dir> --transect z=223 --x -180,40 --image out.png

region_dir is a world's dimensions/mythicbotany/alfheim/region. Reads only; never writes into a
save. For the complementary measurement that needs no generated world at all -- face-height
distributions read straight off the shipped density function, against a control -- see
tools/measure_void_edge.py.
"""
import argparse
import collections
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_terraces import chunks, unpack_bits, biome_at, section_blocks, MIN_Y  # noqa: E402

AIR = {'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air'}
FLUID = {'minecraft:water', 'minecraft:lava'}
SEA_LEVEL = 64
# Below this a column carries the basal guard slab or nothing at all, not ground.
GUARD = -54


def columns(region_dir, want_chunk_z=None):
    """Yield (x, z, surface_y, biome, sections, local_x, local_z) for every generated column."""
    for path in sorted(glob.glob(os.path.join(region_dir, '*.mca'))):
        for chunk in chunks(path):
            if not chunk:
                continue
            heightmap = (chunk.get('Heightmaps') or {}).get('WORLD_SURFACE')
            sections = chunk.get('sections') or []
            cx, cz = chunk.get('xPos'), chunk.get('zPos')
            if not heightmap or cx is None:
                continue
            if want_chunk_z is not None and cz != want_chunk_z:
                continue
            values = unpack_bits(heightmap, 9, 256)
            for index in range(256):
                z, x = divmod(index, 16)
                top = values[index] + MIN_Y - 1
                biome = biome_at(sections, max(top, MIN_Y), x, z)
                if biome:
                    yield cx * 16 + x, cz * 16 + z, top, biome, sections, x, z


def census(region_dir):
    """Water-bearing share per biome. AN OCEAN BIOME WITH DRY COLUMNS IS THE DEFECT."""
    surface = collections.defaultdict(list)
    for _x, _z, top, biome, *_rest in columns(region_dir):
        surface[biome].append(top)
    if not surface:
        print('no generated columns found in', region_dir)
        return 1
    rows = []
    for biome, tops in surface.items():
        tops.sort()
        count = len(tops)
        rows.append((count, biome, tops[0], tops[count // 2], tops[-1],
                     sum(1 for t in tops if t >= SEA_LEVEL - 1) / count,
                     sum(1 for t in tops if t <= GUARD) / count))
    rows.sort(reverse=True)
    print('%-34s %9s %6s %6s %6s %10s %7s' %
          ('biome', 'columns', 'minY', 'medY', 'maxY', 'at sea lv', 'bare'))
    problems = 0
    for count, biome, low, mid, high, wet, bare in rows:
        flag = ''
        if 'ocean' in biome and wet < 0.98:
            flag = '   <-- %.1f%% OF THIS OCEAN IS BELOW SEA LEVEL WITH NOTHING ON IT' % (100 * (1 - wet))
            problems += 1
        print('%-34s %9d %6d %6d %6d %9.1f%% %6.1f%%%s' %
              (biome, count, low, mid, high, 100 * wet, 100 * bare, flag))
    return problems


def profile(column):
    """(runs, solid_count) for one column, counting only ground above the basal guard."""
    solid = [y for y, name in zip(range(MIN_Y, 200), column)
             if name not in AIR and name not in FLUID and y > GUARD]
    runs = []
    start = prev = None
    for y in solid:
        if prev is None or y != prev + 1:
            if start is not None:
                runs.append((start, prev))
            start = y
        prev = y
    if start is not None:
        runs.append((start, prev))
    return runs, len(solid)


def transect(region_dir, z, x0, x1, image=None):
    surface = {}
    depth = {}
    for x, zz, top, biome, sections, lx, lz in columns(region_dir, want_chunk_z=z >> 4):
        if zz != z or not (x0 <= x <= x1) or x in depth:
            continue
        surface[x] = biome
        blocks = {}
        for section in sections:
            names = section_blocks(section)
            if names:
                blocks[section['Y']] = names
        depth[x] = [blocks[y >> 4][(y & 15) * 256 + lz * 16 + lx]
                    if (y >> 4) in blocks else 'minecraft:air'
                    for y in range(MIN_Y, 200)]
    if not depth:
        print('no generated columns at z=%d between x=%d and x=%d' % (z, x0, x1))
        return 1
    print('%6s %-24s %6s %6s %6s %6s %6s %6s  runs' %
          ('x', 'biome', 'top', 'base', 'solid', 'gaps', 'water', 'lava'))
    for x in range(x0, x1 + 1):
        if x not in depth:
            continue
        column = depth[x]
        runs, solid = profile(column)
        print('%6d %-24s %6s %6s %6d %6d %6d %6d  %s' %
              (x, (surface.get(x) or '?').split(':')[-1],
               runs[-1][1] if runs else '-', runs[0][0] if runs else '-', solid,
               max(0, len(runs) - 1),
               sum(1 for n in column if n == 'minecraft:water'),
               sum(1 for n in column if n == 'minecraft:lava'),
               ','.join('%d-%d' % r for r in runs[:5])))
    if image:
        render(depth, surface, x0, x1, image)
    return 0


# Ordered: the first key that appears in a block name wins, so the specific stones are listed
# before the generic livingrock they are all named after.
PALETTE = (
    ('water', (40, 90, 200)), ('lava', (230, 110, 20)), ('deepslate', (70, 70, 78)),
    ('amethyst', (170, 130, 210)), ('prism', (170, 130, 210)), ('riftchalk', (214, 210, 198)),
    ('nightmantle', (60, 60, 90)), ('nullstone', (60, 60, 90)), ('astralite', (110, 110, 160)),
    ('sand', (205, 195, 155)), ('gravel', (150, 148, 142)), ('grass', (95, 150, 70)),
    ('leaves', (80, 130, 60)), ('log', (120, 90, 55)), ('livingrock', (188, 186, 176)),
    ('stone', (140, 140, 140)),
)


def render(depth, surface, x0, x1, path):
    from PIL import Image, ImageDraw
    scale, low, high = 3, MIN_Y, 140
    width, height = (x1 - x0 + 1) * scale, (high - low + 1) * scale
    image = Image.new('RGB', (width, height + 44), (18, 20, 26))
    draw = ImageDraw.Draw(image)
    for x in range(x0, x1 + 1):
        column = depth.get(x)
        if not column:
            continue
        for y in range(low, high + 1):
            name = column[y - MIN_Y]
            if name in AIR:
                continue
            colour = next((c for key, c in PALETTE if key in name), (225, 90, 160))
            px, py = (x - x0) * scale, height - (y - low + 1) * scale
            draw.rectangle([px, py, px + scale - 1, py + scale - 1], fill=colour)
    for x in range(x0, x1 + 1):
        biome = surface.get(x) or ''
        if biome:
            tint = sum(ord(c) for c in biome)
            draw.rectangle([(x - x0) * scale, height + 4,
                            (x - x0) * scale + scale - 1, height + 16],
                           fill=((tint * 37) % 200 + 40, (tint * 91) % 200 + 40,
                                 (tint * 53) % 200 + 40))
    for y in (SEA_LEVEL, 0, GUARD):
        py = height - (y - low + 1) * scale
        draw.line([0, py, width, py], fill=(255, 255, 255))
        draw.text((3, py - 11), 'Y%d' % y, fill=(255, 255, 255))
    image.save(path)
    print('\nwrote', path, image.size)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('region_dir')
    parser.add_argument('--census', action='store_true',
                        help='water-bearing share per biome; the dry-ocean measurement')
    parser.add_argument('--transect', help='z=<value>')
    parser.add_argument('--x', help='<x0>,<x1>')
    parser.add_argument('--image', help='also write a cross-section PNG of the transect')
    args = parser.parse_args()
    status = 0
    if args.census:
        status |= bool(census(args.region_dir))
    if args.transect:
        if not args.x:
            parser.error('--transect needs --x <x0>,<x1>')
        z = int(args.transect.split('=')[1])
        x0, x1 = (int(v) for v in args.x.split(','))
        status |= bool(transect(args.region_dir, z, x0, x1, args.image))
    if not (args.census or args.transect):
        parser.error('nothing to do: pass --census or --transect')
    return status


if __name__ == '__main__':
    sys.exit(main())
