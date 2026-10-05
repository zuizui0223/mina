import unittest
import pandas as pd

from scripts.diagnose_mapppd_intensification_before_expansion import summarize


class IntensificationDiagnosticTests(unittest.TestCase):
    def test_summary_splits_existing_and_zero_to_positive_gain(self):
        df=pd.DataFrame([
            {
                "n_exact_zero_sites_t":1,
                "n_zero_to_positive_sites":1,
                "gross_existing_gain":80.0,
                "gross_expansion_gain":20.0,
                "intensification_fraction":0.8,
            },
            {
                "n_exact_zero_sites_t":0,
                "n_zero_to_positive_sites":0,
                "gross_existing_gain":50.0,
                "gross_expansion_gain":0.0,
                "intensification_fraction":1.0,
            },
        ])
        out=summarize(df)
        self.assertEqual(out["positive_total_transitions"],2)
        self.assertEqual(out["with_exact_zero_site_at_t"],1)
        self.assertEqual(out["with_zero_to_positive_site"],1)
        self.assertAlmostEqual(out["intensification_fraction"],130/150)
        self.assertAlmostEqual(out["expansion_fraction"],20/150)

    def test_empty_summary(self):
        out=summarize(pd.DataFrame())
        self.assertEqual(out["positive_total_transitions"],0)
        self.assertIsNone(out["expansion_fraction"])


if __name__=="__main__":
    unittest.main()
