"""Validate the ancient elven district source contract and generated shipping boundary.

Authority:
  alfheim_reclaimed_design/ANCIENT_ELVEN_STRUCTURE_ROSTER.md
  tools/ancient_district_manifest.json
  tools/ancient_set_dressing_manifest.json
  tools/gen_ancient_districts.py

The manifest currently records the Common Residential Quarter at ``source_contract``. That is
an intentional acceptance boundary: generator source and design topology can be checked now,
while generated NBT/datapack output remains mandatory only after the family advances beyond the
source-contract stage. This prevents a source-only change from being described as a shipped or
runtime-validated structure family.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "ancient_district_manifest.json"
DRESSING = ROOT / "tools" / "ancient_set_dressing_manifest.json"
GENERATOR = ROOT / "tools" / "gen_ancient_districts.py"

STAGES = (
    "planned",
    "source_contract",
    "shipping_generated",
    "static_validated",
    "runtime_validated",
    "fresh_world_validated",
    "production_admitted",
)


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    problems = []

    def fail(code: str, message: str):
        problems.append(f"{code}  {message}")

    for path in (MANIFEST, DRESSING, GENERATOR):
        if not path.exists():
            fail("A1", f"missing authority/source: {path.relative_to(ROOT)}")
    if problems:
        for problem in problems:
            print(problem)
        return 1

    manifest = load_json(MANIFEST)
    dressing = load_json(DRESSING)
    source = GENERATOR.read_text(encoding="utf-8")

    # A2 — authoritative contract identity and global generation policy.
    if manifest.get("schema") != "alfheim:ancient_districts/v1":
        fail("A2", f"unexpected schema {manifest.get('schema')!r}")
    if manifest.get("design_authority") != "alfheim_reclaimed_design/ANCIENT_ELVEN_STRUCTURE_ROSTER.md":
        fail("A2", "design authority drifted")
    policy = manifest.get("generation_policy", {})
    if policy.get("placement_model") != "district_anchor_family":
        fail("A2", "placement_model must remain district_anchor_family")
    if policy.get("forbid_independent_member_random_spread") is not True:
        fail("A2", "independent member random-spread must remain forbidden")
    if policy.get("max_piece_axis") != 48:
        fail("A2", "max_piece_axis must remain the structure-piece boundary of 48")
    if policy.get("terrain_fit_required") is not True:
        fail("A2", "terrain-fit requirement may not be relaxed")

    families = manifest.get("families", [])
    by_id = {family.get("id"): family for family in families}
    family = by_id.get("common_residential_quarter")
    if family is None:
        fail("A3", "Wave-1 common_residential_quarter family is missing")
        family = {}

    # A3 — acceptance stage stays explicit and cannot silently leap.
    stage = family.get("status")
    if stage not in STAGES:
        fail("A3", f"unknown family status {stage!r}")
    if family.get("wave") != 1:
        fail("A3", "common residential quarter must remain Wave 1")
    if family.get("anchor") != "neighborhood_common_hall":
        fail("A3", "neighborhood_common_hall must remain the family anchor")

    members = {member["id"]: member for member in family.get("members", [])}
    required_members = {
        "neighborhood_common_hall", "common_row_house", "courtyard_home",
        "artisan_house_shop", "extended_kin_hall", "district_cistern",
        "avenue_segment", "district_mass_grave", "collapsed_trace_field",
    }
    if set(members) != required_members:
        fail(
            "A3",
            f"member contract mismatch: missing={sorted(required_members-set(members))} "
            f"extra={sorted(set(members)-required_members)}",
        )
    for member in members.values():
        size = member.get("piece_size", [])
        if len(size) != 3 or any(int(axis) > 48 for axis in size):
            fail("A3", f"{member.get('id')}: illegal piece_size {size}")

    acceptance = family.get("acceptance", {})
    for gate in (
        "must_show_original_function", "must_show_emergency_conversion",
        "must_show_terminal_collapse", "must_show_long_decay",
        "must_include_mortuary_edge", "must_include_advanced_infrastructure",
        "must_include_connected_route_from_anchor_to_burial_edge",
        "must_not_bypass_progression",
    ):
        if acceptance.get(gate) is not True:
            fail("A3", f"acceptance requirement weakened or missing: {gate}")

    # A4 — source implements every semantic member and uses one random-spread anchor only.
    source_requirements = {
        "neighborhood_common_hall": "build_common_hall",
        "common_row_house": "build_row_house",
        "courtyard_home": "build_courtyard_home",
        "artisan_house_shop": "build_artisan_shop",
        "extended_kin_hall": "build_kin_hall",
        "district_cistern": "build_cistern",
        "district_mass_grave": "build_mass_grave",
        "collapsed_trace_field": "build_trace",
    }
    for piece, builder in source_requirements.items():
        if f'"{piece}"' not in source or f"def {builder}(" not in source:
            fail("A4", f"{piece}: generator mapping/builder {builder} missing")
    for avenue in ("avenue_north", "avenue_south", "avenue_east", "avenue_west"):
        if f'"{avenue}"' not in source:
            fail("A4", f"{avenue}: generated avenue member missing")
    if source.count('"type": "minecraft:random_spread"') != 1:
        fail("A4", "generator must contain exactly one random-spread placement declaration")
    if "subordinate homes, roads, cistern/trace edges" not in source:
        fail("A4", "generator no longer states its subordinate jigsaw-only contract")

    # A5 — set-dressing vocabulary is complete and consumed by the generator.
    expected_categories = {
        "stone_debris", "wood_debris", "skeletal_remains",
        "elven_remains", "abandoned_objects", "broken_infrastructure",
    }
    categories = set(dressing.get("categories", {}))
    if categories != expected_categories:
        fail("A5", f"set-dressing categories mismatch: {sorted(categories)}")
    for category in expected_categories:
        if f"def {category}(" not in source:
            fail("A5", f"generator does not implement {category}()")
    rules = dressing.get("placement_rules", {})
    if rules.get("persistent_entities_default") is not False:
        fail("A5", "persistent entities must remain opt-in")
    for rule in (
        "context_required", "no_uniform_bone_carpet", "remains_density_tracks_history",
        "debris_follows_collapse_direction", "progression_items_forbidden",
    ):
        if rules.get(rule) is not True:
            fail("A5", f"set-dressing rule weakened or missing: {rule}")

    # A6 — the source/shipping boundary is mechanical, not narrative.
    piece_names = [
        "neighborhood_common_hall", "avenue_north", "avenue_south", "avenue_east",
        "avenue_west", "common_row_house", "courtyard_home", "artisan_house_shop",
        "extended_kin_hall", "district_cistern", "collapsed_trace_field",
        "district_mass_grave",
    ]
    pool_names = [
        "start", "avenue_north", "avenue_south", "avenue_east", "avenue_west",
        "residential", "grave_terminal", "cistern_terminal", "trace_terminal",
    ]
    generated = [
        *(ROOT / "kubejs" / "data" / "alfheim" / "structures" / "ancient" /
          "common_residential" / f"{name}.nbt" for name in piece_names),
        *(ROOT / "kubejs" / "data" / "alfheim" / "worldgen" / "template_pool" /
          "ancient" / "common_residential" / f"{name}.json" for name in pool_names),
        ROOT / "kubejs" / "data" / "alfheim" / "worldgen" / "structure" /
        "common_residential_quarter.json",
        ROOT / "kubejs" / "data" / "alfheim" / "worldgen" / "structure_set" /
        "common_residential_quarter.json",
        ROOT / "kubejs" / "data" / "alfheim" / "tags" / "worldgen" / "biome" /
        "has_common_residential_quarter.json",
    ]
    present = [path for path in generated if path.exists()]
    shipping_required = stage in STAGES and STAGES.index(stage) >= STAGES.index("shipping_generated")
    if shipping_required:
        missing = [str(path.relative_to(ROOT)) for path in generated if not path.exists()]
        if missing:
            fail("A6", f"family status {stage} requires complete shipping corpus; missing {missing}")
    elif present:
        fail(
            "A6",
            f"family status {stage} has a partial/generated shipping corpus ({len(present)}/24); "
            "either regenerate and advance coherently or restore source-contract-only state",
        )

    # A7 — source code itself must preserve the generation boundary.
    if 'assert all(v <= MAX_AXIS for v in p.size)' not in source:
        fail("A7", "generator no longer asserts the 48-axis piece boundary")
    if 'assert p.dropped == 0' not in source:
        fail("A7", "generator no longer rejects clipped piece output")
    if '"terrain_adaptation": "beard_thin"' not in source:
        fail("A7", "terrain adaptation drifted from the source contract")
    if '"project_start_to_heightmap": "WORLD_SURFACE_WG"' not in source:
        fail("A7", "surface projection drifted from the source contract")

    if args.verbose:
        print(f"family status: {stage}")
        print(f"semantic members: {len(members)}; generated piece types: {len(piece_names)}")
        print(f"declared shipping corpus: {len(generated)} files; present: {len(present)}")
        print(f"set dressing: {', '.join(sorted(categories))}")

    if problems:
        print(f"ancient district validation: {len(problems)} problem(s)")
        for problem in problems:
            print(problem)
        return 1

    print(
        f"ancient district validation: 0 problems; status={stage}; "
        f"{len(members)} semantic members, {len(piece_names)} generated piece types, "
        f"{len(categories)} set-dressing categories"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
