import unittest
import pandas as pd

from scripts.audit_dynamic_habitat_imagery_support import (
    collapse_sites,
    summarize_features,
)


class DynamicHabitatSupportTests(unittest.TestCase):
    def test_summarize_features_uses_austral_summer_and_distinct_years(self):
        features = []
        for date in [
            "1984-01-10T00:00:00Z",
            "1984-07-10T00:00:00Z",
            "1987-12-01T00:00:00Z",
            "1990-02-15T00:00:00Z",
            "1991-03-01T00:00:00Z",
            "1994-11-20T00:00:00Z",
        ]:
            features.append({"properties": {
                "datetime": date,
                "platform": "landsat-5",
                "eo:cloud_cover": 50,
            }})
        out = summarize_features(features)
        self.assertEqual(out["summer_distinct_dates"], 5)
        self.assertEqual(out["summer_distinct_years"], 5)
        self.assertTrue(out["support_pass"])

    def test_support_requires_three_years_even_with_many_dates(self):
        features = [
            {"properties": {"datetime": f"2019-01-{day:02d}T00:00:00Z"}}
            for day in range(1, 8)
        ]
        out = summarize_features(features)
        self.assertEqual(out["summer_distinct_dates"], 7)
        self.assertEqual(out["summer_distinct_years"], 1)
        self.assertFalse(out["support_pass"])

    def test_collapse_sites_never_needs_count_magnitude(self):
        forcing = pd.DataFrame([
            {"site_id": "A", "species_id": "ADPE", "seasons": "1980;1990;2020"},
            {"site_id": "A", "species_id": "CHPE", "seasons": "1985;2000;2022"},
            {"site_id": "B", "species_id": "GEPE", "seasons": "1981;2019"},
        ])
        sites = pd.DataFrame([
            {"site_id": "A", "site_name": "A site", "region": "R1", "ccamlr_id": "1",
             "latitude": -64.0, "longitude": -60.0},
            {"site_id": "B", "site_name": "B site", "region": "R2", "ccamlr_id": "2",
             "latitude": -72.0, "longitude": 165.0},
        ])
        out = collapse_sites(forcing, sites)
        self.assertEqual(len(out), 2)
        a = out[out.site_id == "A"].iloc[0]
        self.assertEqual(a["species_ids"], "ADPE;CHPE")
        self.assertEqual(a["first_record_season"], 1980)
        self.assertEqual(a["last_record_season"], 2022)
        self.assertNotIn("count", out.columns)


if __name__ == "__main__":
    unittest.main()
