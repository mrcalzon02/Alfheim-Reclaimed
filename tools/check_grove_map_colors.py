"""Check every owned tree block has a visible, texture-derived map fallback."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'tools/groves_manifest.json').read_text())
    script = (ROOT / 'kubejs/startup_scripts/12_groves.js').read_text()
    count = 0
    for tree in manifest['trees']:
        for suffix in ('log', 'leaves', 'sapling'):
            name = tree['id'] + '_' + suffix
            with Image.open(ROOT / f'kubejs/assets/alfheim/textures/block/{name}.png') as image:
                pixels = list(image.convert('RGBA').getdata())
            weight = sum(a for r, g, b, a in pixels)
            assert weight > 0, name
            rgb = [round(sum(p[c] * p[3] for p in pixels) / weight) for c in range(3)]
            color = '#' + ''.join(f'{v:02x}' for v in rgb)
            line = next(line for line in script.splitlines() if f"event.create('alfheim:{name}')" in line)
            assert f".mapColor('{color}')" in line, name
            assert sum(rgb) > 50, (name, color)
            count += 1
    print(f'GROVE MAP COLORS PASS: {count} blocks, including all 3 leaf canopies')


if __name__ == '__main__':
    main()
