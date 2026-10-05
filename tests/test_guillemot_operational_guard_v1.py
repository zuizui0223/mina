import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.freeze_guillemot_same_site_stageb_v1 import run as freeze_stageb
from scripts.gate_guillemot_same_site_support_v1 import run as run_stageb
from scripts.guarded_run_guillemot_same_site_recovery_v1 import run_guarded


def raw_synthetic(path: Path, aligned: bool = True) -> None:
    rows = []
    years = list(range(2000, 2020))
    for c in range(5):
        sub = f"C{c+1}"
        for j in range(4):
            site = f"{sub}-S{j+1}"
            for year in years:
                occupied = 1
                if year in (2003, 2004, 2008, 2009):
                    occupied = 0
                size = 30
                if aligned:
                    if year in (2002, 2003, 2007, 2008):
                        size = 8
                    if year in (2004, 2005, 2009, 2010):
                        size = 120
                rows.append({
                    "Site.number": site,
                    "Subcolony": sub,
                    "Year": year,
                    "Subcolony.size": size,
                    "Wholecolony.size": size * 5,
                    "Occupancy.status": occupied,
                    "Quality": 0.5,
                    "Trend.phase": "unused",
                    "Colonisation.phase": "unused",
                })
    pd.DataFrame(rows).to_csv(path, index=False)


class GuillemotOperationalGuardTests(unittest.TestCase):
    def test_stageb_is_state_only_and_supports_synthetic_roster(self):
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / "raw.csv"
            raw_synthetic(raw, aligned=True)
            result = run_stageb(raw)
            self.assertEqual(result["status"], "STAGE_B_SUPPORT_PASSED")
            self.assertTrue(result["support"]["passed"])
            self.assertEqual(result["support"]["eligible_completed_spells"], 40)
            self.assertEqual(result["support"]["distinct_sites_with_spells"], 20)
            self.assertEqual(result["source"]["magnitude_fields_read"], [])
            self.assertFalse(result["magnitude_boundary"]["Subcolony.size_read"])
            for spell in result["completed_spells"]:
                self.assertNotIn("subcolony_size", spell)
                self.assertNotIn("H", spell)

    def test_stageb_roster_does_not_depend_on_population_magnitude(self):
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a.csv"
            b = Path(td) / "b.csv"
            raw_synthetic(a, aligned=True)
            df = pd.read_csv(a)
            df["Subcolony.size"] = 9999
            df.to_csv(b, index=False)
            ra = run_stageb(a)
            rb = run_stageb(b)
            self.assertEqual(ra["completed_spells"], rb["completed_spells"])
            self.assertEqual(ra["support"], rb["support"])
            self.assertNotEqual(
                ra["source"]["raw_file_sha256"],
                rb["source"]["raw_file_sha256"],
            )

    def test_freeze_then_guarded_stagec_and_raw_mutation_block(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = root / "raw.csv"
            raw_synthetic(raw, aligned=True)

            stageb = run_stageb(raw)
            stageb_json = root / "stageb.json"
            stageb_json.write_text(
                json.dumps(stageb, indent=2, sort_keys=True),
                encoding="utf-8",
            )

            prereg = {
                "receipt_id": (
                    "mina-guillemot-same-site-recovery-preregistration-test"
                ),
                "frozen_design_head_sha": "synthetic",
                "canonical_files": [],
            }
            prereg_json = root / "prereg.json"
            prereg_json.write_text(
                json.dumps(prereg), encoding="utf-8"
            )

            freeze = freeze_stageb(
                raw, stageb_json, prereg_json, root
            )
            freeze_json = root / "freeze.json"
            freeze_json.write_text(
                json.dumps(freeze, indent=2, sort_keys=True),
                encoding="utf-8",
            )

            result = run_guarded(
                raw, stageb_json, freeze_json, B=999, seed=20261005
            )
            self.assertTrue(
                result["primary"]["decision"][
                    "same_site_recovery_asymmetry_supported"
                ]
            )
            self.assertEqual(
                result["operational_provenance"]["raw_extract_sha256"],
                freeze["input_hashes"]["raw_extract"]["sha256"],
            )

            # Any post-freeze raw mutation must make Stage C refuse to run.
            df = pd.read_csv(raw)
            df.loc[0, "Subcolony.size"] = 999
            df.to_csv(raw, index=False)
            with self.assertRaises(ValueError):
                run_guarded(
                    raw, stageb_json, freeze_json, B=99, seed=20261005
                )

    def test_stageb_tampering_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = root / "raw.csv"
            raw_synthetic(raw, aligned=True)
            stageb = run_stageb(raw)
            stageb_json = root / "stageb.json"
            stageb_json.write_text(json.dumps(stageb), encoding="utf-8")
            prereg_json = root / "prereg.json"
            prereg_json.write_text(json.dumps({
                "receipt_id": (
                    "mina-guillemot-same-site-recovery-preregistration-test"
                ),
                "frozen_design_head_sha": "synthetic",
                "canonical_files": [],
            }), encoding="utf-8")
            freeze = freeze_stageb(
                raw, stageb_json, prereg_json, root
            )
            freeze_json = root / "freeze.json"
            freeze_json.write_text(json.dumps(freeze), encoding="utf-8")

            stageb["completed_spells"][0]["vacancy_pre_year"] += 1
            stageb_json.write_text(json.dumps(stageb), encoding="utf-8")
            with self.assertRaises(ValueError):
                run_guarded(
                    raw, stageb_json, freeze_json, B=99, seed=20261005
                )


if __name__ == "__main__":
    unittest.main()
