"""Source identity and exact two-part GAM source-component arithmetic."""
import unittest,importlib.util,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
P=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_GAM_hurdle_components_GPS_v1.py"
s=importlib.util.spec_from_file_location("hurdle_geo",P)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class HurdleSource(unittest.TestCase):
    def test_exact_log_partition_without_interaction(self):
        a={"prob":.4,"density_positive":6.,"combined":2.4}
        b={"prob":.2,"density_positive":3.,"combined":.6}
        r=m.partition(a,b)
        self.assertAlmostEqual(r["log_combined_GAM_visited_over_background"],math.log(4))
        self.assertAlmostEqual(r["log_occurrence_probability_ratio"],math.log(2))
        self.assertAlmostEqual(r["log_conditional_positive_density_ratio"],math.log(2))
        self.assertAlmostEqual(r["log_aggregation_interaction_residual"],0)
    def test_nonzero_interaction_not_silently_omitted(self):
        a={"prob":.5,"density_positive":4.,"combined":2.8}
        b={"prob":.6,"density_positive":3.,"combined":1.5}
        r=m.partition(a,b)
        self.assertNotAlmostEqual(r["log_aggregation_interaction_residual"],0)
        self.assertAlmostEqual(r["log_combined_GAM_visited_over_background"],
            sum(r[k] for k in ("log_occurrence_probability_ratio",
               "log_conditional_positive_density_ratio",
               "log_aggregation_interaction_residual")))
    def test_zero_is_not_patched_with_pseudocount(self):
        with self.assertRaises(ValueError):
            m.partition({"prob":0,"density_positive":1,"combined":1},
                        {"prob":.5,"density_positive":2,"combined":1})
    def test_original_bas_raster_source_if_available(self):
        root=ROOT/"build/GAM_component_source"
        gps=root/"gps-original.zip"
        model=root/"krill-original.zip"
        if not(gps.exists() and model.exists()):
            self.skipTest("source GPS and Freer model TIFF original ZIP required")
        tags,annual,pairs,gate=m.run(gps,model)
        self.assertEqual((len(tags),len(annual),len(pairs)),(308,14,6))
        self.assertTrue(all(p["mathematical_log_decomposition_exact"] for p in pairs))
if __name__=="__main__":unittest.main()
