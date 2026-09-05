"""Generate the in-game Compendium — reference chapters for everything this pack adds.

Design record: alfheim_reclaimed_design/COMPENDIUM.md

The pack now adds twelve ores, four Rites, six crystals, seven geodes, three trees and five
biomes, none of which JEI can explain. JEI shows a recipe; it cannot say *where a bloom
generates*, *which half of a geode holds which crystal*, or *why a Steeped nodule will take
heat when a raw one will not*. This builds a place to look that up, inside the game.

**The facts are generated; only the prose is authored.** Every number below — y-ranges, drop
rates, rarities, reagents, spawn lists, biome bands — is read out of the same manifests the
implementation is generated from, so the documentation cannot drift from the game. The
hand-written part is the explanation, which is the part a generator cannot supply.

    python tools/gen_compendium.py
    python tools/gen_compendium.py --dry-run

Ownership note: this file owns `config/ftbquests/quests/chapter_groups.snbt`, because the
Compendium adds a second chapter group and two generators must not write one file.
`gen_quests.py` no longer emits it.
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OUT = os.path.join('config', 'ftbquests', 'quests')
CH = os.path.join(OUT, 'chapters')
CAMPAIGN_GROUP = 'alfheim_reclaimed'
REF_GROUP = 'alfheim_compendium'


def qid(*parts):
    return hashlib.sha1(('alfheim:' + ':'.join(parts)).encode('utf-8')).hexdigest()[:16].upper()


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def lines(key, body, indent):
    pad = '\t' * indent
    if not body:
        return f'{pad}{key}: [ ]'
    inner = '\n'.join(f'{pad}\t"{esc(l)}"' for l in body)
    return f'{pad}{key}: [\n{inner}\n{pad}]'


def entry(chapter, key, title, subtitle, desc, icon, x, y, deps=None):
    """One reference page. Optional, so the Compendium never gates progression."""
    ident = qid(chapter, key)
    out = ['\t\t{']
    out.append(f'\t\t\ttitle: "{esc(title)}"')
    if subtitle:
        out.append(f'\t\t\tsubtitle: "{esc(subtitle)}"')
    out.append(f'\t\t\ticon: "{icon}"')
    out.append('\t\t\toptional: true')
    out.append('\t\t\tshape: "gear"')
    out.append(f'\t\t\tx: {x}d')
    out.append(f'\t\t\ty: {y}d')
    out.append(lines('description', desc, 3))
    if deps:
        out.append('\t\t\tdependencies: [%s]' %
                   ', '.join(f'"{qid(chapter, d)}"' for d in deps))
    out.append(f'\t\t\tid: "{ident}"')
    out.append('\t\t\ttasks: [{ id: "%s", type: "checkmark", title: "%s" }]'
               % (qid(chapter, key, 'task'), esc(title)))
    out.append('\t\t}')
    return '\n'.join(out)


def chapter(key, index, title, subtitle, icon, entries):
    body = [
        '{',
        '\tid: "%s"' % qid('chapter', key),
        '\tgroup: "%s"' % qid('group', REF_GROUP),
        '\torder_index: %d' % index,
        '\tfilename: "%s"' % key,
        '\ttitle: "%s"' % esc(title),
        '\ticon: "%s"' % icon,
        lines('subtitle', [subtitle], 1),
        '\tdefault_quest_shape: "gear"',
        '\tdefault_hide_dependency_lines: true',
        '\tquests: [',
    ]
    body.append('\n'.join(entries))
    body += ['\t]', '\tquest_links: [ ]', '}']
    return '\n'.join(body) + '\n'


def pretty_reagents(reagents):
    """'#botania:petals/yellow' x2 -> 'two yellow petals'. Tag paths are not player text."""
    from collections import Counter
    words = {1: 'one', 2: 'two', 3: 'three', 4: 'four'}
    out = []
    for raw, n in Counter(reagents).items():
        name = raw.lstrip('#').split(':')[-1]
        if name.startswith('petals/'):
            name = name.split('/')[1].replace('_', ' ') + ' petal'
        elif name == 'saplings':
            name = 'sapling'
        else:
            name = name.replace('_', ' ')
        out.append(f"{words.get(n, n)} {name}{'s' if n > 1 else ''}")
    return ', '.join(out)


def article(word):
    return 'an' if word[0] in 'aeiou' else 'a'


def grid(i, per_row=5, dx=2.0, dy=2.0, y0=0.0):
    return (i % per_row) * dx, y0 + (i // per_row) * dy


# --------------------------------------------------------------------------- prose
#
# Authored, not generated. Every *number* these pages show comes from a manifest; these are
# the sentences that say what the numbers mean.

BIOME_PROSE = {
    'ashen_grove': ("Where you woke. Drained, spider-ridden and flowerless — the absence of "
                    "mystical flowers here is the strongest single signal that the grove is "
                    "dead. Standing dead dreamwood is the only timber."),
    'silverbark_wood': ("Pale, cold and quiet. Dreamwood that survived by going dormant. "
                        "Cascading archwood grows here and nowhere else nearby."),
    'mana_fen': ("The aqueducts broke and the water stayed. Mana crystals still surface in "
                 "the shallows."),
    'sundered_highlands': ("Where the devastation tore the ground open. Broken uplands, and "
                           "the richest ordinary stone left in Alfheim."),
    'bloomfall_vale': ("Still alive. This is what the elves are trying to get the rest of "
                       "the world back to — and it is the only place mixed archwood grows."),
    'hollow_marches': ("Where it went worst. Era IX territory, and it feels like it."),
    'starved_reach': ("Used up. Not poisoned and not burned — simply spent. Nothing grows "
                      "here at all, which is rarer and worse than it sounds."),
    'scorchfell': ("It burned, and then it kept burning. Ash still hangs in the air. The "
                   "dead wood standing here is the only thing the fire left."),
    'infested_warren': ("Something moved into the roots of the old city and never left. "
                        "Bring light and something with reach."),
    'decayed_mire': ("Rot, standing water, and whatever is still moving in it."),
    'void_verge': ("The rim of the world. The ground thins, breaks into a ragged cliff, and "
                   "stops. What is left floats: islands of living rock that never fell. "
                   "They are the richest ground in Alfheim and the hardest to stand on."),
    'alfheim_plains': "MythicBotany's own. Open, gentle, and where most colonies start.",
    'alfheim_hills': "MythicBotany's own. Higher ground, deeper stone.",
    'alfheim_lakes': "MythicBotany's own. Water, and the biome the Void Verge was carved from.",
    'dreamwood_forest': "MythicBotany's own. Dense dreamwood — the pack's primary timber.",
    'golden_fields': "MythicBotany's own. Wheat grows here without being planted.",
}

MECHANICS = [
    ('three_energies', 'Three Energies, And They Are Not Alike', 'Read this one first',
     ["This pack runs three separate power systems that look similar and behave nothing "
      "alike. Nothing in any mod explains the difference, and confusing them is the single "
      "most common way to waste a week.",
      "",
      "MANA — Botania. Generated by flowers, moved by Mana Spreaders in straight lines "
      "that need line of sight, stored in Pools and Tablets. If your spreader is not "
      "firing, something is in the way.",
      "",
      "SOURCE — Ars Nouveau. Generated by Sourcelinks, stored in Source Jars, moved "
      "wirelessly by Relays within range. It does not travel in a line and does not care "
      "what is between two points.",
      "",
      "AURA — Nature's Aura. Ambient, per chunk, and belonging to the land rather than to "
      "you. It is the only one of the three that PUNISHES you: overdraw a chunk and the "
      "land around you degrades. The Ashen Grove is already depleted by design.",
      "",
      "Mana and Source you build. Aura you spend, and it does not forgive."],
     'botania:mana_pool'),
    ('the_reversal', 'The Gate Runs Outward', 'Why your Botania knowledge is wrong here',
     ["If you have played Botania, unlearn one thing.",
      "",
      "Normally you are a human feeding mundane goods into the Alfheim Portal to receive "
      "elven goods back. Here you are an elf, on the far side of that gate, and the trade "
      "runs the other way.",
      "",
      "Dreamwood grows in your forests. Elementium is an ore you mine. What you CANNOT "
      "easily get is Livingwood, Manasteel and Mana Diamonds — the products of a Midgard "
      "the elves no longer reach freely.",
      "",
      "The gate is not a reward for progression. It is a trade route, it opens in Era IV, "
      "and it leads out."],
     'botania:alfheim_portal'),
    ('why_no_metal', 'Why There Is No Metal', 'And what to do about it',
     ["Alfheim has no ordinary metal because the magic ate it.",
      "",
      "When the ley-lines died, the mana running through the bedrock did not drain away. "
      "It crystallised, and it took the metal with it. What is left in the stone are "
      "BLOOMS: growths that hold the pattern of a metal without being one.",
      "",
      "You cannot smelt a bloom. Heat does nothing to it — the pattern is magical, not "
      "chemical. To make one remember what it was you give it living things: petals, "
      "grain, seed, sapling. Life completes the pattern.",
      "",
      "That is supplementation, and it is the only metallurgy this world has. See the "
      "Blooms and the Rites."],
     'minecraft:iron_ingot'),
    ('petals', 'Where Petals Come From', 'The reagent everything needs',
     ["Petals gate the Pure Daisy, every Petal Apothecary recipe, the Wand of the Forest, "
      "the Mana Spreader and every Rite. They are the most important renewable thing in "
      "the pack.",
      "",
      "THREE SOURCES, in the order you will meet them:",
      "",
      "1. LEAVES. Every tree in Alfheim drops petals of its own colour when you break its "
      "leaves. This is the reliable one. See the Archive Groves.",
      "",
      "2. MYSTICAL FLOWERS, which grow wild here.",
      "",
      "3. FLORAL FERTILIZER, if you ever strip an area bare. It is bone meal plus four "
      "dyes — no petals needed — and using it on grass spawns fresh mystical flowers. "
      "Four WHITE dyes satisfy the recipe, and bone meal comes from a composter, so this "
      "route works from nothing but plant matter."],
     'botania:white_petal'),
]


def bifrost_chapter():
    """The Liquid Bifrost reference, derived from the generator rather than restated.

    gen_liquid_bifrost.TIERS and .CONVERSIONS are the only definition of the chain that exists.
    Reading them here means the Compendium cannot drift from the recipes the way a hand-written
    page would -- add a tier there and this page grows one; change a conversion rate and this
    page changes with it. The same reason court_entities() reads the Hollow Court manifest
    instead of restating the roster.
    """
    import gen_liquid_bifrost as LB

    ents = []
    ents.append(entry(
        'ref_bifrost', 'pool', 'Liquid Bifrost', 'The pools, and what they are',
        ["Bifrost is bridge-stuff. Solid, it is the rainbow road the Aesir walked between the "
         "realms. What lies in Alfheim's shallows is the same substance with the bridge taken "
         "out of it -- what was left when the roads stopped being roads.",
         '',
         "FOUND: pools on the surface, 1 chunk in 40, in the lake biomes, the Mana Fen, the "
         "Hollow Marches, the Bloomfall Vale and the Void Verge.",
         '',
         "It glows faintly. Look for that at dusk.",
         '',
         "IT IS FINITE. Pools do not refill and do not regenerate. Until Era VII teaches you "
         "to make it, every drop you spend is gone. See THE RENEWABLE ROUTE.",
         '',
         "WHAT IT IS FOR: it is the only material in this world that belongs to no magical "
         "tradition, which is exactly why every tradition will accept it."],
        f'{LB.NS}:liquid_bifrost_bucket', 0.0, 0.0))

    station = {'crystallized_bifrost': 'Petal Apothecary',
               'condensed_bifrost': 'Mana Pool infusion',
               'refined_bifrost': 'Alfheim Mana Infuser',
               'distilled_bifrost': 'Runic Altar'}
    for i, t in enumerate(LB.TIERS):
        x, y = grid(i, 4, y0=2.5)
        ents.append(entry(
            'ref_bifrost', t['id'], t['name'], f"Era {t['era']} · tier {i + 1} of 4",
            [t['tooltip'], '',
             f"STATION: {station[t['id']]}",
             f"ERA: {t['era']}",
             '',
             "Each tier is a different station, and every one of them is a station an earlier "
             "quest already taught you. Nothing in this chain introduces a new machine.",
             '',
             "The material does not become more powerful as it refines. It becomes less "
             "attached -- and the final tier is attached to nothing at all, which is what "
             "lets it become anything."],
            f'{LB.NS}:{t["id"]}', x, y))

    rows = ', '.join(f"{c['count']}x {c['to'].split(':')[-1].replace('_', ' ')}"
                     for c in LB.CONVERSIONS)
    ents.append(entry(
        'ref_bifrost', 'exchange', 'The Exchange', 'One material, every road',
        ["Distilled Bifrost converts into the entry currency of five other magical "
         "traditions.",
         '',
         f"YIELDS: {rows}.",
         '',
         "THE RATES ARE POOR AND THAT IS DELIBERATE. This is a foothold in a discipline you "
         "have not studied, not a way to skip studying it. What it buys you is the chance to "
         "begin somewhere new without beginning from nothing.",
         '',
         "Only one conversion reaches past a system's entry tier, and it costs four."],
        'botania:mana_powder', 6.0, 2.5))

    ents.append(entry(
        'ref_bifrost', 'renewable', 'The Renewable Route', 'Era VII · make it, stop finding it',
        ["A heated Create mixer will make Liquid Bifrost from things that grow back.",
         '',
         "RECIPE: 2 crystal shards + 1 mana powder + 500mB water -> 250mB Liquid Bifrost.",
         "STATION: Basin with a Mechanical Mixer, heated.",
         '',
         "WHY IT IS RENEWABLE: six of the seven crystals have a budding block and regrow "
         "forever. The shard tag holds exactly those six -- frost does not bud and is not in "
         "it. Water is water. Mana powder is a flower.",
         '',
         "It is NOT cheaper than finding a pool and was never meant to be. Four mixes to the "
         "bucket. It is only endless, which is a different and better property.",
         '',
         "Era VII because that is the first era that teaches the mixer."],
        'create:basin', 6.0, 0.0))

    return chapter('ref_bifrost', 6, 'Liquid Bifrost',
                   'The bridge between the traditions', f'{LB.NS}:distilled_bifrost', ents)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    blooms = json.load(open('tools/blooms_manifest.json', encoding='utf-8'))
    crystals = json.load(open('tools/crystals_manifest.json', encoding='utf-8'))
    groves = json.load(open('tools/groves_manifest.json', encoding='utf-8'))
    layer = json.load(open('kubejs/data/mythicbotany/libx/biome_layer/alfheim.json',
                           encoding='utf-8'))
    rites = blooms['rites']

    files = {}

    # ---------------------------------------------------------------- blooms
    ents = []
    for i, b in enumerate(blooms['blooms']):
        w = b['worldgen']
        reag = pretty_reagents(b['reagents'])
        x, y = grid(i, 4)
        ents.append(entry('ref_blooms', b['id'], b['name'], f"Era {b['era']} · {b['tier']} tools",
                          [b['tooltip'], '',
                           f"FOUND: y {w['ymin']} to {w['ymax']}, in the {w['group']} spread.",
                           f"NEEDS: {article(b['tier'])} {b['tier']} pickaxe or better.",
                           '',
                           f"MINED it gives Raw {b['name']}, which is inert. A Rite turns that "
                           f"into Quickened {b['name']}, which will take heat.",
                           '',
                           f"RITE I REAGENTS: {reag}.",
                           f"RENDERS INTO: {b['renders']['item'].split(':')[-1].replace('_', ' ')}"
                           f" x{b['renders']['count']}"
                           + (f", plus {b['bonus']['item'].split(':')[-1].replace('_', ' ')} "
                              f"from Rite III." if b['bonus'] else '.')],
                          f"alfheim:{b['id']}_ore", x, y))
    files[os.path.join(CH, 'ref_blooms.snbt')] = chapter(
        'ref_blooms', 0, 'The Twelve Blooms', 'Alfheim\'s ore, and where it hides',
        'alfheim:palebloom_ore', ents)

    # ---------------------------------------------------------------- rites
    rite_prose = {
        'steeping': ("The first Rite, and the only one that needs no mana. Put a raw bloom "
                     "in a Petal Apothecary with two petals and one growing thing, and the "
                     "water does the rest. Slow, cheap, and available the day you wake up."),
        'quickening': ("Mana Pool infusion. The same raw bloom, twice the return. This is "
                       "the era where mana stops being a curiosity and becomes your smelter."),
        'grafting': ("Runic Altar, three plant reagents and a rune. Three times the return, "
                     "and a byproduct the earlier Rites cannot produce at all — this is "
                     "where quartz, ghast tear, glowstone and magma cream come from."),
        'deepening': ("The Mana Infuser. Four times the return on four blooms at once. "
                      "Expensive to run and worth it once your mana economy is real."),
    }
    # Explicit, rather than derived from dict order — the manifest's leading _comment key
    # made an index-based numeral quietly depend on where that comment sat.
    numeral = {'steeping': 'I', 'quickening': 'II', 'grafting': 'III', 'deepening': 'IV'}
    ents = []
    for i, key in enumerate(k for k in rites if not k.startswith('_')):
        r = rites[key]
        x, y = grid(i, 4, dy=3.0)
        mana = f"{r['mana_base']:,} x era" if 'mana_base' in r else 'none'
        ents.append(entry('ref_rites', key, f"Rite {numeral[key]} — The {key.title()}",
                          f"Era {r['era']} · {r['yield']}x return",
                          [rite_prose[key], '',
                           f"STATION: {r['station'].split(':')[-1].replace('_', ' ')}",
                           f"MANA: {mana}",
                           f"RETURN: {r['yield']}x per raw bloom",
                           '',
                           "Later Rites do not replace earlier ones. The same raw bloom is "
                           "valid input to every Rite you have unlocked — they simply pay "
                           "better. Use whichever you can afford to run."],
                          'botania:apothecary_livingrock' if key == 'steeping'
                          else 'botania:mana_pool', x, y))
    files[os.path.join(CH, 'ref_rites.snbt')] = chapter(
        'ref_rites', 1, 'The Four Rites', 'How a bloom becomes a metal',
        'botania:apothecary_livingrock', ents)

    # ---------------------------------------------------------------- crystals
    ents = []
    cr = {c['id']: c for c in crystals['crystals']}
    for i, c in enumerate(crystals['crystals']):
        x, y = grid(i, 3)
        ents.append(entry('ref_crystals', c['id'], c['name'], f"{c['element']} alignment",
                          [c['tooltip'], '',
                           "Found in geodes, never alone — every geode is the seam between "
                           "two alignments.",
                           '',
                           f"BUDDING {c['name'].upper()} grows fresh clusters over time, so "
                           f"a geode is a renewable deposit rather than a finite one. It "
                           f"drops nothing without Silk Touch, so you cannot move it.",
                           '',
                           f"A cluster gives 4 {c['name']} Shards."],
                          f"alfheim:{c['id']}_cluster", x, y))
    for i, g in enumerate(crystals['geodes']):
        x, y = grid(i, 4, y0=6.0)
        a, b = g['pair']
        ents.append(entry('ref_crystals', 'geode_' + g['id'], f"Geode: {g['name']}",
                          f"1 in {g['rarity']} chunks",
                          [f"{cr[a]['name']} on one side, {cr[b]['name']} on the other, with "
                           f"a visible seam between them.",
                           '',
                           f"FREQUENCY: about 1 in {g['rarity']} eligible chunks. Vanilla "
                           f"amethyst is 1 in 24, for comparison.",
                           f"BIOMES: {', '.join(x.split(':')[-1].replace('_', ' ') for x in g['biomes'])}.",
                           '',
                           "These sit 14 to 28 blocks below the surface you are standing on, "
                           "not at a fixed depth.",
                           '',
                           "LOOK FOR THE SMALL ONES. A miniature geode on the surface means a "
                           "full geode is directly below it, within about 32 blocks. Surface "
                           "geodes never appear without one — if you see the crystals, dig."],
                          f"alfheim:{a}_block", x, y))
    files[os.path.join(CH, 'ref_crystals.snbt')] = chapter(
        'ref_crystals', 2, 'Crystallised Mana', 'Six alignments, and the seams between them',
        'alfheim:dawnglass_cluster', ents)

    # ---------------------------------------------------------------- groves
    ents = []
    for i, e in enumerate(groves['leaf_petals']):
        x, y = grid(i, 5)
        nm = e['leaf'].split(':')[-1].replace('_', ' ').title()
        ents.append(entry('ref_groves', 'leaf_' + e['leaf'].split(':')[-1], nm,
                          'Petal source',
                          [f"Breaking these leaves drops "
                           f"{' and '.join(p.replace('_', ' ') for p in e['petals'])} petals, "
                           f"at about {int(e['chance'] * 100)}% per leaf before Fortune.",
                           '',
                           "Shears and Silk Touch give you the leaf block instead, so break "
                           "them bare-handed or with anything else when you want petals.",
                           '',
                           "Fortune raises the rate substantially. A Fortune III axe is a "
                           "reasonable petal farm."],
                          e['leaf'], x, y))
    for i, t in enumerate(groves['trees']):
        x, y = grid(i, 3, y0=4.0)
        saps = ', '.join(s.split(':')[-1].replace('_sapling', '').replace('_', ' ')
                         for s in t['saplings'])
        ents.append(entry('ref_groves', t['id'], t['name'], 'Archive tree',
                          [t['tooltip'], '',
                           "Before the devastation the elves kept a seed-archive of every "
                           "forest in the Nine Realms. Three trees are what survived of it, "
                           "and their leaves still carry other forests' seeds.",
                           '',
                           f"PETALS: {' and '.join(p.replace('_', ' ') for p in t['petals'])}, "
                           f"about {int(t['petal_chance'] * 100)}% per leaf.",
                           f"FOREIGN SEEDS: {saps} — about "
                           f"{t['sapling_chance'] * 100:.1f}% per leaf. These are ordinary "
                           f"saplings and they grow normally, which is how Alfheim gets oak, "
                           f"apples and plank variety at all.",
                           f"ITS OWN SAPLING: about "
                           f"{t.get('own_sapling_chance', 0.03) * 100:.0f}% per leaf, so a "
                           f"grove can be replanted.",
                           '',
                           f"FOUND IN: "
                           f"{', '.join(b.split(':')[-1].replace('_', ' ') for b in t['biomes'])}."],
                          f"alfheim:{t['id']}_sapling", x, y))
    files[os.path.join(CH, 'ref_groves.snbt')] = chapter(
        'ref_groves', 3, 'The Archive Groves', 'Petals, and the seeds of other forests',
        'alfheim:hushbark_sapling', ents)

    # ---------------------------------------------------------------- biomes
    ents = []
    seen = []
    for b in layer['biomes']:
        bid = b['biome']
        if bid in seen:
            continue
        seen.append(bid)
    for i, bid in enumerate(seen):
        short = bid.split(':')[-1]
        x, y = grid(i, 4)
        prose = BIOME_PROSE.get(short, 'No entry written yet.')
        path = os.path.join('kubejs', 'data', 'alfheim', 'worldgen', 'biome', short + '.json')
        facts = []
        if os.path.exists(path):
            bj = json.load(open(path, encoding='utf-8'))
            mobs = sorted({e['type'].split(':')[-1].replace('_', ' ')
                           for v in bj['spawners'].values() for e in v})
            facts = ['', f"SPAWNS: {', '.join(mobs) if mobs else 'nothing'}.",
                     f"RAIN: {'yes' if bj.get('has_precipitation') else 'none'}."]
        ents.append(entry('ref_biomes', short, short.replace('_', ' ').title(),
                          'Alfheim' if bid.startswith('alfheim') else 'MythicBotany',
                          [prose] + facts, 'minecraft:grass_block', x, y))
    files[os.path.join(CH, 'ref_biomes.snbt')] = chapter(
        'ref_biomes', 4, 'The Sixteen Biomes', 'Where you are, and what lives there',
        'minecraft:filled_map', ents)

    # ---------------------------------------------------------------- mechanics
    ents = [entry('ref_mechanics', k, t, s, d, ic, *grid(i, 4))
            for i, (k, t, s, d, ic) in enumerate(MECHANICS)]
    files[os.path.join(CH, 'ref_mechanics.snbt')] = chapter(
        'ref_mechanics', 5, 'How This Pack Works', 'Read these before anything else',
        'minecraft:book', ents)

    # ---------------------------------------------------------------- liquid bifrost
    files[os.path.join(CH, 'ref_bifrost.snbt')] = bifrost_chapter()

    # ---------------------------------------------------------------- groups
    files[os.path.join(OUT, 'chapter_groups.snbt')] = (
        '{\n\tchapter_groups: [\n'
        '\t\t{ id: "%s", title: "Alfheim Reclaimed" }\n'
        '\t\t{ id: "%s", title: "Compendium" }\n'
        '\t]\n}\n' % (qid('group', CAMPAIGN_GROUP), qid('group', REF_GROUP))
    )

    total = 0
    for path, content in files.items():
        n = content.count('\t\t\ttitle: "')
        total += n
        if args.dry_run:
            print(f'   [dry] {path}  ({n} entries, {len(content)} bytes)')
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, 'w', encoding='utf-8').write(content)
            print(f'   wrote {path}  ({n} entries)')
    print(f'\n  {len(files) - 1} reference chapters, {total} entries')
    return 0


if __name__ == '__main__':
    sys.exit(main())
