"""OSI-SAF low-SIC graph is a hypothetical source-native geometry only."""
import sys,importlib.util,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
P=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_daily_ice_graph_connectivity_v1.py"
spec=importlib.util.spec_from_file_location("icegraph",P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class GraphTest(unittest.TestCase):
    def test_four_vs_eight_connectivity_diagonal(self):
        v=np.array([[0.,100.,100.],[100.,0.,100.],[100.,100.,0.]])
        indices=np.arange(9)
        four,ff,_=m.graph_labels(v,indices,15.0,4,(3,3))
        eight,ef,_=m.graph_labels(v,indices,15.0,8,(3,3))
        self.assertNotEqual(four[0],four[4])
        self.assertEqual(eight[0],eight[4])
        self.assertEqual(eight[0],eight[8])
        self.assertFalse(ef[1])
    def test_explicit_no_ice_free_coastal_seed(self):
        v=np.array([100.,100.,100.,0.,0.,100.,100.,100.,100.])
        lab,eligible,_=m.graph_labels(v,np.arange(9),15.0,4,(3,3))
        seed,n=m.select_coast_seed(lab,eligible,[0,1,2,60,70,3,4,5,6],35.)
        self.assertIsNone(seed)
        self.assertEqual(n,0)
        score=m.diagnostic({3:0.,4:0.},v,lab,eligible,
                           np.array([0,1,2,60,70,3,4,5,6],dtype=float),seed)
        self.assertIsNone(score["fraction_visited_in_binary_low_SIC_connected_component"])
        self.assertIsNone(score["n_original_GPS_cells_below_threshold_connected_to_seed"])
        good,n=m.select_coast_seed(lab,eligible,[0,1,2,60,70,3,4,5,6],70.)
        self.assertEqual(good,3)
        self.assertEqual(n,2)
    def test_valid_satellite_zero_ice_is_not_missing(self):
        v=np.array([0.,0.,20.,40.])
        lab,open_mask,_=m.graph_labels(v,np.arange(4),15.0,4,(2,2))
        s=m.diagnostic({0:0.,2:20.},v,lab,open_mask,np.array([10.,20.,30.,40.]),0)
        self.assertEqual(s["n_original_GPS_cells_below_SIC_threshold"],1)
        self.assertEqual(s["n_original_GPS_cells_meeting_or_exceeding_SIC_threshold"],1)
        self.assertEqual(s["n_original_GPS_cells_below_threshold_connected_to_seed"],1)
    def test_empty_source_count_does_not_fake_route_obstruction(self):
        with self.assertRaisesRegex(ValueError,"4320 original source"):
            m.verify_source_graph_receipts([],[])
    def test_full_original_source_if_present(self):
        root=ROOT/"build/chinstrap_ice_graph_original"
        gps=root/"BAS_GPS.zip"
        receipt=root/"original_daily_ice_SHA_receipts.json"
        if not gps.exists() or not receipt.exists():
            self.skipTest("requires original publisher 45 day ice and GPS source files")
        import json
        a,b,c,gate=m.run(gps,root/"original_daily_SIC_NetCDF",json.loads(receipt.read_text()))
        self.assertEqual(gate["n_source_original_daily_NetCDF"],45)
        self.assertEqual(len(b),45*3*2*2*2*2)
        self.assertEqual(gate["original_publisher_source_numeric_receipts"]["original_pixel_days_SIC_ge30"],0)
if __name__=="__main__":
    unittest.main()
