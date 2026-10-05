import unittest
import pandas as pd

from scripts.gate_smp_spatial_recovery_hysteresis_support_v1 import completed_spells_for_site
from scripts.run_smp_spatial_recovery_hysteresis_v1 import spell_effect,aggregate


class HysteresisTests(unittest.TestCase):
    def test_completed_spell_requires_consecutive_zero_run(self):
        years=[2000,2001,2002,2003,2004]
        states=["observed_positive","explicit_zero","explicit_zero","observed_positive","observed_positive"]
        out=completed_spells_for_site(years,states)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]["abandon_from"],2000)
        self.assertEqual(out[0]["recolonize_to"],2003)

    def test_gap_breaks_spell(self):
        years=[2000,2001,2003]
        states=["observed_positive","explicit_zero","observed_positive"]
        self.assertEqual(completed_spells_for_site(years,states),[])

    def test_spell_effect_positive_when_recolonization_parent_is_higher(self):
        mat=pd.DataFrame(
            {
                "focal":[10,0,0,5],
                "other1":[40,35,80,90],
                "other2":[20,20,30,40],
            },
            index=[2000,2001,2002,2003],
        )
        sp={"abandon_from":2000,"abandon_to":2001,"recolonize_from":2002,"recolonize_to":2003}
        out=spell_effect(mat,"focal",sp)
        self.assertGreater(out["H"],0)

    def test_species_balanced_aggregation(self):
        rows=[]
        for s in range(6):
            for m in range(2):
                rows.append({"species":f"sp{s}","master_site":f"M{s}-{m}","site_id":f"S{s}-{m}","H":0.2+0.01*s})
        out=aggregate(pd.DataFrame(rows))
        self.assertGreater(out["primary_T_species_balanced_mean_H"],0)
        self.assertEqual(out["species_count"],6)
        self.assertTrue(out["supported"])


if __name__=="__main__":
    unittest.main()
