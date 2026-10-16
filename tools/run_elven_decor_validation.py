"""Disposable Forge tests for the purely decorative library and prior utility regression."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import run_server

ROOT=Path(__file__).resolve().parents[1];WORLD='validation-elven-decor-20261015';HOME='mythicbotany:alfheim'
REPORT=ROOT/'tools/elven_decor_runtime_report.json'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','reload']);args=ap.parse_args()
    commands=[(2,'gamerule randomTickSpeed 0')]
    for key in ('final','created','foundation_v1'):commands.append((.1,f'scoreboard players set #{key} alfheim.hub 1'))
    for key in ('resolve','inspect_burial','repair_foundation'):commands.append((.1,f'schedule clear alfheim:hub/{key}'))
    commands.extend([(1,f'execute in {HOME} run forceload add 2048 2048 2095 2103'),
        (1,f'execute in {HOME} run forceload add 1024 1024 1071 1039'),(20,'say decorative fixture chunks ready')])
    if args.mode=='audit':
        commands.extend([(1,f'execute in {HOME} run alfheimdecor audit'),(1,f'execute in {HOME} run alfheimfurnish audit'),(6,f'execute in {HOME} run alfheimfurnish automation')])
    else:commands.extend([(1,f'execute in {HOME} run alfheimdecor inspect'),(1,f'execute in {HOME} run alfheimfurnish persistence')])
    commands.extend([(1,'save-all flush'),(1,f'execute in {HOME} run forceload remove all'),(1,'stop')])
    props=ROOT/'server/server.properties';old=props.read_bytes();before=set((ROOT/'server').glob('console-*.log'))
    try:code=run_server.run('3536368297089363045',WORLD,8,commands,420)
    finally:
        props.write_bytes(old);jade=ROOT/'server/config/jade/server-plugin-overrides.json';jade.parent.mkdir(parents=True,exist_ok=True)
        jade.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    console=max(set((ROOT/'server').glob('console-*.log'))-before,key=lambda p:p.stat().st_mtime)
    text=console.read_text(errors='replace');assert 'DECOR_FAIL' not in text and 'FURNISH_FAIL' not in text,'Native audit failure: '+str(console)
    jar='alfheim_leyworks-0.1.0.jar';sha=hashlib.sha256((ROOT/'mods'/jar).read_bytes()).hexdigest()
    assert sha==hashlib.sha256((ROOT/'server/mods'/jar).read_bytes()).hexdigest()==hashlib.sha256((ROOT/'first_party_mods/alfheim_leyworks/build/libs'/jar).read_bytes()).hexdigest()
    if args.mode=='audit':
        assert 'DECOR_AUDIT_PASS objects=38 rotations=152 assemblies=14 walls=13' in text,'Missing decorative audit summary: '+str(console)
        assert 'FURNISH_AUDIT_PASS storage=6 stations=5 recipes=11' in text and text.count('FURNISH_HOPPER_PASS')==6
        ids=re.findall(r'DECOR_OBJECT_PASS (\S+)',text);assert len(ids)==38
        result={'status':'NATIVE_DECOR_PLACEMENT_PASS','world':WORLD,'console':str(console.relative_to(ROOT)),
            'installed_jar_sha256':sha,'registered_ids':ids,'objects':38,'model_parts':52,'facings_tested':152,'assemblies_tested':14,'wall_mounts_tested':13,
            'checks':['actual BlockItem placement and item consumption','four facings','two-part completion','base and extension survival break: one drop','creative extension break: zero drops','blocked assembly rejection','wall support loss recovery','no block entities or menu providers','38 native recipes with resolved ingredients']}
        utility={'status':'NATIVE_INTERACTIONS_PASS','world':WORLD,'audit_console':str(console.relative_to(ROOT)),'installed_jar_sha256':sha,
            'storage':re.findall(r'FURNISH_STORAGE_PASS [^\r\n]+',text),'stations':re.findall(r'FURNISH_STATION_PASS [^\r\n]+',text),'hoppers':re.findall(r'FURNISH_HOPPER_PASS [^\r\n]+',text)}
    else:
        result=json.loads(REPORT.read_text());assert result['installed_jar_sha256']==sha
        assert 'DECOR_RELOAD_PASS objects=38 parts=52' in text and text.count('FURNISH_PERSISTENCE_PASS')==6
        result.update(status='NATIVE_DECOR_AND_RELOAD_PASS',reload_console=str(console.relative_to(ROOT)),saved_objects=38,saved_parts=52)
        utility=json.loads((ROOT/'tools/district_furnishings_runtime_report.json').read_text());assert utility['installed_jar_sha256']==sha
        utility.update(status='NATIVE_INTERACTIONS_AND_RELOAD_PASS',reload_console=str(console.relative_to(ROOT)),persistence=re.findall(r'FURNISH_PERSISTENCE_PASS [^\r\n]+',text))
    result['limits']='Client cutout-glass appearance, item-model presentation and multiplayer placement need visual/play review. No new natural decoration placements in this modeling wave.'
    REPORT.write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'tools/district_furnishings_runtime_report.json').write_text(json.dumps(utility,indent=2)+'\n')
    print('ELVEN DECOR:',result['status'],'prior utility tests pass')

if __name__=='__main__':main()
