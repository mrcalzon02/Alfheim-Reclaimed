"""Generate the Cartographer — a repeatable FTB Quests shop that sells Explorer's Maps.

Design record: alfheim_reclaimed_design/THE_SURFACE.md §5.
Source of truth: tools/surface_works_manifest.json (the same file the structures come from, so
a map and the thing it points at cannot drift apart).

Writes exactly one file: config/ftbquests/quests/chapters/cartographer.snbt. It does NOT touch
chapter_groups.snbt -- gen_compendium.py owns that, and one file has one owner.

Ten purchases, one per archetype, not one per structure. "Different types of structures" is
what was asked for, it is the vanilla idiom (`#minecraft:village` covers five village types),
and it is the version that stays useful after the first buy.

EVERY MECHANISM BELOW WAS READ OUT OF THE SHIPPED JAR, NOT REMEMBERED
---------------------------------------------------------------------
  can_repeat        `Quest.canRepeat` is a Tristate; `Tristate.read` maps a present boolean to
                    TRUE/FALSE and its absence to DEFAULT. So `can_repeat: true` forces
                    repeatability whatever the chapter default is.
  consume_items     `ItemTask.consumeItems`, also a Tristate.
  no accidental buy `ItemTask.submitItemsOnInventoryChange()` returns `!consumesResources()`.
                    A consuming task is NEVER submitted by an inventory change -- the player
                    must click it. Without that, a repeatable shop would drain a player's
                    petals in a loop the moment they picked some up.
  command reward    `CommandReward`, type "command", keys `command` / `elevate_perms` /
                    `silent`. It runs `player.createCommandSourceStack()`, so the command
                    executes AT the player, in the player's dimension -- which is what
                    `exploration_map` needs, because it searches outward from the origin in
                    the loot context.
  {p}               `Pattern.compile("[{](\\w+)}")`; the map holds p / x / y / z / team.
  auto              `Reward.autoclaim`, NBT key `auto`, written from `RewardAutoClaim.id` and
                    read back through a NameMap, so an unknown value degrades to DEFAULT
                    rather than throwing. "enabled" hands the map over the moment the payment
                    is accepted, which is what makes this feel like a counter and not a quest.

    python tools/gen_cartographer.py
    python tools/gen_cartographer.py --dry-run
"""
import argparse
import hashlib
import json
import os
import sys

OUT = os.path.join('config', 'ftbquests', 'quests', 'chapters')
MANIFEST = os.path.join('tools', 'surface_works_manifest.json')
NS = 'alfheim'
CAMPAIGN_GROUP = 'alfheim_reclaimed'
CHAPTER = 'cartographer'
ORDER_INDEX = 20          # after the ten eras, which take 0..9


def qid(*parts):
    """The project's stable id function. Identical to gen_quests.py and gen_compendium.py --
    change one and the campaign group id stops matching and the chapter lands nowhere."""
    return hashlib.sha1(('alfheim:' + ':'.join(parts)).encode('utf-8')).hexdigest()[:16].upper()


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def lines(key, body, indent):
    pad = '\t' * indent
    if not body:
        return f'{pad}{key}: [ ]'
    inner = '\n'.join(f'{pad}\t"{esc(l)}"' for l in body)
    return f'{pad}{key}: [\n{inner}\n{pad}]'


def pretty_item(item_id, count):
    """'16 magenta petals', but '12 livingrock'. Timber and stone are mass nouns here, and
    "12 livingrocks" in a price line is exactly the detail that makes a shop read generated."""
    name = item_id.split(':')[-1].replace('_', ' ')
    plural = 's' if (count != 1 and name.endswith('petal')) else ''
    return f'{count} {name}{plural}'


def pretty_biome(bid):
    return bid.split(':')[-1].replace('_', ' ').title()


# --------------------------------------------------------------------------- layout
#
# Two rows of five, cheapest first, so the counter reads left to right and top to bottom in
# the order a player can afford it.
ROWS = [
    ['shrine', 'barrow', 'hall', 'tower', 'aqueduct'],
    ['span', 'wreck', 'quarry', 'crater', 'castle'],
]

ICONS = {
    'shrine': 'feywild:elven_quartz_pillar',
    'barrow': 'minecraft:bone_block',
    'hall': 'botania:livingrock_bricks',
    'tower': 'feywild:elven_quartz_brick',
    'aqueduct': 'minecraft:prismarine_bricks',
    'span': 'botania:livingrock_bricks_stairs',
    'wreck': 'botania:dreamwood_planks',
    'quarry': 'minecraft:rail',
    'crater': 'minecraft:magma_block',
    'castle': 'minecraft:polished_blackstone_bricks',
}

INTRO = [
    "Loremistress Anwe keeps what is left of the Royal Survey.",
    "",
    "It is not much. The Survey mapped every road, hall and holding in Alfheim, and most of "
    "that is ash — but the elves who drew it were thorough, and a chart drawn from memory of "
    "a thorough survey is still better than walking in a straight line and hoping.",
    "",
    "Bring her pigment and she will draw you one. She works in petals, because that is what "
    "there is, and because a map of a dead country ought to be made of something that grew.",
    "",
    "SHE WILL DRAW THE SAME CHART AS OFTEN AS YOU CAN PAY FOR IT. Each of these is a "
    "purchase, not an achievement — click the payment to hand it over, and the chart is "
    "yours. Then do it again.",
]

WARNING = [
    "Anwe will tell you this herself, so hear it before you spend anything.",
    "",
    "A CHART FINDS THE NEAREST ONE. It does not find a good one, or a safe one, or a close "
    "one. If the nearest Keep is four thousand blocks away through the Hollow Marches, that "
    "is the Keep you have bought directions to.",
    "",
    "IF THERE IS NOTHING WITHIN RANGE, THE PAPER COMES BACK BLANK. The Survey only recorded "
    "what it could reach. Every chart below says which country its subject stands in — if you "
    "have never been anywhere near that country, walk first and buy second.",
    "",
    "AND A CHART IS NOT A GUARD. Knowing where the Marches bastion is has never once made it "
    "survivable. That is the Captain's department, and he charges more.",
]


def purchase(arch_key, arch, biomes, x, y):
    """One repeatable buy. Task takes the payment; the reward runs the loot table."""
    ident = qid(CHAPTER, arch_key)
    cost = arch['cost']
    price = ' and '.join(pretty_item(i, n) for i, n in cost)
    where = ', '.join(sorted(pretty_biome(b) for b in biomes))

    desc = [
        arch['blurb'],
        "",
        f"PRICE: {price}, each time.",
        f"FOUND IN: {where}.",
        "",
        f"The chart points at the nearest one of ANY kind — the Survey filed all of them "
        f"under the same heading, and so does this.",
        "",
        "Repeatable. Buy another whenever you have wandered far enough for the old one to be "
        "useless.",
    ]

    out = ['\t\t{']
    out.append(f"\t\t\ttitle: \"Chart: {esc(arch['plural'])}\"")
    out.append(f"\t\t\tsubtitle: \"{esc(price)}\"")
    out.append(f"\t\t\ticon: \"{ICONS[arch_key]}\"")
    out.append(f'\t\t\tx: {float(x)}d')
    out.append(f'\t\t\ty: {float(y)}d')
    out.append('\t\t\tshape: "rsquare"')
    # A purchase is never a prerequisite for anything, so it must not count toward the
    # chapter's completion. Without `optional` the chapter can never be finished, because a
    # repeatable quest un-completes itself every time it resets.
    out.append('\t\t\toptional: true')
    out.append('\t\t\tcan_repeat: true')
    out.append(lines('description', desc, 3))
    out.append(f'\t\t\tdependencies: ["{qid(CHAPTER, "survey")}"]')
    out.append(f'\t\t\tid: "{ident}"')

    tl = []
    for i, (item, count) in enumerate(cost):
        tl.append(f'\t\t\t\t{{ id: "{qid(CHAPTER, arch_key, "task", str(i))}", type: "item", '
                  f'item: "{item}", count: {count}L, consume_items: true }}')
    out.append('\t\t\ttasks: [\n' + '\n'.join(tl) + '\n\t\t\t]')

    cmd = f'/loot give {{p}} loot {NS}:explorer_maps/{arch_key}'
    out.append('\t\t\trewards: [\n'
               f'\t\t\t\t{{ id: "{qid(CHAPTER, arch_key, "reward")}", type: "command", '
               f'command: "{esc(cmd)}", elevate_perms: true, silent: true, '
               f'auto: "enabled", title: "Survey Chart — {esc(arch["plural"])}" }}\n'
               '\t\t\t]')
    out.append('\t\t}')
    return '\n'.join(out)


def guide(key, title, subtitle, desc, icon, x, y, deps=None):
    ident = qid(CHAPTER, key)
    out = ['\t\t{']
    out.append(f'\t\t\ttitle: "{esc(title)}"')
    out.append(f'\t\t\tsubtitle: "{esc(subtitle)}"')
    out.append(f'\t\t\ticon: "{icon}"')
    out.append(f'\t\t\tx: {float(x)}d')
    out.append(f'\t\t\ty: {float(y)}d')
    out.append('\t\t\tshape: "gear"')
    out.append('\t\t\toptional: true')
    out.append(lines('description', desc, 3))
    if deps:
        out.append('\t\t\tdependencies: [%s]' % ', '.join(f'"{qid(CHAPTER, d)}"' for d in deps))
    out.append(f'\t\t\tid: "{ident}"')
    out.append(f'\t\t\ttasks: [{{ id: "{qid(CHAPTER, key, "task")}", type: "checkmark", '
               f'title: "{esc(title)}" }}]')
    out.append('\t\t}')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    m = json.load(open(MANIFEST, encoding='utf-8'))
    archetypes = m['archetypes']

    biomes_by_arch = {}
    for st in m['structures']:
        biomes_by_arch.setdefault(st['archetype'], []).extend(st['biomes'])

    missing = [k for row in ROWS for k in row if k not in archetypes]
    assert not missing, f'ROWS names an archetype the manifest does not have: {missing}'
    unplaced = sorted(set(archetypes) - {k for row in ROWS for k in row})
    assert not unplaced, f'archetype with no shop entry: {unplaced}'

    entries = [
        guide('survey', 'The Royal Survey', 'Loremistress Anwe', INTRO,
              'minecraft:filled_map', 0.0, 0.0),
        guide('caveat', 'What A Chart Will Not Do', 'Read this before you pay', WARNING,
              'minecraft:paper', 3.0, 0.0, deps=['survey']),
    ]
    for r, row in enumerate(ROWS):
        for c, key in enumerate(row):
            entries.append(purchase(key, archetypes[key], biomes_by_arch[key],
                                    (c - 2) * 2.0, 3.0 + r * 2.5))

    body = [
        '{',
        '\tid: "%s"' % qid('chapter', CHAPTER),
        '\tgroup: "%s"' % qid('group', CAMPAIGN_GROUP),
        '\torder_index: %d' % ORDER_INDEX,
        '\tfilename: "%s"' % CHAPTER,
        '\ttitle: "The Cartographer"',
        '\ticon: "minecraft:filled_map"',
        lines('subtitle', ["What the Royal Survey still remembers"], 1),
        '\tdefault_quest_shape: ""',
        '\tdefault_hide_dependency_lines: false',
        '\tquests: [',
    ]
    body.append('\n'.join(entries))
    body += ['\t]', '\tquest_links: [ ]', '}']
    content = '\n'.join(body) + '\n'

    path = os.path.join(OUT, CHAPTER + '.snbt')
    if args.dry_run:
        print(f'   [dry] {path} ({len(content)} bytes, {len(entries)} entries)')
    else:
        os.makedirs(OUT, exist_ok=True)
        open(path, 'w', encoding='utf-8').write(content)
        print(f'   wrote {path} ({len(entries)} entries)')
    n_buy = len(entries) - 2
    print(f'\n  1 chapter, {n_buy} repeatable purchases, 2 guides')
    for row in ROWS:
        for k in row:
            a = archetypes[k]
            print('   %-9s %-18s %s' % (
                k, a['plural'], ' + '.join(f'{n} {i.split(":")[-1]}' for i, n in a['cost'])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
