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
    from gen_void_worldgen import FRINGE,CLIFF,DEBRIS_Y_RISE
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
                    and node.get('max_exclusive')==CLIFF):
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
                    and n.get('max_exclusive')==CLIFF]
    if not cliff_branches:
        fail('VG3b',f'no continentalness branch at the cliff ({CLIFF}); debris containment '
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
    # rim_top is gradient(RIM_TOP, 1, -1) + relief, so it crosses zero at
    #     y = lo + (hi - lo) * (1 + r) / 2
    # and the lowest surface the plain can produce is that at r = -(RIM_RELIEF + RIM_DETAIL).
    from gen_void_worldgen import (RIM_TOP, RIM_RELIEF, RIM_DETAIL, RIM_BASE,
                                   RIM_BASE_WANDER, UNDERCUT, COAST_RIM, DRY_AQUIFER_RIM,
                                   ATTACH_BIAS)
    SEA_LEVEL=64
    # Read out of the SHIPPED density, not out of the generator's constants: this is the one
    # assertion standing between the approach and a water table inside it, so it reads the
    # bytes the game will load. rim_top is the add() of a 1 -> -1 gradient and the two quiet
    # plain noises, which no other node in this tree has the shape of.
    tops=[]
    for node in walk(density):
        if node.get('type')!='minecraft:add': continue
        grad,relief=node.get('argument1'),node.get('argument2')
        if not (isinstance(grad,dict) and grad.get('type')=='minecraft:y_clamped_gradient'
                and grad.get('from_value')==1 and grad.get('to_value')==-1): continue
        amps={}
        for sub in walk(relief):
            if sub.get('type')!='minecraft:mul': continue
            for scalar,term in ((sub.get('argument1'),sub.get('argument2')),
                                (sub.get('argument2'),sub.get('argument1'))):
                if (isinstance(scalar,(int,float)) and isinstance(term,dict)
                        and term.get('type')=='minecraft:noise'):
                    amps[term.get('noise')]=abs(float(scalar))
        if set(amps)=={'alfheim:void/relief','alfheim:void/detail'}:
            tops.append((grad.get('from_y'),grad.get('to_y'),sum(amps.values())))
    if not tops:
        fail('VG6','no Verge plain surface found in final density: an add() of a 1 -> -1 '
                   'y_clamped_gradient and the relief/detail noises. Its height cannot be '
                   'bounded, so nothing stops the approach reaching the water table.')
    for lo,hi,swing in tops:
        if swing>=1.0:
            fail('VG6',f'plain relief {swing} saturates the y{lo}..y{hi} gradient; the '
                       'surface would no longer track the gradient at all')
            continue
        lowest=lo+(hi-lo)*(1.0-swing)/2.0
        if lowest<=SEA_LEVEL:
            fail('VG6',f'the Verge plain can fall to y{lowest:.1f}, at or below sea level '
                       f'{SEA_LEVEL}: relief totalling {swing} over gradient y{lo}..y{hi}. '
                       'A dry approach cannot have its own water table in it.')
    if RIM_RELIEF+RIM_DETAIL!=max(t[2] for t in tops) or RIM_TOP!=tops[0][:2]:
        fail('VG6','the shipped plain surface does not match the generator constants')
    # And the terms that shape it must be the quiet ones. Which noises, not how loud:
    # the sharper vocabulary belongs to bounded configured features beyond the cliff.
    plain_noises={'alfheim:void/relief','alfheim:void/detail','alfheim:void/rim_base'}
    multipliers={}
    for node in walk(density):
        if node.get('type')!='minecraft:mul':continue
        for scalar,term in ((node.get('argument1'),node.get('argument2')),
                            (node.get('argument2'),node.get('argument1'))):
            if isinstance(scalar,(int,float)) and isinstance(term,dict) and term.get('type')=='minecraft:noise':
                multipliers.setdefault(term.get('noise'),[]).append(abs(float(scalar)))
    for noise_id,amps in multipliers.items():
        if noise_id in plain_noises: continue
        if noise_id in DEBRIS_DENSITY_NOISES: continue
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
                                        'UNDERCUT','RIM_TOP','RIM_RELIEF','RIM_DETAIL')}
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
