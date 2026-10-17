"""Check real emitted war assets, topology, extracted cores and exact stair joins."""
from collections import deque
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import nbt
from gen_void_war import ROOT,KINDS,SURFACE,UNDERGROUND,SURFACE_NAMES,BASEMENT_NAMES,java_source
from void_war_policy import FAMILIES,TYPE

AIR={'minecraft:air','minecraft:cave_air'}
def states(root):return {tuple(map(int,b['pos'])):root['palette'][int(b['state'])] for b in root['blocks']}

def connected_cells(grid,start):
    def clear(x,z):return all(grid.get((x,y,z),{}).get('Name') in AIR for y in (5,6,7))
    seen={start};queue=deque([start])
    while queue:
        x,z=queue.popleft()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            p=x+dx,z+dz
            if p not in seen and 0<=p[0]<47 and 0<=p[1]<47 and clear(*p):seen.add(p);queue.append(p)
    return seen

def main():
    report={'status':'STATIC_VALIDATED_RUNTIME_REQUIRED','biomes':['alfheim:void_verge','alfheim:void_shore'],'templates':[]}
    tag=json.loads((ROOT/'kubejs/data/alfheim/tags/worldgen/biome/has_void_war_remnants.json').read_text())
    assert tag=={'replace':False,'values':report['biomes']}
    roots={}
    generation=json.loads((ROOT/'tools/void_war_generation_report.json').read_text())
    probes=generation['layout']['registry_probes'];assert all(p['level'] in ('exact','vanilla') for p in probes.values())
    for record in generation['layout']['templates']:
        path=ROOT/record['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']
        root=nbt.load(path)[1];name=record['name'];grid=states(root);roots[name]=grid
        assert max(root['size'])<=48 and not root['entities']
        spawners=[]
        for b in root['blocks']:
            palette=root['palette'][int(b['state'])];assert palette['Name'] in probes
            if palette['Name']=='minecraft:spawner':
                entity=b['nbt']['SpawnData']['entity']['id'];assert 'creeper' not in entity
                assert entity in ('alfheim_companion:biome_skeleton','alfheim_companion:biome_endermite','alfheim_companion:marrow_tick','alfheim_companion:rib_burrower','alfheim_companion:sinew_leech','alfheim_companion:parasite_maw');spawners.append(entity)
            if 'LootTable' in b.get('nbt',{}):assert b['nbt']['LootTable']=='alfheim:chests/void_war_salvage'
        detail={'name':name,'sha256':record['sha256'],'blocks':len(root['blocks']),'spawners':spawners}
        if name in BASEMENT_NAMES:
            seen=connected_cells(grid,(23,0))
            assert {(23,0),(23,46),(0,23),(46,23)}<=seen,(name,'disconnected tile entrances')
            for cx in range(5):
                for cz in range(5):assert (5+cx*9,5+cz*9) in seen,(name,'sealed room',cx,cz)
            detail['reachable_room_cells']=25
            for b in root['blocks']:
                if root['palette'][int(b['state'])]['Name']=='minecraft:spawner':
                    sx,sy,sz=map(int,b['pos'])
                    assert all(s['Name']!='alfheim:mana_glass_light' or abs(x-sx)+abs(y-sy)+abs(z-sz)>10
                        for (x,y,z),s in grid.items()),'Ward lighting suppresses the encounter spawner'
        report['templates'].append(detail)
    # Combine the exact order/24-block vertical offset of native surface + basement.
    combined={p:s for p,s in roots['entry_descent'].items()}
    combined={**{(x,y+24,z):s for (x,y,z),s in roots['entry_redoubt'].items()},**combined}
    for i in range(24):
        y,z=5+i,9+i
        for x in range(9,12):
            assert combined[(x,y,z)]['Name']=='alfheim:ivory_livingrock_stairs',(i,'broken stair')
            assert all(combined.get((x,y+d,z),{}).get('Name') in AIR for d in (1,2,3)),(i,'stair headroom')
    assert all(combined[(x,28,23)]['Name'] not in AIR for x in range(47)),'Open hole across the surface crossroads'
    for name in ('crystal_hulk','crystal_hulk_voidscarred'):
        grid=roots[name]
        assert all(grid[(x,y,15)]['Name'] in AIR for x in range(19,28) for y in range(13,23)),'Core extraction cavity filled'
        assert sum(s['Name']=='alfheim:golem_core_socket_empty' for s in grid.values())>30
    for kind,name in enumerate(KINDS):
        body=json.loads((ROOT/f'kubejs/data/alfheim/worldgen/structure/{name}.json').read_text())
        assert body['kind']==kind and body['biomes']=='#alfheim:has_void_war_remnants'
        assert body['type']=='alfheim_companion:void_war' and body['terrain_adaptation']=='none'
        assert len(SURFACE[kind])==len(UNDERGROUND[kind])==(9 if kind<6 else 1)
        assert sum(x.startswith('entry_descent') for x in UNDERGROUND[kind])==1
        assert SURFACE[kind][4 if kind<6 else 0].startswith('entry_redoubt')
    assert (ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/worldgen/VoidWarLayout.java').read_text()==java_source()
    for name in FAMILIES:
        body=json.loads((ROOT/f'kubejs/data/alfheim/worldgen/structure/{name}.json').read_text())
        assert body['type']==TYPE and body['layout']=={k:v for k,v in body.items() if k not in ('type','layout')}
    catalog=json.loads((ROOT/'kubejs/war_remains_catalog.json').read_text());assert len(catalog['blocks'])==32
    for block in catalog['blocks']:
        name=block['id'].split(':')[1]
        for v in range(3):
            stem=name+('' if not v else f'_v{v}')
            model=json.loads((ROOT/f'kubejs/assets/alfheim/models/block/{stem}.json').read_text())
            assert model['parent']=='minecraft:block/cube_all' and 'elements' not in model
            assert (ROOT/f'kubejs/assets/alfheim/textures/block/{stem}.png').exists()
    tests=[ET.parse(p).getroot() for p in (ROOT/'first_party_mods/alfheim_companion/build/test-results/test').glob('TEST-*.xml')]
    assert all(t.attrib['failures']==t.attrib['errors']=='0' for t in tests)
    report.update(java_tests=sum(int(t.attrib['tests']) for t in tests),materials=32,textures=96,continuous_steps=24,
        max_rooms_large_site=201,spatial_scope='900-block reservation from cooperating Void neighbors/dungeons; unrelated non-Void surface proximity requires review',
        installed_jar_sha256=hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest())
    (ROOT/'tools/void_war_static_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('VOID WAR STATIC PASS:',len(report['templates']),'templates, all room cells/portals connected, exact stair/bridge join, empty cores, 32 registered materials')

if __name__=='__main__':main()
