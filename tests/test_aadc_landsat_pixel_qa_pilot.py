import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from scripts.audit_aadc_landsat_pixel_qa_pilot import (
    classify_pixel_qa,validate_source_receipt,permitted_asset
)

class TestSourcePixelQuality(unittest.TestCase):
    def test_USGS_bad_flags_no_false_clear(self):
        self.assertTrue(classify_pixel_qa(0)["candidate_visible_non_snow_non_water"])
        for bit in [0,1,3,4,5,7]:
            self.assertFalse(classify_pixel_qa(1<<bit)["candidate_visible_non_snow_non_water"])
        # Never use the unreliable Landsat 4-7 Clear bit alone.
        self.assertFalse(classify_pixel_qa((1<<6)|(1<<3))["candidate_visible_non_snow_non_water"])
        self.assertTrue(classify_pixel_qa(1<<5)["not_fill_cloud_or_shadow"])
    def test_asset_host_restrictions(self):
        self.assertTrue(permitted_asset("https://landsatlook.usgs.gov/data/QA_PIXEL.TIF"))
        self.assertTrue(permitted_asset("s3://usgs-landsat/collection02/data/file.TIF"))
        self.assertFalse(permitted_asset("http://landsatlook.usgs.gov/data/QA_PIXEL.TIF"))
        self.assertFalse(permitted_asset("https://example.com/QA_PIXEL.TIF"))
        self.assertFalse(permitted_asset("s3://private-bucket/qa.tif"))
    def test_source_only_fixed_ROI_and_events(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"source.json"
            rows=[]
            for code,sp,y in [("IS_70749","SK",2008),("IS_105","ADP",2017)]:
                for side in ("reported_A_season","reported_P_season"):
                    rows.append({"geog_site_id":code,"species_code":sp,"a_season_start":y,
                                 "comparison_side":side,"lat":-66.6,"lon":140.0,
                                 "original_subgroup":"DUM_SG_03","n_scene_items":2})
            # Other original 14 events provide unselected, source-only placeholders.
            for i in range(14):
                for side in ("reported_A_season","reported_P_season"):
                    rows.append({"geog_site_id":f"OTHER{i}","species_code":"SK",
                                 "a_season_start":1998+i,"comparison_side":side,
                                 "n_scene_items":0})
            path.write_text(json.dumps({
                 "status":"LANDSAT_STAC_PILOT_ORIGINAL_SCENE_METADATA_ONLY",
                 "events_sampled":16,"source_queries_run":32,
                 "events_with_any_scene_metadata_in_both_seasons":8,
                 "source_site_scene_metadata":rows
            }))
            selected=validate_source_receipt(path)
            self.assertEqual(len(selected),2)
            self.assertEqual(selected[("IS_105","ADP",2017)]["p_year"],2018)

if __name__=="__main__":
    unittest.main()
