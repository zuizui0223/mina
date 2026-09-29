import unittest

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError as exc:
    raise unittest.SkipTest("integrated recovery tests require numpy/pandas") from exc

from scripts.simulate_paper2_integrated_recovery import (
    collapse_same_season,
    count_to_analysis_scale,
    counts_from_analysis_scale,
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


if __name__=="__main__":
    unittest.main()
