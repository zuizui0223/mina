"""Synthetic-only spatial logic checks; original data are fetched by CI workflow."""
import unittest
import pandas as pd
from scripts.audit_glims_mapppd_retreat_proximity import (
    dated_grouped_features, retreat_candidate_shapes, summarize_site_proximity
)

IDENTITY = lambda x,y,z=None:(x,y) if z is None else (x,y,z)

def square(x0,y0,x1,y1):
    return {"type":"Polygon","coordinates":[[
        [x0,y0],[x1,y0],[x1,y1],[x0,y1],[x0,y0]
    ]]}

class TestGlacierPair(unittest.TestCase):
    def test_earliest_latest_polygon_loss_uses_same_glims_id(self):
        data={"features":[
            {"type":"Feature","geometry":square(0,0,2,2),
             "properties":{"glims_id":"G1","src_date":"2000-01-01"}},
            {"type":"Feature","geometry":square(0,0,1,2),
             "properties":{"glims_id":"G1","src_date":"2010-01-01"}},
            {"type":"Feature","geometry":square(0,0,1,1),
             "properties":{"glims_id":"G2","src_date":"2005-01-01"}}
        ]}
        groups, flags=dated_grouped_features(data, IDENTITY)
        shapes, exclusions=retreat_candidate_shapes(groups)
        self.assertFalse(flags)
        self.assertEqual(len(shapes),1)
        self.assertEqual(shapes[0]["glims_id"],"G1")
        self.assertEqual(shapes[0]["early_year"],2000)
        self.assertEqual(shapes[0]["late_year"],2010)
        self.assertAlmostEqual(shapes[0]["geometry"].area,2)
        self.assertEqual(exclusions["no_valid_multi_epoch_pair_5plus_years"],1)

    def test_missing_source_dates_are_not_filled(self):
        d={"features":[{"type":"Feature","geometry":square(0,0,1,1),
                        "properties":{"glims_id":"G1","date_available":"2026"}}]}
        groups,flags=dated_grouped_features(d, IDENTITY)
        self.assertEqual(len(groups),0)
        self.assertEqual(flags["missing_glacier_id_or_unique_source_year"],1)

    def test_site_nearby_is_only_provisional_support(self):
        x={"glims_id":"G1","early_year":2000,"late_year":2010,
           "geometry":__import__("shapely.geometry",fromlist=["box"]).box(1,0,2,1)}
        frame=pd.DataFrame([{"site_id":"X1","site_name":"Example",
                            "latitude":0.5,"longitude":1.5}])
        rows=summarize_site_proximity(frame,[x],IDENTITY)
        self.assertEqual(len(rows),1)
        self.assertTrue(rows[0]["proximity_not_exact_exposure"])
        self.assertEqual(rows[0]["nearest_apparent_ice_loss_m"],0)


if __name__ == "__main__":
    unittest.main()
