"""Generate restrained, climate-aligned third-party tree placement in Alfheim.

This generator only adds Forge biome modifiers. It reuses the installed mods' placed
features, including their survival filters and sparse rarity, instead of copying or
overriding third-party worldgen.

TaxTreeGiant is intentionally excluded. The 2026-09-06 field-review decision was that
regular giant landmarks would intrinsically change Alfheim's world silhouette. Dense
Feywild tree groupings are likewise reserved for the future pixie sky-island structures;
the surface placements here are isolated accents.

    python tools/gen_tree_worldgen.py
    python tools/gen_tree_worldgen.py --dry-run
"""
import argparse
import glob
import json
import os
import zipfile


OUT = os.path.join('kubejs', 'data', 'alfheim', 'forge', 'biome_modifier')
PLACED_OUT = os.path.join('kubejs', 'data', 'alfheim', 'worldgen', 'placed_feature')

# Path prefixes are numeric because Forge applies biome modifiers in ResourceLocation
# path order. One feature per modifier and a stable order give the global feature sorter
# a single, non-contradictory sequence in every biome where two accents overlap.
PLACEMENTS = (
    {
        'file': 'zz_tree_10_jaffa_orange_warm.json',
        'feature': 'alfheim:tree_jaffa_orange_warm',
        'source_feature': 'jaffabricate:orange_placed',
        'biomes': ['alfheim:bloomfall_vale', 'mythicbotany:golden_fields'],
        'note': 'warm living biomes; source feature averages one attempt per 10 chunks',
    },
    {
        'file': 'zz_tree_11_jaffa_orange_scattered.json',
        'feature': 'alfheim:tree_jaffa_orange_scattered',
        'source_feature': 'jaffabricate:orange_rare_placed',
        'biomes': ['alfheim:silverbark_wood', 'mythicbotany:dreamwood_forest'],
        'note': 'cooler woods; source feature averages one attempt per 16 chunks',
    },
    {
        'file': 'zz_tree_12_feywild_autumn.json',
        'feature': 'alfheim:tree_feywild_autumn',
        'source_feature': 'feywild:autumn_tree_placed',
        'biomes': ['alfheim:ashen_grove', 'alfheim:silverbark_wood'],
        'note': 'muted woodland accent; source rarity is one attempt per 12 chunks',
    },
    {
        'file': 'zz_tree_13_feywild_spring.json',
        'feature': 'alfheim:tree_feywild_spring',
        'source_feature': 'feywild:spring_tree_placed',
        'biomes': ['alfheim:bloomfall_vale', 'mythicbotany:alfheim_plains'],
        'note': 'flowering temperate biomes; source rarity is one attempt per 12 chunks',
    },
    {
        'file': 'zz_tree_14_feywild_summer.json',
        'feature': 'alfheim:tree_feywild_summer',
        'source_feature': 'feywild:summer_tree_placed',
        'biomes': ['mythicbotany:golden_fields'],
        'note': 'warm open biome; source rarity is one attempt per 12 chunks',
    },
    {
        'file': 'zz_tree_15_feywild_winter.json',
        'feature': 'alfheim:tree_feywild_winter',
        'source_feature': 'feywild:winter_tree_placed',
        'biomes': ['alfheim:starved_reach', 'mythicbotany:alfheim_hills'],
        'note': 'cold uplands; source rarity is one attempt per 12 chunks',
    },
)


def write_json(path, obj, dry_run):
    if dry_run:
        print(f'  [dry] {path}')
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def read_installed_placed_feature(feature):
    namespace, path = feature.split(':', 1)
    member = f'data/{namespace}/worldgen/placed_feature/{path}.json'
    for jar_path in sorted(glob.glob(os.path.join('mods', '*.jar'))):
        try:
            with zipfile.ZipFile(jar_path) as jar:
                if member in jar.namelist():
                    return json.loads(jar.read(member)), os.path.basename(jar_path)
        except (OSError, zipfile.BadZipFile, ValueError):
            continue
    raise SystemExit(f'installed placed feature not found: {feature}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    print('Alfheim restrained tree worldgen')
    for placement in PLACEMENTS:
        source_doc, source_jar = read_installed_placed_feature(placement['source_feature'])
        local_path = placement['feature'].split(':', 1)[1]
        # A local placed-feature identity prevents the source mods' vanilla-biome ordering
        # constraints from forming a cycle through Alfheim. Its configured feature and every
        # placement predicate remain byte-for-byte equivalent to the installed source JSON.
        write_json(os.path.join(PLACED_OUT, f'{local_path}.json'), source_doc, args.dry_run)
        path = os.path.join(OUT, placement['file'])
        write_json(path, {
            'type': 'forge:add_features',
            'biomes': placement['biomes'],
            'features': placement['feature'],
            'step': 'vegetal_decoration',
        }, args.dry_run)
        print(f"  {placement['feature']:<40} -> {', '.join(placement['biomes'])}")
        print(f"    mirrors {placement['source_feature']} from {source_jar}")
        print(f"    {placement['note']}")

    print('\n  TaxTreeGiant placement: disabled by field-review decision')
    print('  Dense Feywild groupings: reserved for future pixie sky islands')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
