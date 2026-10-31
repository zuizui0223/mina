import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/south_orkney_krill_source_reconcile_v2.py"
spec=importlib.util.spec_from_file_location("skaret_reconcile",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class SourceReconcileTests(unittest.TestCase):
    def test_combined_2013_unavailable(self):
        a,b=m.sources()
        self.assertNotIn(("Combined",2013),a)
        self.assertIn(("North",2013),a)
        self.assertEqual(sum(z["year_value_conflict"] for z in b),8)
    def test_correct_2014_and_2018_values(self):
        a,_=m.sources()
        self.assertEqual(a["Combined",2014]["density"],76.5)
        self.assertEqual(a["Combined",2018]["density"],69.4)
    def test_primary_source_comparison_requires_stage(self):
        d=m.ROOT/"build/signy_stage_derived"
        if not d.exists():self.skipTest("original BAS stage ZIP reconstruction only available in dedicated workflow")
        rec,conflicts=m.sources()
        stage=m.stage(d/"species_annual_stage_summary.csv",d/"source_stage_site_seasons.csv")
        r=m.compare(rec,m.OLD,stage)
        self.assertTrue(m.numeric_check(r,conflicts))
        self.assertEqual(len(stage),27)
        self.assertEqual(len(r),45)
        self.assertEqual(next(z["n_years"] for z in r if z["exposure"]=="Skaret_combined" and z["cohort"]=="all_available"),8)
        self.assertEqual(next(z["n_years"] for z in r if z["exposure"]=="Skaret_combined" and z["cohort"]=="comparable_complete"),7)
if __name__=="__main__":
    unittest.main()
