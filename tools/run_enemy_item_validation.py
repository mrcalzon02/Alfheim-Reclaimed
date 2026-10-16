"""Check all 390 real spawn-item selections in a disposable dedicated-server world."""
import hashlib,json
from pathlib import Path
import run_server
ROOT=Path(__file__).resolve().parents[1]

def main():
    server=(ROOT/'server').resolve()
    # The existing harness replaces only these runtime mirrors; verify every recursive target.
    for name in run_server.MIRROR:
        target=(server/name).resolve()
        assert target.is_relative_to(server) and target!=server,target
    world='validation-enemy-items-20261016'
    assert not (server/world).exists(),'Use a fresh disposable world name'
    props=server/'server.properties';previous=props.read_bytes()
    commands=[(1,'gamerule doMobSpawning false'),(0,'difficulty normal'),
        (0,'execute in mythicbotany:alfheim run forceload add 480 480 495 495'),
        (4,'execute in mythicbotany:alfheim positioned 488 220 488 run alfheim_enemies_audit items'),
        (5,'save-all flush'),(1,'stop')]
    try:code=run_server.run('3536368297089363045',world,8,commands,300)
    finally:props.write_bytes(previous)
    manifests=[(p,json.loads(p.read_text())) for p in server.glob('manifest-*.json')]
    manifest=max((p,m) for p,m in manifests if m.get('level_name')==world)[1]
    log=(server/manifest['console']).read_text(encoding='utf-8',errors='replace')
    marker='ALFHEIM_ENEMY_ITEMS_PASS selections=390 saved_stacks=390 actual_egg_spawns=390 persisted_appearances=390 automatic_eggs=5'
    assert code==0 and marker in log,manifest['console']
    assert 'An unexpected error occurred' not in log
    jar=ROOT/'mods/alfheim_companion-0.2.0.jar'
    report={'world':world,'console':manifest['console'],'server_exit':code,'proof':marker,
        'jar_sha256':hashlib.sha256(jar.read_bytes()).hexdigest(),'client_visual_review':'pending'}
    (ROOT/'tools/enemy_item_runtime_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(marker)

if __name__=='__main__':main()
