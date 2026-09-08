"""Static acceptance for the Section 8 Deepworks environmental pass."""
import json
from pathlib import Path

from gen_deep_formations import ROOT, build


def walk_names(value, out):
    if isinstance(value, dict):
        if isinstance(value.get("Name"), str):
            out.add(value["Name"])
        for child in value.values():
            walk_names(child, out)
    elif isinstance(value, list):
        for child in value:
            walk_names(child, out)


def main():
    expected = build()
    for name, content in expected.items():
        path = ROOT / name
        assert path.exists() and path.read_bytes() == content, name
        if name.endswith(".json"):
            json.loads(content)

    manifest = json.loads((ROOT / "tools/deep_formations_manifest.json").read_text())
    registry = set(json.loads((ROOT / "tools/registry_items.json").read_text())["ids"])
    deep_catalog = json.loads((ROOT / "kubejs/deepworks_catalog.json").read_text())
    registry.update(block["id"] for block in deep_catalog["blocks"])
    alignments = manifest["alignments"]
    assert len(alignments) == 6
    assert {a["element"] for a in alignments} == {"fire", "water", "earth", "air", "shadow", "light"}
    # HORIZONTAL REACH. A decoration feature may only write inside the chunk being generated
    # and its immediate neighbours; anything further is refused with "Detected setBlock in a
    # far chunk" and the formation is silently truncated at the boundary.
    #
    # This bound was added for the slag terraces after they produced 241 such errors in one
    # session, and it was written naming that one family. The ley scars kept an xz_radius of 16
    # and went on failing the same way -- 20 more errors in the 2026-09-07 field session, from
    # `alfheim:deepworks/formations/ley_scars`. The rule now covers every formation, so the
    # next one to grow is caught by the check rather than by a player.
    MAX_REACH = 15
    for name, spec in sorted(manifest["formations"].items()):
        reach = max(spec["radius"]) + spec.get("lava_spread", 0)
        assert reach <= MAX_REACH, (
            f"{name}: horizontal reach {reach} exceeds {MAX_REACH}; the patch can write "
            "beyond the neighbouring chunk and will be truncated at the boundary")

    objects = {name.replace("\\", "/"): json.loads(body)
               for name, body in expected.items() if name.endswith(".json")}
    configured = {name: body for name, body in objects.items() if "/configured_feature/" in name}
    placed = {name: body for name, body in objects.items() if "/placed_feature/" in name and "/tags/" not in name}
    assert len(configured) == 22, len(configured)  # 18 aligned + 3 selectors + terraces
    assert len(placed) == 4

    expected_types = {
        "crystal_chandeliers": "minecraft:simple_random_selector",
        "ley_scars": "minecraft:simple_random_selector",
        "mineral_columns": "minecraft:simple_random_selector",
        "slag_terraces": "minecraft:vegetation_patch",
    }
    for family, feature_type in expected_types.items():
        key = next(k for k in configured if k.endswith(f"/{family}.json"))
        assert configured[key]["type"] == feature_type

    for alignment in alignments:
        crystal = alignment["crystal"]
        for prefix in ("chandelier", "ley_scar", "mineral_column"):
            assert any(k.endswith(f"/{prefix}_{crystal}.json") for k in configured)

    # Placement is cave-bound and depth-bound. A height-only random patch can bury itself
    # in solid rock and was the exact failure this implementation is designed to avoid.
    for name, body in placed.items():
        types = [p["type"] for p in body["placement"]]
        assert "minecraft:height_range" in types, name
        assert "minecraft:environment_scan" in types, name
        assert types[-1] == "minecraft:biome", name
        height = next(p for p in body["placement"] if p["type"] == "minecraft:height_range")["height"]
        assert height["min_inclusive"]["absolute"] >= -54
        assert height["max_inclusive"]["absolute"] <= 12
        scan = next(p for p in body["placement"] if p["type"] == "minecraft:environment_scan")
        assert scan["max_steps"] == 32, "Minecraft 1.20.1 codec bounds environment_scan to 1..32"
        if name.endswith("slag_terraces.json"):
            assert any(p.get("predicate", {}).get("fluids") == "minecraft:lava"
                       for p in body["placement"] if p["type"] == "minecraft:block_predicate_filter")
        else:
            assert "minecraft:block_predicate_filter" in types

    names = set()
    for body in configured.values():
        walk_names(body, names)
    missing = sorted(name for name in names if name not in registry and name not in {"minecraft:air", "minecraft:lava"})
    assert not missing, f"unregistered formation blocks: {missing}"

    modifier = objects["kubejs/data/alfheim/forge/biome_modifier/deepworks_formations.json"]
    assert modifier["biomes"] == "#alfheim:deepworks_land"
    assert modifier["step"] == "local_modifications"
    assert modifier["features"] == [
        "alfheim:deepworks/formations/crystal_chandeliers",
        "alfheim:deepworks/formations/ley_scars",
        "alfheim:deepworks/formations/mineral_columns",
        "alfheim:deepworks/formations/slag_terraces",
    ]
    assert not any("/worldgen/structure" in name or "/structures/" in name for name in expected)
    print("PASS: 6 aligned chandelier/scar/column variants plus lava-bound terraces; "
          "4 cave-anchored placed features; registered blocks; deterministic output; no room-carving structures")


if __name__ == "__main__":
    main()
