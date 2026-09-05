"""Liquid Bifrost -- a new fluid, its refinement chain, and its conversions.

Asked for by the user 2026-09-04:

    "Let's call it 'liquid bifrost' pools as a new surface feature for the lakes, as a new
     liquid material. It should have the same similar colour tuning properties as the bifrost
     blocks, and it should have a crystallized form and a condensed form and a refined form and
     then a distilled form as the final product, and it should be useful for converting to the
     various types of mana essence from the different magical mods."

    python tools/gen_liquid_bifrost.py
    python tools/gen_liquid_bifrost.py --dry-run

WHAT THIS IS FOR
----------------
Every magic system in the pack has its own currency -- Botania mana, Ars source, Occultism
essence, Iron's arcane, Nature's Aura. `MAGIC_SYSTEMS.md` indexes thirteen of them, and they
do not talk to each other. A player deep in one is starting from nothing in the next, which is
what makes a thirteen-system pack read as thirteen packs.

Liquid Bifrost is the bridge, and it is deliberately a BAD exchange rate. It is not a way to
skip a system; it is a way to carry a little momentum into one. The distilled tier converts at
a loss, and every conversion costs a tier of refinement that had to be built first.

WHY A FLUID AND NOT AN ORE
--------------------------
The user asked for pools on the lakes, and that is the right shape: `ORE_SUPPLEMENTATION.md`
already owns twelve blooms and seven geodes, all of them dug. A surface liquid is a different
verb -- found by looking rather than by mining -- and it gives the Void Verge and the lake
biomes something to be good at.

FEASIBILITY, CHECKED BEFORE BUILDING
------------------------------------
KubeJS 2001.6.5 ships `FluidBuilder` / `FlowingFluidBuilder` / `FluidBlockBuilder` /
`FluidBucketItemBuilder`, so `StartupEvents.registry('fluid', ...)` registers a real flowing
fluid with a block and a bucket. The builder methods used below -- color, bucketColor,
luminosity, density, viscosity, temperature, thickTexture, thinTexture, translucent, tag,
displayName -- were read off FluidBuilder.class rather than assumed, because a misspelled
builder method on a startup script takes the whole registry down.

THE COLOUR
----------
Botania's bifrost cycles the rainbow per-frame; a fluid tint is a single ARGB and cannot. So
the fluid takes bifrost's *character* rather than its animation: a high-luminosity pale cyan
that shifts violet in the flowing texture, which is what bifrost looks like at any one instant.
"""
import argparse
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_items import tint, load_base, CLIENT_JAR  # noqa: E402

NS = 'alfheim'
STARTUP = os.path.join('kubejs', 'startup_scripts')
SERVER = os.path.join('kubejs', 'server_scripts')
DATA = os.path.join('kubejs', 'data', NS)
TEX_OUT = os.path.join('kubejs', 'assets', NS, 'textures', 'item')
MODEL_OUT = os.path.join('kubejs', 'assets', NS, 'models', 'item')

FLUID = f'{NS}:liquid_bifrost'

# --- the refinement chain ----------------------------------------------------------------------
#
# Four tiers, in the user's own words and order. Each step is a DIFFERENT method, and each
# method is one the player has already been taught by the era the tier belongs to -- the
# ordering standard set on 2026-09-04: "when a recipe requires a method it should verify that
# you have previously unlocked that method in some preceding step".
#
#   crystallized  Era II   petal apothecary      the first station the pack teaches
#   condensed     Era II   mana infusion         Botania's own, already on the ladder
#   refined       Era III  alfheim mana infuser  MythicBotany's, gated behind the gate
#   distilled     Era III  runic altar           the last station before Era IV
# ART. Each tier takes a DIFFERENT silhouette rather than four recolours of one shape -- a
# player should be able to tell the tiers apart in a crowded inventory without reading a
# tooltip, and hue alone does not survive a full hotbar. Shard -> cut gem -> sphere -> finished
# gem reads as refinement by outline alone.
#
# The hue walks cyan to violet across the chain, which is the same journey the fluid's own
# colour makes between its still and flowing textures: raw bifrost is cyan, worked bifrost is
# violet. `sat_floor` matters because two of the bases are nearly white, and multiplying a
# near-zero saturation leaves the hue rotation invisible -- the lesson gen_items.py records.
TIERS = [
    {'id': 'crystallized_bifrost', 'name': 'Crystallized Bifrost', 'era': 2,
     'tooltip': 'The pool, given a shape. It still hums.',
     'rarity': 'common',
     'base': 'amethyst_shard.png', 'hue': 188, 'sat': 1.05, 'val': 1.08, 'sat_floor': 0.50},
    {'id': 'condensed_bifrost', 'name': 'Condensed Bifrost', 'era': 2,
     'tooltip': 'Four crystals pressed into one. The hum is lower now.',
     'rarity': 'uncommon',
     'base': 'diamond.png', 'hue': 205, 'sat': 1.10, 'val': 1.02, 'sat_floor': 0.55},
    {'id': 'refined_bifrost', 'name': 'Refined Bifrost', 'era': 3,
     'tooltip': 'The impurities are gone. What is left is only the bridge.',
     'rarity': 'uncommon',
     'base': 'botania:mana_pearl.png', 'hue': 228, 'sat': 1.05, 'val': 1.10,
     'sat_floor': 0.55},
    {'id': 'distilled_bifrost', 'name': 'Distilled Bifrost', 'era': 3,
     'tooltip': 'The final form. It will become whatever magic you ask it to.',
     'rarity': 'rare',
     'base': 'botania:mana_diamond.png', 'hue': 268, 'sat': 1.15, 'val': 1.18,
     'sat_floor': 0.60},
]

# --- conversions -------------------------------------------------------------------------------
#
# One distilled bifrost into each system's ENTRY currency, never its advanced one. Every id here
# was checked against tools/registry_items.json -- the ground-truth dump from a running server,
# not a lang file. That distinction has already cost this project eleven recipes.
#
# The rates are deliberately poor. A player who has built the chain gets a foothold in a new
# system, not a bypass of it: `INSTRUCTIONS.md` 2.3 keeps power on the spine.
CONVERSIONS = [
    {'to': 'botania:mana_powder', 'count': 6, 'system': 'Botania',
     'note': 'Mana powder is the cheapest thing mana buys, so this is a starter and not a shortcut.'},
    {'to': 'ars_nouveau:source_gem', 'count': 3, 'system': 'Ars Nouveau',
     'note': 'Source gems are the whole economy of Ars; three is one spell, not a spellbook.'},
    {'to': 'occultism:otherworld_essence', 'count': 2, 'system': 'Occultism',
     'note': 'The otherworld is the one system that should stay expensive.'},
    {'to': 'irons_spellbooks:arcane_essence', 'count': 4, 'system': "Iron's Spellbooks"},
    {'to': 'naturesaura:gold_leaf', 'count': 4, 'system': "Nature's Aura",
     'note': 'Gold leaf is the aura chain\'s first consumable.'},
    {'to': 'botania:mana_pearl', 'count': 1, 'system': 'Botania (advanced)',
     'note': 'The one advanced conversion, and it costs four distilled rather than one.',
     'cost': 4},
]


def fluid_script():
    return f'''// Alfheim Reclaimed — Liquid Bifrost, the fluid
//
// GENERATED by tools/gen_liquid_bifrost.py — do not hand-edit.
//
// A real flowing fluid: KubeJS builds the source, the flowing variant, the fluid BLOCK that
// worldgen places, and the bucket, from this one call.
//
// COLOUR. Botania's bifrost cycles the rainbow per frame. A fluid tint is one ARGB value and
// cannot cycle, so this takes bifrost's character instead of its animation — a bright pale
// cyan that reads violet where it flows, which is bifrost at any single instant.
//
// luminosity 12 rather than 15: bright enough to light its own pool and to be visible across a
// lake at night, dim enough that a player cannot use it as free full-brightness lighting.
// Lower density than water so it layers on top rather than sinking, and low viscosity so the
// pools actually spread into a pool shape instead of sitting in a one-block dimple.

StartupEvents.registry('fluid', event => {{
    // NAMESPACED on purpose. KubeJS registers a bare `event.create('liquid_bifrost')` under
    // its OWN namespace, giving kubejs:liquid_bifrost and kubejs:liquid_bifrost_bucket — and
    // every recipe below names alfheim:*, so the whole chain would have failed to resolve.
    // Every other startup script in this pack qualifies its ids for the same reason.
    event.create('{NS}:liquid_bifrost')
        .displayName('Liquid Bifrost')
        .thinTexture(0x9FE8FF)
        .color(0xB4F0FF)
        .bucketColor(0xB4F0FF)
        .luminosity(12)
        .density(900)
        .viscosity(900)
        .temperature(300)
        .translucent()
        .tag('alfheim:liquid_bifrost')
}})
'''


def items_script():
    lines = []
    for t in TIERS:
        lines.append(
            f"    event.create('{NS}:{t['id']}')"
            f".displayName('{t['name']}')"
            f".tooltip('{t['tooltip']}')"
            f".rarity('{t['rarity']}')")
    body = '\n'.join(lines)
    return f'''// Alfheim Reclaimed — the Liquid Bifrost refinement chain
//
// GENERATED by tools/gen_liquid_bifrost.py — do not hand-edit.
//
// Four tiers, in the order the user specified: crystallized → condensed → refined → distilled.
// The items are declared here and the recipes that connect them live in
// server_scripts/17_liquid_bifrost.js, because a startup script cannot write recipes.

StartupEvents.registry('item', event => {{
{body}
}})
'''


def _header(era, what):
    return f"""// Alfheim Reclaimed — Liquid Bifrost, Era {era}
//
// GENERATED by tools/gen_liquid_bifrost.py — do not hand-edit.
//
// {what}
//
// ERA-SCOPED FILENAME, ON PURPOSE. check_coverage.py reads a recipe's era from `_era<N>_` in
// its filename and can check nothing without it — the chain shipped as one un-scoped
// 17_liquid_bifrost.js and the coverage report said so directly: "24 contributive step(s)
// belong to no era ... they cannot be checked until they are era-scoped". Splitting the chain
// at its own era boundary is also honest about what it is: two tiers before the gate, two
// after.
"""


def era2_script():
    return _header(2, 'Tiers 1 and 2: the pool given a shape, then pressed.') + f'''
// THE CHAIN, PART ONE. Both steps use a station Era II has already taught, which is the
// ordering rule: a recipe may only require a method some preceding quest unlocked.
//
//   bucket of liquid bifrost  --petal apothecary-->  crystallized
//   crystallized              --mana infusion---->   condensed

ServerEvents.recipes(event => {{

    // ---- tier 1: the pool, given a shape --------------------------------------------------
    // Botania's petal apothecary is the first station the pack teaches, so the entry point to
    // a whole new material costs nothing the player has not already built.
    event.custom({{
        type: 'botania:petal_apothecary',
        ingredients: [
            {{ item: 'botania:livingrock' }},
            {{ item: 'minecraft:amethyst_shard' }},
            {{ item: 'minecraft:amethyst_shard' }},
            {{ item: 'minecraft:glowstone_dust' }},
            {{ item: 'minecraft:prismarine_crystals' }},
        ],
        // The apothecary CONSUMES its reagent, bucket and all, so the yield pays for the
        // iron. Pouring the pool in is also simply what the recipe should look like.
        reagent: {{ item: '{NS}:liquid_bifrost_bucket' }},
        output: {{ item: '{NS}:crystallized_bifrost', count: 4 }},
    }}).id('{NS}:crystallized_bifrost')

    // ---- tier 2: four into one -------------------------------------------------------------
    event.custom({{
        type: 'botania:mana_infusion',
        input: {{ item: '{NS}:crystallized_bifrost' }},
        output: {{ item: '{NS}:condensed_bifrost' }},
        mana: 4000,
    }}).id('{NS}:condensed_bifrost')
}})
'''


def era3_script():
    conv = []
    for c in CONVERSIONS:
        cost = c.get('cost', 1)
        note = c.get('note', '')
        conv.append(f'    // {c["system"]}' + (f': {note}' if note else ''))
        conv.append(
            f"    event.shapeless(Item.of('{c['to']}', {c['count']}), ["
            + ', '.join([f"'{NS}:distilled_bifrost'"] * cost)
            + f"]).id('{NS}:bifrost_to_{c['to'].replace(':', '_')}')")
    conversions = '\n'.join(conv)

    return _header(3, 'Tiers 3 and 4, and the conversions into every other magic system.') + f'''
// THE CHAIN, PART TWO — both steps behind the gate.
//
//   condensed + elf glass     --alfheim infuser-->   refined
//   2x refined + mana pearl   --runic altar------>   distilled
//
// THE CONVERSIONS are deliberately a bad rate. Liquid Bifrost is a bridge between the pack's
// thirteen magic systems (MAGIC_SYSTEMS.md), not a way around any of them — a player who
// builds the chain gets a foothold in a new system, never a shortcut past its early game.

ServerEvents.recipes(event => {{

    // ---- tier 3: the impurities out ---------------------------------------------------------
    // MythicBotany's own infuser, which sits behind the gate — so this tier is unreachable
    // until Era III on the spine rather than merely expensive.
    //
    // The type is `mythicbotany:infuser`, NOT `mythicbotany:mana_infusion`. The latter does not
    // exist: MythicBotany ships exactly one recipe type for the Alfheim infuser and it takes an
    // ingredient LIST plus fromColor/toColor for the beam, not a single `input`. Caught by E13
    // against the jars before it ever reached a server.
    event.custom({{
        type: 'mythicbotany:infuser',
        group: 'infuser',
        ingredients: [
            {{ item: '{NS}:condensed_bifrost' }},
            {{ item: 'botania:elf_glass' }},
            {{ item: 'botania:mana_powder' }},
        ],
        output: {{ item: '{NS}:refined_bifrost', count: 1 }},
        mana: 40000,
        fromColor: 11858175,
        toColor: 10185215,
    }}).id('{NS}:refined_bifrost')

    // ---- tier 4: the final form -------------------------------------------------------------
    event.custom({{
        type: 'botania:runic_altar',
        ingredients: [
            {{ item: '{NS}:refined_bifrost' }},
            {{ item: '{NS}:refined_bifrost' }},
            {{ item: 'botania:mana_pearl' }},
            {{ item: 'botania:elf_glass' }},
        ],
        output: {{ item: '{NS}:distilled_bifrost' }},
        mana: 20000,
    }}).id('{NS}:distilled_bifrost')

    // ---- conversions: one material into every system ----------------------------------------
{conversions}
}})
'''


def era7_script():
    return _header(7, 'The renewable route: make the pools instead of finding them.') + f'''
// WHY THIS EXISTS. Asked for by the user 2026-09-04: "we also need a high level renewable
// bifrost recipe, one would think using the mixer, with say water and a renewable crystal
// based ingredient."
//
// Until now Liquid Bifrost was strictly FINITE. The pools generate at 1-in-40 chunks and do not
// come back, so the bridge between thirteen magic systems was a consumable that ran out — and a
// player who spent their last bucket on the wrong conversion had permanently lost access to a
// system. That is a worse failure than the exchange rate being poor, because it is invisible
// until it has already happened.
//
// ERA VII, and that is not arbitrary: `cr_mix` (create:basin) is first taught by the Era VII
// ladder, so this is the earliest era that can require a mixer without violating the ordering
// rule. It is also the right POWER level — by Era VII a player has a working Create setup, and
// the renewable route should be a reward for that infrastructure rather than a way around the
// pools in the early game.
//
// WHAT MAKES IT RENEWABLE. `#alfheim:crystal_shards` holds exactly the six crystals that have a
// budding block, so every shard in the tag regrows. frost_shard is deliberately NOT in that tag
// — it has no budding form — which means the tag is already precisely "renewable crystal", and
// this recipe inherits that guarantee instead of restating it. Water is water. Mana powder is
// Botania's, and renewable by definition.
//
// The mana powder is the third ingredient for a reason. Crystal and water alone make a slurry;
// what makes bifrost is the charge. It is also what keeps this honest as a HIGH-level recipe:
// it costs a mana economy, not just two rocks.

ServerEvents.recipes(event => {{

    // 250 mB per mix — four mixes to the bucket, at 8 shards and 2 mana powder per bucket.
    // Deliberately not cheaper than finding a pool: this is insurance against running out,
    // not a reason to stop looking.
    event.custom({{
        type: 'create:mixing',
        heatRequirement: 'heated',
        ingredients: [
            {{ tag: '{NS}:crystal_shards' }},
            {{ tag: '{NS}:crystal_shards' }},
            {{ item: 'botania:mana_powder' }},
            {{ amount: 500, fluid: 'minecraft:water', nbt: {{}} }},
        ],
        results: [
            {{ amount: 250, fluid: '{NS}:liquid_bifrost' }},
        ],
    }}).id('{NS}:liquid_bifrost_mixing')
}})
'''


def worldgen():
    """Surface pools, as lakes.

    minecraft:lake is the vanilla feature that carves a basin and fills it, and it is what
    every vanilla lava/water lake uses -- so the pools sit in terrain properly instead of
    being a flat disc pasted on top.

    RARITY. Deliberately rarer than the geodes after their same-day retune (1-in-13 to 1-in-15
    per biome). A pool is a landmark: the whole point is that a player remembers where one is.

    Finite, and that is the point of the Era VII mixing route -- see era7_script(). These are
    what you FIND; the mixer is what you build when finding is no longer enough.
    """
    configured = {
        'type': 'minecraft:lake',
        'config': {
            'fluid': {'type': 'minecraft:simple_state_provider',
                      'state': {'Name': FLUID}},
            'barrier': {'type': 'minecraft:simple_state_provider',
                        'state': {'Name': 'botania:livingrock'}},
        },
    }
    placed = {
        'feature': f'{NS}:liquid_bifrost_pool',
        'placement': [
            {'type': 'minecraft:rarity_filter', 'chance': 40},
            {'type': 'minecraft:in_square'},
            {'type': 'minecraft:heightmap', 'heightmap': 'WORLD_SURFACE_WG'},
            {'type': 'minecraft:biome'},
        ],
    }
    # The lake biomes and the void, where the user asked for them. Not everywhere: a bridge
    # material that turns up in every biome stops being a reason to go anywhere.
    modifier = {
        'type': 'forge:add_features',
        'biomes': [
            'mythicbotany:alfheim_lakes',
            f'{NS}:mana_fen',
            f'{NS}:hollow_marches',
            f'{NS}:void_verge',
            f'{NS}:bloomfall_vale',
        ],
        'features': f'{NS}:liquid_bifrost_pool',
        'step': 'lakes',
    }
    return configured, placed, modifier


def art(dry):
    """Derive a texture and a model for each tier.

    Same pipeline gen_items.py uses for the eighty ladder intermediates: pull a real base out
    of the client jar or a mod jar and recolour it, rather than drawing from nothing. Without
    this the four items render as the missing-texture checkerboard -- KubeJS registers an item
    happily with no model at all, and nothing in the recipe or registry checks notices.
    """
    if not os.path.exists(CLIENT_JAR):
        print(f'  !! client jar not found, skipping art: {CLIENT_JAR}')
        return []
    if not dry:
        os.makedirs(TEX_OUT, exist_ok=True)
        os.makedirs(MODEL_OUT, exist_ok=True)

    made = []
    jar = zipfile.ZipFile(CLIENT_JAR)
    try:
        for t in TIERS:
            img = tint(load_base(jar, t['base']), t['hue'], t['sat'], t['val'],
                       t.get('sat_floor', 0.5))
            tex = os.path.join(TEX_OUT, t['id'] + '.png')
            mdl = os.path.join(MODEL_OUT, t['id'] + '.json')
            if not dry:
                img.save(tex)
                with open(mdl, 'w', encoding='utf-8') as f:
                    json.dump({'parent': 'minecraft:item/generated',
                               'textures': {'layer0': f'{NS}:item/{t["id"]}'}}, f, indent=2)
            made += [tex, mdl]
            print(f"  art        {t['id']:22} <- {t['base']}")
    finally:
        jar.close()
    return made


def tags():
    """Item tags, so the chain is addressable by something other than four literal ids.

    `alfheim:bifrost` covers the whole chain; `alfheim:bifrost/distilled` is the one the
    conversions consume. A tag is what lets a later quest, a later recipe or another mod name
    "any tier" without being rewritten every time a tier is added.
    """
    return {
        os.path.join(DATA, 'tags', 'items', 'bifrost.json'):
            {'replace': False, 'values': [f'{NS}:{t["id"]}' for t in TIERS]},
        os.path.join(DATA, 'tags', 'items', 'bifrost_distilled.json'):
            {'replace': False, 'values': [f'{NS}:distilled_bifrost']},
    }


def write(path, data, dry):
    if not dry:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    dry = a.dry_run

    # An earlier run wrote the whole chain to one un-scoped file. Remove it, or KubeJS loads
    # both and every recipe is defined twice.
    stale = os.path.join(SERVER, '17_liquid_bifrost.js')
    if os.path.exists(stale) and not dry:
        os.remove(stale)
        print(f'  removed    {stale} (superseded by the era-scoped pair)')

    files = []
    for path, text in (
        (os.path.join(STARTUP, '15_liquid_bifrost.js'), fluid_script()),
        (os.path.join(STARTUP, '16_bifrost_chain.js'), items_script()),
        (os.path.join(SERVER, '18_era2_liquid_bifrost.js'), era2_script()),
        (os.path.join(SERVER, '19_era3_liquid_bifrost.js'), era3_script()),
        (os.path.join(SERVER, '20_era7_liquid_bifrost.js'), era7_script()),
    ):
        if not dry:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
        files.append(path)
        print(f'  script     {path}')

    files += art(dry)

    for path, data in tags().items():
        files.append(write(path, data, dry))
        print(f'  tag        {path}')

    configured, placed, modifier = worldgen()
    files.append(write(os.path.join(DATA, 'worldgen', 'configured_feature',
                                    'liquid_bifrost_pool.json'), configured, dry))
    files.append(write(os.path.join(DATA, 'worldgen', 'placed_feature',
                                    'liquid_bifrost_pool.json'), placed, dry))
    files.append(write(os.path.join(DATA, 'forge', 'biome_modifier',
                                    'liquid_bifrost_pool.json'), modifier, dry))
    for p in files[-3:]:
        print(f'  worldgen   {p}')

    print(f'\n  renewable route: create:mixing from #{NS}:crystal_shards (era VII)')
    print(f'  fluid {FLUID}; {len(TIERS)} tiers; {len(CONVERSIONS)} conversions into '
          f'{len({c["system"].split(" (")[0] for c in CONVERSIONS})} magic systems; '
          f'pools in {len(modifier["biomes"])} biome(s) at 1-in-{placed["placement"][0]["chance"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
