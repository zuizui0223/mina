import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.gate_smp_spatial_recovery_hysteresis_structure_v1 import (
    MIN_MASTERS,
    MIN_PANELS,
    MIN_SPECIES,
    run as run_candidate_structure,
)
from scripts.finalize_smp_spatial_recovery_structure_v1 import (
    run as run_identity_resolution,
)
from scripts.gate_smp_spatial_recovery_hysteresis_support_v1 import (
    run as run_state_support,
)


class HysteresisStructureContractTests(unittest.TestCase):
    def test_program_minima_match_downstream_possibility(self):
        self.assertEqual(MIN_PANELS, 10)
        self.assertEqual(MIN_MASTERS, 10)
        self.assertEqual(MIN_SPECIES, 5)

    def test_stage_a_to_b_freezes_cycles_without_exposing_magnitudes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rows = []
            years = list(range(2000, 2012))

            # 5 species x 2 MasterSites = 10 candidate panels.
            # Each panel has 3 stable SiteIDs. Every SiteID has one completed
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

            # A0: count-blind candidate roster.
            candidate = run_candidate_structure(data)
            self.assertTrue(candidate["decision"]["structural_gate_passed"])
            self.assertEqual(candidate["eligible_panel_count"], 10)
            self.assertEqual(candidate["eligible_species_count"], 5)

            candidate_path = root / "candidate.json"
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

            # A1: provider/site-history identity resolution.
            identity_rows = []
            for panel in candidate["eligible_panels"]:
                for site in panel["retained_site_ids"]:
                    identity_rows.append({
                        "species": panel["species"],
                        "MasterSite": panel["master_site"],
                        "SiteID": site,
                        "stable_identity": True,
                        "mutually_exclusive_child": True,
                        "overlaps_parent_or_sibling": False,
                        "boundary_change_during_panel": False,
                        "retired_or_replaced": False,
                        "notes": "synthetic stable child",
                    })
            identity = root / "identity.csv"
            pd.DataFrame(identity_rows).to_csv(identity, index=False)

            resolved = run_identity_resolution(candidate_path, identity)
            self.assertTrue(resolved["decision"]["structural_gate_passed"])
            self.assertEqual(resolved["analysis_id"], "mina-smp-spatial-recovery-structure-v1")
            self.assertEqual(resolved["eligible_panel_count"], 10)
            self.assertEqual(resolved["eligible_species_count"], 5)

            resolved_path = root / "resolved.json"
            resolved_path.write_text(json.dumps(resolved), encoding="utf-8")

            # A2: explicit provider confirmation of zero semantics.
            zero = root / "zero.json"
            zero.write_text(json.dumps({
                "row_with_direct_count_zero_is_surveyed_nil": True,
                "absent_site_year_row_is_not_zero": True,
                "estimated_or_imputed_zero_excluded_from_primary": True,
                "confirmation_source": "synthetic provider confirmation",
            }), encoding="utf-8")

            # B: state-only completed spells and frozen phase blocks.
            state = run_state_support(data, resolved_path, zero)
            self.assertTrue(state["decision"]["hysteresis_magnitude_execution_authorized"])
            self.assertEqual(state["support"]["phase_eligible_completed_spells"], 30)
            self.assertEqual(state["support"]["distinct_siteids_with_spells"], 30)
            self.assertEqual(state["support"]["mastersites_with_spells"], 10)
            self.assertEqual(state["support"]["species_with_spells"], 5)

            # Stage B outputs state timing/support only, not magnitudes or H.
            blob = json.dumps(state).lower()
            self.assertNotIn('"h":', blob)
            self.assertNotIn("abandonment abundance", blob)
            self.assertNotIn("recolonization abundance", blob)
            for spell in state["completed_spells"]:
                self.assertGreaterEqual(spell["phase_block_length"], 6)
                self.assertNotIn("count", spell)


if __name__ == "__main__":
    unittest.main()
