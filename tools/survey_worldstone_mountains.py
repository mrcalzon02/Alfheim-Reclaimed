"""Measure current mountain heights in an isolated world without changing density."""
import hashlib,json,re,time
from pathlib import Path
import run_server

ROOT=Path(__file__).resolve().parents[1]
SEED='-5876049240305171930'


def main():
    world=time.strftime('validation-worldstone-mountains-%Y%m%d-%H%M%S')
    server=(ROOT/'server').resolve()
    for name in run_server.MIRROR:
        target=(server/name).resolve();assert target.is_relative_to(server) and target!=server
    assert not (server/world).exists()
    props=server/'server.properties';old=props.read_bytes();before=set(server.glob('console-*.log'))
    commands=[(1,f'execute in mythicbotany:alfheim run alfheim_worldstone_mountains {x} {z}')
              for x in (-4,-2,0,2) for z in (-4,-2,0,2)]+[(1,'stop')]
    try:code=run_server.run(SEED,world,8,commands,600)
    finally:props.write_bytes(old)
    console=max(set(server.glob('console-*.log'))-before,key=lambda p:p.stat().st_mtime)
    log=console.read_text(encoding='utf-8',errors='replace')
    peaks=[dict(x=int(x),z=int(z),y=int(y),biome=b) for x,z,y,b in re.findall(r'WORLDSTONE_PEAK x=(-?\d+) z=(-?\d+) y=(\d+) biome=([\w:]+)',log)]
    report=dict(world=world,seed=SEED,exit_code=code,console=console.name,
                jar_sha256=hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest(),
                summaries=re.findall(r'WORLDSTONE_MOUNTAINS [^\n]+',log),peaks=sorted(peaks,key=lambda p:-p['y']))
    (ROOT/'tools/worldstone_mountain_survey.json').write_text(json.dumps(report,indent=2)+'\n')
    assert code==0 and report['summaries']
    print('Mountain survey:',len(peaks),'samples >=180; highest:',report['peaks'][:8])


if __name__=='__main__':main()
