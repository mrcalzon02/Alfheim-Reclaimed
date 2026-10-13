"""Controlled fresh-world civic placement and a saved-member census."""
import argparse
from pathlib import Path
import subprocess
import sys
import run_server

ROOT=Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--world',default='validation-civic-center-20261012');args=ap.parse_args()
    home='mythicbotany:alfheim';commands=[(100,'say civic center startup check')]
    for x in (-1600,-1440):
        for z in (496,656):commands.append((2,f'execute in {home} run forceload add {x} {z} {x+159} {z+159}'))
    commands += [(60,f'execute in {home} run place structure alfheim:civic_center -1443 80 654'),
                 (35,'save-all flush'),(5,f'execute in {home} run forceload remove all'),(5,'stop')]
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run('3536368297089363045',args.world,8,commands,300)
    finally:props.write_bytes(original)
    if code:return code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    assert 'Generated structure "alfheim:civic_center"' in text,log
    assert 'All dimensions are saved' in text,log
    subprocess.run([sys.executable,'-B',str(ROOT/'tools/check_ancient_assembly.py'),
                    str(ROOT/'server'/args.world),'--family','civic_center'],check=True)
    print(f'CIVIC CENTER RUNTIME PASS: {log.name}')
    return 0


if __name__=='__main__':sys.exit(main())
