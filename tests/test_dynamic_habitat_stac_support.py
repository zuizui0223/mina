import unittest

from scripts.audit_dynamic_habitat_stac_support import summarize_items


class StacSummaryTests(unittest.TestCase):
    def test_summer_and_cloud_thresholds(self):
        items = [
            {"properties": {"datetime": "1985-12-10T00:00:00Z", "eo:cloud_cover": 10, "platform": "landsat-5"}},
            {"properties": {"datetime": "1986-01-20T00:00:00Z", "eo:cloud_cover": 45, "platform": "landsat-5"}},
            {"properties": {"datetime": "1986-02-20T00:00:00Z", "eo:cloud_cover": 75, "platform": "landsat-5"}},
            {"properties": {"datetime": "1987-07-20T00:00:00Z", "eo:cloud_cover": 0, "platform": "landsat-5"}},
            {"properties": {"datetime": "1988-01-20T00:00:00Z", "eo:cloud_cover": None, "platform": "landsat-5"}},
        ]
        s = summarize_items(items, {11, 12, 1, 2, 3})
        self.assertEqual(s["summer_scenes_total"], 4)
        self.assertEqual(s["scenes_cloud_le_80"], 3)
        self.assertEqual(s["years_cloud_le_80"], 2)
        self.assertEqual(s["scenes_cloud_le_50"], 2)
        self.assertEqual(s["years_cloud_le_50"], 2)
        self.assertEqual(s["scenes_cloud_le_20"], 1)
        self.assertEqual(s["years_cloud_le_20"], 1)

    def test_non_summer_items_are_excluded(self):
        items = [
            {"properties": {"datetime": "2020-06-01T00:00:00Z", "eo:cloud_cover": 0}},
            {"properties": {"datetime": "2020-12-01T00:00:00Z", "eo:cloud_cover": 30}},
        ]
        s = summarize_items(items, {11, 12, 1, 2, 3})
        self.assertEqual(s["summer_scenes_total"], 1)
        self.assertEqual(s["scenes_cloud_le_50"], 1)


if __name__ == "__main__":
    unittest.main()
