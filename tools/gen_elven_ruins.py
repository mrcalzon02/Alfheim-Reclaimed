"""Turn MythicBotany's intact elven houses into the abandoned elven villages of the premise.

Two problems with what the mod ships:

  1. The houses generate pristine. The pack's whole fiction is that Alfheim is a wasteland
     of collapsed tree-cities -- a tidy elven cottage every 24 chunks contradicts the
     opening line of Era I.
  2. They generate ALONE. `elven_house` places one building, and its only outward jigsaw
     leads to a garden. There are no villages, just scattered cottages.

Both are fixed without touching a single NBT, which matters because the pieces are
third-party art we may not modify or redistribute (INSTRUCTIONS.md §5):

  * A `minecraft:block_rot` + rule processor list decays any piece it is applied to --
    shattered elf glass, mossy and cracked livingrock, collapsed dreamwood, cobwebs in
    the gaps. This is BACKLOG B-19: decay procedurally rather than authoring ruins by
    hand, so one intact piece yields both states.
  * `house` and `tower` each carry a jigsaw block NAMED `mythicbotany:entrance`, and the
    entrance connector targets the `gardens` pool. Putting the buildings into that pool
    makes buildings chain to buildings, so a site grows into a cluster. The structure's
    own `size: 5` bounds how far it can spread.

We override MythicBotany's template pools in our datapack rather than editing the jar.

    python tools/gen_elven_ruins.py
"""
import json
import os

OUT = os.path.join('kubejs', 'data')
NS = 'alfheim'
MB = 'mythicbotany'
RUIN = f'{NS}:elven_ruin'

# How much of a building survives. block_rot removes blocks outright; the rules then
# weather what is left. Rules are first-match, so the mossy rule takes 40% of the bricks
# and the cracked rule 30% of the 60% that remain.
INTEGRITY = 0.88

DECAY_RULES = [
    # The windows go first. Nothing reads "abandoned" faster than empty frames.
    ('botania:elf_glass_pane', 0.85, 'minecraft:air'),
    ('botania:elf_glass', 0.60, 'minecraft:air'),
    # Stone weathers rather than vanishing, so walls stay legible as walls.
    ('botania:livingrock_bricks', 0.40, 'botania:mossy_livingrock_bricks'),
    ('botania:livingrock_bricks', 0.30, 'botania:cracked_livingrock_bricks'),
    # Some floors and roofs fall in.
    ('botania:dreamwood_planks', 0.15, 'minecraft:air'),
    # Webs in the interior air. The Ashen Grove spawns spiders; this is where they live.
    ('minecraft:air', 0.05, 'minecraft:cobweb'),
]

# Only blocks with no meaningful blockstate may be swapped: output_state sets Name alone,
# so converting a stair or slab would reset its facing and produce visible nonsense.
STATEFUL = ('_stairs', '_slab', '_wall', '_fence', '_pane')


def processor_list():
    rules = []
    for block, prob, out in DECAY_RULES:
        if out != 'minecraft:air' and block.endswith(STATEFUL):
            raise ValueError(f'{block} carries blockstate; cannot be swapped by name alone')
        rules.append({
            'input_predicate': {'predicate_type': 'minecraft:random_block_match',
                                'block': block, 'probability': prob},
            'location_predicate': {'predicate_type': 'minecraft:always_true'},
            'output_state': {'Name': out},
        })
    return {
        'processors': [
            {'processor_type': 'minecraft:block_rot', 'integrity': INTEGRITY},
            {'processor_type': 'minecraft:rule', 'rules': rules},
        ]
    }


def element(location, weight):
    return {
        'element': {
            'element_type': 'minecraft:single_pool_element',
            'location': location,
            'processors': RUIN,
            'projection': 'rigid',
        },
        'weight': weight,
    }


def empty(weight):
    return {'element': {'element_type': 'minecraft:empty_pool_element'}, 'weight': weight}


def pools():
    """MythicBotany's three pools, decayed, with buildings allowed to chain."""
    buildings = {
        'elements': [
            element(f'{MB}:elven_houses/buildings/house', 2),
            element(f'{MB}:elven_houses/buildings/shed', 1),
            element(f'{MB}:elven_houses/buildings/tower', 1),
        ],
        'fallback': 'minecraft:empty',
    }

    # The entrance connector on house and tower points here. Gardens still dominate so a
    # site reads as a settlement with grounds rather than a wall of houses; the buildings
    # give it the density of a village.
    gardens = {
        'elements': [
            empty(1),
            element(f'{MB}:elven_houses/gardens/flower_garden', 3),
            element(f'{MB}:elven_houses/gardens/crop_garden', 3),
            element(f'{MB}:elven_houses/buildings/house', 2),
            element(f'{MB}:elven_houses/buildings/tower', 1),
        ],
        'fallback': 'minecraft:empty',
    }

    return {
        os.path.join(OUT, NS, 'worldgen', 'processor_list', 'elven_ruin.json'):
            processor_list(),
        os.path.join(OUT, MB, 'worldgen', 'template_pool', 'elven_houses', 'buildings.json'):
            buildings,
        os.path.join(OUT, MB, 'worldgen', 'template_pool', 'elven_houses', 'gardens.json'):
            gardens,
    }


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')
    return path


def main():
    for path, data in pools().items():
        print('  wrote', write(path, data))
    print(f'\nelven houses now generate ruined (integrity {INTEGRITY}) and cluster into '
          f'villages via the entrance connector.')


if __name__ == '__main__':
    main()
