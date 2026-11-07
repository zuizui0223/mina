import datetime as dt,importlib.util,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"research/climate-penguin/work/climate_penguin"
sys.path.insert(0,str(DIR))
P=DIR/"chinstrap_tdr_pressure_gps_pilot_v1.py"
s=importlib.util.spec_from_file_location("tdr_pilot",P)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)
class ChinstrapDivePilotTests(unittest.TestCase):
    def test_original_pilot_ids_no_outcome_selection(self):
        self.assertEqual(m.PILOT,{"LI":"LIC001","PI":"PI001","MI":"MIC001","SI":"SIC004"})
    def test_singleten_second_event(self):
        times=np.arange(0,150,dtype=float)
        p=np.zeros(150)
        p[40:57]=7.0
        d=m.dive_candidates(times,p,5.0)
        self.assertEqual(len(d),1)
        self.assertEqual(d[0]["duration_seconds"],16)
        self.assertEqual(len(m.dive_candidates(times,p,10.0)),0)
    def test_gap_splits_dive_even_above_threshold(self):
        times=np.array([0,1,2,3,4,40,41,42,43,44],float)
        p=np.full(10,10.0)
        self.assertEqual(len(m.dive_candidates(times,p,5)),0)
    def test_original_gps_bracket_not_nearest_unbounded(self):
        epoch=dt.datetime(2015,12,1,12,0)
        gps=[(epoch+dt.timedelta(seconds=s),-60.7,-45.7) for s in (0,240,1800)]
        events=[{"peak_timestamp":(epoch+dt.timedelta(seconds=t)).timestamp()} for t in (100,1000)]
        paired,meta=m.gps_time_brackets(events,gps)
        self.assertEqual(len(paired),1)
        self.assertEqual(meta["events_total"],2)
        self.assertLessEqual(paired[0]["original_GPS_time_offset_seconds"],300)
if __name__=="__main__":
    unittest.main()
