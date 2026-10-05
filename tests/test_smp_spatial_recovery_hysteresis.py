import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.finalize_smp_spatial_recovery_structure_v1 import run as run_identity_gate
from scripts.gate_smp_spatial_recovery_hysteresis_support_v1 import (
    completed_spells_for_site,
    validate_zero_semantics,
)
from scripts.run_smp_spatial_recovery_hysteresis_v1 import (
    aggregate,
    spell_effect,
    trajectory_phase_null,
)


class HysteresisTests(unittest.TestCase):
    def test_completed_spell_requires_consecutive_zero_run(self):
        years=[2000,2001,2002,2003,2004]
        states=["observed_positive","explicit_zero","explicit_zero","observed_positive","observed_positive"]
        out=completed_spells_for_site(years,states)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]["abandon_from"],2000)
        self.assertEqual(out[0]["recolonize_to"],2003)

    def test_recolonization_year_can_start_next_spell(self):
        years=[2000,2001,2002,2003,2004]
        states=["observed_positive","explicit_zero","observed_positive","explicit_zero","observed_positive"]
        out=completed_spells_for_site(years,states)
        self.assertEqual(len(out),2)
        self.assertEqual((out[0]["abandon_from"],out[0]["recolonize_to"]),(2000,2002))
        self.assertEqual((out[1]["abandon_from"],out[1]["recolonize_to"]),(2002,2004))

    def test_gap_breaks_spell(self):
        years=[2000,2001,2003]
        states=["observed_positive","explicit_zero","observed_positive"]
        self.assertEqual(completed_spells_for_site(years,states),[])

    def test_zero_semantics_requires_provider_confirmation(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"zero.json"
            p.write_text(json.dumps({
                "row_with_direct_count_zero_is_surveyed_nil":True,
                "absent_site_year_row_is_not_zero":True,
                "estimated_or_imputed_zero_excluded_from_primary":True,
                "confirmation_source":"synthetic provider documentation",
            }))
            out=validate_zero_semantics(p)
            self.assertIn("confirmation_source",out)

            p.write_text(json.dumps({
                "row_with_direct_count_zero_is_surveyed_nil":False,
                "absent_site_year_row_is_not_zero":True,
                "estimated_or_imputed_zero_excluded_from_primary":True,
                "confirmation_source":"synthetic",
            }))
            with self.assertRaises(ValueError):
                validate_zero_semantics(p)

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
                rows.append({
                    "spell_id":f"{s}-{m}",
                    "species":f"sp{s}",
                    "master_site":f"M{s}-{m}",
                    "unit":"AON",
                    "site_id":f"S{s}-{m}",
                    "H":0.2+0.01*s,
                })
        out=aggregate(pd.DataFrame(rows))
        self.assertGreater(out["primary_T_species_balanced_mean_H"],0)
        self.assertEqual(out["species_count"],6)
        self.assertTrue(out["sign_flip_supported"])

    def test_trajectory_phase_null_preserves_observed_hierarchy_statistic(self):
        mat=pd.DataFrame(
            {
                "focal":[10,0,0,5],
                "other1":[40,35,80,90],
                "other2":[20,20,30,40],
            },
            index=[2000,2001,2002,2003],
        )
        spell={
            "spell_id":"x",
            "species":"sp1",
            "master_site":"M1",
            "unit":"AON",
            "site_id":"focal",
            "abandon_from":2000,
            "abandon_to":2001,
            "recolonize_from":2002,
            "recolonize_to":2003,
        }
        eff=spell_effect(mat,"focal",spell)
        frame=pd.DataFrame([{**spell,**eff}])
        out=trajectory_phase_null(
            frame,
            {("sp1","M1","AON"):mat},
            {("sp1","M1","AON"):[2000,2001,2002,2003]},
            B=500,
            seed=9,
        )
        self.assertAlmostEqual(out["observed_T"],eff["H"],places=12)
        self.assertGreaterEqual(out["one_sided_p"],0)
        self.assertLessEqual(out["one_sided_p"],1)
        self.assertEqual(out["panel_blocks"],1)

    def test_identity_gate_excludes_ambiguous_multiple_units(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            panels=[]
            resolution_rows=[]

            # Twenty unique biological panels satisfy the program threshold.
            for i in range(20):
                species=f"sp{i%8}"
                master=f"M{i}"
                sites=[f"{master}-s{j}" for j in range(3)]
                panel={
                    "species":species,
                    "master_site":master,
                    "unit":"AON",
                    "countries":[f"R{i%3}"],
                    "retained_site_ids":sites,
                    "n_sites":3,
                    "complete_years":list(range(2000,2012)),
                    "n_complete_years":12,
                    "calendar_span_years":12,
                }
                panels.append(panel)
                for site in sites:
                    resolution_rows.append({
                        "species":species,"MasterSite":master,"SiteID":site,
                        "stable_identity":"true","mutually_exclusive_child":"true",
                        "overlaps_parent_or_sibling":"false",
                        "boundary_change_during_panel":"false",
                        "retired_or_replaced":"false","notes":"",
                    })

            # Extra ambiguous species x MasterSite represented in two count units.
            for unit in ("AON","AOS"):
                sites=[f"AMB-s{j}" for j in range(3)]
                panels.append({
                    "species":"sp0","master_site":"AMB","unit":unit,
                    "countries":["R0"],"retained_site_ids":sites,"n_sites":3,
                    "complete_years":list(range(2000,2012)),
                    "n_complete_years":12,"calendar_span_years":12,
                })
            for site in [f"AMB-s{j}" for j in range(3)]:
                resolution_rows.append({
                    "species":"sp0","MasterSite":"AMB","SiteID":site,
                    "stable_identity":"true","mutually_exclusive_child":"true",
                    "overlaps_parent_or_sibling":"false",
                    "boundary_change_during_panel":"false",
                    "retired_or_replaced":"false","notes":"",
                })

            support=root/"support.json"
            support.write_text(json.dumps({
                "eligible_panels":panels,
                "decision":{"structural_gate_passed":True},
            }))
            resolution=root/"identity.csv"
            pd.DataFrame(resolution_rows).to_csv(resolution,index=False)

            out=run_identity_gate(support,resolution)
            self.assertTrue(out["decision"]["structural_gate_passed"])
            self.assertEqual(out["eligible_panel_count"],20)
            self.assertFalse(any(p["master_site"]=="AMB" for p in out["eligible_panels"]))
            self.assertTrue(out["excluded_multi_unit_masterSites"])


if __name__=="__main__":
    unittest.main()
