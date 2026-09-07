"""Validate Deep library closure, stable output, variants, rotations and transparency contracts."""
import json
import re
from PIL import Image
from gen_deepworks import ROOT, build
from material_texture import OUTPUT_SIZE, VARIANT_COUNT, ROTATIONS


def main():
    expected=build()
    for name,content in expected.items():
        assert (ROOT/name).read_bytes()==content, name
        if name.endswith('.json'):
            json.loads(content)
    manifest=json.loads((ROOT/'tools/deepworks_manifest.json').read_text())
    catalog=json.loads((ROOT/'kubejs/deepworks_catalog.json').read_text())
    ids=[b['id'] for b in catalog['blocks']]
    assert len(ids)==len(set(ids))==175
    assert len(manifest['families'])==24
    assert sum(f['group']!='Furnace' for f in manifest['families'])==19
    declarations=[]
    for script in (ROOT/'kubejs/startup_scripts').glob('*.js'):
        declarations+=re.findall(r"event\.create\(['\"](alfheim:[a-z0-9_]+)['\"]",script.read_text(encoding='utf-8'))
    for row in catalog['blocks']:
        assert declarations.count(row['id'])==1,row['id']
        assert len(row['texture_variants'])==VARIANT_COUNT,row['id']
        assert row['rotations']==list(ROTATIONS),row['id']
        for texname in row['texture_variants']:
            tex=ROOT/f'kubejs/assets/alfheim/textures/block/{texname}.png'
            im=Image.open(tex)
            assert im.size==(OUTPUT_SIZE,OUTPUT_SIZE) and im.mode=='RGBA',tex
            alpha=list(im.getchannel('A').getdata())
            if row['glass']:
                assert min(alpha)==0 and max(alpha)<220 and len(set(alpha))>=20,tex
            else:
                assert min(alpha)==max(alpha)==255,tex
        id=row['id'].split(':')[1]
        model=json.loads((ROOT/f'kubejs/assets/alfheim/models/item/{id}.json').read_text())
        if row['form']=='wall':
            assert model['parent']=='minecraft:block/wall_inventory'
        else:
            assert model['parent']=='alfheim:block/'+id
        if row['form'] not in ('slab','stairs','wall'):
            state=json.loads((ROOT/f'kubejs/assets/alfheim/blockstates/{id}.json').read_text())['variants']['']
            assert len(state)==VARIANT_COUNT*len(ROTATIONS),id
            assert sorted(set(v.get('y',0) for v in state))==list(ROTATIONS),id
            assert len(set(v['model'] for v in state))==VARIANT_COUNT,id
    for recipe in catalog['recipes']:
        assert recipe['output'] in ids
        assert recipe['input'] in ids+['botania:livingrock','minecraft:glass']
        assert recipe['count']==(2 if recipe['output'].endswith('_slab') else 1)
    assert len(catalog['recipes'])==174
    assert not any('/worldgen/' in name or '/data/minecraft/tags/' in name for name in expected)
    print(
        f'PASS: 24 families, 175 blocks, 174 recipes, {len(expected)} byte-identical generated files; '
        f'{OUTPUT_SIZE}x{OUTPUT_SIZE}, {VARIANT_COUNT} variants, rotations {ROTATIONS}; transparent mana-glass; '
        'no terrain or broad vanilla tag output'
    )

if __name__=='__main__':
    main()
