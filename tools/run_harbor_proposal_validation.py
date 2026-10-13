"""Native, read-only comparison of current and unbuilt proposed harbor footprints."""
import json
import argparse
from pathlib import Path
import re
import subprocess
import run_server
from plan_harbor_adaptation import proposals
from survey_saved_harbor_coasts import rotate

ROOT=Path(__file__).resolve().parents[1]
WORLD='validation-harbor-proposal-coasts-20261013'
VARIANTS=('shipping','narrow_docks','inland_temple','narrow_docks_inland_temple')
SITES=((-1536,564),(-1528,616),(-1552,544),(704,544),(720,544))

def enrich_attempts(rows):
    for row in rows:
        if ' attempts=' in row['profile']:
            row['profile'],_,row['attempts']=row['profile'].partition(' attempts=')
        else:row.setdefault('attempts','')
        details=[];parts=proposals()[row['proposal']]
        for entry in filter(None,row['attempts'].split(';')):
            head,values=entry.split(':');rotation,lift,requests,wx,wz=map(int,head.split(','))
            local=rotate(wx-row['x'],wz-row['z'],(4-rotation)%4)
            members=[p['name'] for p in parts if p['bounds'][0]<=local[0]<=p['bounds'][2] and p['bounds'][1]<=local[1]<=p['bounds'][3]]
            detail={'rotation':rotation,'lift':lift,'requests':requests,'x':wx,'z':wz,'local':list(local),'members':members}
            if values.startswith('missing'):
                detail.update({'accepted':False,'reason':'missing_column'})
            else:
                surface,floor,water,accepted=values.split(',');surface=int(surface);floor=int(floor);water=water=='true'
                reason='accepted' if accepted=='true' else 'other_waterline_or_support_constraint'
                if accepted!='true':
                    if water and tuple(local) in ((23,23),(23,100)):reason='required_dry_connection_is_water'
                    elif water and floor<58:reason='water_beyond_footing_reach'
                    elif surface>67+lift:reason='land_above_selected_quay_limit'
                    elif floor<58 or surface<58:reason='ground_beyond_footing_reach'
                    elif not water and any(n in ('wavebreak_pier','sunken_drydock') for n in members) and not(-16<=local[1]<16):reason='dock_column_is_dry'
                detail.update({'surface':surface,'floor':floor,'water':water,'accepted':accepted=='true','reason':reason})
            details.append(detail)
        row['attempt_details']=details

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--core',action='store_true');ap.add_argument('--refinement',action='store_true');args=ap.parse_args()
    if args.refinement:args.core=True
    variants=('core_with_approach',) if args.core else VARIANTS
    sites=((-1548,612),(-1528,616),(-1552,544),(704,544),(720,544)) if args.core else SITES
    world='validation-harbor-core-coasts-20261013' if args.core else WORLD
    if args.refinement:world='validation-harbor-refinement-coasts-20261013'
    commands=[(100,'say harbor footprint proposal comparisons; no placement')]
    commands += [(2,f'execute in mythicbotany:alfheim run alfheimharbor audit_proposal {name} {x} {z}')
                 for x,z in sites for name in variants]
    commands += [(5,'save-all flush'),(5,'stop')]
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run('3536368297089363045',world,8,commands,900)
    finally:
        props.write_bytes(original)
        jade=ROOT/'server/config/jade/server-plugin-overrides.json';jade.parent.mkdir(parents=True,exist_ok=True)
        jade.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    pattern=r'Harbor proposal audit proposal=(\S+) x=(-?\d+) z=(-?\d+) accepted=(true|false) columns=(\d+) parity=(true|false) ms=(\d+) eligible=(true|false) biome=(\S+) rotation=(-?\d+) lift=(-?\d+) profile=([^\r\n]*)'
    rows=[{'proposal':name,'x':int(x),'z':int(z),'accepted':accepted=='true','columns':int(cols),'parity':parity=='true',
           'milliseconds':int(ms),'eligible':eligible=='true','biome':biome,'rotation':int(rotation),'lift':int(lift),'profile':profile}
          for name,x,z,accepted,cols,parity,ms,eligible,biome,rotation,lift,profile in re.findall(pattern,text)]
    enrich_attempts(rows)
    assert len(rows)==len(sites)*len(variants),(len(rows),log)
    assert all(r['parity'] for r in rows),rows
    summary={name:{'audits':sum(r['proposal']==name for r in rows),
                   'accepted':sum(r['proposal']==name and r['accepted'] for r in rows),
                   'accepted_eligible':sum(r['proposal']==name and r['accepted'] and r['eligible'] for r in rows),
                   'max_milliseconds':max(r['milliseconds'] for r in rows if r['proposal']==name)} for name in variants}
    result={'world':world,'console':str(log.relative_to(ROOT)),'seed':'3536368297089363045',
            'scope':'native footprint feasibility only; proposed furniture/templates are not authored or placed',
            'server_exit_code':code,'validation_exit_code':0,'sampling_parity':'pass','summary':summary,'audits':rows,
            'natural_placement':'withheld'}
    output='harbor_core_native_validation.json' if args.core else 'harbor_proposal_native_validation.json'
    if args.refinement:
        output='harbor_refinement_native_validation.json'
        prior=json.loads((ROOT/'tools/harbor_core_native_validation.json').read_text(encoding='utf-8'))['audits']
        before={(a['x'],a['z']):a for a in prior}
        for row in rows:
            old=before[(row['x'],row['z'])]
            assert row['accepted']==old['accepted'] and row['eligible']==old['eligible'],(row,old)
        result['comparisons']=[{'x':a['x'],'z':a['z'],'before_columns':before[(a['x'],a['z'])]['columns'],
                                'after_columns':a['columns'],'before_ms':before[(a['x'],a['z'])]['milliseconds'],
                                'after_ms':a['milliseconds']} for a in rows]
        result['acceptance_and_biome_parity']='pass'
    (ROOT/'tools'/output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('HARBOR PROPOSAL NATIVE CHECK PASS:',len(rows),'audits;',json.dumps(summary))

if __name__=='__main__':main()
