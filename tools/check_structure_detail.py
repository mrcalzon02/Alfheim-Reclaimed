"""Assert the detail floor for every shipping structure in the pack.

Design record: `alfheim_reclaimed_design/THE_SURFACE.md` 3.2, which names the five layers a
ruin has to carry. Vocabulary: `tools/structure_detail.py`. Generators: `gen_surface_works`,
`gen_deep_archaeology`, `gen_spawn_hub`, `gen_leyline_corridors`, `gen_pixie_settlements`.

WHY THIS EXISTS
---------------
"Detail complexity" was a judgement call every previous pass made by eye, and the eye kept
passing structures that a census could not. Before the 2026-09-08 pass, `greatbole/trunk`
shipped **three** block ids across 6,645 blocks and every leyline bend, terminal and hub
carried a zero detail-block share -- and nothing in the repository said so, because nothing
was measuring. A number that nobody checks is a number that drifts back.

So this is a regression gate, not a target. Every floor is set BELOW the value the current
set measures, which means it cannot be satisfied by weakening it later without the diff
saying exactly that. It is also deliberately not a maximum: a piece is free to be as detailed
as its geometry can carry.

WHAT IT DOES NOT DO
-------------------
It does not check attachment -- `check_spawn_hub.py` S11 already sweeps every `.nbt` in the
pack for blocks touching nothing, and a second implementation of that rule would be a second
answer to one question. It does not check block ids either; S2 and `check_surface_works.py`
W2 both do, against different registries, for good reasons.

    python tools/check_structure_detail.py
    python tools/check_structure_detail.py --verbose
    python tools/check_structure_detail.py --self-test
"""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402
import structure_detail as sd  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRUCT = os.path.join(ROOT, 'kubejs', 'data', 'alfheim', 'structures')

# A block that emits light, however it was made. Substring rather than exact id, because the
# families that own most of them are ours and the pack's -- `alfheim:mana_glass_light`,
# `alfheim:dawnglass_cluster`, `alfheim:royal_wall_sconce` -- and enumerating them here would
# be a second catalogue to keep in step with the first.
LIGHT_MARKS = ('lantern', 'torch', 'mana_glass', '_cluster', 'glowstone', 'shroomlight',
               'sconce', 'campfire', 'end_rod', 'candle', 'sea_pickle', 'froglight')

# The "advanced civilisation" layer, which is the one the 2026-09-07 field review said was
# missing outright: crystal, conduit glass and emitters. A family with none of it reads as
# medieval masonry in a different palette, which is the exact phrase the review used.
TECH_MARKS = ('_cluster', 'mana_glass', 'end_rod', 'ley_conduit', 'budding_')

# Per family: the minimum distinct non-air block ids in ANY piece, the minimum detail-block
# share in any piece, and whether the family must show the technology layer somewhere.
#
# Every number is under what the set currently measures (2026-09-08, recorded in
# EXECUTION_STATE.md), so this fires on regression rather than describing an aspiration.
# `greatbole` is the deliberate outlier: a colossal tree is mass by nature, and its evidence
# of care is species variation and growth rather than furniture, so its share floor is low
# and its id floor does the work.
FAMILIES = {
    'surface':               dict(ids=8,  share=0.040, tech=True,  interior_light=60),
    'court':                 dict(ids=18, share=0.025, tech=True,  interior_light=80),
    'greatbole':             dict(ids=5,  share=0.010, tech=True,  interior_light=0),
    'leyline':               dict(ids=12, share=0.030, tech=True,  interior_light=40),
    'pixie':                 dict(ids=6,  share=0.008, tech=True,  interior_light=0),
    'deepworks_archaeology': dict(ids=12, share=0.050, tech=True,  interior_light=80),
}


def census_file(path):
    _name, root = nbt.load(path)
    pal = [e['Name'] for e in root['palette']]
    solid = detail = 0
    names = set()
    grid = {}
    for b in root['blocks']:
        pos = tuple(int(v) for v in b['pos'])
        n = pal[int(b['state'])]
        grid[pos] = n
        if n in sd.AIR_NAMES:
            continue
        solid += 1
        names.add(n)
        if sd.is_detail(n):
            detail += 1
    size = [int(v) for v in root['size']]
    # An interior cell: carved air with something solid under it and headroom over it. The
    # same definition `structure_detail.floor_cells` uses, read off the shipped file rather
    # than off a live Piece so this checker never has to run a generator.
    interior = 0
    for (x, y, z), n in grid.items():
        if n not in sd.AIR_NAMES:
            continue
        below = grid.get((x, y - 1, z))
        above = grid.get((x, y + 1, z))
        if below is None or below in sd.AIR_NAMES or below in sd.NON_SOLID:
            continue
        if above is not None and above not in sd.AIR_NAMES:
            continue
        interior += 1
    return dict(size=size, solid=solid, detail=detail, names=names, interior=interior,
                share=(detail / solid) if solid else 0.0)


def collect(mutate=None):
    out = {}
    for path in sorted(glob.glob(os.path.join(STRUCT, '**', '*.nbt'), recursive=True)):
        rel = os.path.relpath(path, STRUCT).replace(os.sep, '/')
        out[rel] = census_file(path)
    if mutate:
        mutate(out)
    return out


def run(pieces, verbose=False):
    problems = []

    def fail(code, msg):
        problems.append(f'{code}  {msg}')

    seen_family = {}
    for rel, c in sorted(pieces.items()):
        family = rel.split('/')[0]
        spec = FAMILIES.get(family)
        if spec is None:
            fail('D0', f'{rel}: no detail floor is declared for family "{family}" -- add one '
                       f'to FAMILIES rather than letting a whole set go unmeasured')
            continue
        seen_family.setdefault(family, {'tech': False, 'n': 0})
        seen_family[family]['n'] += 1

        if len(c['names']) < spec['ids']:
            fail('D1', f'{rel}: {len(c["names"])} distinct block ids, floor is {spec["ids"]} '
                       f'-- a piece built from one block is a texture, not a place')
        if c['share'] < spec['share']:
            fail('D2', f'{rel}: detail share {c["share"] * 100:.1f}%, floor is '
                       f'{spec["share"] * 100:.1f}% over {c["solid"]} solid blocks')

        lit = any(any(m in n for m in LIGHT_MARKS) for n in c['names'])
        if spec['interior_light'] and c['interior'] >= spec['interior_light'] and not lit:
            fail('D3', f'{rel}: {c["interior"]} interior cells and no light source -- a room '
                       f'nobody can see is a room nobody visits')
        if any(any(m in n for m in TECH_MARKS) for n in c['names']):
            seen_family[family]['tech'] = True

        if verbose:
            print(f'  --  {rel:52} {c["solid"]:6} solid  {c["share"] * 100:5.1f}% detail  '
                  f'{len(c["names"]):3} ids  {c["interior"]:5} interior  '
                  f'{"lit" if lit else "dark"}')

    for family, spec in sorted(FAMILIES.items()):
        got = seen_family.get(family)
        if got is None:
            fail('D5', f'family "{family}" has a declared detail floor and no pieces on disk')
            continue
        if spec['tech'] and not got['tech']:
            fail('D4', f'family "{family}": {got["n"]} piece(s) and not one crystal, conduit '
                       f'or emitter -- this is the layer the field review said was missing')
    return problems


# Corrupt one thing at a time and prove the matching code fires. A checker that cannot fail is
# not a checker -- the same discipline check_surface_works.py and check_worldgen.py hold.
SELF_TESTS = [
    ('D0', lambda p: p.__setitem__('mystery/thing.nbt', dict(
        size=[1, 1, 1], solid=1, detail=1, names={'minecraft:stone'}, interior=0, share=1.0))),
    ('D1', lambda p: p['surface/grange_hall.nbt'].__setitem__(
        'names', {'minecraft:stone', 'minecraft:lantern'})),
    # `share` is what run() reads; setting `detail` alone left this check silent, which is
    # exactly the failure the self-test exists to catch.
    ('D2', lambda p: p['surface/grange_hall.nbt'].update({'detail': 0, 'share': 0.0})),
    ('D3', lambda p: p['court/north_council.nbt'].__setitem__(
        'names', {f'minecraft:filler_{i}' for i in range(40)})),
    ('D4', lambda p: [c.__setitem__('names', {f'minecraft:filler_{i}' for i in range(40)})
                      for k, c in p.items() if k.startswith('leyline/')]),
    ('D5', lambda p: [p.pop(k) for k in list(p) if k.startswith('greatbole/')]),
]


def self_test():
    clean = run(collect())
    if clean:
        print('  self-test cannot run: the real structures already fail')
        for c in clean:
            print(f'    {c}')
        return 1
    bad = 0
    for code, mut in SELF_TESTS:
        def mutate(p, mut=mut):
            p['surface/grange_hall.nbt'] = dict(p['surface/grange_hall.nbt'])
            p['court/north_council.nbt'] = dict(p['court/north_council.nbt'])
            for k in list(p):
                p[k] = dict(p[k])
            mut(p)
        probs = run(collect(mutate=mutate))
        hit = [x for x in probs if x.startswith(code)]
        print(f'  {code:4} {"FIRES" if hit else "SILENT -- CHECK IS DEAD"}   '
              f'{hit[0][:100] if hit else ""}')
        if not hit:
            bad += 1
    print(f'\n  {len(SELF_TESTS) - bad}/{len(SELF_TESTS)} checks proven to fire')
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if not os.path.isdir(STRUCT):
        print('no structures -- nothing to check')
        return 0
    if a.self_test:
        return self_test()
    pieces = collect()
    problems = run(pieces, verbose=a.verbose)
    for p in problems:
        print(f'  {p}')
    fam = {}
    for rel, c in pieces.items():
        fam.setdefault(rel.split('/')[0], []).append(c)
    print('=' * 68)
    for name in sorted(fam):
        rows = fam[name]
        shares = sorted(x['share'] for x in rows)
        print(f'  {name:24} {len(rows):3} piece(s)  worst {shares[0] * 100:5.1f}%  '
              f'median {shares[len(shares) // 2] * 100:5.1f}%  '
              f'min ids {min(len(x["names"]) for x in rows):3}')
    print(f'RESULT: {len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
