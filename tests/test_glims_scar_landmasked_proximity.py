import unittest
import pandas as pd
from shapely.geometry import Polygon, box
from scripts.audit_glims_scar_landmasked_proximity import (
    clip_to_current_terrestrial, sites_with_same_feature, build_lands)

def ident(lon,lat):return lon,lat

class TestStrictStaticLand(unittest.TestCase):
    def test_apparent_ice_loss_offshore_must_be_removed(self):
        diffs=[{"glims_id":"g0","geometry":box(20,20,21,21)}]
        parts,failed=clip_to_current_terrestrial(diffs,[box(0,0,10,10)],["island1"])
        self.assertEqual(parts,{})
        self.assertEqual(failed.get("apparent_diff_off_terrestrial_mask"),1)

    def test_within_land_but_other_feature_is_not_same_island(self):
        # Proximity is only computed within same explicitly intersected land feature.
        lands=[box(0,0,10,10),box(11,0,21,10)]
        ice=[{"glims_id":"g1","geometry":box(10.5,0,12,1)}]
        parts,failed=clip_to_current_terrestrial(ice,lands,["a","b"])
        self.assertEqual(set(parts),{"b"})
        sites=pd.DataFrame([
            {"site_id":"S1","site_name":"one","latitude":0.5,"longitude":9.5},
            {"site_id":"S2","site_name":"two","latitude":0.5,"longitude":11.5},
        ])
        got=sites_with_same_feature(sites,lands,["a","b"],parts,ident)
        self.assertFalse(got[0]["within_1km_source_only"])
        self.assertIsNone(got[0]["distance_m_same_feature_terrestrial_glims_difference"])
        self.assertTrue(got[1]["within_1km_source_only"])
        self.assertFalse(got[1]["landmask_proves_new_rock"])

    def test_surface_and_polygon_verification(self):
        fc={"features":[
             {"type":"Feature","properties":{"FID":1,"surface":"land"},
              "geometry":{"type":"Polygon","coordinates":[
                  [[0,0],[2,0],[2,2],[0,2],[0,0]]] }},
             {"type":"Feature","properties":{"FID":2,"surface":"ice shelf"},
              "geometry":{"type":"Polygon","coordinates":[
                  [[3,0],[4,0],[4,1],[3,1],[3,0]]] }},
        ]}
        land, ids, issues=build_lands(fc,ident)
        self.assertEqual(len(land),1)
        self.assertEqual(ids,["1"])
        self.assertEqual(issues["unexpected_surface_not_land"],1)

if __name__=="__main__":
    unittest.main()
