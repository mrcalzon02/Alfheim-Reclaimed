"""Twelve upper-rock discoveries, above the Deep's -60..27 density envelope."""
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

import nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box,HOME_BIOMES

ROOT=Path(__file__).resolve().parents[1]
KINDS=('moss_grotto','calcite_drapery','root_vault','buried_cistern','abandoned_gallery',
       'collapsed_archive','silt_pool','basalt_columns','fossil_pocket','crystal_beds',
       'buried_bridge','lithic_fault')
STONE=B('alfheim:cracked_livingrock');AIR=B('minecraft:air')


def build(kind):
    p=Piece(31,20,31)
    host=B('minecraft:calcite') if kind=='calcite_drapery' else B('minecraft:basalt',axis='y') if kind=='basalt_columns' else STONE
    for x in range(31):
        for z in range(31):
            r=math.hypot(x-15,z-15)
            if r>14.7:continue
            for y in range(20):p.set(x,y,z,host if y<=3 or y>=18 or r>13 else AIR)
    # Four short discovery mouths, not an unbounded cave carver.
    box(p,13,4,0,17,7,30,AIR);box(p,0,4,13,30,7,17,AIR)
    if kind in ('buried_cistern','silt_pool','moss_grotto'):
        for x in range(10,21):
            for z in range(10,21):
                p.set(x,3,z,B('minecraft:clay'))
                p.set(x,4,z,STONE if x in (10,20) or z in (10,20) else B('minecraft:water',level=0))
    if kind in ('moss_grotto','root_vault'):
        for x,z in ((7,9),(9,23),(23,9),(24,20),(6,18),(20,6)):
            p.set(x,3,z,B('minecraft:moss_block'));p.set(x,4,z,B('minecraft:red_mushroom' if (x+z)%2 else 'minecraft:brown_mushroom'))
        for x,z in ((10,10),(20,10),(10,20),(20,20)):
            p.set(x,18,z,STONE);p.set(x,17,z,B('minecraft:hanging_roots'))
    if kind=='calcite_drapery':
        for x,z in ((8,12),(11,9),(19,9),(22,12),(9,21),(21,21)):
            p.set(x,18,z,B('minecraft:dripstone_block'))
            for y,thickness in ((17,'frustum'),(16,'tip')):
                p.set(x,y,z,B('minecraft:pointed_dripstone',vertical_direction='down',thickness=thickness,waterlogged=False))
    if kind in ('basalt_columns','lithic_fault'):
        for x in (7,10,21,24):
            for z in (8,23):
                height=5+(x+z)%5
                box(p,x,4,z,x+1,height,z+1,B('minecraft:basalt',axis='y'))
        if kind=='lithic_fault':
            for x in range(5,26):
                for z in (8,9):p.set(x,3,z,B('minecraft:obsidian' if x%5==0 else 'minecraft:tuff'))
    if kind=='fossil_pocket':
        for x in range(8,23):
            p.set(x,4,10,B('minecraft:bone_block',axis='x'))
            if x%3==0:
                for z in range(8,14):p.set(x,4,z,B('minecraft:bone_block',axis='z'))
        for x in range(8,24):p.set(x,3,10,B('minecraft:clay'))
    if kind=='crystal_beds':
        for x,z in ((7,10),(10,8),(20,8),(24,12),(9,22),(22,22)):
            p.set(x,3,z,B('minecraft:amethyst_block'))
            p.set(x,4,z,B('minecraft:amethyst_cluster',facing='up',waterlogged=False))
    if kind in ('abandoned_gallery','collapsed_archive','root_vault','buried_cistern','buried_bridge'):
        for z in (8,22):
            for x in (7,23):box(p,x,4,z,x,11,z,B('alfheim:ivory_livingrock_bricks'))
            box(p,7,12,z,23,12,z,B('alfheim:moonstone_livingrock_carved'))
        if kind=='collapsed_archive':
            for z in range(8,23):
                box(p,8,4,z,8,6 if z<16 else 4,z,B('minecraft:bookshelf'))
        if kind=='abandoned_gallery':
            for x in range(9,23):p.set(x,3,9,B('botania:dreamwood_planks'))
        if kind in ('collapsed_archive','abandoned_gallery','buried_cistern'):
            p.set(21,4,18,B('minecraft:barrel',facing='up',open=False),
                  {'id':'minecraft:barrel','LootTable':'alfheim:chests/deep_quarry_supplies'})
    if kind=='buried_bridge':
        box(p,9,1,9,21,6,21,AIR)
        box(p,13,7,6,17,7,24,B('alfheim:ivory_livingrock_polished'))
        for z in range(6,25):
            for x in (12,18):p.set(x,7,z,B('alfheim:moonstone_livingrock_carved'))
        # Two supported flights connect the raised bridge to the cave floor.
        for i in range(4):
            for z,facing in ((2+i,'south'),(28-i,'north')):
                box(p,13,3,z,17,3+i,z,STONE)
                for x in range(13,18):p.set(x,4+i,z,B('alfheim:ivory_livingrock_stairs',facing=facing,half='bottom',shape='straight',waterlogged=False))
    # Low light in the floor; never crystal models buried into room walls.
    for x,z in ((6,15),(24,15)):p.set(x,3,z,B('alfheim:mana_glass_light'))
    assert p.dropped==0,(kind,p.dropped)
    p.prune_orphans()
    return p.to_nbt()


class Provider:
    aliases=('alfheim_upper_underworld',)
    provider_id='alfheim_upper_underworld_v1'
    def __init__(self,stage):self.stage=stage
    def describe(self):return {'provider_id':self.provider_id,'aliases':list(self.aliases)}
    def generate(self,request,resolver):
        files={};records=[]
        for name in KINDS:
            root=build(name)
            for state in root['palette']:
                probe=resolver.probe(state['Name'],kind='block');assert probe['level'] in ('exact','vanilla'),probe
            rel=f'kubejs/data/alfheim/structures/upper_underworld/{name}.nbt'
            path=self.stage/rel;path.parent.mkdir(parents=True,exist_ok=True);nbt.save(path,'',root)
            data=gzip.compress(gzip.decompress(path.read_bytes()),mtime=0);path.write_bytes(data);files[name+'.nbt']=data
            records.append({'name':name,'file':rel,'sha256':hashlib.sha256(data).hexdigest()})
        definitions={
            'worldgen/structure/upper_underworld.json':{'type':'alfheim_companion:upper_underworld','biomes':'#alfheim:has_upper_underworld','step':'underground_structures','terrain_adaptation':'none','spawn_overrides':{}},
            'worldgen/structure_set/upper_underworld.json':{'structures':[{'structure':'alfheim:upper_underworld','weight':1}],'placement':{'type':'minecraft:random_spread','spacing':80,'separation':48,'salt':202610151}},
            'tags/worldgen/biome/has_upper_underworld.json':{'replace':False,'values':HOME_BIOMES}}
        for rel,body in definitions.items():
            path=self.stage/'kubejs/data/alfheim'/rel;path.parent.mkdir(parents=True,exist_ok=True)
            data=(json.dumps(body,indent=2)+'\n').encode();path.write_bytes(data);files[rel.replace('/','_')]=data
        return {'provider_id':self.provider_id,'status':'GENERATED_NOT_VALIDATED',
                'generated_layout':{'templates':records,'json':list(definitions),'min_y':32,'max_base_y':96,'max_top_y':115,
                                    'deep_density_envelope':[-60,27],'minimum_roof_cover':12},
                'structure_artifact':{'format':'minecraft_structure_nbt','piece_count':12},'artifact_bytes':files}


def main():
    sys.path.insert(0,'C:/GITS/Structuresmith/StructureSmith/src')
    from structure_capability import StructureCapability
    stage=ROOT/'build/upper-underworld'
    cap=StructureCapability(project_root=ROOT,state_root=stage/'snapshots')
    cap.inventory.add_registry_ids(json.loads((ROOT/'server/local/kubejs/export/registries/block.json').read_text()),kind='block')
    cap.register_generator(Provider(stage))
    result=cap.generate({'structure_id':'alfheim:upper_underworld','target_version':'1.20.1','grade':3,
        'purpose':{'kind':'upper_rock_discoveries','required_zones':['geological caves','buried ruins','fossil beds']},
        'context':{'dimension':'mythicbotany:alfheim','terrain':'stone above Y27 Deep boundary'},
        'integration_contracts':{'minimum_independent_gap':500},'generation':{'kind':'alfheim_upper_underworld','materialize_nbt':True}})
    layout=result['generated_layout']
    for record in layout['templates']:
        target=ROOT/record['file'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((stage/record['file']).read_bytes())
    for rel in layout['json']:
        target=ROOT/'kubejs/data/alfheim'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((stage/'kubejs/data/alfheim'/rel).read_bytes())
    (ROOT/'tools/upper_underworld_report.json').write_text(json.dumps({'capability':'Continuity Works 0.3.2','snapshot_id':result['snapshot']['snapshot_id'],
        'generation':result['generation'],'layout':layout},indent=2)+'\n')
    print('Generated twelve upper-rock discoveries; Y>=32, Deep density unchanged; runtime test required')


if __name__=='__main__':main()
