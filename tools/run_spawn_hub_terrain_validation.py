"""Measure terrain relief around the generated Greatbole without changing pack worldgen.

This is a specialized wrapper around tools/run_server.py. It reuses the existing dedicated-server
harness and adds temporary marker probes around the baked hub anchor after the Greatbole has had
time to generate. Each probe is snapped with `execute positioned over world_surface`, then its NBT
is printed to the server console and the marker is removed.

The tool is diagnostic by design: SPAWN_HUB.md requires a terrain-suitability decision across the
whole footprint, but it does not yet define a numeric relief threshold. This script therefore
reports measured relief and missing evidence without inventing an admission rule. Pass/fail of the
terrain-fit design remains a separate decision until the generator implements a declared placement
or terrain-incorporation contract.

Usage from the pack root:

    python tools/run_spawn_hub_terrain_validation.py --run
    python tools/run_spawn_hub_terrain_validation.py --analyze server/console-YYYYMMDD-HHMMSS.log
    python tools/run_spawn_hub_terrain_validation.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_server  # noqa: E402

DIMENSION = 'mythicbotany:alfheim'
ANCHOR_SELECTOR = '@e[type=minecraft:marker,tag=alfheim_hub_baked,limit=1]'
COMMON_TAG = 'alfheim_terrain_probe'

# Two rings on purpose. The inner ring is close enough to expose abrupt cliff transitions around
# the monument; the outer ring shows whether the hub sits in a broader slope rather than on a
# small local shelf. These are diagnostics, not acceptance thresholds.
OFFSETS = {
    'r40_n': (0, -40), 'r40_ne': (28, -28), 'r40_e': (40, 0), 'r40_se': (28, 28),
    'r40_s': (0, 40), 'r40_sw': (-28, 28), 'r40_w': (-40, 0), 'r40_nw': (-28, -28),
    'r72_n': (0, -72), 'r72_ne': (51, -51), 'r72_e': (72, 0), 'r72_se': (51, 51),
    'r72_s': (0, 72), 'r72_sw': (-51, 51), 'r72_w': (-72, 0), 'r72_nw': (-51, -51),
}

TAG_RE = re.compile(r'alfheim_terrain_probe_([a-z0-9_]+)')
POS_RE = re.compile(
    r'Pos\s*:\s*\[\s*(-?\d+(?:\.\d+)?)[dDfF]?,\s*'
    r'(-?\d+(?:\.\d+)?)[dDfF]?,\s*(-?\d+(?:\.\d+)?)[dDfF]?\s*\]'
)


def probe_tag(name: str) -> str:
    return f'{COMMON_TAG}_{name}'


def build_probe_commands(delay: int = 1):
    commands = [
        (delay, f'execute in {DIMENSION} run kill '
                f'@e[type=minecraft:marker,tag={COMMON_TAG}]')
    ]
    for name, (dx, dz) in OFFSETS.items():
        tag = probe_tag(name)
        commands.append((delay,
            f'execute in {DIMENSION} as {ANCHOR_SELECTOR} at @s '
            f'positioned ~{dx} ~ ~{dz} positioned over world_surface run summon '
            f'minecraft:marker ~ ~ ~ {{Tags:["{COMMON_TAG}","{tag}"]}}'))
        # Full NBT is intentional: the output line carries both the unique tag and Pos, making
        # console parsing robust without relying on command echo order.
        commands.append((delay,
            f'execute in {DIMENSION} run data get entity '
            f'@e[type=minecraft:marker,tag={tag},limit=1]'))
    commands.append((delay, f'execute in {DIMENSION} run kill '
                            f'@e[type=minecraft:marker,tag={COMMON_TAG}]'))
    return commands


def commands_with_probes():
    """Insert probes before save/stop while preserving the authoritative harness sequence."""
    base = list(run_server.DEFAULT_COMMANDS)
    insert_at = next((i for i, (_, cmd) in enumerate(base) if cmd == 'save-all flush'), len(base))
    return base[:insert_at] + build_probe_commands() + base[insert_at:]


def parse_console(text: str):
    samples = {}
    duplicates = defaultdict(int)
    malformed = []
    for line in text.splitlines():
        tag_m = TAG_RE.search(line)
        if not tag_m:
            continue
        name = tag_m.group(1)
        if name not in OFFSETS:
            continue
        pos_m = POS_RE.search(line)
        if not pos_m:
            malformed.append(name)
            continue
        pos = tuple(float(pos_m.group(i)) for i in range(1, 4))
        duplicates[name] += 1
        samples[name] = pos
    return samples, duplicates, malformed


def report(samples, duplicates, malformed):
    problems = []
    expected = set(OFFSETS)
    missing = sorted(expected - set(samples))
    if missing:
        problems.append(f'missing {len(missing)} terrain probe(s): {", ".join(missing)}')
    dup = sorted(name for name, count in duplicates.items() if count > 1)
    if dup:
        problems.append(f'duplicate terrain probe output: {", ".join(dup)}')
    if malformed:
        problems.append(f'malformed terrain probe output: {", ".join(sorted(set(malformed)))}')

    rings = {}
    for prefix in ('r40_', 'r72_'):
        ys = [pos[1] for name, pos in samples.items() if name.startswith(prefix)]
        if ys:
            rings[prefix[:-1]] = {
                'samples': len(ys),
                'min_y': min(ys),
                'max_y': max(ys),
                'relief': max(ys) - min(ys),
            }

    return problems, rings


def analyze(path: str, json_out: str | None = None):
    text = open(path, encoding='utf-8', errors='replace').read()
    samples, duplicates, malformed = parse_console(text)
    problems, rings = report(samples, duplicates, malformed)

    print(f'terrain probes: {len(samples)}/{len(OFFSETS)}')
    for ring in ('r40', 'r72'):
        if ring in rings:
            r = rings[ring]
            print(f'  {ring}: n={r["samples"]}  minY={r["min_y"]:.1f}  '
                  f'maxY={r["max_y"]:.1f}  relief={r["relief"]:.1f}')
    for name in sorted(samples):
        x, y, z = samples[name]
        print(f'  {name:7} ({x:.1f}, {y:.1f}, {z:.1f})')
    for problem in problems:
        print(f'PROBLEM: {problem}')

    result = {
        'console': path,
        'dimension': DIMENSION,
        'anchor_selector': ANCHOR_SELECTOR,
        'diagnostic_only': True,
        'samples': {k: list(v) for k, v in sorted(samples.items())},
        'rings': rings,
        'problems': problems,
    }
    if json_out:
        with open(json_out, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
        print(f'report -> {json_out}')

    if problems:
        return 1
    print('DIAGNOSTIC COMPLETE: relief measured; no terrain-fit acceptance threshold asserted')
    return 0


def self_test():
    lines = []
    for i, name in enumerate(OFFSETS):
        x = i * 3.0
        y = 64.0 + (i % 5)
        z = i * -2.0
        lines.append(
            f'Marker has the following entity data: '
            f'{{Tags: ["{COMMON_TAG}", "{probe_tag(name)}"], '
            f'Pos: [{x}d, {y}d, {z}d]}}')
    text = '\n'.join(lines)
    samples, duplicates, malformed = parse_console(text)
    problems, rings = report(samples, duplicates, malformed)
    assert not problems, problems
    assert len(samples) == len(OFFSETS)
    assert rings['r40']['samples'] == 8 and rings['r72']['samples'] == 8

    # Missing evidence must fail rather than silently shrinking the sample.
    samples2, duplicates2, malformed2 = parse_console('\n'.join(lines[:-1]))
    problems2, _ = report(samples2, duplicates2, malformed2)
    assert problems2 and 'missing 1 terrain probe' in problems2[0]

    # Command construction must remain additive to the established harness and clean up probes.
    cmds = build_probe_commands(delay=0)
    assert len(cmds) == 2 + 2 * len(OFFSETS)
    assert cmds[0][1].endswith(f'tag={COMMON_TAG}]')
    assert cmds[-1][1].endswith(f'tag={COMMON_TAG}]')
    assert sum('positioned over world_surface run summon' in c for _, c in cmds) == len(OFFSETS)

    print(f'self-test: {len(OFFSETS)} probes, two rings, missing-evidence guard PASS')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', action='store_true', help='run the existing headless harness with terrain probes')
    ap.add_argument('--analyze', metavar='CONSOLE', help='analyze an existing terrain-probe console log')
    ap.add_argument('--json', metavar='PATH', help='write analysis as JSON')
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--seed', default='alfheim')
    ap.add_argument('--level-name', default='validation')
    ap.add_argument('--heap', type=int, default=8)
    ap.add_argument('--timeout', type=int, default=1200)
    a = ap.parse_args()

    modes = sum(bool(x) for x in (a.run, a.analyze, a.self_test))
    if modes != 1:
        ap.error('choose exactly one of --run, --analyze, or --self-test')

    if a.self_test:
        return self_test()
    if a.analyze:
        return analyze(a.analyze, a.json)

    return run_server.run(a.seed, a.level_name, a.heap, commands_with_probes(), a.timeout)


if __name__ == '__main__':
    raise SystemExit(main())
