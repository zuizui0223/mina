#!/usr/bin/env python3
"""Check statistical association claims against existing mina source-backed outputs.

This is a POST-RESULT evidence audit, not a new hypothesis test, inference family,
or selection of significant results. Never substitute nominal p for a
spatially/dependence-adjusted or project-wide multiplicity-corrected finding.
"""
from __future__ import annotations
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parents[1] / "outputs"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

def read_table(relative):
    with (ROOT / relative).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def mean(xs):
    return sum(xs) / len(xs)

def numeric_corr(rows, x, y):
    return float(np.corrcoef([float(a[x]) for a in rows], [float(a[y]) for a in rows])[0,1])

def main():
    long = read_table("historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv")
    if len(long) != 39 or len({z["site_id"] for z in long}) != 39:
        raise ValueError("39-site source/census cohort changed")
    x = "historical_nearshore_AugNov_SIC_mean_pct"
    y = "count_growth_log1p_slope_per_decade"
    r, p = pearsonr([float(z[x]) for z in long], [float(z[y]) for z in long])
    groups = defaultdict(list)
    for z in long:
        groups[z["region"]].append(z)
    xr = []
    yr = []
    for z in long:
        vals = groups[z["region"]]
        xr.append(float(z[x]) - mean([float(v[x]) for v in vals]))
        yr.append(float(z[y]) - mean([float(v[y]) for v in vals]))
    within = float(np.corrcoef(xr,yr)[0,1])
    skip_victoria = numeric_corr([z for z in long if z["region"] != "Victoria Land"],x,y)
    if not (abs(r-.6217192758360188)<1e-10 and abs(within-.2389682297732665)<1e-10 and abs(skip_victoria-.28526951764747954)<1e-10):
        raise ValueError("39-site correlation or spatial confounding source drift")
    veg=read_table("vegetation_response_v1/associations.csv")
    target=[z for z in veg if z["cohort"]=="positive_detections" and
        z["endpoint"]=="log1p_count_median" and z["species"]=="GEPE"]
    unadj=next(z for z in target if z["adjustment"]=="unadjusted")
    region=next(z for z in target if z["adjustment"]=="region_fixed_effects")
    rv=float(unadj["pearson_r"]); n=int(unadj["n"])
    from scipy.stats import t as student_t
    tvalue=rv*np.sqrt((n-2)/(1-rv*rv))
    pv=float(2*student_t.sf(abs(tvalue),df=n-2))
    if n!=47 or abs(rv-.2949975052818651)>1e-12 or abs(float(region["pearson_r"])-.058)>0.001:
        raise ValueError("Spatial vegetation site-set/partial-correlation drift")
    three=read_table("niche_multiscale_v1/exact_three_metric_family.csv")
    primary=next(z for z in three if z["metric"]=="fish")
    if len(three)!=3 or abs(float(primary["r"])-.7840427374865907)>1e-12 or abs(float(primary["p_max3"])-.03419863315696649)>1e-12:
        raise ValueError("Signy three-axis pre-coded correction changed")
    species=read_table("hatching_gap_climate_v1/model_coefficients.csv")
    hatch={z["response"]:z for z in species if z["model"]=="ice_only" and z["term"]=="ice10"}
    if {k:round(float(v["p_hc3"]),6) for k,v in hatch.items() if k in ("Adelie","Chinstrap")} != {"Adelie":.019615,"Chinstrap":.018116}:
        raise ValueError("Single-species hatching nominal result drift")
    gap=next(z for z in species if z["response"]=="gap" and z["model"]=="ice_only")
    low=read_table("low_ice_days_count_v1/associations.csv")
    nominal=[z for z in low if z["fdr_by"] not in ("","nan") and float(z["fdr_by"])<.05]
    if len(low)!=48 or len(nominal)!=3 or any(float(z["sign_fdr_by"])<.05 for z in low):
        raise ValueError("Low-ice threshold multiple-testing/permutation statuses changed")
    salinity=read_table("salinity_grid_cluster_v1/tests.csv")
    if len(salinity)!=48 or any(float(z["fdr_bh"])<.05 for z in salinity):
        raise ValueError("Salinity result has become family significant")
    count=read_table("vegetation_annual_ndvi_v1/ndvi_count_correlations.csv")
    output={
       "status":"POST_RESULT_ASSOCIATION_EVIDENCE_RECONCILED_NOT_PROJECT_WIDE_FDR",
       "signy_fish":{
         "years":9,"r":float(primary["r"]),"p_exact":float(primary["p_exact"]),
         "within_three_food_metrics_max_abs_r_p":float(primary["p_max3"]),
         "scope":"Signy 9 years, 3 axes; not all climate-window studies corrected"
       },
       "adelie_spatial_ice_growth":{
         "n_sites":39,"n_regions":len(groups),"region_sizes":{k:len(v) for k,v in groups.items()},
         "pooled_pearson_r":float(r),"nominal_independent_sites_p":float(p),
         "region_demeaned_r_no_robust_p":within,
         "leave_Victoria_Land_out_r":skip_victoria,
         "scope":"spatial and region-confounded; nominal p assumes independent site samples"
       },
       "gentoo_static_mapped_vegetation_vs_site_median_nests":{
         "n_sites":n,"unadjusted_r":rv,"nominal_independent_sites_p":pv,
         "10km_spatial_block_bootstrap_r_range": [
              float(unadj["pearson_r_bootstrap_low"]),float(unadj["pearson_r_bootstrap_high"])],
         "region_demeaned_r":float(region["pearson_r"]),
         "region_block_bootstrap_r_range":[
              float(region["pearson_r_bootstrap_low"]),float(region["pearson_r_bootstrap_high"])],
         "scope":"2017-2023 composite vegetation detectable area near site; no annual greening, no 24-test FDR"
       },
       "hatching_species":{
         s:{"n":int(z["n"]),"slope_days_per_10pp":float(z["estimate"]),
            "nominal_hc3_p":float(z["p_hc3"])}
         for s,z in hatch.items() if s in ("Adelie","Chinstrap")},
       "hatching_species_gap":{
         "n":int(gap["n"]),"slope_days_per_10pp":float(gap["estimate"]),
         "hc3_p":float(gap["p_hc3"]),"status":"No supported species separation in response"
       },
       "low_ice_low_days":{
         "tested":len(low),"n_two_way_cluster_BY_lt_0p05":len(nominal),
         "n_site_year_sign_permutation_BY_lt_0p05":sum(float(z["sign_fdr_by"])<.05 for z in low),
         "scope":"3 nominal clustered-t BY discoveries but none survive corrected sign-flip sensitivity"
       },
       "salinity":{
          "tested":len(salinity),"n_family_BH_significant":sum(float(z["fdr_bh"])<.05 for z in salinity)
       },
       "annual_ndvi":{
          "n_formal_inference_tests":0,"note":"Same pixel NDVI year differences are descriptive, no validated change in vegetation at established plant pixels"
       },
       "guardrail":"Correlation significance is not prediction transfer, not attributable warming mechanism and not project-wide multiple-testing significance."
    }
    (OUT/"source_checked_association_summary.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("ASSOCIATION_EVIDENCE_CHECK="+json.dumps(output,ensure_ascii=False))

if __name__ == "__main__":
    main()
