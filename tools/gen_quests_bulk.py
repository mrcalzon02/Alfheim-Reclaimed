"""Generate quest chapters for Eras IV-X and merge them into tools/gen_quests.py's output.

Eras I-III are hand-authored in gen_quests.py because they carry the pack's teaching load.
Eras IV-X are 154 quests; they are built here from per-era data plus the ladder, so the shape
stays consistent and the tier chains cannot drift out of step with tools/gen_ladder.py.

Every era emits the same 22: Leaf 7, Song 7, Support 4, Wound 3, capstone 1.
Velrous keeps the voice — per-era opening and capstone text is written by hand below; the
chain steps take their text from the station doing the work.

    python tools/gen_quests_bulk.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ladder
import gen_quests

RUNE = {4: 'midgard', 5: 'nidavellir', 6: 'joetunheim', 7: 'muspelheim',
        8: 'niflheim', 9: 'helheim', 10: 'asgard'}

# The item that proves a station is available. B-62: a recipe whose method the player was never
# given is a dead end that produces no error -- the recipe loads, and the block to perform it at
# simply does not exist. Each era now teaches the stations it is the first to use, before use.
#
# `smelt` and `craft` are omitted deliberately: a furnace and a crafting table are not a lesson.
STATION_ITEM = {
    'apothecary':  'botania:apothecary_livingrock',
    'mana_pool':   'botania:mana_pool',
    'runic_altar': 'botania:runic_altar',
    'terra_plate': 'botania:terra_plate',
    'gate':        'botania:alfheim_portal',
    'brew':        'botania:brewery',
    'infuser':     'mythicbotany:mana_infuser',
    'imbuement':   'ars_nouveau:imbuement_chamber',
    'apparatus':   'ars_nouveau:enchanting_apparatus',
    'crush':       'ars_nouveau:scribes_table',
    'na_altar':    'naturesaura:nature_altar',
    'na_tree':     'naturesaura:gold_powder',
    'occ_crush':   'occultism:sacrificial_bowl',
    'occ_fire':    'occultism:sacrificial_bowl',
    'fey_altar':   'feywild:fey_altar',
    'cr_mill':     'create:millstone',
    'cr_mix':      'create:basin',
    'cr_press':    'create:mechanical_press',
    'cr_deploy':   'create:deployer',
    'cr_seq':      'create:depot',
}

# Readable names for the method quests, since the station keys are internal.
STATION_NAME = {
    'gate': 'The Alfheim Gate', 'brew': 'The Brewery', 'infuser': 'The Mana Infuser',
    'terra_plate': 'The Terra Plate', 'imbuement': 'The Imbuement Chamber',
    'apparatus': 'The Enchanting Apparatus', 'crush': 'The Crush Glyph',
    'na_altar': 'The Natural Altar', 'na_tree': 'The Tree Ritual',
    'occ_crush': 'The Sacrificial Bowl', 'occ_fire': 'Spirit Fire',
    'fey_altar': 'The Fey Altar', 'cr_mill': 'The Millstone', 'cr_mix': 'The Basin',
    'cr_press': 'The Mechanical Press', 'cr_deploy': 'The Deployer', 'cr_seq': 'The Depot',
}

# What each station teaches. Shown on the quest that unlocks it.
STATION_TEACH = {
    'gate': ["The gate itself, and it is not what Botania's own books describe.",
             "",
             "Their recipe wants livingwood and terrasteel. We have neither -- livingwood is a "
             "gate-import, which is the joke, and terrasteel is six eras away.",
             "",
             "So we build it from dreamwood around the cord you have just finished. Read that "
             "tooltip again: Elven work, finished on the far side of the gate. It has been "
             "pointing here since the roster was written."],
    'cr_mill': ["A millstone. Yes, really.",
                "",
                "Machinery is not beneath us and it is not the point either. It is a faster way "
                "to break a thing into smaller things, and from here the ladder uses it.",
                "",
                "Build it before the era asks. Nothing downstream of this works without it."],
    'cr_mix': ["A basin, and something to stir it.",
               "",
               "Mixing under heat does what no flower will. You are not abandoning the Song by "
               "owning one; you are admitting that some problems are chemistry."],
    'cr_press': ["The press. Flattening, precisely, the same way every time.",
                 "",
                 "The dead world's whole genius was repetition without attention. Use it."],
    'cr_deploy': ["A deployer holds a tool and uses it, forever, without getting bored.",
                  "",
                  "The Song would have bound a creature to do this. Midgard built a hand."],
    'cr_seq': ["A depot, and the beginning of assembly in sequence.",
               "",
               "Several operations in a fixed order on one moving item. It is the most un-elven "
               "thing in this pack and by Era VIII you will not manage without it."],
    'infuser': ["MythicBotany's Infuser. Deeper than a pool and considerably hungrier.",
                "",
                "It asks what colour the working starts and ends in, and it means it. A recipe "
                "without both is refused at load and leaves no trace that it existed."],
    'terra_plate': ["The agglomeration plate. A quarter of a million mana, and it wants three "
                    "things from the far side of the gate.",
                    "",
                    "Build it now. Use it much later. Let it sit there and be a reminder."],
    'brew': ["The brewery. Not everything worth making is solid."],
    'imbuement': ["The Imbuement Chamber. Slow, and it does not care that you are in a hurry."],
    'apparatus': ["Pedestals in a ring and a reagent at the centre.",
                  "",
                  "Placement is part of the recipe here. The Song asks you to build the working "
                  "rather than type it into a grid."],
    'crush': ["Crush is a glyph, not a machine, which is why you will not find a block for it.",
              "",
              "Scribe it at the table and it lives in your book. The Song does not build "
              "stations for things a spell can already do."],
    'na_altar': ["The Natural Altar. It draws on the aura of the land, which is thin here."],
    'na_tree': ["A Ritual of the Forest. Multi-block, slow, and worth it."],
    'occ_crush': ["A sacrificial bowl and a closed circle. Let the spirits grind it."],
    'occ_fire': ["Spirit fire. It burns what should not burn and leaves what should not remain."],
    'fey_altar': ["The Fey Altar. Five offerings, always five. Ask politely."],
}

STATION_LINE = {
    'apothecary': 'Petals in the basin. You have done this a thousand times; do it again.',
    'mana_pool': 'Into the pool. Watch the level drop and understand what it cost.',
    'runic_altar': 'The altar. Lay it out properly — it is not forgiving of a rushed circle.',
    'terra_plate': 'The agglomeration plate. This one takes a quarter million mana. Plan for it.',
    'gate': 'Through the gate and back. What returns is not what you sent.',
    'brew': 'The brewery. Not everything worth making is solid.',
    'infuser': 'The Mana Infuser. Deep magic, and it will drain everything you have stored.',
    'imbuement': 'The Imbuement Chamber. Slow, and it does not care that you are in a hurry.',
    'apparatus': 'The Enchanting Apparatus. Their tradition, doing what ours cannot.',
    'crush': 'Crushed down. Sometimes progress is subtraction.',
    'na_altar': 'The Natural Altar. It draws on the aura of the land — thin here, so be patient.',
    'na_tree': 'A Ritual of the Forest. Multi-block, slow, and worth it.',
    'occ_crush': 'Let the spirits grind it. Do not watch too closely.',
    'occ_fire': 'Spirit fire. It burns what should not burn and leaves what should not remain.',
    'fey_altar': 'The Fey Altar. Ask politely. They remember being asked rudely.',
    'cr_mill': 'Milled. Machinery is not beneath us; it is simply not the point.',
    'cr_mix': 'Mixed under heat. Elven work still needs a stirring rod sometimes.',
    'cr_press': 'Pressed flat. Crude, effective, unglamorous.',
    'cr_deploy': 'Applied by machine, because your hands are needed elsewhere.',
    'cr_seq': 'A sequenced assembly. By this depth you cannot do it by hand and should not try.',
    'smelt': 'Into the furnace. The oldest process we have and still the honest one.',
    'craft': 'By hand, at the bench. The last step usually is.',
}

ERA_META = {
    4: dict(title='IV — The Long Silence', subtitle='Is anyone still out there?',
            open=["You have built enough that the grove feeds itself. Now we find out whether "
                  "anything else survived.",
                  "",
                  "The gate is not a reward. It is a door, and doors go both ways."],
            cap=["The Rune of Midgard.",
                 "",
                 "You have touched the other side. Whatever is over there heard you.",
                 "",
                 "I do not know yet whether that is good news. Neither do you. We proceed anyway."],
            leaf=['botania:alfheim_portal' if False else 'botania:elf_glass',
                  'botania:pixie_dust', 'botania:manasteel_ingot'],
            song=['ars_nouveau:enchanting_apparatus', 'ars_nouveau:arcane_core',
                  'ars_nouveau:wixie_charm'],
            support=['minecolonies:blockhutbuilder', 'minecraft:lantern'],
            wound=['dungeon_realm:dungeon_map', 'mmorpg:currency/gear_rarity_upgrade']),

    5: dict(title='V — The Deep Forges', subtitle='Can we make our own metal?',
            open=["Down, now. The ore you found in Era Two was the surface of it.",
                  "",
                  "Elementium, Alfsteel, and the pylons that make them. This is the era where "
                  "we stop scavenging metal and start producing it."],
            cap=["The Rune of Nidavellir, realm of the smiths.",
                 "",
                 "They were never the grandest of the nine and they made everything the grand "
                 "ones used. Remember that when someone calls your workshop unglamorous."],
            leaf=['mythicbotany:alfsteel_ingot', 'botania:dragonstone',
                  'mythicbotany:alfsteel_pylon'],
            song=['ars_nouveau:archmage_spell_book', 'ars_nouveau:alchemical_sourcelink',
                  'ars_nouveau:volcanic_sourcelink'],
            support=['minecolonies:blockhutsmeltery', 'minecolonies:blockhutstonemason'],
            wound=['dungeon_realm:dungeon_map', 'mmorpg:currency/socket_adder']),

    6: dict(title='VI — The Wild Marches', subtitle='Can we take back the frontier?',
            open=["Outward. The grove is safe and the grove is small.",
                  "",
                  "What is past the treeline has had an age to get comfortable, and it is not "
                  "going to stand aside because we have runes now."],
            cap=["The Rune of Jötunheim.",
                 "",
                 "The giants were not monsters. They were older than us and they were here "
                 "first, and we called them monsters because it was convenient.",
                 "",
                 "Hold the rune and think about who else we might have been convenient about."],
            leaf=['botania:tiny_planet', 'botania:rune_wrath', 'botania:mana_ring_greater'],
            song=['ars_nouveau:drygmy_stone', 'ars_nouveau:ritual_wilden_summon',
                  'ars_nouveau:relay_warp'],
            support=['minecolonies:blockhutguardtower', 'minecolonies:blockhutbarracks'],
            wound=['dungeon_realm:dungeon_map', 'mmorpg:currency/orb_of_quality']),

    7: dict(title='VII — The Burning Cradle', subtitle='Can we survive our own fire?',
            open=["Fire now. Both kinds — the Nether, and the memory.",
                  "",
                  "Something burned Alfheim. We are about to spend an era learning to hold "
                  "fire safely, which is either wisdom or irony and I have stopped deciding."],
            cap=["The Rune of Muspelheim.",
                 "",
                 "The realm of fire, which in every account is the thing that ends the world.",
                 "",
                 "We have just spent an era making it work for us. Do not let that make you "
                 "comfortable."],
            leaf=['botania:entropinnyum', 'botania:gaia_spreader', 'botania:rune_fire'],
            song=['ars_nouveau:volcanic_sourcelink', 'ars_nouveau:spell_turret',
                  'ars_nouveau:potion_flask'],
            support=['minecolonies:blockhutbaker', 'minecraft:blast_furnace'],
            wound=['dungeon_realm:dungeon_map', 'mmorpg:currency/sharpening_stone_3'],
            extra=[
                ('bifrost_farm', 'A Crystal That Grows Back', 'Budding crystal',
                 ["Before I show you the trick, I want you standing in front of a budding "
                  "crystal with a silk-touch pick you are not going to use.",
                  "",
                  "Six of the seven crystals in this world bud. Break the cluster and the "
                  "block grows another, forever, the way vanilla amethyst does -- that is not "
                  "an accident of the geodes, it is the only reason the next quest is "
                  "possible at all.",
                  "",
                  "The seventh, frost, does not bud. That is why it is not in the shard tag "
                  "and why nothing renewable will ever be built on it. Learn to tell them "
                  "apart by which one is still there tomorrow."],
                 # A CHECKMARK, not a tag task. FTB Quests takes a plain item id here; a
                 # tag needs the itemfilters:tag wrapper, no other quest in this pack uses
                 # one, and the format is client-side so nothing in headless validation
                 # could prove it fired. Naming one shard instead would force a specific
                 # geode type on a player who may never have found that biome. The teaching
                 # is in the description, which is what this quest is for.
                 [('checkmark',)],
                 [('item', 'minecraft:diamond', 2)],
                 [], 0.0, 8.0, 'leaf'),

                ('bifrost_renew', 'Stop Going To The Lakes', 'Liquid Bifrost, made',
                 ["Basin, mixer, fire under it. Two shards, a mana powder, half a bucket of "
                  "water.",
                  "",
                  "You have been spending Liquid Bifrost since Era Two and you have never "
                  "once made any. The pools are one in forty chunks and they do not come "
                  "back -- which means every conversion you have run has been drawn against "
                  "a balance that only goes down. I have watched apprentices spend their "
                  "last bucket on the wrong system and lose that road permanently.",
                  "",
                  "This is the answer, and note what it is made of: water, which is "
                  "everywhere; mana powder, which is a flower; and crystal, which grows "
                  "back. Nothing in it is finite. That is the whole design.",
                  "",
                  "It is not cheaper than finding a pool. It was never supposed to be. It is "
                  "only *endless*, which is a different and better thing."],
                 [('item', 'create:basin'),
                  ('item', 'alfheim:liquid_bifrost_bucket')],
                 [('item', 'alfheim:distilled_bifrost')],
                 ['bifrost_farm'], 1.5, 8.0, 'leaf'),

                ('bifrost_spend', 'Spend It Freely Now', 'The exchange, reopened',
                 ["Go back to the exchange and run it again, and this time do not think about "
                  "it.",
                  "",
                  "That is the point of the mixer. Not that the rate improved -- it did not, "
                  "and it will not -- but that the rate is now the only thing standing "
                  "between you and another system. Cost you can pay. Scarcity you cannot."],
                 [('item', 'alfheim:distilled_bifrost', 4)],
                 [('item', 'botania:mana_pearl', 4)],
                 ['bifrost_renew'], 3.0, 8.0, 'leaf'),
            ]),

    8: dict(title='VIII — The Frozen Archive', subtitle='What did we forget?',
            open=["We wrote things down before it happened. Most of it is under ice.",
                  "",
                  "This era is not about power. It is about recovering what we knew, and "
                  "finding out how much of it we would rather we had not."],
            cap=["The Rune of Niflheim, realm of mist and cold and the things kept in them.",
                 "",
                 "You have read the archive now. You know what the elves were doing in the "
                 "last century before the devastation.",
                 "",
                 "I taught some of it. I am not going to pretend otherwise."],
            leaf=['botania:mana_enchanter' if False else 'botania:manaweave_cloth',
                  'mythicbotany:andwari_ring', 'botania:rune_winter'],
            song=['ars_nouveau:caster_tome', 'ars_nouveau:scryers_crystal',
                  'ars_nouveau:archmage_spell_book'],
            support=['minecolonies:blockhutlibrary', 'minecolonies:blockhutschool'],
            wound=['dungeon_realm:dungeon_map', 'mmorpg:currency/orb_of_relief']),

    9: dict(title='IX — The Debt', subtitle='What did it cost?',
            open=["I have been putting this era off.",
                  "",
                  "You have the archive. You know roughly what happened and roughly whose "
                  "fault it was. Now we go and look at the part of Alfheim where it started.",
                  "",
                  "Bring the colony. They should see it too."],
            cap=["The Rune of Helheim.",
                 "",
                 "Not a punishment. A ledger.",
                 "",
                 "Everything the elves took out of this world is written down somewhere, and "
                 "we have spent nine eras putting a little of it back. That is not absolution "
                 "and I will not offer you any. It is simply the work, continued."],
            leaf=['mythicbotany:kvasir_mead', 'mythicbotany:wither_aconite', 'botania:dice'],
            song=['occultism:book_of_binding_foliot', 'ars_nouveau:ritual_brazier',
                  'mythicbotany:fimbultyr_tablet'],
            support=['minecolonies:blockhutgraveyard', 'minecolonies:blockhutmysticalsite'],
            wound=['dungeon_realm:dungeon_map', 'mmorpg:currency/mirror']),

    10: dict(title='X — The Crown of Branches', subtitle='What do we become?',
             open=["Last era.",
                   "",
                   "Terrasteel — which needs Midgard's metals and our mana both, and which "
                   "you could not have made in Era One if you had wanted to. The Gjallarhorn. "
                   "The branch of the world tree.",
                   "",
                   "And the colony, at full size, with the gates open."],
             cap=["The Rune of Asgard. The ninth.",
                  "",
                  "The way is clear.",
                  "",
                  "I sent word three eras ago, when the aura first held steady. They have been "
                  "coming since. You have been too busy to notice, which is exactly right.",
                  "",
                  "Alfheim is not restored. It will not be restored in your lifetime or mine. "
                  "But it is *inhabited*, and it is defended, and the gate is open in both "
                  "directions, and there are elves being born here who will never know what it "
                  "looked like when you found it.",
                  "",
                  "That was the assignment. You may consider it complete."],
             leaf=['botania:terrasteel_ingot', 'mythicbotany:gjallar_horn_empty',
                   'mythicbotany:yggdrasil_branch'],
             song=['ars_nouveau:archmage_spell_book', 'ars_nouveau:enchanting_apparatus',
                   'ars_nouveau:ritual_brazier'],
             support=['minecolonies:blockhuttownhall', 'minecolonies:blockhutcitizen'],
             wound=['dungeon_realm:dungeon_map', 'mmorpg:currency/perfected_soul_seed']),
}


def build_era(era):
    meta = ERA_META[era]
    L = next(x for x in gen_ladder.LADDER if x['era'] == era)
    chain = gen_ladder.parts_for(L) + [L['tier']]
    stations = L['stations']
    prev = gen_ladder.PREV_TIER[era]
    q = []

    # --- Leaf: opening + the tier chain, condensed to 7 quests -----------------------
    q.append(('open', f'Era {era}', 'Magister Velrous', meta['open'],
              [('checkmark',)], [('item', f'alfheim:{prev}')], [], 0.0, 0.0, 'leaf'))

    # --- Methods this era is the first to use, taught before the era needs them ---------
    #
    # B-61 and B-62, and they have the same root. The previous version BANDED the chain --
    # band = len(chain)//5, capped at six quests -- so Era X named six of its seventeen steps
    # and eleven transformations had no quest at all. And no era taught its stations, so
    # recipes referred to blocks the player had never been handed and could not build.
    #
    # Both are fixed by deriving from the ladder instead of summarising it.
    earlier = set()
    for e2 in range(4, era):
        L2 = next((z for z in gen_ladder.LADDER if z['era'] == e2), None)
        if L2:
            earlier |= set(L2['stations'])
    # Eras I-III teach these by hand; treat them as already known.
    earlier |= {'apothecary', 'mana_pool', 'runic_altar', 'smelt', 'craft', 'imbuement'}

    prev_key = 'open'
    x = 1.5
    for st in [k for k in dict.fromkeys(stations) if k not in earlier]:
        item = STATION_ITEM.get(st)
        if not item:
            continue
        key = 'method_' + st
        q.append((key, STATION_NAME.get(st, gen_ladder.pretty(st)), 'A new method',
                  STATION_TEACH.get(st, ['A station this era needs. Build it first.']),
                  [('item', item)], [('item', 'alfheim:' + prev)],
                  [prev_key], x, -1.5, 'leaf'))
        prev_key = key
        x += 1.5

    # --- The chain, one quest per step -------------------------------------------------
    x = 1.5
    for i, out_item in enumerate(chain):
        st = stations[i % len(stations)]
        desc = [STATION_LINE.get(st, 'Another step.'),
                '',
                f'Step {i + 1} of {len(chain)}.']
        if out_item == L['tier']:
            desc = [f'The last step. {gen_ladder.pretty(out_item)}.',
                    '',
                    L['tooltip'],
                    '',
                    f'{len(chain)} steps, and every one of them rests on the era before it. '
                    f'That is what the ladder is.']
        key = f'chain_{i}'
        q.append((key, gen_ladder.pretty(out_item), f'Step {i + 1}/{len(chain)}', desc,
                  [('item', f'alfheim:{out_item}')], [('item', f'alfheim:{out_item}')],
                  [prev_key], x, 0.0, 'leaf'))
        prev_key = key
        x += 1.5

    # --- Song ------------------------------------------------------------------------
    songs = (meta['song'] * 3)[:7]
    dep = []
    for j, it in enumerate(songs):
        key = f'song_{j}'
        q.append((key, gen_ladder.pretty(it.split(':')[1]), 'Song',
                  ['The other tradition, keeping pace.'],
                  [('item', it)], [('item', 'ars_nouveau:source_gem', 8)],
                  dep, j * 1.5, 2.0, 'song'))
        dep = [key]

    # --- Support ---------------------------------------------------------------------
    sup = (meta['support'] * 2)[:4]
    dep = []
    for j, it in enumerate(sup):
        key = f'sup_{j}'
        q.append((key, gen_ladder.pretty(it.split(':')[1]), 'Support',
                  ['The colony grows, or it does not. There is no third option.'],
                  [('item', it)], [('item', 'minecraft:emerald', 4)],
                  dep, j * 1.5, 4.0, 'support'))
        dep = [key]

    # --- Wound -----------------------------------------------------------------------
    wnd = (meta['wound'] * 2)[:3]
    dep = []
    for j, it in enumerate(wnd):
        key = f'wnd_{j}'
        q.append((key, gen_ladder.pretty(it.split(':')[-1]), 'The Wound',
                  ['Deeper than last time. It always is.'],
                  [('item', it)], [('item', 'minecraft:experience_bottle', 8)],
                  dep, j * 1.5, 6.0, 'wound'))
        dep = [key]

    # --- Capstone --------------------------------------------------------------------
    q.append(('capstone', f'The Rune of {RUNE[era].capitalize()}', 'Capstone', meta['cap'],
              [('item', f'mythicbotany:{RUNE[era]}_rune')],
              [('item', f'alfheim:{L["tier"]}', 2)],
              [prev_key, 'song_6', 'sup_3', 'wnd_2'], 6.0, 4.5, 'leaf'))
    # --- Bespoke quests this era owns ------------------------------------------------
    #
    # build_era derives everything above from the ladder, which is what keeps it honest and
    # what makes it unable to say anything the ladder does not already contain. Some things
    # are era-specific and are not ladder steps -- the Liquid Bifrost renewable route is one:
    # it belongs to Era VII because Era VII is the first to teach the mixer, but it is not a
    # tier and never will be. `extra` is where those live, on row y=8.0, below every derived
    # band (chain 0.0, methods -1.5, song 2.0, support 4.0, capstone 4.5, wound 6.0).
    q += meta.get('extra', [])

    # No truncation. A chapter is as long as its ladder plus its methods -- capping
    # it at 22 is what hid eleven of Era X's steps in the first place.
    return q


def main():
    eras = []
    for era in range(4, 11):
        meta = ERA_META[era]
        L = next(x for x in gen_ladder.LADDER if x['era'] == era)
        eras.append(dict(key=f'era_{era}', index=era - 1, title=meta['title'],
                         subtitle=meta['subtitle'],
                         icon=f'alfheim:{L["tier"]}', quests=build_era(era)))
    gen_quests.ERAS.extend(eras)

    # chapter_groups.snbt is NOT written here. It belongs to gen_compendium.py, which is the
    # only generator that knows about both groups.
    #
    # This file used to write it with gen_quests.CHAPTER_GROUPS, which declares one group --
    # so running this generator after gen_compendium.py silently deleted the Compendium's
    # group and with it all six reference chapters. The same defect was found and fixed in
    # gen_quests.py once already; this was the second copy of it, and it only surfaced because
    # a reproducibility check ran the full generator set in a different order.
    files = {
        os.path.join(gen_quests.OUT, 'data.snbt'): gen_quests.DATA,
    }
    for era in gen_quests.ERAS:
        files[os.path.join(gen_quests.OUT, 'chapters', era['key'] + '.snbt')] = \
            gen_quests.build_chapter(era)

    for path, content in files.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    total = sum(len(e['quests']) for e in gen_quests.ERAS)
    for e in gen_quests.ERAS:
        print(f"  {e['key']:8} {len(e['quests']):>3} quests  {e['title']}")
    print(f'\n{len(gen_quests.ERAS)} chapters, {total} quests')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
