"""Exercise six new monster species, native AI attacks, habitat spawns and saved appearances."""
import hashlib,json,os,time
from pathlib import Path
import run_server

ROOT=Path(__file__).resolve().parents[1]

def main():
    os.chdir(ROOT)
    server=(ROOT/'server').resolve()
    for name in run_server.MIRROR:
        target=(server/name).resolve()
        assert target.parent==server and target.is_relative_to(ROOT),target
    world='validation-monstrosities-'+time.strftime('%Y%m%d-%H%M%S')
    assert not (server/world).exists(),'Disposable world already exists'
    props=server/'server.properties';previous=props.read_bytes()
    try:
        code=run_server.run('20261016',world,6,[
            (1,'gamerule doMobSpawning false'),(0,'difficulty hard'),
            (0,'time set midnight'),(0,'gamerule doDaylightCycle false'),
            (0,'execute in mythicbotany:alfheim run forceload add 480 480 495 495'),
            (1,'execute in mythicbotany:alfheim run fill 480 219 480 495 227 495 minecraft:stone'),
            (1,'execute in mythicbotany:alfheim run fill 481 220 481 494 226 494 minecraft:air'),
            (5,'execute in mythicbotany:alfheim positioned 488 220 488 run alfheim_monstrosities_audit'),
            (4,'save-all flush'),(1,'stop')],120)
    finally:
        props.write_bytes(previous)
    manifests=[(p,json.loads(p.read_text())) for p in server.glob('manifest-*.json')]
    path,evidence=next((p,m) for p,m in sorted(manifests,reverse=True) if m.get('level_name')==world)
    console=server/evidence['console'];log=console.read_text(errors='replace')
    marker='ALFHEIM_MONSTROSITIES_PASS species=6 appearances=18 attack_checks=18 sight_blocks=18 saved_variants=18 ai_attacks=6 habitat_entries=29 troll_player_height_ratio=2.0'
    assert code==0 and evidence['exit_code']==0 and marker in log,(code,console)
    jar=ROOT/'mods/alfheim_companion-0.2.0.jar'
    assert jar.read_bytes()==(server/'mods/alfheim_companion-0.2.0.jar').read_bytes()
    assert jar.read_bytes()==(ROOT/'first_party_mods/alfheim_companion/build/libs/alfheim_companion-0.2.0.jar').read_bytes()
    report={'jar_sha256':hashlib.sha256(jar.read_bytes()).hexdigest(),
        'runtime_manifest':str(path.relative_to(ROOT)),'console':str(console.relative_to(ROOT)),
        'result':marker,'client_visual_review':'pending; native attacks and biome entries tested; client animation/lighting and long-run spawn density remain pending'}
    (ROOT/'tools/monstrosities_build.json').write_text(json.dumps(report,indent=2)+'\n')
    print(marker)

if __name__=='__main__':main()
