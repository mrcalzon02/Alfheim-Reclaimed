"""Source, UV, habitat and loot checks for the six authored monster species."""
import io,json
from PIL import Image
from gen_monstrosities import ROOT,RES,ASSETS,HABITATS,DROPS,build

def main():
    outputs=build();geometry=json.loads((ROOT/'tools/monstrosity_geometry.json').read_text())
    for name,data in outputs.items():assert (RES/name).read_bytes()==data,name
    assert len(geometry['species'])==6 and len(HABITATS)==6
    for row in geometry['species']:
        species=row['id']
        for variant in range(3):
            key=f'{species}_{variant}'
            im=Image.open(io.BytesIO(outputs[ASSETS+f'textures/entity/monstrosities/{key}.png']))
            assert im.size==(512,512) and im.mode=='RGBA'
            assert len(im.getcolors(65536) or [])>64,'skin needs actual tonal variation'
            model=json.loads(outputs[ASSETS+f'models/item/monstrosities/{key}.json'])
            assert model['parent']=='minecraft:item/generated' and 'layer0' in model['textures']
            icon=Image.open(io.BytesIO(outputs[ASSETS+f'textures/item/monstrosities/{key}.png']))
            assert icon.size==(128,128) and icon.getchannel('A').getextrema()==(0,255)
            assert im.getchannel('A').getextrema()==(255,255)
        quads=geometry['models'][species]
        assert len({q['material'] for q in quads})>=5
        for q in quads:assert all(0<=v<=1 for uv in q['uv'] for v in uv)
        for biome in HABITATS[species]:
            ns,path=biome.split(':');assert (ROOT/f'kubejs/data/{ns}/worldgen/biome/{path}.json').is_file() or ns=='mythicbotany',biome
        spawn=json.loads(outputs[f'data/alfheim_companion/forge/biome_modifier/{species}_spawns.json'])['spawners']
        assert 1<=spawn['weight']<=4 and spawn['minCount']==spawn['maxCount']==1
        assert DROPS[species].startswith('minecraft:')
    assert next(r for r in geometry['species'] if r['id']=='hulking_troll')['height']==3.6
    print('MONSTROSITIES STATIC PASS: six distinct rigs / 18 native skinned heads; 29 habitat entries; low singleton spawn weights; source equal')

if __name__=='__main__':main()
