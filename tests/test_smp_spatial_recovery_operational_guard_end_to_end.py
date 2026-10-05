import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.finalize_smp_spatial_recovery_structure_v1 import run as finalize_identity
from scripts.freeze_smp_spatial_recovery_stageb_v1 import run as freeze_stageb
from scripts.gate_smp_spatial_recovery_hysteresis_structure_v1 import run as run_structure
from scripts.gate_smp_spatial_recovery_hysteresis_support_v1 import run as run_state
from scripts.guarded_run_smp_spatial_recovery_stagec_v1 import run_guarded
from scripts.record_smp_raw_custody_v1 import run as record_custody


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "results" / "SMP_SPATIAL_RECOVERY_HYSTERESIS_PREREGISTRATION_RECEIPT_V3.json"


class SmpOperationalGuardEndToEndTests(unittest.TestCase):
    def test_freeze_receipt_and_guarded_stagec_use_exact_same_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            years = list(range(2000, 2012))
            rows = []

            # Frozen minimum synthetic scale:
            # 5 species x 2 physical MasterSites x 3 SiteIDs = 30 spells.
            # All three SiteIDs are vacant in 2002 and return in 2003,
            # with a strong event-aligned increase in surrounding abundance.
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

            # Step 0: custody without content parsing.
            custody = record_custody(
                raw,
                received_at="2026-10-05T20:30:00+09:00",
                provider_filename="synthetic_provider_export.csv",
                source_channel="synthetic test fixture",
            )
            self.assertFalse(custody["content_parsed"])
            custody_json = root / "custody.json"
            custody_json.write_text(json.dumps(custody), encoding="utf-8")

            # A0
            candidate = run_structure(raw)
            self.assertTrue(candidate["decision"]["structural_gate_passed"])
            candidate_json = root / "candidate.json"
            candidate_json.write_text(json.dumps(candidate), encoding="utf-8")

            # A1
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
                        "notes": "synthetic provider-confirmed physical identity",
                    })
            identity_csv = root / "identity.csv"
            pd.DataFrame(identity_rows).to_csv(identity_csv, index=False)

            resolved = finalize_identity(candidate_json, identity_csv)
            self.assertTrue(resolved["decision"]["structural_gate_passed"])
            resolved_json = root / "resolved.json"
            resolved_json.write_text(json.dumps(resolved), encoding="utf-8")

            # A2
            zero = {
                "row_with_direct_count_zero_is_surveyed_nil": True,
                "absent_site_year_row_is_not_zero": True,
                "estimated_or_imputed_zero_excluded_from_primary": True,
                "confirmation_source": "synthetic provider confirmation",
                "compatible_start_year": 2000,
                "compatible_end_year": 2011,
                "compatible_record_family_or_era": "synthetic Whole Colony Counts",
            }
            zero_json = root / "zero.json"
            zero_json.write_text(json.dumps(zero), encoding="utf-8")

            # B
            state = run_state(raw, resolved_json, zero_json)
            self.assertTrue(state["decision"]["hysteresis_magnitude_execution_authorized"])
            stageb_json = root / "stageb.json"
            stageb_json.write_text(json.dumps(state), encoding="utf-8")

            # Immutable pre-magnitude freeze.
            freeze = freeze_stageb(
                raw,
                custody_json,
                candidate_json,
                identity_csv,
                resolved_json,
                zero_json,
                stageb_json,
                PREREG,
                ROOT,
            )
            self.assertTrue(freeze["decision"]["stage_C_authorized"])
            self.assertTrue(freeze["gate_summary"]["raw_custody_verified"])
            self.assertEqual(
                freeze["custody"]["sha256"],
                custody["sha256"],
            )
            freeze_json = root / "freeze.json"
            freeze_json.write_text(json.dumps(freeze), encoding="utf-8")

            # Guarded C.
            result, spells = run_guarded(
                raw,
                resolved_json,
                stageb_json,
                freeze_json,
            )
            self.assertEqual(len(spells), 30)
            self.assertTrue(result["decision"]["spatial_recovery_hysteresis_supported"])
            self.assertEqual(
                result["operational_provenance"]["raw_extract_sha256"],
                freeze["raw_extract_sha256"],
            )

            # Custody mismatch must block the freeze step itself.
            bad_custody = dict(custody)
            bad_custody["byte_size"] = int(custody["byte_size"]) + 1
            bad_custody_json = root / "bad_custody.json"
            bad_custody_json.write_text(json.dumps(bad_custody), encoding="utf-8")
            with self.assertRaises(ValueError):
                freeze_stageb(
                    raw,
                    bad_custody_json,
                    candidate_json,
                    identity_csv,
                    resolved_json,
                    zero_json,
                    stageb_json,
                    PREREG,
                    ROOT,
                )

            # Mutation after freeze must block Stage C.
            stageb_json.write_text(
                json.dumps({**state, "tampered": True}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                run_guarded(raw, resolved_json, stageb_json, freeze_json)


if __name__ == "__main__":
    unittest.main()
