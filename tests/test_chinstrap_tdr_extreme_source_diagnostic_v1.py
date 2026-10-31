import importlib.util,sys,unittest,datetime as dt
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"research/climate-penguin/work/climate_penguin"))
p=R/"research/climate-penguin/work/climate_penguin/chinstrap_tdr_extreme_source_diagnostic_v1.py"
s=importlib.util.spec_from_file_location("ext",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ExtremeSourceTests(unittest.TestCase):
    def test_frozen_source_selected_after_outcomes(self):
        self.assertEqual(set(m.SOURCE_TAGS),{"PI011","PI054","SIC033","SIC036","SIC039","PI009"})
    def test_mixed_same_second_pressure_detected(self):
        t=dt.datetime.fromisoformat("2013-12-01T12:00:00")
        r=m.within_timestamp_source([(t,1.0),(t,2.0),(t,2.0)])
        self.assertEqual(r["same_timestamp_extra_records"],2)
        self.assertEqual(r["same_timestamp_different_pressure_from_first"],2)
    def test_hourly_quantile_synthetic(self):
        t=np.arange(4*3600,dtype=float)
        a=np.r_[np.ones(3600),np.full(3600,5),np.full(3600,40),np.full(3600,110)]
        q=m.hourly_original_range(t,a)
        self.assertAlmostEqual(q["hourly_q01_baseline_range_dbar"],109.0)
        self.assertEqual(q["source_hours_q01_above_50dbar"],1)
if __name__=="__main__":unittest.main()
