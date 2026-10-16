"""A purely decorative elven cultural collection: 38 objects, 52 model parts.

Models and collision share geometry; two-part furniture is owned by one item.
Recipes use the installed Continuity Works vanilla content tool.
"""
import argparse
import json
from pathlib import Path
import sys
from gen_functional_elven_containers import cube,model
from model_geometry import clean_model

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'first_party_mods/alfheim_leyworks/src/main/resources'
JAVA=ROOT/'first_party_mods/alfheim_leyworks/src/main/java/com/continuityworks/leyworks'
NS='alfheim_leyworks'
SPECS={}
def add(name,title,kind,category,accent='green'):SPECS[name]=(title,kind,category,accent)
for n,t in [('sunleaf_medallion','Sunleaf Medallion'),('moonbranch_medallion','Moonbranch Medallion'),('warden_service_medal','Warden Service Medal'),('grovekeeper_medal','Grovekeeper Medal'),('fallen_star_medal','Fallen Star Medal'),('royal_honors_plaque','Royal Honors Plaque')]:add(n,t,'WALL','honors','blue' if 'moon' in n or 'star' in n else 'green')
for n,t,a in [('dreamwood_side_chair','Dreamwood Side Chair','green'),('moonvelvet_armchair','Moonvelvet Armchair','purple'),('leafback_high_chair','Leafback High Chair','green'),('royal_audience_chair','Royal Audience Chair','blue'),('moonvelvet_ottoman','Moonvelvet Ottoman','purple'),('braided_reed_ottoman','Braided Reed Ottoman','green')]:add(n,t,'FLOOR','seating',a)
add('spring_silk_sofa','Spring Silk Sofa','SOFA','seating','green');add('twilight_velvet_sofa','Twilight Velvet Sofa','SOFA','seating','purple')
for n,t in [('relic_display_cabinet','Relic Display Cabinet'),('arms_display_cabinet','Ceremonial Arms Cabinet'),('crystal_display_cabinet','Crystal Display Cabinet'),('ceremonial_display_cabinet','Court Regalia Cabinet')]:add(n,t,'TALL','display','purple')
for n,t in [('crystal_stag_trophy','Crystal Stag Trophy'),('fallen_golem_trophy','Fallen Golem Trophy'),('silverleaf_laurel_trophy','Silverleaf Laurel Trophy'),('regatta_sail_trophy','Regatta Sail Trophy')]:add(n,t,'FLOOR','trophy','blue')
for n,t in [('leafguard_shield_display','Leafguard Shield Display'),('moonward_shield_display','Moonward Shield Display'),('sunblade_sword_display','Sunblade Sword Display'),('crossed_elven_blades','Crossed Elven Blades')]:add(n,t,'WALL','arms','blue' if 'moon' in n else 'green')
for n,t,a in [('elven_knight_watch','Elven Knight of the Watch','blue'),('elven_knight_oath','Elven Knight of the Oath','green'),('elven_knight_mourning','Mourning Elven Knight','purple'),('goddess_renewal','Goddess of Renewal','green'),('goddess_moonlight','Goddess of Moonlight','blue'),('goddess_remembrance','Goddess of Remembrance','purple')]:add(n,t,'TALL','statue',a)
for n,t,k in [('ancestral_wall_relief','Ancestral Wall Relief','WALL'),('sunburst_wall_rosette','Sunburst Wall Rosette','WALL'),('moonwind_windchime','Moonwind Windchime','WALL'),('ceremonial_incense_stand','Ceremonial Incense Stand','FLOOR'),('elven_floor_harp','Elven Floor Harp','TALL'),('leafwoven_privacy_screen','Leafwoven Privacy Screen','TALL')]:add(n,t,k,'ornament','blue' if 'moon' in n else 'green')

TEXTURES={'wood':'botania:block/dreamwood_planks','log':'botania:block/dreamwood_log','gold':'minecraft:block/gold_block',
 'gem':'minecraft:block/amethyst_block','quartz':'minecraft:block/quartz_block_side','paper':'minecraft:block/birch_planks',
 'green':'minecraft:block/green_wool','purple':'minecraft:block/purple_wool','blue':'minecraft:block/light_blue_wool',
 'dark':'minecraft:block/polished_blackstone','glass':'minecraft:block/glass','leaf':'minecraft:block/moss_block'}

def geometry(name,part=0):
    title,kind,cat,accent=SPECS[name];e=[]
    def c(a,b,t):e.append(cube(a,b,t))
    def plinth():
        c([1,0,1],[15,1.5,15],'quartz');c([2,1.5,2],[14,3,14],'gold');c([3,3,3],[13,4,13],'quartz')
    def legs(top=5):
        for x in (2,12):
            for z in (2,12):c([x,0,z],[x+2,top,z+2],'log');c([x-.25,0,z-.25],[x+2.25,1,z+2.25],'gold')
    def leaf(x,y,z,w,h,texture='gold'):
        for a,b in (([x+w*.25,y,z],[x+w*.75,y+h,z+.5]),([x,y+h*.25,z],[x+w,y+h*.75,z+.5])):c(a,b,texture)
    def shield(x,y,z,w=8,h=11):
        c([x+1,y+2,z],[x+w-1,y+h,z+1],'gold');c([x+2,y,z],[x+w-2,y+2,z+1],'gold')
        c([x+2,y+2.5,z-.5],[x+w-2,y+h-1,z],accent)
        if 'moonward' in name:
            c([x+3,y+4,z-1],[x+4,y+9,z-.5],'quartz');c([x+4,y+3.5,z-1],[x+6,y+4.5,z-.5],'quartz');c([x+4,y+8.5,z-1],[x+6,y+9.5,z-.5],'quartz')
        else:leaf(x+3,y+4,z-1,w-6,4,'quartz')
    def sword(x,y,z):
        c([x,y+4,z],[x+1,y+12,z+.75],'quartz');c([x+.25,y+12,z],[x+.75,y+13,z+.75],'quartz')
        c([x-1.25,y+3,z-.25],[x+2.25,y+4,z+1],'gold');c([x+.1,y+.75,z],[x+.9,y+3,z+.75],'log');c([x-.1,y,z-.1],[x+1.1,y+1,z+.85],'gem')
    if kind=='SOFA':
        # The second block is local right (east in the north-facing model).
        c([0,2,2],[16,5,15],'wood');c([0,5,3],[16,7.5,12],accent)
        c([0,6,12],[16,12,15],accent);c([0,11.5,14],[16,13.5,16],'wood')
        c([0,12.5,13.5],[16,13,14],'gold')
        x=0 if part==0 else 13
        c([x,4,2],[x+3,10,14],'wood');c([x+.25,8,3],[x+2.75,10.5,12],accent)
        for z in (3,12):c([x+.5,0,z],[x+2.5,3,z+2],'log');c([x+.25,0,z-.25],[x+2.75,.75,z+2.25],'gold')
        for x in ((5,10) if part==0 else (3,8)):c([x,8,11.5],[x+3,10.5,12],accent)
    elif cat=='seating':
        legs();ottoman='ottoman' in name
        c([1,4,1],[15,6,15],'wood');c([2,6,2],[14,8,14],accent)
        if ottoman:
            c([1.5,7,2],[14.5,9,14],accent)
            if 'reed' in name:
                for x in (3,6,9,12):c([x,9,2],[x+.5,9.25,14],'wood')
                for z in (3,6,9,12):c([2,9.25,z],[14,9.5,z+.5],'paper')
            else:
                for x in (4,8,12):c([x,8.75,7],[x+.5,9.25,7.5],'gold')
        else:
            c([1,5,13],[3,14,15],'log');c([13,5,13],[15,14,15],'log')
            c([3,8,13],[13,13,15],accent);c([2,13,13],[14,14,15],'gold')
            if 'side_chair' not in name:
                for x in (1,13):c([x,6,3],[x+2,10,5],'log');c([x,9,3],[x+2,10.5,14],'wood')
            if 'leafback' in name:leaf(5,12,12,6,4)
            elif 'royal' in name:
                c([4,14,13],[12,15,15],'quartz');leaf(6,13,12,4,3,'gem')
            else:c([6,11,12.5],[10,12,13],'gold')
    elif cat=='display':
        c([1,0,2],[15,2,15],'wood');c([1,14.5,2],[15,16,15],'gold')
        c([1,2,2],[3,14.5,15],'wood');c([13,2,2],[15,14.5,15],'wood');c([3,2,13.5],[13,14.5,15],'log')
        c([3,7.5,3],[13,8.5,13.5],'quartz')
        c([3,2,2.5],[13,14.5,2.75],'glass')
        for x in (2,13):c([x,2,1.75],[x+1,14.5,2.25],'gold')
        c([7,7,1.5],[9,9,2.25],'gem')
        if name.startswith('crystal'):
            for x,y in ((4,2),(9,8.5)):
                c([x,y,6],[x+2,y+4,9],'gem');c([x+.5,y+4,6.5],[x+1.5,y+5,8.5],'blue')
        elif name.startswith('arms'):
            if part==1:shield(4,2,5,8,11)
            else:sword(7,1,6)
        elif name.startswith('relic'):
            for y in (2,8.5):
                c([5,y,5],[11,y+1,11],'quartz');c([6,y+1,6],[10,y+4,10],'gem');c([7,y+4,7],[9,y+5,9],'gold')
        else:
            for y in (2,8.5):
                c([5,y,6],[11,y+1,10],'gold')
                for x in (5,7.5,10):c([x,y+1,7],[x+1,y+3,9],'gold')
    elif cat=='statue':
        if part==0:
            plinth()
            if name.startswith('goddess'):
                for y,inset in ((4,2),(7,3),(10,4),(13,5)):c([inset,y,4],[16-inset,y+3,12],'quartz')
                c([7,4,3.5],[9,16,4],'gold')
                for x in (3,11):c([x,4,12],[x+2,16,13],accent)
            else:
                for x in (4,9):c([x,4,5],[x+3,7,11],'dark');c([x,7,6],[x+3,15,10],'quartz');c([x-.25,10,5.75],[x+3.25,12,10.25],'gold')
                c([3,14,5],[13,16,11],'quartz');c([4,5,11],[12,16,12],accent)
                if 'oath' in name:c([7.5,4,3],[8.5,16,4],'quartz')
                elif 'watch' in name:c([12,5,4],[13,16,5],'quartz')
        else:
            mourning='mourning' in name;head_y=5 if mourning else 8
            c([4,0,5],[12,5,11],'quartz');c([3,4,5],[13,6,11],'gold');c([4,0,11],[12,7,12],accent)
            c([5,head_y,5],[11,head_y+5,11],'quartz')
            # Angular ears and separated relief eyes establish an elven silhouette.
            c([3.5,head_y+2,7],[5,head_y+3,9],'quartz');c([11,head_y+2,7],[12.5,head_y+3,9],'quartz')
            for x in (6,9):c([x,head_y+2.5,4.75],[x+1,head_y+3,5],'dark')
            c([7.5,head_y+1,4.5],[8.5,head_y+2.5,5],'quartz')
            if name.startswith('goddess'):
                c([4.5,head_y,10.5],[11.5,15,12],'quartz');c([5,head_y+5,5],[11,head_y+6,11],'gold')
                for x in (5,7.5,10):c([x,head_y+5.5,6],[x+1,15.5,8],'gold')
                c([2,0,6],[4,6,10],'quartz');c([12,0,6],[14,6,10],'quartz')
                if 'renewal' in name:
                    c([12.75,1,3],[13.5,12,3.75],'wood');leaf(11.5,10,2.5,4,4,'leaf')
                elif 'moonlight' in name:
                    c([1.5,6,3],[2.5,13,4],'gem');c([2.5,5,3],[5,6.5,4],'gem');c([2.5,12,3],[5,13.5,4],'gem')
                else:
                    c([5,1,2],[11,4,5],'paper');c([4.5,.5,2],[11.5,1,5.5],'gold');c([7.75,1,1.75],[8.25,4,2],'dark')
            else:
                c([4.5,head_y+4,4.5],[11.5,head_y+5.5,11.5],'gold')
                c([3,1,6],[5,6,10],'quartz');c([11,1,6],[13,6,10],'quartz')
                if 'watch' in name:shield(1,0,3,7,9);c([12,0,4],[13,8,5],'quartz');c([11,5,3.5],[14,6,5.5],'gold')
                elif 'oath' in name:c([7.5,0,3],[8.5,10,4],'quartz');c([6,3,2.5],[10,4,4.5],'gold');c([6,1,2],[10,2,4],'quartz')
                else:c([5,0,2],[11,2,5],'quartz');c([7.5,2,2.5],[8.5,7,3.5],'gold')
    elif cat=='honors':
        c([2,1,14.5],[14,15,16],'wood')
        for x in (2,13):c([x,1,14],[x+1,15,14.5],'gold')
        c([3,13,14],[13,14,14.5],'gold');c([5,9,13.5],[7,13,14],accent);c([9,9,13.5],[11,13,14],accent)
        for inset,y0,y1 in ((2,5,9),(3,4,10),(4,3,11)):c([inset+2,y0,12.75],[14-inset,y1,13.5],'gold')
        if 'moonbranch' in name:
            c([5.5,5,12.25],[6.5,9,12.75],'gem');c([6.5,4.5,12.25],[9.5,5.5,12.75],'gem');c([6.5,8.5,12.25],[9.5,9.5,12.75],'gem');leaf(8,5.5,12,2,2,'quartz')
        elif 'service' in name:
            c([7.5,4,12],[8.5,10,12.75],'quartz');c([5.5,6,11.75],[10.5,7,12.25],'quartz');c([7.75,10,12],[8.25,11,12.75],'gem')
        elif 'grovekeeper' in name:
            for x,y in ((5,6),(9,6),(7,4),(7,8)):leaf(x,y,12,2,2,'quartz')
            c([7,6,11.75],[9,8,12.25],'leaf')
        elif 'fallen_star' in name:
            c([7,4,12],[9,10,12.75],'gem');c([5,6,12],[11,8,12.75],'gem')
            for x,y in ((5,4),(10,4),(5,9),(10,9)):c([x,y,12.25],[x+1,y+1,12.75],'quartz')
        elif 'plaque' in name:
            for x in (5,7.5,10):c([x,6,12],[x+1,9,12.75],'gem')
            for x in (4,7,10):c([x,2,13.5],[x+2,2.5,14],'quartz')
        else:leaf(6,5,12.25,4,4,'quartz')
    elif cat=='arms':
        c([2,1,15],[14,15,16],'log')
        if 'shield' in name:shield(3,2,13,10,12)
        elif 'crossed' in name:
            for i in range(10):
                c([3+i*.8,3+i,13],[4+i*.8,4+i,14],'quartz');c([12-i*.8,3+i,12],[13-i*.8,4+i,13],'quartz')
            c([2,3,12.5],[6,4,14.5],'gold');c([10,3,11.5],[14,4,13.5],'gold')
        else:sword(7.5,1,13)
    elif cat=='trophy':
        plinth();c([6,4,6],[10,6,10],'dark')
        if 'stag' in name:
            c([5,6,5],[11,10,11],'quartz');c([6,7,3],[10,9,5],'quartz')
            for x in (3,11):
                c([x,9,7],[x+2,14,9],'gold');c([x-1,12,7],[x+3,13,9],'gold');c([x,14,7.25],[x+1,16,8.75],'gem')
        elif 'golem' in name:
            c([4,6,4],[12,12,12],'gem');c([3,8,5],[5,11,10],'dark');c([5,8,3],[11,10,4],'dark');c([6,9,2.75],[10,9.5,3],'blue')
            c([8,12,6],[11,14,10],'gem')
        elif 'laurel' in name:
            c([7.5,6,7],[8.5,9,9],'gold')
            for x,y in ((3,9),(3.5,12),(5,14),(10,14),(11.5,12),(12,9)):leaf(x,y-1,7,2,2,'quartz')
        else:
            c([7.5,6,8],[8.5,16,9],'wood')
            for y in range(7,15):c([8.5,y,7],[8.5+(15-y)*.65,y+1,8],'paper')
            c([3,6,6],[13,7,10],'gold')
    elif name=='elven_floor_harp':
        if part==0:
            plinth();c([2,4,6],[4,16,10],'wood');c([12,4,6],[14,16,10],'wood')
            for x in (5,7,9,11):c([x,5,7.75],[x+.25,16,8],'gold')
        else:
            c([2,0,6],[4,11,10],'wood');c([12,0,6],[14,8,10],'wood');c([3,9,6],[13,12,10],'gold')
            for x in (5,7,9,11):c([x,0,7.75],[x+.25,10,8],'gold')
            leaf(6,10,5,4,5,'gem')
    elif name=='leafwoven_privacy_screen':
        for x in (1,13):c([x,0,7],[x+2,16,9],'log')
        c([3,1,7.5],[13,15,8.5],accent)
        for y in (2,7,12):leaf(6,y,7,4,3,'gold')
        if part==0:
            for x in (0,12):c([x,0,4],[x+4,1.5,12],'wood')
        else:c([2,15,6.75],[14,16,9.25],'gold')
    elif name=='ceremonial_incense_stand':
        plinth();c([6,4,6],[10,11,10],'wood');c([3,11,3],[13,12,13],'gold')
        for x in (4,11):c([x,12,4],[x+1,15,12],'quartz')
        c([5,12,5],[11,13,11],'dark');c([6,13,6],[10,14,10],'gem')
    elif name=='moonwind_windchime':
        c([2,13,14],[14,15,16],'wood')
        for i,x in enumerate((3,6,9,12)):
            c([x,7-i,14],[x+.25,13,14.25],'gold');c([x-.5,4-i,13],[x+1,7-i,15],'gem')
    else:
        c([1,1,15],[15,15,16],'quartz')
        if name=='ancestral_wall_relief':
            c([5,8,14],[11,13,15],'gold');c([7,4,13.5],[9,9,14],'gold');c([4,2,13.5],[12,4,14],'gold');leaf(2,5,14,3,6,'leaf');leaf(11,5,14,3,6,'leaf')
        else:
            for x,y in ((7,2),(7,11),(2,7),(11,7)):leaf(x,y,14,3,3)
            c([5,5,13],[11,11,14],'gold');c([6,6,12.5],[10,10,13],'gem')
    return e

def build():
    sys.path.insert(0,'C:/GITS/Structuresmith/StructureSmith/src');from structure_capability import StructureCapability
    cap=StructureCapability(project_root=ROOT,state_root=ROOT/'build/elven-decor/snapshots')
    out={};manifest={};translations={};gates=[]
    def emit(path,data):out[path]=data if isinstance(data,bytes) else (json.dumps(data,indent=2)+'\n').encode()
    java=['package com.continuityworks.leyworks;','// Generated by tools/gen_elven_decor.py.','import java.util.List;','import net.minecraft.world.level.block.Block;','import net.minecraft.world.phys.shapes.Shapes;','import net.minecraft.world.phys.shapes.VoxelShape;','final class ElvenDecorDefinitions {','    record Definition(String id,ElvenDecorBlock.Kind kind,VoxelShape base,VoxelShape extension) {}','    static List<Definition> all() { return List.of(']
    dyes={'green':'minecraft:green_dye','purple':'minecraft:purple_dye','blue':'minecraft:light_blue_dye'}
    for index,(name,(title,kind,category,accent)) in enumerate(SPECS.items()):
        key='decor_'+name;rid=NS+':'+key;parts=2 if kind in ('TALL','SOFA') else 1;models=[];shapes=[]
        for part in range(parts):
            elements=geometry(name,part)
            doc=clean_model({'parent':'minecraft:block/block','textures':dict(TEXTURES,particle=TEXTURES['quartz' if category=='statue' else 'wood']),'elements':elements})
            for box in elements:assert all(0<=a<b<=16 for a,b in zip(box['from'],box['to'])),(name,part,box)
            mk=key+('_extension' if part else '')
            emit(f'assets/{NS}/models/block/{mk}.json',doc)
            models.append({'model':mk,'source_boxes':elements,'elements':len(doc['elements'])})
            shapes.append('Shapes.or(Shapes.empty(), '+', '.join('Block.box('+', '.join(str(v)+'D' for v in e['from']+e['to'])+')' for e in elements)+')')
        java.append(f'        new Definition("{key}",ElvenDecorBlock.Kind.{kind},{shapes[0]},{shapes[-1]})'+(',' if index<len(SPECS)-1 else ''))
        variants={}
        for facing,y in [('north',0),('east',90),('south',180),('west',270)]:
            for part in ('base','extension'):
                variants[f'facing={facing},part={part}']={'model':NS+':block/'+key+('_extension' if part=='extension' and parts==2 else ''),'y':y}
        emit(f'assets/{NS}/blockstates/{key}.json',{'variants':variants})
        if parts==2:
            from copy import deepcopy
            combined=[]
            axis=1 if kind=='TALL' else 0
            for part in range(2):
                for element in geometry(name,part):
                    el=deepcopy(element)
                    for bound in ('from','to'):
                        coords=el[bound];coords[axis]+=part*16
                        el[bound]=[v*.5+(0 if i==axis else 4) for i,v in enumerate(coords)]
                    combined.append(el)
            emit(f'assets/{NS}/models/item/{key}.json',clean_model({'parent':'minecraft:block/block','textures':dict(TEXTURES,particle=TEXTURES['wood']),'elements':combined}))
        else:emit(f'assets/{NS}/models/item/{key}.json',{'parent':NS+':block/'+key})
        conditions=[{'condition':'minecraft:survives_explosion'}]
        if parts==2:conditions.append({'condition':'minecraft:block_state_property','block':rid,'properties':{'part':'base'}})
        emit(f'data/{NS}/loot_tables/blocks/{key}.json',{'type':'minecraft:block','pools':[{'rolls':1,'conditions':conditions,'entries':[{'type':'minecraft:item','name':rid}]}]})
        # One unique dye pair per object avoids otherwise identical decorative recipes.
        dye_names=['white','orange','magenta','light_blue','yellow','lime','pink','gray','light_gray','cyan','purple','blue','brown','green','red','black']
        request={'target_version':'1.20.1','recipe_id':rid,'type':'crafting_shaped','pattern':['ABA','CDC','AEA'],
            'key':{'A':{'item':'botania:livingrock' if category in ('statue','trophy') else 'botania:dreamwood'},
                   'B':{'item':'minecraft:'+dye_names[index%16]+'_dye'},'C':{'item':'minecraft:'+dye_names[index//16]+'_dye'},
                   'D':{'item':'botania:elf_quartz'},'E':{'item':'minecraft:'+('white_wool' if category=='seating' else 'glass' if category=='display' else 'gold_nugget')}},
            'result':{'item':rid},'id_policy':'namespace'}
        result=cap.minecraft_recipe_generate(request);assert result['materialization_allowed'],result
        emit(f'data/{NS}/recipes/{key}.json',result['json']);gates.append({'id':rid,'gate':result['gate']})
        tip='Decorative wall ornament.' if kind=='WALL' else 'Two-block decorative sofa; place from either facing.' if kind=='SOFA' else 'Two-block decorative statue.' if category=='statue' else 'Fixed ornaments behind glass.' if category=='display' else 'Decorative furnishing.'
        translations[f'block.{NS}.{key}']=title;translations[f'tooltip.{NS}.{key}']=tip
        manifest[key]={'id':rid,'name':title,'kind':kind,'category':category,'accent':accent,'parts':models,'recipe':result['json']}
    java+=['    ); }','    private ElvenDecorDefinitions() {}','}']
    emit('JAVA/ElvenDecorDefinitions.java','\n'.join(java).encode()+b'\n')
    emit('TRANSLATIONS',translations)
    emit('MANIFEST',{'objects':manifest,'recipes':gates,'capability':'Continuity Works minecraft_recipe_generate / Java 1.20.1','semantics':'pure scenery; fixed display contents; no inventories, equipment, buffs, sit entities or tickers'})
    for typ in ('blocks','items'):emit(f'data/{NS}/tags/{typ}/elven_decor.json',{'replace':False,'values':[o['id'] for o in manifest.values()]})
    commands=['# Player-invoked decorative review gallery; use clear space (30 by 18, two high).']
    for i,(name,(_,kind,_,_)) in enumerate(SPECS.items()):
        x,z=i%8*4,i//8*4;rid=NS+':decor_'+name
        commands.append(f'setblock ~{x} ~-1 ~{z} botania:livingrock')
        if kind=='WALL':commands.append(f'setblock ~{x} ~ ~{z+1} botania:livingrock')
        if kind=='SOFA':commands.append(f'setblock ~{x+1} ~-1 ~{z} botania:livingrock')
        commands.append(f'setblock ~{x} ~ ~{z} {rid}[facing=north,part=base]')
        if kind=='TALL':commands.append(f'setblock ~{x} ~1 ~{z} {rid}[facing=north,part=extension]')
        if kind=='SOFA':commands.append(f'setblock ~{x+1} ~ ~{z} {rid}[facing=north,part=extension]')
    emit(f'data/{NS}/functions/elven_decor/review.mcfunction',('\n'.join(commands)+'\n').encode())
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();output=build()
    for rel,data in output.items():
        path=JAVA/rel[5:] if rel.startswith('JAVA/') else ROOT/'tools/elven_decor_manifest.json' if rel=='MANIFEST' else ROOT/'tools/elven_decor_translations.json' if rel=='TRANSLATIONS' else RES/rel
        if args.check:assert path.exists() and path.read_bytes()==data,rel
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    lang_path=RES/f'assets/{NS}/lang/en_us.json';lang=json.loads(lang_path.read_text());new=json.loads(output['TRANSLATIONS'])
    if args.check:assert all(lang.get(k)==v for k,v in new.items())
    else:lang.update(new);lang_path.write_text(json.dumps(lang,indent=2)+'\n')
    print('ELVEN DECOR:',len(SPECS),'objects,',sum(2 if s[1] in ('TALL','SOFA') else 1 for s in SPECS.values()),'model parts')
