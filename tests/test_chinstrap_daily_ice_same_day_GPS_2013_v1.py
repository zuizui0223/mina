"""All tests before real day-level ice source retrieval are source blind."""
import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
p=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_daily_ice_same_day_GPS_2013_v1.py"
s=importlib.util.spec_from_file_location("daily_same",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class SourceDailySIC(unittest.TestCase):
    def test_sources(self):
        self.assertEqual(m.DOI,"10.15770/EUM_SAF_OSI_0023")
        self.assertEqual(m.MONTHS,((2013,12),(2014,1)))
        self.assertEqual(m.RADII,(20.,35.))
    def test_original_0_ice_is_not_missing(self):
        tree=cKDTree(m.unit_xyz([-60.],[-45.]))
        grid={"values":np.array([0.]),"all_tree":tree,
              "all_ids":np.array([0]),"strict_tree":tree,"strict_ids":np.array([0])}
        self.assertEqual(m.sample(grid,[(-60.,-45.)],20,False),{0:0.})
        self.assertEqual(m.sample(grid,[(-65.,-45.)],20,False),{})
    def test_full_publishers_if_downloaded(self):
        import json
        root=ROOT/"build/daily_GPS"
        gps=root/"original_Chinstrap_GPS.zip"
        source=root/"source_daily_NetCDF_SHA_receipts.json"
        if not gps.exists() or not source.exists():
            self.skipTest("Original publisher GPS and real daily NetCDF only in workflow")
        tags,days,_=m.positions(gps)
        u,v,p,res=m.evaluate(tags,days,json.loads(source.read_text()),
                              root/"daily_original_NetCDF")
        self.assertEqual(res["n_original_shared_GPS_days_before_SIC"],len(days))
        self.assertGreater(res["n_SI_PI_comparable_daily_SIC_dates"],0)
if __name__=="__main__":unittest.main()
