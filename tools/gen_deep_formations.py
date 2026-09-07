"""Generate the Deepworks environmental formations from DEEPWORKS.md section 8.

This pass deliberately uses terrain-aware configured features, not structure templates. Every
feature searches for an existing cavern floor or ceiling and therefore decorates the large cave
field without carving a substitute room around itself. Run from the instance root.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path("kubejs/data/alfheim")
MANIFEST = ROOT / "tools/deep_formations_manifest.json"


def uniform(lo, hi):
    return {"type": "minecraft:uniform", "value": {"min_inclusive": lo, "max_inclusive": hi}}


def simple_state(name, props=None):
    state = {"Name": name}
    if props:
        state["Properties"] = props
    return {"type": "minecraft:simple_state_provider", "state": state}


def weighted_state(entries):
    return {"type": "minecraft:weighted_state_provider", "entries": [
        {"data": {"Name": name}, "weight": weight} for name, weight in entries
    ]}


AIR = {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"}
LAVA = {"type": "minecraft:matching_fluids", "fluids": "minecraft:lava"}


def column(direction, height, entries, tip=None):
    layers = [{"height": uniform(*height), "provider": weighted_state(entries)}]
    if tip:
        layers.append({"height": 1, "provider": simple_state(tip)})
    return {"type": "minecraft:block_column", "config": {
        "direction": direction,
        "allowed_placement": AIR,
        "prioritize_tip": True,
        "layers": layers,
    }}


def inert_vegetation(block):
    # vegetation_patch requires a placed feature even at chance zero.
    return {"feature": {"type": "minecraft:simple_block", "config": {
        "to_place": simple_state(block)
    }}, "placement": []}


def patch(surface, radius, depth, ground, vegetation, chance, vertical=8):
    return {"type": "minecraft:vegetation_patch", "config": {
        "surface": surface,
        "depth": uniform(*depth),
        "vertical_range": vertical,
        "xz_radius": uniform(*radius),
        "extra_bottom_block_chance": 0.35,
        "extra_edge_column_chance": 0.68,
        "ground_state": ground,
        "replaceable": "#alfheim:deepworks_replaceable",
        "vegetation_chance": chance,
        "vegetation_feature": vegetation,
    }}


def selector(ids):
    return {"type": "minecraft:simple_random_selector", "config": {"features": [
        {"feature": f"alfheim:deepworks/formations/{name}", "placement": []} for name in ids
    ]}}


def cavern_anchor(direction, scan, offset):
    face = "down" if direction == "up" else "up"
    return [
        {"type": "minecraft:environment_scan", "direction_of_search": direction,
         "max_steps": scan, "allowed_search_condition": AIR,
         "target_condition": {"type": "minecraft:has_sturdy_face", "direction": face}},
        {"type": "minecraft:random_offset", "xz_spread": 0, "y_spread": offset},
        {"type": "minecraft:block_predicate_filter", "predicate": AIR},
    ]


def placed(name, rarity, depth, anchor, extra=None):
    return {"feature": f"alfheim:deepworks/formations/{name}", "placement": [
        {"type": "minecraft:rarity_filter", "chance": rarity},
        {"type": "minecraft:in_square"},
        {"type": "minecraft:height_range", "height": {
            "type": "minecraft:uniform",
            "min_inclusive": {"absolute": depth[0]},
            "max_inclusive": {"absolute": depth[1]},
        }},
        *anchor,
        *(extra or []),
        {"type": "minecraft:biome"},
    ]}


def build():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    depth = (m["depth"]["min"], m["depth"]["max"])
    scan = m["depth"]["scan"]
    formations = m["formations"]
    out = {}

    def emit(relative, body):
        out[str(DATA / relative)] = (json.dumps(body, indent=2) + "\n").encode()

    chandeliers, scars, columns = [], [], []
    for alignment in m["alignments"]:
        crystal = alignment["crystal"]
        element = alignment["element"]
        glass = f"alfheim:mana_glass_{element}"
        crystal_block = f"alfheim:{crystal}_block"
        budding = f"alfheim:budding_{crystal}"
        host = f"alfheim:{alignment['host']}"
        bloom = f"alfheim:{alignment['bloom']}"

        cid = f"chandelier_{crystal}"
        c = formations["crystal_chandeliers"]
        branch = column("down", c["branch_height"], [
            (crystal_block, 6), (budding, 2), (glass, 2)
        ], f"alfheim:{crystal}_cluster")
        emit(f"worldgen/configured_feature/deepworks/formations/{cid}.json",
             patch("ceiling", c["radius"], c["depth"],
                   weighted_state([(glass, 7), (host, 3), (budding, 1)]),
                   {"feature": branch, "placement": []}, c["vegetation_chance"], 10))
        chandeliers.append(cid)

        sid = f"ley_scar_{crystal}"
        s = formations["ley_scars"]
        # A broad surface-following vitrified band. The provider keeps the aligned glass
        # dominant while leaving coherent-looking pressure stone and a few live crystal knots.
        scar_provider = weighted_state([(glass, 9), (host, 3), (budding, 1)])
        emit(f"worldgen/configured_feature/deepworks/formations/{sid}.json",
             patch("floor", s["radius"], s["depth"], scar_provider,
                   inert_vegetation(glass), 0.0, 12))
        scars.append(sid)

        mid = f"mineral_column_{crystal}"
        c = formations["mineral_columns"]
        shaft = column("up", c["column_height"], [
            (host, 11), (glass, 3), (crystal_block, 2), (bloom, 1)
        ], crystal_block)
        emit(f"worldgen/configured_feature/deepworks/formations/{mid}.json",
             patch("floor", c["radius"], c["root_depth"],
                   weighted_state([(host, 8), (glass, 2), (bloom, 1)]),
                   {"feature": shaft, "placement": []}, c["vegetation_chance"], 10))
        columns.append(mid)

    for name, ids in (("crystal_chandeliers", chandeliers),
                      ("ley_scars", scars), ("mineral_columns", columns)):
        emit(f"worldgen/configured_feature/deepworks/formations/{name}.json", selector(ids))

    # Lava terraces are not generic underground patches. Their placement first finds a
    # lava-bearing cavity, verifies the fluid, then fans onto a nearby floor. The irregular
    # material mix continues the existing lava -> magmatic -> cracked -> livingrock grammar.
    t = formations["slag_terraces"]
    terrace_ground = weighted_state([
        ("alfheim:livingrock_slag", 7),
        ("alfheim:magmatic_livingrock", 4),
        ("alfheim:cracked_livingrock", 3),
    ])
    emit("worldgen/configured_feature/deepworks/formations/slag_terraces.json",
         patch("floor", t["radius"], t["depth"], terrace_ground,
               inert_vegetation("alfheim:livingrock_slag"), 0.0, 12))

    ceiling = cavern_anchor("up", scan, -1)
    floor = cavern_anchor("down", scan, 1)
    emit("worldgen/placed_feature/deepworks/formations/crystal_chandeliers.json",
         placed("crystal_chandeliers", formations["crystal_chandeliers"]["rarity"], depth, ceiling))
    emit("worldgen/placed_feature/deepworks/formations/ley_scars.json",
         placed("ley_scars", formations["ley_scars"]["rarity"], depth, floor))
    emit("worldgen/placed_feature/deepworks/formations/mineral_columns.json",
         placed("mineral_columns", formations["mineral_columns"]["rarity"], depth, floor))

    # For the terrace, the scan may pass through either cave air or lava. The current point
    # must be lava before the random horizontal offset carries the patch toward its shore.
    lava_or_air = {"type": "minecraft:matching_blocks", "blocks": ["minecraft:air", "minecraft:lava"]}
    lava_anchor = [
        {"type": "minecraft:environment_scan", "direction_of_search": "down", "max_steps": scan,
         "allowed_search_condition": lava_or_air,
         "target_condition": {"type": "minecraft:matching_fluids", "fluids": "minecraft:lava"}},
        {"type": "minecraft:block_predicate_filter", "predicate": LAVA},
        {"type": "minecraft:random_offset", "xz_spread": t["lava_spread"], "y_spread": 2},
    ]
    emit("worldgen/placed_feature/deepworks/formations/slag_terraces.json",
         placed("slag_terraces", t["rarity"], (depth[0], -45), lava_anchor))

    order = ["crystal_chandeliers", "ley_scars", "mineral_columns", "slag_terraces"]
    emit("forge/biome_modifier/deepworks_formations.json", {
        "type": "forge:add_features",
        "biomes": "#alfheim:deepworks_land",
        "features": [f"alfheim:deepworks/formations/{name}" for name in order],
        "step": "local_modifications",
    })
    emit("tags/worldgen/placed_feature/deepworks_formations.json", {
        "replace": False,
        "values": [f"alfheim:deepworks/formations/{name}" for name in order],
    })
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = build()
    mismatches = []
    for name, data in output.items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                mismatches.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    if mismatches:
        raise SystemExit("Generated output mismatch:\n" + "\n".join(mismatches))
    print(f"{len(output)} Deep formation files " + ("byte-identical" if args.check else "generated"))


if __name__ == "__main__":
    main()
