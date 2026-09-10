"""Fresh, retained world with a real Golden Fields patch generated in it.

B-86 needed this and did it by hand: `locate` reports Golden Fields ~1,300 blocks from spawn,
the spawn area contains none of it, and the first terrace probe came back "no golden_fields
chunks generated". The coordinates were then pasted into `run_server.py --forceload` by a human.
This closes that loop -- the server locates the biomes itself and forceloads around what it
found, so the measurement always reads the patch it meant to read.

Silverbark Wood is located and loaded alongside Golden Fields deliberately. The two share the
whole of continentalness and overlap in weirdness; temperature is the only climate field that
separates them, and the terrace weight had no temperature term until 2026-09-09. A probe that
loads only Golden Fields cannot see the terracing cross the boundary, which is how it shipped.

    python tools/run_terrace_validation.py
    python tools/probe_terraces.py server/<world>/dimensions/mythicbotany/alfheim/region

TREATMENT AND BASELINE, because a cross-biome comparison cannot answer the question. The deep
void share under Golden Fields was 42.2% in the world the field review rejected and 3.4% after
the repair -- but those are different seeds, and a biome whose surface sits at Y 91 has a very
different deep band from one at Y 63. Only the same seed with the terrace addend removed
isolates what the terracing itself does.

    python tools/run_terrace_validation.py --mode treatment
    python tools/run_terrace_validation.py --mode baseline
    python tools/probe_terraces.py server/<world>/dimensions/mythicbotany/alfheim/region --deep

`--mode baseline` rewrites the density function in the SERVER MIRROR only, from
`void_final_density(include_terraces=False)`. The source tree is never touched, and the mirror
is rebuilt from it on the next run.

Never touches a player save: each run gets its own timestamped world directory.
"""
from pathlib import Path
import argparse
import json
import re
import subprocess
import time

import run_server

HOME = 'mythicbotany:alfheim'
# Golden Fields is the target; Silverbark Wood is the containment control.
TARGETS = ['mythicbotany:golden_fields', 'alfheim:silverbark_wood']
# `locate biome` prints the resolved height, not a tilde: "is at [-64, 100, 0]". Matching
# on `~` silently found nothing and the forceload never fired.
LOCATE = re.compile(r'The nearest (\S+) is at \[(-?\d+), (?:~|-?\d+), (-?\d+)\]')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['treatment', 'baseline'], default='treatment')
    ap.add_argument('--seed', default='alfheim-terrace-20260909')
    ap.add_argument('--radius', type=int, default=384,
                    help='half-width in blocks of the patch generated around each biome')
    ap.add_argument('--timeout', type=int, default=1500)
    a = ap.parse_args()

    root = Path.cwd().resolve()
    server = root / 'server'
    assert 'eula=true' in (server / 'eula.txt').read_text().lower()
    assert not run_server.running_servers(), 'Validation server already running'
    run_server.mirror_instance()

    if a.mode == 'baseline':
        # Mirror only. gen_alfheim_biomes owns the source; this is the same
        # untouched-density expression with the terrace addend never appended.
        from gen_alfheim_biomes import void_final_density
        target = (server / 'kubejs/data/mythicbotany/worldgen/density_function'
                         / 'alfheim_final.json')
        target.write_text(json.dumps(void_final_density(include_terraces=False), indent=2) + '\n', newline='\n')
        print('  baseline: terrace addend removed from the server mirror', flush=True)

    prop = server / 'server.properties'
    old = prop.read_bytes()
    stamp = time.strftime('%Y%m%d-%H%M%S')
    world = 'terrace-' + a.mode + '-' + stamp
    assert not (server / world).exists()
    run_server.write_properties(a.seed, world)
    path = server / (world + '.log')

    found, requested, stopped = {}, False, False
    try:
        with path.open('w', encoding='utf-8', newline='\n') as log:
            process = subprocess.Popen(
                [run_server.JAVA17, '-Xmx6G', '-Xms4G',
                 '@libraries/net/minecraftforge/forge/1.20.1-47.4.10/win_args.txt', 'nogui'],
                cwd=server, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT, text=True)
            print('Console:', path, flush=True)
            deadline = time.monotonic() + a.timeout
            asked = False
            while process.poll() is None and time.monotonic() < deadline:
                content = path.read_text(encoding='utf-8', errors='replace')
                if 'Failed to start the minecraft server' in content:
                    process.terminate(); process.wait(timeout=20); break

                if not asked and 'Done (' in content:
                    for biome in TARGETS:
                        process.stdin.write(
                            f'execute in {HOME} positioned 0 100 0 run locate biome {biome}\n')
                    process.stdin.flush()
                    asked = True

                for m in LOCATE.finditer(content):
                    found.setdefault(m.group(1), (int(m.group(2)), int(m.group(3))))

                if asked and not requested and len(found) == len(TARGETS):
                    for biome, (x, z) in found.items():
                        print(f'  {biome:34s} at {x}, {z}', flush=True)
                        # forceload takes at most a 256x256 block square per call.
                        for bx in range(x - a.radius, x + a.radius, 128):
                            for bz in range(z - a.radius, z + a.radius, 128):
                                process.stdin.write(
                                    f'execute in {HOME} run forceload add '
                                    f'{bx} {bz} {bx + 127} {bz + 127}\n')
                    process.stdin.write('save-all flush\n')
                    process.stdin.flush()
                    requested = True
                    settle = time.monotonic() + 240

                if requested and not stopped and time.monotonic() > settle:
                    process.stdin.write(f'execute in {HOME} run forceload remove all\n'
                                        'save-all flush\nstop\n')
                    process.stdin.flush()
                    stopped = True
                time.sleep(1)

            if process.poll() is None:
                process.stdin.write('stop\n'); process.stdin.flush()
                try:
                    process.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    process.terminate(); process.wait(timeout=20)
    finally:
        prop.write_bytes(old)

    ok = process.returncode == 0 and len(found) == len(TARGETS)
    print('exit=', process.returncode, 'located=', len(found), 'of', len(TARGETS), flush=True)
    print('world=', server / world, flush=True)
    raise SystemExit(0 if ok else 1)


if __name__ == '__main__':
    main()
