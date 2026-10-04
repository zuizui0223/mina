import unittest
from scripts.audit_emperor_zenodo_longterm_support import classify_colony, parse_date_series
import pandas as pd

class ZenodoSupportTests(unittest.TestCase):
    def test_classify_colony(self):
        self.assertEqual(classify_colony("foo/Astrid_2012_route.shp"),"Astrid")
        self.assertEqual(classify_colony("Mertz/test.shp"),"Mertz")
        self.assertEqual(classify_colony("sanae_route.shp"),"SANAE")

    def test_parse_dates(self):
        s=pd.Series(["2001-01-02","2002-02-03","bad"])
        r=parse_date_series(s)
        self.assertEqual(r["parsed_n"],2)
        self.assertEqual(r["min_year"],2001)
        self.assertEqual(r["max_year"],2002)

if __name__=="__main__":
    unittest.main()
