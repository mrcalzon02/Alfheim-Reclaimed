#!/usr/bin/env python3
"""Validate the Void Margin structure contract before Surface Works is extended.

This is deliberately a guardrail, not a second generator. It reads the existing
``tools/surface_works_manifest.json`` and generated structure JSON written by
``tools/gen_surface_works.py``. It does not create or mutate shipping data.

The authoritative design is ``alfheim_reclaimed_design/void/TERRAIN_AND_STRUCTURES.md``.
That record requires six Void Margin biomes, exactly two sanctioned structures per
biome, terrain-owned support (never a generated island/foundation), and guaranteed
far-field emptiness in Starless Reach.

Usage:
    python tools/check_void_surface_support.py
    python tools/check_void_surface_support.py --complete
    python tools/check_void_surface_support.py --self-test

Default mode validates every sanctioned Void structure that is already present while
allowing later biome pairs to remain unbuilt. ``--complete`` is the production gate:
all twelve sanctioned ids must exist.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

NS = "alfheim"
ROOT = Path(__file__).resolve().parents[1]

VOID_BIOMES = {
    "alfheim:void_verge": ("verge_spire", "severed_span"),
    "alfheim:shatterfields": ("anchor_bastion", "fracture_gate"),
    "alfheim:prism_drift": ("prism_observatory", "split_gallery"),
    "alfheim:rootfall": ("root_shrine", "garden_archive_terrace"),
    "alfheim:sepulchral_reach": ("kings_cliff_tomb", "mourning_court"),
    "alfheim:starless_reach": ("last_watch", "starless_orrery"),
}

# Host classes and minimum support are copied from the authoritative design record.
# These are candidate requirements. They must describe terrain that already exists;
# no structure is allowed to manufacture blocks merely to satisfy them.
HOST_CONTRACT = {
    "verge_spire": {"class": "verge_table", "terrain_owned": True},
    "severed_span": {"class": "verge_table", "terrain_owned": True, "far_side_absent": True},
    "anchor_bastion": {"class": "fragment_core", "terrain_owned": True},
    "fracture_gate": {"class": "talus_shelf", "terrain_owned": True, "far_side_absent": True},
    "prism_observatory": {"class": "prism_core", "terrain_owned": True},
    "split_gallery": {"class": "prism_core", "terrain_owned": True},
    "root_shrine": {"class": "attached_shelf", "terrain_owned": True},
    "garden_archive_terrace": {"class": "attached_shelf", "terrain_owned": True},
    "kings_cliff_tomb": {
        "class": "burial_face",
        "terrain_owned": True,
        "min_backing_blocks": 16,
    },
    "mourning_court": {"class": "memorial_shelf", "terrain_owned": True},
    "last_watch": {
        "class": "terminal_landing",
        "terrain_owned": True,
        "min_solid_blocks": 1800,
        "min_dimensions": [14, 8, 14],
        "min_support_ratio": 0.86,
        "continentalness_min": -0.94,
        "continentalness_max": -0.925,
    },
    "starless_orrery": {
        "class": "terminal_landing",
        "terrain_owned": True,
        "min_solid_blocks": 1800,
        "min_dimensions": [14, 8, 14],
        "min_support_ratio": 0.86,
        "continentalness_min": -0.94,
        "continentalness_max": -0.925,
    },
}

SANCTIONED = {sid for pair in VOID_BIOMES.values() for sid in pair}


def _load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def collect(root: Path = ROOT):
    manifest_path = root / "tools" / "surface_works_manifest.json"
    structures_dir = root / "kubejs" / "data" / NS / "worldgen" / "structure"
    manifest = _load_json(manifest_path)
    generated = {}
    for path in structures_dir.glob("*.json"):
        generated[path.stem] = _load_json(path)
    return manifest, generated


def validate(manifest, generated, complete=False):
    problems = []

    def fail(code, text):
        problems.append(f"{code}  {text}")

    by_id = {entry["id"]: entry for entry in manifest.get("structures", [])}

    # V1 -- exactly the sanctioned ids may target the six Void Margin biomes.
    void_targets = {}
    for entry in manifest.get("structures", []):
        for biome in entry.get("biomes", []):
            if biome in VOID_BIOMES:
                void_targets.setdefault(biome, []).append(entry["id"])
                if entry["id"] not in SANCTIONED:
                    fail("V1", f"{entry['id']} targets {biome} but is not a sanctioned Void structure")

    for biome, expected in VOID_BIOMES.items():
        got = set(void_targets.get(biome, []))
        extra = got - set(expected)
        if extra:
            fail("V1", f"{biome} has unsanctioned ids {sorted(extra)}")
        if len(got) > 2:
            fail("V1", f"{biome} has {len(got)} structures; contract is exactly two")
        if complete and got != set(expected):
            fail("V1", f"{biome} complete gate wants {sorted(expected)}, got {sorted(got)}")

    # V2 -- any sanctioned structure that exists must target exactly its assigned biome.
    expected_biome = {sid: biome for biome, pair in VOID_BIOMES.items() for sid in pair}
    for sid in SANCTIONED & set(by_id):
        biomes = by_id[sid].get("biomes", [])
        if biomes != [expected_biome[sid]]:
            fail("V2", f"{sid} biomes {biomes} != [{expected_biome[sid]}]")

    # V3 -- terrain support is explicit machine-readable source data.
    for sid in SANCTIONED & set(by_id):
        got = by_id[sid].get("host")
        want = HOST_CONTRACT[sid]
        if not isinstance(got, dict):
            fail("V3", f"{sid} has no host support contract in surface_works_manifest.json")
            continue
        for key, value in want.items():
            if got.get(key) != value:
                fail("V3", f"{sid}.host.{key}={got.get(key)!r}, expected {value!r}")

    # V4 -- no fake island/foundation flags. The known Verge Spire defect used `island: true`.
    for sid in SANCTIONED & set(by_id):
        shape = by_id[sid].get("shape", {})
        forbidden = [k for k in ("island", "foundation", "fill_support", "rescue_terrain")
                     if shape.get(k)]
        if forbidden:
            fail("V4", f"{sid} manufactures terrain through {forbidden}; support must pre-exist")

    # V5 -- every built Void structure must override terrain adaptation to none.
    # Beard/bury adaptation can manufacture hidden support and therefore cannot be the acceptance
    # mechanism at the rim. The ordinary non-Void archetypes may keep their existing adaptation.
    for sid in SANCTIONED & set(by_id):
        if by_id[sid].get("adaptation") != "none":
            fail("V5", f"{sid} must declare per-structure adaptation='none'")
        js = generated.get(sid)
        if js is not None and js.get("terrain_adaptation") != "none":
            fail("V5", f"{sid} shipping terrain_adaptation={js.get('terrain_adaptation')!r}, expected 'none'")

    # V6 -- Starless Reach can only use the terminal strip; the far field is never buildable.
    for sid in VOID_BIOMES["alfheim:starless_reach"]:
        if sid not in by_id:
            continue
        host = by_id[sid].get("host", {})
        lo = host.get("continentalness_min")
        hi = host.get("continentalness_max")
        if (lo, hi) != (-0.94, -0.925):
            fail("V6", f"{sid} must remain inside continentalness -0.94 .. -0.925; got {lo} .. {hi}")
        if host.get("allow_far_field", False):
            fail("V6", f"{sid} explicitly allows the guaranteed-empty far field")

    # V7 -- generated files cannot exist for a sanctioned id that is absent from source.
    for sid in SANCTIONED & set(generated):
        if sid not in by_id:
            fail("V7", f"shipping structure {sid}.json exists without a manifest source entry")

    if complete:
        missing = SANCTIONED - set(by_id)
        if missing:
            fail("V8", f"complete gate missing sanctioned structures {sorted(missing)}")

    return problems


def _good_fixture():
    structures = []
    generated = {}
    for biome, pair in VOID_BIOMES.items():
        for sid in pair:
            structures.append({
                "id": sid,
                "biomes": [biome],
                "adaptation": "none",
                "host": copy.deepcopy(HOST_CONTRACT[sid]),
                "shape": {},
            })
            generated[sid] = {"terrain_adaptation": "none"}
    return {"structures": structures}, generated


SELF_TESTS = [
    ("V1", lambda m, g: m["structures"].append({
        "id": "rogue_void_tower", "biomes": ["alfheim:void_verge"],
        "adaptation": "none", "host": {"class": "verge_table", "terrain_owned": True},
    })),
    ("V2", lambda m, g: m["structures"][0].__setitem__("biomes", ["alfheim:rootfall"])),
    ("V3", lambda m, g: m["structures"][0].pop("host")),
    ("V4", lambda m, g: m["structures"][0].setdefault("shape", {}).__setitem__("island", True)),
    ("V5", lambda m, g: g["verge_spire"].__setitem__("terrain_adaptation", "beard_thin")),
    ("V6", lambda m, g: next(x for x in m["structures"] if x["id"] == "last_watch")["host"].__setitem__("continentalness_min", -1.0)),
    ("V7", lambda m, g: m["structures"].__setitem__(slice(None), [x for x in m["structures"] if x["id"] != "verge_spire"])),
]


def self_test():
    base_m, base_g = _good_fixture()
    clean = validate(base_m, base_g, complete=True)
    if clean:
        print("self-test fixture is not clean:")
        for p in clean:
            print("  " + p)
        return 1

    dead = 0
    for code, mutate in SELF_TESTS:
        m, g = copy.deepcopy(base_m), copy.deepcopy(base_g)
        mutate(m, g)
        hit = [p for p in validate(m, g, complete=True) if p.startswith(code)]
        print(f"  {code}  {'FIRES' if hit else 'SILENT -- CHECK IS DEAD'}")
        if not hit:
            dead += 1
    print(f"\n  {len(SELF_TESTS) - dead}/{len(SELF_TESTS)} checks proven to fire")
    return 1 if dead else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--complete", action="store_true",
                    help="require all twelve sanctioned Void structures")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    manifest, generated = collect()
    problems = validate(manifest, generated, complete=args.complete)
    for problem in problems:
        print("  " + problem)
    print(f"\n  {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
