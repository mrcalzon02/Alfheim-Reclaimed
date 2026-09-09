"""Generate three gigantic Deepworks archaeology complexes.

Each registered structure is a deterministic nine-piece jigsaw assembly: a 47-block centre,
four 33-block approaches and four 47-block wings. Rotating the north-authored approach and wing
onto four centre sockets produces a roughly 207x207-block destination while keeping every NBT
piece under Minecraft's 48-block structure-block editing limit.
"""
import argparse
import hashlib
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402
import structure_detail as sd  # noqa: E402
from structure_nbt import MAX_AXIS, Piece  # noqa: E402

NS = "alfheim"
DATA = os.path.join("kubejs", "data", NS)
STRUCT = os.path.join(DATA, "structures", "deepworks_archaeology")
MANIFEST = os.path.join("tools", "deep_archaeology_manifest.json")
AIR = ("minecraft:air", None)


def B(name, **props):
    return (name, {k: str(v).lower() if isinstance(v, bool) else str(v)
                   for k, v in props.items()} or None)


def box(p, x0, y0, z0, x1, y1, z1, block):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                p.set(x, y, z, block)


def hollow(p, x0, y0, z0, x1, y1, z1, wall, inside=AIR):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                edge = x in (x0, x1) or y in (y0, y1) or z in (z0, z1)
                p.set(x, y, z, wall if edge else inside)


def ring(p, cx, cz, y, radius, width, block):
    for x in range(max(0, cx - radius - 1), min(p.size[0], cx + radius + 2)):
        for z in range(max(0, cz - radius - 1), min(p.size[2], cz + radius + 2)):
            d = math.hypot(x - cx, z - cz)
            if radius - width <= d <= radius + 0.5:
                p.set(x, y, z, block)


def chest(p, x, y, z, facing, table):
    p.set(x, y, z, B("minecraft:chest", facing=facing, type="single", waterlogged=False),
          {"id": "minecraft:chest", "LootTable": f"{NS}:chests/{table}"})


def barrel(p, x, y, z, table):
    p.set(x, y, z, B("minecraft:barrel", facing="up", open=False),
          {"id": "minecraft:barrel", "LootTable": f"{NS}:chests/{table}"})


def shell_and_floor(p, wall, floor, height=None):
    sx, sy, sz = p.size
    top = sy - 2 if height is None else min(sy - 2, height)
    box(p, 0, 0, 0, sx - 1, 1, sz - 1, wall)
    hollow(p, 1, 1, 1, sx - 2, top, sz - 2, wall)
    box(p, 3, 2, 3, sx - 4, 2, sz - 4, floor)
    box(p, 3, 3, 3, sx - 4, top - 1, sz - 4, AIR)


def four_doors(p, y, half_width=3, height=6):
    sx, _, sz = p.size
    cx, cz = sx // 2, sz // 2
    box(p, cx - half_width, y, 0, cx + half_width, y + height, 4, AIR)
    box(p, cx - half_width, y, sz - 5, cx + half_width, y + height, sz - 1, AIR)
    box(p, 0, y, cz - half_width, 4, y + height, cz + half_width, AIR)
    box(p, sx - 5, y, cz - half_width, sx - 1, y + height, cz + half_width, AIR)


def centre_jigsaws(p, family, y=3):
    sx, _, sz = p.size
    cx, cz = sx // 2, sz // 2
    pool = f"{NS}:deepworks_archaeology/{family}/approach"
    target = f"{NS}:{family}_approach_in"
    for x, z, orientation in ((cx, 0, "north_up"), (cx, sz - 1, "south_up"),
                              (0, cz, "west_up"), (sx - 1, cz, "east_up")):
        p.jigsaw(x, y, z, f"{NS}:{family}_centre_out", target, pool, orientation,
                 joint="aligned", final_state="minecraft:air")


def approach_jigsaws(p, family, y=3):
    sx, _, sz = p.size
    cx = sx // 2
    p.jigsaw(cx, y, sz - 1, f"{NS}:{family}_approach_in",
             f"{NS}:{family}_centre_out", "minecraft:empty", "south_up",
             joint="aligned", final_state="minecraft:air")
    p.jigsaw(cx, y, 0, f"{NS}:{family}_approach_out",
             f"{NS}:{family}_wing_in", f"{NS}:deepworks_archaeology/{family}/wing",
             "north_up", joint="aligned", final_state="minecraft:air")


def wing_jigsaw(p, family, y=3):
    cx = p.size[0] // 2
    p.jigsaw(cx, y, p.size[2] - 1, f"{NS}:{family}_wing_in",
             f"{NS}:{family}_approach_out", "minecraft:empty", "south_up",
                 joint="aligned", final_state="minecraft:air")


def sarcophagus(p, x, y, z, facing="north"):
    """Place one three-block-long royal sarcophagus."""
    steps = {"north": (0, 1), "south": (0, -1), "east": (-1, 0), "west": (1, 0)}
    dx, dz = steps[facing]
    for i, part in enumerate(("head", "middle", "foot")):
        p.set(x + dx * i, y, z + dz * i, B(f"alfheim:elder_sarcophagus_{part}", facing=facing))


def funerary_tapestry(p, x, y, z, facing="north"):
    """Place a three-block-tall hanging, with y at its tattered lower edge."""
    for dy, part in enumerate(("bottom", "middle", "top")):
        p.set(x, y + dy, z, B(f"alfheim:funerary_tapestry_{part}", facing=facing))


def grave_door(p, x, y, z, facing="north"):
    """Place a sealed two-wide, three-high grave portal."""
    side_step = {"north": (1, 0), "south": (-1, 0), "east": (0, 1), "west": (0, -1)}[facing]
    for dy, part in enumerate(("base", "middle", "crown")):
        p.set(x, y + dy, z, B(f"alfheim:elder_grave_door_left_{part}", facing=facing))
        p.set(x + side_step[0], y + dy, z + side_step[1],
              B(f"alfheim:elder_grave_door_right_{part}", facing=facing))


def grave_door_bay(p, x, y, z, facing="north"):
    """Close a corridor-sized opening around one deliberately human-scale grave door."""
    side_step = {"north": (1, 0), "south": (-1, 0),
                 "east": (0, 1), "west": (0, -1)}[facing]
    wall = B("alfheim:ivory_livingrock_bricks")
    trim = B("alfheim:moonstone_livingrock_carved")
    # The authored corridors are nine blocks wide and eight high. Fill that
    # entire cross-section, leaving only the two-by-three sealed portal.
    for side in range(-3, 6):
        for dy in range(8):
            block = AIR if side in (0, 1) and dy < 3 else wall
            p.set(x + side_step[0] * side, y + dy,
                  z + side_step[1] * side, block)
    for side in (-1, 2):
        for dy in range(4):
            p.set(x + side_step[0] * side, y + dy,
                  z + side_step[1] * side, trim)
    for side in range(-1, 3):
        p.set(x + side_step[0] * side, y + 3,
              z + side_step[1] * side, trim)
    grave_door(p, x, y, z, facing)


def funerary_statue(p, x, y, z, facing="north"):
    """Place a three-block-tall crowned funerary guardian."""
    for dy, part in enumerate(("base", "body", "crown")):
        p.set(x, y + dy, z, B(f"alfheim:elder_statue_{part}", facing=facing))


def stair(name, facing, half="bottom"):
    return B(name, facing=facing, half=half, shape="straight", waterlogged=False)


def slab(name, slab_type="bottom"):
    return B(name, type=slab_type, waterlogged=False)


def pointed_arch_z(p, cx, z, y, half_width, height, depth, masonry, stair_name):
    """A thick pointed transverse rib; the clear opening remains genuinely vaulted."""
    spring = y + height - half_width
    for dz in range(depth):
        zz = z + dz
        for side in (-1, 1):
            x = cx + side * (half_width + 1)
            box(p, x, y, zz, x, spring, zz, masonry)
        for step in range(half_width + 1):
            yy = spring + step
            left, right = cx - half_width + step, cx + half_width - step
            p.set(left, yy, zz, stair(stair_name, "east", "top"))
            p.set(right, yy, zz, stair(stair_name, "west", "top"))


def pointed_arch_x(p, x, cz, y, half_width, height, depth, masonry, stair_name):
    spring = y + height - half_width
    for dx in range(depth):
        xx = x + dx
        for side in (-1, 1):
            z = cz + side * (half_width + 1)
            box(p, xx, y, z, xx, spring, z, masonry)
        for step in range(half_width + 1):
            yy = spring + step
            north, south = cz - half_width + step, cz + half_width - step
            p.set(xx, yy, north, stair(stair_name, "south", "top"))
            p.set(xx, yy, south, stair(stair_name, "north", "top"))


def gantry_rect(p, x0, z0, x1, z1, y, slab_name, rail, support):
    """Two-wide walkable gallery with an open centre, rails, brackets and load paths."""
    deck = slab(slab_name, "top")
    for x in range(x0, x1 + 1):
        for z in (z0, z0 + 1, z1 - 1, z1):
            p.set(x, y, z, deck)
    for z in range(z0 + 2, z1 - 1):
        for x in (x0, x0 + 1, x1 - 1, x1):
            p.set(x, y, z, deck)
    for x in range(x0, x1 + 1, 2):
        p.set(x, y + 1, z0, rail)
        p.set(x, y + 1, z1, rail)
    for z in range(z0 + 2, z1 - 1, 2):
        p.set(x0, y + 1, z, rail)
        p.set(x1, y + 1, z, rail)
    for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        box(p, x, 3, z, x, y - 1, z, support)
        p.set(x + (1 if x == x0 else -1), y - 1, z, stair(slab_name.replace("_slab", "_stairs"),
                                                            "east" if x == x0 else "west", "top"))


def stair_flight_z(p, x, z, y, rise, width, stair_name, facing="south"):
    dz = 1 if facing == "south" else -1
    for step in range(rise):
        for dx in range(width):
            p.set(x + dx, y + step, z + dz * step, stair(stair_name, facing))
            if step >= 2:
                p.set(x + dx, y + step - 2, z + dz * step, B(stair_name.replace("_stairs", "_bricks")))


def stair_flight_x(p, x, z, y, rise, width, stair_name, facing="east"):
    dx = 1 if facing == "east" else -1
    for step in range(rise):
        for dz in range(width):
            p.set(x + dx * step, y + step, z + dz, stair(stair_name, facing))
            if step >= 2:
                p.set(x + dx * step, y + step - 2, z + dz, B(stair_name.replace("_stairs", "_bricks")))


def alcove_z(p, cx, z, y, inward, masonry, trim_stairs, backing):
    """A three-block-deep wall niche with a concealed luminous rear plane."""
    dz = 1 if inward == "south" else -1
    facing = "north" if inward == "south" else "south"
    for depth in range(3):
        box(p, cx - 1, y + 1, z + dz * depth, cx + 1, y + 4, z + dz * depth, AIR)
    box(p, cx - 1, y, z, cx + 1, y, z, masonry)
    box(p, cx - 2, y, z, cx - 2, y + 5, z, masonry)
    box(p, cx + 2, y, z, cx + 2, y + 5, z, masonry)
    for dx in (-1, 0, 1):
        p.set(cx + dx, y + 5, z, stair(trim_stairs, facing, "top"))
    box(p, cx - 1, y + 1, z + dz * 3, cx + 1, y + 4, z + dz * 3, backing)


def alcove_x(p, x, cz, y, inward, masonry, trim_stairs, backing):
    dx = 1 if inward == "east" else -1
    facing = "west" if inward == "east" else "east"
    for depth in range(3):
        box(p, x + dx * depth, y + 1, cz - 1, x + dx * depth, y + 4, cz + 1, AIR)
    box(p, x, y, cz - 1, x, y, cz + 1, masonry)
    box(p, x, y, cz - 2, x, y + 5, cz - 2, masonry)
    box(p, x, y, cz + 2, x, y + 5, cz + 2, masonry)
    for dz in (-1, 0, 1):
        p.set(x, y + 5, cz + dz, stair(trim_stairs, facing, "top"))
    box(p, x + dx * 3, y + 1, cz - 1, x + dx * 3, y + 4, cz + 1, backing)


def cornice_rect(p, x0, z0, x1, z1, y, stair_name, slab_name):
    """Two-depth alternating corbel and slab course below an otherwise flat roof."""
    for x in range(x0, x1 + 1):
        p.set(x, y, z0, stair(stair_name, "south", "top") if x % 2 == 0 else slab(slab_name, "top"))
        p.set(x, y, z1, stair(stair_name, "north", "top") if x % 2 == 0 else slab(slab_name, "top"))
        p.set(x, y + 1, z0 + 1, slab(slab_name, "top"))
        p.set(x, y + 1, z1 - 1, slab(slab_name, "top"))
    for z in range(z0 + 1, z1):
        p.set(x0, y, z, stair(stair_name, "east", "top") if z % 2 == 0 else slab(slab_name, "top"))
        p.set(x1, y, z, stair(stair_name, "west", "top") if z % 2 == 0 else slab(slab_name, "top"))
        p.set(x0 + 1, y + 1, z, slab(slab_name, "top"))
        p.set(x1 - 1, y + 1, z, slab(slab_name, "top"))


def quarry_centre(size, seed):
    p, rng = Piece(*size), random.Random(seed)
    sx, _, sz = size
    stone, floor = B("alfheim:rootbound_livingrock"), B("alfheim:rootbound_livingrock_polished")
    brick, carved = B("alfheim:rootbound_livingrock_bricks"), B("alfheim:rootbound_livingrock_carved")
    shell_and_floor(p, stone, floor)
    four_doors(p, 3, 4, 8)
    cx, cz = sx // 2, sz // 2
    box(p, cx - 9, 2, cz - 9, cx + 9, 2, cz + 9, brick)
    box(p, cx - 6, 2, cz - 6, cx + 6, 8, cz + 6, AIR)
    for x, z in ((cx - 10, cz - 10), (cx + 10, cz - 10),
                 (cx - 10, cz + 10), (cx + 10, cz + 10)):
        box(p, x - 1, 2, z - 1, x + 1, 17, z + 1, carved)
    for x in range(cx - 10, cx + 11):
        p.set(x, 17, cz - 10, B("botania:dreamwood_log", axis="x"))
        p.set(x, 17, cz + 10, B("botania:dreamwood_log", axis="x"))
    for z in range(cz - 10, cz + 11):
        p.set(cx - 10, 17, z, B("botania:dreamwood_log", axis="z"))
        p.set(cx + 10, 17, z, B("botania:dreamwood_log", axis="z"))
    for y in range(5, 18):
        p.set(cx, y, cz, B("minecraft:chain", axis="y"))
    # Overseer's gallery: a complete upper circulation loop rather than a decorative beam ring.
    gantry_rect(p, 6, 6, sx - 7, sz - 7, 11, "alfheim:rootbound_livingrock_slab",
                B("alfheim:rootbound_livingrock_wall"), B("botania:dreamwood_log", axis="y"))
    stair_flight_z(p, 8, 7, 3, 9, 2, "alfheim:rootbound_livingrock_stairs", "south")
    stair_flight_z(p, sx - 10, sz - 8, 3, 9, 2,
                   "alfheim:rootbound_livingrock_stairs", "north")
    for z in (7, 15, 31, 39):
        pointed_arch_z(p, cx, z, 3, 10, 16, 2, carved,
                       "alfheim:rootbound_livingrock_stairs")
    for x in (7, 15, 31, 39):
        pointed_arch_x(p, x, cz, 3, 10, 16, 2, carved,
                       "alfheim:rootbound_livingrock_stairs")
    for x in (12, 34):
        alcove_z(p, x, 2, 4, "south", brick, "alfheim:rootbound_livingrock_stairs",
                 B("alfheim:mana_glass_earth"))
        alcove_z(p, x, sz - 3, 4, "north", brick, "alfheim:rootbound_livingrock_stairs",
                 B("alfheim:mana_glass_earth"))
    cornice_rect(p, 3, 3, sx - 4, sz - 4, 19, "alfheim:rootbound_livingrock_stairs",
                 "alfheim:rootbound_livingrock_slab")
    for _ in range(65):
        p.set(rng.randrange(5, sx - 5), 3, rng.randrange(5, sz - 5),
              rng.choice([stone, brick, B("minecraft:gravel")]))
    barrel(p, cx + 12, 3, cz + 4, "deep_quarry_supplies")
    centre_jigsaws(p, "deep_quarry")
    return p


def quarry_approach(size, seed):
    p = Piece(*size)
    sx, _, sz = size
    wall, floor = B("alfheim:rootbound_livingrock_bricks"), B("alfheim:rootbound_livingrock_polished")
    shell_and_floor(p, wall, floor, 16)
    cx = sx // 2
    box(p, cx - 4, 3, 0, cx + 4, 11, sz - 1, AIR)
    for z in range(2, sz - 2):
        for x in (cx - 2, cx + 2):
            p.set(x, 3, z, B("minecraft:rail", shape="north_south"))
    for z in range(5, sz - 2, 7):
        for x in (2, sx - 3):
            box(p, x, 3, z, x, 12, z, B("botania:dreamwood_log", axis="y"))
        box(p, 2, 12, z, sx - 3, 12, z, B("botania:dreamwood_log", axis="x"))
    # Repeated load-bearing ribs, bracket shelves and overhead maintenance ledges.
    for z in (4, 11, 18, 25):
        pointed_arch_z(p, cx, z, 3, 5, 10, 2, wall,
                       "alfheim:rootbound_livingrock_stairs")
    for z in range(3, sz - 3):
        for x in (2, 3, sx - 4, sx - 3):
            p.set(x, 10, z, slab("alfheim:rootbound_livingrock_slab", "top"))
    for z in range(4, sz - 3, 3):
        p.set(2, 11, z, B("alfheim:rootbound_livingrock_wall"))
        p.set(sx - 3, 11, z, B("alfheim:rootbound_livingrock_wall"))
    for z in (8, 22):
        alcove_x(p, 2, z, 4, "east", wall, "alfheim:rootbound_livingrock_stairs",
                 B("alfheim:mana_glass_earth"))
        alcove_x(p, sx - 3, z, 4, "west", wall, "alfheim:rootbound_livingrock_stairs",
                 B("alfheim:mana_glass_earth"))
    approach_jigsaws(p, "deep_quarry")
    return p


def quarry_wing(size, seed):
    p, rng = Piece(*size), random.Random(seed)
    sx, _, sz = size
    stone, brick = B("alfheim:rootbound_livingrock"), B("alfheim:rootbound_livingrock_bricks")
    floor = B("alfheim:rootbound_livingrock_polished")
    shell_and_floor(p, stone, floor)
    cx = sx // 2
    box(p, cx - 4, 3, sz - 6, cx + 4, 11, sz - 1, AIR)
    for x0, x1 in ((4, 15), (18, 29), (32, 43)):
        box(p, x0, 3, 5, x1, 16, 38, AIR)
        box(p, x0, 2, 5, x1, 2, 38, floor)
        box(p, x0, 3, 4, x1, 16, 4, stone)
        for y in (7, 12):
            box(p, x0, y, 4, x1, y, 4, brick)
        gantry_rect(p, x0 + 1, 7, x1 - 1, 36, 10,
                    "alfheim:rootbound_livingrock_slab",
                    B("alfheim:rootbound_livingrock_wall"),
                    B("botania:dreamwood_log", axis="y"))
        stair_flight_z(p, x0 + 3, 7, 3, 8, 2,
                       "alfheim:rootbound_livingrock_stairs", "south")
        for z in (8, 17, 26, 35):
            pointed_arch_z(p, (x0 + x1) // 2, z, 10, 4, 7, 1, brick,
                           "alfheim:rootbound_livingrock_stairs")
        alcove_z(p, (x0 + x1) // 2, 4, 4, "south", brick,
                 "alfheim:rootbound_livingrock_stairs", B("alfheim:mana_glass_earth"))
    cornice_rect(p, 3, 3, sx - 4, sz - 4, 19, "alfheim:rootbound_livingrock_stairs",
                 "alfheim:rootbound_livingrock_slab")
    ores = ["cinderbloom", "verdigris", "palebloom", "sparkroot", "duskbloom",
            "sunbloom", "silverthorn", "grievebloom", "rimebloom", "emberwake"]
    for i, ore in enumerate(ores):
        x = 5 + (i * 9) % 38
        y = 5 + (i * 4) % 11
        for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
            p.set(x + dx, y + dy, 4, B(f"alfheim:{ore}_ore"))
    box(p, 20, 3, 31, 27, 3, 37, B("botania:dreamwood_planks"))
    p.set(23, 4, 34, B("botania:apothecary_livingrock"))
    for pos in ((8, 3, 28), (38, 3, 19), (24, 3, 10)):
        barrel(p, *pos, "deep_quarry_supplies")
    for _ in range(90):
        p.set(rng.randrange(4, sx - 4), 3, rng.randrange(5, sz - 5),
              rng.choice([stone, brick, B("minecraft:gravel"), B("alfheim:cracked_livingrock")]))
    wing_jigsaw(p, "deep_quarry")
    return p


def tomb_centre(size, seed):
    p = Piece(*size)
    sx, _, sz = size
    wall, floor = B("alfheim:ivory_livingrock_bricks"), B("alfheim:moonstone_livingrock_polished")
    shell_and_floor(p, wall, floor, 19)
    four_doors(p, 3, 3, 7)
    cx, cz = sx // 2, sz // 2
    box(p, 8, 3, 8, sx - 9, 15, sz - 9, wall)
    box(p, 10, 3, 10, sx - 11, 13, sz - 11, AIR)
    box(p, cx - 4, 3, 1, cx + 4, 10, sz - 2, AIR)
    box(p, 1, 3, cz - 4, sx - 2, 10, cz + 4, AIR)
    for x, z in ((11, 11), (sx - 12, 11), (11, sz - 12), (sx - 12, sz - 12)):
        box(p, x, 3, z, x + 1, 13, z + 1, B("feywild:elven_quartz_pillar", axis="y"))
    box(p, cx - 4, 3, cz - 3, cx + 4, 3, cz + 3, B("minecraft:smooth_quartz"))
    p.set(cx, 4, cz, B("alfheim:mana_glass_light"))
    chest(p, cx, 3, cz + 5, "north", "elder_kings_relic")
    # The Hall of Names is a royal mortuary monument rather than a bare stone junction.
    for x, z, facing in ((14, 14, "south"), (32, 14, "west"),
                         (14, 32, "east"), (32, 32, "north")):
        funerary_statue(p, x, 3, z, facing)
    funerary_tapestry(p, cx, 6, 10, "south")
    funerary_tapestry(p, cx, 6, sz - 11, "north")
    p.set(10, 7, 18, B("alfheim:memorial_carving", facing="east"))
    p.set(sx - 11, 7, 28, B("alfheim:memorial_carving", facing="west"))
    # Royal triforium: stairs reach a bracketed gallery around the Hall of Names.
    gantry_rect(p, 9, 9, sx - 10, sz - 10, 10, "alfheim:ivory_livingrock_slab",
                B("alfheim:moonstone_livingrock_wall"),
                B("feywild:elven_quartz_pillar", axis="y"))
    stair_flight_z(p, 11, 10, 3, 8, 2, "alfheim:ivory_livingrock_stairs", "south")
    stair_flight_x(p, sx - 12, sz - 12, 3, 8, 2,
                   "alfheim:ivory_livingrock_stairs", "west")
    for z in (7, 18, 29, 39):
        pointed_arch_z(p, cx, z, 3, 8, 15, 2, wall, "alfheim:ivory_livingrock_stairs")
    for x in (7, 18, 29, 39):
        pointed_arch_x(p, x, cz, 3, 8, 15, 2, wall, "alfheim:ivory_livingrock_stairs")
    for x in (12, 34):
        alcove_z(p, x, 2, 4, "south", wall, "alfheim:ivory_livingrock_stairs",
                 B("alfheim:mana_glass_light"))
        alcove_z(p, x, sz - 3, 4, "north", wall, "alfheim:ivory_livingrock_stairs",
                 B("alfheim:mana_glass_light"))
    cornice_rect(p, 3, 3, sx - 4, sz - 4, 17, "alfheim:ivory_livingrock_stairs",
                 "alfheim:ivory_livingrock_slab")
    grave_door_bay(p, cx - 1, 3, 5, "south")
    grave_door_bay(p, cx + 1, 3, sz - 6, "north")
    grave_door_bay(p, 5, 3, cx + 1, "east")
    grave_door_bay(p, sx - 6, 3, cx - 1, "west")
    for x, z in ((8, 20), (18, 8), (29, 37), (38, 25), (7, 35), (35, 7)):
        p.set(x, 3, z, B("alfheim:tomb_debris", facing="north"))
    centre_jigsaws(p, "elder_kings_tomb")
    return p


def tomb_approach(size, seed):
    p = Piece(*size)
    sx, _, sz = size
    wall, floor = B("alfheim:ivory_livingrock_bricks"), B("alfheim:moonstone_livingrock_polished")
    shell_and_floor(p, wall, floor, 15)
    cx = sx // 2
    box(p, cx - 3, 3, 0, cx + 3, 10, sz - 1, AIR)
    for dz in range(-6, 7):
        half = 6 - abs(dz)
        z = 16 + dz
        for x in range(cx - half, cx + half + 1):
            p.set(x, 2, z, B("alfheim:silvermist_livingrock_polished"))
            for y in range(3, 9):
                p.set(x, y, z, AIR)
    for z in (7, 25):
        box(p, 2, 3, z, 4, 10, z + 4, B("feywild:elven_quartz_brick"))
        box(p, sx - 5, 3, z, sx - 3, 10, z + 4, B("feywild:elven_quartz_brick"))
    for z in (3, 9, 15, 21, 27):
        pointed_arch_z(p, cx, z, 3, 5, 11, 2, wall, "alfheim:ivory_livingrock_stairs")
    for z in (6, 16, 26):
        alcove_x(p, 2, z, 4, "east", wall, "alfheim:ivory_livingrock_stairs",
                 B("alfheim:mana_glass_light"))
        alcove_x(p, sx - 3, z, 4, "west", wall, "alfheim:ivory_livingrock_stairs",
                 B("alfheim:mana_glass_light"))
    # Corbelled cornice down both flanks of the upper corridor. The bracket has to START on
    # the shell: it used to stand at x=3 with its slab at x=4, two blocks clear of the wall at
    # x=1 and surrounded by air on all six faces, so the whole band -- 28 walls and 28 slabs --
    # hung in the void. The post now rises off the shell face and the slab corbels one step in
    # off the post, which is the shape the band was always drawing.
    for z in range(3, sz - 3, 2):
        for x_post, x_slab in ((2, 3), (sx - 3, sx - 4)):
            p.set(x_post, 12, z, B("alfheim:moonstone_livingrock_wall"))
            p.set(x_post, 13, z, B("alfheim:moonstone_livingrock_wall"))
            p.set(x_slab, 13, z, slab("alfheim:ivory_livingrock_slab", "top"))
    approach_jigsaws(p, "elder_kings_tomb")
    return p


def tomb_wing(size, seed):
    p = Piece(*size)
    sx, _, sz = size
    wall, floor = B("alfheim:ivory_livingrock_bricks"), B("alfheim:moonstone_livingrock_polished")
    shell_and_floor(p, wall, floor, 19)
    cx = sx // 2
    box(p, cx - 3, 3, sz - 7, cx + 3, 10, sz - 1, AIR)
    rooms = ((5, 5, 19, 20), (27, 5, 41, 20), (14, 25, 32, 41))
    for x0, z0, x1, z1 in rooms:
        hollow(p, x0, 2, z0, x1, 14, z1, wall)
        box(p, x0 + 2, 3, z0 + 2, x1 - 2, 12, z1 - 2, AIR)
        box(p, x0 + 4, 3, z0 + 5, x1 - 4, 3, z1 - 3, B("minecraft:smooth_quartz"))
        p.set((x0 + x1) // 2, 4, (z0 + z1) // 2, B("alfheim:mana_glass_light"))
        # Each burial room has a reachable upper ambulatory and a coffered pointed vault.
        gantry_rect(p, x0 + 1, z0 + 1, x1 - 1, z1 - 1, 9,
                    "alfheim:ivory_livingrock_slab", B("alfheim:moonstone_livingrock_wall"),
                    B("feywild:elven_quartz_pillar", axis="y"))
        stair_flight_z(p, x0 + 2, z0 + 2, 3, 7, 2,
                       "alfheim:ivory_livingrock_stairs", "south")
        room_cx = (x0 + x1) // 2
        for z in range(z0 + 3, z1 - 2, 6):
            pointed_arch_z(p, room_cx, z, 9, max(3, (x1 - x0) // 2 - 2), 6, 1,
                           wall, "alfheim:ivory_livingrock_stairs")
        cornice_rect(p, x0 + 1, z0 + 1, x1 - 1, z1 - 1, 13,
                     "alfheim:ivory_livingrock_stairs", "alfheim:ivory_livingrock_slab")
    for inset in (3, 7, 11):
        for x in range(inset, sx - inset):
            if (x + inset) % 9 not in (0, 1):
                box(p, x, 3, inset, x, 8, inset, wall)
                box(p, x, 3, sz - inset - 1, x, 8, sz - inset - 1, wall)
        for z in range(inset + 1, sz - inset - 1):
            if (z + inset * 2) % 11 not in (0, 1):
                box(p, inset, 3, z, inset, 8, z, wall)
                box(p, sx - inset - 1, 3, z, sx - inset - 1, 8, z, wall)
    box(p, cx - 2, 3, 17, cx + 2, 9, sz - 1, AIR)
    box(p, 11, 3, 21, 35, 9, 25, AIR)
    # Twelve chambers across the assembled tomb: three lavish burials in each wing.
    for x, z in ((12, 10), (34, 10), (23, 31)):
        sarcophagus(p, x, 3, z, "north")
    for x, z in ((12, 19), (34, 19), (23, 40)):
        funerary_tapestry(p, x, 6, z, "north")
    for x, z, facing in ((6, 12, "east"), (40, 12, "west"), (15, 33, "east")):
        p.set(x, 7, z, B("alfheim:memorial_carving", facing=facing))
    for x, z, facing in ((8, 9, "south"), (30, 9, "south"), (18, 29, "east")):
        funerary_statue(p, x, 3, z, facing)
    for x in (8, 16, 30, 38):
        alcove_z(p, x, 3, 4, "south", wall, "alfheim:ivory_livingrock_stairs",
                 B("alfheim:mana_glass_light"))
    for z in (29, 37):
        alcove_x(p, 3, z, 4, "east", wall, "alfheim:ivory_livingrock_stairs",
                 B("alfheim:mana_glass_shadow"))
        alcove_x(p, sx - 4, z, 4, "west", wall, "alfheim:ivory_livingrock_stairs",
                 B("alfheim:mana_glass_shadow"))
    grave_door_bay(p, 11, 3, 5, "south")
    grave_door_bay(p, 33, 3, 5, "south")
    grave_door_bay(p, 22, 3, 25, "south")
    for x, z in ((8, 17), (17, 8), (29, 16), (38, 8), (17, 37), (29, 35),
                 (8, 29), (38, 30), (23, 20), (12, 24)):
        p.set(x, 3, z, B("alfheim:tomb_debris", facing="north"))
    wing_jigsaw(p, "elder_kings_tomb")
    return p


def fault_centre(size, seed):
    p, rng = Piece(*size), random.Random(seed)
    sx, _, sz = size
    cracked, floor = B("alfheim:cracked_livingrock"), B("alfheim:gloam_livingrock_polished")
    shell_and_floor(p, cracked, floor)
    four_doors(p, 3, 4, 9)
    cx, cz = sx // 2, sz // 2
    for radius in (7, 12, 17):
        for y in range(3, 14 if radius == 7 else 8):
            ring(p, cx, cz, y, radius, 1.2,
                 B("minecraft:crying_obsidian") if y % 3 else B("alfheim:magmatic_livingrock"))
    for x in range(2, sx - 2):
        for z in range(cz - 2, cz + 3):
            p.set(x, 2, z, rng.choice([B("alfheim:mana_glass_shadow"),
                                       B("alfheim:mana_glass_fire"),
                                       B("alfheim:mana_glass_light")]))
    # A fractured multi-level survey ring crosses the anomaly instead of circling it at floor level.
    gantry_rect(p, 7, 7, sx - 8, sz - 8, 9, "alfheim:gloam_livingrock_slab",
                B("alfheim:leyline_livingrock_wall"), B("alfheim:leyline_livingrock_carved"))
    stair_flight_z(p, 9, 8, 3, 7, 2, "alfheim:gloam_livingrock_stairs", "south")
    stair_flight_x(p, sx - 10, sz - 10, 3, 7, 2, "alfheim:gloam_livingrock_stairs", "west")
    for z in (8, 19, 37):
        pointed_arch_z(p, cx, z, 3, 10, 19, 2, cracked, "alfheim:cracked_livingrock_stairs")
    for x in (8, 19, 37):
        pointed_arch_x(p, x, cz, 3, 10, 19, 2, cracked, "alfheim:cracked_livingrock_stairs")
    for x in (12, 34):
        alcove_z(p, x, 2, 5, "south", cracked, "alfheim:cracked_livingrock_stairs",
                 B("alfheim:mana_glass_fire"))
    cornice_rect(p, 3, 3, sx - 4, sz - 4, 22, "alfheim:cracked_livingrock_stairs",
                 "alfheim:gloam_livingrock_slab")
    centre_jigsaws(p, "faultwork")
    return p


def fault_approach(size, seed):
    p, rng = Piece(*size), random.Random(seed)
    sx, _, sz = size
    cracked = B("alfheim:cracked_livingrock")
    shell_and_floor(p, cracked, B("alfheim:leyline_livingrock_polished"), 18)
    cx = sx // 2
    box(p, cx - 4, 3, 0, cx + 4, 13, sz - 1, AIR)
    for z in range(sz):
        for x in range(cx - 2, cx + 3):
            p.set(x, 2, z, rng.choice([B("alfheim:mana_glass_shadow"),
                                       B("alfheim:mana_glass_fire"),
                                       B("alfheim:mana_glass_light")]))
        if z % 8 == 3:
            for x in (2, sx - 3):
                box(p, x, 3, z, x, 15, z, B("alfheim:leyline_livingrock_carved"))
    for z in (3, 10, 17, 24):
        pointed_arch_z(p, cx, z, 3, 5, 13, 2, cracked,
                       "alfheim:cracked_livingrock_stairs")
    for z in range(3, sz - 3):
        for x in (2, 3, sx - 4, sx - 3):
            p.set(x, 11, z, slab("alfheim:leyline_livingrock_slab", "top"))
        if z % 2 == 0:
            p.set(2, 12, z, B("alfheim:leyline_livingrock_wall"))
            p.set(sx - 3, 12, z, B("alfheim:leyline_livingrock_wall"))
    stair_flight_z(p, 2, 4, 3, 9, 2, "alfheim:leyline_livingrock_stairs", "south")
    for z in range(5, sz - 4, 5):
        p.set(cx, 17, z, B("minecraft:chain", axis="y"))
        p.set(cx, 16, z, B("alfheim:mana_glass_fire" if z % 10 else "alfheim:mana_glass_shadow"))
    for z in (8, 22):
        alcove_x(p, 2, z, 4, "east", cracked, "alfheim:cracked_livingrock_stairs",
                 B("alfheim:mana_glass_shadow"))
        alcove_x(p, sx - 3, z, 4, "west", cracked, "alfheim:cracked_livingrock_stairs",
                 B("alfheim:mana_glass_fire"))
    approach_jigsaws(p, "faultwork")
    return p


def fault_wing(size, seed):
    p, rng = Piece(*size), random.Random(seed)
    sx, sy, sz = size
    cracked = B("alfheim:cracked_livingrock")
    shell_and_floor(p, cracked, B("alfheim:gloam_livingrock_polished"))
    cx, cz = sx // 2, sz // 2
    box(p, cx - 4, 3, sz - 7, cx + 4, 12, sz - 1, AIR)
    for x in range(2, sx - 2):
        for y in range(2, sy - 2):
            for z in range(2, sz - 2):
                d = math.sqrt(((x - cx) / 16.0) ** 2 + ((y - 12) / 13.0) ** 2 +
                              ((z - 18) / 14.0) ** 2)
                if d < 1:
                    p.set(x, y, z, AIR)
                elif d < 1.16 and rng.random() < 0.42:
                    p.set(x, y, z, rng.choice([B("minecraft:crying_obsidian"),
                                               B("alfheim:magmatic_livingrock"),
                                               B("alfheim:mana_glass_shadow"),
                                               B("alfheim:mana_glass_fire")]))
    for radius in (10, 15, 20):
        ring(p, cx, cz, 2 + radius // 5, radius, 1.3, B("minecraft:crying_obsidian"))
    # Suspended fracture bridges at two elevations, joined by opposing stair towers.
    #
    # Both decks used to be two slabs wide with their railings standing one block OUTSIDE the
    # deck edge, a level up -- nothing under them, nothing beside them, so every post on both
    # bridges hung in the cavern air. The decks are four wide now: two lanes to walk, and an
    # outer slab on each side for the railing to stand on.
    for x in range(6, sx - 6):
        for z in (cz - 2, cz - 1, cz, cz + 1):
            p.set(x, 8, z, slab("alfheim:gloam_livingrock_slab", "top"))
        if x % 2 == 0:
            p.set(x, 9, cz - 2, B("alfheim:leyline_livingrock_wall"))
            p.set(x, 9, cz + 1, B("alfheim:leyline_livingrock_wall"))
    for z in range(6, sz - 6):
        for x in (cx - 2, cx - 1, cx, cx + 1):
            p.set(x, 14, z, slab("alfheim:leyline_livingrock_slab", "top"))
        if z % 2 == 0:
            p.set(cx - 2, 15, z, B("alfheim:cracked_livingrock_wall"))
            p.set(cx + 1, 15, z, B("alfheim:cracked_livingrock_wall"))
    stair_flight_x(p, 7, cz - 1, 3, 6, 2, "alfheim:gloam_livingrock_stairs", "east")
    stair_flight_z(p, cx - 1, 7, 8, 7, 2, "alfheim:leyline_livingrock_stairs", "south")
    for x, z in ((8, 8), (38, 8), (8, 36), (38, 36)):
        box(p, x, 3, z, x, 19, z, B("alfheim:leyline_livingrock_carved"))
        for y in (7, 12, 17):
            p.set(x, y, z + (1 if z < cz else -1),
                  stair("alfheim:cracked_livingrock_stairs", "south" if z < cz else "north", "top"))
    cornice_rect(p, 3, 3, sx - 4, sz - 4, 22, "alfheim:cracked_livingrock_stairs",
                 "alfheim:gloam_livingrock_slab")
    for _ in range(140):
        p.set(rng.randrange(3, sx - 3), rng.randrange(3, 11), rng.randrange(3, sz - 3),
              rng.choice([cracked, B("minecraft:crying_obsidian"), B("alfheim:magmatic_livingrock")]))
    for pos in ((7, 3, 37), (39, 3, 37), (23, 3, 40)):
        barrel(p, *pos, "faultwork_salvage")
    wing_jigsaw(p, "faultwork")
    return p



# --- the surface headworks --------------------------------------------------------------------
#
# Field report 2026-09-07: "I was not able to locate a instance of either of the deep works
# spawning structures." Two separate causes. The grid pitch was one (B-83, now 48/24). The other
# is that all three families sit at absolute Y -58..-10 with terrain_adaptation `none` and every
# jigsaw in the chain at local y=3 -- the complexes are entirely horizontal and nothing about
# them reaches the surface. A player standing directly on one sees ordinary ground.
#
# The headworks is the thing you can see. It is a separate structure set with the SAME spacing,
# separation and salt as deepworks_archaeology, so RandomSpreadStructurePlacement resolves both
# to the same chunk and the winding gear stands on top of whatever family is below.
#
# ONE generic head rather than three matched ones, deliberately. The archaeology set picks a
# family with its own weighted roll; a second set would roll independently and a Tomb portal
# would end up over a Quarry a third of the time. A neutral elven mine head is right over all
# three and cannot desynchronise.
#
# The shaft chains DOWNWARD as a jigsaw pool rather than being one tall piece, because the gap it
# has to cross is 50-130 blocks and varies with both terrain and the family's own depth roll --
# no fixed-length piece can span that. Descending segments simply stop when the size budget runs
# out, and an overshoot is a mine shaft that passes through the complex, which is the outcome we
# want anyway.
HEAD_W, HEAD_H = 16, 24
SHAFT_W, SHAFT_H = 8, 24

HEAD_STONE = B("alfheim:cracked_livingrock")
HEAD_BRICK = B("alfheim:ivory_livingrock_bricks")
HEAD_TRIM = B("alfheim:moonstone_livingrock_carved")
HEAD_BEAM = B("botania:dreamwood_log", axis="y")
HEAD_BEAM_X = B("botania:dreamwood_log", axis="x")
HEAD_BEAM_Z = B("botania:dreamwood_log", axis="z")
SPOIL = B("minecraft:gravel")


def headworks_head(size, seed):
    """Winding gear over an open shaft mouth, on a spoil apron. The one thing visible above."""
    p, rng = Piece(*size), random.Random(seed)
    sx, sy, sz = size
    cx, cz = sx // 2, sz // 2

    # A shallow apron of spoil and dressed stone, so the head reads as worked ground rather
    # than a building dropped on grass.
    for x in range(sx):
        for z in range(sz):
            d = math.hypot(x - cx, z - cz)
            if d <= 7.2:
                p.set(x, 0, z, HEAD_STONE if d > 5.4 else HEAD_BRICK)
            elif d <= 8.6 and rng.random() < 0.55:
                p.set(x, 0, z, SPOIL)

    # The shaft mouth: a four-by-four opening ringed by a kerb, carried straight down through
    # the piece so the first shaft segment below joins clean air.
    for x in range(cx - 2, cx + 2):
        for z in range(cz - 2, cz + 2):
            for y in range(0, HEAD_H):
                p.set(x, y, z, AIR)
    for x in range(cx - 3, cx + 3):
        for z in range(cz - 3, cz + 3):
            if x in (cx - 3, cx + 2) or z in (cz - 3, cz + 2):
                p.set(x, 1, z, HEAD_TRIM)

    # Four legs and a head frame over the mouth. Broken to differing heights: this stopped
    # working a long time ago.
    legs = ((cx - 3, cz - 3), (cx + 2, cz - 3), (cx - 3, cz + 2), (cx + 2, cz + 2))
    tops = {}
    for lx, lz in legs:
        h = rng.choice([9, 11, 12, 12, 14])
        for y in range(1, h):
            p.set(lx, y, lz, HEAD_BEAM)
        tops[(lx, lz)] = h - 1
    # The cross-head only survives where both its legs did.
    top = min(tops.values())
    if top >= 8:
        for x in range(cx - 3, cx + 3):
            p.set(x, top, cz - 3, HEAD_BEAM_X)
            p.set(x, top, cz + 2, HEAD_BEAM_X)
        for z in range(cz - 3, cz + 3):
            p.set(cx - 3, top, z, HEAD_BEAM_Z)
            p.set(cx + 2, top, z, HEAD_BEAM_Z)
        # The winding drum, fallen across the frame.
        for x in range(cx - 2, cx + 2):
            p.set(x, top + 1, cz, HEAD_BEAM_X)

    # A ladder down one wall of the mouth, and a lantern that still burns.
    for y in range(1, HEAD_H):
        p.set(cx - 2, y, cz - 2, B("minecraft:ladder", facing="south"))
    p.set(cx + 1, 3, cz + 1, B("alfheim:mana_glass_light"))

    # Scattered spoil and a couple of abandoned barrels.
    for _ in range(26):
        x, z = rng.randrange(sx), rng.randrange(sz)
        if math.hypot(x - cx, z - cz) > 4.5 and (x, 1, z) not in p.blocks:
            p.set(x, 1, z, rng.choice([SPOIL, HEAD_STONE, B("minecraft:cobblestone")]))
    barrel(p, cx + 4, 1, cz, "faultwork_salvage")

    # Down into the first shaft segment.
    p.jigsaw(cx, 0, cz, f"{NS}:headworks_head_out", f"{NS}:headworks_shaft_in",
             f"{NS}:deepworks_archaeology/headworks/shaft", "down_south",
             joint="aligned", final_state="minecraft:air")
    return p


def headworks_shaft(size, seed):
    """One repeatable length of timbered shaft. Chains to the next below it."""
    p, rng = Piece(*size), random.Random(seed)
    sx, sy, sz = size
    cx, cz = sx // 2, sz // 2
    box(p, 0, 0, 0, sx - 1, sy - 1, sz - 1, HEAD_STONE)
    box(p, cx - 2, 0, cz - 2, cx + 1, sy - 1, cz + 1, AIR)
    # Timber sets every four courses, and a ladder the whole way.
    for y in range(0, sy):
        p.set(cx - 2, y, cz - 2, B("minecraft:ladder", facing="south"))
        if y % 4 == 0:
            for x in range(cx - 2, cx + 2):
                p.set(x, y, cz - 2, HEAD_BEAM_X)
                p.set(x, y, cz + 1, HEAD_BEAM_X)
            p.set(cx - 2, y, cz - 2, B("minecraft:ladder", facing="south"))
    # Local collapse: some sets have failed and spilled into the shaft.
    for _ in range(rng.randint(2, 6)):
        y = rng.randrange(1, sy - 1)
        p.set(rng.randrange(cx - 2, cx + 2), y, rng.randrange(cz - 2, cz + 2),
              rng.choice([SPOIL, B("minecraft:cobblestone"), HEAD_STONE]))
    p.jigsaw(cx, sy - 1, cz, f"{NS}:headworks_shaft_in", f"{NS}:headworks_head_out",
             "minecraft:empty", "up_south", joint="aligned", final_state="minecraft:air")
    p.jigsaw(cx, 0, cz, f"{NS}:headworks_shaft_out", f"{NS}:headworks_shaft_in",
             f"{NS}:deepworks_archaeology/headworks/shaft", "down_south",
             joint="aligned", final_state="minecraft:air")
    return p

HEADWORKS_BUILDERS = {"head": headworks_head, "shaft": headworks_shaft}
HEADWORKS_SIZES = {"head": [HEAD_W, HEAD_H, HEAD_W], "shaft": [SHAFT_W, SHAFT_H, SHAFT_W]}

BUILDERS = {
    "deep_quarry": {"centre": quarry_centre, "approach": quarry_approach, "wing": quarry_wing},
    "elder_kings_tomb": {"centre": tomb_centre, "approach": tomb_approach, "wing": tomb_wing},
    "faultwork": {"centre": fault_centre, "approach": fault_approach, "wing": fault_wing},
}


def json_bytes(body):
    return (json.dumps(body, indent=2) + "\n").encode()


def write_json(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(json_bytes(body))


def salt_for(name):
    return int(hashlib.sha1(("deep-archaeology:" + name).encode()).hexdigest()[:7], 16)


def single_pool(name, location):
    return {"name": name, "fallback": "minecraft:empty", "elements": [{"weight": 1,
            "element": {"location": location, "processors": "minecraft:empty",
                        "projection": "rigid", "element_type": "minecraft:single_pool_element"}}]}


def relic_loot():
    entries = []
    for name, color, lore in (
        ("Memory Crystal of Aelthir", "aqua", "A king who ordered the gates sealed."),
        ("Memory Crystal of Maerwyn", "light_purple", "A queen who kept the last census."),
        ("Memory Crystal of Orodain", "gold", "A king who descended when the ley-lines broke."),
    ):
        entries.append({"type": "minecraft:item", "name": "minecraft:amethyst_shard", "weight": 1,
                        "functions": [{"function": "minecraft:set_name",
                                       "name": {"text": name, "italic": False, "color": color}},
                                      {"function": "minecraft:set_lore", "replace": True,
                                       "lore": [{"text": lore, "italic": True, "color": "gray"}]}]})
    return {"type": "minecraft:chest", "random_sequence": f"{NS}:chests/elder_kings_relic",
            "pools": [{"rolls": 1.0, "bonus_rolls": 0.0, "entries": entries}]}


def quarry_loot():
    return {"type": "minecraft:chest", "random_sequence": f"{NS}:chests/deep_quarry_supplies",
            "pools": [{"rolls": {"type": "minecraft:uniform", "min": 1.0, "max": 3.0},
                       "bonus_rolls": 0.0, "entries": [
                           {"type": "minecraft:item", "name": "minecraft:torch", "weight": 8,
                            "functions": [{"function": "minecraft:set_count", "count": {"min": 3.0, "max": 9.0}}]},
                           {"type": "minecraft:item", "name": "minecraft:iron_pickaxe", "weight": 2,
                            "functions": [{"function": "minecraft:set_damage", "damage": {"min": 0.55, "max": 0.92}}]},
                           {"type": "minecraft:item", "name": "botania:livingrock", "weight": 6,
                            "functions": [{"function": "minecraft:set_count", "count": {"min": 2.0, "max": 8.0}}]}
                       ]}]}


def faultwork_loot():
    return {"type": "minecraft:chest", "random_sequence": f"{NS}:chests/faultwork_salvage",
            "pools": [{"rolls": {"type": "minecraft:uniform", "min": 2.0, "max": 4.0},
                       "bonus_rolls": 0.0, "entries": [
                           {"type": "minecraft:item", "name": "occultism:burnt_otherstone", "weight": 8,
                            "functions": [{"function": "minecraft:set_count", "count": {"min": 2.0, "max": 7.0}}]},
                           {"type": "minecraft:item", "name": "minecraft:amethyst_shard", "weight": 4,
                            "functions": [{"function": "minecraft:set_count", "count": {"min": 1.0, "max": 4.0}}]},
                           {"type": "minecraft:item", "name": "botania:mana_powder", "weight": 2,
                            "functions": [{"function": "minecraft:set_count", "count": {"min": 1.0, "max": 3.0}}]}
                       ]}]}


# --- the detail pass -----------------------------------------------------------------------
#
# The three families were already the most architectural geometry in the pack -- pointed
# arches, alcoves, cornices, gantries, sarcophagi -- and still measured 4.5 to 7.8 per cent
# detail blocks, because a hall carved out of rock is mostly rock. What they had none of was
# occupation: no hung light, no tools left where somebody put them down, and no sign that
# three hundred years of groundwater has been coming through the ceiling. Those are the
# layers `structure_detail.py` owns, so the families ask for them here rather than growing a
# fourth copy of the same code.
#
# Two constraints are specific to underground work and are why the tuning is not the
# surface's. `check_deep_archaeology.py` validates every palette entry against an ITEM
# registry, and `minecraft:wall_torch` has no item -- so the light is hung on chains and the
# bracket form is switched off. And down here every floor is roofed, which the weather test
# in `ingress()` would read as "dry": `roofed_ok` inverts it, and the water arrives as
# dripstone through the rock instead of as rain through a missing roof.

DETAIL_KITS = {
    "deep_quarry": dict(
        stone="alfheim:rootbound_livingrock", brick="alfheim:rootbound_livingrock_bricks",
        floor="alfheim:rootbound_livingrock_polished",
        accent="alfheim:rootbound_livingrock_carved",
        stairs="alfheim:rootbound_livingrock_stairs",
        slab="alfheim:rootbound_livingrock_slab",
        wall="alfheim:rootbound_livingrock_wall", pillar="botania:dreamwood_log",
        crystal="alfheim:rootglass_cluster", timber="botania:dreamwood_log",
        plank="botania:dreamwood_planks", fence="botania:dreamwood_fence",
        light="minecraft:lantern",
        rubble=["alfheim:rootbound_livingrock", "minecraft:gravel",
                "alfheim:cracked_livingrock"]),
    "elder_kings_tomb": dict(
        stone="alfheim:ivory_livingrock", brick="alfheim:ivory_livingrock_bricks",
        floor="alfheim:moonstone_livingrock_polished",
        accent="alfheim:ivory_livingrock_polished",
        stairs="alfheim:ivory_livingrock_stairs", slab="alfheim:ivory_livingrock_slab",
        wall="alfheim:ivory_livingrock_wall", pillar="alfheim:moonstone_livingrock_polished",
        crystal="alfheim:duskglass_cluster", timber="botania:dreamwood_log",
        plank="botania:dreamwood_planks", fence="botania:dreamwood_fence",
        light="minecraft:soul_lantern",
        rubble=["alfheim:ivory_livingrock", "minecraft:gravel",
                "alfheim:cracked_livingrock"]),
    "faultwork": dict(
        stone="alfheim:cracked_livingrock", brick="alfheim:gloam_livingrock_bricks",
        floor="alfheim:gloam_livingrock_polished",
        accent="alfheim:leyline_livingrock_carved",
        stairs="alfheim:gloam_livingrock_stairs", slab="alfheim:gloam_livingrock_slab",
        wall="alfheim:gloam_livingrock_wall", pillar="alfheim:leyline_livingrock_polished",
        crystal="alfheim:emberglass_cluster", timber="botania:dreamwood_log",
        plank="botania:dreamwood_planks", fence="botania:dreamwood_fence",
        light="minecraft:soul_lantern",
        rubble=["alfheim:cracked_livingrock", "minecraft:gravel", "minecraft:blackstone"]),
}

# A quarry was worked, a tomb was sealed and a faultwork failed, so they do not get the same
# residue: crates and haulage below, offerings and cobwebs in the tomb, and in the faultwork
# the ley crystal that was the reason anyone dug there.
DETAIL_TUNING = {
    "deep_quarry": dict(
        dress=dict(corbel=0.22, conduit=0.45, sockets=3, sconce=0.60, sconce_spacing=6,
                   furniture=0.45, floor_litter=0.06),
        settle=dict(rubble=0.10, reach=3, weathering=0.08, seep="dust", seep_rate=0.09,
                    roots=0.09, webs=0.02)),
    "elder_kings_tomb": dict(
        dress=dict(corbel=0.25, conduit=0.55, sockets=4, sconce=0.70, sconce_spacing=5,
                   furniture=0.30, furniture_allow=("pot", "bench", "table", "shelf"),
                   floor_litter=0.05),
        settle=dict(rubble=0.07, reach=2, weathering=0.06, seep="damp", seep_rate=0.10,
                    roots=0.10, webs=0.06)),
    "faultwork": dict(
        dress=dict(corbel=0.20, conduit=0.60, sockets=5, sconce=0.55, sconce_spacing=6,
                   furniture=0.35, floor_litter=0.07),
        settle=dict(rubble=0.13, reach=3, weathering=0.10, seep="damp", seep_rate=0.11,
                    roots=0.13, webs=0.04)),
}

# The floor of every authored room sits at y=3; the shell and its bedding are below that.
DETAIL_GROUND = 3


def detail_family(piece, fid, seed):
    """Hang the light, leave the tools, and let three centuries of water in."""
    kit = sd.Kit(**DETAIL_KITS[fid])
    tuning = DETAIL_TUNING[fid]
    counts = sd.dress(piece, seed, kit, ground=DETAIL_GROUND, bracket_light=False,
                      **tuning["dress"])
    counts.update(sd.aftermath(piece, seed, kit, ground=DETAIL_GROUND, hang="drip",
                               roofed_ok=True, **tuning["settle"]))
    return counts


def build_outputs(check=False):
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    json_out, nbt_expected = {}, {}
    for family in manifest["families"]:
        fid = family["id"]
        for role, size in family["pieces"].items():
            assert max(size) <= MAX_AXIS
            seed = int(hashlib.sha1(f"{fid}:{role}".encode()).hexdigest()[:8], 16)
            piece = BUILDERS[fid][role](tuple(size), seed)
            # Collapse and rubble passes here remove blocks without asking what rested on
            # them; sweep anything they left touching nothing on any face.
            piece.prune_orphans()
            path = os.path.join(STRUCT, fid, role + ".nbt")
            nbt_expected[path] = piece.to_nbt()
            if not check:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                nbt.save(path, "", piece.to_nbt())
            print(f"  {fid:18} {role:9} {size[0]}x{size[1]}x{size[2]}  {len(piece.blocks):6} blocks")

    # The headworks: two pieces, shared by all three families.
    for role, builder in HEADWORKS_BUILDERS.items():
        size = HEADWORKS_SIZES[role]
        assert max(size) <= MAX_AXIS
        seed = int(hashlib.sha1(f"headworks:{role}".encode()).hexdigest()[:8], 16)
        piece = builder(tuple(size), seed)
        piece.prune_orphans()
        path = os.path.join(STRUCT, "headworks", role + ".nbt")
        nbt_expected[path] = piece.to_nbt()
        if not check:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            nbt.save(path, "", piece.to_nbt())
        print(f"  {'headworks':18} {role:9} {size[0]}x{size[1]}x{size[2]}  {len(piece.blocks):6} blocks")

        base = f"{NS}:deepworks_archaeology/{fid}"
        for role in ("centre", "approach", "wing"):
            path = os.path.join(DATA, "worldgen", "template_pool", "deepworks_archaeology", fid,
                                role + ".json")
            json_out[path] = single_pool(f"{base}/{role}", f"{base}/{role}")
        lo, hi = family["depth"]
        json_out[os.path.join(DATA, "worldgen", "structure", fid + ".json")] = {
            "type": "minecraft:jigsaw", "biomes": manifest["biomes"],
            "step": "underground_structures", "terrain_adaptation": "none",
            "start_pool": f"{base}/centre", "size": 2, "max_distance_from_center": 116,
            "start_height": {"type": "minecraft:uniform",
                             "min_inclusive": {"absolute": lo},
                             "max_inclusive": {"absolute": hi}},
            "use_expansion_hack": False, "spawn_overrides": {}}
        json_out[os.path.join(DATA, "tags", "worldgen", "structure", fid + ".json")] = {
            "replace": False, "values": [f"{NS}:{fid}"]}

    placement = manifest["placement"]
    json_out[os.path.join(DATA, "worldgen", "structure_set", "deepworks_archaeology.json")] = {
        "structures": [{"structure": f"{NS}:{family['id']}", "weight": 1}
                       for family in manifest["families"]],
        "placement": {"type": "minecraft:random_spread",
                      "spacing": placement["spacing"],
                      "separation": placement["separation"],
                      "spread_type": "linear",
                      "salt": salt_for("deepworks_archaeology")}}

    # --- the headworks: pools, structure and a CO-LOCATED structure set ----------------------
    for role in HEADWORKS_BUILDERS:
        json_out[os.path.join(DATA, "worldgen", "template_pool", "deepworks_archaeology",
                              "headworks", role + ".json")] = single_pool(
            f"{NS}:deepworks_archaeology/headworks/{role}",
            f"{NS}:deepworks_archaeology/headworks/{role}")

    # `size` is the jigsaw depth budget and here it is literally how deep the shaft can go.
    # 1.20.1 CAPS IT AT 7 -- a first attempt at 10 failed world load outright with
    # "Value 10 outside of range [0:7]", which is why the segments are 24 blocks rather than 16:
    # one head plus six segments is 144 blocks of reach either way, and the complexes sit
    # 50-130 blocks below the surface depending on terrain and their own depth roll. A chain
    # that runs out early leaves a shaft ending in stone, which reads as a mine that collapsed
    # rather than as a broken structure, but it must not run out in the common case.
    json_out[os.path.join(DATA, "worldgen", "structure", "deepworks_headworks.json")] = {
        "type": "minecraft:jigsaw", "biomes": manifest["biomes"],
        "step": "surface_structures", "terrain_adaptation": "beard_thin",
        "start_pool": f"{NS}:deepworks_archaeology/headworks/head",
        "size": 7, "max_distance_from_center": 116,
        "start_height": {"type": "minecraft:uniform",
                         "min_inclusive": {"above_bottom": 0},
                         "max_inclusive": {"above_bottom": 0}},
        "project_start_to_heightmap": "WORLD_SURFACE_WG",
        "use_expansion_hack": False, "spawn_overrides": {}}
    json_out[os.path.join(DATA, "tags", "worldgen", "structure", "deepworks_headworks.json")] = {
        "replace": False, "values": [f"{NS}:deepworks_headworks"]}

    # IDENTICAL spacing, separation and salt to deepworks_archaeology. RandomSpreadStructurePlacement
    # derives its chunk from exactly those three plus the world seed, so both sets resolve to the
    # same chunk and the winding gear stands over the complex rather than somewhere near it.
    json_out[os.path.join(DATA, "worldgen", "structure_set", "deepworks_headworks.json")] = {
        "structures": [{"structure": f"{NS}:deepworks_headworks", "weight": 1}],
        "placement": {"type": "minecraft:random_spread",
                      "spacing": placement["spacing"],
                      "separation": placement["separation"],
                      "spread_type": "linear",
                      "salt": salt_for("deepworks_archaeology")}}

    json_out[os.path.join(DATA, "loot_tables", "chests", "deep_quarry_supplies.json")] = quarry_loot()
    json_out[os.path.join(DATA, "loot_tables", "chests", "elder_kings_relic.json")] = relic_loot()
    json_out[os.path.join(DATA, "loot_tables", "chests", "faultwork_salvage.json")] = faultwork_loot()
    json_out[os.path.join("kubejs", "data", "continuityworks_spawn_protection", "tags", "worldgen",
                          "structure", "ignored.json")] = {
        "replace": False, "values": ["alfheim:deep_quarry", "alfheim:elder_kings_tomb",
                                     "alfheim:faultwork", "alfheim:deepworks_headworks"]}
    return json_out, nbt_expected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    json_out, nbt_expected = build_outputs(args.check)
    if args.check:
        problems = [path for path, body in json_out.items()
                    if not os.path.exists(path) or open(path, "rb").read() != json_bytes(body)]
        for path, expected in nbt_expected.items():
            if not os.path.exists(path) or nbt.load(path)[1] != expected:
                problems.append(path)
        if problems:
            raise SystemExit("generated output differs: " + ", ".join(problems))
        print(f"PASS: {len(json_out)} JSON and {len(nbt_expected)} decoded NBT payloads match")
    else:
        for path, body in json_out.items():
            write_json(path, body)
        print(f"generated {len(json_out)} JSON and {len(nbt_expected)} NBT archaeology files")


if __name__ == "__main__":
    main()
