"""Source and time-leakage tests for count_growth_forward_gate_v1."""
import copy
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research/climate-penguin/work/scenario_support_v1"))
import count_growth_forward_gate_v1 as m


class ForwardAuditTests(unittest.TestCase):
    def test_independent_linear_solution(self):
        x = m.linear_solve([[4.0, 1.0], [1.0, 3.0]], [1.0, 2.0])
        self.assertAlmostEqual(x[0], 1.0 / 11.0)
        self.assertAlmostEqual(x[1], 7.0 / 11.0)

    def test_source_and_frozen_receipt(self):
        rows = m.load_rows()
        report = m.run(rows)
        expected = json.loads(m.EXPECTED.read_text(encoding="utf-8"))
        self.assertTrue(m.check_receipt(report, expected))
        self.assertEqual(len(rows), 76)
        self.assertEqual({r["end"] - r["start"] for r in rows}, {1})
        self.assertEqual(len(report["predictions"]), 33)

    def test_training_has_no_future_outcome_leakage(self):
        original = m.load_rows()
        baseline = m.run(original)["predictions"]
        perturbed = copy.deepcopy(original)
        for r in perturbed:
            if r["start"] >= 2015:
                r["y"] += 1000.0
        after = m.run(perturbed)["predictions"]
        old_2015 = [p for p in baseline if p["test_start_year"] == 2015]
        new_2015 = [p for p in after if p["test_start_year"] == 2015]
        for a, b in zip(old_2015, new_2015):
            self.assertEqual(a["site_id"], b["site_id"])
            self.assertAlmostEqual(a["siteyear"], b["siteyear"], places=10)
            self.assertAlmostEqual(a["siteyear_ice"], b["siteyear_ice"], places=10)

    def test_ice_regularization_sensitivity(self):
        rows = m.load_rows()
        expected = json.loads(m.EXPECTED.read_text(encoding="utf-8"))
        for alpha, truth in expected["ice_penalty_sensitivity_mae"].items():
            result = m.run(rows, float(alpha))
            got = result["all_metrics"]["mae_siteyear_ice"]
            self.assertTrue(math.isclose(got, truth, abs_tol=1e-9))


if __name__ == "__main__":
    unittest.main()
