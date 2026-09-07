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

    deep_wrappers=[]
    def strip_deep(value):
        if isinstance(value, dict):
            if (value.get('type')=='minecraft:range_choice' and value.get('input')=='minecraft:y'
                    and (value.get('min_inclusive'),value.get('max_exclusive'))==(-60,28)):
                assert value['when_in_range']['type']=='minecraft:min', 'Deep may only carve'
                deep_wrappers.append(value)
                return strip_deep(value['when_out_of_range'])
            return {key:strip_deep(child) for key,child in value.items()}
        if isinstance(value,list): return [strip_deep(child) for child in value]
        return value
    assert strip_deep(actual)==baseline, 'Deep wrapper changed unrelated upper/Hills/Void density'
    assert deep_wrappers, 'Deep density envelope is missing'
    with zipfile.ZipFile(next((ROOT/'mods').glob('MythicBotany*.jar'))) as jar:
        original=json.loads(jar.read('data/mythicbotany/worldgen/noise_settings/alfheim.json'))
        old_surface=json.loads(jar.read('data/mythicbotany/libx/surface_rule_set/alfheim_surface.json'))
    settings=json.loads(output['kubejs/data/mythicbotany/worldgen/noise_settings/alfheim.json'])
    fluids=settings['noise_router']['fluid_level_floodedness']
    assert fluids['input']==baseline['input'] and fluids['max_exclusive']==baseline['max_exclusive']
    deep_fluids=fluids['when_out_of_range']
    assert deep_fluids['input']=='minecraft:y' and (deep_fluids['min_inclusive'],deep_fluids['max_exclusive'])==(-60,28)
    assert deep_fluids['when_out_of_range']==original['noise_router']['fluid_level_floodedness'], 'Ordinary Alfheim aquifers changed'
    for key in ('fluid_level_floodedness','initial_density_without_jaggedness','fluid_level_spread','lava'):
        settings['noise_router'][key]=original['noise_router'][key]
    assert settings==original, 'Unrelated noise settings changed'
    surface=json.loads(output['kubejs/data/mythicbotany/libx/surface_rule_set/alfheim_surface.json'])
    assert surface['before_biomes']['sequence'][2]==old_surface['before_biomes'], 'Upstream surface rule changed'
    surface['before_biomes']=old_surface['before_biomes']
    assert surface==old_surface, 'Unrelated surface rules changed'
    assert not any('/data/minecraft/' in name or '/dimension/' in name for name in output)
    layer=json.loads((ROOT/'kubejs/data/mythicbotany/libx/biome_layer/alfheim.json').read_text())
    land=json.loads(output['kubejs/data/alfheim/tags/worldgen/biome/deepworks_land.json'])['values']
    from gen_void_worldgen import VOID_IDS
    assert set(land)=={b['biome'] for b in layer['biomes']} - set(VOID_IDS)
    for name,data in output.items():
        if '/configured_feature/deepworks/ore_' in name:
            feature=json.loads(data)
            targets=feature['config']['targets']
            assert targets[0]['target']['predicate_type']=='minecraft:block_match'
            assert targets[-1]['target']['tag']=='alfheim:livingrock_natural'
    print(f'PASS: {len(output)} reproducible files; {len(deep_wrappers)} Deep density branches; '
          f'Void branch, Hills plateau, upper density, bedrock and unrelated noise/surface settings preserved; {len(land)} land biomes')


if __name__=='__main__': main()
