from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from mina.signy_concentration import YEARS
from mina.signy_chinstrap_concentration import PRIMARY_ROSTER, stable_roster_matrix


class SignyChinstrapConcentrationTests(unittest.TestCase):
    def test_frozen_roster_and_panel(self):
        self.assertEqual(len(PRIMARY_ROSTER),9)
        self.assertEqual(len(YEARS),22)
        self.assertNotIn(1997,set(YEARS.tolist()))
        self.assertNotIn(2010,set(YEARS.tolist()))

    def test_stable_roster_matrix(self):
        rows=[]
        for year in YEARS:
            season=f"{int(year)}-{str(int(year)+1)[-2:]}"
            for i,c in enumerate(PRIMARY_ROSTER,1):
                rows.append({
                    "SEASON":season,
                    "COLONY":c,
                    "TOTAL_NUMBER_OF_PAIRS":100+i,
                })
        # Structurally excluded labels and seasons must not affect the panel.
        rows.append({"SEASON":"1997-98","COLONY":"C15","TOTAL_NUMBER_OF_PAIRS":"NA"})
        rows.append({"SEASON":"2005-06","COLONY":"C18a","TOTAL_NUMBER_OF_PAIRS":999999})
        matrix=stable_roster_matrix(pd.DataFrame(rows))
        self.assertEqual(matrix.shape,(9,22))
        np.testing.assert_allclose(matrix[0],101.0)
        np.testing.assert_allclose(matrix[-1],109.0)


if __name__=="__main__":
    unittest.main()
