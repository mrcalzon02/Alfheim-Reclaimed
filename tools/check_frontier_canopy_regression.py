"""Source-only Frontier canopy regression; not a substitute for a Minecraft trial.

The rejected 2026-10-14 natural trial found dreamwood leaves at
(-1340, 94, 621) inside wild_ward_shrine.  Its saved pose maps that block to
local (19, 28, 0).  Verify the *shipped* template still authors air there,
that a supporting floor and clear doorway are authored, and that both
structure codec steps and all six jigsaw pool elements can actually stamp air
AFTER native vegetation.  A synthetic overlay models order only, not engine
placement, terrain fit, or cross-chunk runtime behavior.
"""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'kubejs/data/alfheim'
FAMILY = 'frontier_stewardship'
PIECES = ('green_noble_lodge', 'surveyor_tower', 'forest_waystation',
          'outlying_retreat_hall', 'moon_pool_sanctuary', 'wild_ward_shrine')
CANOPY_AIR = (19, 28, 0)
CANOPY_FLOOR = (19, 8, 0)
JOIN = (15, 9, 30)


def require(condition, detail):
    if not condition:
        raise AssertionError(detail)


def check_settings(spec, pools, natural_set_exists):
    require(not natural_set_exists, 'Frontier natural structure set must remain disabled')
    require(spec.get('type') == 'alfheim_companion:remote_district',
            'Frontier outer codec drift')
    require(spec.get('step') == spec.get('layout', {}).get('step') == 'top_layer_modification',
            'Frontier must stamp after vegetal_decoration in both codec settings')
    require(spec.get('terrain_adaptation') == spec['layout'].get('terrain_adaptation') == 'beard_thin',
            'Frontier terrain adaptation drift')
    for name in PIECES:
        pool = pools[name]
        elements = pool.get('elements', [])
        require(len(elements) == 1 and elements[0].get('weight') == 1,
                ('Frontier pool must have one authored member', name))
        element = elements[0].get('element', {})
        require(element.get('element_type') == 'minecraft:single_pool_element'
                and element.get('processors') == 'minecraft:empty'
                and element.get('projection') == 'rigid'
                and element.get('location') == f'alfheim:ancient/{FAMILY}/{name}',
                ('Frontier pool must place explicit air, not ignore it', name))


def check_shrine(cells):
    require(cells.get(CANOPY_AIR) == 'minecraft:air',
            ('2026-10-14 leaf intrusion is not authored air', CANOPY_AIR, cells.get(CANOPY_AIR)))
    require(cells.get(CANOPY_FLOOR) not in (None, 'minecraft:air', 'minecraft:water'),
            ('missing shrine floor beneath the intrusion', CANOPY_FLOOR))
    require(cells.get(JOIN) == 'minecraft:jigsaw'
            and cells.get((JOIN[0], JOIN[1] + 1, JOIN[2])) == 'minecraft:air'
            and cells.get((JOIN[0], JOIN[1] - 1, JOIN[2])) not in (None, 'minecraft:air', 'minecraft:water'),
            ('shrine entry lacks clear headroom or supporting floor', JOIN))
    # In the recorded shrine pose (origin -1340,66,602, rotation 1), local
    # (x,y,z) becomes (-z,y,x). This is an exact coordinate check, not a
    # guess from the old error string.
    world = (-1340 - CANOPY_AIR[2], 66 + CANOPY_AIR[1], 602 + CANOPY_AIR[0])
    require(world == (-1340, 94, 621), ('regression pose drift', world))
    # Overlay the same native leaf before vs after the authored template. Only
    # the first order clears the intrusion. This proves the data-side contract,
    # NOT that the engine respects it at a chunk boundary.
    preexisting = {CANOPY_AIR: 'mythicbotany:dreamwood_leaves'}
    preexisting.update({CANOPY_AIR: cells[CANOPY_AIR]})
    require(preexisting[CANOPY_AIR] == 'minecraft:air', 'post-vegetation air failed')
    preexisting[CANOPY_AIR] = 'mythicbotany:dreamwood_leaves'
    require(preexisting[CANOPY_AIR] != 'minecraft:air', 'negative order control failed')


def check(root=ROOT):
    import nbt  # project-local parser; no third-party jar or Minecraft dependency
    data = root / 'kubejs/data/alfheim'
    spec = json.loads((data / f'worldgen/structure/{FAMILY}.json').read_text(encoding='utf-8'))
    pools = {name: json.loads((data / f'worldgen/template_pool/ancient/{FAMILY}/{name}.json').read_text(encoding='utf-8'))
             for name in PIECES}
    natural_set = (data / f'worldgen/structure_set/{FAMILY}.json').exists()
    check_settings(spec, pools, natural_set)
    path = data / f'structures/ancient/{FAMILY}/wild_ward_shrine.nbt'
    piece = nbt.load(str(path))[1]
    require(tuple(map(int, piece['size'])) == (31, 30, 31), 'shrine template dimensions drift')
    cells = {}
    for block in piece['blocks']:
        point = tuple(map(int, block['pos']))
        require(point not in cells, ('duplicate template cell', point))
        cells[point] = piece['palette'][int(block['state'])]['Name']
    check_shrine(cells)
    # Inspect authored air along recorded chunk seams; do not confuse this
    # source coverage with actual cross-chunk foliage clearance in a save.
    seam_air = sum(name == 'minecraft:air' and y >= 9 and
                   ((-1340-z) % 16 == 0 or (602+x) % 16 == 0)
                   for (x,y,z),name in cells.items())
    require(seam_air > 0, 'shrine has no authored air crossing recorded chunk seams')
    print(f'FRONTIER CANOPY SOURCE PASS: six air-stamping pools, recorded leaf cell, '
          f'floor and shrine join; {seam_air} seam-adjacent authored air cells; '
          'Minecraft runtime NOT tested')


def self_test():
    spec = {'type':'alfheim_companion:remote_district', 'step':'top_layer_modification',
            'terrain_adaptation':'beard_thin',
            'layout':{'step':'top_layer_modification', 'terrain_adaptation':'beard_thin'}}
    pools = {name:{'elements':[{'weight':1,'element':{
        'element_type':'minecraft:single_pool_element', 'processors':'minecraft:empty',
        'projection':'rigid', 'location':f'alfheim:ancient/{FAMILY}/{name}'}}]}
             for name in PIECES}
    cells = {CANOPY_AIR:'minecraft:air', CANOPY_FLOOR:'minecraft:stone',
             JOIN:'minecraft:jigsaw', (JOIN[0],JOIN[1]+1,JOIN[2]):'minecraft:air',
             (JOIN[0],JOIN[1]-1,JOIN[2]):'minecraft:stone'}
    check_settings(spec,pools,False)
    check_shrine(cells)
    mutations = []
    for key in ('outer','layout'):
        bad = copy.deepcopy(spec)
        if key == 'outer': bad['step'] = 'surface_structures'
        else: bad['layout']['step'] = 'surface_structures'
        mutations.append((bad,pools,False,cells))
    badp = copy.deepcopy(pools)
    badp['wild_ward_shrine']['elements'][0]['element']['element_type'] = 'minecraft:legacy_single_pool_element'
    mutations.append((spec,badp,False,cells))
    mutations.append((spec,pools,True,cells))
    for pos,block in ((CANOPY_AIR,'mythicbotany:dreamwood_leaves'),
                      (CANOPY_FLOOR,'minecraft:air'),
                      (JOIN,'minecraft:air')):
        badc = dict(cells);badc[pos] = block
        mutations.append((spec,pools,False,badc))
    for index,(s,p,n,c) in enumerate(mutations):
        try:
            check_settings(s,p,n)
            check_shrine(c)
        except AssertionError:
            continue
        raise AssertionError(('mutation was not rejected',index))
    print(f'FRONTIER CANOPY SELF-TEST PASS: positive fixture + {len(mutations)} rejected mutations')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test',action='store_true')
    args = parser.parse_args()
    if args.self_test:self_test()
    else:check()
