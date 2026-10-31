import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/signy_prey_fledgling_v2.py"
spec=importlib.util.spec_from_file_location("link_prey",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class PreyLinkTests(unittest.TestCase):
    def test_calendar_boundary(self):
        self.assertEqual(m.date("1998-01-28").year,1998)
        self.assertEqual(m.date("28/01/1998").month,1)
        with self.assertRaises(ValueError):
            m.date("1998-8895")
    def test_missing_not_zero(self):
        self.assertIsNone(m.number("NA"))
        self.assertEqual(m.number("0"),0)
    def test_krill_fraction_source_pin(self):
        self.assertEqual(m.SOURCE["Gentoo"][1],"6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902")
    def test_no_artificial_years(self):
        data=[{"species":"Adelie","season_start":2000,"n_sample":3,
               "first_diet_sample":"2001-01-01","last_diet_sample":"2001-02-01"}]
        result=m.link(data,{("Adelie",2000):1.2},{("Adelie",2000):["2001-02-03"]})
        self.assertEqual(len(result),1)
        self.assertTrue(result[0]["all_diet_samples_before_every_fledgling_count"])

if __name__=="__main__":
    unittest.main()
