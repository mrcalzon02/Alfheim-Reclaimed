"""Bounded native-policy metrics and one actual placement on an unmodified coast."""
import json
from pathlib import Path
import re
import subprocess
import sys
import run_server

ROOT=Path(__file__).resolve().parents[1]
WORLD='validation-harbor-bounded-20261013'
SITES=((-1548,612),(-1528,616),(-1552,544),(704,544),(720,544),(-1600,528),(4096,4096))

def main():
    commands=[(100,'say bounded harbor native checks')]
    commands += [(2,f'execute in mythicbotany:alfheim run alfheimharbor audit_bounded {x} {z}') for x,z in SITES]
    commands += [(2,'execute in mythicbotany:alfheim run forceload add 624 448 815 623'),
                 (60,'execute in mythicbotany:alfheim run place structure alfheim:harbor_complex 704 64 544'),
                 (35,'save-all flush'),(5,'execute in mythicbotany:alfheim run forceload remove all'),(5,'stop')]
    props=ROOT/'server/server.properties';original=props.read_bytes()
    try:code=run_server.run('3536368297089363045',WORLD,8,commands,900)
    finally:
        props.write_bytes(original)
        p=ROOT/'server/config/jade/server-plugin-overrides.json';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
    assert code==0,code
    log=max((ROOT/'server').glob('console-*.log'),key=lambda p:p.stat().st_mtime)
    text=log.read_text(encoding='utf-8',errors='replace')
    pattern=r'Harbor bounded audit x=(-?\d+) z=(-?\d+) accepted=(true|false) columns=(\d+) parity=(true|false) ms=(\d+) eligible=(true|false) biome=(\S+) rotation=(-?\d+) lift=(-?\d+) profile=([^\r\n]*?) attempts=bounded:(\S+)'
    rows=[{'x':int(x),'z':int(z),'accepted':a=='true','columns':int(cols),'parity':parity=='true','ms_including_parity':int(ms),
           'eligible':e=='true','biome':biome,'rotation':int(r),'lift':int(lift),'outcome':outcome}
          for x,z,a,cols,parity,ms,e,biome,r,lift,profile,outcome in re.findall(pattern,text)]
    assert len(rows)==len(SITES),(len(rows),log)
    assert all(a['columns']<=32 and a['parity'] for a in rows),rows
    placed='Generated structure \"alfheim:harbor_complex\"' in text or 'Placed structure alfheim:harbor_complex' in text
    result={'world':WORLD,'console':str(log.relative_to(ROOT)),'scope':'bounded approximate policy; no coastal fixture fills',
            'column_limit':32,'stop_budget_ms':150,'deadline_caveat':'checked between native calls; one in-flight call can overrun',
            'audits':rows,'natural_command_placement_reported':placed,'server_exit_code':0,'assembly_verified':False}
    if placed:
        subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/check_ancient_assembly.py'),str(ROOT/'server'/WORLD),'--family','harbor_complex'],check=True)
        result['assembly_verified']=True
    (ROOT/'tools/harbor_bounded_runtime.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('BOUNDED HARBOR CHECKS:',json.dumps(result))

if __name__=='__main__':main()
