import unittest, pandas as pd
from scripts.run_paper3_zenodo_interannual_aliasing import build_anchors, transitions

class InterannualAliasingTests(unittest.TestCase):
    def test_consecutive_only(self):
        d=pd.DataFrame([
          {"colony":"Astrid","season":"2020-2021","date":"2020-05-01","point_lon":0,"point_lat":-70,"origin_match":True},
          {"colony":"Astrid","season":"2021-2022","date":"2021-05-01","point_lon":0.01,"point_lat":-70,"origin_match":True},
          {"colony":"Astrid","season":"2023-2024","date":"2023-05-01","point_lon":0.02,"point_lat":-70,"origin_match":True},
        ])
        a=build_anchors(d); t=transitions(a)
        self.assertEqual(len(t),1)
        self.assertEqual(t.iloc[0]["from_season"],"2020-2021")
    def test_earliest_date_anchor(self):
        d=pd.DataFrame([
          {"colony":"Astrid","season":"2020-2021","date":"2020-05-02","point_lon":1,"point_lat":-70,"origin_match":True},
          {"colony":"Astrid","season":"2020-2021","date":"2020-05-01","point_lon":0,"point_lat":-70,"origin_match":True},
        ])
        a=build_anchors(d)
        self.assertEqual(a.iloc[0]["anchor_date"],"2020-05-01")
if __name__=="__main__": unittest.main()
