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
    radius = int(one(r'const\s+HUB_RADIUS\s*=\s*(\d+)', 'HUB_RADIUS'))
    blocks = [(0, 0), (radius, radius), (-radius, radius),
              (radius, -radius), (-radius, -radius)]
    chunks = [(x >> 4, z >> 4) for x, z in blocks]
    return dimension, team, radius, chunks


def latest_console():
    paths = glob.glob(CONSOLE_GLOB)
    return max(paths, key=os.path.getmtime) if paths else None


def validate_text(text, dimension, team, chunks):
    """Return human-readable failures for missing/unowned FTB Chunks read-back probes."""
    problems = []
    for cx, cz in chunks:
        location = f'Location: {dimension} [{cx}, {cz}]'
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
            out.append(f'[Server thread/INFO] Location: {dimension} [{cx}, {cz}]')
            out.append(f'[Server thread/INFO] Owner: {owner} / 0123456789abcdef')
            out.append('[Server thread/INFO] Force-loaded: false')
        return '\n'.join(out)

    cases = [
        ('complete', claimed(), 0),
        ('wrong owner', claimed('somebody_else'), 5),
        ('missing corner', claimed(omit=(-12, -12)), 1),
        ('unclaimed centre', claimed().replace(
            f'Location: {dimension} [0, 0]\n[Server thread/INFO] Owner: {team} / 0123456789abcdef',
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
        dimension, team, radius, chunks = protection_contract()
    except (OSError, ValueError) as exc:
        print(f'!! {exc}')
        return 2

    console = a.console or latest_console()
    if not console or not os.path.isfile(console):
        print('!! no server console log found; run tools/run_server.py --run first')
        return 2

    text = open(console, encoding='utf-8', errors='replace').read()
    problems = validate_text(text, dimension, team, chunks)
    print(f'claim contract: team={team} dimension={dimension} radius={radius} blocks')
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
