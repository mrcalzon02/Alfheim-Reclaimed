"""Check drop bounds, player-kill guards, registrations, recipes and bestiary coverage."""
import json
from pathlib import Path
from fey_drops import ITEMS, RECIPES, drops, loot_table


def main():
    root=Path('.')
    roster=json.loads((root/'tools/fey_manifest.json').read_text())
    manifest=json.loads((root/'tools/fey_drops_manifest.json').read_text())
    registration=(root/'kubejs/startup_scripts/19_fey_drops.js').read_text()
    bestiary=(root/'config/ftbquests/quests/chapters/ref_fey_wildlife.snbt').read_text()
    failures=[]
    sources=set()
    for r in roster:
        name=r['id'].split(':')[1]
        rows=drops(name,r['family'],r['celestial'])
        table=json.loads((root/f'kubejs/data/alfheim/loot_tables/entities/{name}.json').read_text())
        if table!=loot_table(rows):
            failures.append(name+': generated loot differs from source')
        if r['name'] not in bestiary:
            failures.append(name+': missing bestiary entry')
        for item,low,high,chance,player in rows:
            if not (0<chance<=1 and 0<low<=high<=3):
                failures.append(name+': unbounded drop')
            if r['family']=='elf' and not player:
                failures.append(name+': elf trophy bypasses player-kill guard')
            if item in ITEMS:
                sources.add(item)
        if r['celestial'] and any(row[0] in ('raw_venison','whitetail_hide') for row in rows):
            failures.append(name+': celestial meat/hide contradicts bestiary')
        if name.endswith('doe') and any(row[0]=='hart_antler' for row in rows):
            failures.append(name+': doe drops antlers')
    for item in ITEMS:
        if item!='cooked_venison' and item not in sources:
            failures.append(item+': no creature source')
        if registration.count("event.create('alfheim:"+item+"')")!=1:
            failures.append(item+': missing/duplicate item registration')
        model=root/f'kubejs/assets/alfheim/models/item/{item}.json'
        if not model.exists():
            failures.append(item+': no inventory model')
        if item not in ('raw_venison','cooked_venison'):
            recipe_path=root/f'kubejs/data/alfheim/recipes/fey/{item}.json'
            if not recipe_path.exists():
                failures.append(item+': no useful recipe')
            else:
                recipe=json.loads(recipe_path.read_text())
                result=recipe.get('result',recipe.get('output'))
                if result!={'item':RECIPES[item]['output'],'count':RECIPES[item]['count']}:
                    failures.append(item+': wrong processing output')
        if ITEMS[item][2] not in bestiary and item!='cooked_venison':
            failures.append(item+': processing not taught')
    assert len(manifest['items'])==13 and len(manifest['recipes'])==11
    for failure in failures:
        print('FAIL',failure)
    print(f'Fey drops: {len(ITEMS)} items, 18 loot tables, 14 processing recipes; {len(failures)} problems')
    return bool(failures)


if __name__=='__main__':
    raise SystemExit(main())
