import unittest
import pandas as pd
from scripts.validate_emperor_zenodo_season_reference_from_v1 import summarize

class FrozenFeatureSemanticTests(unittest.TestCase):
    def test_invariant_season(self):
        c={
          "contract_id":"x",
          "source":{"expected_colonies":["Astrid"]},
          "semantic_test":{
            "within_colony_season_coordinate_tolerance_m":10,
            "minimum_seasons_per_colony":1,
            "required_seasons_with_invariant_reference_fraction":1.0,
            "required_date_parse_fraction":1.0,
            "interpretation_if_passed":"ok"
          }
        }
        d=pd.DataFrame([
          {"colony":"Astrid","season":"2020-2021","date":"2020-09-01","point_lon":1.0,"point_lat":-70.0},
          {"colony":"Astrid","season":"2020-2021","date":"2020-10-01","point_lon":1.0,"point_lat":-70.0},
        ])
        s,o=summarize(d,c)
        self.assertTrue(o["decision"]["semantic_gate_passed"])
        self.assertEqual(len(s),1)

if __name__=="__main__":
    unittest.main()
