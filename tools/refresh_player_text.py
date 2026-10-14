"""Refresh player prose in place, preserving FTB's layout and all progression IDs.

Also updates source manifests. Run after authoring recipes, before launching Minecraft.
"""
import json
import re
from pathlib import Path

import gen_curios
import gen_items
import gen_ladder
import gen_process_tooltips
import gen_quests
from player_text import player_text


def refresh():
    manifest_path = Path('tools/items_manifest.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    generated = {i['id']: i['tooltip'] for i in gen_ladder.build_items()}
    generated.update({
        'living_fibre': 'A botanical thread drawn from Dreamwood and green and lime petals in the Petal Apothecary. Infuse it with 2,000 mana in a Mana Pool to make Charged Fibre.',
        'charged_fibre': 'Living Fibre infused with mana. Bind it with the Runic Altar reagents to make Verdant Filament, the starting material for Gateweaving.',
        'verdant_filament': 'A runically bound botanical filament made from Charged Fibre. Petal binding turns it into Sunbleached Floss, beginning the Gatewrought Cord process.',
    })
    for item in manifest['items']:
        item['tooltip'] = generated.get(item['id'], player_text(item.get('tooltip', '')))
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')

    # Registration-only update. Textures and models are deliberately not regenerated.
    import sys
    saved = sys.argv
    try:
        sys.argv = ['gen_items.py', '--text-only']
        gen_items.main()
    finally:
        sys.argv = saved

    catalog = json.loads(Path(gen_curios.CATALOG).read_text(encoding='utf-8'))
    curios = {'alfheim:' + r['id']: r['tooltip'] for r in gen_curios.plan(catalog)}
    for path in Path('kubejs/startup_scripts').glob('*.js'):
        text = path.read_text(encoding='utf-8')
        original = text
        def registration(match):
            iid, before, tip = match.groups()
            new = curios.get(iid, player_text(tip))
            if new == tip:
                return match[0]
            return f"event.create('{iid}'){before}.tooltip(" + json.dumps(new, ensure_ascii=False) + ')'
        text = re.sub(r"event\.create\('([^']+)'\)([^\n]*?)\.tooltip\('((?:\\.|[^'\\])*)'\)", registration, text)
        if text != original:
            path.write_text(text, encoding='utf-8', newline='\n')

    descriptions = {}
    for L in gen_ladder.LADDER:
        for i in range(len(gen_ladder.chain_for(L))):
            descriptions[gen_quests.qid(f'era_{L["era"]}', f'chain_{i}')] = gen_ladder.chain_description(L, i) + ['', 'See the item recipe for all reagents and resource costs.']

    changed = 0
    for path in Path('config/ftbquests/quests').rglob('*.snbt'):
        text = path.read_text(encoding='utf-8')
        original = text
        def quoted(match):
            value = json.loads(match[0])
            new = player_text(value)
            return json.dumps(new, ensure_ascii=False) if new != value else match[0]
        text = re.sub(r'"(?:\\.|[^"\\])*"', quoted, text)
        def quest(match):
            block = match[0]
            ident = re.search(r'^\t\t\tid: "([A-F0-9]+)"', block, re.M)
            if ident and ident[1] in descriptions:
                new = gen_quests.snbt_lines('description', descriptions[ident[1]], 3)
                block = re.sub(r'^\t\t\tdescription: \[.*?^\t\t\t\]', lambda m: new, block, flags=re.M | re.S)
            return block
        text = re.sub(r'^\t\t\{\n.*?^\t\t\}', quest, text, flags=re.M | re.S)
        if text != original:
            path.write_text(text, encoding='utf-8', newline='\n')
            changed += 1
    script, data = gen_process_tooltips.build()
    gen_process_tooltips.OUT.write_text(script, encoding='utf-8', newline='\n')
    print(f'Updated {changed} quest files and crafting tooltips for {len(data)} custom objects.')


if __name__ == '__main__':
    refresh()
