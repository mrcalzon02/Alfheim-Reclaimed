"""Generate 1.20.1-compatible overrides without changing third-party jars."""
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TABLES = ('chests/citadel/citadel_tomes', 'chests/catacombs/crypt_loot')


def convert(node):
    if isinstance(node, list):
        return [convert(value) for value in node]
    if not isinstance(node, dict):
        return node
    node = {key: convert(value) for key, value in node.items()}
    if node.get('type') == 'minecraft:loot_table' and 'value' in node:
        node['name'] = node.pop('value')
    if node.get('function') == 'minecraft:set_written_book_pages':
        assert node['mode'] == 'insert'
        pages = ','.join(json.dumps(json.dumps(page, ensure_ascii=False))
                         for page in node['pages'])
        return {'function': 'minecraft:set_nbt',
                'tag': '{title:"Citadel Records",author:"Citadel Archivist",pages:[' + pages + ']}' }
    return node


def main():
    jars = list((ROOT / 'mods').glob('irons_spellbooks-*.jar'))
    assert len(jars) == 1, jars
    with zipfile.ZipFile(jars[0]) as jar:
        for table in TABLES:
            name = f'data/irons_spellbooks/loot_tables/{table}.json'
            data = convert(json.loads(jar.read(name)))
            target = ROOT / 'kubejs' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            print(f'Generated {target.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
