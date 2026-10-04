import unittest
import pandas as pd

from scripts.run_paper3_sar_2024_validation import standardize, strip_interannual


class SAR2024ValidationTests(unittest.TestCase):
    def test_standardize_parses_source_and_drops_nonlocations(self):
        raw = pd.DataFrame([
            {"colony":"Atka Bay","image":"2024-04-12-20-38-35_UMBRA-06_GEC.tif","xcoord":-8.1,"ycoord":-70.6,"b_pres":"yes"},
            {"colony":"Atka Bay","image":"2024-04-20-20-38-35_UMBRA-06_GEC.tif","xcoord":None,"ycoord":None,"b_pres":"no"},
        ])
        x = standardize(raw)
        self.assertEqual(len(x), 1)
        self.assertEqual(x.iloc[0].season, 2024)
        self.assertEqual(str(x.iloc[0].obs_date.date()), "2024-04-12")

    def test_external_result_removes_interannual_claims(self):
        fake = {
            "analysis_id":"x",
            "support":{"colonies":1,"seasons":1,"observation_dates":2,"consecutive_interannual_transitions":0,"post_anchor_dates":1},
            "identity_preserving_radii_km":{
                "interannual_anchor_displacement":{"q50":None,"q90":None,"q95":None},
                "within_season_min_group_distance":{"q50":1,"q90":2,"q95":3},
            },
            "aliasing_curve":{"1":{"interannual_false_turnover_fraction":None,"interannual_false_turnover_n":0,"interannual_transition_n":0,"within_season_false_absence_fraction":0.5,"within_season_false_absence_n":1,"within_season_post_anchor_date_n":2}},
            "by_colony":[{"colony_id":"A","seasons":1,"observation_dates":2,"consecutive_transitions":0,"interannual_q95_km":None,"within_season_detection_q95_km":2}],
            "boundary":[],
        }
        y=strip_interannual(fake)
        self.assertNotIn("interannual_anchor_displacement",y["identity_preserving_radii_km"])
        self.assertNotIn("interannual_q95_km",y["by_colony"][0])


if __name__ == "__main__":
    unittest.main()
