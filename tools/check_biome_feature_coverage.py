"""Effective decoration and naturally enabled structures, including Forge modifiers.

Configuration coverage is not proof of visual density. Keep those claims separate.
"""
import glob,hashlib,json
from pathlib import Path
from check_feature_order import Sources,CLIENT_JAR,DATA

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
        natural=sorted(s for s,(biomes,active) in structures.items() if active and bid in biomes)
        controlled=sorted(s for s,(biomes,active) in structures.items() if not active and bid in biomes)
        rows.append(dict(biome=bid,vegetation=vegetation,natural_structures=natural,controlled_only_structures=controlled))
    for bid in ('alfheim:void_shore','alfheim:void_verge'):
        row=next(r for r in rows if r['biome']==bid)
        assert {'alfheim:void_bramble','alfheim:void_thornbush'}<=set(row['vegetation']),bid
        assert {'alfheim:thorn_gate','alfheim:shore_memorial_court'}<=set(row['natural_structures']),bid
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
           'Configuration audit, 2026-10-13. Includes jar defaults, datapack overrides and Forge feature modifiers. Counts are distinct features and first-party structures, not observed density. Controlled-only assemblies do not generate naturally.','',
           '| Biome | Vegetation features | Natural structures | Controlled-only structures |',
           '|---|---:|---:|---:|']
    for r in rows:lines.append(f"| {r['biome']} | {len(r['vegetation'])} | {len(r['natural_structures'])} | {len(r['controlled_only_structures'])} |")
    lines+=['','No vegetation configured: '+(', '.join(gaps) if gaps else 'none')+'.',
            '', 'Only generic mystical flowers in the vegetation step: '+(', '.join(sparse) if sparse else 'none')+'. These outer void areas have geology and ruin identities, but do not yet have distinct vegetation features. They should remain sparse; final visual coverage is not signed off.',
            '', 'Void Shore and Void Verge both receive bramble and thorn patches plus Thorn Gate and Shore Memorial Court. Their substrate filter now includes their actual chalk/shale/sand/gravel surfaces. This corrects a placement blocker; it does not establish final natural density.',
            '', 'Broad density, noise, biome selection and surface rules are unchanged. See tools/biome_feature_coverage.json for exact feature and structure IDs.']
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
    (ROOT/'alfheim_reclaimed_design/BIOME_FEATURE_COVERAGE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('COVERAGE:',len(rows),'biomes;',len(gaps),'without vegetation:',', '.join(gaps))

if __name__=='__main__':main()
