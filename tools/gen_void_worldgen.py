"""Shared dry-margin density, lateral biome claims, and natural stone palettes.

All generation uses unperturbed 2D Alfheim continentalness for membership. Noise
inside the debris band varies shape; it cannot escape the empty far-field cutoff.

The dry-void contract stays entirely data-driven. Detached debris is kept above the
global water table. A sacrificial solid guard covers Minecraft's hardcoded lowest fluid
band and is stripped by Void surface rules; the safe Void Verge shelf remains solid.
"""
import json
from gen_deep_terrain import ROOT, binary, choose, gradient, condition, block, sequence, above, negate

# ONE FIELD DECIDES THE WHOLE MARGIN AND IT IS NAMED EXACTLY ONCE. Today it is
# continentalness. A dedicated void map -- authored with its own gain, so the bands are wide
# on the ground instead of sixteen blocks -- replaces this one name and nothing else, as long
# as it is normalised to the same -1..1 scale so every band constant below keeps its meaning.
MASK='mythicbotany:alfheim_continentalness'

# --- the margin, outward from the sea to the empty far field ------------------------------
#
# THE WHOLE APPROACH USED TO FIT IN 0.06 OF CONTINENTALNESS, AND THAT IS WHY IT WAS A WALL.
# Read out of `saves/New World Ferngale` on 2026-09-11: at z=223 the void_verge biome runs
# x -112..-97 -- SIXTEEN COLUMNS -- while its shelf is 60 blocks thick and its outer face
# drops 72 blocks into a column with no solid block in it at all. A ribbon four times taller
# than it is wide can only read as a curtain. Continentalness is 1.7x badlands_surface and
# then clamped, so it is steep exactly here, and widening a band costs ocean at 1:1.
#
# The breakline, as the BIOME layer draws it. Outward of this the four debris biomes begin.
CLIFF=-0.86
# And where the TERRAIN actually hands over from the shelf to the floating belt, which is not
# the same contour and should never have been.
#
# THE WALL THAT SURVIVED THE EROSION PASS WAS THIS BRANCH. `plain` spans roughly Y 15..76 and the
# debris envelope opens at Y 64, so at a single continentalness value the ground went from a
# sixty-block slab to a band that only exists above sea level. They do not overlap, so no amount
# of shaping on either side could close it: measured on void-margin-20260911-175908, the body
# carve moved runs per column from 1.21 to 1.35 and fins from 10.4% to 8.3% and left the share of
# adjacent pairs that are a 30+ block wall against nothing at 5.3%, exactly where it started.
#
# The handover happens 0.03 further out now, and the carved shelf covers the gap. What fills it
# is solid rock broken into stacks and benches, not floating fragments -- which is both the
# "attached shelves give way to detached blocks" of VOID_MARGINS.md section 1 and the answer to
# "give us actual terrain to attach features and structures to". Solid rock below sea level also
# DISPLACES the air the aquifer would otherwise have filled, so this direction cannot make the
# standing water problem worse.
# PULLED BACK 2026-09-11 AFTER MEASURING WHAT IT COST. At -0.89 the carved shelf covered 0.035
# of the debris band's 0.065 -- more than half of every debris biome -- and the void stopped
# being void: prism_drift went from 88.7% of its columns empty to 7.6%, shatterfields from 89.3%
# to 47.9%, rootfall from 92.0% to 47.2%. The field review called it exactly right: a shelf
# structure in the middle of the void, where there should be void.
#
# The wall does not need it. Moving the handover outward was compensating for an underside lift
# that was too weak at the time; RIM_BASE_LIP has since risen to y48..72, which puts the outer
# underside around Y 53 against a debris envelope opening at Y 64. Eleven blocks of exposed face
# is not a wall, and VG9 now caps how much of the debris band the shelf may take at all.
BREAK=-0.866
# Outer bound of the Void terrain branch and inland edge of the Verge plain proper. RIM stays
# strictly inside BIOME_RIM: check_worldgen W7 requires that, because void-shaped terrain
# under an ordinary biome reads as corruption rather than as the edge of the world.
RIM=-0.722
BIOME_RIM=-0.72
# The waterline. Alfheim Ocean claims everything inland of this; outward of it the approach is
# emerged land, so THE SEA ENDS AGAINST A COAST RATHER THAN AGAINST A DELETION.
COAST_RIM=-0.55
# Where the coast has finished descending into ordinary sea floor.
COAST_TOE=-0.46
# Dry the inward shoulder as well as the visible margin so neighbouring water centres cannot
# bleed through the breakline. Floodedness is evaluated at block coordinates, so it must use
# the exact shifted continentalness field.
#
# THIS NUMBER IS NOT A TUNING CHOICE AND MUST NOT BE PULLED BACK TOWARD THE RIM.
# Aquifer.NoiseBasedAquifer samples preliminary surface at chunk offsets spanning -3..+1 and
# then blends the three nearest aquifer cells, so void air below sea level within roughly
# 48..80 blocks of a seabed below sea level is filled to Y 64 whatever final density said.
# What was actually wrong is that the dried band was left AT SEABED HEIGHT: 123,145 of
# 348,224 ocean columns in `New World Ferngale` carried no water and nothing above Y 40 --
# an ocean biome over an open dry basin, which is the "deeps with nothing above them" of the
# 2026-09-11 field review. The band is emerged land now, so drying it costs nothing.
# check_void_geology VG7 asserts that every dried column is on the plain and above sea level.
DRY_AQUIFER_RIM=-0.58
TERMINAL=-0.925
# Absolute debris limit. Beyond it the branch returns a literal -1.0, so "zero terrain in the
# far field" is a structural property of the function rather than a tuning outcome. The strip
# check_void_surface_support.py reserves for terminal landings (-0.94..-0.925) stays inside it.
FRINGE=-0.99
# Detached debris lives above the global water table, around the same height as the Verge
# shelf it broke away from, so a fragment reads as the land that used to continue.
#
# THE CEILING IS WIDE AND IT WANDERS, and the first fresh world is why. With the fall spanning
# 86..100 the envelope crossed zero at a fixed Y 93 and, being far steeper than the fragment
# noise, decided every top: 74% of shatterfields columns came back at exactly Y 92, 55% of
# prism_drift, 49% of rootfall. A debris belt planed off to one height is a table, not a break.
# The fall now spans 40 blocks rather than 14, so the fragment field's own vertical variation
# is the larger term, and CEILING_WANDER moves the crossing itself by roughly +/-9 blocks.
# LOWERED after the first cross-section. At (68,78)/(84,124) the belt sat Y 85..110 while the
# Verge shelf it is meant to have broken off sits at Y 71, so the fragments read as islands in
# the sky above intact ground rather than as the land coming apart. The band now straddles the
# shelf: solid from about Y 67 to about Y 82, tops wandering Y 73..91.
DEBRIS_Y_RISE=(64,70)
DEBRIS_Y_FALL=(68,96)
CEILING_WANDER=0.45
# The Verge is land, not a curtain. Without a base the shelf was solid from the basal guard at
# Y -54 all the way to its surface, so wherever its continentalness footprint was narrow it
# generated as a 130-block wall -- the vertical fins the September 9 field review photographed.
# It now has an underside around Y 13, wandering, which leaves a deep cliff face and a slab of
# ground roughly 60 blocks thick: enough to carry the structures check_void_surface_support
# requires, and little enough to read as the edge of a broken world.
RIM_BASE=(4,22)
RIM_BASE_WANDER=0.6
# AND THE UNDERCUT IS LOCAL TO THE LIP NOW, BECAUSE THE 2026-09-09 REPAIR CUT BOTH FACES.
# rim_base was applied across the whole Verge band, including the side facing the sea, so the
# shelf stood free on both faces: at z=223 in `New World Ferngale` the seabed at x=-113 is
# solid -53..28 and the Verge one column outward at x=-112 is solid 11..34, a 64-block void
# opening directly under the ground the player is meant to walk in on. `attach` fades the
# undercut in over the last UNDERCUT of the band, so the plain is rooted to bedrock where it
# is walked and only the cliff face is cut away.
#
# IT MUST BE WIDER THAN EDGE_WIDTH, AND THE FIRST GENERATED WORLD IS WHY. At 0.06 against an
# erosion band of 0.09 there was a strip where the breakline erosion removed whole columns from
# a shelf that `attach` had already welded back down to bedrock. What survived in that strip was
# not a butte: it was a 130-block fin. Read out of `void-margin-20260911-171819` at z=-704,
# x=-1711 is void_verge solid -53..76 with prism_drift carrying nothing at all on either side of
# it -- the exact vertical curtain the September 9 review rejected, rebuilt one column wide.
# Erosion only reads as the ground coming apart where the ground is already a slab. VG8 asserts
# the containment now; the analytic sweep in measure_void_edge.py cannot see it, because it
# samples one column at a time and a fin and a butte look identical from inside one column.
UNDERCUT=0.14
# How hard `attach` pushes the underside down outside the lip. It has to clear the underside
# gradient's own floor (-1.0) plus its wander, or "rooted" is only rooted on average.
ATTACH_BIAS=2.0
# The plain's surface. A band five times wider than the old ribbon can carry real relief --
# but never enough to reach the water table, and VG7 asserts that from these three numbers
# rather than capping each amplitude separately and hoping the sum behaves.
RIM_RELIEF=0.34
RIM_DETAIL=0.14
# The approach's surface at three declared heights, INTERPOLATED BETWEEN GRADIENTS rather than
# offset by a scalar. An offset cannot move a y_clamped_gradient's crossing further than its own
# span: outside the span it saturates at +/-1, so subtracting more than 1 makes the term negative
# at EVERY height and the column disappears. Measured on the first attempt at this -- an elevation
# of -2.2 against a 24-block span left continentalness -0.52..-0.48 with no solid block anywhere
# in the column. It is the same trap as the underside lift, which cost the same measurement, and
# the same fix: interpolating two gradients moves the surface the term describes, an offset only
# moves its value. Every span is 24 blocks so a given relief amplitude displaces the surface by
# the same distance wherever it is applied.
RIM_TOP_BREAK=(77,101)   # ~Y89 at the breakline: the approach is highest where the world ends
RIM_TOP_DRY=(62,86)      # ~Y74 at the dry-aquifer rim, and VG6 bounds the dried band from here
RIM_TOP_SEA=(22,46)      # ~Y34 where ordinary density takes over, well under the sea floor
# --- and the approach carries its own elevation ------------------------------------------
#
# THE COAST WAS A STEP FUNCTION WEARING A BLEND'S CLOTHES. `approach` used to interpolate two
# DENSITIES -- coast*normal + (1-coast)*plain -- and between the two surfaces both are saturated:
# `normal` sits at -1 everywhere above its own crossing and `plain` at +1 everywhere below its
# own. Through that whole band the mix evaluates to 1 - 2*coast, which does not depend on Y.
# The surface cannot travel from one height to the other; it JUMPS when coast passes 0.5. That is
# the sheer wall where the Void Shore meets the sea in the 2026-09-11 screenshots, and it is the
# same saturation defect as the knife-cut faces, in a third place.
#
# One surface now, with its height carried by the mask. Two segments, because one cannot do both
# jobs: the approach must stay clear of the water table across the entire dried band -- every
# column the aquifer dries has to be land, VG7 -- and then reach the sea floor quickly enough
# that the last stretch reads as a beach rather than a plateau rim.

# --- the breakline, which was a contour line and is now a coast ---------------------------
#
# EVERY POINT AT THE SAME CONTINENTALNESS USED TO HAVE THE SAME PROFILE, and that is the whole
# reason the edge photographs as one continuous curtain. The margin was a pure function of a
# single smooth 2D scalar, so its outer edge was a contour of that scalar: no bays, no
# headlands, no gaps, and the same face height along its entire length. Fragment noise beyond
# the cliff is what gives the bottom of the drop its crenulation -- the part of the current
# result the field review liked -- and nothing was doing the equivalent job at the lip.
#
# Three terms, because three different things have to vary. EDGE_WIDTH is how far inland the
# break reaches; `appetite` is broad, so whole stretches of rim survive at full height while
# whole stretches are cut down into bays; `spall` is local and fully three-dimensional, so it
# notches the face itself into ledges, alcoves and standing stacks rather than only lowering
# the top. Erosion is clamped at zero: it may remove the lip, never add to it.
EDGE_WIDTH=0.11
EDGE_BITE=0.40
EDGE_SWING=0.80
EDGE_SPALL=0.70
# AND THE UNDERSIDE COMES UP TO MEET IT, BECAUSE CUTTING THE TOP ALONE IS NOT ENOUGH.
# Measured before this term existed: erosion on its own moved the median face height from 69
# to 62 blocks -- a distribution with a tail rather than a constant, but still a wall for most
# of its length, because the slab is 63 blocks thick at the lip and lowering its top by ten
# does not change what that presents to someone standing below it. `lift` raises the shelf's
# underside toward the break, so the slab THINS as well as shortening.
#
# Both terms read the same broad noise ON PURPOSE. Independent fields would give a quarter of
# the rim a cut-down top over an untouched base -- a tall thin blade, which is exactly the
# vertical fin the September 9 review rejected. Sharing it correlates them: where the top
# survives the base stays deep and the result is a thick headland, and where the top is eaten
# the base rises with it and the result is a low bench you can get off.
#
# It is expressed as a SECOND UNDERSIDE GRADIENT rather than an offset on the first, and that
# is not a stylistic choice. y_clamped_gradient saturates at +/-1 outside its span, so
# subtracting a constant larger than 1 from it makes the term negative at EVERY height and
# deletes the rim outright; measured on the first attempt, which drove the median face from 69
# to 123 blocks by pushing the min() the other way entirely. Interpolating between a deep
# underside and a shallow one moves the surface the term describes instead of the value.
#
# AND IT HAS TO REACH THE BELT'S OWN HEIGHT BAND, WHICH IS WHERE THE LAST WALL WAS HIDING.
# The debris envelope opens at Y 64, so a shelf whose underside stops at Y 41 presents about
# 26 blocks of face below anything the belt can put beside it -- the two sides overlap only
# between Y 64 and the shelf top, and everything under that is a wall by construction whatever
# the erosion does to the top. Lifting the outer underside to about Y 43 at the typical sample
# leaves roughly twenty blocks instead of sixty, and the shelf hands over to the belt inside a
# shared band rather than above one.
RIM_BASE_LIP=(48,72)
EDGE_LIFT=0.85
EDGE_LIFT_SWING=0.80
# --- and the body of the shelf, which until 2026-09-11 could not be shaped at all -------------
#
# THE FACES WERE KNIFE CUTS BECAUSE THE DENSITY SATURATES. rim_top and the underside are both
# y_clamped_gradients, so from roughly Y 25 to Y 65 each returns +1 and min() returns +1.0
# whatever any noise does. Erosion could only ever work the two transition bands at the top and
# the bottom; to remove anything between them it had to clear 1.0 in a single sample, which makes
# the answer for a whole column all-or-nothing. A field of all-or-nothing columns reads as a
# sliced cake however much its top and bottom wander, and that is measurable: on
# void-margin-20260911-172920, 5.3% of adjacent pairs at the break are a 30+ block wall against
# nothing, the mean column holds 1.21 solid runs, and 10.4% still reach bedrock.
#
# `body` is a third min() term that is NOT saturated -- a three-dimensional field centred near
# zero -- so it cuts alcoves, overhangs, arches and detached pieces through the shelf itself
# rather than only trimming its edges. That is also what gives the void margin ground worth
# attaching a feature or a structure to: a ledge is somewhere to stand, a slice is not.
#
# BODY_SHELTER is what keeps it off the plain. The carve can only reach where
#   BODY_LEVEL + BODY_SWING*n + BODY_SHELTER*(1 - reach) < 0,
# so at the breakline it bites about a third of samples and by two thirds of the way inland it
# cannot bite at all, whatever the noise does. The plain the player crosses is untouched by
# construction, not by tuning.
BODY_WIDTH=0.14
BODY_LEVEL=0.40
# THREE SCALES, BECAUSE ONE SCALE CANNOT MAKE A FACE. The carve was a single noise at roughly
# 29 blocks horizontally, and at block resolution the result is exactly what that predicts: the
# 2026-09-11 review saw faces carrying one or two blocks of jitter over a hundred and thirty
# blocks of height, and hanging pieces with flat bottoms. A single frequency can decide WHERE a
# mass ends; it cannot give the ending any texture.
#
# The debris field beyond the cliff has produced crenulated fragments all along, and it is a sum
# of three -- 0.55 fragments, 0.30 shape, 0.16 fracture. The shelf gets the same treatment, on
# its own noises: broad to choose the mass, mid to cut benches and alcoves into the face, grain
# to break the last few blocks so nothing reads as a cut sheet.
BODY_SWING=0.70          # ~29 blocks: which stretches come apart at all
BODY_MID=0.48            # ~9 blocks: benches, alcoves, the shape of a face
BODY_GRAIN=0.26          # ~4 blocks: the last detail, so no edge is a clean plane
BODY_SHELTER=1.20
# --- and detail on every surface, including the ones the carve is not allowed to reach -------
#
# THE 2026-09-11 REVIEW PUT IT EXACTLY: "lots of little knobbly caves and nodules and
# indentations on the right side but flat sheer cliff on the left." That asymmetry is the design
# showing through -- `reach` ramps the body carve to nothing inland so the approach stays
# walkable, so detail stops precisely where the carve stops, and every inland face is a clean
# plane.
#
# This term keys off the PLAIN'S OWN VALUE rather than off the mask, which is what lets it
# detail a surface without hollowing what is behind it. Density is near zero at every surface --
# top, underside and vertical face alike -- and large in the interior, so
#     SURFACE_LEVEL + SURFACE_SWING*grain + SURFACE_DEPTH*plain
# can bite at a face and cannot reach the rock behind it. SURFACE_DEPTH is how many units of
# density it may chew through, so it is the knob for how deep the pitting goes, and the interior
# is protected by arithmetic rather than by a ramp.
SURFACE_LEVEL=0.06
SURFACE_SWING=0.74
SURFACE_DEPTH=1.55
# Solidity threshold on the fragment field, interpolated by `outward`. Negative at the cliff
# welds the inner belt to the shelf; strongly positive at the fringe leaves isolated pieces
# that get rarer AND smaller together, because raising a threshold on smooth noise trims the
# blob's shoulders as it removes whole blobs.
# Three control points rather than one line: the belt has to fall away fast just outside the
# cliff and then keep a long thin tail, because check_void_surface_support.py reserves
# -0.94..-0.925 for terminal landings and a single linear ramp either floods the middle belt
# or leaves that strip with no host rock at all. Measured both ways before settling here.
# RAISED 2026-09-09 after measuring the belt as landforms rather than as a density. At
# -0.18/0.46 the field was solid enough to PERCOLATE: probe_void_fragments found 103,440 of
# 103,937 void columns in one connected mass welded to the Verge shelf, against 413 columns of
# detached debris in 23 specks, every one of them within 31 blocks of solid ground. That is a
# shelf with a ragged edge, not the "attached shelves give way to detached blocks, smaller
# fragments and finally empty space" of VOID_MARGINS.md section 1.
#
# Correlated noise connects far more readily than an uncorrelated fraction suggests, so the
# threshold has to sit well below half for pieces to separate at all. The Verge itself supplies
# the attached land the design asks for; the belt beyond the cliff is meant to come apart.
CUT_INNER=0.30
CUT_TERM=0.62
CUT_FAR=0.95
BASAL_LAVA_Y=-54
CATALOG=json.loads((ROOT/'alfheim_reclaimed_design/void/void_catalog.json').read_text())
VOID_IDS=[b['id'] for b in CATALOG['biomes']]
DEBRIS_IDS=[id for id in VOID_IDS if id != 'alfheim:void_verge']

def noise(name,y=0,xz=1.0):
    return {'type':'minecraft:noise','noise':'alfheim:void/'+name,'xz_scale':xz,'y_scale':y}

def clamp(value, low, high):
    return {'type':'minecraft:clamp','input':value,'min':low,'max':high}

def ramp(src, lo, hi):
    """0 at `lo`, 1 at `hi`, clamped. Continuous, so it never steps terrain."""
    return clamp({'type':'minecraft:mul','argument1':1.0/(hi-lo),
                  'argument2':binary('add',src,-lo)},0.0,1.0)


def debris_field():
    """The broken belt between the cliff and the empty far field.

    Restored 2026-09-09. It was removed with the note that "Minecraft's cell interpolation
    could carry an entire jagged splinter far beyond its pointwise mask". That premise was
    measured false on 2026-09-08 while calibrating the Golden Fields terraces: the
    `minecraft:interpolated` markers live inside `alfheim_height` and `alfheim_caves`, not on
    this branch, so an expression written at the `alfheim_final` level is evaluated per block
    at full resolution -- which is why a 4-block sawtooth survived there, and why
    size_vertical 1 vs 2 changed the on-tread share by 0.1 points. The mask and the shape are
    read at the same block, so a fragment cannot outrun its own mask.
    """
    # Two nested ramps: `belt` spans the debris band, `tail` the terminal fringe beyond it.
    # Every outward property derives from these, so "fragments get smaller and rarer outward"
    # cannot drift out of step with itself.
    belt=ramp(MASK,TERMINAL,BREAK)
    tail=ramp(MASK,FRINGE,TERMINAL)

    # Low frequency carries the mass, higher frequencies only break its edges. Flattened in Y
    # (y_scale below xz_scale) so the field parts into slabs and shelves rather than boulders.
    # A 'landing_swell' term was tried here on 2026-09-09 and removed the same day, because it
    # measured as a no-op and the thing it was meant to fix turned out not to be a density
    # problem. It was a very broad, flat noise meant to lift whole neighbourhoods over the cut
    # so the terminal band could carry the substantial landing check_void_surface_support wants.
    # At firstOctave -7 and xz_scale 0.16 its period is on the order of 800 blocks, so inside a
    # 384-block generated patch it is indistinguishable from a constant offset: island counts,
    # medians and maxima came back identical to two significant figures. And the reason Starless
    # Reach carries no landing is that it occupies 142 columns of the sampled area against the
    # Verge's 76,146 -- there is no area to land on, at any density. See VOID_MARGINS section 6.
    frag=binary('add',binary('add',
        binary('mul',0.55,noise('fragments',0.45,0.50)),
        binary('mul',0.30,noise('shape',0.70,0.95))),
        binary('mul',0.16,noise('fracture',1.20,1.70)))

    # Climate, not biome. The four debris biomes are claimed by temperature and humidity in
    # claims(); reading the same two fields here gives each one its own density without a
    # biome test moving terrain -- the failure B-82 had to revert.
    t_hi=ramp('mythicbotany:alfheim_temperature',0.0,0.20)
    h_hi=ramp('mythicbotany:alfheim_humidity',0.0,0.20)
    #   shatterfields  (cold, dry)   +0.00  angular slabs close to the rim
    #   prism_drift    (cold, humid) +0.18  an uncommon pocket with conspicuous gaps
    #   rootfall       (warm, dry)   -0.04  broken shelves that can carry root undersides
    #   sepulchral     (warm, humid) -0.08  the quiet stable shelves, most continuous
    bias=binary('add',binary('mul',0.18,h_hi),
         binary('add',binary('mul',-0.22,binary('mul',t_hi,h_hi)),
                      binary('mul',-0.04,t_hi)))
    # CUT_FAR at the limit, CUT_TERM where the belt ends, CUT_INNER at the cliff.
    cut=binary('add',binary('add',binary('add',CUT_FAR,
        binary('mul',CUT_TERM-CUT_FAR,tail)),
        binary('mul',CUT_INNER-CUT_TERM,belt)),bias)

    # A trapezoid in Y. Outside it the min() returns the envelope, which is negative, so no
    # fragment can reach the water table below or stack into a tower above. The upper edge
    # carries a broad, low-frequency offset so the belt has a skyline instead of a lid.
    ceiling=binary('add',gradient(DEBRIS_Y_FALL,1,-1),
                   binary('mul',CEILING_WANDER,noise('shape',0.0,0.25)))
    envelope=binary('min',gradient(DEBRIS_Y_RISE,-1,1),ceiling)
    field=binary('min',envelope,binary('add',frag,binary('mul',-1.0,cut)))
    # Hard zero past the limit: the far field is empty by construction, not by threshold.
    return choose(MASK,-100,FRINGE,-1.0,field)


def density(normal):
    """Sea -> coast -> Verge plain -> breakline -> debris -> nothing, on one field.

    The four stages are continuous by construction: each boundary is a `ramp` that has
    already reached its endpoint value where the next branch takes over, so no stage can
    step the terrain. The one deliberate discontinuity is the breakline itself.
    """
    # The Verge plain. A broad, dry, gently uneven table that never reaches the water table:
    # rim_top crosses zero at the midpoint of RIM_TOP with slope 2/span per block, so the
    # surface sits at 76 +/- (RIM_RELIEF + RIM_DETAIL) / slope. VG7 does that arithmetic.
    rim_relief=binary('add',binary('mul',RIM_RELIEF,noise('relief',0,xz=0.72)),
                      binary('mul',RIM_DETAIL,noise('detail',0.22,xz=0.62)))
    def lerp(t,a,b):
        return binary('add',binary('mul',binary('add',1.0,binary('mul',-1.0,t)),a),
                      binary('mul',t,b))
    inland=ramp(MASK,BREAK,DRY_AQUIFER_RIM)
    seaward=ramp(MASK,DRY_AQUIFER_RIM,COAST_TOE)
    top=lerp(seaward,lerp(inland,gradient(RIM_TOP_BREAK,1,-1),gradient(RIM_TOP_DRY,1,-1)),
             gradient(RIM_TOP_SEA,1,-1))
    rim_top=binary('add',top,rim_relief)
    # min() with a rising base turns the shelf from a full-depth curtain into a slab of land.
    # The wander keeps the underside from being a machined plane, which is the same mistake
    # the debris ceiling made and the same fix. `attach` reaches 1.0 UNDERCUT inside the
    # cliff, and rim_base + 2.0 is then positive at every Y, so the plain is rooted to bedrock
    # everywhere except the lip -- which is the only place a cliff face belongs.
    attach=ramp(MASK,BREAK,BREAK+UNDERCUT)
    # The lip comes apart. `edge` is 1.0 at the breakline and 0.0 EDGE_WIDTH inland, so every
    # term below is exactly zero across the plain the player crosses and across the shore
    # beyond it -- VG8 asserts that, and asserts that the eroded band stays inside the dry
    # aquifer shoulder, because a lip cut below sea level in wet ground would fill.
    edge=binary('add',1.0,binary('mul',-1.0,ramp(MASK,BREAK,BREAK+EDGE_WIDTH)))
    lift=binary('mul',edge,clamp(binary('add',EDGE_LIFT,
                binary('mul',EDGE_LIFT_SWING,noise('breakline',0.0,0.14))),0.0,1.0))
    rim_base=binary('add',binary('add',
                binary('mul',binary('add',1.0,binary('mul',-1.0,lift)),gradient(RIM_BASE,-1,1)),
                binary('mul',lift,gradient(RIM_BASE_LIP,-1,1))),
                binary('mul',RIM_BASE_WANDER,noise('rim_base',0.30,0.22)))
    plain=binary('min',rim_top,binary('add',rim_base,binary('mul',ATTACH_BIAS,attach)))

    appetite=binary('add',EDGE_BITE,binary('mul',EDGE_SWING,noise('breakline',0.0,0.18)))
    erosion=binary('max',0.0,binary('add',appetite,
                                    binary('mul',EDGE_SPALL,noise('spall',0.80,0.90))))
    plain=binary('add',plain,binary('mul',-1.0,binary('mul',edge,erosion)))

    # The body carve. `reach` is 1.0 at the breakline and 0.0 BODY_WIDTH inland; the shelter term
    # is 0 there and BODY_SHELTER on the plain, where it holds `body` permanently positive so the
    # min() cannot bite. Only this term can remove material from the middle of the shelf.
    reach=binary('add',1.0,binary('mul',-1.0,ramp(MASK,BREAK,BREAK+BODY_WIDTH)))
    grain=binary('add',binary('add',
        binary('mul',BODY_SWING,noise('body',0.85,0.55)),
        binary('mul',BODY_MID,noise('spall',1.05,0.95))),
        binary('mul',BODY_GRAIN,noise('grain',1.60,1.40)))
    body=binary('add',binary('add',BODY_LEVEL,grain),
                binary('mul',BODY_SHELTER,binary('add',1.0,binary('mul',-1.0,reach))))
    plain=binary('min',plain,body)

    # Surface detail, everywhere the approach exists. See SURFACE_DEPTH above: this cannot cut
    # deeper than SURFACE_DEPTH units of density, so it roughens faces and never hollows masses.
    detail=binary('add',binary('add',SURFACE_LEVEL,
                  binary('mul',SURFACE_SWING,noise('grain',1.25,1.15))),
                  binary('mul',SURFACE_DEPTH,plain))
    plain=binary('min',plain,detail)

    void=choose(MASK,-100,BREAK,debris_field(),plain)
    # NoiseBasedChunkGenerator consults its global fluid picker at the lowest ten
    # levels before routed floodedness can return air. Temporary default stone blocks
    # that picker; surface_rule() removes it in debris/terminal Void biomes.
    void=choose('minecraft:y',-64,BASAL_LAVA_Y,1.0,void)

    # THE COAST, WHICH IS WHAT THE OLD SHORELINE BLEND WAS TRYING AND FAILING TO BE.
    # That blend ran SHORE_START -0.81 to RIM -0.802 -- 0.008 of continentalness, which at
    # this field's gradient is about TWO BLOCKS. The measured result is a step, not a shore:
    # at z=223 the ground goes from seabed top Y28 to plain top Y71 across six columns while
    # the underside drops 64 blocks in one. The plain now simply continues past RIM as
    # ordinary ground and only turns into sea floor between DRY_AQUIFER_RIM and COAST_TOE,
    # carried by `elev` above. COAST_RIM is now purely a BIOME boundary -- where Alfheim Ocean
    # takes over from Void Shore -- and VG7 still requires it inland of the dry rim so that no
    # column the aquifer dries is ever claimed by an ocean.
    # The plain simply continues inland as one surface until its own elevation has taken it below
    # the sea floor, and only then does ordinary density take over. The outer branch still ends at
    # RIM, so check_worldgen W7 reads the same bound it always did.
    approach=choose(MASK,-100,COAST_TOE,plain,normal)
    return choose(MASK,-100,RIM,void,approach)

COAST_ID='alfheim:void_shore'

def claims(pt):
    """Outward from the sea. Three bands stand between the ocean and the break, which is what
    the edge was always meant to have: a shore where the water stops, a plain to cross, and
    then the ground giving way. Before 2026-09-11 the first of those was an ocean biome laid
    over a dry basin, so the sequence read water -> hole -> wall."""
    return [('alfheim:starless_reach',pt((-1,TERMINAL))),
            ('alfheim:shatterfields',pt((TERMINAL,CLIFF),temp=(-1,0),hum=(-1,0))),
            ('alfheim:prism_drift',pt((TERMINAL,CLIFF),temp=(-1,0),hum=(0,1))),
            ('alfheim:rootfall',pt((TERMINAL,CLIFF),temp=(0,1),hum=(-1,0))),
            ('alfheim:sepulchral_reach',pt((TERMINAL,CLIFF),temp=(0,1),hum=(0,1))),
            ('alfheim:void_verge',pt((CLIFF,BIOME_RIM))),
            # The void's own coastline: emerged, dry, and outward of the waterline, so the
            # Alfheim Ocean has something to end against. It is NOT in VOID_IDS -- it keeps
            # ordinary hydrology, ores and pools, because it is the last ordinary ground
            # rather than part of the margin's geology.
            (COAST_ID,pt((BIOME_RIM,COAST_RIM)))]

def surface_rule():
    # THE GUARD IS STRIPPED UNDER THE WHOLE MARGIN NOW, VOID VERGE INCLUDED. It exists only to
    # deny Minecraft's hardcoded lowest fluid band an air block to fill, and while the Verge was
    # solid to bedrock nobody could see it. The Verge is a shelf with open air beneath it now, so
    # leaving it solid there hangs a flat pale plate ten blocks thick across the floor of the
    # abyss -- one more hard horizontal slice, in the one place the player looks down into.
    # It cannot reach the shelf: the rule fires only at or below y BASAL_LAVA_Y.
    rules=[condition({'type':'minecraft:biome','biome_is':VOID_IDS},
                     condition(negate(above(BASAL_LAVA_Y)),block('minecraft:air')))]
    floor={'type':'minecraft:stone_depth','offset':3,'add_surface_depth':False,
           'secondary_depth_range':0,'surface_type':'floor'}
    def threshold(name,low,high=100):
        return {'type':'minecraft:noise_threshold','noise':'alfheim:void/'+name,
                'min_threshold':low,'max_threshold':high}
    grammar={b['id']:{r['feature']:r['material'] for r in b['terrain_grammar']}
             for b in CATALOG['biomes']}
    # These are feature grammars, not palettes. A material is selected because the
    # block belongs to a recognisable landform or structural role. Signature stones
    # that are absent here are emitted only by the matching configured feature below.
    palettes={
        'alfheim:void_verge':sequence([
            condition(floor,block(grammar['alfheim:void_verge']['verge_table'])),
            block(grammar['alfheim:void_verge']['breakline_scar'])]),
        'alfheim:shatterfields':sequence([
            condition(threshold('split_seams',-0.035,0.035),block(grammar['alfheim:shatterfields']['split_seam'])),
            condition(floor,block(grammar['alfheim:shatterfields']['pressure_slab'])),
            block(grammar['alfheim:shatterfields']['fault_needle'])]),
        'alfheim:prism_drift':sequence([
            condition(threshold('split_seams',-0.055,0.055),block(grammar['alfheim:prism_drift']['split_seam'])),
            condition(floor,block(grammar['alfheim:prism_drift']['crystal_crown'])),
            block(grammar['alfheim:prism_drift']['prism_core'])]),
        'alfheim:rootfall':sequence([
            condition(threshold('root_ribs',0.12),block(grammar['alfheim:rootfall']['root_apron'])),
            condition(threshold('root_ribs',-0.10,0.12),block(grammar['alfheim:rootfall']['resin_halo'])),
            block(grammar['alfheim:rootfall']['trunk_socket'])]),
        'alfheim:sepulchral_reach':sequence([
            condition(floor,block(grammar['alfheim:sepulchral_reach']['memorial_shelf'])),
            block(grammar['alfheim:sepulchral_reach']['competent_backing'])]),
        'alfheim:starless_reach':sequence([
            condition(threshold('astralite_flecks',0.72),block(grammar['alfheim:starless_reach']['astralite_fleck'])),
            condition(floor,block(grammar['alfheim:starless_reach']['hollow_splinter'])),
            block(grammar['alfheim:starless_reach']['terminal_landing'])]),
    }
    # THE SHORE'S SURFACE BELONGS HERE AND NOT IN identity_surface_rule(), AND THE REASON IS
    # THE AQUIFER REPAIR. Every palette in identity_surface_rule() is wrapped in
    # `above_preliminary_surface`, and inside the dry band initial_density_without_jaggedness
    # is pinned to 1.0, so preliminary surface resolves to the build limit and NO block is
    # ever above it. Measured on `saves/New World Ferngale`: the dried ocean band's top block
    # is bare Deepworks strata -- livingrock 41%, storm 26%, tide 20% -- because its palette
    # could not fire, while void_verge next door reads 87% Riftchalk from this un-gated rule.
    # Deep rock lying on the surface is a large part of why that band read as "the deeps with
    # nothing above them" at all.
    rules.append(condition({'type':'minecraft:biome','biome_is':[COAST_ID]},sequence([
        condition(floor,sequence([
            condition(threshold('shore_wrack',0.34),block('minecraft:gravel')),
            condition(threshold('shore_wrack',-0.30,0.34),block('alfheim:riftchalk_livingrock')),
            block('minecraft:sand')])),
        block('alfheim:riftchalk_livingrock')])))
    for biome,palette in palettes.items():
        rules.append(condition({'type':'minecraft:biome','biome_is':[biome]},palette))
    return sequence(rules)

def extra_files():
    out={}
    def emit(path,value):out['kubejs/data/'+path]=(json.dumps(value,indent=2)+'\n').encode()
    for name,octave,amps in [('relief',-5,[1,0.5]),('detail',-3,[1,0.5]),
                             ('fragments',-5,[1,0.6,0.3]),('fracture',-3,[1,0.45]),
                             ('shape',-4,[1,0.5]),('pressure_plates',-4,[1,0.5]),
                             ('fault_needles',-3,[1,0.45]),('prism_cores',-4,[1,0.55]),
                             ('split_seams',-3,[1,0.5]),('root_ribs',-3,[1,0.48]),
                             ('burial_beds',-5,[1,0.45]),('astralite_flecks',-2,[1,0.35]),
                             # Its own channel: the debris shaping noises are barred from the
                             # supported shore by VG3b, and rightly -- reusing one here would
                             # break up the shelf the player is promised.
                             ('rim_base',-6,[1,0.4]),
                             # The shore's own channel: wrack lines and bleached stone, at a
                             # coarser period than the Verge's seam noises so the strand reads
                             # as banded rather than speckled.
                             ('shore_wrack',-4,[1,0.5]),
                             # Broad enough that a headland is a headland for a few hundred
                             # blocks rather than a single column that happened to survive.
                             ('breakline',-6,[1,0.5,0.25]),
                             # And the local one, read in three dimensions so it cuts the face
                             # and not only the top.
                             ('spall',-3,[1,0.55,0.3]),
                             # Alcove-scale: about 30 blocks across and 19 tall at the scales it
                             # is read at, so it carves recesses and arches rather than pitting.
                             ('body',-4,[1,0.6,0.3]),
                             # Block-scale, so the last few blocks of any edge are ragged.
                             ('grain',-2,[1,0.5])]:
        emit('alfheim/worldgen/noise/void/'+name+'.json',{'firstOctave':octave,'amplitudes':amps})
    emit('alfheim/tags/worldgen/biome/void_margins.json',{'replace':False,'values':VOID_IDS})
    # REMOVE phase runs after all ADD modifiers. Conventional liquid pools must
    # not refill the dry margin. Keep the authored Rim geode/marker until their
    # volume-checked replacement exists; removing them here silently deletes the
    # existing exploration route before that replacement is implemented.
    emit('alfheim/forge/biome_modifier/void_no_pools_geodes.json',{'type':'forge:remove_features','biomes':'#alfheim:void_margins','features':['alfheim:liquid_bifrost_pool'],'steps':['lakes','local_modifications','top_layer_modification']})

    # Small material formations make each margin legible before its full landmark
    # pair is found.  They use the pre-existing surface mass and never manufacture
    # support beneath themselves.
    air={'type':'minecraft:matching_blocks','blocks':'minecraft:air'}
    natural={'type':'minecraft:matching_block_tag','tag':'alfheim:void_natural'}
    def provider(entries):
        if len(entries)==1:return {'type':'minecraft:simple_state_provider','state':{'Name':entries[0][0]}}
        return {'type':'minecraft:weighted_state_provider','entries':[
            {'data':{'Name':state},'weight':weight} for state,weight in entries]}
    def column(direction,layers,allowed):
        return {'type':'minecraft:block_column','config':{'direction':direction,
            'allowed_placement':allowed,'prioritize_tip':True,'layers':[
                {'height':height,'provider':provider(states)} for height,states in layers]}}
    uniform=lambda lo,hi:{'type':'minecraft:uniform','value':{'min_inclusive':lo,'max_inclusive':hi}}

    # Upright markers/steles are columns; the Rootfall formation is a patch of long
    # downward columns inside existing support; crystal crowns remain low hosted piles;
    # Astralite is a tiny replacement fleck. Distinct reads now use distinct codecs.
    formations={
        'verge_markers':('alfheim:void_verge',14,column('up',[(uniform(2,4),[('alfheim:veilstone_livingrock',1)]),(1,[('minecraft:amethyst_block',1)])],air),[]),
        'shatter_anchors':('alfheim:shatterfields',12,column('up',[(uniform(4,9),[('alfheim:anchorstone_livingrock',4),('alfheim:seamstone_livingrock',1)])],air),[]),
        'prism_crowns':('alfheim:prism_drift',8,{'type':'minecraft:block_pile','config':{'state_provider':provider([('alfheim:prismstone_livingrock',4),('minecraft:amethyst_block',2),('minecraft:budding_amethyst',1)])}},[]),
        'root_aprons':('alfheim:rootfall',11,{'type':'minecraft:random_patch','config':{
            'tries':14,'xz_spread':6,'y_spread':0,'feature':{'feature':column('down',[
                (uniform(7,18),[('alfheim:rootfossil_livingrock',5),('alfheim:resinshale_livingrock',1)])],natural),
                'placement':[{'type':'minecraft:random_offset','xz_spread':0,'y_spread':-1},
                             {'type':'minecraft:block_predicate_filter','predicate':natural}]}}},[]),
        'mourning_steles':('alfheim:sepulchral_reach',13,column('up',[(uniform(2,5),[('alfheim:epitaph_livingrock',5)]),(1,[('alfheim:oathstone_livingrock',1)])],air),[]),
        'astralite_flecks':('alfheim:starless_reach',18,{'type':'minecraft:ore','config':{
            'size':3,'discard_chance_on_air_exposure':0.0,'targets':[
                {'target':{'predicate_type':'minecraft:block_match','block':state},
                 'state':{'Name':'alfheim:astralite_livingrock'}}
                for state in ('alfheim:nightmantle_livingrock','alfheim:nullstone_livingrock')]}},
            [{'type':'minecraft:random_offset','xz_spread':0,'y_spread':-2}]),
    }
    for name,(biome,chance,configured,extra_placement) in formations.items():
        emit('alfheim/worldgen/configured_feature/void/'+name+'.json',configured)
        emit('alfheim/worldgen/placed_feature/void/'+name+'.json',{'feature':'alfheim:void/'+name,'placement':[
            {'type':'minecraft:rarity_filter','chance':chance},{'type':'minecraft:in_square'},
            {'type':'minecraft:heightmap','heightmap':'MOTION_BLOCKING_NO_LEAVES'},
            *extra_placement,{'type':'minecraft:biome'}]})
        emit('alfheim/forge/biome_modifier/void_'+name+'.json',{'type':'forge:add_features',
            'biomes':[biome],'features':'alfheim:void/'+name,'step':'local_modifications'})
    return out
