"""Inventory Curios slots and wearable items from the installed, read-only mod jars."""
from collections import defaultdict
import hashlib, json, re, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODS = ROOT / 'mods'
OUT = ROOT / 'alfheim_reclaimed_design/curios'


def load_json(zf, name):
    try:
        return json.loads(zf.read(name))
    except Exception:
        return None


def result_ids(node, under_result=False):
    found = set()
    if isinstance(node, dict):
        for key, value in node.items():
            result_context = under_result or key in {'result', 'results', 'output', 'outputs'}
            if result_context and key in {'item', 'id'} and isinstance(value, str) and ':' in value:
                found.add(value)
            elif result_context and isinstance(value, str) and ':' in value:
                found.add(value)
            found |= result_ids(value, result_context)
    elif isinstance(node, list):
        for value in node:
            found |= result_ids(value, under_result)
    elif under_result and isinstance(node, str) and ':' in node:
        found.add(node)
    return found


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw_tags = defaultdict(list)
    slots = []
    translations = {}
    recipes_by_result = defaultdict(list)
    jar_hashes = {}
    for jar in sorted(MODS.glob('*.jar')):
        try:
            with zipfile.ZipFile(jar) as zf:
                names = zf.namelist()
                relevant = False
                for name in names:
                    low = name.lower()
                    match = re.fullmatch(r'data/curios/tags/items/([^/]+)\.json', low)
                    if match:
                        data = load_json(zf, name)
                        if isinstance(data, dict):
                            raw_tags[f'curios:{match.group(1)}'].append((jar.name, data.get('values', [])))
                            relevant = True
                    if name.endswith('.json') and ('/curios/slots/' in low or '/curios/curios/slots/' in low):
                        data = load_json(zf, name)
                        if isinstance(data, dict):
                            slot_id = Path(name).stem
                            slots.append({'slot': slot_id, 'source_jar': jar.name, 'path': name, **data})
                            relevant = True
                    if re.fullmatch(r'assets/[^/]+/lang/en_us\.json', low):
                        data = load_json(zf, name)
                        if isinstance(data, dict):
                            translations.update({k: v for k, v in data.items() if isinstance(v, str)})
                if relevant:
                    jar_hashes[jar.name] = hashlib.sha256(jar.read_bytes()).hexdigest()
                for name in names:
                    if '/recipes/' not in name or not name.endswith('.json'):
                        continue
                    data = load_json(zf, name)
                    if isinstance(data, dict):
                        for item_id in result_ids(data):
                            recipes_by_result[item_id].append({'source_jar': jar.name, 'path': name, 'type': data.get('type', 'unknown')})
        except zipfile.BadZipFile:
            continue

    # Resolve direct values and tag references against every installed item tag.
    item_tags = defaultdict(list)
    for jar in sorted(MODS.glob('*.jar')):
        try:
            with zipfile.ZipFile(jar) as zf:
                for name in zf.namelist():
                    m = re.fullmatch(r'data/([^/]+)/tags/items/(.+)\.json', name.lower())
                    if not m:
                        continue
                    data = load_json(zf, name)
                    if isinstance(data, dict):
                        item_tags[f'{m.group(1)}:{m.group(2)}'].extend(data.get('values', []))
        except zipfile.BadZipFile:
            continue

    def expand(value, trail=()):
        if isinstance(value, dict):
            value = value.get('id', '')
        if not isinstance(value, str):
            return set()
        if not value.startswith('#'):
            return {value} if ':' in value else set()
        tag = value[1:]
        if tag in trail:
            return set()
        out = set()
        for member in item_tags.get(tag, []):
            out |= expand(member, trail + (tag,))
        return out

    wearables = {}
    for slot_tag, definitions in sorted(raw_tags.items()):
        for source_jar, values in definitions:
            for raw in values:
                for item_id in expand(raw):
                    row = wearables.setdefault(item_id, {'id': item_id, 'slots': [], 'source_tags': [], 'source_jars': [], 'recipes': []})
                    row['slots'].append(slot_tag.split(':', 1)[1])
                    row['source_tags'].append(slot_tag)
                    row['source_jars'].append(source_jar)
    for item_id, row in wearables.items():
        ns, path = item_id.split(':', 1)
        key = f'item.{ns}.{path.replace("/", ".")}'
        row['name'] = translations.get(key, item_id)
        row['slots'] = sorted(set(row['slots']))
        row['source_tags'] = sorted(set(row['source_tags']))
        row['source_jars'] = sorted(set(row['source_jars']))
        row['recipes'] = recipes_by_result.get(item_id, [])
        row['classification'] = 'cosmetic' if path.startswith('cosmetic_') else 'functional'

    data = {
        'status': 'installed-jar inventory; runtime confirms 14 slot types loaded, slot capacities require player capability probe',
        'source': 'read-only scan of mods/*.jar plus server/console-20260904-102701.log',
        'live_slot_type_count': 14,
        'slot_definitions': sorted(slots, key=lambda x: (x['slot'], x['source_jar'])),
        'wearable_count': len(wearables),
        'functional_count': sum(x['classification'] == 'functional' for x in wearables.values()),
        'cosmetic_count': sum(x['classification'] == 'cosmetic' for x in wearables.values()),
        'wearables': sorted(wearables.values(), key=lambda x: (x['slots'], x['id'])),
        'relevant_jar_sha256': jar_hashes,
    }
    (OUT / 'installed_curios_inventory.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    grouped = defaultdict(list)
    for row in data['wearables']:
        if row['classification'] == 'functional':
            for slot in row['slots']:
                grouped[slot].append(row)
    lines = [
        '# Installed Curios inventory', '',
        'Generated by `tools/build_curio_inventory.py` from the installed jars. This records slot eligibility and recipe presence; it does not infer an item effect from its name.', '',
        f"The scan found **{data['wearable_count']} wearable IDs**: **{data['functional_count']} functional** and **{data['cosmetic_count']} Botania cosmetic**. The last headless run reports **14 loaded slot types**.", '',
    ]
    for slot in sorted(grouped):
        lines += [f'## `{slot}`', '', '| Item | ID | Recipe files |', '|---|---|---:|']
        for row in grouped[slot]:
            lines.append(f"| {row['name']} | `{row['id']}` | {len(row['recipes'])} |")
        lines.append('')
    (OUT / 'INSTALLED_CURIOS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f"Curios inventory: {data['wearable_count']} wearable IDs ({data['functional_count']} functional, {data['cosmetic_count']} cosmetic), {len(data['slot_definitions'])} slot definitions, 14 live slot types.")


if __name__ == '__main__':
    main()
