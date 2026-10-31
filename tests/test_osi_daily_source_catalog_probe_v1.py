import sys,importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"research/climate-penguin/work/climate_penguin/osi_daily_source_catalog_probe_v1.py"
s=importlib.util.spec_from_file_location("daily",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class DailySourceProbe(unittest.TestCase):
    def test_accepted_product_and_date_fixed(self):
        self.assertEqual(m.DOI,"10.15770/EUM_SAF_OSI_0023")
        self.assertEqual(m.TARGETS,("20131215","20140115"))
    def test_original_year_filename(self):
        rows=[
            {"url_path":"osisaf/met.no/reprocessed/ice/conc_450a1_files/daily/2013/ice_conc_sh_ease2-250_cdr-v3p1_201312151200.nc"},
            {"url_path":"osisaf/met.no/reprocessed/ice/conc_450a1_files/daily/2014/ice_conc_sh_ease2-250_cdr-v3p1_201401151200.nc"}]
        self.assertEqual(set(m.pick_datasets(rows)),set(m.TARGETS))
    def test_no_cross_publisher_url(self):
        with self.assertRaisesRegex(ValueError,"nonpublisher"):
            m.fetch("https://evil.example.org/source")
if __name__=="__main__":unittest.main()
