"""Source/shipping, registration, portal and spatial gates for transport, bridge and customs."""
from collections import Counter,deque
import json
from pathlib import Path
import re
import nbt
import gen_harbor_complex as gen
from check_ancient_assembly import rotate,world_pos,STEP

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'kubejs/data/alfheim/structures/ancient/harbor_complex'


def topology():
    queue=deque([('harbor_exchange',(0,0,0),0)]);seen=[];joins=[]
    while queue:
        name,origin,r=queue.popleft()
        p=nbt.load(str(PATH/f'{name}.nbt'))[1]
        sx,sy,sz=map(int,p['size'])
        corners=[world_pos((x,y,z),origin,r) for x in (0,sx-1) for y in (0,sy-1) for z in (0,sz-1)]
        bounds=tuple(min(c[i] for c in corners) for i in range(3))+tuple(max(c[i] for c in corners) for i in range(3))
        seen.append({'name':name,'origin':origin,'rotation':r,'bounds':bounds})
        for b in p['blocks']:
            be=b.get('nbt',{})
            if be.get('id')!='minecraft:jigsaw' or be['pool']=='minecraft:empty':continue
            child=be['pool'].split('/')[-1];cp=nbt.load(str(PATH/f'{child}.nbt'))[1]
            socket=next(b for b in cp['blocks'] if b.get('nbt',{}).get('name')==be['target'])
            face=p['palette'][int(b['state'])]['Properties']['orientation'].split('_')[0]
            dx,dz=rotate(*STEP[face],r);point=world_pos(b['pos'],origin,r)
            target=(point[0]+dx,point[1],point[2]+dz)
            cf=cp['palette'][int(socket['state'])]['Properties']['orientation'].split('_')[0]
            cr=next(r for r in range(4) if rotate(*STEP[cf],r)==(-dx,-dz))
            cpos=world_pos(socket['pos'],(0,0,0),cr);co=tuple(target[i]-cpos[i] for i in range(3))
            joins.append((name,child,point,target));queue.append((child,co,cr))
    return seen,joins


def main():
    compare=ROOT/'build/harbor-complex-equality';compare.mkdir(parents=True,exist_ok=True)
    files=gen.generate(compare)
    assert len(files)==46
    placement=json.loads((ROOT/'kubejs/data/alfheim/worldgen/structure_set/harbor_complex.json').read_text(encoding='utf-8'))
    assert placement['structures']==[{'structure':'alfheim:harbor_complex','weight':1}]
    from district_policy import PLACEMENT
    assert placement['placement']==PLACEMENT
    registry=set(json.loads((ROOT/'server/local/kubejs/export/registries/block.json').read_text()))
    for script in (ROOT/'kubejs/startup_scripts').glob('*.js'):
        text=script.read_text(encoding='utf-8')
        if "registry('block'" in text:registry.update(re.findall(r"event\.create\(['\"]([^'\"]+)['\"]",text))
    counts=Counter();cultural=0
    for twin in files:
        path=ROOT/twin.relative_to(compare)
        if path.suffix!='.nbt':assert path.read_bytes()==twin.read_bytes(),path;continue
        p=nbt.load(str(path))[1];assert p==nbt.load(str(twin))[1],path
        assert max(map(int,p['size']))<=48 and p['entities']==[],path
        names={s['Name'] for s in p['palette']};assert names<=registry,(path,names-registry)
        cells={tuple(map(int,b['pos'])):p['palette'][int(b['state'])] for b in p['blocks']}
        # Every port belongs to one supported walking network through its member.
        ports=[tuple(map(int,b['pos'])) for b in p['blocks'] if b.get('nbt',{}).get('id')=='minecraft:jigsaw']
        def walkable(point):
            x,y,z=point
            return (cells.get(point,{}).get('Name') in ('minecraft:air','minecraft:jigsaw')
                    and cells.get((x,y+1,z),{}).get('Name')=='minecraft:air'
                    and cells.get((x,y-1,z),{}).get('Name') not in (None,'minecraft:air','minecraft:water'))
        pending=deque(ports[:1]);reachable=set()
        while pending:
            point=pending.popleft()
            if point in reachable or not walkable(point):continue
            reachable.add(point);x,y,z=point
            pending.extend((x+dx,y,z+dz) for dx,dz in STEP.values())
        assert set(ports)<=reachable,('disconnected internal circulation',path,set(ports)-reachable)
        if path.stem=='signal_lighthouse':
            for i in range(12):
                x,y,z=10,gen.DEPTH+i+1,26-i
                assert cells[(x,y,z)]['Name']=='botania:dreamwood_stairs'
                assert cells[(x,y-1,z)]['Name']!='minecraft:air'
                assert cells[(x,y+1,z)]['Name']==cells[(x,y+2,z)]['Name']=='minecraft:air'
        if path.stem in ('harbor_exchange','sunken_drydock','tide_temple'):
            for x0,x1 in ((10,17),(29,36)):
                for x in range(x0,x1+1):
                    for z in range(6,20):
                        assert cells[(x,gen.DEPTH-3,z)]['Name']!='minecraft:air'
                        assert cells[(x,gen.DEPTH-2,z)]['Name']==cells[(x,gen.DEPTH-1,z)]['Name']=='minecraft:water'
                for y in (gen.DEPTH-2,gen.DEPTH-1):
                    for z in range(6,20):
                        for x in (x0-1,x1+1):assert cells[(x,y,z)]['Name']!='minecraft:air'
                    for x in range(x0,x1+1):
                        for z in (5,20):assert cells[(x,y,z)]['Name']!='minecraft:air'
        for b in p['blocks']:
            state=p['palette'][int(b['state'])];name=state['Name'];counts[name]+=1
            if name.startswith('alfheim:royal_') and name!='alfheim:royal_wall_banner':
                x,y,z=map(int,b['pos'])
                assert cells[(x,y-1,z)]['Name'] not in ('minecraft:air','minecraft:water'),('unsupported harbor furniture',path,name,b['pos'])
            if name.startswith(('alfheim:royal_','alfheim:elder_')):cultural+=1
            if b.get('nbt',{}).get('id')=='minecraft:jigsaw':
                be=b['nbt'];assert re.fullmatch('[a-z0-9_.:/-]+',be['name']),be
                x,y,z=map(int,b['pos']);assert cells[(x,y+1,z)]['Name']=='minecraft:air',(path,b)
                assert cells[(x,y-1,z)]['Name'] not in ('minecraft:air','minecraft:water'),(path,b)
    layout,joins=topology();assert len(layout)==10 and len(joins)==9,(layout,joins)
    for i,a in enumerate(layout):
        for b in layout[i+1:]:
            assert not all(max(a['bounds'][j],b['bounds'][j])<=min(a['bounds'][j+3],b['bounds'][j+3]) for j in range(3)),('overlapping members',a,b)
    assert counts['minecraft:brown_bed']==26,counts
    assert counts['minecraft:oak_fence']==178,counts
    assert counts['minecraft:water']==1344 and counts['minecraft:lava']==0
    assert cultural>=12,cultural
    assert counts['minecraft:lantern']+counts['minecraft:soul_lantern']==0
    # The local bounds of this family fit the codec's adapted 116-block reach.
    assert all(max(abs(n['bounds'][0]-23),abs(n['bounds'][3]-23),
                   abs(n['bounds'][2]-23),abs(n['bounds'][5]-23))<=116 for n in layout)
    (ROOT/'tools/harbor_complex_layout.json').write_text(json.dumps({'layout':layout,'joins':joins,'cultural_modules':cultural,'verified_internal_networks':len(layout),'block_counts':dict(counts)},indent=2)+'\n',encoding='utf-8')
    print(f'HARBOR COMPLEX STATIC PASS: 46 source-equal files, sparse bounded placement, 10 members, 9 supported ports, {cultural} cultural modules')


if __name__=='__main__':main()
