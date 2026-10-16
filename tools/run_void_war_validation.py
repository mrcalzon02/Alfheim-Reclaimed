"""Owned disposable-world registry, gallery and natural-war-site validation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import nbt
import run_server
from probe_terraces import chunks,section_blocks
from gen_void_war import KINDS,SURFACE_NAMES,BASEMENT_NAMES

ROOT=Path(__file__).resolve().parents[1];WORLD='validation-void-war-final-20261015';HOME='mythicbotany:alfheim';SEED='3536368297089363045'
REPORT=ROOT/'tools/void_war_runtime_report.json'

def frozen():
    commands=[(3,'gamerule randomTickSpeed 0')]
    for key in ('final','created','foundation_v1'):commands.append((.2,f'scoreboard players set #{key} alfheim.hub 1'))
    for key in ('resolve','inspect_burial','repair_foundation'):commands.append((.2,f'schedule clear alfheim:hub/{key}'))
    return commands

def launch(commands):
    props=ROOT/'server/server.properties';old=props.read_bytes();before=set((ROOT/'server').glob('console-*.log'))
    try:code=run_server.run(SEED,WORLD,8,commands,600)
    finally:
        props.write_bytes(old);jade=ROOT/'server/config/jade/server-plugin-overrides.json';jade.parent.mkdir(parents=True,exist_ok=True)
        jade.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    console=max(set((ROOT/'server').glob('console-*.log'))-before,key=lambda p:p.stat().st_mtime)
    return console,console.read_text(errors='replace')

def sha():return hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest()

def freeze_evidence(result):
    artifact='alfheim_companion-0.2.0.jar'
    assert hashlib.sha256((ROOT/'server/mods'/artifact).read_bytes()).hexdigest()==sha()
    assert hashlib.sha256((ROOT/'first_party_mods/alfheim_companion/build/libs'/artifact).read_bytes()).hexdigest()==sha()
    generation_path=ROOT/'tools/void_war_generation_report.json';generation=json.loads(generation_path.read_text())
    hashes={}
    for record in generation['layout']['templates']:
        current=hashlib.sha256((ROOT/record['file']).read_bytes()).hexdigest()
        assert current==record['sha256']==hashlib.sha256((ROOT/'server'/record['file']).read_bytes()).hexdigest()
        hashes[record['name']]=current
    result.update(generation_snapshot_id=generation['snapshot_id'],verified_template_hashes=hashes,
        generation_report_sha256_lf=hashlib.sha256(generation_path.read_text().encode()).hexdigest(),
        material_catalog_sha256=hashlib.sha256((ROOT/'kubejs/war_remains_catalog.json').read_bytes()).hexdigest())

def materials():
    console,text=launch(frozen()+[(1,'alfheimwar materials'),(2,'stop')])
    match=re.search(r'War registry ids=\[([^\]]+)\]',text);assert match,'Native registry report missing'
    ids=[s.strip() for s in match[1].split(',')]
    expected=[b['id'] for b in json.loads((ROOT/'kubejs/war_remains_catalog.json').read_text())['blocks']]
    assert set(expected)<=set(ids),(set(expected)-set(ids))
    evidence={'status':'REGISTERED_IN_FORGE','registered_ids':ids,'expected_count':len(expected),'world':WORLD,
              'console':str(console.relative_to(ROOT)),'installed_jar_sha256':sha()}
    (ROOT/'tools/void_war_registry_report.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print('WAR REGISTRY PASS:',len(expected),'new blocks verified in actual game registry')

def survey():
    commands=frozen()
    for x,z in ((2,2),(-10,2),(2,-10),(-10,-10),(10,10),(-18,10),(10,-18),(-18,-18)):
        commands.append((4,f'execute in {HOME} run alfheimwar audit {x} {z} 64'))
    commands.extend([(5,'save-all flush'),(1,'stop')]);console,text=launch(commands)
    sites=[]
    for m in re.finditer(r'War candidate chunk=(-?\d+),(-?\d+) origin=(-?\d+),(\d+),(-?\d+) profile=(large|compact) columns=(\d+) biome_queries=(\d+)',text):
        sites.append(dict(zip(('chunk_x','chunk_z','x','surface_y','z','profile','columns','biome_queries'),
            [int(m[i]) if i!=6 else m[i] for i in range(1,9)])))
    result={'status':'SURVEY_ONLY','world':WORLD,'seed':SEED,'console':str(console.relative_to(ROOT)),
            'sites':sites,'summaries':re.findall(r'War audit region=.*',text),'installed_jar_sha256':sha()}
    REPORT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

def gallery():
    names=SURFACE_NAMES+BASEMENT_NAMES
    commands=frozen()+[(1,f'execute in {HOME} run forceload add 0 0 239 239'),(60,'say war gallery warmed')]
    for i,name in enumerate(names):commands.append((1,f'execute in {HOME} run place template alfheim:void_war/{name} {(i%5)*48} 192 {(i//5)*48}'))
    # Wrong-biome/dimension placements must fail even for operators.
    commands.extend([(1,'execute in minecraft:overworld run forceload add 8192 8192'),
                     (15,'execute in minecraft:overworld run place structure alfheim:last_bulwark 8192 80 8192'),
                     (1,f'execute in {HOME} run place structure alfheim:last_bulwark 0 80 0'),
                     (30,'save-all flush'),(2,f'execute in {HOME} run forceload remove all'),
                     (1,'execute in minecraft:overworld run forceload remove all'),(2,'stop')])
    console,text=launch(commands)
    result=json.loads(REPORT.read_text()) if REPORT.exists() else {'world':WORLD,'seed':SEED,'installed_jar_sha256':sha()}
    result.update(world=WORLD,gallery_console=str(console.relative_to(ROOT)),gallery_names=list(names))
    REPORT.write_text(json.dumps(result,indent=2)+'\n');verify_gallery(result,text)

def world_blocks():
    grid={}
    for path in (ROOT/'server'/WORLD/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
        for c in chunks(path):grid[int(c['xPos']),int(c['zPos'])]=c
    cache={}
    def block(x,y,z):
        key=x//16,y//16,z//16
        if key not in cache:
            section=next((s for s in grid.get((x//16,z//16),{}).get('sections',[]) if int(s['Y'])==y//16),None)
            cache[key]=section_blocks(section) if section else None
        values=cache[key];return values[((y&15)<<8)|((z&15)<<4)|(x&15)] if values else None
    return grid,block

def sample(root,origin,block):
    solid=[b for b in root['blocks'] if root['palette'][int(b['state'])]['Name'] not in ('minecraft:air','minecraft:cave_air','minecraft:jigsaw')]
    tests=solid[::max(1,len(solid)//180)];matched=0;ores=[]
    for b in tests:
        x,y,z=map(int,b['pos']);actual=block(origin[0]+x,origin[1]+y,origin[2]+z);expected=root['palette'][int(b['state'])]['Name']
        if actual==expected:matched+=1
        else:
            assert expected=='alfheim:riftshale_livingrock' and actual in ('alfheim:cinderbloom_riftshale_ore','alfheim:verdigris_riftshale_ore'),(origin,(x,y,z),expected,actual)
            ores.append({'position':[x,y,z],'native_ore':actual})
    assert matched/len(tests)>=.95,(origin,matched,len(tests));return {'samples':len(tests),'matched':matched,'native_ore_substitutions':ores}

def verify_gallery(result,text):
    assert result['installed_jar_sha256']==sha()
    assert text.count('Loaded template "alfheim:void_war/')==len(result['gallery_names'])
    assert 'Generated structure "alfheim:last_bulwark"' not in text,'Wrong biome/origin admitted'
    assert text.count('Failed to place structure')==2,'Both explicit negative placement controls must execute and reject'
    assert 'That position is not loaded' not in text
    grid,block=world_blocks();proof=[];fixtures=block_entities(grid);encounters=0;containers=0
    for i,name in enumerate(result['gallery_names']):
        root=nbt.load(ROOT/f'kubejs/data/alfheim/structures/void_war/{name}.nbt')[1]
        proof.append({'template':name,**sample(root,[(i%5)*48,192,(i//5)*48],block)})
        a,b=verify_fixtures(root,[(i%5)*48,192,(i//5)*48],fixtures);encounters+=a;containers+=b
    result.update(gallery_status='SAVED_TEMPLATES_VALIDATED',gallery_proof=proof,wrong_biome_and_origin='rejected',
                  gallery_spawners=encounters,gallery_loot_containers=containers)
    freeze_evidence(result)
    REPORT.write_text(json.dumps(result,indent=2)+'\n');print('WAR GALLERY PASS:',len(proof),'templates;',sum(p['samples'] for p in proof),'samples')

def block_entities(grid):
    return {(int(b['x']),int(b['y']),int(b['z'])):b for c in grid.values() for b in c.get('block_entities',[])}

def biome_at(grid,x,y,z):
    section=next(s for s in grid[x//16,z//16]['sections'] if int(s['Y'])==y//16)
    biome=section['biomes'];palette=biome['palette']
    if len(palette)==1:return palette[0]
    bits=max(1,(len(palette)-1).bit_length());per_long=64//bits
    index=((y&15)//4)*16+((z&15)//4)*4+(x&15)//4
    value=(int(biome['data'][index//per_long])>>((index%per_long)*bits))&((1<<bits)-1)
    return palette[value]

def verify_fixtures(root,origin,fixtures):
    encounters=containers=0
    for b in root['blocks']:
        expected=b.get('nbt',{})
        if not ('LootTable' in expected or 'SpawnData' in expected):continue
        pos=tuple(origin[i]+int(b['pos'][i]) for i in range(3));actual=fixtures.get(pos,{})
        if 'LootTable' in expected:assert actual.get('LootTable')==expected['LootTable'],pos;containers+=1
        if 'SpawnData' in expected:
            assert actual.get('SpawnData',{}).get('entity',{}).get('id')==expected['SpawnData']['entity']['id'],pos
            assert int(actual['MaxNearbyEntities'])==4 and int(actual['SpawnCount'])==2;encounters+=1
    return encounters,containers

def populate():
    result=json.loads(REPORT.read_text())
    if result.get('world')!=WORLD:
        result.setdefault('survey_world',result.get('world'));result['previous_population_world']=result.get('world');result['world']=WORLD
    if result['installed_jar_sha256']!=sha():
        result.setdefault('survey_jar_sha256',result['installed_jar_sha256'])
        result['previous_population_jar_sha256']=result['installed_jar_sha256'];result['installed_jar_sha256']=sha()
    if result.get('population_console'):result['previous_population_console']=result['population_console']
    result['status']='FINAL_POPULATION_PENDING';result.pop('natural_proof',None)
    REPORT.write_text(json.dumps(result,indent=2)+'\n')
    sites=result.get('sites',[])[:2];assert sites,'No sites passed the bounded survey'
    commands=frozen()
    for s in sites:
        commands.append((2,f'execute in {HOME} run alfheimwar audit {s["chunk_x"]//192} {s["chunk_z"]//192} 1'))
        x,z=s['chunk_x']*16,s['chunk_z']*16
        radius=5 if s['profile']=='large' else 2
        commands.append((1,f'execute in {HOME} run forceload add {x-radius*16} {z-radius*16} {x+(radius+1)*16-1} {z+(radius+1)*16-1}'))
    commands.extend([(90,'save-all flush'),(2,f'execute in {HOME} run forceload remove all'),(2,'stop')])
    console,text=launch(commands);result['population_console']=str(console.relative_to(ROOT));result['population_sites']=sites
    for s in sites:assert f'War candidate chunk={s["chunk_x"]},{s["chunk_z"]} ' in text,'Final artifact no longer admits the surveyed site'
    REPORT.write_text(json.dumps(result,indent=2)+'\n');verify_natural(result)

def verify_natural(result):
    assert result['installed_jar_sha256']==sha();grid,block=world_blocks();proof=[];fixtures=block_entities(grid)
    for s in result['population_sites']:
        starts=grid[s['chunk_x'],s['chunk_z']].get('structures',{}).get('starts',{})
        good=[(name,start) for name,start in starts.items() if name in {'alfheim:'+n for n in KINDS} and start.get('id')!='INVALID']
        assert len(good)==1,(s,starts);name,start=good[0];children=start['Children'];assert len(children) in (2,18)
        width=141 if len(children)==18 else 47;biomes=set();biome_cells=0
        for qx in range(s['x']//4,(s['x']+width-1)//4+1):
            for qz in range(s['z']//4,(s['z']+width-1)//4+1):
                for y in (s['surface_y']-23,s['surface_y']+5):
                    value=biome_at(grid,qx*4,y,qz*4);assert value in ('alfheim:void_verge','alfheim:void_shore'),value
                    biomes.add(value);biome_cells+=1
        tests=[];encounters=containers=0;stairs=None
        for piece in children:
            template=piece['pool_element']['location'];origin=[int(piece['Pos'+a]) for a in ('X','Y','Z')]
            assert int(piece['BB'][1])>=32
            root=nbt.load(ROOT/f'kubejs/data/alfheim/structures/{template.split(":",1)[1]}.nbt')[1]
            tests.append({'template':template,**sample(root,origin,block)})
            a,b=verify_fixtures(root,origin,fixtures);encounters+=a;containers+=b
            if 'entry_descent' in template:stairs=origin
        assert stairs
        for i in range(24):
            for dx in (9,10,11):
                x,y,z=stairs[0]+dx,stairs[1]+5+i,stairs[2]+9+i
                assert block(x,y,z)=='alfheim:ivory_livingrock_stairs',('Missing stair',x,y,z)
                assert all(block(x,y+d,z) in ('minecraft:air','minecraft:cave_air') for d in (1,2,3)),('Stair headroom',x,y,z)
        assert all(block(stairs[0]+x,stairs[1]+28,stairs[2]+23) not in (None,'minecraft:air','minecraft:cave_air') for x in range(47))
        proof.append({'structure':name,'candidate':s,'pieces':tests,'continuous_steps':24,'spawners':encounters,'loot_containers':containers,
                      'saved_biomes':sorted(biomes),'saved_biome_cells_checked':biome_cells})
    result.update(status='NATURAL_WAR_SITES_VALIDATED',natural_proof=proof,visual_review='pending',existing_world_boundary_review='pending')
    freeze_evidence(result)
    REPORT.write_text(json.dumps(result,indent=2)+'\n');print('WAR NATURAL PASS:',len(proof),'sites;',sum(len(p['pieces']) for p in proof),'pieces')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('materials','survey','gallery','populate','verify_gallery','verify_natural'));args=p.parse_args()
    if args.mode.startswith('verify_'):
        r=json.loads(REPORT.read_text())
        if args.mode=='verify_gallery':verify_gallery(r,(ROOT/r['gallery_console']).read_text(errors='replace'))
        else:verify_natural(r)
    else:globals()[args.mode]()
