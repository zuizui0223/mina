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
        tags,annual,pairs,gate,pixel_annual,pixel_pairs=m.run(gps,model)
        self.assertEqual((len(tags),len(annual),len(pairs)),(308,14,6))
        self.assertEqual((len(pixel_annual),len(pixel_pairs)),(14,6))
        self.assertTrue(all(math.isclose(
           sum(r["other_minus_Signy_"+x] for x in (
               "log_occurrence_probability_ratio",
               "log_conditional_positive_density_ratio",
               "log_aggregation_interaction_residual")),
           math.log(r["combined_radial_adjusted_ratio"]),abs_tol=1e-10)
           for r in pixel_pairs))
        self.assertTrue(all(p["mathematical_log_decomposition_exact"] for p in pairs))
        expectations={
            (2011,"LI"):(1.0787113024024448,1.585105793986495),
            (2013,"PI"):(1.4839679857040118,2.777961578471998),
            (2015,"MI"):(1.0499003314311552,2.8998008868270224)}
        independent_pixel={
            (2011,"LI"):(1.1842891836437592,1.4161181880924871),
            (2013,"PI"):(1.7159220936127033,2.7080514566652845),
            (2015,"MI"):(1.0035443087789429,3.275944845264624)}
        for rows,expected in ((pairs,expectations),(pixel_pairs,independent_pixel)):
            for row in rows:
                if row["model_period"]!="preseason":continue
                a,b=expected[row["season_start"],row["other_island"]]
                self.assertTrue(math.isclose(row["prob_radial_adjusted_ratio"],a,abs_tol=1e-10))
                self.assertTrue(math.isclose(row["density_positive_radial_adjusted_ratio"],b,abs_tol=1e-10))

if __name__=="__main__":unittest.main()
