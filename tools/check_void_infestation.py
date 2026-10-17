"""Read back the emitted Titan infestation; source checks are not gameplay evidence."""
import hashlib,json
from pathlib import Path
import nbt
from gen_monstrosities import HABITATS,PARASITES,CRYSTALS

ROOT=Path(__file__).resolve().parents[1]

def main():
    corpses=[]
    for decay,name in enumerate(('bio_titan','bio_titan_desiccated','bio_titan_ossified')):
        path=ROOT/f'kubejs/data/alfheim/structures/void_war/{name}.nbt'
        root=nbt.load(path)[1]
        assert list(root['size'])==[47,48,47]
        grid={tuple(b['pos']):root['palette'][b['state']] for b in root['blocks']}
        spawners=[b for b in root['blocks'] if root['palette'][b['state']]['Name']=='minecraft:spawner']
        mounds=[s for s in grid.values() if s['Name']=='alfheim_companion:maggot_mound']
        assert len(spawners)==4 and len(mounds)==16
        assert {s['Properties']['decay'] for s in mounds}=={str(decay)}
        assert {b['nbt']['SpawnData']['entity']['id'].split(':')[1] for b in spawners}==set(PARASITES)
        for b in spawners:
            data=b['nbt'];assert data['SpawnData']['entity']['MonstrosityVariant']==decay
            for key in ('Delay','MinSpawnDelay','MaxSpawnDelay','SpawnCount','MaxNearbyEntities','RequiredPlayerRange','SpawnRange'):
                assert isinstance(data[key],nbt.Short),key
            assert data['SpawnCount']==1 and data['MaxNearbyEntities']<=3
            assert data['MinSpawnDelay']==500 and data['MaxSpawnDelay']==1000
            x,y,z=b['pos']
            # Each nest has empty columns beside its central cage and a three-wide approach.
            for dx in (-1,1):
                for h in (5,6,7):assert grid[(x+dx,h,z)]['Name']=='minecraft:air'
            for zz in range(min(z,23),max(z,23)+1):
                if zz==z:continue
                for xx in range(x-1,x+2):
                    for h in (5,6,7):assert grid[(xx,h,zz)]['Name']=='minecraft:air'
        corpses.append({'template':name,'spawners':4,'mounds':16,'variant':decay,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    report={'status':'LOCALLY_VALIDATED_RUNTIME_REQUIRED','corpse_templates':corpses,
            'natural_habitat_entries':sum(map(len,HABITATS.values())),
            'crystal_habitats':{k:HABITATS[k] for k in sorted(CRYSTALS)},
            'spawner_only_parasites':sorted(PARASITES),'habitats':HABITATS,
            'gameplay_and_listening_review':'pending; no live server or client validation in this change'}
    (ROOT/'tools/void_infestation_static_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('TITAN INFESTATION STATIC PASS: 3 unchanged footprints, 12 typed bounded spawners, 48 decay-matched mounds and open approaches')

if __name__=='__main__':main()
