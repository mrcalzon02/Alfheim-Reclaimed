"""Source equality for the committed Void remnant plants and model assets."""
import json
from pathlib import Path
import gen_void_vegetation as gen

ROOT=Path(__file__).resolve().parents[1]

def main():
    target=ROOT/'build/void-remnant-equality'
    original=(gen.ROOT,gen.DATA,gen.ASSETS)
    try:
        gen.ROOT=target;gen.DATA=target/'kubejs/data/alfheim';gen.ASSETS=target/'kubejs/assets/alfheim/models/block'
        (target/'kubejs/startup_scripts').mkdir(parents=True,exist_ok=True)
        gen.main()
    finally:gen.ROOT,gen.DATA,gen.ASSETS=original
    files=list((target/'kubejs').rglob('*'))
    checked=0
    for twin in files:
        if not twin.is_file():continue
        actual=ROOT/twin.relative_to(target)
        if twin.suffix=='.json':
            assert json.loads(actual.read_text(encoding='utf-8'))==json.loads(twin.read_text(encoding='utf-8')),actual
        else:assert actual.read_text(encoding='utf-8')==twin.read_text(encoding='utf-8'),actual
        checked+=1
    assert checked==16,checked
    assert len(gen.SPECS)==4 and len(gen.SHAPES)==3
    for spec in gen.SPECS:
        assert spec['support'] and 0<spec['tries']<=14 and spec['chance']>=3,spec['name']
    print('VOID REMNANT SOURCE PASS: 16 matching files; four substrate-gated features and three models')

if __name__=='__main__':main()
