"""Source equality, registered materials, water containment and supported circulation."""
from collections import Counter,deque
import json,re,hashlib
from pathlib import Path
import nbt
import gen_sacred_precinct as gen
from check_civic_center import topology
from check_ancient_assembly import STEP

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'kubejs/data/alfheim/structures/ancient/sacred_precinct'

def main():
    compare=ROOT/'build/sacred-precinct-equality';files=gen.generate(compare);assert len(files)==18
    registry=set(json.loads((ROOT/'server/local/kubejs/export/registries/block.json').read_text(encoding='utf-8')))
    for script in (ROOT/'kubejs/startup_scripts').glob('*.js'):
        text=script.read_text(encoding='utf-8')
        if "registry('block'" in text:registry.update(re.findall(r"event\.create\(['\"]([^'\"]+)['\"]",text))
    counts=Counter();cultural=0;fingerprint=hashlib.sha256()
    for twin in files:
        path=ROOT/twin.relative_to(compare)
        fingerprint.update(str(path.relative_to(ROOT)).replace('\\','/').encode('utf-8'))
        if path.suffix!='.nbt':
            assert path.read_bytes()==twin.read_bytes();fingerprint.update(path.read_bytes());continue
        p=nbt.load(str(path))[1];assert p==nbt.load(str(twin))[1]
        fingerprint.update(json.dumps(p,sort_keys=True,separators=(',',':')).encode('utf-8'))
        assert p['entities']==[] and max(map(int,p['size']))<=48
        assert {s['Name'] for s in p['palette']}<=registry
        cells={tuple(map(int,b['pos'])):p['palette'][int(b['state'])]['Name'] for b in p['blocks']}
        ports=[tuple(map(int,b['pos'])) for b in p['blocks'] if b.get('nbt',{}).get('id')=='minecraft:jigsaw']
        def walkable(point):
            x,y,z=point
            return cells.get(point) in ('minecraft:air','minecraft:jigsaw') and cells.get((x,y+1,z))=='minecraft:air' and cells.get((x,y-1,z)) not in (None,'minecraft:air','minecraft:water')
        pending=deque(ports[:1]);seen=set()
        while pending:
            point=pending.popleft()
            if point in seen or not walkable(point):continue
            seen.add(point);x,y,z=point;pending.extend((x+dx,y,z+dz) for dx,dz in STEP.values())
        assert set(ports)<=seen,('disconnected walking network',path)
        for point,name in cells.items():
            counts[name]+=1
            if name=='minecraft:gravel':
                x,y,z=point;assert cells.get((x,y-1,z)) not in (None,'minecraft:air','minecraft:water'),('unsettled gravel',path,point)
            if name.startswith(('alfheim:royal_','alfheim:elder_')):cultural+=1
            if (name.startswith('alfheim:royal_') and name!='alfheim:royal_wall_banner') or name=='minecraft:barrel':
                x,y,z=point;assert cells.get((x,y-1,z)) not in (None,'minecraft:air','minecraft:water'),('unsupported furnishing',path,point,name)
        if path.stem=='ancestor_reflection_pool':
            for x0,x1 in ((5,10),(20,25)):
                for x in range(x0,x1+1):
                    for z in range(8,20):
                        assert cells[x,5,z] not in ('minecraft:air','minecraft:water')
                        assert cells[x,6,z]==cells[x,7,z]=='minecraft:water'
                for y in (6,7):
                    for z in range(8,20):
                        assert all(cells[x,y,z] not in ('minecraft:air','minecraft:water') for x in (x0-1,x1+1))
                    for x in range(x0,x1+1):
                        assert all(cells[x,y,z] not in ('minecraft:air','minecraft:water') for z in (7,20))
    layout,joins=topology(PATH,'great_temple_court');assert len(layout)==7 and len(joins)==6
    for i,a in enumerate(layout):
        for b in layout[i+1:]:assert not all(max(a['bounds'][j],b['bounds'][j])<=min(a['bounds'][j+3],b['bounds'][j+3]) for j in range(3)),(a,b)
    assert counts['minecraft:water']==288 and counts['minecraft:oak_fence']==48
    assert counts['minecraft:lantern']+counts['minecraft:soul_lantern']==0
    assert cultural>=20 and counts['minecraft:white_bed']>=16
    assert not (ROOT/'kubejs/data/alfheim/worldgen/structure_set/sacred_precinct.json').exists()
    assert all(max(abs(p['bounds'][0]-23),abs(p['bounds'][3]-23),abs(p['bounds'][2]-23),abs(p['bounds'][5]-23))<=116 for p in layout)
    source_fingerprint=fingerprint.hexdigest();runtime_path=ROOT/'tools/sacred_precinct_runtime.json'
    runtime=json.loads(runtime_path.read_text(encoding='utf-8')) if runtime_path.exists() else {}
    verified=runtime.get('source_fingerprint')==source_fingerprint and runtime.get('validation_exit_code')==0
    result={'status':'runtime_validated_visual_pending' if verified else 'static_validated_runtime_pending','source_fingerprint':source_fingerprint,
        'files':18,'members':7,'joins':6,'cultural_modules':cultural,'layout':layout,'block_counts':dict(counts)}
    (ROOT/'tools/sacred_precinct_manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('SACRED PRECINCT STATIC PASS: 18 source-equal files, 7 members, 6 walking connections,',cultural,'cultural modules; contained pools')

if __name__=='__main__':main()
