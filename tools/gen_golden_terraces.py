"""Terrace the Golden Fields: quantized agricultural steps, in data-driven density functions.

    python tools/gen_golden_terraces.py
    python tools/gen_golden_terraces.py --check     # regenerate and compare, mutate nothing

WHY THIS SHAPE. The obvious way to terrace is `floor(h / N) * N`. Minecraft 1.20.1 has no
`floor`, no modulo and no Voronoi -- verified by enumerating every density-function type used
across all 35 vanilla density functions and noise settings. What it does have is
`y_clamped_gradient`, and a staircase is a SUM OF UNIT STEPS: one gradient per riser, 22 of them
for an 88-block band at N=4. Subtracting that staircase from y gives a sawtooth, and adding a
sawtooth to a density that falls with height cancels the fall across a tread, so the iso-surface
pins to the tread and drops at the riser. That is the whole trick.

WHY THE MASK IS A RAMP AND NEVER A BIOME TEST. B-82 reverted a climate-thresholded density
branch because climate thresholds and LibX's nearest-biome result do not coincide: the branch
replaced complete columns inside neighbouring biomes and the seams read as chunky walls. Every
factor in `terrace_weight` is therefore a continuous clamp, and each one reaches zero INSIDE the
biome's own climate box rather than at its edge, so the terrace amplitude is already zero before
the biome boundary can disagree with anything. `check_golden_terraces.py` asserts that.

WHY IT CANNOT AFFECT ANYTHING ELSE. The term is added as `weight * AMPLITUDE * saw`. Where the
weight is zero the addend is exactly zero, so `alfheim_final` is bit-identical to the untouched
generator everywhere outside the fade. That is a static property and the checker proves it.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_void_worldgen import binary, clamp, gradient  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = 'alfheim'
DF = os.path.join('kubejs', 'data', NS, 'worldgen', 'density_function', 'fields')

# --- the tread geometry -----------------------------------------------------------------------
STEP = 4                     # tread height, in blocks. Asked for 2026-09-08.

# THE CEILING ON THIS TECHNIQUE IS THE INTERPOLATION CELL, NOT THE AMPLITUDE.
# alfheim's noise settings use size_vertical 2, so Minecraft samples final_density on an
# 8-BLOCK-TALL grid and interpolates linearly between those samples. A 4-block sawtooth is a
# half-cell signal: the interpolator cannot represent it and averages most of it away. Measured
# in fresh worlds, forceloading a real Golden Fields patch each time:
#
#     N=4, amplitude 0.22   42.0% of columns on a tread   (uniform 25%)   1.7x
#     N=4, amplitude 0.60   49.9%                          (uniform 25%)   2.0x
#     N=8, amplitude 0.60   36.0%                          (uniform 12.5%) 2.9x
#
# Tripling the amplitude bought 8 points, which is what a resolution limit looks like rather
# than a tuning problem. N=8 matches the cell height and pins relatively harder, but its absolute
# flatness is worse and an 8-block riser is not a walkable agricultural step. N=4 is kept.
#
# The result is a real, measurable softening of the terrain into broad stepped shelves -- not the
# crisp geometric terracing of the offline prototype, which had no interpolation grid to fight.
# Getting that would mean size_vertical 1 for the whole dimension: four-block cells, twice the
# density samples per chunk, and a change to every biome's terrain rather than to Golden Fields.
# That is a dimension-wide performance and terrain decision, and it is the user's to make.
BAND_LO, BAND_HI = 56, 144   # the Y band that gets treads; 22 risers at N=4
WORLD_LO, WORLD_HI = -64, 320

# Terrace amplitude, in density units. This is the one number that cannot be derived from the
# data: to pin the surface, the sawtooth's drop across a riser has to exceed the final density's
# own fall over a whole tread, and that slope belongs to MythicBotany's noise router rather than
# to anything here.
#
# CALIBRATED, not guessed. A fresh world at 0.22 put 42.0% of Golden Fields surface columns
# exactly on a tread against 25% for an untreaded control -- a real signal, but far from the
# prototype's 100%, so 0.22 was under the pinning threshold. Raised and re-measured.
AMPLITUDE = 0.60

# --- the climate window -----------------------------------------------------------------------
# Golden Fields occupies cont 0.15..0.30, weird 0..1 (see BIOME_INDEX.md §3). The terracing is
# confined to the LOWER, flatter part of that continentalness range, so the higher ground stays
# continuous and wild behind the farms. Every edge is inset from the biome's own boundary.
CONT = 'mythicbotany:alfheim_continentalness'
WEIRD = 'mythicbotany:alfheim_weirdness'

CONT_IN = (0.155, 0.175)     # fade up across the biome's lower edge
CONT_OUT = (0.265, 0.290)    # fade back down before its upper edge at 0.30
WEIRD_IN = (0.020, 0.080)    # weirdness 0 is the dreamwood/golden split; stay clear of it

# WIDENED 2026-09-08 on measurement. The first pass saturated the weight only in a narrow core,
# and the probe showed the cost precisely: risers 83.0% on-tread and plot interiors 59.5%, but
# unclaimed grass columns only 32.9% against a 25% baseline. The soft aggregate was coverage, not
# resolution -- so each ramp now saturates sooner, while every edge stays inset from the biome's
# own climate box so `check_golden_terraces` G3 still finds an exact zero outside it.

# Plot cells. 1.20.1 has no Voronoi, but the two things the algorithm needs from one are a
# cell-edge distance and cells that tile the plane. |ridge| gives both: its zero contours are
# closed loops that partition the plane, and the magnitude grows toward each cell's interior.
PLOT_NOISE = 'minecraft:ridge'
PLOT_XZ = 2.0                # ridge base period is 128 blocks, so plots run about 64 across
EDGE_GAIN = 2.2              # scales |ridge| into a usable 0..1 before clamping
EDGE_IN = (0.12, 0.34)       # risers occupy the low band; flats begin above it


def ref(name):
    return f'{NS}:fields/{name}'


def ramp(src, lo, hi):
    """clamp((src - lo) / (hi - lo), 0, 1) -- a continuous 0..1 fade, no branch anywhere."""
    return clamp(binary('mul', 1.0 / (hi - lo), binary('add', src, -lo)), 0.0, 1.0)


def ramp_down(src, lo, hi):
    """1 - ramp(src, lo, hi): full below `lo`, zero above `hi`."""
    return binary('add', 1.0, binary('mul', -1.0, ramp(src, lo, hi)))


def flat_cache(fn):
    """Evaluate once per column. Every factor in the weight is 2-D, so all of it belongs here --
    this is what keeps the cost off the per-cell path."""
    return {'type': 'minecraft:flat_cache', 'argument': fn}


# --- deliverable 1: the sawtooth ---------------------------------------------------------------
def terrace_saw():
    """(y - BAND_LO)/STEP - Q(y) - 0.5, where Q is a staircase of unit risers.

    The riser for tread k spans k..k+1, so the last SOLID block of a tread is k itself. Placing
    it at k-1..k instead terraces just as hard but leaves every flat one block below the tread
    line -- measured at 73% of columns on the wrong residue in the prototype.
    """
    y = gradient((WORLD_LO, WORLD_HI), WORLD_LO, WORLD_HI)
    risers = [gradient((k, k + 1), 0.0, 1.0)
              for k in range(BAND_LO + STEP, BAND_HI + STEP, STEP)]
    staircase = risers[0]
    for r in risers[1:]:
        staircase = binary('add', staircase, r)
    frac = binary('mul', 1.0 / STEP, binary('add', y, -BAND_LO))
    saw = binary('add', binary('add', frac, binary('mul', -1.0, staircase)), -0.5)
    # The sawtooth is only meaningful inside the treaded band; outside it the staircase is
    # saturated and `frac` would ramp away without bound. Clamping keeps the addend bounded
    # everywhere, which is what makes the amplitude a true ceiling on the disturbance.
    return clamp(saw, -0.5, 0.5), len(risers)


# --- deliverable 2: the weight -----------------------------------------------------------------
def plot_edge():
    """|ridge| as a cell-edge proxy: near zero on a plot boundary, large in a plot's interior."""
    n = {'type': 'minecraft:noise', 'noise': PLOT_NOISE,
         'xz_scale': PLOT_XZ, 'y_scale': 0.0}
    return flat_cache(clamp(binary('mul', EDGE_GAIN, {'type': 'minecraft:abs', 'argument': n}),
                            0.0, 1.0))


def terrace_weight():
    """edge blend x continentalness window x weirdness ramp, all continuous, all 2-D."""
    edge = ramp(ref('plot_edge'), *EDGE_IN)
    window = binary('mul', ramp(CONT, *CONT_IN), ramp_down(CONT, *CONT_OUT))
    weird = ramp(WEIRD, *WEIRD_IN)
    return flat_cache(binary('mul', edge, binary('mul', window, weird)))


# --- deliverable 3: the injection --------------------------------------------------------------
def terrace_term():
    """weight * AMPLITUDE * saw -- the exact addend appended to the final density.

    Where the weight is zero this is exactly zero, so the sum is bit-identical to the untouched
    density. Nothing outside the fade can move.
    """
    return binary('mul', ref('terrace_weight'),
                  binary('mul', AMPLITUDE, ref('terrace_saw')))


def inject(final_density):
    """Append the terrace term to whatever the base generator produced."""
    return binary('add', final_density, terrace_term())


def strip(final_density):
    """The inverse of inject(): return the density with the terrace addend removed.

    Every existing guard on alfheim_final navigates from the void range_choice at the top, and
    wrapping that in an `add` would otherwise break all of them. Rather than loosen those checks
    -- they are the ones that caught B-82 -- each calls strip() first and keeps asserting exactly
    what it asserted before, on the base. Passing a density that is NOT terraced returns it
    unchanged, so a guard cannot silently accept the wrong shape.
    """
    if (isinstance(final_density, dict)
            and final_density.get('type') == 'minecraft:add'
            and final_density.get('argument2') == terrace_term()):
        return final_density['argument1']
    return final_density


def files():
    saw, risers = terrace_saw()
    return {
        os.path.join(DF, 'terrace_saw.json'): saw,
        os.path.join(DF, 'plot_edge.json'): plot_edge(),
        os.path.join(DF, 'terrace_weight.json'): terrace_weight(),
    }, risers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out, risers = files()
    bad = 0
    for path, doc in sorted(out.items()):
        body = json.dumps(doc, indent=2) + '\n'
        full = os.path.join(ROOT, path)
        if a.check:
            cur = open(full, encoding='utf-8').read() if os.path.exists(full) else None
            if cur != body:
                print(f'  STALE  {path}')
                bad += 1
            continue
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8', newline='\n') as f:
            f.write(body)
        print(f'  wrote {path}  ({len(body):,} bytes)')
    if a.check:
        print('PASS: terrace density functions match their generator' if not bad
              else f'!! {bad} stale file(s); run tools/gen_golden_terraces.py')
        return 1 if bad else 0
    print(f'\n  {risers} risers, tread {STEP} blocks, band Y {BAND_LO}..{BAND_HI}, '
          f'amplitude {AMPLITUDE}')
    return 0


if __name__ == '__main__':
    sys.exit(main())


# --- deliverable 4: surface decoration ---------------------------------------------------------
#
# A SURFACE RULE MAY TEST THE BIOME; A DENSITY FUNCTION MAY NOT. That distinction is the whole
# reason this half is easy and the density half was not. A surface rule only chooses which block
# to paint on a column that already exists, so a biome test there can produce at worst a colour
# seam. A density branch keyed on biome MOVES TERRAIN, and where the climate threshold and LibX's
# nearest-biome result disagree the result is the sheer wall B-82 had to revert. Same lookup,
# entirely different blast radius.
#
# `minecraft:steep` is vanilla's own slope test -- it is what puts stone on mountainsides instead
# of grass. On a terraced field the only steep ground IS the riser, so it separates tread from
# retaining wall without any extra noise.
FIELD_BIOME = 'mythicbotany:golden_fields'
PLOT_EDGE_T = 0.35          # |ridge| above this is plot interior; below it is the verge

BED = 'minecraft:farmland'          # tread: worked ground
BED_DRY = 'minecraft:coarse_dirt'   # tread margin
VERGE = 'minecraft:dirt_path'       # walked plot boundary
RETAIN = 'alfheim:moonstone_livingrock_bricks'   # riser: dressed retaining wall
RETAIN_ROUGH = 'alfheim:cracked_livingrock'      # riser: where it has failed


def _block(name):
    return {'type': 'minecraft:block', 'result_state': {'Name': name}}


def _cond(test, rule):
    return {'type': 'minecraft:condition', 'if_true': test, 'then_run': rule}


def _seq(rows):
    return {'type': 'minecraft:sequence', 'sequence': rows}


def _ridge(lo, hi):
    return {'type': 'minecraft:noise_threshold', 'noise': PLOT_NOISE,
            'min_threshold': lo, 'max_threshold': hi}


def surface_rule():
    """Paint treads as worked fields and risers as retaining walls.

    |ridge| has no single-rule form, so the plot interior is expressed as the OR of its two
    tails: a sequence is first-match-wins, which is exactly an OR here.
    """
    floor = {'type': 'minecraft:stone_depth', 'offset': 0, 'add_surface_depth': False,
             'secondary_depth_range': 0, 'surface_type': 'floor'}
    interior = _seq([
        _cond(_ridge(PLOT_EDGE_T, 100), _block(BED)),
        _cond(_ridge(-100, -PLOT_EDGE_T), _block(BED)),
        _cond(_ridge(PLOT_EDGE_T * 0.55, 100), _block(BED_DRY)),
        _cond(_ridge(-100, -PLOT_EDGE_T * 0.55), _block(BED_DRY)),
        _block(VERGE),
    ])
    risers = _seq([
        _cond(_ridge(-0.25, 100), _block(RETAIN)),
        _block(RETAIN_ROUGH),
    ])
    return _cond({'type': 'minecraft:biome', 'biome_is': [FIELD_BIOME]},
                 _cond(floor, _seq([
                     _cond({'type': 'minecraft:steep'}, risers),
                     interior,
                 ])))
