"""Generate the Hollow Court: quest-giving elves at spawn, and the sealed gate.

Three things, all data. No new mod, no Java.

1. **NPCs from the wood elf entity.** `quest_giver` does not require its own villager: its
   `quest_line_links.json` binds a quest line to any `entity_id` plus a `name`, and
   `QuestLinkManager.getMatchingLink` compares `getType()` against `getCustomName()`. So a
   nametagged `richs_races_wood_elves:wood_elf` is a quest giver.

   The catch, and it is the reason the summon NBT below is not negotiable: `WoodElfEntity`
   extends `Monster`, implements `RangedAttackMob`, and its `NearestAttackableTargetGoal`
   list includes `Player`. Left alone these are hostile archers. `NoAI` freezes targeting,
   movement and despawn in one flag; the rest is presentation.

2. **The Captain gates expeditions.** CORRECTED 2026-09-03: the working Map Device is
   `dungeon_realm:map_device`, not `mmorpg:teleporter`. The latter has no recipe and appears
   to be legacy; the former is craftable from **one diamond over one stone at a vanilla
   crafting table**. So expeditions were never unreachable -- they were unreachable-flavoured
   and actually trivial, which is a straight INSTRUCTIONS.md 2.3 violation: expedition access
   is progression capability obtained with no spine involvement at all.

   06_expedition_gate.js removes that recipe and re-lays it on the Runic Altar in elven
   materials, and Orenvel's line grants one outright. Replacement ships in the same change as
   the removal, per 6.1.

3. **The sealed gate.** A dormant gate face for the arrival chamber -- the thing B-36 asks
   for, "a multiblock the player can *see* from Era I and cannot *finish* until Era IV".
   It is scenery: no teleport, no state change. Era IV's gating stays with B-36.

    python tools/gen_hollow_court.py
    python tools/gen_hollow_court.py --dry-run
"""
import argparse
import colorsys
import json
import math
import os

from PIL import Image

NS = 'alfheim'
DATA = os.path.join('kubejs', 'data', 'quest_giver')
SERVER = os.path.join('kubejs', 'server_scripts')
STARTUP = os.path.join('kubejs', 'startup_scripts')
TEX_BLOCK = os.path.join('kubejs', 'assets', NS, 'textures', 'block')
MANIFEST = os.path.join('tools', 'hollow_court_manifest.json')

ELF = 'richs_races_wood_elves:wood_elf'
SCROLL = 'quest_giver:quest_scroll'
HOME = 'mythicbotany:alfheim'

# --- the court ----------------------------------------------------------------------------
# Offsets are from the player's anchored landing spot, which is where 02_spawn_dimension.js
# puts them and then writes /spawnpoint. Each NPC gets a livingrock plinth set under its feet
# before it is summoned: NoAI mobs do not walk down onto terrain, so a guaranteed floor is
# cheaper than trusting that a 6-block offset lands at the same height.
NAMED = [
    dict(key='velrous', name='Magister Velrous', line='the_reclaiming',
         dx=3, dz=-2, title='the Magister',
         blurb='Elder of the Hollow Court. He taught the vanguard before the ley-lines died, '
               'and has not stopped teaching since.'),
    dict(key='orenvel', name='Captain Orenvel', line='the_royal_guard',
         dx=-3, dz=-2, title='Captain of the Royal Elven Guard',
         blurb='What is left of the Royal Elven Guard is one captain and a locked armoury.'),
]

# Set dressing. No quest lines, so no links: they are survivors, not vendors. Names are ours
# rather than drawn from MineColonies' citizennames/elf.json -- that file is another mod's
# content, and this pack ships to CurseForge.
AMBIENT = [
    ('Sethyr the Quiet',   6, 4), ('Loremistress Anwe', -6, 4),
    ('Faelan Ashbound',    7, -5), ('Nyre of the Boughs', -7, -5),
    ('Warden Ilesh',       0, 7), ('Cinder-Sister Vaal',  0, -8),
]

# --- quest lines --------------------------------------------------------------------------
# Task ids and field names are taken from the shipped examples in quest_giver-1.20.1-1.5.2.jar,
# not guessed: gift/craft/item_stack/kill/tame/pet/name_entity/complete_quest all appear there
# with working shapes, and biome/structure/grow_tree/special were read off their task classes.
RECLAIMING = [
    dict(key='root', icon='botania:white_petal',
         title='The Court Still Stands',
         start='You are awake. Good. Most are not.\n\nI am Velrous, and this was a city. Look '
               'up before you look down -- the boughs held nine hundred of us. Now they hold '
               'cobwebs.\n\nWe will not rebuild it with iron. There is no iron here worth the '
               'name. We rebuild it the way it was built.'),

    dict(key='where_you_are', parent='root', icon='minecraft:compass',
         title='Know The Ground',
         start='Before anything else: walk. Alfheim is not the world you half-remember from '
               'stories, and it is certainly not Midgard.\n\nGo and stand somewhere that is '
               'still alive.',
         complete='You have seen it. Then you know what we lost, and roughly how much of it '
                  'is still worth saving.',
         tasks=[{'id': 'quest_giver:biome', 'biome': f'{NS}:bloomfall_vale'}],
         rewards=[{'id': 'quest_giver:item',
                   'item': {'item': 'botania:fertilizer', 'count': 2}}]),

    dict(key='petals', parent='where_you_are', icon='botania:pink_petal',
         title='Where Petals Come From',
         start='Every elven working begins with petals, and every newcomer assumes they come '
               'from flowers.\n\nThey come from *leaves*. Strip a canopy and you will have '
               'colour enough. The archive trees remember which.',
         complete='Sixteen colours grow in this forest if you know which branch to pull. That '
                  'is the whole of the Spine of Leaf in one sentence.',
         tasks=[{'id': 'quest_giver:item_stack', 'amount': 8,
                 'item': {'item': 'botania:white_petal'}}],
         rewards=[{'id': 'quest_giver:item',
                   'item': {'item': 'botania:pink_petal', 'count': 4}}]),

    dict(key='apothecary', parent='petals', icon='botania:apothecary_livingrock',
         title='The Apothecary',
         start='A basin of water and a ring of petals. It is the crudest thing we make and '
               'nothing else works without it.\n\nBuild one. Fill it. It will not thank you.',
         complete='Now you have a workbench that argues back. Every flower in Alfheim comes '
                  'out of that basin.',
         tasks=[{'id': 'quest_giver:craft',
                 'item': {'item': 'botania:apothecary_livingrock'}}],
         rewards=[{'id': 'quest_giver:item',
                   'item': {'item': 'botania:pure_daisy', 'count': 1}}]),

    dict(key='grow', parent='apothecary', icon='ars_nouveau:blue_archwood_sapling',
         title='Plant Something',
         start='The Court has mourned for a long time and planted almost nothing.\n\nPut an '
               'archwood in the ground. Watch it take. That is the entire argument for staying.',
         complete='It took. Good.\n\nThat is one tree against a dead city, and it is still one '
                  'more than yesterday.',
         # NOT quest_giver:grow_tree. GrowTreeTask ships as a class in the jar and is never
         # registered -- QuestGiver.class registers biome, command, complete_quest, craft,
         # gift, item, item_stack, kill, name_entity, pet, special_task, structure, tame and
         # nothing else. Using it threw "Unknown quest task type" and killed the loading of
         # EVERY quest line, both givers, silently as far as the player is concerned.
         # Runtime-proven 2026-09-04. Asking for the log keeps the intent: plant it, wait,
         # bring back a length of it.
         tasks=[{'id': 'quest_giver:item_stack', 'amount': 4,
                 'item': {'item': 'ars_nouveau:blue_archwood_log'}}],
         rewards=[{'id': 'quest_giver:item',
                   'item': {'item': 'ars_nouveau:blue_archwood_sapling', 'count': 2}}]),

    dict(key='gift', parent='grow', icon='botania:dreamwood',
         title='A Length Of Dreamwood',
         start='One last thing, and it is for me rather than for you.\n\nBring me dreamwood. '
               'My staff is livingwood, and livingwood does not grow here any more. I have '
               'been leaning on a memory for eleven years.',
         complete='That will hold. Thank you.\n\nGo and speak to Orenvel when you can carry a '
                  'blade. He has been waiting longer than I have, and he is worse at it.',
         tasks=[{'id': 'quest_giver:gift', 'entity': ELF,
                 'item': {'item': 'botania:dreamwood'}}],
         rewards=[{'id': 'quest_giver:item',
                   'item': {'item': 'botania:mana_spreader', 'count': 1}}]),
]

ROYAL_GUARD = [
    dict(key='root', icon='minecraft:iron_sword',
         title='What Is Left Of The Guard',
         start='Captain Orenvel. Royal Elven Guard.\n\nYou are looking for the rest of it. '
               'There is no rest of it.\n\nI still hold the roster and the armoury key, so I '
               'still hold the rank. If you want the ruins opened, you go through me.'),

    dict(key='spiders', parent='root', icon='minecraft:cobweb',
         title='Clear The Understory',
         start='The Court is not haunted. It is infested, which is worse, because haunting '
               'does not lay eggs.\n\nStart under the boughs.',
         complete='Cleaner. Not clean.\n\nYou did not flinch at the second one. I noticed.',
         tasks=[{'id': 'quest_giver:kill', 'entity': 'minecraft:spider', 'times': 8}],
         rewards=[{'id': 'quest_giver:item',
                   'item': {'item': 'minecraft:string', 'count': 8}}]),

    dict(key='provision', parent='spiders', icon='botania:livingrock',
         title='Provision Yourself',
         start='I do not equip volunteers. I have nothing to equip them with.\n\nBring your '
               'own stone and I will tell you where the maps are kept.',
         complete='Good. A guard who waits to be supplied is a guard who waits.',
         tasks=[{'id': 'quest_giver:item_stack', 'amount': 16,
                 'item': {'item': 'botania:livingrock'}}],
         rewards=[{'id': 'quest_giver:item',
                   'item': {'item': 'mmorpg:map_creator', 'count': 1}}]),

    dict(key='cartography', parent='provision', icon='mmorpg:map_creator',
         title='Draw Your Own Ground',
         start='The Guard surveyed everything it could reach and the surveys burned with the '
               'archive.\n\nSo you will draw them again. Make the device. I will tell you what '
               'it is for once it is in your hand.',
         complete='That is a map creator. It writes ground you have not walked yet.',
         tasks=[{'id': 'quest_giver:craft', 'item': {'item': 'mmorpg:map_creator'}}],
         rewards=[{'id': 'quest_giver:item', 'item': {'item': 'dungeon_realm:dungeon_map', 'count': 1}}]),

    # The gate. Nothing else in the pack produces mmorpg:teleporter -- verified 0 recipes
    # across every jar -- so this quest is the only route to Mine and Slash's expeditions.
    dict(key='commission', parent='cartography', icon='dungeon_realm:map_device',
         title='The Armoury Key',
         start='Here is what the key opens.\n\nA Map Device. The Guard used them to step into '
               'ground we had surveyed but could not march to. There are four left and I am '
               'not sentimental about the other three.\n\nYou are not being rewarded. You are '
               'being *dispatched*. Bring back what the ruins are holding.',
         complete='Commissioned, then. The roster has two names on it again.\n\nGo carefully. '
                  'Everything out there was killed once already and did not take it well.',
         tasks=[{'id': 'quest_giver:item_stack', 'amount': 1,
                 'item': {'item': 'dungeon_realm:dungeon_map'}}],
         rewards=[{'id': 'quest_giver:item',
                   'item': {'item': 'dungeon_realm:map_device', 'count': 1}},
                  {'id': 'quest_giver:item', 'item': {'item': 'mmorpg:master_bag', 'count': 1}}]),
]

LINES = {'the_reclaiming': RECLAIMING, 'the_royal_guard': ROYAL_GUARD}


def quest_json(q):
    """One quest file. `parent` is namespaced to quest_giver, as the shipped examples are."""
    out = {'icon': q['icon'],
           'start': {'title': {'translate': q['title']},
                     'description': {'translate': q['start']}}}
    if 'parent' in q:
        out['parent'] = f"quest_giver:{q['parent']}"
    if 'complete' in q:
        out['complete'] = {'title': {'translate': q['title']},
                           'description': {'translate': q['complete']}}
    if 'tasks' in q:
        out['tasks'] = q['tasks']
    if 'rewards' in q:
        out['rewards'] = q['rewards']
    return out


def write_json(path, obj, dry):
    if dry:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write('\n')


# --- the sealed gate texture --------------------------------------------------------------
FRAMES = 12
SIZE = 16


def gate_texture():
    """A looping swirl for the dormant gate face.

    Every frame is a function of a phase that completes exactly one turn over FRAMES, so the
    animation loops seamlessly rather than snapping back. Colour runs deep bark to elven gold:
    it should read as a gate that is lit but shut, not as an open portal.
    """
    img = Image.new('RGBA', (SIZE, SIZE * FRAMES))
    px = img.load()
    for f in range(FRAMES):
        phase = 2.0 * math.pi * f / FRAMES
        for y in range(SIZE):
            for x in range(SIZE):
                # Centred polar coordinates, so the pattern turns about the middle of the face.
                cx, cy = (x - 7.5) / 8.0, (y - 7.5) / 8.0
                r = math.sqrt(cx * cx + cy * cy)
                ang = math.atan2(cy, cx)
                v = (math.sin(3.0 * ang + phase - 4.0 * r) + math.sin(6.0 * r - phase)) * 0.5
                v = (v + 1.0) * 0.5                       # -> 0..1
                edge = max(0.0, 1.0 - r)                  # fade out at the rim
                v *= edge ** 0.7
                hue = 0.12 - 0.06 * v                     # gold toward green-gold
                rr, gg, bb = colorsys.hsv_to_rgb(hue, 0.55 + 0.25 * v, 0.10 + 0.80 * v)
                a = int(190 + 65 * v * edge)
                px[x, f * SIZE + y] = (int(rr * 255), int(gg * 255), int(bb * 255), min(255, a))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    dry = a.dry_run

    # ---------------------------------------------------------------- quest lines
    n_quests = 0
    for line, quests in LINES.items():
        for q in quests:
            write_json(os.path.join(DATA, 'quest_lines', line, f"{q['key']}.json"),
                       quest_json(q), dry)
            n_quests += 1
        print(f'  quest line {line:<18} {len(quests)} quests')

    # Additive, not overwrite. `overwrite: true` would clear the registry the mod's own
    # example_quest and wolf_quest live in, while their entries in the mod's
    # quest_line_links.json would survive and point at lines that no longer exist. Adding is
    # harmless: Bob and Wolfie need a villager or wolf carrying those exact names to appear.
    write_json(os.path.join(DATA, 'quest_line_names.json'),
               {'overwrite': False, 'names': sorted(LINES)}, dry)

    write_json(os.path.join(DATA, 'quest_line_links.json'),
               [{'quest_line_id': n['line'], 'entity_id': ELF, 'name': n['name'],
                 'scale': 1.0, 'interaction_item': SCROLL} for n in NAMED], dry)

    # ---------------------------------------------------------------- sealed gate texture
    if not dry:
        os.makedirs(TEX_BLOCK, exist_ok=True)
        gate_texture().save(os.path.join(TEX_BLOCK, 'sealed_gate.png'))
        write_json(os.path.join(TEX_BLOCK, 'sealed_gate.png.mcmeta'),
                   {'animation': {'frametime': 3, 'interpolate': True}}, dry)
    print(f'  sealed gate texture   {FRAMES} frames, {SIZE}x{SIZE}, interpolated')

    # ---------------------------------------------------------------- scripts
    if not dry:
        with open(os.path.join(STARTUP, '14_sealed_gate.js'), 'w', encoding='utf-8') as f:
            f.write(startup_script())
        with open(os.path.join(SERVER, '03_hollow_court.js'), 'w', encoding='utf-8') as f:
            f.write(court_script())
    if not dry:
        with open(os.path.join(SERVER, '06_expedition_gate.js'), 'w', encoding='utf-8') as f:
            f.write(expedition_gate_script())
    print(f'  scripts               {STARTUP}/14_sealed_gate.js, {SERVER}/03_hollow_court.js, '
          f'{SERVER}/06_expedition_gate.js')

    write_json(MANIFEST, {
        '_comment': 'Generated by tools/gen_hollow_court.py. The court roster and its gating.',
        'named': NAMED, 'ambient': [{'name': n, 'dx': x, 'dz': z} for n, x, z in AMBIENT],
        'lines': {k: [q['key'] for q in v] for k, v in LINES.items()},
        'gates': {'dungeon_realm:map_device': 'the_royal_guard/commission'},
    }, dry)

    print(f'\n  {len(NAMED)} named + {len(AMBIENT)} ambient elves, '
          f'{len(LINES)} quest lines, {n_quests} quests')
    return 0


def expedition_gate_script():
    """Re-gate the Map Device.

    `dungeon_realm:map_device` is the block that opens Mine and Slash's dungeon dimension, and
    the jar crafts it from one diamond over one stone at a vanilla crafting table. That is the
    entire cost of entering every expedition in the pack.

    INSTRUCTIONS.md 2.3 is explicit: every progression-relevant recipe routes through a spine,
    and convenience may stay ungated but capability may not. Expedition access is capability.

    6.1 is equally explicit that nothing is removed before its replacement exists, so both
    happen here: the vanilla recipe goes, and a Runic Altar recipe in elven materials replaces
    it in the same file. Captain Orenvel also grants one outright at the end of his line, so
    there are two routes -- commissioned, or built -- and both cost something.
    """
    return """// Alfheim Reclaimed — the expedition gate
//
// GENERATED by tools/gen_hollow_court.py — do not hand-edit.
//
// See BACKLOG B-57. The Map Device was one diamond and one stone; expeditions were the
// cheapest capability in the pack and touched no spine at all.

ServerEvents.recipes(event => {
    const id = s => `alfheim:gate/${s}`

    // Out: diamond over stone at a crafting table.
    event.remove({ id: 'dungeon_realm:map_device' })

    // In: the Runic Altar, which means mana, which means a working spreader and pool. The
    // Guard surveyed with elven instruments; so do you.
    event.custom({
        type: 'botania:runic_altar',
        ingredients: [
            { item: 'minecraft:diamond' },
            { item: 'botania:livingrock' },
            { item: 'botania:dreamwood' },
            { item: 'alfheim:dawnglass_shard' },
            { tag: 'botania:petals/yellow' }
        ],
        mana: 15000,
        output: { item: 'dungeon_realm:map_device', count: 1 }
    }).id(id('map_device'))

    console.info('[Alfheim Reclaimed] expedition gate: Map Device re-laid on the Runic Altar.')
})
"""


def startup_script():
    return '''// Alfheim Reclaimed — the sealed gate
//
// GENERATED by tools/gen_hollow_court.py — do not hand-edit.
//
// Scenery, deliberately. B-36 asks for a gate the player can SEE from Era I and cannot FINISH
// until Era IV, so this block is the seeing half and nothing else: no teleport, no state, no
// recipe. The traversal already exists (botania:alfheim_portal outward,
// mythicbotany:return_portal home) and gating it is B-36's job, not this block's.
//
// It is not in any mineable tag and has a high hardness on purpose: the point of the gate in
// Era I is that it does not open, and a player who can quietly pickaxe it has been told the
// wrong story about the pack.

StartupEvents.registry('block', event => {
    event.create('alfheim:sealed_gate')
        .displayName('Sealed Gate')
        .soundType('amethyst')
        .hardness(-1.0)
        .resistance(3600000.0)
        .lightLevel(0.6)
        .defaultTranslucent()
        .notSolid()
        .fullBlock(false)
        .textureAll('alfheim:block/sealed_gate')
})
'''


def court_script():
    """The placement script.

    Written to the same standard 02_spawn_dimension.js was rewritten to after B-44: ask the
    game what happened, and record nothing that has not been observed.
    """
    named = ',\n'.join(
        f"    {{ name: '{n['name']}', dx: {n['dx']}, dz: {n['dz']}, line: '{n['line']}' }}"
        for n in NAMED)
    ambient = ',\n'.join(
        f"    {{ name: '{n}', dx: {x}, dz: {z} }}" for n, x, z in AMBIENT)
    return f'''// Alfheim Reclaimed — the Hollow Court at spawn
//
// GENERATED by tools/gen_hollow_court.py — do not hand-edit.
//
// Places the surviving court around the player's anchored landing spot in Alfheim, and the
// sealed gate face beside it.
//
// ---------------------------------------------------------------------------------------------
// WHY THE SUMMON NBT LOOKS LIKE THIS. Read before simplifying it.
//
// richs_races_wood_elves:wood_elf is not a villager. WoodElfEntity extends Monster, implements
// RangedAttackMob, and its NearestAttackableTargetGoal list includes Player — these are hostile
// archers that happen to be elves. Four flags make one an NPC:
//
//   NoAI:1b               no targeting, no wandering, no despawn — the whole problem in one flag
//   PersistenceRequired:1b belt and braces; a named mob already resists despawn
//   Invulnerable:1b       a quest giver a creeper can delete is a quest line the player loses
//   Silent:1b             they are standing in a ruin, not grunting in one
//
// CustomName is load-bearing, not decoration: quest_giver's QuestLinkManager matches a link by
// entity type AND custom name, so the name in quest_line_links.json and the name summoned here
// must agree exactly. They are generated from one roster so they cannot drift.
//
// NoAI mobs do not walk down onto terrain, so each one gets a livingrock plinth set under its
// feet first. That is cheaper than trusting an 8-block offset to land at the same height, and it
// reads as intentional — a court standing on what is left of its own floor.
// ---------------------------------------------------------------------------------------------

const COURT_DIMENSION = '{HOME}'
const ELF = '{ELF}'

// World-scoped, not player-scoped. The court belongs to the world; placing it per player would
// give a second player a second Velrous standing in the first one's shoulder.
const COURT_FLAG = 'alfheim_hollow_court_v1'

// Long enough to be after 02_spawn_dimension.js has teleported, spread and verified the player.
// If that has not finished, we do not know where the court belongs yet.
const PLACE_DELAY = 60

const NAMED = [
{named}
]

const AMBIENT = [
{ambient}
]

const NBT = "{{NoAI:1b,PersistenceRequired:1b,Invulnerable:1b,Silent:1b," +
            "CustomNameVisible:1b,CustomName:'{{\\"text\\":\\"%NAME%\\"}}'}}"

// `@e` is scoped to the execution dimension, so this counts one named elf in Alfheim using
// nothing but vanilla commands — the same idiom 02_spawn_dimension.js uses to test a dimension.
function exists(server, name) {{
    try {{
        return server.runCommandSilent(
            `execute in ${{COURT_DIMENSION}} if entity @e[type=${{ELF}},name="${{name}}",limit=1]`
        ) > 0
    }} catch (e) {{
        console.warn(`[Alfheim Reclaimed] could not query for ${{name}}: ${{e}}`)
        return false
    }}
}}

function place(server, name, x, y, z) {{
    if (exists(server, name)) return true          // idempotent: never a second Velrous
    server.runCommandSilent(
        `execute in ${{COURT_DIMENSION}} run setblock ${{x}} ${{y - 1}} ${{z}} botania:livingrock keep`)
    server.runCommandSilent(
        `execute in ${{COURT_DIMENSION}} run summon ${{ELF}} ${{x}} ${{y}} ${{z}} ` +
        NBT.replace('%NAME%', name))
    // Ask, do not assume. A summon that silently failed and was recorded as success is exactly
    // the B-44 mistake, and it would leave a quest line with no one to give it.
    if (exists(server, name)) return true
    console.warn(`[Alfheim Reclaimed] summon of "${{name}}" at ${{x}} ${{y}} ${{z}} did not take.`)
    return false
}}

// A 2x3 gate face in a livingrock surround, a few blocks in front of the court. Small enough to
// place with setblock rather than a structure, which the Greatbole does not yet exist to provide.
function placeGate(server, x, y, z) {{
    for (let dy = -1; dy <= 3; dy++) {{
        for (let dx = -2; dx <= 2; dx++) {{
            const edge = (dy === -1 || dy === 3 || dx === -2 || dx === 2)
            const block = edge ? 'botania:livingrock' : 'alfheim:sealed_gate'
            server.runCommandSilent(
                `execute in ${{COURT_DIMENSION}} run setblock ${{x + dx}} ${{y + dy}} ${{z}} ${{block}}`)
        }}
    }}
}}

// Audit only, by default. The court is seated INSIDE court/amphitheatre.nbt, so on any world
// where the Greatbole generated, these elves already exist in the right place — on the tiers,
// in front of the gate, where SPAWN_HUB.md puts them.
//
// This function used to summon them at the player's landing spot. That was correct when it was
// written and is wrong now: 02_spawn_dimension.js spreads the player up to 2000 blocks from the
// origin, and the hub generates at the origin, so summoning here would build a SECOND court in
// an empty field — with the same names, which means quest_giver would bind quest lines to
// whichever one the player reached first. A duplicate Velrous is worse than a missing one.
//
// So the fallback is off unless someone deliberately turns it on, and it says where it is
// putting them when they do.
const FALLBACK_SUMMON_AT_PLAYER = false

function auditCourt(server, player) {{
    if (server.persistentData.getBoolean(COURT_FLAG)) return

    const roster = NAMED.concat(AMBIENT)
    const missing = roster.filter(n => !exists(server, n.name))

    if (missing.length === 0) {{
        server.persistentData.putBoolean(COURT_FLAG, true)
        console.info(`[Alfheim Reclaimed] Hollow Court present — ${{roster.length}} elves. ` +
                     'Velrous and Orenvel give quests to a player holding a Quest Scroll.')
        return
    }}

    if (!FALLBACK_SUMMON_AT_PLAYER) {{
        console.warn(
            `[Alfheim Reclaimed] Hollow Court: ${{missing.length}}/${{roster.length}} missing ` +
            `(${{missing.map(n => n.name).join(', ')}}). They are seated inside ` +
            'court/amphitheatre.nbt, so this normally means the Greatbole has not generated ' +
            'or its chunks are not loaded. Walk to the hub, or set FALLBACK_SUMMON_AT_PLAYER ' +
            'to place a stand-in court here — which will NOT be at the amphitheatre.')
        return
    }}

    const x = Math.floor(player.x), y = Math.floor(player.y), z = Math.floor(player.z)
    let placed = 0
    NAMED.forEach(n => {{ if (place(server, n.name, x + n.dx, y, z + n.dz)) placed++ }})
    AMBIENT.forEach(n => {{ if (place(server, n.name, x + n.dx, y, z + n.dz)) placed++ }})
    placeGate(server, x, y, z - 9)
    console.warn(`[Alfheim Reclaimed] FALLBACK: ${{placed}} elves placed at ${{x}} ${{y}} ${{z}}, ` +
                 'away from the amphitheatre. Flag left clear deliberately.')
}}

PlayerEvents.loggedIn(event => {{
    const server = event.server
    if (server.persistentData.getBoolean(COURT_FLAG)) return
    try {{
        server.scheduleInTicks(PLACE_DELAY, () => auditCourt(server, event.player))
    }} catch (e) {{
        console.warn('[Alfheim Reclaimed] scheduleInTicks unavailable, auditing court now: ' + e)
        auditCourt(server, event.player)
    }}
}})
'''


if __name__ == '__main__':
    raise SystemExit(main())
