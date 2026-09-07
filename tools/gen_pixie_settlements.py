"""Generate the four seasonal Feywild pixie sky-island settlements.

Design: alfheim_reclaimed_design/PIXIE_SETTLEMENTS.md
Checker: tools/check_pixie_settlements.py

The island is the jigsaw start piece. Its entire bounding box ends one block above the
ground plane, so six upward-facing sockets can attach without intersecting it: one dew
well, three randomized houses, one functional garden and one seasonal tree. The pixie
spawner is deliberately part of the island core rather than the decorative well piece;
that keeps the spawner exactly below the civic centre even if child placement changes.
"""
import hashlib
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402
from structure_nbt import MAX_AXIS, Piece  # noqa: E402

NS = 'alfheim'
DATA = os.path.join('kubejs', 'data', NS)
STRUCT = os.path.join(DATA, 'structures', 'pixie')
SURFACE_Y = 8
SKY_Y = 208


def B(name, **props):
    if not props:
        return (name, None)
    return (name, {k: ('true' if v else 'false') if isinstance(v, bool) else str(v)
                   for k, v in props.items()})


AIR = B('minecraft:air')
WATER = B('minecraft:water', level=0)
FARMLAND = B('minecraft:farmland', moisture=7)


CULTURES = {
    'spring': {
        'entity': 'feywild:spring_pixie',
        'biomes': ['alfheim:bloomfall_vale', 'mythicbotany:alfheim_plains'],
        'wood': 'feywild:spring_tree_planks', 'log': 'feywild:spring_tree_log',
        'leaves': ['feywild:spring_tree_leaves_green', 'feywild:spring_tree_leaves_lime',
                   'feywild:spring_tree_leaves_cyan'],
        'sapling': 'feywild:spring_tree_sapling',
        'surface': 'minecraft:grass_block', 'soil': 'minecraft:rooted_dirt',
        'accent': 'minecraft:mossy_cobblestone', 'light': 'minecraft:lantern',
        'flowers': ['minecraft:pink_tulip', 'minecraft:allium', 'minecraft:azure_bluet'],
        'crops': [('minecraft:carrots', 7), ('minecraft:beetroots', 3)],
        'roof': 'minecraft:flowering_azalea_leaves',
    },
    'summer': {
        'entity': 'feywild:summer_pixie',
        'biomes': ['mythicbotany:golden_fields'],
        'wood': 'feywild:summer_tree_planks', 'log': 'feywild:summer_tree_log',
        'leaves': ['feywild:summer_tree_leaves_yellow', 'feywild:summer_tree_leaves_orange'],
        'sapling': 'feywild:summer_tree_sapling',
        'surface': 'minecraft:grass_block', 'soil': 'minecraft:dirt',
        'accent': 'minecraft:cut_sandstone', 'light': 'minecraft:lantern',
        'flowers': ['minecraft:dandelion', 'minecraft:orange_tulip', 'minecraft:oxeye_daisy'],
        'crops': [('minecraft:wheat', 7), ('minecraft:melon_stem', 7)],
        'roof': 'minecraft:honeycomb_block',
    },
    'autumn': {
        'entity': 'feywild:autumn_pixie',
        'biomes': ['alfheim:ashen_grove', 'alfheim:silverbark_wood'],
        'wood': 'feywild:autumn_tree_planks', 'log': 'feywild:autumn_tree_log',
        'leaves': ['feywild:autumn_tree_leaves_red', 'feywild:autumn_tree_leaves_brown',
                   'feywild:autumn_tree_leaves_light_gray'],
        'sapling': 'feywild:autumn_tree_sapling',
        'surface': 'minecraft:podzol', 'soil': 'minecraft:coarse_dirt',
        'accent': 'minecraft:mud_bricks', 'light': 'minecraft:lantern',
        'flowers': ['minecraft:orange_tulip', 'minecraft:red_tulip', 'minecraft:brown_mushroom'],
        'crops': [('minecraft:potatoes', 7), ('minecraft:pumpkin_stem', 7)],
        'roof': 'minecraft:hay_block',
    },
    'winter': {
        'entity': 'feywild:winter_pixie',
        'biomes': ['alfheim:starved_reach', 'mythicbotany:alfheim_hills'],
        'wood': 'feywild:winter_tree_planks', 'log': 'feywild:winter_tree_log',
        'leaves': ['feywild:winter_tree_leaves_blue', 'feywild:winter_tree_leaves_light_blue'],
        'sapling': 'feywild:winter_tree_sapling',
        'surface': 'minecraft:snow_block', 'soil': 'minecraft:dirt',
        'accent': 'minecraft:packed_ice', 'light': 'minecraft:soul_lantern',
        'flowers': ['minecraft:blue_orchid', 'minecraft:cornflower'],
        'crops': [('minecraft:potatoes', 7), ('minecraft:beetroots', 3)],
        'roof': 'minecraft:blue_ice',
    },
}


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def save_piece(path, piece):
    assert max(piece.size) <= MAX_AXIS, f'{path}: {piece.size} exceeds structure-block limit'
    assert piece.dropped == 0, f'{path}: {piece.dropped} blocks fell outside {piece.size}'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    nbt.save(path, '', piece.to_nbt())


def box(p, x0, y0, z0, x1, y1, z1, block):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                p.set(x, y, z, block)


def spawner(entity):
    return B('minecraft:spawner'), {
        'id': 'minecraft:mob_spawner',
        'Delay': nbt.Short(80),
        'MinSpawnDelay': nbt.Short(500),
        'MaxSpawnDelay': nbt.Short(1100),
        'SpawnCount': nbt.Short(1),
        'MaxNearbyEntities': nbt.Short(4),
        'RequiredPlayerRange': nbt.Short(16),
        'SpawnRange': nbt.Short(3),
        'SpawnData': {'entity': {'id': entity}},
    }


def edge_radius(kind, angle):
    phase = list(CULTURES).index(kind) * 0.71
    return 14.1 + 0.85 * math.sin(angle * 3 + phase) + 0.55 * math.sin(angle * 7 - phase)


def island_core(kind, c):
    """Organic floating landform, hidden spawner vault and six upward sockets."""
    p = Piece(33, 10, 33)
    cx = cz = 16
    for x in range(33):
        for z in range(33):
            dx, dz = x - cx, z - cz
            d = math.hypot(dx, dz)
            edge = edge_radius(kind, math.atan2(dz, dx))
            if d > edge:
                continue
            thickness = min(8, 2 + int(max(0.0, edge - d) * 0.48))
            bottom = max(0, SURFACE_Y - thickness)
            for y in range(bottom, SURFACE_Y + 1):
                if y == SURFACE_Y:
                    block = B(c['surface'])
                elif y >= SURFACE_Y - 2:
                    block = B(c['soil'])
                else:
                    block = B('botania:livingrock')
                p.set(x, y, z, block)

    # A few tapered root/stone pendants break the otherwise bowl-like underside.
    for i, (x, z, length) in enumerate(((16, 16, 5), (10, 15, 3), (23, 18, 4),
                                        (14, 24, 3), (20, 9, 2))):
        block = B(c['log'], axis='y') if i in (1, 3) else B('botania:livingrock')
        for y in range(max(0, SURFACE_Y - length - 3), SURFACE_Y - 2):
            p.set(x, y, z, block)

    # Serviceable 5x5 spawner vault. The shaft emerges behind the dew well, not in its basin.
    brick = B('botania:livingrock_bricks')
    box(p, 13, 2, 13, 19, 2, 19, brick)
    for y in range(3, 8):
        for x in range(13, 20):
            for z in range(13, 20):
                p.set(x, y, z, brick if x in (13, 19) or z in (13, 19) else AIR)
    box(p, 13, 8, 13, 19, 8, 19, brick)
    # East service shaft and chamber opening. Ladder faces west and is backed by island stone.
    for y in range(3, 10):
        p.set(19, y, 16, AIR)
        if y < 9:
            p.set(19, y, 16, B('minecraft:ladder', facing='west', waterlogged=False))
    p.set(18, 4, 16, AIR)
    p.set(18, 5, 16, AIR)
    p.set(16, 3, 16, B(c['accent']))
    p.set(16, 4, 16, *spawner(c['entity']))
    for x, z in ((14, 14), (18, 14), (14, 18), (18, 18)):
        p.set(x, 4, z, B('minecraft:iron_bars', north=False, south=False,
                         east=False, west=False, waterlogged=False))

    # Player-scale paths remain readable even though the houses are deliberately tiny.
    path = B(c['wood'] + '_slab', type='bottom', waterlogged=False)
    for x in range(8, 26):
        p.set(x, 9, 16, path)
    for z in range(8, 27):
        p.set(16, 9, z, path)
    for t in range(9):
        p.set(16 - t, 9, 16 - t, path)
        p.set(16 + t, 9, 16 - min(t, 8), path)
        p.set(16 - min(t, 8), 9, 16 + t, path)

    sockets = [
        ((16, 9, 16), 'centre', 'centre', f'{NS}:pixie/{kind}/centre'),
        ((8, 9, 8), 'house_socket', 'house', f'{NS}:pixie/{kind}/houses'),
        ((25, 9, 8), 'house_socket', 'house', f'{NS}:pixie/{kind}/houses'),
        ((8, 9, 24), 'house_socket', 'house', f'{NS}:pixie/{kind}/houses'),
        ((25, 9, 17), 'garden_socket', 'garden', f'{NS}:pixie/{kind}/garden'),
        ((17, 9, 27), 'tree_socket', 'tree', f'{NS}:pixie/{kind}/tree'),
    ]
    for (x, y, z), name, target, pool in sockets:
        p.jigsaw(x, y, z, f'{NS}:pixie_{name}', f'{NS}:pixie_{target}', pool,
                 'up_north', joint='aligned', final_state=c['log'])
    return p


def centre_piece(kind, c):
    """The seasonal civic centre: four readings of one shared dew-well grammar."""
    p = Piece(9, 7, 9)
    wood, accent = B(c['wood']), B(c['accent'])
    for x in range(1, 8):
        for z in range(1, 8):
            if math.hypot(x - 4, z - 4) <= 4.1:
                p.set(x, 0, z, wood)
    # Well ring, basin and four culture-marking posts.
    for x in range(2, 7):
        for z in range(2, 7):
            d = math.hypot(x - 4, z - 4)
            if 1.6 < d < 3.1:
                p.set(x, 1, z, accent)
            elif d <= 1.6:
                p.set(x, 1, z, WATER)
    for x, z in ((2, 2), (6, 2), (2, 6), (6, 6)):
        p.set(x, 1, z, B(c['log'], axis='y'))
        p.set(x, 2, z, B(c['log'], axis='y'))
        p.set(x, 3, z, B(c['log'], axis='y'))
    roof = B(c['roof'])
    if kind == 'spring':
        for x in range(1, 8):
            for z in range(1, 8):
                if math.hypot(x - 4, z - 4) <= 4.2:
                    p.set(x, 4, z, roof)
        p.set(4, 5, 4, B('minecraft:flowering_azalea'))
    elif kind == 'summer':
        for x in range(2, 7):
            p.set(x, 4, 2, roof); p.set(x, 4, 6, roof)
        for z in range(3, 6):
            p.set(2, 4, z, roof); p.set(6, 4, z, roof)
        p.set(4, 5, 4, B('minecraft:gold_block'))
    elif kind == 'autumn':
        for x in range(1, 8):
            for z in range(2, 7):
                p.set(x, 4 + (1 if x in (3, 4, 5) else 0), z, roof)
    else:
        for x in range(1, 8):
            for z in range(1, 8):
                if abs(x - 4) + abs(z - 4) <= 4:
                    p.set(x, 4, z, roof)
        p.set(4, 5, 4, B('minecraft:end_rod', facing='up'))
    for x, z in ((2, 4), (6, 4), (4, 2), (4, 6)):
        p.set(x, 2, z, B(c['light'], hanging=False, waterlogged=False))

    # An open, visually discreet maintenance hatch aligns to the island's ladder shaft.
    p.set(7, 0, 4, B(c['wood'] + '_trapdoor', facing='east', half='bottom',
                     open=True, powered=False, waterlogged=False))
    # Connectors are always the final write: geometry at y=0 must not silently replace them.
    p.jigsaw(4, 0, 4, f'{NS}:pixie_centre', 'minecraft:empty', 'minecraft:empty',
             'down_north', joint='aligned', final_state=c['accent'])
    return p


def house_piece(kind, c, variant):
    p = Piece(7, 8, 7)
    wood = B(c['wood'])
    log = B(c['log'], axis='y')
    slab = B(c['wood'] + '_slab', type='bottom', waterlogged=False)
    stair_n = B(c['wood'] + '_stairs', facing='north', half='bottom', shape='straight', waterlogged=False)
    stair_s = B(c['wood'] + '_stairs', facing='south', half='bottom', shape='straight', waterlogged=False)
    if variant == 0:  # steep little cottage
        box(p, 1, 0, 1, 5, 0, 5, wood)
        for x in range(1, 6):
            for y in range(1, 4):
                for z in (1, 5): p.set(x, y, z, wood)
        for z in range(2, 5):
            for y in range(1, 4):
                for x in (1, 5): p.set(x, y, z, wood)
        for x, z in ((1, 1), (5, 1), (1, 5), (5, 5)):
            for y in range(1, 4): p.set(x, y, z, log)
        p.set(3, 1, 1, AIR); p.set(3, 2, 1, AIR)
        for x in range(0, 7):
            p.set(x, 4, 2, stair_n); p.set(x, 4, 4, stair_s)
            p.set(x, 5, 3, slab)
    elif variant == 1:  # narrow lantern loft
        box(p, 2, 0, 2, 4, 0, 4, wood)
        for y in range(1, 6):
            for x, z in ((2, 2), (4, 2), (2, 4), (4, 4)): p.set(x, y, z, log)
        for y in range(1, 5):
            p.set(2, y, 3, wood); p.set(4, y, 3, wood); p.set(3, y, 4, wood)
        p.set(3, 1, 2, AIR); p.set(3, 2, 2, AIR)
        box(p, 1, 4, 1, 5, 4, 5, slab)
        for x in range(0, 7):
            p.set(x, 6, 2, stair_n); p.set(x, 6, 4, stair_s)
            p.set(x, 7, 3, slab)
    elif variant == 2:  # leaf-capped tree home
        for y in range(0, 5): p.set(3, y, 3, log)
        box(p, 1, 2, 1, 5, 2, 5, wood)
        for x, z in ((1, 1), (5, 1), (1, 5), (5, 5)):
            p.set(x, 3, z, log); p.set(x, 4, z, log)
        for x in range(1, 6):
            p.set(x, 3, 1, wood); p.set(x, 3, 5, wood)
        for z in range(2, 5):
            p.set(1, 3, z, wood); p.set(5, 3, z, wood)
        p.set(3, 3, 1, AIR); p.set(3, 4, 1, AIR)
        for x in range(0, 7):
            for z in range(0, 7):
                if math.hypot(x - 3, z - 3) <= 3.6:
                    p.set(x, 5 + (1 if abs(x - 3) + abs(z - 3) < 3 else 0), z,
                          B(c['leaves'][(x + z) % len(c['leaves'])], persistent=True, distance=1))
    else:  # low communal pantry
        box(p, 0, 0, 1, 6, 0, 5, wood)
        for x in range(0, 7):
            for y in range(1, 4):
                p.set(x, y, 1, log if x in (0, 6) else wood)
                p.set(x, y, 5, log if x in (0, 6) else wood)
        for z in range(2, 5):
            for y in range(1, 4):
                p.set(0, y, z, wood); p.set(6, y, z, wood)
        p.set(3, 1, 1, AIR); p.set(3, 2, 1, AIR)
        for x in range(0, 7):
            p.set(x, 4, 1, stair_n); p.set(x, 4, 5, stair_s)
            for z in range(2, 5): p.set(x, 5, z, slab)

    # Each home gets one culture-specific, non-container interior marker.
    decor = {'spring': 'minecraft:potted_allium', 'summer': 'minecraft:cake',
             'autumn': 'minecraft:carved_pumpkin', 'winter': 'minecraft:soul_lantern'}[kind]
    p.set(3, 1 if variant != 2 else 3, 4, B(decor, hanging=False, waterlogged=False))
    p.jigsaw(3, 0, 3, f'{NS}:pixie_house', 'minecraft:empty', 'minecraft:empty',
             'down_north', joint='aligned', final_state=c['wood'])
    return p


def garden_piece(kind, c):
    p = Piece(9, 4, 9)
    for x in range(1, 8):
        for z in range(1, 8):
            if x in (1, 7) or z in (1, 7):
                p.set(x, 0, z, B(c['wood']))
            elif x == 4:
                p.set(x, 0, z, WATER)
            else:
                p.set(x, 0, z, FARMLAND)
                crop, age = c['crops'][(x + z) % 2]
                p.set(x, 1, z, B(crop, age=age))
    if kind == 'summer':
        p.set(2, 1, 2, B('minecraft:melon')); p.set(6, 1, 6, B('minecraft:melon'))
    elif kind == 'autumn':
        p.set(2, 1, 2, B('minecraft:pumpkin')); p.set(6, 1, 6, B('minecraft:pumpkin'))
    elif kind == 'winter':
        # A tiny coldframe makes the winter food plot believable and keeps its light readable.
        for x in range(0, 9):
            p.set(x, 2, 0, B('minecraft:glass_pane')); p.set(x, 2, 8, B('minecraft:glass_pane'))
        for z in range(1, 8):
            p.set(0, 2, z, B('minecraft:glass_pane')); p.set(8, 2, z, B('minecraft:glass_pane'))
        for x in range(0, 9):
            for z in range(0, 9): p.set(x, 3, z, B('minecraft:glass'))
        p.set(4, 2, 4, B('minecraft:lantern', hanging=True, waterlogged=False))
    p.jigsaw(4, 0, 4, f'{NS}:pixie_garden', 'minecraft:empty', 'minecraft:empty',
             'down_north', joint='aligned', final_state='minecraft:water')
    return p


def tree_piece(kind, c):
    p = Piece(11, 12, 11)
    for x in range(2, 9):
        for z in range(2, 9):
            if math.hypot(x - 5, z - 5) <= 3.8:
                p.set(x, 0, z, B(c['soil']))
    for y in range(0, 7): p.set(5, y, 5, B(c['log'], axis='y'))
    for y, radius in ((5, 3.6), (6, 4.3), (7, 3.7), (8, 2.8), (9, 1.5)):
        for x in range(11):
            for z in range(11):
                if math.hypot(x - 5, z - 5) <= radius:
                    leaf = c['leaves'][(x + z + y) % len(c['leaves'])]
                    p.set(x, y, z, B(leaf, persistent=True, distance=1))
    p.set(5, 10, 5, B(c['leaves'][0], persistent=True, distance=1))
    p.set(2, 1, 5, B(c['sapling'], stage=0))
    for i, flower in enumerate(c['flowers'][:2]):
        p.set(7, 1, 4 + i * 2, B(flower))
    p.jigsaw(5, 0, 5, f'{NS}:pixie_tree', 'minecraft:empty', 'minecraft:empty',
             'down_north', joint='aligned', final_state=c['log'])
    return p


def pool(name, locations):
    return {'name': name, 'fallback': 'minecraft:empty', 'elements': [
        {'weight': weight, 'element': {'location': location, 'processors': 'minecraft:empty',
                                      'projection': 'rigid',
                                      'element_type': 'minecraft:single_pool_element'}}
        for location, weight in locations
    ]}


def salt_for(kind):
    return int(hashlib.sha1(f'pixie-{kind}'.encode()).hexdigest()[:7], 16)


def main():
    total = 0
    for kind, c in CULTURES.items():
        base = os.path.join(STRUCT, kind)
        pieces = {
            'core': island_core(kind, c),
            'centre': centre_piece(kind, c),
            'garden': garden_piece(kind, c),
            'tree': tree_piece(kind, c),
        }
        for i in range(4): pieces[f'house_{i + 1}'] = house_piece(kind, c, i)
        for name, piece in pieces.items():
            save_piece(os.path.join(base, name + '.nbt'), piece)
            total += len(piece.blocks)

        prefix = f'{NS}:pixie/{kind}'
        pool_dir = os.path.join(DATA, 'worldgen', 'template_pool', 'pixie', kind)
        write_json(os.path.join(pool_dir, 'start.json'), pool(f'{prefix}/start', [(f'{prefix}/core', 1)]))
        write_json(os.path.join(pool_dir, 'centre.json'), pool(f'{prefix}/centre', [(f'{prefix}/centre', 1)]))
        write_json(os.path.join(pool_dir, 'garden.json'), pool(f'{prefix}/garden', [(f'{prefix}/garden', 1)]))
        write_json(os.path.join(pool_dir, 'tree.json'), pool(f'{prefix}/tree', [(f'{prefix}/tree', 1)]))
        write_json(os.path.join(pool_dir, 'houses.json'), pool(
            f'{prefix}/houses', [(f'{prefix}/house_{i}', 1) for i in range(1, 5)]))

        sid = f'pixie_{kind}_hamlet'
        write_json(os.path.join(DATA, 'worldgen', 'structure', sid + '.json'), {
            'type': 'minecraft:jigsaw', 'biomes': f'#{NS}:has_{sid}',
            'step': 'surface_structures', 'terrain_adaptation': 'none',
            'start_pool': f'{prefix}/start', 'size': 1, 'max_distance_from_center': 48,
            'start_height': {'absolute': SKY_Y}, 'use_expansion_hack': False,
            'spawn_overrides': {},
        })
        write_json(os.path.join(DATA, 'worldgen', 'structure_set', sid + '.json'), {
            'structures': [{'structure': f'{NS}:{sid}', 'weight': 1}],
            'placement': {'type': 'minecraft:random_spread', 'spacing': 56, 'separation': 24,
                          'spread_type': 'linear', 'salt': salt_for(kind)},
        })
        write_json(os.path.join(DATA, 'tags', 'worldgen', 'biome', f'has_{sid}.json'),
                   {'replace': False, 'values': c['biomes']})
        print(f'{kind:7} 8 pieces, 5 pools, {c["entity"]}, y={SKY_Y}, biomes={len(c["biomes"])}')
    print(f'generated 32 NBT pieces, 20 pools, 4 structures/sets/tags, {total} placed blocks')
    return 0


if __name__ == '__main__':
    sys.exit(main())
