import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.gate_smp_spatial_recovery_hysteresis_structure_v1 import (
    MIN_MASTERS,
    MIN_PANELS,
    MIN_SPECIES,
    run as run_structure,
)
from scripts.gate_smp_spatial_recovery_hysteresis_support_v1 import (
    run as run_state_support,
)


class HysteresisStructureContractTests(unittest.TestCase):
    def test_program_minima_match_downstream_possibility(self):
        self.assertEqual(MIN_PANELS, 10)
        self.assertEqual(MIN_MASTERS, 10)
        self.assertEqual(MIN_SPECIES, 5)

    def test_structure_gate_has_no_outcome_thresholds(self):
        text = json.dumps({
            "MIN_PANELS": MIN_PANELS,
            "MIN_MASTERS": MIN_MASTERS,
            "MIN_SPECIES": MIN_SPECIES,
        }).lower()
        self.assertNotIn("hysteresis width", text)
        self.assertNotIn("delta_gamma", text)

    def test_stage_a_to_b_freezes_cycles_without_exposing_magnitudes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rows = []
            years = list(range(2000, 2012))

            # 5 species x 2 MasterSites = 10 panels.
            # Every panel has 3 SiteIDs. Each SiteID has one completed
            # positive -> zero -> positive spell and otherwise remains positive.
            for s in range(5):
                species = f"species{s}"
                for m in range(2):
                    master = f"Master-{s}-{m}"
                    for j in range(3):
                        site = f"{master}-S{j}"
                        for y in years:
                            count = 0 if y == 2001 else 100 + s * 10 + m * 3 + j
                            rows.append({
                                "Species": species,
                                "Country": f"Region{s % 3}",
                                "SiteID": site,
                                "Site": site,
                                "MasterSite": master,
                                "Plot": "(Whole Colony)",
                                "Year": y,
                                "Method": "Ground",
                                "Unit": "AON",
                                "Count": count,
                                "Accuracy": "C",
                                "Estimate": "",
                                "Comments": "",
                            })

            data = root / "smp.csv"
            pd.DataFrame(rows).to_csv(data, index=False)

            structural = run_structure(data)
            self.assertTrue(structural["decision"]["structural_gate_passed"])
            self.assertEqual(structural["eligible_panel_count"], 10)
            self.assertEqual(structural["eligible_species_count"], 5)

            support_path = root / "structure.json"
            support_path.write_text(json.dumps(structural), encoding="utf-8")
            state = run_state_support(data, support_path)

            self.assertTrue(state["decision"]["hysteresis_magnitude_execution_authorized"])
            self.assertEqual(state["support"]["null_eligible_completed_spells"], 30)
            self.assertEqual(state["support"]["distinct_siteids_with_spells"], 30)
            self.assertEqual(state["support"]["mastersites_with_spells"], 10)
            self.assertEqual(state["support"]["species_with_spells"], 5)

            # Stage B emits state timing/support, not count magnitude or H.
            blob = json.dumps(state).lower()
            self.assertNotIn('"h":', blob)
            self.assertNotIn("abandonment abundance", blob)
            self.assertNotIn("recolonization abundance", blob)
            for spell in state["completed_spells"]:
                self.assertGreaterEqual(spell["n_pseudo_placements"], 3)
                self.assertNotIn("count", spell)


if __name__ == "__main__":
    unittest.main()
