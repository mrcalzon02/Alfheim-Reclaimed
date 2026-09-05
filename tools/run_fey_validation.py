"""Boot a separate development world, inspect final biome tables and instantiate all fauna."""
import json
from pathlib import Path
import shutil
import subprocess
import time
import run_server

original_mirror = run_server.mirror_instance


def mirror():
    # The existing harness replaces these development mirrors. Resolve every delete target
    # before handing over; no player save directory or path outside server/ is eligible.
    root=Path.cwd().resolve()
    server=(root/'server').resolve()
    assert server.parent==root
    for name in run_server.MIRROR:
        target=(server/name).resolve()
        assert target.parent==server and target.name in run_server.MIRROR
    original_mirror()
    shutil.copy2('tools/fey_validation_probe.js','server/kubejs/server_scripts/99_fey_validation.js')
    shutil.copy2('tools/zombie_habitat_manifest.json','server/kubejs/zombie_habitat_manifest.json')


if __name__=='__main__':
    assert 'eula=true' in Path('server/eula.txt').read_text().lower()
    assert not run_server.running_servers(), 'A validation server is already running'
    mirror()
    run_server.write_properties('alfheim-fey-20260904','fey-validation')
    path=Path('server')/time.strftime('fey-console-%Y%m%d-%H%M%S.log')
    args=['libraries/net/minecraftforge/forge/1.20.1-47.4.10/win_args.txt']
    with path.open('w',encoding='utf-8') as log:
        process=subprocess.Popen([run_server.JAVA17,'-Xmx6G','-Xms4G','@'+args[0],'nogui'],
            cwd='server',stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,text=True)
        print('Validation console:',path,flush=True)
        deadline=time.monotonic()+240
        stopped=False
        while process.poll() is None and time.monotonic()<deadline:
            content=path.read_text(encoding='utf-8',errors='replace')
            if not stopped and ('[FEY AUDIT] COMPLETE' in content or 'Error in scheduled task' in content):
                process.stdin.write('save-all flush\nstop\n')
                process.stdin.flush()
                stopped=True
            time.sleep(1)
        if process.poll() is None:
            process.stdin.write('stop\n')
            process.stdin.flush()
            try:
                process.wait(timeout=45)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=20)
    content=path.read_text(encoding='utf-8',errors='replace')
    passed=process.returncode==0 and '[FEY AUDIT] COMPLETE' in content and 'missing=0' in content
    print('exit=',process.returncode,'audit=',passed,flush=True)
    raise SystemExit(0 if passed else 1)
