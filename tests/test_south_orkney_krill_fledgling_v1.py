"""Source and calendar tests for published South Orkney acoustic biomass."""
import csv
import importlib.util
import json
import math
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"research/climate-penguin/work/climate_penguin/south_orkney_krill_fledgling_v1.py"
spec=importlib.util.spec_from_file_location("south_orkney_krill",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class AcousticStageTests(unittest.TestCase):
    def test_published_acoustic_number_domain(self):
        source=m.acoustic()
        self.assertEqual(len(source),10)
        self.assertAlmostEqual(source[2012]["density"],128.8)
        self.assertAlmostEqual(source[2016]["biomass"],1.40)
        self.assertFalse(source[2013]["full_coverage"])
        self.assertFalse(source[2015]["full_coverage"])

    def test_ties_ranks(self):
        self.assertEqual(m.ranks([1.0,2.0,1.0]),[1.5,3.0,1.5])

    def test_no_false_climate_replication(self):
        v=m.acoustic()
        stage={(species,y):1+(y-2011)/100 for species in m.SPECIES for y in m.YEARS}
        counts={(species,y):1 for species in m.SPECIES for y in m.YEARS}
        out=m.analysis(v,stage,counts,0,"all")
        self.assertEqual(out["n_independent_calendar_year_opportunities"],9)
        self.assertEqual(len(out["species"]),3)
        self.assertEqual(out["survey_years_with_incomplete_source_coverage"],[2013,2015])

    def test_original_source_stage_date_order(self):
        path=ROOT/"build/signy_stage_derived"
        if not path.exists():
            self.skipTest("original BAS publisher source must be provided by dedicated workflow")
        result=m.run(m.SOURCE,path/"species_annual_stage_summary.csv",
                     path/"source_stage_site_seasons.csv")
        self.assertTrue(m.verify(result))
        self.assertEqual(result["comparison"]["preseason"]["coverage_full"]["n_independent_calendar_year_opportunities"],7)

    def test_same_survey_year_vs_concurrent_not_equivalent(self):
        path=ROOT/"build/signy_stage_derived"
        if not path.exists():
            self.skipTest("original BAS publisher source must be provided by dedicated workflow")
        result=m.run(m.SOURCE,path/"species_annual_stage_summary.csv",
                     path/"source_stage_site_seasons.csv")
        b=result["comparison"]["preseason"]["all"]["species"]["Chinstrap"]["r"]
        c=result["comparison"]["concurrent_summer"]["all"]["species"]["Chinstrap"]["r"]
        self.assertLess(b,0)
        self.assertGreater(c,0)

if __name__=="__main__":
    unittest.main()
