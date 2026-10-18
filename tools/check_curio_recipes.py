"""Audit acquisition coverage, costs and text for the existing Guild Regalia."""
import hashlib,json,re,sys
from gen_curio_recipes import ROOT,build
from curio_crafting_catalog import RANK_COSTS
import gen_process_tooltips

def main():
    out,recipes=build()
    catalog=json.loads((ROOT/'alfheim_reclaimed_design/curios/curio_suite_catalog.json').read_text(encoding='utf8'))
    items={i['id']:i for i in catalog['planned_items']};ranks={r['id']:r for r in catalog['ranks']}
    known=set(json.loads((ROOT/'server/local/kubejs/export/registries/item.json').read_text(encoding='utf8')))
    for rel,data in out.items():assert (ROOT/rel).read_bytes()==data,rel
    assert len(recipes)==63 and {r['result'] for r in recipes}==set(items)
    existing=[]
    for path in (ROOT/'kubejs/data').glob('*/mmorpg_profession_recipe/*.json'):
        recipe=json.loads(path.read_text(encoding='utf8'))
        if recipe.get('result') in items:existing.append(recipe)
    assert len(existing)==63 and len({r['result'] for r in existing})==63
    for recipe in existing:
        item=items[recipe['result']];rank=ranks[item['rank']]
        assert recipe['tier']==rank['profession_tier'] and recipe['profession']=='gear_crafting'
        assert not recipe['set_tier_nbt'] and recipe['result_num']==1
        mats=recipe['mats'];assert len({m['id'] for m in mats})==len(mats)
        assert all(m['id'] in known and m['num']>0 and m['type']=='ITEM' for m in mats)
        assert any(m['id']==rank['frame'] and m['num']==RANK_COSTS[item['rank']]['frame_count'] for m in mats)
        assert any(m['id']=='ars_nouveau:source_gem' for m in mats)
        assert not any(m['id'] in items for m in mats)
    text=(ROOT/'kubejs/startup_scripts/18_curios.js').read_text(encoding='utf8')
    assert len(re.findall(r'event.create\(',text))==63
    assert text.count('attunement effects are not implemented.')==63
    script,index=gen_process_tooltips.build()
    assert (ROOT/gen_process_tooltips.OUT).read_text(encoding='utf8')==script
    assert all(any('Gear Crafting station' in route for route in index[i]['from']) for i in items)
    report={'status':'SOURCE_AND_REGISTRY_AUDIT_PASS_RUNTIME_PENDING','native_recipes':63,
            'unique_regalia_outputs':63,'by_rank':{rank:sum(i['rank']==rank for i in items.values()) for rank in ranks},
            'profession_tiers':{r['id']:r['profession_tier'] for r in ranks.values()},
            'exactly_one_native_route_per_item':True,'all_ingredient_ids_resolved':True,
            'leaf_frame_and_source_reagent_required':True,'no_existing_accessories_consumed':True,
            'attunement_effects_added':False,
            'native_schema':'Mine and Slash 6.4.7 ProfessionRecipe, matching installed sharpening-stone and 480 custom armory recipes',
            'native_craft_output_checked':'Installed bytecode constructs result ItemStack directly; decorative result IDs supported',
            'runtime_pending':['Native recipe registry reload','Gear Crafting station display and representative rank transactions','Curios equip/client tooltip presentation'],
            'recipe_hashes':{rel:hashlib.sha256(data).hexdigest() for rel,data in out.items()}}
    (ROOT/'tools/curio_recipes_static_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print('PASS: all 63 regalia have one native recipe, known inputs, correct rank/frame/Source costs and acquisition text')

if __name__=='__main__':main()
