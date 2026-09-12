#!/usr/bin/env python3
"""Guard the Void Margin feature-bound geology against palette regression.

The rejected state used one generic strata noise to paint all three stones through
every mass and represented every named formation as a block pile. This check keeps
the material catalogue, quiet shore-only density, surface roles and placed feature
codecs in agreement. It is static; visual acceptance still requires fresh client chunks.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

EXPECTED_CODECS={
    'verge_markers':'minecraft:block_column',
    'shatter_anchors':'minecraft:block_column',
    'prism_crowns':'minecraft:block_pile',
    'root_aprons':'minecraft:random_patch',
    'mourning_steles':'minecraft:block_column',
    'astralite_flecks':'minecraft:ore',
}
FEATURE_ONLY={
    'alfheim:void_verge':{'alfheim:veilstone_livingrock'},
    'alfheim:sepulchral_reach':{'alfheim:epitaph_livingrock'},
}
# Surface-rule and configured-feature vocabulary. These describe what a face is MADE of and
# where a formation stands; none of them may move terrain, so none may reach final density.
FORBIDDEN_DENSITY_NOISES={
    'alfheim:void/pressure_plates','alfheim:void/fault_needles',
    'alfheim:void/prism_cores','alfheim:void/split_seams',
    'alfheim:void/root_ribs','alfheim:void/burial_beds',
}
# The debris field restored 2026-09-09. VG3 used to forbid these outright, which was a proxy
# for the two things actually at stake -- a fragment escaping its mask, and a far field that
# is only empty by tuning. Both are now asserted directly below, which is strictly stronger:
# the old rule would have passed an unbounded debris field written from any other noise.
DEBRIS_DENSITY_NOISES={
    'alfheim:void/fragments','alfheim:void/fracture','alfheim:void/shape',
}

def strings(value):
    if isinstance(value,str):yield value
    elif isinstance(value,dict):
        for item in value.values():yield from strings(item)
    elif isinstance(value,list):
        for item in value:yield from strings(item)

def walk(value):
    if isinstance(value,dict):
        yield value
        for item in value.values():yield from walk(item)
    elif isinstance(value,list):
        for item in value:yield from walk(item)

def block_names(value):
    return {s for s in strings(value) if s.startswith('alfheim:') and s.endswith('_livingrock')}

def validate(catalog,out,density):
    problems=[]
    def fail(code,text):problems.append(f'{code}  {text}')
    if catalog.get('schema_version') != 3:fail('VG1','void catalog must use feature-grammar schema 3')
    for biome in catalog.get('biomes',[]):
        grammar=biome.get('terrain_grammar',[])
        stones={s['id'] for s in biome.get('stones',[])}
        features=[r.get('feature') for r in grammar]
        materials=[r.get('material') for r in grammar]
        if len(grammar)!=3 or len(set(features))!=3:fail('VG1',f"{biome.get('id')} needs three distinct terrain features")
        if set(materials)!=stones:fail('VG1',f"{biome.get('id')} grammar materials do not exactly cover its stones")

    from gen_void_worldgen import surface_rule
    surface=surface_rule()
    surface_text=json.dumps(surface)
    if 'alfheim:void/strata' in surface_text:fail('VG2','generic Void strata wash returned')
    if 'alfheim:void/root_ribs' not in surface_text:fail('VG2','Rootfall material rule is not tied to root_ribs')
    for biome,materials in FEATURE_ONLY.items():
        # The whole surface rule is safe here: all 18 families are biome-unique.
        leaked=materials & block_names(surface)
        if leaked:fail('VG2',f'{biome} feature-only material leaked into the broad surface rule: {sorted(leaked)}')

    density_strings=set(strings(density))
    leaked=FORBIDDEN_DENSITY_NOISES & density_strings
    if leaked:fail('VG3',f'surface/feature vocabulary reached final density: {sorted(leaked)}')

    # VG3a -- the far field is empty BY CONSTRUCTION. Somewhere in the void branch there must
    # be a range_choice on continentalness whose in-range value is a literal -1.0 and whose
    # bound is at or below the declared FRINGE. A threshold that merely happens to exclude
    # everything is not the same guarantee and does not satisfy this.
    from gen_void_worldgen import FRINGE,BREAK,DEBRIS_Y_RISE
    hard_zero=[n for n in walk(density)
               if n.get('type')=='minecraft:range_choice'
               and n.get('input')=='mythicbotany:alfheim_continentalness'
               and n.get('when_in_range')==-1.0
               and isinstance(n.get('max_exclusive'),(int,float))
               and n['max_exclusive']<=FRINGE]
    if not hard_zero:
        fail('VG3a',f'no literal -1.0 far-field cutoff at or below continentalness {FRINGE}; '
                    'the empty far field would depend on tuning rather than structure')

    # VG3b -- debris shaping noise may appear ONLY inside the branch beyond the cliff. If it
    # leaks into the shore expression it would break up the supported Verge shelf, which is
    # the one piece of ground the player is promised.
    # Structural, not set-difference: the same noise id legitimately appears inside the branch,
    # so membership has to be decided per occurrence rather than per name.
    def noises_outside(node,sheltered):
        if isinstance(node,dict):
            if (node.get('type')=='minecraft:range_choice'
                    and node.get('input')=='mythicbotany:alfheim_continentalness'
                    and node.get('max_exclusive')==BREAK):
                yield from noises_outside(node.get('when_out_of_range'),sheltered)
                yield from noises_outside(node.get('when_in_range'),True)
                return
            if node.get('type')=='minecraft:noise' and not sheltered:
                yield node.get('noise')
            for key,value in node.items():
                if key!='type': yield from noises_outside(value,sheltered)
        elif isinstance(node,list):
            for item in node: yield from noises_outside(item,sheltered)
    cliff_branches=[n for n in walk(density)
                    if n.get('type')=='minecraft:range_choice'
                    and n.get('input')=='mythicbotany:alfheim_continentalness'
                    and n.get('max_exclusive')==BREAK]
    if not cliff_branches:
        fail('VG3b',f'no continentalness branch at the terrain break ({BREAK}); debris containment '
                    'cannot be established')
    else:
        escaped=DEBRIS_DENSITY_NOISES & set(noises_outside(density,False))
        if escaped:
            fail('VG3b',f'debris shaping noise reaches the supported shore: {sorted(escaped)}')

    # VG3c -- the debris field is bounded in Y by a gradient envelope that starts above sea
    # level, so no fragment can hang into the water table below or stack into a tower above.
    # The floor must be a bare gradient -- nothing may lift debris toward the water table. The
    # ceiling may carry an offset, because a fixed one planes the whole belt to a single height
    # (measured 2026-09-09: 74% of shatterfields tops at exactly Y 92), but that offset has to
    # be bounded or the envelope stops bounding anything.
    from gen_void_worldgen import CEILING_WANDER
    envelopes=[]
    for node in walk(density):
        if node.get('type')!='minecraft:min': continue
        inner=node.get('argument1')
        if not (isinstance(inner,dict) and inner.get('type')=='minecraft:min'): continue
        rise,ceiling=inner.get('argument1'),inner.get('argument2')
        if not (isinstance(rise,dict) and rise.get('type')=='minecraft:y_clamped_gradient'): continue
        if not any(isinstance(g,dict) and g.get('type')=='minecraft:y_clamped_gradient'
                   for g in walk(ceiling)): continue
        envelopes.append(ceiling)
    if DEBRIS_DENSITY_NOISES & density_strings:
        if not envelopes:
            fail('VG3c','the debris field is not bounded by a rising y_clamped_gradient floor '
                        'and a falling ceiling; fragments could reach the water table or stack '
                        'without limit')
        elif DEBRIS_Y_RISE[0]<64:
            fail('VG3c',f'debris envelope opens at y{DEBRIS_Y_RISE[0]}, at or below sea level 64; '
                        'detached debris must stay dry')
        else:
            for ceiling in envelopes:
                for node in walk(ceiling):
                    if node.get('type')!='minecraft:mul': continue
                    for scalar,term in ((node.get('argument1'),node.get('argument2')),
                                        (node.get('argument2'),node.get('argument1'))):
                        if (isinstance(scalar,(int,float)) and isinstance(term,dict)
                                and term.get('type')=='minecraft:noise'
                                and abs(float(scalar))>CEILING_WANDER):
                            fail('VG3c',f"ceiling offset on {term.get('noise')} is "
                                        f"{abs(float(scalar))}, above the declared "
                                        f"CEILING_WANDER {CEILING_WANDER}; an unbounded "
                                        f"offset defeats the envelope")
    # VG6 -- THE VERGE PLAIN NEVER REACHES THE WATER TABLE.
    #
    # This used to cap each shaping noise separately: relief <= 0.18, detail <= 0.05. Those
    # numbers were a PROXY for the thing that actually matters, and the two came apart on
    # 2026-09-11 as soon as the plain got wide enough to deserve more relief. A cap on each
    # amplitude says nothing about where the surface lands -- it depends on the gradient the
    # amplitudes are added to, which the old rule never read. The invariant is what the
    # original comment said out loud: "a quiet, continuous shelf whose lowest noise
    # displacement remains above sea level", after the 0.62 combined amplitude put the
    # surface into the global water table and exposed flowing water at the breakline.
    #
    # rim_top interpolates three same-span gradients and adds the relief, so within any one of
    # them it crosses zero at  y = lo + (hi - lo) * (1 + r) / 2. RIM_TOP_DRY is the one that
    # governs: it is exactly the surface at DRY_AQUIFER_RIM, and outward of that the
    # interpolation only ever rises toward RIM_TOP_BREAK, so bounding it bounds the whole dried
    # band. RIM_TOP_SEA is allowed below sea level -- inward of the dry rim it IS sea floor.
    from gen_void_worldgen import (RIM_TOP_BREAK, RIM_TOP_DRY, RIM_TOP_SEA, RIM_RELIEF,
                                   RIM_DETAIL, RIM_BASE, RIM_BASE_WANDER, UNDERCUT, COAST_RIM,
                                   DRY_AQUIFER_RIM, ATTACH_BIAS, BREAK, RIM, EDGE_WIDTH,
                                   EDGE_BITE, EDGE_SWING, EDGE_SPALL, EDGE_LIFT,
                                   EDGE_LIFT_SWING, RIM_BASE_LIP, BODY_WIDTH, BODY_LEVEL,
                                   BODY_SWING, BODY_SHELTER, BODY_MID, BODY_GRAIN,
                                   SURFACE_LEVEL, SURFACE_SWING, SURFACE_DEPTH)
    SEA_LEVEL=64
    swing=RIM_RELIEF+RIM_DETAIL
    if swing>=1.0:
        fail('VG6',f'plain relief {swing} saturates the surface gradients; the surface would no '
                   'longer track them at all')
    spans={'RIM_TOP_BREAK':RIM_TOP_BREAK,'RIM_TOP_DRY':RIM_TOP_DRY,'RIM_TOP_SEA':RIM_TOP_SEA}
    widths={name:hi-lo for name,(lo,hi) in spans.items()}
    if len(set(widths.values()))!=1:
        fail('VG6',f'the surface gradients have different spans {widths}: the same relief would '
                   'displace the surface by different distances along the approach')
    lo,hi=RIM_TOP_DRY
    lowest=lo+(hi-lo)*(1.0-swing)/2.0
    if lowest<=SEA_LEVEL:
        fail('VG6',f'at the dry-aquifer rim the approach can fall to y{lowest:.1f}, at or below '
                   f'sea level {SEA_LEVEL}: relief totalling {swing} over gradient y{lo}..y{hi}. '
                   'Every column the aquifer dries has to be land.')
    if not RIM_TOP_SEA[1]<RIM_TOP_BREAK[0]:
        fail('VG6',f'the surface at the sea end y{RIM_TOP_SEA} is not below the surface at the '
                   f'breakline y{RIM_TOP_BREAK}; the approach would not descend to the coast')
    # And the three must actually be in the shipped bytes, since this is the one assertion
    # standing between the approach and a water table inside it.
    shipped={(n.get('from_y'),n.get('to_y')) for n in walk(density)
             if n.get('type')=='minecraft:y_clamped_gradient'
             and n.get('from_value')==1 and n.get('to_value')==-1}
    for name,span in spans.items():
        if span not in shipped:
            fail('VG6',f'{name} {span} is not present in the shipped density; the surface the '
                       'generator describes is not the surface the game will build')
    # The sea-level arithmetic above is done on the declared amplitudes, so the shipped ones
    # have to match them or the arithmetic describes a different surface than the game builds.
    shipped_amp={}
    for node in walk(density):
        if node.get('type')!='minecraft:mul': continue
        for scalar,term in ((node.get('argument1'),node.get('argument2')),
                            (node.get('argument2'),node.get('argument1'))):
            if (isinstance(scalar,(int,float)) and isinstance(term,dict)
                    and term.get('type')=='minecraft:noise'
                    and term.get('noise') in ('alfheim:void/relief','alfheim:void/detail')):
                shipped_amp.setdefault(term.get('noise'),set()).add(abs(float(scalar)))
    for noise_id,declared in (('alfheim:void/relief',RIM_RELIEF),('alfheim:void/detail',RIM_DETAIL)):
        got=shipped_amp.get(noise_id,set())
        if got!={declared}:
            fail('VG6',f'{noise_id} ships at {sorted(got) or "nothing"} against a declared '
                       f'{declared}; the surface bound above is computed from the declared value '
                       'and would not describe the shipped one')

    # Only the quiet noises may shape it. Which noises, not how loud.
    plain_noises={'alfheim:void/relief','alfheim:void/detail','alfheim:void/rim_base',
                  'alfheim:void/breakline','alfheim:void/spall','alfheim:void/body',
                  'alfheim:void/grain'}
    multipliers={}
    for node in walk(density):
        if node.get('type')!='minecraft:mul':continue
        for scalar,term in ((node.get('argument1'),node.get('argument2')),
                            (node.get('argument2'),node.get('argument1'))):
            if isinstance(scalar,(int,float)) and isinstance(term,dict) and term.get('type')=='minecraft:noise':
                multipliers.setdefault(term.get('noise'),[]).append(abs(float(scalar)))
    for noise_id in multipliers:
        if noise_id in plain_noises or noise_id in DEBRIS_DENSITY_NOISES: continue
        fail('VG6',f'{noise_id} shapes gross terrain but is neither a declared plain noise '
                   f'nor a debris noise')

    # VG7 -- EVERY COLUMN THE AQUIFER DRIES STANDS ON THAT PLAIN, ABOVE SEA LEVEL.
    #
    # Nothing asserted this before, and the cost was 123,145 of 348,224 ocean columns in
    # `saves/New World Ferngale` generating with a seabed at Y 30 and open air to the build
    # limit -- an ocean biome over a dry basin, because the dry-aquifer shoulder reached
    # 0.22 of continentalness inland of the rim while the terrain under it stayed sea floor.
    # DRY_AQUIFER_RIM cannot simply be pulled back: Aquifer.NoiseBasedAquifer samples
    # preliminary surface up to three chunks away, so a narrow shoulder floods the void.
    # The repair is that the shoulder is LAND, and this is the check that keeps it so.
    if not COAST_RIM>DRY_AQUIFER_RIM:
        fail('VG7',f'the coast begins at {COAST_RIM}, at or outward of the dry-aquifer rim '
                   f'{DRY_AQUIFER_RIM}: columns between them would be dried while still '
                   'blending down to ordinary sea floor, which is the dry-basin defect')

    # And the plain is rooted everywhere it is walked. `attach` reaches 1.0 UNDERCUT inside
    # the cliff, so outside the lip the underside term is rim_base + ATTACH_BIAS; that is
    # positive at every Y only if the bias clears the gradient's floor plus its wander.
    if UNDERCUT<=0:
        fail('VG7','UNDERCUT is not positive; the undercut would apply across the whole '
                   'approach and the plain would stand free on its inland face too')
    if ATTACH_BIAS<=1.0+RIM_BASE_WANDER:
        fail('VG7',f'attach bias {ATTACH_BIAS} does not clear the underside floor '
                   f'{-(1.0+RIM_BASE_WANDER)}; the plain would still be hollow inland of '
                   f'the lip, which is the 64-block void measured under x=-112 at z=223')
    if RIM_BASE[0]<=-64:
        fail('VG7',f'the underside gradient opens at y{RIM_BASE[0]}, at or below the world '
                   'floor; the lip would have no cliff face at all')

    # VG8 -- THE LIP MAY COME APART, THE APPROACH MAY NOT.
    #
    # The breakline erosion is the one term in this function allowed to remove the plain, and
    # it is the term that stops the edge being a contour line with the same profile at every
    # point along it. Three things have to stay true of it, and none of them is a matter of
    # taste.
    edge_end=BREAK+EDGE_WIDTH
    if not edge_end<RIM:
        fail('VG8',f'erosion reaches {edge_end:.3f}, at or inland of the void terrain band '
                   f'{RIM}: it would eat the Verge plain and the Void Shore beyond it, which '
                   'are the ground the player is promised')
    if not edge_end<DRY_AQUIFER_RIM:
        fail('VG8',f'erosion reaches {edge_end:.3f}, at or inland of the dry-aquifer rim '
                   f'{DRY_AQUIFER_RIM}: a lip cut below sea level in wet ground fills, and '
                   'water at the breakline is the defect DEFICIENT_BIOMES.md rejected')
    # It must be clamped, or a negative noise sample would ADD material at the breakline and
    # the term would be a displacement rather than an erosion.
    clamped=[n for n in walk(density)
             if n.get('type')=='minecraft:max'
             and 0.0 in (n.get('argument1'),n.get('argument2'))]
    if not clamped:
        fail('VG8','breakline erosion is not clamped at zero; a negative sample would build '
                   'the lip back up instead of removing it')
    # And it has to be able to cut deeper in some places than others, or the rim comes down
    # to one new height and the result is a lower curtain rather than a broken one. The swing
    # is what buys headlands and bays; without it EDGE_BITE alone is a uniform trim.
    if EDGE_SWING<=EDGE_BITE:
        fail('VG8',f'erosion swing {EDGE_SWING} does not exceed its baseline bite '
                   f'{EDGE_BITE}; every stretch of rim would be cut by nearly the same '
                   'amount and the breakline would stay a contour')
    if EDGE_WIDTH>UNDERCUT:
        fail('VG8',f'erosion reaches {EDGE_WIDTH} inland while the undercut reaches only '
                   f'{UNDERCUT}: between them the break removes columns from a shelf still '
                   'rooted to bedrock, and what survives is a full-depth fin rather than a '
                   'butte -- measured at z=-704 x=-1711, solid -53..76 with nothing either side')
    if BREAK+UNDERCUT>RIM:
        fail('VG8',f'the undercut reaches {BREAK+UNDERCUT:.3f}, past the void terrain band '
                   f'{RIM}: the Void Shore would be hollow under the player as well')
    if EDGE_SPALL<=0:
        fail('VG8','no three-dimensional spall term; the erosion would only lower the top '
                   'and the face itself would stay a smooth vertical sheet')
    # And the slab has to thin, not just shorten. Lowering a 63-block section by ten blocks
    # leaves a 53-block wall; measured, erosion alone moved the median face from 69 to 62.
    # The lip underside has to sit above the plain's, or the term is decorative.
    if RIM_BASE_LIP[0]<=RIM_BASE[1]:
        fail('VG8',f'the lip underside y{RIM_BASE_LIP} does not clear the plain underside '
                   f'y{RIM_BASE}; the shelf would present its full section at the break')
    if RIM_BASE_LIP[1]>=RIM_TOP_BREAK[0]:
        fail('VG8',f'the lip underside rises to y{RIM_BASE_LIP[1]}, into the plain surface '
                   f'band y{RIM_TOP_BREAK}; the rim would thin to nothing and detach entirely')
    if EDGE_LIFT+EDGE_LIFT_SWING<=0 or EDGE_LIFT_SWING<=0:
        fail('VG8','the underside lift cannot vary along the rim; every stretch would thin '
                   'by the same amount and the break would be a lower curtain, not a broken '
                   'one')

    # VG9 -- THE BODY OF THE SHELF CAN BE SHAPED, AND ONLY AT THE BREAK.
    #
    # Without a third min() term the density saturates at +1 through the middle of the slab and
    # every column is all-or-nothing, which is a sliced cake however the top and bottom wander.
    # Measured on void-margin-20260911-172920 before this existed: 5.3% of adjacent pairs at the
    # break were a 30+ block wall against nothing and the mean column held 1.21 solid runs.
    # A face needs more than one frequency. One scale decides where a mass ends and gives the
    # ending no texture at all -- measured at block resolution on 2026-09-11 as one or two blocks
    # of jitter over a hundred and thirty blocks of face.
    if not (BODY_MID>0 and BODY_GRAIN>0):
        fail('VG9',f'the body carve runs at one scale (mid {BODY_MID}, grain {BODY_GRAIN}); its '
                   'faces would be clean planes and its hanging pieces flat-bottomed')
    if not BODY_SWING>BODY_MID>BODY_GRAIN:
        fail('VG9',f'the carve scales are not ordered broad > mid > grain '
                   f'({BODY_SWING}, {BODY_MID}, {BODY_GRAIN}); the fine detail would decide '
                   'where masses end instead of how their edges look')
    if BODY_SWING+BODY_MID+BODY_GRAIN<=BODY_LEVEL:
        fail('VG9',f'body swing {BODY_SWING}+{BODY_MID}+{BODY_GRAIN} never overcomes level '
                   f'{BODY_LEVEL}: the carve can '
                   'never go negative, so it removes nothing and the shelf stays saturated')
    if BODY_WIDTH<=0 or BREAK+BODY_WIDTH>RIM:
        fail('VG9',f'the body carve reaches {BREAK+BODY_WIDTH:.3f} against a terrain band ending '
                   f'at {RIM}: it would hollow the Void Shore, which is the ground the ocean '
                   'ends against')
    # And it has to be shut off before the plain. Solve for where it can still bite:
    #   BODY_LEVEL + BODY_SWING*n + BODY_SHELTER*(1 - reach) < 0  at the worst sample n = -1.
    if BODY_SHELTER<=0:
        fail('VG9','no body shelter term; the carve would reach the whole approach at full '
                   'strength and there would be no plain left to walk in on')
    bite_reach=1.0-(BODY_SWING-BODY_LEVEL)/BODY_SHELTER
    if bite_reach<=0.0:
        fail('VG9',f'body shelter {BODY_SHELTER} is too weak to stop the carve anywhere inside '
                   f'the band; it would cut the plain as well as the lip')
    from gen_void_worldgen import CLIFF as _CLIFF, TERMINAL as _TERMINAL
    # AND IT MAY ONLY TAKE A SLIVER OF THE DEBRIS BAND. The shelf is solid ground; the debris
    # biomes are meant to be mostly empty. At BREAK -0.89 it covered over half of their band and
    # prism_drift came back 92.4% solid against 11.3% before -- a shelf in the middle of the void.
    taken=(_CLIFF-BREAK)/(_CLIFF-_TERMINAL)
    if taken>0.20:
        fail('VG9',f'the carved shelf takes {100*taken:.0f}% of the debris band; the void biomes '
                   'are supposed to be void, and past about a fifth they read as a shelf with a '
                   'ragged edge instead')
    if not _TERMINAL<BREAK<_CLIFF:
        fail('VG9',f'the terrain handover {BREAK} is not between the terminal band {_TERMINAL} '
                   f'and the biome contour {_CLIFF}: outward of the contour it leaves the shelf '
                   'ending at a wall again, inward of it there is no floating belt left')

    # VG10 -- THE COAST IS A SLOPE, AND IT ACTUALLY REACHES THE SEA FLOOR.
    #
    # It used to be `coast*normal + (1-coast)*plain`, an interpolation of two DENSITIES. Between
    # the two surfaces both saturate, so the mix is 1 - 2*coast with no Y dependence at all and
    # the surface jumps rather than travels -- the sheer Void Shore wall of 2026-09-11. The
    # replacement carries the height on the mask instead, so what has to be checked is that the
    # taper spans far enough in both directions.
    SEA=64
    if not RIM_TOP_BREAK[0]>RIM_TOP_DRY[0]:
        fail('VG10',f'the approach does not rise toward the break ({RIM_TOP_BREAK} against '
                    f'{RIM_TOP_DRY}); it would be one flat table from the sea to the cliff, '
                    'which is the plateau the field review rejected')
    sea_crossing=(RIM_TOP_SEA[0]+RIM_TOP_SEA[1])/2.0
    if sea_crossing>=SEA:
        fail('VG10',f'the coast bottoms out at y{sea_crossing:.1f}, at or above sea level {SEA}: '
                    'ordinary density takes over while the approach is still standing above the '
                    'water, which puts the step straight back')

    # VG11 -- SURFACE DETAIL MAY ROUGHEN A FACE AND MAY NOT HOLLOW A MASS.
    #
    # It is the one carve with no mask ramp holding it off the walkable approach, so what keeps
    # it honest is arithmetic: it is min()ed against SURFACE_DEPTH * plain, and plain is large in
    # any interior. If the depth term cannot outrun the swing, the carve reaches the rock behind
    # the face and the plain becomes hollow -- which is the thing `reach` exists to prevent.
    if SURFACE_DEPTH<=SURFACE_LEVEL+SURFACE_SWING:
        fail('VG11',f'surface detail depth {SURFACE_DEPTH} does not exceed its own reach '
                    f'{SURFACE_LEVEL}+{SURFACE_SWING}; it would cut past every face into the '
                    'mass behind it and hollow the approach')
    if SURFACE_SWING<=SURFACE_LEVEL:
        fail('VG11',f'surface swing {SURFACE_SWING} never overcomes level {SURFACE_LEVEL}: the '
                    'term can never go negative and no surface would be roughened at all')

    # Three dimensions, or it is another heightfield and cuts no overhangs.
    flat=[n for n in walk(density)
          if n.get('type')=='minecraft:noise' and n.get('noise')=='alfheim:void/body'
          and not n.get('y_scale')]
    if flat:
        fail('VG9','the body carve is read with y_scale 0: a two-dimensional field cuts a '
                   'silhouette, not an alcove, and the faces stay vertical')

    for name,codec in EXPECTED_CODECS.items():
        key=f'kubejs/data/alfheim/worldgen/configured_feature/void/{name}.json'
        try:doc=json.loads(out[key])
        except KeyError:
            fail('VG4',f'missing configured feature {name}')
            continue
        if doc.get('type')!=codec:fail('VG4',f'{name} uses {doc.get("type")}, expected {codec}')
    root=json.loads(out['kubejs/data/alfheim/worldgen/configured_feature/void/root_aprons.json'])
    nested=root.get('config',{}).get('feature',{}).get('feature',{})
    if nested.get('type')!='minecraft:block_column':fail('VG5','root_aprons does not contain coherent block columns')
    config=nested.get('config',{})
    if config.get('direction')!='down':fail('VG5','root_aprons columns must descend into existing shelves')
    allowed=config.get('allowed_placement',{})
    if allowed.get('tag')!='alfheim:void_natural':fail('VG5','root_aprons can replace blocks outside narrow Void host stone')
    if block_names(root)!={'alfheim:rootfossil_livingrock','alfheim:resinshale_livingrock'}:
        fail('VG5','root_aprons materials are not exactly Rootfossil plus Resinshale')
    return problems

_ORIGINAL_DENSITY='{}'

def fixture():
    from gen_void_worldgen import CATALOG,density
    from gen_deep_terrain import build
    return copy.deepcopy(CATALOG),build(),density('mythicbotany:alfheim_final')

def self_test():
    global _ORIGINAL_DENSITY
    _ORIGINAL_DENSITY=json.dumps(fixture()[2])
    tests=[]
    def duplicate(c,o,d):c['biomes'][0]['terrain_grammar'][1]['feature']=c['biomes'][0]['terrain_grammar'][0]['feature']
    tests.append(('VG1',duplicate))
    def old_strata(c,o,d):c['biomes'][0]['terrain_grammar'][2]['material']='alfheim:riftchalk_livingrock'
    tests.append(('VG1',old_strata))
    def wrong_codec(c,o,d):
        k='kubejs/data/alfheim/worldgen/configured_feature/void/root_aprons.json';x=json.loads(o[k]);x['type']='minecraft:block_pile';o[k]=json.dumps(x).encode()
    tests.append(('VG4',wrong_codec))
    def wrong_direction(c,o,d):
        k='kubejs/data/alfheim/worldgen/configured_feature/void/root_aprons.json';x=json.loads(o[k]);x['config']['feature']['feature']['config']['direction']='up';o[k]=json.dumps(x).encode()
    tests.append(('VG5',wrong_direction))
    def loud_shore(c,o,d):
        def mutate(value):
            if isinstance(value,dict):
                term=value.get('argument2')
                if (value.get('type')=='minecraft:mul' and isinstance(term,dict)
                        and term.get('noise')=='alfheim:void/relief'):
                    value['argument1']=1.75;return True
                return any(mutate(v) for v in value.values())
            if isinstance(value,list):return any(mutate(v) for v in value)
            return False
        assert mutate(d)
    tests.append(('VG6',loud_shore))
    # VG7 has no artifact to mutate -- it asserts the generator's band ordering, which
    # check_deep_terrain and check_alfheim_hills separately prove the shipped file matches.
    # So its fixtures move the constants and re-derive, which is what would actually regress.
    def dry_over_seafloor(c,o,d):
        import gen_void_worldgen as g
        g.COAST_RIM=g.DRY_AQUIFER_RIM-0.01
    tests.append(('VG7',dry_over_seafloor))
    def hollow_approach(c,o,d):
        import gen_void_worldgen as g
        g.ATTACH_BIAS=1.0
    tests.append(('VG7',hollow_approach))
    def erosion_eats_the_plain(c,o,d):
        import gen_void_worldgen as g
        g.EDGE_WIDTH=0.40
    tests.append(('VG8',erosion_eats_the_plain))
    def uniform_trim(c,o,d):
        import gen_void_worldgen as g
        g.EDGE_SWING=0.0
    tests.append(('VG8',uniform_trim))
    def flat_face(c,o,d):
        import gen_void_worldgen as g
        g.EDGE_SPALL=0.0
    tests.append(('VG8',flat_face))
    def fins(c,o,d):
        import gen_void_worldgen as g
        g.UNDERCUT=0.06
    tests.append(('VG8',fins))
    def one_scale_only(c,o,d):
        import gen_void_worldgen as g
        g.BODY_MID=0.0
    tests.append(('VG9',one_scale_only))
    def saturated_body(c,o,d):
        import gen_void_worldgen as g
        g.BODY_SWING=0.10; g.BODY_MID=0.02; g.BODY_GRAIN=0.01
    tests.append(('VG9',saturated_body))
    def carve_reaches_the_shore(c,o,d):
        import gen_void_worldgen as g
        g.BODY_WIDTH=0.30
    tests.append(('VG9',carve_reaches_the_shore))
    def handover_back_at_the_contour(c,o,d):
        import gen_void_worldgen as g
        g.BREAK=g.CLIFF
    tests.append(('VG9',handover_back_at_the_contour))
    def shelf_in_the_void(c,o,d):
        import gen_void_worldgen as g
        g.BREAK=-0.90
    tests.append(('VG9',shelf_in_the_void))
    def plateau_to_the_waterline(c,o,d):
        import gen_void_worldgen as g
        g.RIM_TOP_SEA=(62,86)
    tests.append(('VG10',plateau_to_the_waterline))
    def flat_approach(c,o,d):
        import gen_void_worldgen as g
        g.RIM_TOP_BREAK=g.RIM_TOP_DRY
    tests.append(('VG10',flat_approach))
    def detail_hollows_the_plain(c,o,d):
        import gen_void_worldgen as g
        g.SURFACE_DEPTH=0.3
    tests.append(('VG11',detail_hollows_the_plain))
    def detail_does_nothing(c,o,d):
        import gen_void_worldgen as g
        g.SURFACE_SWING=0.0
    tests.append(('VG11',detail_does_nothing))
    def flat_carve(c,o,d):
        def mutate(value):
            if isinstance(value,dict):
                if value.get('noise')=='alfheim:void/body':
                    value['y_scale']=0.0;return True
                return any(mutate(v) for v in value.values())
            if isinstance(value,list):return any(mutate(v) for v in value)
            return False
        assert mutate(d)
    tests.append(('VG9',flat_carve))
    def full_section_at_the_break(c,o,d):
        import gen_void_worldgen as g
        g.RIM_BASE_LIP=(4,22)
    tests.append(('VG8',full_section_at_the_break))
    def uniform_thinning(c,o,d):
        import gen_void_worldgen as g
        g.EDGE_LIFT_SWING=0.0
    tests.append(('VG8',uniform_thinning))
    def no_far_cutoff(c,o,d):
        # Turn the literal far-field -1.0 into a merely-very-negative constant.
        def mutate(value):
            if isinstance(value,dict):
                if (value.get('type')=='minecraft:range_choice'
                        and value.get('input')=='mythicbotany:alfheim_continentalness'
                        and value.get('when_in_range')==-1.0):
                    value['when_in_range']=-0.999;return True
                return any(mutate(v) for v in value.values())
            if isinstance(value,list):return any(mutate(v) for v in value)
            return False
        assert mutate(d)
    tests.append(('VG3a',no_far_cutoff))
    def debris_on_the_shore(c,o,d):
        # Add a fragment term to the top level, outside the cliff branch.
        d.clear();d.update({'type':'minecraft:add','argument1':json.loads(_ORIGINAL_DENSITY),
                            'argument2':{'type':'minecraft:mul','argument1':0.2,
                                         'argument2':{'type':'minecraft:noise',
                                                      'noise':'alfheim:void/fragments',
                                                      'xz_scale':1.0,'y_scale':1.0}}})
    tests.append(('VG3b',debris_on_the_shore))
    def unbounded_debris(c,o,d):
        # Drop the vertical envelope: replace the min(min(grad,grad),field) with just the field.
        def mutate(value):
            if isinstance(value,dict):
                a=value.get('argument1')
                if (value.get('type')=='minecraft:min' and isinstance(a,dict)
                        and a.get('type')=='minecraft:min'
                        and isinstance(a.get('argument1'),dict)
                        and a['argument1'].get('type')=='minecraft:y_clamped_gradient'):
                    replacement=value['argument2']
                    value.clear();value.update(replacement);return True
                return any(mutate(v) for v in value.values())
            if isinstance(value,list):return any(mutate(v) for v in value)
            return False
        assert mutate(d)
    tests.append(('VG3c',unbounded_debris))
    dead=0
    # Some fixtures move generator constants rather than artifact bytes, so the module has to
    # be put back between tests or one fixture silently decides the next one's verdict.
    import gen_void_worldgen as _g
    baseline={k:getattr(_g,k) for k in ('COAST_RIM','DRY_AQUIFER_RIM','ATTACH_BIAS',
                                        'UNDERCUT','RIM_TOP_BREAK','RIM_TOP_DRY','RIM_TOP_SEA','RIM_RELIEF','RIM_DETAIL',
                                        'EDGE_WIDTH','EDGE_BITE','EDGE_SWING','EDGE_SPALL',
                                        'EDGE_LIFT','EDGE_LIFT_SWING','RIM_BASE_LIP',
                                        'BODY_WIDTH','BODY_LEVEL','BODY_SWING','BODY_SHELTER','BREAK','BODY_MID','BODY_GRAIN','SURFACE_LEVEL','SURFACE_SWING','SURFACE_DEPTH',
                                        )}
    for code,mutate in tests:
        try:
            c,o,d=fixture();mutate(c,o,d);hit=any(p.startswith(code) for p in validate(c,o,d))
        finally:
            for k,v in baseline.items():setattr(_g,k,v)
        print(f'  {code}  '+('FIRES' if hit else 'SILENT -- CHECK IS DEAD'));dead+=not hit
    print(f'\n  {len(tests)-dead}/{len(tests)} checks proven to fire')
    return 1 if dead else 0

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    if args.self_test:return self_test()
    catalog,out,density_doc=fixture();problems=validate(catalog,out,density_doc)
    for problem in problems:print('  '+problem)
    print(f'\n  {len(problems)} problem(s)')
    return 1 if problems else 0

if __name__=='__main__':raise SystemExit(main())
