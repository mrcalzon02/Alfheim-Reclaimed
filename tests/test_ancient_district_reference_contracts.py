"""Offline regressions for the first-party district *source-reference* guard.

Fixture contracts are minimal projections of nine source-manifest fields,
not exact original files, NBT objects or evidence of installed world generation.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from tools.check_ancient_district_manifest import check, check_references

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / "tools/ancient_district_manifest.json").read_text(encoding="utf-8"))


class SourceReferenceContractTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "tools").mkdir()
        # Source-derived structural projections only: the genuine authenticated
        # GitHub JSON documents are checked separately; no reconstructed blob
        # is misrepresented as a byte-exact repository checkout.
        self.source = {}
        for fam in BASE["families"]:
            raw = fam.get("contract", fam.get("implementation_contract"))
            if not raw:
                continue
            stem = Path(raw).stem.removesuffix("_manifest")
            if stem == "sacred_precinct":
                contract = {"members": 7, "joins": 6,
                            "layout": [{"name": "great_temple_court"}]}
            else:
                count = fam.get("assembled_members", fam.get("members_per_site"))
                contract = {"schema": f"alfheim:{stem}/v1",
                            "anchor": fam["anchor"], "wave": fam["wave"],
                            "members": [{"id": str(i)} for i in range(count)]}
            self.source[raw] = contract
            self.write(raw, contract)

    def write(self, path, data):
        (self.root / path).write_text(json.dumps(data), encoding="utf-8")

    def problems(self, data=None):
        return check_references(BASE if data is None else data, self.root)

    def assertBroken(self, data, needle):
        errors = self.problems(data)
        self.assertTrue(any(needle in err.lower() for err in errors), errors)

    def test_all_nine_source_projections_and_legacy_invariants(self):
        self.assertEqual(9, len(self.source))
        self.assertEqual([], check(BASE))
        self.assertEqual([], self.problems())
        self.assertEqual([], check({**BASE, "families": [BASE["families"][0]]}))

    def test_missing_and_invalid_original_reference_rejected(self):
        raw = BASE["families"][1]["contract"]
        (self.root / raw).unlink()
        self.assertBroken(BASE, "cannot be read")
        self.write(raw, ["not-object"])
        self.assertBroken(BASE, "json object")
        (self.root / raw).write_text("{", encoding="utf-8")
        self.assertBroken(BASE, "jsondecodeerror")

    def test_duplicate_and_ambiguous_references_rejected(self):
        duplicate = deepcopy(BASE)
        duplicate["families"][2]["implementation_contract"] = duplicate["families"][1]["contract"]
        self.assertBroken(duplicate, "duplicate contract reference")
        ambiguous = deepcopy(BASE)
        ambiguous["families"][1]["implementation_contract"] = "tools/civic_center_manifest.json"
        self.assertBroken(ambiguous, "multiple contract reference")

    def test_wrong_schema_anchor_wave_and_member_count_rejected(self):
        raw = BASE["families"][1]["contract"]
        for key, bad, needle in [("schema", "alfheim:other/v1", "schema"),
                                 ("anchor", "wrong_hall", "anchor"),
                                 ("wave", 3, "wave"),
                                 ("members", [], "member count")]:
            with self.subTest(key=key):
                broken = deepcopy(self.source[raw])
                broken[key] = bad
                self.write(raw, broken)
                self.assertBroken(BASE, needle)
                self.write(raw, self.source[raw])

    def test_sacred_report_shape_is_explicit_and_counted(self):
        raw = BASE["families"][-1]["implementation_contract"]
        for key, bad, needle in [("members", "seven", "members"),
                                 ("joins", 2, "joins"),
                                 ("layout", [], "anchor")]:
            with self.subTest(key=key):
                broken = deepcopy(self.source[raw])
                broken[key] = bad
                self.write(raw, broken)
                self.assertBroken(BASE, needle)
                self.write(raw, self.source[raw])

    def test_contract_path_exclusion_remains_fail_closed(self):
        malformed = deepcopy(BASE)
        malformed["families"][1]["contract"] = "../outside_manifest.json"
        self.assertTrue(any("contract path" in x for x in check(malformed)))
        # The reference loader does not dereference failed path grammar.
        self.assertEqual([], self.problems(malformed))


if __name__ == "__main__":
    unittest.main()
