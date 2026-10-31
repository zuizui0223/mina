"""Tests on the source-pinned 301-interval long sea-ice forward-only diagnostic."""
import copy
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research/climate-penguin/work/scenario_support_v1"))
import long_count_forward_gate_v2 as m


class LongCountForwardGate(unittest.TestCase):
    def test_gaussian_system(self):
        sol = m.solve([[4, 1], [1, 3]], [1, 2])
        self.assertAlmostEqual(sol[0], 1/11, places=12)
        self.assertAlmostEqual(sol[1], 7/11, places=12)

    def test_source_math_and_receipt(self):
        rows = m.rows_from_source()
        self.assertEqual(len(rows), 301)
        self.assertEqual({r["end"]-r["start"] for r in rows}, {1})
        result = m.analyze(rows)
        reference = json.loads(m.EXPECTED.read_text(encoding="utf-8"))
        m.verify(result, reference)
        self.assertEqual(result["subsets"]["all"]["n"], 129)
        self.assertEqual(result["subsets"]["timingNonVictoria"]["n"], 8)

    def test_future_response_is_never_in_2005_training(self):
        rows = m.rows_from_source()
        initial = [x for x in m.analyze(rows)["predictions"] if x["test_start"] == 2005]
        changed = copy.deepcopy(rows)
        for row in changed:
            if row["start"] >= 2005:
                row["y"] += 20
        again = [x for x in m.analyze(changed)["predictions"] if x["test_start"] == 2005]
        for a, b in zip(initial, again):
            self.assertEqual(a["site_id"], b["site_id"])
            for k in m.SPEC:
                self.assertAlmostEqual(a[k], b[k], places=10)

    def test_start_year_and_end_year_exposure_separated(self):
        rows = m.rows_from_source()
        a = m.analyze(rows)["predictions"]
        first = a[0]
        self.assertNotAlmostEqual(first["near"], first["end"], places=8)
        self.assertNotAlmostEqual(first["near"], first["far"], places=8)

    def test_metrics_definition(self):
        fake = [{"site_id":"a","region":"A","test_start":1,"zero":0.0,
                 "site":0.1,"near":0.2,"far":0.3,"both":0.4,"end":0.5,"delta":0.6,
                 "observed_log_growth":0.2}]
        out = m.metrics(fake)
        self.assertAlmostEqual(out["near_mae"],0)
        self.assertAlmostEqual(out["zero_rmse"],0.2)


if __name__ == "__main__":
    unittest.main()
