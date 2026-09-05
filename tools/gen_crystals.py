"""Generate Alfheim's crystallised mana — six crystals, six bifurcated geodes.

Design record: alfheim_reclaimed_design/ORE_SUPPLEMENTATION.md §9
Manifest:      tools/crystals_manifest.json

    python tools/gen_crystals.py
    python tools/gen_crystals.py --dry-run

Three things here are load-bearing and easy to get wrong:

**Bifurcation is spatial, not statistical.** `minecraft:noise_threshold_provider` picks each
block from `low_states` or `high_states` by sampling a noise field at that block's position.
At the manifest's scale a geode straddles roughly one noise boundary, so it comes out in
halves with a visible seam. A `weighted_state_provider` would have given salt-and-pepper.

**Geodes are anchored to the local surface, not to absolute depth.** `heightmap` then a
negative `random_offset` puts them 14-28 blocks under the ground the player is standing on.
This is what makes them findable, and it is also what makes the marker possible at all.

**The surface marker cannot produce a false positive.** `minecraft:environment_scan` caps
`max_steps` at 32, and aborts the placement when it finds nothing. The chain is
heightmap -> scan down for a budding crystal -> heightmap again; the scan moves only Y, so
re-running heightmap returns to the surface at the same x/z. No geode below means no marker.
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
MANIFEST = os.path.join('tools', 'crystals_manifest.json')
DATA = os.path.join('kubejs', 'data')
TEX_BLOCK = os.path.join('kubejs', 'assets', NS, 'textures', 'block')
TEX_ITEM = os.path.join('kubejs', 'assets', NS, 'textures', 'item')
MODEL_ITEM = os.path.join('kubejs', 'assets', NS, 'models', 'item')
MODEL_BLOCK = os.path.join('kubejs', 'assets', NS, 'models', 'block')
STARTUP = os.path.join('kubejs', 'startup_scripts', '13_crystals.js')
LOOT = os.path.join('kubejs', 'server_scripts', '13_crystal_loot.js')

BASES = {
    'block': 'block/amethyst_block.png',
    'budding': 'block/budding_amethyst.png',
    'cluster': 'block/amethyst_cluster.png',
    'shard': 'item/amethyst_shard.png',
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


def noise_split(a, b, kind, seed, p):
    """A spatially-coherent A|B chooser: low side of the noise is A, high side is B.

    kind is 'block' or 'budding'; both halves of a geode must split on the SAME noise
    field and seed, or the budding blocks would land on the wrong side of the seam.
    """
    def state(cid):
        return {'Name': f'{NS}:{cid}_block'} if kind == 'block' \
            else {'Name': f'{NS}:budding_{cid}'}
    return {
        'type': 'minecraft:noise_threshold_provider',
        'seed': seed,
        'noise': {'firstOctave': p['noise_first_octave'], 'amplitudes': [1.0]},
        'scale': p['noise_scale'],
        'threshold': 0.0,
        'high_chance': 1.0,
        'default_state': state(a),
        'low_states': [state(a)],
        'high_states': [state(b)],
    }


def geode_config(g, p, small):
    """Vanilla's geode feature, with both inner layers driven by the same noise split."""
    a, b = g['pair']
    # Python's hash() is salted per process, so it would emit a different seed on every run
    # and the generator would stop being reproducible. Derive it stably instead.
    seed = int(hashlib.sha1(g['id'].encode()).hexdigest()[:6], 16)
    clusters = [{'Name': f'{NS}:{c}_cluster',
                 'Properties': {'facing': 'up', 'waterlogged': 'false'}} for c in (a, b)]
    layers = ({'filling': 1.0, 'inner_layer': 1.5, 'middle_layer': 2.0, 'outer_layer': 2.6}
              if small else
              {'filling': 1.7, 'inner_layer': 2.2, 'middle_layer': 3.2, 'outer_layer': 4.2})
    wall = ({'type': 'minecraft:uniform',
             'value': {'min_inclusive': 1, 'max_inclusive': 2}} if small else
            {'type': 'minecraft:uniform',
             'value': {'min_inclusive': 4, 'max_inclusive': 6}})
    points = ({'type': 'minecraft:uniform',
               'value': {'min_inclusive': 1, 'max_inclusive': 2}} if small else
              {'type': 'minecraft:uniform',
               'value': {'min_inclusive': 3, 'max_inclusive': 4}})
    return {
        'type': 'minecraft:geode',
        'config': {
            'blocks': {
                'filling_provider': {'type': 'minecraft:simple_state_provider',
                                     'state': {'Name': 'minecraft:air'}},
                'inner_layer_provider': noise_split(a, b, 'block', seed, p),
                'alternate_inner_layer_provider': noise_split(a, b, 'budding', seed, p),
                'middle_layer_provider': {'type': 'minecraft:simple_state_provider',
                                          'state': {'Name': 'minecraft:calcite'}},
                'outer_layer_provider': {'type': 'minecraft:simple_state_provider',
                                         'state': {'Name': 'minecraft:smooth_basalt'}},
                'inner_placements': clusters,
                'cannot_replace': '#minecraft:features_cannot_replace',
                'invalid_blocks': '#minecraft:geode_invalid_blocks',
            },
            'layers': layers,
            'crack': {'generate_crack_chance': 0.95 if not small else 1.0,
                      'base_crack_size': 2.0, 'crack_point_offset': 2},
            'noise_multiplier': 0.05,
            'use_potential_placements_chance': 0.4,
            'use_alternate_layer0_chance': 0.14,
            'placements_require_layer0_alternate': True,
            'outer_wall_distance': wall,
            'distribution_points': points,
            'point_offset': {'type': 'minecraft:uniform',
                             'value': {'min_inclusive': 1, 'max_inclusive': 2}},
            'min_gen_offset': -16,
            'max_gen_offset': 16,
            'invalid_blocks_threshold': 1,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    m = json.load(open(MANIFEST, encoding='utf-8'))
    crystals, geodes, p = m['crystals'], m['geodes'], m['placement']
    dry = a.dry_run

    if not os.path.exists(CLIENT_JAR):
        print(f'client jar not found: {CLIENT_JAR}')
        return 2
    jar = zipfile.ZipFile(CLIENT_JAR)

    # ---------------------------------------------------------------- textures + models
    for c in crystals:
        for kind, base in BASES.items():
            img = tint(load_base(jar, base), c['hue'], c['sat'], c['val'], 0.40)
            name = {'block': f"{c['id']}_block", 'budding': f"budding_{c['id']}",
                    'cluster': f"{c['id']}_cluster", 'shard': f"{c['id']}_shard"}[kind]
            if dry:
                continue
            if kind == 'shard':
                os.makedirs(TEX_ITEM, exist_ok=True)
                os.makedirs(MODEL_ITEM, exist_ok=True)
                img.save(os.path.join(TEX_ITEM, name + '.png'))
                with open(os.path.join(MODEL_ITEM, name + '.json'), 'w', encoding='utf-8') as f:
                    json.dump({'parent': 'minecraft:item/generated',
                               'textures': {'layer0': f'{NS}:item/{name}'}}, f, indent=2)
            else:
                os.makedirs(TEX_BLOCK, exist_ok=True)
                img.save(os.path.join(TEX_BLOCK, name + '.png'))
                if kind == 'cluster':
                    # A cross model, the shape vanilla gives amethyst clusters. Without this
                    # the block renders as a cube -- see the note at the cluster registration.
                    os.makedirs(MODEL_BLOCK, exist_ok=True)
                    with open(os.path.join(MODEL_BLOCK, name + '.json'), 'w',
                              encoding='utf-8') as f:
                        json.dump({'parent': 'minecraft:block/cross',
                                   'textures': {'cross': f'{NS}:block/{name}'}}, f, indent=2)
                        f.write(chr(10))
        print(f"   crystal {c['id']:<12} {c['element']:<7} block/budding/cluster/shard")

    # ---------------------------------------------------------------- registration
    L = ['// Alfheim Reclaimed — crystallised mana',
         '//',
         '// GENERATED by tools/gen_crystals.py from tools/crystals_manifest.json — do not hand-edit.',
         '// Design: alfheim_reclaimed_design/ORE_SUPPLEMENTATION.md §9',
         '//',
         '// Where the ley-lines ran hardest the mana separated by alignment and set as gem.',
         '// A geode is never one crystal: it is the boundary between two.',
         '',
         "StartupEvents.registry('block', event => {"]
    for c in crystals:
        cid, nm = c['id'], c['name']
        L.append(f"    event.create('{NS}:{cid}_block').displayName('{nm} Block')"
                 f".soundType('amethyst').hardness(1.5).resistance(1.5).requiresTool(true)"
                 f".tagBlock('minecraft:mineable/pickaxe').tagBlock('{NS}:crystal_blocks')"
                 f".textureAll('{NS}:block/{cid}_block')")
        # Budding blocks grow clusters on random tick. Vanilla's BuddingAmethystBlock is Java;
        # this reproduces the behaviour with the KubeJS randomTick callback so the crystals are
        # renewable rather than a finite deposit.
        L.append(f"    event.create('{NS}:budding_{cid}').displayName('Budding {nm}')"
                 f".soundType('amethyst').hardness(1.5).resistance(1.5).requiresTool(true)"
                 f".tagBlock('minecraft:mineable/pickaxe').tagBlock('{NS}:budding_crystals')"
                 f".textureAll('{NS}:block/budding_{cid}')"
                 f".randomTick(ctx => growCluster(ctx, '{NS}:{cid}_cluster'))")
        # .model(), NOT .textureAll(). Runtime-proven 2026-09-04 from a player's screenshot:
        # textureAll builds a full CUBE model, so every crystal cluster in the world generated
        # as a solid painted block instead of a crystal. Vanilla's amethyst_cluster is
        # parent minecraft:block/cross, and that is what the generated model below uses.
        # The block and budding forms stay cubes on purpose -- so do vanilla's.
        L.append(f"    event.create('{NS}:{cid}_cluster').displayName('{nm} Cluster')"
                 f".soundType('amethyst_cluster').hardness(1.5).resistance(1.5)"
                 f".requiresTool(true).defaultCutout().notSolid().lightLevel(0.4)"
                 f".tagBlock('minecraft:mineable/pickaxe').tagBlock('{NS}:crystal_clusters')"
                 f".model('{NS}:block/{cid}_cluster')")
    L += ['})', '',
          "StartupEvents.registry('item', event => {"]
    for c in crystals:
        L.append(f"    event.create('{NS}:{c['id']}_shard').displayName('{c['name']} Shard')"
                 f".tooltip('{c['tooltip']}').rarity('uncommon')"
                 f".tag('{NS}:crystal_shards')")
    L += ['})', '']

    # The grow helper is declared after use above, which is fine for a hoisted function
    # declaration, and keeps the generated registry block readable.
    L += [
        '// Vanilla grows amethyst through BuddingAmethystBlock in Java. KubeJS 2001.6.5 has no',
        '// binding for that, but it does expose randomTick with a BlockContainerJS, which is',
        '// enough: pick a face, and if it is air, put a cluster there. Slower than vanilla by',
        '// design — a 1-in-5 roll per random tick per face.',
        'function growCluster(ctx, clusterId) {',
        '    if (ctx.random.nextFloat() > 0.2) return',
        "    const faces = ['up', 'down', 'north', 'south', 'east', 'west']",
        '    const face = faces[ctx.random.nextInt(faces.length)]',
        '    const target = ctx.block.offset(face)',
        "    if (target.id !== 'minecraft:air') return",
        '    target.set(clusterId, { facing: face })',
        '}',
        '',
    ]
    write(STARTUP, '\n'.join(L), dry)

    # ---------------------------------------------------------------- loot
    LL = ['// Alfheim Reclaimed — crystal drops',
          '//',
          '// GENERATED by tools/gen_crystals.py — do not hand-edit.',
          '// Clusters drop shards; blocks drop themselves; budding blocks drop nothing without',
          '// Silk Touch, exactly as vanilla budding amethyst behaves, so a deposit cannot be',
          '// trivially relocated.',
          '',
          'ServerEvents.blockLootTables(event => {']
    for c in crystals:
        cid = c['id']
        LL.append(f"    event.addSimpleBlock('{NS}:{cid}_block')")
        LL.append(f"    event.addSimpleBlock('{NS}:{cid}_cluster', "
                  f"Item.of('{NS}:{cid}_shard', 4))")
        # budding_* deliberately absent here: an empty LootBuilder consumer is an API guess,
        # so the drops-nothing table is written as a datapack file below instead.
    LL += ['', f"    console.info('[Alfheim Reclaimed] {len(crystals)} crystal loot sets registered.')",
           '})', '']
    write(LOOT, '\n'.join(LL), dry)

    # ---------------------------------------------------------------- worldgen
    for g in geodes:
        gid = g['id']
        write_json(os.path.join(DATA, NS, 'worldgen', 'configured_feature',
                                f'geode_{gid}.json'), geode_config(g, p, False), dry)
        write_json(os.path.join(DATA, NS, 'worldgen', 'configured_feature',
                                f'geode_{gid}_marker.json'), geode_config(g, p, True), dry)

        # Deep geode: anchored to the local surface, then pushed 14-28 blocks under it.
        write_json(os.path.join(DATA, NS, 'worldgen', 'placed_feature', f'geode_{gid}.json'), {
            'feature': f'{NS}:geode_{gid}',
            'placement': [
                {'type': 'minecraft:rarity_filter', 'chance': g['rarity']},
                {'type': 'minecraft:in_square'},
                {'type': 'minecraft:heightmap', 'heightmap': 'OCEAN_FLOOR_WG'},
                # TWO offsets, not one. RandomOffsetPlacement bounds its IntProvider to
                # +-16, and a single -28..-14 spread is rejected at load with
                #   Value provider too low: -16 [-28--14]
                # which unbinds the placed_feature and takes world creation down with it.
                # Runtime-proven 2026-09-04; no static check saw it because the JSON is
                # perfectly well-formed. Chaining preserves the design in the docstring --
                # surface-relative, 14 to 28 blocks down -- inside the codec's limits.
                {'type': 'minecraft:random_offset', 'xz_spread': 0,
                 'y_spread': p['depth_max']},
                {'type': 'minecraft:random_offset', 'xz_spread': 0,
                 'y_spread': {'type': 'minecraft:uniform',
                              'value': {'min_inclusive': p['depth_min'] - p['depth_max'],
                                        'max_inclusive': 0}}},
                {'type': 'minecraft:biome'},
            ],
        }, dry)

        # Surface marker: only placed where a budding crystal is genuinely within 32 blocks
        # below. environment_scan aborts the placement when it finds nothing, and it moves
        # only Y — so the second heightmap returns us to the surface at the same x/z.
        write_json(os.path.join(DATA, NS, 'worldgen', 'placed_feature',
                                f'geode_{gid}_marker.json'), {
            'feature': f'{NS}:geode_{gid}_marker',
            'placement': [
                {'type': 'minecraft:count', 'count': p['marker_count']},
                {'type': 'minecraft:in_square'},
                {'type': 'minecraft:heightmap', 'heightmap': 'OCEAN_FLOOR_WG'},
                {'type': 'minecraft:environment_scan',
                 'direction_of_search': 'down',
                 'max_steps': p['scan_steps'],
                 'target_condition': {'type': 'minecraft:matching_block_tag',
                                      'tag': f'{NS}:budding_crystals'},
                 'allowed_search_condition': {'type': 'minecraft:true'}},
                {'type': 'minecraft:heightmap', 'heightmap': 'OCEAN_FLOOR_WG'},
                {'type': 'minecraft:biome'},
            ],
        }, dry)

        # One modifier per geode carrying exactly two features, in order: the geode is placed
        # in local_modifications, the marker in top_layer_modification, so the marker's scan
        # runs after the geode it is looking for already exists.
        write_json(os.path.join(DATA, NS, 'forge', 'biome_modifier',
                                f'geode_{gid}.json'), {
            'type': 'forge:add_features',
            'biomes': g['biomes'],
            'features': f'{NS}:geode_{gid}',
            'step': 'local_modifications',
        }, dry)
        write_json(os.path.join(DATA, NS, 'forge', 'biome_modifier',
                                f'zz_geode_{gid}_marker.json'), {
            'type': 'forge:add_features',
            'biomes': g['biomes'],
            'features': f'{NS}:geode_{gid}_marker',
            'step': 'top_layer_modification',
        }, dry)
        print(f"   geode   {gid:<14} {g['pair'][0]:<11}|{g['pair'][1]:<11} "
              f"rarity 1/{g['rarity']:<3} {len(g['biomes'])} biome(s)")

    # Budding blocks drop nothing without Silk Touch, exactly as vanilla budding amethyst
    # behaves, so a deposit cannot be trivially relocated. Written as a plain datapack table
    # rather than through the loot event: an empty pool list is unambiguous, whereas an empty
    # LootBuilder consumer would be a guess about KubeJS's builder semantics.
    for c in crystals:
        write_json(os.path.join(DATA, NS, 'loot_tables', 'blocks',
                                f'budding_{c["id"]}.json'),
                   {'type': 'minecraft:block', 'pools': []}, dry)

    for tag, vals in (
            ('budding_crystals', [f'{NS}:budding_{c["id"]}' for c in crystals]),
            ('crystal_blocks', [f'{NS}:{c["id"]}_block' for c in crystals]),
            ('crystal_clusters', [f'{NS}:{c["id"]}_cluster' for c in crystals])):
        write_json(os.path.join(DATA, NS, 'tags', 'blocks', f'{tag}.json'),
                   {'replace': False, 'values': vals}, dry)
    write_json(os.path.join(DATA, NS, 'tags', 'items', 'crystal_shards.json'),
               {'replace': False, 'values': [f'{NS}:{c["id"]}_shard' for c in crystals]}, dry)

    jar.close()
    pairs = {frozenset(g['pair']) for g in geodes}
    used = {c for g in geodes for c in g['pair']}
    print(f'\n  {len(crystals)} crystals -> {len(crystals)*3} blocks, {len(crystals)} shards')
    print(f'  {len(geodes)} bifurcated geodes ({len(pairs)} distinct pairs), '
          f'{len(geodes)*2} features, {len(geodes)*2} modifiers')
    print(f'  crystals appearing in at least one geode: {len(used)}/{len(crystals)}')
    missing = [c['id'] for c in crystals if c['id'] not in used]
    if missing:
        print(f'  WARNING unreachable crystals: {missing}')
    # Report PER BIOME, not as a mean over geode types. The mean was the wrong statistic and
    # it hid the problem: it answers "how rare is a typical geode type", which no player ever
    # experiences. A player stands in ONE biome and meets only the types valid there, so the
    # density that matters is the sum over the types sharing that biome -- and the worst biome
    # is what gets reported as "too frequent". The user saw overlapping geodes while this line
    # was printing a reassuring 1-in-5.
    per = {}
    for g in geodes:
        for b in g['biomes']:
            per[b] = per.get(b, 0.0) + 1.0 / g['rarity']
    if per:
        worst_b = max(per, key=per.get)
        worst = per[worst_b]
        med = sorted(per.values())[len(per) // 2]
        print(f'  geode density per biome: densest {worst_b} 1 in {1/worst:.0f} chunks '
              f'({worst * 24:.1f}x vanilla amethyst), median 1 in {1/med:.0f}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
