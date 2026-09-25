"""Generate three gigantic Deepworks archaeology complexes.

The quarry and Faultworks are deterministic nine-piece assemblies.  The Elder Kings tomb adds a
side-connected dynastic gallery to each royal wing: centre, four approaches, four royal precincts
and four generation crypts in a dense pinwheel about 207 blocks across.  Every NBT piece stays
under Minecraft's 48-block structure-block editing limit and the assembly stays inside the
1.20.1 jigsaw codec's 128-block reach cap.
"""
import argparse
import hashlib
import json
import math
import os
import random
import sys
from dataclasses import dataclass

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


def vaulted_range_z(p, x0, z0, x1, z1, wall, floor, eave=10, rise=5):
    """Build a narrow stepped barrel vault running north/south, not a cuboid shell."""
    box(p, x0, 0, z0, x1, 1, z1, wall)
    box(p, x0 + 1, 2, z0 + 1, x1 - 1, 2, z1 - 1, floor)
    half = max(1, (x1 - x0) // 2)
    for x in range(x0, x1 + 1):
        roof_y = eave + min(rise, x - x0, x1 - x)
        for z in range(z0, z1 + 1):
            end = z in (z0, z1)
            side = x in (x0, x1)
            if end:
                box(p, x, 2, z, x, roof_y, z, wall)
            else:
                if side:
                    box(p, x, 2, z, x, eave, z, wall)
                if not side:
                    box(p, x, 3, z, x, roof_y - 1, z, AIR)
                p.set(x, roof_y, z, wall)


def vaulted_range_x(p, x0, z0, x1, z1, wall, floor, eave=9, rise=4):
    """East/west counterpart used for transepts and projecting burial chapels."""
    box(p, x0, 0, z0, x1, 1, z1, wall)
    box(p, x0 + 1, 2, z0 + 1, x1 - 1, 2, z1 - 1, floor)
    for z in range(z0, z1 + 1):
        roof_y = eave + min(rise, z - z0, z1 - z)
        for x in range(x0, x1 + 1):
            end = x in (x0, x1)
            side = z in (z0, z1)
            if end:
                box(p, x, 2, z, x, roof_y, z, wall)
            else:
                if side:
                    box(p, x, 2, z, x, eave, z, wall)
                if not side:
                    box(p, x, 3, z, x, roof_y - 1, z, AIR)
                p.set(x, roof_y, z, wall)


def octagonal_rotunda(p, cx, cz, radius, wall, floor, eave=12, rise=5):
    """Carve a true faceted royal chamber whose footprint and crown both step inward."""
    def inside(dx, dz, shrink=0):
        r = radius - shrink
        return r >= 0 and abs(dx) <= r and abs(dz) <= r and abs(dx) + abs(dz) <= r + 7

    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            dx, dz = x - cx, z - cz
            if not inside(dx, dz):
                continue
            boundary = any(not inside(dx + ox, dz + oz)
                           for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            box(p, x, 0, z, x, 1, z, wall)
            p.set(x, 2, z, floor)
            if boundary:
                box(p, x, 3, z, x, eave, z, wall)
            else:
                box(p, x, 3, z, x, eave - 1, z, AIR)
    # Five corbel courses make the crown visibly smaller at every level.
    for lift in range(rise + 1):
        y = eave + lift
        for x in range(cx - radius, cx + radius + 1):
            for z in range(cz - radius, cz + radius + 1):
                dx, dz = x - cx, z - cz
                if inside(dx, dz, lift) and any(
                        not inside(dx + ox, dz + oz, lift)
                        for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    p.set(x, y, z, wall)
    box(p, cx - 2, eave + rise, cz - 2, cx + 2, eave + rise, cz + 2, wall)


def octagonal_register_band(p, cx, cz, radius, y=7, interval=4):
    """Wrap the memorial register around the rotunda's eight faces."""
    polished = B("alfheim:ivory_livingrock_polished")
    carved = B("alfheim:moonstone_livingrock_carved")

    def inside(dx, dz):
        return abs(dx) <= radius and abs(dz) <= radius and abs(dx) + abs(dz) <= radius + 7

    boundary = []
    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            dx, dz = x - cx, z - cz
            if inside(dx, dz) and any(not inside(dx + ox, dz + oz)
                                      for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                boundary.append((x, z))
    for i, (x, z) in enumerate(sorted(boundary)):
        p.set(x, y - 1, z, polished)
        p.set(x, y, z, B("alfheim:memorial_carving", facing="north")
              if i % interval == 0 else carved)
        p.set(x, y + 1, z, polished)


def octagonal_ambulatory(p, cx, cz, radius, y=10):
    """A two-course walk following the rotunda instead of drawing a square inside it."""
    deck = slab("alfheim:ivory_livingrock_slab", "top")
    rail = B("alfheim:moonstone_livingrock_wall")
    support = B("feywild:elven_quartz_pillar", axis="y")

    def inside(dx, dz, r):
        return abs(dx) <= r and abs(dz) <= r and abs(dx) + abs(dz) <= r + 7

    r = radius - 2
    cells = []
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            dx, dz = x - cx, z - cz
            if inside(dx, dz, r) and not inside(dx, dz, r - 3):
                p.set(x, y, z, deck)
                cells.append((x, z))
    for i, (x, z) in enumerate(cells):
        dx, dz = x - cx, z - cz
        if any(not inside(dx + ox, dz + oz, r)
               for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            p.set(x, y + 1, z, rail)
            if i % 9 == 0:
                box(p, x, 3, z, x, y - 1, z, support)


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


def tomb_wing_jigsaws(p, y=3):
    """Join a royal precinct between its approach and the deeper dynastic gallery."""
    cx = p.size[0] // 2
    p.jigsaw(cx, y, p.size[2] - 1, f"{NS}:elder_kings_tomb_wing_in",
             f"{NS}:elder_kings_tomb_approach_out", "minecraft:empty", "south_up",
             joint="aligned", final_state="minecraft:air")
    p.jigsaw(p.size[0] - 1, y, 30, f"{NS}:elder_kings_tomb_wing_out",
             f"{NS}:elder_kings_tomb_gallery_in",
             f"{NS}:deepworks_archaeology/elder_kings_tomb/gallery", "east_up",
             joint="aligned", final_state="minecraft:air")


def tomb_gallery_jigsaw(p, y=3):
    cx = p.size[0] // 2
    p.jigsaw(cx, y, p.size[2] - 1, f"{NS}:elder_kings_tomb_gallery_in",
             f"{NS}:elder_kings_tomb_wing_out", "minecraft:empty", "south_up",
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


@dataclass(frozen=True)
class TombRoom:
    """A semantic room whose furnishings move with its extent and processional axis."""

    role: str
    extent: tuple
    axis: str = "z"

    @property
    def centre(self):
        x0, z0, x1, z1 = self.extent
        return ((x0 + x1) // 2, (z0 + z1) // 2)


# This is deliberately data rather than coordinates dispersed through the builders.  The checker
# imports it and proves that every piece has a programme and every funerary object belongs to one
# of these extents.  Moving a room therefore moves the composition it owns.
TOMB_ROOM_PROGRAM = {
    "centre": (
        TombRoom("hall_of_names", (10, 5, 36, 41), "z"),
        TombRoom("treasury", (3, 17, 10, 27), "z"),
    ),
    "approach": (
        TombRoom("descent", (4, 1, 12, 20), "z"),
        TombRoom("antechamber", (2, 19, 14, 31), "z"),
    ),
    "wing": (
        TombRoom("burial", (8, 6, 38, 36), "z"),
        TombRoom("treasury", (2, 13, 9, 23), "x"),
        TombRoom("serdab", (37, 13, 44, 23), "x"),
    ),
    "gallery": (
        TombRoom("dynastic_cloister", (3, 11, 43, 43), "z"),
        TombRoom("treasure_vault", (15, 2, 31, 10), "z"),
    ),
}


def room_point(room, lateral=0, longitudinal=0):
    """Return a point in room-local coordinates; +longitudinal follows the room axis."""
    cx, cz = room.centre
    if room.axis == "z":
        return cx + lateral, cz + longitudinal
    return cx + longitudinal, cz + lateral


def register_band(p, room, y=7, interval=4):
    """Run one legible memorial register around a room instead of stippling its walls."""
    x0, z0, x1, z1 = room.extent
    polished = B("alfheim:ivory_livingrock_polished")
    carved = B("alfheim:moonstone_livingrock_carved")
    for x in range(x0 + 1, x1):
        p.set(x, y - 1, z0, polished)
        p.set(x, y + 1, z0, polished)
        p.set(x, y - 1, z1, polished)
        p.set(x, y + 1, z1, polished)
        motif = B("alfheim:memorial_carving", facing="south" if (x - x0) % interval == 0 else "north")
        p.set(x, y, z0, motif if (x - x0) % interval == 0 else carved)
        p.set(x, y, z1, B("alfheim:memorial_carving", facing="north")
              if (x - x0) % interval == 0 else carved)
    for z in range(z0 + 1, z1):
        p.set(x0, y - 1, z, polished)
        p.set(x0, y + 1, z, polished)
        p.set(x1, y - 1, z, polished)
        p.set(x1, y + 1, z, polished)
        p.set(x0, y, z, B("alfheim:memorial_carving", facing="east")
              if (z - z0) % interval == 0 else carved)
        p.set(x1, y, z, B("alfheim:memorial_carving", facing="west")
              if (z - z0) % interval == 0 else carved)


def corbelled_burial_vault(p, room, wall):
    """A stepped beehive crown: Celtic massing above an Egyptian axial chamber."""
    x0, z0, x1, z1 = room.extent
    for lift, inset in enumerate((0, 1, 2, 3, 5)):
        y = 14 + lift
        for x in range(x0 + inset, x1 - inset + 1):
            p.set(x, y, z0 + inset, wall)
            p.set(x, y, z1 - inset, wall)
        for z in range(z0 + inset + 1, z1 - inset):
            p.set(x0 + inset, y, z, wall)
            p.set(x1 - inset, y, z, wall)


def chamfer_burial_chamber(p, room, wall, cut=6):
    """Turn the broad burial rectangle into a stepped octagon with carved diagonal faces."""
    x0, z0, x1, z1 = room.extent
    polished = B("alfheim:ivory_livingrock_polished")
    carved = B("alfheim:moonstone_livingrock_carved")
    for u in range(cut + 1):
        for v in range(cut - u):
            for x, z in ((x0 + u, z0 + v), (x1 - u, z0 + v),
                         (x0 + u, z1 - v), (x1 - u, z1 - v)):
                box(p, x, 3, z, x, 13, z, wall)
        v = cut - u
        for i, (x, z) in enumerate(((x0 + u, z0 + v), (x1 - u, z0 + v),
                                    (x0 + u, z1 - v), (x1 - u, z1 - v))):
            p.set(x, 6, z, polished)
            p.set(x, 7, z, carved if u % 2 else
                  B("alfheim:memorial_carving", facing="east" if i % 2 == 0 else "west"))
            p.set(x, 8, z, polished)


def furnish_burial(p, room):
    """Compose the entire grave from the burial extent and its axis."""
    cx, cz = room.centre
    head_x, head_z = room_point(room, 0, -3)
    # The grave is sunk one course below the chamber floor and set on a continuous court-stone dais.
    box(p, cx - 3, 2, cz - 5, cx + 3, 2, cz + 4, B("minecraft:smooth_quartz"))
    sarcophagus(p, head_x, 3, head_z, "north")
    back_x, back_z = room_point(room, 0, -13)
    funerary_tapestry(p, back_x, 6, back_z, "south")
    for lateral in (-5, 5):
        x, z = room_point(room, lateral, -5)
        funerary_statue(p, x, 3, z, "south")


def raised_sarcophagus_dais(p, room, lateral, longitudinal):
    """Set one ancestor on a raised quartz dais with a carved plinth and stair apron."""
    x, z = room_point(room, lateral, longitudinal)
    quartz = B("minecraft:smooth_quartz")
    carved = B("alfheim:moonstone_livingrock_carved")
    box(p, x - 2, 3, z - 1, x + 2, 3, z + 3, quartz)
    for xx in range(x - 1, x + 2):
        p.set(xx, 4, z - 1, carved)
    for zz in range(z, z + 3):
        p.set(x - 2, 3, zz, stair("minecraft:smooth_quartz_stairs", "east"))
        p.set(x + 2, 3, zz, stair("minecraft:smooth_quartz_stairs", "west"))
    sarcophagus(p, x, 4, z, "north")


def tomb_breach(p, room, side="south"):
    """Place debris as a trail from a specific forced threshold, never as floor noise."""
    cx, cz = room.centre
    if side == "south":
        positions = ((cx - 1, room.extent[3] - 1), (cx, room.extent[3] - 2),
                     (cx + 1, room.extent[3] - 3), (cx, room.extent[3] - 5))
    else:
        positions = ((cx, cz),)
    for i, (x, z) in enumerate(positions):
        p.set(x, 3, z, B("alfheim:tomb_debris", facing="east" if i % 2 else "north"))


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
    cx, cz = sx // 2, sz // 2
    hall, treasury = TOMB_ROOM_PROGRAM["centre"]
    x0, z0, x1, z1 = hall.extent
    # A high north/south nave crossed by a much lower sealed transept gives the hub a
    # cruciform footprint. Unowned corners remain native rock instead of becoming a 47x47 box.
    vaulted_range_z(p, x0, z0, x1, z1, wall, floor, 11, 6)
    vaulted_range_x(p, 1, cz - 4, sx - 2, cz + 4, wall, floor, 8, 4)
    # Union the two ranges into one crossing: the transept's side walls must not survive
    # across the nave as two arbitrary screens.
    box(p, cx - 4, 3, cz - 4, cx + 4, 10, cz + 4, AIR)
    box(p, cx - 4, 2, cz - 4, cx + 4, 2, cz + 4, floor)
    box(p, cx - 3, 2, z0 + 1, cx + 3, 2, z1 - 1, B("minecraft:smooth_quartz"))

    # One processional entrance, on the north.  The other three jigsaw branches begin behind
    # royal seals, so the centre reads as a hall with an end rather than a four-way station.
    box(p, cx - 3, 3, 0, cx + 3, 10, z0, AIR)
    box(p, cx - 3, 3, z1, cx + 3, 10, sz - 1, AIR)
    box(p, 0, 3, cz - 3, x0, 10, cz + 3, AIR)
    box(p, x1, 3, cz - 3, sx - 1, 10, cz + 3, AIR)

    # A regular double colonnade creates the Hall of Names' long visual cadence.
    for z in range(z0 + 5, z1 - 3, 7):
        for x in (x0 + 5, x1 - 6):
            box(p, x, 3, z, x + 1, 13, z + 1, B("feywild:elven_quartz_pillar", axis="y"))
            funerary_statue(p, x + (1 if x < cx else 0), 3, z + 2,
                            "east" if x < cx else "west")
    register_band(p, hall, 7, 5)
    funerary_tapestry(p, cx, 6, z0, "south")
    for z in (14, 32):
        alcove_x(p, x0, z, 4, "east", wall, "alfheim:ivory_livingrock_stairs",
                 B("alfheim:mana_glass_light"))

    # Royal triforium: stairs reach a bracketed gallery around the processional hall.
    gantry_rect(p, x0 + 1, z0 + 1, x1 - 1, z1 - 1, 10, "alfheim:ivory_livingrock_slab",
                B("alfheim:moonstone_livingrock_wall"),
                B("feywild:elven_quartz_pillar", axis="y"))
    stair_flight_z(p, x0 + 2, z0 + 2, 3, 8, 2, "alfheim:ivory_livingrock_stairs", "south")
    stair_flight_z(p, x1 - 3, z1 - 2, 3, 8, 2, "alfheim:ivory_livingrock_stairs", "north")
    for z in (10, 18, 26, 34):
        pointed_arch_z(p, cx, z, 3, 8, 15, 2, wall, "alfheim:ivory_livingrock_stairs")

    # The sole relic sits in a one-door treasury off the hall, not in the middle of traffic.
    tx0, tz0, tx1, tz1 = treasury.extent
    hollow(p, tx0, 2, tz0, tx1, 10, tz1, wall)
    box(p, tx0 + 1, 3, tz0 + 1, tx1 - 1, 8, tz1 - 1, AIR)
    box(p, tx1, 3, cz - 1, x0, 6, cz + 1, AIR)
    chest(p, tx0 + 2, 3, cz, "east", "elder_kings_relic")
    for z in (tz0 + 2, tz1 - 2):
        box(p, tx0, 4, z, tx0, 7, z, B("alfheim:mana_glass_light"))

    cornice_rect(p, x0, z0, x1, z1, 17, "alfheim:ivory_livingrock_stairs",
                 "alfheim:ivory_livingrock_slab")
    grave_door_bay(p, cx + 1, 3, z1, "north")
    grave_door_bay(p, x0, 3, cz + 1, "east")
    grave_door_bay(p, x1, 3, cz - 1, "west")
    centre_jigsaws(p, "elder_kings_tomb")
    return p


def tomb_approach(size, seed):
    p = Piece(*size)
    sx, _, sz = size
    wall, floor = B("alfheim:ivory_livingrock_bricks"), B("alfheim:moonstone_livingrock_polished")
    cx = sx // 2
    descent, antechamber = TOMB_ROOM_PROGRAM["approach"]
    # Three overlapping vaulted tubes widen and rise toward the antechamber. Their stepped
    # exterior reads as successive construction campaigns rather than one corridor cuboid.
    vaulted_range_z(p, 5, 0, 11, 10, wall, floor, 8, 3)
    vaulted_range_z(p, 4, 8, 12, 21, wall, floor, 9, 4)
    vaulted_range_z(p, 2, 19, 14, 32, wall, floor, 10, 4)
    # The ceiling and walls compress toward the centre while three broad stair courses descend.
    # Both jigsaw mouths stay at y=3; the processional floor rises only inside the piece.
    box(p, cx - 2, 3, 0, cx + 2, 8, 2, AIR)
    box(p, cx - 3, 3, sz - 3, cx + 3, 10, sz - 1, AIR)
    for z in range(2, sz - 2):
        lift = 2 if z < 8 else 1 if z < 19 else 0
        half = 2 if z < 8 else 3 if z < 19 else 5
        for x in range(cx - half, cx + half + 1):
            p.set(x, 3 + lift, z, B("alfheim:silvermist_livingrock_polished"))
            box(p, x, 4 + lift, z, x, 10 - lift, z, AIR)
    ax0, az0, ax1, az1 = antechamber.extent
    box(p, ax0, 2, az0, ax1, 2, az1, B("minecraft:smooth_quartz"))
    box(p, ax0 + 1, 3, az0 + 1, ax1 - 1, 9, az1 - 1, AIR)
    register_band(p, antechamber, 7, 4)
    for z in (7, 25):
        box(p, 2, 3, z, 4, 10, z + 4, B("feywild:elven_quartz_brick"))
        box(p, sx - 5, 3, z, sx - 3, 10, z + 4, B("feywild:elven_quartz_brick"))
    for z in (3, 9, 15, 21, 27):
        pointed_arch_z(p, cx, z, 3, 5, 11, 2, wall, "alfheim:ivory_livingrock_stairs")
    for z in (22, 28):
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
    cx = sx // 2
    burial, treasury, serdab = TOMB_ROOM_PROGRAM["wing"]
    x0, z0, x1, z1 = burial.extent
    octagonal_rotunda(p, burial.centre[0], burial.centre[1], 15, wall, floor, 12, 5)
    vaulted_range_z(p, 19, 34, 27, sz - 1, wall, floor, 9, 4)
    vaulted_range_x(p, 34, 27, sx - 1, 33, wall, floor, 8, 3)
    # Open the entrance neck through the rotunda overlap; its surviving end wall previously
    # stood two blocks in front of the intended grave seal.
    box(p, cx - 3, 3, 33, cx + 3, 10, sz - 1, AIR)
    box(p, cx - 3, 2, 34, cx + 3, 2, sz - 2, floor)
    box(p, 34, 3, 28, sx - 1, 9, 32, AIR)
    furnish_burial(p, burial)
    octagonal_register_band(p, burial.centre[0], burial.centre[1], 15, 7, 4)

    # The upper walk follows the eight faces; it no longer redraws a square inside the rotunda.
    octagonal_ambulatory(p, burial.centre[0], burial.centre[1], 15, 10)
    stair_flight_z(p, 14, 31, 3, 8, 2,
                   "alfheim:ivory_livingrock_stairs", "north")
    stair_flight_z(p, 28, 31, 3, 8, 2,
                   "alfheim:ivory_livingrock_stairs", "north")
    for z in (11, 19, 27, 33):
        pointed_arch_z(p, cx, z, 9, 7, 7, 1, wall, "alfheim:ivory_livingrock_stairs")

    # Treasury: one doorway, offering benches, but no duplicate relic chest.
    tx0, tz0, tx1, tz1 = treasury.extent
    hollow(p, tx0, 2, tz0, tx1, 10, tz1, wall)
    box(p, tx0 + 1, 3, tz0 + 1, tx1 - 1, 8, tz1 - 1, AIR)
    box(p, x0, 3, treasury.centre[1] - 1, tx1, 6, treasury.centre[1] + 1, AIR)
    for z in range(tz0 + 2, tz1 - 1, 3):
        p.set(tx0 + 1, 3, z, B("minecraft:smooth_quartz"))
        p.set(tx0 + 1, 4, z, B("alfheim:mana_glass_light"))
    box(p, tx0, 4, tz0 + 4, tx0, 7, tz0 + 6, B("alfheim:mana_glass_light"))

    # Serdab: wholly sealed except for a narrow sight-slit into the burial chamber.
    sx0, sz0, sx1, sz1 = serdab.extent
    hollow(p, sx0, 2, sz0, sx1, 10, sz1, wall)
    box(p, sx0 + 1, 3, sz0 + 1, sx1 - 1, 8, sz1 - 1, AIR)
    p.set(sx0, 6, serdab.centre[1], B("alfheim:ivory_livingrock_wall"))
    funerary_statue(p, serdab.centre[0], 3, serdab.centre[1], "west")
    box(p, sx1, 4, sz0 + 3, sx1, 7, sz1 - 3, B("alfheim:mana_glass_shadow"))
    # The dynastic crypt folds sideways from the royal precinct. This keeps thirteen pieces inside
    # Minecraft 1.20.1's hard 128-block jigsaw reach while making the complex a dense monastery-
    # like pinwheel instead of one impossibly long cross.
    box(p, 34, 3, 28, sx - 1, 9, 32, AIR)
    grave_door_bay(p, cx - 1, 3, z1, "south")
    tomb_breach(p, burial, "south")
    tomb_wing_jigsaws(p)
    return p


def tomb_gallery(size, seed):
    """A hypostyle generation crypt: cloister aisles, burial rows and a sealed hoard."""
    p = Piece(*size)
    sx, _, sz = size
    wall = B("alfheim:ivory_livingrock_bricks")
    floor = B("alfheim:moonstone_livingrock_polished")
    cloister, vault = TOMB_ROOM_PROGRAM["gallery"]
    x0, z0, x1, z1 = cloister.extent
    # A narrow processional spine intersects four separated generation transepts. The native
    # rock between them remains intact, so the plan reads as an excavated comb of chapels.
    vaulted_range_z(p, 19, 1, 27, sz - 1, wall, floor, 10, 4)
    generation_z = (15, 23, 31, 39)
    for z in generation_z:
        vaulted_range_x(p, x0, z - 3, x1, z + 3, wall, floor, 9, 4)
    vaulted_range_z(p, 15, 1, 31, 11, wall, floor, 10, 5)
    box(p, 20, 3, z1, 26, 10, sz - 1, AIR)

    # Central monastic nave and paired colonnades.  The raised centre path lets the repeated
    # ancestor daises read as side chapels rather than blocks scattered over one floor.
    box(p, 20, 3, z0 + 2, 26, 3, z1 - 2, B("minecraft:smooth_quartz"))
    for z in range(z0 + 5, z1 - 2, 6):
        for x in (18, 28):
            box(p, x, 3, z, x + 1, 12, z + 1, B("minecraft:quartz_pillar", axis="y"))
            box(p, x - 1, 3, z - 1, x + 2, 3, z + 2, B("minecraft:chiseled_quartz_block"))
        pointed_arch_z(p, 23, z, 9, 5, 8, 1, wall, "alfheim:ivory_livingrock_stairs")

    # Four family lines, four generations deep: sixteen raised graves per gallery, sixty-four
    # around the assembled complex, plus the four sovereign burials in the royal precincts.
    for lateral in (-15, -9, 9, 15):
        for longitudinal in (-12, -4, 4, 12):
            raised_sarcophagus_dais(p, cloister, lateral, longitudinal)
    for z in generation_z:
        bay = TombRoom("generation_bay", (x0, z - 3, x1, z + 3), "x")
        register_band(p, bay, 7, 5)
        alcove_x(p, x0, z - 1, 4, "east", wall, "alfheim:ivory_livingrock_stairs",
                 B("alfheim:mana_glass_light"))
        alcove_x(p, x1, z + 1, 4, "west", wall, "alfheim:ivory_livingrock_stairs",
                 B("alfheim:mana_glass_light"))

    # Every transept builder contributes side-wall and register courses. Cut one continuous
    # processional nave after all four are present so none of those courses becomes a barrier.
    box(p, 20, 3, z0, 26, 9, z1, AIR)
    box(p, 20, 3, z0 + 2, 26, 3, z1 - 2, B("minecraft:smooth_quartz"))

    # Cloister walks above both burial aisles, with stairs at opposite corners and a repeated
    # cornice tying the rows together vertically.
    for z in generation_z:
        gantry_rect(p, x0 + 1, z - 2, x1 - 1, z + 2, 10,
                    "alfheim:ivory_livingrock_slab", B("alfheim:moonstone_livingrock_wall"),
                    B("minecraft:quartz_pillar", axis="y"))
        cornice_rect(p, x0, z - 3, x1, z + 3, 12,
                     "alfheim:ivory_livingrock_stairs", "alfheim:ivory_livingrock_slab")
    stair_flight_z(p, x0 + 2, generation_z[-1] + 1, 3, 8, 2,
                   "alfheim:ivory_livingrock_stairs", "north")
    stair_flight_z(p, x1 - 3, generation_z[0] - 1, 3, 8, 2,
                   "alfheim:ivory_livingrock_stairs", "south")

    # A sealed treasury terminates the nave.  Wealth is architecture first: stepped hoards and
    # precious-metal plinths, with two coffers supplementing rather than replacing the spectacle.
    vx0, vz0, vx1, vz1 = vault.extent
    box(p, vx0 + 1, 3, vz0 + 1, vx1 - 1, 9, vz1 - 1, AIR)
    box(p, 20, 3, vz1, 26, 9, vz1 + 2, AIR)
    grave_door_bay(p, 23, 3, vz1, "south")
    treasure = (
        ("minecraft:gold_block", 4),
        ("botania:manasteel_block", 3),
        ("botania:elementium_block", 2),
        ("botania:mana_diamond_block", 1),
        ("botania:dragonstone_block", 1),
        ("botania:terrasteel_block", 1),
    )
    for i, (name, height) in enumerate(treasure):
        x = vx0 + 2 + (i % 3) * 4
        z = vz0 + 2 + (i // 3) * 4
        box(p, x, 3, z, x + 1, 3 + height - 1, z + 1, B(name))
        p.set(x, 3 + height, z, slab("minecraft:smooth_quartz_slab", "top"))
    chest(p, vx0 + 2, 3, vz1 - 2, "south", "elder_kings_treasure")
    chest(p, vx1 - 2, 3, vz1 - 2, "south", "elder_kings_treasure")
    funerary_tapestry(p, vault.centre[0], 6, vz0, "south")

    tomb_gallery_jigsaw(p)
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
    "elder_kings_tomb": {"centre": tomb_centre, "approach": tomb_approach,
                          "wing": tomb_wing, "gallery": tomb_gallery},
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


def tomb_treasure_loot():
    """Secondary dynastic wealth; spectacular, useful, but not the tomb's unique relic."""
    entries = (
        ("minecraft:gold_ingot", 12, 4, 12),
        ("botania:manasteel_ingot", 10, 3, 9),
        ("botania:mana_pearl", 5, 1, 3),
        ("botania:mana_diamond", 4, 1, 2),
        ("botania:elementium_ingot", 2, 1, 2),
        ("botania:dragonstone", 1, 1, 1),
    )
    return {"type": "minecraft:chest", "random_sequence": f"{NS}:chests/elder_kings_treasure",
            "pools": [{"rolls": {"type": "minecraft:uniform", "min": 3.0, "max": 6.0},
                       "bonus_rolls": 0.0, "entries": [
                           {"type": "minecraft:item", "name": name, "weight": weight,
                            "functions": [{"function": "minecraft:set_count",
                                           "count": {"min": float(lo), "max": float(hi)}}]}
                           for name, weight, lo, hi in entries]}]}


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
        dress=dict(corbel=0.22, conduit=0.45, sockets=3, sconce=0.60, sconce_spacing=6),
        settle=dict(rubble=0.10, reach=3, weathering=0.08, seep="dust", seep_rate=0.09,
                    roots=0.09, webs=0.02)),
    # A SEALED TOMB IS NOT A WORKED MINE, AND THE FIRST PASS DID NOT ACT LIKE IT. The tomb ran
    # roots at 0.10 -- higher than the quarry that is still being dug -- and damp seep at 0.10,
    # in a chamber whose entire architectural purpose is to stay dry and shut. Measured: the wing
    # carried 644 ingress, 364 debris and 158 wear blocks, 10.9% detail over FORTY block ids, so
    # the seventeen bespoke funerary blocks were outnumbered by residue roughly forty to one and
    # a memorial carving read as one more speckle rather than as an ornament. That is the owner's
    # complaint on 2026-09-12 -- "burying the detail under a smattering of random blocks" -- and
    # it is a budget, not a taste. Webs stay: cobweb is the one residue that reads as funerary.
    # The ornament itself is not fixed by turning noise down; see TOMB_ARCHITECTURE.md.
    "elder_kings_tomb": dict(
        dress=dict(corbel=0.25, conduit=0.55, sockets=4, sconce=0.70, sconce_spacing=5),
        settle=dict(rubble=0.03, reach=2, weathering=0.03, seep="damp", seep_rate=0.03,
                    roots=0.02, webs=0.05)),
    "faultwork": dict(
        dress=dict(corbel=0.20, conduit=0.60, sockets=5, sconce=0.55, sconce_spacing=6),
        settle=dict(rubble=0.13, reach=3, weathering=0.10, seep="damp", seep_rate=0.11,
                    roots=0.13, webs=0.04)),
}

# The floor of every authored room sits at y=3; the shell and its bedding are below that.
DETAIL_GROUND = 3

# The headworks is the half of the complex a player can see without caving to Y -40, so it is
# the piece that has to advertise what is underneath it. It is above ground, so the light can
# use wall brackets and the weather is rain rather than groundwater.
HEADWORKS_KIT = dict(
    stone="alfheim:cracked_livingrock", brick="alfheim:ivory_livingrock_bricks",
    floor="alfheim:ivory_livingrock_polished", accent="alfheim:moonstone_livingrock_carved",
    stairs="alfheim:ivory_livingrock_stairs", slab="alfheim:ivory_livingrock_slab",
    wall="alfheim:ivory_livingrock_wall", pillar="botania:dreamwood_log",
    crystal="alfheim:rootglass_cluster", timber="botania:dreamwood_log",
    plank="botania:dreamwood_planks", fence="botania:dreamwood_fence",
    light="minecraft:lantern",
    rubble=["minecraft:gravel", "alfheim:cracked_livingrock", "minecraft:cobblestone"])


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
            counts = detail_family(piece, fid, seed)
            # Collapse and rubble passes here remove blocks without asking what rested on
            # them; sweep anything they left touching nothing on any face.
            piece.prune_orphans()
            path = os.path.join(STRUCT, fid, role + ".nbt")
            nbt_expected[path] = piece.to_nbt()
            if not check:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                nbt.save(path, "", piece.to_nbt())
            cen = sd.census(piece)
            print(f"  {fid:18} {role:9} {size[0]}x{size[1]}x{size[2]}  "
                  f"{len(piece.blocks):6} blocks  detail {cen['share'] * 100:4.1f}% "
                  f"over {cen['names']:>2} ids  "
                  + ' '.join(f'{k}={v}' for k, v in sorted(counts.items()) if v))

        base = f"{NS}:deepworks_archaeology/{fid}"
        for role in family["pieces"]:
            path = os.path.join(DATA, "worldgen", "template_pool", "deepworks_archaeology", fid,
                                role + ".json")
            json_out[path] = single_pool(f"{base}/{role}", f"{base}/{role}")
        lo, hi = family["depth"]
        has_gallery = "gallery" in family["pieces"]
        json_out[os.path.join(DATA, "worldgen", "structure", fid + ".json")] = {
            "type": "minecraft:jigsaw", "biomes": manifest["biomes"],
            "step": "underground_structures", "terrain_adaptation": "none",
            "start_pool": f"{base}/centre", "size": 3 if has_gallery else 2,
            "max_distance_from_center": 128 if has_gallery else 116,
            "start_height": {"type": "minecraft:uniform",
                             "min_inclusive": {"absolute": lo},
                             "max_inclusive": {"absolute": hi}},
            "use_expansion_hack": False, "spawn_overrides": {}}
        json_out[os.path.join(DATA, "tags", "worldgen", "structure", fid + ".json")] = {
            "replace": False, "values": [f"{NS}:{fid}"]}

    # The headworks: two pieces, shared by all three families.
    for role, builder in HEADWORKS_BUILDERS.items():
        size = HEADWORKS_SIZES[role]
        assert max(size) <= MAX_AXIS
        seed = int(hashlib.sha1(f"headworks:{role}".encode()).hexdigest()[:8], 16)
        piece = builder(tuple(size), seed)
        kit = sd.Kit(**HEADWORKS_KIT)
        # Role-aware, because the two headworks pieces are not the same kind of place. The
        # shaft is a vertical drop with a ladder in it: what it carries is bracing, conduit
        # down the wall and light at every landing, not room articulation.
        deep_shaft = (role == "shaft")
        counts = sd.dress(piece, seed, kit, ground=1,
                          corbel=0.80 if deep_shaft else 0.30,
                          opening=0.75 if deep_shaft else 0.50,
                          conduit=0.80 if deep_shaft else 0.55,
                          sockets=6 if deep_shaft else 2,
                          sconce=0.85 if deep_shaft else 0.70, sconce_spacing=3)
        # The shaft is a hole in the ground with a ladder in it: no rain reaches the bottom,
        # so its water arrives the same way the complex below it gets its water.
        #
        # It also gets the heavier decay, and that is not a metric dodge. A 4x4 chimney has
        # no floor to furnish, no overhang to corbel and no wall run long enough to carry a
        # conduit -- corbels, conduits and openings all returned 0 on it. What three hundred
        # years actually leaves on the inside of an abandoned shaft is root, drip and web
        # down every face, and that is the one layer its geometry can carry.
        counts.update(sd.aftermath(piece, seed, kit, ground=1, rubble=0.12, reach=2,
                                   weathering=0.12, seep="damp",
                                   seep_rate=0.34 if deep_shaft else 0.12,
                                   roots=0.30 if deep_shaft else 0.10, hang="drip",
                                   roofed_ok=deep_shaft,
                                   webs=0.12 if deep_shaft else 0.03))
        piece.prune_orphans()
        path = os.path.join(STRUCT, "headworks", role + ".nbt")
        nbt_expected[path] = piece.to_nbt()
        if not check:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            nbt.save(path, "", piece.to_nbt())
        cen = sd.census(piece)
        print(f"  {'headworks':18} {role:9} {size[0]}x{size[1]}x{size[2]}  "
              f"{len(piece.blocks):6} blocks  detail {cen['share'] * 100:4.1f}% "
              f"over {cen['names']:>2} ids  "
              + ' '.join(f'{k}={v}' for k, v in sorted(counts.items()) if v))

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
        # PROJECTION IS ADDITIVE, SO THIS OFFSET MUST BE ZERO AND NOT above_bottom. JigsawPlacement
        # adds getFirstFreeHeight() to start_height; `above_bottom: 0` resolves to Y -64, so the
        # winding gear was being set 64 blocks BELOW the surface it is the entrance to -- and below
        # the floor of the world wherever the ground sat under Y 0, where nothing it writes is
        # kept. Measured in server/void-margin-20260912-151345: 7 of 8 starts between Y -97 and
        # Y -60. That is the unfixed half of the 2026-09-07 field report quoted above; the grid
        # pitch was the half that got found. `absolute: 0` is what "stands on the surface" means
        # once the heightmap is already in the sum.
        "start_height": {"absolute": 0},
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
    json_out[os.path.join(DATA, "loot_tables", "chests", "elder_kings_treasure.json")] = tomb_treasure_loot()
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
