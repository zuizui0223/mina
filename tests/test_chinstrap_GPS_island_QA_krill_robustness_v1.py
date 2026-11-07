import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
p=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_GPS_island_QA_krill_robustness_v1.py"
s=importlib.util.spec_from_file_location("qa_island",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class CohortCheck(unittest.TestCase):
    def test_source_pins(self):
        self.assertEqual(m.GPS_SHA,"44cb30e8b3136317578d4e86b1dcf99146fae6ab0e721e35a05d4e5ebc6bdda6")
        self.assertEqual(len(m.PAIRS),3)
        self.assertEqual(len(m.TIERS),4)
    def test_missing_TDR_not_false_nondiving(self):
        g=[{"deployment":"LI999","season_start":"2011","island":"LI",
            "preseason_native_model_krill_g_m2":"5.0","same_summer_native_model_krill_g_m2":"7.0"}]
        x=m.joined(g,[])[0]
        self.assertIsNone(x["source_QA_primary"])
        self.assertTrue(x["not_source_matched_is_missing_TDR_not_nondiving"])
    def test_frozen_sources_if_present(self):
        gps=ROOT/"build/island_krill_original/source_tag_model_exposures.csv"
        sensor=ROOT/"build/original300/all_300_original_sensor_QA.csv"
        if not gps.exists() or not sensor.exists():
            self.skipTest("BAS original GPS/TDR and original Freer source must be re-extracted in CI")
        x=m.joined(m.original_gps(gps),m.qa.evaluate(m.qa.read(sensor)))
        y=m.comparisons(x)
        result=m.verify(x,y)
        self.assertEqual(result["primary"],175)
        self.assertEqual(len(y),24)
if __name__=="__main__":unittest.main()
