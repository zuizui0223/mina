import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/freer_krill_raster_source_v1.py"
spec=importlib.util.spec_from_file_location("freer_krill",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class FreerSourceTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(m.classify("annual_krill_rasters/2011_combined_mean.tif"),(2011,"combined","mean"))
        self.assertEqual(m.classify("annual_krill_rasters/2012_gam_binom_mean.tif"),(2012,"binom","mean"))
        self.assertEqual(m.classify("annual_krill_rasters/2017_combined_sd.tif"),(2017,"combined","sd"))
    def test_no_unsupported_component(self):
        self.assertEqual(m.classify("krill_decade_combined_decademean.tif"),(None,"combined","mean"))
    def test_all_years(self):
        self.assertEqual(m.EXPECTED,set(range(2011,2021)))
if __name__=="__main__":
    unittest.main()
