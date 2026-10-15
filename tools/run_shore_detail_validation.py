"""Controlled shore decorations and bounded natural-generation smoke samples."""
import argparse,hashlib,json,subprocess,sys
from collections import Counter
from pathlib import Path
import run_server
from gen_shore_details import build,GROUND
from probe_terraces import chunks,section_blocks,unpack_bits,biome_at

ROOT=Path(__file__).resolve().parents[1]
FEATURES=('shore_driftwood','mistbark_stone_scatter','void_shore_wrack')
SCENARIOS=('grass','sand','gravel','native_stone','wrong_host','unsupported','water','edge','occupied')
OUTPUTS={
    'shore_driftwood':{'alfheim:gloambark_log','alfheim:hushbark_log'},
    'mistbark_stone_scatter':{'alfheim:silvermist_livingrock','alfheim:frost_livingrock'},
    'void_shore_wrack':{'alfheim:riftchalk_livingrock','alfheim:riftshale_livingrock'},
}

def source_hashes():
    paths=set(build())|{'kubejs/data/alfheim/worldgen/placed_feature/shore_driftwood.json'}
    from gen_grove_log_axes import LOGS,assets
    paths.add('kubejs/startup_scripts/12_groves.js')
    for tree in LOGS:paths.update(assets(tree))
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}

def census(world):
    cells={};natural=Counter();sampled=Counter()
    for region in (world/'dimensions/mythicbotany/alfheim/region').glob('*.mca'):
        for chunk in chunks(region):
            cx,cz=chunk['xPos'],chunk['zPos']
            pad=64<=cx<=69 and 64<=cz<=81
            patch='void' if -8<=cx<=-1 and -28<=cz<=-21 else (
                'mistbark' if -104<=cx<=-97 and 30<=cz<=37 else None)
            if not pad and not patch:continue
            if patch:assert chunk.get('Status')=='minecraft:full',('unfinished natural sample',cx,cz,chunk.get('Status'))
            if patch:sampled[patch]+=1
            for sec in chunk.get('sections',[]):
                blocks=section_blocks(sec) or []
                if pad and 12<=int(sec['Y'])<=13:
                    palette=sec['block_states']['palette'];bits=max(4,(len(palette)-1).bit_length())
                    indices=unpack_bits(sec['block_states'].get('data'),bits,4096) if len(palette)>1 else [0]*4096
                    for i,block in enumerate(blocks):
                        x=cx*16+(i&15);z=cz*16+((i>>4)&15);y=int(sec['Y'])*16+(i>>8)
                        if 195<=y<=214:cells[x,y,z]=(block,palette[indices[i]].get('Properties',{}))
                if patch:
                    for i,block in enumerate(blocks):
                        if block not in OUTPUTS['shore_driftwood']:continue
                        y=int(sec['Y'])*16+(i>>8);bid=biome_at(chunk.get('sections',[]),y,i&15,(i>>4)&15)
                        natural[patch,bid,block]+=1
    records=[];axes=Counter()
    for col,feature in enumerate(FEATURES):
        for row,scenario in enumerate(SCENARIOS):
            x=1024+col*32;z=1024+row*32
            found=[(p,b,props) for p,(b,props) in cells.items()
                if x<=p[0]<=x+18 and z<=p[2]<=z+18 and b in OUTPUTS[feature] and p[1]>=201]
            expected=scenario in ('grass','sand','gravel','native_stone','edge') and not (
                feature=='void_shore_wrack' and scenario=='grass')
            if expected:assert found,('no placement on supported pad',feature,scenario)
            else:assert not found,('unsafe placement',feature,scenario,len(found))
            for (px,py,pz),block,props in found:
                max_y=202 if feature=='mistbark_stone_scatter' else 201
                assert 201<=py<=max_y and cells[px,py-1,pz][0] in GROUND,('unsupported decoration',feature,(px,py,pz))
                if py==202:
                    assert cells[px,201,pz][0] in OUTPUTS[feature] and cells[px,200,pz][0] in GROUND,('floating upper stone',px,py,pz)
                if feature=='shore_driftwood':
                    assert props.get('axis') in ('x','z'),('upright driftwood',props)
                    axes[props['axis']]+=1
            if scenario=='occupied':
                assert all(cells[px,py,pz][0]=='minecraft:stone' for px in range(x,x+19)
                           for pz in range(z,z+19) for py in range(201,205)),('overwrote obstacle',feature)
            records.append(dict(feature=feature,scenario=scenario,placed_blocks=len(found)))
    assert axes['x'] and axes['z'],('both trunk orientations not exercised',axes)
    assert sampled=={'void':64,'mistbark':64},sampled
    from gen_grove_log_axes import LOGS
    for col,tree in enumerate(LOGS):
        for row,axis in enumerate(('x','y','z','y')):
            block,props=cells[1110+col,201,1306+row]
            assert block=='alfheim:'+tree+'_log' and props.get('axis')==axis,('log state/default lost',tree,row,props)
    return dict(cases=records,horizontal_log_axes=dict(axes),natural_sample_chunks=dict(sampled),
        saved_log_axis_states=12,
        natural_log_blocks=[dict(sample=p,biome=b,block=n,count=count) for (p,b,n),count in sorted(natural.items())])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--world',default='validation-shore-details-axes-20261014')
    ap.add_argument('--resume',action='store_true',help='Reset only the controlled pads in this disposable test world')
    ap.add_argument('--review-only',action='store_true',help='Read saved proof without launching or modifying the world')
    args=ap.parse_args();world=ROOT/'server'/args.world
    assert args.world.startswith('validation-shore-details-') and world.resolve().parent==(ROOT/'server').resolve()
    if args.review_only:
        manifests=[(p,json.loads(p.read_text(encoding='utf-8'))) for p in (ROOT/'server').glob('manifest-*.json')]
        matches=[(p,m) for p,m in manifests if m.get('level_name')==world.name]
        assert matches,world
        _,manifest=max(matches,key=lambda pair:pair[0].name)
        assert manifest['exit_code']==0 and manifest['harness_exit_code']==0 and manifest.get('command_startup_gate'),manifest
        hashes=source_hashes()
        for relative in hashes:assert (ROOT/'server'/relative).read_bytes()==(ROOT/relative).read_bytes(),relative
        write_report(world,ROOT/'server'/manifest['console'],hashes)
        return
    assert args.resume or not world.exists(),'Existing test evidence requires explicit --resume'
    subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/gen_grove_log_axes.py'),'--check'],check=True)
    for script in ('check_shore_details.py','check_field_review.py','check_feature_order.py'):
        subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools'/script)],check=True)
    for p,data in build().items():assert (ROOT/p).read_bytes()==data,p
    hashes=source_hashes();home='execute in mythicbotany:alfheim run '
    commands=[(100,'say shore detail validation'),
        (2,home+'forceload add -128 -448 -1 -321'),
        (2,home+'forceload add -1664 480 -1537 607'),
        (50,'save-all flush'),(3,home+'forceload remove all'),
        (2,home+'forceload add 1024 1024 1119 1311')]
    def add(command,delay=0.4):commands.append((delay,home+command))
    for col,feature in enumerate(FEATURES):
        for row,scenario in enumerate(SCENARIOS):
            x=1024+col*32;z=1024+row*32
            add(f'fill {x} 195 {z} {x+18} 214 {z+18} minecraft:air')
            add(f'fill {x} 198 {z} {x+18} 199 {z+18} minecraft:stone')
            ground={'grass':'minecraft:grass_block','sand':'minecraft:sand','gravel':'minecraft:gravel',
                    'native_stone':'alfheim:tide_livingrock','wrong_host':'minecraft:stone','water':'minecraft:water',
                    'edge':'minecraft:gravel','occupied':'minecraft:gravel'}.get(scenario)
            if ground:
                endx=x+9 if scenario=='edge' else x+18
                endz=z+9 if scenario=='edge' else z+18
                add(f'fill {x} 200 {z} {endx} 200 {endz} {ground}')
            if scenario=='occupied':add(f'fill {x} 201 {z} {x+18} 204 {z+18} minecraft:stone')
            # A sparse random patch may legitimately miss the supported quarter.
            # Exercise the edge with a fixed extra attempt budget, never a site search.
            for _ in range(50 if scenario=='edge' else 5):
                add(f'place feature alfheim:{feature} {x+9} 201 {z+9}',0.05 if scenario=='edge' else 0.4)
    from gen_grove_log_axes import LOGS
    for col,tree in enumerate(LOGS):
        for row,axis in enumerate(('x','y','z',None)):
            add(f'setblock {1110+col} 200 {1306+row} minecraft:stone')
            state='[axis='+axis+']' if axis else ''
            add(f'setblock {1110+col} 201 {1306+row} alfheim:{tree}_log{state}')
    commands.extend([(15,'save-all flush'),(3,home+'forceload remove all'),(3,'stop')])
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run('3536368297089363045',world.name,8,commands,600)
    finally:
        props.write_bytes(original)
        (ROOT/'server/config/jade/server-plugin-overrides.json').write_bytes(
            subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    assert hashes==source_hashes(),'source changed during validation'
    for relative in hashes:assert (ROOT/'server'/relative).read_bytes()==(ROOT/relative).read_bytes(),relative
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    assert 'All dimensions are saved' in log.read_text(encoding='utf-8',errors='replace'),log
    write_report(world,log,hashes)

def write_report(world,log,hashes):
    text=log.read_text(encoding='utf-8',errors='replace')
    assert 'All dimensions are saved' in text and 'An unexpected error occurred trying to execute' not in text,log
    report=dict(world=world.name,console=log.relative_to(ROOT).as_posix(),server_exit_code=0,
        source_sha256=hashes,**census(world),
        limits='Configured features on artificial hosts prove support and obstacle behavior, not outer rarity or biome filtering. Two untouched 64-chunk patches prove bounded natural generation loads, but their raw stone/log counts cannot uniquely identify individual features or establish final frequency. Client appearance pending.')
    (ROOT/'tools/shore_detail_runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('SHORE DETAIL PASS:',json.dumps(report))

if __name__=='__main__':main()
