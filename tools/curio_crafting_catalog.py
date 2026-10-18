"""Shared acquisition policy for the already registered Guild Regalia."""
RANK_COSTS={
    'apprentice':{'frame_count':2,'material_count':1,'source_count':1,'symbol_count':1,'multiplier':1},
    'guild':{'frame_count':4,'material_count':2,'source_count':2,'symbol_count':2,'multiplier':2},
    'master':{'frame_count':6,'material_count':3,'source_count':4,'symbol_count':3,'multiplier':3},
}
FRAME_NAMES={'apprentice':'Quickened Palebloom','guild':'Elementium Core','master':'Rimebound Lattice'}
CLASS_SYMBOLS={
    'warrior':'alfheim:rootglass_shard','hunter':'alfheim:galeglass_shard',
    'sorcerer':'alfheim:emberglass_shard','shaman':'alfheim:rootglass_shard',
    'warlock':'alfheim:duskglass_shard','minstrel':'alfheim:dawnglass_shard',
}
PROFESSION_SYMBOLS={
    'mining':'minecraft:flint','farming':'minecraft:wheat','fishing':'minecraft:cod',
    'husbandry':'minecraft:leather','salvaging':'minecraft:bone',
    'gear_crafting':'minecraft:iron_ingot','enchanting':'minecraft:lapis_lazuli',
    'cooking':'minecraft:bread','alchemy':'minecraft:glass_bottle',
}
FAMILY_MATERIALS={'signet':('minecraft:gold_nugget',4),'emblem':('minecraft:string',2),'cuff':('minecraft:leather',2)}

def recipe_for(item,ranks):
    rank=ranks[item['rank']];cost=RANK_COSTS[item['rank']]
    material,num=FAMILY_MATERIALS[item['family']]
    symbols=CLASS_SYMBOLS if item['kind']=='class' else PROFESSION_SYMBOLS
    # Merge identical materials (e.g. a Wildward cuff's leather) before native matching.
    ingredients={}
    for iid,count in [(rank['frame'],cost['frame_count']),
                      (f"mmorpg:material/mining/{rank['profession_tier']}",cost['material_count']),
                      ('ars_nouveau:source_gem',cost['source_count']),
                      (symbols[item['owner']],cost['symbol_count']),
                      (material,num*cost['multiplier'])]:
        ingredients[iid]=ingredients.get(iid,0)+count
    ident='alfheim_regalia_'+item['id'].split(':')[1].replace('/','_')
    return {'exp':100+rank['profession_tier']*50,'id':ident,
            'mats':[{'type':'ITEM','id':iid,'num':count} for iid,count in ingredients.items()],
            'profession':'gear_crafting','requires_pinnacle_unlock':False,
            'result':item['id'],'result_num':1,'set_tier_nbt':False,'tier':rank['profession_tier']}

def acquisition_text(item):
    return (f"Craft at the Gear Crafting station using {FRAME_NAMES[item['rank']]}, "
            'Source Gems, profession materials and the listed reagents. '
            'Decorative regalia; class and profession attunement effects are not implemented.')
