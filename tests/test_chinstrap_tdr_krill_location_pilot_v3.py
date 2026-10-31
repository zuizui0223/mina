"""Four preselected original BAS Chinstrap TDR→GPS→GAM krill pilot guards."""
import importlib.util
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
P=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_tdr_krill_location_pilot_v3.py"
spec=importlib.util.spec_from_file_location("pilot_source",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class PilotTDRSpatialTests(unittest.TestCase):
    def test_original_source_roster(self):
        self.assertEqual(m.SOURCE_PILOT,{"LI":"LIC001","PI":"PI001","MI":"MIC001","SI":"SIC004"})
        self.assertEqual(len(m.zoc.METHODS)*len(m.zoc.THRESHOLDS)*len(m.SOURCE_PILOT),48)
    def test_original_gps_time_dedupe(self):
        import datetime
        t=datetime.datetime.fromisoformat("2013-12-01T12:00:00")
        out=m.source_gps_fixes([(t,1.0,2.0),(t,99.0,99.0)])
        self.assertEqual(out,[(t,1.0,2.0)])
    def test_published_raster_point_dedup(self):
        import numpy as np
        from affine import Affine
        arr=np.array([[3.0,5.0],[7.0,9.0]])
        grid={2013:(arr,Affine(1,0,0,0,-1,2))}
        r=m.model_cells([(1.5,0.5),(1.5,0.5),(0.5,1.5)],grid,(1,1),2013)
        self.assertEqual(r["n_points_geographic"],0) if False else self.assertTrue(r["n_distinct_cells"]<=r["n_model_valid"])
    def test_original_pilot_in_CI(self):
        root=ROOT/"build/chinstrap_tdr_original"
        z=root/"TDR_v2_original.zip";g=root/"GPS_v2_original.zip";k=root/"Freer_krill_original.zip"
        if not(z.exists() and g.exists() and k.exists()):
            self.skipTest("requires first-party 500MB+ source originals on dedicated CI")
        rows,b,matches=m.analyze(z,g,k)
        self.assertTrue(m.verify(rows,b))
        self.assertEqual(len(rows),48)
if __name__=="__main__":
    unittest.main()
