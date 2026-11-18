"""Daily source satellite SIC directional selection, no capture or access claim."""
import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
P=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_daily_GPS_ice_radial_direction_v1.py"
spec=importlib.util.spec_from_file_location("radialice",P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class NativeRadialDailySIC(unittest.TestCase):
    def test_constant_satellite_field_has_zero_selection(self):
        # 4 native ocean cells around -60,-45, at multiple distances.
        la=np.array([-60.1,-60.2,-60.3,-60.4,-60.5])
        lo=np.array([-45.,-45.,-45.,-45.,-45.])
        vals=np.array([20.,20.,20.,20.,20.])
        r,idx,n=m.ring_means(vals,np.arange(5),la,lo,(-60.,-45.))
        s=m.source_pixel_excess({0:20.,2:20.},idx,r)
        self.assertEqual(s["n_matched_native_source_pixels"],2)
        self.assertAlmostEqual(s["GPS_minus_radial_source_SIC_pp"],0.)
    def test_same_radius_high_SIC_measured_not_navigation(self):
        obs={0:0.,1:40.}
        idx={0:2,1:2,2:2}
        means={2:30.}
        s=m.source_pixel_excess(obs,idx,means)
        self.assertEqual(s["GPS_minus_radial_source_SIC_pp"],-10.)
        self.assertEqual(s["source_GPS_cells_SIC_ge15_fraction"],.5)
    def test_source_missing_ocean_cell_never_recoded_ice_free(self):
        z=m.source_pixel_excess({1:0.,2:80.},{1:1},{1:20.})
        self.assertEqual(z["n_native_pixels_not_in_175km_source_background"],1)
        self.assertAlmostEqual(z["GPS_minus_radial_source_SIC_pp"],-20.)
    def test_empty_source_outcomes_do_not_pass_numeric_receipt(self):
        with self.assertRaisesRegex(ValueError,"time support changed"):
            m.verify_original_45_day_radius_SIC_receipts([],[],[],[])
    def test_original_BAS_and_OSI_if_in_source_workflow(self):
        root=ROOT/"build/daily_GPS_radial"
        gps=root/"gps_original.zip"
        receipt=root/"publisher_original_SIC_daily_receipts.json"
        if not(gps.exists() and receipt.exists()):
            self.skipTest("Publisher original GPS and 45 daily satellite NetCDF required")
        import json
        out=m.run(gps,root/"original_OSI_daily",json.loads(receipt.read_text()))
        self.assertEqual(out[-1]["original_SIC_n_days"],45)
        self.assertEqual(out[-1]["n_daily_island_comparisons"],45*4)
if __name__=="__main__":unittest.main()
