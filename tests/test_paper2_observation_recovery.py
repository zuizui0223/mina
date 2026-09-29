import unittest

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError as exc:
    raise unittest.SkipTest("observation-recovery tests require numpy/pandas") from exc

from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
    estimate_accuracy_scales,
    estimate_method_offset,
    evaluate_observation_recovery,
    run_observation_audit,
    simulate_observation_records,
    validate_frozen_support,
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



class FrozenMetadataTests(unittest.TestCase):
    def test_rebuilds_107_units_without_count_leakage(self):
        gate0={"ADPE":57,"CHPE":46,"GEPE":49}
        bridged={"ADPE":44,"CHPE":34,"GEPE":29}
        rows=[]
        unit_index=0
        for species_id in ("ADPE","CHPE","GEPE"):
            for j in range(gate0[species_id]):
                site_id=f"S{unit_index:03d}"
                years=[1980,1985,1990,1995,2000]
                seasons=(
                    [1980,1990,2000,2010,2020]
                    if j < bridged[species_id]
                    else [1995,2000,2005,2010,2015]
                )
                for k,(year,season) in enumerate(zip(years,seasons)):
                    rows.append({
                        "site_id":site_id,
                        "species_id":species_id,
                        "type":"nests",
                        "count":100000+unit_index*10+k,
                        "year":year,
                        "season":season,
                        "vantage":"ground photo" if k==0 else "ground",
                        "accuracy":1 if k<3 else 2,
                    })
                unit_index+=1
        out=build_frozen_observation_metadata(pd.DataFrame(rows))
        self.assertEqual(out[["site_id","species_id"]].drop_duplicates().shape[0],107)
        self.assertNotIn("count",out.columns)
        self.assertNotIn("year",out.columns)
        self.assertEqual(set(out["accuracy_group"]),{"1","2-5"})
        self.assertIn("image_based",set(out["vantage_family"]))
        self.assertTrue(out["group_id"].str.contains("\\|").all())



class FrozenSupportValidationTests(unittest.TestCase):
    def test_expected_support_passes_and_drift_fails_closed(self):
        expected={
            "records":2100,
            "bridged_units":107,
            "season_groups":1721,
            "repeated_groups":273,
            "direct_records":1889,
            "image_based_records":149,
            "unknown_vantage_records":62,
            "mixed_direct_image_groups":41,
            "mixed_direct_image_groups_by_species":{
                "ADPE":9,"CHPE":10,"GEPE":22,
            },
        }
        validate_frozen_support(expected)
        drift=dict(expected)
        drift["records"]=2099
        with self.assertRaises(ValueError):
            validate_frozen_support(drift)


class EndToEndAuditTests(unittest.TestCase):
    def test_synthetic_full_cohort_audit_runs_without_count_output(self):
        gate0={"ADPE":57,"CHPE":46,"GEPE":49}
        bridged={"ADPE":44,"CHPE":34,"GEPE":29}
        rows=[]
        unit_index=0
        for species_id in ("ADPE","CHPE","GEPE"):
            for j in range(gate0[species_id]):
                site_id=f"T{unit_index:03d}"
                years=[1980,1985,1990,1995,2000]
                seasons=(
                    [1980,1990,2000,2010,2020]
                    if j < bridged[species_id]
                    else [1995,2000,2005,2010,2015]
                )
                for year,season in zip(years,seasons):
                    for vantage,accuracy in (
                        ("ground",1),("ground photo",1),
                        ("ground",2),("ground photo",2),
                    ):
                        rows.append({
                            "site_id":site_id,"species_id":species_id,
                            "type":"nests","count":100000+unit_index,
                            "year":year,"season":season,
                            "vantage":vantage,"accuracy":accuracy,
                        })
                unit_index+=1
        result=run_observation_audit(
            pd.DataFrame(rows),replicates=4,seed_offset=300
        )
        self.assertEqual(result["metadata"]["bridged_units"],107)
        self.assertEqual(result["metadata"]["records"],107*5*4)
        self.assertNotIn("count",repr(result).lower())
        self.assertIn("gate",result["recovery"])


if __name__=="__main__":
    unittest.main()
