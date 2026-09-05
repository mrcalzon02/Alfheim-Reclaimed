"""Static invariants for the composed Deep/Void generator and native ore hosts."""
import json
import zipfile
from pathlib import Path
from gen_deep_terrain import ROOT, build, config
from gen_alfheim_biomes import void_final_density


def main():
    output=build()
    for name,data in output.items():
        assert (ROOT/name).read_bytes()==data, name
    actual=json.loads((ROOT/'kubejs/data/mythicbotany/worldgen/density_function/alfheim_final.json').read_text())
    baseline=void_final_density(False)
    assert actual==void_final_density()
    assert actual['when_in_range']==baseline['when_in_range'], 'Void island density changed'
    assert actual['input']==baseline['input'], 'Void mask changed'
    wrapped=actual['when_out_of_range']
    assert wrapped['input']=='minecraft:y'
    assert (wrapped['min_inclusive'],wrapped['max_exclusive'])==(-60,28)
    assert wrapped['when_out_of_range']==baseline['when_out_of_range']
    assert wrapped['when_in_range']['type']=='minecraft:min', 'Deep may only carve'
    with zipfile.ZipFile(next((ROOT/'mods').glob('MythicBotany*.jar'))) as jar:
        original=json.loads(jar.read('data/mythicbotany/worldgen/noise_settings/alfheim.json'))
        old_surface=json.loads(jar.read('data/mythicbotany/libx/surface_rule_set/alfheim_surface.json'))
    settings=json.loads(output['kubejs/data/mythicbotany/worldgen/noise_settings/alfheim.json'])
    fluids=settings['noise_router']['fluid_level_floodedness']
    assert fluids['input']==baseline['input'] and fluids['max_exclusive']==baseline['max_exclusive']
    assert fluids['when_in_range']==original['noise_router']['fluid_level_floodedness'], 'Void aquifers changed'
    settings['noise_router']['fluid_level_floodedness']=original['noise_router']['fluid_level_floodedness']
    assert settings==original, 'Unrelated noise settings changed'
    surface=json.loads(output['kubejs/data/mythicbotany/libx/surface_rule_set/alfheim_surface.json'])
    assert surface['before_biomes']['sequence'][0]==old_surface['before_biomes'], 'Bedrock rule changed'
    surface['before_biomes']=old_surface['before_biomes']
    assert surface==old_surface, 'Unrelated surface rules changed'
    assert not any('/data/minecraft/' in name or '/dimension/' in name for name in output)
    layer=json.loads((ROOT/'kubejs/data/mythicbotany/libx/biome_layer/alfheim.json').read_text())
    land=json.loads(output['kubejs/data/alfheim/tags/worldgen/biome/deepworks_land.json'])['values']
    assert set(land)=={b['biome'] for b in layer['biomes']} - {'alfheim:void_verge'}
    for name,data in output.items():
        if '/configured_feature/' in name:
            feature=json.loads(data)
            assert feature['config']['targets'][0]['target']['tag']=='alfheim:livingrock_natural'
    print(f'PASS: {len(output)} reproducible files; Void branch, upper density, bedrock and unrelated noise/surface settings preserved; {len(land)} land biomes')


if __name__=='__main__': main()
