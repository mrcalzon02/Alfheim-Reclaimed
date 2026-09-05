"""Generate the Alfheim biome set and its LibX biome layer.

Alfheim ships five biomes and has to carry a ten-era campaign. This adds six more and
rewrites the biome layer to place all eleven.

Why it overrides `data/mythicbotany/libx/biome_layer/alfheim.json` outright rather than
appending a second layer to the tag: LibX layer stacking is governed by `density`/`range`
whose exact semantics are not documented outside the mod's source, and guessing them risks
biomes that silently never place. Replacing the single layer with an expanded one is
predictable — the biome closest in parameter space wins, which is the same rule vanilla
multi-noise uses.

CORRECTED 2026-09-04, after a player explored a fresh world and found none of our biomes.

An earlier version of this note said MythicBotany "leaves temperature and humidity fully open,
so both axes are free". That was exactly backwards and it is what broke the dimension. The mod
ships `alfheim_temperature` and `alfheim_humidity` as `libx:clamp` of a CONSTANT 0.0 -- the axes
are not free, they are dead, and every band constraining either away from zero could never be
selected. Nine of eleven biomes were unreachable by construction.

This file therefore overrides the climate itself (CLIMATE_OVERRIDES) as well as the layer, and
resolves the layer into a genuine disjoint partition rather than a pile of overlapping claims
where the largest, earliest box wins every tie.

    python tools/gen_alfheim_biomes.py
"""
import json
import os

OUT = os.path.join('kubejs', 'data')
NS = 'alfheim'

# --- shared palette ------------------------------------------------------------------

CARVERS = {'air': ['mythicbotany:cave', 'mythicbotany:canyon']}

ORES = [
    'mythicbotany:metamorphic_forest_stone', 'mythicbotany:metamorphic_mountain_stone',
    'mythicbotany:metamorphic_fungal_stone', 'mythicbotany:metamorphic_swamp_stone',
    'mythicbotany:metamorphic_desert_stone', 'mythicbotany:metamorphic_taiga_stone',
    'mythicbotany:metamorphic_mesa_stone', 'mythicbotany:elementium_ore',
    'mythicbotany:dragonstone_ore', 'mythicbotany:gold_ore',
]

PASSIVE = [
    {'type': 'minecraft:sheep',   'maxCount': 4, 'minCount': 4, 'weight': 12},
    {'type': 'minecraft:pig',     'maxCount': 4, 'minCount': 4, 'weight': 10},
    {'type': 'minecraft:chicken', 'maxCount': 4, 'minCount': 4, 'weight': 10},
    {'type': 'minecraft:cow',     'maxCount': 4, 'minCount': 4, 'weight': 8},
    {'type': 'mythicbotany:alf_pixie', 'maxCount': 10, 'minCount': 4, 'weight': 5},
]

HOSTILE = [{'type': 'minecraft:spider', 'maxCount': 4, 'minCount': 1, 'weight': 10}]

# The deficient biomes each spawn something the ordinary ones do not, so the danger reads
# as a property of the place rather than a difficulty slider.
INFESTED = [
    {'type': 'minecraft:cave_spider', 'maxCount': 4, 'minCount': 2, 'weight': 20},
    {'type': 'minecraft:silverfish', 'maxCount': 4, 'minCount': 2, 'weight': 14},
    {'type': 'minecraft:spider', 'maxCount': 3, 'minCount': 1, 'weight': 8},
]
ROTTEN = [
    {'type': 'minecraft:zombie', 'maxCount': 4, 'minCount': 2, 'weight': 20},
    {'type': 'minecraft:husk', 'maxCount': 3, 'minCount': 1, 'weight': 10},
]
VOID_MOBS = [{'type': 'minecraft:enderman', 'maxCount': 2, 'minCount': 1, 'weight': 12}]


# --- ordinary metals: RETIRED 2026-09-03 ---------------------------------------------
#
# Alfheim used to be seeded with scarce VANILLA ore -- copper, iron, coal, lapis, diamond,
# redstone -- placed against #minecraft:stone_ore_replaceables, which livingrock had to be
# force-added to. The user struck it: "I don't want to use vanilla ores because that just
# reskins Alfheim as the Overworld."
#
# Alfheim's minerals are now the Twelve Blooms (tools/blooms_manifest.json,
# tools/gen_blooms.py) and the crystals (tools/crystals_manifest.json). Both target
# #mythicbotany:base_stone_alfheim, the mod's own Alfheim stone tag, so no global vanilla
# tag is overridden any more.
#
# The SCARCE_ORES / ORE_DISTRIBUTION / ORE_BIOME_TAGS tables that lived here were deleted
# with the layer rather than left as dead data describing a system that no longer exists.
# The retired files are preserved with their hashes in
# quarantine/vanilla_ore_layer_2026-09-03/.


# --- canonical feature order ---------------------------------------------------------
#
# Minecraft does not generate a biome's features in the order that biome lists them. It
# flattens every loaded biome into ONE global order per generation step
# (`FeatureSorter`), by topologically sorting the "A before B" constraints each biome
# asserts about ADJACENT pairs. Two biomes that name the same pair in opposite orders make
# that order impossible and the game throws `Feature order cycle found` -- lazily, from
# ChunkGenerator, so it lands on world creation, long after every static check has passed.
#
# Alfheim's eleven biomes therefore have to agree with each other AND with MythicBotany's
# five, which are jar-owned and cannot be reordered. This is the merged order, read off
# those five: `alfheim_grass` first everywhere; `alfheim_plains` fixes
# loose_dreamwood_trees before motif_flowers; `golden_fields` fixes extra_gold_ore last in
# the ore step. Ours are appended where nothing constrains them.
#
# Every step is sorted by this table, so the order cannot be got wrong by writing the
# lists below in a different sequence -- which is exactly how `bloomfall_vale` came to
# contradict `mythicbotany:alfheim_plains` and crash the home dimension. A feature with no
# entry here is a hard error: add it deliberately, in a position MythicBotany allows.
FEATURE_ORDER = [
    # step 4, surface structures
    'mythicbotany:abandoned_apothecaries',
    # step 6, underground ores -- MythicBotany's own order, extra_gold_ore last
    'mythicbotany:metamorphic_forest_stone', 'mythicbotany:metamorphic_mountain_stone',
    'mythicbotany:metamorphic_fungal_stone', 'mythicbotany:metamorphic_swamp_stone',
    'mythicbotany:metamorphic_desert_stone', 'mythicbotany:metamorphic_taiga_stone',
    'mythicbotany:metamorphic_mesa_stone', 'mythicbotany:elementium_ore',
    'mythicbotany:dragonstone_ore', 'mythicbotany:gold_ore',
    'mythicbotany:extra_gold_ore',
    # step 9, vegetal decoration
    'mythicbotany:alfheim_grass',
    'mythicbotany:wheat_fields',
    'mythicbotany:loose_dreamwood_trees',
    'mythicbotany:dense_dreamwood_trees',
    'mythicbotany:motif_flowers',
    'mythicbotany:mana_crystals',
    # ars_nouveau:placed_cascading_tree and placed_mixed_archwoods are deliberately absent.
    # They reach our biomes through GROVE_MODIFIERS instead -- see the note there. A
    # JSON-listed feature sorts before every appended one, which is what produced a
    # feature-order cycle against 125 other biomes.
]

FEATURE_RANK = {f: i for i, f in enumerate(FEATURE_ORDER)}


def ordered(step, feats):
    """Sort one generation step into the canonical order, refusing unranked features."""
    unknown = [f for f in feats if f not in FEATURE_RANK]
    if unknown:
        raise SystemExit(
            f'step {step}: {unknown} has no entry in FEATURE_ORDER. Add it in a position '
            f'MythicBotany\'s five biomes allow, or the merged order may be impossible '
            f'and world generation will crash on the first chunk.')
    return sorted(feats, key=FEATURE_RANK.__getitem__)


def biome(fog, sky, water, water_fog, features, spawners, downfall=1.0,
          temperature=0.7, precipitation=True, particle=None):
    """Feature list is 11 GenerationStep.Decoration slots; short lists are padded."""
    feats = [ordered(i, list(f)) for i, f in enumerate(features)]
    feats += [[] for _ in range(11 - len(feats))]
    effects = {'fog_color': fog, 'sky_color': sky,
               'water_color': water, 'water_fog_color': water_fog}
    if particle:
        effects['particle'] = particle
    return {
        'carvers': CARVERS,
        'creature_spawn_probability': 0.2,
        'downfall': downfall,
        'temperature': temperature,
        'has_precipitation': precipitation,
        'effects': effects,
        'features': feats,
        'spawn_costs': {},
        'spawners': {'ambient': [], 'axolotls': [], 'creature': spawners.get('creature', []),
                     'misc': [], 'monster': spawners.get('monster', []),
                     'underground_water_creature': [], 'water_ambient': [],
                     'water_creature': []},
    }


# --- the six new biomes --------------------------------------------------------------
# Colours run cool and desaturated where the land is drained, warmer where it still lives.

# --- the fey ----------------------------------------------------------------------------------
#
# Asked for 2026-09-04: "we definitely need more fey creatures."
#
# Before this, exactly ONE fey creature spawned anywhere in Alfheim -- mythicbotany:alf_pixie,
# at weight 5, in the three biomes that carry PASSIVE. A dimension whose entire premise is a
# fallen fey world was, in practice, populated by sheep.
#
# Feywild ships sixteen; fourteen are usable. Excluded on purpose:
#   feywild:mab, feywild:titania   bosses, summoned by ritual. World-spawning them would hand
#                                  the player an Era-IV fight in Era I and break the spine.
#
# Each biome gets its OWN roster rather than a shared list, so the fey read as native to the
# place instead of as ambient decoration -- the same reasoning as INFESTED/ROTTEN/VOID_MOBS.
# Every id below was checked against the live entity registry (check_hollow_court.load_ids),
# not against lang keys; `entity.feywild.spring_pixie` existing in a lang file is not evidence
# that `feywild:spring_pixie` is registered, and that distinction has already cost this project
# eleven recipes.
FEY_WOOD = [                                    # silverbark_wood -- the forest still alive
    {'type': 'feywild:spring_pixie',    'maxCount': 4, 'minCount': 2, 'weight': 14},
    {'type': 'feywild:sprite',          'maxCount': 3, 'minCount': 1, 'weight': 10},
    {'type': 'feywild:spring_tree_ent', 'maxCount': 1, 'minCount': 1, 'weight': 2},
]
FEY_BLOOM = [                                   # bloomfall_vale -- high summer, the richest
    {'type': 'feywild:summer_pixie',    'maxCount': 4, 'minCount': 2, 'weight': 14},
    {'type': 'feywild:bee_knight',      'maxCount': 2, 'minCount': 1, 'weight': 6},
    {'type': 'feywild:moo_shroom_cow',  'maxCount': 3, 'minCount': 1, 'weight': 5},
    {'type': 'feywild:summer_tree_ent', 'maxCount': 1, 'minCount': 1, 'weight': 2},
]
FEY_FEN = [                                     # mana_fen -- damp and fungal
    {'type': 'feywild:shroomling',      'maxCount': 4, 'minCount': 2, 'weight': 12},
    {'type': 'feywild:mandragora',      'maxCount': 2, 'minCount': 1, 'weight': 8},
    {'type': 'feywild:sprite',          'maxCount': 2, 'minCount': 1, 'weight': 6},
]
FEY_ASH = [                                     # ashen_grove -- burnt, late autumn
    {'type': 'feywild:autumn_pixie',    'maxCount': 3, 'minCount': 1, 'weight': 8},
    {'type': 'feywild:bellsnickel',     'maxCount': 1, 'minCount': 1, 'weight': 3},
]
FEY_HIGH = [                                    # sundered_highlands -- exposed and turning
    {'type': 'feywild:autumn_pixie',    'maxCount': 3, 'minCount': 1, 'weight': 8},
    {'type': 'feywild:autumn_tree_ent', 'maxCount': 1, 'minCount': 1, 'weight': 2},
]
FEY_COLD = [                                    # hollow_marches -- the cold that followed
    {'type': 'feywild:winter_pixie',    'maxCount': 3, 'minCount': 1, 'weight': 8},
    {'type': 'feywild:bellsnickel',     'maxCount': 1, 'minCount': 1, 'weight': 3},
]
FEY_STARVED = [                                 # starved_reach -- winter that never broke
    {'type': 'feywild:winter_pixie',    'maxCount': 2, 'minCount': 1, 'weight': 6},
    {'type': 'feywild:winter_tree_ent', 'maxCount': 1, 'minCount': 1, 'weight': 2},
]
FEY_MIRE = [                                    # decayed_mire -- what the rot grew instead
    {'type': 'feywild:mandragora',      'maxCount': 3, 'minCount': 1, 'weight': 10},
    {'type': 'feywild:shroomling',      'maxCount': 3, 'minCount': 1, 'weight': 8},
]
FEY_WARREN = [                                  # infested_warren -- barely holding on
    {'type': 'feywild:shroomling',      'maxCount': 2, 'minCount': 1, 'weight': 5},
]
FEY_VOID = [                                    # void_verge -- almost nothing lives here
    {'type': 'feywild:winter_pixie',    'maxCount': 2, 'minCount': 1, 'weight': 3},
]
FEY_SCORCH = [                                  # scorchfell -- only the heat-hardened
    {'type': 'feywild:summer_tree_ent', 'maxCount': 1, 'minCount': 1, 'weight': 2},
    {'type': 'feywild:autumn_pixie',    'maxCount': 2, 'minCount': 1, 'weight': 4},
]

# --- the user's roster, 2026-09-04 -------------------------------------------------------------
#
# "Ideas for fey creatures include deer based off the Minecraft horse -- we would need to add an
#  antler for the bucks; frogs, toads (larger frogs) of kinds and varieties; and of course the
#  various hostile elves."
#
# Two of the three are buildable here and are below. The third is recorded in FEY_BACKLOG rather
# than faked, because pretending it shipped would be worse than saying it did not.
#
# HOSTILE ELVES. Free, and the best fit in the pack: richs_races_wood_elves:wood_elf already
# extends Monster and already targets Player -- it is the Hollow Court's own entity with its AI
# left switched on. The court is the same type with NoAI, placed by structure rather than
# spawned, and the hub's 192-block claim blocks hostile spawns, so the two populations cannot
# be confused with each other. Restricted to the biomes where the fall went WORST, so a wild
# elf reads as what became of the survivors rather than as a generic bandit.
HOSTILE_ELVES = [
    {'type': 'richs_races_wood_elves:wood_elf', 'maxCount': 3, 'minCount': 1, 'weight': 12},
]

# FROGS. Vanilla minecraft:frog picks its variant -- temperate, warm or cold -- from the biome
# it spawns in, so the "kinds and varieties" come for free from our own climate work rather
# than from three separate entries.
FROGS = [{'type': 'minecraft:frog', 'maxCount': 5, 'minCount': 2, 'weight': 10}]
FROGS_SPARSE = [{'type': 'minecraft:frog', 'maxCount': 3, 'minCount': 1, 'weight': 5}]

# The former deer/toad backlog is superseded by tools/gen_fey_wildlife.py (B-77).
# EntityJS registers 18 proper custom creatures; additive biome modifiers own their habitats.
# Keep those additions out of these base lists so biome regeneration cannot duplicate them.

BIOMES = {
    # The start. Drained, spider-ridden, no flowers, no mana crystals — their absence is
    # the strongest signal that the grove is dead. SPAWN_ZONE.md §6.
    # Velrous's opening line is "The trees you see standing are dead" -- but the biome
    # generated none at all, so the player spawned somewhere with no wood within reach and
    # a first quest asking for a crafting table. Loose dreamwood at low density is the
    # standing dead the script already describes.
    'ashen_grove': biome(
        fog=0x6B6F6A, sky=0x8A93A0, water=0x4A5550, water_fog=0x27302C,
        features=[[], [], [], [], ['mythicbotany:abandoned_apothecaries'], [], ORES, [], [],
                  ['mythicbotany:loose_dreamwood_trees']],
        spawners={'creature': FEY_ASH, 'monster': HOSTILE + HOSTILE_ELVES},
        downfall=0.3, temperature=0.5),

    # Pale, cold, sparse. Dreamwood that survived by going quiet.
    'silverbark_wood': biome(
        fog=0xB9C7CC, sky=0x9FB6C4, water=0x53788C, water_fog=0x1E3540,
        features=[[], [], [], [], [], [], ORES, [], [],
                  ['mythicbotany:alfheim_grass', 'mythicbotany:loose_dreamwood_trees']],
        spawners={'creature': PASSIVE + FEY_WOOD, 'monster': []},
        downfall=0.6, temperature=0.35),

    # Drowned gardens. The aqueducts broke and the water stayed.
    'mana_fen': biome(
        fog=0x7FA6A0, sky=0x6E96A8, water=0x2E6B63, water_fog=0x123330,
        features=[[], [], [], [], ['mythicbotany:abandoned_apothecaries'], [], ORES, [], [],
                  ['mythicbotany:alfheim_grass', 'mythicbotany:mana_crystals']],
        spawners={'creature': PASSIVE + FEY_FEN + FROGS, 'monster': []},
        downfall=1.0, temperature=0.8),

    # Broken uplands — where the devastation tore the ground open.
    'sundered_highlands': biome(
        fog=0x9A8F86, sky=0x7E8794, water=0x40525C, water_fog=0x1A2429,
        features=[[], [], [], [], [], [], ORES + ['mythicbotany:extra_gold_ore'], [], [],
                  ['mythicbotany:alfheim_grass']],
        spawners={'creature': FEY_HIGH, 'monster': HOSTILE + HOSTILE_ELVES},
        downfall=0.4, temperature=0.4),

    # Still alive. What the elves are trying to get back to.
    'bloomfall_vale': biome(
        fog=0xD9C7F0, sky=0x86C1F0, water=0x4FA8B8, water_fog=0x1F4A55,
        features=[[], [], [], [], [], [], ORES, [], [],
                  ['mythicbotany:alfheim_grass', 'mythicbotany:loose_dreamwood_trees',
                   'mythicbotany:motif_flowers']],
        spawners={'creature': PASSIVE + FEY_BLOOM + FROGS_SPARSE, 'monster': []},
        downfall=1.0, temperature=0.9),

    # Where it went worst. Era IX territory.
    'hollow_marches': biome(
        fog=0x4E4A55, sky=0x5C5766, water=0x33303B, water_fog=0x16141A,
        features=[[], [], [], [], ['mythicbotany:abandoned_apothecaries'], [], ORES, [], [], []],
        spawners={'creature': FEY_COLD + FROGS_SPARSE, 'monster': HOSTILE + HOSTILE_ELVES},
        downfall=0.2, temperature=0.3, precipitation=False),

    # --- the five deficiencies -------------------------------------------------------
    #
    # Alfheim is a wasteland the player is repairing, and until now every biome was some
    # shade of "damaged but liveable". These are the places the devastation actually
    # finished. They sit in narrow corners of the climate space, so they are pockets to
    # find rather than terrain to cross -- except the Void Verge, which is the world's rim.

    # Nothing grows. Not poisoned, not burned — simply used up. No vegetation feature at all.
    'starved_reach': biome(
        fog=0x8A8578, sky=0x9A9384, water=0x4A4A42, water_fog=0x22221E,
        features=[[], [], [], [], [], [], ORES, [], [], []],
        spawners={'creature': FEY_STARVED, 'monster': HOSTILE + HOSTILE_ELVES},
        downfall=0.0, temperature=0.4, precipitation=False),

    # It burned, and then it kept burning. Standing dead wood and ash in the air.
    'scorchfell': biome(
        fog=0x3A2A22, sky=0x6B4A38, water=0x3A2A22, water_fog=0x1A1210,
        features=[[], [], [], [], [], [], ORES, [], [],
                  ['mythicbotany:loose_dreamwood_trees']],
        spawners={'creature': FEY_SCORCH, 'monster': HOSTILE},
        downfall=0.0, temperature=1.2, precipitation=False,
        particle={'options': {'type': 'minecraft:white_ash'}, 'probability': 0.012}),

    # Something moved into the roots and never left.
    'infested_warren': biome(
        fog=0x5A6B3A, sky=0x7A8A4A, water=0x3A5A2A, water_fog=0x1A2A12,
        features=[[], [], [], [], [], [], ORES, [], [], ['mythicbotany:alfheim_grass']],
        spawners={'creature': FEY_WARREN, 'monster': INFESTED},
        downfall=0.6, temperature=0.7),

    # Rot, standing water, and whatever is still in it.
    'decayed_mire': biome(
        fog=0x4A3A4A, sky=0x5A4A5A, water=0x3A2A3A, water_fog=0x1A121A,
        features=[[], [], [], [], ['mythicbotany:abandoned_apothecaries'], [], ORES, [], [],
                  ['mythicbotany:alfheim_grass']],
        spawners={'creature': FEY_MIRE + FROGS, 'monster': ROTTEN + HOSTILE_ELVES},
        downfall=0.9, temperature=0.6,
        particle={'options': {'type': 'minecraft:ash'}, 'probability': 0.008}),

    # The rim. Terrain stops in a ragged cliff and what is left floats: livingrock, still
    # mana-bearing, still carrying ore and geodes. See void_final_density() for the terrain.
    'void_verge': biome(
        fog=0x0A0A12, sky=0x05050A, water=0x101018, water_fog=0x05050A,
        features=[[], [], [], [], [], [], ORES, [], [], []],
        spawners={'creature': FEY_VOID, 'monster': VOID_MOBS},
        downfall=0.0, temperature=0.5, precipitation=False),
}


# Dry-margin siblings share the existing biome schema; terrain and geology
# distinguish their silhouettes and materials. No geodes or pools are embedded.
import copy as _copy
for _name, _fog, _sky in [('shatterfields',0x20202c,0x101018),('prism_drift',0x283344,0x151c30),('rootfall',0x29251f,0x171812),('sepulchral_reach',0x272632,0x15121f),('starless_reach',0x070910,0x02030a)]:
    BIOMES[_name]=_copy.deepcopy(BIOMES['void_verge'])
    BIOMES[_name]['effects']['fog_color']=_fog
    BIOMES[_name]['effects']['sky_color']=_sky
    BIOMES[_name]['features']=[[],[],[],[],[],[],[f for f in ORES if f.endswith('_ore')],[],[],[]]
BIOMES['void_verge']['features']=[[],[],[],[],[],[],[f for f in ORES if f.endswith('_ore')],[],[],[]]

# --- the void, and why these two numbers differ --------------------------------------
#
# The Void Verge needs two things to agree: a BIOME that says "this is the rim", and
# TERRAIN that actually stops. Density functions cannot read biomes, so the only way to
# make them agree is to drive both from the same signal — `alfheim_continentalness`, which
# is what the biome layer already selects on.
#
# The terrain band is deliberately NARROWER than the biome band. That ordering matters:
# every piece of void terrain then falls inside the void biome, and the leftover strip is
# void *biome* with ordinary ground — a shore, where the sky goes black and the fog closes
# in a little before the floor runs out. The reverse ordering would drop holes in the
# ground under a forest, which is a bug rather than a view.
VOID_BIOME_MAX = -0.80
VOID_TERRAIN_MAX = -0.86

# Islands float in this band only. Below it is open air down to the world floor.
VOID_ISLAND_LOW = (20, 50)
VOID_ISLAND_HIGH = (110, 150)


def void_final_density(include_deepworks=True):
    from gen_void_worldgen import density
    normal = {'type':'minecraft:min','argument1':'mythicbotany:alfheim_initial','argument2':'mythicbotany:alfheim_caves'}
    if include_deepworks:
        from gen_deep_terrain import wrap_density
        normal=wrap_density(normal)
    return density(normal)


def pt(cont, ero=(-1.0, 1.0), weird=(-1.0, 1.0), temp=(-1.0, 1.0), hum=(-1.0, 1.0)):
    return {'continentalness': list(cont), 'erosion': list(ero), 'weirdness': list(weird),
            'temperature': list(temp), 'humidity': list(hum),
            'depth': [-1.0, 1.0], 'offset': 0.0}





# --- abandoned apothecaries ------------------------------------------------------------------
#
# Player report 2026-09-04: "Petal apothecaries everywhere?"  They were right, and it is
# MythicBotany's own default rather than anything we did. The shipped placed_feature is
#
#     count: uniform 1..3          rarity_filter: chance 2
#
# -- one to three apothecaries in every SECOND chunk, so roughly one per chunk across the whole
# dimension. That is scenery, not a discovery, and it devalues the one station Era I is built
# around.
#
# Overridden to one per find at 1-in-20 chunks. Still common enough to be a recognisable motif
# of a ruined elven world; rare enough that finding one means something.
#
# SPAWN_ZONE.md §3.2 wants them DENSER inside the Hollow Court specifically. That is a
# biome-scoped modifier and belongs with the city, not here; this is the global default.
APOTHECARY_PLACEMENT = {
    'feature': 'mythicbotany:abandoned_apothecaries',
    'placement': [
        {'type': 'minecraft:count', 'count': 1},
        {'type': 'minecraft:rarity_filter', 'chance': 20},
        {'type': 'minecraft:in_square'},
        {'type': 'mythicbotany:alfheim_ground'},
        {'type': 'minecraft:biome'},
    ],
}

# MythicBotany's mana crystals are the source of the loose bifrost and diluted mana pools, and
# they ship at the same scenery density the apothecaries did. Reported by the user 2026-09-04:
# "The Bifrost blocks and diluted mana pools are too common."
#
# ManaCrystalFeature (mythicbotany/alfheim/worldgen/feature/ManaCrystalFeature.class references
# `bifrost`, `bifrostPerm` and `dilutedPool`) ships as:
#
#     count          uniform 1..4
#     rarity_filter  2
#
# -- one to four crystal formations in every SECOND chunk, so ~1.25 per chunk dimension-wide.
# Bifrost is Botania's rainbow glass and a diluted pool is a working mana station: both are
# things the player is supposed to EARN, and finding them lying around in every other chunk
# reads as decoration rather than as a ruin worth looting.
#
# Thinned to 1 per find at 1-in-12 chunks -- a 15x reduction in placements. Rarer than the
# geodes (1-in-13 to 1-in-15 after the same-day retune) because a free mana pool is worth more
# than a crystal seam, and kept common enough to stay a recognisable feature of the dimension.
MANA_CRYSTAL_PLACEMENT = {
    'feature': 'mythicbotany:mana_crystals',
    'placement': [
        {'type': 'minecraft:count', 'count': 1},
        {'type': 'minecraft:rarity_filter', 'chance': 12},
        {'type': 'minecraft:in_square'},
        {'type': 'mythicbotany:alfheim_ground'},
        # Kept from the original: these are a surface-and-shallow feature, not a deep one.
        {'type': 'libx:height_filter',
         'max_inclusive': {'absolute': 84},
         'min_inclusive': {'above_bottom': 0}},
        {'type': 'minecraft:biome'},
    ],
}

# --- climate ---------------------------------------------------------------------------------
#
# WHY WE OVERRIDE MYTHICBOTANY'S CLIMATE. Runtime-proven 2026-09-04.
#
# MythicBotany ships Alfheim with:
#
#     alfheim_temperature = libx:clamp of density 0.0     <- a CONSTANT
#     alfheim_humidity    = libx:clamp of density 0.0     <- a CONSTANT
#
# Both axes are dead. Every sample in the dimension reads temperature 0.0 and humidity 0.0, so
# any biome band that constrains either away from zero can NEVER be selected -- and nine of our
# eleven did. All five deficiencies, silverbark_wood, ashen_grove, bloomfall_vale, mana_fen and
# hollow_marches were unreachable by construction. The earlier note in this file that the two
# axes were "free" was exactly backwards: they were not free, they were flat.
#
# So we give Alfheim real climate. Same shape MythicBotany uses for its own continentalness --
# cache_2d over a shifted_noise, offset-shifted -- with vanilla's temperature and vegetation
# noises behind it.
#
# BIOME SIZE. The user asked for biomes large enough to be gameplay elements rather than
# patches. In multi-noise, feature size is set by xz_scale: SMALLER scale means LARGER regions.
# Vanilla overworld runs climate at 0.25 and its large-biomes preset at 0.0625, a 4x increase.
# We take the large-biomes value for temperature and humidity, and pull weirdness down from
# MythicBotany's 0.25 to match, so no single axis stays fine-grained and chops the others up.
CLIMATE_SCALE = 0.0625        # temperature / humidity / weirdness. Lower = bigger biomes.
CONT_SCALE = 0.045            # was 0.088 in the jar; ~2x larger continents and voids

# Continentalness is amplified as well as enlarged. The void band needs continentalness below
# VOID_TERRAIN_MAX, and a raw Perlin-family noise almost never reaches its own extremes -- which
# is the second reason the void never appeared even where the biome band was legal. Multiplying
# before the clamp pushes the tails out far enough for the band to be genuinely reachable.
CONT_AMPLIFY = 1.7

# Temperature and humidity get the same treatment, and for a measured reason. After the first
# climate override, `locate biome` on a live world found every LOW-side band -- silverbark_wood
# (temp < -0.3), ashen_grove (hum < -0.4), starved_reach (temp < -0.45) -- and none of the
# HIGH-side ones: bloomfall_vale (temp > 0.2), scorchfell (temp > 0.55) and decayed_mire
# (hum > 0.5) all came back "Could not find". The raw noises simply do not reach far enough
# into their upper tails often enough to matter. Amplifying before the clamp widens both tails
# symmetrically, which is what makes a band at 0.55 a place rather than a rounding error.
CLIMATE_AMPLIFY = 1.8


def _shift(kind):
    return {'type': 'minecraft:cache_once',
            'argument': {'type': f'minecraft:shift_{kind}', 'argument': 'minecraft:offset'}}


def climate_noise(noise, xz_scale, amplify=None):
    """A climate density function in MythicBotany's own shape, so it drops straight in."""
    inner = {'type': 'minecraft:shifted_noise', 'noise': noise,
             'shift_x': _shift('a'), 'shift_y': 0.0, 'shift_z': _shift('b'),
             'xz_scale': xz_scale, 'y_scale': 0.0}
    if amplify:
        inner = {'type': 'libx:clamp',
                 'density': {'type': 'minecraft:mul', 'argument1': amplify, 'argument2': inner},
                 'max': 1.0, 'min': -1.0}
    return {'type': 'minecraft:cache_2d', 'argument': inner}


CLIMATE_OVERRIDES = {
    'alfheim_temperature': climate_noise('minecraft:temperature', CLIMATE_SCALE,
                                         amplify=CLIMATE_AMPLIFY),
    'alfheim_humidity': climate_noise('minecraft:vegetation', CLIMATE_SCALE,
                                      amplify=CLIMATE_AMPLIFY),
    'alfheim_weirdness': climate_noise('minecraft:ridge', CLIMATE_SCALE),
    'alfheim_continentalness': climate_noise('minecraft:badlands_surface', CONT_SCALE,
                                             amplify=CONT_AMPLIFY),
}

# --- climate partition -----------------------------------------------------------------------
#
# WHY THIS EXISTS. Runtime-proven 2026-09-04: the player explored a fresh world and saw only
# MythicBotany's biomes -- alfheim_lakes, dreamwood_forest -- and none of our eleven. The
# Greatbole never generated either, because it is restricted to `#alfheim:has_greatbole` and
# those biomes were never selected.
#
# The cause was the layer's shape, not its contents. A LibX biome_layer entry is a vanilla
# Climate.ParameterPoint, and selection is NEAREST MATCH: whichever entry has the smallest
# distance to the sample point wins, and a point inside two boxes is distance 0 from both.
#
# MythicBotany's originals were "preserved exactly" with full temperature and humidity spans,
# and our biomes were then added as STRICT SUBSETS of them -- ashen_grove sits entirely inside
# dreamwood_forest's box. A subset can never reliably win that tie. It is decided by KD-tree
# order, and it went to the bigger, earlier entries every time.
#
# So the claims below are now resolved into a genuine DISJOINT PARTITION: each claim keeps its
# box minus every higher-priority claim's box, decomposed back into rectangles. Specific
# biomes are declared first and carve their pockets out; MythicBotany's originals are declared
# last and keep everything left over, so nothing is lost and nothing overlaps.
DIMS = ('continentalness', 'erosion', 'weirdness', 'temperature', 'humidity')


def _empty(box):
    return any(box[d][0] >= box[d][1] for d in DIMS)


def _overlaps(a, b):
    return all(a[d][0] < b[d][1] and b[d][0] < a[d][1] for d in DIMS)


def _subtract(a, b):
    """a minus b, as a list of disjoint rectangles. Standard n-dimensional box difference:
    peel off the slab of `a` on each side of `b` along one axis at a time, then narrow to the
    intersection and move to the next axis."""
    if not _overlaps(a, b):
        return [dict(a)]
    out, cur = [], dict(a)
    for d in DIMS:
        alo, ahi = cur[d]
        blo, bhi = b[d]
        if alo < blo:
            piece = dict(cur)
            piece[d] = [alo, min(blo, ahi)]
            if not _empty(piece):
                out.append(piece)
        if bhi < ahi:
            piece = dict(cur)
            piece[d] = [max(bhi, alo), ahi]
            if not _empty(piece):
                out.append(piece)
        cur = dict(cur)
        cur[d] = [max(alo, blo), min(ahi, bhi)]
        if _empty(cur):
            break
    return out


def partition(claims):
    """Resolve priority-ordered (biome, box) claims into disjoint bands.

    Earlier claims win. Each later claim keeps only what no earlier claim took.
    """
    taken, bands = [], []
    for biome, box in claims:
        regions = [dict(box)]
        for t in taken:
            nxt = []
            for r in regions:
                nxt.extend(_subtract(r, t))
            regions = nxt
            if not regions:
                break
        for r in regions:
            band = dict(r)
            band['depth'] = [-1.0, 1.0]
            band['offset'] = 0.0
            bands.append({'biome': biome, 'parameters': band})
        taken.append(dict(box))
    return bands


def assert_disjoint(bands):
    """No two emitted bands may overlap. This is the invariant the old layer violated, and it
    is cheap enough to assert every time rather than trust."""
    bad = []
    for i in range(len(bands)):
        for j in range(i + 1, len(bands)):
            if _overlaps(bands[i]['parameters'], bands[j]['parameters']):
                bad.append((bands[i]['biome'], bands[j]['biome']))
    return bad


# Priority order: most specific first. MythicBotany's originals come last and keep the
# remainder, so their world is still recognisably theirs where we have not claimed anything.
CLAIMS = [
    # --- the five deficiencies: declared first so they carve their pockets out ------------
    #
    # WIDENED 2026-09-04 after probing a live world with `locate biome`. The first version
    # constrained each of these on FOUR OR FIVE axes at once -- starved_reach wanted a narrow
    # band of continentalness AND erosion AND weirdness AND temperature AND humidity to
    # coincide -- and all four deficiencies came back "Could not find a biome of type ...
    # within reasonable distance". Requiring five independent noises to hit narrow ranges
    # simultaneously is not rare, it is effectively impossible.
    #
    # Two constraining axes each, moderately narrow. Still pockets rather than terrain to
    # cross, but pockets that exist.
    (f'{NS}:starved_reach',   pt((0.45, 1.0), temp=(-1.0, -0.45))),
    # Lowered twice, measured each time: at 0.55 and again at 0.45 `locate biome`
    # still reported "Could not find". bloomfall_vale IS found at temp 0.2..0.45,
    # so the noise reaches the low 0.4s and no further in this continentalness band.
    (f'{NS}:scorchfell',      pt((0.15, 0.45), temp=(0.32, 1.0))),
    (f'{NS}:infested_warren', pt((0.0, 0.15), weird=(-1.0, -0.3), hum=(0.45, 1.0))),
    (f'{NS}:decayed_mire',    pt((0.15, 0.45), weird=(-1.0, -0.3), hum=(0.5, 1.0))),
    * __import__('gen_void_worldgen').claims(pt),

    # --- ours: the six that carry the pack's own geography --------------------------------
    (f'{NS}:silverbark_wood',    pt((0.15, 0.45), temp=(-1.0, -0.3))),
    (f'{NS}:ashen_grove',        pt((0.15, 0.45), hum=(-1.0, -0.4))),
    (f'{NS}:bloomfall_vale',     pt((0.15, 0.45), temp=(0.2, 1.0))),
    (f'{NS}:mana_fen',           pt((0.0, 0.15), hum=(0.35, 1.0))),
    (f'{NS}:sundered_highlands', pt((0.45, 1.0), weird=(0.3, 1.0))),
    (f'{NS}:hollow_marches',     pt((0.45, 1.0), hum=(-1.0, -0.3))),

    # --- MythicBotany's originals: they keep everything left over -------------------------
    ('mythicbotany:alfheim_lakes',    pt((-1.0, 0.0))),
    ('mythicbotany:alfheim_lakes',    pt((0.0, 0.1), ero=(-1.0, 0.0))),
    ('mythicbotany:alfheim_plains',   pt((0.1, 0.15), ero=(-1.0, 0.0))),
    ('mythicbotany:alfheim_plains',   pt((0.0, 0.15), ero=(0.0, 1.0))),
    ('mythicbotany:dreamwood_forest', pt((0.15, 0.4), weird=(-1.0, 0.0))),
    ('mythicbotany:golden_fields',    pt((0.15, 0.4), weird=(0.0, 1.0))),
    ('mythicbotany:alfheim_hills',    pt((0.4, 1.0))),
]

LAYER = {
    'biomes': partition(CLAIMS),
    'density': 0.0,
    'range': pt((-1.0, 1.0)),
}


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')
    return path


# --- vegetation added by modifier, not by biome JSON ----------------------------------
#
# Ars Nouveau's own `rare_archwood_mix` and Nature's Aura's `aura_bloom` both target
# #minecraft:is_overworld, which Alfheim is not in, so neither reaches our biomes. Listing
# their features directly in a biome's JSON is the obvious workaround and it is wrong:
# a JSON-listed feature sorts BEFORE every modifier-appended one, while the rest of the
# world sorts the same features in Forge's modifier path order --
#
#   add_mystical_flowers < add_mystical_mushrooms < aura_bloom < rare_archwood_mix
#
# -- so bloomfall_vale asserted `archwoods -> mystical_flowers` while 125 other biomes
# asserted the reverse chain, and `FeatureSorter` throws `Feature order cycle found` on the
# first chunk. Adding them through our own modifier instead, under a `zz_` path that sorts
# after every modifier above, puts them in the position the rest of the world agrees on.
#
# Each feature appears in exactly one modifier. That disjointness is the invariant.
GROVE_MODIFIERS = [
    ('zz_groves_archwood', ['alfheim:bloomfall_vale'], 'ars_nouveau:placed_mixed_archwoods'),
    ('zz_groves_cascading', ['alfheim:silverbark_wood'], 'ars_nouveau:placed_cascading_tree'),
]


def ore_files():
    """Biome modifiers and tags this generator still owns.

    The scarce **vanilla** ore layer that used to live here -- copper, iron, coal, lapis,
    diamond and redstone injected into Alfheim, plus the global `stone_ore_replaceables`
    override that made them place against livingrock -- was retired on 2026-09-03.

    It made Alfheim a reskinned Overworld, which is the one thing the world must not be.
    Alfheim's minerals are now the Twelve Blooms: `tools/blooms_manifest.json`,
    `tools/gen_blooms.py`, and `alfheim_reclaimed_design/ORE_SUPPLEMENTATION.md`. Those
    target #mythicbotany:base_stone_alfheim -- the mod's own Alfheim stone tag -- so no
    global vanilla tag has to be overridden any more.

    The retired files are preserved with their hashes in
    `quarantine/vanilla_ore_layer_2026-09-03/`.
    """
    out = {}

    for name, biomes, feature in GROVE_MODIFIERS:
        out[os.path.join(OUT, NS, 'forge', 'biome_modifier', name + '.json')] = {
            'type': 'forge:add_features',
            'biomes': biomes,
            'features': feature,
            'step': 'vegetal_decoration',
        }

    # Retained deliberately: Alfheim's noise settings set `default_block` to botania:livingrock,
    # and some non-ore worldgen still keys off #minecraft:base_stone_overworld. This one is not
    # an ore-replaceable tag and does not make vanilla ore place in Alfheim.
    out[os.path.join(OUT, 'minecraft', 'tags', 'blocks', 'base_stone_overworld.json')] = {
        'replace': False, 'values': ['botania:livingrock'],
    }
    return out


def main():
    written = []
    for name, data in BIOMES.items():
        written.append(write(os.path.join(OUT, NS, 'worldgen', 'biome', name + '.json'), data))

    for path, data in ore_files().items():
        written.append(write(path, data))

    # Override MythicBotany's layer with the expanded one.
    written.append(write(
        os.path.join(OUT, 'mythicbotany', 'libx', 'biome_layer', 'alfheim.json'), LAYER))

    # Thin the apothecaries out. MythicBotany places 1-3 per second chunk; see the note above.
    written.append(write(
        os.path.join(OUT, 'mythicbotany', 'worldgen', 'placed_feature',
                     'abandoned_apothecaries.json'),
        APOTHECARY_PLACEMENT))

    # Same treatment for the mana crystals, which are what scatter bifrost and diluted pools.
    written.append(write(
        os.path.join(OUT, 'mythicbotany', 'worldgen', 'placed_feature', 'mana_crystals.json'),
        MANA_CRYSTAL_PLACEMENT))

    # Give Alfheim a real climate. MythicBotany ships temperature and humidity as CONSTANT
    # 0.0, which made nine of our eleven biomes unreachable no matter what the layer said --
    # see the note above CLIMATE_OVERRIDES. Also enlarges every climate axis so biomes are
    # regions rather than patches, and amplifies continentalness so the void band is actually
    # reachable rather than merely declared.
    for name, doc in sorted(CLIMATE_OVERRIDES.items()):
        written.append(write(
            os.path.join(OUT, 'mythicbotany', 'worldgen', 'density_function', name + '.json'),
            doc))

    # Override the dimension's final density so the Void Verge has no floor. This is the
    # single riskiest file in the datapack: a malformed density function fails world
    # creation outright, and no static check can prove the terrain it produces is playable.
    written.append(write(
        os.path.join(OUT, 'mythicbotany', 'worldgen', 'density_function', 'alfheim_final.json'),
        void_final_density()))

    # Keep the tag pointing at that single layer (unchanged, but declared explicitly so the
    # datapack is self-describing).
    written.append(write(
        os.path.join(OUT, 'mythicbotany', 'tags', 'libx', 'biome_layer', 'alfheim.json'),
        {'replace': False, 'values': ['mythicbotany:alfheim']}))

    # Structures placed by MythicBotany key off these tags; the new biomes join them so
    # elven houses and Andwari caves still generate. WORLD_STRUCTURE.md §7.
    written.append(write(
        os.path.join(OUT, 'mythicbotany', 'tags', 'worldgen', 'biome', 'alfheim.json'),
        {'replace': False, 'values': [f'{NS}:{b}' for b in BIOMES]}))
    written.append(write(
        os.path.join(OUT, 'mythicbotany', 'tags', 'worldgen', 'biome', 'elven_houses.json'),
        {'replace': False,
         'values': [f'{NS}:silverbark_wood', f'{NS}:bloomfall_vale', f'{NS}:ashen_grove']}))

    for p in written:
        print('  wrote', p)
    print(f'\n{len(BIOMES)} new biomes; layer now places {len(LAYER["biomes"])} entries.')


if __name__ == '__main__':
    main()
