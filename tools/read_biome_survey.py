"""Read `run_server.py --survey` consoles and report biome reachability.

    python tools/read_biome_survey.py server/console-A.log server/console-B.log ...
    python tools/read_biome_survey.py --all          # every console holding a survey

The question this answers, asked 2026-09-08: are all of our biomes within a reasonable
distance of one day's travel, excluding the Void biomes which need flight?

WHY SEVERAL ORIGINS AND SEVERAL SEEDS. One `locate biome` call is one sample of a noisy field.
A biome 300 blocks from spawn on one seed and 5,000 blocks away from a point 3 km east is not
reliably within a day's walk, and a single probe from the origin would have called it fine. The
survey probes a spread of origins per world; pass several consoles to pool several seeds.

The number that matters is the WORST case, not the mean: a player standing anywhere should be
able to reach every biome. `not found` counts as worse than any distance, and is reported
separately because it is a different kind of failure.
"""
import argparse
import glob
import os
import re
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONSOLE_GLOB = os.path.join(ROOT, 'server', 'console-*.log')

FOUND = re.compile(r'The nearest ([\w:]+) is at \[(-?\d+), (-?\d+), (-?\d+)\] \((\d+) blocks away\)')
MISSING = re.compile(r'Could not find a biome of type "([\w:]+)" within reasonable distance')
ORIGIN = re.compile(r'--- survey origin (-?\d+) (-?\d+) ---')

# One Minecraft day is 20 real minutes. Sprinting is 5.6 blocks/s, so a full day of sprinting is
# about 6,700 blocks -- call it 3,000 out and back with time to look around. That is the budget
# the target below comes from; it is a design target, not a physical limit.
DAY_TRAVEL = 3000
GOOD = 2000


def read(path):
    """-> {biome: [distance or None, ...]}, one entry per origin probed."""
    out = {}
    origins = 0
    for line in open(path, encoding='utf-8', errors='replace'):
        if ORIGIN.search(line):
            origins += 1
            continue
        m = FOUND.search(line)
        if m:
            out.setdefault(m.group(1), []).append(int(m.group(5)))
            continue
        m = MISSING.search(line)
        if m:
            out.setdefault(m.group(1), []).append(None)
    return out, origins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('consoles', nargs='*')
    ap.add_argument('--all', action='store_true', help='every console containing a survey')
    a = ap.parse_args()

    paths = a.consoles
    if a.all or not paths:
        paths = [p for p in sorted(glob.glob(CONSOLE_GLOB))
                 if ORIGIN.search(open(p, encoding='utf-8', errors='replace').read())]
    if not paths:
        print('!! no survey consoles found; run tools/run_server.py --run --survey')
        return 2

    pooled, total_origins = {}, 0
    for p in paths:
        got, origins = read(p)
        total_origins += origins
        for b, ds in got.items():
            pooled.setdefault(b, []).extend(ds)

    void = sorted(b for b in pooled if b.split(':')[-1] in {
        'void_verge', 'starless_reach', 'shatterfields', 'prism_drift', 'rootfall',
        'sepulchral_reach'})
    land = sorted(b for b in pooled if b not in void)

    print(f'{len(paths)} world(s), {total_origins} origins probed, {len(pooled)} biomes\n')

    def table(names, label, gate):
        print(f'{label}')
        print(f'  {"biome":34s} {"probes":>6} {"median":>8} {"worst":>8} {"missing":>8}   verdict')
        worst_overall, failing = 0, []
        for b in names:
            ds = pooled[b]
            hits = [d for d in ds if d is not None]
            miss = len(ds) - len(hits)
            med = f'{statistics.median(hits):,.0f}' if hits else '-'
            wst = max(hits) if hits else None
            wtxt = f'{wst:,}' if wst is not None else '-'
            if miss:
                verdict = 'NOT FOUND'
            elif wst > DAY_TRAVEL:
                verdict = 'too far'
            elif wst > GOOD:
                verdict = 'marginal'
            else:
                verdict = 'ok'
            if gate and (miss or wst is None or wst > DAY_TRAVEL):
                failing.append(b)
            if gate and wst is not None:
                worst_overall = max(worst_overall, wst)
            print(f'  {b:34s} {len(ds):>6} {med:>8} {wtxt:>8} {miss:>8}   {verdict}')
        return worst_overall, failing

    worst, failing = table(land, 'LAND BIOMES -- these are the gate', gate=True)
    print()
    table(void, 'VOID BIOMES -- reached by flight, reported for information', gate=False)
    print()
    print(f'worst land-biome distance from any probed origin: {worst:,} blocks '
          f'(target <= {DAY_TRAVEL:,})')
    if failing:
        print(f'RESULT: {len(failing)} land biome(s) outside the target: '
              + ', '.join(failing))
        return 1
    print(f'RESULT: all {len(land)} land biomes within {DAY_TRAVEL:,} blocks of every origin')
    return 0


if __name__ == '__main__':
    sys.exit(main())
