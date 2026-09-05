"""Extend installed natural zombie spawns to all 16 Alfheim and 146 Midgard biomes.

Read-only jar inspection. Original modifiers remain authoritative for weights and group sizes.
Infectious already uses forge:any for most entries, but hardcodes Overworld in Java.
The generated placement additions retain mutation thresholds and enable switches.
"""
import glob
import json
import re
import subprocess
import zipfile
from pathlib import Path
from gen_fey_wildlife import write

ROOT = Path('kubejs/data')
JAVAP = 'C:/Program Files/Java/jdk-26.0.1/bin/javap.exe'


def main():
    biomes = {}
    for pattern, namespace in [('*MythicBotany*','mythicbotany'),('*ContinuityWorks*','continuityworks_biomes')]:
        with zipfile.ZipFile(glob.glob('mods/'+pattern)[0]) as z:
            prefix=f'data/{namespace}/worldgen/biome/'
            for n in z.namelist():
                if n.startswith(prefix) and n.endswith('.json'):
                    biomes[namespace+':'+Path(n).stem]=json.loads(z.read(n))
    for p in (ROOT/'alfheim/worldgen/biome').glob('*.json'):
        biomes['alfheim:'+p.stem]=json.loads(p.read_text())
    write(ROOT/'alfheim/tags/worldgen/biome/populated_biomes.json',
          {'replace':False,'values':sorted(biomes)})
    registry=json.loads(Path('server/local/kubejs/export/registries/entity_type.json').read_text())
    audit=[]
    extended=[]
    infectious=[]
    for pattern in ['*EggsZombies*','*Infectious*']:
        jar=glob.glob('mods/'+pattern)[0]
        with zipfile.ZipFile(jar) as z:
            for n in z.namelist():
                if '/forge/biome_modifier/' not in n or not n.endswith('.json'):
                    continue
                d=json.loads(z.read(n))
                if d.get('type')!='forge:add_spawns':
                    continue
                spawns=d['spawners'] if isinstance(d['spawners'],list) else [d['spawners']]
                # These are invisible controllers/rewards, not wildlife. Do not widen them.
                if any(s['type'] in ['infectious:lootdrop','infectious:mutation_trigger'] for s in spawns):
                    continue
                assert all(s['type'] in registry for s in spawns), n
                selector=d['biomes']
                already_all=selector=={'type':'forge:any'}
                if not already_all:
                    original=selector if isinstance(selector,list) else [selector]
                    assert all(isinstance(v,str) for v in original), n
                    tag='zombie_habitats/'+n.split('/')[1]+'_'+Path(n).stem
                    write(ROOT/f'alfheim/tags/worldgen/biome/{tag}.json',
                          {'replace':False,'values':original+['#alfheim:populated_biomes']})
                    d['biomes']='#alfheim:'+tag
                    write(Path('kubejs')/n,d)
                    extended.append(n)
                for s in spawns:
                    audit.append(dict(s,source=jar,modifier=n,original_selector=selector))
                    if s['type'].startswith('infectious:'):
                        infectious.append(s['type'])
    # The variant mod converts vanilla zombies instead of supplying biome modifiers.
    # A small direct weight gives every registered variant access to the custom biomes.
    variants=sorted(k for k in registry if k.startswith('zombie_variants:'))
    write(ROOT/'alfheim/forge/biome_modifier/zombie_variants.json',
          {'type':'forge:add_spawns','biomes':'#alfheim:populated_biomes',
           'spawners':[{'type':k,'weight':1,'minCount':1,'maxCount':2} for k in variants]})
    for vanilla in ['minecraft:zombie','minecraft:husk','minecraft:drowned','minecraft:zombie_villager']:
        missing=[b for b,d in biomes.items() if not any(s['type']==vanilla
                 for s in d.get('spawners',{}).get('monster',[]))]
        write(ROOT/f'alfheim/forge/biome_modifier/{vanilla.split(":")[1]}_coverage.json',
              {'type':'forge:add_spawns','biomes':missing,'spawners':{'type':vanilla,
               'weight':12 if vanilla=='minecraft:zombie' else 2,'minCount':1,'maxCount':3}})
    # Inspect all natural-condition classes once, then derive per-entity gates from references.
    jar=glob.glob('mods/*Infectious*')[0]
    with zipfile.ZipFile(jar) as z:
        procedures=[n[:-6].replace('/','.') for n in z.namelist()
                    if n.endswith('NaturalEntitySpawningConditionProcedure.class')]
        result=subprocess.run([JAVAP,'-p','-c','-classpath',jar]+procedures,
                              text=True,capture_output=True)
        chunks=re.split('Compiled from ',result.stdout)[1:]
        rules={}
        for c in chunks:
            cls=c.splitlines()[0].strip('"').removesuffix('.java')
            if cls.startswith(('MutationTrigger','Lootdrop')):
                continue
            gate=re.search(r'InfectiousModGameRules.ZOMBIE_MUTATION_LEVEL:.*?iconst_(\d).*?if_icmplt',c,re.S)
            zero_gate=re.search(r'InfectiousModGameRules.ZOMBIE_MUTATION_LEVEL:.*?\)I\s+\d+: iflt',c,re.S)
            if 'ZOMBIE_MUTATION_LEVEL' in c and not gate and not zero_gate:
                raise ValueError('Unrecognized mutation gate: '+cls)
            rules[cls]={'mutation':int(gate.group(1)) if gate else 0,
                        'switches':sorted(set(re.findall(r'InfectiousModGameRules.(ENABLE_[A-Z_]+)',c)))}
        entity_classes={Path(n).stem.removesuffix('Entity').lower():n for n in z.namelist()
                        if '/entity/' in n and n.endswith('Entity.class')}
        gates=[]
        for ident in sorted(set(infectious)):
            norm=ident.split(':')[1].replace('_','')
            cls=entity_classes.get(norm)
            if not cls:
                # These natural entries spawn entities whose implementation name differs.
                aliases={'screamer':'zombiescreamer','towerzombie1':'towerzombiebase'}
                cls=entity_classes.get(aliases.get(norm,''))
            if not cls:
                raise ValueError('Unmapped natural entity: '+ident)
            references=re.findall(rb'net/mcreator/infectious/procedures/([A-Za-z0-9]+NaturalEntitySpawningConditionProcedure)',z.read(cls))
            ref=sorted(set(x.decode() for x in references))
            if len(ref)>1:
                raise ValueError('Ambiguous condition: '+ident)
            rule=rules[ref[0]] if ref else {'mutation':0,'switches':[]}
            gates.append(dict(id=ident,procedure=ref[0] if ref else None,**rule))
    write(Path('kubejs/zombie_spawn_gates.json'),gates)
    write(Path('tools/zombie_habitat_manifest.json'),dict(biomes=sorted(biomes),
        natural=audit,variants=variants,extended_modifiers=extended,placement_gates=gates,
        excluded=['infectious:lootdrop','infectious:mutation_trigger']))
    print(f'{len(biomes)} biomes; {len(audit)} natural zombie entries; {len(variants)} variants; '
          f'{len(extended)} habitat extensions; {len(gates)} Infectious placement adaptations')


if __name__=='__main__':
    main()
