"""Generate the spawn hub: the Greatbole, the Gate in its flank, and the ruined amphitheatre.

Design: alfheim_reclaimed_design/SPAWN_HUB.md.

Everything here is written from numbers rather than placed by hand, because the user said this
will take many passes to get right. A parametric build means pass 2 is an edit to a constant and
a re-run; a hand-placed one would mean rebuilding. That is the whole reason this file exists in
this shape.

Four pieces, all inside the 48x48x48 structure-block save limit, assembled vertically with
jigsaws because a 186-block tree cannot be one structure:

    greatbole/base    48x48x48   roots, trunk foot, the gate chamber, the court socket
    greatbole/trunk   32x48x32   stackable, rollable so segments do not look extruded
    greatbole/crown   48x40x48   canopy
    court/amphitheatre 48x12x48  marble tiers around a sunken stage

The structure NBT format was read off MythicBotany's shipping house.nbt rather than assumed:
size / entities / blocks / palette / DataVersion, blocks as {pos:[x,y,z], state:int}, and
DataVersion 3465 for 1.20.1.

    python tools/gen_spawn_hub.py
    python tools/gen_spawn_hub.py --dry-run
"""
import argparse
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402
from structure_nbt import ADAPTATION_MARGIN, DATA_VERSION, Piece  # noqa: E402

NS = 'alfheim'
DATA = os.path.join('kubejs', 'data', NS)
STRUCT_DIR = os.path.join(DATA, 'structures')
SEED = 20260903                # fixed, so every run reproduces the same tree
HOME = 'mythicbotany:alfheim'
# HUB_RADIUS must cover the tree WHEREVER concentric_rings puts it. Runtime-reported
# 2026-09-04: "the spawn area around the Great Tree was never claimed and we didn't spawn
# inside it."
#
# The cause was a false premise recorded in this file: that `distance: 0, spread: 0` pins the
# structure to the origin. It does not. ChunkGeneratorStructureState.generateRingPositions
# computes the ring-0 position (which IS the origin for distance 0) and then snaps it to a
# preferred_biomes match with findBiomeHorizontal(..., radius 112, ...). Only 3 of our 11
# biomes carry #alfheim:has_greatbole, so that search almost always MOVES the tree -- by up to
# 112 blocks. A 96-block claim centred on the origin can therefore miss the tree entirely.
#
#     112   worst-case biome-search displacement from the origin
#   +  48   half the base piece, so the claim reaches the far side of the trunk
#   +  32   the amphitheatre apron beyond it
#   = 192
HUB_RADIUS = 192

# Every biome in the Alfheim layer, ours and MythicBotany's, read off
# kubejs/data/mythicbotany/libx/biome_layer/alfheim.json. Listed rather than globbed because
# MythicBotany's five come from its jar and would not appear in a scan of our own biome dir.
LAYER_BIOMES = [
    f'{NS}:ashen_grove', f'{NS}:bloomfall_vale', f'{NS}:decayed_mire',
    f'{NS}:hollow_marches', f'{NS}:infested_warren', f'{NS}:mana_fen',
    f'{NS}:scorchfell', f'{NS}:silverbark_wood', f'{NS}:starved_reach',
    f'{NS}:sundered_highlands', f'{NS}:void_verge',
    'mythicbotany:alfheim_hills', 'mythicbotany:alfheim_lakes',
    'mythicbotany:alfheim_plains', 'mythicbotany:dreamwood_forest',
    'mythicbotany:golden_fields',
]
GREATBOLE_EXCLUDED = {f'{NS}:void_verge', 'mythicbotany:alfheim_lakes'}

# --- dimensions ---------------------------------------------------------------------------
BASE = 48
TRUNK_W, TRUNK_H = 32, 24
CROWN_W, CROWN_H = 48, 40
AMPH_W, AMPH_H = 48, 12

# ONE trunk segment, and the tree is 120 blocks rather than 184.
#
# Player report 2026-09-04: "The Great tree doesn't seem to actually spawn its canopy."
# Correct, and the cause is a hard vanilla limit I had got wrong. Jigsaw placement culls any
# piece whose bounding box leaves a radius of `max_distance_from_center` around the structure
# start -- and that radius is capped at 128 by the codec. The old assembly put the crown 184
# blocks above the base origin, so the crown (and very likely the second trunk) was rejected
# every time. The trunk generated, the canopy did not, which is exactly what was observed.
#
# SPAWN_HUB.md §2.1 asserted "a 190-block tree centred on its base spans ±96 -- inside the
# cap". That was wrong: the tree is not centred on the base, it grows upward FROM it, so the
# span is +184, not ±96. The record has been corrected.
#
# 48 + 32 + 40 = 120, which clears 128 with margin under either reading of where the radius is
# measured from. ASSEMBLED_HEIGHT below is asserted against the cap so this cannot regress
# silently, and check_spawn_hub.py S9 asserts it too.
TRUNK_SEGMENTS = 1

ASSEMBLED_HEIGHT = BASE + TRUNK_SEGMENTS * TRUNK_H + CROWN_H
# THE REAL CAP IS NOT 128. Runtime-proven 2026-09-04: world creation refused the structure with
#
#     Structure size including terrain adaptation must not exceed 128
#
# JigsawStructure's codec validates `max_distance_from_center + margin <= 128`, where the margin
# is 0 for terrain_adaptation `none` and 12 for every other value. We use `beard_thin`, so the
# budget is 128 - 12 = 116 -- which is exactly where the original 116 came from. Raising it to
# 128 to fit the canopy traded a culled crown for a world that would not load at all.
TERRAIN_ADAPTATION = 'beard_thin'
MAX_FROM_CENTER = 128 - ADAPTATION_MARGIN[TERRAIN_ADAPTATION]
assert ASSEMBLED_HEIGHT <= MAX_FROM_CENTER, (
    f'the assembled tree is {ASSEMBLED_HEIGHT} blocks but jigsaw placement culls anything '
    f'beyond {MAX_FROM_CENTER} from the start -- the canopy will not generate')

# Trunk radius profile. The base flares hard and the taper is gentle above it: a tree that
# narrows evenly from root to crown reads as a cone, not as a tree.
R_ROOT, R_BASE_TOP = 15.0, 10.5
R_TRUNK_BOT, R_TRUNK_TOP = 10.0, 8.0

# --- the gate chamber, cut into the north (-Z) flank ----------------------------------------
GATE_W, GATE_H = 8, 10         # the sealed_gate face itself
CH_HALF, CH_TOP, CH_BACK = 6, 13, 22   # chamber half-width, ceiling, and depth into the trunk

# --- palettes -------------------------------------------------------------------------------
OAK_LOG_Y = ('minecraft:oak_log', {'axis': 'y'})
OAK_WOOD = ('minecraft:oak_wood', {'axis': 'y'})
AIR = ('minecraft:air', None)
LEAVES = ('minecraft:oak_leaves', {'distance': '7', 'persistent': 'true', 'waterlogged': 'false'})

# Marble stand-ins. There is no marble block in the load path -- Conquest Reforged is
# quarantined and Quark is absent -- so calcite and the quartz family carry it. SPAWN_HUB.md §3.
MARBLE = [('minecraft:calcite', None), ('minecraft:smooth_quartz', None),
          ('minecraft:quartz_block', None)]
MARBLE_RUINED = [('minecraft:cracked_stone_bricks', None), ('minecraft:mossy_stone_bricks', None),
                 ('minecraft:mossy_cobblestone', None)]
ELVEN_MARBLE = ('feywild:elven_quartz_block', None)
COLUMN = ('minecraft:quartz_pillar', {'axis': 'y'})
COLUMN_FALLEN_X = ('minecraft:quartz_pillar', {'axis': 'x'})
COLUMN_FALLEN_Z = ('minecraft:quartz_pillar', {'axis': 'z'})
CAPITAL = ('minecraft:chiseled_quartz_block', None)
WATER = ('minecraft:water', {'level': '0'})
MOSS = ('minecraft:moss_block', None)
MOSS_CARPET = ('minecraft:moss_carpet', None)
RUBBLE = [('minecraft:cobblestone', None), ('minecraft:mossy_cobblestone', None),
          ('minecraft:cracked_stone_bricks', None), ('minecraft:stone_brick_slab', None)]


def vine(face):
    """A vine clinging to the block on the given side of its own position.

    minecraft:vine carries one boolean per face and every one of them defaults to false -- a
    vine with no face set is a floating quad that drops on the first block update. The face
    names the neighbour it is ATTACHED to, so a vine hanging on a pillar's east side is placed
    east of the pillar with `west` true.
    """
    props = {d: 'false' for d in ('north', 'south', 'east', 'west', 'up')}
    props[face] = 'true'
    return ('minecraft:vine', props)

FRAME = ('botania:livingrock_bricks', None)
FRAME_TRIM = ('minecraft:chiseled_quartz_block', None)
GOLD = ('minecraft:gold_block', None)
GLASS = ('botania:elf_glass', None)
GATE = (f'{NS}:sealed_gate', None)
ELF_ENTITY = 'richs_races_wood_elves:wood_elf'
FLOOR = ('botania:livingrock', None)


def radius_at(y, h, r0, r1):
    """Linear taper, with a root flare in the bottom eighth that grows sharply toward y=0."""
    t = y / max(1, h - 1)
    r = r0 + (r1 - r0) * t
    flare = h / 8.0
    if y < flare:
        r += (r0 * 0.45) * ((flare - y) / flare) ** 2
    return r


def trunk_column(p, cx, cz, h, r0, r1, rng, roots=False):
    """Fill the trunk mass. Surface is oak_log, interior oak_wood -- the bark reads better on
    the outside and the interior is never seen except where the chamber cuts it open."""
    for y in range(h):
        r = radius_at(y, h, r0, r1)
        # Roots: eight buttresses that only exist near the ground, each a lobe of extra radius.
        for x in range(p.size[0]):
            for z in range(p.size[2]):
                dx, dz = x - cx, z - cz
                d = math.hypot(dx, dz)
                rr = r
                if roots and y < 10:
                    ang = math.atan2(dz, dx)
                    lobe = math.cos(4.0 * ang) ** 2
                    rr += lobe * (10 - y) * 0.75
                # A little noise on the surface so the trunk is not a cylinder.
                rr += (rng.random() - 0.5) * 0.7
                if d <= rr:
                    p.set(x, y, z, OAK_LOG_Y if d > rr - 1.6 else OAK_WOOD)


def carve_gate_chamber(p, cx, cz):
    """Hollow the chamber out of the north flank and build the gate into its back wall.

    Cut first, then build: the frame has to survive the carve, so nothing is placed until the
    air is in.
    """
    # --- the void
    for y in range(1, CH_TOP):
        for x in range(cx - CH_HALF, cx + CH_HALF + 1):
            for z in range(0, CH_BACK + 1):
                # An arched ceiling rather than a flat one.
                arch = CH_TOP - abs(x - cx) * 0.45
                if y < arch:
                    p.set(x, y, z, AIR)

    # --- floor
    for x in range(cx - CH_HALF - 1, cx + CH_HALF + 2):
        for z in range(0, CH_BACK + 2):
            p.set(x, 0, z, FLOOR)

    # --- the gate face, RECESSED one block behind the wall
    #
    # Asked for 2026-09-04: "the portal block should be inset like a nether portal or a glass
    # pane." A nether portal reads as inset because the portal plane sits one block behind the
    # obsidian frame, not because the portal block is thin -- so this reproduces the geometry
    # rather than the block shape.
    #
    # It has to be geometry. Jigsaw gives the start piece a RANDOM rotation, rotations are
    # about the Y axis, and a thin vertical plane is not symmetric under a 90-degree Y turn --
    # so a slab-shaped model would render edge-on, as a row of fins, in half of all worlds.
    # KubeJS cannot rescue that either: HorizontalDirectionalBlockJS carries FACING but does
    # not override Block.rotate, so a `facing` property would not be turned with the structure.
    # Cutting the niche is rotation-proof because the niche rotates with everything else.
    gx0, gx1 = cx - GATE_W // 2, cx - GATE_W // 2 + GATE_W - 1
    gate_z = CH_BACK + 1
    for y in range(2, 2 + GATE_H):
        for x in range(gx0, gx1 + 1):
            p.set(x, y, CH_BACK, AIR)      # the opening you look through
            p.set(x, y, gate_z, GATE)      # the surface itself, set back behind the frame

    # --- the frame around it: livingrock with chiseled quartz corners and gold at the keystone
    for y in range(1, 3 + GATE_H):
        for x in range(gx0 - 2, gx1 + 3):
            on_edge = (x < gx0 or x > gx1 or y < 2 or y >= 2 + GATE_H)
            if not on_edge:
                continue
            corner = (x in (gx0 - 2, gx0 - 1, gx1 + 1, gx1 + 2) and
                      y in (1, 2 + GATE_H - 1, 2 + GATE_H))
            p.set(x, y, CH_BACK, FRAME_TRIM if corner else FRAME)
    p.set(cx, 2 + GATE_H, CH_BACK, GOLD)
    p.set(cx - 1, 2 + GATE_H, CH_BACK, GOLD)

    # --- elf glass in the arch above the gate, so the chamber is lit without a torch
    for x in range(gx0, gx1 + 1):
        p.set(x, 2 + GATE_H + 1, CH_BACK, GLASS)


def hub_anchor(c):
    """The world spawn, baked into the gate chamber as a marker entity.

    This is the fix for "we didn't spawn inside it". The previous scheme summoned a marker at
    0 250 0 and let spreadplayers drop it, which anchors the world spawn to the ORIGIN -- and
    the origin is not the tree (see HUB_RADIUS). A marker carried inside the structure's own
    NBT lands wherever the structure lands, so the anchor cannot desynchronise from the tree no
    matter what the biome search does. Same reason the court is baked in rather than summoned.

    Standing on the chamber floor, four blocks in front of the gate, facing it. Rotation yaw 0
    is south (+z) and the gate is at the +z back wall, so a player spawning here looks straight
    at it.
    """
    x, y, z = c, 1, CH_BACK - 4
    return {
        'pos': [nbt.Double(x + 0.5), nbt.Double(y), nbt.Double(z + 0.5)],
        'blockPos': [nbt.Int(x), nbt.Int(y), nbt.Int(z)],
        'nbt': {
            'id': 'minecraft:marker',
            'Rotation': [nbt.Float(0.0), nbt.Float(0.0)],
            # Two tags on purpose. `alfheim_hub` is what every hub command selects on;
            # `alfheim_hub_baked` lets hub/create tell a structure-carried anchor apart from the
            # summoned fallback, so it prefers this one and never ends up with both.
            'Tags': ['alfheim_hub', 'alfheim_hub_baked'],
        },
    }


def build_base(rng):
    p = Piece(BASE, BASE, BASE)
    c = BASE // 2
    trunk_column(p, c, c, BASE, R_ROOT, R_BASE_TOP, rng, roots=True)
    carve_gate_chamber(p, c, c)
    p.entities.append(hub_anchor(c))

    # Up to the first trunk segment. The trunk pool holds only `trunk`, so the segment directly
    # above the base is never the crown -- a tree with no trunk would still be a legal assembly.
    p.jigsaw(c, BASE - 1, c, f'{NS}:bole_top', f'{NS}:trunk_bottom',
             f'{NS}:greatbole/trunk', 'up_north')

    # Out to the amphitheatre, at the chamber mouth, facing north. `aligned` rather than
    # `rollable`: the court has to sit squarely in front of the gate, not at 90 degrees to it.
    p.jigsaw(c, 1, 0, f'{NS}:court_gate', f'{NS}:court_plug',
             f'{NS}:court/amphitheatre', 'north_up', joint='aligned')
    return p


def build_trunk(rng):
    p = Piece(TRUNK_W, TRUNK_H, TRUNK_W)
    c = TRUNK_W // 2
    trunk_column(p, c, c, TRUNK_H, R_TRUNK_BOT, R_TRUNK_TOP, rng)
    p.jigsaw(c, 0, c, f'{NS}:trunk_bottom', f'{NS}:bole_top', 'minecraft:empty', 'down_north')
    # Deterministic: with a single segment the trunk must lead to the crown, not to a pool
    # that might roll another trunk and push the canopy past the placement radius again.
    nxt = f'{NS}:greatbole/trunk_or_crown' if TRUNK_SEGMENTS > 1 else f'{NS}:greatbole/crown_only'
    p.jigsaw(c, TRUNK_H - 1, c, f'{NS}:trunk_top', f'{NS}:trunk_bottom', nxt, 'up_north')
    return p


def build_crown(rng):
    p = Piece(CROWN_W, CROWN_H, CROWN_W)
    c = CROWN_W // 2

    # A PROBE, not decoration. The crown is the piece jigsaw was silently culling when the tree
    # overran max_distance_from_center, and a missing canopy is invisible to every static check
    # -- the .nbt was always fine, it just never got placed. A marker inside the crown turns
    # "did the canopy generate?" into a question a headless server can answer:
    #
    #     data get entity @e[type=minecraft:marker,tag=alfheim_crown_probe,limit=1] Pos
    #
    # which reports nothing at all if the piece was culled, and its world Y if it was not.
    p.entities.append({
        'pos': [nbt.Double(c + 0.5), nbt.Double(CROWN_H // 2), nbt.Double(c + 0.5)],
        'blockPos': [nbt.Int(c), nbt.Int(CROWN_H // 2), nbt.Int(c)],
        'nbt': {'id': 'minecraft:marker', 'Tags': ['alfheim_crown_probe']},
    })

    # The last of the trunk, then boughs, then the canopy shell.
    trunk_column(p, c, c, CROWN_H // 2, R_TRUNK_TOP, 5.0, rng)

    # Four boughs sweeping out and up from the trunk top.
    for k in range(4):
        ang = math.pi / 4 + k * math.pi / 2
        for t in range(20):
            bx = c + math.cos(ang) * t
            bz = c + math.sin(ang) * t
            by = CROWN_H // 2 - 4 + t * 0.45
            for ox in (-1, 0, 1):
                for oz in (-1, 0, 1):
                    p.set(int(bx) + ox, int(by), int(bz) + oz, OAK_WOOD)

    # Canopy: an ellipsoid shell, thinned at random so it is not a solid dome. Dead patches are
    # simply omitted -- the crown is meant to read as half-gone.
    cy = CROWN_H - 13
    for y in range(CROWN_H):
        for x in range(CROWN_W):
            for z in range(CROWN_W):
                dx, dy, dz = (x - c) / 21.0, (y - cy) / 12.0, (z - c) / 21.0
                d = dx * dx + dy * dy + dz * dz
                if 0.55 < d <= 1.0 and rng.random() < 0.72:
                    if (x, y, z) not in p.blocks:
                        p.set(x, y, z, LEAVES)

    p.jigsaw(c, 0, c, f'{NS}:trunk_bottom', f'{NS}:trunk_top', 'minecraft:empty', 'down_north')
    return p


def court_entities(c, ground):
    """Bake the Hollow Court into the amphitheatre.

    The roster is read from tools/hollow_court_manifest.json rather than restated, so the names
    here and the names in quest_line_links.json cannot drift -- and drift is fatal, because
    quest_giver matches an NPC to its quest line by custom name.

    Putting the NPCs in the structure rather than summoning them by command is what makes the
    court land in the amphitheatre at all. 03_hollow_court.js was written before the hub existed
    and placed them at the player's landing spot, which spreadplayers puts up to 2000 blocks from
    the tree. A structure knows where its own seats are; a command does not.

    The NBT is the same as the script used, and for the same reasons: WoodElfEntity extends
    Monster and targets Player, so NoAI is what makes it an NPC rather than an archer.
    """
    man = json.load(open(os.path.join('tools', 'hollow_court_manifest.json'), encoding='utf-8'))
    posts = []
    # Named pair flank the stage, facing the gate to the south.
    #
    # SKIN SLOTS. richs_races_wood_elves picks its texture from `DataSkinSwap` (1..6). Slots 5
    # and 6 carry the custom Magister and Captain art generated by tools/gen_court_skins.py,
    # and 16_wood_elf_skins.js keeps every wild elf out of them. Baked here rather than
    # summoned so the pair are already wearing the right thing the first time anyone sees them.
    for i, n in enumerate(man['named']):
        posts.append((n['name'], c + (-5 if i % 2 else 5), ground, c + 6, 5 + i))
    # Ambient court scattered up the tiers, on their own seats.
    for i, n in enumerate(man['ambient']):
        ang = math.pi * (0.15 + 0.7 * (i / max(1, len(man['ambient']) - 1)))
        r = 12.0 + (i % 3) * 3.5
        x, z = int(c - math.cos(ang) * r), int(c - math.sin(ang) * r)
        # Ambient court draw from the four unreserved slots, so the crowd is varied without
        # any of them wearing the named pair's art.
        posts.append((n['name'], x, ground + int((r - 8.0) / 3.5), z, 1 + (i % 4)))

    out = []
    for name, x, y, z, skin in posts:
        out.append({
            'pos': [nbt.Double(x + 0.5), nbt.Double(y), nbt.Double(z + 0.5)],
            'blockPos': [nbt.Int(x), nbt.Int(y), nbt.Int(z)],
            'nbt': {
                'id': ELF_ENTITY,
                'DataSkinSwap': nbt.Int(skin),
                'NoAI': nbt.Byte(1),
                'PersistenceRequired': nbt.Byte(1),
                'Invulnerable': nbt.Byte(1),
                'Silent': nbt.Byte(1),
                'CustomNameVisible': nbt.Byte(1),
                'CustomName': json.dumps({'text': name}),
            },
        })
    return out, posts


def courtyard_detail(p, c, ground, stage_r, outer_r, rng):
    """Pillars, vines, a fountain and rubble.

    Asked for 2026-09-04: "the courtyard needs some pillars and some vines and a little central
    pool of water with a little fountain, another knobbly detail work giving the image of a
    decayed central amphitheatre court."

    The tiers alone read as a shape rather than as a place -- geometrically correct and
    completely uninhabited. Everything here exists to say the court was USED and then left:
    a fountain that still runs, a colonnade that has lost half its columns, and vines taking
    the rest back.

    Height budget is tight. AMPH_H is 48x12x48 and the top tier already reaches ground+4, so
    nothing here may rise past y = AMPH_H - 1 or it is silently dropped from the piece.
    """
    top = AMPH_H - 1

    # --- the fountain ------------------------------------------------------------------------
    # Sunk into the stage floor rather than sitting on it, so the stage stays walkable and the
    # basin reads as built-in. The court's named pair stand at hypot(5, 6) = 7.8 from centre,
    # comfortably outside the basin's rim.
    basin_r, rim_r = 4.2, 5.4
    for x in range(c - 7, c + 8):
        for z in range(c - 7, c + 8):
            d = math.hypot(x - c, z - c)
            if d <= basin_r:
                p.set(x, ground - 2, z, ELVEN_MARBLE)          # basin floor
                p.set(x, ground - 1, z, WATER)                 # the water itself
            elif d <= rim_r:
                # A kerb one block proud of the stage, broken in places.
                p.set(x, ground - 1, z, ELVEN_MARBLE)
                if rng.random() < 0.72:
                    p.set(x, ground, z, rng.choice(MARBLE_RUINED)
                          if rng.random() < 0.35 else ELVEN_MARBLE)

    # The spout: a short plinth with a bowl on top. The overflow cascading back into the basin
    # is the point -- a still pool reads as a puddle, a running one reads as maintained.
    for y in range(ground - 1, ground + 2):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) + abs(dz) <= 1:
                    p.set(c + dx, y, c + dz, ELVEN_MARBLE)
    p.set(c, ground + 2, c, WATER)

    # --- the colonnade -----------------------------------------------------------------------
    # An inner ring, between the stage and the mid tiers. Standing columns alternate with
    # stumps and with columns that are simply gone; a complete ring would read as restored.
    ring_r = stage_r + 5.0
    for k in range(10):
        ang = k * math.tau / 10
        px, pz = int(c + math.cos(ang) * ring_r), int(c + math.sin(ang) * ring_r)
        fate = rng.random()
        if fate < 0.20:
            # Gone. Leave the drum it fell as, lying where it landed.
            ox, oz = int(math.cos(ang) * 2), int(math.sin(ang) * 2)
            axis = COLUMN_FALLEN_X if abs(ox) >= abs(oz) else COLUMN_FALLEN_Z
            for t in range(rng.randint(2, 4)):
                p.set(px + ox + (t if axis is COLUMN_FALLEN_X else 0), ground,
                      pz + oz + (0 if axis is COLUMN_FALLEN_X else t), axis)
            continue
        h = rng.randint(2, 4) if fate < 0.55 else rng.randint(5, 7)
        base_y = ground
        for y in range(base_y, min(base_y + h, top)):
            p.set(px, y, pz, COLUMN)
        # Only the tall ones kept their capital.
        if h >= 5 and base_y + h < top:
            p.set(px, base_y + h, pz, CAPITAL)
        # Vines down whichever side faces out of the ring.
        face = 'west' if math.cos(ang) > 0 else 'east'
        vx = px + (1 if face == 'west' else -1)
        for y in range(base_y + 1, min(base_y + h, top)):
            if rng.random() < 0.55:
                p.set(vx, y, pz, vine(face))

    # --- vines on the rim stumps and the top tier --------------------------------------------
    for k in range(24):
        ang = k * math.tau / 24
        d = outer_r - rng.uniform(0.5, 3.0)
        vx, vz = int(c + math.cos(ang) * d), int(c + math.sin(ang) * d)
        face = 'west' if math.cos(ang) > 0 else 'east'
        y = ground + int((d - stage_r) / 3.5)
        if rng.random() < 0.5 and y < top:
            p.set(vx + (1 if face == 'west' else -1), y, vz, vine(face))

    # --- knobbly work: rubble, moss and cracked ground ---------------------------------------
    # Scattered rather than patterned. Rubble sits ON the tiers, so it reads as fallen masonry
    # rather than as a floor material.
    for _ in range(150):
        ang = rng.random() * math.tau
        d = rng.uniform(stage_r - 2.0, outer_r)
        x, z = int(c + math.cos(ang) * d), int(c + math.sin(ang) * d)
        y = ground + max(0, int((d - stage_r) / 3.5))
        if y >= top:
            continue
        r = rng.random()
        if r < 0.42:
            p.set(x, y, z, rng.choice(RUBBLE))
        elif r < 0.72:
            p.set(x, y, z, MOSS_CARPET)
        elif r < 0.86:
            p.set(x, y - 1, z, MOSS)
        else:
            p.set(x, y, z, rng.choice(MARBLE_RUINED))


def build_amphitheatre(rng):
    """Concentric ruined tiers around a sunken stage, opening south toward the gate."""
    p = Piece(AMPH_W, AMPH_H, AMPH_W)
    c = AMPH_W // 2
    stage_r, outer_r = 8.0, 22.0
    ground = 4                      # tiers rise from here; the stage is sunk below it

    for x in range(AMPH_W):
        for z in range(AMPH_W):
            dx, dz = x - c, z - c
            d = math.hypot(dx, dz)
            if d > outer_r:
                continue

            # The stage floor, cracked.
            if d <= stage_r:
                blk = ELVEN_MARBLE if rng.random() < 0.12 else (
                    rng.choice(MARBLE_RUINED) if rng.random() < 0.28 else rng.choice(MARBLE))
                p.set(x, ground - 1, z, blk)
                continue

            # Seating tiers: one step up per 3.5 blocks of radius.
            tier = int((d - stage_r) / 3.5)
            top = ground + tier
            # Collapse: the further out, the more of the tier is simply gone.
            if rng.random() < 0.10 + 0.02 * tier:
                continue
            blk = rng.choice(MARBLE_RUINED) if rng.random() < 0.30 else rng.choice(MARBLE)
            for y in range(ground - 1, top + 1):
                p.set(x, y, z, blk)

    # Column stumps around the rim, broken to differing heights.
    for k in range(12):
        ang = k * math.pi / 6
        cxp, czp = int(c + math.cos(ang) * (outer_r - 1.5)), int(c + math.sin(ang) * (outer_r - 1.5))
        h = rng.choice([1, 2, 2, 3, 5, 7])
        for y in range(h):
            p.set(cxp, ground + int((outer_r - 1.5 - stage_r) / 3.5) + y, czp, COLUMN)

    courtyard_detail(p, c, ground, stage_r, outer_r, rng)

    # The court itself, seated in the structure rather than summoned at the player.
    ents, posts = court_entities(c, ground)
    p.entities = ents
    for _, x, y, z, _skin in posts:               # a clear seat under each, so none is buried
        p.set(x, y - 1, z, ELVEN_MARBLE)
        for dy in range(3):
            if (x, y + dy, z) in p.blocks and dy > 0:
                del p.blocks[(x, y + dy, z)]
        p.set(x, y, z, AIR)
        p.set(x, y + 1, z, AIR)

    # The plug, facing south back at the tree.
    p.jigsaw(c, ground, AMPH_W - 1, f'{NS}:court_plug', f'{NS}:court_gate',
             'minecraft:empty', 'south_up', joint='aligned')
    return p


# --- jigsaw wiring ---------------------------------------------------------------------------
def pool(name, elements, fallback='minecraft:empty'):
    return {'name': f'{NS}:{name}', 'fallback': fallback,
            'elements': [{'weight': w, 'element': {
                'location': f'{NS}:{loc}', 'processors': 'minecraft:empty',
                'projection': proj, 'element_type': 'minecraft:single_pool_element'}}
                for loc, w, proj in elements]}


def write_json(path, obj, dry):
    if dry:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    dry = a.dry_run
    rng = random.Random(SEED)

    pieces = {
        'greatbole/base': build_base(rng),
        'greatbole/trunk': build_trunk(rng),
        'greatbole/crown': build_crown(rng),
        'court/amphitheatre': build_amphitheatre(rng),
    }

    for name, p in pieces.items():
        path = os.path.join(STRUCT_DIR, name + '.nbt')
        if not dry:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            nbt.save(path, '', p.to_nbt())
        size = os.path.getsize(path) if (not dry and os.path.exists(path)) else 0
        print(f'  {name:22} {p.size[0]}x{p.size[1]}x{p.size[2]}  '
              f'{len(p.blocks):>6} blocks  {len(p.palette):>3} palette  {size / 1024:6.1f} KB')

    # --- template pools
    write_json(os.path.join(DATA, 'worldgen', 'template_pool', 'greatbole', 'base.json'),
               pool('greatbole/base', [('greatbole/base', 1, 'rigid')]), dry)
    write_json(os.path.join(DATA, 'worldgen', 'template_pool', 'greatbole', 'trunk.json'),
               pool('greatbole/trunk', [('greatbole/trunk', 1, 'rigid')]), dry)
    # Two trunk entries to one crown: the tree usually grows another segment before it tops out,
    # and the pool's own fallback ends the chain if the depth budget runs out first.
    write_json(os.path.join(DATA, 'worldgen', 'template_pool', 'greatbole', 'trunk_or_crown.json'),
               pool('greatbole/trunk_or_crown',
                    [('greatbole/trunk', TRUNK_SEGMENTS, 'rigid'),
                     ('greatbole/crown', 1, 'rigid')],
                    fallback=f'{NS}:greatbole/crown_only'), dry)
    write_json(os.path.join(DATA, 'worldgen', 'template_pool', 'greatbole', 'crown_only.json'),
               pool('greatbole/crown_only', [('greatbole/crown', 1, 'rigid')]), dry)
    write_json(os.path.join(DATA, 'worldgen', 'template_pool', 'court', 'amphitheatre.json'),
               pool('court/amphitheatre', [('court/amphitheatre', 1, 'rigid')]), dry)

    # --- structure. beard_thin is what MythicBotany's own elven houses use, and it is what
    # keeps the root flare sitting in the ground instead of on a pillar of air.
    write_json(os.path.join(DATA, 'worldgen', 'structure', 'greatbole.json'), {
        'type': 'minecraft:jigsaw',
        'biomes': f'#{NS}:has_greatbole',
        'step': 'surface_structures',
        'terrain_adaptation': TERRAIN_ADAPTATION,
        'start_pool': f'{NS}:greatbole/base',
        'size': 6,
        'max_distance_from_center': MAX_FROM_CENTER,
        'start_height': {'absolute': 0},
        'project_start_to_heightmap': 'WORLD_SURFACE_WG',
        'use_expansion_hack': False,
        'spawn_overrides': {},
    }, dry)

    # --- placement: the vanilla "at world spawn" mechanism, the one strongholds use.
    write_json(os.path.join(DATA, 'worldgen', 'structure_set', 'greatbole.json'), {
        'structures': [{'structure': f'{NS}:greatbole', 'weight': 1}],
        # `salt` is MANDATORY on concentric_rings -- omitting it fails world creation with
        #   No key salt in MapLike[{...}]
        # Vanilla's strongholds.json carries salt 0; ours differs so the two rings cannot
        # correlate. Runtime-proven 2026-09-04.
        'placement': {'type': 'minecraft:concentric_rings', 'distance': 0, 'spread': 0,
                      'count': 1, 'salt': 40092026,
                      'preferred_biomes': f'#{NS}:has_greatbole'},
    }, dry)

    # --- the tag, which is what PINS THE TREE TO THE ORIGIN.
    #
    # It is read in two places and they do different jobs, which is why this tag being narrow
    # was two bugs rather than one:
    #
    #   structure.biomes            VALIDITY. If the biome at the chosen chunk is not in the
    #                               tag the Greatbole does not generate AT ALL. With only three
    #                               biomes tagged out of sixteen in the layer, a fresh world
    #                               usually had no tree anywhere -- the user's "No spawn
    #                               structure on Fresh World", 2026-09-04.
    #
    #   structure_set.preferred_biomes
    #                               POSITION. concentric_rings computes ring 0 (the origin, for
    #                               distance 0 / spread 0) and then snaps it to a tag match via
    #                               findBiomeHorizontal(..., radius 112, findClosest=true).
    #                               findClosest returns the CENTRE when the centre matches, so a
    #                               tag that covers the origin's biome leaves the structure at
    #                               chunk 0,0. A narrow tag forces the search outward and moves
    #                               the tree up to 112 blocks -- which is why the claim and the
    #                               spawn point, both pinned to the origin, missed it.
    #
    # So: tag everything buildable. That pins the tree to 0,0 and lets
    # project_start_to_heightmap WORLD_SURFACE_WG + terrain_adaptation beard_thin do the
    # terrain snap, which is the whole of what the hub needs.
    #
    # Two exclusions, both because the snap cannot save them:
    #   void_verge     floating islands over nothing; there is no ground to sit the roots in.
    #   alfheim_lakes  WORLD_SURFACE_WG counts fluids, so the trunk would stand on the water.
    # When the origin lands in one of those the search relocates to the nearest of the other
    # fourteen, which is close -- and the baked anchor (see hub_anchor) means the spawn point
    # follows the tree regardless.
    write_json(os.path.join(DATA, 'tags', 'worldgen', 'biome', 'has_greatbole.json'),
               {'replace': False, 'values': [b for b in LAYER_BIOMES
                                             if b not in GREATBOLE_EXCLUDED]}, dry)

    if not dry:
        with open(os.path.join('kubejs', 'server_scripts', '04_spawn_hub.js'),
                  'w', encoding='utf-8') as f:
            f.write(protection_script())
    print(f'  protection            kubejs/server_scripts/04_spawn_hub.js  '
          f'radius {HUB_RADIUS}, {HOME}')

    total = sum(len(p.blocks) for p in pieces.values())
    print(f'\n  {len(pieces)} pieces, {total} blocks, tree {ASSEMBLED_HEIGHT} blocks tall '
          f'(base + {TRUNK_SEGMENTS} trunk + crown), placement radius {MAX_FROM_CENTER}')
    return 0

def protection_script():
    """The admin hub: no hostile spawns, no blast damage, no griefing, inside a radius.

    FTB Chunks is NOT installed -- the pack has ftblibrary/ftbquests/ftbteams/ftbxmodcompat and
    no ftbchunks -- so the claim layer the user asked for by name is a pack composition decision
    (SPAWN_HUB.md 4.1). The behaviour it was wanted FOR does not need it, and is here.

    Every handler is registered inside its own try/catch and reports whether it armed. KubeJS
    event names have moved between builds, and a protection that silently failed to register is
    worse than none: it would be trusted. The log line at startup is the evidence.
    """
    return f'''// Alfheim Reclaimed — the protected spawn hub
//
// GENERATED by tools/gen_spawn_hub.py — do not hand-edit.
// Design: alfheim_reclaimed_design/SPAWN_HUB.md §4.
//
// The hub is a destination the player returns to for the whole campaign, so it has to survive
// the whole campaign. A creeper crater in the amphitheatre on day 40 is not a war story, it is
// a broken quest hub.
//
// FTB Chunks is not installed, so this is not an FTB claim — it is the behaviour a claim would
// have given, done directly. If ftbchunks is added later, the map/team layer goes on top of
// this rather than replacing it.

const HUB_DIMENSION = '{HOME}'
// The claim is centred on the ORIGIN, not on the tree, because no coordinate for the tree is
// knowable from a script: concentric_rings snaps ring 0 to a preferred_biomes match up to 112
// blocks away. HUB_RADIUS is sized to cover that whole search disc plus the structure, so the
// claim contains the tree no matter which way the search went. The spawn point does not rely
// on this box at all -- it is a marker baked into the base piece (see build_base).
const HUB_X = 0
const HUB_Z = 0
const HUB_RADIUS = {HUB_RADIUS}

// Players may still build inside the hub by default. Flip this to lock it to operators, which
// is what "claimed by admins" implies if the hub is ever opened to other people.
const PROTECT_FROM_PLAYERS = false

function inHub(level, x, z) {{
    if (!level) return false
    try {{
        if (String(level.dimension) !== HUB_DIMENSION) return false
    }} catch (e) {{
        return false
    }}
    return Math.abs(x - HUB_X) <= HUB_RADIUS && Math.abs(z - HUB_Z) <= HUB_RADIUS
}}

const armed = []

// ---------------------------------------------------------------- no hostile spawns
try {{
    EntityEvents.checkSpawn(event => {{
        const e = event.entity
        if (!e || !inHub(e.level, e.x, e.z)) return
        // Our own court is summoned/placed, not spawned, so this never touches it — but the
        // name check is cheap insurance against a future spawn-based placement.
        if (e.type === 'richs_races_wood_elves:wood_elf') return
        if (e.living && e.monster) event.cancel()
    }})
    armed.push('no-hostile-spawns')
}} catch (e) {{
    console.warn('[Alfheim Reclaimed] hub: could not arm spawn suppression: ' + e)
}}

// ---------------------------------------------------------------- no blast damage
try {{
    LevelEvents.beforeExplosion(event => {{
        if (inHub(event.level, event.x, event.z)) event.cancel()
    }})
    armed.push('no-explosions')
}} catch (e) {{
    console.warn('[Alfheim Reclaimed] hub: could not arm explosion protection: ' + e)
}}

// ---------------------------------------------------------------- no mob griefing
try {{
    BlockEvents.broken(event => {{
        if (!inHub(event.level, event.block.x, event.block.z)) return
        const p = event.player
        if (!p) {{ event.cancel(); return }}            // no player == a mob or a mechanism
        if (PROTECT_FROM_PLAYERS && !p.op) {{
            event.cancel()
            p.tell('The court is under the protection of the Royal Elven Guard.')
        }}
    }})
    armed.push(PROTECT_FROM_PLAYERS ? 'blocks-locked-to-ops' : 'no-mob-block-breaking')
}} catch (e) {{
    console.warn('[Alfheim Reclaimed] hub: could not arm block protection: ' + e)
}}

ServerEvents.loaded(event => {{
    console.info(`[Alfheim Reclaimed] spawn hub protected: ${{HUB_RADIUS}}-block radius at ` +
                 `${{HUB_X}},${{HUB_Z}} in ${{HUB_DIMENSION}} — armed: ${{armed.join(', ')}}` +
                 (armed.length < 3 ? '  ** SOME PROTECTIONS DID NOT ARM, see warnings above **'
                                   : ''))
}})
'''


if __name__ == '__main__':
    raise SystemExit(main())
