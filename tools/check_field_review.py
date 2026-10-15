"""Regression guards for the October 12 field-review failures."""
import hashlib
import json
from pathlib import Path
import nbt
from model_geometry import FACES

ROOT = Path(__file__).resolve().parents[1]


def overlaps(doc):
    faces = []
    for element in doc.get('elements', []):
        if 'rotation' in element: continue
        a,b = element['from'],element['to']
        for face in element.get('faces', {}):
            axis,direction = FACES[face]
            u,v = [i for i in range(3) if i!=axis]
            faces.append((face,b[axis] if direction>0 else a[axis],a[u],a[v],b[u],b[v]))
    found = 0
    for i,a in enumerate(faces):
        for b in faces[i+1:]:
            if a[:2]==b[:2] and max(a[2],b[2])<min(a[4],b[4]) and max(a[3],b[3])<min(a[5],b[5]):
                found += 1
    return found


def states(path):
    _,p=nbt.load(str(path))
    return {tuple(map(int,b['pos'])):p['palette'][int(b['state'])] for b in p['blocks']}


def main():
    hashes=json.loads((ROOT/'tools/field_review_terrain_baseline.json').read_text())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items()), 'Terrain changed'
    paths=[*(ROOT/'kubejs/assets/alfheim/models/block').rglob('*.json'),
           *(ROOT/'first_party_mods/alfheim_leyworks/src/main/resources/assets/alfheim_leyworks/models/block').glob('*.json')]
    # Only bespoke cuboid families are owned by this repair; cube-all and inherited models have no elements.
    bad=[]; checked=0
    for p in paths:
        doc=json.loads(p.read_text())
        if not doc.get('elements'): continue
        checked+=1
        if overlaps(doc):bad.append(str(p.relative_to(ROOT)))
    assert not bad, ('Coplanar custom-model faces',bad)
    base=ROOT/'kubejs/data/alfheim/structures/deepworks_archaeology/elder_kings_tomb'
    for role in ('centre','approach','wing','gallery'):
        s=states(base/f'{role}.nbt')
        for (x,y,z),state in s.items():
            if state['Name']!='alfheim:memorial_carving':continue
            dx,dz={'north':(0,-1),'south':(0,1),'east':(1,0),'west':(-1,0)}[state['Properties']['facing']]
            backing=s.get((x-dx,y,z-dz),{}).get('Name','minecraft:air')
            assert backing not in ('minecraft:air','minecraft:water'),(role,(x,y,z),'unbacked carving')
        lamps=sum(s_['Name']=='minecraft:soul_lantern' for s_ in s.values())
        assert lamps<=20,(role,lamps)
    wing=states(base/'wing.nbt')
    # Rotunda centre must own the high air volume beneath its solid crown.
    for y in (14,15,16):assert wing.get((23,y,20),{}).get('Name')=='minecraft:air',('uncarved crown',y)
    assert wing[(23,17,20)]['Name']!='minecraft:air','unsealed crown'
    for name in ('straight','hub'):
        s=states(ROOT/f'kubejs/data/alfheim/structures/leyline/{name}.nbt')
        lamps=sum(x['Name']=='minecraft:lantern' for x in s.values())
        assert lamps<=8,(name,lamps)
        rails=[x for x in s.values() if x['Name']=='alfheim:leyline_livingrock_wall']
        assert not rails or any(any(x.get('Properties',{}).get(f) in ('low','tall') for f in ('north','south','east','west')) for x in rails)
    send=(ROOT/'kubejs/data/alfheim/functions/hub/send.mcfunction').read_text()
    assert 'spreadplayers' not in '\n'.join(l for l in send.splitlines() if not l.startswith('#'))
    assert 'hub/ensure_landing' in send and 'hub/fallback' in send
    rule=json.loads((ROOT/'kubejs/data/mythicbotany/libx/surface_rule_set/alfheim_surface.json').read_text())
    from gen_golden_terraces import surface_rule
    assert rule['before_biomes']['sequence'][0]==surface_rule()
    assert 'above_preliminary_surface' in json.dumps(surface_rule()) and 'minecraft:dirt_path' not in json.dumps(surface_rule())
    from gen_golden_meadow import build as golden_meadow
    for relative,data in golden_meadow().items():assert (ROOT/relative).read_bytes()==data,relative
    from gen_native_feature_guards import build as native_guards
    for relative,data in native_guards().items():assert (ROOT/relative).read_bytes()==data,relative
    meadow=json.loads((ROOT/'kubejs/data/alfheim/worldgen/configured_feature/golden_meadow_grass.json').read_text())
    assert 'minecraft:wheat' not in json.dumps(meadow) and 'minecraft:farmland' not in json.dumps(meadow)
    for name in ('golden_field_dais','thorn_gate','shore_memorial_court'):
        spec=json.loads((ROOT/f'kubejs/data/alfheim/worldgen/structure/{name}.json').read_text())
        assert spec['size']==1, (name,'zero-depth single-piece structures fail world placement on this runtime')
        assert spec['project_start_to_heightmap']=='WORLD_SURFACE_WG'
    patch=json.loads((ROOT/'kubejs/data/alfheim/worldgen/configured_feature/shore_spore_scatter.json').read_text())
    assert 'minecraft:mycelium' in json.dumps(patch),'Mushrooms cannot scatter on their own shore bed'
    print(f'FIELD REVIEW PASS: {len(hashes)} terrain files unchanged, {checked} custom models without coplanar faces; crown, mounts, light budgets, wall states and spawn guards passed')


if __name__=='__main__': main()
