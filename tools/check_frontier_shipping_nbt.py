"""Validate the six *shipping* Frontier NBT templates and negative controls.

Static source contract only. This cannot prove Minecraft vegetation ordering,
terrain fitting, cross-chunk placement or natural-spawn acceptance.
"""
import copy
import json
from pathlib import Path

import nbt
from check_frontier_canopy_regression import (
    ROOT, FAMILY, PIECES, CANOPY_AIR, CANOPY_FLOOR, JOIN,
    check_settings, check_shrine, require,
)

DATA = Path("kubejs/data/alfheim")
EXPECTED_START = f"alfheim:ancient/{FAMILY}/green_noble_lodge"


def decode_template(name, template):
    size = tuple(map(int, template["size"]))
    require(len(size) == 3 and all(0 < value <= 48 for value in size),
            ("invalid shipping template dimensions", name, size))
    palette = template["palette"]
    require(bool(palette), ("empty template palette", name))
    cells = {}
    for block in template["blocks"]:
        point = tuple(map(int, block["pos"]))
        require(len(point) == 3 and all(0 <= p < extent for p, extent in zip(point, size)),
                ("template cell outside bounds", name, point, size))
        require(point not in cells, ("duplicate shipping cell", name, point))
        index = int(block["state"])
        require(0 <= index < len(palette), ("invalid palette state", name, point, index))
        cells[point] = palette[index]["Name"]
    require(any(value == "minecraft:air" for value in cells.values()),
            ("shipping template does not stamp explicit air", name))
    require(any(value == "minecraft:jigsaw" for value in cells.values()),
            ("shipping template has no connection port", name))
    return size, cells


def load_shipping(root=ROOT):
    base = root / DATA
    spec = json.loads((base / f"worldgen/structure/{FAMILY}.json").read_text(encoding="utf-8"))
    pools = {}
    templates = {}
    for name in PIECES:
        pools[name] = json.loads(
            (base / f"worldgen/template_pool/ancient/{FAMILY}/{name}.json").read_text(encoding="utf-8")
        )
        templates[name] = nbt.load(
            str(base / f"structures/ancient/{FAMILY}/{name}.nbt")
        )[1]
    natural_set = (base / f"worldgen/structure_set/{FAMILY}.json").exists()
    return spec, pools, templates, natural_set


def validate(spec, pools, templates, natural_set):
    require(set(pools) == set(PIECES) and set(templates) == set(PIECES),
            "Frontier shipping pool/template inventory drift")
    check_settings(spec, pools, natural_set)
    require(spec.get("start_pool") == spec.get("layout", {}).get("start_pool") == EXPECTED_START,
            "Frontier start pool identity drift")
    results = {}
    for name in PIECES:
        pool = pools[name]
        require(pool.get("name") == f"alfheim:ancient/{FAMILY}/{name}",
                ("shipping pool identity drift", name))
        require(pool.get("fallback") == "minecraft:empty",
                ("shipping pool fallback drift", name))
        size, cells = decode_template(name, templates[name])
        results[name] = {
            "size": size,
            "authored_cells": len(cells),
            "explicit_air": sum(value == "minecraft:air" for value in cells.values()),
            "jigsaw_ports": sum(value == "minecraft:jigsaw" for value in cells.values()),
        }
        if name == "wild_ward_shrine":
            require(size == (31, 30, 31), ("shrine dimensions drift", size))
            check_shrine(cells)
            require(cells[CANOPY_AIR] == "minecraft:air", "recorded canopy cell is not clear")
            require(cells[CANOPY_FLOOR] not in ("minecraft:air", "minecraft:water"),
                    "recorded canopy floor is unsupported")
    return results


def expect_rejected(label, spec, pools, templates, natural_set):
    try:
        validate(spec, pools, templates, natural_set)
    except AssertionError:
        return label
    raise AssertionError(("corrupted shipping-derived fixture was accepted", label))


def mutation_test(spec, pools, templates, natural_set):
    # Each mutation starts from the real shipping data, not a synthetic toy
    # template. The original NBT and JSON files are never written.
    rejected = []
    for location in ("outer", "layout"):
        bad = copy.deepcopy(spec)
        if location == "outer":
            bad["step"] = "surface_structures"
        else:
            bad["layout"]["step"] = "surface_structures"
        rejected.append(expect_rejected("early-" + location, bad, pools, templates, natural_set))

    for field, value in (("element_type", "minecraft:legacy_single_pool_element"),
                         ("processors", "alfheim:ignore_air"),
                         ("location", "alfheim:ancient/frontier_stewardship/other")):
        bad = copy.deepcopy(pools)
        bad["wild_ward_shrine"]["elements"][0]["element"][field] = value
        rejected.append(expect_rejected("pool-" + field, spec, bad, templates, natural_set))

    bad = copy.deepcopy(pools)
    bad["wild_ward_shrine"]["name"] = "alfheim:ancient/frontier_stewardship/wrong"
    rejected.append(expect_rejected("pool-name", spec, bad, templates, natural_set))
    rejected.append(expect_rejected("natural-set-enabled", spec, pools, templates, True))

    # Derive corrupt fixtures from the decoded *shipping* NBT, changing one
    # block's palette index while retaining the original coordinates.
    shrine = templates["wild_ward_shrine"]
    lookup = {tuple(map(int, block["pos"])): index
              for index, block in enumerate(shrine["blocks"])}
    for point, replacement, label in (
        (CANOPY_AIR, "mythicbotany:dreamwood_leaves", "recorded-leaf"),
        (CANOPY_FLOOR, "minecraft:air", "missing-floor"),
        (JOIN, "minecraft:air", "missing-entry-port"),
    ):
        bad_shrine = dict(shrine)
        bad_shrine["palette"] = list(shrine["palette"]) + [{"Name": replacement}]
        bad_shrine["blocks"] = list(shrine["blocks"])
        index = lookup[point]
        bad_shrine["blocks"][index] = dict(shrine["blocks"][index], state=len(bad_shrine["palette"]) - 1)
        bad_templates = dict(templates, wild_ward_shrine=bad_shrine)
        rejected.append(expect_rejected(label, spec, pools, bad_templates, natural_set))

    bad_shrine = dict(shrine)
    bad_shrine["blocks"] = list(shrine["blocks"]) + [{
        "pos": [int(shrine["size"][0]), 0, 0], "state": 0,
    }]
    rejected.append(expect_rejected("out-of-bounds-nbt", spec, pools,
                                    dict(templates, wild_ward_shrine=bad_shrine), natural_set))
    return rejected


def main():
    spec, pools, templates, natural_set = load_shipping()
    results = validate(spec, pools, templates, natural_set)
    rejected = mutation_test(spec, pools, templates, natural_set)
    print("FRONTIER SHIPPING NBT PASS: " + json.dumps(results, sort_keys=True))
    print(f"FRONTIER SHIPPING MUTATION PASS: {len(rejected)} real-NBT-derived corruptions rejected: "
          + ", ".join(rejected))
    print("Minecraft/Forge fresh-world placement NOT TESTED; production natural structure set remains disabled")


if __name__ == "__main__":
    main()
