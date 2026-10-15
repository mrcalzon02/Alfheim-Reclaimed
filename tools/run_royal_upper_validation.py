"""Disposable runtime proof for remote-district veto, castle and upper-rock templates."""
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys

import nbt
import run_server
from probe_terraces import chunks,section_blocks
from check_ancient_assembly import rotate
from gen_royal_castle import KINDS as CASTLE_KINDS
from gen_upper_underworld import KINDS as UPPER_KINDS

ROOT=Path(__file__).resolve().parents[1]
WORLD='validation-royal-upper-20261015';HOME='mythicbotany:alfheim';SEED='3536368297089363045'


def main():
    fixtures=[('royal_castle',name) for name in CASTLE_KINDS]+[('upper_underworld',name) for name in UPPER_KINDS]
    # The normal hub retry may clear force-loads while this isolated fixture is
    # preparing. Freeze onboarding only in this disposable test world's scoreboard.
    commands=[(5,'gamerule randomTickSpeed 0'),(0.2,'scoreboard players set #final alfheim.hub 1'),
              (0.2,'scoreboard players set #created alfheim.hub 1'),(0.2,'scoreboard players set #foundation_v1 alfheim.hub 1'),
              (0.2,'schedule clear alfheim:hub/resolve'),(0.2,'schedule clear alfheim:hub/inspect_burial'),
              (0.2,'schedule clear alfheim:hub/repair_foundation'),
              (1,f'execute in {HOME} run forceload add 0 0 367 175'),
              (1,f'execute in {HOME} run forceload add -1584 512 -1329 767'),(60,'say royal and upper gallery ready'),
              (1,f'execute in {HOME} run place structure alfheim:civic_center 0 80 0'),
              (2,f'execute in {HOME} run place structure alfheim:royal_castle -1443 80 654'),
              (2,f'execute in {HOME} run locate structure alfheim:royal_castle')]
    for i,(folder,name) in enumerate(fixtures):
        commands.append((.5,f'execute in {HOME} run place template alfheim:{folder}/{name} {(i%6)*64} 176 {(i//6)*64}'))
    commands.extend([(15,'save-all flush'),(2,f'execute in {HOME} run forceload remove all'),(2,'stop')])
    props=ROOT/'server/server.properties';old=props.read_bytes()
    try:code=run_server.run(SEED,WORLD,8,commands,600)
    finally:
        props.write_bytes(old)
        (ROOT/'server/config/jade/server-plugin-overrides.json').write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    console=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=console.read_text(errors='replace')
    assert 'Generated structure "alfheim:royal_castle"' in text,'Castle site rejected; inspect bounded terrain profile'
    natural=re.search(r'nearest alfheim:royal_castle is at \[(-?\d+), ~, (-?\d+)\] \((\d+) blocks',text)
    assert natural,'No suitable natural castle ring candidate located'
    assert 'Generated structure "alfheim:civic_center"' not in text,'District entered spawn reservation'
    assert text.count('Loaded template "alfheim:')==18,'Gallery incomplete'
    assert 'That position is not loaded' not in text
    grid={}
    for path in (ROOT/'server'/WORLD/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
        for chunk in chunks(path):grid[(chunk['xPos'],chunk['zPos'])]=chunk
    cache={}
    def block(x,y,z):
        key=x//16,y//16,z//16
        if key not in cache:
            sec=next((s for s in grid.get((x//16,z//16),{}).get('sections',[]) if s['Y']==y//16),None)
            cache[key]=section_blocks(sec) if sec else None
        values=cache[key]
        return values[((y&15)<<8)|((z&15)<<4)|(x&15)] if values else None
    def verify(root,origin,r=0):
        solid=[b for b in root['blocks'] if root['palette'][int(b['state'])]['Name'] not in ('minecraft:air','minecraft:jigsaw')]
        sample=solid[::max(1,len(solid)//180)];matched=0
        for b in sample:
            x,y,z=map(int,b['pos']);x,z=rotate(x,z,r)
            matched+=block(origin[0]+x,origin[1]+y,origin[2]+z)==root['palette'][int(b['state'])]['Name']
        assert matched/len(sample)>=.97,(origin,r,matched,len(sample))
        return len(sample)
    samples=0
    for i,(folder,name) in enumerate(fixtures):
        root=nbt.load(ROOT/f'kubejs/data/alfheim/structures/{folder}/{name}.nbt')[1]
        samples+=verify(root,((i%6)*64,176,(i//6)*64))
    # Fixed command chunk: complete 235-square castle, with four original keep floors.
    x0,z0=-1573,523;cx,cz=x0+117,z0+117
    floors=[y for y in range(32,270) if block(cx,y,cz)=='alfheim:ivory_livingrock_polished']
    floor=next((y for y in floors if all(y+d in floors for d in (12,24,36))),None)
    assert floor is not None,('missing central keep floors',floors)
    base=floor-8
    for gx in range(5):
        for gz in range(5):
            kind='keep' if gx==gz==2 else 'tower' if gx in (0,4) and gz in (0,4) else \
                 ('gate' if gx==2 or gz==2 else 'curtain') if gx in (0,4) or gz in (0,4) else 'hall' if gx==2 or gz==2 else 'garden'
            r=1 if gx==4 and gz==0 else 0 if gz==0 else (2 if gz==4 else 1) if gx==4 else (3 if gx==0 else 2) if gz==4 else 3 if gx==0 else 0
            origin=(x0+gx*47+(46 if r in (1,2) else 0),base,z0+gz*47+(46 if r in (2,3) else 0))
            samples+=verify(nbt.load(ROOT/f'kubejs/data/alfheim/structures/royal_castle/{kind}.nbt')[1],origin,r)
    supports=0
    for dx in (12,117,222):
        for dz in (12,117,222):
            column=[block(x0+dx,y,z0+dz) for y in range(max(-63,base-96),base+8)]
            assert all(v not in (None,'minecraft:air','minecraft:water','minecraft:cave_air') for v in column[-8:]),'Unsupported castle deck'
            assert any(v not in (None,'minecraft:air','minecraft:water','minecraft:cave_air','alfheim:ivory_livingrock_bricks') for v in column), 'Foundation never reached original terrain'
            supports+=1
    result={'status':'LOCALLY_VALIDATED','world':WORLD,'seed':SEED,'console':str(console.relative_to(ROOT)),
            'gallery_templates':18,'castle_tiles':25,'castle_base_y':base,'castle_origin':[x0,z0],
            'verified_samples':samples,'foundation_columns':supports,'near_spawn_district_veto':'pass',
            'native_castle_placement':'forced structure command; natural ring locate output in console',
            'natural_castle_locator':{'position':[int(natural[1]),int(natural[2])],'distance':int(natural[3])},
            'upper_natural_placement':'RUNTIME_TEST_REQUIRED','visual_review':'pending',
            'installed_jar_sha256':hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest()}
    (ROOT/'tools/royal_upper_runtime_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('ROYAL/UPPER PASS:',json.dumps(result))


if __name__=='__main__':main()
