"""Validate Alfheim's surface structures and the Cartographer's map shop.

Design: alfheim_reclaimed_design/THE_SURFACE.md. Generator: tools/gen_surface_works.py.

Fourteen checks. Most of them exist because the failure they catch is SILENT -- the world
still loads, every file still parses, and the thing simply is not there:

  W2  An unknown block id does not error. NbtUtils.readBlockState returns Blocks.AIR for a
      block it cannot resolve, so one typo turns a keep into a hole in the ground and nothing
      anywhere says so.
  W3  A structure whose `biomes` tag does not contain the biome at the chosen chunk does not
      generate AT ALL, with no log line. SPAWN_HUB.md paid for this twice.
  W5  Two random_spread sets sharing spacing and salt pick the SAME chunk in every cell. They
      do not become neighbours -- they generate on top of each other.
  W7  A bad `destination` on an exploration_map hands the player a blank map. They paid for it.
  W12 max_distance_from_center + margin > 128 does not cull a piece, it REFUSES WORLD CREATION.
  W14 Nothing in this pack parses SNBT at build time, so a chapter with one stray brace is
      only discovered when FTB Quests fails to load the whole quest folder.

    python tools/check_surface_works.py
    python tools/check_surface_works.py --verbose
    python tools/check_surface_works.py --self-test     # prove the checks can fail
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402
from structure_nbt import ADAPTATION_MARGIN, DATA_VERSION, MAX_AXIS  # noqa: E402

NS = 'alfheim'
DATA = os.path.join('kubejs', 'data', NS)
MANIFEST = os.path.join('tools', 'surface_works_manifest.json')
REGISTRY = os.path.join('tools', 'registry_items.json')
LAYER = os.path.join('kubejs', 'data', 'mythicbotany', 'libx', 'biome_layer', 'alfheim.json')
CHAPTER = os.path.join('config', 'ftbquests', 'quests', 'chapters', 'cartographer.snbt')
GROUPS = os.path.join('config', 'ftbquests', 'quests', 'chapter_groups.snbt')

# Blocks with no item form. Everything else in a palette must appear in the registry dump,
# which is the only ground truth this project has for what actually exists at runtime.
NO_ITEM = {'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air', 'minecraft:water',
           'minecraft:lava', 'minecraft:wall_torch', 'minecraft:soul_wall_torch',
           'minecraft:structure_void'}

# Read off the shipping 1.20.1 client jar (dyl$a.class), not remembered. 1.20.1 has no
# jungle_temple and no swamp_hut -- those decorations arrived in later versions.
DECORATIONS = {
    'player', 'frame', 'red_marker', 'blue_marker', 'target_x', 'target_point',
    'player_off_map', 'player_off_limits', 'mansion', 'monument', 'red_x',
} | {f'banner_{c}' for c in (
    'white', 'orange', 'magenta', 'light_blue', 'yellow', 'lime', 'pink', 'gray',
    'light_gray', 'cyan', 'purple', 'blue', 'brown', 'green', 'red', 'black')}


def snbt_shape(text):
    """Brace, bracket and quote balance, respecting string escapes.

    FTB Quests reads the whole quest folder at once. A chapter with one unbalanced brace does
    not fail alone -- it can take the file with it, and nothing in the pack parses SNBT at
    build time, so this is the only place a mismatched delimiter can be caught before the game
    tries to load it.
    """
    curly = square = 0
    in_str = esc = False
    for ch in text:
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == '{':
            curly += 1
        elif ch == '}':
            curly -= 1
        elif ch == '[':
            square += 1
        elif ch == ']':
            square -= 1
        if curly < 0 or square < 0:
            break
    return curly, square, in_str


def jload(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def walk_names(obj, out):
    """Every `name`/`item` string in a loot table, however deeply nested."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ('name', 'item') and isinstance(v, str) and ':' in v:
                out.add(v)
            else:
                walk_names(v, out)
    elif isinstance(obj, list):
        for v in obj:
            walk_names(v, out)


def collect(mutate=None):
    """Read every artifact this checker judges. `mutate` lets --self-test corrupt one."""
    m = jload(MANIFEST)
    reg = set(jload(REGISTRY)['ids'])
    layer_biomes = {b['biome'] for b in jload(LAYER)['biomes']}

    state = {
        'm': m, 'reg': reg, 'layer': layer_biomes,
        'structures': {os.path.basename(p)[:-5]: jload(p)
                       for p in glob.glob(os.path.join(DATA, 'worldgen', 'structure', '*.json'))},
        'sets': {os.path.basename(p)[:-5]: jload(p)
                 for p in glob.glob(os.path.join(DATA, 'worldgen', 'structure_set', '*.json'))},
        'pools': {p: jload(p) for p in glob.glob(
            os.path.join(DATA, 'worldgen', 'template_pool', 'surface', '*.json'))},
        'biome_tags': {os.path.basename(p)[:-5]: jload(p) for p in glob.glob(
            os.path.join(DATA, 'tags', 'worldgen', 'biome', '*.json'))},
        'struct_tags': {os.path.basename(p)[:-5]: jload(p) for p in glob.glob(
            os.path.join(DATA, 'tags', 'worldgen', 'structure', '*.json'))},
        'maps': {os.path.basename(p)[:-5]: jload(p) for p in glob.glob(
            os.path.join(DATA, 'loot_tables', 'explorer_maps', '*.json'))},
        'chests': {os.path.basename(p)[:-5]: jload(p) for p in glob.glob(
            os.path.join(DATA, 'loot_tables', 'chests', '*.json'))},
        'nbts': sorted(glob.glob(os.path.join(DATA, 'structures', 'surface', '*.nbt'))),
        'chapter': open(CHAPTER, encoding='utf-8').read() if os.path.exists(CHAPTER) else '',
        'groups': open(GROUPS, encoding='utf-8').read() if os.path.exists(GROUPS) else '',
    }
    if mutate:
        mutate(state)
    return state


def run(st, verbose=False):
    problems = []

    def fail(code, msg):
        problems.append(f'{code}  {msg}')

    m, reg, layer = st['m'], st['reg'], st['layer']
    manifest_ids = [s['id'] for s in m['structures']]
    by_id = {s['id']: s for s in m['structures']}

    # ---------------------------------------------------------------- W1  NBT integrity
    seen_nbt = set()
    palettes_seen = {}
    for path in st['nbts']:
        sid = os.path.basename(path)[:-4]
        seen_nbt.add(sid)
        try:
            _, root = nbt.load(path)
        except Exception as e:                                    # noqa: BLE001
            fail('W1', f'{sid}: unreadable NBT -- {e}')
            continue
        size = [int(v) for v in root['size']]
        if int(root['DataVersion']) != DATA_VERSION:
            fail('W1', f'{sid}: DataVersion {int(root["DataVersion"])}, expected {DATA_VERSION}')
        if any(a > MAX_AXIS for a in size):
            fail('W1', f'{sid}: {size} exceeds the {MAX_AXIS}-block structure limit')
        if sid in by_id:
            want = m['archetypes'][by_id[sid]['archetype']]['size']
            if size != list(want):
                fail('W1', f'{sid}: NBT size {size} != manifest {want} -- stale artifact')
        for e in root['blocks']:
            x, y, z = (int(v) for v in e['pos'])
            if not (0 <= x < size[0] and 0 <= y < size[1] and 0 <= z < size[2]):
                fail('W1', f'{sid}: block at {(x, y, z)} outside {size}')
                break
        palettes_seen[sid] = [p['Name'] for p in root['palette']]
        # every chest/barrel must name a loot table that exists
        for e in root['blocks']:
            be = e.get('nbt')
            if isinstance(be, dict) and 'LootTable' in be:
                lt = be['LootTable']
                ns, _, rest = lt.partition(':')
                if ns != NS or rest.split('/')[0] != 'chests' or \
                        rest.split('/')[-1] not in st['chests']:
                    fail('W8', f'{sid}: block entity names missing loot table {lt}')
    missing_nbt = set(manifest_ids) - seen_nbt
    if missing_nbt:
        fail('W1', f'manifest structures with no .nbt on disk: {sorted(missing_nbt)}')

    # ---------------------------------------------------------------- W2  block ids exist
    for sid, names in palettes_seen.items():
        for name in set(names):
            if name not in NO_ITEM and name not in reg:
                fail('W2', f'{sid}: palette block "{name}" is not in the registry dump -- '
                            f'it will load as AIR')
    for key, pal in m['palettes'].items():
        for slot, val in pal.items():
            if slot.startswith('_'):
                continue
            for b in (val if isinstance(val, list) else [val]):
                if b not in reg and b not in NO_ITEM:
                    fail('W2', f'palette {key}.{slot} = "{b}" is not in the registry dump')

    # ---------------------------------------------------------------- W3  biome validity
    for sid in manifest_ids:
        js = st['structures'].get(sid)
        if js is None:
            fail('W3', f'{sid}: no worldgen/structure json')
            continue
        tag = js['biomes']
        if not tag.startswith(f'#{NS}:has_'):
            fail('W3', f'{sid}: biomes is "{tag}", expected #{NS}:has_{sid}')
            continue
        tagname = tag[len(f'#{NS}:'):]
        body = st['biome_tags'].get(tagname)
        if body is None:
            fail('W3', f'{sid}: biome tag {tagname}.json does not exist')
            continue
        for b in body['values']:
            if b not in layer:
                fail('W3', f'{sid}: biome "{b}" is not in the Alfheim layer -- '
                            f'the structure can never generate there')
        if set(body['values']) != set(by_id[sid]['biomes']):
            fail('W3', f'{sid}: biome tag does not match the manifest')

    # ---------------------------------------------------------------- W4  pool resolution
    pool_by_name = {}
    for path, body in st['pools'].items():
        pool_by_name[body['name']] = body
        for el in body['elements']:
            loc = el['element']['location']
            rel = loc.split(':', 1)[1]
            if not os.path.exists(os.path.join(DATA, 'structures', rel + '.nbt')):
                fail('W4', f'{body["name"]}: element "{loc}" has no .nbt')
    for sid in manifest_ids:
        js = st['structures'].get(sid) or {}
        sp = js.get('start_pool')
        if sp not in pool_by_name:
            fail('W4', f'{sid}: start_pool "{sp}" does not resolve to a template pool')

    # ---------------------------------------------------------------- W5  salts are unique
    salts = {}
    for name, body in st['sets'].items():
        pl = body['placement']
        if pl['type'] != 'minecraft:random_spread':
            continue
        if pl['separation'] >= pl['spacing']:
            fail('W5', f'{name}: separation {pl["separation"]} >= spacing {pl["spacing"]}')
        salts.setdefault(pl['salt'], []).append(name)
        for entry in body['structures']:
            ref = entry['structure'].split(':', 1)[1]
            if ref not in st['structures']:
                fail('W5', f'{name}: references missing structure {entry["structure"]}')
    for salt, names in salts.items():
        if len(names) > 1:
            fail('W5', f'salt {salt} shared by {names} -- these generate in the same chunk')

    # ---------------------------------------------------------------- W6  archetype tags
    want_tags = {}
    for s in m['structures']:
        want_tags.setdefault(s['archetype'], set()).add(f'{NS}:{s["id"]}')
    for arch, want in want_tags.items():
        body = st['struct_tags'].get(arch)
        if body is None:
            fail('W6', f'archetype {arch}: no structure tag -- its map points at nothing')
            continue
        if set(body['values']) != want:
            fail('W6', f'archetype {arch}: tag {sorted(body["values"])} != {sorted(want)}')

    # ---------------------------------------------------------------- W7  the maps
    for arch, body in st['maps'].items():
        fns = body['pools'][0]['entries'][0]['functions']
        em = next((f for f in fns if f['function'] == 'minecraft:exploration_map'), None)
        if em is None:
            fail('W7', f'map {arch}: no exploration_map function -- this is a blank map')
            continue
        dest = em['destination']
        if dest.startswith('#'):
            fail('W7', f'map {arch}: destination "{dest}" has a leading # -- '
                        f'the deserializer builds the TagKey from the RAW string')
        elif dest.split(':', 1)[1] not in st['struct_tags']:
            fail('W7', f'map {arch}: destination "{dest}" is not a structure tag on disk')
        if em['decoration'] not in DECORATIONS:
            fail('W7', f'map {arch}: decoration "{em["decoration"]}" is not a 1.20.1 '
                        f'MapDecoration.Type')
        if not 0 <= em['zoom'] <= 4:
            fail('W7', f'map {arch}: zoom {em["zoom"]} outside 0..4')
        if body['pools'][0]['entries'][0]['name'] != 'minecraft:map':
            fail('W7', f'map {arch}: exploration_map applied to something that is not a map')

    # ---------------------------------------------------------------- W8  loot items exist
    for name, body in list(st['chests'].items()) + list(st['maps'].items()):
        ids = set()
        walk_names(body, ids)
        for i in sorted(ids):
            if i not in reg and i not in NO_ITEM:
                fail('W8', f'loot table {name}: item "{i}" is not in the registry dump')

    # ---------------------------------------------------------------- W9  the shop
    ch = st['chapter']
    if not ch:
        fail('W9', 'the Cartographer chapter has not been generated')
    else:
        group = re.search(r'group: "([0-9A-F]+)"', ch)
        if not group or f'id: "{group.group(1)}"' not in st['groups']:
            fail('W9', 'the chapter names a group that chapter_groups.snbt does not declare')
        cmds = re.findall(r'command: "([^"]+)"', ch)
        if len(cmds) != len(m['archetypes']):
            fail('W9', f'{len(cmds)} command rewards for {len(m["archetypes"])} archetypes')
        for c in cmds:
            mt = re.match(r'^/loot give \{p\} loot ' + NS + r':explorer_maps/(\w+)$', c)
            if not mt:
                fail('W9', f'reward command is not the expected /loot give form: "{c}"')
            elif mt.group(1) not in st['maps']:
                fail('W9', f'reward command names missing loot table: "{c}"')
        for item, count in re.findall(r'type: "item", item: "([^"]+)", count: (\d+)L', ch):
            if item not in reg:
                fail('W9', f'purchase asks for "{item}", which is not in the registry dump')
        n_repeat = ch.count('can_repeat: true')
        if n_repeat != len(m['archetypes']):
            fail('W9', f'{n_repeat} repeatable quests, expected {len(m["archetypes"])}')
        if 'elevate_perms: true' not in ch:
            fail('W9', '/loot needs permission level 2; no reward elevates')
        n_consume = ch.count('consume_items: true')
        n_cost = sum(len(a['cost']) for a in m['archetypes'].values())
        if n_consume != n_cost:
            fail('W9', f'{n_consume} consuming tasks, expected {n_cost} -- '
                       f'a purchase that does not consume is a free map')

    # ---------------------------------------------------------------- W14 the SNBT itself
    if ch:
        curly, square, unterminated = snbt_shape(ch)
        if curly or square or unterminated:
            fail('W14', f'cartographer.snbt is malformed: brace balance {curly}, bracket '
                        f'balance {square}, unterminated string {unterminated}')
        # The generators write with newline=None, so on Windows every line ends CRLF. An
        # anchored `...$` then never matches, every list below comes back empty, and the whole
        # check passes by finding nothing -- which is the failure mode this file exists to
        # prevent. Normalise first, then assert the counts are non-zero.
        flat = ch.replace('\r\n', '\n')
        every_id = re.findall(r'id: "([0-9A-F]{16})"', flat)
        # Three tabs is a quest; one tab is the chapter's own id, which is not a dependency
        # target and must not be counted as one.
        quest_ids = set(re.findall(r'^\t\t\tid: "([0-9A-F]{16})"$', flat, re.M))
        n_quests = flat.count('\n\t\t{')
        if not quest_ids or len(quest_ids) != n_quests:
            fail('W14', f'found {len(quest_ids)} quest ids for {n_quests} quest blocks -- '
                        f'the id scan is not seeing what it thinks it is')
        dupes = sorted({i for i in every_id if every_id.count(i) > 1})
        if dupes:
            fail('W14', f'cartographer.snbt reuses ids, so FTB will drop one: {dupes}')
        for dep in re.findall(r'dependencies: \[([^\]]*)\]', flat):
            for d in re.findall(r'"([0-9A-F]{16})"', dep):
                if d not in quest_ids:
                    fail('W14', f'cartographer.snbt depends on {d}, which is not a quest in '
                                f'the chapter -- FTB drops the dependency silently')

    # ---------------------------------------------------------------- W10 two per biome
    per_biome = {}
    for s in m['structures']:
        for b in s['biomes']:
            per_biome.setdefault(b, []).append(s['id'])
    for b in sorted(layer):
        got = per_biome.get(b, [])
        if len(got) < 2:
            fail('W10', f'biome {b} has {len(got)} structures, the brief asks for 2 or more')
    for b in sorted(per_biome):
        if b not in layer:
            fail('W10', f'manifest assigns structures to {b}, which is not in the layer')

    # ---------------------------------------------------------------- W11 shape variety
    for arch, ids in sorted(want_tags.items()):
        ids = sorted(i.split(':')[1] for i in ids)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = by_id[ids[i]], by_id[ids[j]]
                base = m['archetypes'][arch]['defaults']
                sa = dict(base, **a.get('shape', {}))
                sb = dict(base, **b.get('shape', {}))
                diff = [k for k in sa if sa[k] != sb[k]]
                if len(diff) < 2:
                    fail('W11', f'{a["id"]} and {b["id"]} differ in {len(diff)} shape keys; '
                                f'THE_SURFACE.md 6.3 requires at least 2')

    # ---------------------------------------------------------------- W12/W13 placement
    for sid in manifest_ids:
        js = st['structures'].get(sid)
        if not js:
            continue
        arch = m['archetypes'][by_id[sid]['archetype']]
        margin = ADAPTATION_MARGIN[js['terrain_adaptation']]
        if js['max_distance_from_center'] + margin > 128:
            fail('W12', f'{sid}: max_distance_from_center {js["max_distance_from_center"]} '
                        f'+ margin {margin} > 128 -- this REFUSES WORLD CREATION')
        want_h = -arch['ground']
        if js['start_height'].get('absolute') != want_h:
            fail('W13', f'{sid}: start_height {js["start_height"]} != absolute {want_h}; '
                        f'the piece will sit at the wrong depth')
        if js['step'] != 'surface_structures':
            fail('W13', f'{sid}: step "{js["step"]}" -- these are surface features')

    if verbose:
        print(f'  {len(seen_nbt)} nbt, {len(st["structures"])} structures, '
              f'{len(st["sets"])} sets, {len(st["struct_tags"])} archetype tags, '
              f'{len(st["maps"])} maps, {len(st["chests"])} chest tables, '
              f'{len(salts)} distinct salts')
    return problems


SELF_TESTS = [
    ('W1', lambda s: s.__setitem__('nbts', s['nbts'][:-1])),
    ('W2', lambda s: s['m']['palettes']['livingrock'].__setitem__('brick', 'botania:nonesuch')),
    ('W3', lambda s: s['biome_tags']['has_grey_barrow']['values'].append('alfheim:nowhere')),
    ('W5', lambda s: s['sets']['riven_hold']['placement'].__setitem__(
        'salt', s['sets']['ashwatch_keep']['placement']['salt'])),
    ('W6', lambda s: s['struct_tags']['castle']['values'].pop()),
    ('W7', lambda s: s['maps']['castle']['pools'][0]['entries'][0]['functions'][0].__setitem__(
        'destination', '#alfheim:castle')),
    ('W9', lambda s: s.__setitem__('chapter', s['chapter'].replace('can_repeat: true', '', 1))),
    ('W10', lambda s: s['m']['structures'].pop()),
    ('W14', lambda s: s.__setitem__('chapter', s['chapter'].replace('	quest_links: [ ]', '['))),
    ('W12', lambda s: s['structures']['hillcrown_keep'].__setitem__(
        'max_distance_from_center', 120)),
    ('W13', lambda s: s['structures']['marchfall_crater'].__setitem__(
        'start_height', {'absolute': 0})),
]


def self_test():
    """A checker that cannot fail is not a checker. Corrupt one thing at a time and prove the
    matching code fires -- this is the same discipline check_worldgen.py and
    check_feature_order.py already hold themselves to."""
    clean = run(collect())
    if clean:
        print('  self-test cannot run: the real data already has problems')
        return 1
    bad = 0
    for code, mut in SELF_TESTS:
        probs = run(collect(mutate=mut))
        hit = [p for p in probs if p.startswith(code)]
        print(f'  {code:4} {"FIRES" if hit else "SILENT -- CHECK IS DEAD"}'
              f'   {hit[0][:96] if hit else ""}')
        if not hit:
            bad += 1
    print(f'\n  {len(SELF_TESTS) - bad}/{len(SELF_TESTS)} checks proven to fire')
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    problems = run(collect(), verbose=a.verbose)
    for p in problems:
        print('  ' + p)
    print(f'\n  {len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
