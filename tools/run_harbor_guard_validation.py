"""Installed checked placement on a synthetic coast; never edits player saves."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import run_server

ROOT=Path(__file__).resolve().parents[1]
HOME='mythicbotany:alfheim'
WORLD='validation-harbor-guard-20261012'

def main():
    global WORLD
    ap=argparse.ArgumentParser();ap.add_argument('--world',default=WORLD);ap.add_argument('--repair',action='store_true');ap.add_argument('--raised',action='store_true');args=ap.parse_args();WORLD=args.world
    if args.raised:WORLD='validation-harbor-raised-quay-20261013'
    assert WORLD.startswith('validation-harbor-') and (ROOT/'server'/WORLD).resolve().parent==(ROOT/'server').resolve(), 'only a disposable harbor validation world is allowed'
    commands=[(100,'say harbor guard startup')]
    for x in (-1600,-1440):
        for z in (496,656):commands.append((2,f'execute in {HOME} run forceload add {x} {z} {x+159} {z+159}'))
    def add(command,delay=5):commands.append((delay,f'execute in {HOME} run {command}'))
    add('alfheimharbor audit -1440 656',20 if args.repair else 60)
    add('gamerule commandModificationBlockLimit 12000000',2)
    if not args.repair:
        add('fill -1520 65 584 -1330 319 768 minecraft:air',15)
        add(f'fill -1520 56 656 -1330 {68 if args.raised else 64} 768 minecraft:stone',10)
    else:
        assert (ROOT/'server'/WORLD).exists(), 'repair requires the disposable fixture world'
    add('fill -1520 56 584 -1330 57 655 minecraft:stone',2 if args.repair else 15)
    add('fill -1520 58 584 -1330 63 655 minecraft:water',2 if args.repair else 10)
    add('fill -1520 64 584 -1330 64 655 minecraft:air',2)
    add('alfheimharbor audit -1440 656',5 if args.repair else 10)
    # Single high column between coarse probes must invalidate the entire placement.
    add('setblock -1428 85 668 minecraft:stone',2)
    add('alfheimharbor audit -1440 656',2)
    add('setblock -1428 85 668 minecraft:air',2)
    add('alfheimharbor place_checked -1440 656',2)
    commands += [(35,'save-all flush'),(5,f'execute in {HOME} run forceload remove all'),(5,'stop')]
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run('3536368297089363045',WORLD,8,commands,480)
    finally:props.write_bytes(original)
    if code:return code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    expected_quay=68 if args.raised else 66
    assert f'Harbor accepted: rotation=0 quay={expected_quay}' in text,log
    assert f'Harbor placed: rotation=0 quay={expected_quay}' in text,log
    assert text.count('Harbor rejected:')>=2,log
    assert 'All dimensions are saved' in text,log
    subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/check_ancient_assembly.py'),str(ROOT/'server'/WORLD),'--family','harbor_complex'],check=True)
    (ROOT/'tools/harbor_guard_runtime.json').write_text(json.dumps({'world':WORLD,'console':str(log.relative_to(ROOT)),'synthetic_coast_accepted':True,'single_column_cliff_rejected':True,'pre_repair_site_rejected':True,'checked_assembly_pass':True,'natural_coast_acceptance':'pending','quay_height':expected_quay,'raised_foundations':args.raised},indent=2)+'\n',encoding='utf-8')
    print('HARBOR GUARD RUNTIME PASS:',log.name)
    return 0

if __name__=='__main__':sys.exit(main())
