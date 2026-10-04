import unittest
import numpy as np
import pandas as pd

from scripts.compute_paper2d_marine_distance import epoch_summary


class MarineDistanceTests(unittest.TestCase):
    def test_epoch_support_and_median(self):
        row=type("R",(),{"site_id":"X","early_window_start":2000,"early_window_end":2002})()
        d={}
        for y in range(2000,2003):
            for m,v in zip((1,11,12),(10.0+y-2000,20.0+y-2000,30.0+y-2000)):
                d[("X",y,m)]=v
        s=epoch_summary(row,"early",d)
        self.assertTrue(s["early_marine_epoch_pass"])
        self.assertEqual(s["early_complete_years"],3)
        self.assertAlmostEqual(s["early_median_open_water_distance_km"],21.0)

    def test_missing_month_fraction_fails(self):
        row=type("R",(),{"site_id":"X","early_window_start":2000,"early_window_end":2002})()
        d={("X",2000,1):1.0,("X",2000,11):2.0,("X",2000,12):3.0}
        s=epoch_summary(row,"early",d)
        self.assertFalse(s["early_marine_epoch_pass"])


if __name__=="__main__":
    unittest.main()
