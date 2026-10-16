"""Deterministic furnishing geometry, recipe and utility coverage checks."""
import hashlib
import json
from pathlib import Path
from check_field_review import overlaps
from gen_district_furnishings import ROOT,RES,build

def main():
    m=json.loads((ROOT/'tools/district_furnishings_manifest.json').read_text());signatures=set();hashes={}
    for key,entry in m['objects'].items():
        model=json.loads((RES/f'assets/alfheim_leyworks/models/block/{key}.json').read_text())
        assert model['elements'] and overlaps(model)==0,key
        for e in entry['source_boxes']:
            assert all(0<=a<b<=16 for a,b in zip(e['from'],e['to'])),key
        recipe=RES/f'data/alfheim_leyworks/recipes/{key}.json';r=json.loads(recipe.read_text())
        assert r['result']['item']==entry['id']
        signature=json.dumps({'pattern':r['pattern'],'key':r['key']},sort_keys=True)
        assert signature not in signatures,key;signatures.add(signature)
        ingredients={i['item'] for i in r['key'].values()}
        assert 'ars_nouveau:source_gem' in ingredients
        assert ('alfheim:purified_titan_resin' if isinstance(entry['utility'],int) else 'alfheim:tempered_war_lattice') in ingredients
        hashes[str(recipe.relative_to(ROOT)).replace('\\','/')]=hashlib.sha256(recipe.read_bytes()).hexdigest()
    assert len(m['objects'])==11
    assert sum(isinstance(e['utility'],int) for e in m['objects'].values())==6
    # Exact generated Java shapes link the authored boxes to collision.
    generated=build();java=ROOT/'first_party_mods/alfheim_leyworks/src/main/java/com/continuityworks/leyworks/DistrictFurnishingShapes.java'
    assert java.read_bytes()==generated['JAVA/DistrictFurnishingShapes.java']
    java_dir=java.parent
    assert 'valid(access,p)' in (java_dir/'DistrictStationBlock.java').read_text()
    report=dict(status='STATIC_PASS',functional_models=11,storage_profiles=6,station_types=5,
        recipes=11,distinct_crafting_inputs=True,coplanar_overlaps=0,recipe_sha256=hashes)
    (ROOT/'tools/district_furnishings_static_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DISTRICT FURNISHINGS PASS: 11 recipes/models, 6 storage profiles, 5 native stations, no coplanar faces')

if __name__=='__main__':main()
