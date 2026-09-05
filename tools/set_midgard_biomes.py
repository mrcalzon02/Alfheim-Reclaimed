"""Toggle which TerraBlender regions populate Midgard (`minecraft:overworld`).

WHY THIS IS A TOOL AND NOT A DATAPACK
-------------------------------------
TerraBlender decides how much of the Overworld each mod's biome region gets from **weights read
out of TOML config at mod load**. No datapack can reach them: by the time a datapack is parsed the
regions are already registered and weighted. So the project owns the switch the same way it owns
every other generated artifact -- through a re-runnable tool that writes the files and reads them
back -- rather than through hand-edited config that drifts and is never recorded.

WHAT THE WEIGHTS ARE, AS SHIPPED
--------------------------------
    minecraft:overworld                          10   config/terrablender.toml
    regions_unexplored:primary                   11   config/regions_unexplored/ru-common.toml
    regions_unexplored:secondary                  8   same
    regions_unexplored:rare                       1   same
    continuityworks_biomes:overworld_templates    3   config/continuityworks-biomes-common.toml
    ars_nouveau:overworld                         ?   HARDCODED -- see below

Continuity Works therefore gets roughly 3/33 of Midgard, and its ~144 biomes share that slice.
Any one of them lands on the order of 0.06% of the world, which is why a 2 km walk finds none.
That is arithmetic, not a defect.

THE ONE REGION THIS CANNOT TURN OFF
-----------------------------------
`ars_nouveau:overworld` (`ArchwoodRegion`) registers in code and ships no config key. `cw-only`
therefore means *Continuity Works plus Ars Nouveau archwood*, not Continuity Works alone. Removing
Ars is not an option -- it is the Spine of Song -- and archwood in Midgard is arguably wanted,
since the pack already plants archwood in Alfheim. Stated so it is a decision and not a surprise.

    python tools/set_midgard_biomes.py --show
    python tools/set_midgard_biomes.py --mode cw-only
    python tools/set_midgard_biomes.py --mode mixed     # back to the shipped defaults

Close the game first. Forge rewrites its config files on shutdown, and a running instance will
overwrite whatever this writes.
"""
import argparse
import os
import re

TERRABLENDER = os.path.join('config', 'terrablender.toml')
RU = os.path.join('config', 'regions_unexplored', 'ru-common.toml')
CW = os.path.join('config', 'continuityworks-biomes-common.toml')

# key -> (file, value in cw-only mode, value in mixed mode)
KEYS = {
    'vanilla_overworld_region_weight': (TERRABLENDER, 0, 10),
    'primary_region_weight':           (RU, 0, 11),
    'secondary_region_weight':         (RU, 0, 8),
    'rare_region_weight':              (RU, 0, 1),
    # CW's own range is 1..20, so it cannot be zeroed -- in cw-only it is simply the loudest voice.
    'regionWeight':                    (CW, 20, 3),
}

# Deliberately untouched: the Nether. `vanilla_nether_region_weight` and RU's
# `nether_region_weight` govern a dimension this switch says nothing about.
UNTOUCHED = ['vanilla_nether_region_weight', 'nether_region_weight']


def read_value(path, key):
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            m = re.match(r'\s*%s\s*=\s*(-?\d+)\s*$' % re.escape(key), line)
            if m:
                return int(m.group(1))
    return None


def write_value(path, key, value):
    """Rewrite one key in place, preserving comments, indentation and every other line."""
    with open(path, encoding='utf-8', newline='') as fh:
        text = fh.read()
    pattern = re.compile(r'(?m)^(\s*%s\s*=\s*)(-?\d+)(\s*)$' % re.escape(key))
    if not pattern.search(text):
        return None, 'key not found'
    old = [int(m.group(2)) for m in pattern.finditer(text)]
    if len(old) != 1:
        return None, 'key appears %d times, refusing to guess' % len(old)
    new_text = pattern.sub(lambda m: '%s%d%s' % (m.group(1), value, m.group(3)), text)
    if new_text == text:
        return old[0], 'already %d' % value
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(new_text)
    return old[0], 'set to %d' % value


def show():
    print('  %-34s %-52s %s' % ('key', 'file', 'value'))
    print('  ' + '-' * 100)
    for key, (path, _cw, _mix) in KEYS.items():
        v = read_value(path, key)
        print('  %-34s %-52s %s' % (key, path, 'MISSING' if v is None else v))
    print()
    for key in UNTOUCHED:
        for path in (TERRABLENDER, RU):
            v = read_value(path, key)
            if v is not None:
                print('  (untouched, Nether)  %-28s %-40s %s' % (key, path, v))
    print()
    print('  ars_nouveau:overworld  -- registered in code, no config key, cannot be weighted here')

    total = 0
    parts = []
    for key, (path, _c, _m) in KEYS.items():
        v = read_value(path, key)
        if v:
            total += v
            parts.append('%s %d' % (key.replace('_region_weight', '').replace('regionWeight', 'continuityworks'), v))
    if total:
        cw = read_value(CW, 'regionWeight') or 0
        print('\n  configured overworld weight total (excluding ars): %d' % total)
        print('  Continuity Works share: %d/%d = %.0f%% of Midgard'
              % (cw, total, 100.0 * cw / total))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['cw-only', 'mixed'],
                    help='cw-only: silence vanilla and Regions Unexplored in the Overworld. '
                         'mixed: restore the shipped defaults.')
    ap.add_argument('--show', action='store_true', help='report the current weights and exit')
    a = ap.parse_args()

    missing = [p for p in (TERRABLENDER, RU, CW) if not os.path.exists(p)]
    if missing:
        print('!! config file(s) not written yet -- launch the game once: %s' % missing)
        return 2

    if a.show or not a.mode:
        print('\nCurrent Midgard region weights\n')
        show()
        return 0

    idx = 1 if a.mode == 'cw-only' else 2
    print('\nSetting Midgard to: %s\n' % a.mode)
    failed = 0
    for key, spec in KEYS.items():
        path, target = spec[0], spec[idx]
        old, note = write_value(path, key, target)
        if old is None:
            print('  !! %-32s %s  (%s)' % (key, path, note))
            failed += 1
        else:
            print('  %-32s %-52s %s -> %s' % (key, path, old, note))

    print('\nRead back:\n')
    show()

    if failed:
        print('\nRESULT: %d key(s) could not be written' % failed)
        return 1

    print("""
NEXT, AND NONE OF IT IS OPTIONAL:
  1. This changes GENERATION ONLY, and only for chunks not yet generated. An existing world keeps
     the biomes already baked into its region files. Test in a NEW world.
  2. Verify in game rather than assuming. `/locate biome continuityworks_biomes:terraced_vineyard`
     should now answer from close by.
  3. Check what vanilla took with it: `/locate biome minecraft:ocean` and `minecraft:river`. If
     TerraBlender does not backfill the parameter space vanilla was covering, Midgard may lose
     oceans, rivers or beaches -- that is the real risk of this switch and it can only be settled
     by generating a world.
  4. Regions Unexplored now generates nothing. 170 biomes of dead weight: either accept it as
     disabled-but-installed, or remove the mod (BACKLOG B-05, which this reopens).""")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
