"""235-square royal citadel, emitted by a Continuity Works downstream provider.

25 non-overlapping 47-block tiles; native runtime adds air-only foundation support.
"""
import gzip
import hashlib
import json
from pathlib import Path
import sys

import nbt
from structure_nbt import Piece
from gen_ancient_districts import B,box
from gen_elder_lineage import royal,bench,desk,canopy_bed
from district_refit import detail_nbt

ROOT=Path(__file__).resolve().parents[1]
KINDS=('keep','tower','gate','curtain','hall','garden')
STONE=B('alfheim:ivory_livingrock_bricks')
FLOOR=B('alfheim:ivory_livingrock_polished')
CARVED=B('alfheim:moonstone_livingrock_carved')
AIR=B('minecraft:air')


def tile(kind):
    p=Piece(47,48,47)
    def furnish(builder,x,y,z):
        furniture=Piece(47,48,47);builder(furniture,x,z)
        for (px,py,pz),(state,be) in furniture.blocks.items():
            item=furniture.palette[state]
            p.set(px,py+y-1,pz,(item['Name'],item.get('Properties')),be)
    box(p,0,0,0,46,7,46,STONE);box(p,0,8,0,46,8,46,FLOOR)
    box(p,0,9,0,46,47,46,AIR)
    if kind in ('curtain','gate','tower'):
        box(p,0,9,1,46,27,5,STONE)
        box(p,0,28,0,46,28,8,FLOOR)
        for x in range(47):
            if x%4<2:box(p,x,29,1,x,31,2,CARVED)
        if kind=='tower':
            box(p,1,9,0,5,27,46,STONE);box(p,0,28,0,8,28,46,FLOOR)
            for z in range(47):
                if z%4<2:box(p,1,29,z,2,31,z,CARVED)
    if kind in ('keep','hall','tower'):
        lo,hi=(9,37) if kind=='tower' else (4,42)
        top=44 if kind in ('keep','tower') else 28
        for x in (lo,hi):box(p,x,9,lo,x,top,hi,STONE)
        for z in (lo,hi):box(p,lo,9,z,hi,top,z,STONE)
        for level in ((20,32,44) if kind=='keep' else (28,44) if kind=='tower' else (28,)):
            box(p,lo,level,lo,hi,level,hi,FLOOR)
        for x in range(lo,hi+1,4):
            for z in (lo,hi):
                box(p,x,top+1,z,x,top+3,z,CARVED)
        for z in range(lo+4,hi,4):
            for x in (lo,hi):box(p,x,top+1,z,x,top+3,z,CARVED)
        for y in (13,25,37):
            if y+3>=top:continue
            for q in range(lo+5,hi-3,8):
                for x in (lo,hi):box(p,x,y,q,x,y+3,q+1,B('botania:elf_glass'))
                for z in (lo,hi):box(p,q,y,z,q+1,y+3,z,B('botania:elf_glass'))
        for y in range(9,min(top,22)):
            for q in (lo+2,hi-2):
                for x in (lo+2,hi-2):p.set(x,y,q,CARVED)
        if kind=='keep':
            for z in (11,18,30,37):furnish(bench,12,9,z);furnish(bench,29,9,z)
            royal(p,21,9,10,'royal_audience_bench_left')
            royal(p,22,9,10,'royal_audience_bench_right')
            furnish(desk,12,9,12);furnish(canopy_bed,12,21,12)
            for z in range(12,36,4):
                box(p,6,21,z,7,23,z+1,B('minecraft:bookshelf'))
        else:
            for z in (15,30):furnish(bench,14,9,z);furnish(desk,28,9,z)
        # Broad, illuminated ground-floor doors meet the district-sized courtyard axes.
        box(p,20,9,0,26,13,46,AIR);box(p,0,9,20,46,13,26,AIR)
        # Supported stairs and carved headroom join upper floors and battlements.
        flights=((8,20,35,36,-1),(20,32,9,10,1),(32,44,35,36,-1)) if kind=='keep' else \
                ((8,28,31,34,-1),(28,44,13,12,1)) if kind=='tower' else ((8,28,35,35,-1),)
        for lower,upper,x,start,direction in flights:
            for i in range(upper-lower):
                z=start+i*direction;y=lower+i+1
                box(p,x-1,lower,z,x+1,y-1,z,STONE)
                box(p,x-1,y+1,z,x+1,min(47,y+4),z,AIR)
                for xx in range(x-1,x+2):p.set(xx,y,z,B('alfheim:ivory_livingrock_stairs',facing='north' if direction<0 else 'south',half='bottom',shape='straight',waterlogged=False))
    if kind=='gate':
        box(p,19,1,0,27,24,15,AIR)
        for z in range(16):
            y=z//2
            box(p,19,0,z,27,y,z,STONE)
            for x in range(20,27):p.set(x,y+1,z,B('alfheim:ivory_livingrock_stairs',facing='south',half='bottom',shape='straight',waterlogged=False))
        for x in (14,32):box(p,x,9,7,x,25,9,CARVED)
    if kind=='garden':
        for x0,z0 in ((6,6),(29,6),(6,29),(29,29)):
            box(p,x0,8,z0,x0+10,8,z0+10,B('minecraft:grass_block'))
            for x in (x0,x0+10):box(p,x,9,z0,x,9,z0+10,CARVED)
            for z in (z0,z0+10):box(p,x0,9,z,x0+10,9,z,CARVED)
            p.set(x0+5,9,z0+5,B('minecraft:flowering_azalea'))
        box(p,20,8,20,26,8,26,CARVED)
        for x in range(20,27):
            for z in range(20,27):p.set(x,9,z,CARVED if x in (20,26) or z in (20,26) else B('minecraft:water',level=0))
        for x in (10,33):furnish(bench,x,9,22)
    # Flush lighting on regular architectural centres; no lantern or entity clutter.
    for x,z in ((16,16),(30,16),(16,30),(30,30)):
        p.set(x,8,z,B('alfheim:mana_glass_light'))
    if kind in ('keep','hall','tower'):
        p.set(16,9,18,B('minecraft:barrel',facing='up',open=False),
              {'id':'minecraft:barrel','LootTable':'alfheim:chests/lineage/records'})
    assert p.dropped==0,(kind,p.dropped)
    return detail_nbt(p,'royal_castle',kind)


class CastleProvider:
    aliases=('alfheim_royal_castle',)
    provider_id='alfheim_royal_castle_v1'
    def __init__(self,stage):self.stage=stage
    def describe(self):return {'provider_id':self.provider_id,'aliases':list(self.aliases)}
    def generate(self,request,registry_resolver):
        files={};stats=[]
        for kind in KINDS:
            root=tile(kind)
            for state in root['palette']:
                probe=registry_resolver.probe(state['Name'],kind='block')
                assert probe['level'] in ('exact','vanilla'),probe
            relative=f'kubejs/data/alfheim/structures/royal_castle/{kind}.nbt'
            path=self.stage/relative;path.parent.mkdir(parents=True,exist_ok=True)
            nbt.save(path,'',root);data=gzip.compress(gzip.decompress(path.read_bytes()),mtime=0);path.write_bytes(data)
            files[kind+'.nbt']=data
            stats.append({'kind':kind,'file':relative,'sha256':hashlib.sha256(data).hexdigest(),'blocks':len(root['blocks'])})
        definitions={
          'worldgen/structure/royal_castle.json':{'type':'alfheim_companion:royal_castle','biomes':'#alfheim:has_royal_castle','step':'surface_structures','terrain_adaptation':'none','spawn_overrides':{}},
          'worldgen/structure_set/royal_castle.json':{'structures':[{'structure':'alfheim:royal_castle','weight':1}], 'placement':{'type':'minecraft:concentric_rings','distance':32,'spread':3,'count':3,'salt':202610152,'preferred_biomes':'#alfheim:has_royal_castle'}},
          'tags/worldgen/biome/has_royal_castle.json':{'replace':False,'values':['mythicbotany:golden_fields','mythicbotany:alfheim_plains','alfheim:bloomfall_vale','alfheim:silverbark_wood','mythicbotany:alfheim_hills']}}
        for relative,body in definitions.items():
            path=self.stage/'kubejs/data/alfheim'/relative;path.parent.mkdir(parents=True,exist_ok=True)
            data=(json.dumps(body,indent=2)+'\n').encode();path.write_bytes(data);files[relative.replace('/','_')]=data
        return {'provider_id':self.provider_id,'status':'GENERATED_NOT_VALIDATED',
                'generated_layout':{'footprint':[235,235],'tiles':25,'native_foundation_pieces':1,'templates':stats,'emitted_json':list(definitions)},
                'structure_artifact':{'format':'minecraft_structure_nbt','piece_count':6},'artifact_bytes':files}


def main():
    sys.path.insert(0,'C:/GITS/Structuresmith/StructureSmith/src')
    from structure_capability import StructureCapability
    stage=ROOT/'build/royal-castle'
    cap=StructureCapability(project_root=ROOT,state_root=stage/'snapshots')
    cap.inventory.add_registry_ids(json.loads((ROOT/'server/local/kubejs/export/registries/block.json').read_text()),kind='block')
    cap.register_generator(CastleProvider(stage))
    result=cap.generate({'structure_id':'alfheim:royal_castle','target_version':'1.20.1','grade':3,
        'purpose':{'kind':'royal_citadel','required_zones':['keep','guard towers','four gatehouses','court halls','gardens','battlement walks']},
        'context':{'dimension':'mythicbotany:alfheim','terrain':'bounded native nine-column site check'},
        'integration_contracts':{'independent_district_footprint_gap':500},'generation':{'kind':'alfheim_royal_castle','materialize_nbt':True}})
    for item in result['generated_layout']['templates']:
        target=ROOT/item['file'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((stage/item['file']).read_bytes())
    for rel in result['generated_layout']['emitted_json']:
        target=ROOT/'kubejs/data/alfheim'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((stage/'kubejs/data/alfheim'/rel).read_bytes())
    report={'capability':'Continuity Works 0.3.2','method':'StructureCapability.generate with registered CastleProvider',
            'snapshot_id':result['snapshot']['snapshot_id'],'generation':result['generation'],'layout':result['generated_layout']}
    (ROOT/'tools/royal_castle_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Generated six castle tile types; 25-tile 235x235 citadel; runtime acceptance pending')


if __name__=='__main__':main()
