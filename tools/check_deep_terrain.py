"""Static invariants for the composed Deep/Void generator and native ore hosts."""
import json
import zipfile
from pathlib import Path
from gen_deep_terrain import ROOT, build, config
from gen_alfheim_biomes import void_final_density
from gen_golden_terraces import strip


def main():
    output=build()
    for name,data in output.items():
        assert (ROOT/name).read_bytes()==data, name
    # THE VOID BAND LIVES IN THE VOID AUTHORITY. alfheim_final is the terrain-authority
    # selector since 2026-09-12 and carries no band of its own -- see B-96.
    _leaf=ROOT/'kubejs/data/alfheim/worldgen/density_function/authority/void.json'
    if not _leaf.exists():        # pre-authority layout
        _leaf=ROOT/'kubejs/data/mythicbotany/worldgen/density_function/alfheim_final.json'
    actual=json.loads(_leaf.read_text())
    baseline=strip(void_final_density(False))
    assert actual==void_final_density()
    actual=strip(actual)          # the terracing is an addend; the Void band is underneath it
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
    from gen_void_worldgen import MASK, RIM, DRY_AQUIFER_RIM
    assert RIM < DRY_AQUIFER_RIM < -0.50, 'dry aquifer shoulder must begin safely inside the terrain rim'
    fluids=settings['noise_router']['fluid_level_floodedness']
    assert fluids['input']==MASK and fluids['max_exclusive']==DRY_AQUIFER_RIM
    deep_fluids=fluids['when_out_of_range']
    assert deep_fluids['input']=='minecraft:y' and (deep_fluids['min_inclusive'],deep_fluids['max_exclusive'])==(-60,28)
    assert deep_fluids['when_out_of_range']==original['noise_router']['fluid_level_floodedness'], 'Ordinary Alfheim aquifers changed'
    for key, dry_value in (('fluid_level_floodedness', -1.0),
                           ('initial_density_without_jaggedness', 1.0)):
        branch=settings['noise_router'][key]
        assert branch['input']==MASK and branch['max_exclusive']==DRY_AQUIFER_RIM
        assert branch['when_in_range']==dry_value
    assert settings['noise_router']['fluid_level_spread']==original['noise_router']['fluid_level_spread']
    assert settings['noise_router']['lava']==original['noise_router']['lava']
    for key in ('fluid_level_floodedness','initial_density_without_jaggedness'):
        settings['noise_router'][key]=original['noise_router'][key]
    assert settings==original, 'Unrelated noise settings changed'
    surface=json.loads(output['kubejs/data/mythicbotany/libx/surface_rule_set/alfheim_surface.json'])
    # MythicBotany's own rule must survive verbatim somewhere in our chain. Find it rather than
    # index it: this assertion has already been broken once by prepending a rule ahead of it, and
    # the invariant is "it is still in there unchanged", not "it is third".
    _seq = surface['before_biomes']['sequence']
    assert old_surface['before_biomes'] in _seq, 'Upstream surface rule changed'
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
          f'quiet Void branch, dry aquifer shoulder, continuous ordinary upper density, bedrock '
          f'and unrelated noise/surface settings preserved; {len(land)} land biomes')


if __name__=='__main__': main()
