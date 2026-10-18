"""Verify emitted shop access, entity clearance, stock references and artifact hashes."""
from collections import deque
import hashlib
import json
from pathlib import Path
import zipfile
import nbt
from gen_act_one_refuge import ROOT,RES,REPORT,SERVICES,stock,shop


def main():
    manifest=json.loads((REPORT/'manifest.json').read_text())
    catalogue=json.loads((RES/'data/alfheim_companion/act_one_refuge_trades.json').read_text())
    assert catalogue==stock() and manifest['shops']==6 and manifest['offers']==43
    registry=json.loads((ROOT/'server/local/kubejs/export/registries/item.json').read_text())
    with zipfile.ZipFile(ROOT/'mods/Mine_and_Slash-1.20.1-6.4.7.jar') as jar:
        types={Path(n).stem for n in jar.namelist() if n.startswith('data/mmorpg/mmorpg_base_gear_types/') and n.endswith('.json')}
    for service,offers in catalogue['services'].items():
        assert service in SERVICES and offers
        for offer in offers:
            assert all(offer[key] in registry for key in ('cost_a','cost_b','result'))
            assert 1<=offer['max_uses']<=8 and 1<=offer['count_a']<=64 and 1<=offer['count_b']<=64
            if 'gear_type' in offer:assert offer['gear_type'] in types and offer['gear_level']==1 and offer['gear_rarity']=='common'
            if offer['result'].startswith(('mmorpg:potion/','mmorpg:buff_potion/','mmorpg:food/')):assert offer['tier']==0
    evidence=[]
    for row in manifest['pieces']:
        path=ROOT/row['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        root=nbt.load(path)[1];assert max(root['size'])<=48 and root['DataVersion']==3465
        if 'ashen_refuge/' not in row['path']:continue
        service=path.stem;index=SERVICES.index(service);p,pos=shop(index)
        assert root['blocks']==p.to_nbt()['blocks'] and root['palette']==p.to_nbt()['palette']
        assert len(root['entities'])==1 and root['entities'][0]['nbt']['RefugeService']==service
        assert root['entities'][0]['nbt']['id']=='alfheim_companion:elven_citizen'
        assert root['entities'][0]['pos']==pos
        states={tuple(b['pos']):root['palette'][b['state']]['Name'] for b in root['blocks']}
        nodes={(x,z) for x in range(13) for z in range(19)
               if states[(x,5,z)]==states[(x,6,z)]=='minecraft:air' and states[(x,4,z)]!='minecraft:air'}
        door=(6,18 if index%2==0 else 0);seen={door};q=deque([door]);assert door in nodes
        while q:
            x,z=q.popleft()
            for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
                nxt=x+dx,z+dz
                if nxt in nodes and nxt not in seen:seen.add(nxt);q.append(nxt)
        counter=(6,12 if index%2==0 else 6)
        assert counter in seen and (6,9) in seen,(service,'counter or merchant inaccessible')
        for x in range(5,8):assert (x,door[1]) in seen
        evidence.append({'service':service,'reachable_standing_cells':len(seen),'counter_access':True,'merchant_clearance':True,'three_wide_door':True})
    assert len(evidence)==6
    result={'acceptance':'static validated','templates':23,'shops':evidence,'offers':43,
            'checks':['source-to-NBT equality','file hashes','registry references','MMO gear types','explicit profession tier','counter and merchant reachability','three-wide doors'],
            'runtime_evidence':'tools/act_one_refuge_runtime_report.json; inspect its status separately'}
    (REPORT/'static_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print('ACT I REFUGE STATIC PASS: 23 templates, 6 accessible shops, 43 offers; native MMO IDs and gear types verified.')


if __name__=='__main__':main()
