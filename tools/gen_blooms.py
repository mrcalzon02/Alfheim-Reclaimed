"""Generate the Twelve Blooms — Alfheim's native ore family and the Rites that render it.

Design record: alfheim_reclaimed_design/ORE_SUPPLEMENTATION.md
Manifest:      tools/blooms_manifest.json  (the source of truth; this file only transforms it)

Everything below is reproducible from the manifest. Nothing here is hand-maintained, so the
roster can be re-tuned by editing data rather than by editing twelve copies of the same JSON.

    python tools/gen_blooms.py
    python tools/gen_blooms.py --dry-run
    python tools/gen_blooms.py --list

Produced artifacts
------------------
  kubejs/assets/alfheim/textures/block/<id>_ore.png          12
  kubejs/assets/alfheim/textures/item/raw_<id>.png           12
  kubejs/assets/alfheim/textures/item/quickened_<id>.png     12
  kubejs/assets/alfheim/models/item/{raw,quickened}_<id>.json 24
  kubejs/startup_scripts/11_blooms.js                        blocks + items
  kubejs/server_scripts/11_bloom_loot.js                     block drops
  kubejs/server_scripts/12_rites.js                          Rites I-IV + rendering
  kubejs/data/alfheim/worldgen/configured_feature/bloom_<id>.json  12
  kubejs/data/alfheim/worldgen/placed_feature/bloom_<id>.json      12
  kubejs/data/alfheim/forge/biome_modifier/blooms_<group>.json      4
  kubejs/data/alfheim/tags/worldgen/biome/{veined,deep,drained}.json 3
  kubejs/data/alfheim/tags/blocks/blooms.json                       1

Why the ore texture is built by differencing
--------------------------------------------
A vanilla ore texture is stone plus coloured blobs. Tinting the whole image tints the stone too,
which produces a blue or green *rock*, not a bloom in Alfheim's rock. So the blobs are isolated by
differencing the ore against `block/stone.png` (or netherrack, for quartz), tinted alone, and
composited over `botania:block/livingrock.png`. The result reads as a growth in the stone Alfheim
actually has.
"""
import argparse
import colorsys
import json
import os
import sys
import zipfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_items import tint, load_base, CLIENT_JAR  # noqa: E402  shared, already proven

NS = 'alfheim'
MANIFEST = os.path.join('tools', 'blooms_manifest.json')

TEX_BLOCK = os.path.join('kubejs', 'assets', NS, 'textures', 'block')
TEX_ITEM = os.path.join('kubejs', 'assets', NS, 'textures', 'item')
MODEL_ITEM = os.path.join('kubejs', 'assets', NS, 'models', 'item')
STARTUP = os.path.join('kubejs', 'startup_scripts', '11_blooms.js')
LOOT = os.path.join('kubejs', 'server_scripts', '11_bloom_loot.js')
RITES = os.path.join('kubejs', 'server_scripts', '12_rites.js')
DATA = os.path.join('kubejs', 'data', NS)

HOST_STONE = os.path.join('botania:block', 'livingrock.png').replace('\\', '/')

# Vanilla ore textures sit on stone, except quartz which sits on netherrack. Differencing
# against the wrong host leaves the whole texture in the mask.
STONE_FOR = {'block/nether_quartz_ore.png': 'block/netherrack.png'}

# Harvest tier -> the vanilla block tag that enforces it.
TIER_TAG = {'stone': 'minecraft:needs_stone_tool',
            'iron': 'minecraft:needs_iron_tool',
            'diamond': 'minecraft:needs_diamond_tool'}


def speckle(ore_img, host_img, thresh=30):
    """Isolate an ore texture's blobs by differencing it against its host stone."""
    ore = ore_img.convert('RGBA')
    host = host_img.convert('RGBA').resize(ore.size)
    out = Image.new('RGBA', ore.size)
    op, hp, dp = ore.load(), host.load(), out.load()
    for y in range(ore.height):
        for x in range(ore.width):
            r, g, b, a = op[x, y]
            hr, hg, hb, _ = hp[x, y]
            if a == 0:
                dp[x, y] = (0, 0, 0, 0)
                continue
            if abs(r - hr) + abs(g - hg) + abs(b - hb) > thresh:
                dp[x, y] = (r, g, b, 255)
            else:
                dp[x, y] = (0, 0, 0, 0)
    return out


def rgb_int(hue, sat=0.85, val=0.85):
    """Manifest hue -> packed 0xRRGGBB, for mythicbotany:infuser's fromColor/toColor."""
    r, g, b = colorsys.hsv_to_rgb((hue % 360) / 360.0, sat, val)
    return (int(r * 255) << 16) | (int(g * 255) << 8) | int(b * 255)


def esc(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")


def write(path, content, dry):
    if dry:
        print(f'   [dry] {path} ({len(content)} bytes)')
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def write_json(path, obj, dry):
    write(path, json.dumps(obj, indent=2) + '\n', dry)


# ---------------------------------------------------------------------------- textures

def build_textures(blooms, jar, dry):
    host = load_base(jar, HOST_STONE)
    for b in blooms:
        oid, o = b['id'], b['ore']
        ore_src = load_base(jar, o['base'])
        host_src = load_base(jar, STONE_FOR.get(o['base'], 'block/stone.png'))
        blobs = tint(speckle(ore_src, host_src), o['hue'], o['sat'], o['val'], 0.35)
        img = Image.alpha_composite(host.convert('RGBA').resize(blobs.size), blobs)
        if not dry:
            os.makedirs(TEX_BLOCK, exist_ok=True)
            img.save(os.path.join(TEX_BLOCK, f'{oid}_ore.png'))

        for prefix, spec in (('raw', b['raw']), ('quickened', b['quick'])):
            src = load_base(jar, spec['base'])
            out = tint(src, spec['hue'], spec['sat'], spec['val'], 0.40)
            if not dry:
                os.makedirs(TEX_ITEM, exist_ok=True)
                os.makedirs(MODEL_ITEM, exist_ok=True)
                out.save(os.path.join(TEX_ITEM, f'{prefix}_{oid}.png'))
                with open(os.path.join(MODEL_ITEM, f'{prefix}_{oid}.json'), 'w',
                          encoding='utf-8') as f:
                    json.dump({'parent': 'minecraft:item/generated',
                               'textures': {'layer0': f'{NS}:item/{prefix}_{oid}'}}, f, indent=2)
        print(f"   texture  {oid}_ore, raw_{oid}, quickened_{oid}")


# ---------------------------------------------------------------------------- registration

def build_startup(blooms, dry):
    L = ['// Alfheim Reclaimed — the Twelve Blooms',
         '//',
         '// GENERATED by tools/gen_blooms.py from tools/blooms_manifest.json — do not hand-edit.',
         '// Design: alfheim_reclaimed_design/ORE_SUPPLEMENTATION.md',
         '//',
         '// A bloom is not a metal. It is the pattern of one, left in the stone when the',
         '// ley-lines died. Mining it gives you a raw bloom, which is inert until a Rite',
         '// completes the pattern with living matter. See 12_rites.js.',
         '',
         "StartupEvents.registry('block', event => {"]
    for b in blooms:
        oid = b['id']
        L.append(
            f"    event.create('{NS}:{oid}_ore')"
            f".displayName('{esc(b['name'])} Ore')"
            f".soundType('stone').hardness(3.0).resistance(3.0).requiresTool(true)"
            f".tagBlock('minecraft:mineable/pickaxe')"
            f".tagBlock('{TIER_TAG[b['tier']]}')"
            f".tagBlock('forge:ores').tagBlock('{NS}:blooms')"
            f".textureAll('{NS}:block/{oid}_ore')")
    L += ['})', '', "StartupEvents.registry('item', event => {"]
    for b in blooms:
        oid, nm = b['id'], esc(b['name'])
        tip = esc(b['tooltip'])
        L.append(f"    event.create('{NS}:raw_{oid}').displayName('Raw {nm}')"
                 f".tooltip('{tip}').tag('forge:raw_materials')")
                 # .tag(), not .tagItem(). Runtime-proven 2026-09-04: tagItem exists only
                 # on BlockBuilder; on an ItemBuilder it is
                 #   TypeError: Cannot find function tagItem in object BasicItemJS$Builder
                 # which aborts StartupEvents.registry('item') outright -- so every raw
                 # bloom failed to register and the whole ore economy was absent. Static
                 # checks cannot see this: the script parses perfectly.
        L.append(f"    event.create('{NS}:quickened_{oid}').displayName('Quickened {nm}')"
                 f".tooltip('The pattern is closed. It will take heat now.').rarity('uncommon')")
    L += ['})', '']
    write(STARTUP, '\n'.join(L), dry)


def build_loot(blooms, dry):
    L = ['// Alfheim Reclaimed — bloom drops',
         '//',
         '// GENERATED by tools/gen_blooms.py — do not hand-edit.',
         '// addSimpleBlock(block, item) gives the standard ore contract: the raw item on a',
         '// normal break, the block itself under Silk Touch, and explosion survival.',
         '',
         'ServerEvents.blockLootTables(event => {']
    for b in blooms:
        L.append(f"    event.addSimpleBlock('{NS}:{b['id']}_ore', '{NS}:raw_{b['id']}')")
    L += ['',
          "    console.info('[Alfheim Reclaimed] %d bloom loot tables registered.')" % len(blooms),
          '})', '']
    write(LOOT, '\n'.join(L), dry)


# ---------------------------------------------------------------------------- the Rites

def ing(entry):
    """Manifest reagent string -> a Botania/KubeJS ingredient object literal."""
    if entry.startswith('#'):
        return "{ tag: '%s' }" % entry[1:]
    return "{ item: '%s' }" % entry


def build_rites(blooms, rites, dry):
    L = ['// Alfheim Reclaimed — the Four Rites',
         '//',
         '// GENERATED by tools/gen_blooms.py from tools/blooms_manifest.json — do not hand-edit.',
         '// Design: alfheim_reclaimed_design/ORE_SUPPLEMENTATION.md §4',
         '//',
         '// A raw bloom holds the pattern of a metal but not the metal. A Rite completes that',
         '// pattern with living matter — petals, grain, seed, sapling — and yields a Quickened',
         '// bloom, which is the first form that will accept heat.',
         '//',
         '// The same raw bloom is valid input to every Rite the player has unlocked. Later Rites',
         '// do not obsolete earlier ones; they pay better. That is the ladder.',
         '//',
         '// Every recipe type below was read from the shipping jar before it was emitted',
         '// (B-41: a schema that parses is not a schema the game accepts).',
         '',
         'ServerEvents.recipes(event => {',
         "    const id = s => `alfheim:rites/${s}`",
         '']
    for b in blooms:
        oid, nm = b['id'], b['name']
        raw, quick = f'{NS}:raw_{oid}', f'{NS}:quickened_{oid}'
        r = b['renders']
        L.append(f'    // ---------------------------------------------------------- {nm}')

        # Rite I — The Steeping. Petal Apothecary, water reagent, no mana. Era I.
        items = ', '.join([ing(raw)] + [ing(x) for x in b['reagents']])
        L += [f"    event.custom({{ type: 'botania:petal_apothecary',",
              f"        ingredients: [{items}],",
              f"        output: {{ item: '{quick}' }},",
              f"        reagent: {{ tag: 'botania:seed_apothecary_reagent' }} }})",
              f"        .id(id('{oid}_steeping'))",
              '']

        # Rite II — The Quickening. Mana Pool. Era II. Double yield.
        mana2 = rites['quickening']['mana_base'] * b['era']
        L += [f"    event.custom({{ type: 'botania:mana_infusion',",
              f"        input: {{ item: '{raw}' }}, mana: {mana2},",
              f"        output: {{ item: '{quick}', count: {rites['quickening']['yield']} }} }})",
              f"        .id(id('{oid}_quickening'))",
              '']

        # Rite III — The Grafting. Runic Altar. Era III. Triple yield.
        mana3 = rites['grafting']['mana_base'] * b['era']
        graft = ', '.join([ing(raw), ing(raw), ing(b['reagents'][0]), ing(b['reagents'][2])])
        L += [f"    event.custom({{ type: 'botania:runic_altar',",
              f"        ingredients: [{graft}], mana: {mana3},",
              f"        output: {{ item: '{quick}', count: {rites['grafting']['yield'] * 2} }} }})",
              f"        .id(id('{oid}_grafting'))",
              '']

        # Rite III byproduct — the reason a Grafting is worth the altar time.
        if b['bonus']:
            bn = b['bonus']
            L += [f"    event.custom({{ type: 'botania:runic_altar',",
                  f"        ingredients: [{ing(raw)}, {ing(raw)}, {ing(raw)}, "
                  f"{ing(b['reagents'][0])}], mana: {mana3 * 2},",
                  f"        output: {{ item: '{bn['item']}', count: {bn['count']} }} }})",
                  f"        .id(id('{oid}_grafting_bonus'))",
                  '']

        # Rite IV — The Deepening. MythicBotany Infuser. Era V. Quadruple yield.
        # fromColor/toColor are mandatory ints — their absence silently killed five recipes
        # in B-41, so they are derived here rather than omitted.
        mana4 = rites['deepening']['mana_base'] * b['era']
        L += [f"    event.custom({{ type: 'mythicbotany:infuser',",
              f"        group: 'alfheim_rites',",
              f"        ingredients: [{ing(raw)}, {ing(raw)}, {ing(raw)}, {ing(raw)}],",
              f"        mana: {mana4},",
              f"        fromColor: {rgb_int(b['ore']['hue'], 0.5, 0.6)},",
              f"        toColor: {rgb_int(b['ore']['hue'], 1.0, 1.0)},",
              f"        output: {{ item: '{quick}', count: {rites['deepening']['yield'] * 4} }} }})",
              f"        .id(id('{oid}_deepening'))",
              '']

        # Rendering — the Quickened bloom becomes the base ingredient every chain already wants.
        if r['via'] == 'smelting':
            L += [f"    event.smelting('{r['item']}', '{quick}')"
                  f".id(id('{oid}_render'))",
                  f"    event.blasting('{r['item']}', '{quick}')"
                  f".id(id('{oid}_render_fast'))",
                  '']
        else:
            L += [f"    event.shapeless(Item.of('{r['item']}', {r['count']}), ['{quick}'])"
                  f".id(id('{oid}_render'))",
                  '']

    L += ["    console.info('[Alfheim Reclaimed] Rites I-IV loaded for %d blooms.')" % len(blooms),
          '})', '']
    write(RITES, '\n'.join(L), dry)


# ---------------------------------------------------------------------------- worldgen

def build_worldgen(blooms, groups, biome_tags, dry):
    for b in blooms:
        oid, w = b['id'], b['worldgen']
        write_json(os.path.join(DATA, 'worldgen', 'configured_feature', f'bloom_{oid}.json'), {
            'type': 'minecraft:ore',
            'config': {
                'size': w['size'],
                'discard_chance_on_air_exposure': 0.0,
                # Alfheim's stone, not vanilla's. This is what lets the global
                # #minecraft:stone_ore_replaceables override be retired.
                'targets': [{
                    'target': {'predicate_type': 'minecraft:tag_match',
                               'tag': 'mythicbotany:base_stone_alfheim'},
                    'state': {'Name': f'{NS}:{oid}_ore'},
                }],
            },
        }, dry)
        write_json(os.path.join(DATA, 'worldgen', 'placed_feature', f'bloom_{oid}.json'), {
            'feature': f'{NS}:bloom_{oid}',
            'placement': [
                {'type': 'minecraft:count', 'count': w['count']},
                {'type': 'minecraft:in_square'},
                # TRAPEZOID, not uniform. Player request 2026-09-04: our ores should behave
                # like vanilla's -- a band they are MOST likely to appear in, with upper and
                # lower extents that taper. A uniform provider spreads a bloom evenly across
                # its whole range, so there is no depth worth learning and no reason to dig
                # to a particular level. Vanilla uses trapezoid for diamond, iron, copper and
                # gold for exactly this reason; a symmetric trapezoid peaks at the midpoint
                # of the band, which is the depth the Compendium can then name.
                {'type': 'minecraft:height_range',
                 'height': {'type': 'minecraft:trapezoid',
                            'min_inclusive': {'absolute': w['ymin']},
                            'max_inclusive': {'absolute': w['ymax']}}},
                {'type': 'minecraft:biome'},
            ],
        }, dry)

    # One modifier per group, feature sets disjoint. See ORE_SUPPLEMENTATION.md §3.2 — this
    # disjointness is the whole defence against a CW-4 style feature-order cycle.
    for gname, g in groups.items():
        if gname.startswith('_'):
            continue
        feats = [f'{NS}:bloom_{b["id"]}' for b in blooms if b['worldgen']['group'] == gname]
        write_json(os.path.join(DATA, 'forge', 'biome_modifier', f'blooms_{gname}.json'), {
            'type': 'forge:add_features',
            'biomes': g['biomes'],
            'features': feats,
            'step': 'underground_ores',
        }, dry)

    for tname, values in biome_tags.items():
        write_json(os.path.join(DATA, 'tags', 'worldgen', 'biome', f'{tname}.json'),
                   {'replace': False, 'values': values}, dry)

    write_json(os.path.join(DATA, 'tags', 'blocks', 'blooms.json'),
               {'replace': False,
                'values': [f'{NS}:{b["id"]}_ore' for b in blooms]}, dry)


# ---------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()

    m = json.load(open(MANIFEST, encoding='utf-8'))
    blooms, groups = m['blooms'], m['groups']

    if a.list:
        for b in blooms:
            w = b['worldgen']
            print(f"  era {b['era']:>2}  {b['id']:<14} {b['tier']:<8} "
                  f"y{w['ymin']:>4}..{w['ymax']:<4} {w['group']:<8} -> {b['renders']['item']}")
        print(f'\n{len(blooms)} blooms')
        return 0

    # Disjointness is an invariant, not a hope. Assert it here as well as in the checker.
    seen = {}
    for b in blooms:
        g = b['worldgen']['group']
        seen.setdefault(g, []).append(b['id'])
    allf = [b['id'] for b in blooms]
    if len(allf) != len(set(allf)):
        print('FAIL: duplicate bloom id in manifest')
        return 2
    if len(blooms) != 12:
        print(f'WARNING: manifest has {len(blooms)} blooms, design says 12')

    if not os.path.exists(CLIENT_JAR):
        print(f'client jar not found: {CLIENT_JAR}')
        return 2
    jar = zipfile.ZipFile(CLIENT_JAR)

    print(f'Generating {len(blooms)} blooms...')
    build_textures(blooms, jar, a.dry_run)
    build_startup(blooms, a.dry_run)
    build_loot(blooms, a.dry_run)
    build_rites(blooms, m['rites'], a.dry_run)
    build_worldgen(blooms, groups, m['biome_tags'], a.dry_run)
    jar.close()

    print(f'\n  {len(blooms)} ore blocks, {len(blooms) * 2} items')
    print(f'  {len(blooms) * 2} worldgen features, '
          f'{len([g for g in groups if not g.startswith("_")])} biome modifiers')
    for g, ids in sorted(seen.items()):
        print(f'    {g:<8} {ids}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
