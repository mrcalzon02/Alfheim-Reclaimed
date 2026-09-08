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
FORBIDDEN_DENSITY_NOISES={
    'alfheim:void/fragments','alfheim:void/fracture','alfheim:void/shape',
    'alfheim:void/pressure_plates','alfheim:void/fault_needles',
    'alfheim:void/prism_cores','alfheim:void/split_seams',
    'alfheim:void/root_ribs','alfheim:void/burial_beds',
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
    if leaked:fail('VG3',f'procedural debris fields returned to final density: {sorted(leaked)}')
    # Only broad, low-amplitude relief may shape the supported shore. All sharper
    # vocabulary belongs to bounded configured features beyond the cliff.
    multipliers={}
    for node in walk(density):
        if node.get('type')!='minecraft:mul':continue
        for scalar,term in ((node.get('argument1'),node.get('argument2')),
                            (node.get('argument2'),node.get('argument1'))):
            if isinstance(scalar,(int,float)) and isinstance(term,dict) and term.get('type')=='minecraft:noise':
                multipliers.setdefault(term.get('noise'),[]).append(abs(float(scalar)))
    limits={'alfheim:void/relief':0.18,'alfheim:void/detail':0.05}
    for noise_id,limit in limits.items():
        if max(multipliers.get(noise_id,[999]))>limit:
            fail('VG6',f'{noise_id} exceeds quiet gross-terrain amplitude {limit}')

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

def fixture():
    from gen_void_worldgen import CATALOG,density
    from gen_deep_terrain import build
    return copy.deepcopy(CATALOG),build(),density('mythicbotany:alfheim_final')

def self_test():
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
    dead=0
    for code,mutate in tests:
        c,o,d=fixture();mutate(c,o,d);hit=any(p.startswith(code) for p in validate(c,o,d))
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
