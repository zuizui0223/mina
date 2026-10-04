import unittest
import numpy as np

from scripts.recover_paper2d_summer_exposure_beaufort import (
    fraction_at_threshold,
    qa_flag,
)


class SummerExposureRecoveryTests(unittest.TestCase):
    def test_qa_flag(self):
        x = np.array([[0, 1 << 5, 1 << 7, (1 << 5) | (1 << 7)]], dtype=np.uint16)
        self.assertEqual(qa_flag(x, 5).tolist(), [[False, True, False, True]])
        self.assertEqual(qa_flag(x, 7).tolist(), [[False, False, True, True]])

    def test_persistent_fraction_uses_paired_denominator(self):
        valid = np.array([[2, 2], [1, 3]], dtype=np.uint16)
        exposed = np.array([[2, 1], [1, 0]], dtype=np.uint16)
        paired = np.array([[True, True], [False, True]])
        # Frequencies on paired cells: 1.0, 0.5, 0.0 -> two of three pass >=0.5.
        self.assertAlmostEqual(fraction_at_threshold(valid, exposed, paired, 0.5), 2/3)

    def test_higher_threshold_is_not_more_permissive(self):
        valid = np.array([[3, 3, 3]], dtype=np.uint16)
        exposed = np.array([[3, 2, 1]], dtype=np.uint16)
        paired = np.array([[True, True, True]])
        p50 = fraction_at_threshold(valid, exposed, paired, 0.5)
        p67 = fraction_at_threshold(valid, exposed, paired, 0.67)
        self.assertLessEqual(p67, p50)


if __name__ == "__main__":
    unittest.main()
