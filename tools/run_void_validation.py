"""Fresh, retained Void world; never touches a player save."""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import time
import run_server

def prune(server, keep):
    """Delete all but the newest `keep` disposable worlds and their consoles.

    Every run leaves a world behind and nothing ever removed one: by 2026-09-12 there were 27 of
    them holding 6.1 GB. They are untracked, so this was never a repository problem -- it is a
    disk problem that grows by roughly a quarter of a gigabyte per validation run, which is
    exactly the sort of thing that goes unnoticed until a generation fails for want of space.

    Only `void-margin-*` is touched, and only after the run has finished with it.
    """
    if keep <= 0:
        return
    worlds = sorted((p for p in server.glob('void-margin-*') if p.is_dir()),
                    key=lambda p: p.name, reverse=True)
    for stale in worlds[keep:]:
        shutil.rmtree(stale, ignore_errors=True)
        console = stale.with_suffix('.log')
        if console.exists():
            console.unlink()
    if len(worlds) > keep:
        print('pruned %d disposable world(s), kept %d' % (len(worlds) - keep, keep), flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',default='alfheim-deep-terrain-20260905')
    parser.add_argument('--keep',type=int,default=4,
                        help='disposable worlds to retain; 0 keeps all')
    parser.add_argument('--radius',type=int,default=192,
                        help='half-width in blocks generated around each void site')
    parser.add_argument('--probe',default='void_terrain_probe.js',
                        choices=['void_terrain_probe.js','void_landing_probe.js'],
                        help='void_landing_probe.js surveys the continentalness field for a '
                             'place where a terminal landing can exist at all')
    args=parser.parse_args()
    root=Path.cwd().resolve();server=root/'server'
    assert 'eula=true' in (server/'eula.txt').read_text().lower()
    assert not run_server.running_servers(),'Validation server already running'
    run_server.mirror_instance()
    # Which probe runs is the only difference between the ordinary margin audit and the
    # terminal-landing survey; both emit the same SITES marker, so the force-generation
    # and reporting path below is shared.
    shutil.copy2(root/'tools'/args.probe,server/'kubejs/server_scripts/99_void_audit.js')
    shutil.copy2(root/'tools/deep_terrain_treatment.json',server/'kubejs/void_prior_deep.json')
    prop=server/'server.properties';old=prop.read_bytes();stamp=time.strftime('%Y%m%d-%H%M%S');world='void-margin-'+stamp
    assert not (server/world).exists()
    run_server.write_properties(args.seed,world);path=server/(world+'.log')
    try:
        with path.open('w',encoding='utf-8',newline='\n') as log:
            process=subprocess.Popen([run_server.JAVA17,'-Xmx6G','-Xms4G','@libraries/net/minecraftforge/forge/1.20.1-47.4.10/win_args.txt','nogui'],cwd=server,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,text=True)
            print('Console:',path,flush=True);deadline=time.monotonic()+1800;requested=False;stopped=False
            while process.poll() is None and time.monotonic()<deadline:
                content=path.read_text(encoding='utf-8',errors='replace')
                match=re.search(r'\[VOID AUDIT\] SITES (\[.*\])',content)
                if match and not requested:
                    for p in json.loads(match.group(1)):
                        # Rhino serializes the lattice coordinates as JSON numbers and the
                        # decoder may therefore return e.g. -1856.0. Minecraft's command
                        # parser requires integer tokens even when the value is integral.
                        x,z=int(p['x']),int(p['z'])
                        # A SQUARE, NOT A LINE. This was `add {x-16} {z} {x+16} {z}` -- a 33x1 strip,
                        # which is enough to sample a column and not enough to see a landform. Every
                        # fragment measured out of such a world is clipped by the generated boundary,
                        # so probe_void_fragments.py reported the belt as rubble when the question was
                        # whether it carries the 14x14 landing check_void_surface_support requires.
                        for bx in range(x-args.radius,x+args.radius,128):
                            for bz in range(z-args.radius,z+args.radius,128):
                                process.stdin.write('execute in mythicbotany:alfheim run forceload '
                                                    f'add {bx} {bz} {bx+127} {bz+127}\n')
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
        (root/'tools'/('void-report-'+stamp+'.json')).write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    for name in ['startup','server']:
        if '[ERROR]' in (server/f'logs/kubejs/{name}.log').read_text(encoding='utf-8',errors='replace'):passed=False
    prune(root/'server',args.keep)
    print('exit=',process.returncode,'audit=',passed,flush=True)
    raise SystemExit(0 if passed else 1)

if __name__=='__main__':main()
