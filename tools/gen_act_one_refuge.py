"""Act I shops, stock and dungeon interiors through the local Continuity Works provider."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

import nbt
from structure_nbt import Piece
from gen_labyrinth_asset_kit import B, box, generate_piece, ROOMS, SEED

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'first_party_mods/alfheim_companion/src/main/resources'
REPORT=ROOT/'alfheim_reclaimed_design/monastery_labyrinth/act_one_refuge'
SERVICES=['arms','provisions','apothecary','repair','supplies','salvage']
NAMES=['Cloister Arms Dealer','Cloister Provisioner','Cloister Apothecary','Cloister Repairer','Cloister Combat Supplier','Cloister Salvage Broker']


def stock():
    rows={s:[] for s in SERVICES}
    def sell(service,item,price=1,gems=1,count=1,uses=8,**extra):
        rows[service].append(dict(cost_a='botania:manasteel_ingot',count_a=price,
            cost_b='ars_nouveau:source_gem',count_b=gems,result=item,count=count,max_uses=uses,**extra))
    for i,kind in enumerate(['sword','bow','staff','plate_chest','leather_chest','cloth_chest','shield']):
        sell('arms','minecraft:iron_sword',4,4,uses=2,gear_type=kind,gear_level=1,gear_rarity='common')
    for kind in ('health','resource'):
        for tier,price in enumerate((1,3,6)):
            sell('apothecary',f'mmorpg:potion/{kind}/{tier}',price,price,count=4,uses=8 if tier==0 else 4,tier=0)
    for potion,price in [('regeneration',2),('swiftness',1),('fire_resistance',3),('night_vision',1),('water_breathing',2)]:
        sell('apothecary','minecraft:potion',price,price,potion='minecraft:'+potion,uses=4)
    for kind in ('str','dex','int','might','arcane','crit'):
        sell('supplies','mmorpg:buff_potion/common_'+kind,2,2,count=2,uses=4,tier=0)
    sell('supplies','mmorpg:currency/sharpening_stone_0',2,2,uses=4)
    sell('supplies','mmorpg:enchantment/family/weapon/common',4,4,uses=2)
    sell('supplies','mmorpg:enchantment/family/armor/common',4,4,uses=2)
    for item,count in [('minecraft:cooked_beef',8),('minecraft:bread',16),('minecraft:arrow',32),('minecraft:torch',32),('minecraft:milk_bucket',1)]:
        sell('provisions',item,1,1,count=count)
    for kind in ('life','mana','energy'):
        sell('provisions','mmorpg:food/common_'+kind,2,2,count=2,tier=0)
    sell('repair','minecraft:anvil',8,8,uses=1)
    sell('repair','minecraft:grindstone',2,2,uses=2)
    sell('repair','minecraft:experience_bottle',1,2,count=4,uses=4)
    sell('repair','mmorpg:currency/sharpening_stone_0',2,2,uses=4)
    for material in ('mining','farming','meat','fishing'):
        rows['salvage'].append(dict(cost_a=f'mmorpg:material/{material}/0',count_a=16,
            cost_b='ars_nouveau:source_gem',count_b=1,result='mmorpg:potion/health/0',count=2,max_uses=4,tier=0))
    return {'version':1,'restock_ticks':24000,'act':1,'services':rows,
            'repair':{'durability_per_payment':100,'cost_a':'botania:manasteel_ingot','cost_b':'ars_nouveau:source_gem'},
            'equipment_policy':'Common level-one native MMO gear, rolled once and saved. No late material unlocks or unique items.',
            'potion_policy':'Three native potion rarities, all explicit profession tier zero; native level/use checks remain in force.'}


def shop(index):
    p=Piece(13,14,19);south=index%2==0
    box(p,(0,0,0),(12,13,18),B('air'))
    box(p,(0,0,0),(12,3,18),B('stone_bricks'))
    box(p,(0,4,0),(12,4,18),B('spruce_planks'))
    for x in (0,12):box(p,(x,5,0),(x,12,18),B('mossy_stone_bricks'))
    for z in (0,18):box(p,(0,5,z),(12,12,z),B('mossy_stone_bricks'))
    box(p,(0,13,0),(12,13,18),B('stone_brick_slab',type='bottom',waterlogged=False))
    doorz=18 if south else 0
    box(p,(5,5,doorz),(7,8,doorz),B('air'))
    for x in (0,12):
        for z in (5,12):box(p,(x,7,z),(x,9,z+1),B('glass_pane',north=True,south=True,east=False,west=False,waterlogged=False))
    # The three-wide aisle reaches the counter from either row's street-facing door.
    counterz=11 if south else 7
    box(p,(3,5,counterz),(9,6,counterz),B('spruce_planks'))
    for x in (2,10):
        for z in (3,15):
            box(p,(x,5,z),(x,7,z),B('spruce_planks'))
            p.set(x,8,z,B('lantern',hanging=False,waterlogged=False))
    station=['smithing_table','smoker','brewing_stand','anvil','fletching_table','grindstone'][index]
    props={'facing':'south'} if station=='smoker' else {'facing':'north'} if station in ('anvil','grindstone') else {}
    if station=='smoker':props['lit']=False
    if station=='grindstone':props['face']='floor'
    p.set(3,5,9,B(station,**props))
    for z in (5,13):
        p.set(9,5,z,B('barrel',facing='up',open=False))
        p.set(9,6,z,B('flower_pot'))
    return p, [6.5,5.,9.5]


class RefugeProvider:
    provider_id='alfheim_act_one_refuge_v1'
    aliases=('act_one_refuge',)
    def describe(self):return {'provider_id':self.provider_id,'aliases':list(self.aliases),'operation':'six fitted service shops and authored dungeon interiors'}
    def generate(self,request,registry_resolver):
        rows=[];artifacts={};probes={}
        catalogue=stock()
        for offers in catalogue['services'].values():
            for offer in offers:
                for key in ('cost_a','cost_b','result'):
                    rid=offer[key];probe=registry_resolver.probe(rid,kind='item')
                    assert probe['level'] in ('exact','vanilla'),probe
        def emit(rel,p,entity=None):
            root=p.to_nbt();assert not p.dropped and max(p.size)<=48
            if entity is not None:root['entities']=[entity]
            for state in root['palette']:
                rid=state['Name'];probes[rid]=registry_resolver.probe(rid,kind='block')
                assert probes[rid]['level'] in ('exact','vanilla'),probes[rid]
            path=RES/rel;path.parent.mkdir(parents=True,exist_ok=True);nbt.save(path,'',root)
            payload=gzip.compress(gzip.decompress(path.read_bytes()),mtime=0);path.write_bytes(payload)
            artifacts[rel.replace('/','_')]=payload
            rows.append({'path':str(path.relative_to(ROOT)).replace('\\','/'),'size':list(p.size),'sha256':hashlib.sha256(payload).hexdigest()})
        for i,service in enumerate(SERVICES):
            p,pos=shop(i)
            # Vanilla template placement clips entities to the current generation chunk.
            tag={'id':'alfheim_companion:elven_citizen','ElfRole':'artisan','ElfAppearance':i%4,
                 'RefugeService':service,'PersistenceRequired':1,'CustomName':json.dumps({'text':NAMES[i]})}
            emit(f'data/alfheim/structures/ashen_refuge/{service}.nbt',p,
                 {'pos':pos,'blockPos':[6,5,9],'nbt':tag})
        for family in ROOMS:
            if family=='switchback_stair':continue
            p,_,_=generate_piece(family,'weathered')
            emit(f'data/alfheim/structures/ashen_cloister/{family}.nbt',p)
        rel='data/alfheim_companion/act_one_refuge_trades.json'
        payload=(json.dumps(catalogue,indent=2)+'\n').encode();(RES/rel).write_bytes(payload);artifacts['stock']=payload
        return {'provider_id':self.provider_id,'status':'LOCALLY_VALIDATED',
                'generated_layout':{'pieces':rows,'shops':6,'offers':sum(map(len,catalogue['services'].values())),
                                    'registry_probes':probes,'natural_placement':'not registered'},
                'structure_artifact':{'format':'minecraft_structure_nbt','piece_count':len(rows)},'artifact_bytes':artifacts}


def main():
    cw=Path('C:/GITS/Structuresmith/StructureSmith');sys.path.insert(0,str(cw/'src'))
    from structure_capability import StructureCapability
    cap=StructureCapability(project_root=ROOT,state_root=ROOT/'build/act-one-refuge/snapshots')
    assert cap.capabilities()['service']=='Continuity Works'
    for kind in ('block','item'):
        cap.inventory.add_registry_ids(json.loads((ROOT/f'server/local/kubejs/export/registries/{kind}.json').read_text()),kind=kind)
    cap.register_generator(RefugeProvider())
    req={'structure_id':'alfheim:act_one_refuge','target_version':'1.20.1','operation':'generate','grade':4,
         'purpose':{'kind':'elven_combat_service_refuge','required_zones':SERVICES,
                    'required_routes':['three-wide shop approaches','clear service counter access','shared monastery entrance']},
         'theme':{'name':'Ashen Cloister refuge','culture':'Alfheim elven','palette_roles':{'masonry':['minecraft:mossy_stone_bricks']}},
         'context':{'dimension':'mythicbotany:alfheim','terrain':'existing 13 by 19 shop plots, same family reservation'},
         'preserve':['existing site allocator','six native shop footprints','five-wide dungeon doorways'],
         'integration_contracts':{'independent_structure_gap':500,'same_family':'monastery plus refuge plus labyrinth','deployment':'native adapter; runtime validation required'},
         'generation':{'kind':'act_one_refuge','seed':SEED,'materialize_nbt':True}}
    plan=cap.plan(req);assert plan['audit']['status']!='FAIL'
    result=cap.generate(req);assert result['generation']['status']=='LOCALLY_VALIDATED'
    REPORT.mkdir(parents=True,exist_ok=True)
    report={'seed':SEED,'target':'Minecraft 1.20.1 / Forge 47.4.10','execution':'Continuity Works StructureCapability.plan / generate',
            'cw_source_sha256':hashlib.sha256((cw/'src/structure_capability/api.py').read_bytes()).hexdigest(),
            'snapshot':result['snapshot'],**result['generated_layout']}
    (REPORT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f"Continuity Works emitted {len(report['pieces'])} templates, six service profiles and {report['offers']} offers.")


if __name__=='__main__':main()
