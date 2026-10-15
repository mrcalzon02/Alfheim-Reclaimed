"""Disposable runtime slice/roster proof. Spawn rules are checked, not player-driven natural density."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import nbt,run_server
from gen_themed_enemies import profiles,SPECIES
from probe_terraces import chunks
ROOT=Path(__file__).resolve().parents[1]
SEED=3536368297089363045

def review(world,full):
 matches=[(p,json.loads(p.read_text(encoding='utf-8'))) for p in (ROOT/'server').glob('manifest-*.json')]
 manifest=max((p,m) for p,m in matches if m.get('level_name')==world.name)[1]
 assert manifest['exit_code']==manifest['harness_exit_code']==0
 log=(ROOT/'server'/manifest['console']).read_text(encoding='utf-8',errors='replace')
 assert 'An unexpected error occurred' not in log and 'Unknown or incomplete command' not in log
 audits=[]
 for line in log.splitlines():
  if 'ALFHEIM_ENEMY_AUDIT ' in line:
   audits.append(json.loads(line.split('ALFHEIM_ENEMY_AUDIT ',1)[1]))
 assert len(audits)==2,audits
 for audit in audits:
  assert audit['coverage_gaps']==audit['unreplaced_vanilla_entries']==0
  assert len(audit['biomes'])==30
  assert all(r['natural_rule_acceptances']>0 for r in audit['rules_at_command_position']),audit['rules_at_command_position']
 factories=[json.loads(line.split('ALFHEIM_ENEMY_FACTORY ',1)[1]) for line in log.splitlines() if 'ALFHEIM_ENEMY_FACTORY ' in line]
 assert len(factories)==2,len(factories)
 for factory in factories:
  assert len(factory['mobs'])==5
  for mob in factory['mobs']:
   species=mob['type'].split('biome_')[-1]
   assert mob['biome']==mob['expected_biome'] and 0<=mob['style']<3,mob
   assert mob['loot']=='minecraft:entities/'+species,mob
   if species=='skeleton':assert mob['main_hand']=='minecraft:bow',mob
   if species=='pillager':assert mob['main_hand']=='minecraft:crossbow',mob
 saved=[];controls=[]
 for file in (world/'dimensions/mythicbotany/alfheim/entities').glob('*.mca'):
  if file.stat().st_size<8192:continue
  for c in chunks(file):
   for entity in c.get('Entities',[]):
    tags=entity.get('Tags',[])
    if 'alfheim_enemy_fixture' in tags:saved.append(entity)
    if 'alfheim_enemy_control' in tags:controls.append(entity)
 wanted=profiles() if full else [next(r for r in profiles() if r['biome']=='mythicbotany:golden_fields')]
 expected={(r['biome'],species,style) for r in wanted for _,_,species,_ in SPECIES for style in range(3)}
 actual={(e.get('AlfheimBiome'),str(e['id']).split('biome_')[-1],int(e.get('AlfheimStyle',-1))) for e in saved}
 assert len(saved)==len(expected) and actual==expected,(len(saved),len(expected),expected-actual)
 assert len(controls)==5,len(controls)
 mmo={}
 for _,_,species,_ in SPECIES:
  custom=next(e for e in saved if e['id']=='alfheim_companion:biome_'+species)
  vanilla=next(e for e in controls if e['id']=='minecraft:'+species)
  a=custom.get('ForgeCaps',{});b=vanilla.get('ForgeCaps',{})
  common=sorted(k for k in set(a)&set(b) if 'mmorpg' in k or 'exile' in k)
  required={k for k in b if 'mmorpg' in k or 'exile' in k}
  assert required<=set(common),(species,required,common)
  mmo[species]={'shared_combat_capabilities':common,'custom_capability_keys':sorted(a),'vanilla_capability_keys':sorted(b)}
  assert float(custom['Health'])>0
 source=ROOT/'first_party_mods/alfheim_companion/src/main/java/com/continuityworks/alfheimcompanion'
 paths=list((source/'enemy').glob('*.java'))+[source/'client/ThemedMaterialLayer.java',source/'client/ThemedEnemyRenderers.java']
 report={'world':world.name,'console':'server/'+manifest['console'],'server_exit':0,'fixture_appearances':len(saved),
  'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
  'shipping_jar_sha256':hashlib.sha256((ROOT/'mods/alfheim_companion-0.2.0.jar').read_bytes()).hexdigest(),
  'spawn_audits':audits,'natural_reason_factory_probes':factories,'combat_capability_comparison':mmo,
  'saved_appearances':[{'id':e['id'],'biome':e['AlfheimBiome'],'style':int(e['AlfheimStyle']),'health':float(e['Health'])} for e in saved],
  'limits':'Controlled NoAI fixtures, NATURAL-reason spawn factory, spawn tables and placement predicates. Factory probes are operator-triggered; no live-player natural-density observation, combat balance or client visual admission.'}
 (ROOT/('tools/themed_enemy_runtime_roster.json' if full else 'tools/themed_enemy_runtime_slice.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print('ENEMY RUNTIME PASS:',len(saved),'saved appearances; 30 biome tables; NATURAL rules in both dimensions; vanilla control capabilities compared')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--world',required=True);ap.add_argument('--full-roster',action='store_true');ap.add_argument('--review-only',action='store_true');args=ap.parse_args()
 assert args.world.startswith('validation-enemies-') and Path(args.world).name==args.world
 world=ROOT/'server'/args.world
 if args.review_only:review(world,args.full_roster);return
 assert not world.exists(),'Refusing to overwrite a validation world'
 wanted=profiles() if args.full_roster else [next(r for r in profiles() if r['biome']=='mythicbotany:golden_fields')]
 maxz=480+3*(len(wanted)-1)+6
 commands=[(5,'difficulty normal'),(1,'time set midnight'),(1,'gamerule doDaylightCycle false'),(1,'gamerule doMobSpawning false')]
 for dim in ('minecraft:overworld','mythicbotany:alfheim'):
  endx=527 if dim=='mythicbotany:alfheim' else 495;endz=maxz if dim=='mythicbotany:alfheim' else 495
  commands += [(1,f'execute in {dim} run forceload add 480 480 {endx} {endz}'),
   (2,f'execute in {dim} run fill 480 200 480 {endx} 200 {endz} minecraft:grass_block'),
   (1,f'execute in {dim} run fill 480 201 480 {endx} 205 {endz} minecraft:air'),
   (1,f'execute in {dim} run fill 480 206 480 {endx} 206 {endz} minecraft:stone')]
  if endz<495: # keep the audit point inside its loaded, dark test room
   commands += [(1,f'execute in {dim} run fill 480 200 488 495 200 495 minecraft:grass_block'),
    (1,f'execute in {dim} run fill 480 201 488 495 205 495 minecraft:air'),
    (1,f'execute in {dim} run fill 480 206 488 495 206 495 minecraft:stone')]
  commands.append((5,f'execute in {dim} positioned 488 201 492 run alfheim_enemies_audit'))
  commands.append((1,f'execute in {dim} positioned 481 201 492 run alfheim_enemies_audit probe'))
 for ri,r in enumerate(wanted):
  for si,(_,_,species,_) in enumerate(SPECIES):
   for style in range(3):
    tag={'Tags':['alfheim_enemy_fixture'],'PersistenceRequired':True,'NoAI':True,'Invulnerable':True,
         'AlfheimBiome':r['biome'],'AlfheimStyle':style}
    # SNBT booleans must be bytes; JSON true/false are accepted by the SNBT parser.
    commands.append((0,f'execute in mythicbotany:alfheim run summon alfheim_companion:biome_{species} {481+(si*3+style)*3} 201 {481+ri*3} '+json.dumps(tag,separators=(',',':'))))
 for si,(_,_,species,_) in enumerate(SPECIES):
  commands.append((0,f'execute in mythicbotany:alfheim run summon minecraft:{species} {481+si*3} 201 {maxz-1} '+
   '{Tags:["alfheim_enemy_control"],PersistenceRequired:1b,NoAI:1b,Invulnerable:1b}'))
 commands += [(8,'save-all flush'),(2,'execute in mythicbotany:alfheim run forceload remove all'),(1,'execute in minecraft:overworld run forceload remove all'),(2,'stop')]
 props=ROOT/'server/server.properties';original=props.read_bytes()
 try:code=run_server.run(str(SEED),world.name,8,commands,600)
 finally:
  props.write_bytes(original)
  (ROOT/'server/config/jade/server-plugin-overrides.json').write_bytes(subprocess.check_output(['git','show','HEAD:server/config/jade/server-plugin-overrides.json']))
 assert code==0,code
 review(world,args.full_roster)
if __name__=='__main__':main()
