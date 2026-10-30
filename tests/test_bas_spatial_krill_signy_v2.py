import importlib.util, unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"research/climate-penguin/work/climate_penguin/bas_spatial_krill_signy_v2.py"
spec=importlib.util.spec_from_file_location("signyspatial",path)
x=importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)

class SourceSpatialTests(unittest.TestCase):
    def test_native_anchor_from_original_GPS(self):
        a=x.anchor()
        self.assertTrue(-60.75<a["lat"]<-60.67)
        self.assertTrue(-45.70<a["lon"]<-45.55)
        self.assertIn("NOT_foraging_site",a["source"])
    def test_geodesic(self):
        d=x.distance_km(-60.7,-45.6,np.array([-60.7,-59.7]),np.array([-45.6,-45.6]))
        self.assertAlmostEqual(float(d[0]),0.0)
        self.assertTrue(110<float(d[1])<113)
    def test_source_input_years(self):
        self.assertEqual(x.YEARS,tuple(range(2011,2021)))
        self.assertEqual(len(x.BANDS),3)
        self.assertEqual(len(x.PRODUCTS),3)
    def test_source_file_digest_guard(self):
        self.assertEqual(x.EXPECTED_MODEL_PAYLOAD_SHA,"f4fffbc2b0cbe2dffc5a5728c81f1b46ba9ff99988c6589bb3515d38d2a2fead")
    def test_full_original_data_only_in_actions(self):
        p=ROOT/"build/bas_spatial_krill/source.zip"
        stage=ROOT/"build/signy_stage_derived"
        if not p.exists() or not stage.exists():
            self.skipTest("requires original BAS archives")
        rows,_,_,grid=x.extract(p)
        self.assertEqual(len(rows),90)
        self.assertAlmostEqual(grid["grid_resolution_deg"],1/12,places=9)
        out=x.analyze(rows,stage)
        self.assertEqual(out["combined"]["0-50"]["all"]["n"],9)
        self.assertEqual(out["combined"]["0-50"]["complete"]["n"],7)
        self.assertEqual(out["combined"]["0-50"]["complete_minus_2012"]["n"],6)

if __name__=="__main__":unittest.main()
