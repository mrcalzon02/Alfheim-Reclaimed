"""Fresh-world natural discovery and actual creature-item runtime checks.

Never uses /place structure; keeps the current district exclusion policy intact.
Player saves and JourneyMap caches are not touched.
"""
import argparse
import json
from pathlib import Path
import run_server

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--world', default='validation-test-run-regressions-20261017')
    ap.add_argument('--seed', default='3536368297089363045')
    args = ap.parse_args()
    world = args.world
    assert world.startswith('validation-test-run-') and Path(world).name == world
    server = (ROOT / 'server').resolve()
    assert not (server / world).exists(), 'Use a fresh disposable world'
    for name in run_server.MIRROR:
        target = (server / name).resolve()
        assert target.is_relative_to(server) and target != server
    home = 'execute in mythicbotany:alfheim '
    commands = [(1, 'gamerule doMobSpawning false'), (0, 'difficulty hard'),
                (0, 'gamerule doDaylightCycle false'), (0, home + 'run time set midnight'),
                (0, home + 'run forceload add 480 480 495 495'),
                (4, home + 'positioned 488 220 488 run alfheim_enemies_audit items'),
                (1, home + 'positioned 488 220 488 run alfheim_society_audit'),
                (1, home + 'run fill 480 219 480 495 227 495 minecraft:stone'),
                (1, home + 'run fill 481 220 481 494 226 494 minecraft:air'),
                (1, home + 'positioned 488 220 488 run alfheim_monstrosities_audit')]
    # Discovery outside the deliberately protected spawn/origin area.
    for family in ('common_residential_quarter', 'production_district', 'relief_district'):
        commands.append((1, home + f'positioned 8000 100 8000 run locate structure alfheim:{family}'))
    commands += [(5, 'save-all flush'), (1, home + 'run forceload remove all'), (1, 'stop')]
    props = server / 'server.properties'
    original = props.read_bytes()
    try:
        code = run_server.run(args.seed, world, 8, commands, 300)
    finally:
        props.write_bytes(original)
    manifests = [json.loads(p.read_text()) for p in sorted(server.glob('manifest-*.json'))]
    manifest = next(m for m in reversed(manifests) if m.get('level_name') == world)
    log = (server / manifest['console']).read_text(encoding='utf-8', errors='replace')
    evidence = [line for line in log.splitlines() if any(token in line for token in
                ('ALFHEIM_ENEMY_ITEMS_', 'ALFHEIM_SOCIETY_', 'ALFHEIM_MONSTROSITIES_',
                 'nearest alfheim:', 'Could not find', 'unexpected error', 'Exception'))]
    checks = {marker: marker in log for marker in
              ('ALFHEIM_ENEMY_ITEMS_PASS', 'ALFHEIM_SOCIETY_PASS', 'ALFHEIM_MONSTROSITIES_PASS')}
    checks['natural_discovery'] = all(f'The nearest alfheim:{family} is at' in log for family in
                                    ('common_residential_quarter', 'production_district', 'relief_district'))
    report = dict(world=world, seed=manifest['seed'], console=manifest['console'], checks=checks,
                  status='PASS' if code == 0 and all(checks.values()) else 'PARTIAL_OR_FAILED',
                  exit_code=code, evidence=evidence, client_visual_review='pending')
    (ROOT / 'tools/test_run_runtime_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    assert code == 0
    for marker in ('ALFHEIM_ENEMY_ITEMS_PASS', 'ALFHEIM_SOCIETY_PASS', 'ALFHEIM_MONSTROSITIES_PASS'):
        assert marker in log, marker
    for family in ('common_residential_quarter', 'production_district', 'relief_district'):
        assert f'The nearest alfheim:{family} is at' in log, family


if __name__ == '__main__':
    main()
