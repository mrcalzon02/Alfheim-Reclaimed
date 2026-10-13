"""Fresh-world checks for the field review; never opens a player save."""
import argparse
from pathlib import Path
import re
import run_server
import nbt

ROOT=Path(__file__).resolve().parents[1]
HOME='mythicbotany:alfheim'
ANCHOR='@e[type=minecraft:marker,tag=alfheim_hub_baked,limit=1]'


def commands():
    out=[(100,'say field review startup reached'),(2,'function alfheim:hub/status'),
         (2,f'execute in {HOME} at {ANCHOR} run function alfheim:hub/ensure_landing'),
         (2,f'execute in {HOME} at {ANCHOR} unless block ~ ~-1 ~ minecraft:air '
          'run say FIELD_REVIEW_PASS landing_floor'),
         (2,f'execute in {HOME} at {ANCHOR} if block ~ ~ ~ minecraft:air '
          'if block ~ ~1 ~ minecraft:air run say FIELD_REVIEW_PASS landing_headroom'),
         (2,f'execute in {HOME} at {ANCHOR} positioned ~-48 ~-7 ~-48 '
          'unless block ~ ~ ~ minecraft:air run say FIELD_REVIEW_PASS court_foundation')]
    sites=[('deepworks_archaeology/elder_kings_tomb/wing',384,40,384),
           ('leyline/straight',256,80,256),('field_review/golden_field_dais',512,120,512),
           ('field_review/thorn_gate',576,120,512),('field_review/shore_memorial_court',640,120,512)]
    for name,x,y,z in sites:
        out += [(2,f'execute in {HOME} run forceload add {x} {z} {x+47} {z+63}'),
                (5,f'execute in {HOME} run place template alfheim:{name} {x} {y} {z}')]
    out += [(2,f'execute in {HOME} if block 407 54 404 minecraft:air '
             'if block 407 55 404 minecraft:air if block 407 56 404 minecraft:air '
             'unless block 407 57 404 minecraft:air run say FIELD_REVIEW_PASS rotunda_crown'),
            (2,f'execute in {HOME} if block 531 124 531 minecraft:dirt_path '
             'if block 531 123 531 alfheim:ivory_livingrock_bricks '
             'run say FIELD_REVIEW_PASS raised_field'),
            (2,f'execute in {HOME} if block 586 125 520 alfheim:gloam_livingrock_bricks '
             'run say FIELD_REVIEW_PASS thorn_gate'),
            (2,f'execute in {HOME} if block 655 123 527 alfheim_leyworks:memorial_urn '
             'run say FIELD_REVIEW_PASS memorial_court')]
    _,p=nbt.load(str(ROOT/'kubejs/data/alfheim/structures/leyline/straight.nbt'))
    for b in p['blocks']:
        state=p['palette'][int(b['state'])]
        if state['Name'].endswith('_wall') and any(v=='low' for v in state.get('Properties',{}).values()):
            x,y,z=map(int,b['pos']); props=','.join(f'{k}={v}' for k,v in state['Properties'].items())
            out.append((2,f'execute in {HOME} if block {256+x} {80+y} {256+z} '
                        f'{state["Name"]}[{props}] run say FIELD_REVIEW_PASS connected_rail'))
            break
    out += [(2,f'execute in {HOME} run forceload add -1507 590 -1379 718'),
            (45,'say Golden Fields screenshot area generated'),
            (25,'save-all flush'),(4,'stop')]
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true')
    ap.add_argument('--finish',action='store_true',help='Bounded mushroom and existing-hub upgrade checks')
    ap.add_argument('--structures-only',action='store_true',help='Biome and heightmap placement checks')
    ap.add_argument('--seed',default='3536368297089363045')
    ap.add_argument('--world',default='validation-field-review-bounded-20261012')
    args=ap.parse_args()
    sequence=commands()
    if args.finish:
        from gen_world_hub import OBJ
        sequence=[(75,'say field review final checks'),
                  (2,f'execute if score #foundation_v1 {OBJ} matches 1 run say FIELD_REVIEW_PASS legacy_foundation'),
                  (2,f'execute in {HOME} run forceload add 864 512 895 543'),
                  (5,f'execute in {HOME} run fill 864 180 512 895 180 543 minecraft:mycelium'),
                  (2,f'execute in {HOME} run fill 864 181 512 895 184 543 minecraft:air')]
        sequence += [(2,f'execute in {HOME} run place feature alfheim:shore_spore_scatter 880 181 528') for _ in range(8)]
        sequence += [(2,f'execute in {HOME} store success score #field_check {OBJ} '
                      'run place structure alfheim:golden_field_dais -1443 80 654'),
                     (2,f'execute if score #field_check {OBJ} matches 1 '
                      'run say FIELD_REVIEW_PASS natural_field_placement'),
                     (5,f'execute in {HOME} run forceload remove all'),
                     (5,'save-all flush'),(4,'stop')]
    if args.structures_only:
        from gen_world_hub import OBJ
        sequence=[(75,'say field review structure checks')]
        for name,x,z in [('golden_field_dais',-1443,654),('thorn_gate',-280,72),('shore_memorial_court',24,-296)]:
            sequence += [(2,f'execute in {HOME} run forceload add {x-32} {z-32} {x+32} {z+32}'),
                         (15,f'execute in {HOME} store success score #structure_check {OBJ} '
                          f'run place structure alfheim:{name} {x} 80 {z}'),
                         (2,f'execute if score #structure_check {OBJ} matches 1 '
                          f'run say FIELD_REVIEW_PASS {name}')]
        sequence += [(5,f'execute in {HOME} run forceload remove all'),(5,'save-all flush'),(4,'stop')]
    if not args.run:
        for delay,line in sequence:print(delay,line)
        return
    properties=ROOT/'server/server.properties'
    original=properties.read_bytes()
    try:
        code=run_server.run(args.seed,args.world,8,sequence,300)
    finally:
        properties.write_bytes(original)
    assert code==0,code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    expected={'landing_floor','landing_headroom','court_foundation','rotunda_crown',
              'raised_field','thorn_gate','memorial_court','connected_rail'}
    if args.finish:expected={'legacy_foundation','natural_field_placement'}
    if args.structures_only:expected={'golden_field_dais','thorn_gate','shore_memorial_court'}
    found=set(re.findall(r'FIELD_REVIEW_PASS (\w+)',text))
    assert expected <= found, ('Missing runtime probes',expected-found,log)
    assert 'All dimensions are saved' in text
    assert not re.search(r'Failed to parse|Couldn.t parse element|Unknown registry key|Errors in currently selected datapacks',text)
    print(f'FIELD REVIEW RUNTIME PASS: {len(expected)} probes, saved and exited; {log.name}')


if __name__=='__main__': main()
