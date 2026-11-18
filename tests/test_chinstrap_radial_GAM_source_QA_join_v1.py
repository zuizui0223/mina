import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
P=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_radial_GAM_source_QA_join_v1.py"
spec=importlib.util.spec_from_file_location("rqa",P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class RadialSourceQATests(unittest.TestCase):
    def test_cardinality_and_tiers_fixed(self):
        self.assertEqual(len(m.ISLAND_YEARS),7)
        self.assertEqual(len(m.TIERS),4)
        self.assertEqual(m.NUMERIC_PRIMARY[2013,"PI"],4.499387620290262)
    def test_missing_TDR_is_not_no_dive_and_GPS_source_unit_is_kept(self):
        x={"island":"SI","season_start":"2018","deployment":"SIC999",
           "preseason_qualified_source_hourly":"True",
           "same_summer_qualified_source_hourly":"True",
           "preseason_observed_track_mean_GAM_g_m2":"2.0",
           "same_summer_observed_track_mean_GAM_g_m2":"1.0"}
        got=m.attach_QA([x],[],require_complete_source=False)[0]
        self.assertTrue(got["GPS_source_hourly_ge10"])
        self.assertTrue(got["source_not_in_TDR_300_is_not_animal_no_dive"])
        self.assertIsNone(got["TDR_source_covered_and_QA_primary"])
    def test_missing_QA_strict_site_year_explicit(self):
        rows=[{"island":"SI","season_start":"2018","deployment":"SIC998",
               "GPS_source_hourly_ge10":True,"source_original_BAS_TDR_GPS_pair_exists":True,
               "TDR_source_covered_and_QA_primary":True,
               "TDR_source_covered_and_QA_strict":False,
               "preseason_observed_track_mean_GAM_g_m2":"3.0",
               "preseason_distance_matched_reference_GAM_g_m2":"10.0",
               "same_summer_observed_track_mean_GAM_g_m2":"4.0",
               "same_summer_distance_matched_reference_GAM_g_m2":"12.0"}]
        self.assertFalse(m.eligible(rows[0],"sensor_QA_strict"))
        self.assertTrue(m.eligible(rows[0],"sensor_QA_primary"))
    def test_original_source_replay_end_to_end(self):
        root=ROOT/"build"
        radial=root/"source_geo/derived/original_tag_visited_vs_radial_background.csv"
        qa_csv=root/"original300/all_300_original_sensor_QA.csv"
        if not radial.exists() or not qa_csv.exists():
            self.skipTest("needs original publisher GPS/model and 300 original TDR source replay")
        tags=m.attach_QA(m.modelled_tag_rows(radial),m.qa.evaluate(m.qa.read(qa_csv)))
        groups,pairs=m.summarize(tags)
        counts=m.verify(tags,groups,pairs)
        self.assertEqual(counts["sensor_QA_primary"],175)
        self.assertEqual(len(pairs),24)

if __name__=="__main__":unittest.main()
