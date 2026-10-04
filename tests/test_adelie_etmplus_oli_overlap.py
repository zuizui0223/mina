import unittest
from datetime import datetime, timezone
from scripts.audit_adelie_etmplus_oli_overlap import pair_scenes, filter_items

class SensorOverlapTests(unittest.TestCase):
    def test_pairing_is_nearest_and_unique(self):
        e=[
            {"id":"e1","datetime":datetime(2013,12,1,tzinfo=timezone.utc),"cloud":10},
            {"id":"e2","datetime":datetime(2014,1,20,tzinfo=timezone.utc),"cloud":10},
        ]
        o=[
            {"id":"o1","datetime":datetime(2013,12,7,tzinfo=timezone.utc),"cloud":10},
            {"id":"o2","datetime":datetime(2014,1,25,tzinfo=timezone.utc),"cloud":10},
        ]
        p=pair_scenes(e,o,8)
        self.assertEqual(len(p),2)
        self.assertEqual(p[0]["etmplus_id"],"e2") if p[0]["absolute_day_difference"]<p[1]["absolute_day_difference"] else None

    def test_filter_platform_month_cloud(self):
        items=[
            {"id":"a","properties":{"platform":"LANDSAT_7","datetime":"2014-12-01T00:00:00Z","eo:cloud_cover":20}},
            {"id":"b","properties":{"platform":"LANDSAT_8","datetime":"2014-12-01T00:00:00Z","eo:cloud_cover":20}},
            {"id":"c","properties":{"platform":"LANDSAT_7","datetime":"2014-06-01T00:00:00Z","eo:cloud_cover":20}},
            {"id":"d","properties":{"platform":"LANDSAT_7","datetime":"2014-12-02T00:00:00Z","eo:cloud_cover":90}},
        ]
        q=filter_items(items,"LANDSAT_7",{11,12,1,2,3},80)
        self.assertEqual([x["id"] for x in q],["a"])

if __name__=="__main__":
    unittest.main()
