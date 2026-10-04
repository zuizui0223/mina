import unittest
import pandas as pd
from scripts.run_paper3_zenodo_interannual_aliasing_v2 import build_anchors, transitions

class InterannualV2Tests(unittest.TestCase):
    def test_build_and_consecutive(self):
        d=pd.DataFrame([
          {"colony":"Astrid","season":"2020-2021","reference_lon":0.0,"reference_lat":-70.0,"reference_invariant":True},
          {"colony":"Astrid","season":"2021-2022","reference_lon":0.01,"reference_lat":-70.0,"reference_invariant":True},
          {"colony":"Astrid","season":"2023-2024","reference_lon":0.02,"reference_lat":-70.0,"reference_invariant":True},
        ])
        a=build_anchors(d)
        t=transitions(a)
        self.assertEqual(len(t),2)
        self.assertTrue(bool(t.iloc[0]["consecutive"]))
        self.assertFalse(bool(t.iloc[1]["consecutive"]))
    def test_reject_duplicate_anchor(self):
        d=pd.DataFrame([
          {"colony":"Astrid","season":"2020-2021","reference_lon":0.0,"reference_lat":-70.0,"reference_invariant":True},
          {"colony":"Astrid","season":"2020-2021","reference_lon":0.0,"reference_lat":-70.0,"reference_invariant":True},
        ])
        with self.assertRaises(ValueError):
            build_anchors(d)

    def test_radius_keys_keep_1_and_10_distinct(self):
        from scripts.run_paper3_zenodo_interannual_aliasing_v2 import summarize
        a=pd.DataFrame([
          {"colony_id":"A","season":"2020-2021","season_start":2020,"reference_lon":0.0,"reference_lat":-70.0,"x3031":0.0,"y3031":0.0},
          {"colony_id":"A","season":"2021-2022","season_start":2021,"reference_lon":0.0,"reference_lat":-70.0,"x3031":1500.0,"y3031":0.0},
        ])
        tr=transitions(a)
        r=summarize(a,tr,[1,10])
        self.assertIn("1",r["aliasing_curve"])
        self.assertIn("10",r["aliasing_curve"])
        self.assertNotEqual(r["aliasing_curve"]["1"]["false_turnover_fraction"],r["aliasing_curve"]["10"]["false_turnover_fraction"])

if __name__=="__main__":
    unittest.main()
