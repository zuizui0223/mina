"""Do not choose GPS days using ice, nor silently extrapolate ice-free days."""
import sys,importlib.util,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
p=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_daily_SIC_three_island_year_pairs_v1.py"
s=importlib.util.spec_from_file_location("allice",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class MultiYearSourceDailySIC(unittest.TestCase):
    def test_fixed_original_island_seasons(self):
        self.assertEqual(m.PAIRS,((2011,"LI"),(2013,"PI"),(2015,"MI")))
        self.assertEqual(m.PHASES,("all_GPS_days","Dec_GPS_only","Jan_GPS_only"))
    def test_source_2013_control(self):
        self.assertEqual(m.EXPECTED_2013[0],"20131229")
        self.assertEqual(m.EXPECTED_2013[-1],"20140111")
        self.assertEqual(len(m.EXPECTED_2013),14)
    def test_originals_when_available(self):
        root=ROOT/"build/three_GPS_islands_daily"
        gps=root/"original_chinstrap_gps.zip"
        receipt=root/"source_daily_ice_download_receipts.json"
        if not(gps.exists() and receipt.exists()):
            self.skipTest("original BAS GPS and OSI daily NetCDF only available in dedicated Actions run")
        _,dates,frozen=m.original_source_days(gps)
        assert len(dates)==3
        v=m.valid_cell_means(m.original_source_days(gps)[0],dates,json.loads(receipt.read_text()),
                             root/"daily_original_NetCDF")
        self.assertEqual(len(v[-1]["source_three_pairs"]),3)
        self.assertTrue(v[-1]["selected_2013_published_result_matched_as_positive_control"])
if __name__=="__main__":unittest.main()
