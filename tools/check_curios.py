"""Check the generated Guild Regalia against the catalog that authorised it.

`tools/build_curio_plan.py` proves the *plan* is coherent. This proves the **assets match the
plan**: that all 63 planned ids were registered and no others, that each has a texture and a model
that point at each other, that each lands in the slot the catalog assigned, that no new slot type
appeared, and that the three signals the icons carry -- form, hue, rank -- are actually separable
rather than merely intended to be. Pixel thresholds are regression heuristics; the contact sheet
still needs visual review.

The last two are the ones worth having. A generator that quietly emits fifteen shades of the same
brown, or three ranks a player cannot tell apart, can pass structural checks; C8, C9, C12, C15 and
C16 measure the pixels instead of trusting the constants that produced them.

    python tools/check_curios.py
    python tools/check_curios.py --verbose
    python tools/check_curios.py --self-test
"""
import argparse
import colorsys
import glob
import json
import math
import os
import re
import sys

from PIL import Image

NS = 'alfheim'
CATALOG = os.path.join('alfheim_reclaimed_design', 'curios', 'curio_suite_catalog.json')
SCRIPT = os.path.join('kubejs', 'startup_scripts', '18_curios.js')
TEX = os.path.join('kubejs', 'assets', NS, 'textures', 'item')
MODEL = os.path.join('kubejs', 'assets', NS, 'models', 'item')
TAGS = os.path.join('kubejs', 'data', 'curios', 'tags', 'items')

# Project heuristic for owners sharing a slot, supplemented by visual review.
# This is a regression threshold, not a guarantee of perceptual or colour-blind accessibility.
MIN_HUE_SEP = 25.0
# Rank must be visible without reading the name; this is the minimum mean-brightness step.
MIN_VAL_STEP = 0.04
RANK_ORDER = ['apprentice', 'guild', 'master']


def measure(path):
    """Mean hue and brightness of a texture's opaque pixels.

    Hue is a circular quantity, so it is averaged as unit vectors rather than as numbers -- a
    naive mean of 350 and 10 is 180, which is the opposite colour. Each pixel is weighted by
    saturation * value so that near-grey shading pixels do not drag the result toward an
    arbitrary hue they barely express.
    """
    with Image.open(path) as source:
        mode = source.mode
        im = source.convert('RGBA')
    w, h = im.size
    px = im.load()
    x_sum = y_sum = wt = 0.0
    vals = []
    opaque = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            opaque += 1
            hh, ss, vv = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            vals.append(vv)
            k = ss * vv
            ang = hh * 2 * math.pi
            x_sum += math.cos(ang) * k
            y_sum += math.sin(ang) * k
            wt += k
    hue = (math.degrees(math.atan2(y_sum, x_sum)) % 360) if wt > 1e-6 else None
    mask = tuple(px[x, y][3] > 0 for y in range(h) for x in range(w))
    clear = {(x, y) for y in range(h) for x in range(w) if px[x, y][3] == 0}
    border = [(x, y) for x, y in clear if x in (0, w - 1) or y in (0, h - 1)]
    reached = set(border)
    while border:
        x, y = border.pop()
        for nxt in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nxt in clear and nxt not in reached:
                reached.add(nxt)
                border.append(nxt)
    return {'size': (w, h), 'opaque': opaque, 'mode': mode, 'mask': mask,
            'transparent': len(clear), 'hole_pixels': len(clear - reached),
            'hue': hue, 'val': (sum(vals) / len(vals)) if vals else 0.0}


def hue_gap(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def collect(mutate=None):
    catalog = json.load(open(CATALOG, encoding='utf-8'))
    planned = []
    for it in catalog['planned_items']:
        row = dict(it)
        row['path'] = it['id'].split(':', 1)[1]
        planned.append(row)

    registered = {}
    duplicates = []
    txt = open(SCRIPT, encoding='utf-8').read() if os.path.exists(SCRIPT) else ''
    for line in txt.split('\n'):
        m = re.search(r"""event\.create\(\s*'([a-z0-9_]+:[a-z0-9_/.]+)'\s*\)""", line)
        if not m:
            continue
        name = re.search(r"""\.displayName\('((?:[^'\\]|\\.)*)'\)""", line)
        rarity = re.search(r"""\.rarity\('([a-z]+)'\)""", line)
        if m.group(1) in registered:
            duplicates.append(m.group(1))
        registered[m.group(1)] = {
            'name': name.group(1) if name else None,
            'rarity': rarity.group(1) if rarity else None,
            'unstackable': '.unstackable()' in line or '.maxStackSize(1)' in line,
        }

    models, textures, parents = {}, {}, {}
    for row in planned:
        mp = os.path.join(MODEL, *row['path'].split('/')) + '.json'
        tp = os.path.join(TEX, *row['path'].split('/')) + '.png'
        if os.path.exists(mp):
            try:
                data = json.load(open(mp, encoding='utf-8'))
                models[row['id']] = data.get('textures', {}).get('layer0')
                parents[row['id']] = data.get('parent')
            except Exception:
                models[row['id']] = '<unparseable>'
        if os.path.exists(tp):
            try:
                textures[row['id']] = measure(tp)
            except (OSError, ValueError):
                pass  # Report as a missing usable texture under C3.

    tags = {}
    for p in sorted(glob.glob(os.path.join(TAGS, '*.json'))):
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception:
            d = {}
        tags[os.path.splitext(os.path.basename(p))[0]] = {
            'values': list(d.get('values', [])), 'replace': d.get('replace')}

    asset_ids = set()
    for root, ext in ((MODEL, '.json'), (TEX, '.png')):
        for p in glob.glob(os.path.join(root, 'curio', '**', '*' + ext), recursive=True):
            asset_ids.add(NS + ':' + os.path.relpath(p, root)[:-len(ext)].replace('\\', '/'))
    st = {'catalog': catalog, 'planned': planned, 'registered': registered,
          'models': models, 'textures': textures, 'tags': tags, 'parents': parents,
          'duplicates': duplicates, 'asset_ids': asset_ids}
    if mutate:
        mutate(st)
    return st


def run(st, verbose=False):
    problems = []

    def bad(code, msg):
        problems.append(f'{code}  {msg}')

    planned = st['planned']
    by_id = {r['id']: r for r in planned}
    reg = st['registered']
    for i in st['duplicates']:
        bad('C2', f'duplicate registration: {i}')
    for i in sorted(st['asset_ids'] - set(by_id)):
        bad('C14', f'stale or unplanned curio asset: {i}')

    # --- structure -----------------------------------------------------------------------
    for r in planned:
        if r['id'] not in reg:
            bad('C1', f"planned but never registered: {r['id']}")
    for i in reg:
        if i not in by_id:
            bad('C2', f"registered but not in the catalog: {i}")

    for r in planned:
        if r['id'] not in st['textures']:
            bad('C3', f"no texture for {r['id']}")
        if r['id'] not in st['models']:
            bad('C3', f"no model for {r['id']}")

    for r in planned:
        want = f"{NS}:item/{r['path']}"
        got = st['models'].get(r['id'])
        if got is not None and got != want:
            bad('C4', f"{r['id']} model layer0 is {got!r}, expected {want!r}")
        if r['id'] in st['models'] and st['parents'].get(r['id']) != 'minecraft:item/generated':
            bad('C4', f"{r['id']} must use the generated item model parent")

    # --- slots ---------------------------------------------------------------------------
    placed = {}
    for slot, d in st['tags'].items():
        for i in d['values']:
            placed.setdefault(i, []).append(slot)
    for r in planned:
        got = placed.get(r['id'], [])
        if len(got) != 1:
            bad('C5', f"{r['id']} is in {len(got)} slot tag(s) {got}, expected exactly 1")
        elif got[0] != r['slot']:
            bad('C5', f"{r['id']} tagged {got[0]}, catalog says {r['slot']}")
    for i in placed:
        if i not in by_id:
            bad('C5', f"slot tag lists an item we do not own: {i}")

    allowed = {r['slot'] for r in planned}
    if st['catalog']['slot_policy']['new_slot_types'] == 0:
        for slot in st['tags']:
            if slot not in allowed:
                bad('C6', f"slot tag {slot}.json introduces a slot the plan does not use "
                          f"(slot_policy.new_slot_types is 0)")

    for slot, d in st['tags'].items():
        if d['replace'] is not False:
            bad('C7', f"{slot}.json has replace={d['replace']!r}; must be false or every other "
                      f"mod's item is evicted from that slot")

    # --- registration quality ------------------------------------------------------------
    seen = {}
    for i, v in reg.items():
        if not v['unstackable']:
            bad('C10', f"{i} is stackable; a worn proof-of-rank that stacks is a duplication "
                       f"surface")
        if not v['name']:
            bad('C10', f'{i} has no display name')
        rank = by_id.get(i, {}).get('rank')
        expected_rarity = dict(apprentice='uncommon', guild='rare', master='epic').get(rank)
        if not v['rarity'] or (expected_rarity and v['rarity'] != expected_rarity):
            bad('C10', f"{i} has incorrect rarity {v['rarity']!r} for {rank}")
        if v['name']:
            if v['name'] in seen:
                bad('C11', f"display name {v['name']!r} used by both {seen[v['name']]} and {i}")
            seen[v['name']] = i

    # --- the pixels ----------------------------------------------------------------------
    for i, m in st['textures'].items():
        if m['size'] != (16, 16):
            bad('C8', f"{i} is {m['size'][0]}x{m['size'][1]}, expected 16x16")
        if m['opaque'] == 0:
            bad('C8', f"{i} is fully transparent")
        if m['hue'] is None:
            bad('C8', f"{i} has no colour at all; the hue never took")
        if m['mode'] != 'RGBA' or m['transparent'] == 0:
            bad('C15', f'{i} requires literal RGBA transparency')
        if by_id[i]['family'] == 'signet' and m['hole_pixels'] < 4:
            bad('C15', f'{i} has no enclosed transparent ring opening')

    # Family silhouettes must stay distinct, and overlays cannot change their alpha footprint.
    shapes = {}
    for r in planned:
        m = st['textures'].get(r['id'])
        if m:
            shapes.setdefault(r['family'], set()).add(m['mask'])
    for family, masks in shapes.items():
        if len(masks) != 1:
            bad('C16', f'{family} silhouette changes between owners or ranks')
    families = sorted(shapes)
    for index, family in enumerate(families):
        for other in families[index + 1:]:
            if shapes[family] & shapes[other]:
                bad('C16', f'{family} and {other} share a silhouette')

    # C9 -- two owners in the same slot must be separable by colour.
    per_slot = {}
    for r in planned:
        m = st['textures'].get(r['id'])
        if m and m['hue'] is not None:
            per_slot.setdefault((r['slot'], r['rank']), {}).setdefault(r['owner'], []).append(m['hue'])
    for slot, owners in sorted(per_slot.items()):
        mean = {}
        for o, hs in owners.items():
            x = sum(math.cos(math.radians(h)) for h in hs)
            y = sum(math.sin(math.radians(h)) for h in hs)
            mean[o] = math.degrees(math.atan2(y, x)) % 360
        names = sorted(mean)
        for a in range(len(names)):
            for b in range(a + 1, len(names)):
                g = hue_gap(mean[names[a]], mean[names[b]])
                if g < MIN_HUE_SEP:
                    bad('C9', f"in slot/rank {slot}, {names[a]} and {names[b]} are {g:.1f}deg apart "
                              f"(minimum {MIN_HUE_SEP}); review colour separation")
                elif verbose:
                    print(f'  -- {str(slot):26} {names[a]:14} vs {names[b]:14} {g:5.1f}deg')

    # C12 -- rank has to be visible without reading the tooltip.
    fam = {}
    for r in planned:
        m = st['textures'].get(r['id'])
        if m:
            fam.setdefault((r['owner'], r['family']), {})[r['rank']] = m['val']
    for (owner, family), vals in sorted(fam.items()):
        chain = [vals.get(k) for k in RANK_ORDER]
        if any(v is None for v in chain):
            continue
        for lo, hi, a, b in zip(chain, chain[1:], RANK_ORDER, RANK_ORDER[1:]):
            if hi - lo < MIN_VAL_STEP:
                bad('C12', f"{owner}/{family}: {b} is only {hi - lo:+.3f} brighter than {a} "
                           f"(minimum {MIN_VAL_STEP}); the ranks look identical")

    # --- counts --------------------------------------------------------------------------
    c = st['catalog']['counts']
    if len(planned) != c['planned_items']:
        bad('C13', f"catalog lists {len(planned)} items but counts says {c['planned_items']}")
    n_class = sum(1 for r in planned if r['kind'] == 'class')
    n_prof = sum(1 for r in planned if r['kind'] == 'profession')
    if n_class != c['class_items']:
        bad('C13', f"{n_class} class items, counts says {c['class_items']}")
    if n_prof != c['profession_items']:
        bad('C13', f"{n_prof} profession items, counts says {c['profession_items']}")

    if verbose:
        print(f"\n  {len(planned)} planned  {len(reg)} registered  "
              f"{len(st['textures'])} textures  {len(st['models'])} models")
        for slot, d in sorted(st['tags'].items()):
            print(f'  {slot:10} {len(d["values"]):2} items')
    return problems


def _drop_reg(st):
    st['registered'].pop(sorted(st['registered'])[0], None)


def _extra_reg(st):
    st['registered']['alfheim:curio/class/warrior/signet_legendary'] = {
        'name': 'X', 'rarity': 'epic', 'unstackable': True}


def _drop_tex(st):
    st['textures'].pop(sorted(st['textures'])[0], None)


def _bend_model(st):
    k = sorted(st['models'])[0]
    st['models'][k] = 'alfheim:item/wrong'


def _double_slot(st):
    k = st['planned'][0]['id']
    st['tags'].setdefault('belt', {'values': [], 'replace': False})['values'].append(k)


def _new_slot(st):
    st['tags']['back'] = {'values': [], 'replace': False}


def _replace_true(st):
    st['tags'][sorted(st['tags'])[0]]['replace'] = True


def _stackable(st):
    st['registered'][sorted(st['registered'])[0]]['unstackable'] = False


def _dupe_name(st):
    a, b = sorted(st['registered'])[:2]
    st['registered'][b]['name'] = st['registered'][a]['name']


def _wrong_size(st):
    st['textures'][sorted(st['textures'])[0]]['size'] = (32, 32)


def _hue_collide(st):
    """Give every mining cuff the gear_crafting hue -- the exact failure C9 exists to catch."""
    gear = [r['id'] for r in st['planned'] if r['owner'] == 'gear_crafting']
    target = st['textures'][gear[0]]['hue']
    for r in st['planned']:
        if r['owner'] == 'mining':
            st['textures'][r['id']]['hue'] = target


def _flat_ranks(st):
    for r in st['planned']:
        if r['owner'] == 'warrior' and r['family'] == 'signet':
            st['textures'][r['id']]['val'] = 0.5


def _miscount(st):
    st['catalog']['counts']['planned_items'] = 999


SELF_TESTS = [
    ('C1', _drop_reg), ('C2', _extra_reg), ('C3', _drop_tex), ('C4', _bend_model),
    ('C5', _double_slot), ('C6', _new_slot), ('C7', _replace_true), ('C8', _wrong_size),
    ('C9', _hue_collide), ('C10', _stackable), ('C11', _dupe_name), ('C12', _flat_ranks),
    ('C13', _miscount),
    ('C14', lambda s: s['asset_ids'].add('alfheim:curio/retired')),
    ('C15', lambda s: s['textures'][s['planned'][0]['id']].update(hole_pixels=0)),
    ('C15', lambda s: s['textures'][s['planned'][0]['id']].update(mode='RGB', transparent=0)),
    ('C16', lambda s: s['textures'][s['planned'][0]['id']].update(mask=(True,) * 256)),
    ('C2', lambda s: s['duplicates'].append(s['planned'][0]['id'])),
]


def self_test():
    """A checker that cannot fail is not a checker. Corrupt one thing at a time and prove the
    matching code fires -- the same discipline check_surface_works.py holds itself to."""
    clean = run(collect())
    if clean:
        print('  self-test cannot run: the real data already has problems')
        for p in clean[:5]:
            print('   ', p)
        return 1
    bad = 0
    for code, mut in SELF_TESTS:
        probs = run(collect(mutate=mut))
        hit = [p for p in probs if p.startswith(code + ' ')]
        print(f'  {code:4} {"FIRES" if hit else "SILENT -- CHECK IS DEAD"}'
              f'   {hit[0][:92] if hit else ""}')
        if not hit:
            bad += 1
    print(f'\n  {len(SELF_TESTS) - bad}/{len(SELF_TESTS)} checks proven to fire')
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    problems = run(collect(), verbose=a.verbose)
    for p in problems:
        print('  ' + p)
    print(f'\n  {len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
