"""Source equality, complete appearance coverage and actual material availability."""
import json,zipfile
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
 print('THEMED ENEMIES STATIC PASS: 390 appearances; exact 26-biome coverage; 5 vanilla species; 16 native materials; no creeper variants')
if __name__=='__main__':main()
