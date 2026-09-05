"""Generate the Archive Groves — petals from leaves, and Alfheim's own trees.

Design record: alfheim_reclaimed_design/ORE_SUPPLEMENTATION.md §9
Manifest:      tools/groves_manifest.json

Two jobs:

1. **Petals from leaves.** Every tree that grows in Alfheim drops petals of its own colour.
   This is the renewable answer to B-46. The mod's existing loot pools are copied *verbatim
   out of its jar* and one petal pool is appended — nothing is authored by hand, so the
   archwood saplings that Rite I depends on cannot be silently dropped. Re-running after a
   mod update re-reads the jar, so the override re-syncs instead of drifting.

2. **Three trees of our own** whose leaves carry other forests' seeds. No vanilla tree
   generates in Alfheim, so without these there is no oak, no apple, no plank variety at
   all. Their leaves drop randomized vanilla saplings — and, more rarely, the tree's own.

   They are replantable. KubeJS 2001.6.5 has no SaplingBlock builder and no TreeGrower
   binding, so the sapling grows in its randomTick callback by placing trunk and canopy
   directly through BlockContainerJS.offset(Direction, int) — the one overload confirmed
   present in the jar. Closes B-49.

    python tools/gen_groves.py
    python tools/gen_groves.py --dry-run
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_items import tint, load_base, CLIENT_JAR  # noqa: E402

NS = 'alfheim'
MANIFEST = os.path.join('tools', 'groves_manifest.json')
DATA = os.path.join('kubejs', 'data')
TEX_BLOCK = os.path.join('kubejs', 'assets', NS, 'textures', 'block')
MODEL_ITEM = os.path.join('kubejs', 'assets', NS, 'models', 'item')
STARTUP = os.path.join('kubejs', 'startup_scripts', '12_groves.js')

# Fortune ladders lifted from vanilla's own leaf tables so our pools behave like the ones
# players already know. Index 0 is Fortune 0.
FORTUNE_PETAL = [1.0, 1.15, 1.3, 1.6, 2.4]
FORTUNE_SAPLING = [1.0, 1.11, 1.25, 1.67, 5.0]

NOT_SHEARS = {
    'condition': 'minecraft:inverted',
    'term': {
        'condition': 'minecraft:any_of',
        'terms': [
            {'condition': 'minecraft:match_tool',
             'predicate': {'items': ['minecraft:shears']}},
            {'condition': 'minecraft:match_tool',
             'predicate': {'enchantments': [
                 {'enchantment': 'minecraft:silk_touch', 'levels': {'min': 1}}]}},
        ],
    },
}


def chance_pool(entries, base, ladder):
    """A vanilla apple-pool shaped pool: not on shears, survives explosion, scales with Fortune."""
    return {
        'bonus_rolls': 0.0,
        'rolls': 1.0,
        'conditions': [NOT_SHEARS],
        'entries': [
            {'type': 'minecraft:item',
             'name': name,
             'weight': weight,
             'conditions': [
                 {'condition': 'minecraft:survives_explosion'},
                 {'condition': 'minecraft:table_bonus',
                  'enchantment': 'minecraft:fortune',
                  'chances': [round(base * m, 6) for m in ladder]},
             ]}
            for name, weight in entries
        ],
    }


def write(path, content, dry):
    if dry:
        print(f'   [dry] {path}')
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def write_json(path, obj, dry):
    write(path, json.dumps(obj, indent=2) + '\n', dry)


# ------------------------------------------------------------------ 1. petals from mod leaves

def build_leaf_petals(entries, dry):
    """Copy each mod's leaf loot table out of its jar and append a petal pool."""
    for e in entries:
        ns, path = e['leaf'].split(':', 1)
        jar = os.path.join('mods', e['jar'])
        if not os.path.exists(jar):
            print(f'   SKIP {e["leaf"]}: {e["jar"]} not installed')
            continue
        member = f'data/{ns}/loot_tables/blocks/{path}.json'
        with zipfile.ZipFile(jar) as z:
            try:
                raw = z.read(member)
            except KeyError:
                print(f'   SKIP {e["leaf"]}: no loot table at {member}')
                continue
        table = json.loads(raw)
        src_hash = hashlib.sha1(raw).hexdigest()[:12]
        before = len(table.get('pools', []))

        table.setdefault('pools', []).append(chance_pool(
            [(f'botania:{c}_petal', 1) for c in e['petals']],
            e['chance'], FORTUNE_PETAL))

        # Provenance: makes drift from an updated jar visible without diffing the whole file.
        table['__alfheim'] = {
            'generated_by': 'tools/gen_groves.py',
            'source_jar': e['jar'],
            'source_sha1_12': src_hash,
            'original_pools': before,
            'added': f'petal pool ({", ".join(e["petals"])}) at {e["chance"]}',
        }
        out = os.path.join(DATA, ns, 'loot_tables', 'blocks', f'{path}.json')
        write_json(out, table, dry)
        print(f"   petals  {e['leaf']:<40} {before} pool(s) kept + {'/'.join(e['petals'])}")


# ------------------------------------------------------------------ 2. our own trees

def build_trees(trees, jar, dry):
    reg = ['// Alfheim Reclaimed — the Archive Groves',
           '//',
           '// GENERATED by tools/gen_groves.py from tools/groves_manifest.json — do not hand-edit.',
           '//',
           '// Three trees that carry other forests\' seeds. No vanilla tree generates in Alfheim,',
           '// so their leaves are the only source of oak, birch, spruce, acacia, jungle, dark oak',
           '// and cherry saplings — and with them apples, plank variety and a normal wood economy.',
           '//',
           '// Their leaves drop plantable vanilla saplings, and more rarely their own — grown',
           '// by growGrove() below, since KubeJS exposes no TreeGrower to hand the job to.',
           '',
           "StartupEvents.registry('block', event => {"]

    for t in trees:
        tid = t['id']
        # --- textures
        lg = load_base(jar, t['log']['base'])
        lt = load_base(jar, t['log']['top'])
        lv = load_base(jar, t['leaves']['base'])
        sp = load_base(jar, t.get('sapling_base', 'block/oak_sapling.png'))
        imgs = {
            f'{tid}_log': tint(lg, t['log']['hue'], t['log']['sat'], t['log']['val'], 0.30),
            f'{tid}_log_top': tint(lt, t['log']['hue'], t['log']['sat'], t['log']['val'], 0.30),
            f'{tid}_leaves': tint(lv, t['leaves']['hue'], t['leaves']['sat'],
                                  t['leaves']['val'], 0.35),
            f'{tid}_sapling': tint(sp, t['leaves']['hue'], t['leaves']['sat'],
                                   t['leaves']['val'], 0.35),
        }
        if not dry:
            os.makedirs(TEX_BLOCK, exist_ok=True)
            os.makedirs(MODEL_ITEM, exist_ok=True)
            for name, im in imgs.items():
                im.save(os.path.join(TEX_BLOCK, name + '.png'))
            with open(os.path.join(MODEL_ITEM, f'{tid}_sapling.json'), 'w',
                      encoding='utf-8') as f:
                json.dump({'parent': 'minecraft:item/generated',
                           'textures': {'layer0': f'{NS}:block/{tid}_sapling'}}, f, indent=2)

        # --- blocks
        reg.append(
            f"    event.create('{NS}:{tid}_log')"
            f".displayName('{t['name']} Log').soundType('wood')"
            f".hardness(2.0).resistance(2.0)"
            f".tagBlock('minecraft:mineable/axe').tagBlock('minecraft:logs')"
            f".tagBlock('minecraft:logs_that_burn').tagBlock('{NS}:grove_logs')"
            f".textureAll('{NS}:block/{tid}_log')"
            f".texture('up', '{NS}:block/{tid}_log_top')"
            f".texture('down', '{NS}:block/{tid}_log_top')")
        reg.append(
            f"    event.create('{NS}:{tid}_leaves')"
            f".displayName('{t['name']} Leaves').soundType('grass')"
            f".hardness(0.2).resistance(0.2).defaultCutout().notSolid()"
            f".tagBlock('minecraft:mineable/hoe').tagBlock('minecraft:leaves')"
            f".tagBlock('{NS}:grove_leaves')"
            f".textureAll('{NS}:block/{tid}_leaves')")
        # Sapling. KubeJS 2001.6.5 has no SaplingBlock builder and no TreeGrower binding, so
        # growth is done in the randomTick callback by placing the trunk and canopy directly
        # through BlockContainerJS.offset(Direction, int) — the one overload confirmed present
        # in the jar. The shape mirrors this tree's worldgen trunk/foliage numbers.
        reg.append(
            f"    event.create('{NS}:{tid}_sapling')"
            f".displayName('{t['name']} Sapling').soundType('grass')"
            f".hardness(0.0).resistance(0.0).defaultCutout().notSolid().fullBlock(false)"
            f".box(4, 0, 4, 12, 12, 12)"
            f".tagBlock('minecraft:mineable/axe').tagBlock('{NS}:grove_saplings')"
            f".textureAll('{NS}:block/{tid}_sapling')"
            f".randomTick(ctx => growGrove(ctx, '{NS}:{tid}_log', '{NS}:{tid}_leaves', "
            f"{t['trunk'][0]}, {t['trunk'][1]}, {t['foliage'][0]}))")

        # --- leaf loot: leaves on shears/silk, sticks, petals, foreign saplings
        table = {
            'type': 'minecraft:block',
            'pools': [
                {'bonus_rolls': 0.0, 'rolls': 1.0, 'entries': [{
                    'type': 'minecraft:item',
                    'name': f'{NS}:{tid}_leaves',
                    'conditions': [{
                        'condition': 'minecraft:any_of',
                        'terms': [
                            {'condition': 'minecraft:match_tool',
                             'predicate': {'items': ['minecraft:shears']}},
                            {'condition': 'minecraft:match_tool',
                             'predicate': {'enchantments': [
                                 {'enchantment': 'minecraft:silk_touch',
                                  'levels': {'min': 1}}]}},
                        ]}],
                }]},
                {'bonus_rolls': 0.0, 'rolls': 1.0, 'conditions': [NOT_SHEARS], 'entries': [{
                    'type': 'minecraft:item', 'name': 'minecraft:stick',
                    'conditions': [{'condition': 'minecraft:table_bonus',
                                    'enchantment': 'minecraft:fortune',
                                    'chances': [0.02, 0.022222223, 0.025, 0.033333335, 0.1]}],
                    'functions': [
                        {'function': 'minecraft:set_count', 'add': False,
                         'count': {'type': 'minecraft:uniform', 'min': 1.0, 'max': 2.0}},
                        {'function': 'minecraft:explosion_decay'}],
                }]},
                chance_pool([(f'botania:{c}_petal', 1) for c in t['petals']],
                            t['petal_chance'], FORTUNE_PETAL),
                # Foreign seeds — the archive. These are the plantable vanilla saplings.
                chance_pool([(s, 1) for s in t['saplings']],
                            t['sapling_chance'], FORTUNE_SAPLING),
                # ...and the tree's own sapling, so a grove can be replanted rather than
                # strip-mined. Rarer than the foreign seeds on purpose (B-49).
                chance_pool([(f'{NS}:{tid}_sapling', 1)],
                            t.get('own_sapling_chance', 0.03), FORTUNE_SAPLING),
            ],
            'random_sequence': f'{NS}:blocks/{tid}_leaves',
        }
        write_json(os.path.join(DATA, NS, 'loot_tables', 'blocks', f'{tid}_leaves.json'),
                   table, dry)

        # --- worldgen: a plain vanilla tree feature using our blocks
        write_json(os.path.join(DATA, NS, 'worldgen', 'configured_feature', f'tree_{tid}.json'), {
            'type': 'minecraft:tree',
            'config': {
                'decorators': [],
                'dirt_provider': {'type': 'minecraft:simple_state_provider',
                                  'state': {'Name': 'minecraft:dirt'}},
                'trunk_provider': {'type': 'minecraft:simple_state_provider',
                                   'state': {'Name': f'{NS}:{tid}_log',
                                             'Properties': {'axis': 'y'}}},
                'foliage_provider': {'type': 'minecraft:simple_state_provider',
                                     'state': {'Name': f'{NS}:{tid}_leaves'}},
                'trunk_placer': {'type': 'minecraft:straight_trunk_placer',
                                 'base_height': t['trunk'][0],
                                 'height_rand_a': t['trunk'][1],
                                 'height_rand_b': t['trunk'][2]},
                'foliage_placer': {'type': 'minecraft:blob_foliage_placer',
                                   'radius': t['foliage'][0],
                                   'offset': t['foliage'][1],
                                   'height': t['foliage'][2]},
                'minimum_size': {'type': 'minecraft:two_layers_feature_size',
                                 'limit': 1, 'lower_size': 0, 'upper_size': 1},
                'ignore_vines': True,
                'force_dirt': False,
            },
        }, dry)
        write_json(os.path.join(DATA, NS, 'worldgen', 'placed_feature', f'tree_{tid}.json'), {
            'feature': f'{NS}:tree_{tid}',
            'placement': [
                {'type': 'minecraft:count', 'count': t['count']},
                {'type': 'minecraft:rarity_filter', 'chance': t['rarity']},
                {'type': 'minecraft:in_square'},
                # Runtime-proven 2026-09-04 from a player's screenshot: grove trees were
                # growing out of open lakes, and stacking on top of each other.
                #
                # OCEAN_FLOOR is what vanilla trees use too -- it is not the problem on its
                # own. The problem was using it UNGUARDED. Vanilla's trees_plains pairs it
                # with exactly these two filters, and without them OCEAN_FLOOR happily returns
                # a lake bed (tree in the water) or the top of a log that another tree just
                # placed (tree on a tree).
                {'type': 'minecraft:surface_water_depth_filter', 'max_water_depth': 0},
                {'type': 'minecraft:heightmap', 'heightmap': 'OCEAN_FLOOR'},
                # would_survive is probed with an OAK sapling deliberately, not with our own.
                # Ours are KubeJS blocks whose canSurvive is permissive, so they would accept
                # anything and the filter would do nothing. Oak's rule -- dirt, grass, podzol,
                # not logs, not water -- is the canonical "could a tree grow here".
                {'type': 'minecraft:block_predicate_filter',
                 'predicate': {'type': 'minecraft:would_survive',
                               'state': {'Name': 'minecraft:oak_sapling',
                                         'Properties': {'stage': '0'}}}},
                {'type': 'minecraft:biome'},
            ],
        }, dry)

        # One modifier per tree, one feature each -> disjoint by construction, so no two
        # biomes can ever be handed contradictory orders by us. The zz_ prefix keeps these
        # sorting after every vegetal modifier the mods ship (see gen_alfheim_biomes.py).
        write_json(os.path.join(DATA, NS, 'forge', 'biome_modifier', f'zz_grove_{tid}.json'), {
            'type': 'forge:add_features',
            'biomes': t['biomes'],
            'features': f'{NS}:tree_{tid}',
            'step': 'vegetal_decoration',
        }, dry)
        print(f"   tree    {tid:<12} {t['name']:<12} petals={'/'.join(t['petals'])} "
              f"saplings={len(t['saplings'])} biomes={len(t['biomes'])}")

    reg += ['})', '',
            '// Grow a grove tree from its sapling.',
            '//',
            '// Vanilla would do this with a TreeGrower placing the configured feature. KubeJS',
            '// 2001.6.5 exposes neither, so the trunk and canopy are placed directly. Only',
            '// offset(Direction, int) is confirmed present on BlockContainerJS, so horizontal',
            '// offsets are reached by chaining it rather than by an offset(x, y, z) that may',
            '// not exist.',
            '//',
            '// Headroom is checked before anything is written, so a sapling under a ceiling',
            '// stays a sapling instead of growing a trunk into the floor above.',
            'function growGrove(ctx, logId, leafId, baseH, randH, radius) {',
            '    if (ctx.random.nextFloat() > 0.15) return',
            '    const root = ctx.block',
            '    const h = baseH + ctx.random.nextInt(randH + 1)',
            '',
            '    for (let y = 1; y <= h + 1; y++) {',
            "        const id = root.offset('up', y).id",
            "        if (id !== 'minecraft:air' && id !== leafId) return",
            '    }',
            '',
            "    for (let y = 0; y < h; y++) root.offset('up', y).set(logId)",
            '',
            '    for (let dy = -1; dy <= 2; dy++) {',
            '        const r = dy >= 2 ? radius - 1 : radius',
            '        if (r < 0) continue',
            "        const layer = root.offset('up', h + dy - 1)",
            '        for (let dx = -r; dx <= r; dx++) {',
            '            for (let dz = -r; dz <= r; dz++) {',
            '                if (Math.abs(dx) + Math.abs(dz) > r + 1) continue',
            '                if (dx === 0 && dz === 0 && dy < 1) continue',
            '                let t = layer',
            "                if (dx !== 0) t = t.offset(dx > 0 ? 'east' : 'west', Math.abs(dx))",
            "                if (dz !== 0) t = t.offset(dz > 0 ? 'south' : 'north', Math.abs(dz))",
            "                if (t.id === 'minecraft:air') t.set(leafId)",
            '            }',
            '        }',
            '    }',
            '}',
            '']
    write(STARTUP, '\n'.join(reg), dry)

    for tag, suffix in (('grove_leaves', '_leaves'), ('grove_logs', '_log'),
                        ('grove_saplings', '_sapling')):
        write_json(os.path.join(DATA, NS, 'tags', 'blocks', f'{tag}.json'),
                   {'replace': False,
                    'values': [f'{NS}:{t["id"]}{suffix}' for t in trees]}, dry)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    m = json.load(open(MANIFEST, encoding='utf-8'))
    leaves, trees = m['leaf_petals'], m['trees']

    if not os.path.exists(CLIENT_JAR):
        print(f'client jar not found: {CLIENT_JAR}')
        return 2
    jar = zipfile.ZipFile(CLIENT_JAR)

    print('Archive Groves')
    build_leaf_petals(leaves, a.dry_run)
    build_trees(trees, jar, a.dry_run)
    jar.close()

    covered = sorted({c for e in leaves for c in e['petals']} |
                     {c for t in trees for c in t['petals']})
    print(f'\n  {len(leaves)} mod leaf tables extended, {len(trees)} trees added')
    print(f'  petal colours with a leaf source: {len(covered)}/16')
    missing = sorted({'white', 'orange', 'magenta', 'light_blue', 'yellow', 'lime', 'pink',
                      'gray', 'light_gray', 'cyan', 'purple', 'blue', 'brown', 'green',
                      'red', 'black'} - set(covered))
    print('  missing:', missing if missing else 'none')
    saps = sorted({s for t in trees for s in t['saplings']})
    print(f'  vanilla saplings reachable: {len(saps)} -> '
          f'{[s.split(":")[1].replace("_sapling", "") for s in saps]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
