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
# The breakline. Outward of it the ground has already come apart.
CLIFF=-0.86
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
RIM_BASE_WANDER=0.5
# AND THE UNDERCUT IS LOCAL TO THE LIP NOW, BECAUSE THE 2026-09-09 REPAIR CUT BOTH FACES.
# rim_base was applied across the whole Verge band, including the side facing the sea, so the
# shelf stood free on both faces: at z=223 in `New World Ferngale` the seabed at x=-113 is
# solid -53..28 and the Verge one column outward at x=-112 is solid 11..34, a 64-block void
# opening directly under the ground the player is meant to walk in on. `attach` fades the
# undercut in over the last UNDERCUT of the band, so the plain is rooted to bedrock where it
# is walked and only the cliff face is cut away.
UNDERCUT=0.06
# How hard `attach` pushes the underside down outside the lip. It has to clear the underside
# gradient's own floor (-1.0) plus its wander, or "rooted" is only rooted on average.
ATTACH_BIAS=2.0
# The plain's surface. A band five times wider than the old ribbon can carry real relief --
# but never enough to reach the water table, and VG7 asserts that from these three numbers
# rather than capping each amplitude separately and hoping the sum behaves.
RIM_TOP=(64,88)
RIM_RELIEF=0.30
RIM_DETAIL=0.10
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
    belt=ramp(MASK,TERMINAL,CLIFF)
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
                      binary('mul',RIM_DETAIL,noise('detail',0,xz=0.62)))
    rim_top=binary('add',gradient(RIM_TOP,1,-1),rim_relief)
    # min() with a rising base turns the shelf from a full-depth curtain into a slab of land.
    # The wander keeps the underside from being a machined plane, which is the same mistake
    # the debris ceiling made and the same fix. `attach` reaches 1.0 UNDERCUT inside the
    # cliff, and rim_base + 2.0 is then positive at every Y, so the plain is rooted to bedrock
    # everywhere except the lip -- which is the only place a cliff face belongs.
    attach=ramp(MASK,CLIFF,CLIFF+UNDERCUT)
    rim_base=binary('add',gradient(RIM_BASE,-1,1),
                    binary('mul',RIM_BASE_WANDER,noise('rim_base',0.0,0.22)))
    plain=binary('min',rim_top,binary('add',rim_base,binary('mul',ATTACH_BIAS,attach)))

    void=choose(MASK,-100,CLIFF,debris_field(),plain)
    # NoiseBasedChunkGenerator consults its global fluid picker at the lowest ten
    # levels before routed floodedness can return air. Temporary default stone blocks
    # that picker; surface_rule() removes it in debris/terminal Void biomes.
    void=choose('minecraft:y',-64,BASAL_LAVA_Y,1.0,void)

    # THE COAST, WHICH IS WHAT THE OLD SHORELINE BLEND WAS TRYING AND FAILING TO BE.
    # That blend ran SHORE_START -0.81 to RIM -0.802 -- 0.008 of continentalness, which at
    # this field's gradient is about TWO BLOCKS. The measured result is a step, not a shore:
    # at z=223 the ground goes from seabed top Y28 to plain top Y71 across six columns while
    # the underside drops 64 blocks in one. The plain now simply continues past RIM as
    # ordinary ground and only turns into sea floor between COAST_RIM and COAST_TOE, ~0.09
    # wide. `coast` is 0.0 outward of COAST_RIM, which is what keeps every dried column on
    # the plain, and 1.0 inland of COAST_TOE, where this returns `normal` unchanged.
    coast=ramp(MASK,COAST_RIM,COAST_TOE)
    approach=binary('add',binary('mul',coast,normal),
                    binary('mul',binary('add',1.0,binary('mul',-1.0,coast)),plain))
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
    rules=[condition({'type':'minecraft:biome','biome_is':DEBRIS_IDS},
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
                             ('shore_wrack',-4,[1,0.5])]:
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
