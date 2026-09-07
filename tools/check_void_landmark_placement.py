"""Guard the additive Void landmark vertical-placement contract."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'tools' / 'void_landmarks_manifest.json'
STRUCTURE_DIR = ROOT / 'kubejs' / 'data' / 'alfheim' / 'worldgen' / 'structure'


def main():
    data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    placement = data['placement']
    assert placement['mode'] == 'absolute_void_space'
    assert placement['start_height'] == {'absolute': 0}
    assert placement.get('project_start_to_heightmap') is None
    assert placement['terrain_adaptation'] == 'none'
    assert placement['shared_structure_set'] is True

    landmark_ids = ('void_floating_geode', 'void_astral_tower', 'void_ley_focus')
    checked = 0
    for sid in landmark_ids:
        path = STRUCTURE_DIR / f'{sid}.json'
        if not path.exists():
            continue
        obj = json.loads(path.read_text(encoding='utf-8'))
        assert obj['start_height'] == {'absolute': 0}, f'{sid}: wrong start height'
        assert 'project_start_to_heightmap' not in obj, f'{sid}: heightmap projection forbidden'
        assert obj['terrain_adaptation'] == 'none', f'{sid}: terrain adaptation must be none'
        checked += 1

    print(f'Void landmark placement contract OK: absolute Y=0, no heightmap projection; {checked} shipping registrations checked')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
