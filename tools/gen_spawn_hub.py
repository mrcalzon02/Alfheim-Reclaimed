"""Generate the spawn hub: the Greatbole, the Gate in its flank, and the ruined amphitheatre.

Design: alfheim_reclaimed_design/SPAWN_HUB.md.

Everything here is written from numbers rather than placed by hand, because the user said this
will take many passes to get right. A parametric build means pass 2 is an edit to a constant and
a re-run; a hand-placed one would mean rebuilding. That is the whole reason this file exists in
this shape.

Seven pieces, all inside the 48x48x48 structure-block save limit. The tree is assembled
vertically and the civic wings are placed on one fixed origin grid:

    greatbole/base    48x48x48   roots, trunk foot, the gate chamber, the court socket
    greatbole/trunk   32x48x32   stackable, rollable so segments do not look extruded
    greatbole/crown   48x40x48   canopy
    court/amphitheatre 48x12x48  marble tiers around a sunken stage
    court/*             3x 48x16x48  detailed residences, service halls and council terrace

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
# The protection envelope, in block coordinates, inclusive.
#
# History: this was a 128-block radius square centred on the tree, sized in 2026-09-04 to cover
# a placement probe that could displace the whole complex up to 512 blocks from the origin. That
# probe is gone -- gen_world_hub now places every template at fixed offsets from X=0/Z=0 -- so
# the allowance became 289 claimed chunks around a 144-by-144 build, most of it empty ground
# south of the tree. Reported from the field 2026-09-07: "the claimed area is successfully
# claiming, but much too large an area."
#
# The envelope is now the union of the seven placed templates, snapped out to chunk boundaries.
# Derived from the placement table in gen_world_hub.PLACE (offset + size, per piece):
#
#     west_residence   X -72..-25    east_service   X  24.. 71
#     north_council    Z -120..-73   amphitheatre   Z -72..-25
#     base / crown     X -24.. 23    Z -24.. 23
#     -------------------------------------------------------
#     union            X -72.. 71    Z -120.. 23
#     chunk-snapped    X -80.. 79    Z -128.. 31     = 10 x 10 = 100 chunks
#
# check_spawn_hub re-derives this from assemble.mcfunction and fails if the two disagree, so a
# future piece or a moved offset cannot silently escape the claim.
HUB_MIN_X, HUB_MAX_X = -80, 79
HUB_MIN_Z, HUB_MAX_Z = -128, 31

# Every biome in the Alfheim layer, ours and MythicBotany's, read off
# kubejs/data/mythicbotany/libx/biome_layer/alfheim.json. Listed rather than globbed because
# MythicBotany's five come from its jar and would not appear in a scan of our own biome dir.
LAYER_BIOMES = [
    f'{NS}:ashen_grove', f'{NS}:bloomfall_vale', f'{NS}:decayed_mire',
    f'{NS}:hollow_marches', f'{NS}:infested_warren', f'{NS}:mana_fen',
    f'{NS}:scorchfell', f'{NS}:silverbark_wood', f'{NS}:starved_reach',
    f'{NS}:sundered_highlands', f'{NS}:alfheim_ocean', f'{NS}:void_verge',
    f'{NS}:shatterfields', f'{NS}:prism_drift', f'{NS}:rootfall',
    f'{NS}:sepulchral_reach', f'{NS}:starless_reach',
    'mythicbotany:alfheim_hills', 'mythicbotany:alfheim_lakes',
    'mythicbotany:alfheim_plains', 'mythicbotany:dreamwood_forest',
    'mythicbotany:golden_fields',
]

# --- dimensions ---------------------------------------------------------------------------
BASE = 48
TRUNK_W, TRUNK_H = 32, 24
CROWN_W, CROWN_H = 48, 40
AMPH_W, AMPH_H = 48, 12
# Sink the root plate twenty blocks into the sampled terrain.  The gate/court floor
# is raised by the same amount inside the base piece, so the playable route remains
# on the heightmap while roots and masonry have real buried support below it.
ROOT_EMBED = 20

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
ELDER_BARK = (f'{NS}:gloambark_log', None)
ELDER_HEARTWOOD = (f'{NS}:hushbark_log', None)
AIR = ('minecraft:air', None)
LEAVES = (f'{NS}:gloambark_leaves', None)

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

# Royal Tile Set I / Wave A. These blocks are intentionally used in the worldgen templates,
# not left isolated in a review grid: the three court wings need to read as inhabited royal
# architecture at player scale as well as marble masses from a distance.
ROYAL_CHAIR = ('alfheim:royal_highback_chair', {'facing': 'north'})
ROYAL_SCONCE_N = ('alfheim:royal_wall_sconce', {'facing': 'north'})
ROYAL_SCONCE_S = ('alfheim:royal_wall_sconce', {'facing': 'south'})
ROYAL_SCONCE_E = ('alfheim:royal_wall_sconce', {'facing': 'east'})
ROYAL_SCONCE_W = ('alfheim:royal_wall_sconce', {'facing': 'west'})
ROYAL_RUNNER_EW = ('alfheim:royal_carpet_runner', {'facing': 'east'})
ROYAL_RUNNER_NS = ('alfheim:royal_carpet_runner', {'facing': 'north'})
ROYAL_BALUSTRADE_N = ('alfheim:royal_balustrade', {'facing': 'north'})
ROYAL_BALUSTRADE_E = ('alfheim:royal_balustrade', {'facing': 'east'})
ROYAL_AMPHORA = ('alfheim:royal_lidded_amphora', {'facing': 'north'})
ROYAL_BANNER_N = ('alfheim:royal_wall_banner', {'facing': 'north'})
ROYAL_BANNER_S = ('alfheim:royal_wall_banner', {'facing': 'south'})
ROYAL_BANNER_E = ('alfheim:royal_wall_banner', {'facing': 'east'})
ROYAL_BANNER_W = ('alfheim:royal_wall_banner', {'facing': 'west'})
QUARTZ_SLAB = ('minecraft:quartz_slab', {'type': 'bottom', 'waterlogged': 'false'})
DREAMWOOD = ('botania:dreamwood_planks', None)
LIVINGROCK = ('botania:livingrock_bricks', None)
ELF_GLASS = ('botania:elf_glass', None)


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


# --- support tests ----------------------------------------------------------------------------
# Dressing loops compute where a block *should* sit from the same formula that drew the tiers,
# then place it whether or not the tier survived. Two things defeat that: the tier collapse
# roll leaves gaps, and the processional aisles are cut through the seating afterwards. Both
# leave the decoration hanging in mid-air -- reported from the field 2026-09-07 as "noise
# detail blocks hovering in the central pathway of the main dais". Every scatter below now
# asks the piece what is actually there.

def solid_at(p, x, y, z):
    """True when the piece places a real, non-air block at this position.

    Absent means the structure does not own the position at all -- `place template` leaves
    whatever terrain is there, which is not something decoration may stand on either.
    """
    entry = p.blocks.get((x, y, z))
    if entry is None:
        return False
    return p.palette[entry[0]].get('Name') != 'minecraft:air'


def supported(p, x, y, z):
    """True when something solid sits directly beneath this position."""
    return solid_at(p, x, y - 1, z)


VINE_NEIGHBOUR = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}


def set_vine(p, x, y, z, face):
    """Place a vine only when the block it claims to cling to is really there."""
    dx, dz = VINE_NEIGHBOUR[face]
    if not solid_at(p, x + dx, y, z + dz):
        return False
    return p.set(x, y, z, vine(face))


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


def box(p, x0, y0, z0, x1, y1, z1, block):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                p.set(x, y, z, block)


def trunk_column(p, cx, cz, h, r0, r1, rng, roots=False):
    """Fill the trunk mass. Gloambark wraps a Hushbark heartwood core -- the bark reads on
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
                    p.set(x, y, z, ELDER_BARK if d > rr - 1.6 else ELDER_HEARTWOOD)


def major_roots(p, cx, cz, rng):
    """Eight long, descending root buttresses that visibly enter the surrounding terrain."""
    for k in range(8):
        angle = k * math.tau / 8.0 + rng.uniform(-0.10, 0.10)
        for distance in range(8, 31):
            x = int(round(cx + math.cos(angle) * distance))
            z = int(round(cz + math.sin(angle) * distance))
            if not (1 <= x < p.size[0] - 1 and 1 <= z < p.size[2] - 1):
                continue
            y = max(1, ROOT_EMBED + 7 - int((distance - 8) * 0.58))
            radius = 3 if distance < 15 else (2 if distance < 23 else 1)
            for ox in range(-radius, radius + 1):
                for oz in range(-radius, radius + 1):
                    if ox * ox + oz * oz > radius * radius + 1:
                        continue
                    for oy in range(-1, 2):
                        xx, yy, zz = x + ox, y + oy, z + oz
                        if 0 <= xx < p.size[0] and 0 <= yy < p.size[1] and 0 <= zz < p.size[2]:
                            p.set(xx, yy, zz, ELDER_BARK if abs(oy) == 1 else ELDER_HEARTWOOD)


def carve_gate_chamber(p, cx, cz, ground=ROOT_EMBED):
    """Hollow the chamber out of the north flank and build the gate into its back wall.

    Cut first, then build: the frame has to survive the carve, so nothing is placed until the
    air is in.
    """
    # --- the void
    for y in range(ground + 1, ground + CH_TOP):
        for x in range(cx - CH_HALF, cx + CH_HALF + 1):
            for z in range(0, CH_BACK + 1):
                # An arched ceiling rather than a flat one.
                arch = ground + CH_TOP - abs(x - cx) * 0.45
                if y < arch:
                    p.set(x, y, z, AIR)

    # --- floor
    for x in range(cx - CH_HALF - 1, cx + CH_HALF + 2):
        for z in range(0, CH_BACK + 2):
            p.set(x, ground, z, FLOOR)

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
    for y in range(ground + 2, ground + 2 + GATE_H):
        for x in range(gx0, gx1 + 1):
            p.set(x, y, CH_BACK, AIR)      # the opening you look through
            p.set(x, y, gate_z, GATE)      # the surface itself, set back behind the frame

    # --- the frame around it: livingrock with chiseled quartz corners and gold at the keystone
    for y in range(ground + 1, ground + 3 + GATE_H):
        for x in range(gx0 - 2, gx1 + 3):
            on_edge = (x < gx0 or x > gx1 or y < ground + 2 or y >= ground + 2 + GATE_H)
            if not on_edge:
                continue
            corner = (x in (gx0 - 2, gx0 - 1, gx1 + 1, gx1 + 2) and
                      y in (ground + 1, ground + 2 + GATE_H - 1, ground + 2 + GATE_H))
            p.set(x, y, CH_BACK, FRAME_TRIM if corner else FRAME)
    p.set(cx, ground + 2 + GATE_H, CH_BACK, GOLD)
    p.set(cx - 1, ground + 2 + GATE_H, CH_BACK, GOLD)

    # --- elf glass in the arch above the gate, so the chamber is lit without a torch
    for x in range(gx0, gx1 + 1):
        p.set(x, ground + 2 + GATE_H + 1, CH_BACK, GLASS)


def hub_anchor(c):
    """The world spawn, baked into the gate chamber as a marker entity.

    This is the fix for "we didn't spawn inside it". The previous scheme summoned a marker at
    0 250 0 and let spreadplayers drop it, which anchors the world spawn to the ORIGIN -- and
    the origin is not the tree (see HUB_MIN_X). A marker carried inside the structure's own
    NBT lands wherever the structure lands, so the anchor cannot desynchronise from the tree no
    matter what the biome search does. Same reason the court is baked in rather than summoned.

    Standing on the chamber floor, four blocks in front of the gate, facing it. Rotation yaw 0
    is south (+z) and the gate is at the +z back wall, so a player spawning here looks straight
    at it.
    """
    x, y, z = c, ROOT_EMBED + 1, CH_BACK - 4
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
    major_roots(p, c, c, rng)
    carve_gate_chamber(p, c, c)
    p.entities.append(hub_anchor(c))

    # Up to the first trunk segment. The trunk pool holds only `trunk`, so the segment directly
    # above the base is never the crown -- a tree with no trunk would still be a legal assembly.
    p.jigsaw(c, BASE - 1, c, f'{NS}:bole_top', f'{NS}:trunk_bottom',
             f'{NS}:greatbole/trunk', 'up_north')

    # Out to the amphitheatre, at the chamber mouth, facing north. `aligned` rather than
    # `rollable`: the court has to sit squarely in front of the gate, not at 90 degrees to it.
    p.jigsaw(c, ROOT_EMBED + 1, 0, f'{NS}:court_gate', f'{NS}:court_plug',
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
                    p.set(int(bx) + ox, int(by), int(bz) + oz, ELDER_HEARTWOOD)

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
    # LEGACY SKIN SLOTS. These values stay in the structure until the queued dedicated
    # court-NPC model/texture pass replaces the fragile global wood-elf slot override. There is
    # deliberately no runtime handler policing natural elves out of slots 5 and 6.
    for i, n in enumerate(man['named']):
        posts.append((n['name'], c + (-5 if i % 2 else 5), ground, c + 6, 5 + i))
    # Ambient court scattered up the tiers, on their own seats.
    #
    # The arc runs across the northern tiers, which is exactly where the north approach is now
    # cut. A post left inside an aisle gets a seat block built under it by build_amphitheatre,
    # and that block lands in mid-air over the carved route -- one of the hovering blocks
    # reported 2026-09-07. Nudge each post clear of every aisle first, then derive its tier
    # height from where it actually ended up.
    for i, n in enumerate(man['ambient']):
        ang = math.pi * (0.15 + 0.7 * (i / max(1, len(man['ambient']) - 1)))
        r = 12.0 + (i % 3) * 3.5
        x, z = int(c - math.cos(ang) * r), int(c - math.sin(ang) * r)
        x, z = clear_of_aisles(x, z)
        seat_r = math.hypot(x - c, z - c)
        # Ambient court draw from the four unreserved slots, so the crowd is varied without
        # any of them wearing the named pair's art.
        posts.append((n['name'], x, ground + int(max(0.0, seat_r - 8.0) / 3.5), z, 1 + (i % 4)))

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
                'Tags': ['alfheim_hub_court'],
                'CustomNameVisible': nbt.Byte(1),
                'CustomName': json.dumps({'text': name}),
            },
        })
    return out, posts


# --- the court's four approaches ---------------------------------------------------------------
# One entry per neighbouring piece, as (name, axis, first, last). `axis` is the direction the
# aisle runs; the other horizontal axis is always the seven-wide clear span centred on the piece
# centre, matching the nine-wide spine the wings drive at the same elevation. The spans stop one
# block short of the stage rim so the seating still closes the circle around the stage itself.
AISLE_HALF = 3                      # 7 wide clear: c-3 .. c+3
AISLES = (
    ('south', 'z', 31, 47),         # the Greatbole gate
    ('north', 'z', 0, 17),          # court/north_council
    ('west', 'x', 0, 17),           # court/west_residence
    ('east', 'x', 31, 47),          # court/east_service
)


AISLE_KEEPOUT = AISLE_HALF + 2      # clear span plus both retaining cheeks


def clear_of_aisles(x, z):
    """Push a point sideways out of any aisle it landed in, to the nearer flank."""
    c = AMPH_W // 2
    for _name, axis, first, last in AISLES:
        run, cross = (x, z) if axis == 'x' else (z, x)
        if not (first <= run <= last) or abs(cross - c) > AISLE_KEEPOUT:
            continue
        cross = c - AISLE_KEEPOUT - 1 if cross <= c else c + AISLE_KEEPOUT + 1
        x, z = (run, cross) if axis == 'x' else (cross, run)
    return x, z


def aisle_cells(spec):
    """Every (x, z) in one aisle's clear span, plus its two retaining cheeks."""
    _name, axis, first, last = spec
    c = AMPH_W // 2
    for run in range(first, last + 1):
        clear = [((run, cross) if axis == 'x' else (cross, run))
                 for cross in range(c - AISLE_HALF, c + AISLE_HALF + 1)]
        cheeks = [((run, cross) if axis == 'x' else (cross, run))
                  for cross in (c - AISLE_HALF - 1, c + AISLE_HALF + 1)]
        yield run, clear, cheeks


def aisle_paving(p, rng, c, ground, spec):
    """Lay one aisle's floor and its broken retaining cheeks."""
    walk_y = ground - 1
    for run, clear, cheeks in aisle_cells(spec):
        for x, z in clear:
            paving = ELVEN_MARBLE if (x + z) % 5 else rng.choice(MARBLE_RUINED)
            p.set(x, walk_y, z, paving)
        # Broken retaining cheeks make each cut read as authored circulation rather
        # than seven missing columns through the seating.
        if run % 4 != 0:
            for x, z in cheeks:
                p.set(x, walk_y, z, rng.choice(MARBLE_RUINED))


def aisle_clear(p, ground):
    """Last writer wins: reopen every approach after the dressing passes have run.

    courtyard_detail scatters rubble, moss and fallen drums at computed tier heights, and the
    column rings stand wherever the ring formula puts them. Both can land inside a carved
    aisle. Clearing here, after all of it, is what guarantees the four routes are walkable --
    the same discipline build_royal_annex already applies to its own spine.
    """
    walk_y = ground - 1
    for spec in AISLES:
        for _run, clear, _cheeks in aisle_cells(spec):
            for x, z in clear:
                for y in range(walk_y + 1, AMPH_H):
                    p.set(x, y, z, AIR)


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
            # Gone. Leave the drum it fell as, lying where it landed -- but only on ground
            # that is actually there, so a fallen column cannot bridge the carved aisle.
            ox, oz = int(math.cos(ang) * 2), int(math.sin(ang) * 2)
            axis = COLUMN_FALLEN_X if abs(ox) >= abs(oz) else COLUMN_FALLEN_Z
            for t in range(rng.randint(2, 4)):
                dx = px + ox + (t if axis is COLUMN_FALLEN_X else 0)
                dz = pz + oz + (0 if axis is COLUMN_FALLEN_X else t)
                if supported(p, dx, ground, dz):
                    p.set(dx, ground, dz, axis)
            continue
        h = rng.randint(2, 4) if fate < 0.55 else rng.randint(5, 7)
        base_y = ground
        if not supported(p, px, base_y, pz):
            continue
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
                set_vine(p, vx, y, pz, face)

    # --- vines on the rim stumps and the top tier --------------------------------------------
    for k in range(24):
        ang = k * math.tau / 24
        d = outer_r - rng.uniform(0.5, 3.0)
        vx, vz = int(c + math.cos(ang) * d), int(c + math.sin(ang) * d)
        face = 'west' if math.cos(ang) > 0 else 'east'
        y = ground + int((d - stage_r) / 3.5)
        if rng.random() < 0.5 and y < top:
            set_vine(p, vx + (1 if face == 'west' else -1), y, vz, face)

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
        if r < 0.86:
            # Rubble, carpet and moss all need a floor. `y` is the tier height this position
            # *would* have if its tier survived the collapse roll and if no aisle were cut
            # through it; neither is guaranteed, so ask before placing.
            if r < 0.42:
                if supported(p, x, y, z):
                    p.set(x, y, z, rng.choice(RUBBLE))
            elif r < 0.72:
                if supported(p, x, y, z):
                    p.set(x, y, z, MOSS_CARPET)
            elif solid_at(p, x, y - 1, z):
                # Moss replaces the top course of an existing tier rather than adding to it.
                p.set(x, y - 1, z, MOSS)
        elif supported(p, x, y, z):
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

    # Four broad processional aisles enter the court on the same elevation as the Greatbole
    # gate, one per neighbouring piece: south to the Greatbole itself, and north, west and east
    # to the three civic wings. Each is carved after the seating so the route cannot be closed
    # by a surviving tier.
    #
    # The three wing aisles were missing entirely until 2026-09-07. The wings tile flush against
    # this piece and each drives a nine-wide spine at exactly this elevation, but the spines
    # terminated against the intact outer seating bank -- a five-to-six block wall of marble
    # with a two-block void at the seam. Reported from the field as the wings "not properly
    # connecting to the central area". AISLES is now the single authority for where the court
    # opens, and check_spawn_hub asserts all four are clear.
    for spec in AISLES:
        aisle_paving(p, rng, c, ground, spec)

    # Column stumps around the rim, broken to differing heights. A stump whose tier collapsed
    # or was cut away by an approach has nothing to stand on, so it is simply not raised.
    for k in range(12):
        ang = k * math.pi / 6
        cxp, czp = int(c + math.cos(ang) * (outer_r - 1.5)), int(c + math.sin(ang) * (outer_r - 1.5))
        h = rng.choice([1, 2, 2, 3, 5, 7])
        base_y = ground + int((outer_r - 1.5 - stage_r) / 3.5)
        if not supported(p, cxp, base_y, czp):
            continue
        for y in range(h):
            p.set(cxp, base_y + y, czp, COLUMN)

    courtyard_detail(p, c, ground, stage_r, outer_r, rng)

    # Reopen the four approaches last, before the court and the jigsaw are seated -- both of
    # those sit inside the south aisle and must survive.
    aisle_clear(p, ground)

    # The court itself, seated in the structure rather than summoned at the player.
    ents, posts = court_entities(c, ground)
    p.entities = ents
    for _, x, y, z, _skin in posts:               # a clear seat under each, so none is buried
        # Build the seat down to the tier base course rather than laying one block at the
        # computed tier height: where the collapse roll removed that tier, a single block
        # would hang in the air with the elf standing on nothing.
        for sy in range(ground - 1, y):
            p.set(x, sy, z, ELVEN_MARBLE)
        for dy in range(3):
            if (x, y + dy, z) in p.blocks and dy > 0:
                del p.blocks[(x, y + dy, z)]
        p.set(x, y, z, AIR)
        p.set(x, y + 1, z, AIR)

    # The plug, facing south back at the tree.
    p.jigsaw(c, ground, AMPH_W - 1, f'{NS}:court_plug', f'{NS}:court_gate',
             'minecraft:empty', 'south_up', joint='aligned')
    return p


COURT_FLOOR_Y = 5


def royal(name, facing='north'):
    return (f'alfheim:{name}', {'facing': facing})


def court_foundation(p, rng):
    """A stepped, buried terrain interface rather than one square floating slab.

    The hub is assembled with `/place template`, so the parent jigsaw's `beard_thin` processor
    cannot be trusted to grow support under these separately placed wings. Their own bottom five
    courses therefore form a visible beard: a clipped-corner terrace, continuous retaining
    walls, deep piers and two lower talus steps. The top course remains at the amphitheatre's
    world-space floor datum.
    """
    fy = COURT_FLOOR_Y

    def in_terrace(x, z):
        if not (2 <= x <= 45 and 2 <= z <= 45):
            return False
        # Clip the corners so the silhouette follows terrain instead of exposing a 48x48 plate.
        return min(x + z, x + 47 - z, 47 - x + z, 94 - x - z) >= 7

    for x in range(48):
        for z in range(48):
            if not in_terrace(x, z):
                continue
            edge = not all(in_terrace(nx, nz) for nx, nz in
                           ((x - 1, z), (x + 1, z), (x, z - 1), (x, z + 1)))
            top = ELVEN_MARBLE if (x + z) % 9 == 0 else rng.choice(MARBLE)
            p.set(x, fy, z, top)
            p.set(x, fy - 1, z, rng.choice(MARBLE_RUINED))
            if edge or (x % 8 in (0, 1) and z % 8 in (0, 1)):
                for y in range(fy - 3, fy - 1):
                    p.set(x, y, z, rng.choice(MARBLE_RUINED))
            if edge:
                for y in range(0, fy - 3):
                    p.set(x, y, z, rng.choice(MARBLE_RUINED))

    # Lower courses flare out in irregular runs. From a valley or cliff side these read as
    # masonry sunk into the slope; from above they read as old collapsed terrace aprons.
    for edge in ('north', 'south', 'west', 'east'):
        for u in range(7, 42):
            if (u * 7 + len(edge)) % 11 == 0:
                continue
            for step, level in ((1, fy - 2), (0, fy - 3)):
                x, z = ((u, step) if edge == 'north' else
                        (u, 47 - step) if edge == 'south' else
                        (step, u) if edge == 'west' else (47 - step, u))
                for y in range(0, level + 1):
                    p.set(x, y, z, rng.choice(MARBLE_RUINED))

    # Heavy buttresses continue all the way to the template bottom, so the support language is
    # legible even where the surrounding terrain drops by several blocks.
    for u in (9, 16, 24, 32, 39):
        for x, z, dx, dz in ((u, 2, 0, -1), (u, 45, 0, 1),
                             (2, u, -1, 0), (45, u, 1, 0)):
            for reach in range(3):
                h = fy - reach
                for y in range(0, h + 1):
                    p.set(x + dx * reach, y, z + dz * reach,
                          COLUMN if reach == 0 and y >= 2 else rng.choice(MARBLE_RUINED))


def court_room(p, rng, x0, z0, x1, z1, doors=(), windows=()):
    """Build one ruined but readable palace room with layered walls and a broken cornice."""
    fy = COURT_FLOOR_Y
    # Explicitly clear the occupied volume. The hub's one shared height datum can put an annex
    # against a rising slope; omitted template positions preserve that terrain and previously
    # left the nominal rooms packed solid with hillside. Retaining walls hold the cut outside.
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            for y in range(fy + 1, 15):
                p.set(x, y, z, AIR)
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            p.set(x, fy, z, ELVEN_MARBLE if (x + z) % 7 == 0 else rng.choice(MARBLE))
    for y in range(fy + 1, fy + 7):
        for x in range(x0, x1 + 1):
            for z in (z0, z1):
                p.set(x, y, z, LIVINGROCK if (x + y) % 6 else rng.choice(MARBLE_RUINED))
        for z in range(z0 + 1, z1):
            for x in (x0, x1):
                p.set(x, y, z, LIVINGROCK if (z + y) % 6 else rng.choice(MARBLE_RUINED))

    # Pilasters, capitals and a partly collapsed double cornice give every room façade depth.
    pilasters = {(x0, z0), (x1, z0), (x0, z1), (x1, z1),
                 ((x0 + x1) // 2, z0), ((x0 + x1) // 2, z1)}
    for x, z in pilasters:
        for y in range(fy + 1, fy + 8):
            p.set(x, y, z, COLUMN)
        p.set(x, fy + 8, z, CAPITAL)
    for x in range(x0, x1 + 1):
        for z in (z0, z1):
            if (x * 3 + z) % 7 not in (0, 1):
                p.set(x, fy + 8, z, CAPITAL if x % 4 == 0 else QUARTZ_SLAB)
    for z in range(z0 + 1, z1):
        for x in (x0, x1):
            if (x + z * 3) % 7 not in (0, 1):
                p.set(x, fy + 8, z, QUARTZ_SLAB)

    # Surviving roof skirts create a layered skyline but leave most of each ruined room open.
    for x in range(x0 + 1, x1):
        for z in (z0 + 1, z0 + 2, z1 - 2):
            if (x * 5 + z) % 9 not in (0, 1):
                p.set(x, fy + 9, z, QUARTZ_SLAB)

    # Openings are explicit after wall construction. `windows` entries are (axis, fixed, span).
    for axis, fixed, a, b in windows:
        for q in range(a, b + 1):
            for y in range(fy + 3, fy + 6):
                x, z = (q, fixed) if axis == 'x' else (fixed, q)
                p.set(x, y, z, ELF_GLASS)
    for axis, fixed, centre in doors:
        for q in range(centre - 1, centre + 2):
            for y in range(fy + 1, fy + 5):
                x, z = (q, fixed) if axis == 'x' else (fixed, q)
                p.set(x, y, z, AIR)


def place_canopy_bed(p, x, z, facing='north'):
    names = (('royal_canopy_bed_head_left', 'royal_canopy_bed_head_right'),
             ('royal_canopy_bed_middle_left', 'royal_canopy_bed_middle_right'),
             ('royal_canopy_bed_foot_left', 'royal_canopy_bed_foot_right'))
    for dz, row in enumerate(names):
        for dx, name in enumerate(row):
            p.set(x + dx, COURT_FLOOR_Y + 1, z + dz, royal(name, facing))


def place_astrolabe(p, x, z):
    for dz, row in enumerate((('royal_astrolabe_nw', 'royal_astrolabe_ne'),
                              ('royal_astrolabe_sw', 'royal_astrolabe_se'))):
        for dx, name in enumerate(row):
            p.set(x + dx, COURT_FLOOR_Y + 1, z + dz, royal(name))


def dress_west_residence(p, rng):
    fy = COURT_FLOOR_Y
    rooms = ((5, 5, 20, 18), (27, 5, 42, 18),
             (5, 29, 20, 42), (27, 29, 42, 42))
    for i, rect in enumerate(rooms):
        x0, z0, x1, z1 = rect
        door_z = z1 if i < 2 else z0
        court_room(p, rng, *rect, doors=(('x', door_z, (x0 + x1) // 2),),
                   windows=(('x', z0 if i < 2 else z1, x0 + 4, x0 + 6),))

    # Two private suites, a salon and a dining/library room.
    place_canopy_bed(p, 8, 8)
    place_canopy_bed(p, 8, 36, 'south')
    for x, z, facing in ((31, 9, 'south'), (35, 9, 'south'), (31, 15, 'north'),
                         (35, 15, 'north'), (31, 34, 'south'), (35, 34, 'south')):
        p.set(x, fy + 1, z, royal('royal_highback_chair', facing))
    box(p, 32, fy + 1, 11, 34, fy + 1, 13, DREAMWOOD)
    box(p, 31, fy + 1, 37, 38, fy + 2, 38, ('minecraft:bookshelf', None))
    for x, z in ((7, 7), (18, 7), (7, 40), (18, 40), (29, 31), (40, 31)):
        p.set(x, fy + 1, z, ROYAL_AMPHORA)
    for x, z, block in ((12, 18, ROYAL_SCONCE_S), (34, 18, ROYAL_SCONCE_S),
                        (12, 29, ROYAL_SCONCE_N), (34, 29, ROYAL_SCONCE_N)):
        p.set(x, fy + 4, z, block)
    for x, z, block in ((16, 5, ROYAL_BANNER_N), (38, 5, ROYAL_BANNER_N),
                        (16, 42, ROYAL_BANNER_S), (38, 42, ROYAL_BANNER_S)):
        p.set(x, fy + 4, z, block)


def dress_east_service(p, rng):
    fy = COURT_FLOOR_Y
    rooms = ((5, 5, 20, 18), (27, 5, 42, 18),
             (5, 29, 20, 42), (27, 29, 42, 42))
    for i, rect in enumerate(rooms):
        x0, z0, x1, z1 = rect
        door_z = z1 if i < 2 else z0
        court_room(p, rng, *rect, doors=(('x', door_z, (x0 + x1) // 2),),
                   windows=(('x', z0 if i < 2 else z1, x0 + 4, x0 + 6),))

    # Kitchen, stillroom, stores and the steward's work room. Dense repetition is deliberate:
    # service architecture should feel busy and useful rather than ceremonially empty.
    for x in (7, 10, 13, 16):
        p.set(x, fy + 1, 7, ('minecraft:smoker' if x % 2 else 'minecraft:furnace', None))
        p.set(x, fy + 1, 16, ('minecraft:cauldron', None))
    box(p, 29, fy + 1, 7, 40, fy + 1, 8, ('minecraft:barrel', None))
    box(p, 7, fy + 1, 31, 18, fy + 2, 32, ('minecraft:bookshelf', None))
    for x, z, name in ((30, 32, 'minecraft:crafting_table'),
                       (34, 32, 'minecraft:cartography_table'),
                       (38, 32, 'minecraft:brewing_stand'),
                       (30, 39, 'minecraft:barrel'), (34, 39, 'minecraft:barrel'),
                       (38, 39, 'minecraft:barrel')):
        p.set(x, fy + 1, z, (name, None))
    for x, z in ((7, 16), (19, 16), (28, 7), (41, 7), (7, 40), (19, 40)):
        p.set(x, fy + 1, z, ROYAL_AMPHORA)
    for x, z, block in ((12, 18, ROYAL_SCONCE_S), (34, 18, ROYAL_SCONCE_S),
                        (12, 29, ROYAL_SCONCE_N), (34, 29, ROYAL_SCONCE_N)):
        p.set(x, fy + 4, z, block)


def dress_north_council(p, rng):
    fy = COURT_FLOOR_Y
    # A single transverse council hall at the far end, with two archive chambers flanking the
    # processional approach. It no longer shares the residence's four-room plan.
    court_room(p, rng, 6, 5, 41, 21,
               doors=(('x', 21, 24),), windows=(('x', 5, 11, 14), ('x', 5, 33, 36)))
    court_room(p, rng, 5, 28, 19, 42,
               doors=(('z', 19, 35),), windows=(('z', 5, 32, 35),))
    court_room(p, rng, 29, 28, 43, 42,
               doors=(('z', 29, 35),), windows=(('z', 43, 32, 35),))

    # Raised dais, councillors, central astrolabe and paired record rooms.
    box(p, 15, fy + 1, 8, 33, fy + 1, 14, ELVEN_MARBLE)
    box(p, 19, fy + 2, 9, 29, fy + 2, 12, CAPITAL)
    place_astrolabe(p, 23, 15)
    for x in (17, 21, 27, 31):
        p.set(x, fy + 2, 11, royal('royal_highback_chair', 'south'))
    for x in (12, 16, 32, 36):
        p.set(x, fy + 1, 18, royal('royal_highback_chair', 'north'))
    for x in list(range(16, 21)) + list(range(28, 33)):
        p.set(x, fy + 2, 14, ROYAL_BALUSTRADE_N)
    for z in range(30, 41, 3):
        p.set(7, fy + 1, z, ('minecraft:bookshelf', None))
        p.set(17, fy + 1, z, ('minecraft:bookshelf', None))
        p.set(31, fy + 1, z, ('minecraft:bookshelf', None))
        p.set(41, fy + 1, z, ('minecraft:bookshelf', None))
    p.set(9, fy + 1, 40, ('minecraft:lectern', None))
    p.set(39, fy + 1, 40, ('minecraft:cartography_table', None))
    for x, z in ((8, 7), (40, 7), (7, 26), (41, 26),
                 (7, 40), (41, 40)):
        p.set(x, fy + 1, z, ROYAL_AMPHORA)
    for x in (10, 24, 38):
        p.set(x, fy + 5, 21, ROYAL_BANNER_S)
        p.set(x, fy + 4, 5, ROYAL_SCONCE_N)


def build_royal_annex(rng, role):
    """One high-detail civic wing of the ruined palace surrounding the Hollow Court."""
    p = Piece(48, 16, 48)
    c = 24
    fy = COURT_FLOOR_Y
    court_foundation(p, rng)

    # A continuous processional spine aligns with the central court at the same world Y. The
    # custom runner provides close-range detail while the elven-quartz margins carry the route
    # at long range.
    if role == 'north_council':
        box(p, c - 4, fy, 0, c + 4, fy, 47, ELVEN_MARBLE)
        for z in range(1, 47):
            p.set(c, fy + 1, z, ROYAL_RUNNER_NS)
        dress_north_council(p, rng)
    elif role == 'west_residence':
        box(p, 0, fy, c - 4, 47, fy, c + 4, ELVEN_MARBLE)
        for x in range(1, 47):
            p.set(x, fy + 1, c, ROYAL_RUNNER_EW)
        dress_west_residence(p, rng)
    elif role == 'east_service':
        box(p, 0, fy, c - 4, 47, fy, c + 4, ELVEN_MARBLE)
        for x in range(1, 47):
            p.set(x, fy + 1, c, ROYAL_RUNNER_EW)
        dress_east_service(p, rng)
    else:
        raise ValueError(f'unknown court annex role: {role}')

    # Court-facing entrance loggias frame the route without blocking the 9-wide opening.
    if role == 'north_council':
        edge_posts = ((18, 45), (30, 45))
        for x in range(19, 30):
            p.set(x, fy + 1, 45, ROYAL_BALUSTRADE_N if x not in range(21, 28) else AIR)
    else:
        ex = 45 if role == 'west_residence' else 2
        edge_posts = ((ex, 18), (ex, 30))
        for z in list(range(14, 19)) + list(range(30, 35)):
            p.set(ex, fy + 1, z, ROYAL_BALUSTRADE_E)
    for x, z in edge_posts:
        for y in range(fy + 1, fy + 9):
            p.set(x, y, z, COLUMN)
        p.set(x, fy + 9, z, CAPITAL)

    # Greatbole roots bind the inner palace edge. They stop outside the clear processional
    # route and descend into the new foundation beard rather than lying on top of the paving.
    root_edge = 45 if role in ('north_council', 'west_residence') else 2
    for offset in (-13, 12):
        for step in range(11):
            if role == 'north_council':
                x, z = c + offset // 3, root_edge - step
            else:
                x = root_edge - step if role == 'west_residence' else root_edge + step
                z = c + offset
            y = fy + max(0, 3 - step // 3)
            for w in (-1, 0, 1):
                xx, zz = (x + w, z) if role == 'north_council' else (x, z + w)
                p.set(xx, y, zz, ELDER_HEARTWOOD)

    # Causal decay is concentrated along one outer corner per wing. The rooms, doors and route
    # remain legible; rubble is evidence of that local collapse rather than uniform noise.
    collapse = ((7, 8) if role == 'west_residence' else
                (40, 8) if role == 'east_service' else (39, 9))
    cx, cz = collapse
    for radius in range(1, 6):
        for _ in range(5):
            x = max(1, min(46, cx + rng.randint(-radius, radius)))
            z = max(1, min(46, cz + rng.randint(-radius, radius)))
            # Debris piles two deep near the collapse centre, but only where the first course
            # actually landed -- otherwise the upper block hangs over the floor it never hit.
            y = fy + 1
            if radius < 3 and rng.random() < 0.35 and solid_at(p, x, y, z):
                y += 1
            p.set(x, y, z, rng.choice(RUBBLE))
    for x, z in ((4, 12), (43, 15), (8, 45), (39, 44)):
        p.set(x, fy + 1, z, MOSS_CARPET)

    # Last writer wins: guarantee the nine-wide spine remains navigable after roots, furniture
    # and collapse dressing. Carpet occupies y+1, so clearance starts above it.
    if role == 'north_council':
        for z in range(48):
            for x in range(c - 3, c + 4):
                for y in range(fy + 2, 16):
                    p.set(x, y, z, AIR)
    else:
        for x in range(48):
            for z in range(c - 3, c + 4):
                for y in range(fy + 2, 16):
                    p.set(x, y, z, AIR)
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
        'court/west_residence': build_royal_annex(rng, 'west_residence'),
        'court/east_service': build_royal_annex(rng, 'east_service'),
        'court/north_council': build_royal_annex(rng, 'north_council'),
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
        'start_height': {'absolute': -ROOT_EMBED},
        'project_start_to_heightmap': 'WORLD_SURFACE_WG',
        'use_expansion_hack': False,
        'spawn_overrides': {},
    }, dry)

    # --- placement is explicit and idempotent -----------------------------------------------
    # New World Gamma proved that passively waiting for a concentric-ring structure is not a
    # spawn system: the forced search area remained empty for twenty minutes.  hub/place now
    # owns the single placement and verifies the baked marker.  Remove the obsolete natural
    # structure set so later chunk generation can never add a second Greatbole.
    obsolete = os.path.join(DATA, 'worldgen', 'structure_set', 'greatbole.json')
    if not dry and os.path.exists(obsolete):
        os.remove(obsolete)

    # `/place structure` still evaluates the structure's biome holder set.  The placement probe
    # already rejects water, fire and missing ground, so the tag must cover the complete layer;
    # restricting it here would turn an otherwise safe probe into another silent placement miss.
    write_json(os.path.join(DATA, 'tags', 'worldgen', 'biome', 'has_greatbole.json'),
               {'replace': False, 'values': LAYER_BIOMES}, dry)

    if not dry:
        with open(os.path.join('kubejs', 'server_scripts', '04_spawn_hub.js'),
                  'w', encoding='utf-8') as f:
            f.write(protection_script())
    print(f'  protection            kubejs/server_scripts/04_spawn_hub.js  '
          f'X {HUB_MIN_X}..{HUB_MAX_X}, Z {HUB_MIN_Z}..{HUB_MAX_Z}, {HOME}')

    total = sum(len(p.blocks) for p in pieces.values())
    print(f'\n  {len(pieces)} pieces, {total} blocks, tree {ASSEMBLED_HEIGHT} blocks tall '
          f'(base + {TRUNK_SEGMENTS} trunk + crown), placement radius {MAX_FROM_CENTER}')
    return 0


def protection_script():
    """Render the checked-in API implementation; the generator owns only stable constants."""
    template = os.path.join('tools', 'templates', 'spawn_hub_protection.js')
    text = open(template, encoding='utf-8').read()
    text = text.replace('__HOME_DIMENSION__', HOME)
    for token, value in (('__HUB_MIN_X__', HUB_MIN_X), ('__HUB_MAX_X__', HUB_MAX_X),
                         ('__HUB_MIN_Z__', HUB_MIN_Z), ('__HUB_MAX_Z__', HUB_MAX_Z)):
        text = text.replace(token, str(value))
    return text


if __name__ == '__main__':
    raise SystemExit(main())
