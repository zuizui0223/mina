import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.audit_dynamic_habitat_imagery_support import summarize_items


class FakeItem:
    def __init__(self, dt, cloud=None):
        self.datetime = dt
        self.properties = {}
        if cloud is not None:
            self.properties["eo:cloud_cover"] = cloud


class DynamicHabitatSupportTests(unittest.TestCase):
    def test_summer_support_requires_dates_and_years(self):
        items = [
            FakeItem(datetime(1984, 11, 1, tzinfo=timezone.utc), 10),
            FakeItem(datetime(1985, 1, 2, tzinfo=timezone.utc), 30),
            FakeItem(datetime(1985, 2, 3, tzinfo=timezone.utc), 50),
            FakeItem(datetime(1985, 7, 1, tzinfo=timezone.utc), 5),
        ]
        out = summarize_items(items, max_items=5000)
        self.assertEqual(out["n_summer_dates"], 3)
        self.assertEqual(out["n_summer_years"], 2)
        self.assertTrue(out["catalog_support"])
        self.assertEqual(out["n_summer_dates_cloud_lt20"], 1)
        self.assertEqual(out["n_summer_dates_cloud_lt40"], 2)
        self.assertEqual(out["n_summer_dates_cloud_lt60"], 3)

    def test_single_year_does_not_pass(self):
        items = [
            FakeItem(datetime(2019, 11, 1, tzinfo=timezone.utc)),
            FakeItem(datetime(2019, 12, 1, tzinfo=timezone.utc)),
            FakeItem(datetime(2019, 12, 15, tzinfo=timezone.utc)),
        ]
        out = summarize_items(items, max_items=5000)
        self.assertEqual(out["n_summer_dates"], 3)
        self.assertEqual(out["n_summer_years"], 1)
        self.assertFalse(out["catalog_support"])

    def test_max_item_ceiling_fails_closed(self):
        items = [
            FakeItem(datetime(2020, 11, 1, tzinfo=timezone.utc)),
            FakeItem(datetime(2021, 1, 1, tzinfo=timezone.utc)),
            FakeItem(datetime(2021, 2, 1, tzinfo=timezone.utc)),
        ]
        out = summarize_items(items, max_items=3)
        self.assertTrue(out["query_hit_max_items"])
        self.assertFalse(out["catalog_support"])

    def test_contract_is_outcome_blind(self):
        path = Path(__file__).resolve().parents[1] / "contracts" / "DYNAMIC_HABITAT_IMAGERY_SUPPORT_AUDIT_V1.json"
        c = json.loads(path.read_text(encoding="utf-8"))
        prohibited = " ".join(c["prohibited_fields"]).lower()
        self.assertIn("count magnitude", prohibited)
        self.assertIn("population trend", prohibited)
        self.assertIn("effective breeding-component", prohibited)
        self.assertEqual(c["stac"]["primary_collection"], "landsat-c2-l2")
        self.assertEqual(c["stac"]["validation_collection"], "sentinel-2-l2a")


if __name__ == "__main__":
    unittest.main()
