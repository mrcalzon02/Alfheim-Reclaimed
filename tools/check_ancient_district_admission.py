"""Fail-closed evidence gate for Common Residential Quarter production admission.

This verifies declaration consistency, not actual NBT or fresh-world gameplay.
The enclosing district checker separately verifies source/shipping artifact equality.
"""
from __future__ import annotations

import copy

REQUIRED_ADMISSION_EVIDENCE = {
    "evidence_scope": "fresh_world_natural_placement",
    "shipping_state": "committed_and_verified",
    "source_to_shipping_equality": "pass_decoded_nbt_and_json_bytes",
    "runtime_state": "natural_placement_validated",
    "client_visual_state": "accepted",
    "fresh_world_state": "accepted",
    "terrain_fit_state": "accepted",
}


def admission_errors(manifest: dict) -> list[str]:
    """Reject an asserted production status lacking independent acceptance fields."""
    families = manifest.get("families", [])
    if not isinstance(families, list):
        return ["families must be a list"]

    problems = []
    matches = []
    for index, family in enumerate(families):
        if not isinstance(family, dict):
            problems.append(f"families[{index}] must be an object")
        elif family.get("id") == "common_residential_quarter":
            matches.append(family)

    if len(matches) > 1:
        problems.append("duplicate common_residential_quarter family ids are forbidden")

    # Inspect *every* matching entry: a non-admitted first match must not mask
    # a later production claim with missing or forged evidence.
    if not any(family.get("status") == "production_admitted" for family in matches):
        return problems
    evidence = manifest.get("generation_evidence")
    if not isinstance(evidence, dict):
        problems.append("production_admitted requires generation_evidence object")
        return problems
    if evidence.get("family") != "common_residential_quarter":
        problems.append("production_admitted evidence must belong to common_residential_quarter")
    for field, required in REQUIRED_ADMISSION_EVIDENCE.items():
        if evidence.get(field) != required:
            problems.append(
                f"production_admitted requires generation_evidence.{field}={required!r}"
            )
    return problems


def self_test() -> None:
    # Reproduce current source evidence: controlled assembly, not admitted production.
    baseline = {
        "families": [{"id": "common_residential_quarter", "status": "runtime_validated"}],
        "generation_evidence": {
            "family": "common_residential_quarter",
            "evidence_scope": "controlled_fresh_world_assembly",
            "shipping_state": "generated_uncommitted",
            "source_to_shipping_equality": "pass_decoded_nbt_and_json_bytes",
            "runtime_state": "assembly_validated",
            "client_visual_state": "pending",
        },
    }
    assert not admission_errors(baseline), "existing runtime status must remain valid"
    forged = copy.deepcopy(baseline)
    forged["families"][0]["status"] = "production_admitted"
    problems = admission_errors(forged)
    assert any("shipping_state" in p for p in problems), problems
    assert any("client_visual_state" in p for p in problems), problems
    assert any("fresh_world_state" in p for p in problems), problems
    assert any("terrain_fit_state" in p for p in problems), problems

    complete = copy.deepcopy(forged)
    complete["generation_evidence"].update(REQUIRED_ADMISSION_EVIDENCE)
    assert not admission_errors(complete), admission_errors(complete)
    for field in REQUIRED_ADMISSION_EVIDENCE:
        partial = copy.deepcopy(complete)
        partial["generation_evidence"].pop(field)
        assert any(field in p for p in admission_errors(partial)), field
    wrong_family = copy.deepcopy(complete)
    wrong_family["generation_evidence"]["family"] = "elder_lineage_precinct"
    assert admission_errors(wrong_family)
    missing_evidence = copy.deepcopy(complete)
    del missing_evidence["generation_evidence"]
    assert admission_errors(missing_evidence)

    # Regression: duplicate IDs must never bypass independent admission evidence,
    # whether the production claim comes first or second.
    for statuses in (
        ("runtime_validated", "production_admitted"),
        ("production_admitted", "runtime_validated"),
    ):
        duplicate = copy.deepcopy(baseline)
        duplicate["families"] = [
            {"id": "common_residential_quarter", "status": status}
            for status in statuses
        ]
        duplicate.pop("generation_evidence")
        problems = admission_errors(duplicate)
        assert any("duplicate" in p for p in problems), problems
        assert any("generation_evidence" in p for p in problems), problems
        duplicate["generation_evidence"] = complete["generation_evidence"]
        assert any("duplicate" in p for p in admission_errors(duplicate))

    # Malformed family entries produce explicit errors rather than crashing or
    # being skipped because a valid entry appears earlier.
    for entries in ((None, baseline["families"][0]), (baseline["families"][0], "bad")):
        problems = admission_errors({"families": list(entries)})
        assert any("families[" in p for p in problems), problems
    assert any("families" in p for p in admission_errors({"families": None}))



if __name__ == "__main__":
    self_test()
    print("ancient district production-admission negative controls: PASS")
