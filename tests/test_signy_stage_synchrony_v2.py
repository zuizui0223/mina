"""Source/falsification tests; run after publisher-original stage intake."""
import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
mod_path=ROOT/"research/climate-penguin/work/climate_penguin/signy_stage_synchrony_v2.py"
spec=importlib.util.spec_from_file_location("signy_stage_v2",mod_path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
DERIVED=ROOT/"build/signy_stage_derived"

class SignyStageSynchronyTests(unittest.TestCase):
    def test_known_source_three_species(self):
        result=mod.analyze(mod.read_csv(DERIVED/"species_annual_stage_summary.csv"),mod.read_csv(DERIVED/"source_stage_site_seasons.csv"))
        self.assertEqual(len(result["common_years"]),22)
        self.assertEqual(result["n_consecutive_transitions"],19)
        self.assertEqual(result["all_species_same_direction_year_changes"],12)
        for pair,expected in [
            ("Adelie|Chinstrap",0.794364142838016),
            ("Adelie|Gentoo",0.702585668658692),
            ("Chinstrap|Gentoo",0.7382168266825719)
        ]:
            self.assertTrue(math.isclose(result["source_median_pair_correlations"][pair],expected,abs_tol=1e-10))

    def test_no_cross_gap_interpolation(self):
        years=list(mod.EXPECTED_YEARS)
        x={y:{s:float(y) for s in mod.SPECIES} for y in years}
        diffs=mod.differences(x,years)
        self.assertEqual([r["year"] for r in diffs],list(mod.EXPECTED_TRANSITIONS))
        self.assertNotIn(1998,[r["year"] for r in diffs])
        self.assertNotIn(2011,[r["year"] for r in diffs])

    def test_source_pin(self):
        self.assertEqual(mod.SOURCE_PINS["Gentoo"],"53fe3821f313ed35840376fcf4d11c8e0e8fbbd63f01ba84a5e21c2db4df6d6b")

    def test_exact_group_offsets(self):
        z=[{"year":y,**{s:float(i) for s in mod.SPECIES}} for i,y in enumerate(mod.EXPECTED_TRANSITIONS)]
        self.assertEqual(mod.grouped_rotate(z,"Adelie",0,0),[float(i) for i in range(19)])
        self.assertEqual(len(mod.grouped_rotate(z,"Gentoo",1,1)),19)

    def test_source_flags_prevent_pseudoreplication(self):
        rows=mod.read_csv(DERIVED/"source_stage_site_seasons.csv")
        a=mod.read_csv(DERIVED/"species_annual_stage_summary.csv")
        years=mod.analyze(a,rows)
        self.assertEqual(years["strict_ordered_fledgling_pair_rows"],392)
        self.assertEqual(years["source_rows"],463)
        self.assertEqual(years["phase_group_diagnostic"]["comparison_count"],7744)
        self.assertTrue(0<years["phase_group_diagnostic"]["upper_fraction_including_identity"]<=1)
        self.assertLess(years["ratio_le_2_pair_correlations"]["Adelie|Chinstrap"],1.0)


if __name__=="__main__":
    unittest.main()
