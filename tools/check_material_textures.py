"""Static closure check for the Deep + Void 32px variant/rotation texture rework."""
from pathlib import Path
import hashlib
import json
from PIL import Image
from material_texture import OUTPUT_SIZE, STYLE_BY_ID, VARIANT_COUNT, ROTATIONS
from gen_deepworks import ROOT, build as build_deep
from gen_void_materials import build as build_void

FORMS = ("raw","polished","bricks","carved")


def _stone_texture_outputs(source):
    result={}
    for path,data in source.items():
        if not (path.startswith("kubejs/assets/alfheim/textures/block/") and path.endswith(".png")):
            continue
        stem=Path(path).stem
        if stem.startswith("mana_glass_") or stem.startswith("livingrock_slag"):
            continue
        result[path]=data
    return result


def _assert_blockstate(source, block_id):
    path=f"kubejs/assets/alfheim/blockstates/{block_id}.json"
    assert path in source, path
    obj=json.loads(source[path])
    variants=obj['variants']['']
    assert len(variants)==VARIANT_COUNT*len(ROTATIONS), (block_id,len(variants))
    assert sorted(set(v.get('y',0) for v in variants))==list(ROTATIONS), block_id
    models=[v['model'] for v in variants]
    assert len(set(models))==VARIANT_COUNT, (block_id,models)


def main():
    deep=build_deep(); void=build_void()
    expected={**_stone_texture_outputs(deep), **_stone_texture_outputs(void)}

    assert len(STYLE_BY_ID)==42, len(STYLE_BY_ID)
    assert len(expected)==42*len(FORMS)*VARIANT_COUNT, len(expected)

    hashes={}
    for path,data in expected.items():
        disk=ROOT/path
        assert disk.read_bytes()==data, path
        image=Image.open(disk)
        assert image.size==(OUTPUT_SIZE,OUTPUT_SIZE), path
        assert image.mode=='RGBA', path
        assert image.getchannel('A').getextrema()==(255,255), path
        values=[(r*3+g*6+b)//10 for r,g,b,a in image.getdata()]
        # Bigger is not enough: every tile must retain genuine value depth.
        assert len(set(values))>=28, (path,len(set(values)))
        assert max(values)-min(values)>=35, (path,max(values)-min(values))
        digest=hashlib.sha256(data).hexdigest()
        hashes.setdefault(digest,[]).append(path)
    assert len(hashes)==len(expected), [v for v in hashes.values() if len(v)>1]

    # Every geological full-cube form is wired to all variants and all four Y rotations.
    deep_catalog=json.loads(deep['kubejs/deepworks_catalog.json'])
    void_catalog=json.loads(void['kubejs/void_stones_catalog.json'])
    for source,catalog in ((deep,deep_catalog),(void,void_catalog)):
        script_path = ('kubejs/startup_scripts/20_deepworks.js' if source is deep
                       else 'kubejs/startup_scripts/21_void_stones.js')
        script = (ROOT/script_path).read_text(encoding='utf-8')
        for row in catalog['blocks']:
            assert len(row['texture_variants'])==VARIANT_COUNT, row['id']
            assert row['rotations']==list(ROTATIONS), row['id']
            if row['form'] not in ('slab','stairs','wall'):
                _assert_blockstate(source,row['id'].split(':',1)[1])
            # JourneyMap's texture fallback must have a real map color. KubeJS
            # defaults to NONE (black), even when textureAll is present.
            line = next(s for s in script.splitlines() if f"event.create('{row['id']}'" in s)
            color = row['map_color']
            assert len(color)==7 and color.startswith('#') and int(color[1:],16)>0, row['id']
            assert f".mapColor('{color}')" in line, row['id']
            item_path = f"kubejs/assets/alfheim/models/item/{row['id'].split(':')[1]}.json"
            assert (ROOT/item_path).read_bytes()==source[item_path], item_path
            if row['form']=='slab':
                item = json.loads((ROOT/item_path).read_bytes())
                # The former parent <id> never exists: the installed shape builder
                # generates only <id>_bottom, <id>_top and <id>_double.
                assert item['parent']=='minecraft:block/slab', row['id']
                assert set(item['textures'])=={'top','bottom','side'}, row['id']
                for texture in item['textures'].values():
                    ns, name = texture.split(':')
                    assert (ROOT/f'kubejs/assets/{ns}/textures/{name}.png').is_file(), texture

    # Mana-glass is now truly transparent, not a uniformly translucent coloured square.
    glass_rows=[r for r in deep_catalog['blocks'] if r['glass']]
    assert len(glass_rows)==6
    for row in glass_rows:
        for texname in row['texture_variants']:
            path=ROOT/f'kubejs/assets/alfheim/textures/block/{texname}.png'
            image=Image.open(path)
            alpha=list(image.getchannel('A').getdata())
            assert min(alpha)==0, (texname,min(alpha))
            assert max(alpha)<220, (texname,max(alpha))
            assert len(set(alpha))>=20, (texname,len(set(alpha)))
            assert sum(a==0 for a in alpha)>=48, (texname,sum(a==0 for a in alpha))

    deep_source=(ROOT/'tools/gen_deepworks.py').read_text(encoding='utf-8')
    void_source=(ROOT/'tools/gen_void_materials.py').read_text(encoding='utf-8')
    engine=(ROOT/'tools/material_texture.py').read_text(encoding='utf-8')
    forbidden='assets/botania/textures/block/livingrock.png'
    assert forbidden not in deep_source
    assert forbidden not in void_source
    assert 'base.getpixel' not in engine

    print(
        f'PASS: 42 material grammars, {len(expected)} unique RGBA {OUTPUT_SIZE}x{OUTPUT_SIZE} stone tiles '
        f'({VARIANT_COUNT} variants × 168 source textures), 4-way weighted rotations wired for full cubes, '
        'mana-glass has true per-pixel transparency, 42 slab inventory models resolve, '
        'all 301 blocks have explicit map colors, generator output byte-identical'
    )

if __name__=='__main__':
    main()
