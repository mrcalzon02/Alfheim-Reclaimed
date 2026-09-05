"""Runtime-accept the generated fey wildlife through the authoritative server harness.

The probe validates only the fey-wildlife contract: every manifest habitat must contain its
species in the final Forge biome mob table, and all 18 entity registrations must instantiate with
the registered dimensions and health. Zombie habitat validation is deliberately separate because
B-76 remains an independent unresolved spawn-policy defect.

This wrapper does not own server launch semantics. It injects one development-only probe into the
runtime mirror, then delegates launch, world creation, command sequencing, shutdown, exit status,
console capture and manifest evidence to tools/run_server.py.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import run_server

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / 'server'
PROBE_SOURCE = ROOT / 'tools' / 'fey_validation_probe.js'
PROBE_TARGET = SERVER / 'kubejs' / 'server_scripts' / '99_fey_validation.js'
SEED = 'alfheim-fey-20260904'
LEVEL_NAME = 'fey-validation'
HEAP_GIB = 6
TIMEOUT_S = 1200

_original_mirror = run_server.mirror_instance


<<<<<<< Updated upstream
def mirror_with_probe():
    """Use the normal runtime mirror, then add the non-shipping audit script."""
    _original_mirror()
    PROBE_TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROBE_SOURCE, PROBE_TARGET)
    print(f'  injected {PROBE_TARGET.relative_to(ROOT)}')


def new_console(before: set[Path]) -> Path:
    after = {p.resolve() for p in SERVER.glob('console-*.log')}
    created = sorted(after - before, key=lambda p: p.stat().st_mtime)
    if len(created) != 1:
        names = ', '.join(str(p.name) for p in created) or 'none'
        raise RuntimeError(f'expected exactly one new server console, found {len(created)}: {names}')
    return created[0]
=======
def mirror():
    # The existing harness replaces these development mirrors. Resolve every delete target
    # before handing over; no player save directory or path outside server/ is eligible.
    root = Path.cwd().resolve()
    server = (root / 'server').resolve()
    assert server.parent == root
    for name in run_server.MIRROR:
        target = (server / name).resolve()
        assert target.parent == server and target.name in run_server.MIRROR
    original_mirror()
    shutil.copy2('tools/fey_validation_probe.js',
                 'server/kubejs/server_scripts/99_fey_validation.js')
    shutil.copy2('tools/fey_drops_manifest.json','server/kubejs/fey_drops_manifest.json')


if __name__ == '__main__':
    assert 'eula=true' in Path('server/eula.txt').read_text().lower()
    assert not run_server.running_servers(), 'A validation server is already running'
    mirror()
    run_server.write_properties('alfheim-fey-20260904', 'fey-validation')
    path = Path('server') / time.strftime('fey-console-%Y%m%d-%H%M%S.log')
    args = ['libraries/net/minecraftforge/forge/1.20.1-47.4.10/win_args.txt']
    with path.open('w', encoding='utf-8') as log:
        process = subprocess.Popen(
            [run_server.JAVA17, '-Xmx6G', '-Xms4G', '@' + args[0], 'nogui'],
            cwd='server', stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT, text=True)
        print('Validation console:', path, flush=True)
        deadline = time.monotonic() + 240
        stopped = False
        while process.poll() is None and time.monotonic() < deadline:
            content = path.read_text(encoding='utf-8', errors='replace')
            if not stopped and ('[FEY AUDIT] COMPLETE' in content or
                                'Error in scheduled task' in content or
                                'Error occurred while handling scheduled event callback' in content):
                process.stdin.write('save-all flush\nstop\n')
                process.stdin.flush()
                stopped = True
            time.sleep(1)
        if process.poll() is None:
            process.stdin.write('stop\n')
            process.stdin.flush()
            try:
                process.wait(timeout=45)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=20)
>>>>>>> Stashed changes


def analyze_console(path: Path, harness_exit: int) -> int:
    content = path.read_text(encoding='utf-8', errors='replace')
    required = (
        '[FEY AUDIT] Habitat coverage: species=18',
        ' missing=0',
        '[FEY AUDIT] Creature construction: created=18 expected=18 mismatches=0',
        '[FEY AUDIT] COMPLETE habitat_missing=0 creature_mismatches=0',
        '[FEY AUDIT] Drops: items=13 recipes=14 errors=0',
    )
    missing = [marker for marker in required if marker not in content]
    passed = harness_exit == 0 and not missing
    print('harness_exit=', harness_exit, 'audit=', passed, 'console=', path, flush=True)
    if missing:
        print('missing acceptance marker(s):', *missing, sep='\n  ', flush=True)
    return 0 if passed else 1


def main() -> int:
    assert ROOT == Path.cwd().resolve(), 'run from the Alfheim Reclaimed repository root'
    assert PROBE_SOURCE.is_file(), f'missing probe: {PROBE_SOURCE}'

    before = {p.resolve() for p in SERVER.glob('console-*.log')}
    run_server.mirror_instance = mirror_with_probe
    try:
        harness_exit = run_server.run(
            SEED,
            LEVEL_NAME,
            HEAP_GIB,
            list(run_server.DEFAULT_COMMANDS),
            TIMEOUT_S,
        )
    finally:
        run_server.mirror_instance = _original_mirror

    path = new_console(before)
    return analyze_console(path, harness_exit)


if __name__ == '__main__':
    raise SystemExit(main())
