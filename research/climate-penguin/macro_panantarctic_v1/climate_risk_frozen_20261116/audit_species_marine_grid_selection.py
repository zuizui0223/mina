#!/usr/bin/env python3
"""Audit species differences in future SIC exposure caused by grid-distance selection.

Source-backed, physical-only geography QA. Do not interpret 'within 50 km
of model wet-grid-cell center' as a penguin foraging range, a climate refuge,
independent climate realizations, future nest counts or biological adaptation.

Inputs are exactly the same original 595-site CMIP6 Zarr derived physical
delta artifact and 2456 original historical nest counts as the prior 271-site
exposure decomposition. Do not impute unmeasured sites or species as zero.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from derive_species_geographic_exposure_decomposition import (
    MAIN, MODS, SP, audit_counts, mean, original_cmip6
)

COHORTS = ("all_counted_species_sites", "all3_marine50_pass", "all3_marine50_fail")
SOURCES = ("three_model_equal_mean",) + MODS


def weighted_group(g, name):
    w = g.source_observed_nest_median.to_numpy(dtype=float)
    vals = g.physical_sic_delta_pp.to_numpy(dtype=float)
    n = float(w.sum())
    assert np.isfinite(vals).all() and np.isfinite(w).all() and (w >= 0).all()
    return dict(
        group=name,
        n_species_sites=len(g),
        n_distinct_site_ids=g.site_id.nunique(),
        n_original_regions=g.source_region.nunique(),
        total_species_nest_median_proxy=n,
        sic_weighted_delta_pp=float(np.average(vals, weights=w)) if n > 0 else None,
    )


def calc(physical, species, obs):
    assert (len(physical), physical.site_id.nunique()) == (21420,595)
    assert set(physical.source_id) == set(MODS)
    assert set(physical.variable_id) == {"siconc","sos","tas"}
    assert physical.complete_years.eq(20).all()
    assert not physical.duplicated(
        ["site_id","source_id","variable_id","experiment_id","period"]
    ).any()
    assert not species.duplicated(["site_id","species"]).any()

    # The spatial screening was originally defined for all three models
    # and BOTH marine fields. Re-validate exact site ID agreement against
    # an independently calculated sea-ice-only model grid mask.
    coastal = physical.loc[physical.variable_id.isin(["siconc","sos"]),
                            ["site_id","source_id","variable_id","distance_km"]].drop_duplicates()
    assert len(coastal)==595*3*2
    pairs = coastal.groupby("site_id").distance_km
    both_ok = pairs.max().le(50).rename("marine50_both_variables")
    sic_only = coastal[coastal.variable_id.eq("siconc")].groupby(
        "site_id").distance_km.max().le(50)
    orig = obs.merge(both_ok,on="site_id",validate="one_to_one")
    orig = orig.merge(sic_only.rename("marine50_sic_only"),on="site_id",validate="one_to_one")
    # Fail rather than silently mixing two distinct spatial support definitions.
    assert (orig.marine50_both_variables == orig.marine50_sic_only).all(), (
        "50-km BOTH-marine mask differs from SIC-only source support"
    )
    assert (len(orig), int(orig.marine50_both_variables.sum()))==(271,158)
    assert orig.site_id.is_unique

    s = species.merge(
        orig[["site_id","source_region","marine50_both_variables"]],
        on="site_id",validate="many_to_one"
    )
    assert len(s)==331

    delta = physical.loc[physical.variable_id.eq("siconc")].copy()
    assert len(delta)==595*3*4
    ensemble = delta.groupby(
        ["site_id","experiment_id","period"],as_index=False
    ).change.mean()
    ensemble["source_id"]="three_model_equal_mean"
    source = pd.concat([
        ensemble[["site_id","experiment_id","period","source_id","change"]],
        delta[["site_id","experiment_id","period","source_id","change"]],
    ], ignore_index=True)
    assert len(source)==595*4*4

    rows=[]
    geo=[]
    for (scenario,period,model),x in source.groupby(
        ["experiment_id","period","source_id"],sort=True
    ):
        assert len(x)==595
        z=s.merge(x[["site_id","change"]].rename(columns={"change":"physical_sic_delta_pp"}),
                  on="site_id",validate="many_to_one")
        assert len(z)==331
        for sp in SP:
            q=z[z.species.eq(sp)]
            near=q[q.marine50_both_variables]
            far=q[~q.marine50_both_variables]
            all_g=weighted_group(q,COHORTS[0])
            near_g=weighted_group(near,COHORTS[1])
            far_g=weighted_group(far,COHORTS[2])
            assert all_g["sic_weighted_delta_pp"] is not None
            assert near_g["sic_weighted_delta_pp"] is not None
            assert far_g["sic_weighted_delta_pp"] is not None

            ws=all_g["total_species_nest_median_proxy"]
            pn=near_g["total_species_nest_median_proxy"]/ws
            pf=far_g["total_species_nest_median_proxy"]/ws
            assert abs(pn+pf-1)<1e-12
            assert all_g["n_species_sites"]==(near_g["n_species_sites"]+far_g["n_species_sites"])
            all_delta=all_g["sic_weighted_delta_pp"]
            near_delta=near_g["sic_weighted_delta_pp"]
            far_delta=far_g["sic_weighted_delta_pp"]
            assert abs(all_delta - (pn*near_delta+pf*far_delta))<1e-10
            coverage_shift = near_delta-all_delta
            excluded_contribution = pf*(near_delta-far_delta)
            assert abs(coverage_shift-excluded_contribution)<1e-10

            row=dict(
                experiment=scenario,period=period,model=model,species=sp,
                n_full_sites=all_g["n_species_sites"],
                n_marine50_sites=near_g["n_species_sites"],
                n_excluded_sites=far_g["n_species_sites"],
                n_regions_full=all_g["n_original_regions"],
                n_regions_marine50=near_g["n_original_regions"],
                sum_original_species_nest_medians=ws,
                sum_marine50_nest_medians=near_g["total_species_nest_median_proxy"],
                sum_excluded_nest_medians=far_g["total_species_nest_median_proxy"],
                marine50_species_site_fraction=near_g["n_species_sites"]/all_g["n_species_sites"],
                marine50_species_nest_proxy_fraction=pn,
                excluded_species_nest_proxy_fraction=pf,
                full_species_sic_delta_pp=all_delta,
                marine50_species_sic_delta_pp=near_delta,
                excluded_species_sic_delta_pp=far_delta,
                marine50_minus_full_delta_pp=coverage_shift,
                excluded_group_contribution_to_selection_pp=excluded_contribution,
                physical_only_no_demographic_forecast=True
            )
            rows.append(row)
            if (scenario,period)==MAIN and model=="three_model_equal_mean":
                for label,sub in [(COHORTS[1],near),(COHORTS[2],far)]:
                    for region,r in sub.groupby("source_region"):
                        weight=float(r.source_observed_nest_median.sum())
                        geo.append({
                            "species":sp,"region":region,"support":label,
                            "n_observed_species_sites":len(r),
                            "n_species_nest_median_proxy":weight,
                            "fraction_of_all_species_nests":weight/ws,
                            "sic_pp_when_positive_nest_weight":(
                                mean(r.physical_sic_delta_pp,r.source_observed_nest_median)
                                if weight>0 else None),
                            "contribution_to_whole_species_sic_pp":(
                                float((r.source_observed_nest_median*r.physical_sic_delta_pp).sum()/ws)
                            ),
                            "region_has_zero_observed_nest_proxy_weight":weight==0,
                        })
    result = pd.DataFrame(rows).sort_values(
        ["experiment","period","model","species"]
    ).reset_index(drop=True)
    assert len(result)==4*4*3
    zone = pd.DataFrame(geo).sort_values(["species","support","region"])
    # Strict independent anchor against previous original 271 and 158 site
    # species-specific physical exposure; no supplied old response coefficients.
    old = {"ADPE":(-11.255590902359002,-10.652460494928887),
           "CHPE":(-17.53353708343837,-15.872451220324917),
           "GEPE":(-34.839065958067366,-18.779299013693276)}
    focus=result[
        (result.experiment==MAIN[0])&(result.period==MAIN[1])&
        (result.model=="three_model_equal_mean")
    ]
    assert len(focus)==3
    for sp,(full,near) in old.items():
        r=focus[focus.species.eq(sp)].iloc[0]
        assert abs(r.full_species_sic_delta_pp-full)<1e-10
        assert abs(r.marine50_species_sic_delta_pp-near)<1e-10
    assert result.groupby(["experiment","period","model"]).size().eq(3).all()
    return result,zone,focus


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--counts",required=True,type=Path)
    p.add_argument("--inventory",required=True,type=Path)
    p.add_argument("--cmip6-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)

    original_count=pd.read_csv(a.counts)
    inventory=pd.read_csv(a.inventory)
    physical=original_cmip6(a.cmip6_zip)
    species,obs=audit_counts(original_count,inventory)
    result,geo,focus=calc(physical,species,obs)
    result.to_csv(a.out/"species_50km_support_selection_all_models_scenarios.csv",index=False)
    geo.to_csv(a.out/"species_50km_support_selection_regions_main.csv",index=False)

    def serialize(row):
        return {k:(None if pd.isna(v) else (v.item() if isinstance(v,np.generic) else v))
                for k,v in row.items()}

    # Explicit excluded-region concentration: avoid an unsupported conclusion
    # that the 50km screen is geographically neutral or representative.
    excluded_top_regions={}
    for sp in SP:
        bad=geo[(geo.species.eq(sp)) & (geo.support.eq(COHORTS[2]))].sort_values(
            ["n_species_nest_median_proxy","region"],ascending=[False,True]
        )
        excluded_top_regions[sp]=[
            dict(region=str(z.region),
                 n_species_sites=int(z.n_observed_species_sites),
                 excluded_source_nest_proxy=float(z.n_species_nest_median_proxy),
                 fraction_of_all_species_nest_proxy=float(z.fraction_of_all_species_nests),
                 mean_sic_pp_if_positive_weight=(
                     None if pd.isna(z.sic_pp_when_positive_nest_weight)
                     else float(z.sic_pp_when_positive_nest_weight)))
            for z in bad.head(8).itertuples(index=False)
        ]
    receipt={
        "status":"PASS_SOURCE_SPECIES_MARINE50_COVERAGE_SELECTION_PHYSICAL_ONLY",
        "n_original_source_sites":595,
        "n_sites_with_observed_2011_2020_nests":271,
        "n_both_marine50_sites":158,
        "n_source_species_medians":331,
        "n_cmip6_original_rows":21420,
        "n_species_model_scenario_rows":len(result),
        "n_original_source_regions":obs.source_region.nunique(),
        "n_source_models":3,
        "original_count_sha256":hashlib.sha256(a.counts.read_bytes()).hexdigest(),
        "original_inventory_sha256":hashlib.sha256(a.inventory.read_bytes()).hexdigest(),
        "original_cmip6_zip_sha256":hashlib.sha256(a.cmip6_zip.read_bytes()).hexdigest(),
        "main_ssp585_late_century":[serialize(x) for x in focus.to_dict("records")],
        "top_excluded_source_regions_by_species":excluded_top_regions,
        "uncertainty_statement":"Three chosen model members, not probabilistic scenario/ensemble confidence interval",
        "grid50km_is_model_cell_proximity_not_penguin_foraging_range":True,
        "no_unobserved_nests_or_species_imputed":True,
        "no_future_nests_or_species_vulnerability_estimated":True,
    }
    (a.out/"species_50km_source_selection_receipt.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n"
    )
    print("PASS_SOURCE_SPECIES_MARINE50_SELECTION="+json.dumps({
        "status":receipt["status"],
        "main_ssp585_late_century":receipt["main_ssp585_late_century"],
        "top_excluded_source_regions_by_species":excluded_top_regions
    },ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
