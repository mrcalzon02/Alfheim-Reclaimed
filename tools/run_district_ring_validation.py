"""Native ring discovery, creature items and natural block census in a fresh world."""
import hashlib,json,re,time
from pathlib import Path
import run_server
import nbt
from probe_terraces import chunks,section_blocks

ROOT=Path(__file__).resolve().parents[1]
WORLD='validation-test-run-rings-20261017'
SEED='-5876049240305171930'
HOME='execute in mythicbotany:alfheim '


class Plan:
    def __init__(self):
        self.sites=[];self.expanded=False
        self.commands=[(1,'gamerule doMobSpawning false'),(0,'gamerule randomTickSpeed 0'),
            (0,'difficulty hard'),(0,'gamerule doDaylightCycle false'),(0,HOME+'run time set midnight'),
            (0,HOME+'run forceload add 480 480 495 495'),
            (2,HOME+'run fill 480 219 480 495 227 495 minecraft:stone'),
            (1,HOME+'run fill 481 220 481 494 226 494 minecraft:air'),
            (2,HOME+'positioned 488 220 488 run alfheim_enemies_audit items'),
            (1,HOME+'positioned 488 220 488 run alfheim_society_audit'),
            (1,HOME+'positioned 488 220 488 run alfheim_monstrosities_audit'),
            (1,HOME+'run forceload remove all'),
            (1,HOME+'run alfheim_district_rings_audit')]
    def __iter__(self):
        if self.expanded:return iter(self.commands)
        return self.expand()
    def expand(self):
        yield from self.commands
        deadline=time.monotonic()+60
        while True:
            console=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
            log=console.read_text(encoding='utf-8',errors='replace')
            if 'DISTRICT_RING_AUDIT_PASS' in log:break
            if time.monotonic()>deadline:raise RuntimeError('Native district ring audit did not finish')
            time.sleep(.25)
        candidates=[dict(ring=int(r),slot=int(s),family=f,x=int(x),z=int(z)) for r,s,f,x,z in re.findall(
            r'DISTRICT_RING_SITE ring=(\d+) slot=(\d+) family=(alfheim:\w+) x=(-?\d+) z=(-?\d+) viable=true',log)]
        for ring in (1,2,3):
            site=next((s for s in candidates if s['ring']==ring),None)
            assert site is not None,('No viable site on requested ring',ring,candidates)
            self.sites.append(site)
        extra=[(0,HOME+'positioned 0 100 0 run locate structure #alfheim:districts')]
        for site in self.sites:
            x,z=site['x'],site['z']
            extra.extend([(1,HOME+f'run forceload add {x-128} {z-128} {x+127} {z+127}'),
                          (45,'save-all flush'),(1,HOME+'run forceload remove all')])
        extra.extend([(2,'stop')]);self.commands.extend(extra);self.expanded=True
        yield from extra


def verify(world,sites):
    required={(s['x']//16+dx,s['z']//16+dz) for s in sites for dx in range(-8,8) for dz in range(-8,8)}
    region=ROOT/'server'/world/'dimensions/mythicbotany/alfheim/region';grid={};cache={}
    for rx,rz in sorted({(x//32,z//32) for x,z in required}):
        for c in chunks(region/f'r.{rx}.{rz}.mca'):
            key=int(c['xPos']),int(c['zPos'])
            if key in required:grid[key]=c
    def block(p):
        x,y,z=p;key=x//16,y//16,z//16
        if key not in cache:
            sec=next((s for s in grid.get((x//16,z//16),{}).get('sections',[]) if int(s['Y'])==y//16),None)
            cache[key]=section_blocks(sec) if sec else None
        data=cache[key]
        return data[((y&15)<<8)|((z&15)<<4)|(x&15)] if data else None
    proofs=[]
    for site in sites:
        start=grid[site['x']//16,site['z']//16]['structures']['starts'].get(site['family'])
        assert start and start.get('id')!='INVALID',site
        cells=[];owners={};pieces=[]
        for index,piece in enumerate(start['Children']):
            location=piece['pool_element']['location'];template=nbt.load(ROOT/f'kubejs/data/alfheim/structures/{location.split(":",1)[1]}.nbt')[1]
            origin=[int(piece['Pos'+a]) for a in ('X','Y','Z')]
            rotation=['NONE','CLOCKWISE_90','CLOCKWISE_180','COUNTERCLOCKWISE_90'].index(piece['rotation'])
            own=[]
            for cell in template['blocks']:
                name=template['palette'][int(cell['state'])]['Name']
                if name=='minecraft:structure_void':continue
                x,y,z=map(int,cell['pos'])
                for _ in range(rotation):x,z=-z,x
                p=(origin[0]+x,origin[1]+y,origin[2]+z);owners[p]=index
                if name not in ('minecraft:air','minecraft:cave_air','minecraft:jigsaw'):own.append((p,name))
            cells.append(own);pieces.append(dict(template=location,bounds=list(map(int,piece['BB']))))
        for index,(own,piece) in enumerate(zip(cells,pieces)):
            # Joined templates intentionally overlap; later pieces own those cells.
            exposed=[(p,name) for p,name in own if owners[p]==index]
            sample=exposed[::max(1,len(exposed)//150)]
            matched=sum(block(p)==name for p,name in sample)
            assert sample and matched/len(sample)>=.95,(site,piece,matched,len(sample))
            piece.update(sampled=len(sample),matched=matched)
        assert len(pieces)>1,site
        proofs.append(dict(**site,radius=round((site['x']**2+site['z']**2)**.5,2),pieces=pieces))
    return proofs


def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--verify-only',action='store_true');args=ap.parse_args()
    server=(ROOT/'server').resolve();report_path=ROOT/'tools/district_ring_runtime_report.json'
    if args.verify_only:
        report=json.loads(report_path.read_text());console=server/report['console'];sites=report['sites'];code=report['exit_code']
    else:
        assert not (server/WORLD).exists(),'Use a fresh disposable world'
        for name in run_server.MIRROR:
            target=(server/name).resolve();assert target.is_relative_to(server) and target!=server
        plan=Plan();props=server/'server.properties';old=props.read_bytes();before=set(server.glob('console-*.log'))
        try:code=run_server.run(SEED,WORLD,8,plan,600)
        finally:props.write_bytes(old)
        console=max(set(server.glob('console-*.log'))-before,key=lambda p:p.stat().st_mtime);sites=plan.sites
        report=dict(world=WORLD,seed=SEED,console=console.name,sites=sites,exit_code=code,status='PENDING_CENSUS')
        report_path.write_text(json.dumps(report,indent=2)+'\n')
    log=console.read_text(encoding='utf-8',errors='replace')
    assert code==0
    for marker in ('ALFHEIM_ENEMY_ITEMS_PASS','ALFHEIM_SOCIETY_PASS','ALFHEIM_MONSTROSITIES_PASS','DISTRICT_RING_AUDIT_PASS'):
        assert marker in log,marker
    report['proofs']=verify(WORLD,sites)
    report.update(status='NATURAL_RINGS_AND_CREATURE_ITEMS_VERIFIED',jar_sha256=hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest(),
        evidence=[s for s in log.splitlines() if any(m in s for m in ('ALFHEIM_ENEMY_ITEMS_PASS','ALFHEIM_SOCIETY_PASS','ALFHEIM_MONSTROSITIES_PASS','DISTRICT_RING_','The nearest #alfheim:districts'))],
        client_visual_review='pending full restart; existing map cache may require remapping')
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('RING RUNTIME PASS:',[(p['ring'],p['family'],p['radius'],len(p['pieces'])) for p in report['proofs']])

if __name__=='__main__':main()
