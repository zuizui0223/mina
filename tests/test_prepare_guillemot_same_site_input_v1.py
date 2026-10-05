import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.prepare_guillemot_same_site_input_v1 import prepare


class GuillemotAdapterTests(unittest.TestCase):
    def test_frozen_column_mapping_and_na_drop(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "raw.csv"
            pd.DataFrame([
                {
                    "Site.number": "A1", "Subcolony": "A", "Year": 2000,
                    "Subcolony.size": 10, "Wholecolony.size": 100,
                    "Occupancy.status": 1, "Quality": 0.8,
                    "Trend.phase": "Positive",
                },
                {
                    "Site.number": "A1", "Subcolony": "A", "Year": 2001,
                    "Subcolony.size": 9, "Wholecolony.size": 99,
                    "Occupancy.status": 0, "Quality": 0.8,
                    "Trend.phase": "Negative",
                },
                {
                    "Site.number": "A2", "Subcolony": "A", "Year": 2000,
                    "Subcolony.size": 10, "Wholecolony.size": 100,
                    "Occupancy.status": None, "Quality": 0.5,
                    "Trend.phase": "Positive",
                },
            ]).to_csv(p, index=False)

            x, audit = prepare(p)
            self.assertEqual(list(x.columns), [
                "subcolony", "site_id", "year", "occupied", "subcolony_size"
            ])
            self.assertEqual(len(x), 2)
            self.assertEqual(audit["rows_dropped_required_NA"], 1)
            self.assertFalse(audit["biological_effect_opened"])

    def test_inconsistent_parent_size_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "raw.csv"
            pd.DataFrame([
                {"Site.number": "A1", "Subcolony": "A", "Year": 2000,
                 "Subcolony.size": 10, "Occupancy.status": 1},
                {"Site.number": "A2", "Subcolony": "A", "Year": 2000,
                 "Subcolony.size": 11, "Occupancy.status": 1},
            ]).to_csv(p, index=False)
            with self.assertRaises(ValueError):
                prepare(p)

    def test_duplicate_site_year_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "raw.csv"
            pd.DataFrame([
                {"Site.number": "A1", "Subcolony": "A", "Year": 2000,
                 "Subcolony.size": 10, "Occupancy.status": 1},
                {"Site.number": "A1", "Subcolony": "A", "Year": 2000,
                 "Subcolony.size": 10, "Occupancy.status": 1},
            ]).to_csv(p, index=False)
            with self.assertRaises(ValueError):
                prepare(p)


if __name__ == "__main__":
    unittest.main()
