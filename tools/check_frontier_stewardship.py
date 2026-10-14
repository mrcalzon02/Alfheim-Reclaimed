"""Check source equality, connected routes, foundations and frontier waterworks."""
from collections import Counter,deque
import hashlib,json,re
from pathlib import Path
import nbt
import gen_frontier_stewardship as gen
from check_civic_center import topology
from check_ancient_assembly import STEP

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'kubejs/data/alfheim/structures/ancient/frontier_stewardship'

def main():
    compare=ROOT/'build/frontier-stewardship-equality';files=gen.generate(compare);assert len(files)==16
    registry=set(json.loads((ROOT/'server/local/kubejs/export/registries/block.json').read_text(encoding='utf-8')))
    for script in (ROOT/'kubejs/startup_scripts').glob('*.js'):
        text=script.read_text(encoding='utf-8')
        if "registry('block'" in text:registry.update(re.findall(r"event\.create\(['\"]([^'\"]+)['\"]",text))
    counts=Counter();fingerprint=hashlib.sha256()
    for twin in files:
        path=ROOT/twin.relative_to(compare);fingerprint.update(path.relative_to(ROOT).as_posix().encode())
        if path.suffix!='.nbt':
            assert path.read_bytes()==twin.read_bytes();fingerprint.update(path.read_bytes());continue
        p=nbt.load(str(path))[1];assert p==nbt.load(str(twin))[1]
        fingerprint.update(json.dumps(p,sort_keys=True,separators=(',',':')).encode())
        assert p['entities']==[] and max(map(int,p['size']))<=48
        assert {s['Name'] for s in p['palette']}<=registry,(path,{s['Name'] for s in p['palette']}-registry)
        cells={tuple(map(int,b['pos'])):p['palette'][int(b['state'])] for b in p['blocks']}
        ports=[tuple(map(int,b['pos'])) for b in p['blocks'] if b.get('nbt',{}).get('id')=='minecraft:jigsaw']
        def name(point):return cells.get(point,{}).get('Name')
        def walkable(point):
            x,y,z=point
            return name(point) in ('minecraft:air','minecraft:jigsaw') and name((x,y+1,z))=='minecraft:air' and name((x,y-1,z)) not in (None,'minecraft:air','minecraft:water')
        pending=deque(ports[:1]);seen=set()
        while pending:
            point=pending.popleft()
            if point in seen or not walkable(point):continue
            seen.add(point);x,y,z=point;pending.extend((x+dx,y,z+dz) for dx,dz in STEP.values())
        assert set(ports)<=seen,('blocked join',path)
        for point,state in cells.items():
            block=state['Name'];counts[block]+=1;x,y,z=point
            if y<8 and not (path.stem=='moon_pool_sanctuary' and y in (6,7)):assert block not in ('minecraft:air','minecraft:water')
            if block.startswith('alfheim:royal_') and block!='alfheim:royal_wall_banner' or block=='minecraft:barrel':
                assert name((x,y-1,z)) not in (None,'minecraft:air','minecraft:water'),('unsupported fixture',path,point)
            if block.endswith('_bed'):assert name((x,y-1,z)) not in (None,'minecraft:air','minecraft:water')
        if path.stem=='surveyor_tower':
            for k in range(14):assert name((5,9+k,7+k))=='alfheim:ivory_livingrock_stairs'
            assert name((5,23,21))!='minecraft:air'
        if path.stem=='surveyor_tower':
            # Test the whole approach, not just whether stair blocks exist.
            target=(5,24,22)
            queue=deque(ports[:1]);reachable=set()
            while queue:
                point=queue.popleft()
                if point in reachable or not walkable(point):continue
                reachable.add(point);x,y,z=point
                for dx,dz in STEP.values():
                    for dy in (-1,0,1):queue.append((x+dx,y+dy,z+dz))
            assert target in reachable,('upper platform cannot be reached',path)
        if path.stem=='moon_pool_sanctuary':
            for x0,x1 in ((6,12),(26,32)):
                for x in range(x0,x1+1):
                    for z in range(11,28):
                        assert name((x,5,z)) not in (None,'minecraft:air','minecraft:water')
                        assert name((x,6,z))==name((x,7,z))=='minecraft:water'
                        assert name((x,8,z))=='minecraft:air'
                for y in (6,7):
                    for z in range(11,28):assert all(name((x,y,z)) not in (None,'minecraft:air','minecraft:water') for x in (x0-1,x1+1))
                    for x in range(x0,x1+1):assert all(name((x,y,z)) not in (None,'minecraft:air','minecraft:water') for z in (10,28))
    layout,joins=topology(PATH,'green_noble_lodge');assert len(layout)==6 and len(joins)==5
    for i,a in enumerate(layout):
        for b in layout[i+1:]:assert not all(max(a['bounds'][j],b['bounds'][j])<=min(a['bounds'][j+3],b['bounds'][j+3]) for j in range(3)),(a,b)
    assert all(max(abs(n['bounds'][0]-23),abs(n['bounds'][3]-23),abs(n['bounds'][2]-23),abs(n['bounds'][5]-23))<=116 for n in layout)
    assert counts['minecraft:water']==477 and counts['minecraft:wheat']==48
    assert counts['minecraft:green_bed']>=24 and counts['minecraft:white_bed']>=16
    assert counts['minecraft:oak_fence']==76
    assert counts['minecraft:lantern']+counts['minecraft:soul_lantern']==0
    assert not (ROOT/'kubejs/data/alfheim/worldgen/structure_set/frontier_stewardship.json').exists()
    source=fingerprint.hexdigest();runtime_path=ROOT/'tools/frontier_stewardship_runtime.json'
    runtime=json.loads(runtime_path.read_text(encoding='utf-8')) if runtime_path.exists() else {}
    verified=runtime.get('source_fingerprint')==source and runtime.get('validation_exit_code')==0
    report={'status':'runtime_validated_visual_pending' if verified else 'static_validated_runtime_pending',
            'source_fingerprint':source,'files':16,'members':6,'joins':5,'layout':layout,'block_counts':dict(counts)}
    (ROOT/'tools/frontier_stewardship_manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('FRONTIER STATIC PASS: 6 members, 5 supported joins; contained moon pools, supported survey platform and survival garden')

if __name__=='__main__':main()
