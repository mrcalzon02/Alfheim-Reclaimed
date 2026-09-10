"""Prove the Golden Fields terracing cannot disturb anything outside Golden Fields.

    python tools/check_golden_terraces.py

This exists because of B-82. A climate-keyed density change is the one class of edit in this
pack that has already shipped a visible defect: thresholds and LibX's nearest-biome result do
not coincide, so a branch that replaced whole columns produced sheer walls inside neighbouring
biomes. The terracing is built as a bounded ADDEND with a continuous weight precisely so that
failure is impossible, and the point of this file is to assert that rather than trust it.

G1  the shipping density functions match their generator
G2  the injection is an `add`, and its first argument is the untouched density unchanged
G3  the weight is exactly 0.0 outside Golden Fields' climate box -- continentalness,
    weirdness AND temperature -- on a dense sweep
G4  the weight is continuous -- no step larger than a small epsilon anywhere in the sweep
G5  the sawtooth is bounded to +/-0.5 across the entire world height, so the worst-case
    disturbance is AMPLITUDE/2 and not a function of terrain
G6  the surface rule paints only inside Golden Fields
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_golden_terraces as T  # noqa: E402
from gen_alfheim_biomes import void_final_density  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --- a small interpreter for the subset we emit ------------------------------------------------
def ev(node, env):
    if isinstance(node, (int, float)):
        return float(node)
    if isinstance(node, str):
        if node in env:
            return float(env[node])
        raise KeyError(f'unresolved reference {node}')
    t = node['type']
    if t == 'minecraft:y_clamped_gradient':
        y, f, to = env['@y'], node['from_y'], node['to_y']
        fv, tv = float(node['from_value']), float(node['to_value'])
        if y <= f:
            return fv
        if y >= to:
            return tv
        return fv + (y - f) / (to - f) * (tv - fv)
    if t == 'minecraft:add':
        return ev(node['argument1'], env) + ev(node['argument2'], env)
    if t == 'minecraft:mul':
        return ev(node['argument1'], env) * ev(node['argument2'], env)
    if t == 'minecraft:min':
        return min(ev(node['argument1'], env), ev(node['argument2'], env))
    if t == 'minecraft:max':
        return max(ev(node['argument1'], env), ev(node['argument2'], env))
    if t == 'minecraft:abs':
        return abs(ev(node['argument'], env))
    if t == 'minecraft:clamp':
        return max(float(node['min']), min(float(node['max']), ev(node['input'], env)))
    if t in ('minecraft:flat_cache', 'minecraft:cache_2d', 'minecraft:cache_once',
             'minecraft:interpolated'):
        return ev(node['argument'], env)
    raise NotImplementedError(t)


def load(name):
    p = os.path.join(ROOT, T.DF, name + '.json')
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def main():
    problems = []

    def fail(code, msg):
        problems.append(code)
        print(f'  {code}  {msg}')

    # ---- G1
    for path, doc in T.files()[0].items():
        full = os.path.join(ROOT, path)
        body = json.dumps(doc, indent=2) + '\n'
        if not os.path.exists(full) or open(full, encoding='utf-8').read() != body:
            fail('G1', f'{path} does not match its generator')

    saw, weight = load('terrace_saw'), load('terrace_weight')

    # ---- G2
    final = void_final_density()
    untouched = void_final_density(include_terraces=False)
    if final.get('type') != 'minecraft:add':
        fail('G2', f'final density is {final.get("type")}, expected an add')
    elif final['argument1'] != untouched:
        fail('G2', 'the injection changed the base density instead of adding to it')
    elif final['argument2'] != T.terrace_term():
        fail('G2', 'the addend is not the terrace term')

    # ---- G3 / G4: sweep the climate box and beyond it
    lo_c, hi_c = T.CONT_IN[0], T.CONT_OUT[1]
    prev = None
    worst_step = 0.0
    outside_nonzero = []
    # TEMPERATURE IS SWEPT TOO, since 2026-09-09. Golden Fields and Silverbark Wood share the
    # whole of continentalness and overlap in weirdness; temperature at -0.3 is the only field
    # that separates them, so a sweep that does not vary it cannot see the terracing cross the
    # boundary -- and it did: 59.3% of Silverbark Wood columns on one residue on the shipped
    # world, against Golden Fields' 68.7%.
    for i in range(-400, 801):
        c = i / 1000.0
        for wd in (-0.6, -0.05, 0.0, 0.02, 0.3, 0.9):
            for tp in (-0.9, -0.35, -0.30, -0.20, 0.0, 0.6):
                env = {'@y': 70, T.CONT: c, T.WEIRD: wd, T.TEMP: tp,
                       T.ref('plot_edge'): 1.0}
                w = ev(weight, env)
                # Golden Fields is cont 0.15..0.30, weirdness 0..1, temperature -0.3..1.
                # Anything outside that, the weight must be exactly zero -- not small, zero.
                if (c < 0.15 or c > 0.30 or wd <= 0.0 or tp < -0.3) and w != 0.0:
                    outside_nonzero.append((round(c, 3), wd, tp, round(w, 6)))
                if wd == 0.9 and tp == 0.6:
                    if prev is not None:
                        worst_step = max(worst_step, abs(w - prev))
                    prev = w
    if outside_nonzero:
        fail('G3', f'weight is non-zero outside the biome box at {len(outside_nonzero)} '
                   f'sample(s), first {outside_nonzero[0]}')
    # G4 detects a DISCONTINUITY, so its bound has to come from the ramps themselves rather than
    # from a constant. A linear ramp of width w, sampled every `step`, rises step/w per sample --
    # narrowing a ramp legitimately raises that, and a fixed 0.05 ceiling simply made the guard
    # fire on a narrower-but-still-continuous fade. Derive the expected rise, allow a little
    # float slack, and the check still catches the thing that matters: a step function.
    narrowest = min(T.CONT_IN[1] - T.CONT_IN[0], T.CONT_OUT[1] - T.CONT_OUT[0])
    if narrowest < 0.012:
        fail('G4', f'narrowest continentalness ramp is {narrowest:.4f} wide; that is close '
                   f'enough to a step to risk the B-82 seam')
    expected = 0.001 / narrowest
    if worst_step > expected * 1.05:
        fail('G4', f'weight jumps by {worst_step:.4f} between adjacent continentalness samples, '
                   f'above the {expected:.4f} a {narrowest:.3f}-wide ramp explains; '
                   f'it is not continuous')

    # ---- G5
    vals = [ev(saw, {'@y': y}) for y in range(T.WORLD_LO, T.WORLD_HI + 1)]
    if min(vals) < -0.5001 or max(vals) > 0.5001:
        fail('G5', f'sawtooth ranges {min(vals):+.3f}..{max(vals):+.3f}, must stay within +/-0.5')
    treads = [ev(saw, {'@y': y}) for y in range(T.BAND_LO + T.STEP, T.BAND_HI, T.STEP)]
    if not all(abs(v - 0.5) < 1e-9 for v in treads):
        fail('G5', 'the sawtooth does not peak on every tread line; the phase is wrong and the '
                   'flats will land off the tread')

    # ---- G7: the sawtooth is EXACTLY ZERO outside the treaded band.
    #
    # This is the check that was missing, and its absence is what shipped. G5 asserts the
    # +/-0.5 bound and the tread peaks; a saturated constant satisfies both. The old saw sat
    # at a constant -0.5 from Y 53 down to bedrock and +0.5 above Y 148, and because the
    # weight is a flat_cache with no vertical term, that constant applied to the whole column:
    # a -0.30 density subtraction through 118 blocks of deep rock at the shipped amplitude.
    # Measured on the world it produced, the deep band Y -64..48 under Golden Fields was 42.2%
    # void against 25.3% under Dreamwood Forest, with lava exposure up from 1.2% to 2.0%.
    #
    # A surface feature must not reach the deep. Bounded is not the same as absent.
    outside_band = [(y, round(v, 6))
                    for y, v in ((y, ev(saw, {'@y': y})) for y in range(T.WORLD_LO, T.WORLD_HI + 1))
                    if (y <= T.BAND_LO - T.STEP or y >= T.BAND_HI + T.STEP) and v != 0.0]
    if outside_band:
        fail('G7', f'the sawtooth is non-zero at {len(outside_band)} block level(s) outside the '
                   f'treaded band Y {T.BAND_LO}..{T.BAND_HI}, first {outside_band[0]} -- a '
                   f'constant addend below the band carves the deep')

    # ---- G6
    rule = T.surface_rule()
    if rule.get('if_true', {}).get('biome_is') != [T.FIELD_BIOME]:
        fail('G6', 'the surface rule is not gated to Golden Fields')

    span = T.AMPLITUDE * (max(vals) - min(vals))
    print()
    print(f'terrace: {len(treads) + 1} treads of {T.STEP} blocks, Y {T.BAND_LO}..{T.BAND_HI}')
    print(f'weight:  full only inside cont {T.CONT_IN[1]}..{T.CONT_OUT[0]}, '
          f'zero at or below weirdness {T.WEIRD_IN[0]} '
          f'and at or below temperature {T.TEMP_IN[0]}')
    print(f'worst-case density disturbance anywhere in the world: {span:.3f} '
          f'(amplitude {T.AMPLITUDE} x sawtooth span {max(vals) - min(vals):.1f})')
    print('=' * 68)
    print(f'RESULT: {len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
