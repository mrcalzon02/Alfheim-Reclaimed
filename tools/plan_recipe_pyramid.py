"""Build a reviewable recipe-reduction proposal. Never writes to game data.

Selection is deterministic. Budgets are design constraints, not proof that a recipe can
be disabled. Every omitted output and every retained consumer without a selected supplier
is exported for migration review. Raw source IDs remain intact.
"""
from __future__ import annotations
import collections as C
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/recipe-pyramid'
SOURCE=ROOT/'build/recipe-tree/normalized_recipes.json'
sys.path.insert(0,str(ROOT/'tools'))
from gen_ladder import LADDER,chain_for
from player_text import WORKINGS,player_text

BUDGETS={'Foundation':600,'Leaf':600,'Song':400,'Campaign':200,'Wound':450,'Settlement':1000,'Support':300}
RESERVE=200
COLORS=['white','orange','magenta','light_blue','yellow','lime','pink','gray','light_gray','cyan','purple','blue','brown','green','red','black']
DECOR={'refurbished_furniture','cfm_wap','cozyhome','framedblocks','domum_ornamentum','mcwbridges','regions_unexplored'}
WOUND={'mmorpg','mmorpg_profession','dungeon_realm','knightquest','alfheim_companion'}
rows=[r for r in json.loads(SOURCE.read_text(encoding='utf-8')) if r['condition_status']!='disabled']
byid={r['id']:r for r in rows}
assert len(byid)==len(rows)
names={n['ref']:n['label'] for n in json.loads((ROOT/'build/recipe-tree/graph.json').read_text(encoding='utf-8'))['nodes'] if n['kind'] in ('item','tag')}

def pretty(i):return player_text(names.get(i,i.split(':')[-1].replace('_',' ').title()))
def outputs(r):return [i for i,n in r['outputs']]
def category(r):
    ns=r['id'].split(':')[0]
    if ns in ('minecolonies','structurize','domum_ornamentum') or ns in DECOR or r['id'].startswith(('alfheim:deepworks/','alfheim:void/','alfheim:war_salvage/','alfheim:worldstone/')):return 'Settlement'
    if ns in WOUND or any(i.startswith('alfheim:armory/') for i in outputs(r)):return 'Wound'
    if ns in ('botania','mythicbotany'):return 'Leaf'
    if ns=='ars_nouveau':return 'Song'
    if ns in ('alfheim','alfheim_leyworks','alfheim_golems'):return 'Campaign'
    if ns=='minecraft':return 'Foundation'
    return 'Support'

all_chain={}
chain_alias={}
retained_chain=set()
chain_plan=[]
stages={
  4:('sunbleached_floss','ars_nouveau:enchanting_apparatus','botania:runic_altar',['botania:dreamwood','botania:livingrock']),
  5:('raw_alloy_grit','botania:runic_altar','ars_nouveau:enchanting_apparatus',['mythicbotany:elementium_ore','ars_nouveau:source_gem']),
  6:('march_hide','feywild:fey_altar','botania:runic_altar',['minecraft:leather','botania:livingrock']),
  7:('scorched_filament','occultism:spirit_fire','ars_nouveau:enchanting_apparatus',['minecraft:blaze_powder','ars_nouveau:source_gem']),
  8:('frost_shard','ars_nouveau:imbuement','botania:runic_altar',['minecraft:prismarine_shard','botania:livingrock']),
  9:('ash_of_names','occultism:spirit_fire','ars_nouveau:enchanting_apparatus',['minecraft:bone','ars_nouveau:source_gem']),
  10:('heartwood_strand','mythicbotany:infuser','botania:terra_plate',['botania:dreamwood','ars_nouveau:source_gem'])}
previous='alfheim:verdant_filament'
for L in LADDER:
    era=L['era'];chain=['alfheim:'+i for i in chain_for(L)]
    precursor,first,second,reagents=stages[era];precursor='alfheim:'+precursor;finish='alfheim:'+L['tier']
    for i in chain:
        all_chain[i]=era
        if i not in (precursor,finish):chain_alias[i]=finish
    for out,ins,typ,role in [(precursor,[(previous,2),(reagents[0],1)],first,'prepare'),(finish,[(precursor,1),(reagents[1],1)],second,'bind')]:
        if first in ('occultism:spirit_fire','ars_nouveau:imbuement'):
            # These serializers have one input slot. Put doubling and the material
            # adjunct in the following multi-ingredient binding recipe instead.
            ins=[(previous,1)] if role=='prepare' else [(precursor,2),(reagents[0],1),(reagents[1],1)]
        retained_chain.add(out)
        old=next(r for r in rows if out in outputs(r) and r['id'].startswith(f'alfheim:era{era}/'))
        chain_plan.append(dict(id=old['id'],working=WORKINGS[era],output=out,output_count=1,inputs=[dict(item=i,count=n) for i,n in ins],recipe_type=typ,role=role,status='proposed; schema/resource costs and station access require validation',old_recipe_type=old['type']))
    previous=finish
early=['alfheim:living_fibre','alfheim:charged_fibre','alfheim:verdant_filament']
retained_chain.update(early)
for out in early:
    r=next(r for r in rows if out in outputs(r) and r['id'].startswith('alfheim:era3/'))
    chain_plan.insert(len([x for x in chain_plan if x['working']=='Verdant Grafting']),dict(id=r['id'],working='Verdant Grafting',output=out,output_count=1,inputs=r['inputs'],recipe_type=r['type'],role='bootstrap',status='retain current recipe',old_recipe_type=r['type']))
chain_byid={r['id']:r for r in chain_plan}

# Only the 77 generated ladder recipes plus the three early transformations comprise
# this count. Other recipes under alfheim:era3/ remain ordinary candidates.
old_chain_rows={r['id'] for r in rows if any(i in all_chain or i in early for i in outputs(r)) and re.match(r'alfheim:era(?:3|4|5|6|7|8|9|10)/',r['id'])}

woods={'oak','spruce','birch','jungle','acacia','dark_oak','mangrove','cherry','bamboo','crimson','warped','dreamwood','livingwood','archwood','stripped_oak'}
for r in rows:
    for i in outputs(r):
        if i.endswith('_planks'):woods.add(i.split(':')[1][:-7])
tokens=sorted(woods|set(COLORS),key=len,reverse=True)
def family(r):
    if not r['outputs']:return 'dynamic:'+r['id']
    i=r['outputs'][0][0];ns,path=i.split(':',1)
    if r['type']=='mmorpg:profession_crafting':
        m=re.search(r'era_(\d+)',path)
        if m:
            level=int(m[1]);tier=1 if level<=3 else 5 if level<=7 else 10
            return ns+':'+re.sub(r'era_\d+',f'era_{tier:02d}',path)
    if category(r)=='Settlement' or ns=='supplementaries':
        for token in tokens:
            path=re.sub(r'(?<![a-z])'+re.escape(token)+r'(?=_|/|$)','{palette}',path)
        path=re.sub(r'(?:\{palette\}_?)+','{palette}_',path)
    return ns+':'+path

def score(r):
    value=100
    if r['source'].startswith('kubejs/server_scripts'):value+=260
    if r['source'].startswith('kubejs/data'):value+=100
    if r['id'] in chain_byid:value+=10000
    if r['type'].startswith(('botania:','ars_nouveau:','mythicbotany:')):value+=80
    if r['type'].startswith('create:'):value-=120
    if r['condition_status']=='unresolved':value-=40
    if not r['outputs'] or not r['inputs']:value-=30
    path=r['outputs'][0][0] if r['outputs'] else r['id']
    if r['type']=='mmorpg:profession_crafting':
        m=re.search(r'era_(\d+)',path)
        value+=100 if m and int(m[1]) in (1,5,10) else -100
    if category(r)=='Settlement':
        if any(x in path for x in ('dreamwood','livingrock','oak_','white_')):value+=60
        if r['type']=='minecraft:stonecutting':value+=15
    if r['type'] in ('minecraft:crafting_shaped','minecraft:crafting_shapeless'):value+=10
    return value

producers=C.defaultdict(list)
for r in rows:
    for i in outputs(r):producers[i].append(r['id'])
for i in producers:producers[i].sort(key=lambda rid:(-score(byid[rid]),rid))
quest_refs=C.defaultdict(set)
for p in (ROOT/'config/ftbquests/quests/chapters').glob('*.snbt'):
    for i in re.findall(r'\bitem:\s*"([a-z0-9_.-]+:[a-z0-9_./-]+)"',p.read_text(encoding='utf-8')):
        quest_refs[i].add(p.name)
quest_items={chain_alias.get(i,i) for i in quest_refs}
stations={'botania:pure_daisy','botania:petal_apothecary','botania:twig_wand','botania:mana_spreader','botania:mana_pool','botania:runic_altar','botania:alfheim_portal','botania:terra_plate','ars_nouveau:imbuement_chamber','ars_nouveau:enchanting_apparatus','ars_nouveau:agronomic_sourcelink','ars_nouveau:ritual_brazier','mythicbotany:mana_infuser','dungeon_realm:map_device','minecraft:crafting_table','minecraft:furnace','minecraft:stonecutter'}
required=quest_items|stations|retained_chain

def eligible(r):
    return not any(i in chain_alias for i in outputs(r)) and not (r['type']=='mmorpg:profession_crafting' and family(r) != r['outputs'][0][0])

eligible_rows=[r for r in rows if eligible(r)]
eligible_ids={r['id'] for r in eligible_rows}
def preferred(i):
    candidates=[rid for rid in producers.get(i,[]) if rid in eligible_ids]
    return candidates[0] if candidates else None

# Natural sources remain explicitly external, not inferred craftable from reciprocal
# log/plank recipes. These are not assertions about access in Alfheim.
def natural(i):
    p=i.split(':')[-1]
    return bool(re.search(r'(_log|_wood|_stem|_hyphae|_ore|_sapling|_leaves|_petal|_seed|_seeds|_shard|_crystal|_flower)$',p)) or i in {'minecraft:stone','minecraft:cobblestone','minecraft:dirt','minecraft:sand','minecraft:gravel','minecraft:water','minecraft:lava','minecraft:leather','minecraft:bone','minecraft:blaze_powder','minecraft:prismarine_shard'}

def effective_slots(r):
    if r['id'] in chain_byid and chain_byid[r['id']]['role']!='bootstrap':
        return [dict(options=[(v['item'],v['count'])],role='ingredient') for v in chain_byid[r['id']]['inputs']]
    return [dict(options=[(chain_alias.get(i,i),q) for i,q in s['options']],role=s['role']) for s in r['inputs']]

selected=set();why={};external=set();families={}
def include(rid,reason,stack=None):
    if rid in selected:return
    if rid not in eligible_ids:return
    selected.add(rid);why[rid]=reason;families.setdefault(family(byid[rid]),rid)
    stack=set() if stack is None else stack
    if rid in stack:return
    for slot in effective_slots(byid[rid]):
        opts=slot['options']
        # Tags require runtime tag checks. Their full alternatives stay in the audit.
        if any(i.startswith(('#','fluid:','process:')) for i,q in opts):continue
        candidate=next((i for i,q in opts if i in required),opts[0][0])
        if natural(candidate):external.add(candidate);continue
        p=preferred(candidate)
        if p and p not in stack:include(p,'supplier for '+rid,stack|{rid})
        elif not p:external.add(candidate)

for i in sorted(required):
    rid=preferred(i)
    if rid:include(rid,'quest / station / retained component: '+i)
for r in sorted(eligible_rows,key=lambda r:(-score(r),r['id'])):
    # Dynamic recipes are held for manual serializer review, not assumed removable.
    if not r['outputs'] and category(r) in ('Foundation','Leaf','Song','Campaign','Wound','Settlement'):
        include(r['id'],'hold dynamic serializer until reviewed')
mandatory_count=len(selected)

def counts():return C.Counter(category(byid[rid]) for rid in selected)
candidate_groups=C.defaultdict(list)
for r in sorted(eligible_rows,key=lambda r:(-score(r),r['id'])):candidate_groups[category(r)].append(r)
# Fill family representatives in rounds. Supplier closure can spill across category
# ceilings; it must fit the global retained budget, or that candidate is rejected.
for cat,budget in BUDGETS.items():
    for r in candidate_groups[cat]:
        if counts()[cat]>=budget:break
        if r['id'] in selected or family(r) in families:continue
        before=set(selected);prior_external=set(external)
        include(r['id'],'representative family: '+family(r))
        if len(selected)>sum(BUDGETS.values()):
            selected.clear();selected.update(before);external.clear();external.update(prior_external)
            families.clear()
            for rid in sorted(selected):families.setdefault(family(byid[rid]),rid)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    print('Mandatory suppliers and quest routes:',mandatory_count)
    print('Selected',len(selected),'category counts',dict(counts()))
    plan=[];selected_producers=C.defaultdict(list)
    for rid in selected:
        for i in outputs(byid[rid]):selected_producers[i].append(rid)
    for i in selected_producers:selected_producers[i].sort()
    for r in rows:
        rid=r['id'];out=outputs(r);replaced_inputs=sorted({i for s in r['inputs'] for i,q in s['options'] if i in chain_alias})
        if rid in selected:
            action='replace' if rid in chain_byid and chain_byid[rid]['role']!='bootstrap' or replaced_inputs else 'keep'
            target=rid;target_output='; '.join(out);reason=why[rid]
            migration='prototype shortened material recipe; validate schema, cost and station access' if rid in chain_byid and action=='replace' else 'rewire retired intermediate inputs to finished component' if replaced_inputs else 'retain existing definition'
        else:
            shared=[p for i in out for p in selected_producers.get(i,[])]
            alias=[chain_alias[i] for i in out if i in chain_alias]
            family_rid=families.get(family(r))
            if shared:
                action='consolidate';target=sorted(shared,key=lambda x:(-score(byid[x]),x))[0];target_output='; '.join(outputs(byid[target]));reason='alternate producing route for retained output'
                migration='validate retained station, yield, NBT and source access; byproducts reviewed separately'
            elif alias:
                action='consolidate';target=preferred(alias[0]) or '';target_output='; '.join(alias);reason='collapse obsolete serial intermediate into finished working component'
                migration='update all ingredient references, quest tasks/rewards and tooltips; retain existing item registration for saves'
            elif family_rid:
                action='consolidate';target=family_rid;target_output='; '.join(outputs(byid[target]));reason='one explicit representative for palette / equipment family'
                migration='CRAFTABLE VARIANT RETIRED; no automatic workshop-selection capability assumed; update building/gear/quest demand or provide a separately budgeted route'
            else:
                action='retire';target='';target_output='';reason='outside retained family budget; remove this crafting capability or variant'
                migration='review all output uses and colony requests; no loot or trading substitute asserted'
        lost=[i for i in out if not selected_producers.get(i) and i not in chain_alias]
        plan.append(dict(recipe_id=rid,category=category(r),action=action,family=family(r),outputs='; '.join(out),target_recipe_id=target,target_output=target_output,reason=reason,migration=migration,quest_outputs='; '.join(i for i in out if i in quest_refs),rewire_inputs='; '.join(replaced_inputs),lost_craftable_outputs='; '.join(lost),condition_status=r['condition_status'],endpoint_coverage='explicit' if r['inputs'] and r['outputs'] else 'dynamic / partial',source=r['source'],implementation_status='PROPOSAL ONLY'))
    # Count distinct lost outputs, never byproduct appearances as removed recipe rows.
    lost_outputs=sorted(set(producers)-set(selected_producers))
    impact=[]
    consumer_index=C.defaultdict(set)
    for r in rows:
        for s in r['inputs']:
            for i,q in s['options']:consumer_index[i].add(r['id'])
    for i in lost_outputs:
        consumers=sorted(consumer_index[i])
        retained_consumers=[rid for rid in consumers if rid in selected]
        impact.append(dict(item_id=i,name=pretty(i),proposed_component_alias=chain_alias.get(i,''),old_producing_recipes='; '.join(producers[i]),retained_consumers='; '.join(retained_consumers),other_consumers=len(consumers)-len(retained_consumers),quest_files='; '.join(sorted(quest_refs.get(i,[]))),status='rewire to finished component' if i in chain_alias else 'craft route removed; source / colony / recipe review required'))
    # Explicit retained inputs with a previous producer must have a selected supplier,
    # a named natural-source assumption, or a reported blocker.
    gaps=[]
    for rid in sorted(selected):
        for slot in effective_slots(byid[rid]):
            opts=[i for i,q in slot['options']]
            if any(i.startswith(('#','fluid:','process:')) for i in opts):continue
            if any(i in selected_producers or natural(i) or i not in producers for i in opts):continue
            gaps.append(dict(consumer_recipe=rid,ingredient_options=' OR '.join(opts),issue='all previous explicit producers omitted; replacement route required'))
    def savecsv(name,rr,fields=None):
        fields=fields or list(rr[0])
        with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rr)
    savecsv('recipe_dispositions.csv',plan)
    savecsv('output_migration.csv',impact)
    savecsv('supplier_gaps.csv',gaps,['consumer_recipe','ingredient_options','issue'])
    savecsv('shortened_material_chain.csv',[dict(recipe_id=x['id'],working=x['working'],output=x['output'],recipe_type=x['recipe_type'],inputs=json.dumps(x['inputs']),status=x['status']) for x in chain_plan])
    q_migration=[]
    for p in sorted((ROOT/'config/ftbquests/quests/chapters').glob('*.snbt')):
        for number,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
            m=re.search(r'\bitem:\s*"([a-z0-9_.-]+:[a-z0-9_./-]+)"',line)
            if m and m[1] in chain_alias:
                q_migration.append(dict(file=p.relative_to(ROOT).as_posix(),line=number,old_item=m[1],proposed_item=chain_alias[m[1]],instruction='preserve quest/task/reward IDs; merge redundant step goals and rewrite descriptions; check reward quantities'))
    savecsv('quest_reference_migration.csv',q_migration)
    source_rollup=[]
    for ns in sorted({r['id'].split(':')[0] for r in rows}):
        part=[p for p in plan if p['recipe_id'].split(':')[0]==ns]
        actions=C.Counter(p['action'] for p in part)
        source_rollup.append(dict(namespace=ns,baseline=len(part),keep=actions['keep'],replace=actions['replace'],consolidate=actions['consolidate'],retire=actions['retire'],retained_slots=actions['keep']+actions['replace']))
    savecsv('recipe_family_budget.csv',source_rollup)
    budgets=[dict(category=k,retained_target=v,selected_existing_slots=counts()[k],supplier_spill=max(0,counts()[k]-v)) for k,v in BUDGETS.items()]
    budgets.append(dict(category='Replacement reserve',retained_target=RESERVE,selected_existing_slots=0,supplier_spill=0))
    savecsv('recipe_budget.csv',budgets)
    stats=dict(status='draft design; no live recipe edits',baseline=len(rows),target_ceiling=3750,existing_recipe_slots=len(selected),new_route_reserve=RESERVE,planned_ceiling=len(selected)+RESERVE,unallocated_slots=3750-len(selected)-RESERVE,baseline_rows_displaced=len(rows)-len(selected),reduction_at_ceiling=1-(len(selected)+RESERVE)/len(rows),actions=dict(C.Counter(x['action'] for x in plan)),categories=budgets,mandatory_selection=mandatory_count,old_chain_transformations=len(old_chain_rows),new_chain_transformations=len(chain_plan),retired_chain_items=len(chain_alias),distinct_outputs_losing_selected_producer=len(lost_outputs),quest_items_to_migrate=sum(i in chain_alias for i in quest_refs),quest_item_occurrences_to_migrate=len(q_migration),explicit_supplier_gaps=len(gaps),selected_dynamic_or_partial=sum(not byid[r]['outputs'] or not byid[r]['inputs'] for r in selected),selected_unresolved_conditions=sum(byid[r]['condition_status']=='unresolved' for r in selected),external_source_assumptions=len(external),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest())
    blockers=[
      'Candidate plan only. No row is approved for live deletion by this classification.',
      'Existing static recipe reconstruction is not a final runtime export; verify condition and serializer coverage before applying IDs.',
      'Preserve startup item/block registrations and existing structures/saves. Retiring a crafting route is not deleting a registered block.',
      'Palette/equipment consolidation retires craftable outputs. Generic workshop menus are not counted as implemented or assumed to exist.',
      'MineColonies requests, schematics/blueprints, tags, loot, shops and Java-generated recipes are not exhaustively modeled. Their required palette can force recipe reinstatement or consume reserve slots.',
      'Tag alternatives, catalysts, probabilities and NBT need semantic checks. Explicit endpoint closure does not prove material or station reachability.',
      'Each retained progression capability must consume a Leaf/Song component or require an enforced spine unlock; retained support recipes are not automatically compliant.',
      'World/loot-source assumptions require dimension and accessibility checks. Natural does not mean available at the start.',
      'Shortened recipes are draft data. Resource quantities, mana/Source prices and serializers need balancing and runtime playthroughs.',
      'The 200-slot reserve counts all genuinely new replacement routes; multiple output choices require actual output recipes unless a verified dynamic serializer supports them.',
      'No saved quest IDs are deleted. Remap removed intermediate tasks/rewards and rewrite obsolete step descriptions before rollout.',
      'Keep all nine realm-rune milestones. The five pyramid bands group material families, not campaign chapters or the full recipe count.'
    ]
    package=dict(summary=stats,recipe_dispositions=plan,shortened_chain=chain_plan,component_aliases=chain_alias,external_source_assumptions=[dict(item=i,basis='natural/world interaction assumed' if natural(i) else 'no explicit supplier extracted; runtime/loot/trade/dynamic source must be checked') for i in sorted(external)],supplier_gaps=gaps,blockers=blockers)
    (OUT/'recipe_pyramid_plan.json').write_text(json.dumps(package,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'summary.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
    design=dict(status='draft proposal; no live implementation',generated_by='tools/plan_recipe_pyramid.py',summary=stats,selection_policy='Heuristic candidate selection: protect quest outputs and known station outputs with explicit suppliers; prefer pack-authored and magical routes; retain one palette/equipment family representative within category budgets; preserve core dynamic serializers for manual review.',shortened_chain=chain_plan,component_aliases=chain_alias,required_migration_checks=blockers,review_report='build/recipe-pyramid/recipe-pyramid-proposal.html',full_classification='build/recipe-pyramid/recipe_dispositions.csv',output_migration='build/recipe-pyramid/output_migration.csv')
    (ROOT/'alfheim_reclaimed_design/RECIPE_PYRAMID_PROPOSAL.json').write_text(json.dumps(design,ensure_ascii=False,indent=2),encoding='utf-8')
    build_report(stats,plan,impact,blockers)
    build_image(stats)
    validate(package)
    print(json.dumps(stats,indent=2))

def validate(package):
    """Audit the design arithmetic and protected explicit routes, not runtime playability."""
    stats=package['summary'];checks={}
    checks['one_disposition_per_included_recipe']=len(package['recipe_dispositions'])==len(rows)==len({r['recipe_id'] for r in package['recipe_dispositions']})
    checks['actions_reconcile']=sum(stats['actions'].values())==stats['baseline']
    checks['retained_slots_reconcile']=stats['actions']['keep']+stats['actions']['replace']==len(selected)
    checks['within_recipe_ceiling']=stats['planned_ceiling']<=stats['target_ceiling']
    checks['chain_arithmetic']=stats['old_chain_transformations']==80 and stats['new_chain_transformations']==17 and stats['retired_chain_items']==63
    retained_outputs={i for rid in selected for i in outputs(byid[rid])}
    missing=sorted(i for i in required if i in producers and i not in retained_outputs)
    checks['quest_and_station_outputs_preserved']=not missing
    runes={f'mythicbotany:{x}_rune' for x in ['alfheim','vanaheim','midgard','nidavellir','joetunheim','muspelheim','niflheim','helheim','asgard']}
    checks['nine_realm_runes_preserved']=runes<=retained_outputs
    checks['retired_intermediates_have_finished_targets']=set(chain_alias.values())<=retained_outputs
    checks['no_explicit_supplier_gaps']=not package['supplier_gaps']
    checks['prototype_ingredient_order']=True
    chain_outputs={x['output'] for x in chain_plan};visited=set()
    for p in chain_plan:
        if p['role']!='bootstrap':
            for x in p['inputs']:
                if x['item'] in chain_outputs and x['item'] not in visited:checks['prototype_ingredient_order']=False
            if p['recipe_type'] in ('occultism:spirit_fire','ars_nouveau:imbuement') and len(p['inputs'])!=1:checks['prototype_ingredient_order']=False
        visited.add(p['output'])
    gate_chain=[x for x in chain_plan if x['working']=='Gateweaving']
    checks['cord_prototype_does_not_require_gate_trade']=all(x['recipe_type']!='botania:elven_trade' for x in gate_chain)
    import xml.etree.ElementTree as ET
    root=ET.parse(OUT/'recipe-pyramid.svg').getroot()
    checks['svg_dimensions']=root.attrib['width']=='3200' and root.attrib['height']=='2730'
    png=(OUT/'recipe-pyramid.png').read_bytes()
    checks['png_signature_and_end']=png.startswith(b'\x89PNG\r\n\x1a\n') and png[-8:-4]==b'IEND'
    result=dict(status='static plan checks only',checks=checks,missing_required_outputs=missing,runtime_validated=False)
    (OUT/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    assert all(checks.values()),result

def build_report(stats,plan,impact,blockers):
    E=html.escape
    table='<table><tr><th>Recipe family</th><th>Retained target</th><th>Selected existing slots</th><th>Supplier spill</th></tr>'+''.join(f'<tr><td>{E(x["category"])}</td><td>{x["retained_target"]:,}</td><td>{x["selected_existing_slots"]:,}</td><td>{x["supplier_spill"]}</td></tr>' for x in stats['categories'])+'</table>'
    chain='<table><tr><th>Working</th><th>New chain</th><th>Processes</th></tr>'
    for L in LADDER:
        pp=[p for p in chain_plan if p['working']==WORKINGS[L['era']]]
        chain+=f'<tr><td>{E(WORKINGS[L["era"]])}</td><td>{E(" → ".join(pretty(p["output"]) for p in pp))}</td><td>{E(" → ".join(p["recipe_type"].split(":")[-1].replace("_"," ") for p in pp))}</td></tr>'
    chain+='</table>'
    content=f'''<!doctype html><meta charset="utf-8"><title>Alfheim recipe pyramid proposal</title><style>body{{font:16px/1.55 system-ui;max-width:1100px;margin:40px auto;padding:0 24px;color:#18352d;background:#f5f3e9}}h1,h2{{line-height:1.2}}table{{border-collapse:collapse;width:100%;background:white;margin:20px 0}}td,th{{padding:10px;text-align:left;border:1px solid #bcc9bc}}th{{background:#dce8dc}}code{{font-size:14px}}img{{width:100%}}a{{color:#1b6752}}.callout{{padding:20px;background:#dfebdf}}@media print{{body{{margin:0}}h2{{break-after:avoid}}tr{{break-inside:avoid}}}}</style>
    <h1>Alfheim Reclaimed: recipe pyramid proposal</h1><p>Draft design for review. Live recipes, quests, registrations, mods and saves are unchanged.</p>
    <div class="callout"><b>{stats['baseline']:,} current static definitions → at most {stats['planned_ceiling']:,} planned recipe slots</b><br>{stats['existing_recipe_slots']:,} selected existing slots + {RESERVE} replacement reserve. Target reduction: {stats['reduction_at_ceiling']:.1%}. These are design counts, not runtime-validated savings.</div>
    <p>One main route per shared material. Leaf and Song co-author advancement. Mine and Slash supplies expedition demand and rewards. MineColonies owns settlement growth.</p>
    <img src="recipe-pyramid.png" alt="Proposed recipe pyramid">
    <h2>Budget</h2>{table}<p>Category ceilings are targets. A necessary supplier can spill into another family; the global ceiling still applies. Unallocated headroom: {stats['unallocated_slots']} slots. Native profession definitions count as recipe slots.</p>
    <h2>The concrete material-chain reduction</h2><p>{stats['old_chain_transformations']} existing transformations become {stats['new_chain_transformations']}. The three early fibre transformations stay. Each later working keeps one precursor and its finished material. All nine realm runes and campaign milestone identities stay.</p>{chain}
    <p><b>Gate access correction:</b> the present cord chain includes an elven trade, while <code>alfheim:gate/alfheim_portal</code> consumes Gatewrought Cord. The proposal makes Sunbleached Floss at the Enchanting Apparatus and finishes Gatewrought Cord at the Runic Altar, before any portal trade. This addresses the visible dependency cycle in the authored recipes; runtime access still needs a playthrough.</p>
    <h2>What the classification means</h2><p>This is a heuristic candidate selection, not a validated deletion list. It protects quest and known station outputs with explicit suppliers, prefers pack-authored and magical routes, selects palette/equipment representatives within category budgets, and holds core dynamic serializers for manual review. Palette grouping and source namespace do not prove an item's gameplay role.</p><ul><li><b>Keep:</b> retain the selected definition, subject to access and gating checks.</li><li><b>Replace:</b> preserve its slot/output but change the long material chain or inputs that named a retired intermediate.</li><li><b>Consolidate:</b> point duplicate output routes to a retained recipe, or reduce a palette/equipment family to a selected representative. The CSV states which kind. A different target output means a craftable variant is being retired.</li><li><b>Retire:</b> remove that crafting capability from the proposed scope; no unverified loot or trade substitute is promised.</li></ul>
    <p>{stats['distinct_outputs_losing_selected_producer']:,} distinct outputs lose a selected explicit producer, including collapsed intermediates. This is the content cost of the target and requires the migration review below. Registrations and placed blocks remain.</p>
    <h2>Implementation sequence</h2><ol><li>Validate the runtime recipe inventory and dynamic serializers against this baseline.</li><li>Implement and play the 17-step material chain in an isolated test profile. Remap intermediate ingredients and quest tasks/rewards; update tooltips.</li><li>Consolidate identical-output routes in small batches. Verify stations, yield, catalysts, NBT and byproducts for every retained route.</li><li>Audit MineColonies demands and the selected architectural palette. Decide which missing variants need a reinstated recipe, a verified workshop route, or an authored schematic substitution.</li><li>Reduce armory crafting to three proposed bands (entry, established, pinnacle) across retained equipment families; preserve Mine and Slash combat/loot systems and validate gear gaps.</li><li>Retire overlapping support crafting after the equivalent Leaf/Song route is usable. Re-gate retained power recipes through shared components.</li><li>Check actual recipe count, all required output suppliers, station order, quest completion, colony requests and existing-save loading before enabling each batch.</li></ol>
    <h2>Checks still required</h2><p>Explicit retained-input supplier gaps in this model: {stats['explicit_supplier_gaps']}. This excludes tag, natural-source, station and dynamic semantics. Selected dynamic/partial definitions: {stats['selected_dynamic_or_partial']}; unresolved conditions: {stats['selected_unresolved_conditions']}.</p><ul>{''.join('<li>'+E(x)+'</li>' for x in blockers)}</ul>
    <h2>Detailed proposal files</h2><p><a href="recipe_dispositions.csv">Every recipe and its disposition</a><br><a href="output_migration.csv">Every output losing a selected producer, with consumer and quest references</a><br><a href="quest_reference_migration.csv">Exact quest item references requiring migration</a><br><a href="shortened_material_chain.csv">The 17 proposed material transformations</a><br><a href="recipe_budget.csv">Category budgets</a><br><a href="recipe_family_budget.csv">Recipe counts by source family and disposition</a><br><a href="supplier_gaps.csv">Explicit supplier gaps</a><br><a href="recipe_pyramid_plan.json">Complete structured plan</a></p>'''
    (OUT/'recipe-pyramid-proposal.html').write_text(content,encoding='utf-8')

def build_image(stats):
    E=html.escape;W=3200;H=2730
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<defs><marker id="a" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0L9 4.5L0 9Z" fill="#a4bdb1"/></marker></defs>',
         '<rect width="3200" height="2730" fill="#101f23"/>',
         '<style>text{font-family:Segoe UI,Arial,sans-serif;fill:#eef3e8}.sub{fill:#b8c9c1}.arrow{fill:none;stroke:#a4bdb1;stroke-width:3;marker-end:url(#a)}</style>']
    def text(x,y,s,size=26,fill=None,bold=False,anchor='start'):
        svg.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}"'+(f' fill="{fill}"' if fill else '')+(' font-weight="700"' if bold else '')+'>'+E(s)+'</text>')
    def rect(x,y,w,h,fill,stroke='#476258',rx=15):svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    def arrow(x1,y1,x2,y2):svg.append(f'<path class="arrow" d="M{x1} {y1}L{x2} {y2}"/>')
    def card(x,y,w,h,title,lines,fill='#203c36',accent='#739783'):
        rect(x,y,w,h,fill,accent)
        text(x+20,y+38,title,27,bold=True)
        for j,line in enumerate(lines):text(x+20,y+76+31*j,line,23)
    text(70,78,'ALFHEIM RECLAIMED',30,'#c5d2b9',True)
    text(70,153,'A smaller crafting economy',64,bold=True)
    text(70,202,'Proposed recipe pyramid • Shared materials converge into a few meaningful end uses',29)
    rect(70,238,3060,132,'#192f31')
    text(105,291,f'{stats["baseline"]:,} definitions',42,bold=True)
    arrow(650,285,860,285)
    text(910,291,f'≤ {stats["planned_ceiling"]:,} planned slots',42,'#e1ce95',True)
    text(1900,291,f'{stats["reduction_at_ceiling"]:.1%} fewer',42,'#b5d9ad',True)
    text(105,339,f'{stats["existing_recipe_slots"]:,} selected existing slots + 200 reserved replacement routes • 3,750 hard ceiling',26)
    # The pyramid is a family-level design, deliberately separated from the exact
    # 17-item transformation chain below. Families are not counted as single recipes.
    text(70,424,'MATERIAL ARCHITECTURE',25,'#b8c9c1',True)
    text(1900,424,'Family counts below are proposed design budgets',24,'#b8c9c1')
    bands=[(490,860,1480,200),(740,560,2080,200),(990,350,2500,200),(1240,180,2840,215),(1505,70,3060,225)]
    for index,(y,x,w,h) in enumerate(bands):
        top=w-150
        svg.append(f'<path d="M{x+75} {y-18}H{x+w-75}L{x+w+15} {y+h+12}H{x-15}Z" fill="#172c2d" stroke="#476258" stroke-width="2"/>')
    # Arrows express intended supply direction, not invented ingredient edges.
    for x in (780,1200,1600,2000,2420):arrow(x,1486,x,1462)
    for x in (820,1260,1700,2140):arrow(x,1221,x,1198)
    for x in (1010,1600,2190):arrow(x,972,x,947)
    for x in (1230,1960):arrow(x,722,x,697)
    text(1600,476,'3 END-USE FAMILIES',24,'#e1ce95',True,'middle')
    topcards=[('Crown & realm mastery',['Crownwork and nine realm runes']),('Masterwork equipment',['Mine and Slash, armory and regalia']),('Settlement restoration',['MineColonies and magical supply'])]
    for j,(title,lines) in enumerate(topcards):card(875+j*490,505,470,145,title,lines,'#4a432e','#cbb777')
    text(1600,726,'5 MAJOR ASSEMBLY FAMILIES',24,'#d7dac0',True,'middle')
    assems=[('Gate & travel',['Portal construction','Expedition access']),('Mana infrastructure',['Pools, spreaders','Infusion structures']),('Source infrastructure',['Sourcelinks','Apparatus and rituals']),('Colony workshops',['Builders and crafters','Magical supply inputs']),('Equipment fittings',['Weapons and regalia','Shared binding materials'])]
    for j,(title,lines) in enumerate(assems):card(575+j*412,755,394,155,title,lines,'#334638','#8fa584')
    text(1600,976,'10 SHARED PROGRESSION COMPONENTS',24,'#b8d4c2',True,'middle')
    comps=[('Botanical thread',['Living Fibre','Charged Fibre']),('Runic bindings',['Verdant Filament','Gatewrought Cord']),('Forged & fey materials',['Elementium Core','Wildmarch Sinew']),('Tempered & inscribed',['Emberbound Weave','Rimebound Lattice']),('Ancestral crownwork',['Grave-Gilt Thread','Crown Filament'])]
    for j,(title,lines) in enumerate(comps):card(365+j*496,1005,476,155,title,lines,'#244438','#70a78b')
    text(1600,1226,'20 SHARED REFINED MATERIAL SLOTS',24,'#b8d4c2',True,'middle')
    refined=[('Worked wood & stone',['Dreamwood · Livingrock','Twigs · mana glass']),('Metal stock',['Elementium · Manasteel','Common metals · alloys']),('Mana / Source reagents',['Mana powder · Source gems','Mana pearls · mana diamonds']),('Essence stock',['Air · earth · fire · water','Spell and ritual reagents']),('Bifrost refinement',['Crystallized · condensed','Refined · distilled'])]
    for j,(title,lines) in enumerate(refined):card(195+j*564,1255,545,170,title,lines,'#1f3b3f','#6b9b9a')
    text(1600,1490,'40 GATHERED RESOURCE FAMILY SLOTS',24,'#b8d4c2',True,'middle')
    raw=[('Woods',['Dreamwood','Archwood and timber']),('Stone & earth',['Livingrock source','Clay, sand and stone']),('Plants',['Petals and seeds','Cultivated blooms']),('Ore & minerals',['Native elementium','Exotic metal supply']),('Fey materials',['Frontier drops','Wildlife supplies']),('Expedition loot',['Mine and Slash','Currency and salvage']),('Mana inputs',['Flower fuel','Botanical reagents']),('Source inputs',['Farming activity','Magical reagents'])]
    for j,(title,lines) in enumerate(raw):card(85+j*380,1520,362,170,title,lines,'#1c3438','#557b79')
    text(70,1790,'Bands group material roles, not unlock dates. Advanced resources enter only when their working is accessible.',25,'#b8c9c1')
    text(70,1830,'Building palettes and equipment branch off shared supplies. A family remains many recipes unless its serializer supports selection.',25,'#b8c9c1')
    # Actual retained item identities are shown in full. The long chain folds once.
    text(70,1915,'THE CONCRETE MATERIAL CHAIN',33,bold=True)
    text(70,1960,'80 transformations → 17 • Same finished tier materials • Nine realm-rune milestones retained',28,'#e1ce95')
    order=[next(p for p in chain_plan if p['output']==i) for i in early]+[p for p in chain_plan if p['output'] not in early]
    stepcoords=[]
    for idx,p in enumerate(order):
        col=idx if idx<9 else 16-idx
        row=0 if idx<9 else 1
        x=85+col*342;y=2005+row*170
        stepcoords.append((x,y))
    for idx in range(16):
        x,y=stepcoords[idx];xx,yy=stepcoords[idx+1]
        if yy==y:arrow(x+318 if xx>x else x,y+64,xx if xx>x else xx+318,yy+64)
        else:
            # Last box on row one routes around the right edge to row two's first.
            svg.append(f'<path class="arrow" d="M{x+318} {y+64}H3170V{yy+64}H{xx+318}"/>')
    import textwrap
    for idx,p in enumerate(order):
        x,y=stepcoords[idx];song=p['recipe_type'].startswith('ars_nouveau:');spirit=p['recipe_type'].startswith('occultism:')
        fill='#233d50' if song else '#41344a' if spirit else '#244438'
        rect(x,y,318,132,fill,'#709c99')
        text(x+15,y+25,f'{idx+1:02d}',18,'#becfc2',True)
        for j,line in enumerate(textwrap.wrap(pretty(p['output']),22)):text(x+15,y+55+j*26,line,23,bold=True)
        method=p['recipe_type'].split(':')[-1].replace('_',' ')
        method={'enchanting apparatus':'Source apparatus','petal apothecary':'petal binding','mana infusion':'mana infusion','state copying pure daisy':'Pure Daisy','runic altar':'runic binding','terra plate':'mana agglomeration','imbuement':'Source imbuement','infuser':'mana infuser','fey altar':'fey binding'}.get(method,method)
        text(x+15,y+113,method,18,'#bacfc7')
    rect(70,2380,1490,205,'#25382f','#718e72')
    text(100,2425,'WHAT STAYS',27,'#bed9b1',True)
    for j,line in enumerate(['Leaf + Song interlock; Mine and Slash combat and rewards.','MineColonies settlement ownership; world and building registrations.','Gatewrought Cord is made before the gate can be constructed.']):text(100,2470+j*36,line,25)
    rect(1590,2380,1540,205,'#3d3428','#a48c63')
    text(1620,2425,'WHAT THIS TARGET COSTS',27,'#e3c98f',True)
    for j,line in enumerate([f'{stats["distinct_outputs_losing_selected_producer"]:,} outputs lose a selected explicit producer; migration is required.','Palette / gear variants and redundant routes are proposed cuts.','Workshop menus, colony demand and runtime access need validation.']):text(1620,2470+j*36,line,25)
    text(70,2655,'DRAFT PROPOSAL • No live recipes changed • Counts come from the static local inventory',26,'#b8c9c1')
    text(70,2698,'Detailed dispositions, replacement IDs, consumer impacts and budget are supplied separately for review.',24,'#b8c9c1')
    svg.append('</svg>')
    (OUT/'recipe-pyramid.svg').write_text('\n'.join(svg),encoding='utf-8')
    # Use the already-installed native SVG renderer. This is a data diagram, not an
    # AI-generated illustration, and remains a self-contained static SVG/PNG.
    import render_recipe_tree as raster
    handle=raster.new(str(OUT/'recipe-pyramid.svg').encode('utf-8'),None)
    assert handle,'SVG parse failed'
    surface=raster.image(0,W,H);assert raster.status(surface)==0
    ctx=raster.create(surface);assert raster.render(handle,ctx)
    assert raster.write_png(surface,str(OUT/'recipe-pyramid.png').encode('utf-8'))==0
    raster.destroy(ctx);raster.destroy_surface(surface)

if __name__=='__main__':main()
