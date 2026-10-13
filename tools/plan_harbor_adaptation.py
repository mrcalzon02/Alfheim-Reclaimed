"""Compare socket-connected footprint proposals, without changing shipping templates.

Saved heightmaps include decoration and infer fluid presence: results are screening
evidence only. A proposed footprint is not an authored or runtime-accepted template.
"""
import argparse
from collections import Counter,deque
import copy
import json
from pathlib import Path
from gen_harbor_complex import SIZES,LINKS
from survey_saved_harbor_coasts import load_columns,rotate

ROOT=Path(__file__).resolve().parents[1]
STEP={'north':(0,-1),'south':(0,1),'west':(-1,0),'east':(1,0)}

def socket(size,face):
    sx,_,sz=size
    return {'north':(sx//2,0),'south':(sx//2,sz-1),'west':(0,sz//2),'east':(sx-1,sz//2)}[face]

def topology(sizes,links):
    q=deque([('harbor_exchange',(0,0),0)]);seen=[];joins=[]
    while q:
        name,origin,r=q.popleft();sx,_,sz=sizes[name]
        points=[rotate(x,z,r) for x in (0,sx-1) for z in (0,sz-1)]
        bounds=[min(p[0] for p in points)+origin[0],min(p[1] for p in points)+origin[1],
                max(p[0] for p in points)+origin[0],max(p[1] for p in points)+origin[1]]
        seen.append({'name':name,'origin':origin,'rotation':r,'bounds':bounds})
        for face,child in links.get(name,{}).items():
            px,pz=rotate(*socket(sizes[name],face),r);dx,dz=rotate(*STEP[face],r)
            target=(origin[0]+px+dx,origin[1]+pz+dz)
            cr=next(cr for cr in range(4) if rotate(0,1,cr)==(-dx,-dz))
            cx,cz=rotate(*socket(sizes[child],'south'),cr)
            q.append((child,(target[0]-cx,target[1]-cz),cr));joins.append((name,child))
    assert Counter(n['name'] for n in seen)==Counter(sizes.keys()),seen
    assert len(joins)==len(sizes)-1
    for i,a in enumerate(seen):
        for b in seen[i+1:]:
            assert not all(max(a['bounds'][j],b['bounds'][j])<=min(a['bounds'][j+2],b['bounds'][j+2]) for j in range(2)),(a,b)
    return seen

def proposals():
    baseline=topology(SIZES,LINKS)
    shipping=json.loads((ROOT/'tools/harbor_complex_layout.json').read_text(encoding='utf-8'))['layout']
    assert sorted((n['name'],list(n['origin']),n['rotation'],n['bounds']) for n in baseline)==sorted((n['name'],[n['origin'][0],n['origin'][2]],n['rotation'],[n['bounds'][i] for i in (0,2,3,5)]) for n in shipping)
    narrow=copy.deepcopy(SIZES);narrow['wavebreak_pier']=(23,20,27);narrow['sunken_drydock']=(23,24,23)
    inward=copy.deepcopy(LINKS)
    inward['bonded_warehouse']={'west':'tide_temple'}
    del inward['quay_court']['east']
    inward['harbor_approach']={'east':'dockworker_housing'}
    inland_sizes=copy.deepcopy(SIZES);inland_sizes['harbor_approach']=(23,14,40)
    combined=copy.deepcopy(narrow);combined['harbor_approach']=(23,14,40)
    core_names=('harbor_exchange','wavebreak_pier','harbormaster_house','quay_court','harbor_approach')
    core_sizes={name:narrow[name] for name in core_names}
    core_links={'harbor_exchange':{'east':'harbormaster_house','north':'wavebreak_pier','south':'quay_court'},
                'quay_court':{'north':'harbor_approach'}}
    return {'shipping':baseline,'narrow_docks':topology(narrow,LINKS),
            'inland_temple':topology(inland_sizes,inward),'narrow_docks_inland_temple':topology(combined,inward),
            'core_with_approach':topology(core_sizes,core_links)}

def reason(c,wet=False,mixed=False):
    if c is None:return 'outside_saved_columns'
    surface,floor=c;water=surface==64 and floor<64
    if (wet and not mixed) or (mixed and water):
        if not water:return 'dry_dock_column'
        if floor<58:return 'water_beyond_footing_reach'
        return None
    if water:return 'wet_land_connection'
    if surface<58 or floor<58:return 'ground_beyond_footing_reach'
    if surface>73:return 'land_above_highest_quay'
    if surface!=floor:return 'decorated_or_ambiguous_column'
    return None

def samples(parts):
    out=[]
    for n in parts:
        x0,z0,x1,z1=n['bounds'];marine=n['name'] in ('wavebreak_pier','sunken_drydock')
        for x in sorted(set(range(x0,x1+1,8))|{x1}):
            for z in sorted(set(range(z0,z1+1,8))|{z1}):
                out.append((n['name'],x,z,marine,(-16<=z<16) or not marine))
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('world');ap.add_argument('--step',type=int,default=4);args=ap.parse_args()
    assert args.step in (4,8,16)
    grid,chunk_count=load_columns(args.world);layouts=proposals();results={}
    origins=[(x,z) for x,z in sorted(grid) if x%args.step==z%args.step==0 and not(abs(x)<400 and abs(z)<400)]
    for variant,parts in layouts.items():
        approach=next(n for n in parts if n['name']=='harbor_approach')['bounds']
        dry=((approach[0]+approach[2])//2,(approach[1]+approach[3])//2)
        checks=samples(parts);rows=[];preflight=0;failures=Counter()
        for x,z in origins:
            for r in range(4):
                def at(px,pz):
                    dx,dz=rotate(px,pz,r);return grid.get((x+dx,z+dz))
                if reason(at(23,-20),wet=True) or reason(at(23,23)) or reason(at(*dry)):continue
                preflight+=1;bad=Counter();members=Counter();passed=0
                for name,px,pz,wet,mixed in checks:
                    why=reason(at(px,pz),wet,mixed)
                    if why:bad[why]+=1;members[name]+=1
                    else:passed+=1
                failures.update(bad)
                rows.append({'x':x,'z':z,'rotation':r,'passing_fraction':round(passed/len(checks),5),
                             'failed_samples':sum(bad.values()),'full_saved_coverage':not bad['outside_saved_columns'],
                             'reasons':dict(bad),'members_with_failures':dict(members)})
        rows.sort(key=lambda n:(not n['full_saved_coverage'],n['failed_samples']!=0,-n['passing_fraction'],n['failed_samples'],n['x'],n['z'],n['rotation']))
        results[variant]={'layout':parts,'coarse_sample_count':len(checks),'preflight_candidates':preflight,
                          'coarse_passes':sum(n['failed_samples']==0 for n in rows),'failure_counts':dict(failures),'best_candidates':rows[:12],
                          'fully_covered_candidates':sum(n['full_saved_coverage'] for n in rows),
                          'status':'shipping prototype' if variant=='shipping' else 'footprint proposal; furniture and NBT not authored'}
        print(variant,'preflight',preflight,'coarse passes',results[variant]['coarse_passes'],'best',rows[0] if rows else None)
    result={'world':args.world,'saved_chunks':chunk_count,'saved_columns':len(grid),'origin_step':args.step,
            'scope':'read-only decorated saved terrain; inferred fluids; coarse screening only; no admission',
            'variants':results}
    (ROOT/'tools/harbor_adaptation_screen.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
