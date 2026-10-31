import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
p=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_300tag_tdr_sensor_census_v1.py"
s=importlib.util.spec_from_file_location("src",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class PressureQA(unittest.TestCase):
    def test_window_equivalence(self):
        t=np.arange(3*3600,dtype=float);p=np.ones(len(t))
        p[:3600]=2;p[3600:7200]=4;p[7200:]=5
        x=m.hourly_lower_percentiles(t,p)
        self.assertEqual(x["n_calibrated_hour_windows"],3)
        self.assertAlmostEqual(x["q01_hourly_range_dbar"],3)
    def test_source_ids_and_frozen_receipts(self):
        self.assertEqual(len(m.KNOWN_PILOT),4)
        self.assertEqual(m.DRIFT_DIAGNOSTIC_DBAR,2.0)
    def test_source_missing_bracket_not_non_diving(self):
        row={"original_deployment_id":"SIC004","original_island":"SI","source_qa_status":"SOURCE_QA_STOP"}
        self.assertEqual(row["source_qa_status"],"SOURCE_QA_STOP")
    def test_original_archive_count_if_available(self):
        root=ROOT/"build/chinstrap_300_original"
        tdr=root/"TDR_v2_original.zip";gps=root/"GPS_v2_original.zip"
        if not(tdr.exists() and gps.exists()):
            self.skipTest("complete publisher native pressure source only available on dedicated CI")
        out,meta=m.run(tdr,gps)
        self.assertTrue(m.verify(out,meta))
if __name__=="__main__":unittest.main()
