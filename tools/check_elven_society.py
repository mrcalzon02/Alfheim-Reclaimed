"""Verify external elf identity references, transparent face protection, finery and source equality."""
import io,json,zipfile
from PIL import Image
from gen_elven_society import ROOT,ASSETS,build

def main():
    outputs=build()
    for name,data in outputs.items():assert (ROOT/name).read_bytes()==data,name
    manifest=json.loads(outputs['tools/elven_society_manifest.json'])
    assert len(manifest['roles'])==12 and manifest['total_appearances']==48
    with zipfile.ZipFile(ROOT/'mods/richs_races_wood_elves-1.0.0-forge-1.20.1.jar') as archive:
        for row in manifest['roles']:
            for texture in row['base_skins']:
                namespace,name=texture.split(':')
                assert f'assets/{namespace}/textures/{name}.png' in archive.namelist()
    clothes=[(name,data) for name,data in outputs.items() if name.endswith('.png') and '/wardrobe/' not in name]
    finery=[(name,data) for name,data in outputs.items() if name.endswith('.png') and '/wardrobe/' in name]
    assert len(clothes)==len(finery)==48
    for name,data in clothes:
        im=Image.open(io.BytesIO(data));assert im.size==(64,64) and im.mode=='RGBA'
        assert im.getchannel('A').getextrema()==(0,0),name+' covers original elf skin or clothing'
    for name,data in finery:
        im=Image.open(io.BytesIO(data));assert im.size==(128,128) and im.mode=='RGBA'
    egg=json.loads(outputs[ASSETS+'models/item/elven_citizen_spawn_egg.json'])
    assert [r['predicate']['alfheim_companion:social_appearance'] for r in egg['overrides']]==list(range(1,49))
    for override in egg['overrides']:
        model=json.loads(outputs[ASSETS+'models/'+override['model'].split(':')[1]+'.json'])
        assert model['textures']['base'].startswith('richs_races_wood_elves:entities/woodelf_')
        for e in model['elements']:
            assert len(e['faces'])==6
            assert all(0<=a<b<=16 for a,b in zip(e['from'],e['to']))
            assert all('tintindex' not in f for f in e['faces'].values())
            assert all(0<=n<=16 for f in e['faces'].values() for n in f['uv'])
    print('ELVEN SOCIETY STATIC PASS: 12 roles / 48 appearances; original elf faces/hair protected; modeled wardrobe and matching heads; source equal')
if __name__=='__main__':main()
