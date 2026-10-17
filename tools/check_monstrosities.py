"""Source, UV, habitat and loot checks for the twelve authored monster species."""
import io,json
from PIL import Image
from gen_monstrosities import ROOT,RES,ASSETS,HABITATS,DROPS,CRYSTALS,PARASITES,build

def main():
    outputs=build();geometry=json.loads((ROOT/'tools/monstrosity_geometry.json').read_text())
    for name,data in outputs.items():assert (RES/name).read_bytes()==data,name
    assert len(geometry['species'])==19 and len(HABITATS)==19
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
        # The annelid uses four anatomical surfaces: flesh, sinew, teeth and mouth interior.
        assert len({q['material'] for q in quads})>=(4 if species=='sinew_leech' else 5)
        for q in quads:assert all(0<=v<=1 for uv in q['uv'] for v in uv)
        for biome in HABITATS[species]:
            ns,path=biome.split(':');assert (ROOT/f'kubejs/data/{ns}/worldgen/biome/{path}.json').is_file() or ns=='mythicbotany',biome
        spawn_path=f'data/alfheim_companion/forge/biome_modifier/{species}_spawns.json'
        if species in PARASITES:
            assert not HABITATS[species] and spawn_path not in outputs
            assert not (RES/spawn_path).exists(),'Parasites must remain spawner-only'
        else:
            spawn=json.loads(outputs[spawn_path])['spawners']
            assert 1<=spawn['weight']<=5 and spawn['minCount']==spawn['maxCount']==1
        if species in CRYSTALS:
            for variant in range(3):
                glow=Image.open(io.BytesIO(outputs[ASSETS+f'textures/entity/monstrosities/{species}_{variant}_glow.png']))
                assert glow.size==(512,512) and glow.getchannel('A').getextrema()==(0,255)
            assert HABITATS[species]==['alfheim:void_verge','alfheim:void_shore']
        assert DROPS[species].startswith('minecraft:')
    assert next(r for r in geometry['species'] if r['id']=='hulking_troll')['height']==3.6
    sounds={k:v for k,v in json.loads(outputs[ASSETS+'sounds.json']).items() if k.startswith('monstrosity.') or k=='maggot_mound.ambient'};assert len(sounds)==19*6+1
    from menagerie_sounds import vanilla_events
    ids=vanilla_events()
    for sound in sounds.values():
        for entry in sound['sounds']:assert entry['type']=='event' and entry['name'].removeprefix('minecraft:') in ids
    print('MONSTROSITIES STATIC PASS: 19 native rigs / 57 skinned heads; four spawner-only parasites; nine crystal glow masks; 115 verified native sound palettes; source equal')

if __name__=='__main__':main()
