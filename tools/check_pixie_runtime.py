"""Verify the four directly placed pixie hamlets in a saved Forge validation world.

Usage:
    python tools/check_pixie_runtime.py --world server/validation-pixie-assembly-0907b

The `--pixie-only` mode in tools/run_server.py owns the four test sites. A successful
`place structure` message proves only that a start was accepted; this checker reads what
Minecraft actually saved and proves that the well, randomized houses, garden, tree and
buried seasonal spawner all survived jigsaw assembly.
"""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from biome_census import chunks  # noqa: E402
from gen_pixie_settlements import CULTURES  # noqa: E402

SITES = {
    'spring': (128, 128),
    'summer': (144, 128),
    'autumn': (160, 128),
    'winter': (176, 128),
}


def section_names(root):
    out = set()
    for section in root.get('sections', []):
        # The test structures run from y=208 through about y=229. Sections 13 and 14
        # therefore contain the village while excluding almost all terrain noise.
        if not 13 <= int(section.get('Y', -99)) <= 14:
            continue
        palette = section.get('block_states', {}).get('palette', [])
        out.update(str(state.get('Name')) for state in palette if state.get('Name'))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--world', default=os.path.join('server', 'validation-pixie-assembly-0907b'))
    a = ap.parse_args()
    region_dir = os.path.join(a.world, 'dimensions', 'mythicbotany', 'alfheim', 'region')
    if not os.path.isdir(region_dir):
        print(f'FAILED: no Alfheim region directory at {region_dir}')
        return 1

    saved = {}
    for path in glob.glob(os.path.join(region_dir, '*.mca')):
        for root in chunks(path):
            saved[(int(root.get('xPos', 999999)), int(root.get('zPos', 999999)))] = root

    failures = []
    for kind, (cx, cz) in SITES.items():
        culture = CULTURES[kind]
        nearby = [saved[(x, z)] for x in range(cx - 2, cx + 3)
                  for z in range(cz - 2, cz + 3) if (x, z) in saved]
        names = set().union(*(section_names(root) for root in nearby)) if nearby else set()
        spawners = [be for root in nearby for be in root.get('block_entities', [])
                    if str(be.get('id')) == 'minecraft:mob_spawner' and int(be.get('y', -999)) >= 200]
        required = {
            culture['wood'], culture['wood'] + '_stairs', culture['log'], culture['sapling'],
            *culture['leaves'], *(crop for crop, _age in culture['crops']),
            'minecraft:farmland', 'minecraft:water', culture['accent'],
        }
        missing = sorted(required - names)
        if missing:
            failures.append(f'{kind}: assembled child-piece blocks missing: {missing}')
        if 'minecraft:jigsaw' in names:
            failures.append(f'{kind}: an exposed/unretired jigsaw block remains in the saved hamlet')
        if len(spawners) != 1:
            failures.append(f'{kind}: expected one high-sky spawner, found {len(spawners)}')
        else:
            be = spawners[0]
            actual = str(be.get('SpawnData', {}).get('entity', {}).get('id'))
            if actual != culture['entity']:
                failures.append(f'{kind}: spawner entity {actual}, expected {culture["entity"]}')
            profile = (int(be.get('SpawnCount', 0)), int(be.get('MaxNearbyEntities', 0)),
                       int(be.get('RequiredPlayerRange', 0)), int(be.get('SpawnRange', 0)))
            if profile != (1, 4, 16, 3):
                failures.append(f'{kind}: spawner profile changed to {profile}')
        print(f'{kind:7} chunks={len(nearby):2} palette={len(names):2} '
              f'spawner={len(spawners)} required={len(required - set(missing))}/{len(required)}')

    if failures:
        print('Pixie runtime assembly check FAILED')
        for problem in failures:
            print('  ' + problem)
        return 1
    print('Pixie runtime assembly check passed')
    print('  4/4 structures contain centre + houses + garden + seasonal tree + bounded spawner')
    return 0


if __name__ == '__main__':
    sys.exit(main())
