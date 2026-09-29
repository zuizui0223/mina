import unittest

try:
    import numpy as np
    import pandas as pd  # noqa: F401
    import pyreadr  # noqa: F401
    import rasterio  # noqa: F401
    import pyproj  # noqa: F401
    import dbfread  # noqa: F401
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(
        "Breeding-option hierarchy tests require raster/data dependencies"
    ) from exc

from scripts.extract_breeding_option_hierarchy import summarize


class BreedingOptionMissingnessTests(unittest.TestCase):
    def test_empty_raster_support_is_missing_not_true_zero(self):
        result = summarize(np.array([], dtype=int), {}, 10000.0)

        self.assertEqual(result["mapped_ice_free_pixel_count"], 0)
        self.assertIsNone(result["mapped_ice_free_area_ha"])
        self.assertIsNone(result["tier1_richness"])
        self.assertIsNone(result["tier1_shannon"])
        self.assertIsNone(result["tier2_richness"])
        self.assertIsNone(result["tier2_shannon"])
        self.assertIsNone(result["tier3_richness"])
        self.assertIsNone(result["tier3_shannon"])

    def test_nonempty_support_retains_numeric_metrics(self):
        maps = {
            1: {"tier1": "A", "tier2": "X", "tier3": "x1"},
            2: {"tier1": "A", "tier2": "Y", "tier3": "y1"},
        }
        result = summarize(np.array([1, 1, 2], dtype=int), maps, 10000.0)

        self.assertEqual(result["mapped_ice_free_pixel_count"], 3)
        self.assertEqual(result["mapped_ice_free_area_ha"], 3.0)
        self.assertEqual(result["tier1_richness"], 1)
        self.assertEqual(result["tier2_richness"], 2)
        self.assertEqual(result["tier3_richness"], 2)


if __name__ == "__main__":
    unittest.main()
