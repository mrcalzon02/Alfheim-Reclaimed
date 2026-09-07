"""Validate the renderer-neutral 47-state connected palette."""
import hashlib
import json
from pathlib import Path
from PIL import Image
from gen_connected_palette import (
    CONTINUITY_ROOT, ROOT, SOURCE_TO_CONTINUITY, build, states47,
)
from material_texture import OUTPUT_SIZE


def main():
    out=build(); states=states47(); assert len(states)==47
    catalog=json.loads(out['tools/connected_palette_catalog.json'])
    assert catalog['schema']==2
    assert len(catalog['families'])==42
    assert len(catalog['states'])==47
    tiles=[]
    for family in catalog['families']:
        assert len(family['tiles'])==47,family['id']
        source_data=[]
        for rel in family['tiles']:
            assert rel in out,rel
            assert (ROOT/rel).read_bytes()==out[rel],rel
            im=Image.open(ROOT/rel)
            assert im.size==(OUTPUT_SIZE,OUTPUT_SIZE) and im.mode=='RGBA',rel
            assert im.getchannel('A').getextrema()==(255,255),rel
            source_data.append(out[rel])
            tiles.append(hashlib.sha256(out[rel]).hexdigest())
        continuity=family['continuity']
        assert len(continuity['tiles'])==47,family['id']
        assert continuity['rule'].startswith(CONTINUITY_ROOT+'/'),continuity['rule']
        rule=(ROOT/continuity['rule']).read_text()
        stem=family['id'].split(':',1)[1]
        assert rule==(
            'method=ctm\n'
            f'matchBlocks={family["id"]}\n'
            'tiles=0-46\n'
            'connect=block\n'
            f'resourceCondition=textures/block/{stem}.png\n'
        ),family['id']
        for source_index,continuity_index in enumerate(SOURCE_TO_CONTINUITY):
            rel=continuity['tiles'][continuity_index]
            assert rel in out,rel
            assert (ROOT/rel).read_bytes()==out[rel],rel
            assert out[rel]==source_data[source_index],(family['id'],source_index,continuity_index)
    assert len(tiles)==42*47
    # Across the full library, palette generation must produce substantial variation.
    assert len(set(tiles))>len(tiles)*.97,(len(set(tiles)),len(tiles))
    print(
        f'PASS: 42 families × 47 connected states = {len(tiles)} native '
        f'{OUTPUT_SIZE}x{OUTPUT_SIZE} CTM source tiles; Continuity rules and remapped runtime tiles '
        'present; generator output byte-identical'
    )

if __name__=='__main__': main()
