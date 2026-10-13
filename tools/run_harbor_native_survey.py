"""Read-only native density/height audit, no artificial coastal edits."""
import argparse
import json
from pathlib import Path
import re
import run_server

ROOT=Path(__file__).resolve().parents[1]
WORLD='validation-harbor-real-coasts-20261012'

def main():
    global WORLD
    ap=argparse.ArgumentParser();ap.add_argument('--apron',action='store_true');ap.add_argument('--profiles',action='store_true');ap.add_argument('--adaptive',action='store_true');ap.add_argument('--mainland',action='store_true');ap.add_argument('--low-bank',action='store_true');args=ap.parse_args()
    saved=json.loads((ROOT/'tools/harbor_saved_coast_survey.json').read_text())
    unique=list(dict.fromkeys((p['x'],p['z']) for p in saved['preflight_candidates']))
    selected=unique[::3]
    if args.apron:
        previous=json.loads((ROOT/'tools/harbor_native_coast_survey_before_apron.json').read_text())['audits']
        selected=[(r['x'],r['z']) for r in sorted((r for r in previous if r['eligible']),key=lambda r:r['columns'],reverse=True)[:4]]
        WORLD='validation-harbor-real-coasts-apron-20261012'
    if args.profiles:
        selected=[(-1600,528),(-1616,528)]
        WORLD='validation-harbor-coast-profiles-20261013'
    if args.adaptive:
        selected=[(-1600,528),(-1616,528)]
        WORLD='validation-harbor-adaptive-coasts-20261013'
    if args.mainland:
        saved=json.loads((ROOT/'tools/harbor_mainland_coast_survey.json').read_text(encoding='utf-8'))
        selected=list(dict.fromkeys((p['x'],p['z']) for p in saved['preflight_candidates']))
        WORLD='validation-harbor-mainland-coasts-20261013'
    if args.low_bank:
        saved=json.loads((ROOT/'tools/harbor_mainland_low_bank_survey.json').read_text(encoding='utf-8'))
        selected=list(dict.fromkeys((p['x'],p['z']) for p in saved['preflight_candidates']))
        WORLD='validation-harbor-low-bank-coasts-20261013'
    assert selected,'No sites selected for native audit'
    commands=[(100,'say harbor native shoreline audit')]
    commands += [(2,f'execute in mythicbotany:alfheim run alfheimharbor audit_generated {x} {z}') for x,z in selected]
    commands += [(5,'save-all flush'),(5,'stop')]
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run('3536368297089363045',WORLD,8,commands,900)
    finally:props.write_bytes(original)
    assert code==0,code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    rows=[{'x':int(x),'z':int(z),'accepted':a=='true','columns':int(cols),'parity':parity=='true','milliseconds':int(ms),'eligible':eligible=='true','biome':biome}
          for x,z,a,cols,parity,ms,eligible,biome in re.findall(r'Harbor generated audit x=(-?\d+) z=(-?\d+) accepted=(true|false) columns=(\d+) parity=(true|false) ms=(\d+) eligible=(true|false) biome=(\S+)',text)]
    assert len(rows)==len(selected),(len(rows),len(selected),log)
    assert all(r['parity'] for r in rows),rows
    result={'world':WORLD,'console':str(log.relative_to(ROOT)),'seed':'3536368297089363045','source':'native generator, no fixture fills','audits':rows,'accepted':sum(r['accepted'] for r in rows),'accepted_and_biome_eligible':sum(r['accepted'] and r['eligible'] for r in rows),'max_milliseconds':max(r['milliseconds'] for r in rows),'sampling_parity':'pass','site_plans':re.findall(r'Harbor generated audit x=(-?\d+) z=(-?\d+).*rotation=(-?\d+) lift=(-?\d+)',text),'profiles':re.findall(r'Harbor generated audit .*profile=(.*)',text),'natural_placement':'withheld'}
    output='harbor_low_bank_native_survey.json' if args.low_bank else 'harbor_mainland_native_survey.json' if args.mainland else 'harbor_native_coast_survey.json'
    (ROOT/'tools'/output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('HARBOR NATIVE SURVEY PASS:',len(rows),'sites;',result['accepted'],'accepted;',result['accepted_and_biome_eligible'],'eligible; max',result['max_milliseconds'],'ms')

if __name__=='__main__':main()
