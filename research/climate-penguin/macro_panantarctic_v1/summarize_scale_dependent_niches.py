#!/usr/bin/env python3
"""Consolidate verified Antarctic-scale ecological results, no new p-value tests.

Sources: independently completed original 595-site 30y SIC and 100-series
species×colony trend workflow, plus fixed positive-mapped vegetation 173-site
spatial model. Outcomes were known before this descriptive scale audit.
"""
from __future__ import annotations
import argparse,csv,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

OUT=Path(__file__).resolve().parent/"outputs"
OUT.mkdir(parents=True,exist_ok=True)

def csvrows(path):
    with Path(path).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))
def pearson(x,y):
    a=np.asarray(x,dtype=float);b=np.asarray(y,dtype=float)
    if len(a)<3 or min(np.std(a),np.std(b))<1e-12:return None
    return float(np.corrcoef(a,b)[0,1])
def region_decomp(a):
    x=np.array([float(z["mean_SIC"]) for z in a])
    y=np.array([float(z["log_plant_area"]) for z in a])
    region=defaultdict(list)
    for i,z in enumerate(a):region[z["source_region"]].append(i)
    xm=x.mean();ym=y.mean()
    rx=np.zeros_like(x);ry=np.zeros_like(y)
    for ind in region.values():
        rx[ind]=x[ind].mean()
        ry[ind]=y[ind].mean()
    raw_cov=float(np.mean((x-xm)*(y-ym)))
    within_cov=float(np.mean((x-rx)*(y-ry)))
    between_cov=float(np.mean((rx-xm)*(ry-ym)))
    if not math.isclose(raw_cov,within_cov+between_cov,abs_tol=1e-8):
        raise ValueError("Regional covariance decomposition identity failed")
    return {
      "n_sites":len(a),"n_regions":len(region),
      "r_raw_sites":pearson(x,y),
      "r_within_region_demeaned":pearson(x-rx,y-ry),
      "total_site_equal_covariance":raw_cov,
      "within_region_site_equal_covariance":within_cov,
      "between_region_site_equal_covariance":between_cov,
      "between_share_of_negative_total_covariance":between_cov/raw_cov,
      "fraction_site_SIC_variance_explained_by_region_means":float(np.var(rx)/np.var(x)),
      "fraction_site_log_mapped_vegetation_variance_explained_by_region_means":float(np.var(ry)/np.var(y)),
      "leave_one_region_out":{
        key: {
            "remaining_site_count":len(a)-len(ix),
            "r_raw":region_decomp_small([v for v in a if v["source_region"]!=key])[0],
            "r_region_demeaned":region_decomp_small([v for v in a if v["source_region"]!=key])[1]
        }
        for key,ix in sorted(region.items())
      },
      "source_region_site_counts":{key:len(ix) for key,ix in sorted(region.items())}
    }
def region_decomp_small(a):
    x=np.array([float(z["mean_SIC"]) for z in a]);y=np.array([float(z["log_plant_area"]) for z in a])
    groups=defaultdict(list)
    for i,z in enumerate(a):groups[z["source_region"]].append(i)
    ax=x.copy();by=y.copy()
    for ind in groups.values():
        ax[ind]-=np.mean(x[ind]);by[ind]-=np.mean(y[ind])
    return pearson(x,y),pearson(ax,by)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--land-sites",type=Path,required=True)
    ap.add_argument("--land-summary",type=Path,required=True)
    ap.add_argument("--nest-trends",type=Path,required=True)
    ap.add_argument("--trend-summary",type=Path,required=True)
    args=ap.parse_args()
    env=csvrows(args.land_sites)
    land=json.loads(args.land_summary.read_text(encoding="utf-8"))
    trend=csvrows(args.nest_trends)
    trends=json.loads(args.trend_summary.read_text(encoding="utf-8"))
    if len(env)!=173 or len({z["site_id"] for z in env})!=173:
        raise ValueError("Source vegetation geography changed")
    if len(trend)!=100 or len({z["site_id"] for z in trend})!=77:
        raise ValueError("Original observed source nesting trend cohort changed")
    if land["n_original_observed_penguin_sites_total"]!=595 or trends["original_macro_site_support"]["all_sites"]!=595:
        raise ValueError("Independent original full 595-sites base changed")
    spatial=region_decomp(env)
    reference=land["environment_environment_173_unique_sites"]
    if not math.isclose(spatial["r_raw_sites"],reference["r_raw_SIC_vs_log1p_static_mapped_area"],abs_tol=1e-10):
        raise ValueError("Original published pooled spatial correlation drift")
    if not math.isclose(spatial["r_within_region_demeaned"],reference["r_within_region_demeaned"],abs_tol=1e-10):
        raise ValueError("Original published region conditioned spatial correlation drift")
    models=land["fixed_3species_conditional_nest_count_median_model_197_site_species"]
    if models["n"]!=197 or land["n_original_source_region_labels"]!=8:
        raise ValueError("Land original counts and regions changed")
    rows=[]
    for species in ("ADPE","CHPE","GEPE"):
        a=[z for z in trend if z["species"]==species]
        src=trends["pre_fixed_family_three_species"][species]
        if len(a)!=src["matched_original_series"]:
            raise ValueError("SIC/colony by-species actual site count changed")
        ice=[float(z["sic_trend_pp_per_decade"]) for z in a]
        nest=[float(z["observed_log_nest_trend_per_decade"]) for z in a]
        raw=pearson(ice,nest)
        meanreg=defaultdict(list)
        for i,z in enumerate(a):meanreg[z["source_region"]].append(i)
        xi=np.array(ice);yi=np.array(nest)
        rx=xi.copy();ry=yi.copy()
        for ix in meanreg.values():
            rx[ix]-=np.mean(xi[ix]);ry[ix]-=np.mean(yi[ix])
        regionr=pearson(rx,ry)
        if not math.isclose(raw,src["raw_site_species_trend_correlation"],abs_tol=1e-10) or not math.isclose(regionr,src["within_region_demeaned_correlation"],abs_tol=1e-10):
            raise ValueError("Trends original source correlation drift: "+species)
        ci=src["250km_spatial_block_bootstrap"]["interval_95_percentile"]
        rows.append({
          "species":species,"n_original_sites":len(a),
          "n_regions":len(meanreg),
          "n_independent_250km_source_bins":src["n_original_250km_blocks"],
          "r_raw_same_observed_year_climate_and_nest_trends":raw,
          "r_region_demeaned":regionr,
          "spatial_block_bootstrap_95pct_low":ci[0] if ci else "",
          "spatial_block_bootstrap_95pct_high":ci[1] if ci else "",
          "spatial_block_interval_includes_zero":bool(ci and ci[0]<=0<=ci[1]),
          "n_species_specific_climate_trend_series":len(a),
          "nominal_p_or_causal_climate_effect_inferred":False
        })
    if [x["n_original_sites"] for x in rows]!=[37,27,36]:
        raise ValueError("Original species source-group size changed")
    if not all(z["spatial_block_interval_includes_zero"] for z in rows):
        raise ValueError("A previous source-verified evidence boundary has changed")
    out={
      "status":"MACRO_595_SITE_3AXIS_EVIDENCE_SCALES_RECONCILED_NO_CAUSAL_JOINT_EFFECT",
      "stage":"post-result statistical scale decomposition; no new fitted ecology model or p-value search",
      "macro_all_original_colonies":595,
      "macro_SIC_original_1991_2020_source_site_months":71400,
      "longitudinal_census_analysis":{"site_species_series":100,"sites":77,
           "n_source_regions":7,"species_source":rows},
      "static_marine_terrestrial_cross_section":{"positive_map_sites":173,
           "species_count_median_rows":197,"n_source_regions":8,
           "n_250km_blocks":14,
           "region_variance_and_covariance":spatial,
           "region_demeaned_spatial_block_95pct_interval":reference["r_region_demeaned_250km_block_bootstrap_95_pct"],
           "observed_count_model_vegetation_coefficient":models["beta_vegetation"],
           "vegetation_block_95pct_interval":models["vegetation_per_log_area_250km_block_bootstrap_95_pct"],
           "observed_count_model_SIC_per_10pp_coefficient":models["beta_sic_per_10pp"],
           "SIC_block_95pct_interval":models["SIC_per_10pp_250km_block_bootstrap_95_pct"]},
      "scientific_interpretation":"Original Antarctic environmental contrasts occur strongly among regions; after regional demeaning the ice–mapped vegetation relationship weakens and count–environment associations are uncertain; temporal nest–SIC slopes differ among species but 250km block intervals all span zero.",
      "critical_limit":["Breeding-site database documents observed presence and counts, not exhaustive distribution or true unoccupied habitat.",
         "The 173 land sites are a positive Plantarctica detection subset of 595, so environmental correlations conditional on site and map detection are not continent-wide vegetation trends.",
         "1991–2020 SIC and 2017–2023 mapped land are different temporal objects; no annual warming-to-greening mediation is inferred.",
         "Both 7/8 source regions and 14 mapped-terrestrial spatial blocks limit environmental association generalization.",
         "Raw observations in one colony do not establish absence of missing taxa, breeding success or climate-caused movement.",
         "Do not interpret descriptive covariance fractions as causal variance explained by temperature or habitat selection.",
         "No new fishing over MaxEnt, GAM, climate lag, native count distribution or arbitrary threshold to force significance."]
    }
    path=OUT/"scale_decomposition_595source_173land_100trends.json"
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (OUT/"species_climate_nest_trend_scale_checks.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    print("PANANTARCTIC_MACRO_SCALE_DECOMPOSITION="+json.dumps({
      "status":out["status"],"n_original_sites":595,
      "n_landsites":173,"n_breeding_trend_site_species":100,
      "regional_SIC_variance_share":spatial["fraction_site_SIC_variance_explained_by_region_means"],
      "regional_plant_variance_share":spatial["fraction_site_log_mapped_vegetation_variance_explained_by_region_means"],
      "within_region_SIC_mapped_land_r":spatial["r_within_region_demeaned"],
      "species_block_CI_span_zero":{z["species"]:z["spatial_block_interval_includes_zero"] for z in rows}
     },ensure_ascii=False),flush=True)
if __name__=="__main__":
    main()
