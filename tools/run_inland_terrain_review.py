"""Generate one bounded terrain-only reference patch; never place review structures."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import run_server

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--world',default='validation-inland-terrain-baseline-20261014');args=ap.parse_args()
    assert args.world.startswith('validation-inland-terrain-') and Path(args.world).name==args.world
    subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/check_field_review.py')],check=True)
    props=ROOT/'server/server.properties';original=props.read_bytes();home='mythicbotany:alfheim'
    commands=[(100,'say inland terrain reference patch'),
        (2,f'execute in {home} run forceload add -1552 544 -1297 799'),
        (65,'save-all flush'),(5,f'execute in {home} run forceload remove all'),(5,'stop')]
    try:code=run_server.run('3536368297089363045',args.world,8,commands,500)
    finally:
        props.write_bytes(original)
        (ROOT/'server/config/jade/server-plugin-overrides.json').write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    assert 'Done (' in text and 'All dimensions are saved' in text,log
    result={'world':args.world,'seed':'3536368297089363045','console':log.relative_to(ROOT).as_posix(),
        'bounds':[-1552,544,-1297,799],'forceload_chunk_limit':256,'structures_placed_by_harness':0,'server_exit_code':0,
        'protected_terrain_baseline_sha256':hashlib.sha256((ROOT/'tools/field_review_terrain_baseline.json').read_bytes()).hexdigest(),
        'scope':'One inland reference patch generated normally; existing naturally generated structures are retained and reported. No player saves are edited.'}
    (ROOT/'tools/inland_terrain_reference.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('INLAND TERRAIN REFERENCE SAVED:',json.dumps(result))

if __name__=='__main__':main()
