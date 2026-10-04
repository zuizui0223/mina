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

if __name__=="__main__":
    unittest.main()
