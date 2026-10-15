"""Guard the reproduced high-hill spawn and corridor lane regressions."""
import json
from pathlib import Path
import nbt
ROOT=Path(__file__).resolve().parents[1]

def main():
    place=(ROOT/'kubejs/data/alfheim/functions/hub/place.mcfunction').read_text()
    assert 'positioned 0 80 0' not in place
    assert 'positioned over motion_blocking_no_leaves if predicate' in place
    fallback=(ROOT/'kubejs/data/alfheim/functions/hub/fallback.mcfunction').read_text()
    assert 'positioned over motion_blocking_no_leaves' in fallback and 'hub/platform' in fallback
    assert 'fill -2 99' not in fallback
    assert 'positioned 0 0 0 positioned over' in fallback,'Emergency landing must stay inside the origin claim'
    limit=json.loads((ROOT/'kubejs/data/alfheim/predicates/hub/emergency_height.json').read_text())
    assert limit['predicate']['position']['y']=={'min':64,'max':315}
    buried=json.loads((ROOT/'kubejs/data/alfheim/predicates/hub/buried.json').read_text())
    assert [t['offsetY'] for t in buried['terms']]==[100,110,120]
    evidence=json.loads((ROOT/'tools/staven_field_audit.json').read_text())
    assert [p['block'] for p in evidence['burial_probe_blocks']]==['botania:livingrock']*3
    send=(ROOT/'kubejs/data/alfheim/functions/hub/send.mcfunction').read_text()
    assert 'hub/inspect_burial' in send and 'tag=!alfheim_hub_buried' in send
    s=nbt.load(str(ROOT/'kubejs/data/alfheim/structures/leyline/straight.nbt'))[1]
    states={tuple(map(int,b['pos'])):s['palette'][int(b['state'])]['Name'] for b in s['blocks']}
    walls=[p for p,n in states.items() if n=='alfheim:leyline_livingrock_wall']
    assert walls and all(x in (0,6) for x,y,z in walls),walls
    print('SPAWN/CORRIDOR STATIC PASS: no underground assembly fallback; bounded emergency headroom; recessed straight-run walls')

if __name__=='__main__':main()
