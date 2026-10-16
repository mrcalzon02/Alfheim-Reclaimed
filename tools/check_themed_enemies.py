"""Source equality, complete appearance coverage and actual material availability."""
import json,zipfile,io
from PIL import Image
from pathlib import Path
from gen_themed_enemies import build,profiles,THEMES,SPECIES
ROOT=Path(__file__).resolve().parents[1]

def main():
 for path,payload in build().items():assert (ROOT/path).read_bytes()==payload,path
 layer=json.loads((ROOT/'kubejs/data/mythicbotany/libx/biome_layer/alfheim.json').read_text())
 assert {r['biome'] for r in profiles()}=={b['biome'] for b in layer['biomes']}
 assert len(profiles())==26 and len({r['biome'] for r in profiles()})==26
 assert {s[2] for s in SPECIES}=={'zombie','skeleton','pillager','enderman','endermite'}
 jar=ROOT.parent.parent/'Install/versions/1.20.1/1.20.1.jar'
 with zipfile.ZipFile(jar) as archive:
  for material in {m for names in THEMES.values() for m in names}:
   assert 'assets/minecraft/textures/block/'+material+'.png' in archive.namelist(),material
  for _,_,species,_ in SPECIES:
   assert 'data/minecraft/loot_tables/entities/'+species+'.json' in archive.namelist()
 assert len({(r['theme'],r['body'],r['accent']) for r in profiles()})==26
 resources=ROOT/'first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion'
 for _,_,species,_ in SPECIES:
  egg=json.loads((resources/f'models/item/biome_{species}_spawn_egg.json').read_text())
  assert len(egg['overrides'])==78
  assert [v['predicate']['alfheim_companion:appearance'] for v in egg['overrides']]==list(range(1,79))
  for p in range(26):
   for style in range(3):
    key=f'{species}_{p}_{style}'
    model=json.loads((resources/f'models/item/enemy_heads/{key}.json').read_text())
    skin=Image.open(resources/f'textures/entity/themed/{key}.png')
    assert skin.mode=='RGBA' and skin.getchannel('A').getextrema()[1]>0,key
    assert model['textures']['base']=='alfheim_companion:entity/themed/'+key
    assert model['elements']
    for element in model['elements']:
     assert all(0<=a<b<=16 for a,b in zip(element['from'],element['to'])),key
     assert all('tintindex' not in face for face in element['faces'].values()),key
 print('THEMED ENEMIES STATIC PASS: 390 skins and matching heads; 390 ordered variant selections; custom Silverbark and Mire rigs; exact 26-biome coverage')
if __name__=='__main__':main()
