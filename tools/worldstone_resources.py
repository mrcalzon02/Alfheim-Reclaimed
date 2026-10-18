"""Gameplay resources emitted by the Worldstone CW provider; no native data guesses."""
import copy,io,json,zipfile
from PIL import Image

NATIVE='alfheim_companion:'
BLOCK_IDS=('worldstone_crystal','worldstone_heart','worldstone_fragment_ore','worldstone_small_bud','worldstone_medium_bud','worldstone_large_bud','worldstone_cluster')
ITEM_IDS=('worldstone_crystal','worldstone_heart','worldstone_fragment_ore','worldstone_cluster','worldstone_fragment','attuned_worldstone','worldstone_compass')
NAMES={'worldstone_crystal':'Budding Crimson Worldstone','worldstone_heart':'Radiant Worldstone Heart','worldstone_fragment_ore':'Worldstone Fragment Ore','worldstone_small_bud':'Small Worldstone Bud','worldstone_medium_bud':'Medium Worldstone Bud','worldstone_large_bud':'Large Worldstone Bud','worldstone_cluster':'Worldstone Crystal Cluster','worldstone_fragment':'Worldstone Fragment','attuned_worldstone':'Attuned Worldstone','worldstone_compass':'Worldstone Compass'}
RECIPE_IDS=('worldstone_compass','attuned_worldstone','divine_ore','godly_ore','legendary_stone','mythic_stone')
EXTERNAL=('minecraft:compass','botania:elementium_ingot','ars_nouveau:source_gem','alfheim:dawnglass_shard',
          'ars_nouveau:manipulation_essence','botania:rune_mana','mythicbotany:alfsteel_ingot','alfheim:rimebound_lattice',
          'alfheim:gravegilt_thread','alfheim:crown_filament','botania:gaia_ingot',
          'mmorpg:material/mining/3','mmorpg:material/mining/4','mmorpg:material/mining/5','mmorpg:stone/3','mmorpg:stone/4','mmorpg:stone/5')


def item(i):return {'item':i}


def apparatus(reagent,materials,result,count,cost):
    return {'type':'ars_nouveau:enchanting_apparatus','reagent':[item(reagent)],'pedestalItems':[item(i) for i in materials],
            'output':{'item':result,'count':count},'sourceCost':cost,'keepNbtOfReagent':False}


def recipes():
    return {
        'worldstone_compass':apparatus('minecraft:compass',
            ['botania:elementium_ingot']*2+['ars_nouveau:source_gem']*2+['alfheim:dawnglass_shard']*2+
            ['ars_nouveau:manipulation_essence','botania:rune_mana'],NATIVE+'worldstone_compass',1,6000),
        'attuned_worldstone':{'type':'mythicbotany:infuser','group':'alfheim_worldstone',
            'ingredients':[item(NATIVE+'worldstone_fragment')]*4+[item('mythicbotany:alfsteel_ingot')]*2+[item('alfheim:rimebound_lattice')]*2,
            'mana':600000,'fromColor':7864336,'toColor':16716064,'output':{'item':NATIVE+'attuned_worldstone','count':1}},
        'divine_ore':apparatus(NATIVE+'attuned_worldstone',
            ['alfheim:gravegilt_thread']+['mmorpg:material/mining/3']*2+['ars_nouveau:source_gem']*2,'mmorpg:material/mining/4',2,10000),
        'godly_ore':apparatus(NATIVE+'attuned_worldstone',
            ['alfheim:crown_filament']+['mmorpg:material/mining/4']*2+['ars_nouveau:source_gem']*2+['botania:gaia_ingot'],'mmorpg:material/mining/5',2,20000),
        'legendary_stone':apparatus(NATIVE+'attuned_worldstone',
            ['alfheim:gravegilt_thread']+['mmorpg:stone/3']*2+['ars_nouveau:source_gem']*2,'mmorpg:stone/4',2,10000),
        'mythic_stone':apparatus(NATIVE+'attuned_worldstone',
            ['alfheim:crown_filament']+['mmorpg:stone/4']*2+['ars_nouveau:source_gem']*2+['botania:gaia_ingot'],'mmorpg:stone/5',2,20000)
    }


def drop_table(name,count,fortune=False,silk=False):
    entry={'type':'minecraft:item','name':name,'functions':[{'function':'minecraft:set_count','count':count}]}
    if fortune:entry['functions'].append({'function':'minecraft:apply_bonus','enchantment':'minecraft:fortune','formula':'minecraft:ore_drops'})
    entry['functions'].append({'function':'minecraft:explosion_decay'})
    if silk:
        entry={'type':'minecraft:alternatives','children':[
            {'type':'minecraft:item','name':silk,'conditions':[{'condition':'minecraft:match_tool','predicate':{'enchantments':[{'enchantment':'minecraft:silk_touch','levels':{'min':1}}]}}]},entry]}
    return {'type':'minecraft:block','pools':[{'rolls':1,'entries':[entry]}]}


def resources(root,asset):
    data='kubejs/data/alfheim_companion/';out={}
    for name,h in (('worldstone_small_bud',4),('worldstone_medium_bud',7),('worldstone_large_bud',11),('worldstone_cluster',16)):
        faces={f:{'texture':'#cross','uv':[0,0,16,16],'tintindex':-1} for f in ('north','south')}
        elements=[]
        for angle in (45,-45):
            elements.append({'from':[8-h*.45,0,8],'to':[8+h*.45,h,8],
                'rotation':{'origin':[8,0,8],'axis':'y','angle':angle,'rescale':True},'shade':False,'faces':copy.deepcopy(faces)})
        out[asset+f'models/block/{name}.json']={'ambientocclusion':False,'textures':{'cross':'alfheim_companion:item/worldstone_fragment','particle':'alfheim_companion:block/worldstone_crimson'},'elements':elements}
        variants={}
        for facing,rotation in {'up':{},'down':{'x':180},'north':{'x':90},'south':{'x':90,'y':180},'west':{'x':90,'y':270},'east':{'x':90,'y':90}}.items():
            variants['facing='+facing]={'model':'alfheim_companion:block/'+name,**rotation}
        out[asset+f'blockstates/{name}.json']={'variants':variants}
        out[data+f'loot_tables/blocks/{name}.json']={'type':'minecraft:block','pools':[]}
    out[asset+'blockstates/worldstone_fragment_ore.json']={'variants':{'':{'model':'alfheim_companion:block/worldstone_fragment_ore'}}}
    out[asset+'models/block/worldstone_fragment_ore.json']={'parent':'minecraft:block/cube_all','textures':{'all':'alfheim_companion:block/worldstone_fragment_ore'}}
    for name in ('worldstone_fragment_ore','worldstone_cluster'):
        out[asset+f'models/item/{name}.json']={'parent':'alfheim_companion:block/'+name}
    for name in ('worldstone_fragment','attuned_worldstone'):
        out[asset+f'models/item/{name}.json']={'parent':'minecraft:item/generated','textures':{'layer0':'alfheim_companion:item/worldstone_fragment'}}
    with zipfile.ZipFile('C:/Users/Admin/curseforge/minecraft/Install/versions/1.20.1/1.20.1.jar') as z:
        compass=json.loads(z.read('assets/minecraft/models/item/compass.json'))
    # Vanilla predicates/models are reused with an explicitly registered custom angle function.
    out[asset+'models/item/worldstone_compass.json']=compass
    out[data+'loot_tables/blocks/worldstone_crystal.json']={'type':'minecraft:block','pools':[]}
    out[data+'loot_tables/blocks/worldstone_fragment_ore.json']=drop_table(NATIVE+'worldstone_fragment',{'type':'minecraft:uniform','min':1,'max':3},True,NATIVE+'worldstone_fragment_ore')
    out[data+'loot_tables/blocks/worldstone_cluster.json']=drop_table(NATIVE+'worldstone_fragment',4,True,NATIVE+'worldstone_cluster')
    for name,body in recipes().items():out['kubejs/data/alfheim/recipes/worldstone/'+name+'.json']=body
    for master,target,mode in (('shard_master.png','textures/item/worldstone_fragment.png','RGBA'),('ore_master.png','textures/block/worldstone_fragment_ore.png','RGB')):
        image=Image.open(root/'tools/worldstone_art'/master).convert(mode).resize((32,32),Image.Resampling.NEAREST)
        stream=io.BytesIO();image.save(stream,format='PNG');out[asset+target]=stream.getvalue()
    return out
