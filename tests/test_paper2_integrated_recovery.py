import unittest

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError as exc:
    raise unittest.SkipTest("integrated recovery tests require numpy/pandas") from exc

from scripts.simulate_paper2_integrated_recovery import (
    build_interval_payload,
    collapse_same_season,
    count_to_analysis_scale,
    counts_from_analysis_scale,
    fit_species_from_counts,
    run_integrated_replicate,
    simulate_species_counts,
)


class ZeroSafeTransformTests(unittest.TestCase):
    def test_log1p_transform_is_finite_at_zero(self):
        counts=np.array([0.0,1.0,9.0,99.0])
        z=count_to_analysis_scale(counts)
        self.assertTrue(np.isfinite(z).all())
        self.assertAlmostEqual(float(z[0]),0.0,places=12)
        np.testing.assert_allclose(z,np.log1p(counts))

    def test_inverse_roundtrip_on_integer_counts(self):
        counts=np.array([0,1,2,10,100],dtype=int)
        restored=counts_from_analysis_scale(np.log1p(counts))
        np.testing.assert_array_equal(restored,counts)


class SameSeasonCollapseTests(unittest.TestCase):
    def test_method_corrected_inverse_variance_collapse(self):
        delta=np.log(1.15)
        s1=np.log(1.05)
        s2=np.log(1.25)
        frame=pd.DataFrame([
            {
                "group_id":"S1|ADPE|2000","site_id":"S1","species_id":"ADPE",
                "season":2000,"vantage_family":"direct","accuracy_group":"1",
                "count":int(round(np.expm1(8.0))),
            },
            {
                "group_id":"S1|ADPE|2000","site_id":"S1","species_id":"ADPE",
                "season":2000,"vantage_family":"image_based","accuracy_group":"2-5",
                "count":int(round(np.expm1(8.0+delta))),
            },
        ])
        out=collapse_same_season(
            frame,delta_image=delta,sigma1=s1,sigma2plus=s2
        )
        self.assertEqual(len(out),1)
        expected_var=1.0/(1.0/s1**2+1.0/s2**2)
        self.assertAlmostEqual(float(out.iloc[0]["state_hat"]),8.0,places=3)
        self.assertAlmostEqual(float(out.iloc[0]["observation_var"]),expected_var,places=12)

    def test_unknown_vantage_is_retained_without_method_shift(self):
        s1=np.log(1.05)
        frame=pd.DataFrame([
            {
                "group_id":"S1|ADPE|2000","site_id":"S1","species_id":"ADPE",
                "season":2000,"vantage_family":"unknown","accuracy_group":"1",
                "count":int(round(np.expm1(7.0))),
            }
        ])
        out=collapse_same_season(
            frame,delta_image=np.log(1.15),sigma1=s1,sigma2plus=np.log(1.25)
        )
        self.assertEqual(len(out),1)
        self.assertAlmostEqual(float(out.iloc[0]["state_hat"]),7.0,places=3)
        self.assertAlmostEqual(float(out.iloc[0]["observation_var"]),s1**2,places=12)


def dense_species_fixture():
    seasons=";".join(str(y) for y in range(1980,2026))
    vals=[
        (-1.5,-1.2),(-1.0,1.1),(-0.5,-0.8),(-0.2,1.4),
        (0.2,-1.1),(0.6,0.7),(1.0,-0.4),(1.4,1.0),
    ]
    frame=pd.DataFrame([
        {
            "unit_id":f"ADPE|S{i}","site_id":f"S{i}","species_id":"ADPE",
            "forcing_group":"G1","A":a,"H":h,"AH":a*h,"seasons":seasons,
        }
        for i,(a,h) in enumerate(vals)
    ])
    metadata=[]
    for i in range(len(frame)):
        for season in range(1980,2026):
            metadata.append({
                "group_id":f"S{i}|ADPE|{season}",
                "site_id":f"S{i}","species_id":"ADPE","season":season,
                "vantage_family":"direct","accuracy_group":"1",
            })
    return frame,pd.DataFrame(metadata)


class JointIntegratedTests(unittest.TestCase):
    def test_joint_fit_estimates_observation_nuisance_from_same_counts(self):
        frame,metadata=dense_species_fixture()
        frames={"ADPE":frame}
        sim=simulate_integrated_dataset(
            frames,metadata,
            gamma_a=0.0,gamma_ah=-0.35,seed=777,
            forcing_sd=0.10,loading_sd=0.0,process_sd=0.0,
            drift_mean=-0.01,drift_sd=0.0,
            delta_image=np.log(1.15),
            sigma1=np.log(1.05),sigma2plus=np.log(1.25),
        )
        fit=fit_integrated_dataset(
            frames,
            sim["observations"],
            sim["truth"],
        )
        self.assertLess(
            abs(fit["observation"]["delta_image"]-np.log(1.15)),0.03
        )
        self.assertLess(
            abs(
                fit["observation"]["accuracy"]["1"]["sigma"]
                -np.log(1.05)
            )/np.log(1.05),
            0.15,
        )
        self.assertLess(
            abs(fit["species"]["ADPE"]["gamma_ah"]+0.35),0.08
        )
        self.assertGreater(
            fit["species"]["ADPE"]["forcing_correlation"]["G1"],0.90
        )


class IntegratedSpeciesTests(unittest.TestCase):
    def test_dense_near_noiseless_integer_counts_recover_crossover(self):
        frame,metadata=dense_species_fixture()
        sim=simulate_species_counts(
            frame,metadata,
            gamma_a=0.0,gamma_ah=-0.35,seed=123,
            forcing_sd=0.10,loading_sd=0.0,process_sd=0.0,
            drift_mean=-0.01,drift_sd=0.0,
            delta_image=0.0,sigma1=1e-6,sigma2plus=1e-6,
        )
        fit=fit_species_from_counts(
            frame,sim["observations"],
            delta_image=0.0,sigma1=1e-6,sigma2plus=1e-6,
            truth_forcing=sim["true_forcing"],
            true_lambda=sim["true_lambda"],
        )
        self.assertLess(abs(fit["gamma_ah"]+0.35),0.06)
        self.assertGreater(fit["forcing_correlation"]["G1"],0.98)

    def test_interval_payload_uses_adjacent_observed_seasons(self):
        frame=pd.DataFrame([{
            "unit_id":"ADPE|S1","site_id":"S1","species_id":"ADPE",
            "forcing_group":"G1","A":0.0,"H":0.0,"AH":0.0,
            "seasons":"1980;1990;2000",
        }])
        collapsed=pd.DataFrame([
            {"group_id":"S1|ADPE|1980","site_id":"S1","species_id":"ADPE",
             "season":1980,"state_hat":5.0,"observation_var":0.1,"n_records":1},
            {"group_id":"S1|ADPE|1990","site_id":"S1","species_id":"ADPE",
             "season":1990,"state_hat":5.5,"observation_var":0.1,"n_records":1},
            {"group_id":"S1|ADPE|2000","site_id":"S1","species_id":"ADPE",
             "season":2000,"state_hat":5.2,"observation_var":0.1,"n_records":1},
        ])
        payload=build_interval_payload(frame,collapsed)
        self.assertEqual(len(payload["records"]),2)
        self.assertEqual(payload["records"][0][:4],(0,"G1",1980,1990))
        self.assertAlmostEqual(payload["records"][0][4],0.5,places=12)
        self.assertAlmostEqual(payload["records"][1][4],-0.3,places=12)


class IntegratedJointRecoveryTests(unittest.TestCase):
    def test_one_dense_replicate_recovers_nuisance_and_crossover(self):
        frame,_=dense_species_fixture()
        rows=[]
        for i in range(len(frame)):
            for season in range(1980,2026):
                for family,accuracy in (
                    ("direct","1"),("image_based","1"),
                    ("direct","2-5"),("image_based","2-5"),
                ):
                    rows.append({
                        "group_id":f"S{i}|ADPE|{season}",
                        "site_id":f"S{i}","species_id":"ADPE","season":season,
                        "vantage_family":family,"accuracy_group":accuracy,
                    })
        metadata=pd.DataFrame(rows)
        out=run_integrated_replicate(
            {"ADPE":frame},
            metadata,
            gamma_a=0.0,
            gamma_ah=-0.35,
            seed=707,
            forcing_sd=0.08,
            loading_sd=0.0,
            process_sd=0.02,
            drift_mean=-0.01,
            drift_sd=0.0,
        )
        self.assertLess(
            abs(out["observation"]["delta_image"]-np.log(1.15)),0.03
        )
        fit=out["species"]["ADPE"]
        self.assertLess(abs(fit["gamma_ah"]+0.35),0.10)
        self.assertGreater(fit["forcing_correlation"]["G1"],0.90)


if __name__=="__main__":
    unittest.main()
