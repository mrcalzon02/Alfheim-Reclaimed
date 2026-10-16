"""Describe custom materials using authored recipe data, without changing recipes.

Run after recipe generators. Shift reveals source and use routes; JEI remains the
authority for quantities, layouts, catalysts and alternate ingredient tags.
"""
import json
import ast
import re
import zipfile
from collections import defaultdict
from pathlib import Path

from check_era import parse_recipes
from gen_ladder import METHODS, STATIONS, pretty
from player_text import player_text

OUT = Path('kubejs/client_scripts/10_process_tooltips.js')


def registered_names():
    names = {}
    for path in Path('kubejs/startup_scripts').glob('*.js'):
        pattern = r'''event\.create\(\s*['"]([^'"]+)['"](?:\s*,[^)]*)?\)\s*\.displayName\(("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')\)'''
        source = path.read_text(encoding='utf-8')
        for match in re.finditer(pattern, source):
            tail = source[match.end():].split('event.create(', 1)[0]
            if '.noItem()' not in tail:
                names[match[1]] = ast.literal_eval(match[2])
    return names


def all_recipes():
    recipes = []
    for path in sorted(Path('kubejs/server_scripts').glob('*.js')):
        recipes.extend(r for r in parse_recipes(path) if r['outputs'])
    # Data recipes include furnishings, wildlife supplies and other custom objects.
    def items(value):
        if isinstance(value, str):
            return [value] if ':' in value and not value.startswith('#') else []
        if isinstance(value, list):
            return [i for v in value for i in items(v)]
        if isinstance(value, dict):
            return [value['item']] if 'item' in value else []
        return []
    data_roots = [Path('kubejs/data'),
                  Path('first_party_mods/alfheim_leyworks/src/main/resources/data')]
    for path in sorted(p for root in data_roots for p in root.glob('*/recipes/**/*.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        outputs = items(data.get('result', data.get('output', data.get('results', []))))
        if not outputs:
            continue
        inputs = []
        for key in ('ingredient', 'ingredients', 'input', 'reagent', 'pedestalItems', 'catalyst'):
            inputs += items(data.get(key, []))
        # Shaped keys are ingredients; their pattern determines counts in JEI.
        for value in data.get('key', {}).values():
            inputs += items(value)
        recipes.append(dict(type=data.get('type'), method='custom', inputs=inputs,
                            outputs=outputs, body=json.dumps(data), id=str(path)))
    return recipes


def build():
    names = registered_names()
    translations = {}
    for path in sorted(Path('mods').glob('*.jar')):
        with zipfile.ZipFile(path) as jar:
            for entry in jar.namelist():
                if re.fullmatch(r'assets/[^/]+/lang/en_us.json', entry):
                    try:
                        translations.update(json.loads(jar.read(entry)))
                    except (ValueError, UnicodeError):
                        pass

    def name(iid):
        if iid.startswith('#'):
            return pretty(iid.split(':', 1)[-1].replace('/', ' ')) + ' (ingredient group)'
        if iid in names:
            return names[iid]
        ns, path = iid.split(':', 1)
        for kind in ('item', 'block'):
            key = f'{kind}.{ns}.{path.replace("/", ".")}'
            if key in translations:
                return player_text(translations[key])
        return pretty(path.replace('/', ' '))

    methods = {typ: METHODS[key] for key, (typ, _) in STATIONS.items()}
    methods.update({'minecraft:crafting_shaped': 'shaped crafting',
                    'minecraft:crafting_shapeless': 'shapeless crafting',
                    'minecraft:smoking': 'smoking', 'minecraft:blasting': 'blasting'})
    origins, uses = defaultdict(list), defaultdict(list)
    for r in all_recipes():
        # Substeps and transitionalItem are not independent sources or uses.
        ins = list(dict.fromkeys(i for i in r['inputs'] if i not in r['outputs'] and
                                not i.startswith('alfheim:incomplete_')))
        ins += ['#' + tag for tag in r.get('tags', [])]
        outs = list(dict.fromkeys(i for i in r['outputs'] if not i.startswith('alfheim:incomplete_')))
        if not ins or not outs:
            continue
        method = methods.get(r['type'], r['method'] if r['method'] != 'custom'
                             else pretty((r['type'] or 'crafting').split(':')[-1]))
        costs = []
        for key, label in [('mana', 'mana'), ('sourceCost', 'Source'), ('source', 'Source'), ('aura', 'aura')]:
            match = re.search(r'\b' + key + r'"?\s*:\s*(\d+)', r['body'])
            if match and int(match[1]):
                costs.append(f'{int(match[1]):,} {label}')
        route = f'{method}: {", ".join(map(name, ins))} -> {", ".join(map(name, outs))}'
        if costs:
            route += ' (' + ', '.join(costs) + ')'
        for iid in outs:
            if iid in names and route not in origins[iid]:
                origins[iid].append(route)
        for iid in ins:
            if iid in names and route not in uses[iid]:
                uses[iid].append(route)

    data = {}
    for iid in sorted(origins.keys() | uses.keys()):
        data[iid] = {'from': origins[iid], 'uses': uses[iid]}
    script = [
        '// GENERATED by tools/gen_process_tooltips.py; run after recipe generators.',
        '// Authored routes only. JEI supplies quantities, layouts and alternatives.',
        'ItemEvents.tooltip(event => {',
        '    const routes = ' + json.dumps(data, ensure_ascii=False, indent=4),
        '    Object.keys(routes).forEach(id => {',
        '        event.addAdvanced(id, (item, advanced, text) => {',
        '            const entry = routes[id]',
        "            if (!event.isShift()) {",
        "                text.add(Text.darkGray('Hold Shift for crafting origins and uses.'))",
        '                return',
        '            }',
        "            text.add(Text.gray('Crafting routes — see JEI for quantities and layouts.'))",
        "            ;[['from', 'Made by'], ['uses', 'Used to produce']].forEach(section => {",
        '                const lines = entry[section[0]]',
        '                if (!lines.length) return',
        '                text.add(Text.aqua(section[1]))',
        '                lines.slice(0, 6).forEach(line => {',
        '                    const words = line.split(" ")',
        '                    let row = ""',
        '                    words.forEach(word => {',
        '                        if (row.length + word.length > 78) { text.add(Text.gray(row)); row = "" }',
        '                        row += (row ? " " : "") + word',
        '                    })',
        '                    if (row) text.add(Text.gray(row))',
        '                })',
        "                if (lines.length > 6) text.add(Text.darkGray('Further routes are listed in JEI.'))",
        '            })',
        '        })',
        '    })',
        '})', '',
    ]
    return '\n'.join(script), data


if __name__ == '__main__':
    script, data = build()
    OUT.write_text(script, encoding='utf-8', newline='\n')
    print(f'{len(data)} custom objects have recipe-origin and use tooltips -> {OUT}')
