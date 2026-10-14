"""Bounded substrate/underside tests in a disposable world, never player saves.

Test-only selector wrappers retain the production offset and environment scan.
They omit rarity, in_square, heightmap and biome filters; natural frequency and
heightmap selection remain unproved. The 32-step underside scan IS exercised.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import run_server
from probe_terraces import chunks,section_blocks

ROOT=Path(__file__).resolve().parents[1]
CASES=[
    ('verge_markers','riftchalk','veilstone','up'),
    ('shatter_anchors','shardbreccia','anchorstone','up'),
    ('mourning_steles','mourning','epitaph','up'),
    ('verge_shear_steps','riftchalk','riftshale','up'),
    ('shatter_fault_teeth','shardbreccia','seamstone','up'),
    ('prism_split_inclusions','aetherquartzite','glintschist','ore'),
    ('rootfall_fossil_knots','hollowheart','rootfossil','ore'),
    ('sepulchral_fallen_plates','mourning','epitaph','up'),
    ('starless_null_teeth','nightmantle','nullstone','up'),
    ('shatter_hanging_faults','shardbreccia','seamstone','down'),
    ('prism_suspended_needles','aetherquartzite','amethyst','down'),
    ('rootfall_hanging_ribs','hollowheart','rootfossil','down'),
]
SCENARIOS=('native_host','wrong_host','unsupported_air','thick_shelf_or_water')

def stone(name):
    return 'minecraft:amethyst_block' if name=='amethyst' else 'alfheim:'+name+'_livingrock'

def paths(name):
    return [ROOT/f'kubejs/data/alfheim/worldgen/{kind}/void/{name}.json'
            for kind in ('configured_feature','placed_feature')]+[
            ROOT/f'kubejs/data/alfheim/forge/biome_modifier/void_{name}.json',
            ROOT/'kubejs/data/alfheim/tags/blocks/void_natural.json']

def census(world):
    blocks={}
    for file in (world/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
        for chunk in chunks(file):
            if not (128<=chunk['xPos']<=146 and 128<=chunk['zPos']<=133):continue
            for sec in chunk.get('sections',[]):
                if not 11<=int(sec['Y'])<=16:continue
                for i,name in enumerate(section_blocks(sec) or []):
                    x=chunk['xPos']*16+(i&15);z=chunk['zPos']*16+((i>>4)&15)
                    y=int(sec['Y'])*16+(i>>8)
                    if 2048<=x<=2330 and 2048<=z<=2138 and 180<=y<=260:
                        blocks[x,y,z]=name
    records=[]
    for index,(name,host,signature,mode) in enumerate(CASES):
        counts=[];attachment_columns=0
        for scenario in range(4):
            x=2048+index*24;z=2048+scenario*24
            cells=[(p,b) for p,b in blocks.items() if x<=p[0]<=x+18 and z<=p[2]<=z+18]
            assert len(cells)==19*19*81,('missing test cells',name,scenario,len(cells))
            hits=sum(b==stone(signature) for _,b in cells)
            if scenario==0:
                assert hits>0,('no signature',name)
                if mode in ('up','down'):
                    # Every generated column connects to the original host face.
                    columns={ (p[0],p[2]) for p,b in cells
                        if b!='minecraft:air' and (p[1]>244 if mode=='up' else p[1]<240)}
                    for px,pz in columns:
                        assert blocks[px,244 if mode=='up' else 240,pz]==stone(host),(name,'detached host')
                        occupied=[py for py in range(180,261) if blocks[px,py,pz]!='minecraft:air'
                            and (py>244 if mode=='up' else py<240)]
                        expected=list(range(245,max(occupied)+1)) if mode=='up' else list(range(min(occupied),240))
                        assert occupied==expected,(name,'broken column',px,pz)
                    attachment_columns=len(columns)
            else:
                assert hits==0,('unsafe placement',name,SCENARIOS[scenario],hits)
                def names(value):
                    if isinstance(value,dict):
                        if 'Name' in value:yield value['Name']
                        for v in value.values():yield from names(v)
                    elif isinstance(value,list):
                        for v in value:yield from names(v)
                outputs=set(names(json.loads(paths(name)[0].read_text(encoding='utf-8'))))
                unexpected=[p for p,b in cells if b in outputs and not (
                    scenario==3 and mode=='down' and 208<=p[1]<=244 and b==stone(host))]
                assert not unexpected,('unsafe non-signature material',name,SCENARIOS[scenario],unexpected[:3])
            counts.append(hits)
        records.append(dict(feature=name,mode=mode,signature_blocks=dict(zip(SCENARIOS,counts)),
                            attached_columns=attachment_columns))
    return records

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--world',default='validation-void-formations-20261014')
    ap.add_argument('--review-only',action='store_true',help='Read existing saved evidence without booting')
    args=ap.parse_args();world=ROOT/'server'/args.world
    assert args.world.startswith('validation-void-formations-') and world.resolve().parent==(ROOT/'server').resolve()
    if args.review_only:
        review_saved(world)
        return
    assert not world.exists(),'Use a fresh disposable world; refusing to overwrite evidence'
    for script in ('check_field_review.py','check_void_geology.py','check_feature_order.py'):
        subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools'/script)],check=True)
    source={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for name,_,_,_ in CASES for p in paths(name)}
    pack=world/'datapacks/formation_probe'
    pack.mkdir(parents=True)
    (pack/'pack.mcmeta').write_text(json.dumps({'pack':{'pack_format':15,'description':'Disposable formation placement probes'}}),encoding='utf-8')
    commands=[(100,'say void formation support tests'),
              (2,'execute in mythicbotany:alfheim run forceload add 2048 2048 2335 2143')]
    def command(line,delay=0.25):commands.append((delay,'execute in mythicbotany:alfheim run '+line))
    for index,(name,host,signature,mode) in enumerate(CASES):
        placed=json.loads(paths(name)[1].read_text(encoding='utf-8'))
        modifiers=[p for p in placed['placement'] if p['type'] in
                   ('minecraft:random_offset','minecraft:environment_scan','minecraft:block_predicate_filter')]
        wrapper={'type':'minecraft:simple_random_selector','config':{'features':[
            {'feature':'alfheim:void/'+name,'placement':modifiers}]}}
        path=pack/f'data/formation_probe/worldgen/configured_feature/{name}.json'
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(wrapper,indent=2)+'\n',encoding='utf-8')
        for scenario in range(4):
            x=2048+index*24;z=2048+scenario*24
            command(f'fill {x} 180 {z} {x+18} 260 {z+18} minecraft:air')
            if scenario!=2:
                material=stone(host) if scenario==0 or (scenario==3 and mode=='down') else (
                    'minecraft:stone' if scenario==1 else 'minecraft:water')
                bottom=208 if scenario==3 and mode=='down' else 240
                command(f'fill {x} {bottom} {z} {x+18} 244 {z+18} {material}')
            for _ in range(5 if mode=='ore' else 2):
                command(f'place feature formation_probe:{name} {x+9} {244 if mode=="ore" else 245} {z+9}')
            # Persist BulkSectionAccess ore edits by touching each affected host chunk.
            if mode=='ore' and scenario==0:
                for px in range(x//16*16,(x+18)//16*16+1,16):
                    for pz in range(z//16*16,(z+18)//16*16+1,16):
                        tx=max(x,px);tz=max(z,pz)
                        command(f'setblock {tx} 240 {tz} minecraft:stone')
                        command(f'setblock {tx} 240 {tz} {stone(host)}')
    commands.extend([(15,'save-all flush'),(3,'execute in mythicbotany:alfheim run forceload remove all'),(3,'stop')])
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run('3536368297089363045',world.name,8,commands,600)
    finally:
        props.write_bytes(original)
        (ROOT/'server/config/jade/server-plugin-overrides.json').write_bytes(
            subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    assert 'All dimensions are saved' in text and 'Placed "formation_probe:' in text,log
    for relative,digest in source.items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,relative
        assert (ROOT/'server'/relative).read_bytes()==(ROOT/relative).read_bytes(),relative
    report=dict(world=world.name,console=log.relative_to(ROOT).as_posix(),server_exit_code=0,
        scope='Controlled hosts with production offsets and bounded underside scans; rarity, heightmap, biome selection, natural frequency and client appearance untested.',
        forced_chunk_limit=108,cases=census(world),source_sha256=source)
    write_review(report)
    print('VOID FORMATION PASS:',json.dumps(report['cases']))

def review_saved(world):
    manifests=[json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'server').glob('manifest-*.json')]
    matching=[m for m in manifests if m.get('level_name')==world.name]
    assert len(matching)==1,('ambiguous runtime evidence',world.name)
    manifest=matching[0]
    assert manifest['exit_code']==0 and manifest['harness_exit_code']==0,manifest
    text=(ROOT/'server'/manifest['console']).read_text(encoding='utf-8',errors='replace')
    assert 'All dimensions are saved' in text and 'Placed "formation_probe:' in text
    source={}
    for name,_,_,_ in CASES:
        for p in paths(name):
            assert (ROOT/'server'/p.relative_to(ROOT)).read_bytes()==p.read_bytes(),p
            source[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
        placed=json.loads(paths(name)[1].read_text(encoding='utf-8'))
        modifiers=[p for p in placed['placement'] if p['type'] in
                   ('minecraft:random_offset','minecraft:environment_scan','minecraft:block_predicate_filter')]
        wrapper=json.loads((world/f'datapacks/formation_probe/data/formation_probe/worldgen/configured_feature/{name}.json').read_text(encoding='utf-8'))
        assert wrapper=={'type':'minecraft:simple_random_selector','config':{'features':[
            {'feature':'alfheim:void/'+name,'placement':modifiers}]}},name
    report=dict(world=world.name,console='server/'+manifest['console'],server_exit_code=0,
        scope='Controlled hosts with production offsets and bounded underside scans; rarity, heightmap, biome selection, natural frequency and client appearance untested.',
        forced_chunk_limit=108,cases=census(world),source_sha256=source)
    write_review(report)
    print('VOID FORMATION SAVED PASS:',json.dumps(report['cases']))

def write_review(report):
    world=ROOT/'server'/report['world'];pack=world/'datapacks/formation_probe'
    report['test_pack_sha256']={p.relative_to(world).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in pack.rglob('*') if p.is_file()}
    (ROOT/'tools/void_formation_runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# Void formation support review','',
        'Controlled runtime review, 2026-10-14. Player saves and broad terrain were not modified.','',
        'Verge markers, Shatter anchors and mourning steles now require their native stone beneath the initial air cell. They retain one column per attempt, original height distributions and outer rarity. Previously their configured columns accepted air without checking the support below.','',
        'The nine newer formations are tested alongside those three repairs. Test-only selector wrappers preserve production offsets and environment scans. Hanging formations start above a five-block native shelf, scan down through it, and grow from its underside; a 37-block shelf exceeds the 32-step limit and rejects.','',
        '| Formation | Correct-host signature blocks | Wrong host | Unsupported air | Thick shelf or water | Attached columns |',
        '|---|---:|---:|---:|---:|---:|']
    for case in report['cases']:
        counts=case['signature_blocks']
        lines.append('| '+case['feature']+' | '+' | '.join(str(counts[s]) for s in SCENARIOS)+
                     ' | '+str(case['attached_columns'])+' |')
    lines+=['','Every upright and hanging column is continuous and touches its original native host. Ore inclusions replace only their matching host; ordinary host updates persist the manual ore edits before the saved-world census. Each case occupies four isolated 19×19 pads. The test forces 108 chunks once and performs no site search.','',
        'Rarity, in-square, heightmap and biome filters are omitted from these controlled wrappers. This establishes substrate behavior and bounded underside scanning, not natural frequency, landscape fit or client appearance. Existing bramble/thorn natural-sample evidence remains separate.','',
        f"World: `server/{world.name}`. Console: `{report['console']}`. Machine-readable source and test-pack hashes: `tools/void_formation_runtime.json`."]
    (ROOT/'alfheim_reclaimed_design/void/FORMATION_SUPPORT_REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':main()
