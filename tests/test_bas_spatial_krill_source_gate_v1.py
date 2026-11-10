"""Structure-only synthetic smoke guards for original BAS spatial krill rasters."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"research/climate-penguin/work/climate_penguin/bas_spatial_krill_source_gate_v1.py"
spec=importlib.util.spec_from_file_location("bas_spatial_krill",p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class RasterGateTests(unittest.TestCase):
    def test_publication_doi(self):
        self.assertEqual(m.DOI,"10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32")
    def test_year_cohort(self):
        self.assertEqual(m.EXPECTED_YEARS,tuple(range(2011,2021)))
    def test_invalid_zip_rejected(self):
        with self.assertRaises(ValueError):
            m.audit(__file__)

if __name__=="__main__":
    unittest.main()
