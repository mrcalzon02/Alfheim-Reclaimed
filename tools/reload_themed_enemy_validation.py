"""Reload the completed roster with the shipping jar; compare actual entity UUIDs."""
import argparse,json,subprocess
from run_themed_enemy_validation import ROOT,SEED,review
from probe_terraces import chunks
import run_server

def appearances(world):
 result={}
 for file in (world/'dimensions/mythicbotany/alfheim/entities').glob('*.mca'):
  if file.stat().st_size<8192:continue
  for c in chunks(file):
   for e in c.get('Entities',[]):
    if 'alfheim_enemy_fixture' in e.get('Tags',[]):
     result[tuple(map(int,e['UUID']))]=(e['id'],e['AlfheimBiome'],int(e['AlfheimStyle']))
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--world',required=True);args=ap.parse_args()
 assert args.world.startswith('validation-enemies-') and '/' not in args.world and '\\' not in args.world
 world=ROOT/'server'/args.world;before=appearances(world);assert len(before)==390
 report=ROOT/'tools/themed_enemy_runtime_roster.json'
 assert json.loads(report.read_text())['world']==args.world
 initial=ROOT/'tools/themed_enemy_runtime_roster_initial.json'
 assert not initial.exists();initial.write_bytes(report.read_bytes())
 commands=[(5,'say final enemy appearance persistence reload'),
  (1,'execute in mythicbotany:alfheim run forceload add 480 480 527 561'),
  (1,'execute in minecraft:overworld run forceload add 480 480 495 495')]
 for dim in ('minecraft:overworld','mythicbotany:alfheim'):
  commands.extend([(3,f'execute in {dim} positioned 488 201 492 run alfheim_enemies_audit'),
                   (1,f'execute in {dim} positioned 481 201 492 run alfheim_enemies_audit probe')])
 commands.extend([(5,'save-all flush'),(1,'execute in mythicbotany:alfheim run forceload remove all'),
                  (1,'execute in minecraft:overworld run forceload remove all'),(2,'stop')])
 props=ROOT/'server/server.properties';original=props.read_bytes()
 try:code=run_server.run(str(SEED),world.name,8,commands,500)
 finally:
  props.write_bytes(original)
  (ROOT/'server/config/jade/server-plugin-overrides.json').write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
 assert code==0,code
 assert appearances(world)==before,'An entity UUID, species, biome or style changed across restart'
 review(world,True)
 current=json.loads(report.read_text(encoding='utf-8'))
 current['persistence_reload']={'same_entity_uuids':390,'same_species_biome_style':True,
     'initial_report':'tools/themed_enemy_runtime_roster_initial.json'}
 report.write_text(json.dumps(current,indent=2)+'\n',encoding='utf-8')
 print('ENEMY RELOAD PASS: same 390 entity UUIDs and appearances')
if __name__=='__main__':main()
