import unittest
from scripts.audit_scar_v713_land_service import choose_layer, schema_support, BOXES

class TestSCARStaticSource(unittest.TestCase):
    def test_only_one_explicit_feature_layer(self):
        self.assertEqual(choose_layer({"layers":[{"id":0,"type":"Feature Layer"}]}),0)
        self.assertIsNone(choose_layer({"layers":[{"id":0,"type":"Feature Layer"},
                                                   {"id":1,"type":"Feature Layer"}]}))
        self.assertIsNone(choose_layer({"layers":[{"id":0,"type":"Raster Layer"}]}))
    def test_surface_field_required(self):
        self.assertEqual(schema_support({"fields":[{"name":"SuRfAcE"},{"name":"OBJECTID"}]})["surface_field"],"SuRfAcE")
        self.assertIsNone(schema_support({"fields":[{"name":"habitat"}]})["surface_field"])
    def test_frozen_boxes(self):
        self.assertEqual(len(BOXES),3)
        for w,s,e,n in BOXES.values():
            self.assertLess(w,e)
            self.assertLess(s,n)

if __name__=="__main__":
    unittest.main()
