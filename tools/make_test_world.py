"""Build a disposable test world with a chosen Overworld generator, for autonomous worldgen checks.

The world-preset override in `kubejs/data` only takes effect on the world-creation screen, which
needs a human. Writing the generator straight into `level.dat` tests the same question — does this
generator work in the `minecraft:overworld` slot — without one.

    python tools/make_test_world.py                 # build "Alfheim Test" with the Alfheim generator
    python tools/make_test_world.py --vanilla       # control world, stock generator
    python tools/make_test_world.py --name X --seed 123

Copies an existing world's level.dat for its registry/datapack context, swaps the Overworld
generator, and clears region data so everything regenerates.
"""
import argparse
import os
import random
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt

SAVES = 'saves'

ALFHEIM_GENERATOR = {
    'type': 'libx:noise',
    'biome_source': {
        'type': 'libx:layered',
        'layers': '#mythicbotany:alfheim',
    },
    'settings': 'mythicbotany:alfheim',
    'surface_override': 'mythicbotany:alfheim_surface',
}

VANILLA_GENERATOR = {
    'type': 'minecraft:noise',
    'settings': 'minecraft:overworld',
    'biome_source': {
        'type': 'minecraft:multi_noise',
        'preset': 'minecraft:overworld',
    },
}

# Regenerated on next load; removing them forces fresh terrain.
VOLATILE = ('region', 'entities', 'poi', 'DIM-1', 'DIM1', 'dimensions')


def pick_source():
    """Any existing world will do — we only want its registry and datapack context."""
    for name in os.listdir(SAVES):
        p = os.path.join(SAVES, name, 'level.dat')
        if os.path.exists(p):
            return os.path.join(SAVES, name)
    return None


def build(name, generator, seed):
    src = pick_source()
    if not src:
        print('No existing world to use as a template. Create one in-game once, then rerun.')
        return 1
    dst = os.path.join(SAVES, name)

    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f'template : {src}')
    print(f'target   : {dst}')

    for d in VOLATILE:
        p = os.path.join(dst, d)
        if os.path.isdir(p):
            shutil.rmtree(p)
            print(f'  cleared {d}/')
    for f in ('session.lock',):
        p = os.path.join(dst, f)
        if os.path.exists(p):
            os.remove(p)

    lvl = os.path.join(dst, 'level.dat')
    root_name, root = nbt.load(lvl)
    data = root['Data']

    data['LevelName'] = name
    data['Time'] = nbt.Long(0)
    data['DayTime'] = nbt.Long(0)
    data['initialized'] = nbt.Byte(0)          # force spawn re-selection
    data['allowCommands'] = nbt.Byte(1)

    wgs = data['WorldGenSettings']
    wgs['seed'] = nbt.Long(seed)
    ow = wgs['dimensions']['minecraft:overworld']
    before = ow['generator'].get('type')
    ow['generator'] = generator
    print(f'  overworld generator: {before}  ->  {generator["type"]}')
    print(f'  seed: {seed}')

    # Player state carries an old position and dimension; drop it so spawn is chosen fresh.
    data.pop('Player', None)

    nbt.save(lvl, root_name, root)
    old = lvl + '_old'
    if os.path.exists(old):
        os.remove(old)

    # Verify by reading it back rather than trusting the write.
    _, check = nbt.load(lvl)
    got = check['Data']['WorldGenSettings']['dimensions']['minecraft:overworld']['generator']
    ok = got.get('type') == generator['type'] and got.get('settings') == generator.get('settings')
    print(f'  readback: {"OK" if ok else "MISMATCH"} ({got.get("type")}, {got.get("settings")})')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', default=None)
    ap.add_argument('--seed', type=int, default=None)
    ap.add_argument('--vanilla', action='store_true',
                    help='control world with the stock generator')
    a = ap.parse_args()

    gen = VANILLA_GENERATOR if a.vanilla else ALFHEIM_GENERATOR
    name = a.name or ('Vanilla Control' if a.vanilla else 'Alfheim Test')
    seed = a.seed if a.seed is not None else random.getrandbits(48)
    return build(name, gen, seed)


if __name__ == '__main__':
    sys.exit(main())
