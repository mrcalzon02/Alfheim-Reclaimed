"""Static acceptance for zombie habitat extensions and Infectious dimension gating."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    manifest = read(ROOT / 'tools/zombie_habitat_manifest.json')
    infectious_entries = [entry for entry in manifest['natural']
                          if entry['type'].startswith('infectious:')]
    expected_modifiers = sorted({entry['modifier'] for entry in infectious_entries})
    overrides = sorted(manifest['infectious_overrides'])
    assert overrides == expected_modifiers, \
        'every natural Infectious modifier must be overridden at its original resource path'
    for relative in overrides:
        body = read(ROOT / 'kubejs' / relative)
        assert body['type'] == 'forge:add_spawns', relative
        assert body['biomes'] == '#minecraft:is_overworld', relative
        spawners = body['spawners'] if isinstance(body['spawners'], list) else [body['spawners']]
        assert all(spawn['type'].startswith('infectious:') for spawn in spawners), relative
    assert not any(path.startswith('data/infectious/')
                   for path in manifest['extended_modifiers']), \
        'Infectious cannot be extended into Alfheim because its Java predicate rejects the dimension'
    stale_tags = list((ROOT / 'kubejs/data/alfheim/tags/worldgen/biome/zombie_habitats').glob('infectious_*.json'))
    assert not stale_tags, stale_tags
    print(f'PASS: {len(infectious_entries)} Infectious spawn entries in {len(overrides)} modifiers '
          'are constrained to Level.OVERWORLD; no invalid Alfheim pointers remain')


if __name__ == '__main__':
    main()
