"""All fixed-source footprint contracts; no exposure result chosen to fit sign."""
import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
P=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_OSI_daily_fixed_native_cells_v1.py"
s=importlib.util.spec_from_file_location("fixed_ice",P)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class FixedNativeSatellitePixels(unittest.TestCase):
    def test_sources_footprints(self):
        self.assertEqual(m.PHASES,("all_14_source_GPS_days","Dec_2013_source_GPS_only",
                                   "Jan_2014_source_GPS_only"))
        self.assertEqual(m.SOURCE_DAY_N,14)
        self.assertEqual(m.ISLANDS,("SI","PI"))
    def test_full_native_source_replay(self):
        root=ROOT/"build/daily_GPS"
        receipt=root/"source_daily_NetCDF_SHA_receipts.json"
        obs=root/"daily_GPS_tag_original_SIC.csv"
        if not receipt.exists() or not obs.exists():
            self.skipTest("requires original daily satellite and GPS source in CI")
        import json
        a,b,c,d=m.baseline(m.read_csv(obs),json.loads(receipt.read_text()),
                           root/"daily_original_NetCDF")
        self.assertEqual(len(a),84)
        self.assertEqual(len(b),42)
        self.assertTrue(d["no_daily_ice_navigability_or_causal_breeding_response_tested"])
        expected={
            "all_14_source_GPS_days":(10.97786900584795,2.6582947368421053,25,57),
            "Dec_2013_source_GPS_only":(11.594778325123151,1.082872816838334,14,29),
            "Jan_2014_source_GPS_only":(11.051169444444444,2.482710606060606,25,48)
        }
        for key,(dec,jan,nSI,nPI) in expected.items():
            val=d["fixed_footprint_analysis"][key]
            self.assertAlmostEqual(val["December_Signy_minus_Powell_pp"],dec,places=7)
            self.assertAlmostEqual(val["January_Signy_minus_Powell_pp"],jan,places=7)
            self.assertEqual((val["Signy_original_fixed_cells"],val["Powell_original_fixed_cells"]),
                             (nSI,nPI))

if __name__=="__main__":unittest.main()
