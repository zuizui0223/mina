import unittest

import numpy as np
import pandas as pd

from scripts.run_smp_trend_symmetry_effect_v1 import (
    effective_number,
    macro_summary,
    panel_effect,
)


class SmpTrendSymmetryEffectTests(unittest.TestCase):
    def test_effective_number(self):
        self.assertAlmostEqual(effective_number(np.array([10, 10, 10])), 3.0)
        self.assertAlmostEqual(effective_number(np.array([30, 0, 0])), 1.0)

    def test_panel_effect_detects_concentration_during_growth(self):
        years = list(range(2000, 2012))
        rows = []
        roster = ["s1", "s2", "s3"]
        for t, year in enumerate(years):
            total = 300 + 15 * t
            # Increasingly concentrated composition while total abundance grows.
            p1 = 1/3 + 0.035 * t
            p2 = (1 - p1) / 2
            counts = np.floor(np.array([p1, p2, p2]) * total).astype(int)
            counts[0] += total - int(counts.sum())
            for sid, n in zip(roster, counts):
                rows.append({
                    "_species": "species1",
                    "_master_norm": "master 1",
                    "_unit": "AON",
                    "_site_id": sid,
                    "year": year,
                    "_count": int(n),
                })
        x = pd.DataFrame(rows)
        support = {
            "species": "species1",
            "master_site": "Master 1",
            "unit": "AON",
            "retained_site_ids": roster,
            "complete_years": years,
        }
        balance = {
            "panel_id": "species1|Master 1|AON",
            "n_positive_total_years": len(years),
            "positive_total_span_years": 12,
            "composition_eligible": True,
            "b_log1pN_per_year": 0.01,
            "trend_label": "increasing",
        }
        out = panel_effect(x, support, balance, B=1000, seed=123)
        self.assertLess(out["gamma_obs"], 0)
        self.assertLess(out["delta_gamma"], 0)

    def test_macro_directional_persistence_species_balanced(self):
        rows = []
        for s in range(6):
            species = f"sp{s}"
            # Each species has one increasing and one declining panel.
            rows.append({
                "species": species,
                "master_site": f"I{s}",
                "unit": "AON",
                "delta_gamma": -0.04 - 0.001*s,
                "b_log1pN_per_year": 0.02 + 0.001*s,
                "trend_label": "increasing",
            })
            rows.append({
                "species": species,
                "master_site": f"D{s}",
                "unit": "AON",
                "delta_gamma": -0.06 - 0.001*s,
                "b_log1pN_per_year": -0.02 - 0.001*s,
                "trend_label": "declining",
            })
        out = macro_summary(pd.DataFrame(rows), B=2000, seed=456)
        self.assertEqual(
            out["trend_class_species_balanced"]["pattern"],
            "directional_persistence",
        )
        self.assertTrue(out["alpha_species_balanced"]["overall_concentration_supported"])
        self.assertGreaterEqual(out["beta_within_species"]["identified_species_count"], 4)


if __name__ == "__main__":
    unittest.main()
