"""Bounded noise-only survey, then natural saved-start validation in a disposable world.

Run survey first; populate reads its accepted candidates and loads at most three
5x5-chunk sites. Never uses /place structure or edits a player's saved world.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import run_server
from probe_terraces import chunks, section_blocks
import nbt

ROOT=Path(__file__).resolve().parents[1]
WORLD='validation-upper-natural-20261015'
HOME='mythicbotany:alfheim'
SEED='3536368297089363045'
REPORT=ROOT/'tools/upper_natural_runtime_report.json'

def launch(commands):
    props=ROOT/'server/server.properties';old=props.read_bytes()
    before=set((ROOT/'server').glob('console-*.log'))
    try:code=run_server.run(SEED,WORLD,8,commands,600)
    finally:
        props.write_bytes(old)
        jade=ROOT/'server/config/jade/server-plugin-overrides.json'
        jade.parent.mkdir(parents=True,exist_ok=True)
        jade.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    console=max(set((ROOT/'server').glob('console-*.log'))-before,key=lambda p:p.stat().st_mtime)
    return console,console.read_text(errors='replace')

def survey():
    commands=[(3,'gamerule randomTickSpeed 0')]
    for key in ('final','created','foundation_v1'):
        commands.append((.2,f'scoreboard players set #{key} alfheim.hub 1'))
    for name in ('resolve','inspect_burial','repair_foundation'):
        commands.append((.2,f'schedule clear alfheim:hub/{name}'))
    for x,z in ((4,4),(-12,4),(4,-12),(-12,-12)):
        commands.append((4,f'execute in {HOME} run alfheimupper audit {x} {z} 64'))
    commands.extend([(5,'save-all flush'),(1,'stop')])
    console,text=launch(commands)
    sites=[dict(zip(('x','y','z','chunk_x','chunk_z'),map(int,m))) for m in re.findall(
        r'Upper candidate x=(-?\d+) y=(\d+) z=(-?\d+) chunk=(-?\d+),(-?\d+)',text)]
    summaries=re.findall(r'Upper audit seed=.*',text)
    result={'status':'SURVEY_ONLY','seed':SEED,'world':WORLD,'survey_console':str(console.relative_to(ROOT)),
            'summaries':summaries,'accepted_candidates':sites,'natural_starts':'PENDING',
            'installed_jar_sha256':hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest()}
    baseline=ROOT/'build/continuity-district-refit/upper-survey-before.json'
    if baseline.exists():
        prior=json.loads(baseline.read_text())
        result['before_fix']={k:prior[k] for k in ('survey_console','summaries','installed_jar_sha256')}
    capability=ROOT/'build/upper-natural-audit/capability-audit.json'
    if capability.exists():
        result['continuity_works_audit']=json.loads(capability.read_text())
    REPORT.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

def populate(verify_only=False):
    result=json.loads(REPORT.read_text());sites=result['accepted_candidates'][:3]
    assert sites,'No accepted candidates; inspect reservation/terrain rejection summaries'
    assert result['installed_jar_sha256']==hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest()
    commands=[(3,'gamerule randomTickSpeed 0')]
    for s in sites:
        x,z=s['chunk_x']*16,s['chunk_z']*16
        commands.append((1,f'execute in {HOME} run forceload add {x-32} {z-32} {x+47} {z+47}'))
    commands.extend([(90,'save-all flush'),(2,f'execute in {HOME} run forceload remove all'),(2,'stop')])
    if verify_only:
        console=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
        text=console.read_text(errors='replace')
    else:
        console,text=launch(commands)
    assert 'That position is not loaded' not in text
    grid={}
    for path in (ROOT/'server'/WORLD/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
        for c in chunks(path):grid[int(c['xPos']),int(c['zPos'])]=c
    cache={}
    def block(x,y,z):
        key=x//16,y//16,z//16
        if key not in cache:
            sec=next((s for s in grid.get((x//16,z//16),{}).get('sections',[]) if int(s['Y'])==y//16),None)
            cache[key]=section_blocks(sec) if sec else None
        v=cache[key]
        return v[((y&15)<<8)|((z&15)<<4)|(x&15)] if v else None
    proofs=[]
    for site in sites:
        c=grid[site['chunk_x'],site['chunk_z']]
        start=c.get('structures',{}).get('starts',{}).get('alfheim:upper_underworld')
        assert start and start.get('id')!='INVALID',(site,start)
        children=start['Children'];assert len(children)==1,children
        piece=children[0];template=piece['pool_element']['location']
        origin=[int(piece['Pos'+axis]) for axis in ('X','Y','Z')]
        assert origin==[site['x'],site['y'],site['z']],(origin,site)
        bounds=list(map(int,piece['BB']));assert bounds[1]>=32 and bounds[4]<=115,bounds
        root=nbt.load(ROOT/f'kubejs/data/alfheim/structures/{template.split(":",1)[1]}.nbt')[1]
        solid=[b for b in root['blocks'] if root['palette'][int(b['state'])]['Name'] not in ('minecraft:air','minecraft:cave_air','minecraft:jigsaw')]
        sample=solid[::max(1,len(solid)//300)];matched=0
        for b in sample:
            x,y,z=map(int,b['pos'])
            matched+=block(origin[0]+x,origin[1]+y,origin[2]+z)==root['palette'][int(b['state'])]['Name']
        assert matched/len(sample)>=.95,(site,template,matched,len(sample))
        proofs.append({'candidate':site,'template':template,'bounds':bounds,'samples':len(sample),'matched':matched,
                       'natural_start_id':start['id']})
    result.update(status='NATURAL_STARTS_VALIDATED',natural_starts=proofs,population_console=str(console.relative_to(ROOT)),
                  visual_review='pending',density_review='bounded one-seed sample; not a population-wide density claim')
    REPORT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('survey','populate','verify'));args=p.parse_args()
    if args.mode=='survey':survey()
    else:populate(verify_only=args.mode=='verify')
