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

# THE INTERPOLATION-CELL THEORY WAS TESTED AND IT WAS WRONG. It is recorded here because the
# numbers below were read under it and would otherwise mislead. alfheim_final contains no
# `minecraft:interpolated` -- the markers live inside alfheim_height and alfheim_caves -- so it
# is evaluated per block at full resolution and the 8-block cell grid never touched the sawtooth.
# The size_vertical 1 probe on 2026-09-08 confirmed it: 49.8% on-tread against 49.9% at 2.
# Measured in fresh worlds, forceloading a real Golden Fields patch each time:
#
#     N=4, amplitude 0.22   42.0% of columns on a tread   (uniform 25%)   1.7x
#     N=4, amplitude 0.60   49.9%                          (uniform 25%)   2.0x
#     N=8, amplitude 0.60   36.0%                          (uniform 12.5%) 2.9x
#
# Tripling the amplitude bought 8 points because on-tread share is a saturating measure, not
# because a cell grid was eating the signal. N=8 pins harder in relative terms but its absolute
# flatness is worse and an 8-block riser is not a walkable agricultural step. N=4 is kept.
BAND_LO, BAND_HI = 56, 144   # the Y band that gets treads; 22 risers at N=4
WORLD_LO, WORLD_HI = -64, 320

# Terrace amplitude, in density units. This is the one number that cannot be derived from the
# data: to pin the surface, the sawtooth's drop across a riser has to exceed the final density's
# own fall over a whole tread, and that slope belongs to MythicBotany's noise router rather than
# to anything here.
#
# LOWERED 2026-09-09 after the field review. 0.60 was chosen to push the on-tread share up,
# and it did: measured on the shipped world, 68.7% of Golden Fields columns sat on one residue
# against a 25% uniform baseline, 2.75x. That is what the review saw and rejected -- "the effect
# of multiple floors stacked on top of each other rather than gradual laid out terraces over a
# large terrain distance". On-tread share rewards exactly the failure mode: a number that rises
# as EVERY column gets quantised cannot tell terracing from a staircase, and chasing it built
# one.
#
# The intent is occasional worked shelves on ground gentle enough to farm, with steeper ground
# left wild behind them. Whether a column pins depends on the sawtooth's rise per block,
# AMPLITUDE/STEP, against the final density's own fall per block: at 0.60 that is 0.15 and
# overwhelms the natural fall everywhere the weight is non-zero. At 0.20 it is 0.05, the same
# order as the terrain's own gradient, so the surface pins where the ground is already gentle
# and is left alone where it is not. The selectivity is the point, not the average.
AMPLITUDE = 0.20

# --- the climate window -----------------------------------------------------------------------
# Golden Fields occupies cont 0.15..0.30, weird 0..1 (see BIOME_INDEX.md §3). The terracing is
# confined to the LOWER, flatter part of that continentalness range, so the higher ground stays
# continuous and wild behind the farms. Every edge is inset from the biome's own boundary.
CONT = 'mythicbotany:alfheim_continentalness'
WEIRD = 'mythicbotany:alfheim_weirdness'
TEMP = 'mythicbotany:alfheim_temperature'

# NARROWED BACK 2026-09-09. These were widened on 2026-09-08 to lift the aggregate on-tread
# share from 49.8% to 59.7%. It worked by saturating the weight over more of the biome, which
# is the same thing as "they apply far too persistently" -- the metric went up because the
# defect got worse. Restored to values that terrace a core and leave the edges alone.
CONT_IN = (0.170, 0.190)     # fade up across the biome's lower edge
CONT_OUT = (0.235, 0.265)    # fade back down well before its upper edge at 0.30
WEIRD_IN = (0.030, 0.100)    # weirdness 0 is the dreamwood/golden split; stay clear of it

# THE AXIS THE WEIGHT WAS MISSING. Golden Fields and Silverbark Wood share the whole of
# continentalness 0.15..0.30 and overlap in weirdness; the only climate field that separates
# them is TEMPERATURE, at -0.3 (BIOME_INDEX.md). The weight read the two axes they share and
# not the one that tells them apart, so the terracing crossed the boundary: measured on the
# shipped world, 59.3% of Silverbark Wood columns on one residue against Golden Fields' 68.7%.
# A climate ramp is not the biome test B-82 had to revert -- it is the same kind of continuous
# fade the other three factors already are, and it reaches exactly zero on the cold side.
TEMP_IN = (-0.280, -0.180)

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
    # OUTSIDE THE BAND THE SAWTOOTH MUST BE ZERO, NOT MERELY BOUNDED. The previous version
    # clamped and stopped there, which left a CONSTANT -0.5 on every block from Y 53 down to
    # bedrock and +0.5 above Y 148 -- `frac` saturates against a staircase that has run out of
    # risers, and clamp() turns a runaway into a constant rather than into nothing. The weight
    # is a flat_cache with no vertical term, so that constant applied down the whole column.
    #
    # At AMPLITUDE 0.60 it was a -0.30 density subtraction through 118 blocks of deep rock, and
    # the field review found it. Measured on the shipped world, the deep band Y -64..48:
    #
    #     under golden_fields      42.2% void, 2.03% lava
    #     under dreamwood_forest   25.3% void, 1.22% lava
    #     under alfheim_plains     19.4% void, 0.89% lava
    #
    # Subterranean caverns and opened lava under a surface feature with no business below Y 56.
    # G5 never saw it because it asserts the +/-0.5 BOUND and the tread peaks, both of which a
    # saturated constant satisfies. A window fixes it at the source: the addend is now exactly
    # 0.0 outside BAND_LO..BAND_HI, fading over one tread at each end so the outermost treads
    # are not cut off with a step.
    band = binary('min', gradient((BAND_LO - STEP, BAND_LO), 0.0, 1.0),
                  gradient((BAND_HI, BAND_HI + STEP), 1.0, 0.0))
    return binary('mul', band, clamp(saw, -0.5, 0.5)), len(risers)


# --- deliverable 2: the weight -----------------------------------------------------------------
def plot_edge():
    """|ridge| as a cell-edge proxy: near zero on a plot boundary, large in a plot's interior."""
    n = {'type': 'minecraft:noise', 'noise': PLOT_NOISE,
         'xz_scale': PLOT_XZ, 'y_scale': 0.0}
    return flat_cache(clamp(binary('mul', EDGE_GAIN, {'type': 'minecraft:abs', 'argument': n}),
                            0.0, 1.0))


def terrace_weight():
    """edge blend x continentalness window x weirdness ramp x temperature ramp.

    All four factors are continuous and 2-D, and any one of them reaching zero zeroes the
    whole weight, which is what lets G3 find an exact 0.0 outside the biome's climate box.
    """
    edge = ramp(ref('plot_edge'), *EDGE_IN)
    window = binary('mul', ramp(CONT, *CONT_IN), ramp_down(CONT, *CONT_OUT))
    weird = ramp(WEIRD, *WEIRD_IN)
    temp = ramp(TEMP, *TEMP_IN)
    climate = binary('mul', window, binary('mul', weird, temp))
    return flat_cache(binary('mul', edge, climate))


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
