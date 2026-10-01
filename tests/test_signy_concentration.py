from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from mina.signy_concentration import (
    YEARS,
    PRIMARY_ROSTER,
    canonical_label,
    effective_number,
    slope,
    stable_roster_matrix,
)


class SignyConcentrationTests(unittest.TestCase):
    def test_canonical_a1_a60_labels(self):
        for label in ("A1", "A60", "A1 + A60", "A1+A60"):
            self.assertEqual(canonical_label(label), "A1+A60")
        self.assertEqual(canonical_label("A2"), "A2")

    def test_effective_number_known_cases(self):
        equal = np.asarray([[5.0], [5.0]])
        dominant = np.asarray([[10.0], [0.0]])
        self.assertAlmostEqual(float(effective_number(equal)[0]), 2.0)
        self.assertAlmostEqual(float(effective_number(dominant)[0]), 1.0)

    def test_negative_slope_for_decreasing_series(self):
        values = np.linspace(5.0, 2.0, len(YEARS))
        self.assertLess(float(slope(values)), 0.0)

    def test_stable_roster_matrix_harmonizes_a1_a60(self):
        rows = []
        for year in YEARS:
            season = f"{int(year)}-{str(int(year)+1)[-2:]}"
            if year <= 2005:
                rows.append(
                    {"SEASON": season, "COLONY": "A1", "TOTAL_NUMBER_OF_PAIRS": 7}
                )
                rows.append(
                    {"SEASON": season, "COLONY": "A60", "TOTAL_NUMBER_OF_PAIRS": 3}
                )
            else:
                rows.append(
                    {
                        "SEASON": season,
                        "COLONY": "A1 + A60",
                        "TOTAL_NUMBER_OF_PAIRS": 10,
                    }
                )
            for idx, colony in enumerate(PRIMARY_ROSTER[1:], start=1):
                rows.append(
                    {
                        "SEASON": season,
                        "COLONY": colony,
                        "TOTAL_NUMBER_OF_PAIRS": 10 + idx,
                    }
                )
        frame = pd.DataFrame(rows)
        matrix = stable_roster_matrix(frame)
        self.assertEqual(matrix.shape, (5, 24))
        np.testing.assert_allclose(matrix[0], 10.0)
        np.testing.assert_allclose(matrix[1], 11.0)
        np.testing.assert_allclose(matrix[4], 14.0)


if __name__ == "__main__":
    unittest.main()
