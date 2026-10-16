"""Independent checks for route preservation, an eightfold detail target and anomaly isolation."""
import json
from pathlib import Path

import nbt
import structure_detail as sd
from cw_district_refit import ROOT,compare,cells
from gen_ley_fracture import build


def orphan_cells(root):
    grid=cells(root)
    return {pos for pos,(state,be) in grid.items() if state['Name'] not in sd.AIR_NAMES
            and all(grid.get(tuple(pos[i]+step[i] for i in range(3)),({},None))[0].get('Name') in sd.AIR_NAMES
                    for step in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)))}


def main():
    if (ROOT/'tools/district_furnishing_placement_report.json').exists():
        from check_furnished_districts import main as check_furnishings
        check_furnishings()
    report=json.loads((ROOT/'tools/continuity_district_refit_report.json').read_text())
    changed=relief=pieces=0
    for family in report['families']:
        totals=family['totals']
        assert totals['detail_ratio']>=8, (family['family'],'eightfold detail floor',totals)
        for metric in family['metrics']:
            relative=Path('kubejs/data/alfheim/structures/ancient')/family['family']/(metric['piece']+'.nbt')
            before=nbt.load(ROOT/'build/continuity-district-refit/baseline'/relative)[1]
            after=nbt.load(ROOT/relative)[1]
            # Furnishing placement has its own exact-cell/loot/connectivity audit;
            # retain this older eightfold architectural metric on its original air cells.
            from district_furnishing_placement import without_furnishings
            after=without_furnishings(after)
            actual=compare(before,after)
            assert not orphan_cells(after)-orphan_cells(before),('new orphan geometry',relative)
            assert all(actual[k]==metric[k] for k in actual),relative
            changed+=actual['changed_cells'];relief+=actual['relief_cells'];pieces+=1
    for family in ('deep_quarry','elder_kings_tomb','faultwork'):
        for path in (ROOT/'kubejs/data/alfheim/structures/deepworks_archaeology'/family).glob('*.nbt'):
            root=nbt.load(path)[1]
            names={root['palette'][int(b['state'])]['Name'] for b in root['blocks']}
            assert not {'minecraft:crying_obsidian','alfheim:magmatic_livingrock'} & names,path
    core=ROOT/'kubejs/data/alfheim/structures/ley_fracture/core.nbt'
    root=nbt.load(core)[1]
    assert root==build().to_nbt(),'Anomaly source/shipping mismatch'
    assert not orphan_cells(root),'Unattached standalone anomaly blocks'
    assert max(root['size'])<=48
    names={e['Name'] for e in root['palette']}
    assert {'minecraft:crying_obsidian','alfheim:magmatic_livingrock'}<=names
    # No automatic placements may bypass the independent structure reservation gate.
    for path in (ROOT/'kubejs/data/alfheim/worldgen/structure_set').glob('*.json'):
        assert 'alfheim:ley_fracture' not in path.read_text(),path
    print(f'DISTRICT REFIT PASS: {pieces} templates; {changed} changed cells, {relief} supported relief cells; '
          '12 eightfold family floors; protected routes/fixtures; isolated purple anomaly, natural placement blocked')


if __name__=='__main__':main()
