import unittest
import numpy as np
from scripts.simulate_paper2_cross_species_generality_v4 import summarize

class GeneralityAggregationTests(unittest.TestCase):
    def test_single_species_driver_has_zero_median(self):
        raw=[
          {"gamma":{"ADPE":-.35,"CHPE":0.0,"GEPE":0.0},"median_gamma":0.0,"n_negative":1}
          for _ in range(10)
        ]
        x=summarize(raw)
        self.assertAlmostEqual(x["median_of_species_gamma"]["median"],0.0)
        self.assertEqual(x["at_least_two_species_negative_fraction"],0.0)

    def test_common_effect_has_negative_median_and_replication(self):
        raw=[
          {"gamma":{"ADPE":-.3,"CHPE":-.4,"GEPE":-.35},"median_gamma":-.35,"n_negative":3}
          for _ in range(10)
        ]
        x=summarize(raw)
        self.assertLess(x["median_of_species_gamma"]["median"],0)
        self.assertEqual(x["at_least_two_species_negative_fraction"],1.0)

if __name__=="__main__":unittest.main()
