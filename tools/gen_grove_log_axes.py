"""Axis registration and models for existing grove logs; no new block IDs."""
import argparse,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOGS=('emberbark','gloambark','hushbark')

def builder(tree):
    return (".property(BlockProperties.AXIS)"
            ".defaultState(e => e.set(BlockProperties.AXIS, 'y'))"
            ".placementState(e => e.set(BlockProperties.AXIS, e.getClickedFace().getAxis().name().toLowerCase()))"
            f".model('alfheim:block/{tree}_log_axis')")

def assets(tree):
    return {
        f'kubejs/assets/alfheim/models/block/{tree}_log_axis.json':{
            'parent':'minecraft:block/cube_column','textures':{
                'end':f'alfheim:block/{tree}_log_top','side':f'alfheim:block/{tree}_log'}},
        f'kubejs/assets/alfheim/blockstates/{tree}_log.json':{'variants':{
            'axis=x':{'model':f'alfheim:block/{tree}_log_axis','x':90,'y':90},
            'axis=y':{'model':f'alfheim:block/{tree}_log_axis'},
            'axis=z':{'model':f'alfheim:block/{tree}_log_axis','x':90}}},
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    startup=ROOT/'kubejs/startup_scripts/12_groves.js';text=startup.read_text(encoding='utf-8')
    for tree in LOGS:
        old=f".texture('down', 'alfheim:block/{tree}_log_top')"
        new=old+builder(tree)
        assert text.count(old)==1,tree
        if args.check:assert new in text,tree
        elif new not in text:text=text.replace(old,new)
        for relative,doc in assets(tree).items():
            content=(json.dumps(doc,indent=2)+'\n').encode();path=ROOT/relative
            if args.check:assert path.read_bytes()==content,relative
            else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
    if not args.check:startup.write_text(text,encoding='utf-8')
    print('GROVE AXES:', 'registration and six assets match' if args.check else 'registration and six assets generated')

if __name__=='__main__':main()
