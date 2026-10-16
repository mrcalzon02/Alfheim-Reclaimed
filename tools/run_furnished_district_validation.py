"""Materialize every changed district template in an owned layered test gallery."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import nbt
import run_server
from probe_terraces import chunks,unpack_bits

ROOT=Path(__file__).resolve().parents[1];WORLD='validation-furnished-districts-20261015';HOME='mythicbotany:alfheim'

def records():
    report=json.loads((ROOT/'tools/district_furnishing_placement_report.json').read_text())
    return [r for f in report['families'] for r in f['templates']]

def verify(console):
    console=console.resolve()
    entries=records();side=4 if len(entries)<=80 else 5
    text=console.read_text(errors='replace');assert text.count('Loaded template "alfheim:ancient/')==len(entries)
    assert 'That position is not loaded' not in text
    grid={};entities={}
    for path in (ROOT/'server'/WORLD/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
        for chunk in chunks(path):
            if chunk:
                grid[int(chunk['xPos']),int(chunk['zPos'])]=chunk
                for be in chunk.get('block_entities',[]):entities[int(be['x']),int(be['y']),int(be['z'])]=be
    cache={}
    def state(pos):
        x,y,z=pos;key=x//16,y//16,z//16
        if key not in cache:
            section=next(s for s in grid[x//16,z//16]['sections'] if int(s['Y'])==y//16)
            bs=section['block_states'];palette=bs['palette']
            cache[key]=[palette[0]]*4096 if len(palette)==1 else [palette[i] for i in unpack_bits(bs['data'],max(4,(len(palette)-1).bit_length()),4096)]
        return cache[key][((y&15)<<8)|((z&15)<<4)|(x&15)]
    storage=stations=loot=0;hashes={};families=set();assigned_seeds=[]
    for i,r in enumerate(entries):
        origin=((i%side)*48,80+(i//(side*side))*48,((i//side)%side)*48)
        def absolute(p):return tuple(int(a)+b for a,b in zip(p,origin))
        root=nbt.load(ROOT/r['file'])[1];families.add(Path(r['file']).parent.name)
        current=hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest()
        assert current==r['sha256']==hashlib.sha256((ROOT/'server'/r['file']).read_bytes()).hexdigest()
        hashes[r['file']]=current
        for placement in r['placements']:
            pos=absolute(placement['pos']);actual=state(pos)
            assert actual['Name']==placement['id'] and actual.get('Properties',{}).get('facing')==placement['facing'],(r['file'],pos,actual)
            if placement['id'].endswith(('cabinet','locker','hutch','counter')):
                be=entities[pos];assert be['id']=='alfheim_leyworks:elven_container' and not be.get('Items') and 'LootTable' not in be,(pos,be)
                storage+=1
            else:assert pos not in entities;stations+=1
        for block in root['blocks']:
            old=block.get('nbt',{})
            if 'LootTable' not in old:continue
            pos=absolute(block['pos']);be=entities[pos]
            assert be['id']==old['id'] and be['LootTable']==old['LootTable'] and not be.get('Items'),(r['file'],pos,'loot changed')
            # Vanilla StructureTemplate assigns random LootTableSeed values when
            # placing RandomizableContainerBlockEntity; the source records remain exact.
            assert 'LootTableSeed' in be and isinstance(be['LootTableSeed'],int),(r['file'],pos,'missing native loot seed')
            assigned_seeds.append({'template':r['file'],'pos':pos,'seed':int(be['LootTableSeed'])})
            loot+=1
    jar='alfheim_leyworks-0.1.0.jar';sha=hashlib.sha256((ROOT/'mods'/jar).read_bytes()).hexdigest()
    assert sha==hashlib.sha256((ROOT/'server/mods'/jar).read_bytes()).hexdigest()
    result={'status':'SAVED_FURNISHED_TEMPLATES_PASS','world':WORLD,'console':str(console.relative_to(ROOT)),
        'templates':len(entries),'families':sorted(families),'storage_block_entities':storage,'workstations':stations,'preserved_loot_records':loot,
        'native_loot_seeds':assigned_seeds,
        'template_sha256':hashes,'installed_leyworks_sha256':sha,
        'limits':'Template placement, facing, empty storage initialization and untouched loot verified; this does not re-prove natural site selection or client appearance.'}
    (ROOT/'tools/furnished_district_runtime_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('FURNISHED DISTRICT GALLERY PASS:',len(entries),'templates,',storage,'storage,',stations,'workstations,',loot,'untouched loot records')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--verify-console',type=Path);args=ap.parse_args()
    if args.verify_console:verify(args.verify_console);return
    entries=records();side=4 if len(entries)<=80 else 5;assert len(entries)<=side*side*5
    commands=[(2,'gamerule randomTickSpeed 0')]
    for key in ('final','created','foundation_v1'):commands.append((.1,f'scoreboard players set #{key} alfheim.hub 1'))
    for key in ('resolve','inspect_burial','repair_foundation'):commands.append((.1,f'schedule clear alfheim:hub/{key}'))
    commands.extend([(1,f'execute in {HOME} run forceload add 0 0 {side*48-1} {side*48-1}'),(60,'say district furnishing gallery warmed')])
    for i,r in enumerate(entries):
        name='alfheim:'+r['file'].split('/structures/')[1][:-4]
        x,y,z=(i%side)*48,80+(i//(side*side))*48,((i//side)%side)*48
        commands.append((.3,f'execute in {HOME} run place template {name} {x} {y} {z}'))
    commands.extend([(15,'save-all flush'),(1,f'execute in {HOME} run forceload remove all'),(2,'stop')])
    props=ROOT/'server/server.properties';old=props.read_bytes();before=set((ROOT/'server').glob('console-*.log'))
    try:code=run_server.run('3536368297089363045',WORLD,8,commands,600)
    finally:
        props.write_bytes(old);jade=ROOT/'server/config/jade/server-plugin-overrides.json';jade.parent.mkdir(parents=True,exist_ok=True)
        jade.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    verify(max(set((ROOT/'server').glob('console-*.log'))-before,key=lambda p:p.stat().st_mtime))

if __name__=='__main__':main()
