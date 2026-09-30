import math
import unittest

import pandas as pd

from mina.signy_replication import (
    build_signy_rows,
    run_configuration,
)


def synthetic_frame():
    colonies=["A2","A3","A4","A41","A1 + A60"]
    base={"A2":120,"A3":100,"A4":80,"A41":60,"A1 + A60":140}
    rate={"A2":0.12,"A3":0.05,"A4":-0.03,"A41":-0.10,"A1 + A60":0.08}
    fec={"A2":1.5,"A3":1.2,"A4":0.8,"A41":0.5,"A1 + A60":1.35}
    rows=[]
    for year in range(1996,2008):
        season=f"{year}-{year+1}"
        for colony in colonies:
            pairs=max(0,round(base[colony]*math.exp(rate[colony]*(year-1996))))
            chicks=round(pairs*fec[colony])
            comment="logistical constraints delayed optimum time" if year==2002 and colony=="A2" else ""
            rows.append({
                "SEASON":season,
                "COLONY":colony,
                "TOTAL_NUMBER_OF_PAIRS":pairs,
                "TOTAL_NUMBER_OF_CHICKS":chicks,
                "COMMENTS":comment,
            })
    return pd.DataFrame(rows)


class SourceConstructionTests(unittest.TestCase):
    def test_literal_pooled_label_is_not_split(self):
        adults,chicks,meta=build_signy_rows(synthetic_frame())
        self.assertIn("A1 + A60",meta["literal_labels"])
        self.assertTrue(any(r["colony"]=="A1 + A60" for r in adults))
        self.assertTrue(any(r["colony"]=="A1 + A60" for r in chicks))

    def test_atomic_sensitivity_excludes_plus_label_only(self):
        _,_,meta=build_signy_rows(synthetic_frame(),atomic_only=True)
        self.assertNotIn("A1 + A60",meta["literal_labels"])
        self.assertIn("A2",meta["literal_labels"])

    def test_comment_flag_excludes_whole_season(self):
        _,_,meta=build_signy_rows(
            synthetic_frame(),
            exclude_comment_flagged_seasons=True,
        )
        self.assertIn(2002,meta["comment_flagged_seasons"])
        self.assertNotIn(2002,meta["seasons"])


class ReplicationEstimatorTests(unittest.TestCase):
    def test_synthetic_positive_state_has_positive_lag2_beta(self):
        result=run_configuration(
            synthetic_frame(),
            atomic_only=False,
            exclude_comment_flagged_seasons=False,
            lag2_seed=17,
            hinge_seed=18,
            permutations=500,
        )
        self.assertGreater(result["primary_lag2"]["beta"],0)
        self.assertGreaterEqual(result["lag2_support"]["rows"],20)
        self.assertTrue(0 < result["primary_lag2"]["one_sided_upper_p"] <= 1)

    def test_replication_is_seed_deterministic(self):
        a=run_configuration(
            synthetic_frame(),
            atomic_only=True,
            exclude_comment_flagged_seasons=False,
            lag2_seed=29,
            hinge_seed=30,
            permutations=200,
        )
        b=run_configuration(
            synthetic_frame(),
            atomic_only=True,
            exclude_comment_flagged_seasons=False,
            lag2_seed=29,
            hinge_seed=30,
            permutations=200,
        )
        self.assertEqual(a["primary_lag2"],b["primary_lag2"])
        self.assertEqual(a["secondary_hinge"],b["secondary_hinge"])


if __name__=="__main__":
    unittest.main()
