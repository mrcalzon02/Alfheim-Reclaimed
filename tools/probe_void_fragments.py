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
    a = ap.parse_args()

    cells = collect(a.region_dir)
    if not cells:
        print('no void columns with terrain found'); return 1
    patches = [p for p in fragments(cells) if len(p) >= a.min_area]
    print(f'void columns with terrain: {len(cells)}   fragments >= {a.min_area} columns: '
          f'{len(patches)}\n')

    # ATTACHED OR DETACHED, which is the distinction VOID_MARGINS actually draws: "Attached
    # shelves give way to detached blocks, smaller fragments and finally empty space." Grouping
    # by majority biome instead hid the belt entirely -- the inner debris is CONNECTED to the
    # Verge shelf, so a flood fill merges the two and the verge's column count swallows it.
    attached, detached = [], []
    for patch in patches:
        if any(cells[c][1] == 'alfheim:void_verge' for c in patch):
            attached.append(patch)
        else:
            detached.append(patch)

    def summarise(label, group):
        if not group:
            print(f'{label:24s} none')
            return
        areas = sorted(len(g) for g in group)
        big = sum(1 for g in group
                  if len(g) >= LANDING_AREA and largest_square(set(g)) >= LANDING_SIDE)
        print(f'{label:24s} {len(group):6d} {sum(areas):9d} {areas[len(areas) // 2]:7d} '
              f'{areas[-1]:8d} {big:8d}')

    print(f"{'':24s} {'frags':>6} {'columns':>9} {'median':>7} {'largest':>8} {'>=14x14':>8}")
    summarise('attached to the Verge', attached)
    summarise('detached fragments', detached)

    # Does the belt actually thin outward? Distance from the nearest attached landmass is the
    # honest proxy: continentalness is not stored in the chunk, but "how far from solid ground"
    # is exactly what the player experiences.
    if attached and detached:
        anchor = set()
        for g in attached:
            anchor.update(g)
        buckets = collections.defaultdict(list)
        for g in detached:
            cx = sum(c[0] for c in g) / len(g)
            cz = sum(c[1] for c in g) / len(g)
            best = min(((cx - ax) ** 2 + (cz - az) ** 2) for ax, az in anchor)
            d = int(best ** 0.5)
            buckets[min(d // 32, 6)].append(len(g))
        print(f"\n{'distance from solid ground':30s} {'frags':>6} {'median area':>12} "
              f"{'largest':>8}")
        for k in sorted(buckets):
            areas = sorted(buckets[k])
            lo = k * 32
            label = f'{lo}-{lo + 31} blocks' if k < 6 else '192+ blocks'
            print(f'{label:30s} {len(areas):6d} {areas[len(areas) // 2]:12d} {areas[-1]:8d}')

    # Terminal landings: check_void_surface_support wants 1,800 solid blocks and 14x8x14 in
    # Starless Reach. Report whether any fragment there could host one.
    terminal = [g for g in patches
                if collections.Counter(cells[c][1] for c in g).most_common(1)[0][0]
                == 'alfheim:starless_reach']
    print(f'\nStarless Reach fragments: {len(terminal)}'
          + (f', largest {max(len(g) for g in terminal)} columns' if terminal else ''))
    if not any(len(g) >= LANDING_AREA and largest_square(set(g)) >= LANDING_SIDE
               for g in terminal):
        print('  NO fragment there clears the 14x14 footprint last_watch and starless_orrery '
              'need\n  (check_void_surface_support: 1,800 solid blocks, 14x8x14, '
              'continentalness -0.94..-0.925)')

    biggest = max(patches, key=len)
    xs = [c[0] for c in biggest]; zs = [c[1] for c in biggest]
    print(f'\nlargest fragment overall: {len(biggest)} columns, bbox '
          f'{max(xs) - min(xs) + 1} x {max(zs) - min(zs) + 1} blocks '
          f'-- one fragment spanning the whole sampled region would be the '
          f'"accidental walkable road" VOID_MARGINS warns against')
    return 0


if __name__ == '__main__':
    sys.exit(main())
