import unittest
import numpy as np

from scripts.run_paper2_detectable_effect import (
    isotonic_non_decreasing,
    interpolate_mde,
    exact_frozen_p,
)

class DetectableEffectTests(unittest.TestCase):
    def test_exact_frozen_p(self):
        null=np.asarray([-3.,-2.,-1.,0.,1.])
        # Function denominator is frozen at 10000 because production uses B=9999;
        # check rank counting itself rather than nominal p scale.
        self.assertEqual(np.searchsorted(null,-1.5,side="right"),2)
        self.assertAlmostEqual(exact_frozen_p(-1.5,null),(1+2)/10000)

    def test_isotonic_repairs_monte_carlo_wiggle(self):
        y=[0.10,0.30,0.28,0.80]
        out=isotonic_non_decreasing(y,[300]*4)
        self.assertAlmostEqual(out[1],0.29)
        self.assertAlmostEqual(out[2],0.29)
        self.assertTrue(all(out[i]<=out[i+1] for i in range(len(out)-1)))

    def test_interpolate_mde(self):
        mags=[0.2,0.3,0.4]
        power=[0.2,0.7,0.9]
        self.assertAlmostEqual(interpolate_mde(mags,power,0.8),0.35)
        self.assertIsNone(interpolate_mde(mags,power,0.95))

if __name__=="__main__":
    unittest.main()
