#!/usr/bin/env python3
"""Measure the breakline's shape off the shipped density function, against a control.

WHY THIS EXISTS AND NOT JUST A FRESH WORLD. Generating one costs about half an hour and can only
be read after the fact. This compiles alfheim_final into a Python closure and samples it, which
turns the same question into thirty seconds -- and it caught a sign error that a generated world
would have shown only as "the rim got worse": lifting the shelf's underside by SUBTRACTING from
its y_clamped_gradient drove the median face height from 69 blocks to 123, because the gradient
saturates at +/-1 outside its span and the min() went the other way entirely.

IT IS NOT A SUBSTITUTE FOR A GENERATED WORLD. Each noise is drawn as an independent sample rather
than evaluated as a field, so this says nothing about connectivity, about whether fragments
percolate into one welded mass, or about anything an aquifer or a surface rule does. It answers
exactly one question: what SHAPE does the density function describe at a point, and how much does
that shape vary from place to place. Use probe_void_fragments.py for landforms and
probe_void_margin.py for a generated cross-section.

ALWAYS READ IT AGAINST THE CONTROL, which is the same function with the breakline terms zeroed.
B-86 and B-93 both burned a calibration cycle on a metric with no meaningful zero. The control
here has one: it reports edge spread 0.0000 and face standard deviation 3.2, because before these
terms existed every point at the same continentalness had literally the same profile.

    python tools/measure_void_edge.py
    python tools/measure_void_edge.py --segments 60 --columns 60
"""
import argparse
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Noises the void branch and its neighbours read. Anything not listed resolves to 0.0.
SAMPLED = (
    'alfheim:void/relief', 'alfheim:void/detail', 'alfheim:void/rim_base',
    'alfheim:void/breakline', 'alfheim:void/spall', 'alfheim:void/fragments',
    'alfheim:void/fracture', 'alfheim:void/shape',
    'alfheim:fields/terrace_saw', 'alfheim:fields/terrace_weight',
    'alfheim:deepworks/cavities',
)
# The breakline terms, zeroed to build the control.
EDGE_TERMS = ('EDGE_BITE', 'EDGE_SWING', 'EDGE_SPALL', 'EDGE_LIFT', 'EDGE_LIFT_SWING')
ORDINARY_SEABED = 30


def compile_df(node):
    """Density-function JSON -> f(c, y, noises, ordinary) -> float."""
    if isinstance(node, (int, float)):
        value = float(node)
        return lambda c, y, n, o: value
    if isinstance(node, str):
        if node == 'mythicbotany:alfheim_continentalness':
            return lambda c, y, n, o: c
        if node == 'minecraft:y':
            return lambda c, y, n, o: float(y)
        key = node
        return lambda c, y, n, o: o(key, y)
    kind = node['type'].split(':')[-1]
    if kind in ('cache_2d', 'cache_once', 'cache_all_in_cell', 'interpolated', 'flat_cache',
                'blend_density'):
        return compile_df(node['argument'])
    if kind in ('add', 'mul', 'min', 'max'):
        a, b = compile_df(node['argument1']), compile_df(node['argument2'])
        if kind == 'add':
            return lambda c, y, n, o: a(c, y, n, o) + b(c, y, n, o)
        if kind == 'mul':
            return lambda c, y, n, o: a(c, y, n, o) * b(c, y, n, o)
        if kind == 'min':
            return lambda c, y, n, o: min(a(c, y, n, o), b(c, y, n, o))
        return lambda c, y, n, o: max(a(c, y, n, o), b(c, y, n, o))
    if kind == 'abs':
        a = compile_df(node['argument'])
        return lambda c, y, n, o: abs(a(c, y, n, o))
    if kind == 'square':
        a = compile_df(node['argument'])
        return lambda c, y, n, o: a(c, y, n, o) ** 2
    if kind == 'clamp':
        a, low, high = compile_df(node['input']), node['min'], node['max']
        return lambda c, y, n, o: min(high, max(low, a(c, y, n, o)))
    if kind == 'y_clamped_gradient':
        from_y, to_y = node['from_y'], node['to_y']
        from_v, to_v = node['from_value'], node['to_value']
        span = to_y - from_y

        def gradient(c, y, n, o):
            f = (y - from_y) / span
            return from_v + min(1.0, max(0.0, f)) * (to_v - from_v)
        return gradient
    if kind == 'range_choice':
        inp = compile_df(node['input'])
        low, high = node['min_inclusive'], node['max_exclusive']
        inside, outside = compile_df(node['when_in_range']), compile_df(node['when_out_of_range'])

        def choose(c, y, n, o):
            value = inp(c, y, n, o)
            return inside(c, y, n, o) if low <= value < high else outside(c, y, n, o)
        return choose
    if kind in ('noise', 'shifted_noise'):
        key = node['noise']
        return lambda c, y, n, o: n.get(key, 0.0)
    if kind == 'constant':
        value = float(node['argument'])
        return lambda c, y, n, o: value
    if kind == 'old_blended_noise':
        return lambda c, y, n, o: 0.0
    raise ValueError('measure_void_edge cannot evaluate ' + node['type'])


def build(edge_terms_on):
    import gen_void_worldgen
    import gen_alfheim_biomes
    saved = {k: getattr(gen_void_worldgen, k) for k in EDGE_TERMS}
    if not edge_terms_on:
        for k in EDGE_TERMS:
            setattr(gen_void_worldgen, k, 0.0)
    try:
        return compile_df(gen_alfheim_biomes.void_final_density())
    finally:
        for k, v in saved.items():
            setattr(gen_void_worldgen, k, v)


def ordinary(_key, y):
    """Stand-in for alfheim_initial/alfheim_caves: an ordinary sea floor. Only its sign near the
    surface matters here, because nothing in the breakline band reads it."""
    return min(1.0, max(-1.0, (ORDINARY_SEABED - y) / 12.0))


def sample():
    """Bell-ish on [-1, 1]; a summed-octave Perlin sample is not uniform."""
    return min(1.0, max(-1.0, (random.random() + random.random() + random.random() - 1.5) * 1.15))


def measure(density, cliff, segments, per_segment, seed):
    random.seed(seed)
    faces, tops, bases, edges = [], [], [], []
    band = [round(cliff + 0.0025 * i, 4) for i in range(60)]
    for _segment in range(segments):
        # breakline is broad: one draw per rim segment, shared by its columns. That is what makes
        # a headland a headland for a few hundred blocks instead of one lucky column.
        broad = sample()
        for _column in range(per_segment):
            noises = {n: sample() for n in SAMPLED}
            noises['alfheim:void/breakline'] = broad
            for c in band:
                solid = [y for y in range(-53, 140) if density(c, y, noises, ordinary) > 0]
                if len(solid) < 8:
                    continue
                run = longest = 1
                for a, b in zip(solid, solid[1:]):
                    run = run + 1 if b == a + 1 else 1
                    longest = max(longest, run)
                faces.append(longest)
                tops.append(solid[-1])
                bases.append(solid[0])
                edges.append(c)
                break
    return faces, tops, bases, edges


def report(label, faces, tops, bases, edges):
    quartiles = statistics.quantiles(faces, n=4)
    spread = max(edges) - min(edges)
    print('%-8s  face min %2d p25 %2d med %3d p75 %3d max %3d sd %4.1f | top %d..%d | '
          'base %d..%d | edge spread %.4f (~%d blocks)'
          % (label, min(faces), quartiles[0], statistics.median(faces), quartiles[2], max(faces),
             statistics.pstdev(faces), min(tops), max(tops), min(bases), max(bases),
             spread, round(spread / 0.004)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--segments', type=int, default=30)
    parser.add_argument('--columns', type=int, default=30, help='columns per rim segment')
    parser.add_argument('--seed', type=int, default=20260911)
    args = parser.parse_args()

    import gen_void_worldgen
    cliff = gen_void_worldgen.CLIFF
    total = args.segments * args.columns
    print("The Verge plain's outer edge, %d columns over %d rim segments, from the cliff "
          'inward:\n' % (total, args.segments))
    control = measure(build(False), cliff, args.segments, args.columns, args.seed)
    shaped = measure(build(True), cliff, args.segments, args.columns, args.seed)
    report('control', *control)
    report('shipped', *shaped)

    print('\nface height -- blocks of continuous vertical rock at the rim:')
    for low in range(0, 90, 10):
        c = sum(1 for f in control[0] if low <= f < low + 10)
        s = sum(1 for f in shaped[0] if low <= f < low + 10)
        print('  %2d-%2d  control %-26s shipped %s'
              % (low, low + 9, '#' * (c * 26 // total), '#' * (s * 26 // total)))

    walkable = sum(1 for f in shaped[0] if f < 40) / total
    print('\n  %.0f%% of the rim now presents under 40 blocks (control: %.0f%%)'
          % (100 * walkable, 100 * sum(1 for f in control[0] if f < 40) / total))
    if statistics.pstdev(shaped[0]) <= statistics.pstdev(control[0]):
        print('  WARNING: the shipped rim varies no more than the control. The breakline is '
              'still a contour.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
