"""Read a saved test assembly and verify its actual members and doorway joins."""
import argparse
from collections import Counter,deque
import json
from pathlib import Path
import nbt
from probe_terraces import chunks,section_blocks

ROOT=Path(__file__).resolve().parents[1]
TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/common_residential'
POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/common_residential'
STEP={'north':(0,-1),'east':(1,0),'south':(0,1),'west':(-1,0)}


def rotate(x,z,r):
    for _ in range(r):x,z=-z,x
    return x,z


def load_piece(name):
    _,p=nbt.load(str(TEMPLATES/f'{name}.nbt'))
    return p


def world_pos(pos,origin,r):
    x,y,z=map(int,pos);x,z=rotate(x,z,r)
    return origin[0]+x,origin[1]+y,origin[2]+z


def main():
    global TEMPLATES,POOL
    ap=argparse.ArgumentParser();ap.add_argument('world')
    ap.add_argument('--family',choices=('common_residential','elder_lineage','civic_center','relief_district','scholastic_quarter','production_district','agricultural_estate','roads_trade','harbor_complex','sacred_precinct','military_warden','frontier_stewardship'),default='common_residential');args=ap.parse_args()
    lineage=args.family=='elder_lineage'
    civic=args.family=='civic_center'
    relief=args.family=='relief_district'
    scholastic=args.family=='scholastic_quarter'
    production=args.family=='production_district'
    agricultural=args.family=='agricultural_estate'
    trade=args.family=='roads_trade'
    harbor=args.family=='harbor_complex'
    frontier=args.family=='frontier_stewardship'
    military=args.family=='military_warden'
    sacred=args.family=='sacred_precinct'
    institutional=lineage or civic or relief or scholastic or production or agricultural or trade or harbor or sacred or military or frontier
    if frontier:
        from gen_frontier_stewardship import SIZES
        TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/frontier_stewardship'
        POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/frontier_stewardship'
    elif military:
        from gen_military_warden import SIZES
        TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/military_warden'
        POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/military_warden'
    elif sacred:
        from gen_sacred_precinct import SIZES
        TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/sacred_precinct'
        POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/sacred_precinct'
    elif harbor:
        from gen_harbor_complex import SIZES
        TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/harbor_complex'
        POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/harbor_complex'
    elif trade:
        from gen_roads_trade import SIZES
        TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/roads_trade'
        POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/roads_trade'
    elif agricultural:
        from gen_agricultural_estate import SIZES
        TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/agricultural_estate'
        POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/agricultural_estate'
    elif production:
        from gen_production_district import SIZES
        TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/production_district'
        POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/production_district'
    elif scholastic:
        from gen_scholastic_quarter import SIZES
        TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/scholastic_quarter'
        POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/scholastic_quarter'
    elif relief:
        from gen_relief_district import SIZES
        TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/relief_district'
        POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/relief_district'
    elif civic:
        from gen_civic_center import SIZES
        TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/civic_center'
        POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/civic_center'
    elif lineage:
        from gen_elder_lineage import SIZES
        TEMPLATES=ROOT/'kubejs/data/alfheim/structures/ancient/elder_lineage'
        POOL=ROOT/'kubejs/data/alfheim/worldgen/template_pool/ancient/elder_lineage'
    prefix='Harbor ' if harbor else 'Trade ' if trade else 'Agricultural ' if agricultural else 'Production ' if production else 'Scholastic ' if scholastic else 'Relief ' if relief else 'Civic ' if civic else 'Lineage ' if lineage else 'Ancient '
    rootname='harbor_exchange' if harbor else 'caravan_court' if trade else 'water_garden' if agricultural else 'freight_yard' if production else 'lore_college' if scholastic else 'triage_court' if relief else 'assembly_hall' if civic else 'palace_center' if lineage else 'neighborhood_common_hall'
    rootlabel='harbor_exchange' if harbor else 'caravan_court' if trade else 'water_garden' if agricultural else 'freight_yard' if production else 'lore_college' if scholastic else 'triage_court' if relief else 'assembly_hall' if civic else 'palace_center' if lineage else 'common_hall'
    if sacred:prefix='Sacred ';rootname=rootlabel='great_temple_court'
    if military:prefix='Warden ';rootname=rootlabel='border_keep'
    if frontier:prefix='Frontier ';rootname=rootlabel='green_noble_lodge'
    region=Path(args.world)/'dimensions/mythicbotany/alfheim/region'
    grid={};cache={};labels=Counter();markers={};hall=None
    for file in region.glob('*.mca'):
        for c in chunks(file):
            grid[(c['xPos'],c['zPos'])]=c
            for b in c.get('block_entities',[]):
                title=b.get('CustomName','')
                if prefix not in title:continue
                name=json.loads(title)['text'].removeprefix(prefix)
                labels[name]+=1
                markers.setdefault(name,set()).add((int(b['x']),int(b['y']),int(b['z'])))
                if name==rootlabel:hall=(b['x'],b['y'],b['z'])
    expected=Counter({name:1 for name in SIZES}) if institutional else Counter(common_hall=1,common_row_house=6,courtyard_home=4,artisan_house_shop=4,extended_kin_hall=2)
    if institutional:
        assert labels[rootlabel]==1,('ambiguous assembly root',markers.get(rootlabel))
    else:assert labels==expected,labels
    def block(x,y,z):
        key=(x//16,y//16,z//16)
        if key not in cache:
            c=grid.get((x//16,z//16),{})
            s=next((s for s in c.get('sections',[]) if int(s['Y'])==y//16),None)
            cache[key]=section_blocks(s) if s else None
        data=cache[key]
        return data[(y%16)*256+(z%16)*16+x%16] if data else 'minecraft:air'
    p=load_piece(rootname)
    solids=[b for b in p['blocks'] if p['palette'][int(b['state'])]['Name'] not in ('minecraft:air','minecraft:jigsaw')]
    local=(7,9,10) if institutional else (8,7,24)
    candidates=[]
    for r in range(4):
        x,z=rotate(local[0],local[2],r)
        origin=(hall[0]-x,hall[1]-local[1],hall[2]-z)
        score=sum(block(*world_pos(b['pos'],origin,r))==p['palette'][int(b['state'])]['Name']
                  for b in solids[::max(1,len(solids)//500)])
        candidates.append((score,origin,r))
    _,origin,rotation=max(candidates)
    queue=deque([(rootname,origin,rotation,0)])
    seen=[];joins=[]
    while queue:
        name,origin,r,depth=queue.popleft()
        p=load_piece(name)
        seen.append({'name':name,'origin':origin,'rotation':r})
        for b in p['blocks']:
            be=b.get('nbt',{})
            if be.get('id')!='minecraft:jigsaw' or be.get('pool')=='minecraft:empty':continue
            spec=json.loads((POOL/(be['pool'].split('/')[-1]+'.json')).read_text())
            assert len(spec['elements'])==1,be
            childname=spec['elements'][0]['element']['location'].split('/')[-1]
            cp=load_piece(childname)
            socket=next(b for b in cp['blocks'] if b.get('nbt',{}).get('name')==be['target'])
            face=p['palette'][int(b['state'])]['Properties']['orientation'].split('_')[0]
            dx,dz=rotate(*STEP[face],r)
            world=world_pos(b['pos'],origin,r)
            target=(world[0]+dx,world[1],world[2]+dz)
            cf=cp['palette'][int(socket['state'])]['Properties']['orientation'].split('_')[0]
            cr=next(r for r in range(4) if rotate(*STEP[cf],r)==(-dx,-dz))
            cx,cy,cz=world_pos(socket['pos'],(0,0,0),cr)
            co=(target[0]-cx,target[1]-cy,target[2]-cz)
            assert depth<(4 if relief else 3),('unexpected expansion',name)
            for point in (world,target):
                x,y,z=point
                assert block(x,y-1,z) not in ('minecraft:air','minecraft:water','minecraft:lava'),('unsupported join',name,point)
                assert block(x,y,z)=='minecraft:air' and block(x,y+1,z)=='minecraft:air',('blocked join',name,point,block(x,y,z),block(x,y+1,z),origin,r)
            joins.append([name,childname,world,target])
            queue.append((childname,co,cr,depth+1))
    counts=Counter(s['name'] for s in seen)
    assert len(seen)==(6 if military or frontier else 7 if sacred else 11 if relief else 10 if production or agricultural or trade or harbor else 9 if institutional else 26),counts
    if institutional:
        assert counts==expected,('wrong assembled membership',counts,expected)
        for node in seen:
            marker=world_pos((7,9,26) if sacred and node['name']=='ancestor_reflection_pool' else (7,9,10),node['origin'],node['rotation'])
            assert marker in markers.get(node['name'],set()),('missing member marker',node,marker)
    # Every declared piece must actually exist in the save, beyond its cache marker.
    clear_air=0;verified_foundation_cells=0
    for node in seen:
        p=load_piece(node['name'])
        solids=[b for b in p['blocks'] if p['palette'][int(b['state'])]['Name'] not in ('minecraft:air','minecraft:jigsaw','minecraft:water')]
        sample=solids[::max(1,len(solids)//200)]
        ratio=sum(block(*world_pos(b['pos'],node['origin'],node['rotation']))==p['palette'][int(b['state'])]['Name'] for b in sample)/len(sample)
        assert ratio>=.97,(node['name'],'missing or mismatched geometry',ratio)
        if sacred or military or frontier:
            for b in p['blocks']:
                if int(b['pos'][1])<8:
                    expected_name=p['palette'][int(b['state'])]['Name']
                    assert block(*world_pos(b['pos'],node['origin'],node['rotation']))==expected_name,('missing sacred foundation cell',node['name'],b['pos'])
                    verified_foundation_cells+=1
        if trade and node['name']=='bridge_gate':
            for b in p['blocks']:
                x,y,z=map(int,b['pos'])
                name=p['palette'][int(b['state'])]['Name']
                if 14<=z<=24 and 18<=x<=28 and 4<=y<=8 and name!='minecraft:air':
                    assert block(*world_pos(b['pos'],node['origin'],node['rotation']))==name,('missing bridge deck or pier',b['pos'])
        if civic or relief or scholastic or production or agricultural or trade or harbor or sacred or military or frontier:
            for b in p['blocks']:
                if p['palette'][int(b['state'])]['Name']=='minecraft:air':
                    point=world_pos(b['pos'],node['origin'],node['rotation'])
                    assert block(*point)=='minecraft:air',('infilled authored volume',node['name'],point,block(*point))
                    clear_air+=1
        if institutional:
            for b in p['blocks']:
                name=p['palette'][int(b['state'])]['Name']
                if name.startswith(('alfheim:royal_','alfheim:elder_')):
                    assert block(*world_pos(b['pos'],node['origin'],node['rotation']))==name,('missing cultural module',node['name'],name,b['pos'])
                if (relief or scholastic or production or agricultural or trade or harbor or sacred or military or frontier) and (name.endswith('_bed') or name in ('minecraft:skeleton_skull','minecraft:bone_block','minecraft:oak_fence')):
                    assert block(*world_pos(b['pos'],node['origin'],node['rotation']))==name,('missing relief fixture',node['name'],name,b['pos'])
                if harbor and name in ('minecraft:water','botania:dreamwood_stairs','botania:elf_glass'):
                    assert block(*world_pos(b['pos'],node['origin'],node['rotation']))==name,('missing harbor fixture',node['name'],name,b['pos'])
                if sacred and name in ('minecraft:water','botania:elf_glass','minecraft:white_wool','botania:dreamwood_log'):
                    assert block(*world_pos(b['pos'],node['origin'],node['rotation']))==name,('missing sacred fixture',node['name'],name,b['pos'])
                if frontier and (name in ('minecraft:water','minecraft:wheat','minecraft:farmland','botania:elf_glass','botania:dreamwood_log','alfheim:ivory_livingrock_stairs') or name=='minecraft:moss_carpet'):
                    assert block(*world_pos(b['pos'],node['origin'],node['rotation']))==name,('missing frontier fixture',node['name'],name,b['pos'])
                if military and name in ('alfheim:ivory_livingrock_stairs','minecraft:iron_door','minecraft:iron_bars','botania:elf_glass','botania:dreamwood_log'):
                    assert block(*world_pos(b['pos'],node['origin'],node['rotation']))==name,('missing military fixture',node['name'],name,b['pos'])
                if agricultural and (name in ('minecraft:water','minecraft:beehive','minecraft:wheat','minecraft:carrots','minecraft:farmland','minecraft:mycelium','minecraft:clay','botania:dreamwood_log','mythicbotany:dreamwood_leaves') or name.endswith('_mushroom')):
                    assert block(*world_pos(b['pos'],node['origin'],node['rotation']))==name,('missing agricultural fixture',node['name'],name,b['pos'])
                if production and name in ('minecraft:furnace','ars_nouveau:sourcestone','botania:elf_glass'):
                    assert block(*world_pos(b['pos'],node['origin'],node['rotation']))==name,('missing production fixture',node['name'],name,b['pos'])
                if scholastic and name in ('minecraft:bookshelf','minecraft:end_rod','botania:dreamwood_stairs'):
                    assert block(*world_pos(b['pos'],node['origin'],node['rotation']))==name,('missing scholastic fixture',node['name'],name,b['pos'])
    verified_footer_cells=0
    if harbor:
        root=next(n for n in seen if n['name']=='harbor_exchange')
        lift=root['origin'][1]-58
        if lift in (2,4,6):
            for node in seen:
                piece=load_piece(node['name']);sx,_,sz=map(int,piece['size'])
                footer=nbt.load(str(TEMPLATES/'foundations'/f'{sx}x{sz}_{lift}.nbt'))[1]
                at=(node['origin'][0],node['origin'][1]-lift,node['origin'][2])
                for b in footer['blocks']:
                    expected_name=footer['palette'][int(b['state'])]['Name']
                    assert block(*world_pos(b['pos'],at,node['rotation']))==expected_name,('missing raised harbor foundation',node['name'],b['pos'])
                    verified_footer_cells+=1
    result={'world':str(Path(args.world)),'pieces':len(seen),'inhabited_members':None if institutional else 16,
            'counts':dict(counts),'background_markers':dict(labels-counts) if institutional else {},'clear_supported_joins':len(joins),'verified_air_cells':clear_air,'verified_footer_cells':verified_footer_cells,'verified_foundation_cells':verified_foundation_cells,'layout':seen}
    census='harbor_complex_runtime_census.json' if harbor else 'roads_trade_runtime_census.json' if trade else 'agricultural_estate_runtime_census.json' if agricultural else 'production_district_runtime_census.json' if production else 'scholastic_quarter_runtime_census.json' if scholastic else 'relief_district_runtime_census.json' if relief else 'civic_center_runtime_census.json' if civic else 'elder_lineage_runtime_census.json' if lineage else 'ancient_district_runtime_census.json'
    if sacred:census='sacred_precinct_runtime_census.json'
    if military:census='military_warden_runtime_census.json'
    if frontier:census='frontier_stewardship_runtime_census.json'
    (ROOT/'tools'/census).write_text(json.dumps(result,indent=2)+'\n')
    print(f'SAVED ASSEMBLY PASS: {len(seen)} members, {len(joins)} clear supported joins; family={args.family}')


if __name__=='__main__':main()
