"""Owned disposable-world tests for the native furnishing mechanics and reload."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import run_server

ROOT=Path(__file__).resolve().parents[1];WORLD='validation-district-furnishings-20261015';HOME='mythicbotany:alfheim'
REPORT=ROOT/'tools/district_furnishings_runtime_report.json'

def launch(commands):
    props=ROOT/'server/server.properties';old=props.read_bytes();before=set((ROOT/'server').glob('console-*.log'))
    try:code=run_server.run('3536368297089363045',WORLD,8,commands,360)
    finally:
        props.write_bytes(old);jade=ROOT/'server/config/jade/server-plugin-overrides.json';jade.parent.mkdir(parents=True,exist_ok=True)
        jade.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    console=max(set((ROOT/'server').glob('console-*.log'))-before,key=lambda p:p.stat().st_mtime)
    return console,console.read_text(errors='replace')

def commands(mode):
    result=[(2,'gamerule randomTickSpeed 0')]
    for key in ('final','created','foundation_v1'):result.append((.1,f'scoreboard players set #{key} alfheim.hub 1'))
    for key in ('resolve','inspect_burial','repair_foundation'):result.append((.1,f'schedule clear alfheim:hub/{key}'))
    result.extend([(1,f'execute in {HOME} run forceload add 1024 1024 1071 1039'),(15,'say furnishing chunks ready')])
    if mode=='audit':result.extend([(1,f'execute in {HOME} run alfheimfurnish audit'),(6,f'execute in {HOME} run alfheimfurnish automation')])
    else:result.append((1,f'execute in {HOME} run alfheimfurnish persistence'))
    result.extend([(1,'save-all flush'),(1,f'execute in {HOME} run forceload remove all'),(1,'stop')]);return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','reload']);args=ap.parse_args()
    console,text=launch(commands(args.mode))
    assert 'FURNISH_FAIL' not in text,text[text.find('FURNISH_FAIL'):][:900]
    jar='alfheim_leyworks-0.1.0.jar';sha=hashlib.sha256((ROOT/'mods'/jar).read_bytes()).hexdigest()
    assert sha==hashlib.sha256((ROOT/'server/mods'/jar).read_bytes()).hexdigest()==hashlib.sha256((ROOT/'first_party_mods/alfheim_leyworks/build/libs'/jar).read_bytes()).hexdigest()
    if args.mode=='audit':
        assert 'FURNISH_AUDIT_PASS storage=6 stations=5 recipes=11' in text,'Native audit did not complete; inspect '+str(console)
        assert text.count('FURNISH_HOPPER_PASS')==6
        evidence={'status':'NATIVE_INTERACTIONS_PASS','world':WORLD,'audit_console':str(console.relative_to(ROOT)),
            'installed_jar_sha256':sha,'storage':re.findall(r'FURNISH_STORAGE_PASS [^\r\n]+',text),
            'stations':re.findall(r'FURNISH_STATION_PASS [^\r\n]+',text),'hoppers':re.findall(r'FURNISH_HOPPER_PASS [^\r\n]+',text)}
    else:
        evidence=json.loads(REPORT.read_text());assert evidence['installed_jar_sha256']==sha
        assert text.count('FURNISH_PERSISTENCE_PASS')==6
        evidence.update(status='NATIVE_INTERACTIONS_AND_RELOAD_PASS',reload_console=str(console.relative_to(ROOT)),
            persistence=re.findall(r'FURNISH_PERSISTENCE_PASS [^\r\n]+',text))
    evidence['limits']='Native server menu transactions, storage, NBT, drops, hoppers and reload tested; multiplayer screen synchronization and client visuals require play review.'
    REPORT.write_text(json.dumps(evidence,indent=2)+'\n');print('DISTRICT FURNISHING',evidence['status'])

if __name__=='__main__':main()
