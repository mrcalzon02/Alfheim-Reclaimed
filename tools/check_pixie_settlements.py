"""Static acceptance checks for the seasonal pixie sky-island settlements."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402
from gen_pixie_settlements import CULTURES, NS, SKY_Y  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'kubejs', 'data', NS)
failures = []


def fail(code, message):
    failures.append(f'{code}: {message}')


def read_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as exc:
        fail('P1', f'{os.path.relpath(path, ROOT)} is not valid JSON: {exc}')
        return {}


def load_piece(path):
    try:
        _name, root = nbt.load(path)
        return root
    except Exception as exc:
        fail('P2', f'{os.path.relpath(path, ROOT)} is not valid structure NBT: {exc}')
        return {'size': [], 'palette': [], 'blocks': []}


def entries(piece):
    palette = piece.get('palette', [])
    out = []
    for block in piece.get('blocks', []):
        try:
            state = palette[int(block['state'])]
        except (IndexError, KeyError, TypeError, ValueError):
            fail('P3', f'invalid palette reference in block {block}')
            continue
        out.append((tuple(int(v) for v in block['pos']), state, block.get('nbt')))
    return out


def names(piece):
    return [state.get('Name') for _pos, state, _be in entries(piece)]


def jigsaws(piece):
    return [(pos, state, be) for pos, state, be in entries(piece)
            if state.get('Name') == 'minecraft:jigsaw']


def check_structure_data(kind, c):
    sid = f'pixie_{kind}_hamlet'
    structure = read_json(os.path.join(DATA, 'worldgen', 'structure', sid + '.json'))
    if structure.get('type') != 'minecraft:jigsaw':
        fail('P4', f'{sid}: not a jigsaw structure')
    if structure.get('biomes') != f'#{NS}:has_{sid}':
        fail('P4', f'{sid}: wrong biome tag {structure.get("biomes")}')
    if structure.get('terrain_adaptation') != 'none':
        fail('P4', f'{sid}: floating island must use terrain_adaptation none')
    if structure.get('start_height') != {'absolute': SKY_Y}:
        fail('P4', f'{sid}: start height is not fixed high-sky Y={SKY_Y}')
    if 'project_start_to_heightmap' in structure:
        fail('P4', f'{sid}: heightmap projection would pull the island onto terrain')
    if structure.get('size') != 1 or structure.get('max_distance_from_center', 999) > 128:
        fail('P4', f'{sid}: one-step jigsaw/depth-distance contract changed')

    tag = read_json(os.path.join(DATA, 'tags', 'worldgen', 'biome', f'has_{sid}.json'))
    if tag.get('replace') is not False or tag.get('values') != c['biomes']:
        fail('P5', f'{sid}: host biomes differ from the culture manifest')

    struct_set = read_json(os.path.join(DATA, 'worldgen', 'structure_set', sid + '.json'))
    placement = struct_set.get('placement', {})
    if placement.get('type') != 'minecraft:random_spread':
        fail('P6', f'{sid}: missing random-spread placement')
    if placement.get('spacing', 0) < 48 or placement.get('separation', 0) < 16:
        fail('P6', f'{sid}: placement is too dense for a rare skyline discovery')
    if placement.get('spacing', 0) <= placement.get('separation', 0):
        fail('P6', f'{sid}: invalid spacing/separation')
    return placement.get('salt')


def check_pools_and_pieces(kind, c):
    piece_dir = os.path.join(DATA, 'structures', 'pixie', kind)
    pool_dir = os.path.join(DATA, 'worldgen', 'template_pool', 'pixie', kind)
    required = ['core', 'centre', 'garden', 'tree'] + [f'house_{i}' for i in range(1, 5)]
    loaded = {}
    for name in required:
        path = os.path.join(piece_dir, name + '.nbt')
        if not os.path.isfile(path):
            fail('P7', f'{kind}: missing {name}.nbt')
            continue
        loaded[name] = load_piece(path)
        size = [int(v) for v in loaded[name].get('size', [])]
        if len(size) != 3 or any(v <= 0 or v > 48 for v in size):
            fail('P7', f'{kind}/{name}: invalid or uninspectable size {size}')

    pool_specs = {'start': ['core'], 'centre': ['centre'], 'garden': ['garden'],
                  'tree': ['tree'], 'houses': [f'house_{i}' for i in range(1, 5)]}
    prefix = f'{NS}:pixie/{kind}'
    for pool_name, member_names in pool_specs.items():
        pool = read_json(os.path.join(pool_dir, pool_name + '.json'))
        if pool.get('name') != f'{prefix}/{pool_name}':
            fail('P8', f'{kind}/{pool_name}: pool name is inconsistent')
        locations = [e.get('element', {}).get('location') for e in pool.get('elements', [])]
        expected = [f'{prefix}/{name}' for name in member_names]
        if locations != expected:
            fail('P8', f'{kind}/{pool_name}: members {locations}, expected {expected}')
        if pool.get('fallback') != 'minecraft:empty':
            fail('P8', f'{kind}/{pool_name}: fallback must terminate safely')

    if 'core' not in loaded:
        return
    core = loaded['core']
    core_jigs = jigsaws(core)
    targets = [be.get('target') for _pos, _state, be in core_jigs if be]
    expected_targets = ([f'{NS}:pixie_centre'] + [f'{NS}:pixie_house'] * 3 +
                        [f'{NS}:pixie_garden', f'{NS}:pixie_tree'])
    if sorted(targets) != sorted(expected_targets):
        fail('P9', f'{kind}: core socket targets are {targets}')
    for pos, state, be in core_jigs:
        if state.get('Properties', {}).get('orientation') != 'up_north':
            fail('P9', f'{kind}: root socket {pos} does not face upward')
        if not be or be.get('joint') != 'aligned':
            fail('P9', f'{kind}: root socket {pos} can rotate away from authored support')

    root_entries = entries(core)
    spawners = [(pos, be) for pos, state, be in root_entries
                if state.get('Name') == 'minecraft:spawner']
    if len(spawners) != 1:
        fail('P10', f'{kind}: expected one buried spawner, found {len(spawners)}')
    else:
        pos, be = spawners[0]
        if pos != (16, 4, 16):
            fail('P10', f'{kind}: spawner moved away from below the centre: {pos}')
        if not be or be.get('id') != 'minecraft:mob_spawner':
            fail('P10', f'{kind}: invalid spawner block entity')
        elif be.get('SpawnData', {}).get('entity', {}).get('id') != c['entity']:
            fail('P10', f'{kind}: spawner has the wrong seasonal pixie')
        elif (int(be.get('SpawnCount', 0)), int(be.get('MaxNearbyEntities', 0)),
              int(be.get('SpawnRange', 99))) != (1, 4, 3):
            fail('P10', f'{kind}: bounded spawner profile changed')
    if not any(state.get('Name') == 'minecraft:ladder' for _p, state, _be in root_entries):
        fail('P10', f'{kind}: buried vault has no maintenance/escape shaft')

    # The ground footprint must be visibly organic, not a disguised square platform.
    occupied_xz = {(x, z) for (x, y, z), state, _be in root_entries
                   if y == 8 and state.get('Name') != 'minecraft:air'}
    if not (480 <= len(occupied_xz) <= 760):
        fail('P11', f'{kind}: island surface area {len(occupied_xz)} is not a small organic island')
    for corner in ((0, 0), (0, 32), (32, 0), (32, 32)):
        if corner in occupied_xz:
            fail('P11', f'{kind}: square bounding corner {corner} is filled')

    child_names = {'centre': f'{NS}:pixie_centre', 'garden': f'{NS}:pixie_garden',
                   'tree': f'{NS}:pixie_tree'}
    for name, connector in child_names.items():
        if name not in loaded:
            continue
        js = jigsaws(loaded[name])
        if len(js) != 1 or not js[0][2] or js[0][2].get('name') != connector:
            fail('P12', f'{kind}/{name}: connector does not answer its root target')
        elif js[0][1].get('Properties', {}).get('orientation') != 'down_north':
            fail('P12', f'{kind}/{name}: child connector does not face down')
    for i in range(1, 5):
        name = f'house_{i}'
        if name not in loaded:
            continue
        js = jigsaws(loaded[name])
        if len(js) != 1 or not js[0][2] or js[0][2].get('name') != f'{NS}:pixie_house':
            fail('P12', f'{kind}/{name}: house connector does not answer the house socket')

    if 'centre' in loaded:
        centre_entries = entries(loaded['centre'])
        if 'minecraft:water' not in names(loaded['centre']):
            fail('P13', f'{kind}: civic centre is no longer a well')
        hatches = [state for _p, state, _be in centre_entries
                   if state.get('Name') == c['wood'] + '_trapdoor']
        if len(hatches) != 1 or hatches[0].get('Properties', {}).get('open') != 'true':
            fail('P13', f'{kind}: service hatch is absent or blocks the pixie exit')

    if 'tree' in loaded:
        tree_names = names(loaded['tree'])
        for block in [c['log'], c['sapling'], *c['leaves']]:
            if block not in tree_names:
                fail('P14', f'{kind}: seasonal tree piece omits {block}')

    if 'garden' in loaded:
        garden_names = names(loaded['garden'])
        for crop, _age in c['crops']:
            if crop not in garden_names:
                fail('P15', f'{kind}: garden omits functional crop {crop}')
        for block in ('minecraft:farmland', 'minecraft:water'):
            if block not in garden_names:
                fail('P15', f'{kind}: garden omits {block}')
        if kind == 'winter' and 'minecraft:glass' not in garden_names:
            fail('P15', 'winter: garden is no longer a lit coldframe')


def main():
    salts = []
    for kind, culture in CULTURES.items():
        salts.append(check_structure_data(kind, culture))
        check_pools_and_pieces(kind, culture)
    if len(set(salts)) != len(salts) or None in salts:
        fail('P16', f'structure-set salts are missing or duplicated: {salts}')

    if failures:
        print('Pixie settlement check FAILED')
        for problem in failures:
            print('  ' + problem)
        return 1
    print('Pixie settlement check passed')
    print('  4 cultures; 32 NBT pieces; 20 pools; 4 rare fixed-height structure sets')
    print('  each core: 1 dew well + 3 houses + 1 garden + 1 seasonal tree')
    print('  each vault: exactly 1 bounded seasonal pixie spawner below the centre')
    return 0


if __name__ == '__main__':
    sys.exit(main())
