"""Isolated fresh-world generation; baseline uses exactly the same seed and sites.

First: python tools/run_deep_terrain_validation.py --mode treatment
Then:  python tools/run_deep_terrain_validation.py --mode baseline
Each run gets a unique world directory. No player save is touched or recycled.
"""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import time
import run_server
import gen_deep_terrain
from gen_alfheim_biomes import void_final_density


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--mode',choices=['treatment','baseline'],required=True)
    args=parser.parse_args()
    root=Path.cwd().resolve(); server=(root/'server').resolve()
    assert server.parent==root
    assert 'eula=true' in (server/'eula.txt').read_text().lower()
    assert not run_server.running_servers(), 'A validation server is already running'
    for name in run_server.MIRROR:
        target=(server/name).resolve(); assert target.parent==server
    run_server.mirror_instance()
    if args.mode=='baseline':
        for relative in gen_deep_terrain.build():
            target=(server/relative).resolve()
            assert target.is_relative_to(server/'kubejs/data')
            target.unlink()
        path=server/'kubejs/data/mythicbotany/worldgen/density_function/alfheim_final.json'
        path.write_text(json.dumps(void_final_density(False),indent=2)+'\n')
    shutil.copy2('tools/deep_terrain_probe.js',server/'kubejs/server_scripts/99_deep_terrain_probe.js')
    centers=[]
    if args.mode=='baseline':
        centers=json.loads((root/'tools/deep_terrain_treatment.json').read_text())['centers']
    (server/'kubejs/deep_terrain_options.json').write_text(json.dumps({'mode':args.mode,'centers':centers}))
    prop=server/'server.properties'; old=prop.read_bytes()
    stamp=time.strftime('%Y%m%d-%H%M%S')
    world='deep-terrain-'+args.mode+'-'+stamp
    assert not (server/world).exists()
    run_server.write_properties(gen_deep_terrain.config()['seed'],world)
    path=server/f'deep-terrain-{args.mode}-{stamp}.log'
    try:
        with path.open('w',encoding='utf-8') as log:
            process=subprocess.Popen([run_server.JAVA17,'-Xmx6G','-Xms4G',
                '@libraries/net/minecraftforge/forge/1.20.1-47.4.10/win_args.txt','nogui'],
                cwd=server,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,text=True)
            print('Console:',path,flush=True)
            deadline=time.monotonic()+900; stopped=False; requested=False
            while process.poll() is None and time.monotonic()<deadline:
                text=path.read_text(encoding='utf-8',errors='replace')
                match=re.search(r'\[TERRAIN AUDIT\] SITES (\[.*\])',text)
                if match and not requested:
                    for site in json.loads(match.group(1)):
                        x,z=int(site['x']),int(site['z'])
                        for bounds in [(x-128,z,x+128,z),(x,z-128,x,z+128)]:
                            process.stdin.write('execute in mythicbotany:alfheim run forceload add '+' '.join(map(str,bounds))+'\n')
                    process.stdin.flush(); requested=True
                if 'Failed to start the minecraft server' in text:
                    process.terminate(); process.wait(timeout=20); break
                if not stopped and any(s in text for s in ['[TERRAIN AUDIT] COMPLETE','Error in scheduled task',
                       'Error occurred while handling scheduled event callback']):
                    process.stdin.write('save-all flush\nstop\n'); process.stdin.flush(); stopped=True
                time.sleep(1)
            if process.poll() is None:
                process.stdin.write('stop\n'); process.stdin.flush()
                try: process.wait(timeout=45)
                except subprocess.TimeoutExpired:
                    process.terminate(); process.wait(timeout=20)
    finally: prop.write_bytes(old)
    content=path.read_text(encoding='utf-8',errors='replace')
    passed=process.returncode==0 and '[TERRAIN AUDIT] COMPLETE sections=6 samples=112230' in content
    for name in ['startup','server']:
        if '[ERROR]' in (server/f'logs/kubejs/{name}.log').read_text(encoding='utf-8',errors='replace'): passed=False
    if passed:
        report=json.loads((server/'kubejs/deep_terrain_result.json').read_text())
        report.update(world=world,console=path.name)
        (root/f'tools/deep_terrain_{args.mode}.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
    # The baseline was only a development-mirror experiment. Restore the source's
    # worldgen after shutdown, so a later manual server launch uses the real pack.
    if args.mode=='baseline':
        files=list(gen_deep_terrain.build())+['kubejs/data/mythicbotany/worldgen/density_function/alfheim_final.json']
        for name in files:
            target=(server/name).resolve()
            assert target.is_relative_to(server/'kubejs/data')
            target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(root/name,target)
    for name in ['kubejs/server_scripts/99_deep_terrain_probe.js','kubejs/deep_terrain_options.json']:
        target=(server/name).resolve()
        assert target.is_relative_to(server/'kubejs')
        target.unlink(missing_ok=True)
    print('exit=',process.returncode,'audit=',passed,'world=',world,flush=True)
    raise SystemExit(0 if passed else 1)


if __name__=='__main__': main()
