import unittest
import pandas as pd

from scripts.run_paper3_zenodo_interannual_aliasing import build_anchors, transitions

class InterannualAliasingTests(unittest.TestCase):
    def test_consecutive_only(self):
        d=pd.DataFrame([
          {"colony":"Astrid","season":"2020-2021","point_lon":0,"point_lat":-70,"earliest_route_date":"2020-09-01"},
          {"colony":"Astrid","season":"2021-2022","point_lon":0.01,"point_lat":-70,"earliest_route_date":"2021-09-01"},
          {"colony":"Astrid","season":"2023-2024","point_lon":0.02,"point_lat":-70,"earliest_route_date":"2023-09-01"},
        ])
        a=build_anchors(d); t=transitions(a)
        self.assertEqual(len(t),1)
        self.assertEqual(t.iloc[0]["from_season"],"2020-2021")

    def test_semantic_annual_anchor_is_used_directly(self):
        d=pd.DataFrame([
          {"colony":"Astrid","season":"2020-2021","point_lon":1.0,"point_lat":-70.0,"earliest_route_date":"2020-09-02"},
        ])
        a=build_anchors(d)
        self.assertEqual(a.iloc[0]["anchor_date"],"2020-09-02")
        self.assertNotIn("origin_match",a.columns)

    def test_duplicate_colony_season_fails_closed(self):
        d=pd.DataFrame([
          {"colony":"Astrid","season":"2020-2021","point_lon":1.0,"point_lat":-70.0,"earliest_route_date":"2020-09-02"},
          {"colony":"Astrid","season":"2020-2021","point_lon":1.0,"point_lat":-70.0,"earliest_route_date":"2020-09-02"},
        ])
        with self.assertRaises(ValueError):
            build_anchors(d)

if __name__=="__main__":
    unittest.main()
