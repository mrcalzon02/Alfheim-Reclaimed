"""Standalone purple ley anomaly, separated from the Faultwork mine architecture.

No natural structure set is emitted: a runtime reservation adapter must establish
500 blocks between independent footprints before this can be admitted naturally.
"""
import gzip
import hashlib
import json
import math
from pathlib import Path

import nbt
from structure_nbt import Piece


def build():
    p=Piece(47,32,47)
    # A bounded cavity with a supported, circular stone shell and sealed roof.
    for x in range(47):
        for z in range(47):
            radius=math.hypot(x-23,z-23)
            if radius > 22:
                continue
            for y in range(30):
                edge=radius>20 or y<3 or y>=28
                p.set(x,y,z,('alfheim:cracked_livingrock' if edge else 'minecraft:air',None))
            if radius <=20:
                p.set(x,2,z,('alfheim:gloam_livingrock_polished',None))
    # Original concentric fracture vocabulary, now owned by this one structure.
    for x in range(4,43):
        for z in range(4,43):
            radius=math.hypot(x-23,z-23)
            # Four clear cardinal aisles cross the concentric rings.
            if abs(x-23)<=2 or abs(z-23)<=2:
                continue
            for ring,height in ((7,13),(12,8),(17,6)):
                if abs(radius-ring)<=0.7:
                    for y in range(3,height):
                        p.set(x,y,z,('alfheim:magmatic_livingrock' if y%3==0 else 'minecraft:crying_obsidian',None))
    for x in range(22,25):
        for z in range(22,25):
            for y in range(3,18):
                p.set(x,y,z,('alfheim:magmatic_livingrock' if y<5 else 'minecraft:crying_obsidian',None))
    # Navigable service apron and low-key light; no lantern multiplication.
    for x,z in ((23,5),(5,23),(41,23),(23,41)):
        p.set(x,2,z,('alfheim:mana_glass_light',None))
    p.set(17,3,23,('minecraft:barrel',{'facing':'up','open':'false'}),
          {'id':'minecraft:barrel','LootTable':'alfheim:chests/faultwork_salvage'})
    assert p.dropped==0
    return p


class LeyFractureProvider:
    provider_id='alfheim_standalone_ley_fracture_v1'
    aliases=('alfheim_ley_fracture',)

    def __init__(self,stage):self.stage=stage

    def describe(self):
        return {'provider_id':self.provider_id,'aliases':list(self.aliases),
                'operation':'materialize isolated ley anomaly; natural placement blocked'}

    def generate(self,request,registry_resolver):
        p=build()
        probes=[registry_resolver.probe(s['Name'],kind='block') for s in p.palette]
        assert all(v['level'] in ('exact','vanilla') for v in probes),probes
        base=Path('kubejs/data/alfheim')
        relative=base/'structures/ley_fracture/core.nbt'
        path=self.stage/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        nbt.save(path,'',p.to_nbt())
        data=gzip.compress(gzip.decompress(path.read_bytes()),mtime=0)
        path.write_bytes(data)
        files={str(relative):data}
        pool={'name':'alfheim:ley_fracture/core','fallback':'minecraft:empty',
              'elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element',
              'location':'alfheim:ley_fracture/core','processors':'minecraft:empty','projection':'rigid'}}]}
        spec={'type':'minecraft:jigsaw','biomes':'#alfheim:deepworks_land',
              'step':'underground_structures','terrain_adaptation':'none','spawn_overrides':{},
              'start_pool':'alfheim:ley_fracture/core','size':1,'start_height':{'absolute':-40},
              'max_distance_from_center':116,'use_expansion_hack':False}
        for rel,body in ((base/'worldgen/template_pool/ley_fracture/core.json',pool),
                         (base/'worldgen/structure/ley_fracture.json',spec)):
            blob=(json.dumps(body,indent=2)+'\n').encode()
            target=self.stage/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
            files[str(rel)]=blob
        return {'provider_id':self.provider_id,'status':'LOCALLY_VALIDATED',
                'generated_layout':{'placement_status':'BLOCKED_PENDING_500_BLOCK_RESERVATION_ADAPTER',
                                    'envelope':[47,32,47],'registry_probes':probes,
                                    'emitted_files':list(files)},
                'structure_artifact':{'format':'minecraft_structure_nbt','piece_count':1,
                                      'sha256':hashlib.sha256(data).hexdigest()},
                'artifact_bytes':{'core.nbt':data,'pool.json':next(v for k,v in files.items() if 'template_pool' in k),
                                  'structure.json':next(v for k,v in files.items() if 'worldgen/structure/' in k.replace('\\','/'))}}
