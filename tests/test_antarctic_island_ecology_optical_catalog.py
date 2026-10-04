import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
import tempfile

import pandas as pd

from scripts.audit_antarctic_island_ecology_optical_catalog import (
    epoch_window,
    summarize_items,
    build_units,
)


class FakeItem:
    def __init__(self, dt, cloud):
        self.datetime = datetime.fromisoformat(dt).replace(tzinfo=timezone.utc)
        self.properties = {"eo:cloud_cover": cloud}


class OpticalCatalogAuditTests(unittest.TestCase):
    def test_epoch_window_clips_to_archive_bounds(self):
        self.assertEqual(epoch_window(1980), (1984, 1992))
        self.assertEqual(epoch_window(1986), (1984, 1990))
        self.assertEqual(epoch_window(2024), (2017, 2025))

    def test_scene_summary_uses_austral_months_and_cloud_gate(self):
        items = [
            FakeItem("1988-01-15T00:00:00", 20),
            FakeItem("1989-02-15T00:00:00", 40),
            FakeItem("1990-12-15T00:00:00", 70),
            FakeItem("1990-07-15T00:00:00", 10),
            FakeItem("1991-01-15T00:00:00", 90),
        ]
        s = summarize_items(items)
        self.assertEqual(s["n_scenes_cloud_le80"], 3)
        self.assertEqual(s["n_scenes_cloud_le50"], 2)
        self.assertEqual(s["n_distinct_years"], 3)
        self.assertTrue(s["catalog_support"])

    def test_forbidden_demographic_field_fails_closed(self):
        forcing = pd.DataFrame([
            {
                "unit_id": f"ADPE|S{i:03d}",
                "site_id": f"S{i:03d}",
                "species_id": "ADPE",
                "region": "R",
                "first_observed_season": 1985,
                "last_observed_season": 2000,
                "n_observed_seasons": 5,
                "count": 1,
            }
            for i in range(107)
        ])
        options = pd.DataFrame([
            {"site_id": f"S{i:03d}", "latitude": -62.0, "longitude": -58.0}
            for i in range(107)
        ])
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "f.csv"
            o = Path(td) / "o.csv"
            forcing.to_csv(f, index=False)
            options.to_csv(o, index=False)
            with self.assertRaisesRegex(ValueError, "forbidden demographic fields"):
                build_units(f, o)


if __name__ == "__main__":
    unittest.main()
