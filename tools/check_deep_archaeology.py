"""Validate DEEPWORKS section 9 archaeology and its generator closure."""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "kubejs", "data", "alfheim")
MANIFEST = os.path.join(ROOT, "tools", "deep_archaeology_manifest.json")


def read(path):
    return json.load(open(path, encoding="utf-8"))


def main():
    manifest = read(MANIFEST)
    registry = set(read(os.path.join(ROOT, "tools", "registry_items.json"))["ids"])
    deep_catalog = read(os.path.join(ROOT, "kubejs", "deepworks_catalog.json"))
    registry.update(block["id"] for block in deep_catalog["blocks"])
    funerary = read(os.path.join(ROOT, "tools", "funerary_set_manifest.json"))
    registry.update(block["id"] for block in funerary["blocks"])
    registry.update({"minecraft:air", "minecraft:cave_air", "minecraft:water", "minecraft:lava"})
    salts = set()
    total_blocks = 0
    for family in manifest["families"]:
        fid = family["id"]
        structure = read(os.path.join(DATA, "worldgen", "structure", fid + ".json"))
        assert structure["type"] == "minecraft:jigsaw" and structure["size"] == 2, fid
        assert structure["max_distance_from_center"] >= 110, fid
        assert structure["step"] == "underground_structures", fid
        assert structure["terrain_adaptation"] == "none", fid
        assert "project_start_to_heightmap" not in structure, fid
        provider = structure["start_height"]
        assert provider["type"] == "minecraft:uniform", fid
        assert [provider["min_inclusive"]["absolute"], provider["max_inclusive"]["absolute"]] == family["depth"], fid
        struct_set = read(os.path.join(DATA, "worldgen", "structure_set", fid + ".json"))
        placement = struct_set["placement"]
        assert placement["type"] == "minecraft:random_spread", fid
        assert placement["spacing"] > placement["separation"] >= 1, fid
        assert placement["salt"] not in salts, fid
        salts.add(placement["salt"])
        footprint = family["pieces"]["centre"][0] + 2 * family["pieces"]["approach"][2] + 2 * family["pieces"]["wing"][2]
        assert footprint >= 190, f"{fid}: not a gigantic complex ({footprint})"
        for role, expected_size in family["pieces"].items():
            pool = read(os.path.join(DATA, "worldgen", "template_pool", "deepworks_archaeology", fid, role + ".json"))
            assert len(pool["elements"]) == 1, f"{fid}/{role}"
            path = os.path.join(DATA, "structures", "deepworks_archaeology", fid, role + ".nbt")
            _, piece = nbt.load(path)
            size = [int(x) for x in piece["size"]]
            assert size == expected_size and max(size) <= 48, path
            assert piece["entities"] == [], path
            names = {entry["Name"] for entry in piece["palette"]}
            unknown = sorted(names - registry)
            assert not unknown, f"{path}: unknown blocks {unknown}"
            assert "minecraft:spawner" not in names, f"{path}: authored mob spawner"
            assert "minecraft:air" in names, f"{path}: structure cannot open rooms"
            jigsaws = [b for b in piece["blocks"] if b.get("nbt", {}).get("id") == "minecraft:jigsaw"]
            expected_jigsaws = {"centre": 4, "approach": 2, "wing": 1}[role]
            assert len(jigsaws) == expected_jigsaws, f"{path}: {len(jigsaws)} jigsaws"
            assert all(b["nbt"]["final_state"] == "minecraft:air" for b in jigsaws), path
            total_blocks += len(piece["blocks"])

    quarry_names = set()
    for role in manifest["families"][0]["pieces"]:
        _, piece = nbt.load(os.path.join(DATA, "structures", "deepworks_archaeology", "deep_quarry", role + ".nbt"))
        quarry_names |= {entry["Name"] for entry in piece["palette"]}
    assert len([x for x in quarry_names if x.startswith("alfheim:") and x.endswith("_ore")]) >= 8
    assert "botania:apothecary_livingrock" in quarry_names

    relic_chests = 0
    for role in manifest["families"][1]["pieces"]:
        _, piece = nbt.load(os.path.join(DATA, "structures", "deepworks_archaeology", "elder_kings_tomb", role + ".nbt"))
        chests = [b for b in piece["blocks"] if b.get("nbt", {}).get("LootTable") == "alfheim:chests/elder_kings_relic"]
        relic_chests += len(chests)
    assert relic_chests == 1, "the entire tomb complex needs exactly one relic chest"
    tomb_names = set()
    for role in manifest["families"][1]["pieces"]:
        _, piece = nbt.load(os.path.join(DATA, "structures", "deepworks_archaeology", "elder_kings_tomb", role + ".nbt"))
        tomb_names |= {entry["Name"] for entry in piece["palette"]}
    assert {block["id"] for block in funerary["blocks"]} <= tomb_names

    fault_names = set()
    for role in manifest["families"][2]["pieces"]:
        _, piece = nbt.load(os.path.join(DATA, "structures", "deepworks_archaeology", "faultwork", role + ".nbt"))
        fault_names |= {entry["Name"] for entry in piece["palette"]}
    assert "minecraft:crying_obsidian" in fault_names
    assert {"alfheim:mana_glass_shadow", "alfheim:mana_glass_fire", "alfheim:mana_glass_light"} <= fault_names
    salvage = read(os.path.join(DATA, "loot_tables", "chests", "faultwork_salvage.json"))
    assert "occultism:burnt_otherstone" in json.dumps(salvage)

    ignored = read(os.path.join(ROOT, "kubejs", "data", "continuityworks_spawn_protection", "tags",
                                "worldgen", "structure", "ignored.json"))["values"]
    assert set(ignored) == {"alfheim:deep_quarry", "alfheim:elder_kings_tomb", "alfheim:faultwork"}
    subprocess.run([sys.executable, "-B", os.path.join(ROOT, "tools", "gen_deep_archaeology.py"), "--check"],
                   cwd=ROOT, check=True)
    print(f"PASS: 3 underground families, three 9-piece ~200-block complexes, {total_blocks} source template blocks; random depth bands; no authored mobs; generator closed")


if __name__ == "__main__":
    main()
