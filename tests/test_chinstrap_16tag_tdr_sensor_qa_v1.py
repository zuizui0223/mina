import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
path=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_16tag_tdr_sensor_qa_v1.py"
spec=importlib.util.spec_from_file_location("tag_qa",path)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class SixteenTDRQA(unittest.TestCase):
    def test_original_roster_fixed(self):
        self.assertEqual(len(m.choose()),16)
        self.assertEqual(m.SOURCE_TAGS["PI"],("PI001","PI002","PI003","PI004"))
        self.assertEqual(m.SOURCE_TAGS["SI"],("SIC004","SIC008","SIC009","SIC010"))
    def test_known_four_pilot_preserved(self):
        self.assertEqual(m.EXPECTED_PILOT["MIC001"],(1369,876))
        self.assertEqual(len(m.zoc.METHODS),4)
        self.assertEqual(m.THRESHOLD_DBAR,5.0)
    def test_no_cherrypick_survivors(self):
        self.assertTrue(all(isinstance(a,str) for _,a in m.choose()))
        self.assertEqual(m.DRIFT_FLAG_DBAR,2.0)
    def test_real_original_files_if_available(self):
        root=ROOT/"build/chinstrap_tdr_original"
        tdr=root/"TDR_v2_original.zip"
        gps=root/"GPS_v2_original.zip"
        if not(tdr.exists() and gps.exists()):
            self.skipTest("First-party original publisher archives required")
        out=m.execute(tdr,gps)
        summary=m.summarize(out)
        self.assertTrue(m.verify(out,summary))
        self.assertEqual(len(out),64)
if __name__=="__main__":unittest.main()
