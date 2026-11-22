"""Fail-closed regressions for the existing static district manifest checker.

Only source JSON contracts are checked; this suite does not generate or inspect NBT.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.check_ancient_district_manifest import check

BASE = json.loads((ROOT / "tools/ancient_district_manifest.json").read_text(encoding="utf-8"))


class ManifestSchemaSafetyTest(unittest.TestCase):
    def test_original_manifest_and_inline_family_valid(self):
        self.assertEqual([], check(deepcopy(BASE)))
        self.assertEqual([], check({**deepcopy(BASE), "families": [deepcopy(BASE["families"][0])]}))

    def test_top_level_and_policy_reject_invalid_types(self):
        samples = [("top_list", []), ("top_null", None)]
        for name, payload in samples:
            with self.subTest(name=name):
                self.assertProblems(payload, "manifest")
        for name, value in [("policy_list", []), ("policy_null", None), ("policy_string", "bad")]:
            with self.subTest(name=name):
                self.assertPatched(["generation_policy"], value, "generation_policy")
        for val in ["forty-eight", [], {}, None, True, 48.9, -1, 49]:
            with self.subTest(max_axis=val):
                self.assertPatched(["generation_policy", "max_piece_axis"], val, "max_piece_axis")
        self.assertPatched(["generation_policy", "terrain_fit_required"], False, "terrain_fit_required")
        self.assertPatched(["generation_policy", "minimum_decline_stages_hero"], "three", "minimum_decline_stages_hero")

    def test_malformed_families_fail_closed(self):
        for val in ["wrong", {}, None, [None], ["not a family"], [123], [["bad"]]]:
            with self.subTest(families=val):
                self.assertPatched(["families"], val, "famil")
        self.assertPatched(["families", 0, "id"], [], "family id")
        self.assertPatched(["families", 0, "id"], "", "family id")
        self.assertPatched(["families", 1, "implementation_contract"], [], "contract")
        self.assertPatched(["families", 1, "contract"], "../escape.json", "contract")
        self.assertPatched(["families", 1, "decline_stages"], [[1]], "decline_stages")

    def test_inline_family_requires_structure_and_chronology(self):
        f = 0
        for key, val, needle in [
            ("intended_extent", 12, "intended_extent"),
            ("intended_extent", ["huge", 48, 100], "intended_extent"),
            ("intended_extent", [100, 48, 100], "160"),
            ("decline_stages", "12345", "decline_stages"),
            ("decline_stages", [[1], 3, 4, 5], "decline_stages"),
            ("advanced_systems", "abc", "advanced_systems"),
            ("advanced_systems", ["one"], "advanced_systems"),
            ("circulation", [], "circulation"),
            ("circulation", {"must_connect_every_inhabited_member": True}, "burial edge"),
            ("terrain", None, "terrain"),
            ("members", "not-members", "members"),
            ("members", [None] * 9, "member"),
            ("acceptance", "anything", "acceptance"),
        ]:
            with self.subTest(key=key, val=val):
                self.assertPatched(["families", f, key], val, needle)

    def test_inline_member_types_and_bounds(self):
        pos = ["families", 0, "members", 0]
        for key, val, needle in [
            ("id", [], "member id"),
            ("role", [], "role"),
            ("archetype", {}, "archetype"),
            ("piece_size", None, "piece_size"),
            ("piece_size", [48, "x", 48], "piece_size"),
            ("piece_size", [48, 0, 48], "piece_size"),
            ("piece_size", [48.5, 34, 40], "piece_size"),
            ("count", "range", "count"),
            ("count", [1, "many"], "count"),
            ("count", [True, 1], "count"),
            ("decline_stages", "1345", "decline_stages"),
            ("decline_stages", [[1], 3, 4, 5], "decline_stages"),
            ("evidence", {"wrong": "type"}, "evidence"),
            ("evidence", [["bad"]], "evidence"),
        ]:
            with self.subTest(key=key, val=val):
                self.assertPatched(pos + [key], val, needle)
        self.assertPatched(["families", 0, "members", 0, "piece_size"], [49, 34, 40], "piece_size")

    def test_invariant_gates_stay_active(self):
        self.assertPatched(["families", 0, "circulation", "must_connect_burial_edge"], False, "burial edge")
        self.assertPatched(["families", 0, "circulation", "must_connect_every_inhabited_member"], False, "circulation")
        self.assertPatched(["families", 0, "terrain", "reject_naked_cantilever"], False, "terrain")
        self.assertPatched(["families", 0, "terrain", "severe_relief_requires_authored_substructure"], False, "terrain")
        self.assertPatched(["families", 0, "acceptance", "must_include_mortuary_edge"], False, "must_include_mortuary_edge")
        missing_collapse = deepcopy(BASE)
        for member in missing_collapse["families"][0]["members"]:
            member["evidence"] = [e for e in member["evidence"]
                                  if e not in {"civilian_remains", "household_remains", "unfinished_pits", "workbench_remains"}]
        self.assertProblems(missing_collapse, "collapse")

    def assertPatched(self, path, value, substring):
        payload = deepcopy(BASE)
        cur = payload
        for key in path[:-1]:
            cur = cur[key]
        cur[path[-1]] = value
        self.assertProblems(payload, substring)

    def assertProblems(self, payload, needle):
        try:
            problems = check(payload)
        except Exception as exc:
            self.fail(f"checker raised {type(exc).__name__} instead of returning stable failures: {exc}")
        self.assertIsInstance(problems, list)
        self.assertTrue(any(needle.lower() in p.lower() for p in problems),
                        f"must reject {needle!r}; got {problems[:5]!r}")


if __name__ == "__main__":
    unittest.main()
