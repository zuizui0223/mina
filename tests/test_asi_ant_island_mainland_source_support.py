import unittest
from unittest.mock import patch
import pandas as pd
from shapely.geometry import box
from scripts.audit_asi_ant_island_mainland_source_support import (
    classify_source_sites, geography_support
)

class FakeTransform:
    def transform(self,lon,lat): return lon,lat

class TestASIGeographyOnly(unittest.TestCase):
    def test_unique_land_proxy_and_offland_without_nearest_rescue(self):
        land=[box(-20,-20,0,20),box(1,0,3,3)]
        sites=pd.DataFrame([
            {"Code":"C0","Name":"Main", "Lat":"1","Lon":"-10"},
            {"Code":"I0","Name":"Island","Lat":"1","Lon":"2"},
            {"Code":"O0","Name":"Ocean", "Lat":"1","Lon":"4"},
        ])
        with patch("scripts.audit_asi_ant_island_mainland_source_support.Transformer.from_crs",return_value=FakeTransform()):
            got=classify_source_sites(sites,land,["big","little"])
        by=got.set_index("Code")
        self.assertEqual(by.loc["C0","geography_group"],"CONTINENT_LARGEST_LAND_POLYGON_PROXY")
        self.assertEqual(by.loc["I0","geography_group"],"NONCONTINENTAL_LAND_POLYGON_PROXY")
        self.assertEqual(by.loc["O0","geography_group"],"OFF_LAND_OR_AMBIGUOUS")
        self.assertFalse(by.loc["I0","polygon_source_row_is_validated_physical_island"])

    def test_structure_gate_does_not_use_breeding_effect(self):
        geo=pd.DataFrame([
            {"Code":"I0","geography_group":"NONCONTINENTAL_LAND_POLYGON_PROXY",
             "spatial_block_100km":"1_1","SCAR_source_land_index":"1"},
            {"Code":"C0","geography_group":"CONTINENT_LARGEST_LAND_POLYGON_PROXY",
             "spatial_block_100km":"2_1","SCAR_source_land_index":"0"},
        ])
        visits=pd.DataFrame([
            {"Code":"I0","season_start":2000,"ADPE":"0","CHPE":"0","GEPE":"2"},
            {"Code":"I0","season_start":2001,"ADPE":"0","CHPE":"1","GEPE":"2"},
            {"Code":"C0","season_start":2001,"ADPE":"0","CHPE":"0","GEPE":"NA"}
        ])
        panel=pd.DataFrame([
            {"Code":"I0","ADPE":"ALL_VISITS_NONDETECTION","CHPE":"ALL_VISITS_NONDETECTION","GEPE":"BREEDING_OBSERVED"},
            {"Code":"I0","ADPE":"ALL_VISITS_NONDETECTION","CHPE":"PRESENCE_ONLY_OBSERVED","GEPE":"BREEDING_OBSERVED"},
            {"Code":"C0","ADPE":"ALL_VISITS_NONDETECTION","CHPE":"ALL_VISITS_NONDETECTION","GEPE":"INCOMPLETE_OR_MISSING"},
        ])
        r,g,j=geography_support(geo,panel,visits)
        self.assertEqual(r["NONCONTINENTAL_LAND_POLYGON_PROXY"]["source_visits"],2)
        self.assertEqual(r["CONTINENT_LARGEST_LAND_POLYGON_PROXY"]["species_scored_visit_counts"]["GEPE"],0)
        self.assertFalse(all(g["NONCONTINENTAL_LAND_POLYGON_PROXY"].values()))

if __name__=="__main__":
    unittest.main()
