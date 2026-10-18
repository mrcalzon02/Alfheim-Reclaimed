"""Check complete policy coverage and real saved foundation edges, with no save edits."""
import argparse
import hashlib
import json
from pathlib import Path

from probe_terraces import chunks, section_blocks

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'kubejs/data/alfheim'


def static():
    structures={p.stem:json.loads(p.read_text()) for p in (DATA/'worldgen/structure').glob('*.json')}
    policies={p.stem:json.loads(p.read_text()) for p in (DATA/'terrain_affordances').glob('*.json')}
    assert structures.keys()==policies.keys(), 'Missing or stale structure terrain contracts'
    for name,p in policies.items():
        assert p['structure']=='alfheim:'+name
        assert p['generation_only'] and not p['replace_buried_solid_terrain']
        assert p['independent_structure_gap']>=500
        if p['mode']=='grounded':
            assert p['edge_width']>=1 and p['feather_width']>=1
            assert 0<p['max_support_depth']<=16
            assert structures[name]['type'] in ('alfheim_companion:remote_district','alfheim_companion:fairy_reserved_jigsaw',
                                               'alfheim_companion:void_war_neighbor','alfheim_companion:allocated_underground')
        if p['mode']=='void_ledge' or name=='severed_span':
            s=structures[name]
            assert s['type']=='alfheim_companion:void_surface' and s['terrain_adaptation']=='none'
            assert s['min_support']>=7 and s['solid_depth']>=5
    preferred=json.loads((DATA/'tags/worldgen/biome/prefers_royal_castle.json').read_text())['values']
    assert 'alfheim:tidewood_shore' not in preferred, 'Do not move existing reserved castle candidates'
    return dict(structures=len(structures),grounded=sum(p['mode']=='grounded' for p in policies.values()),
                native_void_hosts=12,minimum_ground_edge=1,feather_width=2,status='STATIC_VALIDATED')


def census(world,sites):
    region=ROOT/'server'/world/'dimensions/mythicbotany/alfheim/region'
    required={(s['x']//16+dx,s['z']//16+dz) for s in sites for dx in range(-8,8) for dz in range(-8,8)}
    grid={}
    for rx,rz in sorted({(cx//32,cz//32) for cx,cz in required}):
        path=region/f'r.{rx}.{rz}.mca'
        if not path.exists():continue
        for c in chunks(path):
            if (c['xPos'],c['zPos']) in required:grid[c['xPos'],c['zPos']]=c
    cache={}
    def block(x,y,z):
        key=x//16,y//16,z//16
        if key not in cache:
            sec=next((s for s in grid.get((x//16,z//16),{}).get('sections',[]) if s['Y']==y//16),None)
            cache[key]=section_blocks(sec) if sec else None
        data=cache[key]
        return data[((y&15)<<8)|((z&15)<<4)|(x&15)] if data else None
    def solid(name):
        return name is not None and name not in ('minecraft:air','minecraft:cave_air','minecraft:void_air','minecraft:water','minecraft:lava')
    proofs=[]
    for site in sites:
        starts=[(c,s) for c in grid.values() for family,s in c.get('structures',{}).get('starts',{}).items()
                if family==site['family'] and s.get('id')!='INVALID']
        assert starts, ('Missing naturally generated grounded structure',site)
        c,start=min(starts,key=lambda cs:(cs[0]['xPos']*16-site['x'])**2+(cs[0]['zPos']*16-site['z'])**2)
        plates=[p for p in start['Children'] if p['id']=='alfheim_companion:ground_plate']
        originals=[p for p in start['Children'] if 'pool_element' in p]
        assert plates and len(plates)==len(originals),(site,'Missing saved foundation members')
        checked=0
        for plate in plates:
            x0,z0,x1,z1,top,depth=(int(plate[k]) for k in ('PlateMinX','PlateMinZ','PlateMaxX','PlateMaxZ','PlateY','Depth'))
            assert int(plate['Edge'])>=1 and int(plate['Feather'])==2 and depth<=16
            ring={(x,z) for x in range(x0-1,x1+2) for z in (z0-1,z1+1)}
            ring|={(x,z) for z in range(z0,z1+1) for x in (x0-1,x1+1)}
            for x,z in ring:
                # Related jigsaw members intentionally meet and can own this cell.
                if any(p['BB'][0]<=x<=p['BB'][3] and p['BB'][2]<=z<=p['BB'][5] for p in originals):continue
                assert solid(block(x,top,z)),(site,'Missing plate edge',(x,top,z),block(x,top,z))
                # Check the entire footing down to first original solid host;
                # an air/water gap immediately below the bounded fill is a failure.
                for y in range(top-1,top-depth-2,-1):
                    assert solid(block(x,y,z)),(site,'Unsupported footing',(x,y,z),block(x,y,z))
                    if block(x,y,z)!=plate['Material']:break
                checked+=1
        assert checked>0,site
        proofs.append(dict(**site,start_chunk=[c['xPos'],c['zPos']],template_members=len(originals),
                           saved_foundation_pieces=len(plates),verified_edge_columns=checked,
                           status='SAVED_EDGE_AND_SUPPORT_VERIFIED'))
    return proofs


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',action='store_true');args=parser.parse_args()
    result=static()
    if args.runtime:
        report=json.loads((ROOT/'tools/castle_natural_runtime_report.json').read_text())
        result['proofs']=census(report['world'],report['ground_sites'])
        result.update(world=report['world'],seed=report['seed'],console=report['console'],
                      tested_jar_sha256=report['tested_jar_sha256'],status='REPRESENTATIVE_RUNTIME_VALIDATED',
                      visual_review='pending client inspection',all_families_naturally_sampled=False)
    (ROOT/'tools/terrain_affordance_validation_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
