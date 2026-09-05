"""Machine-check Midgard biome ownership under the current cw-only TerraBlender contract.

This consumes the per-run console written by tools/run_server.py and checks the same six Midgard
probes already emitted by that harness. Static config is checked first so runtime evidence cannot
be interpreted against a stale mode.

    python tools/check_midgard_biomes.py
    python tools/check_midgard_biomes.py server/console-YYYYMMDD-HHMMSS.log
    python tools/check_midgard_biomes.py --self-test
"""
import argparse
import glob
import os
import re
import sys

TERRABLENDER = os.path.join('config', 'terrablender.toml')
RU = os.path.join('config', 'regions_unexplored', 'ru-common.toml')
CW = os.path.join('config', 'continuityworks-biomes-common.toml')
RUN_SERVER = os.path.join('tools', 'run_server.py')
CONSOLE_GLOB = os.path.join('server', 'console-*.log')

CW_EXPECTED = (
    'continuityworks_biomes:temperate_grove',
    'continuityworks_biomes:misty_highlands',
    'continuityworks_biomes:amber_forest',
    'continuityworks_biomes:neon_city_grid',
)
ABSENT_EXPECTED = (
    'regions_unexplored:alpha_grove',
    'minecraft:plains',
)
ALL_PROBES = CW_EXPECTED + ABSENT_EXPECTED


def read_int(path, key):
    text = open(path, encoding='utf-8').read()
    match = re.search(r'(?m)^\s*%s\s*=\s*(-?\d+)\s*$' % re.escape(key), text)
    if not match:
        raise ValueError(f'{path}: cannot read {key}')
    return int(match.group(1))


def static_contract():
    """Return problems if current config or harness does not match the cw-only acceptance contract."""
    problems = []
    try:
        actual = {
            'vanilla_overworld_region_weight': read_int(TERRABLENDER, 'vanilla_overworld_region_weight'),
            'primary_region_weight': read_int(RU, 'primary_region_weight'),
            'secondary_region_weight': read_int(RU, 'secondary_region_weight'),
            'rare_region_weight': read_int(RU, 'rare_region_weight'),
            'regionWeight': read_int(CW, 'regionWeight'),
        }
    except (OSError, ValueError) as exc:
        return [str(exc)]

    expected = {
        'vanilla_overworld_region_weight': 0,
        'primary_region_weight': 0,
        'secondary_region_weight': 0,
        'rare_region_weight': 0,
        'regionWeight': 20,
    }
    for key, wanted in expected.items():
        if actual[key] != wanted:
            problems.append(f'{key}={actual[key]}, expected {wanted} for cw-only Midgard')

    try:
        harness = open(RUN_SERVER, encoding='utf-8').read()
    except OSError as exc:
        problems.append(str(exc))
        return problems
    for biome in ALL_PROBES:
        command = f'locate biome {biome}'
        if command not in harness:
            problems.append(f'{RUN_SERVER}: missing probe `{command}`')
    return problems


def latest_console():
    paths = glob.glob(CONSOLE_GLOB)
    return max(paths, key=os.path.getmtime) if paths else None


def outcome(text, biome):
    """Classify the terminal output for one locate-biome command."""
    if re.search(rf'The nearest\s+{re.escape(biome)}\s+is at', text):
        return 'found'
    # 1.20.1 emits this wording for a valid biome that is not reachable within the search radius.
    if re.search(rf'Could not find a biome of type\s+"?{re.escape(biome)}"?\s+within reasonable distance', text):
        return 'absent'
    if re.search(rf'(There is no biome|Unknown biome).*{re.escape(biome)}', text, re.I):
        return 'invalid'
    return 'missing'


def validate_text(text):
    problems = []
    for biome in CW_EXPECTED:
        got = outcome(text, biome)
        if got != 'found':
            problems.append(f'{biome}: expected reachable Continuity Works biome, got {got}')
    for biome in ABSENT_EXPECTED:
        got = outcome(text, biome)
        if got != 'absent':
            problems.append(f'{biome}: expected absent under cw-only config, got {got}')
    return problems


def self_test():
    def line(biome, state):
        if state == 'found':
            return f'The nearest {biome} is at [128, 80, -64] (143 blocks away)'
        if state == 'absent':
            return f'Could not find a biome of type "{biome}" within reasonable distance'
        if state == 'invalid':
            return f'There is no biome with type {biome}'
        return ''

    good = '\n'.join([line(b, 'found') for b in CW_EXPECTED]
                     + [line(b, 'absent') for b in ABSENT_EXPECTED])
    cases = [
        ('complete', good, 0),
        ('missing CW', good.replace(line(CW_EXPECTED[0], 'found'), ''), 1),
        ('vanilla leaked', good.replace(line('minecraft:plains', 'absent'),
                                        line('minecraft:plains', 'found')), 1),
        ('RU leaked', good.replace(line('regions_unexplored:alpha_grove', 'absent'),
                                   line('regions_unexplored:alpha_grove', 'found')), 1),
        ('invalid CW id', good.replace(line(CW_EXPECTED[-1], 'found'),
                                       line(CW_EXPECTED[-1], 'invalid')), 1),
    ]
    bad = 0
    for name, text, expected in cases:
        got = len(validate_text(text))
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

    contract = static_contract()
    for problem in contract:
        print(f'  M0  {problem}')
    if contract:
        print(f'RESULT: {len(contract)} static contract problem(s) — runtime result is not admissible')
        return 1

    console = a.console or latest_console()
    if not console or not os.path.isfile(console):
        print('!! no server console log found; run tools/run_server.py --run first')
        return 2

    text = open(console, encoding='utf-8', errors='replace').read()
    problems = validate_text(text)
    print('Midgard contract: cw-only (vanilla=0, RU=0/0/0, Continuity Works=20)')
    print(f'console: {console}')
    for problem in problems:
        print(f'  M1  {problem}')
    if problems:
        print(f'RESULT: {len(problems)} problem(s) — Midgard biome ownership is NOT runtime accepted')
        return 1
    print(f'RESULT: 0 problems — {len(CW_EXPECTED)}/{len(CW_EXPECTED)} CW probes reachable; '
          f'{len(ABSENT_EXPECTED)}/{len(ABSENT_EXPECTED)} excluded-biome probes absent')
    return 0


if __name__ == '__main__':
    sys.exit(main())
