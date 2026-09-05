"""Fresh, retained Void world; never touches a player save."""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import time
import run_server

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seed',default='alfheim-deep-terrain-20260905');args=parser.parse_args()
    root=Path.cwd().resolve();server=root/'server'
    assert 'eula=true' in (server/'eula.txt').read_text().lower()
    assert not run_server.running_servers(),'Validation server already running'
    run_server.mirror_instance()
    shutil.copy2(root/'tools/void_terrain_probe.js',server/'kubejs/server_scripts/99_void_audit.js')
    shutil.copy2(root/'tools/deep_terrain_treatment.json',server/'kubejs/void_prior_deep.json')
    prop=server/'server.properties';old=prop.read_bytes();stamp=time.strftime('%Y%m%d-%H%M%S');world='void-margin-'+stamp
    assert not (server/world).exists()
    run_server.write_properties(args.seed,world);path=server/(world+'.log')
    try:
        with path.open('w',encoding='utf-8') as log:
            process=subprocess.Popen([run_server.JAVA17,'-Xmx6G','-Xms4G','@libraries/net/minecraftforge/forge/1.20.1-47.4.10/win_args.txt','nogui'],cwd=server,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,text=True)
            print('Console:',path,flush=True);deadline=time.monotonic()+720;requested=False;stopped=False
            while process.poll() is None and time.monotonic()<deadline:
                content=path.read_text(encoding='utf-8',errors='replace')
                match=re.search(r'\[VOID AUDIT\] SITES (\[.*\])',content)
                if match and not requested:
                    for p in json.loads(match.group(1)):
                        x,z=p['x'],p['z'];process.stdin.write(f'execute in mythicbotany:alfheim run forceload add {x-16} {z} {x+16} {z}\n')
                    process.stdin.flush();requested=True
                if 'Failed to start the minecraft server' in content:process.terminate();process.wait(timeout=20);break
                if not stopped and any(s in content for s in ['[VOID AUDIT] COMPLETE','Error in scheduled task','Error occurred while handling scheduled event callback']):
                    process.stdin.write('save-all flush\nstop\n');process.stdin.flush();stopped=True
                time.sleep(1)
            if process.poll() is None:
                process.stdin.write('stop\n');process.stdin.flush()
                try:process.wait(timeout=45)
                except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=20)
    finally:
        prop.write_bytes(old)
        for name in ['server_scripts/99_void_audit.js','void_prior_deep.json']:(server/'kubejs'/name).unlink(missing_ok=True)
    content=path.read_text(encoding='utf-8',errors='replace')
    passed=process.returncode==0 and '[VOID AUDIT] COMPLETE errors=0' in content
    if '[VOID AUDIT] COMPLETE' in content:
        report=json.loads((server/'kubejs/void_terrain_result.json').read_text());report.update(world=world,seed=args.seed,console=path.name)
        (root/'tools'/('void-report-'+stamp+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    for name in ['startup','server']:
        if '[ERROR]' in (server/f'logs/kubejs/{name}.log').read_text(encoding='utf-8',errors='replace'):passed=False
    print('exit=',process.returncode,'audit=',passed,flush=True)
    raise SystemExit(0 if passed else 1)

if __name__=='__main__':main()
