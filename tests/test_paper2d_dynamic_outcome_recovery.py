import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.simulate_paper2d_dynamic_outcome_recovery import _fit_ols, parse_seasons


class Paper2DDynamicOutcomeRecoveryTests(unittest.TestCase):
    def test_parse_seasons(self):
        self.assertEqual(parse_seasons("1980;1982;1982;1990"), [1980,1982,1990])

    def test_two_way_fe_recovers_exact_beta_without_noise(self):
        rows=[]
        for site,h in [("A",-1.0),("B",0.0),("C",1.0)]:
            for season in [2000,2010,2020]:
                tau=(season-2010)/10
                rows.append({"site_id":site,"region":"R","season":season,"x":h*tau})
        d=pd.DataFrame(rows)
        site_effect={"A":1.2,"B":-0.4,"C":0.8}
        year_effect={2000:-0.2,2010:0.5,2020:-0.1}
        beta=0.37
        y=[site_effect[r.site_id]+year_effect[r.season]+beta*r.x for r in d.itertuples()]
        got=_fit_ols(y,d)
        self.assertAlmostEqual(got,beta,places=10)


if __name__ == "__main__":
    unittest.main()
