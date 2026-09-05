"""Generate the Wave-1 Common Residential Quarter and its reusable set-dressing vocabulary.

Authority:
  alfheim_reclaimed_design/ANCIENT_ELVEN_STRUCTURE_ROSTER.md
  tools/ancient_district_manifest.json
  tools/ancient_set_dressing_manifest.json

The district is one random-spread anchor family. Subordinate homes, roads, cistern/trace edges
and the Last Order burial edge are jigsaw members and never receive independent structure sets.

Every piece remains inside the existing 48-block Piece boundary. The reusable set-dressing helpers
encode the civilization-remnant vocabulary (masonry/timber debris, skeletal and elven remains,
abandoned objects, broken civic/magical infrastructure) directly into structure generation rather
than hand-patching generated NBT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402
from structure_nbt import ADAPTATION_MARGIN, MAX_AXIS, Piece  # noqa: E402

NS = "alfheim"
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "kubejs" / "data" / NS
STRUCT = DATA / "structures" / "ancient" / "common_residential"
POOL = DATA / "worldgen" / "template_pool" / "ancient" / "common_residential"
HOME_BIOMES = [
    "alfheim:ashen_grove", "alfheim:bloomfall_vale", "alfheim:decayed_mire",
    "alfheim:hollow_marches", "alfheim:infested_warren", "alfheim:mana_fen",
    "alfheim:scorchfell", "alfheim:silverbark_wood", "alfheim:starved_reach",
    "alfheim:sundered_highlands",
    "mythicbotany:alfheim_hills", "mythicbotany:alfheim_plains",
    "mythicbotany:dreamwood_forest", "mythicbotany:golden_fields",
]
SEED = 20260905
STONE = ("feywild:elven_quartz_brick", None)
CRACKED = ("feywild:elven_quartz_cracked_brick", None)
MOSSY = ("feywild:elven_quartz_mossy_brick", None)
FLOOR = ("feywild:elven_quartz_polished", None)
PILLAR = ("feywild:elven_quartz_pillar", {"axis": "y"})
DREAM = ("botania:dreamwood_planks", None)
DREAM_LOG_Y = ("botania:dreamwood_log", {"axis": "y"})
DREAM_LOG_X = ("botania:dreamwood_log", {"axis": "x"})
DREAM_LOG_Z = ("botania:dreamwood_log", {"axis": "z"})
LIVING = ("botania:livingrock_bricks", None)
SOURCE = ("ars_nouveau:sourcestone", None)
AIR = ("minecraft:air", None)
WATER = ("minecraft:water", {"level": "0"})


def B(name, **props):
    return (name, {k: ("true" if v is True else "false" if v is False else str(v))
                   for k, v in props.items()} if props else None)


def box(p, x0, y0, z0, x1, y1, z1, block):
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for z in range(min(z0, z1), max(z0, z1) + 1):
                p.set(x, y, z, block)


def perimeter(p, x0, y0, z0, x1, y1, z1, block):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            p.set(x, y, z0, block); p.set(x, y, z1, block)
    for z in range(z0 + 1, z1):
        for y in range(y0, y1 + 1):
            p.set(x0, y, z, block); p.set(x1, y, z, block)


# ---------------------------------------------------------------- set-dressing primitives

def stone_debris(p, x, y, z, seed, radius=4):
    """Directional rubble fan: collapsed masonry has a source and a fall direction."""
    rng = random.Random(seed)
    dx, dz = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
    for i in range(radius * 3):
        run = rng.randint(0, radius)
        side = rng.randint(-max(1, radius // 2), max(1, radius // 2))
        px = x + dx * run + (side if dz else 0)
        pz = z + dz * run + (side if dx else 0)
        blk = rng.choice([CRACKED, CRACKED, ("minecraft:gravel", None),
                          ("minecraft:calcite", None)])
        p.set(px, y + (1 if rng.random() < 0.12 else 0), pz, blk)
    axis = DREAM_LOG_X if dx else DREAM_LOG_Z
    for i in range(3):
        p.set(x + dx * i, y + 1, z + dz * i, axis)


def wood_debris(p, x, y, z, seed, span=5):
    rng = random.Random(seed)
    axis_x = rng.random() < 0.5
    beam = DREAM_LOG_X if axis_x else DREAM_LOG_Z
    for i in range(span):
        p.set(x + (i if axis_x else 0), y, z + (0 if axis_x else i), beam)
    for _ in range(5):
        p.set(x + rng.randint(-2, span + 1), y, z + rng.randint(-2, span + 1), DREAM)


def skeletal_remains(p, x, y, z, seed, cloth=False):
    """Low-cost block-state remains; no persistent entity by default."""
    rng = random.Random(seed)
    p.set(x, y, z, B("minecraft:skeleton_skull", rotation=rng.randrange(16)))
    axis = rng.choice(["x", "z"])
    bone = B("minecraft:bone_block", axis=axis)
    for i in range(1, 3):
        p.set(x + (i if axis == "x" else 0), y, z + (i if axis == "z" else 0), bone)
    if cloth:
        color = rng.choice(["green", "purple", "light_blue"])
        p.set(x, y, z + 1, (f"minecraft:{color}_carpet", None))
        p.set(x + 1, y, z + 1, ("feywild:elven_quartz_brick_slab",
                                {"type": "bottom", "waterlogged": "false"}))


def elven_remains(p, x, y, z, seed, role="civilian"):
    """Distinct elven-context remains: body + surviving cloth/professional residue."""
    skeletal_remains(p, x, y, z, seed, cloth=True)
    if role == "warden":
        p.set(x - 1, y, z, ("minecraft:iron_bars", None))
        p.set(x - 1, y, z + 1, ("minecraft:tripwire_hook", {"facing": "north", "attached": "false", "powered": "false"}))
    elif role == "healer":
        p.set(x - 1, y, z, ("minecraft:flower_pot", None))
        p.set(x - 1, y, z + 1, ("minecraft:cauldron", {"level": "1"}))
    else:
        p.set(x - 1, y, z, ("minecraft:flower_pot", None))


def abandoned_objects(p, x, y, z, seed, kind="household"):
    rng = random.Random(seed)
    if kind == "ration":
        p.set(x, y, z, B("minecraft:barrel", facing="up", open=False))
        p.set(x + 1, y, z, ("minecraft:cauldron", {"level": "1"}))
        p.set(x + 2, y, z, ("minecraft:flower_pot", None))
    elif kind == "work":
        p.set(x, y, z, ("minecraft:crafting_table", None))
        p.set(x + 1, y, z, B("minecraft:barrel", facing="up", open=False))
        p.set(x + 2, y, z, ("minecraft:anvil", {"facing": rng.choice(["north", "south"])}))
    else:
        p.set(x, y, z, B("minecraft:barrel", facing="up", open=False))
        p.set(x + 1, y, z, ("minecraft:flower_pot", None))
        p.set(x + 2, y, z, ("minecraft:lantern", {"hanging": "false", "waterlogged": "false"}))


def broken_infrastructure(p, x, y, z, seed, kind="mana"):
    rng = random.Random(seed)
    if kind == "water":
        box(p, x, y, z, x + 4, y, z + 1, LIVING)
        p.set(x + 2, y + 1, z, WATER)
        p.set(x + 3, y + 1, z, ("minecraft:gravel", None))
    elif kind == "waystone":
        box(p, x, y, z, x, y + 3, z, PILLAR)
        p.set(x, y + 2, z, ("minecraft:amethyst_block", None))
        p.set(x + 1, y, z, CRACKED)
    else:
        for i in range(6):
            p.set(x + i, y, z, SOURCE if i % 2 else LIVING)
        p.set(x + 2, y + 1, z, ("minecraft:amethyst_block", None))
        if rng.random() < 0.7:
            p.set(x + 3, y + 1, z, ("minecraft:sea_lantern", None))
        stone_debris(p, x + 4, y, z + 1, seed + 19, radius=2)


# ---------------------------------------------------------------- buildings

def shell_building(size, height, seed, door_width=3):
    sx, sy, sz = size
    p = Piece(sx, sy, sz)
    box(p, 1, 0, 1, sx - 2, 0, sz - 2, FLOOR)
    perimeter(p, 1, 1, 1, sx - 2, height, sz - 2, STONE)
    cx = sx // 2
    for x in range(cx - door_width // 2, cx + door_width // 2 + 1):
        for y in range(1, 4):
            p.set(x, y, sz - 2, AIR)
    rng = random.Random(seed)
    for x in range(2, sx - 2, 4):
        if rng.random() > 0.28:
            box(p, x, height + 1, 2, x, height + 1, sz - 3, DREAM_LOG_Z)
    for z in range(6, sz - 6, 8):
        for y in (3, 4):
            p.set(1, y, z, ("botania:elf_glass", None))
            p.set(sx - 2, y, z, ("botania:elf_glass", None))
    return p


def add_building_connector(p):
    p.jigsaw(p.size[0] // 2, 1, p.size[2] - 1,
             f"{NS}:residential_member_in", f"{NS}:residential_socket",
             "minecraft:empty", "south_up", joint="aligned")


def build_common_hall():
    p = shell_building((48, 28, 40), 12, SEED + 1, 5)
    for x in range(8, 40, 4):
        p.set(x, 1, 8, ("minecraft:campfire", {"lit": "false", "signal_fire": "false", "waterlogged": "false"}))
    for x in range(7, 41):
        if x % 3:
            p.set(x, 1, 16, ("botania:dreamwood_fence", None))
    abandoned_objects(p, 10, 1, 20, SEED + 10, "ration")
    abandoned_objects(p, 30, 1, 20, SEED + 11, "ration")
    broken_infrastructure(p, 19, 1, 4, SEED + 12, "mana")
    elven_remains(p, 14, 1, 17, SEED + 20, "civilian")
    elven_remains(p, 29, 1, 18, SEED + 21, "civilian")
    stone_debris(p, 38, 1, 6, SEED + 22, 4)
    c = 24
    p.jigsaw(c, 1, 0, f"{NS}:hall_north", f"{NS}:road_in", f"{NS}:ancient/common_residential/avenue_north", "north_up", joint="aligned")
    p.jigsaw(c, 1, 39, f"{NS}:hall_south", f"{NS}:road_in", f"{NS}:ancient/common_residential/avenue_south", "south_up", joint="aligned")
    p.jigsaw(0, 1, 20, f"{NS}:hall_west", f"{NS}:road_in", f"{NS}:ancient/common_residential/avenue_west", "west_up", joint="aligned")
    p.jigsaw(47, 1, 20, f"{NS}:hall_east", f"{NS}:road_in", f"{NS}:ancient/common_residential/avenue_east", "east_up", joint="aligned")
    return p


def build_avenue(terminal_pool, seed):
    p = Piece(16, 12, 48)
    for z in range(48):
        for x in range(4, 11):
            p.set(x, 0, z, FLOOR if (z + x) % 11 else CRACKED)
        p.set(3, 0, z, LIVING); p.set(11, 0, z, LIVING)
    broken_infrastructure(p, 5, 1, 20, seed + 1, "waystone")
    broken_infrastructure(p, 5, 1, 34, seed + 2, "water")
    wood_debris(p, 5, 1, 25, seed + 3, 4)
    p.jigsaw(8, 1, 47, f"{NS}:road_in", f"{NS}:hall_north", "minecraft:empty", "south_up", joint="aligned")
    p.jigsaw(8, 1, 0, f"{NS}:road_out", f"{NS}:terminal_in", terminal_pool, "north_up", joint="aligned")
    for z in (31, 12):
        p.jigsaw(0, 1, z, f"{NS}:residential_socket", f"{NS}:residential_member_in", f"{NS}:ancient/common_residential/residential", "west_up", joint="aligned")
        p.jigsaw(15, 1, z, f"{NS}:residential_socket", f"{NS}:residential_member_in", f"{NS}:ancient/common_residential/residential", "east_up", joint="aligned")
    return p


def build_row_house():
    p = shell_building((32, 24, 24), 10, SEED + 30)
    add_building_connector(p)
    box(p, 15, 1, 2, 15, 8, 21, STONE)
    abandoned_objects(p, 5, 1, 6, SEED + 31, "household")
    wood_debris(p, 20, 1, 7, SEED + 32)
    skeletal_remains(p, 9, 1, 16, SEED + 33, cloth=True)
    return p


def build_courtyard_home():
    p = shell_building((40, 24, 40), 9, SEED + 40)
    add_building_connector(p)
    box(p, 12, 1, 12, 27, 1, 27, ("minecraft:coarse_dirt", None))
    box(p, 18, 0, 18, 22, 0, 22, LIVING)
    box(p, 19, 1, 19, 21, 1, 21, WATER)
    p.set(14, 1, 14, ("minecraft:composter", {"level": "5"}))
    skeletal_remains(p, 25, 1, 25, SEED + 41, cloth=True)
    broken_infrastructure(p, 5, 1, 5, SEED + 42, "water")
    return p


def build_artisan_shop():
    p = shell_building((32, 24, 32), 10, SEED + 50)
    add_building_connector(p)
    abandoned_objects(p, 6, 1, 8, SEED + 51, "work")
    abandoned_objects(p, 20, 1, 8, SEED + 52, "work")
    broken_infrastructure(p, 8, 1, 21, SEED + 53, "mana")
    elven_remains(p, 18, 1, 20, SEED + 54, "civilian")
    return p


def build_kin_hall():
    p = shell_building((48, 28, 36), 12, SEED + 60, 5)
    add_building_connector(p)
    for z in (7, 13, 19):
        for x in range(6, 42, 6):
            p.set(x, 1, z, ("minecraft:green_carpet", None))
            p.set(x + 1, 1, z, ("minecraft:white_carpet", None))
    abandoned_objects(p, 9, 1, 26, SEED + 61, "ration")
    elven_remains(p, 28, 1, 18, SEED + 62, "civilian")
    elven_remains(p, 34, 1, 20, SEED + 63, "civilian")
    stone_debris(p, 40, 1, 7, SEED + 64, 4)
    return p


def terminal_connector(p):
    p.jigsaw(p.size[0] // 2, 1, p.size[2] - 1, f"{NS}:terminal_in", f"{NS}:road_out", "minecraft:empty", "south_up", joint="aligned")


def build_cistern():
    p = Piece(32, 20, 32)
    box(p, 2, 0, 2, 29, 0, 29, LIVING)
    perimeter(p, 3, 1, 3, 28, 6, 28, LIVING)
    box(p, 8, 0, 8, 23, 0, 23, ("minecraft:dark_prismarine", None))
    box(p, 9, 1, 9, 22, 2, 22, WATER)
    broken_infrastructure(p, 5, 1, 8, SEED + 70, "water")
    skeletal_remains(p, 25, 1, 15, SEED + 71, cloth=True)
    terminal_connector(p)
    return p


def build_trace():
    p = Piece(24, 12, 24)
    for x in range(2, 22):
        p.set(x, 0, 4, CRACKED)
        if x % 3: p.set(x, 0, 18, CRACKED)
    for z in range(5, 18):
        if z % 2: p.set(5, 0, z, CRACKED)
    stone_debris(p, 11, 0, 10, SEED + 80, 5)
    wood_debris(p, 4, 1, 14, SEED + 81, 5)
    broken_infrastructure(p, 8, 0, 5, SEED + 82, "mana")
    terminal_connector(p)
    return p


def build_mass_grave():
    p = Piece(48, 20, 48)
    for z in range(28, 48):
        for x in range(21, 27):
            p.set(x, 0, z, ("minecraft:coarse_dirt", None))
    for row, x0 in enumerate((5, 14, 23, 32)):
        box(p, x0, 0, 6, x0 + 5, 0, 30, ("minecraft:coarse_dirt", None))
        for z in range(8, 29, 5):
            skeletal_remains(p, x0 + 2, 1, z, SEED + 100 + row * 20 + z, cloth=row < 2)
            p.set(x0 + 5, 1, z, ("minecraft:oak_sign", {"rotation": str((row * 3) % 16), "waterlogged": "false"}))
    box(p, 39, 0, 8, 45, 0, 23, ("minecraft:coarse_dirt", None))
    for z in (10, 13, 16):
        skeletal_remains(p, 41 + (z % 2), 1, z, SEED + 150 + z, cloth=False)
    abandoned_objects(p, 7, 1, 37, SEED + 160, "work")
    wood_debris(p, 15, 1, 37, SEED + 161, 6)
    elven_remains(p, 11, 1, 39, SEED + 162, "healer")
    stone_debris(p, 36, 1, 35, SEED + 163, 4)
    terminal_connector(p)
    return p


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def pool(name, elements):
    return {
        "name": f"{NS}:ancient/common_residential/{name}",
        "fallback": "minecraft:empty",
        "elements": [{"weight": weight, "element": {
            "location": f"{NS}:ancient/common_residential/{loc}",
            "processors": "minecraft:empty",
            "projection": "rigid",
            "element_type": "minecraft:single_pool_element",
        }} for loc, weight in elements],
    }


def salt_for(name):
    return int(hashlib.sha1(name.encode()).hexdigest()[:7], 16)


def main():
    global ROOT, DATA, STRUCT, POOL
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-root", default=str(ROOT), help="repository-shaped output root; used by equality checks")
    args = ap.parse_args()
    ROOT = Path(args.output_root).resolve()
    DATA = ROOT / "kubejs" / "data" / NS
    STRUCT = DATA / "structures" / "ancient" / "common_residential"
    POOL = DATA / "worldgen" / "template_pool" / "ancient" / "common_residential"

    pieces = {
        "neighborhood_common_hall": build_common_hall(),
        "avenue_north": build_avenue(f"{NS}:ancient/common_residential/grave_terminal", SEED + 200),
        "avenue_south": build_avenue(f"{NS}:ancient/common_residential/cistern_terminal", SEED + 201),
        "avenue_east": build_avenue(f"{NS}:ancient/common_residential/trace_terminal", SEED + 202),
        "avenue_west": build_avenue(f"{NS}:ancient/common_residential/trace_terminal", SEED + 203),
        "common_row_house": build_row_house(),
        "courtyard_home": build_courtyard_home(),
        "artisan_house_shop": build_artisan_shop(),
        "extended_kin_hall": build_kin_hall(),
        "district_cistern": build_cistern(),
        "collapsed_trace_field": build_trace(),
        "district_mass_grave": build_mass_grave(),
    }
    for name, p in pieces.items():
        assert all(v <= MAX_AXIS for v in p.size), (name, p.size)
        assert p.dropped == 0, f"{name}: {p.dropped} out-of-bounds placements"
        path = STRUCT / f"{name}.nbt"
        nbt.save(path, "", p.to_nbt())

    pools = {
        "start": pool("start", [("neighborhood_common_hall", 1)]),
        "avenue_north": pool("avenue_north", [("avenue_north", 1)]),
        "avenue_south": pool("avenue_south", [("avenue_south", 1)]),
        "avenue_east": pool("avenue_east", [("avenue_east", 1)]),
        "avenue_west": pool("avenue_west", [("avenue_west", 1)]),
        "residential": pool("residential", [("common_row_house", 6), ("courtyard_home", 3), ("artisan_house_shop", 3), ("extended_kin_hall", 2)]),
        "grave_terminal": pool("grave_terminal", [("district_mass_grave", 1)]),
        "cistern_terminal": pool("cistern_terminal", [("district_cistern", 1)]),
        "trace_terminal": pool("trace_terminal", [("collapsed_trace_field", 1)]),
    }
    for name, obj in pools.items():
        write_json(POOL / f"{name}.json", obj)

    write_json(DATA / "worldgen" / "structure" / "common_residential_quarter.json", {
        "type": "minecraft:jigsaw", "biomes": f"#{NS}:has_common_residential_quarter",
        "step": "surface_structures", "terrain_adaptation": "beard_thin",
        "start_pool": f"{NS}:ancient/common_residential/start", "size": 3,
        "max_distance_from_center": 128 - ADAPTATION_MARGIN["beard_thin"],
        "start_height": {"absolute": 0}, "project_start_to_heightmap": "WORLD_SURFACE_WG",
        "use_expansion_hack": False, "spawn_overrides": {},
    })
    write_json(DATA / "worldgen" / "structure_set" / "common_residential_quarter.json", {
        "structures": [{"structure": f"{NS}:common_residential_quarter", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 40, "separation": 20,
                      "spread_type": "linear", "salt": salt_for("common_residential_quarter")},
    })
    write_json(DATA / "tags" / "worldgen" / "biome" / "has_common_residential_quarter.json", {
        "replace": False, "values": HOME_BIOMES,
    })
    print(f"common residential quarter: {len(pieces)} piece types, {len(pools)} pools")
    print("set dressing: stone debris, wood debris, skeletal remains, elven remains, abandoned objects, broken infrastructure")
    print("placement: one random-spread anchor; subordinate members are jigsaw-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
