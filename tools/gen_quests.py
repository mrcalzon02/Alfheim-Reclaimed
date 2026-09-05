"""Generate FTB Quests SNBT for Alfheim Reclaimed.

215 quests cannot be hand-authored, so eras are declared as Python data here and emitted as
SNBT. IDs are derived deterministically from a stable key, so regenerating does not churn
them and player progress survives edits.

Voice: every description is Magister Velrous, an elder elf teaching a vanguard of students
how to use their magic and rebuild the world. Second person. He is a teacher, not a narrator.

    python tools/gen_quests.py            # write to config/ftbquests/quests/
    python tools/gen_quests.py --dry-run
"""
import argparse
import hashlib
import os

OUT = os.path.join('config', 'ftbquests', 'quests')
GROUP_KEY = 'alfheim_reclaimed'


def qid(*parts):
    """Deterministic 16-char uppercase hex id from a stable key."""
    h = hashlib.sha1(('alfheim:' + ':'.join(parts)).encode('utf-8')).hexdigest()
    return h[:16].upper()


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def snbt_lines(key, lines, indent):
    pad = '\t' * indent
    if not lines:
        return f'{pad}{key}: [ ]'
    body = '\n'.join(f'{pad}\t"{esc(l)}"' for l in lines)
    return f'{pad}{key}: [\n{body}\n{pad}]'


# --------------------------------------------------------------------------- Era I

# (key, title, subtitle, description lines, tasks, rewards, deps, x, y, track)
# tasks/rewards: ('item', id) | ('item', id, count) | ('checkmark',) | ('advancement', adv)
ERA_I = [
    ('wake', 'You Are Awake', 'Magister Velrous',
     ["I did not think any of you would wake.",
      "",
      "Look around before you speak. That grey is not morning fog; it is what is left of the "
      "grove when the mana went out of it. The trees you see standing are dead and have been "
      "dead a long time.",
      "",
      "You are the first elves to stand in Alfheim since. Others will follow — but only when "
      "the way is clear, and it is not clear. That is the work.",
      "",
      "Take the books. Begin."],
     [('checkmark',)], [('item', 'botania:lexicon'), ('item', 'ftbquests:book')],
     [], 0.0, 0.0, 'leaf'),

    ('shelter', 'Somewhere To Stand', 'Before anything else',
     ["Cut yourself a shelter. Not a home — a place the spiders cannot reach tonight.",
      "",
      "There is no shame in this. Every restoration begins with someone deciding not to die "
      "in the first week."],
     [('item', 'minecraft:crafting_table')], [('item', 'minecraft:torch', 16)],
     ['wake'], 1.5, 0.0, 'support'),

    ('first_night', 'The First Night', 'Survive it',
     ["The dark here is not the dark you remember. Things live in the ruins now that did not "
      "ask permission.",
      "",
      "Survive until morning. That is the whole lesson."],
     [('checkmark',)], [('item', 'minecraft:cooked_beef', 6)],
     ['shelter'], 3.0, 0.0, 'wound'),

    ('spiders', 'The Infestation', 'Clear ten',
     ["The webs are not decoration. Something has been breeding in the roots of our cities for "
      "a very long time.",
      "",
      "Kill ten of them. Then look at what you killed — they are fat, and they are not hungry. "
      "Ask yourself what they have been eating."],
     [('kill', 'minecraft:spider', 10)], [('item', 'minecraft:string', 8)],
     ['first_night'], 4.5, 0.0, 'wound'),

    ('crops', 'Something That Grows', 'Horticulture',
     ["Find seed. Any seed. Put it in ground you have turned with your own hands and watch "
      "whether it comes up.",
      "",
      "You will spend ten eras learning to make plants do industrial work. It begins with "
      "proving that a plant will still grow here at all."],
     [('item', 'minecraft:wheat_seeds')], [('item', 'minecraft:bone_meal', 8)],
     ['shelter'], 1.5, 1.5, 'support'),

    ('ruin', 'What Fell Here', 'Clear a ruin',
     ["Find one of the collapsed houses and go through it properly.",
      "",
      "You are not looting. You are reading. The way a building failed tells you what killed it."],
     [('checkmark',)], [('item', 'minecraft:iron_ingot', 3)],
     ['spiders'], 6.0, 0.0, 'support'),

    ('apothecary_found', 'An Abandoned Apothecary', 'Recover one',
     ["You will find these scattered through the grove — stone basins with the petals still in "
      "them, dry as paper.",
      "",
      "Somebody was working when it happened. They did not finish. You will."],
     [('item', 'botania:apothecary_default')], [('item', 'botania:white_petal', 8)],
     ['ruin'], 7.5, 0.0, 'support'),

    ('pure_daisy', 'The Pure Daisy', 'The first flower',
     ["Here is the first thing I will teach you that matters.",
      "",
      "The Pure Daisy does not fight, does not harvest, does not produce. It simply insists — "
      "quietly, over hours — that the world nearby should be clean. Set it beside dead wood "
      "and wait.",
      "",
      "Do not stand over it. It will not work faster because you are impatient."],
     [('item', 'botania:pure_daisy')], [('item', 'botania:apothecary_default')],
     ['crops'], 1.5, 3.0, 'leaf'),

    ('dreamwood', 'Dreamwood', 'Not Livingwood',
     ["Your daisy will give you Dreamwood.",
      "",
      "I want you to understand why that is strange. In every account you were ever taught, an "
      "elf trades *for* Dreamwood — it is the far material, the one that comes through the "
      "gate. Here it grows out of dead logs in your own hands.",
      "",
      "We are on the other side of the gate now. What was exotic is native. What was ordinary "
      "is gone. Livingwood — plain, human Livingwood — you will not see again until you can "
      "trade for it."],
     [('item', 'botania:dreamwood_log')], [('item', 'botania:dreamwood', 8)],
     ['pure_daisy'], 3.0, 3.0, 'leaf'),

    ('twig', 'A Dreamwood Twig', 'Your first tool',
     ["Two pieces of Dreamwood, laid across each other.",
      "",
      "Small things first. You cannot hold a wand you have not made."],
     [('item', 'botania:dreamwood_twig')], [('item', 'botania:dreamwood', 4)],
     ['dreamwood'], 4.5, 3.0, 'leaf'),

    ('wand', 'The Wand of the Forest', 'How elves see',
     ["This is not a weapon and it is not a tool. It is a way of looking.",
      "",
      "Point it at anything botanical and it will tell you what that thing is doing. Most of "
      "what you need to learn in the next ten eras, you will learn by pointing this at "
      "something and paying attention."],
     [('item', 'botania:twig_wand')], [('item', 'botania:manasteel_ingot')],
     ['twig'], 6.0, 3.0, 'leaf'),

    ('apothecary_use', 'Petals and Water', 'Make a flower',
     ["Fill the basin. Put petals in it. Take out a living thing.",
      "",
      "You will do this ten thousand times before you are finished. Learn to enjoy it."],
     [('item', 'botania:endoflame')], [('item', 'botania:yellow_petal', 8)],
     ['apothecary_found'], 7.5, 1.5, 'leaf'),

    ('spreader', 'A Spreader of Dreamwood', 'Move the mana',
     ["Mana does not travel on its own. Something must throw it.",
      "",
      "Build the frame from Dreamwood. It will want a little copper too — we are not so proud "
      "that we refuse a good conductor.",
      "",
      "There is a finer pattern, worked in Elementium, that throws further and truer. You "
      "cannot make it yet. Elementium is a thing you dig out of Alfheim, and you have not "
      "learned where to dig."],
     [('item', 'botania:mana_spreader')], [('item', 'botania:dreamwood', 8)],
     ['wand'], 7.5, 3.0, 'leaf'),

    ('pool', 'The Diluted Pool', 'Somewhere to put it',
     ["A pool to catch what the spreader throws. Small. It will not hold much.",
      "",
      "When you see mana move from a flower, through the air, and settle into stone you shaped "
      "— that is the moment you stop being a refugee and start being an engineer.",
      "",
      "That is Era One. Everything after this is the same lesson, larger."],
     [('item', 'botania:diluted_pool')], [('item', 'botania:mana_pearl')],
     ['spreader'], 9.0, 3.0, 'leaf'),

    ('notebook', 'A Worn Notebook', 'Someone left it',
     ["This is not mine and it is not new. Somebody kept notes while the world was ending, and "
      "the notes are better than the ones I could give you.",
      "",
      "Read it. It teaches a different craft to mine — theirs works on *source*, not mana. Two "
      "traditions. You will need both, and I will not pretend I understand the second as well "
      "as I understand the first."],
     [('item', 'ars_nouveau:worn_notebook')], [('item', 'ars_nouveau:magebloom_fiber', 4)],
     ['wake'], 0.0, 3.0, 'song'),

    ('spellbook', 'The Novice Book', 'The other tradition',
     ["Bind yourself a book and write one glyph in it.",
      "",
      "I am a botanist. This is not my art, and I have watched enough students hurt themselves "
      "with it to be honest about that. Go slowly. It answers faster than a flower does, and "
      "that is exactly the danger."],
     [('item', 'ars_nouveau:novice_spell_book')], [('item', 'ars_nouveau:source_gem', 4)],
     ['notebook'], 0.0, 4.5, 'song'),

    ('gear', 'What The Dead Left', 'First equipment',
     ["Somewhere out there is the first thing worth wearing.",
      "",
      "Take it. They do not need it. And do not let sentiment slow you down — the fastest way "
      "to honour the dead of Alfheim is to not join them."],
     [('checkmark',)], [('item', 'minecraft:iron_ingot', 5)],
     ['ruin'], 6.0, 1.5, 'wound'),

    # ================================================================= GUIDES
    #
    # ERA_EXPANSION.md §3-4. Era I carries the heaviest teaching load in the pack, because
    # everything the player knows about Botania is wrong here and nothing else explains it.
    # Guides sit in the top band (negative y), gate nothing, and cost nothing.

    ('g_metal', 'Why There Is No Metal', 'Magister Velrous',
     ["You will dig, and you will find nothing, and you will assume I have sent you to a poor "
      "place. I have not. I have sent you to a place that was rich in a way that ruined it.",
      "",
      "When the ley-lines died, the mana in the bedrock did not drain away. It set. And it "
      "took the metal with it.",
      "",
      "What is down there now are BLOOMS — growths that hold the pattern of a metal without "
      "being one. Cinderbloom where coal should be. Palebloom where iron should be. "
      "Verdigris, green as a drowned coin, where copper should be.",
      "",
      "You cannot smelt them. Put one in a furnace and nothing happens, and you will think it "
      "a bug. It is not. The pattern is magical, not chemical, and heat has no argument with "
      "it.",
      "",
      "To open a bloom you give it living things. That is the next lesson."],
     [('checkmark',)], [], [], 0.0, -5.0, 'guide'),

    ('g_rite', 'The Steeping', 'The first Rite',
     ["Life completes the pattern. That is the whole of it, and it took us an age to learn.",
      "",
      "Put a raw bloom in a Petal Apothecary with two petals and one growing thing — grain, "
      "seed, a sapling. The water does the rest. What comes out is QUICKENED, and a quickened "
      "bloom will take heat.",
      "",
      "Bloom, into Rite, into metal. Three steps where the humans of Midgard have one. They "
      "would call that inefficient. They also cannot make iron out of a flower pot.",
      "",
      "There are three more Rites after this one, and each pays better than the last. You "
      "will not need them yet. The Steeping asks for no mana at all, which is the only reason "
      "you can perform it on your first morning."],
     [('checkmark',)], [], ['g_metal'], 2.0, -5.0, 'guide'),

    ('g_petals', 'Where Petals Come From', 'The thing everything needs',
     ["Petals gate the daisy, the wand, the spreader, the apothecary and every Rite. If you "
      "run out you stop, so learn all three sources now rather than the hard way.",
      "",
      "FIRST, LEAVES. Every tree in Alfheim drops petals of its own colour when you break its "
      "leaves. Dreamwood gives white and pale grey. The archwoods give their own colours. "
      "This is the reliable one, and it works from the first tree you find.",
      "",
      "SECOND, THE FLOWERS THEMSELVES, which still grow wild in the living places.",
      "",
      "THIRD, and remember this one — FLORAL FERTILIZER. Bone meal and four dyes. No petals "
      "in the recipe, which is the point: four white dyes will do, and bone meal comes from a "
      "composter, so you can make it out of nothing but weeds. Scatter it on grass and fresh "
      "mystical flowers come up.",
      "",
      "You cannot be stranded. Make sure you understand why."],
     [('checkmark',)], [('item', 'botania:fertilizer', 2)], ['g_rite'], 4.0, -5.0, 'guide'),

    ('g_energies', 'Three Energies', 'And they are not alike',
     ["Three powers run through this world and they look alike to a beginner. Confusing them "
      "will cost you a season.",
      "",
      "MANA is Botania's. Flowers make it. Spreaders throw it in straight lines that need "
      "clear sight — if your spreader will not fire, something is in the way of it. Pools "
      "and tablets hold it.",
      "",
      "SOURCE is the Song's. Sourcelinks make it, jars hold it, relays move it through the "
      "air without caring what stands between. It does not need a line.",
      "",
      "AURA belongs to the land, not to you. It sits in the chunk you are standing in. Draw "
      "too much and the ground itself degrades — and this grove is already drawn down, which "
      "is part of why nothing grows.",
      "",
      "Mana and Source you build. Aura you spend, and it does not forgive."],
     [('checkmark',)], [], ['g_petals'], 6.0, -5.0, 'guide'),

    ('g_reversal', 'The Gate Runs Outward', 'If you have done this before',
     ["Some of you will have read of Botania as the humans practise it. Set that down.",
      "",
      "In their telling, a human feeds ordinary goods into the Alfheim Portal and receives "
      "elven goods back. We are on the other side of that gate. The trade runs the other way.",
      "",
      "Dreamwood grows in our forests. Elementium is an ore we mine. What we cannot easily "
      "get is Livingwood, Manasteel, Mana Diamonds — the work of a Midgard we no longer reach "
      "freely.",
      "",
      "So the gate is not a prize at the end of your road. It is a trade route, it opens in "
      "the fourth era, and it leads OUT. Everything you build until then, you build alone."],
     [('checkmark',)], [], ['g_energies'], 8.0, -5.0, 'guide'),

    ('g_crystals', 'Reading a Geode', 'And the sign on the surface',
     ["Where the ley-lines ran hardest the mana did not merely set into stone. It separated "
      "by alignment, and it set as gem.",
      "",
      "So a geode is never one crystal. It is the seam between two — Emberglass against "
      "Duskglass, Tidewake against Galeglass — half and half, with a visible join. Which pair "
      "you find depends on where you are standing.",
      "",
      "Now the part worth walking for. LOOK AT THE GROUND. A small geode on the surface means "
      "a full one lies directly beneath it, within thirty-odd blocks. Those small ones never "
      "appear over empty stone. If you see the crystals, dig.",
      "",
      "The budding stone grows fresh clusters if you leave it be. Take the clusters and leave "
      "the bed, and it will keep paying you."],
     [('checkmark',)], [], ['g_reversal'], 10.0, -5.0, 'guide'),

    ('g_apothecary_read', 'Reading the Apothecary', 'Your first station',
     ["Livingrock, and water in the basin. That is all it is, and it will carry you for two "
      "eras.",
      "",
      "Fill it with water first — it does nothing dry, and half of everyone forgets. Then "
      "throw the ingredients in, one at a time, and strike the basin with your wand when the "
      "set is complete.",
      "",
      "Order does not matter. Quantity does. Two petals means two petals, not one used twice.",
      "",
      "It makes flowers, and it performs the Steeping. Those are the two jobs that begin "
      "everything else."],
     [('checkmark',)], [], ['g_rite'], 2.0, -3.5, 'guide'),

    ('g_spreader', 'Why Your Spreader Will Not Fire', 'Line of sight',
     ["A Mana Spreader is a thrower, not a pipe. It needs to SEE what it is feeding.",
      "",
      "Bind it with your wand: strike the spreader, then strike the pool. If the burst has "
      "anything in its way — a block, a fence, a torch you forgot — it will not connect, and "
      "the spreader will sit there looking healthy and doing nothing.",
      "",
      "Distance costs you. A burst loses mana over a long throw, so short lines beat clever "
      "ones.",
      "",
      "And a spreader will not pull from a flower it cannot see either. Build the flower, the "
      "spreader and the pool in a straight open line, and only make it elegant once it works."],
     [('checkmark',)], [], ['g_energies'], 6.0, -3.5, 'guide'),

    ('g_flowers_kind', 'Two Kinds of Flower', 'The distinction that defeats everyone',
     ["Botania's flowers come in two sorts and they do opposite jobs. Nothing in the book "
      "labels them clearly, so I will.",
      "",
      "GENERATING flowers make mana. They eat something — fuel, food, an event — and produce "
      "mana for a spreader to collect. The Endoflame burns coal. That is your first one.",
      "",
      "FUNCTIONAL flowers spend mana. They sit near a pool, draw from it, and do work: "
      "growing crops, moving items, killing things.",
      "",
      "A functional flower with nothing feeding it does nothing at all, and looks exactly "
      "like one that is working. Before you conclude a flower is broken, ask whether anything "
      "is filling it."],
     [('checkmark',)], [], ['g_spreader'], 8.0, -3.5, 'guide'),

    ('g_groves', 'The Archive Groves', 'Other forests, kept',
     ["You will notice there are no oaks here. No birch, no apple. Alfheim grew dreamwood and "
      "archwood and nothing else, and after the devastation it grew very little of either.",
      "",
      "But before the end, we kept a seed-archive — every forest of the Nine Realms, held in "
      "trust. Three trees survived it. Emberbark on the high dry ground. Gloambark in the wet "
      "dark. Hushbark where it is pale and quiet.",
      "",
      "Break their leaves and you will sometimes find a seed that is not theirs: oak, birch, "
      "spruce, cherry. Those grow normally. Plant them and you have wood, and apples, and a "
      "world that looks a little less like a graveyard.",
      "",
      "Rarely the tree gives up its own sapling too. Take that one and plant it somewhere "
      "safe. There are not many left."],
     [('checkmark',)], [], ['g_petals'], 4.0, -3.5, 'guide'),

    ('g_deficient', 'The Places That Finished Dying', 'Know them before you walk in',
     ["Not everywhere here is merely damaged. Some ground is done.",
      "",
      "The STARVED REACH grows nothing at all — not poisoned, not burned, just spent. The "
      "SCORCHFELL burned and is somehow still burning; there is ash in the air. The INFESTED "
      "WARREN has things living in the old roots that did not ask. The DECAYED MIRE is rot "
      "and standing water and whatever moves in it.",
      "",
      "And at the edge of everything is the VOID VERGE, where the ground thins, breaks into a "
      "cliff, and stops. What is left out there floats.",
      "",
      "I am not telling you to avoid them. The Verge holds the richest stone in Alfheim. I am "
      "telling you to know which one you are standing in before it matters."],
     [('checkmark',)], [], ['g_crystals'], 10.0, -3.5, 'guide'),

    ('g_wound', 'What The Ruins Became', 'Levels, and why they matter',
     ["The things in the ruins are not simply hostile. They have LEVELS, and so do you.",
      "",
      "A creature two levels above you does not fight harder. It fights on a different scale, "
      "and your good sword becomes a stick. Check what you are walking toward.",
      "",
      "Your gear has levels too, and rolled qualities that vary between two of the same item. "
      "A common blade with good rolls will outlast a rare one with poor ones.",
      "",
      "You will find orbs. Do not spend them the day you find them — some are worth far more "
      "later, and there is no way to get one back once it is used."],
     [('checkmark',)], [], [], 0.0, -3.5, 'guide'),

    # ---------------------------------------------------------------- Guides, second row
    # MAGIC_SYSTEMS.md §1: ten magic systems had no quest coverage at all across Eras I-III.
    # Each tradition now opens with a Guide that says what it IS before anything asks for its
    # materials. Guides gate nothing; they sit above the work and can be ignored.
    ('g_mana_fluid', 'Mana Is Not A Number', 'Magister Velrous',
     ["Forget every tally you have kept in your life. Mana is not a score.",
      "",
      "It is a fluid. It sits in a pool, it is thrown through the air in bursts, and every "
      "burst that misses is simply gone. You do not spend mana; you move it, and you lose "
      "some in the moving.",
      "",
      "This is why our workshops look like plumbing and not like arithmetic."],
     [('checkmark',)], [], [], 0.0, -6.5, 'guide'),

    ('g_pure_daisy', 'The Daisy Works Where It Stands', 'Magister Velrous',
     ["The Pure Daisy transmutes. It does not craft.",
      "",
      "Put it in the world, put the material beside it, and wait. It changes the block where "
      "the block lies. No basin, no table, no fuel - only patience, which is the one resource "
      "this grove still has in quantity.",
      "",
      "Wood becomes Dreamwood. Stone becomes Livingrock. Both take their time about it."],
     [('checkmark',)], [], [], 1.5, -6.5, 'guide'),

    ('g_heat', 'Heat Does Nothing', 'Magister Velrous',
     ["You will try to smelt a bloom. Everyone does. It will not work.",
      "",
      "A bloom is not ore and a furnace is not a rite. Fire opens metal; it does not open a "
      "living thing. What a bloom wants is time in water and a ring of petals - the Steeping.",
      "",
      "Once it is quickened, then heat has something to bite on. Order matters here more than "
      "temperature."],
     [('checkmark',)], [], [], 3.0, -6.5, 'guide'),

    ('g_aura', 'The Land Keeps Accounts', "Nature's Aura",
     ["There is a third power here, and it is the only one that can be owed.",
      "",
      "Aura is not carried and not thrown. It sits in the ground itself, chunk by chunk, and "
      "when you draw on it the land holds less than it did. It does not refill on its own.",
      "",
      "Make an Environmental Eye and look through it before you build anything. You will find "
      "that where you are standing is already poor - that is not an accident of terrain. "
      "Something drew this grove down and never paid it back."],
     [('checkmark',)], [], [], 4.5, -6.5, 'guide'),

    ('g_occult', 'Someone Was Here Before Us', 'Occultism',
     ["You will find stone that is the wrong colour and was never quarried.",
      "",
      "Otherstone is what is left where something was called across and did not go quietly. It "
      "predates the collapse. Whoever drew those circles is not here to explain them.",
      "",
      "Chalk, candles, a closed shape on the floor. The work is not difficult. Deciding to do "
      "it is the difficult part, and I will not decide for you."],
     [('checkmark',)], [], [], 6.0, -6.5, 'guide'),

    ('g_fey', 'Ask, Do Not Take', 'Feywild',
     ["The pixies survived. Of course they did.",
      "",
      "They will not be farmed, trapped or reasoned with, and they cannot be robbed - try it "
      "and you will find nothing in your hand. But they will trade, and their price is absurd "
      "and non-negotiable: sweets.",
      "",
      "Offer a cookie. Receive Fey Dust. This is the cheapest magic in Alfheim and the best "
      "lesson in it - everything here is a bargain, and the ones who forget that end up owing."],
     [('checkmark',)], [], [], 7.5, -6.5, 'guide'),

    ('g_arcane', 'The Magic Of The World That Died', "Iron's Spells",
     ["There is debris in the stone that is not ours.",
      "",
      "Humans made a magic of books and syllables - schools, cooldowns, ink. It was clumsy "
      "beside the Song and it worked anyway, and their world is the one that ended.",
      "",
      "You will find it here as wreckage, because Alfheim traded with Midgard for a long time "
      "before the gate closed. Learn it if you like. It is a dead craft, and it is still the "
      "fastest way to put fire in your hand."],
     [('checkmark',)], [], [], 9.0, -6.5, 'guide'),

    ('g_book', 'How This Book Works', 'Magister Velrous',
     ["Two kinds of entry, and you can tell them apart at a glance.",
      "",
      "The gear-shaped ones are me talking. They cost nothing, unlock nothing, and can be "
      "ignored entirely. Read them anyway - nothing else in this pack will explain why a "
      "spreader refuses to fire.",
      "",
      "The rest are work. Those chain, and the chains are what carry you between eras."],
     [('checkmark',)], [], [], 10.5, -6.5, 'guide'),

    # ---------------------------------------------------------------- Nature's Aura
    ('aura_eye', 'Look At The Ground', "Nature's Aura",
     ["Before you take anything out of this grove, measure what is in it.",
      "",
      "The Eye is glass and gold fibre and it shows you the aura of the chunk you stand in. "
      "Carry it. Look often. You are about to learn that the Ashen Grove is not poor by "
      "metaphor."],
     [('item', 'naturesaura:eye')], [('item', 'naturesaura:gold_fiber', 4)],
     ['pure_daisy'], 1.5, 6.0, 'leaf'),

    ('aura_read', 'A Grove Drawn Down', "Nature's Aura",
     ["Now you have seen the number.",
      "",
      "Low. Lower than any forest has business being. Something stood here and pulled until "
      "there was nothing left to pull, and then the trees died standing up.",
      "",
      "Remember it, because you are about to start drawing on it yourself."],
     [('checkmark',)], [('item', 'naturesaura:gold_fiber', 8)],
     ['aura_eye'], 3.0, 6.0, 'leaf'),

    ('aura_altar', 'The Natural Altar', "Nature's Aura",
     ["A flat stone under open sky, and the air does the rest.",
      "",
      "This is the crudest of the three energies and the only honest one: it takes from the "
      "place you are standing, visibly, and it tells you what it took."],
     [('item', 'naturesaura:nature_altar')], [('item', 'botania:white_petal', 8)],
     ['aura_read'], 4.5, 6.0, 'leaf'),

    # ---------------------------------------------------------------- Occultism
    ('occ_otherstone', 'Stone Of The Wrong Colour', 'Occultism',
     ["Bring me a piece of it.",
      "",
      "You will know it when you see it - it belongs to no layer, and it is burnt in a way "
      "stone does not burn. Someone opened a door here. The door is shut. The frame is not."],
     [('item', 'occultism:burnt_otherstone')], [('item', 'occultism:chalk_white')],
     ['ruin'], 1.5, 7.5, 'support'),

    ('occ_book', 'The Taboo Book', 'Occultism',
     ["Read it. I am not going to pretend I approve.",
      "",
      "It is a catalogue of things that can be called and what each of them will accept as "
      "payment. The elves who wrote our histories left this out on purpose, which tells you "
      "either that it is beneath us or that it worked."],
     [('item', 'occultism:taboo_book')], [('item', 'minecraft:gold_ingot', 3)],
     ['occ_otherstone'], 3.0, 7.5, 'support'),

    # ---------------------------------------------------------------- Feywild
    ('fey_cookie', 'Bring A Cookie', 'Feywild',
     ["I am entirely serious.",
      "",
      "Bake it, carry it, and find something small and bright that watches you from the "
      "leaves. Hold it out. Do not grab."],
     [('item', 'minecraft:cookie', 4)], [('item', 'minecraft:sugar', 8)],
     ['crops'], 1.5, 9.0, 'support'),

    ('fey_dust', 'Fey Dust', 'Feywild',
     ["There. That is a fair trade, and you are now on speaking terms with a species that "
      "outlived the collapse without lifting a finger.",
      "",
      "The dust is in everything they touch. Keep it - the Court will want it long before you "
      "understand why."],
     [('item', 'feywild:fey_dust')], [('item', 'feywild:feywild_lexicon')],
     ['fey_cookie'], 3.0, 9.0, 'support'),

    ('fey_lexicon', 'Their Own Account', 'Feywild',
     ["The pixies keep a book, after a fashion, and it is more reliable than ours on the "
      "subject of pixies.",
      "",
      "Read the parts about the courts. You will meet them, and they do not all like each "
      "other."],
     [('checkmark',)], [('item', 'feywild:fey_dust', 2)],
     ['fey_dust'], 4.5, 9.0, 'support'),

    # ---------------------------------------------------------------- Iron's Spellbooks
    ('arc_debris', 'Wreckage In The Stone', "Iron's Spells",
     ["Dig down and you will strike something black and glassy that no elf put there.",
      "",
      "Arcane Debris. It came through the gate as trade goods, or as weapons, and then the "
      "gate shut with it still in the ground."],
     [('item', 'irons_spellbooks:arcane_debris')], [('item', 'minecraft:iron_ingot', 4)],
     ['ruin'], 1.5, 10.5, 'song'),

    ('arc_essence', 'What Is Left In It', "Iron's Spells",
     ["Break the debris down and the magic is still in there, thin but awake.",
      "",
      "Human magic keeps. That is the frightening thing about it - ours needs a living flower "
      "and theirs needs a jar."],
     [('item', 'irons_spellbooks:arcane_essence')], [('item', 'minecraft:lapis_lazuli', 8)],
     ['arc_debris'], 3.0, 10.5, 'song'),

    ('arc_ink', 'A Dead Craft, Learned', "Iron's Spells",
     ["Ink, and something to write on.",
      "",
      "You are about to learn the magic of the world that died. Learn it well enough to know "
      "why it died, and you will have got more out of it than they did."],
     [('item', 'irons_spellbooks:common_ink')], [('item', 'irons_spellbooks:arcane_essence', 2)],
     ['arc_essence'], 4.5, 10.5, 'song'),

    # ---------------------------------------------------------------- The Court
    ('court_velrous', 'Present Yourself', 'The Hollow Court',
     ["You have been working alone long enough that I am beginning to take it personally.",
      "",
      "Come to the amphitheatre. Carry a Petition Scroll - the Court is reduced, not informal, "
      "and I am still owed the courtesy."],
     [('item', 'quest_giver:quest_scroll')], [('item', 'botania:white_petal', 16)],
     ['apothecary_use'], 9.0, 2.0, 'support'),

    ('court_orenvel', 'The Captain Is Waiting', 'The Hollow Court',
     ["Orenvel holds the roster and the armoury key, and there is nobody left on the roster.",
      "",
      "He will not say so, but he has been waiting eleven years for someone to report. Do not "
      "make a speech. He will hate that."],
     [('checkmark',)], [('item', 'minecraft:iron_ingot', 4)],
     ['court_velrous'], 10.5, 2.0, 'support'),

    # ---------------------------------------------------------------- Leaf, extended
    ('petal_colours', 'Four Colours', 'Leaf',
     ["One colour is an accident. Four is a supply.",
      "",
      "The leaves of this forest drop by species, so four colours means four kinds of tree "
      "found and stripped. Go and find them."],
     [('item', 'botania:white_petal', 8), ('item', 'botania:pink_petal', 8)],
     [('item', 'botania:fertilizer', 2)],
     ['apothecary_use'], 10.5, 0.0, 'leaf'),

    ('fertilizer', 'Floral Fertilizer', 'Leaf',
     ["Bone meal and four dyes, and the ground answers with flowers you did not plant.",
      "",
      "It is not elegant. It is the fastest way from an empty grove to sixteen colours, and "
      "elegance is a later era's problem."],
     [('item', 'botania:fertilizer')], [('item', 'botania:pink_petal', 8)],
     ['petal_colours'], 12.0, 0.0, 'leaf'),

    ('bloom_find', 'Read The Surface', 'Leaf',
     ["Blooms grow in stone, and stone tells you which one before you break it.",
      "",
      "The sign is on the surface - a colour in the rock that has no business being there. "
      "Learn the signs and you will stop mining hopefully."],
     [('item', 'alfheim:raw_cinderbloom')], [('item', 'minecraft:torch', 16)],
     ['dreamwood'], 10.5, 1.5, 'leaf'),

    ('bloom_steep', 'Rite I - The Steeping', 'Leaf',
     ["Water, petals, patience. No fire.",
      "",
      "The bloom comes out quickened, and a quickened bloom will give up its metal to a "
      "furnace the way ore never did. This is how Alfheim has metal at all."],
     [('item', 'alfheim:quickened_cinderbloom')], [('item', 'minecraft:coal', 8)],
     ['bloom_find'], 12.0, 1.5, 'leaf'),

    # The render. This is the payoff of the entire ore chain and it had no quest at all --
    # found by check_coverage.py, which scored rite:render as 12 recipes and 0 covered.
    # Alfheim's vanilla ore layer was retired with B-47, so a rendered bloom is the ONLY
    # source of coal in this world. Asking for coal here is asking for the whole chain.
    ('bloom_render', 'Rite I Concluded - The Rendering', 'Leaf',
     ["Now put it in the fire.",
      "",
      "Not before. A raw bloom in a furnace gives you nothing and teaches you nothing; a "
      "quickened one gives up what it has been holding.",
      "",
      "There is no coal seam in Alfheim. There is no iron vein. Every scrap of metal on this "
      "side of the gate came out of a flower that someone steeped first - and now you have "
      "done the whole of it yourself, from a coloured stain in the rock to a useful thing in "
      "your hand."],
     [('item', 'minecraft:coal', 8)], [('item', 'alfheim:raw_palebloom', 4)],
     ['bloom_steep'], 13.5, 1.5, 'leaf'),

    # ---------------------------------------------------------------- Song, extended
    ('song_source', 'Source Is Not Mana', 'Song',
     ["Do not let the glow fool you. Source and mana share nothing but a colour.",
      "",
      "Source is generated by Sourcelinks and carried by relays, within range, without line of "
      "sight. It will not fill a mana pool and a mana pool will not fill it."],
     [('item', 'ars_nouveau:source_gem', 4)], [('item', 'ars_nouveau:magebloom_fiber', 4)],
     ['spellbook'], 1.5, 4.5, 'song'),

    ('song_glyph', 'Form, Effect, Augment', 'Song',
     ["Every spell in the Song is three questions in order. What shape does it take? What does "
      "it do? And how hard?",
      "",
      "Get the order wrong and the spell simply will not assemble. That is the Song being "
      "strict, not broken."],
     [('checkmark',)], [('item', 'ars_nouveau:source_gem', 4)],
     ['song_source'], 3.0, 4.5, 'song'),

    # ---------------------------------------------------------------- The Wound, extended
    ('wound_level', 'You Are Level One', 'The Wound',
     ["Whatever you were before you slept, you are level one now.",
      "",
      "So is almost everything in this grove, which is the only reason you are still standing. "
      "Kill things near your own level until that stops being true."],
     [('kill', 'minecraft:zombie', 8)], [('item', 'minecraft:cooked_beef', 8)],
     ['spiders'], 6.0, 3.0, 'wound'),

    ('wound_orb', 'Do Not Spend It', 'The Wound',
     ["You will find orbs. They are currency, and they are the only currency here that cannot "
      "be remade.",
      "",
      "A common orb spent on a common blade in your first week is an orb you will want back in "
      "your fifth. Hold them. Boredom is cheaper than regret."],
     [('checkmark',)], [('item', 'minecraft:gold_ingot', 3)],
     ['wound_level'], 7.5, 3.0, 'wound'),

    ('wound_clear', 'The Understory', 'The Wound',
     ["Orenvel will ask you for this whether you take it from me or not.",
      "",
      "The Court is not haunted. It is infested. Clear far enough out that the amphitheatre is "
      "quiet, and he will start talking to you like a soldier."],
     [('kill', 'minecraft:spider', 20)], [('item', 'minecraft:string', 16)],
     ['wound_orb'], 9.0, 3.0, 'wound'),

    ('wound_gear_roll', 'Two Of The Same Sword', 'The Wound',
     ["Pick up two blades of the same name and compare them properly.",
      "",
      "They are not the same blade. The rolls differ, and a common weapon that rolled well "
      "will outlast a rare one that did not. Read before you equip."],
     [('checkmark',)], [('item', 'minecraft:iron_ingot', 6)],
     ['wound_clear'], 10.5, 3.0, 'wound'),
]

# --------------------------------------------------------------------------- Era II

ERA_II = [
    ('livingrock', 'Stone That Remembers', 'Leaf',
     ["Set the daisy beside plain stone this time, not wood.",
      "",
      "Livingrock is the material every elven workshop is built from. It is not stronger than "
      "stone. It simply holds a charge, the way a good student holds an idea."],
     [('item', 'botania:livingrock', 16)], [('item', 'botania:livingrock', 8)],
     [], 0.0, 0.0, 'leaf'),

    ('mana_pool', 'The Pool', 'Somewhere it gathers',
     ["The Diluted Pool taught you the shape. This is the real one.",
      "",
      "Everything you build for the next nine eras draws from a pool like this. Put it "
      "somewhere you are willing to walk to a thousand times."],
     [('item', 'botania:mana_pool')], [('item', 'botania:livingrock', 16)],
     ['livingrock'], 1.5, 0.0, 'leaf'),

    ('circuit', 'A Circuit', 'Flower, spreader, pool',
     ["Now put the three together and stand back.",
      "",
      "A flower that burns, a spreader that throws, a pool that holds. That is the whole of "
      "our industry in miniature, and every factory you build hereafter is this repeated "
      "until it is embarrassing."],
     [('checkmark',)], [('item', 'botania:mana_pearl')],
     ['mana_pool'], 3.0, 0.0, 'leaf'),

    ('tablet', 'Carry It With You', 'A mana tablet',
     ["Mana in a pool is mana that stays where you left it.",
      "",
      "Take some with you. You will need it far from home more often than you expect."],
     [('item', 'botania:mana_tablet')], [('item', 'botania:mana_pearl')],
     ['circuit'], 4.5, 0.0, 'leaf'),

    ('runic_altar', 'The Runic Altar', 'Where words are made',
     ["This is where our craft stops being gardening and starts being language.",
      "",
      "You lay materials around it, pour mana in, and it gives back a rune: a fixed idea, "
      "reusable. Every serious thing you make from here needs one."],
     [('item', 'botania:runic_altar')], [('item', 'botania:livingrock', 16)],
     ['tablet'], 6.0, 0.0, 'leaf'),

    ('first_rune', 'The First Rune', 'Earth',
     ["Begin with Earth. It is the patient one and it forgives a clumsy altar.",
      "",
      "When you hold it, look at it properly. Somebody made the first of these once, in a "
      "world that had not yet broken, and we have been copying them ever since."],
     [('item', 'botania:rune_earth')], [('item', 'botania:rune_water')],
     ['runic_altar'], 7.5, 0.0, 'leaf'),

    ('elementium', 'What The Ground Keeps', 'Dig',
     ["Here is a thing I want you to find out for yourself, so I will only point.",
      "",
      "Go underground. Look for a green-white ore in the livingrock. When you find it, "
      "remember every book that told you Elementium comes through the gate.",
      "",
      "It does not. It is ours. It was always under our feet. They had the gate and we had "
      "the mine, and we let them tell the story."],
     [('item', 'botania:elementium_ingot')], [('item', 'botania:elementium_ingot', 2)],
     ['first_rune'], 9.0, 0.0, 'leaf'),

    ('archwood', 'Wood That Hums', 'Song',
     ["The other tradition needs its own timber.",
      "",
      "Archwood grows in the quieter valleys. You will hear it before you see it. Do not ask "
      "me how it does that; it is not my art."],
     [('item', 'ars_nouveau:archwood_planks', 8)], [('item', 'ars_nouveau:source_gem', 2)],
     [], 0.0, 2.0, 'song'),

    ('imbuement', 'The Imbuement Chamber', 'Source begins',
     ["Archwood and gold. The gold you will dig for; Alfheim keeps a great deal of it, which "
      "tells you something about what the elves valued.",
      "",
      "This chamber turns very little into Source, slowly. Let it be slow."],
     [('item', 'ars_nouveau:imbuement_chamber')], [('item', 'ars_nouveau:source_gem', 4)],
     ['archwood'], 1.5, 2.0, 'song'),

    ('source_gem', 'Source', 'The other current',
     ["Mana comes out of living things that are willing. Source comes out of events: growth, "
      "burning, dying, being.",
      "",
      "They are not the same, and you should stop trying to make them the same. I did, for "
      "two hundred years, and I was wrong."],
     [('item', 'ars_nouveau:source_gem', 8)], [('item', 'ars_nouveau:source_gem', 4)],
     ['imbuement'], 3.0, 2.0, 'song'),

    ('source_jar', 'A Jar of Source', 'Storage',
     ["Source will not hang in the air waiting for you. Put it somewhere."],
     [('item', 'ars_nouveau:source_jar')], [('item', 'ars_nouveau:source_gem', 4)],
     ['source_gem'], 4.5, 2.0, 'song'),

    ('sourcelink', 'Growth Into Source', 'The interlock',
     ["The Agronomic Sourcelink turns the fact of a plant growing into Source.",
      "",
      "Note what it stands on: our livingrock, their gold, their gems. Neither tradition made "
      "this alone. That is not an accident of the recipe. That is the point.",
      "",
      "Song cannot begin without Leaf. Remember that when one of you decides to specialise."],
     [('item', 'ars_nouveau:agronomic_sourcelink')], [('item', 'ars_nouveau:source_gem', 8)],
     ['source_jar'], 6.0, 2.0, 'song'),

    ('magelight', 'Light Without Fire', 'A small mercy',
     ["The grove is very dark, and torches are an insult to it.",
      "",
      "Make light that burns nothing. You will sleep better and so will the trees."],
     [('item', 'ars_nouveau:magelight_torch', 4)], [('item', 'minecraft:glowstone_dust', 8)],
     ['sourcelink'], 7.5, 2.0, 'song'),

    ('starbuncle', 'A Starbuncle', 'Your first familiar',
     ["It will carry things for you and steal things from you, and both are affection.",
      "",
      "Be kind to it. There is not much left in Alfheim that is glad to see anyone."],
     [('item', 'ars_nouveau:starbuncle_charm')], [('item', 'ars_nouveau:source_gem', 8)],
     ['magelight'], 9.0, 2.0, 'song'),

    ('colonists', 'The First To Follow', 'Support',
     ["I said others would come when the way was clear. It is not clear. But it is clearer, "
      "and some of them would rather risk it than keep waiting.",
      "",
      "Set down a supply camp. Whoever arrives will need somewhere to put their hands."],
     [('item', 'minecolonies:supplychestdeployer')], [('item', 'minecraft:oak_log', 32)],
     [], 0.0, 4.0, 'support'),

    ('builder', 'A Builders Hut', 'Somebody else does the work',
     ["You cannot rebuild a civilisation by hand. That is not humility, it is arithmetic.",
      "",
      "Give the first of them a hut and a purpose. Watch what happens when an elf who is not "
      "you decides where a wall goes."],
     [('item', 'minecolonies:blockhutbuilder')], [('item', 'minecraft:iron_ingot', 8)],
     ['colonists'], 1.5, 4.0, 'support'),

    ('kitchen', 'A Kitchen', 'Feed them',
     ["A colony that eats badly does not build well.",
      "",
      "This is not a small quest. Every settlement in the old records failed at the larder "
      "before it failed at the wall."],
     [('item', 'farmersdelight:cooking_pot')], [('item', 'minecraft:bread', 8)],
     ['builder'], 3.0, 4.0, 'support'),

    ('shrine', 'Restore a Shrine', 'One small thing put right',
     ["Find one of the broken shrines and make it whole. Not useful. Whole.",
      "",
      "You will want to argue that this is a waste of stone. Do it anyway. The others are "
      "coming home to a graveyard, and it would be good if one thing in it were standing."],
     [('checkmark',)], [('item', 'botania:mana_pearl')],
     ['kitchen'], 4.5, 4.0, 'support'),

    ('map', 'An Adventure Map', 'The Wound',
     ["The ruins go deeper than they look, and something has been living down there.",
      "",
      "Take a map. Do not take it alone."],
     [('item', 'dungeon_realm:dungeon_map')], [('item', 'minecraft:golden_apple')],
     [], 0.0, 6.0, 'wound'),

    ('chart', 'Chart the Ruins', 'Make your own',
     ["Once you can draw your own maps you stop being a scavenger and start being an "
      "expedition."],
     [('item', 'mmorpg:map_creator')], [('item', 'minecraft:experience_bottle', 8)],
     ['map'], 1.5, 6.0, 'wound'),

    ('named', 'Something With A Name', 'Kill it',
     ["Down there is something the ruin has been feeding. It has a name now, which means it "
      "has been alive long enough to earn one.",
      "",
      "Take that away from it."],
     [('checkmark',)], [('item', 'botania:mana_diamond')],
     ['chart'], 3.0, 6.0, 'wound'),

    ('rune_of_alfheim', 'The Rune of Alfheim', 'Capstone',
     ["Elementium from your own mine. Runes from your own altar. Leaves from six trees that "
      "should not still be alive.",
      "",
      "Lay them out and make the Rune of Alfheim.",
      "",
      "Understand what you are holding. It is not a key and it is not a trophy. It is a "
      "claim. It says the ground under you is Alfheim, and that it answers to elves again.",
      "",
      "It is the smallest possible version of that claim. There are eight more."],
     [('item', 'mythicbotany:alfheim_rune')], [('item', 'botania:elementium_ingot', 4)],
     ['elementium', 'starbuncle', 'named'], 6.0, 4.5, 'leaf'),

    # ---------------------------------------------------------------- Guides
    # Era II had ZERO guides, which is why MAGIC_SYSTEMS.md calls it the worst gap in the tree:
    # ERA_EXPANSION.md §4.1 puts the three-energies disambiguation here, and it was missing
    # entirely. These 19 are the second teaching layer -- Era I says what a system IS, Era II
    # says how it fails.
    ('g2_mana_pool', 'The Pool, And The Diluted Trap', 'Magister Velrous',
     ["A Mana Pool holds what your spreaders throw at it. Simple enough.",
      "",
      "But there is a second recipe for a smaller pool, and it looks like a saving. It is not. "
      "The Diluted Pool holds a tenth as much and every guide that ever ruined a beginner "
      "recommended it as a starter.",
      "",
      "Build the full pool. You will fill it slowly and then never think about it again."],
     [('checkmark',)], [], [], 0.0, -6.0, 'guide'),

    ('g2_los', 'Line Of Sight, Not Distance', 'Magister Velrous',
     ["A spreader throws a physical burst. The burst travels, and anything in the way stops it.",
      "",
      "A leaf. A fence. Your own scaffolding. If a spreader is not filling a pool, the answer "
      "is almost never mana and almost always a block you forgot you placed.",
      "",
      "Stand where the spreader stands and look. If you cannot see the pool, neither can it."],
     [('checkmark',)], [], [], 1.5, -6.0, 'guide'),

    ('g2_burst_loss', 'Distance Costs', 'Magister Velrous',
     ["A burst loses mana as it flies. Not much over a short hop; a great deal over a long one.",
      "",
      "Two short throws beat one long one, which is why our workshops are cramped and full of "
      "relays rather than elegant and spread out. Efficiency here looks like clutter."],
     [('checkmark',)], [], [], 3.0, -6.0, 'guide'),

    ('g2_tablet', 'Mana You Can Carry', 'Magister Velrous',
     ["The pool does not travel. The tablet does.",
      "",
      "Fill it at the pool, carry it to the work, and it will feed a rod or a tool in the "
      "field. It is the difference between a workshop and an expedition."],
     [('checkmark',)], [], [], 4.5, -6.0, 'guide'),

    ('g2_runic', 'Runes Are Catalysts', 'Magister Velrous',
     ["This one costs people whole afternoons, so read it twice.",
      "",
      "A rune is placed on the altar and it is NOT consumed. It sits there, it makes the "
      "working possible, and you take it back afterwards.",
      "",
      "You need one of each rune, once, forever. Not one per craft. Anyone who tells you to "
      "mass-produce runes has misread the altar."],
     [('checkmark',)], [], [], 6.0, -6.0, 'guide'),

    ('g2_rite2', 'Rite II - The Quickening', 'Magister Velrous',
     ["The Steeping wakes a bloom. The Quickening opens it.",
      "",
      "Where Rite I was water and patience, this one is mana and a ring of petals on the Runic "
      "Altar, and it returns far more than steeping alone. It is the first working that pays "
      "for the infrastructure you have been building."],
     [('checkmark',)], [], [], 7.5, -6.0, 'guide'),

    ('g2_smelter', 'Mana Is Now Your Furnace', 'Magister Velrous',
     ["From here you stop burning things.",
      "",
      "Mana infusion replaces smelting for everything that matters, and it is not a "
      "substitution of convenience - it yields what fire cannot. Keep a furnace for bread. "
      "Everything else goes in the pool."],
     [('checkmark',)], [], [], 9.0, -6.0, 'guide'),

    ('g2_source_gen', 'Sourcelinks Make, They Do Not Keep', 'Song',
     ["The commonest Song mistake, and it looks like a bug when it happens to you.",
      "",
      "A Sourcelink generates Source. It does not store it. Without a Jar in range the Source "
      "is made and immediately lost, and your Agronomic link will look broken while it is "
      "working perfectly.",
      "",
      "Generation, storage and delivery are three separate blocks. Build all three."],
     [('checkmark',)], [], [], 0.0, -4.5, 'guide'),

    ('g2_jar_relay', 'Jars Hold, Relays Carry', 'Song',
     ["Source moves by relay, within a radius, and it does not care what is between them.",
      "",
      "This is the opposite of a mana spreader in every respect, which is exactly why people "
      "who learn Leaf first keep building the Song wrong. No line of sight. No bursts. Just "
      "range."],
     [('checkmark',)], [], [], 1.5, -4.5, 'guide'),

    ('g2_spell_parts', 'Form, Then Effect, Then Augment', 'Song',
     ["A spell is read left to right and it is strict.",
      "",
      "The Form comes first and decides the shape - touch, projectile, self. Then the Effects, "
      "in order. Then Augments, which modify the effect immediately before them, not the whole "
      "spell.",
      "",
      "An Amplify in the wrong slot amplifies the wrong thing. The Scribe's Table will let you "
      "do it, too."],
     [('checkmark',)], [], [], 3.0, -4.5, 'guide'),

    ('g2_glyph_cost', 'Every Glyph Costs', 'Song',
     ["The book has a mana bar of its own and each glyph you add makes the spell dearer.",
      "",
      "A three-glyph spell you can cast eight times is worth more than a six-glyph spell you "
      "can cast twice. Restraint is a mechanic here, not a virtue."],
     [('checkmark',)], [], [], 4.5, -4.5, 'guide'),

    ('g2_scribes', "The Scribe's Table", 'Song',
     ["Glyphs are not found. They are written, from experience and reagents, at the table.",
      "",
      "Unlock them deliberately. The book will only hold what you have scribed, and the "
      "reagent for a glyph is usually a hint about what it does."],
     [('checkmark',)], [], [], 6.0, -4.5, 'guide'),

    ('g2_aura_draw', 'What You Draw Down Stays Down', "Nature's Aura",
     ["You have an altar now, so here is the bill.",
      "",
      "Every infusion takes aura from the chunk it happens in. The chunk does not refill on a "
      "timer and there is no reservoir underneath. Work in one place long enough and the land "
      "there will stop working at all - and it will show, visibly, in the world.",
      "",
      "Move your altar. Or plant. Those are the two answers and there is not a third."],
     [('checkmark',)], [], [], 7.5, -4.5, 'guide'),

    ('g2_aura_flower', 'The Land Tells You First', "Nature's Aura",
     ["Before the ground fails it warns you.",
      "",
      "Colour goes out of the grass. The aura blooms stop appearing. Read the warning and move; "
      "ignore it and you will be standing in a second Ashen Grove of your own making.",
      "",
      "That is not a metaphor I am reaching for. It is the mechanic, and it is what happened "
      "here."],
     [('checkmark',)], [], [], 9.0, -4.5, 'guide'),

    ('g2_chalk', 'A Closed Circle', 'Occultism',
     ["Chalk on stone, candles at the points, and the shape must close.",
      "",
      "A pentacle with a gap is not a weaker pentacle, it is nothing at all. Count your glyphs "
      "before you light anything.",
      "",
      "What you call is bound by the circle, and the circle is only as good as its worst line."],
     [('checkmark',)], [], [], 0.0, -3.0, 'guide'),

    ('g2_foliot', 'A Foliot Is Not A Machine', 'Occultism',
     ["It is the lowest thing you can bind and it is still a someone.",
      "",
      "Give it a job and it does the job, indefinitely, without power or fuel or a mana line. "
      "That is the appeal, and it is why this tradition keeps being rediscovered by people who "
      "swore they would not.",
      "",
      "I am not going to moralise. I will only note that nothing else in this pack works for "
      "free, and that should tell you the cost is somewhere you have not looked."],
     [('checkmark',)], [], [], 1.5, -3.0, 'guide'),

    ('g2_fey_altar_five', 'Always Five', 'Feywild',
     ["The Fey Altar takes five offerings. Not four, not six.",
      "",
      "Every recipe in their tradition is built on five, and a short offering simply does not "
      "resolve. If an altar is refusing you, count again before you blame the recipe."],
     [('checkmark',)], [], [], 3.0, -3.0, 'guide'),

    ('g2_spellbook', 'Schools And Cooldowns', "Iron's Spells",
     ["Human magic sorts itself into schools, and a book is loyal to one of them.",
      "",
      "A copper book holds little and casts slowly. What it teaches you is the shape of the "
      "system: schools, cooldowns, and a mana bar that is not Botania's and not Ars Nouveau's.",
      "",
      "Four energy systems now, if you are counting. I did warn you."],
     [('checkmark',)], [], [], 4.5, -3.0, 'guide'),

    ('g2_bridge', 'Mana In A Bottle', 'Create: Wizardry',
     ["Here is the join, and it is the most important thing in this era.",
      "",
      "Mana can be bottled. Once it is a fluid in a container it is a fluid Create can pump, "
      "measure and pipe - and the moment that is true, the industry of the dead world runs on "
      "elven power.",
      "",
      "That is the whole design of this pack in one item. Nothing in Create will be allowed to "
      "matter unless it drinks from a spine first."],
     [('checkmark',)], [], [], 6.0, -3.0, 'guide'),

    # ---------------------------------------------------------------- Nature's Aura
    ('aura2_fiber', 'Gold Fibre', "Nature's Aura",
     ["Gold drawn out until it will carry aura the way a wick carries oil.",
      "",
      "Everything in this tradition is built on it. Make a great deal more than you think you "
      "need."],
     [('item', 'naturesaura:gold_fiber', 8)], [('item', 'minecraft:gold_ingot', 4)],
     ['livingrock'], 1.5, 6.0, 'leaf'),

    ('aura2_infuse', 'The First Infusion', "Nature's Aura",
     ["Set it on the altar and let the sky pay for it.",
      "",
      "Watch the Eye while it works. That falling number is the chunk you are standing in, and "
      "it is the first honest price anything in this pack has quoted you."],
     [('item', 'naturesaura:infused_iron')], [('item', 'naturesaura:gold_fiber', 8)],
     ['aura2_fiber'], 3.0, 6.0, 'leaf'),

    ('aura2_cache', 'Somewhere To Put It', "Nature's Aura",
     ["A cache holds aura outside the ground, which means you can carry a good chunk's worth "
      "into a poor one.",
      "",
      "It does not create anything. It moves the debt. Remember that when you are tempted to "
      "call it a solution."],
     [('item', 'naturesaura:aura_cache')], [('item', 'naturesaura:token_joy', 2)],
     ['aura2_infuse'], 4.5, 6.0, 'leaf'),

    # ---------------------------------------------------------------- Occultism
    ('occ2_chalk', 'White Chalk', 'Occultism',
     ["Mana-worked metal, ground to dust and bound. Even this tradition has to come through "
      "the Pool to start.",
      "",
      "Draw with it on stone. The glyph stays until something scuffs it, so pick your floor."],
     [('item', 'occultism:chalk_white')], [('item', 'occultism:candle_white', 4)],
     ['mana_pool'], 1.5, 7.5, 'support'),

    ('occ2_bowl', 'The Sacrificial Bowl', 'Occultism',
     ["The bowl is where the offering goes and where the circle is anchored.",
      "",
      "Set one at the centre. Candles at the points. Then read the book again, properly, "
      "before you light anything."],
     [('item', 'occultism:sacrificial_bowl')], [('item', 'occultism:chalk_white')],
     ['occ2_chalk'], 3.0, 7.5, 'support'),

    ('occ2_binding', 'A Book Of Binding', 'Occultism',
     ["The terms, written down, for the smallest thing that will come.",
      "",
      "A Foliot. It will fetch, or it will crush, or it will trade - one task, forever, without "
      "a mana line or a millstone. Decide which before you call it."],
     [('item', 'occultism:book_of_binding_foliot')], [('item', 'minecraft:gold_ingot', 6)],
     ['occ2_bowl'], 4.5, 7.5, 'support'),

    # ---------------------------------------------------------------- Feywild
    ('fey2_altar', 'The Fey Altar', 'Feywild',
     ["Five offerings, arranged, and something on the other side decides whether it likes them.",
      "",
      "It is the only station in the pack that can refuse you for reasons of taste. Petals help. "
      "They always help."],
     [('item', 'feywild:fey_altar')], [('item', 'feywild:fey_dust', 4)],
     ['mana_pool'], 1.5, 9.0, 'support'),

    ('fey2_gem', 'A Fey Gem', 'Feywild',
     ["Dust compressed until it holds its shape, or torn out of a scarred log by a very "
      "annoyed tree.",
      "",
      "Either way it is the currency of every bargain worth making with them. MythicBotany "
      "wants one too, for a flower you will meet in the next era."],
     [('item', 'feywild:fey_gem')], [('item', 'feywild:fey_dust', 6)],
     ['fey2_altar'], 3.0, 9.0, 'support'),

    ('fey2_scroll', 'An Empty Scroll', 'Feywild',
     ["Blank, and waiting for a name.",
      "",
      "A summoning scroll is a written invitation, and the courts hold you to what it says. "
      "Fill one in when you know which court you would rather owe."],
     [('item', 'feywild:empty_summoning_scroll')], [('item', 'feywild:fey_gem')],
     ['fey2_gem'], 4.5, 9.0, 'support'),

    # ---------------------------------------------------------------- Iron's Spellbooks
    ('arc2_book', 'A Copper Book', "Iron's Spells",
     ["Thin, slow, and it holds almost nothing.",
      "",
      "It is also the first time in your life something has cast a spell for you because you "
      "read it correctly rather than because you grew it. Sit with that."],
     [('item', 'irons_spellbooks:copper_spell_book')], [('item', 'irons_spellbooks:common_ink', 4)],
     ['mana_pool'], 1.5, 10.5, 'song'),

    ('arc2_scroll', 'One Spell, Written Down', "Iron's Spells",
     ["Ink, a blank, and a school to commit to.",
      "",
      "Their magic does not grow and cannot be tended. It is copied. That is its weakness and "
      "the reason it spread across a whole world while ours stayed in one forest."],
     [('item', 'irons_spellbooks:scroll')], [('item', 'irons_spellbooks:arcane_essence', 4)],
     ['arc2_book'], 3.0, 10.5, 'song'),

    ('arc2_anvil', 'The Arcane Anvil', "Iron's Spells",
     ["Where their runes go onto their gear.",
      "",
      "Crude beside an Enchanting Apparatus and considerably faster. Midgard was always in a "
      "hurry."],
     [('item', 'irons_spellbooks:arcane_anvil')], [('item', 'irons_spellbooks:arcane_ingot', 2)],
     ['arc2_scroll'], 4.5, 10.5, 'song'),

    # ---------------------------------------------------------------- Create: Wizardry
    ('cw_bottle', 'Mana In A Bottle', 'Create: Wizardry',
     ["Draw from a full pool into glass.",
      "",
      "It is a small thing to hold and it is the hinge of the entire pack: from here, elven "
      "power is a fluid, and a fluid is something the dead world's machinery already knows how "
      "to move."],
     [('item', 'create_wizardry:mana_bucket')], [('item', 'botania:mana_tablet')],
     ['tablet'], 1.5, 12.0, 'leaf'),

    ('cw_mithril', 'Crushed Mithril', 'Create: Wizardry',
     ["Their metal, our power.",
      "",
      "You will need a mill and you will need mana, and the fact that both are required is the "
      "point rather than an inconvenience."],
     [('item', 'create_wizardry:mithril_nugget')], [('item', 'create_wizardry:mana_bucket')],
     ['cw_bottle'], 3.0, 12.0, 'leaf'),

    # ---------------------------------------------------------------- Leaf, extended
    ('leaf2_diluted', 'Build The Full Pool', 'Leaf',
     ["Not the diluted one. I have said why.",
      "",
      "Livingrock, and a great deal of it. This is the single most important block you will "
      "place this era and it should feel expensive."],
     [('item', 'botania:mana_pool')], [('item', 'botania:livingrock', 16)],
     ['livingrock'], 7.5, 0.0, 'leaf'),

    ('leaf2_rune_earth', 'The First Rune', 'Leaf',
     ["One rune, made once, kept forever.",
      "",
      "Put it on the altar when a working calls for it and take it back when the working is "
      "done. If you find yourself making a second one, re-read the guide."],
     [('item', 'botania:rune_earth')], [('item', 'botania:manasteel_ingot', 2)],
     ['runic_altar'], 9.0, 0.0, 'leaf'),

    ('leaf2_quicken', 'Rite II - The Quickening', 'Leaf',
     ["Petals, mana, and a bloom that has already been steeped.",
      "",
      "The yield is several times what the Steeping alone gave you. This is the era where the "
      "grove starts paying you back."],
     [('item', 'alfheim:quickened_verdigris', 8)], [('item', 'minecraft:copper_ingot', 8)],
     ['leaf2_rune_earth'], 10.5, 0.0, 'leaf'),

    # The blast furnace half of the render, which had no coverage either.
    ('leaf2_render_fast', 'Rendering, Faster', 'Leaf',
     ["A blast furnace does the same work in half the time and wastes nothing.",
      "",
      "Palebloom renders to iron. Verdigris to copper. Cinderbloom to coal, which is what "
      "feeds the furnace that renders the other two - the grove pays for its own fire.",
      "",
      "You are no longer scraping a living out of this forest. You are running it."],
     [('item', 'minecraft:iron_ingot', 16)], [('item', 'alfheim:raw_palebloom', 8)],
     ['leaf2_quicken'], 12.0, 0.0, 'leaf'),

    ('leaf2_manasteel', 'Manasteel At Last', 'Leaf',
     ["An import in this world, and now you can make it.",
      "",
      "Drop iron into a full pool and wait. It is the first time the reversal cuts in your "
      "favour rather than against you."],
     [('item', 'botania:manasteel_ingot', 8)], [('item', 'botania:mana_tablet')],
     ['leaf2_diluted'], 7.5, 1.5, 'leaf'),

    ('leaf2_infuser', 'The Mana Infuser', 'Leaf',
     ["MythicBotany's own station, and the one that will carry the next four eras.",
      "",
      "It wants colours as well as materials - it will ask you what shade the working starts "
      "and ends in. Do not skip those; the mod means them."],
     [('item', 'mythicbotany:mana_infuser')], [('item', 'botania:mana_diamond', 2)],
     ['leaf2_manasteel'], 9.0, 1.5, 'leaf'),

    # ---------------------------------------------------------------- Song, extended
    ('song2_jar', 'Somewhere For Source To Go', 'Song',
     ["Build the jar before the link, or you will spend an afternoon watching nothing happen.",
      "",
      "Storage first, generation second, delivery third. That order is the whole of the Song's "
      "infrastructure."],
     [('item', 'ars_nouveau:source_jar')], [('item', 'ars_nouveau:source_gem', 8)],
     ['source_gem'], 7.5, 3.0, 'song'),

    ('song2_relay', 'Carry It', 'Song',
     ["A relay moves Source within its radius and does not care about walls.",
      "",
      "Chain them. It is the cheapest infrastructure in the pack and the reason a Song "
      "workshop can be spread out where a Leaf one cannot."],
     [('item', 'ars_nouveau:relay')], [('item', 'ars_nouveau:source_gem', 8)],
     ['song2_jar'], 9.0, 3.0, 'song'),

    ('song2_scribes', 'Write A Glyph', 'Song',
     ["The table, and then the first glyph you choose for yourself.",
      "",
      "Whatever you scribe first, you will use for a hundred hours. Choose a Form, not an "
      "Effect - Forms are what make the rest possible."],
     [('item', 'ars_nouveau:scribes_table')], [('item', 'ars_nouveau:magebloom_fiber', 8)],
     ['song2_relay'], 10.5, 3.0, 'song'),

    ('song2_apparatus', 'The Enchanting Apparatus', 'Song',
     ["Pedestals in a ring, a reagent at the centre, and Source in range.",
      "",
      "Placement is part of the recipe here. The Song asks you to build the working, not to "
      "type it into a grid."],
     [('item', 'ars_nouveau:enchanting_apparatus')], [('item', 'ars_nouveau:arcane_pedestal', 4)],
     ['song2_scribes'], 12.0, 3.0, 'song'),

    # ---------------------------------------------------------------- The Wound
    ('wound2_talent', 'Commit To Something', 'The Wound',
     ["The tree will let you dabble and dabbling is how people end up level thirty and "
      "useless.",
      "",
      "Pick a direction and spend into it. You can respec, at a price, and the price exists "
      "precisely so that the choice means something."],
     [('checkmark',)], [('item', 'minecraft:gold_ingot', 6)],
     ['map'], 7.5, 4.5, 'wound'),

    ('wound2_rarity', 'Rarity Is Not Quality', 'The Wound',
     ["A rare item has more affixes. It does not have better ones.",
      "",
      "Read the rolls. A common piece that rolled high on the stat you actually use will beat "
      "a rare one that rolled low on three you do not."],
     [('checkmark',)], [('item', 'minecraft:diamond', 2)],
     ['wound2_talent'], 9.0, 4.5, 'wound'),

    ('wound2_map', 'Your First Map', 'The Wound',
     ["An Adventure Map is a place that does not exist until you open it.",
      "",
      "Check its level against yours before you step through. The map does not care that you "
      "were brave."],
     [('item', 'dungeon_realm:dungeon_map')], [('item', 'minecraft:golden_apple', 2)],
     ['wound2_rarity'], 10.5, 4.5, 'wound'),

    ('wound2_orbs', 'What The Orbs Are For', 'The Wound',
     ["You have been hoarding them since Era I because I told you to. Here is the payoff.",
      "",
      "Orbs reroll. They change an affix, or its tier, or the whole set - and each kind does "
      "exactly one thing, so read before you use.",
      "",
      "Spend them on a piece you intend to keep, not on the best thing you happen to be "
      "holding this week."],
     [('checkmark',)], [('item', 'minecraft:diamond', 3)],
     ['wound2_map'], 12.0, 4.5, 'wound'),

    # ---------------------------------------------------------------- Flavour
    ('court2_report', 'Report To The Captain', 'The Hollow Court',
     ["You have a pool, a rune and something that passes for a workshop.",
      "",
      "Orenvel will want to know. He will not say well done - he will say what is next, which "
      "from him is the same thing."],
     [('checkmark',)], [('item', 'minecraft:iron_ingot', 8)],
     ['first_rune'], 12.0, 4.5, 'support'),

    ('court2_scouts', 'The Court Sends Word', 'The Hollow Court',
     ["Two of the ambient court will walk out past the ring this era.",
      "",
      "Not far. Far enough that the Hollow Court is a place people leave from again, rather "
      "than a place eight elves are waiting to die in."],
     [('checkmark',)], [('item', 'botania:white_petal', 16)],
     ['court2_report'], 13.5, 4.5, 'support'),

    # --- Liquid Bifrost, tiers 1 and 2 ------------------------------------------------------
    #
    # LIQUID_BIFROST.md is the design record; this is its teaching layer. Placed at y 13.5/15.0,
    # below every existing Era II row, so the chain reads as its own band rather than being
    # threaded through the Botania spine it happens to borrow stations from.
    #
    # The coverage standard is per OUTPUT: "every intended processing step for an ore or a
    # contributive item ... should have a quest covering the process by which that is created".
    # Two steps in this era, so two quests, plus a find-it quest for the fluid itself -- a
    # player who has never seen a pool cannot begin the chain, and nothing else in the tree
    # says the pools exist.
    ('bifrost_pool', 'The Bridge, Poured Out', 'Liquid Bifrost',
     ["There is a thing on the lakes you will not have seen anywhere else, and I want you to "
      "bring me a bucket of it before you ask what it is for.",
      "",
      "Bifrost is the bridge-stuff. Solid, it is the rainbow the Aesir walked on. What is "
      "lying in the shallows of Alfheim is the same substance with the bridge taken out of it "
      "-- what was left when the roads between the realms stopped being roads.",
      "",
      "It glows. Look for that at dusk. It is not common and it is not supposed to be."],
     [('item', 'alfheim:liquid_bifrost_bucket')], [('item', 'botania:livingrock', 16)],
     [], 0.0, 13.5, 'leaf'),

    ('bifrost_crystallized', 'Give It A Shape', 'Crystallized Bifrost',
     ["Into the apothecary. Bucket and all -- you will not get the iron back, and I am not "
      "going to pretend otherwise.",
      "",
      "A liquid cannot be worked. Crystallised, it can. This is the same lesson the petals "
      "taught you and it will be the same lesson at every tier: the material does not become "
      "more powerful, it becomes more *handleable*.",
      "",
      "Four to a bucket. Do not be precious with them."],
     [('item', 'alfheim:crystallized_bifrost', 4)],
     [('item', 'minecraft:bucket', 2)],
     ['bifrost_pool'], 1.5, 13.5, 'leaf'),

    ('bifrost_condensed', 'Press Them Together', 'Condensed Bifrost',
     ["Now the pool. Mana in, crystals in, and wait.",
      "",
      "Four shards go in and one stone comes out, and the stone is not four times anything. "
      "You are paying for density, not for power. Everything after this needs the material "
      "small enough to work with and stubborn enough to survive being worked.",
      "",
      "This is as far as it goes on this side of the gate."],
     [('item', 'alfheim:condensed_bifrost')],
     [('item', 'botania:mana_powder', 8)],
     ['bifrost_crystallized'], 3.0, 13.5, 'leaf'),

]


# --------------------------------------------------------------------------- Era III

ERA_III = [
    ('agricarnation', 'The Agricarnation', 'Leaf',
     ["A flower that tends other flowers.",
      "",
      "This is the first machine you will build that does work you would otherwise do with your "
      "hands. Notice how little it looks like a machine."],
     [('item', 'botania:agricarnation')], [('item', 'minecraft:bone_meal', 16)],
     [], 0.0, 0.0, 'leaf'),

    ('hydroangeas', 'Hydroangeas', 'Passive mana',
     ["It drinks water and gives mana, slowly, forever, asking nothing.",
      "",
      "Build several. A garden that only works when you are watching it is not a garden, it is "
      "a hobby."],
     [('item', 'botania:hydroangeas', 4)], [('item', 'botania:mana_pearl')],
     ['agricarnation'], 1.5, 0.0, 'leaf'),

    ('living_fibre', 'Living Fibre', 'Step one of three',
     ["Now we begin the work properly.",
      "",
      "Petals and Dreamwood in the basin, and what comes out is a thread that is still, "
      "faintly, alive. Make a great many. Everything above this rests on it.",
      "",
      "From here each era asks two more steps than the last. Three now. Five in the next. "
      "Seventeen by the end. I am telling you so that you can build for it rather than be "
      "surprised by it."],
     [('item', 'alfheim:living_fibre', 8)], [('item', 'botania:green_petal', 8)],
     ['hydroangeas'], 3.0, 0.0, 'leaf'),

    ('charged_fibre', 'Charged Fibre', 'Step two',
     ["Drop the fibre in the pool and let it drink.",
      "",
      "Two thousand mana per thread. You will want the Hydroangeas now, and you will "
      "understand why I made you build several."],
     [('item', 'alfheim:charged_fibre', 4)], [('item', 'botania:mana_powder', 8)],
     ['living_fibre'], 4.5, 0.0, 'leaf'),

    ('verdant_filament', 'Verdant Filament', 'Step three',
     ["Two charged threads, two runes, and a measure of mana dust on the altar.",
      "",
      "Hold it when it is done. This is the first thing the elves of this age have made that "
      "they did not first dig up or find in a ruin. Everything before it was recovery. This "
      "is manufacture.",
      "",
      "It is a small green filament and it is worth more than the city you found it in."],
     [('item', 'alfheim:verdant_filament')], [('item', 'alfheim:verdant_filament')],
     ['charged_fibre'], 6.0, 0.0, 'leaf'),

    ('elven_quartz', 'Elven Quartz', 'Another thing they told us we could not make',
     ["Quartz, in the pool, with enough mana behind it.",
      "",
      "Another material every account says comes through the gate. Another one that does not. "
      "I am beginning to think the histories were written by whoever owned the gate."],
     [('item', 'botania:quartz_elven', 4)], [('item', 'minecraft:quartz', 8)],
     ['verdant_filament'], 7.5, 0.0, 'leaf'),

    ('generator_array', 'A Garden That Works', 'Automation',
     ["Enough flowers, feeding enough spreaders, filling enough pools that you can walk away.",
      "",
      "This is the quest I care most about in this era. Not because it is hard, but because "
      "everything after Era Five assumes you did it and will punish you if you did not."],
     [('checkmark',)], [('item', 'botania:mana_tablet')],
     ['elven_quartz'], 9.0, 0.0, 'leaf'),

    ('whirlisprig', 'The Whirlisprig', 'Song',
     ["It tends growing things and asks for nothing but somewhere pleasant to be.",
      "",
      "The other tradition is better at this than we are. I have made my peace with it."],
     [('item', 'ars_nouveau:whirlisprig_charm')], [('item', 'ars_nouveau:source_gem', 8)],
     [], 0.0, 2.0, 'song'),

    ('drygmy', 'The Drygmy Henge', 'Harvest without killing',
     ["A henge that persuades animals to give up what you would otherwise take from them dead.",
      "",
      "We have killed enough in this world. Build it."],
     [('item', 'ars_nouveau:drygmy_stone')], [('item', 'ars_nouveau:drygmy_charm')],
     ['whirlisprig'], 1.5, 2.0, 'song'),

    ('mycelial', 'The Mycelial Sourcelink', 'Rot into source',
     ["Decay is not the opposite of growth. It is the other half of it.",
      "",
      "This grove is full of dead matter. Put it to work."],
     [('item', 'ars_nouveau:mycelial_sourcelink')], [('item', 'ars_nouveau:source_gem', 8)],
     ['drygmy'], 3.0, 2.0, 'song'),

    ('vitalic', 'The Vitalic Sourcelink', 'Life into source',
     ["The counterpart. One takes from what is ending, one from what is beginning.",
      "",
      "Run both. The tradition is built on the pair, not on either."],
     [('item', 'ars_nouveau:vitalic_sourcelink')], [('item', 'ars_nouveau:source_gem', 8)],
     ['mycelial'], 4.5, 2.0, 'song'),

    ('relay', 'A Source Relay', 'Move it',
     ["Source will cross distance if you give it somewhere to stand.",
      "",
      "Build the network before you need it. You will not want to be laying relays in an "
      "emergency."],
     [('item', 'ars_nouveau:relay', 2)], [('item', 'ars_nouveau:source_gem', 8)],
     ['vitalic'], 6.0, 2.0, 'song'),

    ('brazier', 'The Ritual Brazier', 'The interlock, again',
     ["Remember this one.",
      "",
      "Rituals are how the other tradition does the things our altar does. In two eras you "
      "will find that our highest metal will not form without one of these burning beside it.",
      "",
      "Neither of us finishes alone. I have said it before; the recipes will say it for me "
      "soon enough."],
     [('item', 'ars_nouveau:ritual_brazier')], [('item', 'ars_nouveau:source_gem', 16)],
     ['relay'], 7.5, 2.0, 'song'),

    ('ritual_growth', 'A Ritual of Growth', 'First working',
     ["Set the brazier, place the tablet, and let it run.",
      "",
      "Watch what it does to the ground. Then go and look at ground you have not treated, and "
      "understand exactly how much of Alfheim is still waiting."],
     [('checkmark',)], [('item', 'ars_nouveau:source_gem', 16)],
     ['brazier'], 9.0, 2.0, 'song'),

    ('farmer', 'A Farmer', 'Support',
     ["Somebody who is not you, growing food you did not plant.",
      "",
      "This is what we are for. Not the flowers, not the runes. This."],
     [('item', 'minecolonies:blockhutfarmer')], [('item', 'minecraft:wheat', 32)],
     [], 0.0, 4.0, 'support'),

    ('forester', 'A Forester', 'Wood at scale',
     ["Dreamwood by hand is a hobby. Dreamwood by forester is an economy."],
     [('item', 'minecolonies:blockhutlumberjack')], [('item', 'botania:dreamwood', 32)],
     ['farmer'], 1.5, 4.0, 'support'),

    ('miners_delight', 'Deeper Digging', 'The Harvest and the mines',
     ["The colony will want ore and the ore is not near the surface any more.",
      "",
      "Something drank the shallow seams. I do not know what. Neither does anyone else."],
     [('item', 'minecolonies:blockhutminer')], [('item', 'minecraft:iron_ingot', 16)],
     ['forester'], 3.0, 4.0, 'support'),

    ('square', 'A Village Square', 'Somewhere to stand together',
     ["Not a wall. Not a store. A square — the place a settlement decides things in.",
      "",
      "Build it before you need it, because the day you need it you will not have time."],
     [('checkmark',)], [('item', 'minecraft:bell')],
     ['miners_delight'], 4.5, 4.0, 'support'),

    ('map_tier2', 'Deeper Maps', 'The Wound',
     ["The first maps were the shallow ruins. These go under them.",
      "",
      "Take the Drygmy henge seriously first. You will want the health."],
     [('item', 'dungeon_realm:dungeon_map', 3)], [('item', 'minecraft:golden_carrot', 8)],
     [], 0.0, 6.0, 'wound'),

    ('gear_set', 'A Full Set', 'Stop dying',
     ["You have been wearing whatever the dead left. Make something that fits."],
     [('checkmark',)], [('item', 'mmorpg:currency/gear_rarity_upgrade', 2)],
     ['map_tier2'], 1.5, 6.0, 'wound'),

    ('talent', 'Choose What You Are', 'Commit',
     ["Pick a path and put points in it. Properly. Not a little of everything.",
      "",
      "There are four of you and one of Alfheim. Specialise, and cover each other."],
     [('checkmark',)], [('item', 'minecraft:experience_bottle', 16)],
     ['gear_set'], 3.0, 6.0, 'wound'),

    ('rune_of_vanaheim', 'The Rune of Vanaheim', 'Capstone',
     ["Vanaheim is the realm of growing things, and of the gods who were traded away as "
      "hostages and chose to stay.",
      "",
      "There is a lesson in that which I will let you find on your own.",
      "",
      "Make the rune. The grove is feeding itself now, and that is the first thing in this "
      "world that has been true for a very long time."],
     [('item', 'mythicbotany:vanaheim_rune')], [('item', 'alfheim:verdant_filament', 2)],
     ['generator_array', 'ritual_growth', 'square', 'talent'], 6.0, 4.5, 'leaf'),

    # ---------------------------------------------------------------- Guides
    # Third teaching layer. Era I says what a system is, Era II how it fails, Era III how it
    # scales -- and where two systems meet. MAGIC_SYSTEMS.md §4.
    ('g3_passive', 'Growth You Do Not Watch', 'Magister Velrous',
     ["Until now every flower you own has needed you standing next to it.",
      "",
      "The Agricarnation ends that. It hurries what grows around it and asks only for mana, "
      "and mana is something you now make while asleep.",
      "",
      "This is the era where the grove starts working without you. Notice the date. It matters "
      "more than any rune."],
     [('checkmark',)], [], [], 0.0, -6.0, 'guide'),

    ('g3_hydroangeas', 'The Trap That Looks Like A Gift', 'Leaf',
     ["The Hydroangeas makes mana out of water. It is early, it is cheap, and every new player "
      "builds a wall of them.",
      "",
      "It is a dead end on purpose. The rate is poor, it consumes the water, and the hours you "
      "spend scaling it are hours not spent on a generating flower that would have paid ten "
      "times over.",
      "",
      "Build one to see it work. Then build something else."],
     [('checkmark',)], [], [], 1.5, -6.0, 'guide'),

    ('g3_yield', 'Yield Beats Speed', 'Leaf',
     ["You will be offered a choice between a working that is fast and one that returns more.",
      "",
      "Take the return, almost always. Time is the resource this grove has most of; materials "
      "are the resource it has least of. That asymmetry does not change until Era VII."],
     [('checkmark',)], [], [], 3.0, -6.0, 'guide'),

    ('g3_rite3', 'Rite III - The Grafting', 'Leaf',
     ["Two blooms and an altar, and what comes out is not either of them.",
      "",
      "The Grafting is the first working that makes a material the world does not contain. "
      "Everything above Era III is built on things that did not exist until an elf made them."],
     [('checkmark',)], [], [], 4.5, -6.0, 'guide'),

    ('g3_infuser_colour', 'The Infuser Wants Colours', 'Leaf',
     ["MythicBotany's Infuser asks for a starting colour and an ending one, and it means it.",
      "",
      "They are not decoration. A recipe without both is rejected outright and never appears "
      "in the book - which is a failure you cannot see, because a recipe that did not load "
      "leaves no trace.",
      "",
      "If something you are certain exists is not in the index, this is usually why."],
     [('checkmark',)], [], [], 6.0, -6.0, 'guide'),

    ('g3_elementium_ore', 'Elementium Is An Ore Here', 'Leaf',
     ["In every other telling, Elementium is what you trade for.",
      "",
      "Here it is in the ground. You will mine it, and the elves you read about in Midgard's "
      "books would have considered that obscene wealth.",
      "",
      "What you cannot get is Manasteel without work, and Mana Diamonds at all until the gate "
      "opens. Remember which way round this world runs."],
     [('checkmark',)], [], [], 7.5, -6.0, 'guide'),

    ('g3_familiar', 'A Familiar Is Not A Pet', 'Song',
     ["A Starbuncle will carry things between chests all day and never ask for anything.",
      "",
      "A Whirlisprig tends crops. A Drygmy farms mobs without killing them. Each is a whole "
      "automation the Leaf would need a room of machinery to match, and each is one creature "
      "you bound once.",
      "",
      "The Song's automation is small, alive, and slightly embarrassing to explain."],
     [('checkmark',)], [], [], 9.0, -6.0, 'guide'),

    ('g3_brazier', 'Rituals Are Not Spells', 'Song',
     ["A spell is cast and finishes. A ritual runs.",
      "",
      "You lay the brazier, you feed it the reagent, and it changes something about the place "
      "you are standing until it is done. Some take minutes. Some change the weather.",
      "",
      "Do not stand a ritual next to anything you would mind it affecting."],
     [('checkmark',)], [], [], 10.5, -6.0, 'guide'),

    ('g3_pedestals', 'Placement Is The Recipe', 'Song',
     ["The Enchanting Apparatus reads the pedestals around it, and their arrangement is part "
      "of what you are making.",
      "",
      "This is the Song's whole character in one block: you build the working in the world "
      "rather than typing it into a grid. It is slower and it is why the tradition feels like "
      "a craft."],
     [('checkmark',)], [], [], 12.0, -6.0, 'guide'),

    ('g3_aura_repay', 'Planting Is The Only Repayment', "Nature's Aura",
     ["You have drawn on this land for two eras. Here is how you give it back.",
      "",
      "Ancient trees restore aura to the chunk they grow in, slowly, and they are the only "
      "thing in this pack that does.",
      "",
      "The Ashen Grove is what happens when nobody plants for three hundred years. You are "
      "standing in the argument."],
     [('checkmark',)], [], [], 0.0, -4.5, 'guide'),

    ('g3_foliot_work', 'Bound Labour', 'Occultism',
     ["A Foliot will carry, crush or trade, forever, with no power and no upkeep.",
      "",
      "Every other automation in this pack has a running cost. This one does not, and that is "
      "the whole reason the tradition exists and the whole reason the Court disapproves of it.",
      "",
      "I have taught you how. I have not told you to."],
     [('checkmark',)], [], [], 1.5, -4.5, 'guide'),

    ('g3_pentacle_scale', 'Bigger Circles, Bigger Things', 'Occultism',
     ["A Foliot needs a small pentacle. A Djinni needs a larger one, and a Marid one larger "
      "still.",
      "",
      "The shape is the specification. Get one glyph wrong on a large circle and you have "
      "spent a great deal of chalk on nothing."],
     [('checkmark',)], [], [], 3.0, -4.5, 'guide'),

    ('g3_courts', 'The Courts Do Not Agree', 'Feywild',
     ["Spring, Summer, Autumn, Winter. Four courts, and they are not four flavours of the "
      "same thing.",
      "",
      "Bargain with one and the others notice. Choose the court whose gifts you actually want, "
      "because switching later costs more than starting over."],
     [('checkmark',)], [], [], 4.5, -4.5, 'guide'),

    ('g3_feysythia', 'Where Two Traditions Meet', 'Feywild',
     ["Feysythia is MythicBotany's flower and it will not grow without a Fey Gem.",
      "",
      "That is the first time in this pack that one magic system is simply unable to proceed "
      "without another. It is not the last.",
      "",
      "The shipped recipe asks for a gem Feywild stopped making years ago; ours does not. If "
      "you read about a Lesser Fey Gem somewhere, it does not exist."],
     [('checkmark',)], [], [], 6.0, -4.5, 'guide'),

    ('g3_runes_arcane', 'Their Runes, Their Anvil', "Iron's Spells",
     ["Human runes go on human gear at a human anvil, and none of it talks to the Song.",
      "",
      "Two enchanting systems that cannot read each other. Choose per item, not per character - "
      "there is no rule against carrying one of each."],
     [('checkmark',)], [], [], 7.5, -4.5, 'guide'),

    ('g3_channeler', 'Mana As A Fluid', 'Create: Wizardry',
     ["A bottle was a curiosity. A bucket is infrastructure.",
      "",
      "The Channeler turns a mana pool into a tank Create can draw from, and from that moment "
      "every pump, pipe and basin in the dead world's machinery runs on elven power.",
      "",
      "This is the join the whole pack is built around. Everything Create does from here is "
      "downstream of a flower."],
     [('checkmark',)], [], [], 9.0, -4.5, 'guide'),

    ('g3_occ_eng', 'Rituals, Mechanised', 'Occult Engineering',
     ["Someone looked at a pentacle and asked whether the chalk could be laid by machine.",
      "",
      "It can. The Pentacle Altar builds the circle for you, and the Otherworld Detector finds "
      "what is worth calling. It is the second bridge in this pack, and it only works because "
      "you already learned both halves separately."],
     [('checkmark',)], [], [], 10.5, -4.5, 'guide'),

    # ---------------------------------------------------------------- Nature's Aura
    ('aura3_sapling', 'Plant An Ancient', "Nature's Aura",
     ["Put it in the poorest ground you own.",
      "",
      "It will take a long time and it will give the chunk back what you took out of it. That "
      "is the only restoration mechanic in this pack, and it is deliberately slower than the "
      "damage was."],
     [('item', 'naturesaura:ancient_sapling')], [('item', 'naturesaura:gold_fiber', 8)],
     ['agricarnation'], 1.5, 6.0, 'leaf'),

    ('aura3_bark', 'Ancient Bark', "Nature's Aura",
     ["The wood of a tree that has been paying a debt down for a century.",
      "",
      "It is worth more than its plank value suggests. Do not build a fence out of it."],
     [('item', 'naturesaura:ancient_bark', 4)], [('item', 'naturesaura:gold_powder', 4)],
     ['aura3_sapling'], 3.0, 6.0, 'leaf'),

    ('aura3_offering', 'The Offering Table', "Nature's Aura",
     ["Give something up and the land notices.",
      "",
      "It is a crude exchange and an honest one, and it is the closest this tradition comes to "
      "asking politely."],
     [('item', 'naturesaura:offering_table')], [('item', 'naturesaura:token_joy', 4)],
     ['aura3_bark'], 4.5, 6.0, 'leaf'),

    # ---------------------------------------------------------------- Occultism
    ('occ3_foliot', 'Call The First One', 'Occultism',
     ["Circle drawn, candles lit, terms written. Say the word.",
      "",
      "What arrives is small, tired and entirely willing. It will do one job forever. Choose "
      "the job carefully - it is not a conversation you get to reopen."],
     [('item', 'occultism:spirit_attuned_gem')], [('item', 'occultism:chalk_white', 2)],
     ['ritual_growth'], 1.5, 7.5, 'support'),

    ('occ3_goggles', 'Seeing The Other Side', 'Occultism',
     ["Otherworld Goggles show you what is there and was always there.",
      "",
      "Ores that read as stone. Things standing in the room with you. It is not a comfortable "
      "item and it is the only way to find several materials this tradition needs."],
     [('item', 'occultism:otherworld_goggles')], [('item', 'occultism:datura', 4)],
     ['occ3_foliot'], 3.0, 7.5, 'support'),

    ('occ3_storage', 'A Room That Is Not There', 'Occultism',
     ["The dimensional matrix stores more than the space it occupies, because the space it "
      "occupies is not where the things are.",
      "",
      "Every other storage solution in this pack is a chest with extra steps. This one is a "
      "hole in the world with a spirit minding it."],
     [('item', 'occultism:storage_controller')], [('item', 'minecraft:diamond', 3)],
     ['occ3_goggles'], 4.5, 7.5, 'support'),

    # ---------------------------------------------------------------- Feywild
    ('fey3_scroll', 'Name A Court', 'Feywild',
     ["Fill in the scroll. Spring is the kindest and gives the least.",
      "",
      "Whichever you write, the others will remember that you did not write them."],
     [('item', 'feywild:summoning_scroll_spring_pixie')], [('item', 'feywild:fey_gem', 2)],
     ['ritual_growth'], 1.5, 9.0, 'support'),

    ('fey3_orb', 'A Pixie Of Your Own', 'Feywild',
     ["It is not tamed and it is not owned. It has agreed to stay.",
      "",
      "Feed it. Genuinely - the arrangement lapses if you stop, and a lapsed pixie does not "
      "come back."],
     [('item', 'feywild:pixie_orb')], [('item', 'minecraft:cookie', 16)],
     ['fey3_scroll'], 3.0, 9.0, 'support'),

    ('fey3_feysythia', 'Feysythia', 'Feywild',
     ["The flower that needs both traditions. Yellow petals, purple, and a Fey Gem in the "
      "basin.",
      "",
      "It is a small thing and it is the proof of the design: from here, no single system "
      "finishes on its own."],
     [('item', 'mythicbotany:feysythia')], [('item', 'botania:mana_diamond')],
     ['fey3_orb'], 4.5, 9.0, 'support'),

    # ---------------------------------------------------------------- Iron's Spellbooks
    ('arc3_rune', 'A Blank Rune', "Iron's Spells",
     ["Their runes are stamped, not grown, and a blank one is just a slug of arcane metal.",
      "",
      "What it becomes depends on the anvil and what you feed it."],
     [('item', 'irons_spellbooks:blank_rune')], [('item', 'irons_spellbooks:arcane_ingot', 2)],
     ['relay'], 1.5, 10.5, 'song'),

    ('arc3_cooldown', 'Cut The Wait', "Iron's Spells",
     ["A cooldown rune is the first upgrade that makes their magic feel usable.",
      "",
      "That it exists at all tells you their casting was too slow to fight with. Ours never "
      "needed the fix."],
     [('item', 'irons_spellbooks:cooldown_rune')], [('item', 'irons_spellbooks:arcane_essence', 8)],
     ['arc3_rune'], 3.0, 10.5, 'song'),

    ('arc3_ingot', 'Arcane Ingots', "Iron's Spells",
     ["Debris, refined, until it is a metal rather than a scar.",
      "",
      "Everything above this in their tradition is made of it, and there is a finite amount in "
      "this world because nobody is making any more."],
     [('item', 'irons_spellbooks:arcane_ingot', 4)], [('item', 'minecraft:diamond', 2)],
     ['arc3_cooldown'], 4.5, 10.5, 'song'),

    # ---------------------------------------------------------------- Create: Wizardry
    ('cw3_channeler', 'The Channeler', 'Create: Wizardry',
     ["Set it on a full pool and it becomes a tank.",
      "",
      "From here Create can draw mana directly, and every machine downstream is running on "
      "something a flower made. That is the sentence this whole pack is built to earn."],
     [('item', 'create_wizardry:channeler')], [('item', 'create_wizardry:mana_bucket')],
     ['generator_array'], 1.5, 12.0, 'leaf'),

    ('cw3_bucket', 'A Bucket Of It', 'Create: Wizardry',
     ["Portable, pumpable, and measurable in millibuckets like anything else.",
      "",
      "The indignity of it would have started a war three hundred years ago. Now it is how we "
      "get the lights on."],
     [('item', 'create_wizardry:mana_bucket')], [('item', 'create_wizardry:crushed_mithril', 2)],
     ['cw3_channeler'], 3.0, 12.0, 'leaf'),

    # ---------------------------------------------------------------- Occult Engineering
    ('oe3_detector', 'The Otherworld Detector', 'Occult Engineering',
     ["It points at what is worth calling.",
      "",
      "Built by a ritual, used by a machine. The two halves of this pack shaking hands."],
     [('item', 'occultengineering:otherworld_detector')], [('item', 'occultism:chalk_white', 2)],
     ['occ3_storage'], 6.0, 7.5, 'support'),

    ('oe3_altar', 'The Pentacle Altar', 'Occult Engineering',
     ["Chalk laid by machine, exactly, every time.",
      "",
      "It removes the one part of Occultism that was genuinely tedious and leaves the part "
      "that was genuinely questionable. Make of that what you like."],
     [('item', 'occultengineering:pentacle_altar')], [('item', 'occultengineering:chalk_copper')],
     ['oe3_detector'], 7.5, 7.5, 'support'),

    # ---------------------------------------------------------------- Leaf, extended
    ('leaf3_agri', 'The Agricarnation', 'Leaf',
     ["Mana in, growth out, and you do not have to be there.",
      "",
      "The first flower that gives you back time rather than material."],
     [('item', 'botania:agricarnation')], [('item', 'botania:mana_diamond')],
     ['verdant_filament'], 7.5, 0.0, 'leaf'),

    ('leaf3_graft', 'Rite III - The Grafting', 'Leaf',
     ["Two quickened blooms on the altar, and something neither of them was.",
      "",
      "This is where Alfheim stops being a place that has materials and starts being a place "
      "that makes them."],
     [('item', 'alfheim:verdant_filament', 2)], [('item', 'botania:mana_diamond', 2)],
     ['leaf3_agri'], 9.0, 0.0, 'leaf'),

    ('leaf3_diamond', 'Mana Diamonds', 'Leaf',
     ["Diamond, in a pool, patient.",
      "",
      "Cheap in Midgard and precious here, which is the reversal stated in a single item."],
     [('item', 'botania:mana_diamond', 4)], [('item', 'botania:manasteel_ingot', 8)],
     ['leaf3_graft'], 10.5, 0.0, 'leaf'),

    ('leaf3_terra', 'The Terra Plate', 'Leaf',
     ["Build it now. You will not be able to use it for three eras.",
      "",
      "It wants three things the gate has not opened for yet. Let it sit in your workshop as a "
      "reminder of which way the trade route runs."],
     [('item', 'botania:terra_plate')], [('item', 'botania:mana_diamond', 2)],
     ['leaf3_diamond'], 12.0, 0.0, 'leaf'),

    ('leaf3_elem', 'Elementium From The Ground', 'Leaf',
     ["Mine it. Smelt it. Try not to think about what a Midgard merchant would have paid.",
      "",
      "This is the single clearest proof of the premise, and it is worth stopping for a moment "
      "to appreciate before it becomes routine."],
     [('item', 'botania:elementium_ingot', 8)], [('item', 'alfheim:verdant_filament')],
     ['leaf3_terra'], 13.5, 0.0, 'leaf'),

    # ---------------------------------------------------------------- Song, extended
    ('song3_brazier', 'Lay A Brazier', 'Song',
     ["The ritual runs in the world, not in your hand.",
      "",
      "Choose where. A ritual of growth in the middle of your workshop will grow your workshop."],
     [('item', 'ars_nouveau:ritual_brazier')], [('item', 'ars_nouveau:source_gem', 12)],
     ['brazier'], 7.5, 3.0, 'song'),

    ('song3_apparatus', 'Enchant Something Properly', 'Song',
     ["Pedestals, reagent, Source. The arrangement is half the recipe.",
      "",
      "What comes out is better than an enchanting table could manage and you will have "
      "understood every step of why."],
     [('item', 'ars_nouveau:dominion_wand')], [('item', 'ars_nouveau:source_gem', 12)],
     ['song3_brazier'], 9.0, 3.0, 'song'),

    ('song3_wixie', 'The Wixie Cauldron', 'Song',
     ["It crafts. On its own. Because you asked a small creature nicely and it agreed.",
      "",
      "The Leaf would need a room of machinery. The Song needed a hat."],
     [('item', 'ars_nouveau:wixie_hat')], [('item', 'ars_nouveau:source_gem', 16)],
     ['song3_apparatus'], 10.5, 3.0, 'song'),

    # ---------------------------------------------------------------- The Wound
    ('wound3_device', 'The Map Device', 'The Wound',
     ["Orenvel can commission you one, or you can lay it on the Runic Altar yourself.",
      "",
      "It used to be a diamond on a stone. We changed that - expedition access is capability, "
      "and capability comes through a spine in this pack or it does not come at all."],
     [('item', 'dungeon_realm:map_device')], [('item', 'dungeon_realm:dungeon_map')],
     ['map_tier2'], 7.5, 4.5, 'wound'),

    ('wound3_first_run', 'Step Through', 'The Wound',
     ["A map, a device, and somewhere that did not exist this morning.",
      "",
      "Carry a Home Pearl. The Guard lost more people to not being able to leave than to "
      "anything they met inside."],
     [('item', 'dungeon_realm:home_pearl')], [('item', 'minecraft:golden_apple', 4)],
     ['wound3_device'], 9.0, 4.5, 'wound'),

    ('wound3_harvest', 'A Different Kind Of Ground', 'The Wound',
     ["Not every expedition is a dungeon. The Harvest is its own thing and it is worse.",
      "",
      "Read what a map is before you open it. They are not interchangeable and the level "
      "ranges are not comparable."],
     [('item', 'the_harvest:harvest_map')], [('item', 'minecraft:diamond', 3)],
     ['wound3_first_run'], 10.5, 4.5, 'wound'),

    ('wound3_obelisk', 'Obelisks', 'The Wound',
     ["Something stands in the wild and calls waves at whoever touches it.",
      "",
      "It is the only expedition you can attempt without a map, which makes it the one you "
      "will attempt underlevelled. Do not."],
     [('item', 'ancient_obelisks:obelisk_map')], [('item', 'minecraft:diamond', 3)],
     ['wound3_harvest'], 12.0, 4.5, 'wound'),

    # ---------------------------------------------------------------- Flavour
    ('court3_scouts', 'The Scouts Come Back', 'The Hollow Court',
     ["Two went out in Era II. Both are back, which is better than the Court expected.",
      "",
      "They have found ruins we did not know were standing. Orenvel has stopped calling this a "
      "holding action."],
     [('checkmark',)], [('item', 'botania:mana_diamond')],
     ['square'], 13.5, 4.5, 'support'),

    ('court3_grove', 'Something Planted', 'The Hollow Court',
     ["Velrous asked for one tree in Era I and you gave him one tree.",
      "",
      "Bring him a grove. He will pretend it is not what he wanted all along, and he will be "
      "lying."],
     [('item', 'naturesaura:ancient_sapling', 4)], [('item', 'alfheim:verdant_filament')],
     ['court3_scouts'], 15.0, 4.5, 'support'),

    # --- Liquid Bifrost, tiers 3 and 4, and the exchange -------------------------------------
    #
    # Both remaining tiers are behind the gate: the infuser is MythicBotany's and only exists
    # in Alfheim, so this half of the chain is unreachable in Era II no matter how much
    # condensed bifrost a player hoards. That is the gate doing its job rather than a number
    # being raised.
    #
    # The exchange quest carries SIX task items on purpose. Coverage counts per output, and the
    # six conversions produce six different currencies -- one quest that asks for all of them
    # is the honest shape, because the point of the chain is precisely that it is one material
    # reaching every system. Six separate quests would say the opposite.
    ('bifrost_refined', 'Take The Rest Out', 'Refined Bifrost',
     ["The infuser, and no, you could not have done this before. It does not exist on the "
      "other side of the gate.",
      "",
      "Everything you have made so far still has Alfheim in it -- silt, ley-residue, the "
      "ordinary dirt of a broken world. That is what makes it *ours*, and it is also what "
      "makes it useless to anyone else's magic.",
      "",
      "Take it out. What is left will not look like much."],
     [('item', 'alfheim:refined_bifrost')],
     [('item', 'botania:elf_glass', 8)],
     [], 0.0, 13.5, 'leaf'),

    ('bifrost_distilled', 'The Last Step', 'Distilled Bifrost',
     ["Two refined, a pearl, and elf glass, on the runic altar.",
      "",
      "This is the finished thing, and I want to be exact about what you have made. It is not "
      "a power source. It holds nothing. Set it on a table and it will sit there for a "
      "thousand years being violet.",
      "",
      "What it is, is *unattached*. Every other material in this world already belongs to a "
      "system -- mana is Botania's, source is the Ars-wrights', essence belongs to whatever "
      "answers when the Occultists knock. This belongs to none of them, which means it can "
      "become any of them."],
     [('item', 'alfheim:distilled_bifrost')],
     [('item', 'botania:mana_pearl', 2)],
     ['bifrost_refined'], 1.5, 13.5, 'leaf'),

    ('bifrost_exchange', 'One Material, Every Road', 'The exchange',
     ["Now spend it, and spend it badly.",
      "",
      "You will notice the rates are poor. That is deliberate and I will not apologise for it. "
      "Distilled bifrost is a *foothold* in a discipline you have not studied, not a way to "
      "skip studying it. Six of these into mana powder is an insult to the powder and a "
      "bargain to you, because the alternative was starting that system from nothing.",
      "",
      "Bring me one of each. I want to see that you have walked all six roads at least once "
      "before you decide which one is yours.",
      "",
      "The Court spent four hundred years being certain that our way was the way. Look where "
      "the Court is."],
     [('item', 'botania:mana_powder'),
      ('item', 'ars_nouveau:source_gem'),
      ('item', 'occultism:otherworld_essence'),
      ('item', 'irons_spellbooks:arcane_essence'),
      ('item', 'naturesaura:gold_leaf'),
      ('item', 'botania:mana_pearl')],
     [('item', 'alfheim:distilled_bifrost', 2)],
     ['bifrost_distilled'], 3.0, 13.5, 'leaf'),

]


ERAS = [
    dict(key='era_1', index=0, title='I — The Ashen Grove',
         subtitle='Can anything still grow here?',
         icon='botania:pure_daisy', quests=ERA_I),
    dict(key='era_2', index=1, title='II — The First Light',
         subtitle='Can we hold ground?',
         icon='mythicbotany:alfheim_rune', quests=ERA_II),
    dict(key='era_3', index=2, title='III \u2014 The Green Return',
         subtitle='Can we feed ourselves?',
         icon='alfheim:verdant_filament', quests=ERA_III),
]


def build_quest(era_key, q):
    # `track` may be 'guide'. A Guide teaches a mechanic instead of asking for one: it costs
    # nothing, gates nothing, and is drawn as a gear so the teaching band reads as separate
    # from the work. ERA_EXPANSION.md §3.
    key, title, subtitle, desc, tasks, rewards, deps, x, y, track = q
    guide = track == 'guide'
    ident = qid(era_key, key)
    out = ['\t\t{']
    out.append(f'\t\t\ttitle: "{esc(title)}"')
    if subtitle:
        out.append(f'\t\t\tsubtitle: "{esc(subtitle)}"')
    out.append(f'\t\t\tx: {x}d')
    out.append(f'\t\t\ty: {y}d')
    if guide:
        out.append('\t\t\toptional: true')
        out.append('\t\t\tshape: "gear"')
    else:
        out.append('\t\t\tshape: "circle"' if not deps else '\t\t\tshape: "rsquare"')
    out.append(snbt_lines('description', desc, 3))
    if deps:
        dl = ', '.join(f'"{qid(era_key, d)}"' for d in deps)
        out.append(f'\t\t\tdependencies: [{dl}]')
    out.append(f'\t\t\tid: "{ident}"')

    tl = []
    for i, t in enumerate(tasks):
        tident = qid(era_key, key, 'task', str(i))
        if t[0] == 'item':
            cnt = f', count: {t[2]}L' if len(t) > 2 else ''
            tl.append(f'\t\t\t\t{{ id: "{tident}", type: "item", item: "{t[1]}"{cnt} }}')
        elif t[0] == 'kill':
            tl.append(f'\t\t\t\t{{ id: "{tident}", type: "kill", entity: "{t[1]}", value: {t[2]}L }}')
        elif t[0] == 'checkmark':
            tl.append(f'\t\t\t\t{{ id: "{tident}", type: "checkmark", title: "{esc(title)}" }}')
    out.append('\t\t\ttasks: [\n' + '\n'.join(tl) + '\n\t\t\t]')

    rl = []
    for i, r in enumerate(rewards):
        rident = qid(era_key, key, 'reward', str(i))
        cnt = r[2] if len(r) > 2 else 1
        rl.append(f'\t\t\t\t{{ id: "{rident}", type: "item", item: "{r[1]}", count: {cnt} }}')
    if rl:
        out.append('\t\t\trewards: [\n' + '\n'.join(rl) + '\n\t\t\t]')
    out.append('\t\t}')
    return '\n'.join(out)


def build_chapter(era):
    key = era['key']
    body = [
        '{',
        '\tid: "%s"' % qid('chapter', key),
        '\tgroup: "%s"' % qid('group', GROUP_KEY),
        '\torder_index: %d' % era['index'],
        '\tfilename: "%s"' % key,
        '\ttitle: "%s"' % esc(era['title']),
        '\ticon: "%s"' % era['icon'],
        snbt_lines('subtitle', [era['subtitle']], 1),
        '\tdefault_quest_shape: ""',
        '\tdefault_hide_dependency_lines: false',
        '\tquests: [',
    ]
    body.append('\n'.join(build_quest(key, q) for q in era['quests']))
    body += ['\t]', '\tquest_links: [ ]', '}']
    return '\n'.join(body) + '\n'


CHAPTER_GROUPS = (
    '{\n\tchapter_groups: [\n'
    '\t\t{ id: "%s", title: "Alfheim Reclaimed" }\n'
    '\t]\n}\n' % qid('group', GROUP_KEY)
)

DATA = (
    '{\n'
    '\tdefault_reward_team: false\n'
    '\tdefault_team_consume_items: false\n'
    '\tdetection_delay: 20\n'
    '\temergency_items_cooldown: 300\n'
    '\tgrid_scale: 0.5d\n'
    '\tlock_message: ""\n'
    '\tpause_game: false\n'
    '\ttitle: "Alfheim Reclaimed"\n'
    '}\n'
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    # chapter_groups.snbt is NOT written here. The Compendium adds a second chapter group,
    # and one file must have one owner -- tools/gen_compendium.py declares both groups.
    files = {
        os.path.join(OUT, 'data.snbt'): DATA,
    }
    for era in ERAS:
        files[os.path.join(OUT, 'chapters', era['key'] + '.snbt')] = build_chapter(era)

    total = sum(len(e['quests']) for e in ERAS)
    for path, content in files.items():
        if a.dry_run:
            print(f'--- {path} ({len(content)} bytes) ---')
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print('  wrote', path)
    print(f'\n{len(ERAS)} chapter(s), {total} quests.')


if __name__ == '__main__':
    main()
