"""Validate the FTB Chunks ownership read-back for the Alfheim spawn hub.

This consumes the per-run console written by tools/run_server.py.  It does not infer success from
`claim_as` return values: it requires `ftbchunks info` to report the expected owner at the centre
and all four corners of the generated hub protection envelope.

    python tools/check_spawn_hub_claim.py
    python tools/check_spawn_hub_claim.py server/console-YYYYMMDD-HHMMSS.log
    python tools/check_spawn_hub_claim.py --self-test
"""
import argparse
import glob
import os
import re
import sys

SCRIPT = os.path.join('kubejs', 'server_scripts', '04_spawn_hub.js')
CONSOLE_GLOB = os.path.join('server', 'console-*.log')


def protection_contract(path=SCRIPT):
    """Read the shipping protection script so validator expectations cannot drift from it."""
    text = open(path, encoding='utf-8').read()

    def one(pattern, label):
        match = re.search(pattern, text)
        if not match:
            raise ValueError(f'{path}: cannot read {label} from generated protection script')
        return match.group(1)

    dimension = one(r"const\s+HUB_DIMENSION\s*=\s*'([^']+)'", 'HUB_DIMENSION')
    team = one(r"const\s+HUB_FTB_TEAM\s*=\s*'([^']+)'", 'HUB_FTB_TEAM')
    # The envelope became an explicit rectangle on 2026-09-07: the complex is not centred on
    # the tree, so a radius both over-claimed to the south and under-claimed to the north.
    bounds = tuple(int(one(rf'const\s+{name}\s*=\s*(-?\d+)', name)) for name in
                   ('HUB_MIN_X', 'HUB_MAX_X', 'HUB_MIN_Z', 'HUB_MAX_Z'))
    min_x, max_x, min_z, max_z = bounds
    blocks = [((min_x + max_x) // 2, (min_z + max_z) // 2),
              (min_x, min_z), (max_x, min_z), (min_x, max_z), (max_x, max_z)]
    chunks = [(x >> 4, z >> 4) for x, z in blocks]
    return dimension, team, bounds, chunks


def latest_console():
    paths = glob.glob(CONSOLE_GLOB)
    return max(paths, key=os.path.getmtime) if paths else None


def location_line(dimension, cx, cz):
    """How FTB Chunks actually prints a chunk address.

    It is `Location: [mythicbotany:alfheim:-1:-4]` -- dimension and both chunk coordinates
    colon-joined inside one bracket. This validator was written expecting
    `Location: mythicbotany:alfheim [-1, -4]`, which no FTB Chunks build emits, so every probe
    read as "no read-back in console" and the check could only ever fail. Caught 2026-09-07,
    when all five probes in fact reported `Owner: alfheim_hub`.
    """
    return f'Location: [{dimension}:{cx}:{cz}]'


def validate_text(text, dimension, team, chunks):
    """Return human-readable failures for missing/unowned FTB Chunks read-back probes."""
    problems = []
    for cx, cz in chunks:
        location = location_line(dimension, cx, cz)
        start = text.find(location)
        if start < 0:
            problems.append(f'{location}: no `ftbchunks info` read-back in console')
            continue

        tail = text[start + len(location):]
        next_location = tail.find('Location:')
        block = tail if next_location < 0 else tail[:next_location]
        owner = re.search(r'Owner:\s*([^\r\n/]+)', block)
        if not owner:
            problems.append(f'{location}: claim owner was not reported')
            continue
        actual = owner.group(1).strip()
        if actual != team:
            problems.append(f'{location}: owner is {actual!r}, expected {team!r}')
    return problems


def self_test():
    dimension = 'mythicbotany:alfheim'
    team = 'alfheim_hub'
    chunks = [(0, 0), (12, 12), (-12, 12), (12, -12), (-12, -12)]

    def claimed(owner=team, omit=None):
        out = []
        for pos in chunks:
            if pos == omit:
                continue
            cx, cz = pos
            out.append(f'[Server thread/INFO] {location_line(dimension, cx, cz)}')
            out.append(f'[Server thread/INFO] Owner: {owner} / 0123456789abcdef')
            out.append('[Server thread/INFO] Force-loaded: false')
        return '\n'.join(out)

    cases = [
        ('complete', claimed(), 0),
        ('wrong owner', claimed('somebody_else'), 5),
        ('missing corner', claimed(omit=(-12, -12)), 1),
        ('unclaimed centre', claimed().replace(
            f'{location_line(dimension, 0, 0)}\n[Server thread/INFO] Owner: {team} '
            f'/ 0123456789abcdef',
            'Chunk not claimed', 1), 1),
    ]
    bad = 0
    for name, text, expected in cases:
        got = len(validate_text(text, dimension, team, chunks))
        if got != expected:
            print(f'  FAIL  {name}: expected {expected} problem(s), got {got}')
            bad += 1
        else:
            print(f'  OK    {name}: {got} problem(s)')
    print(f'RESULT: {bad} self-test failure(s)')
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('console', nargs='?', help='console log; defaults to newest server/console-*.log')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    try:
        dimension, team, bounds, chunks = protection_contract()
    except (OSError, ValueError) as exc:
        print(f'!! {exc}')
        return 2

    console = a.console or latest_console()
    if not console or not os.path.isfile(console):
        print('!! no server console log found; run tools/run_server.py --run first')
        return 2

    text = open(console, encoding='utf-8', errors='replace').read()
    problems = validate_text(text, dimension, team, chunks)
    print(f'claim contract: team={team} dimension={dimension} envelope X {bounds[0]}..{bounds[1]} Z {bounds[2]}..{bounds[3]} ({len(chunks)} probes)')
    print(f'console: {console}')
    for problem in problems:
        print(f'  C1  {problem}')
    if problems:
        print(f'RESULT: {len(problems)} problem(s) — hub claim is NOT runtime accepted')
        return 1
    print(f'RESULT: 0 problems — {len(chunks)}/{len(chunks)} ownership probes report {team}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
