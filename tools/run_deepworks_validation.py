"""Validate the new library in an isolated, retained material-review world."""
from pathlib import Path
import shutil
import subprocess
import time
import run_server


if __name__ == '__main__':
    root = Path.cwd().resolve()
    server = (root/'server').resolve()
    assert server.parent == root
    assert 'eula=true' in (server/'eula.txt').read_text().lower()
    assert not run_server.running_servers(), 'A validation server is already running'
    for name in run_server.MIRROR:
        target = (server/name).resolve()
        assert target.parent == server and target.name in run_server.MIRROR
    run_server.mirror_instance()
    shutil.copy2('tools/deepworks_validation_probe.js', server/'kubejs/server_scripts/99_deepworks_validation.js')
    # Restore the previous harness configuration after the isolated run.
    properties = server/'server.properties'
    old_properties = properties.read_bytes() if properties.exists() else None
    run_server.write_properties('alfheim-deepworks-materials-20260905', 'deepworks-validation')
    path = server/time.strftime('deepworks-console-%Y%m%d-%H%M%S.log')
    try:
        with path.open('w', encoding='utf-8') as log:
            process = subprocess.Popen([run_server.JAVA17, '-Xmx6G', '-Xms4G',
                '@libraries/net/minecraftforge/forge/1.20.1-47.4.10/win_args.txt', 'nogui'],
                cwd=server, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT, text=True)
            print('Validation console:', path, flush=True)
            deadline = time.monotonic()+420
            stopped = False
            while process.poll() is None and time.monotonic()<deadline:
                content = path.read_text(encoding='utf-8', errors='replace')
                if 'Failed to start the minecraft server' in content:
                    process.terminate(); process.wait(timeout=20)
                    break
                if not stopped and ('[DEEP AUDIT] COMPLETE' in content or 'Error in scheduled task' in content or
                    'Error occurred while handling scheduled event callback' in content):
                    process.stdin.write('save-all flush\nstop\n'); process.stdin.flush()
                    stopped = True
                time.sleep(1)
            if process.poll() is None:
                process.stdin.write('stop\n'); process.stdin.flush()
                try: process.wait(timeout=45)
                except subprocess.TimeoutExpired:
                    process.terminate(); process.wait(timeout=20)
    finally:
        if old_properties is not None: properties.write_bytes(old_properties)
    content = path.read_text(encoding='utf-8', errors='replace')
    passed = process.returncode == 0 and '[DEEP AUDIT] COMPLETE blocks=175 recipes=174 loot=374 errors=0' in content
    for name in ['startup','server']:
        logfile = server/f'logs/kubejs/{name}.log'
        if logfile.exists() and '[ERROR]' in logfile.read_text(encoding='utf-8', errors='replace'):
            passed = False
    print('exit=', process.returncode, 'audit=', passed, flush=True)
    raise SystemExit(0 if passed else 1)
