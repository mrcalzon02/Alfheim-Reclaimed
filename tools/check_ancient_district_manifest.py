"""Static contract checker for civilization-scale ancient Alfheim district families.

This checker validates the source contract only. It does not claim NBT generation, runtime
placement, fresh-world generation, terrain fit, or production admission.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "ancient_district_manifest.json"

REQUIRED_EVIDENCE = {
    "original": {"durable_paving", "shared_walls", "public_kitchen", "sleeping_galleries", "filter_beds"},
    "emergency": {"ration_queue", "barricades", "refuge_crowding", "emergency_water_queue", "sealed_sick_room"},
    "collapse": {"civilian_remains", "household_remains", "unfinished_pits", "workbench_remains"},
    "decay": {"root_buckling", "silted_basin", "secondary_collapse", "patched_roofs"},
}


def fail(problems: list[str], message: str) -> None:
    problems.append(message)


def check(data: dict) -> list[str]:
    problems: list[str] = []
    policy = data.get("generation_policy", {})
    if data.get("schema") != "alfheim:ancient_districts/v1":
        fail(problems, "schema must be alfheim:ancient_districts/v1")
    if policy.get("placement_model") != "district_anchor_family":
        fail(problems, "placement model must be district_anchor_family")
    if policy.get("forbid_independent_member_random_spread") is not True:
        fail(problems, "independent member random_spread must be forbidden")
    max_axis = int(policy.get("max_piece_axis", 0))
    if not 1 <= max_axis <= 48:
        fail(problems, "max_piece_axis must remain within Minecraft's 48-block template boundary")

    families = data.get("families", [])
    if not families:
        fail(problems, "at least one district family is required")
        return problems

    seen = set()
    for fam in families:
        fid = fam.get("id", "<missing>")
        if fid in seen:
            fail(problems, f"{fid}: duplicate family id")
        seen.add(fid)
        extent = fam.get("intended_extent", [0, 0, 0])
        if len(extent) != 3 or max(extent[0], extent[2]) < 160:
            fail(problems, f"{fid}: district must span at least 160 blocks horizontally")
        stages = set(fam.get("decline_stages", []))
        if not {1, 3, 4, 5}.issubset(stages):
            fail(problems, f"{fid}: family must carry healthy/emergency/collapse/long-decay chronology")
        if len(fam.get("advanced_systems", [])) < 2:
            fail(problems, f"{fid}: advanced elven infrastructure is under-specified")

        circulation = fam.get("circulation", {})
        if circulation.get("must_connect_every_inhabited_member") is not True:
            fail(problems, f"{fid}: inhabited members must share real circulation")
        if circulation.get("must_connect_burial_edge") is not True:
            fail(problems, f"{fid}: district must physically connect to its burial edge")

        members = fam.get("members", [])
        if len(members) < 8:
            fail(problems, f"{fid}: district vocabulary too small ({len(members)} members)")
        member_ids = set()
        evidence = set()
        minimum_count = 0
        inhabited_min = 0
        archetypes = set()
        roles = set()
        for member in members:
            mid = member.get("id", "<missing>")
            if mid in member_ids:
                fail(problems, f"{fid}: duplicate member id {mid}")
            member_ids.add(mid)
            roles.add(member.get("role"))
            archetypes.add(member.get("archetype"))
            size = member.get("piece_size", [999, 999, 999])
            if len(size) != 3 or any(int(v) > max_axis for v in size):
                fail(problems, f"{fid}/{mid}: piece exceeds {max_axis}-block axis boundary: {size}")
            count = member.get("count", [0, 0])
            if len(count) != 2 or count[0] < 0 or count[1] < count[0]:
                fail(problems, f"{fid}/{mid}: invalid count range {count}")
                continue
            minimum_count += int(count[0])
            if member.get("role") in {"hero_anchor", "residential_member", "economic_member"}:
                inhabited_min += int(count[0])
            member_stages = set(member.get("decline_stages", []))
            min_member_stages = policy.get("minimum_decline_stages_hero", 3) if member.get("role") == "hero_anchor" else policy.get("minimum_decline_stages_member", 2)
            if len(member_stages) < int(min_member_stages):
                fail(problems, f"{fid}/{mid}: insufficient decline chronology")
            evidence.update(member.get("evidence", []))

        if "hero_anchor" not in roles or "mortuary_edge_member" not in roles or "circulation_member" not in roles:
            fail(problems, f"{fid}: requires hero anchor, circulation, and mortuary-edge members")
        acc = fam.get("acceptance", {})
        if minimum_count < int(acc.get("minimum_members_per_site", 0)):
            fail(problems, f"{fid}: minimum generated member count {minimum_count} below acceptance floor")
        if inhabited_min < int(acc.get("minimum_inhabited_members", 0)):
            fail(problems, f"{fid}: inhabited minimum {inhabited_min} below acceptance floor")
        if len(archetypes) < int(acc.get("minimum_distinct_archetypes", 0)):
            fail(problems, f"{fid}: insufficient archetype diversity")
        for band, options in REQUIRED_EVIDENCE.items():
            if not evidence.intersection(options):
                fail(problems, f"{fid}: no evidence covers {band} chronology")
        for key in (
            "must_show_original_function", "must_show_emergency_conversion",
            "must_show_terminal_collapse", "must_show_long_decay",
            "must_include_mortuary_edge", "must_include_advanced_infrastructure",
            "must_include_connected_route_from_anchor_to_burial_edge",
            "must_not_bypass_progression",
        ):
            if acc.get(key) is not True:
                fail(problems, f"{fid}: acceptance invariant {key} must be true")
    return problems


def self_test() -> None:
    clean = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert not check(clean), check(clean)
    bad = json.loads(json.dumps(clean))
    bad["families"][0]["members"][0]["piece_size"][0] = 49
    assert any("exceeds" in p for p in check(bad))
    bad = json.loads(json.dumps(clean))
    bad["families"][0]["circulation"]["must_connect_burial_edge"] = False
    assert any("burial edge" in p for p in check(bad))
    bad = json.loads(json.dumps(clean))
    bad["generation_policy"]["forbid_independent_member_random_spread"] = False
    assert any("random_spread" in p for p in check(bad))


def main() -> int:
    if "--self-test" in sys.argv:
        self_test()
        print("ancient district manifest self-test: PASS")
        return 0
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    problems = check(data)
    if problems:
        for problem in problems:
            print("FAIL:", problem)
        return 1
    fam = data["families"][0]
    print(f"ancient district manifest: PASS — {len(data['families'])} family, {len(fam['members'])} member types, extent {fam['intended_extent'][0]}x{fam['intended_extent'][2]}")
    print("static contract only; runtime/worldgen/terrain-fit admission remains pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
