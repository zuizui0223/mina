#!/usr/bin/env python3
"""Original source biological co-census climate PC1/PC2 with site and YEAR FE.

Frisch-Waugh-Lovell on only actually observed same-year 2-species nesting.
The fixed-year control is post-result source sensitivity, NOT a causal salinity
effect, a biologically privileged estimate, or valid future count prediction.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from analyze_original_588_18region_marine_pca import readcsv, writecsv
from test_dual_marine_axis_paired_penguin_response import (
    equal_site_within_two_axes, EXPECTED_ORIGINAL_PAIR_ROWS, TARGET
)

SOURCE_EXPECTED_BASELINE_COEF={
    "ADPE__GEPE":(-0.11320342609617592,+0.06752990948753577),
    "CHPE__GEPE":(+0.0698008153327617,-0.18706554658934277),
    "ADPE__CHPE":(+0.053715003694226986,+0.0549120780934726),
}
PREDICTORS=("PC1_warm_low_ice_global_source_SD","PC2_saline_global_source_SD")
RESPONSE="observed_log1p_second_minus_first_nest_ratio"


def sign(v,threshold=1e-9):
    if v is None:return "UNIDENTIFIED"
    return "POSITIVE" if v>threshold else "NEGATIVE" if v<-threshold else "NEAR_ZERO"


def source_year_graph_components(rows):
    parent={}
    def find(x):
        if x not in parent:parent[x]=x
        if parent[x]!=x:parent[x]=find(parent[x])
        return parent[x]
    def union(a,b):
        a=find(a);b=find(b)
        if a!=b:parent[b]=a
    for r in rows:
        union("s:"+r["site_id"],"y:"+str(r["year"]))
    groups=defaultdict(set)
    for k in list(parent):groups[find(k)].add(k)
    n_sites_per_year=Counter(r["year"] for r in rows)
    return {
        "n_components":len(groups),
        "n_components_with_2plus_original_census_sites":
            sum(sum(k.startswith("s:") for k in q)>=2 for q in groups.values()),
        "n_years_observed_from_2plus_original_source_colonies":
            sum(v>=2 for v in n_sites_per_year.values()),
        "n_years_with_only_one_real_cocensus_colony":
            sum(v==1 for v in n_sites_per_year.values()),
        "calendar_years":sorted(n_sites_per_year)
    }


def FWL_twice(rows):
    grouped=defaultdict(list)
    for r in rows:grouped[r["site_id"]].append(r)
    panel=[r for r in rows if len(grouped[r["site_id"]])>=2]
    sites=sorted({r["site_id"] for r in panel})
    years=sorted({int(r["year"]) for r in panel})
    result={
        "n_actual_same_site_same_season_source_count_records":len(rows),
        "n_repeated_siteyear_rows_used":len(panel),
        "n_repeated_original_colony_sites":len(sites),
        "n_source_regions_repeated":len({r["source_region"] for r in panel}),
        "n_original_250km_blocks_repeated":len({r["source_250km_block"] for r in panel}),
        "n_actual_source_years":len(years),
        "actual_years_span":[years[0],years[-1]] if years else None,
        "model":"equal-colony weighted site + global calendar-year FE, two fixed original climate PC scores",
        "source_sites_and_calendar_years_are_not_independent_climate_or_population_trials":True,
    }
    if len(panel)<12 or len(sites)<3 or len(years)<4:
        result["status"]="SOURCE_TOO_FEW_REPEATED_COCENSUS_SITES_OR_YEARS"
        return result
    result.update(source_year_graph_components(panel))
    nx=len(panel)
    # Every site contributes one unit of total squared-error weight.
    wt=np.asarray([1.0/len(grouped[r["site_id"]]) for r in panel],dtype=float)
    sw=np.sqrt(wt)
    # Full site dummies + years except earliest ensure an identifiable
    # reference in each connected bipartite site-year component.
    nuisance=np.zeros((nx,len(sites)+len(years)-1),dtype=float)
    where_site={name:i for i,name in enumerate(sites)}
    where_year={year:i for i,year in enumerate(years[1:])}
    for ix,r in enumerate(panel):
        nuisance[ix,where_site[r["site_id"]]]=1.0
        year=int(r["year"])
        if year in where_year:
            nuisance[ix,len(sites)+where_year[year]]=1.0
    Dw=nuisance*sw[:,None]
    Yw=np.asarray([r[RESPONSE] for r in panel],dtype=float)*sw
    Xw=np.asarray([[r[k] for k in PREDICTORS] for r in panel],
                  dtype=float)*sw[:,None]
    rankD=int(np.linalg.matrix_rank(Dw))
    residY=Yw-Dw@np.linalg.lstsq(Dw,Yw,rcond=None)[0]
    residX=Xw-Dw@np.linalg.lstsq(Dw,Xw,rcond=None)[0]
    rankX=int(np.linalg.matrix_rank(residX))
    effective_df=nx-rankD-rankX
    result["fixed_effect_source_nuisance_rank"]=rankD
    result["source_partialled_original_2PC_rank"]=rankX
    result["effective_unclustered_residual_degrees_of_freedom_NOT_INDEPENDENT"]=effective_df
    result["n_nonzero_calendar_year_dummies"]=len(years)-1
    result["year_FWL_PC_design_condition_number"]=float(np.linalg.cond(residX)) if rankX==2 else None
    if rankX<2 or effective_df<5:
        result["status"]="SOURCE_SITE_AND_YEAR_EFFECTS_LEAVE_NO_TWO_PC_RESIDUAL_SUPPORT"
        return result
    beta=np.linalg.lstsq(residX,residY,rcond=None)[0]
    resid=residY-residX@beta
    ss=float(residY@residY)
    result.update({
        "status":"POST_RESULT_DESCRIPTIVE_SITE_AND_YEAR_FWL_TWO_SOURCE_MARINE_PCS",
        "PC1_warm_low_ice_coef_per_original_global_source_SD":float(beta[0]),
        "PC2_saline_coef_per_original_global_source_SD":float(beta[1]),
        "PC1_sign":sign(float(beta[0])),
        "PC2_sign":sign(float(beta[1])),
        "source_year_and_site_partialled_in_sample_R2_NOT_FORECAST":
            float(1-(resid@resid)/ss) if ss>1e-14 else None,
        "source_calendar_year_fixed_effects_also_remove_real_shared_climate_signal":True,
    })
    return result


def geographic_year_FWL_sensitivity(rows,original_fit,source_group):
    """Delete every original region or polar250km source block, one at a time.

    This is post-result geography diagnostics, never a spatially independent
    confidence interval or external validation of selected candidate biology.
    """
    checks=[]
    for omitted in sorted({r[source_group] for r in rows}):
        kept=[r for r in rows if r[source_group]!=omitted]
        fit=FWL_twice(kept)
        checks.append({
            "deleted_source_unit_type":source_group,
            "deleted_original_source_unit":omitted,
            "n_remaining_actual_both_species_count_records":len(kept),
            "status":fit["status"],
            "n_repeat_colonies":fit.get("n_repeated_original_colony_sites"),
            "n_source_regions":fit.get("n_source_regions_repeated"),
            "n_source_blocks":fit.get("n_original_250km_blocks_repeated"),
            "PC1_year_adjusted_coef":fit.get(
                "PC1_warm_low_ice_coef_per_original_global_source_SD"),
            "PC2_year_adjusted_coef":fit.get(
                "PC2_saline_coef_per_original_global_source_SD"),
        })
    success=[r for r in checks if r["status"]==
             "POST_RESULT_DESCRIPTIVE_SITE_AND_YEAR_FWL_TWO_SOURCE_MARINE_PCS"]
    def pkey(axis):
        return "PC1_warm_low_ice_coef_per_original_global_source_SD" if axis==1 \
            else "PC2_saline_coef_per_original_global_source_SD"
    def summary(axis):
        vals=[r[f"PC{axis}_year_adjusted_coef"] for r in success]
        original=original_fit.get(pkey(axis))
        return {
            "n_fitted_source_geographic_omissions":len(vals),
            "n_source_geographic_omission_units":len(checks),
            "coefficient_sign_original":sign(original),
            "coefficient_delete_unit_min":min(vals) if vals else None,
            "coefficient_delete_unit_max":max(vals) if vals else None,
            "every_original_unit_omission_supported":len(vals)==len(checks),
            "every_supported_omission_preserves_original_sign":
                bool(original is not None and len(vals)==len(checks)
                     and all(sign(v)==sign(original) and sign(original)!="NEAR_ZERO"
                             for v in vals))
        }
    return {
        "source_unit_type":source_group,
        "PC1":summary(1),
        "PC2":summary(2),
        "original_omissions":checks,
        "post_result_diagnostic_not_independent_replication":True
    }


def run(args):
    raw=readcsv(args.input)
    if len(raw)!=sum(EXPECTED_ORIGINAL_PAIR_ROWS.values()):
        raise ValueError("Original 351 source co-census census universe changed")
    groups=defaultdict(list)
    for r in raw:
        groups[r["species_pair"]].append({
            **r,
            "year":int(r["year"]),
            "original_real_zero_in_either_species":
                str(r["original_real_zero_in_either_species"]).lower()=="true",
            "source_same_count_method_both_species":
                str(r["source_same_count_method_both_species"]).lower()=="true",
            **{k:float(r[k]) for k in (*PREDICTORS,RESPONSE)},
        })
    if {k:len(v) for k,v in groups.items()}!=EXPECTED_ORIGINAL_PAIR_ROWS:
        raise ValueError("Original same-site/year source species pair counts drift")
    out={}
    tables=[]
    for pair in EXPECTED_ORIGINAL_PAIR_ROWS:
        allpairs=groups[pair]
        same=[r for r in allpairs if r["source_same_count_method_both_species"]]
        nozeros=[r for r in same if not r["original_real_zero_in_either_species"]]
        within_original=equal_site_within_two_axes(same)
        expected=SOURCE_EXPECTED_BASELINE_COEF[pair]
        if (abs(within_original["PC1_warm_low_ice_coef_per_original_global_source_SD"]-expected[0])>1e-10
                or abs(within_original["PC2_saline_coef_per_original_global_source_SD"]-expected[1])>1e-10):
            raise ValueError("Original source PCA dual-axis site-only coefficient not reproduced")
        same_year=FWL_twice(same)
        sensitivity=FWL_twice(nozeros)
        geo_year={
            "source_region":geographic_year_FWL_sensitivity(
                same,same_year,"source_region"),
            "source_250km_block":geographic_year_FWL_sensitivity(
                same,same_year,"source_250km_block")
        }
        values={
            "species_pair":pair,
            "same_original_recorded_survey_method_co_count_source_records":len(same),
            "zero_nest_free_original_dual_count_source_records":len(nozeros),
            "site_only_original_2PC_baseline":{
                "site_count":within_original["n_repeated_colony_sites"],
                "rows":within_original["n_repeated_real_cocensus_siteyears"],
                "PC1_coef_per_original_global_SD":expected[0],
                "PC2_coef_per_original_global_SD":expected[1],
                "source_site_only_in_sample_R2":within_original["within_sample_explained_residual_fraction_NOT_A_FORECAST"],
                "PC2_baseline_sign":sign(expected[1]),
            },
            "source_site_and_calendar_year_fixed_effects":same_year,
            "original_region_and_250km_block_delete_one_source_sensitivity":geo_year,
            "actual_recorded_zero_free_site_and_calendar_year_sensitivity":sensitivity,
            "physical_2PC_was_fitted_without_penguin_counts":True,
            "siteyear_pseudoreplication_does_not_permit_simple_pvalues":True,
            "year_FE_is_negative_control_not_prospective_historical_response":True,
            "site_fixed_calendar_year_FE_is_not_a_calibrated_salinity_or_ice_causal_effect":True
        }
        out[pair]=values
        tables.append({
            "species_pair":pair,
            "source_count_record_rows":len(allpairs),
            "same_method_rows":len(same),
            "source_real_zero_excluded_rows":len(same)-len(nozeros),
            "site_only_PC1":expected[0],"site_only_PC2":expected[1],
            "site_plus_year_PC1":same_year.get("PC1_warm_low_ice_coef_per_original_global_source_SD"),
            "site_plus_year_PC2":same_year.get("PC2_saline_coef_per_original_global_source_SD"),
            "site_plus_year_years_with_2plus_cocensus_sites":
                same_year.get("n_years_observed_from_2plus_original_source_colonies"),
            "site_plus_year_effective_unclustered_resid_df":
                same_year.get("effective_unclustered_residual_degrees_of_freedom_NOT_INDEPENDENT"),
            "site_plus_year_source_status":same_year["status"],
            "site_plus_year_PC2_region_delete_range":[
                geo_year["source_region"]["PC2"]["coefficient_delete_unit_min"],
                geo_year["source_region"]["PC2"]["coefficient_delete_unit_max"]],
            "site_plus_year_PC2_block_delete_range":[
                geo_year["source_250km_block"]["PC2"]["coefficient_delete_unit_min"],
                geo_year["source_250km_block"]["PC2"]["coefficient_delete_unit_max"]],
            "site_plus_year_PC2_stable_under_all_source_region_omissions":
                geo_year["source_region"]["PC2"]["every_supported_omission_preserves_original_sign"],
            "site_plus_year_PC2_stable_under_all_source_250km_block_omissions":
                geo_year["source_250km_block"]["PC2"]["every_supported_omission_preserves_original_sign"],
            "source_zero_free_site_plus_year_PC1":
                sensitivity.get("PC1_warm_low_ice_coef_per_original_global_source_SD"),
            "source_zero_free_site_plus_year_PC2":
                sensitivity.get("PC2_saline_coef_per_original_global_source_SD"),
            "source_zero_free_site_plus_year_status":sensitivity["status"]
        })
    receipt={
        "status":"ORIGINAL_GENUINE_PENGUIN_351_PAIR_SITE_AND_YEAR_FWL_DIAGNOSTIC_COMPLETE",
        "original_input_source":"GitHub Actions 42969734584 351 actual original same-colony same-year 2-species observations",
        "n_original_actual_two_species_siteyear_records":len(raw),
        "genuine_pair_years_not_filled_with_pseudoabsence":True,
        "original_source_site_only_two_axis_coefficient_exactly_reproduced":True,
        "diagnostic_per_species_pair":out,
        "warnings":[
            "Post-result diagnostic motivated by weak salinity PC2 × CHPE/GEPE relative nests association; not preregistered independent confirmation.",
            "Removing global common-year variation could remove genuine biological climate forcing, so it is a conservative descriptive sensitivity and not the true causal effect.",
            "Original source nest counts and marine reanalysis have shared location/year dependencies and counting date/effort uncertainty.",
            "The site+year model uses residual source degrees of freedom, not independent ecological trials or valid inferential p-values.",
            "An observed zero-count can be excluded for sensitivity but must not be recoded as unobserved or a verified local species absence.",
            "No causal ocean salinity driver, 18-region species replacement, warming climate debt or penguin future population forecast is identified."
        ]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    writecsv(args.out/"penguin_dual_original_PC1_PC2_site_year_fixed_effect_coefficient_sensitivity.csv",tables)
    (args.out/"original_351_true_pair_dual_marine_PC1_PC2_site_year_FWL_verdict.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("DUAL_SOURCE_PC1_PC2_WITH_YEAR_EFFECT="+json.dumps(tables,ensure_ascii=False),flush=True)
    print("DUAL_SOURCE_SITEYEAR_SUPPORT="+json.dumps({
        k:{"n":v["same_original_recorded_survey_method_co_count_source_records"],
           "with_year":v["source_site_and_calendar_year_fixed_effects"],
           "without_original_zeros":v["actual_recorded_zero_free_site_and_calendar_year_sensitivity"]}
        for k,v in out.items()},ensure_ascii=False),flush=True)
    print("DUAL_SOURCE_ORIGINAL_REGION_BLOCK_YEAR_FWL="+json.dumps({
        k:{"region":[{"region_omitted":x["deleted_original_source_unit"],
                         "remaining_regions":x["n_source_regions"],
                         "remaining_blocks":x["n_source_blocks"],
                         "PC2":x["PC2_year_adjusted_coef"],
                         "status":x["status"]}
                        for x in v["original_region_and_250km_block_delete_one_source_sensitivity"]
                              ["source_region"]["original_omissions"]],
           "block":[{"block_omitted":x["deleted_original_source_unit"],
                      "PC2":x["PC2_year_adjusted_coef"],
                      "status":x["status"]}
                     for x in v["original_region_and_250km_block_delete_one_source_sensitivity"]
                           ["source_250km_block"]["original_omissions"]]}
        for k,v in out.items()},ensure_ascii=False),flush=True)
    return receipt


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    run(ap.parse_args())


if __name__=="__main__":
    main()
