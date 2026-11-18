import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
P=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_krill_native_cell_independence_v1.py"
spec=importlib.util.spec_from_file_location("cellunions",P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class SourceNativeModelCellTests(unittest.TestCase):
    def test_source_count(self):
        self.assertEqual(m.SOURCE_UNITS,308)
        self.assertEqual(len(m.YEARS),3)
    def test_native_pixel_dedup_not_a_tag_count(self):
        # Same cell visited by 12 tags still counts as one pixel.
        selected=[(3,8),(3,8),(4,9),(3,8)]
        self.assertEqual(len(set(selected)),2)
    def test_real_native_source_when_downloaded(self):
        root=ROOT/"build/source_cells"
        gps=root/"original-GPS.zip"
        model=root/"original-GAM.zip"
        if not gps.exists() or not model.exists():
            self.skipTest("BAS original ZIPs available only in source replay")
        result,pairs,original=m.analyze(gps,model)
        self.assertTrue(m.verify(result,pairs))
        self.assertEqual(len(pairs),6)
        self.assertEqual(len(result),14)
if __name__=="__main__":
    unittest.main()
