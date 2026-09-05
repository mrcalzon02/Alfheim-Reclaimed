"""Measure instructional coverage: does every processing step have a quest?

The standard, set by the user 2026-09-04:

    Every intended processing step for an ore, a contributive item or a componentary item
    should have a quest covering the process by which it is created, so that every
    contributive processing step has a quest charting progress from a raw ingredient to a
    useful component or a useful output.

A "processing step" here is one recipe this pack emits that either produces one of our items or
CONSUMES one to make something useful. The second half matters: `cinderbloom_render` turns a
quickened bloom into coal, and that is the payoff of the whole ore chain -- counting only
alfheim: outputs would have scored the most important step in the pack as not a step at all.

Alternate uses and sinks are counted separately, because a use is not a step on the way to
anything.

The Rites are four PARALLEL routes, not a chain: steeping, quickening, grafting and deepening all
take raw bloom to quickened bloom, at improving yields, unlocked in different eras. Render then
takes quickened to metal. So a bloom has two conceptual steps and four conversion methods, which
is why the per-process and per-item readings diverge so hard here.

The report is deliberately given two ways, because the standard is ambiguous by a factor of ten
and the difference is worth hundreds of quests:

    PER PROCESS   the Steeping is one process, applied to twelve blooms -> one quest
    PER ITEM      steeping cinderbloom and steeping verdigris are two steps -> twelve quests

A third, HYBRID, is printed and is the recommended standard: per item for ladder steps, per
process for the Rites. A ladder step is a genuinely distinct transformation with its own output,
so it earns a quest. The Steeping applied to a twelfth bloom teaches nothing the first eleven did
not -- the blooms want an introduction each, which the Compendium already gives them, not a
process quest each.

Neither of the first two is assumed. All three are printed; the project decides.

    python tools/check_coverage.py
    python tools/check_coverage.py --verbose
    python tools/check_coverage.py --era 3
"""
import argparse
import collections
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_era  # noqa: E402

NS = 'alfheim'
SCRIPTS = os.path.join('kubejs', 'server_scripts')
CHAPTERS = os.path.join('config', 'ftbquests', 'quests', 'chapters')

# Which era teaches which Rite. From ERA_EXPANSION.md §4.2 and CAMPAIGN_ERAS.md.
RITE_ERA = {'steeping': 1, 'quickening': 2, 'grafting': 3, 'deepening': 5,
            'render': 1, 'render_fast': 2, 'grafting_bonus': 3}

# Scripts whose recipes are alternate uses rather than steps toward a component.
USE_SCRIPTS = ('30_item_uses.js',)

# The station each recipe type is worked at. A recipe is only reachable once the player has been
# taught to build its station, so this is what the ordering check asserts against.
#
# User requirement, 2026-09-04: "when a recipe requires a method it should verify that you have
# previously unlocked that method in some preceding step, so that the recipes are used
# consecutively in a proceeding manner rather than requiring crashing methods you have not yet
# unlocked."
# Values are the set of items ANY ONE of which proves the station is available. Botania ships
# twelve cosmetic Petal Apothecary variants that are one station, and Create's basin recipes are
# equally satisfied by a mixer -- a single-id map scored both as untaught and buried the real
# violations underneath them.
METHOD_STATION = {
    'botania:petal_apothecary': {'botania:apothecary_default', 'botania:apothecary_livingrock',
                                 'botania:apothecary_forest', 'botania:apothecary_plains',
                                 'botania:apothecary_mossy', 'botania:apothecary_desert',
                                 'botania:apothecary_fungal', 'botania:apothecary_taiga',
                                 'botania:apothecary_mesa', 'botania:apothecary_mountain',
                                 'botania:apothecary_swamp', 'botania:apothecary_deepslate'},
    'botania:mana_infusion': {'botania:mana_pool', 'botania:dilluted_pool', 'botania:fabulous_pool'},
    'botania:runic_altar': {'botania:runic_altar'},
    'botania:terra_plate': {'botania:terra_plate'},
    'botania:elven_trade': {'botania:alfheim_portal'},
    'botania:brew': {'botania:brewery'},
    'mythicbotany:infuser': {'mythicbotany:mana_infuser'},
    'ars_nouveau:imbuement': {'ars_nouveau:imbuement_chamber'},
    'ars_nouveau:enchanting_apparatus': {'ars_nouveau:enchanting_apparatus',
                                         'ars_nouveau:arcane_pedestal'},
    'naturesaura:altar': {'naturesaura:nature_altar'},
    'naturesaura:tree_ritual': {'naturesaura:gold_powder', 'naturesaura:ancient_sapling',
                                'naturesaura:gold_fiber'},
    'occultism:crushing': {'occultism:sacrificial_bowl', 'occultism:spirit_attuned_gem',
                           'occultism:chalk_white'},
    'occultism:spirit_fire': {'occultism:sacrificial_bowl', 'occultism:chalk_white'},
    'feywild:fey_altar': {'feywild:fey_altar'},
    'create:milling': {'create:millstone', 'create:crushing_wheel'},
    'create:pressing': {'create:mechanical_press'},
    'create:mixing': {'create:basin', 'create:mechanical_mixer'},
    'create:deploying': {'create:deployer', 'create:depot'},
    'create:sequenced_assembly': {'create:depot', 'create:deployer', 'create:mechanical_arm'},
    # Crush is a GLYPH, not a machine -- ars_nouveau.glyph_name.glyph_crush, "turns stone into
    # gravel". There is no block to build, so the unlock is the means to scribe it.
    'ars_nouveau:crush': {'ars_nouveau:scribes_table', 'ars_nouveau:novice_spell_book'},
}

# Methods every player has from the first minute. Asserting an unlock for these would be noise.
FREE_METHODS = {'minecraft:smelting', 'minecraft:blasting', 'minecraft:smoking',
                'minecraft:crafting_shaped', 'minecraft:crafting_shapeless', None}


def task_items_by_era():
    """Items named by a quest TASK, per era.

    Rewards are excluded on purpose: being handed a thing is not being taught to make it, and
    the standard is about the process. The tasks: block is read out of the SNBT directly so
    this measures what the game will actually load, not what a generator intended.
    """
    out = collections.defaultdict(set)
    for p in sorted(glob.glob(os.path.join(CHAPTERS, 'era_*.snbt'))):
        m = re.search(r'era_(\d+)\.snbt$', p)
        if not m:
            continue
        era = int(m.group(1))
        txt = open(p, encoding='utf-8').read()
        for tb in re.finditer(r'tasks:\s*\[(.*?)\n\t\t\t\]', txt, re.S):
            for im in re.finditer(r'item:\s*"([^"]+)"', tb.group(1)):
                out[era].add(im.group(1))
    return out


def compendium_items():
    """Items documented by a Compendium entry.

    Not the same as a quest and not counted as coverage, but it is the difference between a
    player who has never heard of a material and one who can look it up. Reported alongside.
    """
    out = set()
    for p in sorted(glob.glob(os.path.join(CHAPTERS, 'ref_*.snbt'))):
        txt = open(p, encoding='utf-8').read()
        # Compendium entries are checkmark quests: the subject is the entry's icon, not a task
        # item. Reading `item:` here found nothing at all, which is how this was caught.
        for m in re.finditer(r'icon:\s*"([^"]+)"', txt):
            out.add(m.group(1))
            # An ore block documented is its drop documented.
            if m.group(1).endswith('_ore'):
                out.add(m.group(1).replace(':', ':raw_').replace('_ore', ''))
    return out


def era_of(rec):
    """The era a recipe belongs to, or None if it is not era-scoped."""
    m = re.search(r'_era(\d+)_', rec['file'])
    if m:
        return int(m.group(1))
    if rec['file'] == '12_rites.js' and rec['id']:
        stem = rec['id'].split('/')[-1]
        for suffix, era in sorted(RITE_ERA.items(), key=lambda kv: -len(kv[0])):
            if stem.endswith(suffix):
                return era
    return None


def process_of(rec):
    """The named process a recipe instantiates, for the per-process reading.

    A ladder step is its own process. A Rite is one process across twelve blooms.
    """
    if rec['file'] == '12_rites.js' and rec['id']:
        stem = rec['id'].split('/')[-1]
        for suffix in sorted(RITE_ERA, key=len, reverse=True):
            if stem.endswith(suffix):
                return f'rite:{suffix}'
    return f"step:{rec['id']}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--era', type=int)
    a = ap.parse_args()

    recs = []
    for p in sorted(glob.glob(os.path.join(SCRIPTS, '*.js'))):
        recs.extend(check_era.parse_recipes(p))

    tasks = task_items_by_era()
    # An item taught in an earlier era counts as covered later: you are not re-taught a step.
    cumulative = {}
    seen = set()
    for e in range(1, 11):
        seen |= tasks.get(e, set())
        cumulative[e] = set(seen)

    steps, uses = [], []
    for r in recs:
        if r['method'] == 'remove' or not r['outputs']:
            continue
        contributive = [o for o in r['outputs'] if o.startswith(NS + ':')]
        if not contributive:
            # A step that consumes one of ours and yields something useful is still a step --
            # the render is the entire point of the ore chain.
            if any(i.startswith(NS + ':') for i in r['inputs']):
                contributive = list(r['outputs'])
            else:
                continue
        (uses if r['file'] in USE_SCRIPTS else steps).append((r, contributive))

    comp = compendium_items()
    print(f'contributive processing steps: {len(steps)}')
    print(f'alternate uses (not steps):    {len(uses)}')
    print(f'items documented in Compendium: {len(comp)}')
    print()

    # ---- per item ------------------------------------------------------------------------
    per_item = collections.defaultdict(lambda: {'total': 0, 'covered': 0, 'missing': []})
    unscoped = []
    for r, outs in steps:
        e = era_of(r)
        if e is None:
            unscoped.append(r)
            continue
        for o in outs:
            d = per_item[e]
            d['total'] += 1
            if o in cumulative.get(e, set()):
                d['covered'] += 1
            else:
                d.setdefault('documented', 0)
                if o in comp:
                    d['documented'] += 1
                d['missing'].append((o, r['id']))

    # ---- per process ---------------------------------------------------------------------
    proc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for r, outs in steps:
        e = era_of(r)
        if e is None:
            continue
        key = process_of(r)
        cell = proc[e][key]
        cell[0] += 1
        if any(o in cumulative.get(e, set()) for o in outs):
            cell[1] += 1

    print('=' * 74)
    print('PER ITEM  -- every output of every step needs its own quest')
    print('=' * 74)
    print(f'{"era":>4} {"steps":>7} {"covered":>8} {"gap":>6}   quests to add')
    tot_gap = 0
    for e in range(1, 11):
        d = per_item.get(e)
        if not d:
            continue
        gap = d['total'] - d['covered']
        tot_gap += gap
        doc = d.get('documented', 0)
        print(f'{e:>4} {d["total"]:>7} {d["covered"]:>8} {gap:>6}   '
              f'{"+" + str(gap) if gap else "-":<6} ({doc} of the gap is Compendium-documented)')
    print(f'{"":>4} {"":>7} {"":>8} {tot_gap:>6}   TOTAL')

    print()
    print('=' * 74)
    print('PER PROCESS  -- one quest per named process, applied to many materials')
    print('=' * 74)
    print(f'{"era":>4} {"procs":>7} {"covered":>8} {"gap":>6}   quests to add')
    tot_pgap = 0
    for e in range(1, 11):
        if e not in proc:
            continue
        procs = proc[e]
        covered = sum(1 for k, v in procs.items() if v[1] > 0)
        gap = len(procs) - covered
        tot_pgap += gap
        print(f'{e:>4} {len(procs):>7} {covered:>8} {gap:>6}   {"+" + str(gap) if gap else "-"}')
    print(f'{"":>4} {"":>7} {"":>8} {tot_pgap:>6}   TOTAL')

    # ---- hybrid --------------------------------------------------------------------------
    print()
    print('=' * 74)
    print('HYBRID  -- per item for ladder steps, per process for the Rites  [RECOMMENDED]')
    print('=' * 74)
    lad = collections.defaultdict(lambda: [0, 0])
    rite = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for r, outs in steps:
        e = era_of(r)
        if e is None:
            continue
        covered = any(o in cumulative.get(e, set()) for o in outs)
        if r['file'] == '12_rites.js':
            cell = rite[e][process_of(r)]
            cell[0] += 1
            cell[1] += 1 if covered else 0
        else:
            lad[e][0] += 1
            lad[e][1] += 1 if covered else 0

    print(f'{"era":>4} {"ladder":>8} {"gap":>6} {"rites":>7} {"gap":>6} {"to add":>8}')
    tot_h = 0
    for e in range(1, 11):
        ls, lc = lad[e]
        rg = sum(1 for v in rite[e].values() if v[1] == 0)
        add = (ls - lc) + rg
        tot_h += add
        print(f'{e:>4} {ls:>8} {ls - lc:>6} {len(rite[e]):>7} {rg:>6} {add:>8}')
    print(f'{"":>4} {"":>8} {"":>6} {"":>7} {"":>6} {tot_h:>8}   TOTAL')

    # ---- method ordering -------------------------------------------------------------------
    print()
    print('=' * 74)
    print('METHOD ORDERING  -- is the station taught before the recipe needs it?')
    print('=' * 74)
    first_taught = {}
    for e in range(1, 11):
        for it in tasks.get(e, set()):
            first_taught.setdefault(it, e)

    violations = []
    method_use = collections.defaultdict(set)
    for r, _ in steps:
        e = era_of(r)
        if e is None:
            continue
        t = r['type']
        if t in FREE_METHODS:
            continue
        stations = METHOD_STATION.get(t)
        method_use[t].add(e)
        if not stations:
            continue
        taught = min((first_taught[s] for s in stations if s in first_taught), default=None)
        label = sorted(stations)[0] if len(stations) == 1 else f'{sorted(stations)[0]} (+alts)'
        if taught is None:
            violations.append((e, t, label, r['id'], 'never taught'))
        elif taught > e:
            violations.append((e, t, label, r['id'], f'taught in era {taught}'))

    print(f'{"era":>4}  {"method":34} {"station":34} when')
    for e, t, station, rid, why in sorted(violations)[:40]:
        print(f'{e:>4}  {t:34} {station:34} {why}')
    if not violations:
        print("  none -- every recipe's station is taught in its era or earlier")
    print()
    print(f'{len(violations)} ordering violation(s) across '
          f'{len({v[1] for v in violations})} method(s)')

    unmapped = sorted(t for t in method_use if t not in METHOD_STATION and t not in FREE_METHODS)
    if unmapped:
        print(f'{len(unmapped)} method(s) have no station mapped, so are unchecked: '
              f'{", ".join(unmapped)}')

    if unscoped:
        print()
        print(f'{len(unscoped)} contributive step(s) belong to no era '
              f'({", ".join(sorted({r["file"] for r in unscoped}))}) -- '
              'they cannot be checked until they are era-scoped')

    if a.verbose or a.era:
        print()
        print('=' * 74)
        print('UNCOVERED OUTPUTS')
        print('=' * 74)
        for e in range(1, 11):
            if a.era and e != a.era:
                continue
            d = per_item.get(e)
            if not d or not d['missing']:
                continue
            print(f'\n--- Era {e}: {len(d["missing"])} uncovered')
            for o, rid in d['missing'][:60]:
                print(f'    {o:44} {rid}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
