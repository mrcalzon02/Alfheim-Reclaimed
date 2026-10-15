"""Test the floor repair against a disposable copy of real saved holes."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
import run_server
from probe_terraces import chunks,section_blocks
ROOT=Path(__file__).resolve().parents[1]

def floors(world):
    result={}
    for c in chunks(world/'dimensions/mythicbotany/alfheim/region/r.0.0.mca'):
        x,z=int(c['xPos']),int(c['zPos'])
        if not(0<=x<=3 and 0<=z<=9) or c.get('Status')!='minecraft:full':continue
        sec=next(s for s in c['sections'] if s['Y']==-4)
        result[x,z]=section_blocks(sec)[:256]
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--world',default='validation-floor-20261014');args=ap.parse_args()
    assert args.world.startswith('validation-floor-') and Path(args.world).name==args.world
    src=ROOT/'saves/New World staven';world=ROOT/'server'/args.world
    assert not world.exists()
    for rel in ('level.dat','data/scoreboard.dat','dimensions/mythicbotany/alfheim/region/r.0.0.mca',
                'dimensions/mythicbotany/alfheim/entities/r.0.0.mca',
                'dimensions/mythicbotany/alfheim/region/r.0.-1.mca',
                'dimensions/mythicbotany/alfheim/entities/r.0.-1.mca'):
        source=src/rel
        if source.exists():
            target=world/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    before=floors(world);assert len(before)==40
    missing=sum(b!='minecraft:bedrock' for bs in before.values() for b in bs);assert missing>0
    commands=[(5,'say floor repair on disposable saved-world copy'),
        (1,'execute in mythicbotany:alfheim run forceload add -16 -16 63 159'),
        (5,'function alfheim:hub/inspect_burial'),
        (10,'function alfheim:hub/fallback'),
        (5,'execute in mythicbotany:alfheim run data get entity @e[type=minecraft:marker,tag=alfheim_hub,tag=!alfheim_hub_baked,limit=1] Pos'),
        (5,'save-all flush'),(2,'execute in mythicbotany:alfheim run forceload remove all'),(2,'stop')]
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run('-3282135118187884121',world.name,8,commands,400)
    finally:
        props.write_bytes(original)
        (ROOT/'server/config/jade/server-plugin-overrides.json').write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    after=floors(world);assert set(after)==set(before)
    remaining=sum(b!='minecraft:bedrock' for bs in after.values() for b in bs)
    report={'world':world.name,'copied_source':src.name,'checked_chunks':len(after),'checked_columns':len(after)*256,
        'missing_before':missing,'missing_after':remaining,'server_exit':code,
        'limits':'Only the four-by-ten chunk non-Void sample. Void exclusion requires separate runtime review. Player save untouched.'}
    manifests=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'server').glob('manifest-*.json'))]
    manifest=next(m for m in reversed(manifests) if m.get('level_name')==world.name)
    report['console']='server/'+manifest['console']
    report['build']=json.loads((ROOT/'tools/bedrock_guard_build.json').read_text())
    guard=ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion/worldgen/BedrockFloorGuard.java'
    report['guard_source_sha256']=hashlib.sha256(guard.read_bytes()).hexdigest()
    (ROOT/'tools/bedrock_guard_runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('FLOOR GUARD:',report);assert remaining==0

if __name__=='__main__':main()
