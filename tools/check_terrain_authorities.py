#!/usr/bin/env python3
"""Prove the terrain selector and the biome layer cannot disagree.

This is the check the whole architecture rests on, and it is the one B-82 did not have. That
build thresholded climate independently of the biome source; the two disagreed at the edges and
Hills terrain appeared inside Plains and Silverbark. The defence here is not better thresholds --
it is that selector and layer are generated from ONE partition, and that this check evaluates the
emitted selector against the emitted layer point by point rather than trusting that they were.

    A1  the partition is disjoint and covering -- without both, membership is a nearest-neighbour
        distance computation and no density function can reproduce it at all
    A2  every biome the layer places is owned by exactly one authority
    A3  the emitted selector returns that authority, for every sampled climate point
    A4  the selector is a chain of NAMED steps, so it cannot have blown up inline
    A5  stage 1 moves no terrain: every authority resolves to the same expression

    python tools/check_terrain_authorities.py
    python tools/check_terrain_authorities.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gen_terrain_authorities as authorities_module  # noqa: E402

AXES = [axis for axis, _ in authorities_module.AXES]
FUNCTIONS = {function: axis for axis, function in authorities_module.AXES}
SAMPLES = 60000


def contains(parameters, point):
    for axis in AXES:
        low, high = authorities_module.span(parameters, axis)
        if not (low <= point[axis] < high):
            return False
    return True


def evaluate(selector, entry, point):
    """Follow the emitted chain exactly as the game would, resolving named steps by reference."""
    node = entry
    seen = 0
    while True:
        seen += 1
        if seen > 5000:
            raise RuntimeError('selector does not terminate')
        if isinstance(node, str):
            if node.startswith('%s:authority/step_' % authorities_module.NS):
                node = selector[node]
                continue
            return node                                   # an authority leaf
        assert node['type'] == 'minecraft:range_choice', node['type']
        axis = FUNCTIONS[node['input']]
        inside = node['min_inclusive'] <= point[axis] < node['max_exclusive']
        node = node['when_in_range'] if inside else node['when_out_of_range']


def validate(bands, owners, out, entry, seed=11):
    problems = []

    def fail(code, text):
        problems.append('%s  %s' % (code, text))

    # --- A1 ------------------------------------------------------------------------------
    def overlaps(a, b):
        return all(authorities_module.span(a, x)[0] < authorities_module.span(b, x)[1]
                   and authorities_module.span(b, x)[0] < authorities_module.span(a, x)[1]
                   for x in AXES)
    clashes = [(bands[i]['biome'], bands[j]['biome'])
               for i in range(len(bands)) for j in range(i + 1, len(bands))
               if overlaps(bands[i]['parameters'], bands[j]['parameters'])]
    if clashes:
        fail('A1', 'the partition overlaps (%d pair(s), e.g. %s): membership is then a '
                   'nearest-neighbour distance and the selector cannot reproduce it'
                   % (len(clashes), clashes[0]))

    # --- A2 ------------------------------------------------------------------------------
    placed = {b['biome'] for b in bands}
    explicit = [a for a in owners if a['biomes'] is not None]
    for i in range(len(explicit)):
        for j in range(i + 1, len(explicit)):
            both = explicit[i]['biomes'] & explicit[j]['biomes']
            if both:
                fail('A2', '%s and %s both claim %s' % (explicit[i]['id'], explicit[j]['id'],
                                                       sorted(both)))
    for authority in explicit:
        stray = authority['biomes'] - placed
        if stray:
            fail('A2', '%s claims %s, which the layer does not place'
                 % (authority['id'], sorted(stray)))

    # --- A3, and A1's covering half, in the same sweep ------------------------------------
    selector = {'%s:authority/%s' % (authorities_module.NS, os.path.basename(p)[:-5]):
                json.loads(data) for p, data in out.items()
                if os.path.basename(p).startswith('step_')}
    random.seed(seed)
    uncovered = 0
    mismatched = []
    for _ in range(SAMPLES):
        point = {axis: random.uniform(-1.0, 1.0) for axis in AXES}
        owning = [b for b in bands if contains(b['parameters'], point)]
        if not owning:
            uncovered += 1
            continue
        expected = '%s:authority/%s' % (authorities_module.NS,
                                        authorities_module.owner_of(owning[0]['biome'], owners))
        got = evaluate(selector, entry, point)
        if got != expected and len(mismatched) < 4:
            mismatched.append((owning[0]['biome'], expected, got))
    if uncovered:
        fail('A1', '%d of %d sampled climate points fall in no band; the layer must cover the '
                   'whole cube or the game falls back to nearest-neighbour there'
                   % (uncovered, SAMPLES))
    if mismatched:
        fail('A3', 'selector disagrees with the layer, e.g. %s' % (mismatched[:2],))

    # --- A4 ------------------------------------------------------------------------------
    steps = {p: v for p, v in out.items() if os.path.basename(p).startswith('step_')}
    # One step per MERGED authority region, not per band. Emitting per band gave 44, and a
    # 44-deep reference chain as final_density killed the dedicated server twice during level
    # preparation with no exception and no crash dump. A3 proves the merge lost no territory.
    if len(steps) > len(bands):
        fail('A4', 'more selector steps (%d) than bands (%d); the merge is inventing regions'
             % (len(steps), len(bands)))
    if len(steps) > 12:
        fail('A4', 'the chain is %d steps deep; merged authority regions should be a handful, '
                   'and depth here has already cost two dead servers' % len(steps))
    named = {'%s:authority/%s' % (authorities_module.NS, os.path.basename(p)[:-5]) for p in out}
    for path, data in steps.items():
        for ref in json.dumps(json.loads(data)).split('"'):
            if ref.startswith('%s:authority/' % authorities_module.NS) and ref not in named:
                fail('A4', '%s references %s, which is not emitted; an orphan step is a '
                           'datapack that refuses to load' % (os.path.basename(path), ref))
    biggest = max((len(v) for v in steps.values()), default=0)
    if biggest > 4096:
        fail('A4', 'a selector step is %d bytes; the chain is being written inline and will '
                   'grow as 5^bands rather than linearly' % biggest)

    # --- A5 ------------------------------------------------------------------------------
    targets = {authorities_module.owner_of(b['biome'], owners) for b in bands}
    if len(targets) < 2:
        fail('A5', 'only one authority is reachable; the selector is not selecting anything')
    # Every authority the chain can reach must have a file, or the datapack will not load.
    leaves = {os.path.basename(p)[:-5] for p in out if not os.path.basename(p).startswith('step_')}
    for target in targets:
        if target not in leaves:
            fail('A5', 'the chain can reach authority %r but no density function was emitted '
                       'for it; Minecraft resolves these at load time and will refuse the pack'
                       % target)
    # Stage 1 moves no terrain: the leaves are byte-identical to each other.
    bodies = {out[p] for p in out if not os.path.basename(p).startswith('step_')}
    if len(bodies) != 1:
        fail('A5', 'authority expressions already differ; stage 1 is meant to be inert so that '
                   'a later regression cannot be confused with the migration')
    return problems


def fixture():
    import gen_alfheim_biomes
    bands = [dict(b) for b in gen_alfheim_biomes.LAYER['biomes']]
    owners = [dict(a) for a in authorities_module.authorities()]
    out, entry = authorities_module.build(bands, owners)
    return bands, owners, out, entry


def self_test():
    tests = []

    def overlap_the_partition(bands, owners, out, entry):
        bands.append({'biome': bands[0]['biome'], 'parameters': dict(bands[0]['parameters'])})
        return bands, owners, out, entry
    tests.append(('A1', overlap_the_partition))

    def double_claim(bands, owners, out, entry):
        owners[0] = dict(owners[0]); owners[0]['biomes'] = set(owners[0]['biomes'])
        owners.insert(1, {'id': 'rogue', 'biomes': set(owners[0]['biomes']), 'note': 'x'})
        return bands, owners, out, entry
    tests.append(('A2', double_claim))

    def drop_a_leaf(bands, owners, out, entry):
        for p in list(out):
            if os.path.basename(p) == 'void.json':
                del out[p]
        return bands, owners, out, entry
    tests.append(('A5', drop_a_leaf))

    def sever_the_chain(bands, owners, out, entry):
        # Point one step's miss branch at the wrong authority: the layer still says one thing
        # and the selector now says another for every point that falls past it.
        # A STEP, not any file: with the chain merged down to one step, an index into the whole
        # output lands on an authority leaf, whose root is a density expression with no branches.
        key = sorted(p for p in out if os.path.basename(p).startswith('step_'))[0]
        node = json.loads(out[key])
        def retarget(n):
            if isinstance(n, dict):
                for k in ('when_in_range', 'when_out_of_range'):
                    if isinstance(n[k], str) and n[k].endswith('/upstream'):
                        n[k] = '%s:authority/void' % authorities_module.NS
                    else:
                        retarget(n[k])
        retarget(node)
        out[key] = (json.dumps(node) + '\n').encode()
        return bands, owners, out, entry
    tests.append(('A3', sever_the_chain))

    def leave_a_hole(bands, owners, out, entry):
        victim = max(bands, key=lambda b: (authorities_module.span(b['parameters'],
                                                                   'continentalness')[1]
                                           - authorities_module.span(b['parameters'],
                                                                     'continentalness')[0]))
        bands.remove(victim)
        return bands, owners, out, entry
    tests.append(('A1', leave_a_hole))

    dead = 0
    for code, mutate in tests:
        bands, owners, out, entry = mutate(*fixture())
        hit = any(p.startswith(code) for p in validate(bands, owners, out, entry))
        print('  %s  %s' % (code, 'FIRES' if hit else 'SILENT -- CHECK IS DEAD'))
        dead += not hit
    print('\n  %d/%d checks proven to fire' % (len(tests) - dead, len(tests)))
    return 1 if dead else 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    bands, owners, out, entry = fixture()
    problems = validate(bands, owners, out, entry)
    steps = sum(1 for p in out if os.path.basename(p).startswith('step_'))
    print('%d bands -> %d selector step(s) + %d authority leaves, %d climate points sampled'
          % (len(bands), steps, len(out) - steps, SAMPLES))
    for problem in problems:
        print('  ' + problem)
    print('\n  %d problem(s)' % len(problems))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
