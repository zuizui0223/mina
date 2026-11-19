import unittest
from scripts.replay_aadc_adelie_original_season_codec import (
    parse_season_sixdigits,legacy_unconverted_season,make_site_states,transitions
)
class TestSixDigitOriginalPublisherCodec(unittest.TestCase):
    def test_semantics_and_century_rollover(self):
        self.assertEqual(parse_season_sixdigits(191213),1912)
        self.assertEqual(parse_season_sixdigits(195960.0),1959)
        self.assertEqual(parse_season_sixdigits(199900),1999)
        self.assertEqual(parse_season_sixdigits(200001),2000)
        self.assertIsNone(parse_season_sixdigits(200003))
        self.assertIsNone(parse_season_sixdigits(199901))
        self.assertIsNone(parse_season_sixdigits(None))
        self.assertEqual(legacy_unconverted_season(191213),191213)
    def test_real_previously_missed_adjacent_years(self):
        x=[{"species_code":"ADP","geog_site_id":"IS1","season":191213,
            "occurrence":"A","sub_group":"SG1"},
           {"species_code":"ADP","geog_site_id":"IS1","season":191314,
            "occurrence":"P","sub_group":"SG1"}]
        legacy,meta=make_site_states(x,legacy_unconverted_season)
        corrected,newmeta=make_site_states(x,parse_season_sixdigits)
        self.assertEqual(len(legacy),2)
        self.assertEqual(legacy[("IS1",191213)],"A")
        self.assertEqual(corrected[("IS1",1912)],"A")
        old=transitions(legacy,meta["site_subgroups"],{"IS1":"island"})
        new=transitions(corrected,newmeta["site_subgroups"],{"IS1":"island"})
        self.assertEqual(old["pairs"].get("AP",0),0)
        self.assertEqual(new["pairs"]["AP"],1)
        self.assertEqual(new["AP_subgroups"],1)
        self.assertEqual(new["AP_first_observed"],1)
        self.assertFalse(new["observed_AP_events"][0]["confirmed_first_ever_settlement"])
    def test_same_year_P_A_conflict_preserves_frozen_P_wins(self):
        x=[{"species_code":"ADP","geog_site_id":"S","season":201920,
            "occurrence":"P","sub_group":"S1"},
           {"species_code":"ADP","geog_site_id":"S","season":201920,
            "occurrence":"A","sub_group":"S1"}]
        v,meta=make_site_states(x,parse_season_sixdigits)
        self.assertEqual(v[("S",2019)],"P")
        self.assertEqual(meta["P_and_A_same_site_season"],1)
if __name__=="__main__":
    unittest.main()
