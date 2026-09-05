"""Give every custom item 2-6 genuine uses beyond feeding the next ladder step.

Without this each of the 80 intermediates has exactly one purpose — hand it to the next
recipe — which makes them inventory tokens rather than materials. A material earns its place
by being useful in more than one direction.

Six use families, all producing items that already exist so the roster does not grow:

  multiplier   ore/raw + item -> extra ingots. The classic reason to keep a stack around.
  edible       nourishment; elven field rations
  restorative  healing and repair consumables
  enhancer     feeds the magic economies (mana powder, source gems, aura)
  reagent      brewing and ritual inputs
  shortcut     4x an intermediate -> the NEXT intermediate, skipping a station at a cost

Which families an item gets is derived deterministically from its id, so regenerating is
stable, but the spread is varied across the roster.

    python tools/gen_item_uses.py
    python tools/gen_item_uses.py --report
"""
import argparse
import hashlib
import json
import os

MANIFEST = os.path.join('tools', 'items_manifest.json')
OUT = os.path.join('kubejs', 'server_scripts', '30_item_uses.js')
NS = 'alfheim'

# Raw ore doubled by spending an intermediate as the catalyst. Every entry must be a
# genuine raw -> ingot conversion: an ingot that yields more of the same ingot is a
# duplication loop, which is what the first two revisions of this table shipped.
MULTIPLIER = [
    # Retargeted 2026-09-03 onto the Twelve Blooms (B-48). These used to consume
    # minecraft:raw_iron and friends, which stopped having a source in Alfheim the moment
    # the vanilla ore layer was retired -- so 48 recipes quietly became Midgard-only.
    # A Quickened bloom is the right input anyway: it is the form that has already taken a
    # Rite, so doubling it reads as "the pattern is open, push more through it".
    ('alfheim:quickened_palebloom', 'minecraft:iron_ingot', 2),
    ('alfheim:quickened_verdigris', 'minecraft:copper_ingot', 3),
    ('alfheim:quickened_sunbloom', 'minecraft:gold_ingot', 2),
    ('alfheim:quickened_silverthorn', 'occultism:silver_ingot', 2),
    ('alfheim:quickened_rimebloom', 'minecraft:diamond', 2),
    ('mythicbotany:raw_elementium', 'botania:elementium_ingot', 2),
]

EDIBLE = [
    ('minecraft:bread', 'minecraft:golden_carrot', 1),
    ('minecraft:apple', 'minecraft:golden_apple', 1),
    ('minecraft:melon_slice', 'minecraft:glistering_melon_slice', 3),
    ('farmersdelight:pumpkin_slice', 'minecraft:golden_carrot', 2),
]

RESTORATIVE = [
    ('alfheim:quickened_sparkroot', 'minecraft:glistering_melon_slice', 2),
    ('alfheim:quickened_grievebloom', 'minecraft:golden_apple', 1),
    ('botania:mana_powder', 'minecraft:golden_carrot', 4),
]

# Crystal shards enter here. Each alignment feeds the economy it belongs to, which is the
# whole point of giving them alignments: Dawnglass into mana, Galeglass into Source,
# Rootglass into Aura. Before this the six crystals had zero uses anywhere in the pack.
ENHANCER = [
    ('botania:mana_powder', 4),
    ('ars_nouveau:source_gem', 3),
    ('naturesaura:aura_cache', 1),
    ('botania:white_petal', 6),
    ('alfheim:dawnglass_shard', 2),
    ('alfheim:galeglass_shard', 2),
]

REAGENT = [
    ('alfheim:emberglass_shard', 'minecraft:blaze_powder', 2),
    ('alfheim:duskglass_shard', 'minecraft:gunpowder', 3),
    ('alfheim:tidewake_shard', 'minecraft:redstone', 4),
    ('alfheim:rootglass_shard', 'minecraft:glowstone_dust', 2),
    # The five non-metal blooms. They have no place in MULTIPLIER -- doubling is a raw-to-
    # ingot idea and these render into coal, lapis, quartz, blaze powder and ender pearls --
    # but without a row here they appeared in no recipe outside their own Rite. Outputs are
    # deliberately NOT the bloom's own render target, so this is a second use rather than a
    # cheaper duplicate of the first.
    ('alfheim:quickened_cinderbloom', 'minecraft:torch', 8),
    ('alfheim:quickened_duskbloom', 'ars_nouveau:source_gem', 2),
    ('alfheim:quickened_cloudglass', 'minecraft:glass', 4),
    ('alfheim:quickened_emberwake', 'minecraft:magma_cream', 2),
    ('alfheim:quickened_farbloom', 'minecraft:ender_eye', 1),
]

# --- how a use is CRAFTED, as opposed to what it produces ----------------------------
#
# Measured 2026-09-03: this file emitted 238 shapeless recipes, 54% of every recipe the
# pack ships, all through one method -- while the era ladder rotated 23. The uses were the
# single thing flattening the pack's crafting variety.
#
# Arity is not decorative. B-41 shipped eleven dead recipes by handing multi-input data to
# single-input Create types, so the two tables are separated by how many inputs the station
# actually accepts, verified against Create's own recipes in its jar.
TWO_INPUT = [
    ('shapeless', None),
    ('deploying', 'create:deploying'),
    ('mixing', 'create:mixing'),
    ('na_altar', 'naturesaura:altar'),
]

ONE_INPUT = [
    ('crushing', 'create:crushing'),
    ('milling', 'create:milling'),
    ('pressing', 'create:pressing'),
    ('haunting', 'create:haunting'),
    ('splashing', 'create:splashing'),
    ('cutting', 'create:cutting'),
    ('polishing', 'create:sandpaper_polishing'),
    ('ars_crush', 'ars_nouveau:crush'),
    ('mana_pool', 'botania:mana_infusion'),
]


# The shortcut family is a COSTED skip: 4 of an intermediate plus mana powder buys the next
# one, trading material for a station visit. Routing it through the single-input helper
# silently dropped both the 4x and the powder, turning it into a 1:1 conversion identical to
# the ladder step it was supposed to bypass -- check_era.py E7 caught exactly that, twice.
SHORTCUT_STATIONS = ['shapeless', 'create:mixing', 'botania:runic_altar', 'naturesaura:altar']


def shortcut_recipe(rid, src, out):
    kind = pick(SHORTCUT_STATIONS, 'short')
    if kind == 'shapeless':
        return (f"    event.shapeless('{out}', ['4x {src}', 'botania:mana_powder'])"
                f".id(id('{rid}'))")
    four = ', '.join([f"{{ item: '{src}' }}"] * 4)
    if kind == 'botania:runic_altar':
        return (f"    event.custom({{ type: 'botania:runic_altar',"
                f" ingredients: [{four}, {{ item: 'botania:mana_powder' }}], mana: 3000,"
                f" output: {{ item: '{out}', count: 1 }} }}).id(id('{rid}'))")
    if kind == 'naturesaura:altar':
        return (f"    event.custom({{ type: 'naturesaura:altar',"
                f" input: {{ item: '{src}' }},"
                f" catalyst: {{ item: 'botania:mana_powder' }},"
                f" output: {{ item: '{out}', count: 1 }}, aura: 30000, time: 200 }})"
                f".id(id('{rid}'))")
    return (f"    event.custom({{ type: 'create:mixing',"
            f" ingredients: [{four}, {{ item: 'botania:mana_powder' }}],"
            f" results: [{{ item: '{out}', count: 1 }}] }}).id(id('{rid}'))")


def two_input(rid, a, b, out, count, s):
    """Emit a two-ingredient conversion through a rotated station."""
    kind, typ = pick(TWO_INPUT, 'two')
    if kind == 'shapeless':
        return (f"    event.shapeless('{count}x {out}', ['{a}', '{b}'])"
                f".id(id('{rid}'))")
    if kind == 'na_altar':
        # input + catalyst is a genuine two-slot station, not a shapeless in disguise.
        return (f"    event.custom({{ type: 'naturesaura:altar',"
                f" input: {{ item: '{a}' }}, catalyst: {{ item: '{b}' }},"
                f" output: {{ item: '{out}', count: {count} }},"
                f" aura: 12000, time: 120 }}).id(id('{rid}'))")
    return (f"    event.custom({{ type: '{typ}',"
            f" ingredients: [{{ item: '{a}' }}, {{ item: '{b}' }}],"
            f" results: [{{ item: '{out}', count: {count} }}] }})"
            f".id(id('{rid}'))")


def one_input(rid, a, out, count, s):
    """Emit a single-ingredient conversion through a rotated station."""
    kind, typ = pick(ONE_INPUT, 'one')
    if kind == 'mana_pool':
        return (f"    event.custom({{ type: 'botania:mana_infusion',"
                f" input: {{ item: '{a}' }}, mana: 1200,"
                f" output: {{ item: '{out}', count: {count} }} }})"
                f".id(id('{rid}'))")
    if kind == 'ars_crush':
        return (f"    event.custom({{ type: 'ars_nouveau:crush',"
                f" input: {{ item: '{a}' }},"
                f" output: [{{ item: '{out}', count: {count}, chance: 1.0, maxRange: 1 }}],"
                f" skip_block_place: false }}).id(id('{rid}'))")
    time = ", processingTime: 150" if kind in ('crushing', 'milling', 'cutting') else ''
    return (f"    event.custom({{ type: '{typ}',"
            f" ingredients: [{{ item: '{a}' }}],"
            f" results: [{{ item: '{out}', count: {count} }}]{time} }})"
            f".id(id('{rid}'))")


FAMILIES = ['multiplier', 'edible', 'restorative', 'enhancer', 'reagent', 'shortcut']


# --- table selection ------------------------------------------------------------------
#
# Selection used to be `TABLE[seed(item) % len(TABLE)]`. That is deterministic but it is not
# COVERING: measured on the real roster it left 7 of 12 quickened blooms and 1 of 6 crystal
# shards in no recipe at all, because a hash simply never landed on those indices among the
# items that carried the family. Round-robin over a fixed iteration order is just as stable
# and guarantees every row is reached, which is what "our ores find their way into the
# recipes" actually requires.
_RR = {}


def pick(table, key):
    i = _RR.get(key, 0)
    _RR[key] = i + 1
    return table[i % len(table)]


def seed(item_id):
    return int(hashlib.sha1(item_id.encode()).hexdigest(), 16)


def families_for(item_id, era):
    """2-6 families, deterministic per item. Later eras get more uses."""
    s = seed(item_id)
    n = 2 + (s % 3) + (1 if era >= 7 else 0)
    n = min(6, n)
    order = FAMILIES[:]
    # rotate so different items favour different families
    r = s % len(order)
    order = order[r:] + order[:r]
    return order[:n]


def build(items):
    by_era = {}
    for it in items:
        by_era.setdefault(it['era'], []).append(it)

    lines = [
        '// Alfheim Reclaimed — uses for the custom materials',
        '//',
        '// GENERATED by tools/gen_item_uses.py — do not hand-edit.',
        '//',
        '// Every ladder intermediate gets 2-6 uses beyond feeding the next step, so materials',
        '// are worth keeping rather than being single-purpose tokens. Outputs are existing',
        '// items only; this adds no new registrations.',
        '',
        'ServerEvents.recipes(event => {',
        "    const id = s => `alfheim:uses/${s}`",
        '',
    ]

    total = 0
    for era in sorted(by_era):
        chain = by_era[era]
        lines.append(f'    // ---------------------------------------------- Era {era}')
        for idx, it in enumerate(chain):
            iid = f"{NS}:{it['id']}"
            fams = families_for(it['id'], era)
            s = seed(it['id'])
            lines.append(f"    // {it['name']} — {len(fams)} uses: {', '.join(fams)}")
            for f in fams:
                total += 1
                if f == 'multiplier':
                    src, out, cnt = pick(MULTIPLIER, 'mult')
                    # The intermediate is the catalyst and is consumed with the ore. An
                    # earlier revision emitted an occultism:crushing recipe that named only
                    # the ore, so the "use" used nothing: 53 recipes collapsed into 5
                    # duplicates, two of which doubled an ingot into itself for free.
                    lines.append(two_input(f"{it['id']}_mult", src, iid, out, cnt, s))
                elif f == 'edible':
                    src, out, cnt = pick(EDIBLE, 'food')
                    lines.append(two_input(f"{it['id']}_food", iid, src, out, cnt, s + 1))
                elif f == 'restorative':
                    src, out, cnt = pick(RESTORATIVE, 'heal')
                    lines.append(two_input(f"{it['id']}_heal", iid, src, out, cnt, s + 2))
                elif f == 'enhancer':
                    out, cnt = pick(ENHANCER, 'enh')
                    lines.append(one_input(f"{it['id']}_enhance", iid, out, cnt, s))
                elif f == 'reagent':
                    src, out, cnt = pick(REAGENT, 'reag')
                    lines.append(two_input(f"{it['id']}_reagent", iid, src, out, cnt, s + 3))
                elif f == 'shortcut':
                    nxt = chain[idx + 1] if idx + 1 < len(chain) else None
                    if not nxt:
                        total -= 1
                        continue
                    lines.append(shortcut_recipe(f"{it['id']}_shortcut",
                                                iid, f"{NS}:{nxt['id']}"))
            lines.append('')
    lines.append(f"    console.info('[Alfheim Reclaimed] item uses loaded ({total} recipes).')")
    lines.append('})')
    lines.append('')
    return '\n'.join(lines), total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    a = ap.parse_args()

    items = json.load(open(MANIFEST, encoding='utf-8'))['items']

    # Transitional items are Create sequenced-assembly progress states, not materials. They
    # exist only between sub-steps on the assembler, so they must not gain uses: a `shortcut`
    # use would mint one directly, and the food/heal/enhance families would let the player
    # trade a half-finished thing that should never leave the machine.
    items = [it for it in items if not it.get('transitional')]

    script, total = build(items)

    if a.report:
        counts = {}
        for it in items:
            n = len(families_for(it['id'], it['era']))
            counts[n] = counts.get(n, 0) + 1
        print('uses per item:')
        for k in sorted(counts):
            print(f'  {k} uses: {counts[k]} items')
        print(f'\n{len(items)} items, {total} use-recipes')
        return 0

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(script)
    print(f'{len(items)} items -> {total} use-recipes')
    print('wrote', OUT)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
