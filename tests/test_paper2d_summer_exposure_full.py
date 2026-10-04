import unittest
import numpy as np
import pandas as pd

from scripts.run_paper2d_summer_exposure_full import frozen_sites, any_fraction


class FullSummerExposureTests(unittest.TestCase):
    def test_frozen_sites_requires_exact_77(self):
        x = pd.DataFrame({
            "site_id": [f"S{i:02d}" for i in range(77)],
            "site_pass": [True] * 77,
        })
        self.assertEqual(len(frozen_sites(x)), 77)

    def test_frozen_sites_rejects_roster_drift(self):
        x = pd.DataFrame({"site_id": ["A"], "site_pass": [True]})
        with self.assertRaises(ValueError):
            frozen_sites(x)

    def test_any_fraction_uses_paired_support(self):
        valid = np.array([[2,2],[2,2]], dtype=np.uint16)
        exposed = np.array([[1,0],[1,1]], dtype=np.uint16)
        paired = np.array([[True,True],[False,True]])
        self.assertAlmostEqual(any_fraction(valid, exposed, paired), 2/3)


if __name__ == "__main__":
    unittest.main()
