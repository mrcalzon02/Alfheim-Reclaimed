"""Frontier assembly and existing void details in a disposable validation world."""
import argparse,json,subprocess,sys
from pathlib import Path
import run_server
from check_void_details_runtime import CASES,census

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--world',default='validation-frontier-stewardship-20261013');args=ap.parse_args()
    world=ROOT/'server'/args.world
    assert args.world.startswith('validation-frontier-') and world.resolve().parent==(ROOT/'server').resolve()
    subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/check_frontier_stewardship.py')],check=True)
    expected=json.loads((ROOT/'tools/frontier_stewardship_manifest.json').read_text(encoding='utf-8'))['source_fingerprint']
    home='mythicbotany:alfheim'
    commands=[(100,'say frontier stewardship assembly check'),
        (2,f'execute in {home} run forceload add -1552 544 -1297 799'),
        (60,f'execute in {home} run place structure alfheim:frontier_stewardship -1443 80 654'),
        (35,'save-all flush'),(5,f'execute in {home} run forceload remove all'),
        (2,f'execute in {home} run forceload add 1024 1024 1247 1055')]
    for index,(feature,biome,host,_) in enumerate(CASES):
        x=1024+index*48;z=1024
        commands.extend([(3,f'execute in {home} run fill {x} 180 {z} {x+30} 200 {z+30} alfheim:{host}_livingrock'),
            (1,f'execute in {home} run fill {x} 201 {z} {x+30} 216 {z+30} minecraft:air'),
            (1,f'execute in {home} run fillbiome {x} 176 {z} {x+30} 216 {z+30} alfheim:{biome}')])
        # /place feature addresses ConfiguredFeature, so ore starts inside its host;
        # root_aprons itself offsets down one. Outer rarity/heightmap are not tested here.
        y=199 if feature=='astralite_flecks' else 201
        for _ in range(10 if feature=='astralite_flecks' else 3):
            commands.append((1,f'execute in {home} run place feature alfheim:void/{feature} {x+8} {y} {z+8}'))
    commands.extend([(30,'save-all flush'),(5,f'execute in {home} run forceload remove all'),(5,'stop')])
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run('3536368297089363045',args.world,8,commands,700)
    finally:
        props.write_bytes(original)
        path=ROOT/'server/config/jade/server-plugin-overrides.json'
        path.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    assert 'Generated structure "alfheim:frontier_stewardship"' in text and 'All dimensions are saved' in text,log
    census(world)
    subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/check_ancient_assembly.py'),str(world),'--family','frontier_stewardship'],check=True)
    saved=json.loads((ROOT/'tools/frontier_stewardship_runtime_census.json').read_text(encoding='utf-8'))
    assert json.loads((ROOT/'tools/frontier_stewardship_manifest.json').read_text(encoding='utf-8'))['source_fingerprint']==expected
    report={'world':args.world,'console':log.relative_to(ROOT).as_posix(),'source_fingerprint':expected,
            'members':saved['pieces'],'joins':saved['clear_supported_joins'],'verified_air_cells':saved['verified_air_cells'],
            'verified_foundation_cells':saved['verified_foundation_cells'],'validation_exit_code':0,'server_exit_code':0,
            'visual_review':'pending','natural_placement':'not_enabled'}
    (ROOT/'tools/frontier_stewardship_runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('FRONTIER RUNTIME PASS:',json.dumps(report))

if __name__=='__main__':main()
