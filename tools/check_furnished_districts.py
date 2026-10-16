"""Every furnishing cell must reproduce the bounded mutator; every other cell/NBT stays intact."""
import hashlib
import json
from collections import Counter
import nbt
from cw_furnish_districts import ROOT,BASE,STAGE,piece,validate
from district_furnishing_placement import apply,ROLES,verified_registry_ids

def main():
    report=json.loads((ROOT/'tools/district_furnishing_placement_report.json').read_text())
    records={r['file']:r for f in report['families'] for r in f['templates']}
    counts=Counter();families=Counter();fixtures=0;visited=set();templates=0
    for family in ROLES:
        for path in sorted((STAGE/'baseline'/BASE/family).glob('*.nbt')):
            before=nbt.load(path)[1];p=piece(before);placements=apply(p,family,path.stem);expected=p.to_nbt()
            rel=(BASE/family/path.name).as_posix();actual=nbt.load(ROOT/rel)[1]
            assert actual==expected,('Shipping/source mismatch',rel)
            changed,protected=validate(before,actual,placements);fixtures+=protected;templates+=1
            if not changed:assert rel not in records;continue
            r=records[rel];visited.add(rel)
            assert r['placements']==placements
            assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==r['sha256']
            for pl in placements:counts[pl['id']]+=1
            families[family]+=1
    assert set(records)==visited and set(families)==set(ROLES)
    assert set(counts)==verified_registry_ids(),('Missing furniture roles',counts)
    out={'status':'PASS','source_templates':templates,'furnished_templates':len(records),'placed_objects':sum(counts.values()),
        'families':dict(families),'objects':dict(counts),'protected_block_entities':fixtures,
        'contracts':['unchanged template size/cell ownership/entities','all original block entities and loot unchanged','original supported walking components remain connected','two-wide approach and wall backing','two objects per template maximum','all generated furnishing cells reproduce deterministic source']}
    (ROOT/'tools/district_furnishing_placement_static_report.json').write_text(json.dumps(out,indent=2)+'\n')
    print('FURNISHED DISTRICTS PASS:',json.dumps({k:v for k,v in out.items() if k not in ('objects','contracts')},ensure_ascii=False))

if __name__=='__main__':main()
