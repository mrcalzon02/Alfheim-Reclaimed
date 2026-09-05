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


def analyze_console(path: Path, harness_exit: int) -> int:
    content = path.read_text(encoding='utf-8', errors='replace')
    required = (
        '[FEY AUDIT] Habitat coverage: species=18',
        ' missing=0',
        '[FEY AUDIT] Creature construction: created=18 expected=18 mismatches=0',
        '[FEY AUDIT] COMPLETE habitat_missing=0 creature_mismatches=0',
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
