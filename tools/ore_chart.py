"""Render the vertical distribution of every ore Alfheim generates.

Asked for by the user 2026-09-04:

    "I'd like to get some kind of ore distribution chart for our different custom [ores] and
    ensure that they are distributed throughout the world height proportionately so that they
    each like vanilla ores have spawning ranges that they are most likely to spawn in and have
    upper and lower extents."

Read from the PLACED FEATURES, not from the manifests. The manifests say what was intended; the
placed features are what the game loads, and this whole session has been a lesson in the
difference. If a bloom's band is edited by hand the chart shows the edit.

    python tools/ore_chart.py
    python tools/ore_chart.py --vanilla     # overlay vanilla's ores for comparison
"""
import argparse
import glob
import json
import os
import zipfile

DATA = os.path.join('kubejs', 'data', 'alfheim', 'worldgen', 'placed_feature')
CLIENT_JAR = (r'C:\Users\Admin\curseforge\minecraft\Install\versions'
              r'\1.20.1\1.20.1.jar')

# Alfheim's build height, from its dimension type: min_y -64, height 384.
Y_MIN, Y_MAX = -64, 320
ROWS = 32                       # each row is 12 blocks
SURFACE = 72                    # nominal Alfheim ground level, for charting
                                # surface-relative features against absolute ones
BLOCKS_PER_ROW = (Y_MAX - Y_MIN) / ROWS


def anchor(v, default):
    """A vanilla VerticalAnchor as an absolute y."""
    if v is None:
        return default
    if isinstance(v, (int, float)):
        return int(v)
    if 'absolute' in v:
        return int(v['absolute'])
    if 'above_bottom' in v:
        return Y_MIN + int(v['above_bottom'])
    if 'below_top' in v:
        return Y_MAX + int(v['below_top'])
    return default


def read_band(doc):
    """(low, high, kind, count) for one placed feature, or None if it has no height range."""
    lo = hi = None
    kind = 'uniform'
    count = None
    for st in doc.get('placement', []):
        t = st.get('type', '')
        if t.endswith(':count'):
            c = st.get('count')
            count = c if isinstance(c, int) else c.get('value', c) if isinstance(c, dict) else c
        elif t.endswith(':rarity_filter'):
            count = f"1/{st.get('chance')}"
        elif t.endswith(':height_range'):
            h = st.get('height', {})
            kind = h.get('type', '').split(':')[-1] or 'uniform'
            lo = anchor(h.get('min_inclusive'), Y_MIN)
            hi = anchor(h.get('max_inclusive'), Y_MAX)
    if lo is None:
        # Surface-relative features -- the geodes -- have no height_range at all. They use
        # heightmap + random_offset, so their depth is "N blocks under wherever the ground is"
        # rather than an absolute band. Charted against a nominal surface so they can be
        # compared with the blooms at a glance; the real depth follows the terrain.
        off = 0
        anchored = False
        for st in doc.get('placement', []):
            t = st.get('type', '')
            if t.endswith(':heightmap'):
                anchored = True
            elif t.endswith(':random_offset'):
                y = st.get('y_spread', 0)
                if isinstance(y, (int, float)):
                    off += int(y)
                elif isinstance(y, dict):
                    v = y.get('value', {})
                    off += (int(v.get('min_inclusive', 0)) + int(v.get('max_inclusive', 0))) // 2
        if not anchored:
            return None
        return SURFACE + off - 8, SURFACE + off + 8, 'surface', count
    return lo, hi, kind, count


def ours():
    out = {}
    for p in sorted(glob.glob(os.path.join(DATA, '*.json'))):
        name = os.path.basename(p)[:-5]
        if not (name.startswith('bloom_') or name.startswith('geode_')):
            continue
        if name.endswith('_marker'):
            continue
        band = read_band(json.load(open(p, encoding='utf-8')))
        if band:
            out[name] = band
    return out


def vanilla():
    out = {}
    if not os.path.exists(CLIENT_JAR):
        return out
    with zipfile.ZipFile(CLIENT_JAR) as z:
        for n in z.namelist():
            if '/placed_feature/ore_' not in n or not n.endswith('.json'):
                continue
            name = os.path.basename(n)[:-5]
            try:
                band = read_band(json.loads(z.read(n)))
            except Exception:
                continue
            if band:
                out[name] = band
    return out


def row_of(y):
    return int((Y_MAX - y) / BLOCKS_PER_ROW)


def chart(bands, title):
    print(f'\n{title}')
    print('=' * 78)
    names = sorted(bands)
    width = max((len(n) for n in names), default=0)

    for name in names:
        lo, hi, kind, count = bands[name]
        peak = (lo + hi) // 2 if kind == 'trapezoid' else None
        bar_lo, bar_hi = min(lo, hi), max(lo, hi)
        # 60-column band, one char per (Y_MAX-Y_MIN)/60 blocks
        cols = 56
        span = Y_MAX - Y_MIN
        c0 = int((bar_lo - Y_MIN) / span * cols)
        c1 = int((bar_hi - Y_MIN) / span * cols)
        row = [' '] * cols
        for i in range(c0, max(c0 + 1, min(c1, cols))):
            row[i] = '-'
        if peak is not None:
            pc = min(cols - 1, max(0, int((peak - Y_MIN) / span * cols)))
            row[pc] = '#'
        shape = 'peak' if kind == 'trapezoid' else 'flat'
        print(f'  {name:{width}}  {"".join(row)}  y{bar_lo:>5}..{bar_hi:<4} '
              f'{shape}  n={count}')

    print(f'  {"":{width}}  ' + ''.join(
        '|' if i % 7 == 0 else ' ' for i in range(56)))
    ticks = ''
    for i in range(0, 56, 7):
        ticks += f'{int(Y_MIN + i / 56 * (Y_MAX - Y_MIN)):<7}'
    print(f'  {"":{width}}  {ticks}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vanilla', action='store_true')
    a = ap.parse_args()

    o = ours()
    chart(o, f'ALFHEIM ORE DISTRIBUTION  ({len(o)} features)   # = most likely depth')

    flat = sorted(n for n, (lo, hi, k, c) in o.items() if k not in ('trapezoid', 'surface'))
    if flat:
        print(f'\n  {len(flat)} feature(s) still use a FLAT distribution, so they have no '
              'depth worth learning:')
        for n in flat:
            print(f'    {n}')

    if a.vanilla:
        chart(vanilla(), 'VANILLA, for comparison')

    print()
    covered = set()
    for lo, hi, _, _ in o.values():
        covered |= set(range(min(lo, hi), max(lo, hi) + 1))
    total = Y_MAX - Y_MIN
    print(f'vertical coverage: y{min(covered)}..{max(covered)} '
          f'({len(covered)} of {total} blocks, {100 * len(covered) // total}%)')
    gaps = []
    y = Y_MIN
    while y <= Y_MAX:
        if y not in covered:
            start = y
            while y <= Y_MAX and y not in covered:
                y += 1
            if y - start >= 16:
                gaps.append((start, y - 1))
        else:
            y += 1
    if gaps:
        print('bands with NO ore of any kind:')
        for lo, hi in gaps:
            print(f'   y{lo} .. y{hi}   ({hi - lo + 1} blocks)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
