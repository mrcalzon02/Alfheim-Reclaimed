"""Effective decoration and naturally enabled structures, including Forge modifiers.

Configuration coverage is not proof of visual density. Keep those claims separate.
"""
import glob,hashlib,json
from pathlib import Path
from check_feature_order import Sources,CLIENT_JAR,DATA,STEPS

ROOT=Path(__file__).resolve().parents[1]

def main():
    src=Sources();src.add_jar(CLIENT_JAR)
    for path in sorted(glob.glob('mods/*.jar')):src.add_jar(path)
    src.add_datapack(DATA,'kubejs/data');src.apply_modifiers()
    data=ROOT/'kubejs/data/alfheim'
    layer=json.loads((ROOT/'kubejs/data/mythicbotany/libx/biome_layer/alfheim.json').read_text(encoding='utf-8'))
    home_biomes={entry['biome'] for entry in layer['biomes']}
    assert home_biomes<=src.biomes.keys(),('biome definitions missing',home_biomes-src.biomes.keys())
    enabled=set()
    for path in (data/'worldgen/structure_set').glob('*.json'):
        enabled.update(e['structure'] for e in json.loads(path.read_text(encoding='utf-8'))['structures'])
    structures={}
    for path in (data/'worldgen/structure').glob('*.json'):
        doc=json.loads(path.read_text(encoding='utf-8'));sid='alfheim:'+path.stem
        structures[sid]=(src.biomes_in(doc['biomes']),sid in enabled)
    rows=[]
    for bid in sorted(src.biomes):
        if bid not in home_biomes:continue
        steps=src.biomes[bid]
        vegetation=sorted(set(src.resolve(steps[9]))) if len(steps)>9 else []
        by_step={name:sorted(set(src.resolve(steps[i]))) if i<len(steps) else [] for i,name in enumerate(STEPS)}
        details=sorted(set(by_step['local_modifications']+by_step['surface_structures']))
        natural=sorted(s for s,(biomes,active) in structures.items() if active and bid in biomes)
        controlled=sorted(s for s,(biomes,active) in structures.items() if not active and bid in biomes)
        rows.append(dict(biome=bid,vegetation=vegetation,surface_details=details,features_by_step=by_step,
                         natural_structures=natural,controlled_only_structures=controlled))
    expected_void={'shatterfields':'shatter_anchors','prism_drift':'prism_crowns','rootfall':'root_aprons',
                   'sepulchral_reach':'mourning_steles','starless_reach':'astralite_flecks'}
    for biome,feature in expected_void.items():
        row=next(r for r in rows if r['biome']=='alfheim:'+biome)
        assert 'alfheim:void/'+feature in row['surface_details'],('void geology missing from effective features',biome)
    for biome,feature in {'shatterfields':'shatter_bramble','rootfall':'rootfall_rootlet',
                          'prism_drift':'prism_lichen','sepulchral_reach':'mourning_reed'}.items():
        row=next(r for r in rows if r['biome']=='alfheim:'+biome)
        assert 'alfheim:'+feature in row['vegetation'],('void remnant absent from effective modifiers',biome)
    for bid in ('alfheim:void_shore','alfheim:void_verge'):
        row=next(r for r in rows if r['biome']==bid)
        assert {'alfheim:void_bramble','alfheim:void_thornbush'}<=set(row['vegetation']),bid
        assert {'alfheim:thorn_gate','alfheim:shore_memorial_court'}<=set(row['natural_structures']),bid
    for biome,feature in (('alfheim:mistbark_shore','mistbark_stone_scatter'),
                          ('alfheim:void_shore','void_shore_wrack')):
        row=next(r for r in rows if r['biome']==biome)
        assert 'alfheim:'+feature in row['vegetation'],('shore detail absent from effective modifiers',biome,feature)
    for feature in ('void_bramble','void_thornbush'):
        config=json.loads((data/f'worldgen/configured_feature/{feature}.json').read_text(encoding='utf-8'))['config']
        supports=config['feature']['placement'][0]['predicate']['predicates'][1]['blocks']
        assert {'alfheim:riftchalk_livingrock','alfheim:riftshale_livingrock','minecraft:sand','minecraft:gravel'}<=set(supports),('void surface substrate missing',feature)
        assert config['tries']==20 and config['xz_spread']==6
        placed=json.loads((data/f'worldgen/placed_feature/{feature}.json').read_text(encoding='utf-8'))
        assert placed['placement'][0]=={'type':'minecraft:count','count':3}
    gaps=[r['biome'] for r in rows if not r['vegetation']]
    sparse=[r['biome'] for r in rows if not any(f!='botania:mystical_flowers' for f in r['vegetation'])]
    report={'scope':'effective first-party biome configuration; natural density and visual quality require field review',
            'only_generic_flowers':sparse,
            'biomes':len(rows),'no_vegetation':gaps,'unmodelled_modifiers':src.unmodelled,'rows':rows}
    (ROOT/'tools/biome_feature_coverage.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# Custom biome feature coverage','',
           'Configuration audit, 2026-10-14. Includes jar defaults, datapack overrides and Forge feature modifiers. Counts are distinct features and first-party structures, not observed density. Controlled-only assemblies do not generate naturally.','',
           '| Biome | Vegetation features | Surface detail features | Natural structures | Controlled-only structures |',
           '|---|---:|---:|---:|---:|']
    for r in rows:lines.append(f"| {r['biome']} | {len(r['vegetation'])} | {len(r['surface_details'])} | {len(r['natural_structures'])} | {len(r['controlled_only_structures'])} |")
    lines+=['','No vegetation configured: '+(', '.join(gaps) if gaps else 'none')+'.',
            '', 'Only generic mystical flowers in the vegetation step: '+(', '.join(sparse) if sparse else 'none')+'. Sparse vegetation is not missing overall feature coverage. The earlier table omitted the local-modifications stage; all five outer void regions have distinct geological details. The current committed additions also supply Shatter Bramble, Petrified Rootlet, Prism Lichen and Mourning Stone-Reed to four regions. Starless Reach retains its bare terminal character. All eleven generation stages are listed in the JSON audit.',
            '', 'Void identities: Shatterfields anchor needles, Prism Drift crystal crowns, Rootfall fossil root aprons, Sepulchral Reach mourning steles, and Starless Reach astralite flecks. Source registration alone does not establish their natural success rate or visual quality; controlled placement evidence is recorded separately.',
            '', 'Void Shore and Void Verge both receive bramble and thorn patches plus Thorn Gate and Shore Memorial Court. Their substrate filter now includes their actual chalk/shale/sand/gravel surfaces. This corrects a placement blocker; it does not establish final natural density.',
            '', 'Broad density, noise, biome selection and surface rules are unchanged. See tools/biome_feature_coverage.json for exact feature and structure IDs.']
    shore_path=ROOT/'tools/shore_detail_runtime.json'
    shore=json.loads(shore_path.read_text(encoding='utf-8')) if shore_path.exists() else {}
    shore_hashes=shore.get('source_sha256',{})
    shore_current=bool(shore_hashes) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in shore_hashes.items())
    shore_status=(f"Controlled saved-world validation passes {len(shore['cases'])} cases and {shore['saved_log_axis_states']} log axis/default states. Two 64-chunk natural-generation samples also save successfully; natural counts cannot identify individual decorations or establish their frequency."
                  if shore_current else 'Runtime support tests remain pending for the current source.')
    lines+=['','Shore detail additions: Mistbark stone scatter and Void Shore chalk/shale wrack. Driftwood now accepts sand, gravel and native shoreline stone, uses horizontal logs and requires support at every cell. '+shore_status+' Client review remains pending; see `SHORE_DETAIL_REVIEW.md`.']
    runtime_path=ROOT/'tools/void_undergrowth_runtime.json'
    if runtime_path.exists():
        runtime=json.loads(runtime_path.read_text(encoding='utf-8'))
        hashes=runtime.get('feature_sha256',{})
        if hashes and all(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected for path,expected in hashes.items()):
            lines+=['','## Observed void undergrowth','',
                f"Fresh test world `{runtime['world']}`: {runtime['natural_sample_chunks']} sampled natural chunks. These counts include naturally placed undergrowth and any natural court plants; controlled pads are outside this sample.",'',
                '| Biome | Plant | Saved blocks |','|---|---|---:|']
            for row in runtime['natural_plants']:lines.append(f"| {row['biome']} | {row['plant']} | {row['count']} |")
            lines+=['','Both plant types also survived the controlled chalk, shale, sand and gravel tests after block updates. A few plants cross the adjoining ocean biome boundary within patch spread. This local sample proves generation works; it does not establish final visual density or populate existing chunks.']
    tested=set()
    detail_path=ROOT/'tools/void_details_runtime.json'
    if detail_path.exists():
        detail=json.loads(detail_path.read_text(encoding='utf-8'));hashes=detail.get('source_sha256',{})
        current_cases=[]
        for case in detail['cases']:
            name=case['feature'].split('/')[-1]
            relevant={p:h for p,h in hashes.items() if p.endswith('/'+name+'.json') or p.endswith('/void_'+name+'.json')}
            if len(relevant)==3 and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in relevant.items()):
                current_cases.append(case['feature'])
        if current_cases:
            lines+=['','## Controlled current-detail validation','',
                f"World `{detail['world']}`: current-source configured features with saved signature blocks on native-stone hosts: "+', '.join(current_cases)+'.','',
                'These are artificial-host tests of configured features. Outer rarity, natural site success, visual quality and overall frequency still require field review. They are not natural-frequency evidence.']
            tested.update(current_cases)
        remnant_hashes={p:h for p,h in hashes.items() if '/void/' not in p and '/void_' not in p}
        if remnant_hashes and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in remnant_hashes.items()):
            lines+=['','The four current remnant features also survived controlled placement and block updates in that world.']
    formation_path=ROOT/'tools/void_formation_runtime.json'
    if formation_path.exists():
        formation=json.loads(formation_path.read_text(encoding='utf-8'));hashes=formation.get('source_sha256',{})
        if hashes and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items()):
            lines+=['','## Controlled formation support and underside validation','',
                f"World `{formation['world']}`: {len(formation['cases'])} formations produced saved blocks on correct hosts and rejected wrong hosts, unsupported air and water or oversized shelves. All upright/hanging columns remain attached to native support.",'',
                'Test-only wrappers retain production offsets and the 32-step underside scan. The hanging formations accept thin shelves and reject 37-block shelves. Outer rarity, heightmap and biome filters are omitted; natural frequency and client appearance remain untested.']
            tested.update('alfheim:void/'+case['feature'] for case in formation['cases'])
    pending=sorted({feature for row in rows for feature in row['surface_details'] if feature.startswith('alfheim:void/')} - tested)
    lines+=['','Geological details without current controlled placement proof in this report: '+(', '.join(pending) if pending else 'none')+'.']
    smoke_path=ROOT/'tools/void_merged_load_smoke.json'
    if smoke_path.exists():
        smoke=json.loads(smoke_path.read_text(encoding='utf-8'));hashes=smoke.get('source_sha256',{})
        if hashes and all(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected for path,expected in hashes.items()):
            lines+=['','The merged geological datapack passes a dedicated-server registry/startup smoke test. This proves codec loading, not controlled placement of the additional formations. The staged native Java structure type is not claimed built or deployed.']
    (ROOT/'alfheim_reclaimed_design/BIOME_FEATURE_COVERAGE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('COVERAGE:',len(rows),'biomes;',len(gaps),'without vegetation:',', '.join(gaps))

if __name__=='__main__':main()
