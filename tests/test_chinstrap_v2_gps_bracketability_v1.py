import importlib.util,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/chinstrap_v2_gps_bracketability_v1.py"
s=importlib.util.spec_from_file_location("gap_gate",P)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

class GPSGapGateTests(unittest.TestCase):
    def test_elapsed_time_not_gap_count(self):
        a=m.summarize({("SI",2015):[[240.0,240.0,3600.0]]})[0]
        self.assertAlmostEqual(a["fraction_intervals_le_600s"],2/3)
        self.assertAlmostEqual(a["fraction_record_span_in_bracket_le_600s"],480/4080)
        self.assertGreater(a["fraction_intervals_le_600s"],a["fraction_record_span_in_bracket_le_600s"])
    def test_original_source_receipt(self):
        self.assertEqual(m.EXPECTED_PIN,"f56dc817aefefda41e509541d24a184f68644d12c0a1c28af8071717275101c9")
        self.assertEqual(len(m.SITES),4)
    def test_long_gap_is_not_interpolated(self):
        a=m.summarize({("LI",2011):[[120.0,120.0,7200.0]]})[0]
        self.assertLess(a["fraction_record_span_in_bracket_le_600s"],0.1)
if __name__=="__main__":
    unittest.main()
