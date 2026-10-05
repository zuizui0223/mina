import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.gate_smp_trend_symmetry_support_v1 import apply_composite_gate
from scripts.gate_smp_trend_balance_v1 import run as run_balance


class SmpTrendSymmetryGateTests(unittest.TestCase):
    def test_composite_gate_uses_stricter_span_and_program_thresholds(self):
        panels = []
        for i in range(20):
            sp = f"species{i % 8}"
            panels.append({
                "species": sp,
                "master_site": f"M{i}",
                "unit": "AON",
                "countries": [f"R{i % 3}"],
                "retained_site_ids": ["s1","s2","s3"],
                "retained_site_names": {},
                "stable_method_by_site": {},
                "n_sites": 3,
                "n_complete_years": 10,
                "first_complete_year": 2000,
                "last_complete_year": 2011,
                "calendar_span_years": 12,
                "complete_years": list(range(2000,2010)),
            })
        # ensure >=4 species have >=2 panels
        legacy = {
            "analysis_id": "legacy",
            "source": {"count_field_present_but_dropped_before_analysis": True},
            "eligible_panel_count": 20,
            "eligible_panels": panels,
        }
        out = apply_composite_gate(legacy)
        self.assertTrue(out["decision"]["structural_gate_passed"])
        self.assertEqual(out["eligible_panel_count"], 20)
        self.assertNotIn("count magnitudes", json.dumps(out).lower())

    def test_balance_gate_emits_only_panel_trends_not_component_composition(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rows = []
            panels = []
            # 12 panels, 6 increasing + 6 declining, 6 species and 12 masters.
            for i in range(12):
                species = f"species{i % 6}"
                master = f"Master {i}"
                site_ids = [f"{master}-s{j}" for j in range(3)]
                years = list(range(2000, 2012))
                panels.append({
                    "species": species,
                    "master_site": master,
                    "unit": "AON",
                    "countries": ["R1"],
                    "retained_site_ids": site_ids,
                    "retained_site_names": {},
                    "stable_method_by_site": {s:"Ground" for s in site_ids},
                    "n_sites": 3,
                    "n_complete_years": len(years),
                    "first_complete_year": min(years),
                    "last_complete_year": max(years),
                    "calendar_span_years": 12,
                    "complete_years": years,
                })
                sign = 1 if i < 6 else -1
                for y in years:
                    base = 100 + sign * 4 * (y - 2000)
                    for j, sid in enumerate(site_ids):
                        rows.append({
                            "Species": species,
                            "Country": "R1",
                            "SiteID": sid,
                            "Site": sid,
                            "MasterSite": master,
                            "Plot": "(Whole Colony)",
                            "Year": y,
                            "Method": "Ground",
                            "Unit": "AON",
                            "Count": max(1, base + j),
                            "Accuracy": "C",
                            "Estimate": "",
                            "Comments": "",
                        })
            data = root / "smp.csv"
            pd.DataFrame(rows).to_csv(data, index=False)
            support = root / "support.json"
            support.write_text(json.dumps({
                "analysis_id": "mina-smp-trend-symmetry-support-v1",
                "eligible_panels": panels,
                "decision": {"structural_gate_passed": True}
            }))
            out = run_balance(data, support)
            self.assertEqual(out["trend_support"]["increasing_panels"], 6)
            self.assertEqual(out["trend_support"]["declining_panels"], 6)
            blob = json.dumps(out).lower()
            self.assertNotIn('"e"', blob)
            self.assertNotIn("delta_gamma", blob)
            self.assertNotIn("annual panel total abundance values": [", blob)


if __name__ == "__main__":
    unittest.main()
