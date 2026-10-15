"""Place every refitted template in a disposable, bounded four-level test gallery.

This is a template registration/materialization test, not natural placement acceptance.
The tightly packed cells are test fixtures; no player save or natural structure set changes.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import nbt
import run_server
from cw_district_refit import ROOT, FAMILIES, cells
from probe_terraces import chunks, section_blocks

WORLD='validation-cw-refit-gallery-20261015'
HOME='mythicbotany:alfheim'
SEED='3536368297089363045'


def main():
    paths=[]
    for family in FAMILIES:
        paths.extend(sorted((ROOT/'kubejs/data/alfheim/structures/ancient'/family).glob('*.nbt')))
    paths.extend(sorted((ROOT/'kubejs/data/alfheim/structures/deepworks_archaeology/faultwork').glob('*.nbt')))
    paths.append(ROOT/'kubejs/data/alfheim/structures/ley_fracture/core.nbt')
    assert len(paths)==113,len(paths)
    commands=[(5,'gamerule randomTickSpeed 0')]
    for x in (0,192):
        for z in (0,192):
            commands.append((1,f'execute in {HOME} run forceload add {x} {z} {x+191} {z+191}'))
    commands.append((90,'say CW refit template gallery ready'))
    placements=[]
    for i,path in enumerate(paths):
        x,z=(i%6)*64,((i%36)//6)*64
        y=112+(i//36)*48
        template='alfheim:'+path.relative_to(ROOT/'kubejs/data/alfheim/structures').with_suffix('').as_posix()
        placements.append((path,(x,y,z)))
        commands.append((0.2,f'execute in {HOME} run place template {template} {x} {y} {z}'))
    commands.extend([(20,'save-all flush'),(3,f'execute in {HOME} run forceload remove all'),(2,'stop')])
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:
        code=run_server.run(SEED,WORLD,8,commands,600)
    finally:
        props.write_bytes(original)
        jade=ROOT/'server/config/jade/server-plugin-overrides.json'
        jade.parent.mkdir(parents=True,exist_ok=True)
        jade.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(errors='replace')
    assert 'All dimensions are saved' in text
    assert 'That position is not loaded' not in text,'Unloaded fixture cells: gallery placement is incomplete'
    assert text.count('Loaded template "alfheim:')==len(paths), 'Not every template command succeeded'
    grid={}
    for path in (ROOT/'server'/WORLD/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
        for chunk in chunks(path):grid[(chunk['xPos'],chunk['zPos'])]=chunk
    cache={}
    def block(x,y,z):
        key=x//16,y//16,z//16
        if key not in cache:
            chunk=grid.get((x//16,z//16),{})
            sec=next((s for s in chunk.get('sections',[]) if s['Y']==y//16),None)
            cache[key]=section_blocks(sec) if sec else None
        values=cache[key]
        return values[((y&15)<<8)|((z&15)<<4)|(x&15)] if values else None
    results=[]
    for path,origin in placements:
        root=nbt.load(path)[1];pal=root['palette']
        # Check every added relief cell and every block entity, plus a broad geometry sample.
        relative=path.relative_to(ROOT)
        baseline=ROOT/'build/continuity-district-refit/baseline'/relative
        added=[]
        if baseline.exists():
            old=cells(nbt.load(baseline)[1])
            added=[b for b in root['blocks'] if old[tuple(map(int,b['pos']))][0]['Name']=='minecraft:air'
                   and pal[int(b['state'])]['Name']!='minecraft:air']
        critical=added+[b for b in root['blocks'] if b.get('nbt') and pal[int(b['state'])]['Name']!='minecraft:jigsaw']
        for cell in critical:
            at=tuple(origin[i]+int(cell['pos'][i]) for i in range(3))
            assert block(*at)==pal[int(cell['state'])]['Name'],(path.name,at,'missing relief/fixture',block(*at))
        solids=[b for b in root['blocks'] if pal[int(b['state'])]['Name'] not in ('minecraft:air','minecraft:jigsaw')]
        sample=solids[::max(1,len(solids)//250)]
        matched=sum(block(*(origin[i]+int(b['pos'][i]) for i in range(3)))==pal[int(b['state'])]['Name'] for b in sample)
        assert matched/len(sample)>=.97,(path,matched,len(sample))
        results.append({'template':str(relative),'origin':list(origin),'relief_and_fixture_cells':len(critical),
                        'sample_matched':matched,'sample_total':len(sample),
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    report={'status':'LOCALLY_VALIDATED','runtime':'dedicated Forge 1.20.1 template placement and saved-world census',
            'seed':SEED,'minecraft':'1.20.1','forge':'47.4.10',
            'natural_placement':'RUNTIME_TEST_REQUIRED','visual_review':'pending',
            'world':WORLD,'console':str(log.relative_to(ROOT)),'templates':results}
    output=ROOT/'tools/continuity_refit_runtime_report.json'
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(f'CW REFIT RUNTIME PASS: {len(results)} templates; all added relief and fixtures saved; geometry samples passed')


if __name__=='__main__':main()
