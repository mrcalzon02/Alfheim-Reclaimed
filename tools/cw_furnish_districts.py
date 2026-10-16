"""Continuity Works adapter for supported room furnishings in existing district templates."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import nbt
from structure_nbt import Piece
from cw_district_refit import FAMILIES,cells
from district_furnishing_placement import apply,components,grid,preserves_routes,walkable

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('kubejs/data/alfheim/structures/ancient')
STAGE=ROOT/'build/district-furnishing-placement'

def piece(root):
    p=Piece(*map(int,root['size']));p.palette=list(root['palette']);p.entities=list(root['entities'])
    p.blocks={tuple(map(int,b['pos'])):(int(b['state']),b.get('nbt')) for b in root['blocks']}
    p._index={(s['Name'],tuple(sorted(s.get('Properties',{}).items())) or None):i for i,s in enumerate(p.palette)}
    return p

def validate(before,after,placements):
    assert before['size']==after['size'] and before['entities']==after['entities']
    a,b=cells(before),cells(after);assert set(a)==set(b)
    expected={tuple(p['pos']):p for p in placements};changes=[]
    for pos,(state,be) in a.items():
        new,newbe=b[pos]
        if (state,be)==(new,newbe):continue
        assert pos in expected and be is None and newbe is None,('Unowned or loot change',pos)
        p=expected[pos]
        assert state==p['original'] and new=={'Name':p['id'],'Properties':{'facing':p['facing']}},pos
        changes.append(pos)
    assert set(changes)==set(expected)
    assert preserves_routes(components(walkable({p:s for p,(s,_) in a.items()})),set(expected))
    assert len(placements)<=2
    return len(changes),sum(be is not None for _,be in a.values())

class Provider:
    provider_id='alfheim_district_furnishing_placement_v1';aliases=('alfheim_district_furnishing_placement',)
    def __init__(self,reuse=False):self.reuse=reuse
    def describe(self):return {'provider_id':self.provider_id,'aliases':list(self.aliases),'operation':'existing room furniture, preserved geometry and loot'}
    def generate(self,request,registry_resolver):
        family=request.generation['family'];assert family in FAMILIES
        stem='ancient_districts' if family=='common_residential' else family
        env=dict(os.environ,ALFHEIM_DISTRICT_FURNISHINGS='0',ALFHEIM_DISTRICT_BASELINE='0')
        if not self.reuse:
            subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools'/f'gen_{stem}.py'),'--output-root',str(STAGE/'baseline')],
                cwd=ROOT,env=env,check=True,capture_output=True)
        assert {p.name for p in (STAGE/'baseline'/BASE/family).glob('*.nbt')}=={p.name for p in (ROOT/BASE/family).glob('*.nbt')},'Missing baseline templates'
        records=[];files={};probes={}
        for path in sorted((STAGE/'baseline'/BASE/family).glob('*.nbt')):
            before=nbt.load(path)[1];p=piece(before);placements=apply(p,family,path.stem);after=p.to_nbt()
            changed,fixtures=validate(before,after,placements)
            # Shipping architectural cells must match the current sources before promotion.
            shipped=nbt.load(ROOT/BASE/family/path.name)[1]
            shipped_cells=cells(shipped)
            assert before['size']==shipped['size'] and before['entities']==shipped['entities'] and set(cells(before))==set(shipped_cells),'Shipping ownership differs from source'
            for pos,(s,be) in cells(before).items():
                actual,abe=shipped_cells[pos]
                assert (s,be)==(actual,abe) or (pos in {tuple(x['pos']) for x in placements} and actual.get('Name','').startswith('alfheim_leyworks:district_') and abe is None),(family,path.stem,pos,'source drift')
            if not changed:continue
            for place in placements:
                rid=place['id'];probes.setdefault(rid,registry_resolver.probe(rid,kind='block'))
                assert probes[rid]['level']=='exact',probes[rid]
            destination=STAGE/'generated'/BASE/family/path.name;destination.parent.mkdir(parents=True,exist_ok=True)
            nbt.save(destination,'',after);data=gzip.compress(gzip.decompress(destination.read_bytes()),mtime=0);destination.write_bytes(data)
            rel=(BASE/family/path.name).as_posix();files[rel]=data
            records.append(dict(file=rel,placements=placements,preserved_block_entities=fixtures,changed_cells=changed,sha256=hashlib.sha256(data).hexdigest()))
        return {'provider_id':self.provider_id,'status':'LOCALLY_VALIDATED','generated_layout':{'family':family,'templates':records,'registry_probes':probes},
            'structure_artifact':{'format':'minecraft_structure_nbt','piece_count':len(records)},'artifact_bytes':files}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--promote',action='store_true');ap.add_argument('--reuse-baseline',action='store_true',help='Reuse locally generated architecture only after cell-wise shipping comparison');args=ap.parse_args()
    sys.path.insert(0,'C:/GITS/Structuresmith/StructureSmith/src');from structure_capability import StructureCapability
    cap=StructureCapability(project_root=ROOT,state_root=STAGE/'snapshots');cap.register_generator(Provider(args.reuse_baseline))
    evidence=json.loads((ROOT/'tools/district_furnishings_runtime_report.json').read_text())
    assert evidence['status']=='NATIVE_INTERACTIONS_AND_RELOAD_PASS'
    assert evidence['installed_jar_sha256']==hashlib.sha256((ROOT/'mods/alfheim_leyworks-0.1.0.jar').read_bytes()).hexdigest()
    ids=set(re.findall(r'alfheim_leyworks:district_\w+',' '.join(evidence['storage']+evidence['stations'])))
    assert len(ids)==11;cap.inventory.add_registry_ids(ids,kind='block')
    report={'capability':'Continuity Works StructureCapability.generate','target_version':'1.20.1','registry_evidence':'tools/district_furnishings_runtime_report.json',
        'placement_policy':'unchanged existing same-family rooms; no independent structures added','families':[]}
    for family in FAMILIES:
        result=cap.generate({'structure_id':'alfheim:district_furnishings/'+family,'target_version':'1.20.1','grade':3,
            'purpose':{'kind':'functional_room_furnishing','required_zones':['supported interior corners'],'required_routes':['original walking components']},
            'context':{'dimension':'mythicbotany:alfheim'},'generation':{'kind':'alfheim_district_furnishing_placement','family':family,'materialize_nbt':True}})
        assert result['generation']['status']=='LOCALLY_VALIDATED',result['generation']
        layout=result['generated_layout'];report['families'].append(dict(snapshot_id=result['snapshot']['snapshot_id'],**layout))
        print(f'{family}: {len(layout["templates"])} furnished templates',flush=True)
        if args.promote:
            for rec in layout['templates']:(ROOT/rec['file']).write_bytes((STAGE/'generated'/rec['file']).read_bytes())
    (ROOT/'tools/district_furnishing_placement_report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
