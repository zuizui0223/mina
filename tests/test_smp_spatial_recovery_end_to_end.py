import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.finalize_smp_spatial_recovery_structure_v1 import run as finalize_identity
from scripts.gate_smp_spatial_recovery_hysteresis_structure_v1 import run as run_structure
from scripts.gate_smp_spatial_recovery_hysteresis_support_v1 import run as run_state
from scripts.run_smp_spatial_recovery_hysteresis_v1 import run as run_effect


class SpatialRecoveryEndToEndTests(unittest.TestCase):
    def test_true_same_site_recovery_barrier_passes_full_frozen_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            years = list(range(2000, 2012))
            rows = []

            # 5 species x 2 independent physical MasterSites = 10 geographic
            # replicates. Each MasterSite has 3 stable SiteIDs. All three sites
            # are abandoned in 2002 and reoccupied in 2003 at much higher
            # counts than before abandonment. Other years are stable.
            for s in range(5):
                species = f"species{s}"
                for m in range(2):
                    master = f"Master-{s}-{m}"
                    for j in range(3):
                        site = f"{master}-S{j}"
                        for year in years:
                            if year == 2002:
                                count = 0
                            elif year == 2001:
                                count = 10 + j
                            elif year == 2003:
                                count = 100 + 5 * j
                            else:
                                count = 25 + j
                            rows.append({
                                "Species": species,
                                "Country": f"Region{s % 3}",
                                "SiteID": site,
                                "Site": site,
                                "MasterSite": master,
                                "Plot": "(Whole Colony)",
                                "Year": year,
                                "Method": "Ground",
                                "Unit": "AON",
                                "Count": count,
                                "Accuracy": "C",
                                "Estimate": "",
                                "Comments": "",
                            })

            raw = root / "smp.csv"
            pd.DataFrame(rows).to_csv(raw, index=False)

            # A0: count-blind candidate structure.
            candidate = run_structure(raw)
            self.assertTrue(candidate["decision"]["structural_gate_passed"])
            self.assertEqual(candidate["eligible_panel_count"], 10)

            candidate_json = root / "candidate.json"
            candidate_json.write_text(json.dumps(candidate), encoding="utf-8")

            # A1: provider-resolved physical identity.
            identity_rows = []
            for panel in candidate["eligible_panels"]:
                for site in panel["retained_site_ids"]:
                    identity_rows.append({
                        "species": panel["species"],
                        "MasterSite": panel["master_site"],
                        "SiteID": site,
                        "master_site_key": panel["master_site"],
                        "master_site_identity_confirmed": True,
                        "stable_identity": True,
                        "mutually_exclusive_child": True,
                        "overlaps_parent_or_sibling": False,
                        "boundary_change_during_panel": False,
                        "retired_or_replaced": False,
                        "canonical_unit": "",
                        "notes": "synthetic stable physical site",
                    })
            identity_csv = root / "identity.csv"
            pd.DataFrame(identity_rows).to_csv(identity_csv, index=False)

            resolved = finalize_identity(candidate_json, identity_csv)
            self.assertTrue(resolved["decision"]["structural_gate_passed"])
            self.assertEqual(resolved["distinct_master_site_count"], 10)

            resolved_json = root / "resolved.json"
            resolved_json.write_text(json.dumps(resolved), encoding="utf-8")

            # A2: provider-confirmed zero semantics.
            zero_json = root / "zero.json"
            zero_json.write_text(json.dumps({
                "row_with_direct_count_zero_is_surveyed_nil": True,
                "absent_site_year_row_is_not_zero": True,
                "estimated_or_imputed_zero_excluded_from_primary": True,
                "confirmation_source": "synthetic provider confirmation",
                "compatible_start_year": 2000,
                "compatible_end_year": 2011,
                "compatible_record_family_or_era": "synthetic direct Whole Colony Counts",
            }), encoding="utf-8")

            # B: freeze occupancy spells and common non-circular offsets.
            state = run_state(raw, resolved_json, zero_json)
            self.assertTrue(state["decision"]["hysteresis_magnitude_execution_authorized"])
            self.assertEqual(
                state["support"]["linear_shift_eligible_completed_spells"],
                30,
            )
            self.assertEqual(state["support"]["mastersites_with_spells"], 10)
            self.assertEqual(state["support"]["species_with_spells"], 5)
            for spell in state["completed_spells"]:
                self.assertGreaterEqual(spell["n_common_offsets"], 3)
                self.assertIn(0, spell["common_offset_values"])
                self.assertNotIn("H", spell)

            state_json = root / "state.json"
            state_json.write_text(json.dumps(state), encoding="utf-8")

            # C: one frozen magnitude execution.
            result, spell_frame = run_effect(raw, resolved_json, state_json)
            self.assertEqual(len(spell_frame), 30)
            self.assertTrue(result["decision"]["spatial_recovery_hysteresis_supported"])

            macro = result["macro"]
            self.assertGreater(macro["primary_T_species_balanced_mean_H"], 0)
            self.assertLessEqual(
                macro["species_sign_flip"]["one_sided_p"],
                0.05,
            )
            self.assertLessEqual(
                macro["physical_master_site_sign_flip"]["one_sided_p"],
                0.05,
            )
            self.assertGreater(
                macro["structured_linear_shift_null"]["delta_linear_observed_minus_median"],
                0,
            )
            self.assertLessEqual(
                macro["structured_linear_shift_null"]["upper_tail_p"],
                0.05,
            )


if __name__ == "__main__":
    unittest.main()
