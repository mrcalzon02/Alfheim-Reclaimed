"""CW-backed additive natural gem resources, host-matched deposits and organic finds."""
import hashlib,io,json,math,random,re,sys,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from gemstone_catalog import GEMS,POOLS,SOURCES
from gen_blooms import ore_hosts
from gemstone_art import master,accent,accent_color

ROOT=Path(__file__).resolve().parents[1]
ASSET='kubejs/assets/alfheim/'
DATA='kubejs/data/alfheim/'
STARTUP='kubejs/startup_scripts/30_real_gemstones.js'
WOODS=['alfheim:ashen_grove','alfheim:bloomfall_vale','alfheim:silverbark_wood','alfheim:rootfall','mythicbotany:dreamwood_forest','mythicbotany:golden_fields']
MARINE=['alfheim:alfheim_ocean','alfheim:mistbark_shore','alfheim:sporebank_shore','alfheim:tidewood_shore']
FRESHWATER=['alfheim:mana_fen','alfheim:decayed_mire','mythicbotany:alfheim_lakes']
BIOMES=sorted(['alfheim:'+p.stem for p in (ROOT/'kubejs/data/alfheim/worldgen/biome').glob('*.json')]+['mythicbotany:'+k for k in ('alfheim_plains','alfheim_hills','dreamwood_forest','golden_fields','alfheim_lakes')])
LOOKUP={g['id']:g for g in GEMS}

def png(im):
    stream=io.BytesIO();im.save(stream,format='PNG');return stream.getvalue()
def rgb(value):return tuple(bytes.fromhex(value))
def shade(c,k):return tuple(max(0,min(255,round(v*k))) for v in c)+(255,)
def overlay(pool):
    im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im);r=random.Random(pool['id']);gems=[LOOKUP[k] for k in pool['gems']]
    for i in range(7):
        x,y=r.randrange(1,14),r.randrange(1,14);c=rgb(gems[i%len(gems)]['color'])
        d.polygon([(x,y),(x+2,y-1),(min(15,x+3),y+1),(x+1,min(15,y+3)),(x-1,y+1)],fill=shade(c,.6))
        d.polygon([(x,y),(x+2,y),(x+1,y+2)],fill=shade(c,1.2));d.point((x,y),fill=shade(c,1.5))
    return im

def aquatic_texture(pool):
    c=rgb(pool['color']);im=Image.new('RGBA',(16,16));pixels=im.load()
    for y in range(16):
        for x in range(16):
            k=.82+.14*math.sin(math.hypot(x-8,y-16)*1.4)+.1*math.cos(x*.7)
            pixels[x,y]=shade((216,201,178) if 'pearl' in pool['id'] else c,k)
    return im

def hosts():
    rows=[{'key':h['id'].removesuffix('_livingrock'),'block':'alfheim:'+h['id'],'texture':'alfheim:block/'+h['id'],'name':h['name']} for h in ore_hosts()]
    rows += [{'key':'livingrock','block':'botania:livingrock','texture':'botania:block/livingrock','name':'Livingrock'},
             {'key':'stone','block':'minecraft:stone','texture':'minecraft:block/stone','name':'Stone'},
             {'key':'deepslate','block':'minecraft:deepslate','texture':'minecraft:block/deepslate','name':'Deepslate'}]
    return rows

def ore_model(texture,pool):
    sides=('north','south','east','west','up','down')
    return {'textures':{'particle':texture,'host':texture,'gem':'alfheim:block/gemstones/'+pool},'elements':[
        {'from':[0,0,0],'to':[16,16,16],'faces':{s:{'texture':'#host','cullface':s} for s in sides}},
        {'from':[-.01,-.01,-.01],'to':[16.01,16.01,16.01],'faces':{s:{'texture':'#gem','uv':[0,0,16,16],'cullface':s} for s in sides}}]}

def node_model(pool):
    elems=[]
    def cube(lo,hi):elems.append({'from':lo,'to':hi,'faces':{s:{'texture':'#node','uv':[0,0,16,16]} for s in ('north','south','east','west','up','down')}})
    if 'pearl' in pool:
        for x,z in ((1,2),(8,5),(3,10)):
            cube([x,0,z],[x+6,1,z+4]);cube([x+1,1,z],[x+5,2,z+4]);cube([x+2,2,z+1],[x+4,3,z+3])
    else:
        cube([6,0,6],[10,8,10]);cube([2,5,6],[8,8,9]);cube([2,5,6],[4,12,8]);cube([9,7,6],[14,10,9]);cube([12,7,6],[14,14,8]);cube([7,8,7],[9,16,9])
    return {'parent':'minecraft:block/block','textures':{'particle':'alfheim:block/gemstones/'+pool,'node':'alfheim:block/gemstones/'+pool},'elements':elems}

def display_resources():
    prefix='first_party_mods/alfheim_companion/src/main/resources/';asset=prefix+'assets/alfheim_companion/';out={}
    def js(path,value):out[path]=(json.dumps(value,indent=2)+'\n').encode()
    js(asset+'gemstone_displays.json',[dict({k:g[k] for k in ('id','name','item','color')},accent=accent_color(g)) for g in GEMS])
    elems=[]
    def cube(lo,hi,tex):elems.append({'from':lo,'to':hi,'faces':{s:{'texture':'#'+tex,'uv':[0,0,16,16]} for s in ('north','south','east','west','up','down')}})
    cube([1,0,1],[15,2,15],'dark');cube([2,2,2],[14,3,14],'stone');cube([4,3,4],[12,10,12],'stone');cube([3,10,3],[13,12,13],'gold');cube([1,12,1],[15,14,15],'stone');cube([2,14,2],[14,15,14],'velvet')
    cube([2.5,8,1],[13.5,11,1.5],'plaque')
    for x,z in ((2,2),(13,2),(2,13),(13,13)):cube([x,14,z],[x+1,26,z+1],'gold')
    cube([2,26,2],[14,27,14],'gold')
    for lo,hi in (([2,15,2],[14,26,2.1]),([2,15,13.9],[14,26,14]),([2,15,2],[2.1,26,14]),([13.9,15,2],[14,26,14]),([2,26,2],[14,26.1,14])):cube(lo,hi,'glass')
    textures={'particle':'alfheim:block/ivory_livingrock_bricks','stone':'alfheim:block/ivory_livingrock_bricks','dark':'minecraft:block/polished_deepslate','gold':'minecraft:block/gold_block','plaque':'minecraft:block/sandstone_top','velvet':'minecraft:block/blue_wool','glass':'minecraft:block/glass'}
    js(asset+'models/block/geologist_pedestal.json',{'parent':'minecraft:block/block','textures':textures,'elements':elems})
    js(asset+'blockstates/geologist_pedestal.json',{'variants':{f'facing={d}':{'model':'alfheim_companion:block/geologist_pedestal','y':a} for d,a in [('north',0),('east',90),('south',180),('west',270)]}})
    js(asset+'models/item/geologist_pedestal.json',{'parent':'alfheim_companion:block/geologist_pedestal'})
    # Separate icon layers keep the pedestal neutral while the native shader colours only its gem.
    plinth=Image.new('RGBA',(128,128));d=ImageDraw.Draw(plinth)
    d.polygon([(24,100),(64,89),(104,100),(102,115),(64,126),(26,115)],fill='#57616b');d.polygon([(40,76),(64,69),(88,76),(88,104),(64,111),(40,104)],fill='#d7d0bc');d.polygon([(17,69),(64,56),(111,69),(111,79),(64,93),(17,79)],fill='#ded8c9');d.line((18,79,64,92,110,79),fill='#a3a18c',width=3);d.rectangle((47,94,80,100),fill='#c7a855')
    out[asset+'textures/item/geologist_pedestal_base.png']=png(plinth)
    langpath=ROOT/(asset+'lang/en_us.json');lang=json.loads(langpath.read_text());lang['block.alfheim_companion.geologist_pedestal']='Geologist Display Pedestal';lang['item.alfheim_companion.geologist_pedestal']='Geologist Display Pedestal'
    for g in GEMS:
        sprite=master(g,128);sprite.thumbnail((60,60),Image.Resampling.LANCZOS);icon=Image.new('RGBA',(128,128));icon.alpha_composite(sprite,((128-sprite.width)//2,5))
        key=g['id']+'_display_pedestal';out[asset+f'textures/item/gem_displays/{key}.png']=png(icon)
        js(asset+f'models/item/{key}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'alfheim_companion:item/geologist_pedestal_base','layer1':'alfheim_companion:item/gem_displays/'+key}})
        lang['item.alfheim_companion.'+key]=g['name']+' Display Pedestal'
    js(asset+'lang/en_us.json',lang)
    js(prefix+'data/alfheim_companion/recipes/geologist_pedestal.json',{'type':'minecraft:crafting_shaped','pattern':['GGG','SNS','SSS'],'key':{'G':{'item':'minecraft:glass'},'S':{'item':'minecraft:smooth_stone'},'N':{'item':'minecraft:gold_nugget'}},'result':{'item':'alfheim_companion:geologist_pedestal'}})
    gallery=['# Operator preview only: 46x43-block grid; place in an empty prepared exhibition space.']
    for i,g in enumerate(GEMS):gallery.append(f'setblock ~{(i%16)*3} ~ ~{(i//16)*3} alfheim_companion:geologist_pedestal[facing=north]{{Sample:{{id:"{g["item"]}",Count:1b}}}}')
    out[DATA+'functions/debug/gemstone_gallery.mcfunction']=('\n'.join(gallery)+'\n').encode()
    return out

def build():
    out={};blocks=[];newitems=[];features=[];targets_used=set();basehosts=hosts()
    def js(path,value):out[path]=(json.dumps(value,indent=2)+'\n').encode()
    lines=['// GENERATED by tools/gen_gemstones.py. Additive natural gems; no existing items replaced.','StartupEvents.registry(\'item\', event => {']
    for g in GEMS:
        if not g['item'].startswith('alfheim:'):continue
        pool=POOLS[g['pool']];info=f"{pool['label']}. "+('Underwater find.' if pool['source'].startswith('aquatic') else f"Search between Y {pool['y'][0]} and {pool['y'][1]}.")
        lines.append(f"  event.create({json.dumps(g['item'])}).displayName({json.dumps(g['name'])}).texture('alfheim:item/gemstones/{g['id']}').tooltip({json.dumps(info)}).tag('forge:gems').tag('forge:gems/{g['id']}')")
        newitems.append(g['item']);out[ASSET+f'textures/item/gemstones/{g["id"]}.png']=png(master(g))
        textures={'layer0':'alfheim:item/gemstones/'+g['id']}
        if accent_color(g)!=g['color']:
            out[ASSET+f'textures/item/gemstones/{g["id"]}_accent.png']=png(accent(g));textures['layer1']='alfheim:item/gemstones/'+g['id']+'_accent'
        js(ASSET+f'models/item/gem_{g["id"]}.json',{'parent':'minecraft:item/generated','textures':textures})
    lines+=['})',"StartupEvents.registry('block', event => {"]
    for key,pool in POOLS.items():
        out[ASSET+f'textures/block/gemstones/{key}.png']=png(aquatic_texture(pool) if pool['source'].startswith('aquatic') else overlay(pool))
        # Weighted family finds are a gameplay pool, not a claim that all varieties co-occur.
        entries=[{'type':'minecraft:item','name':LOOKUP[g]['item'],'weight':LOOKUP[g]['weight']} for g in pool['gems']]
        js(DATA+f'loot_tables/gemstones/{key}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':entries}]})
        replacements=[]
        if pool['source'].startswith('aquatic'):
            variants=[{'key':'bed','block':None,'texture':None,'name':''}]
        elif pool['source'].startswith('woodland'):
            variants=[{'key':'bed','block':None,'texture':'minecraft:block/rooted_dirt' if key=='amber' else 'minecraft:block/coal_ore','name':''}]
        else:variants=basehosts
        for host in variants:
            block=f'alfheim:gem_{key}_{host["key"]}_deposit';stem=block.split(':')[1];blocks.append(block)
            model='gemstones/'+stem
            js(ASSET+f'models/block/{model}.json',node_model(key) if pool['source'].startswith('aquatic') else ore_model(host['texture'],key))
            js(ASSET+f'blockstates/{stem}.json',{'variants':{'':{'model':'alfheim:block/'+model}}})
            js(ASSET+f'models/item/{stem}.json',{'parent':'alfheim:block/'+model})
            name=((host['name']+' ') if host['name'] else '')+pool['label']
            line=f"  event.create('{block}').displayName({json.dumps(name)}).model('alfheim:block/{model}').soundType('stone').hardness(3.0).resistance(3.0).renderType('cutout').mapColor('#{pool['color']}').tagBoth('alfheim:gemstone_deposits')"
            if pool['source'].startswith('aquatic'):line+=".hardness(0.6).fullBlock(false).notSolid().noValidSpawns(true).box(0,0,0,16,4,16)"
            else:line+=".requiresTool(true).tagBlock('minecraft:mineable/pickaxe').tagBlock('minecraft:needs_iron_tool').tagBoth('forge:ores')"
            lines.append(line)
            js(DATA+f'loot_tables/blocks/{stem}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:alternatives','children':[
                {'type':'minecraft:item','name':block,'conditions':[{'condition':'minecraft:match_tool','predicate':{'enchantments':[{'enchantment':'minecraft:silk_touch','levels':{'min':1}}]}}]},
                {'type':'minecraft:loot_table','name':'alfheim:gemstones/'+key,'functions':[{'function':'minecraft:apply_bonus','enchantment':'minecraft:fortune','formula':'minecraft:ore_drops'},{'function':'minecraft:explosion_decay'}]}]}]}]})
            if host['block']:
                replacements.append({'target':{'predicate_type':'minecraft:block_match','block':host['block']},'state':{'Name':block}});targets_used.add(host['block'])
        node=blocks[-1];configured='gemstones/'+key;placed='gemstones/'+key
        if pool['source'].startswith('aquatic'):
            js(DATA+f'worldgen/configured_feature/{configured}.json',{'type':'minecraft:simple_block','config':{'to_place':{'type':'minecraft:simple_state_provider','state':{'Name':node}}}})
            bed=['minecraft:sand','minecraft:gravel','minecraft:clay','minecraft:dirt','minecraft:stone']+[h['block'] for h in basehosts if h['block'].startswith('alfheim:')]
            targets_used.update(bed)
            placement=[{'type':'minecraft:rarity_filter','chance':pool['rarity']},{'type':'minecraft:in_square'},{'type':'minecraft:heightmap','heightmap':'OCEAN_FLOOR_WG'},
                {'type':'minecraft:block_predicate_filter','predicate':{'type':'minecraft:all_of','predicates':[{'type':'minecraft:matching_fluids','fluids':['minecraft:water']},{'type':'minecraft:matching_blocks','offset':[0,-1,0],'blocks':bed}]}},{'type':'minecraft:biome'}]
            biomes=FRESHWATER if key=='freshwater_pearl' else MARINE;step='vegetal_decoration'
        else:
            if pool['source'].startswith('woodland'):
                matches=['minecraft:dirt','minecraft:rooted_dirt','minecraft:coarse_dirt','minecraft:podzol']
                if key=='jet':matches+=['minecraft:coal_ore','minecraft:deepslate_coal_ore']
                replacements=[{'target':{'predicate_type':'minecraft:block_match','block':b},'state':{'Name':node}} for b in matches];targets_used.update(matches)
            js(DATA+f'worldgen/configured_feature/{configured}.json',{'type':'minecraft:ore','config':{'size':4 if key!='quartz' else 6,'discard_chance_on_air_exposure':.1,'targets':replacements}})
            placement=[{'type':'minecraft:rarity_filter','chance':pool['rarity']},{'type':'minecraft:in_square'},{'type':'minecraft:height_range','height':{'type':'minecraft:uniform','min_inclusive':{'absolute':pool['y'][0]},'max_inclusive':{'absolute':pool['y'][1]}}},{'type':'minecraft:biome'}]
            biomes=WOODS if pool['source'].startswith('woodland') else BIOMES;step='underground_ores'
        js(DATA+f'worldgen/placed_feature/{placed}.json',{'feature':'alfheim:'+configured,'placement':placement})
        js(DATA+f'forge/biome_modifier/zz_gemstones_{key}.json',{'type':'forge:add_features','biomes':biomes,'features':'alfheim:'+placed,'step':step})
        features.append({'id':'alfheim:'+placed,'step':step,'biomes':biomes,'y':pool['y'],'rarity':pool['rarity'],'source':pool['source']})
    lines+=['})',''];out[STARTUP]='\n'.join(lines).encode()
    # Reused vanilla gem items keep their IDs and receive the same detailed art/tint treatment.
    for g in GEMS:
        if g['item'].startswith('minecraft:'):out['kubejs/assets/minecraft/textures/item/'+g['item'].split(':')[1]+'.png']=png(master(g))
    out.update(display_resources())
    js('kubejs/data/forge/tags/items/gems.json',{'replace':False,'values':sorted({g['item'] for g in GEMS})})
    js(DATA+'tags/items/real_world_gemstones.json',{'replace':False,'values':sorted({g['item'] for g in GEMS})})
    js(DATA+'tags/blocks/gemstone_deposits.json',{'replace':False,'values':blocks})
    manifest={'status':'SOURCE_GENERATED_RUNTIME_REQUIRED','gems':GEMS,'pools':POOLS,'features':features,'new_items':newitems,'new_blocks':blocks,'existing_host_blocks':sorted(targets_used),'sources':SOURCES,'scope':'Alfheim home-world biomes; additive to existing ores','exhaustiveness':'Broad natural-gem and organic-material baseline, not every historic trade synonym or mineral ever faceted','distribution':'gameplay Y bands and weighted deposit pools, not a simulation of real geology'}
    return out,manifest

class Provider:
    provider_id='alfheim_real_gemstones_v1';aliases=('alfheim_real_gemstones',)
    def __init__(self,stage,outputs,manifest):self.stage=stage;self.outputs=outputs;self.manifest=manifest
    def describe(self):return {'provider_id':self.provider_id,'aliases':list(self.aliases)}
    def generate(self,request,resolver):
        probes={}
        for key in self.manifest['existing_host_blocks']:probes[key]=resolver.probe(key,kind='block');assert probes[key]['level'] in ('exact','vanilla'),probes[key]
        for g in GEMS:
            if not g['item'].startswith('alfheim:'):probes[g['item']]=resolver.probe(g['item'],kind='item');assert probes[g['item']]['level'] in ('exact','vanilla')
        records=[];artifacts={}
        for rel,data in self.outputs.items():
            path=self.stage/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);records.append({'file':rel,'sha256':hashlib.sha256(data).hexdigest()});artifacts[rel.replace('/','_')]=data
        return {'provider_id':self.provider_id,'status':'GENERATED_NOT_VALIDATED','generated_layout':{'files':records,'registry_probes':probes,'gems':len(GEMS),'pools':len(POOLS),'new_block_count':len(self.manifest['new_blocks']),'new_item_count':len(self.manifest['new_items'])},'structure_artifact':{'format':'minecraft_datapack','piece_count':0},'artifact_bytes':artifacts}

def main():
    outputs,manifest=build()
    if '--check' in sys.argv:
        for rel,data in outputs.items():assert (ROOT/rel).read_bytes()==data,rel
        print('GEMSTONE SOURCE EQUALITY PASS',len(outputs),'files');return
    sys.path.insert(0,'C:/GITS/Structuresmith/StructureSmith/src')
    from structure_capability import StructureCapability
    stage=ROOT/'build/gemstones/generated';cap=StructureCapability(project_root=ROOT,state_root=stage/'snapshots')
    for kind in ('block','item'):cap.inventory.add_registry_ids(json.loads((ROOT/f'server/local/kubejs/export/registries/{kind}.json').read_text()),kind=kind)
    cap.register_generator(Provider(stage,outputs,manifest))
    result=cap.generate({'structure_id':'alfheim:real_world_gemstones','target_version':'1.20.1','grade':3,'purpose':{'kind':'natural_gemstone_resources','required_zones':['deep seams','middle-depth pockets','highland crystals','woodland fossil beds','aquatic organic gems']},'context':{'dimension':'mythicbotany:alfheim'},'generation':{'kind':'alfheim_real_gemstones','materialize_nbt':False}})
    for rel,data in outputs.items():path=ROOT/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    (ROOT/'tools/gemstone_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'tools/gemstone_generation.json').write_text(json.dumps({'capability':'Continuity Works','snapshot_id':result['snapshot']['snapshot_id'],'generation':result['generation'],'layout':result['generated_layout'],'new_registry_status':'KubeJS startup declarations generated; actual registration pending restart','ore_features_not_independent_structures':True},indent=2)+'\n')
    print(f'CW emitted {len(GEMS)} natural gem materials, {len(POOLS)} source pools, {len(manifest["new_blocks"])} host-matched deposits and {len(manifest["new_items"])} new items')

if __name__=='__main__':main()
