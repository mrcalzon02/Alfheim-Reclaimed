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


def _integer(value: object, minimum: int = 0) -> bool:
    """Reject booleans, strings and fractional JSON values even if int() accepts them."""
    return type(value) is int and value >= minimum


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _text_list(value: object, minimum: int = 0) -> bool:
    return isinstance(value, list) and len(value) >= minimum and all(_text(v) for v in value)


def _stages(value: object) -> bool:
    return isinstance(value, list) and all(type(v) is int and 1 <= v <= 5 for v in value)


def _contract_path(value: object) -> bool:
    """Recognize already-authored first-party district manifest references; never resolve arbitrary paths."""
    return (_text(value) and value.startswith("tools/") and value.endswith("_manifest.json")
            and all(part not in ("", ".", "..") for part in value.split("/"))
            and len(value.split("/")) == 2)


def check(data: dict) -> list[str]:
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["manifest must be an object"]
    if data.get("schema") != "alfheim:ancient_districts/v1":
        fail(problems, "schema must be alfheim:ancient_districts/v1")

    policy = data.get("generation_policy")
    if not isinstance(policy, dict):
        fail(problems, "generation_policy must be an object")
        return problems
    if policy.get("placement_model") != "district_anchor_family":
        fail(problems, "placement model must be district_anchor_family")
    if policy.get("forbid_independent_member_random_spread") is not True:
        fail(problems, "independent member random_spread must be forbidden")
    if policy.get("terrain_fit_required") is not True:
        fail(problems, "terrain_fit_required must be true")
    max_axis = policy.get("max_piece_axis")
    if not _integer(max_axis, 1) or max_axis > 48:
        fail(problems, "max_piece_axis must be an integer within Minecraft's 1–48-block template boundary")
        # A missing/invalid limit cannot safely be compared against member dimensions.
        return problems
    min_stages = {}
    for key, default in (("minimum_decline_stages_hero", 3), ("minimum_decline_stages_member", 2)):
        value = policy.get(key, default)
        if not _integer(value, 1) or value > 5:
            fail(problems, f"{key} must be an integer between 1 and 5")
            value = default
        min_stages[key] = value

    families = data.get("families")
    if not isinstance(families, list):
        fail(problems, "families must be a list")
        return problems
    if not families:
        fail(problems, "at least one district family is required")
        return problems

    seen: set[str] = set()
    for index, fam in enumerate(families):
        if not isinstance(fam, dict):
            fail(problems, f"family #{index}: family must be an object")
            continue
        fid = fam.get("id")
        if not _text(fid):
            fail(problems, f"family #{index}: family id must be nonempty text")
            fid = f"<family #{index}>"
        elif fid in seen:
            fail(problems, f"{fid}: duplicate family id")
        seen.add(fid)
        if not _text(fam.get("anchor")):
            fail(problems, f"{fid}: anchor must be nonempty text")

        # Newer district families store their detailed chronology/geometry in a
        # separate original manifest; the top-level entry is only a summary.
        # Do not mistake a summary for a fully inlined member declaration.
        refs = [key for key in ("contract", "implementation_contract") if key in fam]
        for key in refs:
            if not _contract_path(fam[key]):
                fail(problems, f"{fid}: {key} must be a tools/*_manifest.json contract path")
        if "members" not in fam and refs:
            if "decline_stages" in fam:
                stages = fam["decline_stages"]
                if not _stages(stages) or not {1, 3, 4, 5}.issubset(stages):
                    fail(problems, f"{fid}: decline_stages must preserve healthy/emergency/collapse/long-decay chronology")
            continue
        if "members" not in fam:
            fail(problems, f"{fid}: members or a referenced implementation contract is required")
            continue

        extent = fam.get("intended_extent")
        if not (isinstance(extent, list) and len(extent) == 3
                and all(_integer(v, 1) for v in extent)):
            fail(problems, f"{fid}: intended_extent must have three positive integer axes")
        elif max(extent[0], extent[2]) < 160:
            fail(problems, f"{fid}: district must span at least 160 blocks horizontally")
        stages = fam.get("decline_stages")
        if not _stages(stages):
            fail(problems, f"{fid}: decline_stages must be a list of integer stages 1 through 5")
        elif not {1, 3, 4, 5}.issubset(stages):
            fail(problems, f"{fid}: family must carry healthy/emergency/collapse/long-decay chronology")
        advanced = fam.get("advanced_systems")
        if not _text_list(advanced, 2):
            fail(problems, f"{fid}: advanced_systems must contain at least two named systems")

        circulation = fam.get("circulation")
        if not isinstance(circulation, dict):
            fail(problems, f"{fid}: circulation must be an object")
        else:
            if circulation.get("must_connect_every_inhabited_member") is not True:
                fail(problems, f"{fid}: inhabited members must share real circulation")
            if circulation.get("must_connect_burial_edge") is not True:
                fail(problems, f"{fid}: district must physically connect to its burial edge")
            if circulation.get("must_show_blocked_or_failed_routes") is not True:
                fail(problems, f"{fid}: circulation must show blocked or failed routes")
        terrain = fam.get("terrain")
        if not isinstance(terrain, dict):
            fail(problems, f"{fid}: terrain must be an object")
        elif (terrain.get("reject_naked_cantilever") is not True
              or terrain.get("severe_relief_requires_authored_substructure") is not True):
            fail(problems, f"{fid}: terrain must prohibit cantilevers and require severe-relief substructure")

        members = fam.get("members")
        if not isinstance(members, list):
            fail(problems, f"{fid}: members must be a list")
            continue
        if len(members) < 8:
            fail(problems, f"{fid}: district vocabulary too small ({len(members)} members)")
        member_ids: set[str] = set()
        evidence: set[str] = set()
        minimum_count = 0
        inhabited_min = 0
        archetypes: set[str] = set()
        roles: set[str] = set()
        for mi, member in enumerate(members):
            if not isinstance(member, dict):
                fail(problems, f"{fid}: member #{mi} must be an object")
                continue
            mid = member.get("id")
            if not _text(mid):
                fail(problems, f"{fid}: member id at #{mi} must be nonempty text")
                mid = f"<member #{mi}>"
            elif mid in member_ids:
                fail(problems, f"{fid}: duplicate member id {mid}")
            member_ids.add(mid)
            role = member.get("role")
            if not _text(role):
                fail(problems, f"{fid}/{mid}: role must be nonempty text")
            else:
                roles.add(role)
            archetype = member.get("archetype")
            if not _text(archetype):
                fail(problems, f"{fid}/{mid}: archetype must be nonempty text")
            else:
                archetypes.add(archetype)
            size = member.get("piece_size")
            if not (isinstance(size, list) and len(size) == 3
                    and all(_integer(v, 1) for v in size)):
                fail(problems, f"{fid}/{mid}: piece_size requires three positive integer axes")
            elif any(v > max_axis for v in size):
                fail(problems, f"{fid}/{mid}: piece_size exceeds {max_axis}-block axis boundary: {size}")
            count = member.get("count")
            if not (isinstance(count, list) and len(count) == 2
                    and all(_integer(v) for v in count) and count[1] >= count[0]):
                fail(problems, f"{fid}/{mid}: invalid count range {count}")
            else:
                minimum_count += count[0]
                if _text(role) and role in {"hero_anchor", "residential_member", "economic_member"}:
                    inhabited_min += count[0]
            member_stages = member.get("decline_stages")
            if not _stages(member_stages):
                fail(problems, f"{fid}/{mid}: decline_stages must be integer stages 1–5")
            else:
                required = min_stages["minimum_decline_stages_hero"] if role == "hero_anchor" else min_stages["minimum_decline_stages_member"]
                if len(set(member_stages)) < required:
                    fail(problems, f"{fid}/{mid}: insufficient decline chronology")
            member_evidence = member.get("evidence")
            if not _text_list(member_evidence):
                fail(problems, f"{fid}/{mid}: evidence must be a list of named clues")
            else:
                evidence.update(member_evidence)

        if not {"hero_anchor", "mortuary_edge_member", "circulation_member"}.issubset(roles):
            fail(problems, f"{fid}: requires hero anchor, circulation, and mortuary-edge members")
        acc = fam.get("acceptance")
        if not isinstance(acc, dict):
            fail(problems, f"{fid}: acceptance must be an object")
            continue
        for key, actual, explanation in (
            ("minimum_members_per_site", minimum_count, "minimum generated member count"),
            ("minimum_inhabited_members", inhabited_min, "inhabited minimum"),
            ("minimum_distinct_archetypes", len(archetypes), "archetype diversity"),
        ):
            floor = acc.get(key)
            if not _integer(floor):
                fail(problems, f"{fid}: acceptance {key} must be a nonnegative integer")
            elif actual < floor:
                fail(problems, f"{fid}: {explanation} {actual} below acceptance floor {floor}")
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


def check_references(data: object, source_root: Path = ROOT) -> list[str]:
    """Fail closed on broken first-party referenced family contracts.

    The reference files are source JSON, *not* NBT or runtime/world evidence.  The
    sacred-precinct contract is a generated numeric/layout report rather than the
    eight authored schema/member-list manifests; keep that distinction explicit.
    """
    problems: list[str] = []
    if not isinstance(data, dict) or not isinstance(data.get("families"), list):
        return ["referenced family check requires a manifest with a families list"]
    seen_paths: set[str] = set()
    for index, fam in enumerate(data["families"]):
        if not isinstance(fam, dict):
            continue  # already rejected by check()
        fid = fam.get("id", f"family #{index}")
        refs = [key for key in ("contract", "implementation_contract") if key in fam]
        if len(refs) > 1:
            fail(problems, f"{fid}: multiple contract reference fields are ambiguous")
        for key in refs:
            raw = fam[key]
            if not _contract_path(raw):
                continue  # already rejected by check(); never open unsafe paths
            if raw in seen_paths:
                fail(problems, f"{fid}: duplicate contract reference {raw}")
                continue
            seen_paths.add(raw)
            path = source_root / raw
            try:
                reference = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                fail(problems, f"{fid}: contract {raw} cannot be read as JSON ({type(exc).__name__})")
                continue
            if not isinstance(reference, dict):
                fail(problems, f"{fid}: contract {raw} must contain a JSON object")
                continue
            stem = path.stem.removesuffix("_manifest")
            expected_schema = f"alfheim:{stem}/v1"
            if stem != "sacred_precinct":
                if reference.get("schema") != expected_schema:
                    fail(problems, f"{fid}: contract {raw} schema must be {expected_schema}")
                anchor = reference.get("anchor")
                if not isinstance(reference.get("members"), list):
                    fail(problems, f"{fid}: contract {raw} members must be a list")
                    member_count = None
                else:
                    member_count = len(reference["members"])
                wave = reference.get("wave")
                if type(wave) is not int or wave != fam.get("wave"):
                    fail(problems, f"{fid}: contract {raw} wave disagrees with summary")
            else:
                # The existing generated sacred report has no schema/wave/anchor
                # fields, but its first layout entry names the authored anchor.
                layout = reference.get("layout")
                anchor = (layout[0].get("name") if isinstance(layout, list)
                          and layout and isinstance(layout[0], dict) else None)
                member_count = reference.get("members")
                if not _integer(member_count, 1):
                    fail(problems, f"{fid}: sacred contract {raw} members must be a positive integer")
                    member_count = None
                joins = reference.get("joins")
                if not _integer(joins) or joins != fam.get("supported_connections"):
                    fail(problems, f"{fid}: sacred contract {raw} joins disagree with summary")
            if not _text(anchor) or anchor != fam.get("anchor"):
                fail(problems, f"{fid}: contract {raw} anchor disagrees with summary")
            summary_count = fam.get("assembled_members", fam.get("members_per_site"))
            if not _integer(summary_count, 1) or member_count != summary_count:
                fail(problems, f"{fid}: contract {raw} member count disagrees with summary")
    return problems


def self_test() -> None:
    clean = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert not check(clean), check(clean)
    assert not check_references(clean), check_references(clean)
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
    if not problems:
        problems.extend(check_references(data))
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
