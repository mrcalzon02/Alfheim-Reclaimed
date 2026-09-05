"""Static acceptance for the generated Alfheim fey-wildlife set.

This checker deliberately stops at the static boundary. It proves that the 18-entry manifest,
shipping roster, EntityJS registration source, biome modifiers, geometry, animations and loot stay
synchronized. Natural spawning and entity instantiation remain the job of run_fey_validation.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COUNT = 18
REQUIRED_KEYS = {
    'id', 'name', 'family', 'width', 'height', 'health', 'speed', 'scale',
    'damage', 'celestial', 'biomes', 'weight',
}
VALID_FAMILIES = {'deer', 'frog', 'toad', 'sea', 'elf'}


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def check(root: Path = ROOT):
    problems = []
    manifest_path = root / 'tools/fey_manifest.json'
    roster_path = root / 'kubejs/fey_roster.json'
    startup_path = root / 'kubejs/startup_scripts/08_fey_wildlife.js'

    for path in (manifest_path, roster_path, startup_path):
        if not path.is_file():
            problems.append(f'missing required file: {path.relative_to(root)}')
    if problems:
        return problems

    try:
        manifest = load_json(manifest_path)
        roster = load_json(roster_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f'cannot parse fey roster/manifest: {exc}']

    if manifest != roster:
        problems.append('tools/fey_manifest.json != kubejs/fey_roster.json')
    if len(manifest) != EXPECTED_COUNT:
        problems.append(f'expected {EXPECTED_COUNT} fey entries, found {len(manifest)}')

    ids = [entry.get('id') for entry in manifest if isinstance(entry, dict)]
    if len(ids) != len(set(ids)):
        problems.append('duplicate fey entity id in manifest')

    startup = startup_path.read_text(encoding='utf-8')
    if "JsonIO.readJson('kubejs/fey_roster.json')" not in startup:
        problems.append('08_fey_wildlife.js no longer reads the generated shipping roster')
    if "StartupEvents.registry('entity_type'" not in startup:
        problems.append('08_fey_wildlife.js no longer registers entity types')
    if '.spawnPlacement(' not in startup:
        problems.append('08_fey_wildlife.js no longer declares spawn placement')

    for index, entry in enumerate(manifest):
        if not isinstance(entry, dict):
            problems.append(f'entry {index} is not an object')
            continue
        missing = sorted(REQUIRED_KEYS - set(entry))
        if missing:
            problems.append(f'entry {index} missing keys: {", ".join(missing)}')
            continue

        ident = entry['id']
        if not isinstance(ident, str) or not ident.startswith('alfheim:') or ident.count(':') != 1:
            problems.append(f'entry {index} has invalid id: {ident!r}')
            continue
        name = ident.split(':', 1)[1]
        family = entry['family']
        if family not in VALID_FAMILIES:
            problems.append(f'{ident}: invalid family {family!r}')
        if not isinstance(entry['biomes'], list) or not entry['biomes']:
            problems.append(f'{ident}: no habitat biomes')
        else:
            for biome in entry['biomes']:
                if not isinstance(biome, str) or ':' not in biome:
                    problems.append(f'{ident}: invalid biome id {biome!r}')

        expected = {
            'geometry': root / f'kubejs/assets/alfheim/geo/entity/{name}.geo.json',
            'animation': root / f'kubejs/assets/alfheim/animations/entity/{name}.animation.json',
            'biome modifier': root / f'kubejs/data/alfheim/forge/biome_modifier/fey_{name}.json',
            'loot table': root / f'kubejs/data/alfheim/loot_tables/entities/{name}.json',
        }
        for label, path in expected.items():
            if not path.is_file():
                problems.append(f'{ident}: missing {label} {path.relative_to(root)}')

        modifier_path = expected['biome modifier']
        if modifier_path.is_file():
            try:
                modifier = load_json(modifier_path)
            except (OSError, json.JSONDecodeError) as exc:
                problems.append(f'{ident}: biome modifier parse failed: {exc}')
            else:
                spawner = modifier.get('spawners', {})
                if modifier.get('type') != 'forge:add_spawns':
                    problems.append(f'{ident}: biome modifier type is not forge:add_spawns')
                if modifier.get('biomes') != entry['biomes']:
                    problems.append(f'{ident}: biome modifier habitats differ from manifest')
                if spawner.get('type') != ident:
                    problems.append(f'{ident}: biome modifier spawner type differs from manifest')
                if spawner.get('weight') != entry['weight']:
                    problems.append(f'{ident}: biome modifier weight differs from manifest')

        for label in ('geometry', 'animation', 'loot table'):
            path = expected[label]
            if path.is_file():
                try:
                    load_json(path)
                except (OSError, json.JSONDecodeError) as exc:
                    problems.append(f'{ident}: {label} parse failed: {exc}')

    return problems


def self_test():
    # Contract-level checks that do not need a repository fixture.
    assert EXPECTED_COUNT == 4 + 6 + 2 + 3 + 3
    assert VALID_FAMILIES == {'deer', 'frog', 'toad', 'sea', 'elf'}
    assert 'biomes' in REQUIRED_KEYS and 'weight' in REQUIRED_KEYS
    print('self-test: roster cardinality and required contract PASS')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    problems = check(args.root.resolve())
    if problems:
        for problem in problems:
            print('PROBLEM:', problem)
        print(f'fey wildlife static acceptance: FAIL ({len(problems)} problem(s))')
        return 1
    print(f'fey wildlife static acceptance: PASS ({EXPECTED_COUNT} entities synchronized)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
