"""Verify positive evidence numbers against original frozen outputs and retain negative gates."""
import unittest
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"research/climate-penguin/outputs/positive_evidence_merged_v1/ledger.json"
class EvidenceMergeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.j=json.loads(FILE.read_text(encoding="utf-8"))
    def test_science_merges_not_author_signoff_merges(self):
        self.assertFalse(self.j["paper_status"]["merge_main_authorized"])
        self.assertEqual(self.j["state"],"merged_scientific_evidence_in_draft_PR206_only")
    def test_exact_frozen_numerical_endpoints(self):
        for row in self.j["supported"]:
            source=ROOT/row["source"]
            self.assertTrue(source.exists(),row["id"])
            original=json.loads(source.read_text(encoding="utf-8"))
            value=original
            for part in row["key"]:value=value[part]
            self.assertTrue(math.isclose(value,row["value"],rel_tol=1e-12,abs_tol=1e-12),row["id"])
            self.assertTrue(row["boundary"])
    def test_bad_scientific_news_not_erased(self):
        self.assertGreaterEqual(len(self.j["failed_or_open"]),7)
        self.assertTrue(any("2013" in x for x in self.j["failed_or_open"]))
        self.assertTrue(any("2050/2100" in x for x in self.j["failed_or_open"]))
    def test_draft_references_separated(self):
        self.assertEqual({x["pr"] for x in self.j["external_draft_evidence"]},{189,199})
        self.assertGreaterEqual(len(self.j["external_draft_evidence"]),2)
        self.assertGreaterEqual(len(self.j["verified_exploratory"]),5)
if __name__=="__main__":
    unittest.main()
