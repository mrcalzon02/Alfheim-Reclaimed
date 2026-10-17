"""Check generated gem registrations, reachability, models, loot and placement bounds."""
import hashlib,io,json,re,zipfile
from pathlib import Path
from PIL import Image
from gen_gemstones import ROOT,ASSET,DATA,STARTUP,build
from gemstone_catalog import GEMS,POOLS

def main():
    outputs,manifest=build()
    for rel,data in outputs.items():assert (ROOT/rel).read_bytes()==data,rel
    source=outputs[STARTUP].decode();declared=re.findall(r'event.create\([\'"]([^\'"]+)[\'"]\)',source)
    assert len(declared)==len(set(declared))==len(manifest['new_items'])+len(manifest['new_blocks'])
    assert not any(k.startswith('minecraft:') for k in declared)
    knownitems=json.loads((ROOT/'server/local/kubejs/export/registries/item.json').read_text());knownblocks=json.loads((ROOT/'server/local/kubejs/export/registries/block.json').read_text())
    assert not set(declared)&set(knownitems),'new IDs collide with exported registry'
    jars=[zipfile.ZipFile(p) for p in (ROOT/'mods').glob('*.jar')]
    jars.append(zipfile.ZipFile('C:/Users/Admin/curseforge/minecraft/Install/versions/1.20.1/1.20.1.jar'))
    resources={n for z in jars for n in z.namelist() if n.startswith(('assets/','data/'))}
    def exists(path):return path in resources or (ROOT/'kubejs'/path).exists() or (ROOT/'first_party_mods/alfheim_companion/src/main/resources'/path).exists()
    gems_reached=set();texture_refs=set()
    for key,pool in POOLS.items():
        loot=json.loads(outputs[DATA+f'loot_tables/gemstones/{key}.json'])
        drops=loot['pools'][0]['entries'];assert all(e['weight']>0 for e in drops)
        assert {e['name'] for e in drops}=={g['item'] for g in GEMS if g['id'] in pool['gems']}
        gems_reached.update(e['name'] for e in drops)
        feature=json.loads(outputs[DATA+f'worldgen/configured_feature/gemstones/{key}.json'])
        placed=json.loads(outputs[DATA+f'worldgen/placed_feature/gemstones/{key}.json'])
        modifier=json.loads(outputs[DATA+f'forge/biome_modifier/zz_gemstones_{key}.json'])
        assert placed['placement'][0]['type']=='minecraft:rarity_filter' and placed['placement'][0]['chance']>=7
        for biome in modifier['biomes']:
            ns,path=biome.split(':');assert exists(f'data/{ns}/worldgen/biome/{path}.json'),biome
        if pool['source'].startswith('aquatic'):
            assert feature['type']=='minecraft:simple_block' and modifier['step']=='vegetal_decoration'
            preds=placed['placement'][-2]['predicate']['predicates'];assert preds[0]['fluids']==['minecraft:water'] and preds[1]['offset']==[0,-1,0]
        else:
            assert feature['type']=='minecraft:ore' and feature['config']['size']<=6
            assert pool['y'][0]>=-64 and pool['y'][1]<320
            for t in feature['config']['targets']:
                assert t['target']['block'] in knownblocks and t['state']['Name'] in manifest['new_blocks']
    assert gems_reached=={g['item'] for g in GEMS}
    for g in GEMS:
        if not g['item'].startswith('alfheim:'):assert g['item'] in knownitems;continue
        icon=Image.open(io.BytesIO(outputs[ASSET+f'textures/item/gemstones/{g["id"]}.png']))
        assert icon.size==(128,128) and icon.getchannel('A').getextrema()==(0,255)
        assert len(icon.getcolors(65536))>=6
    for block in manifest['new_blocks']:
        stem=block.split(':')[1];loot=json.loads(outputs[DATA+f'loot_tables/blocks/{stem}.json']);children=loot['pools'][0]['entries'][0]['children']
        assert children[0]['name']==block and children[0]['conditions'][0]['predicate']['enchantments'][0]['enchantment']=='minecraft:silk_touch'
        assert children[1]['functions'][0]['enchantment']=='minecraft:fortune'
        model=json.loads(outputs[ASSET+f'models/block/gemstones/{stem}.json'])
        for ref in model['textures'].values():
            ns,path=ref.split(':');tex=f'assets/{ns}/textures/{path}.png'
            assert exists(tex),tex;texture_refs.add(tex)
    native='first_party_mods/alfheim_companion/src/main/resources/assets/alfheim_companion/'
    selections=json.loads(outputs[native+'gemstone_displays.json']);assert len(selections)==len(GEMS)
    for selection in selections:
        assert selection['item'] in gems_reached
        assert native+f'models/item/{selection["id"]}_display_pedestal.json' in outputs
        assert len(selection['accent'])==6
    for rel,data in outputs.items():
        if '/models/' not in rel or not rel.endswith('.json'):continue
        for ref in json.loads(data).get('textures',{}).values():
            if ref.startswith('#'):continue
            ns,path=ref.split(':');assert exists(f'assets/{ns}/textures/{path}.png'),ref
    recipe=json.loads(outputs['first_party_mods/alfheim_companion/src/main/resources/data/alfheim_companion/recipes/geologist_pedestal.json']);assert recipe['result']['item']=='alfheim_companion:geologist_pedestal'
    for z in jars:z.close()
    result={'status':'LOCALLY_VALIDATED_RUNTIME_REQUIRED','gem_materials':len(GEMS),'new_items':len(manifest['new_items']),'new_blocks':len(manifest['new_blocks']),'display_selections':len(selections),'source_pools':len(POOLS),'generated_files':len(outputs),'model_texture_paths':len(texture_refs),'checks':['exact source equality','unique non-colliding startup IDs','all gem items reachable in positive-weight loot pools','Silk Touch preserves every deposit','Fortune applies to gem drops','existing host and reused item IDs verified','all biome and model texture IDs resolved including pedestal','bounded rarity/vein sizes and Y ranges','aquatic water and seabed predicates present','232 display entries and models match gem roster; empty pedestal recipe only'],'runtime':'KubeJS startup registration, mining drops, displays and new-chunk generation still require a live game check'}
    (ROOT/'tools/gemstone_static_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('GEMSTONE STATIC PASS:',len(GEMS),'materials;',len(manifest['new_blocks']),'host-matched deposits;',len(outputs),'source-equal files')

if __name__=='__main__':main()
