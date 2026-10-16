"""Purpose-built district furnishings: native utility with shared visible/collision geometry."""
import argparse
import json
from pathlib import Path
import sys
from gen_functional_elven_containers import cube, model, TEXTURES
from model_geometry import clean_model

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'first_party_mods/alfheim_leyworks/src/main/resources'
JAVA=ROOT/'first_party_mods/alfheim_leyworks/src/main/java/com/continuityworks/leyworks'
NS='alfheim_leyworks'
SPECS={
 'seed_cabinet': ('Living Seed Cabinet',27,'agricultural_estate','minecraft:wheat_seeds','Stores 27 stacks; hopper access and comparator fullness.'),
 'apothecary_cabinet': ('Apothecary Cabinet',18,'relief_district','minecraft:glass_bottle','Stores 18 stacks of remedies, ingredients and field supplies.'),
 'armory_locker': ("Warden's Armory Locker",54,'military_warden','minecraft:leather','Stores 54 stacks of expedition equipment and supplies.'),
 'provision_hutch': ('Provision Hutch',27,'common_residential','minecraft:bread','Stores 27 stacks of settlement provisions.'),
 'archive_cabinet': ("Scholar's Archive Cabinet",54,'scholastic_quarter','minecraft:book','Stores 54 stacks; accepts books, maps and other ordinary items.'),
 'market_counter': ('Tradehall Service Counter',27,'roads_trade','minecraft:paper','Stores 27 stacks with hopper access and comparator fullness.'),
 'artificer_desk': ("Artificer's Workdesk",'CRAFT','production_district','minecraft:crafting_table','Opens a 3 by 3 crafting grid for existing crafting recipes.'),
 'masons_bench': ("Livingrock Mason's Bench",'STONECUT','production_district','minecraft:stonecutter','Cuts stone using existing stonecutting recipes.'),
 'weaving_frame': ('Dreamwood Weaving Frame','LOOM','common_residential','minecraft:loom','Patterns banners using the ordinary loom interface and dye costs.'),
 'cartographers_table': ("Frontier Cartographer's Table",'CARTOGRAPHY','frontier_stewardship','minecraft:cartography_table','Copies, scales and locks maps with the ordinary cartography interface.'),
 'mending_bench': ("Warden's Mending Bench",'GRINDSTONE','military_warden','minecraft:grindstone','Repairs compatible equipment and removes ordinary enchantments like a grindstone.'),
}

def geometry(name):
    e=[]
    def c(a,b,t):e.append(cube(a,b,t))
    def legs(height=11):
        for x in (1,12):
            for z in (2,12):
                c([x,0,z],[x+3,height,z+2],'log')
                c([x-.25,0,z-.25],[x+3.25,1,z+2.25],'gold')
    def table():
        legs();c([0,11,1],[16,13,15],'wood')
        c([0,12,0],[16,13,1],'gold');c([0,12,15],[16,13,16],'gold')
        c([0,12,1],[1,13,15],'gold');c([15,12,1],[16,13,15],'gold')
        c([3,4,12],[13,5,14],'wood')
    def cabinet():
        c([1,0,2],[15,2,15],'log');c([1,14,2],[15,16,15],'wood')
        c([1,2,13],[15,14,15],'log');c([1,2,2],[3,14,13],'wood');c([13,2,2],[15,14,13],'wood')
        c([1,1,1],[15,2,2],'gold');c([1,14,1],[15,15,2],'gold')
        c([1,2,1],[2,14,2],'gold');c([14,2,1],[15,14,2],'gold')
        c([3,7,3],[13,8,13],'wood')
    if name=='market_counter':
        table();c([2,1,6],[14,10,14],'wood');c([2,4,5],[14,5,6],'gold')
        for x in (3,7,11):c([x,6,4],[x+2,9,6],'paper');c([x+.5,7,3.5],[x+1.5,8,4],'gem')
        c([3,13,3],[10,13.5,9],'paper');c([12,13,5],[14,15,8],'gold')
    elif name in ('seed_cabinet','apothecary_cabinet','armory_locker','provision_hutch','archive_cabinet'):
        cabinet()
        if name=='seed_cabinet':
            for x in (3.5,8.5):
                for y in (2.5,8.5):
                    c([x,y,3],[x+4,y+4.5,12],'wood');c([x+.5,y+.5,2],[x+3.5,y+3.5,3],'green')
                    c([x+1.25,y+1.75,1.5],[x+2.75,y+2.5,2],'gold')
        elif name=='apothecary_cabinet':
            for x in (4,8,11):
                for y in (2,8):
                    c([x,y,5],[x+1.75,y+3,8],'gem' if x==8 else 'green')
                    c([x+.5,y+3,5.75],[x+1.25,y+4,7.25],'quartz')
                    c([x+.25,y+4,5.5],[x+1.5,y+4.5,7.5],'gold')
        elif name=='armory_locker':
            c([3,3,4],[13,13,6],'dark')
            for x in (4,10):
                c([x,5,2],[x+1,12,3],'quartz');c([x-.75,4,1.5],[x+1.75,5,3.5],'gold')
                c([x+.25,2.5,2.25],[x+.75,4,2.75],'wood')
            c([7,7,1],[9,10,3],'gem')
        elif name=='provision_hutch':
            for x in (3.5,8.5):
                for y in (2,8):
                    c([x,y,4],[x+4,y+1,12],'wood')
                    for z in (5,8):c([x+.25,y+1,z],[x+3.75,y+3,z+2],'green' if y==8 else 'paper')
            c([5,15,4],[11,16,9],'quartz')
        else:
            for row in (2,8):
                for i,x in enumerate((3.5,5.5,7.5,9.5,11.5)):
                    height=3.5+(i%3)*.5
                    c([x,row,3.5],[x+1.25,row+height,10],'green' if i%2 else 'paper')
                    c([x,row+.75,3],[x+1.25,row+1.25,3.5],'gold')
    else:
        table()
        if name=='artificer_desk':
            c([2,13,3],[10,13.5,10],'paper')
            for x in (3,5,7):c([x,13.5,4],[x+.25,13.75,9],'dark')
            for z in (5,7,9):c([2.5,13.5,z],[9,13.75,z+.25],'dark')
            c([11,13,5],[14,15,8],'quartz');c([12,15,6],[13,16,7],'gem')
        elif name=='masons_bench':
            c([2,13,3],[14,14,13],'quartz')
            for x,y,z,X,Y,Z in ((5,14,6,11,15,10),(6,15,6,10,16,10),(4,13,7,5,15,9),(11,13,7,12,15,9)):
                c([x,y,z],[X,Y,Z],'dark')
            c([2,14,3],[4,15,5],'gold');c([12,14,11],[14,15,13],'gem')
        elif name=='weaving_frame':
            # Low horizontal hand loom, its threads and shuttle visible from above.
            for x in (2,13):c([x,13,3],[x+1,16,13],'log')
            for z in (3,12):c([3,14,z],[13,15,z+1],'gold')
            for x in (4,6,8,10,12):c([x,14,4],[x+.25,14.25,12],'paper')
            for z in (5,7,9):c([3,14.5,z],[13,14.75,z+.5],'green')
            c([6,15,8],[10,15.5,9],'gem')
        elif name=='cartographers_table':
            c([2,13,3],[12,13.25,12],'paper')
            for a,b in (([3,13.25,5],[8,13.5,6]),([6,13.25,6],[7,13.5,10]),([8,13.25,8],[11,13.5,10])):c(a,b,'green')
            for x in (2,11):c([x,13,2],[x+1,15,13],'quartz')
            c([13,13,4],[15,14,7],'gold');c([13.5,14,4.5],[14.5,15,6.5],'gem')
        else:
            for x in (3,11):c([x,13,5],[x+2,15,11],'log')
            c([5,13,5],[11,15,11],'dark');c([6,15,6],[10,16,10],'quartz')
            c([2,13,2],[7,14,3],'gold');c([2,13,2],[3,15,5],'dark')
    return e

def build():
    sys.path.insert(0,'C:/GITS/Structuresmith/StructureSmith/src')
    from structure_capability import StructureCapability
    cap=StructureCapability(project_root=ROOT,state_root=ROOT/'build/district-furnishings/snapshots')
    out={};manifest={};gates=[]
    def emit(rel,data):out[rel]=data if isinstance(data,bytes) else (json.dumps(data,indent=2)+'\n').encode()
    shapes=['package com.continuityworks.leyworks;','// Generated by tools/gen_district_furnishings.py.','import net.minecraft.world.level.block.Block;','import net.minecraft.world.phys.shapes.Shapes;','import net.minecraft.world.phys.shapes.VoxelShape;','final class DistrictFurnishingShapes {']
    lang={}
    for name,(title,utility,district,anchor,tip) in SPECS.items():
        key='district_'+name;rid=NS+':'+key;elements=geometry(name)
        doc=clean_model(model(elements));emit(f'assets/{NS}/models/block/{key}.json',doc)
        emit(f'assets/{NS}/models/item/{key}.json',{'parent':NS+':block/'+key})
        emit(f'assets/{NS}/blockstates/{key}.json',{'variants':{f'facing={f}':{'model':NS+':block/'+key,'y':y} for f,y in [('north',0),('east',90),('south',180),('west',270)]}})
        emit(f'data/{NS}/loot_tables/blocks/{key}.json',{'type':'minecraft:block','pools':[{'rolls':1,'conditions':[{'condition':'minecraft:survives_explosion'}],'entries':[{'type':'minecraft:item','name':rid}]}]})
        is_storage=isinstance(utility,int)
        ingredients={'P':{'item':'botania:dreamwood'},'M':{'item':'alfheim:purified_titan_resin' if is_storage else 'botania:mana_powder'},'S':{'item':'ars_nouveau:source_gem'},'C':{'item':'minecraft:chest' if utility==54 else 'minecraft:barrel'} if is_storage else {'item':anchor},'D':{'item':anchor if is_storage else 'alfheim:tempered_war_lattice'}}
        result=cap.minecraft_recipe_generate({'target_version':'1.20.1','recipe_id':rid,'type':'crafting_shaped','pattern':['PMP','SCS','PDP'],'key':ingredients,'result':{'item':rid},'id_policy':'namespace'})
        assert result['materialization_allowed'],result
        emit(f'data/{NS}/recipes/{key}.json',result['json']);gates.append({'id':rid,'gate':result['gate']})
        lang[f'block.{NS}.{key}']=title;lang[f'tooltip.{NS}.{key}']=tip
        terms=[f'Block.box({", ".join(str(v)+"D" for v in e["from"]+e["to"])})' for e in elements]
        shapes.append(f'    static final VoxelShape {name.upper()} = Shapes.or(Shapes.empty(), '+', '.join(terms)+');')
        manifest[key]=dict(id=rid,title=title,utility=utility,district=district,tip=tip,model_elements=len(doc['elements']),source_boxes=elements)
    shapes+=['    private DistrictFurnishingShapes() {}','}']
    emit('JAVA/DistrictFurnishingShapes.java','\n'.join(shapes).encode()+b'\n')
    emit(f'assets/{NS}/lang/en_us.district.json',lang) # merged separately without replacing existing names
    for kind in ('blocks','items'):emit(f'data/{NS}/tags/{kind}/district_furnishings.json',{'replace':False,'values':[v['id'] for v in manifest.values()]})
    emit(f'data/{NS}/tags/blocks/mineable_district_furnishings.json',{'replace':False,'values':[v['id'] for v in manifest.values()]})
    # An additive conventional tag file named distinctly inside this mod's namespace.
    emit('data/minecraft/tags/blocks/mineable/axe.json',{'replace':False,'values':[v['id'] for v in manifest.values()]})
    commands=['# Player-invoked gallery; relative coordinates. Empty inventories, no free progression loot.']
    for i,key in enumerate(manifest):commands.append(f'setblock ~{i%6*3} ~ ~{i//6*3} {NS}:{key}[facing=north]')
    emit(f'data/{NS}/functions/district_furnishings/review.mcfunction',('\n'.join(commands)+'\n').encode())
    emit('MANIFEST',{'capability':'Continuity Works minecraft_recipe_generate / Java 1.20.1','objects':manifest,'crafting_gates':gates,'runtime_status':'separate Forge audit required'})
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();output=build()
    for rel,data in output.items():
        path=JAVA/rel[5:] if rel.startswith('JAVA/') else ROOT/'tools/district_furnishings_manifest.json' if rel=='MANIFEST' else RES/rel
        if args.check:assert path.exists() and path.read_bytes()==data,rel
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    # Minecraft only loads en_us.json, so merge owned keys into the established file.
    translations=json.loads(output[f'assets/{NS}/lang/en_us.district.json'])
    lang_path=RES/f'assets/{NS}/lang/en_us.json';lang=json.loads(lang_path.read_text())
    if args.check:assert all(lang.get(k)==v for k,v in translations.items())
    else:lang.update(translations);lang_path.write_text(json.dumps(lang,indent=2)+'\n')
    print('DISTRICT FURNISHINGS:',len(SPECS),'functional models;',len(output),'generated files')
