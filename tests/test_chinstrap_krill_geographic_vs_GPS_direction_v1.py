"""Geographic and distance-matched source null unit checks."""
import sys,importlib.util,math,unittest
from pathlib import Path
import numpy as np
from affine import Affine
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
P=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_krill_geographic_vs_GPS_direction_v1.py"
spec=importlib.util.spec_from_file_location("geogeometry",P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class GeoKrilTest(unittest.TestCase):
    def test_constant_GAM_null_source_selection_one(self):
        arr=np.full((241,241),5.0)
        tr=Affine(1/12,0,-55,0,-1/12,-50)
        # Anchor centered on source native raster extent; all model valid
        v,rings,bins=m.grid_reference(arr,tr,-60.,-45.)
        self.assertAlmostEqual(v["geographic_baseline"],5.)
        self.assertTrue(all(math.isclose(x,5.) for x in rings.values()))
        self.assertGreater(v["n_model_valid_geographic_cells"],20)
    def test_GPS_native_visit_cells_respects_original_hour_criterion(self):
        source={"points":[(__import__("datetime").datetime(2013,12,1,0,0),-60.8,-45.8,0)]}
        centre={"center_lat":-60.7,"center_lon":-45.7}
        a,tr=np.full((241,241),2.0),Affine(1/12,0,-55,0,-1/12,-50)
        hours,cells=m.source_selected_unique_cells(source,centre,a,tr)
        self.assertEqual(hours,1)
        self.assertIsNone(cells)
    def test_public_originals_available_only_in_source_replay(self):
        root=ROOT/"build/source_geo"
        gps=root/"gps-original.zip"
        model=root/"krill-original.zip"
        if not gps.exists() or not model.exists():
            self.skipTest("original published GPS and krill TIFF need source-replay CI")
        tracks,annual,contrast,_=m.run(gps,model)
        self.assertEqual(len(tracks),308)
        self.assertEqual(len(annual),14)
        self.assertEqual(len(contrast),6)
        self.assertTrue(all(math.isclose(r["other_div_Signy_GPS_visited_model_ratio"]/
                        r["other_div_Signy_distance_matched_GAM_reference_ratio"],
                        r["other_div_Signy_GPS_use_after_radial_background_ratio"],abs_tol=1e-10)
                        for r in contrast))
if __name__=="__main__":
    unittest.main()
