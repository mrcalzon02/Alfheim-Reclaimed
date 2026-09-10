"""Measure the void debris belt as landforms rather than as a density function.

`check_void_surface_support` states what the void owes its structures: `last_watch` and
`starless_orrery` need a terminal landing of at least 1,800 solid blocks and 14x8x14, at a
support ratio of 0.86, inside continentalness -0.94..-0.925. Nothing measured whether the belt
actually supplies one, because the belt did not exist -- every debris biome generated as open
air until 2026-09-09.

This reads generated chunks and reports the belt as fragments: 4-connected patches of columns
that carry terrain above the basal guard. Three things it can answer that a density sweep
cannot, because all three are properties of a landform rather than of a point:

  CAN YOU STAND ON IT   the footprint distribution, and how many fragments clear the 14x14 a
                        terminal landing needs.
  DOES IT THIN OUTWARD  VOID_MARGINS.md's central invariant is that fragments get smaller and
                        rarer outward. Fragment area per biome is the direct test; the inner
                        belt should carry the mass and Starless Reach the last scraps.
  IS IT A ROAD          Shatterfields "must not form an accidental walkable road". One
                        fragment spanning the whole sampled region is that road.

    python tools/probe_void_fragments.py server/<world>/dimensions/mythicbotany/alfheim/region
"""
import argparse
import collections
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_terraces import chunks, unpack_bits, biome_at, MIN_Y  # noqa: E402

# Below this a column is the basal guard slab or nothing at all, not a fragment.
FLOOR = -54
VOID_BIOMES = (
    'alfheim:shatterfields', 'alfheim:prism_drift', 'alfheim:rootfall',
    'alfheim:sepulchral_reach', 'alfheim:starless_reach', 'alfheim:void_verge',
)
LANDING_SIDE = 14          # check_void_surface_support min_dimensions
LANDING_AREA = 14 * 14


def collect(region_dir):
    """(x, z) -> (surface Y, biome) for every column carrying terrain above the guard."""
    cells = {}
    for p in sorted(glob.glob(os.path.join(region_dir, '*.mca'))):
        for ch in chunks(p):
            if not ch:
                continue
            hm = (ch.get('Heightmaps') or {}).get('WORLD_SURFACE')
            secs = ch.get('sections') or []
            cx, cz = ch.get('xPos'), ch.get('zPos')
            if not hm or cx is None:
                continue
            vals = unpack_bits(hm, 9, 256)
            for idx in range(256):
                z, x = divmod(idx, 16)
                top = vals[idx] + MIN_Y - 1
                if top <= FLOOR:
                    continue
                bi = biome_at(secs, top, x, z)
                if bi in VOID_BIOMES:
                    cells[(cx * 16 + x, cz * 16 + z)] = (top, bi)
    return cells


def fragments(cells):
    """4-connected patches. Iterative flood fill: these can be large."""
    seen = set()
    out = []
    for start in cells:
        if start in seen:
            continue
        stack, patch = [start], []
        seen.add(start)
        while stack:
            x, z = stack.pop()
            patch.append((x, z))
            for nx, nz in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if (nx, nz) in cells and (nx, nz) not in seen:
                    seen.add((nx, nz))
                    stack.append((nx, nz))
        out.append(patch)
    return out


def largest_square(patch_set, cap=64):
    """Side of the largest axis-aligned solid square inside the patch (classic DP)."""
    if not patch_set:
        return 0
    xs = [p[0] for p in patch_set]; zs = [p[1] for p in patch_set]
    x0, z0 = min(xs), min(zs)
    W, H = max(xs) - x0 + 1, max(zs) - z0 + 1
    if W * H > 4_000_000:
        return -1                      # too large to score cheaply; report as unknown
    prev = [0] * (W + 1)
    best = 0
    for z in range(H):
        cur = [0] * (W + 1)
        for x in range(W):
            if (x + x0, z + z0) in patch_set:
                cur[x + 1] = min(prev[x + 1], cur[x], prev[x]) + 1
                best = max(best, cur[x + 1])
                if best >= cap:
                    return best
        prev = cur
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('region_dir')
    ap.add_argument('--min-area', type=int, default=4,
                    help='ignore patches smaller than this (single-block noise)')
    ap.add_argument('--near', metavar='X,Z,R',
                    help='restrict to one rim segment: blocks within R of (X, Z). The void '
                         'audit locates several sites thousands of blocks apart and generates '
                         'a patch at each, so a whole-world run reports other sites as '
                         '"islands 1,863 blocks out". VOID_MARGINS 5.7 asks for at least three '
                         'separated rim segments; this is how you look at one.')
    a = ap.parse_args()

    cells = collect(a.region_dir)
    if a.near:
        nx, nz, nr = (int(v) for v in a.near.split(','))
        cells = {c: v for c, v in cells.items()
                 if (c[0] - nx) ** 2 + (c[1] - nz) ** 2 <= nr * nr}
        print(f'restricted to {nr} blocks around ({nx}, {nz})')
    if not cells:
        print('no void columns with terrain found'); return 1
    patches = [p for p in fragments(cells) if len(p) >= a.min_area]
    print(f'void columns with terrain: {len(cells)}   fragments >= {a.min_area} columns: '
          f'{len(patches)}\n')

    # THE MAINLAND IS THE LARGEST CONNECTED PIECE, and everything else is an island. An
    # earlier version called a fragment "attached" when it merely contained a void_verge
    # column, which is a biome test rather than a connectivity test: as the belt broke up, its
    # separate landmasses kept their verge columns and went on being counted as attached. A
    # connected component is already the answer to "is this one landform"; the only question
    # left is which component is the shore you walked in from.
    main = max(patches, key=len)
    main_set = set(main)
    islands = [g for g in patches if g is not main]

    def summarise(label, group):
        if not group:
            print(f'{label:26s} {"none":>6}')
            return
        areas = sorted(len(g) for g in group)
        big = sum(1 for g in group
                  if len(g) >= LANDING_AREA and largest_square(set(g)) >= LANDING_SIDE)
        print(f'{label:26s} {len(group):6d} {sum(areas):9d} {areas[len(areas) // 2]:7d} '
              f'{areas[-1]:8d} {big:8d}')

    xs = [c[0] for c in main]; zs = [c[1] for c in main]
    print(f"{'':26s} {'pieces':>6} {'columns':>9} {'median':>7} {'largest':>8} {'>=14x14':>8}")
    summarise('mainland (1 piece)', [main])
    summarise('islands', islands)
    print(f'  mainland bbox {max(xs) - min(xs) + 1} x {max(zs) - min(zs) + 1} blocks')

    # Does the belt thin outward? Distance from the MAINLAND edge, which is what the player
    # crosses. VOID_MARGINS section 1: "Fragments become smaller and rarer outward. Their
    # disappearance is part of the landscape."
    if islands:
        edge = [c for c in main_set
                if any((c[0] + dx, c[1] + dz) not in main_set
                       for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        buckets = collections.defaultdict(list)
        for g in islands:
            cx = sum(c[0] for c in g) / len(g)
            cz = sum(c[1] for c in g) / len(g)
            d = min((cx - ax) ** 2 + (cz - az) ** 2 for ax, az in edge) ** 0.5
            buckets[min(int(d) // 24, 5)].append(len(g))
        print(f"\n{'distance from the mainland':28s} {'islands':>8} {'median area':>12} "
              f"{'largest':>8}")
        for k in sorted(buckets):
            areas = sorted(buckets[k])
            lo = k * 24
            label = f'{lo}-{lo + 23} blocks' if k < 5 else '120+ blocks'
            print(f'{label:28s} {len(areas):8d} {areas[len(areas) // 2]:12d} {areas[-1]:8d}')
        far = max(
            min((sum(c[0] for c in g) / len(g) - ax) ** 2
                + (sum(c[1] for c in g) / len(g) - az) ** 2 for ax, az in edge) ** 0.5
            for g in islands)
        print(f'furthest island from the mainland: {far:.0f} blocks')

    # Terminal landings: check_void_surface_support wants 1,800 solid blocks and 14x8x14 in
    # Starless Reach, inside continentalness -0.94..-0.925.
    terminal = [g for g in patches
                if collections.Counter(cells[c][1] for c in g).most_common(1)[0][0]
                == 'alfheim:starless_reach']
    print(f'\nStarless Reach fragments: {len(terminal)}'
          + (f', largest {max(len(g) for g in terminal)} columns' if terminal else ''))
    if not any(len(g) >= LANDING_AREA and largest_square(set(g)) >= LANDING_SIDE
               for g in terminal):
        print('  NO fragment there clears the 14x14 footprint last_watch and starless_orrery '
              'need')
    return 0


if __name__ == '__main__':
    sys.exit(main())
