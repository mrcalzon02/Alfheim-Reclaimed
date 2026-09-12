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


# EVERY void biome, not just the Verge. The terrain handover is not the biome contour -- it sits
# further out, under the inner debris biomes -- so measuring only Verge columns would reward
# moving the handover rather than testing it, and the wall would simply relocate out of frame.
DEBRIS_BIOMES = {'alfheim:shatterfields', 'alfheim:prism_drift', 'alfheim:rootfall',
                 'alfheim:sepulchral_reach', 'alfheim:starless_reach'}
MARGIN_BIOMES = {'alfheim:void_verge'} | DEBRIS_BIOMES
# A mass this tall standing against nothing is a wall. Genuine floating debris is well under it,
# so raising the threshold would hide walls and lowering it would count islands as walls.
WALL = 30


def edge_quality(region_dir):
    """HOW SLICED IS THE EDGE? Three numbers, none of which a per-column sweep can produce.

    A density function whose body saturates at +1 can only ever answer "whole slab" or "nothing"
    for a given column, and a field of those reads as a sliced cake however much its top and
    bottom wander. These measure that directly, over Verge columns that have void within reach:

      CUT SHARE   adjacent pairs where one column carries 30+ blocks of ground and its
                  neighbour carries none at all. That IS a hard slice: a 30-block wall between
                  two columns, with nothing in between to read as a slope, a ledge or a talus.

      STEP        mean absolute change in solid-block count between adjacent columns. A knife
                  edge concentrates all its change in a few pairs; broken ground spreads it.

      RUNS        mean separate solid runs per column. Exactly 1.0 everywhere means every
                  column is one unbroken slab -- no alcoves, no overhangs, no arches, no
                  detached pieces. Anything a cliff face is made of raises this.
    """
    from probe_terraces import chunks as _chunks, unpack_bits, biome_at
    solid, biome = {}, {}
    for path in sorted(glob.glob(os.path.join(region_dir, '*.mca'))):
        for chunk in _chunks(path):
            if not chunk or chunk.get('Status') != 'minecraft:full':
                continue
            sections = chunk.get('sections') or []
            cx, cz = chunk.get('xPos'), chunk.get('zPos')
            heightmap = (chunk.get('Heightmaps') or {}).get('WORLD_SURFACE')
            if cx is None or not heightmap:
                continue
            values = unpack_bits(heightmap, 9, 256)
            blocks = {}
            for section in sections:
                names = section_blocks(section)
                if names:
                    blocks[section['Y']] = names
            for index in range(256):
                z, x = divmod(index, 16)
                top = values[index] + MIN_Y - 1
                b = biome_at(sections, max(top, MIN_Y), x, z)
                if b is None:
                    continue
                gx, gz = cx * 16 + x, cz * 16 + z
                biome[(gx, gz)] = b
                if b not in MARGIN_BIOMES:
                    continue
                column = [blocks[y >> 4][(y & 15) * 256 + z * 16 + x]
                          if (y >> 4) in blocks else 'minecraft:air'
                          for y in range(MIN_Y, 140)]
                runs, count = profile(column)
                solid[(gx, gz)] = (count, len(runs), runs[0][0] if runs else None)

    # "at the break" means it has void within reach, whatever biome that void wears.
    near = {p for p in solid
            if any(solid.get((p[0] + dx, p[1] + dz), (1,))[0] == 0
                   or biome.get((p[0] + dx, p[1] + dz)) in MARGIN_BIOMES
                   and (p[0] + dx, p[1] + dz) not in solid
                   for dx, dz in ((-8, 0), (8, 0), (0, -8), (0, 8), (-4, 0), (4, 0)))}
    cuts = pairs = 0
    steps, runs_all, rooted = [], [], 0
    for (x, z) in near:
        count, nruns, base = solid[(x, z)]
        # Only columns that carry ground: an empty one has no runs, and averaging zeros in
        # drags the figure below 1.0 and makes it unreadable.
        if count:
            runs_all.append(nruns)
        if base is not None and base <= -50:
            rooted += 1
        for dx, dz in ((1, 0), (0, 1)):
            other = solid.get((x + dx, z + dz))
            if other is None:
                # a neighbour with no Verge column at all: void, if it is a debris biome
                if biome.get((x + dx, z + dz)) in MARGIN_BIOMES:
                    pairs += 1
                    if count >= WALL:
                        cuts += 1
                continue
            pairs += 1
            steps.append(abs(count - other[0]))
            if (count >= WALL and other[0] == 0) or (other[0] >= WALL and count == 0):
                cuts += 1
    if not near:
        print('no Verge columns with void in reach; nothing to measure')
        return 1
    print('margin columns beside void: %d   of them carrying ground: %d   adjacent pairs: %d'
          % (len(near), len(runs_all), pairs))
    # CUT SHARE's denominator moves when terrain is ADDED -- filling a gap removes benign
    # pairs from it as well as walls -- so the rate can rise while the walls fall. WALLS is the
    # one to read across builds: margin biome membership does not change with terrain, so it is
    # a fixed denominator.
    print('  CUT SHARE  %5.1f%%  of adjacent pairs are a %d+ block wall against nothing'
          % (100 * cuts / pairs if pairs else 0, WALL))
    print('  WALLS      %5.1f   such walls per 1000 margin columns (%d over %d) <-- compare THIS'
          % (1000 * cuts / len(solid) if solid else 0, cuts, len(solid)))
    print('  STEP       %5.1f   mean change in solid blocks between neighbours'
          % (sum(steps) / len(steps) if steps else 0))
    print('  RUNS       %5.2f   mean solid runs per column (1.00 = every column one slab)'
          % (sum(runs_all) / len(runs_all) if runs_all else 0))
    print('  ROOTED     %5.1f%%  of them still reach bedrock (full-depth fins)'
          % (100 * rooted / len(runs_all) if runs_all else 0))
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('region_dir')
    parser.add_argument('--edge-quality', action='store_true',
                        help='how sliced the break is: cut share, step, runs per column')
    parser.add_argument('--census', action='store_true',
                        help='water-bearing share per biome; the dry-ocean measurement')
    parser.add_argument('--transect', help='z=<value>')
    parser.add_argument('--x', help='<x0>,<x1>')
    parser.add_argument('--image', help='also write a cross-section PNG of the transect')
    args = parser.parse_args()
    status = 0
    if args.edge_quality:
        status |= bool(edge_quality(args.region_dir))
    if args.census:
        status |= bool(census(args.region_dir))
    if args.transect:
        if not args.x:
            parser.error('--transect needs --x <x0>,<x1>')
        z = int(args.transect.split('=')[1])
        x0, x1 = (int(v) for v in args.x.split(','))
        status |= bool(transect(args.region_dir, z, x0, x1, args.image))
    if not (args.census or args.transect or args.edge_quality):
        parser.error('nothing to do: pass --census, --transect or --edge-quality')
    return status


if __name__ == '__main__':
    sys.exit(main())
