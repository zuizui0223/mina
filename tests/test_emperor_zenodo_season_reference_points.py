import unittest
import pandas as pd
from scripts.validate_emperor_zenodo_season_reference_points import geod_m

class SeasonReferenceSemanticTests(unittest.TestCase):
    def test_geod_zero(self):
        self.assertAlmostEqual(geod_m((8.3,-69.9),(8.3,-69.9)),0.0,places=6)
    def test_small_offset_positive(self):
        self.assertGreater(geod_m((8.3,-69.9),(8.3001,-69.9)),0.0)

if __name__=="__main__":
    unittest.main()
