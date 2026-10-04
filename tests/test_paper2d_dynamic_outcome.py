import unittest
import numpy as np
import pandas as pd

from scripts.run_paper2d_dynamic_outcome import holm_adjust, beta_from_residuals


class Paper2DDynamicOutcomeTests(unittest.TestCase):
    def test_holm(self):
        out=holm_adjust({"A":0.01,"B":0.04,"C":0.2})
        self.assertAlmostEqual(out["A"],0.03)
        self.assertAlmostEqual(out["B"],0.08)
        self.assertAlmostEqual(out["C"],0.2)

    def test_beta(self):
        x=np.array([-1.0,0.0,1.0])
        y=0.25*x
        self.assertAlmostEqual(beta_from_residuals(x,y),0.25)


if __name__ == "__main__":
    unittest.main()
