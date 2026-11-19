import unittest
import pandas as pd
from scripts.audit_asi_glims_rock_candidate_source import (
    season_state,annual_panel,transition_support,crosswalk_25
)

class TestASIOriginalStateSemantics(unittest.TestCase):
    def test_observed_zero_not_true_absence(self):
        self.assertEqual(season_state(["0","0"]),"ALL_VISITS_NONDETECTION")
        self.assertEqual(season_state(["0","2"]),"BREEDING_OBSERVED")
        self.assertEqual(season_state(["0","1"]),"PRESENCE_ONLY_OBSERVED")
        self.assertEqual(season_state(["NA"]),"INCOMPLETE_OR_MISSING")
        self.assertEqual(season_state(["0","NA"]),"INCOMPLETE_OR_MISSING")

    def test_real_0_to_breeding_is_only_observed_transition(self):
        r=pd.DataFrame([
            {"Code":"TEST","season_start":2002,"ADPE":"0","CHPE":"NA","GEPE":"0"},
            {"Code":"TEST","season_start":2002,"ADPE":"0","CHPE":"NA","GEPE":"0"},
            {"Code":"TEST","season_start":2003,"ADPE":"2","CHPE":"NA","GEPE":"2"},
            {"Code":"TEST","season_start":2003,"ADPE":"0","CHPE":"NA","GEPE":"0"},
            {"Code":"TEST","season_start":2005,"ADPE":"0","CHPE":"NA","GEPE":"0"}
        ])
        panel=annual_panel(r)
        pairs={x["species_id"]:x for x in transition_support(panel)}
        self.assertEqual(len(pairs["ADPE"]["candidate_0_to_breeding_events"]),1)
        self.assertFalse(pairs["ADPE"]["candidate_0_to_breeding_events"][0]["true_colonization_confirmed"])
        self.assertEqual(pairs["ADPE"]["source_observed_transition_counts"]["consecutive_seasons_with_states"],1)
        self.assertTrue(panel[panel.season_start.eq(2003)]["ADPE_within_season_0_and_positive"].iloc[0])

    def test_source_code_match_rejects_territorial_mislabel(self):
        mock=pd.DataFrame([{
            "site_id":f"S{i:02d}","site_name":f"Site{i}",
            "latitude":-64.5,"longitude":-63.5,
            "near_1km_source_only":True,
            "glims_late_year":2002,"rock_source_year":2024,
            "land_source_feature_id":100
        } for i in range(25)])
        meta=pd.DataFrame([{"Code":"S00","Name":"Site0",
                           "Lat":"-64.5000","Lon":"-63.5000"}])
        visits=pd.DataFrame([{"Code":"S00","season_start":2010}])
        x=crosswalk_25(visits,meta,mock)
        self.assertEqual(int(x["matched_code"].sum()),1)
        self.assertEqual(int(x["matched_exact_source_location"].sum()),1)
        self.assertEqual(int(x["asi_original_visits"].fillna(0).sum()),1)
        self.assertFalse(x.loc[x["site_id"].eq("S00"),"verified_prior_absence_of_breeding_at_the_rock_patch"].iloc[0])

if __name__=="__main__":
    unittest.main()
