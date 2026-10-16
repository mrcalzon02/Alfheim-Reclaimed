"""Continuity Works provider adapter for the pack's existing district authoring tools.

Generate to a staging root, audit, and only then promote the returned NBT bytes. This
does not enable new natural structure sets or assert worldgen exclusion is implemented.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib

import nbt
import structure_detail as sd

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ('common_residential', 'elder_lineage', 'civic_center', 'relief_district',
            'scholastic_quarter', 'production_district', 'agricultural_estate',
            'roads_trade', 'harbor_complex', 'sacred_precinct', 'military_warden',
            'frontier_stewardship')


def generate_family(family, destination, baseline=False):
    stem = 'ancient_districts' if family == 'common_residential' else family
    env = dict(os.environ)
    env['ALFHEIM_DISTRICT_BASELINE'] = '1' if baseline else '0'
    subprocess.run([sys.executable, '-X', 'utf8', '-B', str(ROOT/'tools'/f'gen_{stem}.py'),
                    '--output-root', str(destination)], cwd=ROOT, env=env,
                   check=True, capture_output=True)
    return destination/'kubejs/data/alfheim/structures/ancient'/family


def cells(root):
    return {tuple(map(int,b['pos'])): (root['palette'][int(b['state'])], b.get('nbt'))
            for b in root['blocks']}


def compare(before, after):
    assert before['size'] == after['size'] and max(after['size']) <= 48
    assert before['entities'] == after['entities']
    a,b = cells(before),cells(after)
    assert set(a) == set(b), 'A refit cannot take ownership of new terrain cells'
    changed = relief = 0
    for pos,(state,be) in a.items():
        new,newbe = b[pos]
        assert be == newbe, ('block entity changed',pos)
        if state == new:
            continue
        changed += 1
        assert be is None, ('fixture changed',pos)
        if state['Name'] in sd.AIR_NAMES:
            relief += 1
            # All new relief must touch an ORIGINAL solid, and clear every original
            # walking surface by four blocks, including galleries above ground level.
            x,y,z = pos
            def air(at): return a.get(at,({},None))[0].get('Name') in sd.AIR_NAMES
            assert all(air((x,y-d,z)) for d in range(1,5)), ('headroom',pos)
            assert any(a.get((x+dx,y,z+dz),({},None))[0].get('Name') not in sd.AIR_NAMES|{None}
                       for dx,dz in ((1,0),(-1,0),(0,1),(0,-1))), ('unbacked',pos)
        else:
            assert state['Name'] != 'minecraft:jigsaw'
            assert new['Name'] not in sd.AIR_NAMES, ('carved structural block',pos)
    detail = lambda grid: sum(sd.is_detail(s['Name']) for s,be in grid.values())
    return {'changed_cells':changed,'relief_cells':relief,
            'detail_before':detail(a),'detail_after':detail(b)}


class DistrictProvider:
    provider_id = 'alfheim_existing_district_refit_v1'
    aliases = ('alfheim_district_refit',)

    def __init__(self, stage, baseline):
        self.stage,self.baseline = stage,baseline

    def describe(self):
        return {'provider_id':self.provider_id,'aliases':list(self.aliases),
                'operation':'existing authored district refit; eight geometric detail layers'}

    def generate(self, request, registry_resolver):
        family = request.generation['family']
        assert family in FAMILIES
        old_dir = generate_family(family,self.baseline,baseline=True)
        new_dir = generate_family(family,self.stage)
        files,metrics,probes = {},[],{}
        assert list(new_dir.glob('*.nbt')), ('Generator emitted no templates', family, new_dir)
        assert {p.name for p in new_dir.glob('*.nbt')} == {p.name for p in old_dir.glob('*.nbt')} == \
               {p.name for p in (ROOT/'kubejs/data/alfheim/structures/ancient'/family).glob('*.nbt')}, \
               ('Refit changed the family member inventory',family)
        for path in sorted(new_dir.glob('*.nbt')):
            before = nbt.load(old_dir/path.name)[1]
            after = nbt.load(path)[1]
            from district_furnishing_placement import without_furnishings
            metric = compare(before,without_furnishings(after))
            for state in after['palette']:
                rid = state['Name']
                if rid not in probes:
                    probes[rid] = registry_resolver.probe(rid,kind='block')
                assert probes[rid]['level'] in ('exact','vanilla'), probes[rid]
            data = gzip.compress(gzip.decompress(path.read_bytes()),mtime=0)
            path.write_bytes(data)
            files[path.name] = data
            metrics.append({'piece':path.stem,**metric,'sha256':hashlib.sha256(data).hexdigest()})
        return {'provider_id':self.provider_id,'status':'LOCALLY_VALIDATED',
                'generated_layout':{'family':family,'metrics':metrics,'registry_probes':probes,
                                    'runtime_state':'RUNTIME_TEST_REQUIRED'},
                'structure_artifact':{'format':'minecraft_structure_nbt','piece_count':len(files),
                                      'pieces':[{'name':m['piece'],'sha256':m['sha256']} for m in metrics]},
                'artifact_bytes':files}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cw-source',type=Path,required=True)
    ap.add_argument('--family',choices=FAMILIES,action='append')
    ap.add_argument('--include-anomaly',action='store_true')
    ap.add_argument('--update-report',action='store_true',help='Replace selected family results in an existing full report')
    ap.add_argument('--promote',action='store_true')
    args=ap.parse_args()
    sys.path.insert(0,str(args.cw_source/'src'))
    from structure_capability import StructureCapability
    stage=ROOT/'build/continuity-district-refit'
    cap=StructureCapability(project_root=ROOT,state_root=stage/'snapshots')
    assert cap.capabilities()['service'] == 'Continuity Works'
    registry_path=ROOT/'server/local/kubejs/export/registries/block.json'
    # Published inventory extension: use an actual running-server registry export,
    # rather than treating a discovered namespace/model as proof of registration.
    cap.inventory.add_registry_ids(json.loads(registry_path.read_text()),kind='block')
    from district_furnishing_placement import verified_registry_ids
    cap.inventory.add_registry_ids(verified_registry_ids(),kind='block')
    stage.mkdir(parents=True,exist_ok=True)
    (stage/'tool-catalog.json').write_text(json.dumps(cap.tools(),indent=2))
    (stage/'inventory.json').write_text(json.dumps(cap.inventory_project(),indent=2))
    cap.register_generator(DistrictProvider(stage/'generated',stage/'baseline'))
    report={'capability':'Continuity Works','execution':'StructureCapability.audit / plan / generate',
            'source':str(args.cw_source),'version':'1.20.1','loader':'Forge 47.4.10',
            'capability_version':tomllib.loads((args.cw_source/'pyproject.toml').read_text())['project']['version'],
            'capability_source_sha256':hashlib.sha256((args.cw_source/'src/structure_capability/api.py').read_bytes()).hexdigest(),
            'seed_policy':'original deterministic authoring seeds retained',
            'block_registry_evidence':{'path':str(registry_path.relative_to(ROOT)),
                'sha256':hashlib.sha256(registry_path.read_bytes()).hexdigest()},
            'natural_placement':'unchanged; independent 500-block exclusion requires runtime adapter',
            'visual_state':'RUNTIME_TEST_REQUIRED','families':[]}
    if args.update_report:
        assert args.family, '--update-report requires explicit --family selections'
        previous=json.loads((ROOT/'tools/continuity_district_refit_report.json').read_text())
        report['families']=[f for f in previous['families'] if f['family'] not in args.family]
        if 'anomaly' in previous:report['anomaly']=previous['anomaly']
    # Fail closed before promotion; every family finishes all local gates first.
    for family in args.family or FAMILIES:
        source=next((ROOT/'kubejs/data/alfheim/structures/ancient'/family).glob('*.nbt'))
        request={'structure_id':'alfheim:refit_'+family,'source':str(source),
                 'operation':'generate','grade':3,'target_version':'1.20.1',
                 'purpose':{'kind':'ruined_elven_district','required_zones':['existing functional rooms'],
                            'required_routes':['existing streets, doors, stairs and jigsaw joins']},
                 'context':{'dimension':'mythicbotany:alfheim','terrain':'existing authored terraces'},
                 'preserve':['bounding boxes','socket NBT','loot NBT','foundations','walking clearance'],
                 'mutable':['upper wall relief','masonry courses','paving patterns','beam joints'],
                 'generation':{'kind':'alfheim_district_refit','family':family,'materialize_nbt':True}}
        audit=cap.audit(request)
        assert audit['audit']['status'] != 'FAIL',audit['audit']
        plan=cap.plan(request)
        result=cap.generate(request)
        assert result['generation']['status']=='LOCALLY_VALIDATED'
        layout=result['generated_layout']
        totals={k:sum(m[k] for m in layout['metrics']) for k in
                ('changed_cells','relief_cells','detail_before','detail_after')}
        totals['detail_ratio']=round(totals['detail_after']/max(1,totals['detail_before']),3)
        report['families'].append({'family':family,'totals':totals,**layout,
                                  'snapshot_id':result['snapshot']['snapshot_id']})
        print(f'{family}: {totals}',flush=True)
    if args.include_anomaly:
        from gen_ley_fracture import LeyFractureProvider
        cap.register_generator(LeyFractureProvider(stage/'generated'))
        result=cap.generate({'structure_id':'alfheim:ley_fracture','operation':'generate',
            'target_version':'1.20.1','grade':3,
            'purpose':{'kind':'independent_ley_anomaly','required_zones':['fracture','clear service apron']},
            'context':{'dimension':'mythicbotany:alfheim','terrain':'underground'},
            'integration_contracts':{'minimum_independent_footprint_gap':500,
                                     'natural_placement':'blocked pending reservation adapter'},
            'generation':{'kind':'alfheim_ley_fracture','materialize_nbt':True}})
        assert result['generation']['status']=='LOCALLY_VALIDATED'
        report['anomaly']={**result['generated_layout'],'snapshot_id':result['snapshot']['snapshot_id']}
    if args.promote:
        assert all(f['totals']['detail_ratio']>=8 for f in report['families']), \
            'Do not promote a family that misses the requested eightfold detail floor'
        for family in report['families']:
            for metric in family['metrics']:
                relative=Path('kubejs/data/alfheim/structures/ancient')/family['family']/(metric['piece']+'.nbt')
                data=(stage/'generated'/relative).read_bytes()
                assert hashlib.sha256(data).hexdigest()==metric['sha256'],relative
                (ROOT/relative).write_bytes(data)
        for relative in report.get('anomaly',{}).get('emitted_files',[]):
            destination=ROOT/relative;destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes((stage/'generated'/relative).read_bytes())
    target=ROOT/'tools/continuity_district_refit_report.json'
    target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(target)


if __name__=='__main__':main()
