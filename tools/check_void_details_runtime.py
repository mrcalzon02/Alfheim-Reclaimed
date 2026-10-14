"""Read-only, controlled configured-feature proof; not natural-frequency evidence."""
from collections import Counter
import hashlib,json
from pathlib import Path
from probe_terraces import chunks,section_blocks

ROOT=Path(__file__).resolve().parents[1]
CASES=[('shatter_anchors','shatterfields','shardbreccia',('anchorstone','seamstone')),
       ('prism_crowns','prism_drift','aetherquartzite',('prismstone',)),
       ('root_aprons','rootfall','hollowheart',('rootfossil','resinshale')),
       ('mourning_steles','sepulchral_reach','mourning',('epitaph','oathstone')),
       ('astralite_flecks','starless_reach','nightmantle',('astralite',))]

def census(world):
    results=[Counter() for _ in CASES]
    for file in (world/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
        for c in chunks(file):
            if not (64<=c['xPos']<=77 and 64<=c['zPos']<=65):continue
            for sec in c.get('sections',[]):
                if not (11<=int(sec['Y'])<=13):continue
                for i,name in enumerate(section_blocks(sec) or []):
                    x=c['xPos']*16+(i&15);z=c['zPos']*16+((i>>4)&15);y=int(sec['Y'])*16+(i>>8)
                    if not (1024<=z<=1054 and 180<=y<=216):continue
                    for case,(_,_,_,stones) in enumerate(CASES):
                        if 1024+case*48<=x<=1054+case*48 and name in {'alfheim:'+s+'_livingrock' for s in stones}:
                            results[case][name]+=1
    records=[]
    for case,counts in zip(CASES,results):
        feature,biome,host,stones=case
        assert sum(counts.values())>0,('configured feature produced no signature blocks',feature)
        records.append(dict(feature='alfheim:void/'+feature,biome='alfheim:'+biome,signature_blocks=dict(counts)))
    paths=[ROOT/f'kubejs/data/alfheim/{kind}/void/{case[0]}.json' for case in CASES
           for kind in ('worldgen/configured_feature','worldgen/placed_feature')]
    paths += [ROOT/f'kubejs/data/alfheim/forge/biome_modifier/void_{case[0]}.json' for case in CASES]
    report={'world':world.name,'status':'controlled_configured_features_passed','cases':records,
        'limits':'Commands place configured features on artificial native-stone hosts. Effective biome injection is checked separately; natural site success, frequency and client appearance are not established.',
        'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (ROOT/'tools/void_details_runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('VOID DETAIL CONTROLLED PASS:',json.dumps(records))

if __name__=='__main__':
    import sys
    census(Path(sys.argv[1]))
