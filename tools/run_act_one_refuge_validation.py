"""Test the candidate JAR in a new disposable server world; preserve installed pack JAR."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
import run_server

ROOT=Path(__file__).resolve().parents[1]


def main():
    os.chdir(ROOT);server=(ROOT/'server').resolve()
    assert not run_server.running_servers(),'Another validation server is running; leave it untouched'
    for name in run_server.MIRROR:
        target=(server/name).resolve();assert target.is_relative_to(server) and target!=server
    candidate=ROOT/'first_party_mods/alfheim_companion/build/libs/alfheim_companion-0.2.0.jar'
    tested=hashlib.sha256(candidate.read_bytes()).hexdigest()
    previous=set(server.glob('console-*.log'));props=server/'server.properties';original_props=props.read_bytes()
    server_jar=server/'mods/alfheim_companion-0.2.0.jar';original_jar=server_jar.read_bytes()
    installed=ROOT/'mods/alfheim_companion-0.2.0.jar';installed_hash=hashlib.sha256(installed.read_bytes()).hexdigest()
    mirror=run_server.mirror_instance
    def candidate_mirror():
        count=mirror();shutil.copyfile(candidate,server_jar);return count
    run_server.mirror_instance=candidate_mirror
    world='validation-act-one-refuge-'+time.strftime('%Y%m%d-%H%M%S')
    assert not (server/world).exists()
    try:
        code=run_server.run('2026101801',world,6,[
            (1,'gamerule doMobSpawning false'),(0,'gamerule randomTickSpeed 0'),
            (0,'execute in mythicbotany:alfheim run forceload add 2048 2048 2175 2143'),
            (7,'execute in mythicbotany:alfheim positioned 2048 180 2048 run alfheim_refuge_audit'),
            (5,'save-all flush'),(2,'stop')],180)
    finally:
        props.write_bytes(original_props);server_jar.write_bytes(original_jar);run_server.mirror_instance=mirror
    consoles=set(server.glob('console-*.log'))-previous;assert consoles,'Server did not launch'
    console=max(consoles,key=lambda p:p.stat().st_mtime);log=console.read_text(errors='replace')
    marker='ALFHEIM_REFUGE_PASS vendors=6 offers=43 persisted_stock=6 restocks=6 repairs=paid_atomic_nbt_preserved dungeon_doors=preserved'
    passed=code==0 and marker in log
    report={'status':'runtime validated in disposable test' if passed else 'runtime failed',
            'test':'controlled native piece placement, merchant menu transactions and paid repairs; not natural placement',
            'world':world,'console':str(console.relative_to(ROOT)),'candidate_jar_sha256':tested,'harness_exit':code,
            'installed_jar_unchanged':hashlib.sha256(installed.read_bytes()).hexdigest()==installed_hash,
            'server_jar_restored':server_jar.read_bytes()==original_jar,'marker':marker if passed else None,
            'pending':['natural monastery/refuge placement','full client visual and interaction review','encounter controllers and safe-town combat boundaries','multiplayer sessions']}
    (ROOT/'tools/act_one_refuge_runtime_report.json').write_text(json.dumps(report,indent=2)+'\n')
    assert passed,(code,console)
    print(marker,flush=True)


if __name__=='__main__':main()
