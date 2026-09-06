"""Validate the native ore tuning and all host-matched variants.

    python tools/check_native_ores.py
"""
import json
import os
import sys

from PIL import Image

from gen_blooms import ore_hosts
from gen_native_ores import DATA, MANIFEST, NS, STARTUP, TEXTURES, variant_id


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def main():
    manifest = read_json(MANIFEST)
    hosts = ore_hosts()
    problems = []

    def fail(message):
        problems.append(message)
        print(f'  FAIL {message}')

    if len(hosts) != 42 or len({h['id'] for h in hosts}) != 42:
        fail(f'host catalog is not 42 unique stones: {len(hosts)} rows')

    try:
        startup = open(STARTUP, encoding='utf-8').read()
    except OSError as exc:
        startup = ''
        fail(f'{STARTUP}: unreadable ({exc})')
    for forbidden in ('ServerEvents.tick', 'PlayerEvents.tick', 'LevelEvents.tick',
                      'setInterval', 'scheduleRepeating'):
        if forbidden in startup:
            fail(f'{STARTUP}: recurring runtime hook {forbidden!r} is forbidden')

    expected_ids = []
    for ore in manifest['ores']:
        namespace = 'mythicbotany' if ore['id'] in ('elementium', 'dragonstone') else NS
        configured_path = os.path.join(
            DATA, namespace, 'worldgen', 'configured_feature', ore['id'] + '_ore.json')
        placed_path = os.path.join(
            DATA, namespace, 'worldgen', 'placed_feature', ore['id'] + '_ore.json')
        try:
            configured = read_json(configured_path)
            placed = read_json(placed_path)
        except (OSError, ValueError) as exc:
            fail(f'{ore["id"]}: worldgen unreadable ({exc})')
            continue

        config = configured.get('config', {})
        if configured.get('type') != 'minecraft:ore':
            fail(f'{ore["id"]}: configured feature is not minecraft:ore')
        if config.get('size') != ore['size']:
            fail(f'{ore["id"]}: vein size {config.get("size")} != {ore["size"]}')
        targets = config.get('targets', [])
        if len(targets) != len(hosts) + 1:
            fail(f'{ore["id"]}: {len(targets)} targets, expected {len(hosts) + 1}')

        exact = {}
        for target in targets[:-1]:
            predicate = target.get('target', {})
            if predicate.get('predicate_type') == 'minecraft:block_match':
                exact[predicate.get('block')] = target.get('state', {}).get('Name')
        expected_exact = {
            f'{NS}:{host["id"]}': f'{NS}:{variant_id(ore, host)}'
            for host in hosts
        }
        if exact != expected_exact:
            fail(f'{ore["id"]}: exact host-to-ore target mapping differs')
        fallback = targets[-1] if targets else {}
        if fallback != {
            'target': {'predicate_type': 'minecraft:tag_match',
                       'tag': 'mythicbotany:base_stone_alfheim'},
            'state': {'Name': ore['base_block']},
        }:
            fail(f'{ore["id"]}: broad Alfheim fallback is absent or not last')

        placements = placed.get('placement', [])
        expected_placed = [
            {'type': 'minecraft:count', 'count': ore['count']},
            {'type': 'minecraft:in_square'},
            {'type': 'minecraft:height_range', 'height': ore['height']},
            {'type': 'minecraft:biome'},
        ]
        if placed.get('feature') != f'{namespace}:{ore["id"]}_ore':
            fail(f'{ore["id"]}: placed feature points at {placed.get("feature")}')
        if placements != expected_placed:
            fail(f'{ore["id"]}: placement count/height/filters differ from manifest')

        for host in hosts:
            vid = variant_id(ore, host)
            expected_ids.append(f'{NS}:{vid}')
            if startup.count(f"event.create('{NS}:{vid}')") != 1:
                fail(f'{vid}: not registered exactly once')

            texture_path = os.path.join(TEXTURES, vid + '.png')
            try:
                with Image.open(texture_path) as image:
                    image.verify()
            except (OSError, ValueError) as exc:
                fail(f'{texture_path}: invalid texture ({exc})')
            if ore['id'] in ('elementium', 'dragonstone'):
                meta_path = texture_path + '.mcmeta'
                try:
                    meta = read_json(meta_path)
                    if len(meta.get('animation', {}).get('frames', [])) != 6:
                        fail(f'{meta_path}: expected six animation frames')
                except (OSError, ValueError) as exc:
                    fail(f'{meta_path}: invalid animation metadata ({exc})')

            loot_path = os.path.join(DATA, NS, 'loot_tables', 'blocks', vid + '.json')
            try:
                loot = read_json(loot_path)
                children = loot['pools'][0]['entries'][0]['children']
                if children[0].get('name') != f'{NS}:{vid}':
                    fail(f'{vid}: Silk Touch does not return its hosted block')
                if children[1].get('name') != ore['drop']:
                    fail(f'{vid}: normal drop is {children[1].get("name")}')
            except (OSError, ValueError, KeyError, IndexError) as exc:
                fail(f'{loot_path}: invalid source-equivalent loot ({exc})')

    if len(expected_ids) != 126 or len(set(expected_ids)) != 126:
        fail(f'expected 126 unique hosted variants, found {len(set(expected_ids))}')

    modifier_path = os.path.join(DATA, NS, 'forge', 'biome_modifier',
                                 'zz_native_fey_gem.json')
    expected_modifier = {
        'type': 'forge:add_features',
        'biomes': manifest['fey_gem_biomes'],
        'features': f'{NS}:fey_gem_ore',
        'step': 'underground_ores',
    }
    try:
        if read_json(modifier_path) != expected_modifier:
            fail('Fey Gem biome modifier differs from the climate-limited manifest')
    except (OSError, ValueError) as exc:
        fail(f'{modifier_path}: unreadable ({exc})')

    print(f'\nAlfheim native ores: {len(problems)} problem(s), '
          f'{len(expected_ids)} hosted variants, startup-only registration')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
