import unittest
from scripts.audit_all8_aadc_landsat_local_qa import selected_scene, index_events
class TestFixedSourceSelection(unittest.TestCase):
    def test_source_scene_metadata_not_local_clear_filter(self):
        q={"scene_first_twelve_by_datetime":[
          {"stac_id":"a","acquired":"2018-11-11","qa_pixel_asset_listed":True,
           "global_scene_cloud_cover":20},
          {"stac_id":"b","acquired":"2018-11-18","qa_pixel_asset_listed":True,
           "global_scene_cloud_cover":5},
          {"stac_id":"c","acquired":"2018-11-01","qa_pixel_asset_listed":False,
           "global_scene_cloud_cover":0},
        ]}
        self.assertEqual(selected_scene(q)["stac_id"],"b")
    def test_source_inventory_exact_source_events(self):
        src={"events_sampled":16,"source_site_scene_metadata":[]}
        with self.assertRaises(ValueError):index_events(src)
if __name__=="__main__":unittest.main()
