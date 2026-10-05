import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.gate_smp_spatial_recovery_hysteresis_support_v1 import (
    completed_spells_for_site,
    consecutive_blocks,
    containing_block,
    validate_zero_semantics,
)
from scripts.run_smp_spatial_recovery_hysteresis_v1 import (
    build_panel_cache,
    hierarchical_means,
    prepare_count_frame,
    shifted_spell_H,
    sign_flip_test,
    spell_effect,
    structured_phase_null,
)


class HysteresisTests(unittest.TestCase):

    def test_zero_semantics_confirmation_is_required(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"zero.json"
            p.write_text(json.dumps({
                "row_with_direct_count_zero_is_surveyed_nil": True,
                "absent_site_year_row_is_not_zero": True,
                "estimated_or_imputed_zero_excluded_from_primary": True,
                "confirmation_source": "BTO provider email 2026-10-05",
                "compatible_start_year": 1986,
                "compatible_end_year": 2024,
                "compatible_record_family_or_era": "direct Whole Colony Counts",
            }),encoding="utf-8")
            out=validate_zero_semantics(p)
            self.assertTrue(out["row_with_direct_count_zero_is_surveyed_nil"])
            self.assertTrue(out["absent_site_year_row_is_not_zero"])
            self.assertTrue(out["estimated_or_imputed_zero_excluded_from_primary"])
            self.assertTrue(out["confirmation_source"])

    def test_zero_semantics_rejects_unconfirmed_zero(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"zero.json"
            p.write_text(json.dumps({
                "row_with_direct_count_zero_is_surveyed_nil": False,
                "absent_site_year_row_is_not_zero": True,
                "estimated_or_imputed_zero_excluded_from_primary": True,
                "confirmation_source": "unconfirmed",
                "compatible_start_year": 1986,
                "compatible_end_year": 2024,
                "compatible_record_family_or_era": "direct Whole Colony Counts",
            }),encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_zero_semantics(p)


    def test_zero_semantics_rejects_missing_scope(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"zero.json"
            p.write_text(json.dumps({
                "row_with_direct_count_zero_is_surveyed_nil": True,
                "absent_site_year_row_is_not_zero": True,
                "estimated_or_imputed_zero_excluded_from_primary": True,
                "confirmation_source": "provider statement",
                "compatible_start_year": None,
                "compatible_end_year": None,
                "compatible_record_family_or_era": "",
            }),encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_zero_semantics(p)

    def test_completed_spell_requires_consecutive_zero_run(self):
        years=[2000,2001,2002,2003,2004]
        states=["observed_positive","explicit_zero","explicit_zero","observed_positive","observed_positive"]
        out=completed_spells_for_site(years,states)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]["abandon_from"],2000)
        self.assertEqual(out[0]["recolonize_to"],2003)


    def test_immediate_reabandonment_yields_two_spells(self):
        years=[2000,2001,2002,2003,2004]
        states=[
            "observed_positive",
            "explicit_zero",
            "observed_positive",
            "explicit_zero",
            "observed_positive",
        ]
        out=completed_spells_for_site(years,states)
        self.assertEqual(len(out),2)
        self.assertEqual(out[0]["abandon_from"],2000)
        self.assertEqual(out[0]["recolonize_to"],2002)
        self.assertEqual(out[1]["abandon_from"],2002)
        self.assertEqual(out[1]["recolonize_to"],2004)

    def test_gap_breaks_spell(self):
        years=[2000,2001,2003]
        states=["observed_positive","explicit_zero","observed_positive"]
        self.assertEqual(completed_spells_for_site(years,states),[])

    def test_consecutive_block_assignment(self):
        blocks=consecutive_blocks([2000,2001,2002,2005,2006,2007,2008,2009,2010])
        self.assertEqual(blocks,[[2000,2001,2002],[2005,2006,2007,2008,2009,2010]])
        sp={"abandon_from":2006,"recolonize_to":2009}
        self.assertEqual(containing_block([2000,2001,2002,2005,2006,2007,2008,2009,2010],sp),
                         [2005,2006,2007,2008,2009,2010])

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

    def test_species_balanced_hierarchy(self):
        rows=[]
        for s in range(6):
            for m in range(2):
                rows.append({
                    "species":f"sp{s}",
                    "master_site":f"M{s}-{m}",
                    "site_id":f"S{s}-{m}",
                    "H":0.2+0.01*s,
                })
        h=hierarchical_means(pd.DataFrame(rows))
        self.assertGreater(h["T"],0)
        self.assertEqual(len(h["species"]),6)

    def test_exact_sign_flip_for_six_positive_species(self):
        out=sign_flip_test(np.array([1,1,1,1,1,1],float))
        self.assertEqual(out["mode"],"exact")
        self.assertAlmostEqual(out["one_sided_p"],1/64)


    def test_stage_c_cache_uses_only_stage_b_frozen_years(self):
        x = pd.DataFrame([
            {
                "_species": "sp1",
                "_master": "M1",
                "_master_norm": "m1",
                "_unit": "AON",
                "_site_id": site,
                "year": year,
                "_count": float(10 + year - 2000 + j),
            }
            for year in range(2000, 2006)
            for j, site in enumerate(["s1", "s2", "s3"])
        ])
        structural = {
            "eligible_panels": [{
                "species": "sp1",
                "master_site": "M1",
                "unit": "AON",
                "retained_site_ids": ["s1", "s2", "s3"],
                "complete_years": list(range(2000, 2006)),
            }]
        }
        spells = [{
            "species": "sp1",
            "master_site": "M1",
            "unit": "AON",
            "site_id": "s1",
            "state_complete_years": [2001, 2002, 2003, 2004],
        }]
        cache = build_panel_cache(x, structural, spells)
        mat = cache[("sp1", "m1", "AON")]
        self.assertEqual(list(mat.index), [2001, 2002, 2003, 2004])

    def test_stage_c_cache_rejects_missing_count_only_inside_frozen_support(self):
        x = pd.DataFrame([
            {
                "_species": "sp1",
                "_master": "M1",
                "_master_norm": "m1",
                "_unit": "AON",
                "_site_id": site,
                "year": year,
                "_count": (float("nan") if (year == 2003 and site == "s2") else 10.0),
            }
            for year in range(2000, 2006)
            for site in ["s1", "s2", "s3"]
        ])
        structural = {
            "eligible_panels": [{
                "species": "sp1",
                "master_site": "M1",
                "unit": "AON",
                "retained_site_ids": ["s1", "s2", "s3"],
                "complete_years": list(range(2000, 2006)),
            }]
        }
        spells = [{
            "species": "sp1",
            "master_site": "M1",
            "unit": "AON",
            "site_id": "s1",
            "state_complete_years": [2000, 2001, 2002],
        }]
        # The invalid 2003 count is outside Stage-B-frozen support and must not fail.
        cache = build_panel_cache(x, structural, spells)
        self.assertEqual(list(cache[("sp1", "m1", "AON")].index), [2000, 2001, 2002])

        spells_bad = [{
            "species": "sp1",
            "master_site": "M1",
            "unit": "AON",
            "site_id": "s1",
            "state_complete_years": [2001, 2002, 2003],
        }]
        with self.assertRaises(ValueError):
            build_panel_cache(x, structural, spells_bad)

    def test_zero_phase_shift_equals_observed_spell_effect(self):
        years=list(range(2000,2006))
        mat=pd.DataFrame(
            {
                "focal":[8,0,0,4,5,6],
                "other1":[10,12,14,16,18,20],
                "other2":[5,6,7,8,9,10],
            },
            index=years,
        )
        sp={
            "abandon_from":2000,
            "abandon_to":2001,
            "recolonize_from":2002,
            "recolonize_to":2003,
            "phase_block_start":2000,
            "phase_block_end":2005,
            "phase_block_years":years,
        }
        observed=spell_effect(mat,"focal",sp)["H"]
        shifted=shifted_spell_H(mat,"focal",sp,0)
        self.assertAlmostEqual(observed,shifted)

    def test_structured_phase_null_returns_frozen_summary(self):
        years=list(range(2000,2006))
        cache={}
        spells=[]
        observed_rows=[]
        for s in range(5):
            species=f"sp{s}"
            master=f"M{s}"
            unit="AON"
            mat=pd.DataFrame(
                {
                    "focal":[5,0,0,4,5,6],
                    "other1":[10,12,18,25,28,30],
                    "other2":[8,9,12,16,18,20],
                },
                index=years,
            )
            key=(species,master.lower(),unit)
            cache[key]=mat
            sp={
                "species":species,
                "master_site":master,
                "unit":unit,
                "site_id":"focal",
                "abandon_from":2000,
                "abandon_to":2001,
                "recolonize_from":2002,
                "recolonize_to":2003,
                "phase_block_start":2000,
                "phase_block_end":2005,
                "phase_block_years":years,
            }
            spells.append(sp)
            H=spell_effect(mat,"focal",sp)["H"]
            observed_rows.append({
                "species":species,
                "master_site":master,
                "site_id":"focal",
                "H":H,
            })
        out=structured_phase_null(pd.DataFrame(observed_rows),spells,cache,B=200,seed=42)
        self.assertEqual(out["resamples"],200)
        self.assertEqual(out["distinct_phase_blocks"],5)
        self.assertIn("upper_tail_p",out)
        self.assertIn("delta_phase_observed_minus_median",out)


if __name__=="__main__":
    unittest.main()
