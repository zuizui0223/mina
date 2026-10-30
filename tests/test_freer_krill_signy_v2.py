import importlib.util
import math
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/freer_krill_signy_v2.py"
spec=importlib.util.spec_from_file_location("freer_signy",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class FreerSignyTests(unittest.TestCase):
    def test_gps_midpoint(self):
        a,b=m.gps_anchor()
        self.assertAlmostEqual(a,-60.704025,places=6)
        self.assertAlmostEqual(b,-45.6275835,places=6)
    def test_distance(self):
        a,b=m.gps_anchor()
        self.assertAlmostEqual(float(m.great_circle(a,b,a,b)),0,places=8)
        self.assertGreater(float(m.great_circle(a+0.5,b,a,b)),50)
    def test_rank_ties(self):
        self.assertEqual(m.ranks([10,10,9]),[2.5,2.5,1])
    def test_source_pin_count(self):
        import json
        d=json.loads(m.PINS.read_text(encoding="utf-8"))
        self.assertEqual(len(d),10)
    def test_source_stage_and_all_54_associations(self):
        root=Path(__file__).resolve().parents[1]
        source=root/"build/freer_krill/bas_published_source.zip"
        stage=root/"build/signy_stage_derived"
        if not source.exists() or not stage.exists():
            self.skipTest("original BAS source ZIP only available in dedicated workflow")
        spatial,comparison,acoustic,meta=m.run(source,stage)
        self.assertTrue(m.check(spatial,comparison,meta))
        self.assertEqual(len(acoustic),3)
        self.assertEqual(len({z["breeding_years"] for z in comparison if z["cohort"]=="all"}),2)
if __name__=="__main__":
    unittest.main()
