"""Survey, naturally populate and open loot in multiple islands; never uses /place."""
import argparse,hashlib,json,re,time
from pathlib import Path
import run_server,nbt
from probe_terraces import chunks,section_blocks

ROOT=Path(__file__).resolve().parents[1]
WORLD=time.strftime('validation-fairy-islands-%Y%m%d-%H%M%S');SEED='-5876049240305171930'
HOME='execute in mythicbotany:alfheim '
REPORT=ROOT/'tools/fairy_island_runtime_report.json'


class Plan:
    def __init__(self):
        self.expanded=False;self.sites=[]
        self.commands=[(1,'gamerule doMobSpawning false'),(0,'gamerule randomTickSpeed 0')]
    def __iter__(self):return iter(self.commands) if self.expanded else self.expand()
    def expand(self):
        yield from self.commands
        self.expanded=True
        queries=[(-12,-4),(-12,4)]+[(x,z) for x in (-12,-4,4,12) for z in (-12,-4,4,12) if (x,z) not in ((-12,-4),(-12,4))]
        candidates=[]
        for x,z in queries:
            command=(1,HOME+f'run alfheim_fairy_islands_audit {x} {z}')
            self.commands.append(command);yield command
            deadline=time.monotonic()+90
            while True:
                console=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
                log=console.read_text(encoding='utf-8',errors='replace')
                if f'FAIRY_SURVEY region={x},{z} ' in log:break
                if time.monotonic()>deadline:raise RuntimeError('Fairy survey did not finish')
                time.sleep(.25)
            candidates=[dict(season=s,x=int(px),z=int(pz)) for s,px,pz in re.findall(r'FAIRY_SITE season=(\w+) x=(-?\d+) z=(-?\d+)',log)]
            if len(candidates)>=2:break
        if len(candidates)>=2:
            self.sites=[candidates[0],next((s for s in candidates[1:] if s['season']!=candidates[0]['season']),candidates[1])]
        extra=[]
        for site in self.sites:
            x,z=site['x'],site['z']
            extra += [(1,HOME+f'run forceload add {x-48} {z-48} {x+63} {z+63}'),(25,'save-all flush'),
                (1,HOME+f'run alfheim_fairy_islands_loot {x} {z}'),(2,'save-all flush'),
                (1,HOME+'run forceload remove all')]
        extra += [(1,'stop')];self.commands.extend(extra);yield from extra


def verify(report):
    world=report['world'];sites=report['sites'];log=(ROOT/'server'/report['console']).read_text(encoding='utf-8',errors='replace')
    loot=[json.loads(s) for s in re.findall(r'FAIRY_LOOT_RESULT (\{[^\n]+\})',log)]
    assert len(sites)==2 and len(loot)==2,(sites,report['survey'])
    region=ROOT/'server'/world/'dimensions/mythicbotany/alfheim/region';grid={};cache={};be={}
    required={(s['x']//16+dx,s['z']//16+dz) for s in sites for dx in range(-3,4) for dz in range(-3,4)}
    for rx,rz in sorted({(x//32,z//32) for x,z in required}):
        for c in chunks(region/f'r.{rx}.{rz}.mca'):
            key=int(c['xPos']),int(c['zPos'])
            if key not in required:continue
            grid[key]=c
            for entity in c.get('block_entities',[]):be[int(entity['x']),int(entity['y']),int(entity['z'])]=entity
    def block(p):
        x,y,z=p;key=x//16,y//16,z//16
        if key not in cache:
            sec=next((s for s in grid.get((x//16,z//16),{}).get('sections',[]) if int(s['Y'])==y//16),None)
            cache[key]=section_blocks(sec) if sec else None
        return cache[key][((y&15)<<8)|((z&15)<<4)|(x&15)] if cache[key] else None
    proofs=[];seeds=[];fingerprints=[]
    for site in sites:
        start=grid[site['x']//16,site['z']//16]['structures']['starts'].get('alfheim:pixie_'+site['season']+'_hamlet')
        assert start and start.get('id')!='INVALID' and len(start['Children'])==4,site
        pieces=[]
        homes=0
        for piece in start['Children']:
            location=piece['pool_element']['location'];template=nbt.load(ROOT/f'kubejs/data/alfheim/structures/{location.split(":",1)[1]}.nbt')[1]
            origin=[int(piece['Pos'+a]) for a in ('X','Y','Z')]
            solid=[b for b in template['blocks'] if template['palette'][int(b['state'])]['Name'] not in ('minecraft:air','minecraft:structure_void')]
            sample=solid[::max(1,len(solid)//200)];matched=0
            for cell in sample:
                p=tuple(origin[i]+int(cell['pos'][i]) for i in range(3))
                matched+=block(p)==template['palette'][int(cell['state'])]['Name']
            assert matched/len(sample)>=.98,(site,location,matched,len(sample))
            for cell in template['blocks']:
                name=template['palette'][int(cell['state'])]['Name']
                if not name.endswith('_fey_apartment'):continue
                p=tuple(origin[i]+int(cell['pos'][i]) for i in range(3))
                assert block(p)==name and be.get(p,{}).get('id')=='alfheim_companion:fey_home',(site,p,name)
                homes+=1
            pieces.append(dict(template=location,sampled=len(sample),matched=matched))
        opened=next(r for r in loot if r['x']==site['x'] and r['z']==site['z'])['containers']
        assert len(opened)==(14 if site['season']=='autumn' else 10),(site,len(opened))
        for barrel in opened:
            assert barrel['seed']!=0 and barrel['items'],barrel
            seeds.append(barrel['seed']);fingerprints.append(sorted((i['item'],i['count']) for i in barrel['items']))
            saved=be[barrel['x'],barrel['y'],barrel['z']]
            assert 'LootTable' not in saved and saved.get('Items'),saved
            actual=sorted((int(i['Slot']),str(i['id']),int(i['Count'])) for i in saved['Items'])
            expected=sorted((i['slot'],i['item'],i['count']) for i in barrel['items'])
            assert actual==expected,(barrel,actual)
        assert homes>=6,(site,homes)
        proofs.append(dict(**site,pieces=pieces,containers=len(opened),registered_homes=homes,saved_loot_verified=True))
    assert len(set(seeds))==len(seeds),'Repeated fixed loot seed'
    assert len({json.dumps(x) for x in fingerprints})>1,'Loot inventories did not vary'
    distance=((sites[0]['x']-sites[1]['x'])**2+(sites[0]['z']-sites[1]['z'])**2)**.5
    assert distance-96>=500,distance
    report.update(status='MULTIPLE_NATURAL_ISLANDS_AND_RANDOMIZED_SAVED_LOOT_VERIFIED',proofs=proofs,
        unique_loot_seeds=len(set(seeds)),unique_inventories=len({json.dumps(x) for x in fingerprints}),
        opened_loot=loot,inter_island_center_distance=distance,client_visual_review='pending')
    REPORT.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('FAIRY ISLAND PASS:',[(s['season'],s['x'],s['z'],s['containers']) for s in proofs],report['unique_inventories'],'different inventories')


def main():
    global WORLD
    ap=argparse.ArgumentParser();ap.add_argument('--verify-only',action='store_true');ap.add_argument('--world',default=WORLD);args=ap.parse_args()
    WORLD=args.world
    assert WORLD.startswith('validation-fairy-islands-') and Path(WORLD).name==WORLD
    if args.verify_only:return verify(json.loads(REPORT.read_text()))
    server=(ROOT/'server').resolve();assert not (server/WORLD).exists(),'Fresh world required'
    for name in run_server.MIRROR:
        target=(server/name).resolve();assert target.is_relative_to(server) and target!=server
    props=server/'server.properties';old=props.read_bytes();before=set(server.glob('console-*.log'));plan=Plan()
    try:code=run_server.run(SEED,WORLD,8,plan,600)
    finally:props.write_bytes(old)
    console=max(set(server.glob('console-*.log'))-before,key=lambda p:p.stat().st_mtime)
    log=console.read_text(encoding='utf-8',errors='replace')
    report=dict(world=WORLD,seed=SEED,console=console.name,exit_code=code,sites=plan.sites,
        survey=[s for s in log.splitlines() if 'FAIRY_SURVEY ' in s or 'FAIRY_SITE ' in s],
        jar_sha256=hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest(),status='SURVEY_OR_POPULATION_PENDING_VERIFICATION')
    REPORT.write_bytes((json.dumps(report,indent=2)+'\n').encode());assert code==0
    verify(report)

if __name__=='__main__':main()
