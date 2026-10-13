"""Controlled Sacred Precinct placement; only disposable validation worlds."""
import argparse,json
from pathlib import Path
import subprocess,sys
import run_server

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--world',default='validation-sacred-precinct-20261013');args=ap.parse_args()
    world=ROOT/'server'/args.world
    assert args.world.startswith('validation-sacred-') and world.resolve().parent==(ROOT/'server').resolve()
    subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/check_sacred_precinct.py')],check=True)
    expected_fingerprint=json.loads((ROOT/'tools/sacred_precinct_manifest.json').read_text(encoding='utf-8'))['source_fingerprint']
    home='mythicbotany:alfheim'
    commands=[(100,'say sacred precinct assembly check'),
        (2,f'execute in {home} run forceload add -1552 544 -1297 799'),
        (60,f'execute in {home} run place structure alfheim:sacred_precinct -1443 80 654'),
        (35,'save-all flush'),(5,f'execute in {home} run forceload remove all'),(5,'stop')]
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run('3536368297089363045',args.world,8,commands,600)
    finally:
        props.write_bytes(original)
        p=ROOT/'server/config/jade/server-plugin-overrides.json';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    assert 'Generated structure "alfheim:sacred_precinct"' in text,log
    assert 'All dimensions are saved' in text,log
    subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/check_ancient_assembly.py'),str(world),'--family','sacred_precinct'],check=True)
    census=json.loads((ROOT/'tools/sacred_precinct_runtime_census.json').read_text(encoding='utf-8'))
    result={'world':args.world,'console':str(log.relative_to(ROOT)),'members':census['pieces'],
        'joins':census['clear_supported_joins'],'verified_air_cells':census['verified_air_cells'],
        'verified_foundation_cells':census['verified_foundation_cells'],
        'server_exit_code':0,'validation_exit_code':0,'visual_review':'pending','natural_placement':'not_enabled'}
    manifest=json.loads((ROOT/'tools/sacred_precinct_manifest.json').read_text(encoding='utf-8'))
    assert manifest['source_fingerprint']==expected_fingerprint,'source changed during validation'
    result['source_fingerprint']=expected_fingerprint
    (ROOT/'tools/sacred_precinct_runtime.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('SACRED PRECINCT RUNTIME PASS:',json.dumps(result))

if __name__=='__main__':main()
