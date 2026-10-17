"""Validate barter progression against the pack's authored material catalogue."""
import json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOGUE=ROOT/'first_party_mods/alfheim_companion/src/main/resources/data/alfheim_companion/elven_trades.json'

def main():
    trades=json.loads(CATALOGUE.read_text())
    materials={f"alfheim:{r['id']}":r for r in json.loads((ROOT/'tools/items_manifest.json').read_text())['items']}
    roles=json.loads((ROOT/'tools/elven_society_manifest.json').read_text())['roles']
    assert set(trades['roles'])=={r['id'] for r in roles}
    assert trades['restock_ticks']==24000
    models=set()
    for jar in (ROOT/'mods').glob('*.jar'):
        with zipfile.ZipFile(jar) as z:
            for name in z.namelist():
                if '/models/item/' in name and name.endswith('.json'):
                    ns,path=name.removeprefix('assets/').split('/models/item/',1);models.add(ns+':'+path[:-5])
    count=0
    for role,offers in trades['roles'].items():
        assert len(offers)==6,role
        assert len({o['result'] for o in offers})==6,role
        for offer in offers:
            payment=materials[offer['cost_a']]
            assert payment.get('tier') and 7<=payment['era']<=10
            assert offer['cost_b'].startswith('ars_nouveau:')
            assert offer['cost_b'].endswith(('_essence','source_gem'))
            assert 1<=offer['count_a']<=64 and 1<=offer['count_b']<=64
            assert 1<=offer['count']<=64 and 1<=offer['max_uses']<=8
            for key in ('cost_a','cost_b','result'):
                assert offer[key] in materials or offer[key] in models,(role,key,offer[key])
            output=materials.get(offer['result'])
            if output:
                assert not output.get('tier') and not output['id'].startswith('incomplete_')
                assert output['era']==payment['era'],(role,'must already have completed the same chain')
                assert offer['count']==1,'Do not multiply intermediate outputs'
            assert offer['result'] not in (offer['cost_a'],offer['cost_b'])
            count+=1
    assert count==72
    print('ELVEN TRADES STATIC PASS: 12 roles / 72 offers; verified item references; same-chain finished payments; Source reagents; bounded stock')

if __name__=='__main__':main()
