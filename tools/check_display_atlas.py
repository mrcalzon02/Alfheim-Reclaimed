"""Keep direct-render textures used by baked items in the block atlas as well.

Minecraft's default atlas includes block/ and item/, not entity/ or models/armor/.
Use explicit single sources: a directory source would load every mod's mob skins.
Run with --write after changing generated companion models, then build the mod.
"""
import argparse
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'first_party_mods/alfheim_companion/src/main/resources'
ATLAS = 'assets/minecraft/atlases/blocks.json'


def expected():
    textures = set()
    models = list((RES / 'assets/alfheim_companion/models').rglob('*.json'))
    for path in models:
        for texture in json.loads(path.read_text()).get('textures', {}).values():
            if texture.startswith('alfheim_companion:'):
                name = texture.split(':', 1)[1]
                assert (RES / f'assets/alfheim_companion/textures/{name}.png').is_file(), (path, texture)
                if not name.startswith(('block/', 'item/')):
                    textures.add(texture)
    return {'sources': [{'type': 'minecraft:single', 'resource': t} for t in sorted(textures)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--jar', action='store_true')
    args = ap.parse_args()
    doc = expected()
    data = (json.dumps(doc, indent=2) + '\n').encode()
    if args.write:
        (RES / ATLAS).parent.mkdir(parents=True, exist_ok=True)
        (RES / ATLAS).write_bytes(data)
    assert (RES / ATLAS).read_bytes() == data, 'Refresh display atlas with --write'
    if args.jar:
        with zipfile.ZipFile(ROOT / 'mods/alfheim_companion-0.2.0.jar') as jar:
            assert jar.read(ATLAS) == data
            for row in doc['sources']:
                ns, path = row['resource'].split(':')
                asset = f'assets/{ns}/textures/{path}.png'
                assert jar.read(asset) == (RES / asset).read_bytes(), asset
    print(f'DISPLAY ATLAS PASS: {len(doc["sources"])} explicitly stitched textures; all model references resolve')


if __name__ == '__main__':
    main()
