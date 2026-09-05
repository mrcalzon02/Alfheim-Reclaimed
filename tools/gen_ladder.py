"""Generate the tier ladder: intermediates and their recipe chains, Eras III-X.

Steps per era are 2n-3 (III=3 ... X=17), and each era's chain consumes the previous era's tier
material, so the transitive depth accumulates to ~80 steps and ~80 intermediates.

Hand-writing that is not realistic, so the ladder is declared here as data and emitted as:
  * entries appended to tools/items_manifest.json  (gen_items.py turns them into assets)
  * one KubeJS recipe script per era

Station rotation is drawn from PROCESS_INDEX.md. Each era introduces at least one station the
player has not used, per CAMPAIGN_ERAS.md §1b rule 2, and eras alternate between the two
traditions so neither completes a chain alone (TWIN_SPINES.md §2).

    python tools/gen_ladder.py            # write manifest entries + recipe scripts
    python tools/gen_ladder.py --dry-run
"""
import argparse
import colorsys
import json
import os

MANIFEST = os.path.join('tools', 'items_manifest.json')
SCRIPTS = os.path.join('kubejs', 'server_scripts')
NS = 'alfheim'


def steps_for(era):
    return 2 * era - 3


# --- station vocabulary -------------------------------------------------------------------
# (key, kind) — kind drives which recipe shape gets emitted.
STATIONS = {
    'apothecary':  ('botania:petal_apothecary', 'petal'),
    'mana_pool':   ('botania:mana_infusion', 'infusion'),
    'runic_altar': ('botania:runic_altar', 'runic'),
    'terra_plate': ('botania:terra_plate', 'terra'),
    'gate':        ('botania:elven_trade', 'trade'),
    'brew':        ('botania:brew', 'shaped'),
    'infuser':     ('mythicbotany:infuser', 'infusion'),
    'imbuement':   ('ars_nouveau:imbuement', 'shaped'),
    'apparatus':   ('ars_nouveau:enchanting_apparatus', 'shaped'),
    'crush':       ('ars_nouveau:crush', 'shaped'),
    'na_altar':    ('naturesaura:altar', 'shaped'),
    'na_tree':     ('naturesaura:tree_ritual', 'shaped'),
    'occ_crush':   ('occultism:crushing', 'shaped'),
    'occ_fire':    ('occultism:spirit_fire', 'shaped'),
    'fey_altar':   ('feywild:fey_altar', 'shaped'),
    'cr_mill':     ('create:milling', 'shaped'),
    'cr_mix':      ('create:mixing', 'shaped'),
    'cr_press':    ('create:pressing', 'shaped'),
    'cr_deploy':   ('create:deploying', 'shaped'),
    'cr_seq':      ('create:sequenced_assembly', 'shaped'),
    'smelt':       ('minecraft:smelting', 'smelt'),
    'craft':       ('minecraft:crafting_shaped', 'shaped'),
}

# --- the ladder ---------------------------------------------------------------------------
# tier: the era's final material. chain: the intermediates leading to it.
# Chains are shorter than the step count because the *first* steps of each era are the
# previous era's chain, consumed as input — that is what makes the depth accumulate.
LADDER = [
    dict(era=4, tier='gatewrought_cord', tier_name='Gatewrought Cord',
         hue=45, sat=1.2, val=1.05, base='string.png',
         tooltip='Era IV. Elven work, finished on the far side of the gate.',
         stations=['apothecary', 'mana_pool', 'gate', 'apparatus', 'runic_altar'],
         parts=['sunbleached_floss', 'traded_skein']),

    dict(era=5, tier='elementium_core', tier_name='Elementium Core',
         hue=140, sat=1.4, val=1.1, base='botania:elementium_ingot.png',
         tooltip='Era V. Mined, smelted and sung to. Ours from the ground up.',
         stations=['smelt', 'cr_mill', 'mana_pool', 'infuser', 'apparatus', 'runic_altar', 'craft'],
         parts=['raw_alloy_grit', 'annealed_plate', 'core_blank']),

    dict(era=6, tier='wildmarch_sinew', tier_name='Wildmarch Sinew',
         hue=25, sat=1.3, val=0.95, base='minecraft:phantom_membrane.png',
         tooltip='Era VI. Taken from the frontier, and it has not forgiven you.',
         stations=['fey_altar', 'na_altar', 'apothecary', 'gate', 'crush', 'mana_pool',
                   'apparatus', 'runic_altar', 'craft'],
         parts=['march_hide', 'fey_bound_cord', 'sinew_braid', 'warded_sinew']),

    dict(era=7, tier='emberbound_weave', tier_name='Emberbound Weave',
         hue=15, sat=1.6, val=1.15, base='minecraft:blaze_powder.png',
         tooltip='Era VII. It remembers the fire and has agreed to hold it.',
         stations=['occ_fire', 'cr_mix', 'smelt', 'brew', 'mana_pool', 'apparatus',
                   'na_tree', 'gate', 'runic_altar', 'infuser', 'craft'],
         parts=['scorched_filament', 'quenched_thread', 'ember_lattice', 'bound_weave',
                'tempered_weave']),

    dict(era=8, tier='rimebound_lattice', tier_name='Rimebound Lattice',
         hue=195, sat=1.4, val=1.2, base='minecraft:prismarine_shard.png',
         tooltip='Era VIII. Cold enough to keep a memory intact.',
         stations=['cr_press', 'crush', 'mana_pool', 'imbuement', 'apparatus', 'na_altar',
                   'occ_crush', 'gate', 'runic_altar', 'cr_seq', 'infuser', 'terra_plate',
                   'craft'],
         parts=['frost_shard', 'silvered_flake', 'archive_leaf', 'rime_cord', 'lattice_blank',
                'sealed_lattice']),

    dict(era=9, tier='gravegilt_thread', tier_name='Grave-Gilt Thread',
         hue=280, sat=1.3, val=0.9, base='minecraft:phantom_membrane.png',
         tooltip='Era IX. Spun from what it cost. Do not wear it lightly.',
         stations=['occ_fire', 'occ_crush', 'na_altar', 'brew', 'mana_pool', 'apothecary',
                   'apparatus', 'imbuement', 'gate', 'cr_seq', 'runic_altar', 'infuser',
                   'terra_plate', 'na_tree', 'craft'],
         parts=['ash_of_names', 'mourning_dust', 'gilded_ash', 'debt_cord', 'reckoned_thread',
                'grave_braid', 'settled_thread']),

    dict(era=10, tier='crown_filament', tier_name='Crown Filament',
         hue=52, sat=1.5, val=1.25, base='minecraft:nether_star.png',
         tooltip='Era X. The crown of the world tree, drawn out to a thread.',
         stations=['apothecary', 'mana_pool', 'runic_altar', 'infuser', 'terra_plate',
                   'apparatus', 'imbuement', 'na_tree', 'fey_altar', 'occ_fire', 'gate',
                   'cr_seq', 'cr_mix', 'crush', 'brew', 'na_altar', 'craft'],
         parts=['heartwood_strand', 'crowned_fibre', 'yggdrasil_floss', 'branch_cord',
                'living_crown', 'woven_crown', 'ninefold_thread', 'crown_blank']),
]

PREV_TIER = {4: 'verdant_filament', 5: 'gatewrought_cord', 6: 'elementium_core',
             7: 'wildmarch_sinew', 8: 'emberbound_weave', 9: 'rimebound_lattice',
             10: 'gravegilt_thread'}

# Bases cycled for intermediates, so a chain does not look like eight copies of one icon.
PART_BASES = ['string.png', 'minecraft:phantom_membrane.png', 'minecraft:amethyst_shard.png',
              'minecraft:prismarine_shard.png', 'minecraft:glow_ink_sac.png',
              'minecraft:sugar.png', 'minecraft:brick.png', 'minecraft:copper_ingot.png']


def pretty(key):
    return ' '.join(w.capitalize() for w in key.replace('_', ' ').split())


# Suffixes used to pad a hand-written part list out to the full 2n-4 length. The named parts
# carry the era's flavour; these carry its depth.
PAD = ['drawn', 'folded', 'stilled', 'rebound', 'quenched', 'layered', 'proofed', 'settled',
       'trued', 'sealed', 'wound', 'finished']


def parts_for(L):
    """A chain of 2n-3 steps needs 2n-4 intermediates plus the tier material."""
    want = steps_for(L['era']) - 1
    parts = list(L['parts'])
    stem = L['tier'].rsplit('_', 1)[0]
    i = 0
    while len(parts) < want:
        parts.append(f'{stem}_{PAD[i % len(PAD)]}' if i < len(PAD)
                     else f'{stem}_stage{i}')
        i += 1
    return parts[:want]


def chain_for(L):
    """The era's full output sequence: its intermediates, then its tier material."""
    return parts_for(L) + [L['tier']]


def station_at(L, i):
    """The station step i draws. build_items and build_script must agree on this, so
    both ask here rather than each re-deriving the rotation."""
    return L['stations'][i % len(L['stations'])]


def seq_transitionals(L):
    """Outputs whose step runs on Create's sequenced assembler.

    That recipe type needs a registered `transitionalItem` to carry progress between
    sub-steps -- an incomplete form of the output, the way Create ships
    `create:incomplete_track`. They are real items and must reach the item registry,
    so they are emitted into the manifest alongside the chain itself.
    """
    return [item for i, item in enumerate(chain_for(L)) if station_at(L, i) == 'cr_seq']


def transitional_id(item):
    return f'incomplete_{item}'


def hsv_int(hue, sat, val):
    """Pack an HSV colour into the 0xRRGGBB int MythicBotany's infuser asks for.

    `hue` is the ladder's own degrees on the wheel. `sat`/`val` are true 0..1 HSV here
    and deliberately NOT the manifest's `sat`/`val`, which exceed 1.0 because they are
    texture-recolour multipliers and mean something else entirely.
    """
    r, g, b = colorsys.hsv_to_rgb((hue % 360) / 360.0, sat, val)
    return (int(r * 255) << 16) | (int(g * 255) << 8) | int(b * 255)


def build_items():
    out = []
    for L in LADDER:
        era, n = L['era'], steps_for(L['era'])
        for i, part in enumerate(parts_for(L)):
            out.append({
                'id': part, 'name': pretty(part), 'era': era, 'step': i + 1,
                'base': PART_BASES[i % len(PART_BASES)],
                'hue': (L['hue'] + i * 14) % 360,
                'sat': round(max(0.6, L['sat'] - i * 0.06), 2),
                'val': round(min(1.35, L['val'] + i * 0.03), 2),
                'tooltip': f'Era {era} intermediate.',
            })
        # Offset from the parts so the tier item never renders identically to step 1.
        out.append({
            'id': L['tier'], 'name': L['tier_name'], 'era': era, 'step': n, 'tier': True,
            'rarity': 'rare' if era >= 8 else 'uncommon',
            'base': L['base'], 'hue': L['hue'],
            'sat': round(min(2.0, L['sat'] + 0.25), 2),
            'val': round(min(1.4, L['val'] + 0.12), 2),
            'tooltip': L['tooltip'],
        })
        # Create's sequenced assembler needs a registered item to carry progress between
        # sub-steps. Half-finished work: duller and darker than the thing it becomes, so
        # it reads as unfinished in the inventory rather than as a second tier material.
        for item in seq_transitionals(L):
            out.append({
                'id': transitional_id(item), 'name': f'Unfinished {pretty(item)}',
                'era': era, 'step': chain_for(L).index(item) + 1, 'transitional': True,
                'base': 'minecraft:brick.png', 'hue': L['hue'],
                'sat': round(max(0.4, L['sat'] - 0.5), 2),
                'val': round(max(0.5, L['val'] - 0.35), 2),
                'tooltip': 'Still on the assembler. It is not finished with you yet.',
            })
    return out


def recipe_for(kind, station, inputs, output, count=1, hue=0):
    """Emit a KubeJS custom-recipe literal in the station's own recipe format.

    An earlier version fell back to event.shaped() for anything it did not special-case,
    which silently collapsed every Ars Nouveau / Nature's Aura / Occultism / Feywild /
    Create step into a vanilla crafting recipe. The whole point of the ladder is that each
    step is a different machine, so every station now emits its real type.
    """
    ins = ', '.join(f"{{ item: '{i}' }}" for i in inputs)
    first = inputs[0]
    second = inputs[1] if len(inputs) > 1 else inputs[0]

    # ---- Botania -------------------------------------------------------------------
    if kind == 'petal':
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredients: [{ins}],\n"
                f"            output: {{ item: '{output}', count: {count} }},\n"
                f"            reagent: {{ tag: 'botania:seed_apothecary_reagent' }} }})")
    if kind == 'infusion' and station.startswith('botania'):
        return (f"        event.custom({{ type: '{station}',\n"
                f"            input: {{ item: '{first}' }}, mana: 12000,\n"
                f"            output: {{ item: '{output}' }} }})")
    if kind == 'runic':
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredients: [{ins}], mana: 18000,\n"
                f"            output: {{ item: '{output}', count: {count} }} }})")
    if kind == 'terra':
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredients: [{ins}], mana: 250000,\n"
                f"            result: {{ item: '{output}' }} }})")
    if kind == 'trade':
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredients: [{ins}],\n"
                f"            output: [{{ item: '{output}' }}] }})")
    if station == 'botania:brew':
        return (f"        event.shapeless('{output}', ['{first}', '{second}'])")

    # ---- MythicBotany --------------------------------------------------------------
    if station == 'mythicbotany:infuser':
        # Schema read from MythicBotany-1.20.1-4.0.4.jar (alfsteel_ingot, terrasteel_ingot):
        # the input key is `ingredients`, not `input`, and fromColor/toColor are mandatory
        # ints. Emitting `input:` with neither colour is what got all five of these
        # rejected at load with "Missing fromColor, expected to find a Int" -- B-41.
        # The beam runs from a dull form of the era's own hue to a bright one.
        return (f"        event.custom({{ type: '{station}',\n"
                f"            group: 'alfheim_ladder',\n"
                f"            ingredients: [{ins}], mana: 400000,\n"
                f"            fromColor: {hsv_int(hue, 0.55, 0.45)},"
                f" toColor: {hsv_int(hue, 0.85, 0.98)},\n"
                f"            output: {{ item: '{output}' }} }})")

    # ---- Ars Nouveau ---------------------------------------------------------------
    if station == 'ars_nouveau:enchanting_apparatus':
        peds = ', '.join(f"{{ item: '{i}' }}" for i in (inputs + ['botania:dreamwood'])[:3])
        return (f"        event.custom({{ type: '{station}',\n"
                f"            reagent: [{{ item: '{first}' }}],\n"
                f"            pedestalItems: [{peds}],\n"
                f"            output: {{ item: '{output}' }},\n"
                f"            sourceCost: 2000, keepNbtOfReagent: false }})")
    if station == 'ars_nouveau:imbuement':
        return (f"        event.custom({{ type: '{station}',\n"
                f"            input: {{ item: '{first}' }}, count: {count},\n"
                f"            output: '{output}', source: 3000,\n"
                f"            pedestalItems: [] }})")
    if station == 'ars_nouveau:crush':
        return (f"        event.custom({{ type: '{station}',\n"
                f"            input: {{ item: '{first}' }},\n"
                f"            output: [{{ item: '{output}', count: {count}, chance: 1.0,"
                f" maxRange: 1 }}],\n"
                f"            skip_block_place: false }})")

    # ---- Nature's Aura -------------------------------------------------------------
    if station == 'naturesaura:altar':
        return (f"        event.custom({{ type: '{station}',\n"
                f"            input: {{ item: '{first}' }},\n"
                f"            output: {{ item: '{output}' }},\n"
                f"            aura: 30000, time: 200 }})")
    if station == 'naturesaura:tree_ritual':
        ritual = ', '.join(f"{{ item: '{i}' }}" for i in
                           (inputs + ['botania:dreamwood', 'naturesaura:gold_leaf'])[:5])
        return (f"        event.custom({{ type: '{station}',\n"
                f"            sapling: {{ item: 'minecraft:oak_sapling' }},\n"
                f"            ingredients: [{ritual}],\n"
                f"            output: {{ item: '{output}' }}, time: 400 }})")

    # ---- Occultism -----------------------------------------------------------------
    if station == 'occultism:crushing':
        # All 180 crushing recipes in the Occultism jar set ignore_crushing_multiplier;
        # omitting it left ours the only ones without it.
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredient: {{ item: '{first}' }},\n"
                f"            result: {{ item: '{output}', count: {count} }},\n"
                f"            ignore_crushing_multiplier: false,\n"
                f"            crushing_time: 200 }})")
    if station == 'occultism:spirit_fire':
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredient: {{ item: '{first}' }},\n"
                f"            result: {{ item: '{output}' }} }})")

    # ---- Feywild -------------------------------------------------------------------
    if station == 'feywild:fey_altar':
        # Five, not four. All 29 fey_altar recipes in feywild-1.20.1-5.5.5.jar use exactly
        # five ingredients and none uses four, so the altar's slot count is five. B-42 read
        # the JEI crash the other way round -- "Index 4 out of bounds for length 4" in
        # FeyAltarRecipeCategory is the category reaching for a fifth slot that our
        # four-ingredient array does not have, so we were short an ingredient, not over.
        alt = ', '.join(f"{{ item: '{i}' }}" for i in
                        (inputs + ['botania:dreamwood', 'minecraft:gold_ingot',
                                   'botania:livingrock'])[:5])
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredients: [{alt}],\n"
                f"            output: {{ item: '{output}', count: {count} }} }})")

    # ---- Create --------------------------------------------------------------------
    # One emitter per type. The single `create:*` emitter this replaces gave every type
    # two ingredients and a processingTime, which milling and pressing both reject on
    # arity and which sequenced assembly does not even have a field for -- B-41.
    #
    # Arities and fields below are counted, not assumed, across all 396 Create recipes
    # in create-1.20.1-6.0.8.jar:
    #   milling    231 recipes, ingredients always 1, processingTime always present
    #   pressing    39 recipes, ingredients always 1, processingTime never present
    #   mixing      14 recipes, ingredients 1-5,      processingTime never present
    #   deploying  112 recipes, ingredients always 2, processingTime never present
    if station == 'create:milling':
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredients: [{{ item: '{first}' }}],\n"
                f"            processingTime: 200,\n"
                f"            results: [{{ item: '{output}', count: {count} }}] }})")
    if station == 'create:pressing':
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredients: [{{ item: '{first}' }}],\n"
                f"            results: [{{ item: '{output}', count: {count} }}] }})")
    if station == 'create:mixing':
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredients: [{ins}],\n"
                f"            results: [{{ item: '{output}', count: {count} }}] }})")
    if station == 'create:deploying':
        held = second if len(inputs) > 1 else 'botania:dreamwood'
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredients: [{{ item: '{first}' }}, {{ item: '{held}' }}],\n"
                f"            keepHeldItem: false,\n"
                f"            results: [{{ item: '{output}', count: {count} }}] }})")
    if station == 'create:sequenced_assembly':
        # A different shape from every other Create type: a singular `ingredient`, a
        # registered `transitionalItem` that carries progress between sub-steps, `loops`,
        # `results`, and a `sequence` of sub-recipes that each consume and return the
        # transitional item. We were emitting ingredients/processingTime/results, so
        # transitionalItem resolved to null -- the "Item cannot be null" of B-41.
        t = f'{NS}:{transitional_id(output.split(":", 1)[1])}'
        return (f"        event.custom({{ type: '{station}',\n"
                f"            ingredient: {{ item: '{first}' }},\n"
                f"            transitionalItem: {{ item: '{t}' }},\n"
                f"            loops: 2,\n"
                f"            results: [{{ item: '{output}', count: {count} }}],\n"
                f"            sequence: [\n"
                f"                {{ type: 'create:deploying',\n"
                f"                    ingredients: [{{ item: '{t}' }},"
                f" {{ item: 'botania:dreamwood' }}],\n"
                f"                    keepHeldItem: false,\n"
                f"                    results: [{{ item: '{t}' }}] }},\n"
                f"                {{ type: 'create:pressing',\n"
                f"                    ingredients: [{{ item: '{t}' }}],\n"
                f"                    results: [{{ item: '{t}' }}] }}\n"
                f"            ] }})")

    # ---- vanilla -------------------------------------------------------------------
    if kind == 'smelt':
        return f"        event.smelting('{output}', '{first}')"
    return (f"        event.shaped('{output}', ['AB', 'BA'], "
            f"{{ A: '{first}', B: '{second}' }})")


def build_script(L):
    era, n = L['era'], steps_for(L['era'])
    chain = chain_for(L)
    prev = PREV_TIER[era]
    lines = [
        f'// Alfheim Reclaimed — Era {era}: tier ladder',
        '//',
        f'// GENERATED by tools/gen_ladder.py — do not hand-edit.',
        f'// {n} steps (2n-3). Chain consumes the Era {era - 1} tier material, so transitive',
        f'// depth accumulates. Stations rotate so each step is a different process.',
        '',
        'ServerEvents.recipes(event => {',
        f"    const id = s => `alfheim:era{era}/${{s}}`",
        '',
    ]
    for i, out_item in enumerate(chain):
        st_key = station_at(L, i)
        station, kind = STATIONS[st_key]
        if i == 0:
            ins = [f'{NS}:{prev}', 'botania:dreamwood']
        else:
            ins = [f'{NS}:{chain[i - 1]}']
            if kind in ('petal', 'runic', 'terra', 'shaped'):
                ins.append('botania:dreamwood' if i % 2 else 'botania:livingrock')
        lines.append(f'    // step {i + 1}/{len(chain)} — {st_key}')
        lines.append('    {')
        lines.append(recipe_for(kind, station, ins, f'{NS}:{out_item}', hue=L['hue']))
        lines.append(f"            .id(id('{out_item}'))")
        lines.append('    }')
        lines.append('')
    lines.append(f"    console.info('[Alfheim Reclaimed] Era {era} tier ladder loaded.')")
    lines.append('})')
    lines.append('')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    manifest = json.load(open(MANIFEST, encoding='utf-8'))
    existing = {it['id'] for it in manifest['items']}
    new = [it for it in build_items() if it['id'] not in existing]
    manifest['items'].extend(new)

    total_steps = sum(steps_for(L['era']) for L in LADDER) + 3
    print(f'ladder: eras III-X, {total_steps} steps, {len(manifest["items"])} items total')
    for L in LADDER:
        print(f"  era {L['era']:>2}  {steps_for(L['era']):>2} steps  "
              f"{len(parts_for(L)) + 1} items  tier={L['tier']}")

    if a.dry_run:
        return 0

    with open(MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')
    print(f'\n  +{len(new)} manifest entries')

    for L in LADDER:
        p = os.path.join(SCRIPTS, f"2{L['era']}_era{L['era']}_tier_ladder.js")
        with open(p, 'w', encoding='utf-8') as f:
            f.write(build_script(L))
        print('  wrote', p)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
