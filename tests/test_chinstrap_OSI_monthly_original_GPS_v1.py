import sys,importlib.util,unittest
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
p=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_OSI_monthly_original_GPS_v1.py"
spec=importlib.util.spec_from_file_location("penguin_osi",p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SourceSIC(unittest.TestCase):
    def test_source_product_DOI_and_month_radius(self):
        self.assertEqual(m.DOI,"10.15770/EUM_SAF_OSI_0023")
        self.assertEqual(m.RADII,(20.,35.))
    def test_original_lat_lon_ecef(self):
        self.assertTrue(np.allclose(m.xyz([0,0,90],[0,90,0]),np.eye(3)))
    def test_coast_missing_is_not_ice_zero(self):
        t=m.xyz([-60],[-45])
        src={"sic":np.array([0.]),"flags":np.array([0]),
             "all_tree":cKDTree(t),"all_idx":np.array([0]),
             "strict_tree":cKDTree(t),"strict_idx":np.array([0])}
        self.assertEqual(m.match_month(src,[-60],[-45],20,False)[0][0],0.0)
        self.assertIsNone(m.match_month(src,[-64],[-45],20,False)[0][0])
        self.assertIsNone(m.match_month(src,[-64],[-45],20,False)[0][3])
        self.assertEqual(m.match_month(src,[-60],[-45],20,False)[0][3],0)
    def test_original_in_environment(self):
        root=ROOT/"build/observed_ice_GPS"
        gps=root/"gps.zip";proof=root/"satellite_original_receipts.json"
        if not gps.exists() or not proof.exists():self.skipTest("first-party source NetCDF unavailable in local unit context")
        import json
        result=m.analyze(gps,root/"original_OSI_monthly",json.loads(proof.read_text()))
        self.assertEqual(result[3]["n_original_source_GPS_tracks"],308)
        self.assertEqual(result[3]["n_GPS_qualified_tracks"],253)
if __name__=="__main__":unittest.main()
