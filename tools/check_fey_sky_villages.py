"""Read emitted tiles, inhabited bark fronts and connected village routes. No runtime claims."""
import hashlib,json
from collections import deque
from pathlib import Path
import nbt
from gen_fey_sky_villages import ROOT,CULTURES,plan,village

def read_village(kind,variant):
    grid={};homes=[]
    for gx in range(2):
        for gz in range(2):
            root=nbt.load(ROOT/f'kubejs/data/alfheim/structures/pixie/{kind}/village_{variant}_{gx}_{gz}.nbt')[1]
            assert list(root['size'])==[48,48,48] and root['DataVersion']==3465
            for b in root['blocks']:
                x,y,z=map(int,b['pos']);assert 0<=x<48 and 0<=y<48 and 0<=z<48
                pos=(x+gx*48,y,z+gz*48);assert pos not in grid
                state=root['palette'][b['state']];grid[pos]=state
                if state['Name'].endswith('_fey_apartment'):homes.append((pos,b.get('nbt',{}),state))
    return grid,homes

def main():
    report=json.loads((ROOT/'tools/fey_sky_villages_generation.json').read_text());results=[]
    for template in report['layout']['templates']:assert hashlib.sha256((ROOT/template['file']).read_bytes()).hexdigest()==template['sha256']
    entities=json.loads((ROOT/'server/local/kubejs/export/registries/entity_type.json').read_text())
    shapes=[]
    for kind,c in CULTURES.items():
        assert c['entity'] in entities
        for variant in range(2):
            grid,homes=read_village(kind,variant);assert len(homes)>=6
            barrels=0
            for gx in range(2):
                for gz in range(2):
                    tile=nbt.load(ROOT/f'kubejs/data/alfheim/structures/pixie/{kind}/village_{variant}_{gx}_{gz}.nbt')[1]
                    for cell in tile['blocks']:
                        if tile['palette'][cell['state']]['Name']!='minecraft:barrel':continue
                        loot=cell.get('nbt',{});barrels+=1
                        assert loot.get('LootTable')==f'alfheim:chests/fairy_island_{kind}',(kind,variant,cell)
                        assert 'Items' not in loot and 'LootTableSeed' not in loot,(kind,variant,'fixed loot')
            assert barrels==(14 if kind=='autumn' else 10),(kind,variant,barrels)
            loot=json.loads((ROOT/f'kubejs/data/alfheim/loot_tables/chests/fairy_island_{kind}.json').read_text())
            assert len(loot['pools'])==2 and all(p['rolls']['type']=='minecraft:uniform' for p in loot['pools'])
            source,record=village(kind,variant)
            expected={pos:source.palette[s] for pos,(s,be) in source.blocks.items()}
            assert grid==expected,(kind,variant,'emitted/source mismatch')
            for (x,y,z),be,state in homes:
                assert state['Name']=='alfheim_companion:'+kind+'_fey_apartment'
                assert be['id']=='alfheim_companion:fey_home'
                dz=-1 if state['Properties']['facing']=='north' else 1
                assert all(grid.get((x,h,z+dz),{}).get('Name','minecraft:air')=='minecraft:air' for h in (y,y+1)),(kind,'sealed home exit',x,y,z)
            # Walk the terraced landform in three dimensions, allowing ordinary one-block steps.
            walk={ (x,y,z) for (x,y,z),s in grid.items() if 13<=y<=23 and s['Name'] not in ('minecraft:air','minecraft:water') and
                all(grid.get((x,h,z),{}).get('Name','minecraft:air') in ('minecraft:air','minecraft:snow') for h in (y+1,y+2)) }
            start=min(walk,key=lambda p:(p[0]-48)**2+(p[2]-40)**2)
            seen={start};q=deque([start])
            while q:
                x,y,z=q.popleft()
                for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
                    for dy in (-1,0,1):
                        p=(x+dx,y+dy,z+dz)
                        if p in walk and p not in seen:seen.add(p);q.append(p)
            for x,z in plan(kind,variant)[0]:
                assert any((x+dx,y,z+dz) in seen for dx in (-3,3) for dz in (-3,3) for y in range(13,24)),(kind,variant,'cottage disconnected',x,z)
            assert len(seen)>1000,(kind,variant,len(seen))
            silhouette={(x,z) for x,y,z in grid if y<=23 and grid[(x,y,z)]['Name']!='minecraft:air'};shapes.append(silhouette)
            record.update({'blocks':len(grid),'reachable_surface_cells':len(seen),'home_exits_clear':True});results.append(record)
        model=json.loads((ROOT/f'first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion/models/block/{kind}_fey_apartment.json').read_text())
        assert len(model['elements'])>=25
        for e in model['elements']:assert all(0<=v<=16 for v in e['from']+e['to'])
    assert len({frozenset(s) for s in shapes})==8
    result={'status':'LOCALLY_VALIDATED_RUNTIME_REQUIRED','villages':results,'total_related_tiles':32,'seasonal_entity_ids':{k:c['entity'] for k,c in CULTURES.items()},'native_behavior':'compiled; storage, entry/exit, ownership, bounded population and crop visits require in-game validation','minimum_independent_gap':500,'neighbor_reservation':900,'runtime_placement':'checked separately in tools/fairy_island_runtime_report.json; this checker makes no runtime claim'}
    (ROOT/'tools/fey_sky_villages_static.json').write_text(json.dumps(result,indent=2)+'\n')
    print('FEY SKY VILLAGES STATIC PASS: eight different 96-block layouts, 32 joined tiles, 80 cottages, 16 apartment trees, modeled home blocks, open home exits and connected surface approaches')

if __name__=='__main__':main()
