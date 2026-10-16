"""Bounded, deterministic room-corner furnishing; no terrain or placement-policy ownership."""
from collections import deque
import os

AIR={'minecraft:air','minecraft:cave_air'}
PREFIX='alfheim_leyworks:district_'
ROLES={
 'agricultural_estate':('seed_cabinet','artificer_desk'),
 'civic_center':('market_counter','archive_cabinet'),
 'common_residential':('provision_hutch','weaving_frame'),
 'elder_lineage':('archive_cabinet','weaving_frame'),
 'frontier_stewardship':('cartographers_table','provision_hutch'),
 'harbor_complex':('market_counter','cartographers_table'),
 'military_warden':('armory_locker','mending_bench'),
 'production_district':('masons_bench','artificer_desk'),
 'relief_district':('apothecary_cabinet','provision_hutch'),
 'roads_trade':('market_counter','cartographers_table'),
 'sacred_precinct':('archive_cabinet','weaving_frame'),
 'scholastic_quarter':('archive_cabinet','artificer_desk'),
}
DIRECTIONS=(('north',0,-1),('east',1,0),('south',0,1),('west',-1,0))

def full(state):
    name=state.get('Name','')
    return name not in AIR|{'','minecraft:structure_void','minecraft:water','minecraft:lava'} and (
        name.endswith(('_planks','_bricks','_brick','_polished','_log','_wood','_livingrock','_quartz','_tiles'))
        or name in {'minecraft:stone','minecraft:stone_bricks','ars_nouveau:sourcestone'})

def grid(piece):return {p:piece.palette[v[0]] for p,v in piece.blocks.items()}

def walkable(states):
    return {p for p,s in states.items() if s.get('Name') in AIR
            and states.get((p[0],p[1]+1,p[2]),{}).get('Name') in AIR
            and full(states.get((p[0],p[1]-1,p[2]),{}))}

def neighbors(pos,nodes):
    x,y,z=pos
    for _,dx,dz in DIRECTIONS:
        for dy in (-1,0,1):
            p=(x+dx,y+dy,z+dz)
            if p in nodes:yield p

def components(nodes):
    remaining=set(nodes);out=[]
    while remaining:
        seed=min(remaining);remaining.remove(seed);part={seed};todo=deque([seed])
        while todo:
            for p in neighbors(todo.popleft(),remaining):remaining.remove(p);part.add(p);todo.append(p)
        out.append(part)
    return out

def preserves_routes(parts,occupied):
    for part in parts:
        allowed=part-occupied
        if not allowed:continue
        reached={min(allowed)};todo=deque(reached)
        while todo:
            for p in neighbors(todo.popleft(),allowed):
                if p not in reached:reached.add(p);todo.append(p)
        if reached!=allowed:return False
    return True

def apply(piece,family,name):
    if family not in ROLES or os.environ.get('ALFHEIM_DISTRICT_FURNISHINGS')=='0':return []
    states=grid(piece);nodes=walkable(states);parts=components(nodes)
    protected=[]
    for p,(idx,be) in piece.blocks.items():
        rid=piece.palette[idx]['Name']
        if be is not None or rid=='minecraft:jigsaw' or rid.endswith(('_stairs','_ladder','_bed')):
            protected.append((p,4 if rid=='minecraft:jigsaw' else 2))
    sx,sy,sz=piece.size;candidates=[]
    for x,y,z in sorted(nodes):
        if not(2<=x<sx-2 and 2<=z<sz-2 and 1<y<sy-3):continue
        if any(abs(y-p[1])<=2 and abs(x-p[0])+abs(z-p[2])<=radius for p,radius in protected):continue
        if not any(full(states.get((x,y+dy,z),{})) or states.get((x,y+dy,z),{}).get('Name','').endswith(('_slab','_stairs')) for dy in range(3,min(13,sy-y))):continue
        if any(states.get((x+dx,y,z+dz),{}).get('Name','').endswith('_wall') for _,dx,dz in DIRECTIONS):continue
        for facing,dx,dz in DIRECTIONS:
            # A genuine inside corner, backing and side wall, with a two-wide approach.
            if not full(states.get((x-dx,y,z-dz),{})):continue
            for side in (-1,1):
                px,pz=-dz*side,dx*side
                if not full(states.get((x-px,y,z-pz),{})):continue
                approach={(x+dx*d+px*w,y,z+dz*d+pz*w) for d in (1,2) for w in (0,1)}
                if not approach<=nodes:continue
                candidates.append(((y,z,x,facing), (x,y,z),facing));break
    selected=[];occupied=set()
    for _,pos,facing in sorted(candidates):
        if pos in occupied or any(abs(pos[1]-p['pos'][1])<3 and abs(pos[0]-p['pos'][0])+abs(pos[2]-p['pos'][2])<7 for p in selected):continue
        if not preserves_routes(parts,occupied|{pos}):continue
        role=ROLES[family][len(selected)];rid=PREFIX+role
        piece.set(*pos,(rid,{'facing':facing}))
        selected.append({'pos':list(pos),'id':rid,'facing':facing,'original':states[pos]})
        occupied.add(pos)
        if len(selected)==2:break
    return selected

def without_furnishings(root):
    """Normalize only owned new furniture to its original air for the architectural audit."""
    from copy import deepcopy
    result=deepcopy(root)
    for state in result['palette']:
        if state['Name'].startswith(PREFIX):state.clear();state['Name']='minecraft:air'
    return result

def verified_registry_ids():
    import hashlib,json,re
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    proof=json.loads((root/'tools/district_furnishings_runtime_report.json').read_text())
    assert proof['status']=='NATIVE_INTERACTIONS_AND_RELOAD_PASS'
    assert proof['installed_jar_sha256']==hashlib.sha256((root/'mods/alfheim_leyworks-0.1.0.jar').read_bytes()).hexdigest()
    ids=set(re.findall(r'alfheim_leyworks:district_\w+',' '.join(proof['storage']+proof['stations'])))
    assert len(ids)==11
    return ids
