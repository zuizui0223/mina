import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"research/climate-penguin/work/climate_penguin"
sys.path.insert(0,str(DIR))
P=DIR/"chinstrap_tdr_zoc_sensitivity_v2.py"
spec=importlib.util.spec_from_file_location("zoc_v2",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class PilotOffsetTests(unittest.TestCase):
    def test_constant_baseline_exact(self):
        t=np.arange(0,100,dtype=float)
        p=np.concatenate([np.zeros(80),np.full(20,20.0)])
        x,meta=m.offset_method(t,p,None,1,None)
        self.assertAlmostEqual(float(x[90]),20.0)
        self.assertEqual(meta["baseline_range_dbar"],0)
    def test_source_methods_frozen(self):
        self.assertEqual([z[0] for z in m.METHODS],["q1_60min","q1_30min","q5_60min","global_q1"])
        self.assertEqual(m.THRESHOLDS,(2,5,10))
    def test_hour_window_sensitivity_on_synthetic_drift(self):
        t=np.arange(0,4*3600,dtype=float)
        p=np.zeros_like(t)
        p[t>=2*3600]+=3.0
        a,meta=m.offset_method(t,p,3600,1,300)
        self.assertAlmostEqual(meta["baseline_range_dbar"],3)
        self.assertAlmostEqual(float(np.median(a)),0,places=4)
    def test_original_archive_source_receipt_when_available(self):
        root=ROOT/"build/chinstrap_original_pilot"
        if not(root/"TDR.zip").exists() or not(root/"GPS.zip").exists():
            self.skipTest("original BAS v2 downloads only in source workflow")
        rows=m.run(root/"TDR.zip",root/"GPS.zip")
        self.assertTrue(m.receipt(rows))
        self.assertEqual(len(rows),48)
        self.assertTrue(m.summarize(rows)[2]["large_local_drift_flag_2dbar"])
if __name__=="__main__":
    unittest.main()
