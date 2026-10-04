import unittest
from datetime import datetime
from pathlib import Path
import tempfile

import pandas as pd

from scripts.audit_paper2_dynamic_habitat_catalog import (
    austral_season,
    build_site_seed,
    summarize_features,
    summarize_audit,
)


class DynamicHabitatCatalogAuditTests(unittest.TestCase):
    def test_austral_season(self):
        self.assertEqual(austral_season(datetime(2020, 12, 1)), 2021)
        self.assertEqual(austral_season(datetime(2021, 1, 15)), 2021)
        self.assertEqual(austral_season(datetime(2021, 7, 1)), 2022)

    def test_summer_filter_and_gate(self):
        feats = [
            {"id": "a", "properties": {"datetime": "1985-11-01T00:00:00Z", "eo:cloud_cover": 20}},
            {"id": "b", "properties": {"datetime": "1986-01-10T00:00:00Z", "eo:cloud_cover": 30}},
            {"id": "c", "properties": {"datetime": "1987-02-12T00:00:00Z", "eo:cloud_cover": 10}},
            {"id": "winter", "properties": {"datetime": "1987-06-12T00:00:00Z", "eo:cloud_cover": 0}},
        ]
        s = summarize_features(feats)
        self.assertEqual(s["n_distinct_dates"], 3)
        self.assertGreaterEqual(s["n_austral_seasons"], 2)
        self.assertTrue(s["passes_catalog_gate"])

    def test_build_seed_uses_support_only_fields(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            forcing = pd.DataFrame([
                {"site_id":"A","species_id":"ADPE","first_observed_season":1981,"last_observed_season":2020},
                {"site_id":"A","species_id":"GEPE","first_observed_season":1982,"last_observed_season":2021},
                {"site_id":"B","species_id":"CHPE","first_observed_season":1980,"last_observed_season":2019},
            ])
            habitat = pd.DataFrame([
                {"site_id":"A","site_name":"A site","region":"R1","ccamlr_id":"1","latitude":-66.0,"longitude":10.0,"mapped_ice_free_area_ha_2000m":100},
                {"site_id":"B","site_name":"B site","region":"R2","ccamlr_id":"2","latitude":-62.0,"longitude":20.0,"mapped_ice_free_area_ha_2000m":200},
            ])
            f = td/"f.csv"; h = td/"h.csv"
            forcing.to_csv(f,index=False); habitat.to_csv(h,index=False)
            out = build_site_seed(f,h,expected_units=3,expected_sites=2)
            self.assertEqual(len(out),2)
            self.assertEqual(out.loc[out.site_id=="A","species_ids"].iloc[0],"ADPE;GEPE")
            self.assertTrue(bool(out.loc[out.site_id=="A","high_latitude_gt65"].iloc[0]))

    def test_feasibility_rule_is_frozen(self):
        rows = []
        for i in range(30):
            rows.append({
                "site_id":f"S{i:02d}",
                "region":f"R{i%3}",
                "species_ids":"ADPE;CHPE;GEPE",
                "high_latitude_gt65": True,
                "early_landsat_passes_catalog_gate": True,
                "late_landsat_passes_catalog_gate": True,
                "sentinel2_validation_passes_catalog_gate": i < 20,
                "primary_dynamic_habitat_eligible": True,
                "sentinel_validation_eligible": i < 20,
            })
        # summarize_audit expects an 88-site frame only for provenance counts, not gate arithmetic.
        while len(rows) < 88:
            i=len(rows)
            rows.append({
                "site_id":f"S{i:02d}","region":"RX","species_ids":"ADPE","high_latitude_gt65":True,
                "early_landsat_passes_catalog_gate":False,
                "late_landsat_passes_catalog_gate":False,
                "sentinel2_validation_passes_catalog_gate":False,
                "primary_dynamic_habitat_eligible":False,
                "sentinel_validation_eligible":False,
            })
        result=summarize_audit(pd.DataFrame(rows))
        self.assertTrue(result["program_feasibility_gate_passed"])


if __name__ == "__main__":
    unittest.main()
