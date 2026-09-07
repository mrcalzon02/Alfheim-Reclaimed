"""Static contract for the high Alfheim Hills plateau."""
import json
from pathlib import Path

from gen_alfheim_biomes import HILLS_SURFACE_BAND, void_final_density

ROOT = Path(__file__).resolve().parents[1]


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def main():
    path = ROOT / 'kubejs/data/mythicbotany/worldgen/density_function/alfheim_final.json'
    actual = json.loads(path.read_text(encoding='utf-8'))
    assert actual == void_final_density(), 'shipping final density differs from its generator'
    gradients = [node for node in walk(actual)
                 if node.get('type') == 'minecraft:y_clamped_gradient'
                 and node.get('from_y') == HILLS_SURFACE_BAND[0]
                 and node.get('to_y') == HILLS_SURFACE_BAND[1]
                 and node.get('from_value') == 1.0
                 and node.get('to_value') == -1.0]
    assert len(gradients) == 1, 'the Hills surface transition must be uniquely 191..194'
    selectors = {(node.get('input'), node.get('min_inclusive'), node.get('max_exclusive'))
                 for node in walk(actual) if node.get('type') == 'minecraft:range_choice'}
    required = {
        ('mythicbotany:alfheim_continentalness', 0.4, 100),
        ('mythicbotany:alfheim_temperature', -0.45, 100),
        ('mythicbotany:alfheim_weirdness', -100, 0.3),
        ('mythicbotany:alfheim_humidity', -0.3, 100),
        ('minecraft:y', 128, 256),
    }
    assert required <= selectors, 'Hills density no longer matches the biome layer partition'
    print('PASS: Alfheim Hills plateau signal matches the biome partition and caps terrain '
          'through the Y=191..194 surface transition')


if __name__ == '__main__':
    main()
