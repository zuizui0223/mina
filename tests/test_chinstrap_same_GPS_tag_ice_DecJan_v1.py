import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_same_GPS_tag_ice_DecJan_v1.py"
s=importlib.util.spec_from_file_location("paired_month",P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class PairMonth(unittest.TestCase):
    def test_real_source_month_if_present(self):
        path=ROOT/"build/observed_ice_GPS/original_GPS_tag_month_SIC.csv"
        if not path.exists():self.skipTest("requires original satellite GPS source run")
        data,summary=m.paired(m.read(path))
        self.assertGreaterEqual(len(data),12)
        self.assertEqual(next(x["n_identical_source_GPS_tags_observed_both_months"]
           for x in summary if x["original_island"]=="SI" and x["season_start"]==2013),2)
        self.assertEqual(next(x["n_identical_source_GPS_tags_observed_both_months"]
           for x in summary if x["original_island"]=="PI" and x["season_start"]==2013),10)
    def test_missing_not_ice_zero(self):
        self.assertEqual(m.ORIG_DOI,"10.15770/EUM_SAF_OSI_0023")
        self.assertEqual(m.EXPECTED_2013,{"SI":2,"PI":10})
if __name__=="__main__":unittest.main()
