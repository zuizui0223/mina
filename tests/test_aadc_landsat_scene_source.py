import unittest
from scripts.audit_aadc_landsat_scene_source import (
    season_bounds, site_geometry, EXPECTED_EVENTS,EXPECTED_SITES
)
class TestLandsatSourceWindow(unittest.TestCase):
    def test_fixed_austral_season_dates(self):
        self.assertEqual(season_bounds(1998),
                         "1998-11-01T00:00:00Z/1999-03-31T23:59:59Z")
        self.assertEqual(season_bounds(2017),
                         "2017-11-01T00:00:00Z/2018-03-31T23:59:59Z")
    def test_source_site_codes_and_bounds(self):
        e={"geog_site_id":"IS_105","species_code":"ADP",
           "season_start":2017,"season_next":2018,
           "geog_site_feature":"island"}
        s={"geog_site_latitude":-66.5,"geog_site_longitude":112.2,
           "geog_site_feature":"island","sub_group":"LUT_SG_01"}
        x=site_geometry(e,s)
        self.assertEqual(x["a_season_start"],2017)
        self.assertFalse(x["source_location_is_nest_patch_polygon"])
        self.assertEqual((EXPECTED_EVENTS,EXPECTED_SITES),(16,14))
        with self.assertRaises(ValueError):
            site_geometry(e,{**s,"geog_site_feature":"continent"})
        with self.assertRaises(ValueError):
            site_geometry(e,{**s,"geog_site_longitude":-63.2})
if __name__=="__main__":
    unittest.main()
