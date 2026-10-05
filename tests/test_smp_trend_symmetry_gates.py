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
                "retained_site_ids": ["s1", "s2", "s3"],
                "retained_site_names": {},
                "stable_method_by_site": {},
                "n_sites": 3,
                "n_complete_years": 10,
                "first_complete_year": 2000,
                "last_complete_year": 2011,
                "calendar_span_years": 12,
                "complete_years": list(range(2000, 2010)),
            })

        legacy = {
            "analysis_id": "legacy",
            "source": {"count_field_present_but_dropped_before_analysis": True},
            "eligible_panel_count": 20,
            "eligible_panels": panels,
        }
        out = apply_composite_gate(legacy)
        self.assertTrue(out["decision"]["structural_gate_passed"])
        self.assertEqual(out["eligible_panel_count"], 20)

        # Stage A may expose roster/support metadata but no ecological magnitude.
        allowed_panel_keys = {
            "species", "master_site", "unit", "countries",
            "retained_site_ids", "retained_site_names",
            "stable_method_by_site", "n_sites", "n_complete_years",
            "first_complete_year", "last_complete_year",
            "calendar_span_years", "complete_years",
        }
        for panel in out["eligible_panels"]:
            self.assertTrue(set(panel).issubset(allowed_panel_keys))
            self.assertNotIn("count", panel)
            self.assertNotIn("E", panel)
            self.assertNotIn("kappa", panel)

    def test_balance_gate_emits_only_panel_trends_not_component_composition(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rows = []
            panels = []

            # 12 panels: 6 increasing + 6 declining, 6 species, 12 MasterSites.
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
                    "stable_method_by_site": {s: "Ground" for s in site_ids},
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
                "decision": {"structural_gate_passed": True},
            }))

            out = run_balance(data, support)
            self.assertEqual(out["trend_support"]["increasing_panels"], 6)
            self.assertEqual(out["trend_support"]["declining_panels"], 6)

            # Stage B output is panel trend only: no annual totals or composition.
            allowed_trend_keys = {
                "panel_id", "species", "master_site", "unit",
                "n_components", "n_complete_years", "first_year",
                "last_year", "b_log1pN_per_year", "trend_label",
            }
            for row in out["panel_trends"]:
                self.assertEqual(set(row), allowed_trend_keys)
                self.assertNotIn("annual_totals", row)
                self.assertNotIn("site_counts", row)
                self.assertNotIn("E", row)
                self.assertNotIn("kappa", row)
                self.assertNotIn("gamma_obs", row)
                self.assertNotIn("delta_gamma", row)

    def test_balance_gate_does_not_authorize_symmetry_with_one_sided_trends(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rows = []
            panels = []

            # 12 increasing panels only: should fail symmetry identifiability.
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
                    "stable_method_by_site": {s: "Ground" for s in site_ids},
                    "n_sites": 3,
                    "n_complete_years": len(years),
                    "first_complete_year": min(years),
                    "last_complete_year": max(years),
                    "calendar_span_years": 12,
                    "complete_years": years,
                })
                for y in years:
                    base = 100 + 4 * (y - 2000)
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
                            "Count": base + j,
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
                "decision": {"structural_gate_passed": True},
            }))

            out = run_balance(data, support)
            self.assertFalse(out["decision"]["symmetry_identifiability_gate_passed"])
            self.assertFalse(out["decision"]["component_concentration_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
