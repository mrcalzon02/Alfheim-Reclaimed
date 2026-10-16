"""War salvage: additive recipes, spine processing and six bounded object models.

Vanilla recipes are emitted by the installed Continuity Works content tool.
Mod station recipes follow the already shipped pack schemas, verified in Forge.
"""
import argparse
import json
from pathlib import Path
import sys
from model_geometry import clean_model, FACES

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, 'C:/GITS/Structuresmith/StructureSmith/src')
from structure_capability import StructureCapability

def box(a, b):
    return {'from': a, 'to': b, 'faces': {f: {'texture': '#all'} for f in FACES}}

# Geometry and collision share precisely the same boxes. No rotated/coplanar overlays.
OBJECTS = {
    'salvaged_core_cradle': ('golem_core_socket_empty', 0, [([1,0,1],[15,3,15]),([2,3,2],[5,12,14]),([11,3,2],[14,12,14]),([5,3,2],[11,12,5]),([5,3,11],[11,12,14])]),
    'severed_conduit_display': ('golem_conduit_severed', 0, [([1,0,2],[15,2,14]),([3,2,5],[6,6,11]),([10,2,5],[13,6,11]),([2,6,4],[7,10,12]),([9,6,4],[14,10,12])]),
    'titan_rib_reliquary': ('titan_bone', 0, [([1,0,1],[15,2,15]),([7,2,2],[9,5,14]),([2,2,3],[4,11,5]),([12,2,3],[14,11,5]),([2,2,11],[4,11,13]),([12,2,11],[14,11,13]),([4,10,3],[12,12,5]),([4,10,11],[12,12,13])]),
    'sealed_organ_vessel': ('titan_organ_calcified', 0, [([3,0,3],[13,2,13]),([4,2,4],[12,11,12]),([3,11,3],[13,13,13]),([6,13,6],[10,15,10])]),
    'reclaimed_ward_brazier': ('war_wardplate_fractured', 12, [([2,0,2],[14,2,14]),([6,2,6],[10,8,10]),([2,8,2],[14,10,14]),([2,10,2],[4,14,14]),([12,10,2],[14,14,14]),([4,10,2],[12,14,4]),([4,10,12],[12,14,14])]),
    'restored_lattice_lamp': ('golem_lattice_shards', 15, [([2,0,2],[14,2,14]),([5,2,5],[11,4,11]),([4,4,4],[12,12,12]),([5,12,5],[11,14,11]),([3,14,3],[13,16,13])]),
}
ITEMS = {
    'washed_titan_biomass': ('bio_sludge_mineralized', 'Mana-washed remains. Purify with Source into titan resin.'),
    'washed_golem_grit': ('golem_crystal_fractured', 'Mana-washed salvage. Temper with Source into inert war lattice.'),
    'purified_titan_resin': ('titan_organ_calcified', 'Era III fertilizer and binding supplies; Era VI expedition relief. No active titan tissue.'),
    'tempered_war_lattice': ('golem_lattice_shards', 'Restored lamps, Era VI relief and Era VIII gear-quality supplies. No recovered active core.'),
}

def build():
    cap = StructureCapability(project_root=ROOT, state_root=ROOT/'build/war-salvage/snapshots')
    # Existing exported IDs are evidence; newly authored IDs are not claimed runtime-proven here.
    cap.inventory.add_registry_ids(json.loads((ROOT/'server/local/kubejs/export/registries/item.json').read_text()), kind='item')
    recipes = {}; out = {}; gates = []
    def emit(p, value):
        out[p] = value if isinstance(value, bytes) else (json.dumps(value, indent=2)+'\n').encode()
    def vanilla(name, kind, result, ingredients=None, **kw):
        request = dict(recipe_id='alfheim:war_salvage/'+name, target_version='1.20.1', type=kind,
                       result=result, id_policy='namespace', **kw)
        if ingredients is not None: request['ingredients']=[{'item': x} for x in ingredients]
        answer = cap.minecraft_recipe_generate(request)
        assert answer['materialization_allowed'], answer
        gates.append({'id':answer['resource_id'], 'gate':answer['gate']})
        recipes[name]=answer['json']
    def station(name, data): recipes[name]=data
    def mana(name, material, result, cost):
        station(name, dict(type='botania:mana_infusion',input={'item':material},output={'item':result},mana=cost))
    def apparatus(name, reagent, pedestals, result, cost, count=1):
        station(name, dict(type='ars_nouveau:enchanting_apparatus', reagent=[{'item':reagent}],
            pedestalItems=[{'item':x} for x in pedestals], output={'item':result,'count':count},
            sourceCost=cost,keepNbtOfReagent=False))
    catalog=json.loads((ROOT/'kubejs/war_remains_catalog.json').read_text())['blocks']
    family_counts={}
    dyes=['white','gray','brown','green','black','purple','cyan','light_blue']
    for b in catalog:
        name=b['id'].split(':')[1]; family=b['family']
        # Replica blocks cost ordinary matter; they cannot produce powered cores or era tokens.
        base = 'minecraft:rotten_flesh' if family in ('sludge','flesh','organ','hide') else 'minecraft:bone_block' if family=='bone' else 'minecraft:amethyst_block' if name.startswith('golem') else 'minecraft:stone_bricks'
        # Distinct ingredients are essential: identical shapeless inputs would make
        # only one of several decay states craftable in a real crafting grid.
        group='golem' if name.startswith('golem') else 'war' if name.startswith('war') else family
        variant=family_counts.get(group,0);family_counts[group]=variant+1
        replica=[base,'minecraft:clay_ball','minecraft:'+dyes[variant]+'_dye']
        helper={'sludge':'slime_ball','flesh':'beetroot','organ':'kelp','hide':'leather'}.get(family)
        if helper:replica.append('minecraft:'+helper)
        vanilla('replica/'+name,'crafting_shapeless',{'item':b['id']},replica)
        organic=family in ('sludge','flesh','organ','hide','bone')
        mana('wash/'+name,b['id'],'alfheim:washed_titan_biomass' if organic else 'alfheim:washed_golem_grit',4000 if organic else 6000)
    apparatus('purify_resin','alfheim:washed_titan_biomass',['botania:mana_powder','ars_nouveau:source_gem'],'alfheim:purified_titan_resin',2000)
    apparatus('temper_lattice','alfheim:washed_golem_grit',['botania:mana_powder','ars_nouveau:source_gem'],'alfheim:tempered_war_lattice',3000)
    station('era3_reclamation_fertilizer',dict(type='botania:runic_altar',ingredients=[{'item':x} for x in ['alfheim:purified_titan_resin','alfheim:living_fibre','botania:mana_powder']],output={'item':'botania:fertilizer','count':4},mana=8000))
    apparatus('binding_slime','alfheim:purified_titan_resin',['botania:mana_powder'],'minecraft:slime_ball',1500,4)
    apparatus('preserved_leather','alfheim:purified_titan_resin',['minecraft:leather','botania:mana_powder'],'minecraft:leather',2000,4)
    apparatus('era6_expedition_relief','alfheim:purified_titan_resin',['alfheim:tempered_war_lattice','alfheim:wildmarch_sinew'],'mmorpg:currency/orb_of_relief',6000,2)
    apparatus('era8_lattice_quality','alfheim:tempered_war_lattice',['alfheim:tempered_war_lattice','alfheim:rimebound_lattice'],'mmorpg:currency/orb_of_quality',10000,2)
    script=["// Generated by tools/gen_war_salvage.py. Restart required.","StartupEvents.registry('item', event => {"]
    for name,(tex,tip) in ITEMS.items():
        script.append(f"  event.create('alfheim:{name}').displayName('{name.replace('_',' ').title()}').texture('alfheim:block/{tex}').tooltip({json.dumps(tip)})")
    script += ['})',"StartupEvents.registry('block', event => {"]
    ingredients=['golem_core_socket_empty','golem_conduit_severed','titan_bone_fractured','titan_organ_calcified','war_wardplate_fractured','golem_lattice_shards']
    for (name,(tex,light,boxes)),raw in zip(OBJECTS.items(),ingredients):
        model=clean_model({'parent':'minecraft:block/block','textures':{'all':'alfheim:block/'+tex,'particle':'alfheim:block/'+tex},'elements':[box(a,b) for a,b in boxes]})
        emit(f'kubejs/assets/alfheim/models/block/war_salvage/{name}.json',model)
        emit(f'kubejs/assets/alfheim/models/item/{name}.json',{'parent':'alfheim:block/war_salvage/'+name})
        emit(f'kubejs/assets/alfheim/blockstates/{name}.json',{'variants':{'':{'model':'alfheim:block/war_salvage/'+name}}})
        emit(f'kubejs/data/alfheim/loot_tables/blocks/{name}.json',{'type':'minecraft:block','pools':[{'rolls':1,'conditions':[{'condition':'minecraft:survives_explosion'}],'entries':[{'type':'minecraft:item','name':'alfheim:'+name}]}]})
        script.append(f"  event.create('alfheim:{name}').displayName('{name.replace('_',' ').title()}').model('alfheim:block/war_salvage/{name}').hardness(2).resistance(6).soundType('stone').fullBlock(false).notSolid().noValidSpawns(true).lightLevel({light / 15})")
        script.extend('    .box('+', '.join(map(str,a+b))+')' for a,b in boxes)
        script.append("    .tagBlock('minecraft:mineable/pickaxe').tagBoth('alfheim:war_salvage_objects')")
        if light:
            apparatus('restore/'+name,'alfheim:'+raw,['alfheim:tempered_war_lattice','botania:mana_powder','ars_nouveau:source_gem'],'alfheim:'+name,2000)
        else: vanilla('display/'+name,'crafting_shapeless',{'item':'alfheim:'+name},['alfheim:'+raw,'botania:livingrock'])
    script+=['})','']
    emit('kubejs/startup_scripts/27_war_salvage.js','\n'.join(script).encode())
    for name,data in recipes.items(): emit('kubejs/data/alfheim/recipes/war_salvage/'+name+'.json',data)
    emit('tools/war_salvage_manifest.json',dict(capability='Continuity Works minecraft_recipe_generate, Java 1.20.1',
        id_policy='namespace during authoring; actual recipe/ingredient registries checked separately in Forge',
        recipes=recipes,objects=OBJECTS,items=ITEMS,cw_gates=gates))
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    output=build()
    for rel,data in output.items():
        path=ROOT/rel
        if args.check: assert path.exists() and path.read_bytes()==data,rel
        else: path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print('WAR SALVAGE:',len(output),'files', 'verified' if args.check else 'generated')
