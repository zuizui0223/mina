import unittest

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(
        "Paper 2 predictor-identifiability tests require numpy and pandas"
    ) from exc

from scripts.audit_paper2_predictor_identifiability import diagnose_species


def balanced_frame(n_per_quadrant=4):
    rows=[]
    i=0
    patterns=[(-1.5,-1.5),(-1.5,1.5),(1.5,-1.5),(1.5,1.5)]
    for group in ("G1","G2"):
        for a,h in patterns:
            for rep in range(n_per_quadrant):
                rows.append({
                    "unit_id":f"u{i}",
                    "group":group,
                    "A":a + 0.05*rep,
                    "H":h + 0.10*rep,
                    "R":(-1 if group=="G1" else 1) + 0.03*rep,
                    "H_raw":1 + ((i+rep) % 4),
                })
                i+=1
    return pd.DataFrame(rows)


class PredictorIdentifiabilityTests(unittest.TestCase):
    def test_balanced_design_passes_crossover_gate(self):
        result=diagnose_species(balanced_frame())
        self.assertTrue(result["crossover_eligible"])
        self.assertEqual(result["design_rank"], result["design_columns"])
        self.assertLess(result["crossover_condition_number"], 10)
        self.assertLess(result["interaction_vif"], 5)
        self.assertTrue(all(v >= 3 for v in result["quadrant_counts"].values()))

    def test_sparse_quadrant_fails_gate(self):
        frame=balanced_frame()
        frame=frame[~((frame["A"] < 0) & (frame["H"] > 0))].copy()
        result=diagnose_species(frame)
        self.assertFalse(result["crossover_eligible"])
        self.assertLess(result["quadrant_counts"].get("-+",0),3)

    def test_group_with_too_few_habitat_levels_fails_gate(self):
        frame=balanced_frame()
        frame.loc[frame["group"]=="G2","H_raw"]=2
        result=diagnose_species(frame)
        self.assertFalse(result["crossover_eligible"])
        by_group={row["group"]:row for row in result["group_support"]}
        self.assertEqual(by_group["G2"]["unique_habitat_complex_values"],1)

    def test_small_species_sample_fails_gate(self):
        frame=balanced_frame(n_per_quadrant=1)
        result=diagnose_species(frame)
        self.assertFalse(result["crossover_eligible"])
        self.assertLess(result["n_complete_units"],25)


if __name__=="__main__":
    unittest.main()
