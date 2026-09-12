"""Reject discontinuous climate-stamped plateaus in ordinary Alfheim terrain."""
import json
from pathlib import Path

from gen_alfheim_biomes import void_final_density
from gen_golden_terraces import strip, terrace_term
from gen_deep_terrain import wrap_density
from gen_void_worldgen import density

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
    base = {'type': 'minecraft:min',
            'argument1': 'mythicbotany:alfheim_initial',
            'argument2': 'mythicbotany:alfheim_caves'}
    expected = density(wrap_density(base))
    # The Golden Fields terracing is an addend on top of this. Remove it and the assertion below
    # is the same one it always was -- ordinary Alfheim terrain must still be the continuous
    # upstream field. strip() returns its input untouched if the addend is not the known terrace
    # term, so a different wrapper cannot sneak past here.
    assert actual['argument2'] == terrace_term(), 'unexpected addend on the final density'
    assert strip(actual) == expected, 'ordinary Alfheim density is no longer the continuous upstream terrain'
    upper_plateaus = [node for node in walk(actual)
                      if node.get('type') == 'minecraft:y_clamped_gradient'
                      and node.get('from_value') == 1.0
                      and node.get('to_value') == -1.0
                      and node.get('from_y', -1000) >= 128]
    assert not upper_plateaus, 'a hard high-altitude plateau has returned to ordinary terrain'
    print('PASS: ordinary Alfheim keeps continuous upstream terrain; no climate-stamped '
          'high-altitude plateau can create sheer Hills/Plains/Starved ranges')


if __name__ == '__main__':
    main()
