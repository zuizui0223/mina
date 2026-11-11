#!/usr/bin/env python3
"""Post-result exploratory physical PC1 vs PC2 and true dual-count penguin response.

Only the frozen source-observed 588 original colony×1993–2020 marine time
series and real same-site same-year ADPE/CHPE/GEPE original observed nests.
No ecological absences, habitat inference, p-hacking, or future prediction.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from analyze_original_588_18region_marine_pca import (
    VARIABLES, PAIRS, pca, pearson, slope_year, readcsv, writecsv, flag
)

EXPECTED_CLIMATE_ROWS=588*28
EXPECTED_ORIGINAL_PAIR_ROWS={"ADPE__GEPE":98,"CHPE__GEPE":165,"ADPE__CHPE":88}
EXPECTED_PC1_VAR=0.6036542337658517
EXPECTED_PC2_VAR=0.33377323063920294
EXPECTED_PC1_LOAD=(-0.7073417653855445,-0.0383492862417919,0.7058306873365638)
EXPECTED_PC2_SAL_LOAD=0.9977192916153914
EXPECTED_SOURCE_PC1_TOL=1e-8
MIN_SITE_SLOPE_COUNT=3
MIN_SITE_SLOPE_YEARS=10
TARGET=(("ADPE","GEPE"),("CHPE","GEPE"),("ADPE","CHPE"))


def reconstruct_source_pcs(climate):
    if len(climate)!=EXPECTED_CLIMATE_ROWS:
        raise ValueError("Frozen original complete 588-site 28-year climate source drift")
    siteyears={(r["site_id"],int(r["year"])):r for r in climate}
    if len(siteyears)!=len(climate):
        raise ValueError("Original 588 source climate duplicate site-year")
    if len({r["site_id"] for r in climate})!=588:
        raise ValueError("Original native wet-grid site cohort drift")
    years=Counter(int(r["year"]) for r in climate)
    if any(years.get(y,0)!=588 for y in range(1993,2021)):
        raise ValueError("Full original 1993–2020 calendar missing source values")
    A=np.asarray([[float(r[v]) for v in VARIABLES] for r in climate],dtype=float)
    fit=pca(A)
    if abs(float(fit["explained"][0])-EXPECTED_PC1_VAR)>1e-10 or \
       abs(float(fit["explained"][1])-EXPECTED_PC2_VAR)>1e-10 or \
       max(abs(fit["loadings"][:,0]-np.asarray(EXPECTED_PC1_LOAD)))>1e-10:
        raise ValueError("Published original full 18-region physical axes failed independent reconstruction")
    second=np.asarray(fit["loadings"][:,1],dtype=float)
    if second[1]<0:
        second=-second
    if abs(float(second[1])-EXPECTED_PC2_SAL_LOAD)>1e-10:
        raise ValueError("Original salinity-positive PC2 orientation/source drift")
    PC1=np.asarray(fit["scores"][:,0],dtype=float)
    PC2=((A-fit["means"])/fit["stds"])@second
    if abs(float(np.mean(PC1)))>1e-9 or abs(float(np.mean(PC2)))>1e-9:
        raise ValueError("Original marine physical PCA scores not centered")
    pc1_sd=float(np.std(PC1));pc2_sd=float(np.std(PC2))
    if min(pc1_sd,pc2_sd)<=1e-8:
        raise ValueError("Original marine PC scores not identifiable")
    expanded={}
    maxdiff=0.0
    for r,x1,x2 in zip(climate,PC1,PC2):
        old=float(r["warm_direction_three_var_marine_PCA_score"])
        maxdiff=max(maxdiff,abs(old-float(x1)))
        expanded[r["site_id"],int(r["year"])]={
            "PC1_warm_low_ice_original_score":float(x1),
            "PC2_saline_original_score":float(x2),
            "PC1_global_source_SD":float(x1/pc1_sd),
            "PC2_global_source_SD":float(x2/pc2_sd),
            "source_region":r["source_region"],
            "source_250km_block":r["source_250km_block"],
            "GLORYS_cell":str(r["GLORYS_cell_y"])+":"+str(r["GLORYS_cell_x"])
        }
    if maxdiff>EXPECTED_SOURCE_PC1_TOL:
        raise ValueError("Existing per-site 18-region climate PC1 observations not reproduced")
    return expanded,{
        "original_588_colony_28year_source_rows":len(climate),
        "original_588_unique_sites":588,
        "original_18_source_region_count":len({r["source_region"] for r in climate}),
        "original_378_native_GLORYS_cells":len({(r["GLORYS_cell_y"],r["GLORYS_cell_x"]) for r in climate}),
        "source_PC1_fraction":float(fit["explained"][0]),
        "source_PC2_fraction":float(fit["explained"][1]),
        "source_PC1_loading":dict(zip(VARIABLES,[float(v) for v in fit["loadings"][:,0]])),
        "source_PC2_saline_positive_loading":dict(zip(VARIABLES,[float(v) for v in second])),
        "max_original_archived_PC1_score_difference":maxdiff,
        "source_PC1_score_standard_deviation":pc1_sd,
        "source_PC2_score_standard_deviation":pc2_sd,
        "physical_axis_built_without_species_count_outcomes":True
    }


def biological_rows(original,climate):
    n=Counter(r["species_pair"] for r in original)
    if dict(n)!=EXPECTED_ORIGINAL_PAIR_ROWS:
        raise ValueError("Source original same-year species count pair universe drift")
    records=[];seen=set()
    for r in original:
        site=r["site_id"];year=int(r["season"]);sp=r["species_pair"]
        key=(sp,site,year)
        if key in seen:
            raise ValueError("Duplicate observed original penguin co-census")
        seen.add(key)
        physical=climate.get((site,year))
        if physical is None:
            raise ValueError("Original dual-observed nests missing source 3var marine year")
        for k in ("source_region","source_250km_block"):
            if physical[k]!=r[k]:
                raise ValueError("Original species pair region/geographic block changes")
        prior=float(r["fixed_marine_PC1_original_global_axis"])
        if abs(prior-physical["PC1_warm_low_ice_original_score"])>1e-8:
            raise ValueError("Prior source original co-census 588-site PC1 mismatched")
        a=int(r["nests_first_species_actual_source_count"])
        b=int(r["nests_second_species_actual_source_count"])
        outcome=float(np.log1p(b)-np.log1p(a))
        if abs(outcome-float(r["log1p_second_minus_first_actual_nests"]))>1e-10:
            raise ValueError("Original observed penguin source count log1p ratio mismatch")
        records.append({
            "species_pair":sp,"site_id":site,"year":year,
            "source_region":r["source_region"],
            "source_250km_block":r["source_250km_block"],
            "source_ocean_GLORYS_cell":physical["GLORYS_cell"],
            "actual_nests_first_species":a,"actual_nests_second_species":b,
            "source_same_count_method_both_species":flag(r["original_source_same_method_both_species"]),
            "source_original_method_first":r["original_method_first_species"],
            "source_original_method_second":r["original_method_second_species"],
            "original_real_zero_in_either_species":a==0 or b==0,
            "observed_log1p_second_minus_first_nest_ratio":outcome,
            "PC1_warm_low_ice_global_source_SD":physical["PC1_global_source_SD"],
            "PC2_saline_global_source_SD":physical["PC2_global_source_SD"],
            "source_PC1":physical["PC1_warm_low_ice_original_score"],
            "source_PC2":physical["PC2_saline_original_score"],
            "coobserved_species_not_the_same_as_known_true_absence":True
        })
    return records


def raw_vs_within(rows,key):
    if not rows:
        return {"raw_r":None,"within_site_r":None,"n_records":0,"n_informative_sites":0,
                "n_source_regions":0,"n_250km_blocks":0}
    groups=defaultdict(list)
    for r in rows:groups[r["site_id"]].append(r)
    xx=[];yy=[];informative=[]
    outcome="observed_log1p_second_minus_first_nest_ratio"
    for site,rs in groups.items():
        if len(rs)<2:continue
        informative+=rs
        mx=float(np.mean([r[key] for r in rs]))
        my=float(np.mean([r[outcome] for r in rs]))
        xx.extend([r[key]-mx for r in rs])
        yy.extend([r[outcome]-my for r in rs])
    return {
        "raw_r":pearson([r[key] for r in rows],[r[outcome] for r in rows]),
        "within_site_r":pearson(xx,yy) if len({r["site_id"] for r in informative})>=3 and len(xx)>=5 else None,
        "n_records":len(rows),
        "n_original_colony_sites":len(groups),
        "n_informative_sites":len({r["site_id"] for r in informative}),
        "n_informative_siteyears":len(informative),
        "n_source_regions":len({r["source_region"] for r in informative}),
        "n_250km_blocks":len({r["source_250km_block"] for r in informative}),
        "source_siteyear_pseudoreplication_caution":True
    }


def equal_site_within_two_axes(rows):
    """Within-colony model y~PC1+PC2, each colony contributes weight 1."""
    groups=defaultdict(list)
    for r in rows:groups[r["site_id"]].append(r)
    used={s:v for s,v in groups.items() if len(v)>=2}
    if len(used)<3:return {"status":"INSUFFICIENT_THREE_REPEAT_SITES",
                           "n_repeat_sites":len(used)}
    keys=("PC1_warm_low_ice_global_source_SD","PC2_saline_global_source_SD")
    response="observed_log1p_second_minus_first_nest_ratio"
    xrows=[];ys=[];wts=[]
    for _,obs in sorted(used.items()):
        X=np.asarray([[r[k] for k in keys] for r in obs],dtype=float)
        Y=np.asarray([r[response] for r in obs],dtype=float)
        if len(Y)<2:continue
        xrows.extend(X-X.mean(axis=0))
        ys.extend(Y-Y.mean())
        wts.extend([1/len(obs)]*len(obs))
    X=np.asarray(xrows,dtype=float)
    Y=np.asarray(ys,dtype=float)
    W=np.asarray(wts,dtype=float)
    WX=X*np.sqrt(W[:,None])
    WY=Y*np.sqrt(W)
    if len(Y)<5 or np.linalg.matrix_rank(WX)<2:
        return {"status":"SOURCE_PHYSICAL_AXIS_COLLINEAR_OR_UNDERPOWERED",
                "n_repeat_sites":len(used),"n_rows":len(Y)}
    coef=np.linalg.lstsq(WX,WY,rcond=None)[0]
    resid=WY-WX@coef
    ss=float(WY@WY)
    coefficient={
        "PC1_warm_low_ice_coef_per_original_global_source_SD":float(coef[0]),
        "PC2_saline_coef_per_original_global_source_SD":float(coef[1])
    }
    return {
        "status":"DESCRIPTIVE_ONLY_SAME_SITE_TWO_PHYSICAL_AXIS_ASSOCIATION",
        "n_repeated_colony_sites":len(used),
        "n_repeated_real_cocensus_siteyears":len(Y),
        "n_regions_with_real_repeat_site_cocensus":len({r["source_region"] for rs in used.values() for r in rs}),
        "n_source_250km_blocks_with_real_repeat_site_cocensus":
            len({r["source_250km_block"] for rs in used.values() for r in rs}),
        **coefficient,
        "within_sample_explained_residual_fraction_NOT_A_FORECAST":float(1-(resid@resid)/ss) if ss>1e-12 else None,
        "within_data_weighted_2PC_condition_number":float(np.linalg.cond(WX)),
        "per_colony_total_weight_equal_one":True,
        "no_causal_or_future_population_interpretation":True
    }


def leave_geography_out(rows,field):
    result=[]
    units=sorted({r[field] for r in rows})
    for value in units:
        retained=[r for r in rows if r[field]!=value]
        estimated=equal_site_within_two_axes(retained)
        result.append({
            "unit_type":field,"removed":value,
            "n_records_left":len(retained),
            "n_repeated_colony_sites_left":estimated.get("n_repeated_colony_sites",
                                                          estimated.get("n_repeat_sites")),
            "n_regions_with_repeats_left":estimated.get("n_regions_with_real_repeat_site_cocensus"),
            "n_blocks_with_repeats_left":estimated.get("n_source_250km_blocks_with_real_repeat_site_cocensus"),
            "status":estimated["status"],
            "PC1_coef_per_original_source_SD":
                estimated.get("PC1_warm_low_ice_coef_per_original_global_source_SD"),
            "PC2_coef_per_original_source_SD":
                estimated.get("PC2_saline_coef_per_original_global_source_SD"),
        })
    return result


def slope_per_actual_colony(rows):
    groups=defaultdict(list)
    for r in rows:groups[r["site_id"]].append(r)
    results=[]
    for site,observed in sorted(groups.items()):
        obs=sorted(observed,key=lambda r:r["year"])
        years=[r["year"] for r in obs]
        if (len(obs)<MIN_SITE_SLOPE_COUNT
                or max(years)-min(years)<MIN_SITE_SLOPE_YEARS):
            continue
        source={
            "species_pair":obs[0]["species_pair"],
            "site_id":site,"source_region":obs[0]["source_region"],
            "source_250km_block":obs[0]["source_250km_block"],
            "source_ocean_GLORYS_cell":obs[0]["source_ocean_GLORYS_cell"],
            "n_original_actual_dual_species_count_years":len(obs),
            "first_observed_both_counted_year":min(years),
            "last_observed_both_counted_year":max(years),
            "observed_source_span_years":max(years)-min(years),
            "contains_original_actual_recorded_zero":any(r["original_real_zero_in_either_species"] for r in obs),
            "first_second_species_counts_are_not_census_population_composition_of_unobserved_birds":True
        }
        for var,name in [
           ("observed_log1p_second_minus_first_nest_ratio","observed_nest_logratio_slope_per_decade"),
           ("PC1_warm_low_ice_global_source_SD","marine_PC1_global_SD_slope_per_decade"),
           ("PC2_saline_global_source_SD","marine_PC2_global_SD_slope_per_decade")]:
            source[name]=slope_year([(r["year"],r[var]) for r in obs])
        if any(source[name] is None for name in (
            "observed_nest_logratio_slope_per_decade",
            "marine_PC1_global_SD_slope_per_decade",
            "marine_PC2_global_SD_slope_per_decade")):
            raise AssertionError("Incomplete true original species ratio temporal slopes")
        results.append(source)
    return results


def summary_site_slopes(site_slopes):
    if not site_slopes:
        return {"n_original_site_slopes":0,"enough_independent_regions_for_time_source":False}
    x="observed_nest_logratio_slope_per_decade"
    regions={r["source_region"] for r in site_slopes}
    blocks={r["source_250km_block"] for r in site_slopes}
    cov=[]
    for c in ("marine_PC1_global_SD_slope_per_decade","marine_PC2_global_SD_slope_per_decade"):
        overall=pearson([r[c] for r in site_slopes],[r[x] for r in site_slopes])
        vals=defaultdict(list)
        for r in site_slopes:vals[r["source_region"]].append(r)
        xx=[];yy=[]
        for group in vals.values():
            if len(group)<2:continue
            mu1=np.mean([r[c] for r in group]);mu2=np.mean([r[x] for r in group])
            xx.extend([r[c]-mu1 for r in group])
            yy.extend([r[x]-mu2 for r in group])
        cov.append({
            "marine_predictor_actual_site_slope":c,
            "between_site_original_source_climate_vs_bio_slope_Pearson":overall,
            "source_region_demeaned_original_site_slope_Pearson":
                pearson(xx,yy) if len(xx)>=5 and len(vals)>=2 else None,
            "n_sites_contributing_to_within_region_source_slope":len(xx)
        })
    return {
        "n_original_site_slopes":len(site_slopes),
        "n_original_regions":len(regions),
        "n_original_250km_blocks":len(blocks),
        "n_source_ocean_GLORYS_cells":len({r["source_ocean_GLORYS_cell"] for r in site_slopes}),
        "source_sites_with_actual_zero_censuses":sum(r["contains_original_actual_recorded_zero"] for r in site_slopes),
        "per_axis_relationship":cov,
        "n_sites_with_three_plus_genuinely_co_counted_years_spanning_10plus":len(site_slopes),
        "not_a_time_lag_or_individual_migration_estimate":True
    }


def analyze(args):
    climate=readcsv(args.climate)
    rawpairs=readcsv(args.pairs)
    scores,source=reconstruct_source_pcs(climate)
    rows=biological_rows(rawpairs,scores)
    results={};overall_slopes=[];loo_rows=[]
    for a,b in TARGET:
        key=a+"__"+b
        study=[r for r in rows if r["species_pair"]==key]
        same=[r for r in study if r["source_same_count_method_both_species"]]
        zero_free=[r for r in same if not r["original_real_zero_in_either_species"]]
        marginals={}
        for label,rs in (
            ("original_all_actual_same_site_year_pairs",study),
            ("same_original_survey_method_both_species_primary",same),
            ("same_method_source_records_no_actual_nest_zeros_sensitivity",zero_free)
        ):
            marginals[label]={
                "PC1_warm_low_ice":raw_vs_within(rs,"PC1_warm_low_ice_global_source_SD"),
                "PC2_saline":raw_vs_within(rs,"PC2_saline_global_source_SD"),
                "two_physical_axis_site_equal_model":equal_site_within_two_axes(rs),
                "n_original_actual_zero_rows_excluded_from_same_method":
                    len(same)-len(zero_free) if label.endswith("sensitivity") else None
            }
        # Actual source same-method true pair site×season count response fixed.
        coef=marginals["same_original_survey_method_both_species_primary"]["two_physical_axis_site_equal_model"]
        regions=leave_geography_out(same,"source_region")
        blocks=leave_geography_out(same,"source_250km_block")
        loo_rows.extend([{"species_pair":key,**r} for r in regions+blocks])
        candidates=slope_per_actual_colony(same)
        overall_slopes.extend(candidates)
        n_repeated=coef.get("n_repeated_colony_sites",coef.get("n_repeat_sites",0))
        eligible=(
            coef["status"]=="DESCRIPTIVE_ONLY_SAME_SITE_TWO_PHYSICAL_AXIS_ASSOCIATION"
            and coef["n_regions_with_real_repeat_site_cocensus"]>=3
            and coef["n_source_250km_blocks_with_real_repeat_site_cocensus"]>=3
            and all(x["status"]=="DESCRIPTIVE_ONLY_SAME_SITE_TWO_PHYSICAL_AXIS_ASSOCIATION" for x in regions)
            and all(x["status"]=="DESCRIPTIVE_ONLY_SAME_SITE_TWO_PHYSICAL_AXIS_ASSOCIATION" for x in blocks))
        signs={}
        if eligible:
            for pcidx,col in (
                ("PC1","PC1_coef_per_original_source_SD"),
                ("PC2","PC2_coef_per_original_source_SD")):
                v=float(coef[
                    "PC1_warm_low_ice_coef_per_original_global_source_SD" if pcidx=="PC1"
                    else "PC2_saline_coef_per_original_global_source_SD"])
                sensitivity=[x[col] for x in regions+blocks]
                signs[pcidx]=bool(all(s is not None and v*s>0 for s in sensitivity))
        results[key]={
            "source_observed_same_site_species_pair":key,
            "original_true_co_count_rows":len(study),
            "same_method_dual_count_rows":len(same),
            "source_positive_both_counts_rows":len(zero_free),
            "n_unique_source_sites":len({r["site_id"] for r in same}),
            "n_unique_source_reporting_regions":len({r["source_region"] for r in same}),
            "n_unique_source_250km_blocks":len({r["source_250km_block"] for r in same}),
            "n_unique_GLORYS_marine_cells":len({r["source_ocean_GLORYS_cell"] for r in same}),
            "marginal_original_2axis_Pearson_and_equal_site_source_model":marginals,
            "primary_source_region_and_block_deletion":{
                "source_region":regions,"source_polar_250km_block":blocks,
                "source_support_gate_for_region_block_coefficient_sign_stability":eligible,
                "coeff_sign_stable_under_every_geographic_deletion":signs
            },
            "true_co_count_site_decadal_slope_support":summary_site_slopes(candidates),
            "source_species_shift_identification":
                "WITHIN_SITE_TWO_AXES_EXPLORATORY_ONLY_NO_CAUSAL_OR_INDEPENDENT_TIME_TRANSFER",
            "not_a_18region_species_replacement_occurrence_probability":True
        }
    out={
        "status":"SOURCE_FIXED_588SITE_28Y_TWO_AXIS_PENGUIN_COCENSUS_EXPLORATORY_COMPLETED",
        "original_physical_source_18region_PCA_reproduced":source,
        "original_true_three_species_pair_source":results,
        "inference_limits":[
            "The physical marine SIC and salinity/temp axes are source PC coordinates, not calibrated penguin niche or causal variables.",
            "A second GLORYS reanalysis salinity PC is not an independent environmental experiment.",
            "All pair responses are genuine co-recorded species nest counts at identical source site and season; same calendar year does not prove identical sampling date, area or effort.",
            "Original source zero-nest observations are real source zeros, but unrecorded species and years are never pseudo-absences.",
            "Within-colony repeated count records and nearby sea-ice/reanalysis cells produce autocorrelated ecological samples.",
            "Equal-site in-sample two-axis R2 is an arithmetic description; not an out-of-year or out-of-region predictive performance gain.",
            "More than one original region or 250km source block does not by itself provide randomized or transferable ecological effects.",
            "Within-site climate associations need truly independent ecological replication, survey effort/detection controls, and source-restricted historical exposure for future tests.",
            "No 1993–2020 vegetation dynamics, greening, penguin migration, climate debt, or CMIP6 colony-count projections are inferred.",
            "Do not tune time lag, p-value cutoff, PCA axis orientation, threshold, species outcome, or spatial region post-result."
        ]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    writecsv(args.out/"original_351_actual_same_site_year_species_pairs_with_two_fixed_marine_PCs.csv",rows)
    writecsv(args.out/"source_actual_3plus_10yr_same_year_two_species_site_slopes.csv",overall_slopes)
    writecsv(args.out/"source_leave_region_or_block_out_dual_physical_axes.csv",loo_rows)
    (args.out/"original_dual_marine_PC1_PC2_three_penguin_pair_source_verdict.json").write_text(
        json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("TWO_MARINE_AXIS_SOURCE_REPRODUCED="+json.dumps(source,ensure_ascii=False),flush=True)
    print("TWO_MARINE_AXIS_COCOUNT="+json.dumps({
        k:{
            "source_count":r["original_true_co_count_rows"],
            "same_method":r["same_method_dual_count_rows"],
            "source_zeros_free":r["source_positive_both_counts_rows"],
            "regions":r["n_unique_source_reporting_regions"],
            "blocks":r["n_unique_source_250km_blocks"],
            "full_pair":r["marginal_original_2axis_Pearson_and_equal_site_source_model"][
                "same_original_survey_method_both_species_primary"],
            "zero_free":r["marginal_original_2axis_Pearson_and_equal_site_source_model"][
                "same_method_source_records_no_actual_nest_zeros_sensitivity"],
            "region_block_source_gate":r["primary_source_region_and_block_deletion"][
                "source_support_gate_for_region_block_coefficient_sign_stability"],
            "sign_stability":r["primary_source_region_and_block_deletion"][
                "coeff_sign_stable_under_every_geographic_deletion"],
            "true_observed_count_site_slope":r["true_co_count_site_decadal_slope_support"]
        } for k,r in results.items()},ensure_ascii=False),flush=True)
    print("TWO_MARINE_AXIS_LEAVE_ORIGINAL_GEOGRAPHY_OUT="+json.dumps(loo_rows,ensure_ascii=False),flush=True)
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--climate",type=Path,required=True)
    ap.add_argument("--pairs",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    analyze(ap.parse_args())


if __name__=="__main__":
    main()
