"""Validate library closure, stable output, recipes and shaped-model contracts."""
import json
import re
from pathlib import Path
from PIL import Image
from gen_deepworks import ROOT, build


def main():
    expected = build()
    for name, content in expected.items():
        assert (ROOT/name).read_bytes() == content, name
        if name.endswith('.json'): json.loads(content)
    manifest = json.loads((ROOT/'tools/deepworks_manifest.json').read_text())
    catalog = json.loads((ROOT/'kubejs/deepworks_catalog.json').read_text())
    ids = [b['id'] for b in catalog['blocks']]
    assert len(ids) == len(set(ids)) == 175
    assert len(manifest['families']) == 24
    assert sum(f['group'] != 'Furnace' for f in manifest['families']) == 19
    declarations = []
    for script in (ROOT/'kubejs/startup_scripts').glob('*.js'):
        declarations += re.findall(r"event\.create\(['\"](alfheim:[a-z0-9_]+)['\"]", script.read_text(encoding='utf-8'))
    for row in catalog['blocks']:
        assert declarations.count(row['id']) == 1, row['id']
        tex = ROOT/f"kubejs/assets/alfheim/textures/block/{row['texture']}.png"
        im = Image.open(tex)
        assert im.size == (16,16) and im.mode == 'RGBA', tex
        alpha = im.getchannel('A').getextrema()
        assert alpha[0] < alpha[1] < 255 if row['glass'] else alpha == (255,255)
        id = row['id'].split(':')[1]
        model = json.loads((ROOT/f'kubejs/assets/alfheim/models/item/{id}.json').read_text())
        if row['form'] == 'wall': assert model['parent'] == 'minecraft:block/wall_inventory'
        else: assert model['parent'] == 'alfheim:block/'+id
    for recipe in catalog['recipes']:
        assert recipe['output'] in ids
        assert recipe['input'] in ids+['botania:livingrock','minecraft:glass']
        assert recipe['count'] == (2 if recipe['output'].endswith('_slab') else 1)
    assert len(catalog['recipes']) == 174
    assert not any('/worldgen/' in name or '/data/minecraft/tags/' in name for name in expected)
    print(f'PASS: 24 families, 175 blocks, 174 recipes, {len(expected)} byte-identical generated files; no terrain or broad vanilla tag output')


if __name__ == '__main__': main()
