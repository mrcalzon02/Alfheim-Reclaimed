"""Audit the three directly assembled gigantic archaeology complexes in a saved world."""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from biome_census import chunks  # noqa: E402

SITES = {
    "deep_quarry": (128, 128, {"alfheim:rootbound_livingrock_bricks", "alfheim:emberwake_ore",
                                "botania:apothecary_livingrock"}),
    "elder_kings_tomb": (160, 128, {"alfheim:ivory_livingrock_bricks",
                                     "alfheim:moonstone_livingrock_polished",
                                     "alfheim:mana_glass_light", "alfheim:tomb_debris",
                                     "alfheim:elder_sarcophagus_head", "alfheim:funerary_tapestry_top",
                                     "alfheim:memorial_carving", "alfheim:elder_grave_door_left_base",
                                     "alfheim:elder_statue_crown"}),
    "faultwork": (192, 128, {"minecraft:crying_obsidian", "alfheim:magmatic_livingrock",
                              "alfheim:mana_glass_shadow"}),
}


def names(root):
    out = set()
    for section in root.get("sections", root.get("Level", {}).get("Sections", [])):
        y = int(section.get("Y", -99))
        if -4 <= y <= 1:
            palette = section.get("block_states", {}).get("palette", [])
            out.update(str(state.get("Name")) for state in palette if state.get("Name"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default=os.path.join("server", "deep-archaeology-grand-validation"))
    ap.add_argument("--only", choices=sorted(SITES))
    args = ap.parse_args()
    region_dir = os.path.join(args.world, "dimensions", "mythicbotany", "alfheim", "region")
    if not os.path.isdir(region_dir):
        print("FAILED: no Alfheim region directory at " + region_dir)
        return 1
    saved = {}
    for path in glob.glob(os.path.join(region_dir, "*.mca")):
        for root in chunks(path):
            saved[(int(root.get("xPos", 999999)), int(root.get("zPos", 999999)))] = root
    failures = []
    natural = {sid: [] for sid in SITES}
    for root in saved.values():
        starts = root.get("structures", {}).get("starts", {})
        for sid, start in starts.items():
            short = str(sid).split(":", 1)[-1]
            if short not in natural or not isinstance(start, dict) or not start.get("Children"):
                continue
            roles = [str(child.get("pool", "")).rsplit("/", 1)[-1]
                     for child in start.get("Children", [])]
            natural[short].append(roles)
    for sid, (cx, cz, required) in SITES.items():
        if args.only and sid != args.only:
            continue
        nearby = [saved[(x, z)] for x in range(cx - 8, cx + 9)
                  for z in range(cz - 8, cz + 9) if (x, z) in saved]
        palette = set().union(*(names(root) for root in nearby)) if nearby else set()
        missing = sorted(required - palette)
        if missing:
            failures.append(f"{sid}: missing assembled-piece signatures {missing}")
        if "minecraft:jigsaw" in palette:
            failures.append(f"{sid}: exposed jigsaw remained after assembly")
        complete = [roles for roles in natural[sid]
                    if len(roles) == 9 and roles.count("centre") == 1
                    and roles.count("approach") == 4 and roles.count("wing") == 4]
        if not complete:
            failures.append(f"{sid}: no naturally generated complete 1+4+4 assembly was saved")
        print(f"{sid:18} chunks={len(nearby):3} palette={len(palette):3} signatures={len(required)-len(missing)}/{len(required)} natural_complete={len(complete)}")
    if failures:
        print("Deep archaeology runtime check FAILED")
        for failure in failures:
            print("  " + failure)
        return 1
    selected = "all three gigantic complexes" if not args.only else args.only
    print(f"PASS: {selected} assembled child-piece signatures and natural 1+4+4 layouts with no exposed jigsaws")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
