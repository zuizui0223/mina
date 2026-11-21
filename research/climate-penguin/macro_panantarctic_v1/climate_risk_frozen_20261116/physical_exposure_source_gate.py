#!/usr/bin/env python3
"""Source-gated CMIP6 physical-only ice/temperature exposure, NEVER projected nests.

The archived 3-model CMIP6 input is a same-site co-census cohort of 25 colonies,
not a 595-colony or new 265-site/species pan-Antarctic scenario source.
"""
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

MODELS=("ACCESS-CM2","BCC-CSM2-MR","CESM2")
EXPS=("ssp245","ssp585")
PERIODS=("2041-2060","2081-2100")
VARS=("siconc","tos")
MAX_DISTANCE_KM=50.
YEARS=(2011,2020)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--count-csv",type=Path,required=True)
    p.add_argument("--inventory-csv",type=Path,required=True)
    p.add_argument("--physical-csv",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    c=pd.read_csv(a.count_csv)
    geo=pd.read_csv(a.inventory_csv)
    f=pd.read_csv(a.physical_csv)
    expect=set(MODELS)
    assert set(f.source_id)==expect and set(f.experiment_id)==set(EXPS)
    assert set(f.period)==set(PERIODS) and set(f.variable_id)==set(VARS)
    assert len(f)==600 and f.site_id.nunique()==25
    assert f.groupby(["source_id","experiment_id","period","variable_id"]).site_id.nunique().eq(25).all()
    assert not f.duplicated(["source_id","experiment_id","period","variable_id","site_id"]).any()
    assert set(f.site_id).issubset(set(geo.site_id)) and (f.complete_years==20).all()
    assert f.loc[f.variable_id=="siconc","units"].eq("percent").all()
    assert f[["delta","distance_km","baseline","seasonal_mean"]].notna().all().all()
    assert np.max(np.abs(f.seasonal_mean-f.baseline-f.delta))<1e-8

    baseline=c[c.season.between(*YEARS)].groupby(["site_id","species"],as_index=False).agg(
        median_observed_nests=("observed_nest_count","median"),
        n_real_seasons=("season","nunique"))
    assert not baseline.duplicated(["site_id","species"]).any()
    assert (baseline.median_observed_nests>=0).all()
    weights=baseline.groupby("site_id",as_index=False).agg(
        sum_species_medians_nests_not_synchronous=("median_observed_nests","sum"),
        observed_species=("species","nunique"),
        real_site_species_survey_records=("n_real_seasons","sum"),
        max_observed_seasons=("n_real_seasons","max"))
    weights["strict_two_plus_site_seasons"]=weights.max_observed_seasons.ge(2)
    physical_sites=set(f.site_id)
    weights["in_archived_25_physical_source"]=weights.site_id.isin(physical_sites)
    denom=weights.sum_species_medians_nests_not_synchronous.sum()
    with_physical=weights.loc[weights.in_archived_25_physical_source]
    assert denom>0
    # Actual physical source supports only a western-Peninsula co-census cohort,
    # and some extracted marine pixels are >50km from an original colony.
    frame=f.merge(weights,on="site_id",how="left",validate="many_to_one")
    frame["actual_baseline_count_exists"]=frame.sum_species_medians_nests_not_synchronous.notna()
    frame["wet_model_point_within_50km"]=frame.distance_km.le(MAX_DISTANCE_KM)
    frame["physical_and_baseline_same_site_supported"]=frame.actual_baseline_count_exists & frame.wet_model_point_within_50km
    coverage=[]
    effects=[]
    for (model,ssp,period,var),g in frame.groupby(
            ["source_id","experiment_id","period","variable_id"],sort=True):
        valid=g[g.physical_and_baseline_same_site_supported]
        cover_sids=valid.site_id.nunique()
        weight=valid.sum_species_medians_nests_not_synchronous.to_numpy(float)
        # This is a descriptive within-source physical exposure, not real sampled
        # Antarctic population exposure, future survival or protected-area coverage.
        effects.append({
            "source_id":model,"experiment_id":ssp,"period":period,"variable_id":var,
            "n_archived_physical_site":len(g),
            "n_true_breeding_site_with_known_2011_2020_count_and_50km_wet_match":cover_sids,
            "n_original_595_with_true_2011_2020_count":int(weights.site_id.nunique()),
            "source_subset_nest_median_weight_fraction_of_all_known_observed":float(weight.sum()/denom),
            "site_equal_mean_delta_on_supported_sites":float(valid.delta.mean()) if len(valid) else None,
            "nest_median_weighted_mean_delta_on_supported_sites":float(np.average(valid.delta,weights=weight)) if weight.sum()>0 else None,
            "all_595_source_coverage":False,
            "is_a_future_penguin_nest_change_forecast":False,
            "original_historical_model_delta_used_without_observation_model_bias_replacement":True
        })
        coverage.append({"model":model,"ssp":ssp,"period":period,"variable":var,
           "n_sites_present_in_this_archived_scenario":len(g),
           "n_sites_with_any_real_2011_2020_census":int(g.actual_baseline_count_exists.sum()),
           "n_sites_farther_than_50km":int((~g.wet_model_point_within_50km).sum()),
           "n_valid_source_sites":cover_sids,
           "n_invalid_source_sites":int((~g.physical_and_baseline_same_site_supported).sum())})
    assert len(effects)==24 and len(coverage)==24
    frame.to_csv(a.out_dir/"original_25source_cmip6_model_delta_join_counts.csv",index=False)
    pd.DataFrame(effects).to_csv(a.out_dir/"only_archived_25site_physical_exposure_not_antarctic_population.csv",index=False)
    pd.DataFrame(coverage).to_csv(a.out_dir/"model_site_distance_and_nest_weight_coverage.csv",index=False)
    source_hashes={k:hashlib.sha256(path.read_bytes()).hexdigest() for k,path in {
        "count_csv":a.count_csv,"inventory_csv":a.inventory_csv,"physical_csv":a.physical_csv}.items()}
    verdict={
       "source_status":"STOP_SCENARIO_COVERAGE_NOT_PAN_ANTARCTIC",
       "reason":"Original CMIP6 suite covers only 25 true sites, not the 595 known colonies or proposed new 265 series",
       "input_source_model_n":len(MODELS),"ssp_n":len(EXPS),"period_n":len(PERIODS),
       "variable_n":len(VARS),"source_physical_scenarios":len(f),
       "source_25_cohort_site_ids":sorted(physical_sites),
       "n_known_census_sites_in_2011_2020":int(weights.site_id.nunique()),
       "original_known_site_universe":int(geo.site_id.nunique()),
       "original_2011_2020_site_species_observed_pairs":len(baseline),
       "observed_nested_nest_median_total_not_real_population":float(denom),
       "n_archived_25_with_actual_baseline_nests":int(with_physical.site_id.nunique()),
       "sum_nests_in_archived_25_fraction_of_real_counted_sites":float(
           with_physical.sum_species_medians_nests_not_synchronous.sum()/denom),
       "n_supported_rows_in_24_scenarios":[int(x["n_true_breeding_site_with_known_2011_2020_count_and_50km_wet_match"]) for x in effects],
       "cmip6_is_not_all_antarctica":True,
       "source_neighborhood_265_series_still_unverified":True,
       "no_full_population_risk_map_or_2050_2100_nest_forecast":True,
       "no_official_CCAMLR_MPA_polygon_source_assigned":True,
       "protected_area_overlap_status":"NO_GO_PROTECTION_COVERAGE",
       "historic_25_model_site_exposure_is_only_a_selected_source_pilot":True,
       "source_sha256":source_hashes
    }
    (a.out_dir/"physical_exposure_coverage.json").write_text(json.dumps(verdict,ensure_ascii=False,indent=2)+"\n")
    (a.out_dir/"risk_gate_verdict.json").write_text(json.dumps({
        "source_series_265":"STOP_UNVERIFIED","cmip6_595":"STOP_SCENARIO_COVERAGE",
        "future_nest_number_projection":"STOP_CROSS_SECTIONAL_TO_TEMPORAL_EXTRAPOLATION",
        "protected_area_overlay":"STOP_NO_VERIFIED_POLYGONS",
        "allowed":"Original 25-site subset physical-only model change, explicit source count-weight denominator"
    },ensure_ascii=False,indent=2)+"\n")
    print("PHYSICAL_ONLY_SOURCE_PILOT="+json.dumps(verdict,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
