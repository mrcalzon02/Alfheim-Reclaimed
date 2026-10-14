"""Read-only census of natural void chunks and eight controlled substrate pads."""
import hashlib,json
from collections import Counter
from pathlib import Path
from probe_terraces import chunks,section_blocks,biome_at

ROOT=Path(__file__).resolve().parents[1]
SUBSTRATES=['alfheim:riftchalk_livingrock','alfheim:riftshale_livingrock','minecraft:sand','minecraft:gravel']
PLANTS=['alfheim:bramble','mmorpg:thorn_bush']

def census(world):
    natural=Counter();natural_chunks=0;pads=Counter()
    for file in (world/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
        for c in chunks(file):
            cx,cz=c['xPos'],c['zPos'];is_natural=-8<=cx<=-1 and -28<=cz<=-21
            if is_natural:natural_chunks+=1
            for sec in c.get('sections',[]):
                pal=sec.get('block_states',{}).get('palette',[])
                if not any(p.get('Name') in PLANTS for p in pal):continue
                blocks=section_blocks(sec)
                for i,name in enumerate(blocks or []):
                    if name not in PLANTS:continue
                    x=i&15;z=(i>>4)&15;y=int(sec['Y'])*16+(i>>8);wx=cx*16+x;wz=cz*16+z
                    if is_natural:
                        bid=biome_at(c.get('sections',[]),y,x,z)
                        natural[(bid,name)]+=1
                    if 1024<=wx<1152 and 1024<=wz<1088 and y==201:
                        col=(wx-1024)//32;row=(wz-1024)//32
                        assert blocks[i-256]==SUBSTRATES[col],('plant lacks its expected support',wx,y,wz)
                        pads[(SUBSTRATES[col],PLANTS[row],name)]+=1
    results=[]
    for substrate in SUBSTRATES:
        for plant in PLANTS:
            count=pads[(substrate,plant,plant)]
            assert count>0,('feature did not survive placement',substrate,plant)
            results.append(dict(substrate=substrate,plant=plant,surviving_blocks=count))
    report={'world':world.name,'controlled_pads':results,'natural_sample_chunks':natural_chunks,
            'natural_plants':[dict(biome=b,plant=p,count=n) for (b,p),n in sorted(natural.items())],
            'limits':'One seed and local sample; counts do not establish final visual density. Pads use fillbiome then place feature and save after updates.'}
    report['feature_sha256']={str(path.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(path.read_bytes()).hexdigest()
        for kind in ('configured_feature','placed_feature') for feature in ('void_bramble','void_thornbush')
        for path in [ROOT/f'kubejs/data/alfheim/worldgen/{kind}/{feature}.json']}
    (ROOT/'tools/void_undergrowth_runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('VOID UNDERGROWTH PASS:',json.dumps(report))

if __name__=='__main__':
    import sys
    census(Path(sys.argv[1]))
