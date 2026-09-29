import unittest

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError as exc:
    raise unittest.SkipTest("observation-recovery tests require numpy/pandas") from exc

from scripts.simulate_paper2_observation_recovery import (
    estimate_accuracy_scales,
    estimate_method_offset,
    evaluate_observation_recovery,
    simulate_observation_records,
)


class ObservationEstimatorTests(unittest.TestCase):
    def test_method_offset_uses_within_group_direct_image_difference(self):
        frame=pd.DataFrame([
            {"group_id":"g1","species_id":"ADPE","vantage_family":"direct","accuracy_group":"1","log_observed":8.0},
            {"group_id":"g1","species_id":"ADPE","vantage_family":"image_based","accuracy_group":"1","log_observed":8.2},
            {"group_id":"g2","species_id":"CHPE","vantage_family":"direct","accuracy_group":"1","log_observed":9.0},
            {"group_id":"g2","species_id":"CHPE","vantage_family":"image_based","accuracy_group":"2-5","log_observed":9.2},
        ])
        result=estimate_method_offset(frame)
        self.assertEqual(result["mixed_groups"],2)
        self.assertAlmostEqual(result["delta_image"],0.2,places=12)

    def test_unknown_vantage_does_not_enter_method_offset(self):
        frame=pd.DataFrame([
            {"group_id":"g1","species_id":"ADPE","vantage_family":"direct","accuracy_group":"1","log_observed":8.0},
            {"group_id":"g1","species_id":"ADPE","vantage_family":"image_based","accuracy_group":"1","log_observed":8.1},
            {"group_id":"g1","species_id":"ADPE","vantage_family":"unknown","accuracy_group":"1","log_observed":99.0},
        ])
        result=estimate_method_offset(frame)
        self.assertAlmostEqual(result["delta_image"],0.1,places=12)

    def test_accuracy_scales_use_only_repeated_same_accuracy_groups(self):
        root=np.sqrt(0.05)
        frame=pd.DataFrame([
            {"group_id":"g1","species_id":"ADPE","vantage_family":"direct","accuracy_group":"1","log_observed":7.9},
            {"group_id":"g1","species_id":"ADPE","vantage_family":"direct","accuracy_group":"1","log_observed":8.1},
            {"group_id":"g2","species_id":"CHPE","vantage_family":"direct","accuracy_group":"1","log_observed":8.8},
            {"group_id":"g2","species_id":"CHPE","vantage_family":"direct","accuracy_group":"1","log_observed":9.2},
            {"group_id":"g3","species_id":"GEPE","vantage_family":"direct","accuracy_group":"2-5","log_observed":10.0},
            {"group_id":"g3","species_id":"GEPE","vantage_family":"direct","accuracy_group":"2-5","log_observed":10.2},
            {"group_id":"g4","species_id":"GEPE","vantage_family":"direct","accuracy_group":"2-5","log_observed":11.0},
        ])
        result=estimate_accuracy_scales(frame,delta_image=0.0)
        self.assertAlmostEqual(result["1"]["sigma"],root,places=12)
        self.assertEqual(result["1"]["repeat_groups"],2)
        self.assertAlmostEqual(result["2-5"]["sigma"],np.sqrt(0.02),places=12)
        self.assertEqual(result["2-5"]["repeat_groups"],1)

    def test_simulation_is_deterministic(self):
        metadata=pd.DataFrame([
            {"group_id":"g1","species_id":"ADPE","vantage_family":"direct","accuracy_group":"1"},
            {"group_id":"g1","species_id":"ADPE","vantage_family":"image_based","accuracy_group":"1"},
            {"group_id":"g2","species_id":"CHPE","vantage_family":"direct","accuracy_group":"2-5"},
            {"group_id":"g2","species_id":"CHPE","vantage_family":"image_based","accuracy_group":"2-5"},
        ])
        a=simulate_observation_records(
            metadata,delta_image=np.log(1.15),sigma1=np.log(1.05),
            sigma2plus=np.log(1.25),seed=77
        )
        b=simulate_observation_records(
            metadata,delta_image=np.log(1.15),sigma1=np.log(1.05),
            sigma2plus=np.log(1.25),seed=77
        )
        self.assertEqual(a["log_observed"].tolist(),b["log_observed"].tolist())


class MonteCarloTests(unittest.TestCase):
    def test_recovery_summary_has_frozen_outputs(self):
        rows=[]
        for g in range(30):
            group=f"g{g}"
            species=("ADPE","CHPE","GEPE")[g%3]
            rows.extend([
                {"group_id":group,"species_id":species,"vantage_family":"direct","accuracy_group":"1"},
                {"group_id":group,"species_id":species,"vantage_family":"image_based","accuracy_group":"1"},
                {"group_id":group,"species_id":species,"vantage_family":"direct","accuracy_group":"2-5"},
                {"group_id":group,"species_id":species,"vantage_family":"image_based","accuracy_group":"2-5"},
            ])
        metadata=pd.DataFrame(rows)
        out=evaluate_observation_recovery(metadata,replicates=8,seed_offset=900)
        self.assertIn("offset",out)
        self.assertIn("accuracy",out)
        self.assertIn("gate",out)
        self.assertEqual(out["replicates"],8)


if __name__=="__main__":
    unittest.main()
