"""Source and matched-island cohort audits for Chinstrap original GPS."""
import importlib.util,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"research/climate-penguin/work/climate_penguin"
sys.path.insert(0,str(DIR))
import signy_gps_krill_access_v1 as b
p=DIR/"south_orkney_chinstrap_island_krill_v1.py"
spec=importlib.util.spec_from_file_location("soislands",p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class IslandGPSKrillTests(unittest.TestCase):
    def test_unchanged_source_identity(self):
        self.assertEqual(m.GPS_SHA,"f56dc817aefefda41e509541d24a184f68644d12c0a1c28af8071717275101c9")
        self.assertEqual({r[0] for r in m.PAIRS},{2011,2013,2015})
        self.assertEqual(set(m.SITES),{"SI","LI","PI","MI"})
    def test_original_Powell_file_id_has_no_species_letter(self):
        self.assertEqual(m.SITES["PI"],"Powell")
        self.assertNotEqual("PI001","PIC001")
    def test_centers_are_not_krill_fitted(self):
        a=[{"island":"PI","season":2013,"points":[(None,-60.73,-45.02,0)]},
           {"island":"PI","season":2013,"points":[(None,-60.72,-45.01,0)]}]
        with self.assertRaisesRegex(ValueError,"four islands"):
            m.island_source_centers(a)
    def test_equal_mean_source(self):
        self.assertAlmostEqual(m.base.geodesic([-60.7],[-45.6],-60.7,-45.6)[0],0)
    def test_full_original_source_when_available(self):
        gps=ROOT/"build/signy_gps_source/chinstrap.zip"
        krill=ROOT/"build/freer_krill/bas_published_source.zip"
        if not gps.exists() or not krill.exists():
            self.skipTest("needs first-party BAS originals via dedicated CI")
        tr,qc=m.read_all_chinstrap(gps)
        assert qc["qc"]["empty_original_file"]==4
        assert qc["qc"]["identical_duplicate_original_file"]==1
        models=b.source_models(krill)
        origins=m.island_source_centers(tr)
        rows=m.tag_exposures(tr,origins,models)
        summ=m.aggregate(rows)
        cross=m.comparisons(summ)
        self.assertTrue(m.verify(tr,origins,summ,cross))
        self.assertEqual(len(rows),308*4)
        self.assertEqual(len(cross),3*4*2)
        self.assertEqual(set((v["island"],v["season_start"]) for v in summ),set(origins))
if __name__=="__main__":
    unittest.main()
