"""Decorative coverage, full item assemblies, recipe uniqueness and face checks."""
import json
from pathlib import Path
from check_field_review import overlaps
from gen_elven_decor import ROOT,RES,SPECS

def main():
    m=json.loads((ROOT/'tools/elven_decor_manifest.json').read_text());signatures=set();models=0;categories={}
    for key,obj in m['objects'].items():
        categories[obj['category']]=categories.get(obj['category'],0)+1
        for part in obj['parts']:
            doc=json.loads((RES/f'assets/alfheim_leyworks/models/block/{part["model"]}.json').read_text())
            assert doc['elements'] and overlaps(doc)==0,key
            for el in part['source_boxes']:assert all(0<=a<b<=16 for a,b in zip(el['from'],el['to'])),key
            models+=1
        item=json.loads((RES/f'assets/alfheim_leyworks/models/item/{key}.json').read_text())
        if len(obj['parts'])==2:
            assert item['elements'] and overlaps(item)==0
            assert all(all(0<=a<b<=16 for a,b in zip(e['from'],e['to'])) for e in item['elements'])
        r=json.loads((RES/f'data/alfheim_leyworks/recipes/{key}.json').read_text());assert r==obj['recipe']
        signature=json.dumps({'pattern':r['pattern'],'key':r['key']},sort_keys=True);assert signature not in signatures;signatures.add(signature)
        loot=json.loads((RES/f'data/alfheim_leyworks/loot_tables/blocks/{key}.json').read_text())
        if len(obj['parts'])==2:assert any(c.get('properties')=={'part':'base'} for c in loot['pools'][0]['conditions'])
    assert len(m['objects'])==38 and models==52
    out={'status':'STATIC_PASS','objects':38,'block_model_parts':52,'complete_assembly_item_models':14,'categories':categories,'recipes':len(signatures),'coplanar_overlaps':0}
    (ROOT/'tools/elven_decor_static_report.json').write_text(json.dumps(out,indent=2)+'\n')
    print('ELVEN DECOR STATIC PASS:',json.dumps(out))

if __name__=='__main__':main()
