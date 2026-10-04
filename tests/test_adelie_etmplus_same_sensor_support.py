import unittest
from pathlib import Path
import tempfile
import pandas as pd

from scripts.audit_adelie_etmplus_same_sensor_support import build_roster, summarize


class SameSensorSupportTests(unittest.TestCase):
    def test_summary_counts_only_landsat7_and_summer(self):
        items = [
            {"properties":{"platform":"LANDSAT_7","datetime":"2000-12-01T00:00:00Z","eo:cloud_cover":20}},
            {"properties":{"platform":"LANDSAT_7","datetime":"2001-01-02T00:00:00Z","eo:cloud_cover":30}},
            {"properties":{"platform":"LANDSAT_7","datetime":"2002-02-02T00:00:00Z","eo:cloud_cover":40}},
            {"properties":{"platform":"LANDSAT_8","datetime":"2002-02-02T00:00:00Z","eo:cloud_cover":0}},
            {"properties":{"platform":"LANDSAT_7","datetime":"2002-06-02T00:00:00Z","eo:cloud_cover":0}},
        ]
        q = summarize(items, {11,12,1,2,3})
        self.assertEqual(q["summer_scenes_total"], 3)
        self.assertEqual(q["years_cloud_le_80"], 3)

    def test_roster_is_species_specific_and_outcome_blind(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            forcing = pd.DataFrame([
                {"site_id":"A","species_id":"ADPE"},
                {"site_id":"A","species_id":"CHPE"},
                {"site_id":"B","species_id":"ADPE"},
            ])
            atlas = pd.DataFrame([
                {"site_id":"A","site_name":"A","region":"R1","latitude":-64.0,"longitude":-60.0},
                {"site_id":"B","site_name":"B","region":"R2","latitude":-66.0,"longitude":160.0},
            ])
            fp=td/"f.csv"; ap=td/"a.csv"
            forcing.to_csv(fp,index=False); atlas.to_csv(ap,index=False)
            roster=build_roster(fp,ap,expected_sites=2)
            self.assertEqual(set(roster.site_id),{"A","B"})

    def test_forbidden_outcome_column_fails(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            forcing = pd.DataFrame([{"site_id":"A","species_id":"ADPE","count":10}])
            atlas = pd.DataFrame([{"site_id":"A","site_name":"A","region":"R1","latitude":-64.0,"longitude":-60.0}])
            fp=td/"f.csv"; ap=td/"a.csv"
            forcing.to_csv(fp,index=False); atlas.to_csv(ap,index=False)
            with self.assertRaises(ValueError):
                build_roster(fp,ap,expected_sites=1)


if __name__ == "__main__":
    unittest.main()
