"""Check the field-review contract for Alfheim's third-party tree accents.

    python tools/check_tree_worldgen.py
"""
import glob
import json
import os
import sys
import zipfile

from gen_tree_worldgen import OUT, PLACED_OUT, PLACEMENTS


FORBIDDEN_BIOMES = {
    'alfheim:alfheim_ocean',
    'alfheim:void_verge',
    'alfheim:scorchfell',
    'alfheim:prism_drift',
    'alfheim:rootfall',
    'alfheim:sepulchral_reach',
    'alfheim:shatterfields',
    'alfheim:starless_reach',
}


def feature_member(feature):
    namespace, path = feature.split(':', 1)
    return f'data/{namespace}/worldgen/placed_feature/{path}.json'


def installed_feature(feature):
    member = feature_member(feature)
    for jar_path in glob.glob(os.path.join('mods', '*.jar')):
        try:
            with zipfile.ZipFile(jar_path) as jar:
                if member in jar.namelist():
                    return os.path.basename(jar_path), json.loads(jar.read(member))
        except (OSError, zipfile.BadZipFile, ValueError):
            continue
    return None, None


def main():
    problems = []

    def fail(message):
        problems.append(message)
        print(f'  FAIL {message}')

    expected_files = {p['file'] for p in PLACEMENTS}
    actual_files = {
        os.path.basename(path)
        for path in glob.glob(os.path.join(OUT, 'zz_tree_*.json'))
    }
    if actual_files != expected_files:
        fail(f'generated modifier set is {sorted(actual_files)}, expected {sorted(expected_files)}')

    seen_features = set()
    for placement in PLACEMENTS:
        path = os.path.join(OUT, placement['file'])
        try:
            with open(path, encoding='utf-8') as f:
                doc = json.load(f)
        except (OSError, ValueError) as exc:
            fail(f'{path}: unreadable ({exc})')
            continue

        expected = {
            'type': 'forge:add_features',
            'biomes': placement['biomes'],
            'features': placement['feature'],
            'step': 'vegetal_decoration',
        }
        if doc != expected:
            fail(f'{path}: content differs from generator contract')

        forbidden = FORBIDDEN_BIOMES.intersection(placement['biomes'])
        if forbidden:
            fail(f'{path}: tree accents target forbidden biomes {sorted(forbidden)}')

        if placement['feature'] in seen_features:
            fail(f'{placement["feature"]}: assigned by more than one modifier')
        seen_features.add(placement['feature'])

        jar, source_doc = installed_feature(placement['source_feature'])
        if source_doc is None:
            fail(f'{placement["source_feature"]}: placed feature is absent from installed mods')
            continue

        local_id = placement['feature'].split(':', 1)[1]
        local_path = os.path.join(PLACED_OUT, f'{local_id}.json')
        try:
            with open(local_path, encoding='utf-8') as f:
                feature_doc = json.load(f)
        except (OSError, ValueError) as exc:
            fail(f'{local_path}: unreadable ({exc})')
            continue
        if feature_doc != source_doc:
            fail(f'{local_path}: no longer exactly mirrors {placement["source_feature"]} ({jar})')

        placement_types = [p.get('type') for p in feature_doc.get('placement', [])]
        if 'minecraft:biome' not in placement_types:
            fail(f'{placement["feature"]}: source feature lacks a biome filter ({jar})')
        if 'minecraft:surface_water_depth_filter' not in placement_types:
            fail(f'{placement["feature"]}: source feature lacks a dry-surface filter ({jar})')
        if 'minecraft:block_predicate_filter' not in placement_types:
            fail(f'{placement["feature"]}: source feature lacks a survival predicate ({jar})')

    giant_outputs = (
        glob.glob(os.path.join('kubejs', 'data', 'alfheim', 'worldgen', 'structure',
                               'giant*_landmark.json'))
        + glob.glob(os.path.join('kubejs', 'data', 'alfheim', 'worldgen', 'structure_set',
                                'giant*_landmark.json'))
        + glob.glob(os.path.join(OUT, '*giant*.json'))
    )
    if giant_outputs:
        fail(f'TaxTreeGiant placement must remain disabled: {giant_outputs}')

    print(f'\nAlfheim tree worldgen: {len(problems)} problem(s), '
          f'{len(PLACEMENTS)} sparse modifiers, 0 giant-tree placements')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
