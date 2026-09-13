#!/usr/bin/env python3
"""Count the structures that actually reached the ground in a generated Alfheim, and find the ones
that were placed below the floor of the world instead.

WHY THIS EXISTS. A jigsaw structure with `project_start_to_heightmap` has its start Y computed as
`start_height + chunkGenerator.getFirstFreeHeight(x, z, heightmap)`. In a column that is air from
min_y to build height there is no free height to find, the lookup falls back to the minimum build
height, and the start lands at or below min_y. Everything the jigsaw then writes below the floor is
discarded, silently: no exception, no log line, and the chunk's `structures.starts` entry still
exists. So a void biome can be fully stocked with structures on paper and empty in play, and the
only way to tell the difference is to read the placed bounding boxes out of a saved world.

    python tools/probe_void_structures.py --world "saves/New World burnshire"
    python tools/probe_void_structures.py --world ... --only verge_spire

Reads `structures.starts` from every Alfheim region file. A start is COUNTED as placed only when it
has Children -- vanilla keeps an entry for a start it then discarded -- and its bounding box is
reported in Y, because that is the number the failure shows up in.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from biome_census import chunks  # noqa: E402

MIN_Y = -64          # mythicbotany:alfheim noise_settings
SEA = 64


def void_registered():
    """Structure short-names registered in a genuinely-void biome, and whether they project.

    void_shore is excluded on purpose: it is the aquifer collar and it is land above sea level by
    design, so a heightmap lookup there succeeds and projection is the right choice.
    """
    from gen_void_worldgen import VOID_IDS, COAST_ID
    deep = set(VOID_IDS) - {COAST_ID}
    tags = {}
    for path in glob.glob(os.path.join('kubejs', 'data', '*', 'tags', 'worldgen', 'biome', '*.json')):
        parts = path.replace(os.sep, '/').split('/')
        with open(path, encoding='utf-8') as handle:
            tags['#%s:%s' % (parts[2], parts[-1][:-5])] = json.load(handle).get('values', [])

    def expand(entry, depth=0):
        if depth > 5:
            return []
        out = []
        for item in ([entry] if isinstance(entry, str) else entry):
            item = item if isinstance(item, str) else item.get('id', '')
            if item.startswith('#'):
                out += expand(tags.get(item, []), depth + 1)
            elif item:
                out.append(item)
        return out

    found = {}
    for path in glob.glob(os.path.join('kubejs', 'data', '*', 'worldgen', 'structure', '*.json')):
        with open(path, encoding='utf-8') as handle:
            body = json.load(handle)
        if set(expand(body.get('biomes', []))) & deep:
            name = os.path.basename(path)[:-5]
            found[name] = body.get('project_start_to_heightmap') is not None
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--world', default=os.path.join('saves', 'New World burnshire'))
    parser.add_argument('--only')
    parser.add_argument('--ground', action='store_true',
                        help='where solid rock actually is, per void biome')
    parser.add_argument('--every', type=int, default=4,
                        help='sample 1 chunk in N for --ground')
    args = parser.parse_args()

    region = os.path.join(args.world, 'dimensions', 'mythicbotany', 'alfheim', 'region')
    if not os.path.isdir(region):
        print('no Alfheim region directory at ' + region)
        return 1
    if args.ground:
        return ground_report(region, max(1, args.every))
    projected = void_registered()

    placed = collections.defaultdict(list)      # short -> [y0]
    hollow = collections.Counter()              # short -> starts with no Children
    files = sorted(glob.glob(os.path.join(region, '*.mca')))
    scanned = 0
    for path in files:
        for root in chunks(path):
            scanned += 1
            for sid, start in root.get('structures', {}).get('starts', {}).items():
                short = str(sid).split(':', 1)[-1]
                if args.only and short != args.only:
                    continue
                if not isinstance(start, dict):
                    continue
                children = start.get('Children') or []
                if not children:
                    hollow[short] += 1
                    continue
                lows = [int(c['BB'][1]) for c in children if c.get('BB')]
                if lows:
                    placed[short].append(min(lows))

    print('%d chunks in %d region files under %s' % (scanned, len(files), region))
    print()
    print('%-24s %-5s %6s %6s %6s %6s  %s'
          % ('structure', 'proj', 'starts', 'minY', 'medY', 'maxY', 'verdict'))
    print('-' * 92)
    names = sorted(set(placed) | set(hollow))
    for short in names:
        ys = sorted(placed[short])
        mark = {True: 'yes', False: 'no'}.get(projected.get(short), '-')
        if not ys:
            print('%-24s %-5s %6d %6s %6s %6s  NO PLACED PIECES (%d empty starts)'
                  % (short, mark, 0, '-', '-', '-', hollow[short]))
            continue
        low, high = ys[0], ys[-1]
        mid = ys[len(ys) // 2]
        if high < MIN_Y:
            verdict = 'ENTIRELY BELOW THE WORLD FLOOR -- writes nothing'
        elif low < MIN_Y:
            verdict = 'some starts below the floor (%d of %d)' % (sum(1 for y in ys if y < MIN_Y), len(ys))
        elif short in projected and projected[short] and high <= MIN_Y + 8:
            verdict = 'pinned to the floor: the heightmap found no surface'
        else:
            verdict = 'ok'
        print('%-24s %-5s %6d %6d %6d %6d  %s' % (short, mark, len(ys), low, mid, high, verdict))
    print('-' * 92)
    void_only = [n for n in projected if projected[n]]
    seen = [n for n in void_only if placed.get(n)]
    print('%d of the %d projected void structures put a single piece anywhere in this world: %s'
          % (len(seen), len(void_only), ', '.join(sorted(seen)) or 'none'))
    return 0




# --- where the rock actually is ------------------------------------------------------------
# Choosing a Y band for a void structure by eye is how the projected placements got written in
# the first place. This reports, per void biome, the share of chunks carrying any solid block in
# each 16-block section, at section resolution: presence is exact at that granularity because a
# section whose palette holds nothing but air is empty by definition, no index unpacking needed.
AIR_NAMES = {'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air'}


def section_biomes(section):
    body = section.get('biomes')
    if not isinstance(body, dict):
        return []
    palette = [str(x) for x in (body.get('palette') or [])]
    if section.get('biomes', {}).get('data') is None:
        return palette[:1] * 64 if palette else []
    bits = max(1, (len(palette) - 1).bit_length())
    mask = (1 << bits) - 1
    out = []
    for word in body['data']:
        value = int(word) & 0xFFFFFFFFFFFFFFFF
        for slot in range(64 // bits):
            if len(out) >= 64:
                break
            index = (value >> (slot * bits)) & mask
            out.append(palette[index] if index < len(palette) else '')
        if len(out) >= 64:
            break
    return out


def ground_report(region, every):
    import collections as _c
    from gen_void_worldgen import VOID_IDS, COAST_ID
    wanted = set(VOID_IDS) | {COAST_ID}
    rock = _c.defaultdict(_c.Counter)     # biome -> Counter(section_y -> chunks with rock)
    total = _c.Counter()                  # biome -> chunks attributed
    seen = 0
    for path in sorted(glob.glob(os.path.join(region, '*.mca'))):
        for root in chunks(path):
            if str(root.get('Status', '')) != 'minecraft:full':
                continue
            seen += 1
            if seen % every:
                continue
            tally = _c.Counter()
            solid = set()
            for section in root.get('sections', []):
                for name in section_biomes(section):
                    if name in wanted:
                        tally[name] += 1
                palette = [str(s.get('Name', '')) for s
                           in (section.get('block_states', {}).get('palette') or [])]
                if any(n and n not in AIR_NAMES for n in palette):
                    solid.add(int(section.get('Y', -99)))
            if not tally:
                continue
            biome = tally.most_common(1)[0][0]
            total[biome] += 1
            for y in solid:
                rock[biome][y] += 1
    print('%d full chunks, 1 in %d sampled' % (seen, every))
    print()
    for biome in sorted(total):
        n = total[biome]
        print('%s  (%d chunks)' % (biome, n))
        bars = []
        for y in range(-4, 20):
            share = rock[biome][y] / n if n else 0.0
            if share >= 0.01:
                bars.append('Y%+4d..%+4d %5.1f%%' % (y * 16, y * 16 + 15, share * 100))
        print('   ' + ('  '.join(bars) if bars else 'no solid block in any section'))
        floor = min((y for y in rock[biome] if rock[biome][y] / n >= 0.10), default=None)
        print('   lowest section holding rock in >=10%% of chunks: %s'
              % ('Y %d..%d' % (floor * 16, floor * 16 + 15) if floor is not None else 'none'))
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
