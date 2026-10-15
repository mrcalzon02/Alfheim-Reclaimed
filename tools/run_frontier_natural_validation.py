"""One-site normal Frontier generation; test-only structure set, no /place command.

The salt selects a known reference site using vanilla's linear random-spread
algorithm. No runtime site search and no production structure_set is installed.
"""
import argparse,copy,hashlib,json,subprocess,sys
from pathlib import Path
import nbt,run_server
from probe_terraces import chunks
from review_inland_terrain import Reference,support,seed
from check_ancient_assembly import world_pos

ROOT=Path(__file__).resolve().parents[1]
SEED=3536368297089363045
SALT=1014208980
TARGET=(-91,40)
BOUNDS=(-1552,544,-1297,799)
SID='alfheim:frontier_stewardship'
CENSUS=ROOT/'tools/frontier_natural_runtime_census.json'

class LegacyRandom:
    def __init__(self,value):self.value=(value^0x5DEECE66D)&((1<<48)-1)
    def next(self,bits):
        self.value=(self.value*0x5DEECE66D+11)&((1<<48)-1)
        return self.value>>(48-bits)
    def integer(self,bound):
        assert bound>0
        if bound&(bound-1)==0:return (bound*self.next(31))>>31
        while True:
            bits=self.next(31);value=bits%bound
            if bits-value+bound-1<1<<31:return value

def candidate(rx,rz):
    random=LegacyRandom(SEED+rx*341873128712+rz*132897987541+SALT)
    return rx*32+random.integer(24),rz*32+random.integer(24)

def source_hashes():
    paths=list((ROOT/'kubejs/data/alfheim/structures/ancient/frontier_stewardship').glob('*.nbt'))
    paths+=list((ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/frontier_stewardship').glob('*.json'))
    paths+=[ROOT/'kubejs/data/alfheim/worldgen/structure/frontier_stewardship.json',
            ROOT/'kubejs/data/alfheim/tags/worldgen/biome/has_frontier_stewardship.json']
    paths+=list((ROOT/'kubejs/data/alfheim/loot_tables/chests/frontier').glob('*.json'))
    from gen_golden_meadow import build
    paths+=[ROOT/p for p in build()]
    from gen_native_feature_guards import build as guards
    paths+=[ROOT/p for p in guards()]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

def trial_set():
    return {'structures':[{'structure':SID,'weight':1}],
        'placement':{'type':'minecraft:random_spread','spacing':32,'separation':8,
                     'spread_type':'linear','salt':SALT}}

def check_candidates(reference_world):
    # Include the reference world's bootstrap chunks, not just the requested patch.
    full=[]
    for path in (reference_world/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
        for chunk in chunks(path):
            if chunk.get('Status')=='minecraft:full':full.append((chunk['xPos'],chunk['zPos']))
    assert full and candidate(TARGET[0]//32,TARGET[1]//32)==TARGET
    regions={(x//32,z//32) for px,pz in full for x in (px-9,px,px+9) for z in (pz-9,pz,pz+9)}
    nearby={candidate(rx,rz) for rx,rz in regions}
    assert not any(max(abs(x-px),abs(z-pz))<=9 for x,z in nearby-{TARGET} for px,pz in full),nearby
    return {'placement_regions_checked':len(regions),'reference_full_chunks':len(full),
            'other_candidates_outside_reference_plus_9_chunk_margin':True}

def review(world,hashes,candidates):
    assert seed(world)==SEED
    pack=world/'datapacks/frontier_natural_trial'
    assert json.loads((pack/'data/alfheim_trial/worldgen/structure_set/frontier.json').read_text(encoding='utf-8'))==trial_set()
    manifests=[(p,json.loads(p.read_text(encoding='utf-8'))) for p in (ROOT/'server').glob('manifest-*.json')]
    matches=[(p,m) for p,m in manifests if m.get('level_name')==world.name]
    _,manifest=max(matches,key=lambda pair:pair[0].name)
    assert manifest['exit_code']==manifest['harness_exit_code']==0
    assert not any('place structure' in c or 'place feature' in c for c in manifest['commands'])
    text=(ROOT/'server'/manifest['console']).read_text(encoding='utf-8',errors='replace')
    assert 'All dimensions are saved' in text and 'An unexpected error occurred' not in text
    tested_hashes={};frequency_difference=None
    from gen_native_feature_guards import PATH as apothecary_path
    for relative in hashes:
        published=(ROOT/relative).read_bytes();tested=(ROOT/'server'/relative).read_bytes()
        tested_hashes[relative]=hashlib.sha256(tested).hexdigest()
        if published!=tested:
            assert relative==apothecary_path,relative
            current=json.loads(published);runtime=json.loads(tested);normalised=copy.deepcopy(runtime)
            frequency_difference={'tested':runtime['placement'][:2],'published':current['placement'][:2]}
            normalised['placement'][:2]=current['placement'][:2]
            assert normalised==current,'Only the apothecary attempt/rareness stress setting may differ'
    starts=[];full=0
    for path in (world/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
        for chunk in chunks(path):
            if BOUNDS[0]//16<=chunk['xPos']<=BOUNDS[2]//16 and BOUNDS[1]//16<=chunk['zPos']<=BOUNDS[3]//16:
                assert chunk.get('Status')=='minecraft:full',(chunk['xPos'],chunk['zPos'],chunk.get('Status'))
                full+=1
            start=chunk.get('structures',{}).get('starts',{}).get(SID,{})
            if start.get('Children'):starts.append(dict(chunk=[chunk['xPos'],chunk['zPos']],children=len(start['Children']),bounds=start.get('BB')))
    assert full==256,full
    assert len(starts)==1 and starts[0]['chunk']==list(TARGET) and starts[0]['children']==6,starts
    result=subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/check_ancient_assembly.py'),str(world),
                    '--family','frontier_stewardship','--output',str(CENSUS)],capture_output=True,text=True,encoding='utf-8')
    if result.returncode:
        report=dict(status='rejected',world=world.name,console='server/'+manifest['console'],seed=str(SEED),
            source_sha256=hashes,tested_source_sha256=tested_hashes,
            apothecary_frequency_stress=frequency_difference,test_structure_set=trial_set(),candidate_checks=candidates,
            natural_starts=starts,forced_chunks=full,manual_placement_commands=0,server_exit_code=0,
            census_exit_code=result.returncode,census_error=result.stderr.strip(),
            limits='Census stopped at the first obstruction; no complete AIR or foundation pass. One chosen Golden Fields locality. Apothecary stress frequency differs from the sparse published rate. Production Frontier set remains disabled.')
        (ROOT/'tools/frontier_natural_runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(result.stderr,file=sys.stderr)
        raise SystemExit(result.returncode)
    census=json.loads(CENSUS.read_text(encoding='utf-8'))
    reference_meta=json.loads((ROOT/'tools/inland_terrain_reference.json').read_text(encoding='utf-8'))
    baseline=Reference(ROOT/'server'/reference_meta['world'],BOUNDS)
    actual=Reference(world,BOUNDS)
    pieces=[];all_points=[]
    for node in census['layout']:
        source=nbt.load(str(ROOT/f'kubejs/data/alfheim/structures/ancient/frontier_stewardship/{node["name"]}.nbt'))[1]
        sx,_,sz=map(int,source['size'])
        points=[world_pos((x,0,z),node['origin'],node['rotation']) for x in range(sx) for z in range(sz)]
        all_points+=points
        pieces.append(dict(name=node['name'],origin=node['origin'],rotation=node['rotation'],
                           native_below_foundation=support(actual,points),same_pose_without_trial=support(baseline,points)))
    report=dict(status='passed',world=world.name,console='server/'+manifest['console'],seed=str(SEED),
        source_sha256=source_hashes(),tested_source_sha256=tested_hashes,
        apothecary_frequency_stress=frequency_difference,test_structure_set=trial_set(),candidate_checks=candidates,
        test_pack_sha256={p.relative_to(world).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in pack.rglob('*') if p.is_file()},
        natural_starts=starts,forced_chunks=full,manual_placement_commands=0,server_exit_code=0,
        source_fingerprint=json.loads((ROOT/'tools/frontier_stewardship_manifest.json').read_text(encoding='utf-8'))['source_fingerprint'],
        members=census['pieces'],joins=census['clear_supported_joins'],verified_air_cells=census['verified_air_cells'],
        verified_foundation_cells=census['verified_foundation_cells'],
        native_below_foundation=support(actual,all_points),same_pose_without_trial=support(baseline,all_points),pieces=pieces,
        limits='One chosen Golden Fields locality, normal structure generation and beard_thin adaptation. The earlier same-seed reference shares the protected broad terrain but is not an otherwise identical decoration control. Test-only salt controls the site; natural frequency, other biomes, client appearance and production admission remain unproved.')
    (ROOT/'tools/frontier_natural_runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('FRONTIER NATURAL TRIAL:',json.dumps({k:report[k] for k in ('members','joins','native_below_foundation','same_pose_without_trial')}))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--world',default='validation-frontier-natural-20261014')
    ap.add_argument('--review-only',action='store_true');args=ap.parse_args()
    world=ROOT/'server'/args.world
    assert args.world.startswith('validation-frontier-natural-') and world.resolve().parent==(ROOT/'server').resolve()
    for script in ('check_field_review.py','check_frontier_stewardship.py','check_feature_order.py','check_biome_feature_coverage.py'):
        subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools'/script)],check=True)
    reference=ROOT/'server/validation-inland-terrain-baseline-20261014'
    assert seed(reference)==SEED
    candidates=check_candidates(reference);hashes=source_hashes()
    if args.review_only:review(world,hashes,candidates);return
    assert not world.exists(),'Use a fresh disposable world; refusing to overwrite evidence'
    pack=world/'datapacks/frontier_natural_trial';pack.mkdir(parents=True)
    (pack/'pack.mcmeta').write_text(json.dumps({'pack':{'pack_format':15,'description':'Disposable one-site Frontier natural trial'}}),encoding='utf-8')
    path=pack/'data/alfheim_trial/worldgen/structure_set/frontier.json';path.parent.mkdir(parents=True)
    path.write_text(json.dumps(trial_set(),indent=2)+'\n',encoding='utf-8')
    commands=[(5,'say frontier normal terrain adaptation trial'),
        (2,'execute in mythicbotany:alfheim run forceload add -1552 544 -1297 799'),
        (70,'save-all flush'),(5,'execute in mythicbotany:alfheim run forceload remove all'),(5,'stop')]
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run(str(SEED),world.name,8,commands,600)
    finally:
        props.write_bytes(original)
        (ROOT/'server/config/jade/server-plugin-overrides.json').write_bytes(
            subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    review(world,hashes,candidates)

if __name__=='__main__':main()
