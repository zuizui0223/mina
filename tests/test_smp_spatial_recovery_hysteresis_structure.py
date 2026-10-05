import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.finalize_smp_spatial_recovery_structure_v1 import run as finalize_identity
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
    def _synthetic_extract(self, root: Path) -> Path:
        rows = []
        years = list(range(2000, 2012))

        # 5 species x 2 MasterSites = 10 panels.
        # Every panel has 3 SiteIDs. Each SiteID has one completed
        # positive -> explicit zero -> positive spell.
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
        return data

    def _identity_csv(self, root: Path, structural: dict) -> Path:
        rows = []
        for panel in structural["eligible_panels"]:
            for site in panel["retained_site_ids"]:
                rows.append({
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
                    "notes": "synthetic stable SiteID",
                })
        p = root / "identity.csv"
        pd.DataFrame(rows).to_csv(p, index=False)
        return p

    def _zero_json(self, root: Path) -> Path:
        p = root / "zero.json"
        p.write_text(json.dumps({
            "row_with_direct_count_zero_is_surveyed_nil": True,
            "absent_site_year_row_is_not_zero": True,
            "estimated_or_imputed_zero_excluded_from_primary": True,
            "confirmation_source": "synthetic provider confirmation",
            "compatible_start_year": 2000,
            "compatible_end_year": 2011,
            "compatible_record_family_or_era": "synthetic direct Whole Colony Counts",
        }), encoding="utf-8")
        return p

    def test_program_minima_match_hysteresis_design(self):
        self.assertEqual(MIN_PANELS, 10)
        self.assertEqual(MIN_MASTERS, 10)
        self.assertEqual(MIN_SPECIES, 5)

    def test_full_blind_pipeline_freezes_cycles_without_magnitudes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = self._synthetic_extract(root)

            raw = run_structure(data)
            self.assertTrue(raw["decision"]["structural_gate_passed"])
            self.assertEqual(raw["eligible_panel_count"], 10)
            self.assertEqual(raw["eligible_species_count"], 5)

            raw_path = root / "raw_structure.json"
            raw_path.write_text(json.dumps(raw), encoding="utf-8")

            identity = finalize_identity(
                raw_path,
                self._identity_csv(root, raw),
            )
            self.assertEqual(
                identity["analysis_id"],
                "mina-smp-spatial-recovery-structure-v1",
            )
            self.assertEqual(
                identity["status"],
                "identity_resolved_count_blind_structure",
            )
            for panel in identity["eligible_panels"]:
                self.assertTrue(panel["master_site_key"])
            self.assertTrue(identity["decision"]["structural_gate_passed"])
            self.assertEqual(identity["eligible_panel_count"], 10)
            self.assertEqual(identity["eligible_species_count"], 5)

            identity_path = root / "identity_structure.json"
            identity_path.write_text(json.dumps(identity), encoding="utf-8")

            state = run_state_support(
                data,
                identity_path,
                self._zero_json(root),
            )

            self.assertTrue(
                state["decision"]["hysteresis_magnitude_execution_authorized"]
            )
            self.assertEqual(
                state["support"]["linear_shift_eligible_completed_spells"],
                30,
            )
            self.assertEqual(
                state["support"]["distinct_siteids_with_spells"],
                30,
            )
            self.assertEqual(state["support"]["mastersites_with_spells"], 10)
            self.assertEqual(state["support"]["species_with_spells"], 5)

            # Stage B emits timing/common-offset support, not count magnitudes or H.
            blob = json.dumps(state).lower()
            self.assertNotIn('"h":', blob)
            self.assertNotIn("abandon_state", blob)
            self.assertNotIn("recolonize_state", blob)
            for spell in state["completed_spells"]:
                self.assertGreaterEqual(spell["shift_block_length"], 6)
                self.assertEqual(spell["shift_block_start"], 2000)
                self.assertEqual(spell["shift_block_end"], 2011)
                self.assertGreaterEqual(spell["n_common_offsets"], 3)
                self.assertIn(0, spell["common_offset_values"])
                self.assertTrue(spell["linear_shift_null_eligible"])
                self.assertNotIn("count", spell)
                self.assertGreaterEqual(spell["n_common_offsets"], 3)
                self.assertIn(0, spell["common_offset_values"])
                self.assertNotIn("pseudo_start_years", spell)


    def test_ambiguous_master_identity_excludes_only_that_panel(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = self._synthetic_extract(root)
            raw = run_structure(data)
            raw_path = root / "raw.json"
            raw_path.write_text(json.dumps(raw), encoding="utf-8")

            identity_path = self._identity_csv(root, raw)
            ids = pd.read_csv(identity_path)

            # Make one candidate species x MasterSite map to two physical keys.
            target_species = raw["eligible_panels"][0]["species"]
            target_master = raw["eligible_panels"][0]["master_site"]
            mask = (
                ids["species"].astype(str).eq(str(target_species))
                & ids["MasterSite"].astype(str).eq(str(target_master))
            )
            idx = ids.index[mask].tolist()
            self.assertGreaterEqual(len(idx), 2)
            ids.loc[idx[0], "master_site_key"] = "physical-A"
            ids.loc[idx[1:], "master_site_key"] = "physical-B"
            ids.to_csv(identity_path, index=False)

            out = finalize_identity(raw_path, identity_path)
            self.assertEqual(out["eligible_panel_count"], 9)
            self.assertEqual(len(out["excluded_master_identity_panels"]), 1)
            self.assertEqual(
                out["excluded_master_identity_panels"][0]["master_site"],
                target_master,
            )
            # Program minimum is 10 panels, so the overall gate now fails
            # without salvaging or splitting the ambiguous candidate.
            self.assertFalse(out["decision"]["structural_gate_passed"])

    def test_stage_b_rejects_raw_structure_before_identity_finalize(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = self._synthetic_extract(root)
            raw = run_structure(data)
            raw_path = root / "raw.json"
            raw_path.write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaises(ValueError):
                run_state_support(data, raw_path, self._zero_json(root))

    def test_stage_b_rejects_unconfirmed_zero_semantics(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = self._synthetic_extract(root)
            raw = run_structure(data)
            raw_path = root / "raw.json"
            raw_path.write_text(json.dumps(raw), encoding="utf-8")
            identity = finalize_identity(
                raw_path,
                self._identity_csv(root, raw),
            )
            identity_path = root / "identity.json"
            identity_path.write_text(json.dumps(identity), encoding="utf-8")
            zero = root / "zero_bad.json"
            zero.write_text(json.dumps({
                "row_with_direct_count_zero_is_surveyed_nil": False,
                "absent_site_year_row_is_not_zero": True,
                "estimated_or_imputed_zero_excluded_from_primary": True,
                "confirmation_source": "not confirmed",
                "compatible_start_year": 2000,
                "compatible_end_year": 2011,
                "compatible_record_family_or_era": "synthetic direct Whole Colony Counts",
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                run_state_support(data, identity_path, zero)


if __name__ == "__main__":
    unittest.main()
