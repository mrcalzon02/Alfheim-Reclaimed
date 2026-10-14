"""Controlled Military/Warden placement; only disposable validation worlds."""
import argparse,json
from pathlib import Path
import subprocess,sys
import run_server

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--world',default='validation-military-warden-20261013')
    ap.add_argument('--plants-only',action='store_true',help='Retest pads in an existing disposable assembly world')
    args=ap.parse_args()
    world=ROOT/'server'/args.world
    assert args.world.startswith('validation-military-') and world.resolve().parent==(ROOT/'server').resolve()
    subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/check_military_warden.py')],check=True)
    expected_fingerprint=json.loads((ROOT/'tools/military_warden_manifest.json').read_text(encoding='utf-8'))['source_fingerprint']
    home='mythicbotany:alfheim'
    commands=[(100,'say military warden assembly check'),
        (2,f'execute in {home} run forceload add -1552 544 -1297 799'),
        (60,f'execute in {home} run place structure alfheim:military_warden -1443 80 654'),
        (35,'save-all flush'),(5,f'execute in {home} run forceload remove all'),
        (2,f'execute in {home} run forceload add -128 -448 -1 -321'),
        (50,f'execute in {home} run forceload remove all'),
        (2,f'execute in {home} run forceload add 1024 1024 1151 1087')]
    if args.plants_only:
        assert world.is_dir(),'plants-only requires an existing validation world'
        commands=[(100,'say void undergrowth substrate check'),
                  (2,f'execute in {home} run forceload add 1024 1024 1151 1087')]
    from check_void_undergrowth_runtime import SUBSTRATES,PLANTS,census
    for row,plant in enumerate(PLANTS):
        for col,substrate in enumerate(SUBSTRATES):
            x=1024+col*32;z=1024+row*32
            commands.extend([(1,f'execute in {home} run fill {x} 198 {z} {x+24} 198 {z+24} minecraft:stone'),
                (2,f'execute in {home} run fill {x} 199 {z} {x+24} 200 {z+24} {substrate}'),
                (1,f'execute in {home} run fill {x} 201 {z} {x+24} 212 {z+24} minecraft:air'),
                (1,f'execute in {home} run fillbiome {x} 196 {z} {x+24} 216 {z+24} alfheim:void_shore')])
            feature='void_bramble' if row==0 else 'void_thornbush'
            for _ in range(3):commands.append((1,f'execute in {home} run place feature alfheim:{feature} {x+12} 201 {z+12}'))
    commands.extend([(30,'save-all flush'),(5,f'execute in {home} run forceload remove all'),(5,'stop')])
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run('3536368297089363045',args.world,8,commands,800)
    finally:
        props.write_bytes(original)
        p=ROOT/'server/config/jade/server-plugin-overrides.json';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    if not args.plants_only:assert 'Generated structure "alfheim:military_warden"' in text,log
    assert 'All dimensions are saved' in text,log
    census(world)
    subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/check_ancient_assembly.py'),str(world),'--family','military_warden'],check=True)
    census=json.loads((ROOT/'tools/military_warden_runtime_census.json').read_text(encoding='utf-8'))
    result={'world':args.world,'console':str(log.relative_to(ROOT)),'members':census['pieces'],
        'joins':census['clear_supported_joins'],'verified_air_cells':census['verified_air_cells'],
        'verified_foundation_cells':census['verified_foundation_cells'],
        'server_exit_code':0,'validation_exit_code':0,'visual_review':'pending','natural_placement':'not_enabled'}
    manifest=json.loads((ROOT/'tools/military_warden_manifest.json').read_text(encoding='utf-8'))
    assert manifest['source_fingerprint']==expected_fingerprint,'source changed during validation'
    result['source_fingerprint']=expected_fingerprint
    (ROOT/'tools/military_warden_runtime.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('MILITARY/WARDEN RUNTIME PASS:',json.dumps(result))

if __name__=='__main__':main()
