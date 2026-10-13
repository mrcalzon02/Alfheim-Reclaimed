"""Bounded, player-save-independent assembly probe for the residential quarter."""
from pathlib import Path
import sys
import argparse
import run_server

ROOT=Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--world',default='validation-residential-quarter-final-20261012');args=ap.parse_args()
    home='mythicbotany:alfheim'
    commands=[(100,'say residential district startup check')]
    for x in (-1600,-1440):
        for z in (496,656):
            commands.append((2,f'execute in {home} run forceload add {x} {z} {x+159} {z+159}'))
    commands += [(60,f'execute in {home} run place structure alfheim:common_residential_quarter -1443 80 654'),
                 (35,'save-all flush'),(5,f'execute in {home} run forceload remove all'),(5,'stop')]
    properties=ROOT/'server/server.properties'
    original=properties.read_bytes()
    try:
        code=run_server.run('3536368297089363045',args.world,8,commands,300)
    finally:properties.write_bytes(original)
    if code:return code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    assert 'Generated structure "alfheim:common_residential_quarter"' in text,log
    assert 'All dimensions are saved' in text,log
    assert 'Errors in currently selected datapacks' not in text
    import subprocess
    subprocess.run([sys.executable,'-B',str(ROOT/'tools/check_ancient_assembly.py'),
                    str(ROOT/'server'/args.world)],check=True)
    print(f'ASSEMBLY VALIDATED AND SAVED: {log.name}')
    return 0


if __name__=='__main__':sys.exit(main())
