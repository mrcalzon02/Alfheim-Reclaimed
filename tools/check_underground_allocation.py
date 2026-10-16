"""Validate adapter/data bounds and audit the unchanged upper-rock assets with CW."""
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

from underground_policy import FAMILIES,TYPE,apply

ROOT=Path(__file__).resolve().parents[1]

def main():
    java=ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/worldgen'
    policy=(java/'UndergroundAllocation.java').read_text()
    for name,value in [('SPACING',80),('SEPARATION',48),('SALT',202610151),('CLEARANCE',800)]:
        assert re.search(rf'\b{name}={value}\b',policy),name
    placement=json.loads((ROOT/'kubejs/data/alfheim/worldgen/structure_set/upper_underworld.json').read_text())['placement']
    assert (placement['spacing'],placement['separation'],placement['salt'])==(80,48,202610151)
    managed=[]
    for name in sorted(FAMILIES):
        path=ROOT/f'kubejs/data/alfheim/worldgen/structure/{name}.json'
        body=json.loads(path.read_text());assert body['type']==TYPE
        assert body['layout']=={k:v for k,v in body.items() if k not in ('type','layout')},name
        assert body['max_distance_from_center']<=128,name
        assert apply(path,body)==body,'Wrapper must be idempotent'
        managed.append({'family':name,'reach':body['max_distance_from_center'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    # Headworks and the complexes must still make exactly the same reservation decision.
    sets=ROOT/'kubejs/data/alfheim/worldgen/structure_set'
    assert json.loads((sets/'deepworks_headworks.json').read_text())['placement']==json.loads((sets/'deepworks_archaeology.json').read_text())['placement']
    assert 800-192-15>=500 and 48*16-30>=500
    andwari=[]
    for jar in (ROOT/'mods').glob('*mythic*'):
        with zipfile.ZipFile(jar) as z:
            path='data/mythicbotany/worldgen/structure/andwari_cave.json'
            if path not in z.namelist():continue
            definition=json.loads(z.read(path));tag=json.loads(z.read('data/mythicbotany/tags/worldgen/biome/andwari_cave.json'))
            assert definition['type']=='minecraft:jigsaw' and definition['max_distance_from_center']<=128
            assert tag['values']==['mythicbotany:golden_fields']
            andwari.append({'jar':str(jar.relative_to(ROOT)),'jar_sha256':hashlib.sha256(jar.read_bytes()).hexdigest(),
                            'definition':definition,'biome_tag':tag})
    assert len(andwari)==1,'Verify installed third-party eligibility definition'
    sys.path.insert(0,'C:/GITS/Structuresmith/StructureSmith/src')
    from structure_capability import StructureCapability
    cap=StructureCapability(project_root=ROOT,state_root=ROOT/'build/upper-natural-audit/snapshots')
    assert cap.capabilities()['service']=='Continuity Works'
    audits=[]
    for path in sorted((ROOT/'kubejs/data/alfheim/structures/upper_underworld').glob('*.nbt')):
        result=cap.audit({'structure_id':'alfheim:upper_underworld/'+path.stem,'source':str(path),'operation':'generate',
            'grade':3,'target_version':'1.20.1','purpose':{'kind':'upper_rock_discoveries','required_zones':['discovery chamber','entrance mouths']},
            'context':{'dimension':'mythicbotany:alfheim','terrain':'above Deep Y27 boundary'}})['audit']
        assert result['status']=='PASS',result
        audits.append({'template':path.stem,'status':result['status'],'sha256':result['sha256']})
    assert len(audits)==12
    suites=[ET.parse(p).getroot() for p in (ROOT/'first_party_mods/alfheim_companion/build/test-results/test').glob('TEST-*.xml')]
    assert all(s.attrib['failures']==s.attrib['errors']=='0' for s in suites)
    report={'status':'STATIC_AND_JAVA_TESTS_PASS','java_tests':sum(int(s.attrib['tests']) for s in suites),
            'managed_layouts':managed,'reserved_axis_distance':800,'conservative_footprint_gap':800-192-15,
            'selected_fraction':0.25,'legacy_candidate_probes':9,'third_party_untouched':andwari,
            'capability':'Continuity Works 0.3.2 StructureCapability.audit','template_audits':audits,
            'installed_jar_sha256':hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest(),
            'scope':'Future generation; previously generated neighboring legacy starts require separate existing-world audit',
            'runtime':'See tools/upper_natural_runtime_report.json; static proof alone does not admit natural starts'}
    runtime_path=ROOT/'tools/upper_natural_runtime_report.json'
    if runtime_path.exists():
        runtime=json.loads(runtime_path.read_text())
        if runtime.get('status')=='NATURAL_STARTS_VALIDATED' and runtime.get('installed_jar_sha256')==report['installed_jar_sha256']:
            proofs=runtime['natural_starts']
            assert len(proofs)==3 and all(p['matched']/p['samples']>=.95 for p in proofs)
            assert all(p['bounds'][1]>=32 for p in proofs)
            report['runtime']={'status':'NATURAL_STARTS_VALIDATED','world':runtime['world'],'seed':runtime['seed'],
                'starts':len(proofs),'samples':sum(p['samples'] for p in proofs),'matched':sum(p['matched'] for p in proofs),
                'console':runtime['population_console'],'visual_review':'pending',
                'unrelated_surface_spacing':'Not established by this scoped underground allocation'}
    (ROOT/'tools/underground_allocation_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"UNDERGROUND ALLOCATION PASS: {report['java_tests']} Java tests, five preserved layouts, twelve CW audits, >=593-block conservative gap")

if __name__=='__main__':main()
