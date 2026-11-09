#!/usr/bin/env python3
"""Antarctic macro: static terrestrial area × 30y marine SIC × observed nests.

One pre-fixed descriptive 173-site environment correlation and 197 site-species
conditional OLS with 250-km geography-block bootstrap. Not actual annual
greening, species absence, causal migration or climate population forecasts.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from pyproj import Transformer

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/"land_173_macro_outputs"
OUT.mkdir(parents=True,exist_ok=True)
SOURCE_REL="outputs/vegetation_response_v1/site_species_cohort.csv"
SOURCE_GIT_BLOB="23fea5988889303ecdc16f4b5309073cf38e366a"
B=2000
SEED=20261109

def load(p):
    with p.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def write(p,rows):
    if not rows:raise ValueError("No data to save "+str(p))
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def corr(x,y):
    a=np.asarray(x,dtype=float);b=np.asarray(y,dtype=float)
    if len(a)<4 or min(np.std(a),np.std(b))<1e-10:return None
    return float(np.corrcoef(a,b)[0,1])

def design(rows):
    # Fixed factor reference coding; omit globally absent levels in each
    # block-bootstrap draw rather than pretending a missing region is observed.
    spp=sorted({z["species"] for z in rows})
    region=sorted({z["source_region"] for z in rows})
    cols=[
      np.ones(len(rows)),
      *[np.array([int(z["species"]==sp) for z in rows]) for sp in spp[1:]],
      *[np.array([int(z["source_region"]==reg) for z in rows]) for reg in region[1:]],
      np.array([z["log1p_observed_seasons"] for z in rows]),
      np.array([z["mean_1991to2020_SIC_per_10pp"] for z in rows]),
      np.array([z["log1p_static_vegetation_area"] for z in rows])
    ]
    X=np.column_stack(cols)
    y=np.array([z["log1p_observed_nest_median"] for z in rows],dtype=float)
    if len(rows)<=X.shape[1]+5 or np.linalg.matrix_rank(X)<X.shape[1]:
        return None
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    return {"beta_vegetation":float(beta[-1]),"beta_sic_per_10pp":float(beta[-2]),
            "r2_observed_in_sample":float(1-np.sum((y-X@beta)**2)/np.sum((y-np.mean(y))**2)),
            "n_terms":X.shape[1],"n":len(rows)}

def environmental_corr(rows):
    x=np.array([z["mean_SIC"] for z in rows])
    y=np.array([z["log_plant_area"] for z in rows])
    xa=x.copy();ya=y.copy()
    regs=defaultdict(list)
    for i,z in enumerate(rows):regs[z["source_region"]].append(i)
    for ix in regs.values():
        xa[ix]-=np.mean(x[ix]);ya[ix]-=np.mean(y[ix])
    return {"pooled":corr(x,y),"region_demeaned":corr(xa,ya)}

def block_sample(data,rng):
    keys=sorted({z["spatial_250km_block"] for z in data})
    selected=rng.choice(keys,size=len(keys),replace=True)
    by=defaultdict(list)
    for z in data:by[z["spatial_250km_block"]].append(z)
    return [a for k in selected for a in by[k]]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--full-ice-csv",required=True,type=Path)
    ap.add_argument("--full-ice-summary",required=True,type=Path)
    args=ap.parse_args()
    main_sites=load(HERE/"outputs/panantarctic_595_site_inventory.csv")
    macro=json.loads((HERE/"outputs/macro_original_coverage.json").read_text())
    ice=load(args.full_ice_csv)
    ice_receipt=json.loads(args.full_ice_summary.read_text())
    landpath=ROOT/SOURCE_REL
    raw=landpath.read_bytes()
    gitsha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
    if gitsha!=SOURCE_GIT_BLOB:raise ValueError("Original positive map/median count source SHA drift")
    land=load(landpath)
    if len(land)!=246 or len(main_sites)!=595 or len(ice)!=595*120:
        raise ValueError("Large source panel coverage drift")
    if ice_receipt["status"]!="PANANTARCTIC_ORIGINAL_30YR_MONTHLY_SIC_MACRO_SOURCE_COMPLETE":
        raise ValueError("No accepted original 595-site climate source receipt")
    sites={z["site_id"]:z for z in main_sites}
    ice_stats=defaultdict(list)
    for r in ice:
        if r["source_full_595_site_monthly_support"]!="OK":
            continue
        ice_stats[r["site_id"]].append(float(r["source_25km_buffer_mean_SIC_pct"]))
    if len(ice_stats)!=595 or any(len(v)!=120 for v in ice_stats.values()):
        raise ValueError("Missing original mean climate at a known penguin site")
    env=[]
    land_records=[]
    for z in land:
        site=z["site_id"]
        if site not in sites:continue
        if z["positive_mapped_detection"]!="True":continue
        area=float(z["mapped_terrestrial_union_area_2km_m2"])
        if area<=0:raise ValueError("Invalid original positive vegetation")
        med=float(z["count_median"])
        nobs=int(z["observed_seasons"])
        if med<0 or nobs<=0:raise ValueError("Original observed nest medians invalid")
        src=sites[site]
        if src["source_region"]!=z["region"]:
            raise ValueError("Region of original climate and land site differs")
        land_records.append({
            "site_id":site,"species":z["species_id"],
            "source_region":z["region"],
            "spatial_250km_block":src["polar_250km_fixed_grid_block"],
            "n_original_modern_observed_seasons":nobs,
            "log1p_observed_seasons":math.log1p(nobs),
            "observed_median_nests":med,
            "log1p_observed_nest_median":math.log1p(med),
            "static_2017to2023_mapped_vegetation_area_m2":area,
            "log1p_static_vegetation_area":math.log1p(area),
            "mean_1991to2020_SIC_pct":float(np.mean(ice_stats[site])),
            "mean_1991to2020_SIC_per_10pp":float(np.mean(ice_stats[site]))/10.,
            "is_a_biologically_confirmed_annual_green_up":False,
            "site_species_was_actually_observed":True
        })
    if len(land_records)!=197 or len({r["site_id"] for r in land_records})!=173:
        raise ValueError("Original positive mapped-vegetation macro cohort drift")
    land_records.sort(key=lambda z:(z["site_id"],z["species"]))
    for site in sorted({z["site_id"] for z in land_records}):
        values={z["log1p_static_vegetation_area"] for z in land_records if z["site_id"]==site}
        if len(values)!=1:raise ValueError("Land cover is duplicated with different values by species")
        v=next(z for z in land_records if z["site_id"]==site)
        env.append({"site_id":site,
            "source_region":v["source_region"],
            "spatial_250km_block":v["spatial_250km_block"],
            "mean_SIC":v["mean_1991to2020_SIC_pct"],
            "log_plant_area":v["log1p_static_vegetation_area"],
            "static_plant_area_m2":v["static_2017to2023_mapped_vegetation_area_m2"]})
    if len({z["source_region"] for z in env})!=8 or len({z["spatial_250km_block"] for z in env})!=14:
        raise ValueError("Original land-positive geography/region blocks changed")
    envcorr=environmental_corr(env)
    fixed_fit=design(land_records)
    if fixed_fit is None:raise ValueError("Initial model fixed factors structurally rank deficient")
    rng=np.random.default_rng(SEED)
    corrs=[]
    betas=[]
    for i in range(B):
        trial=block_sample(env,rng)
        a=environmental_corr(trial)["region_demeaned"]
        if a is not None: corrs.append(a)
        chosen=block_sample(land_records,rng)
        b=design(chosen)
        if b is not None:betas.append(b)
    if len(corrs)<.75*B or len(betas)<.75*B:
        bootstrap_status="REGIONAL_INFERENCE_UNSTABLE"
    else:
        bootstrap_status="DESCRIPTIVE_BLOCK_INTERVAL_SUPPORTED"
    def ci(z):
        if len(z)<.75*B:return None
        return [float(np.quantile(z,.025)),float(np.quantile(z,.975))]
    summary={
      "status":"PANANTARCTIC_3AXIS_STATIC_LAND_AND_MARINE_ENVIRONMENT_REVIEW_COMPLETE",
      "n_original_observed_penguin_sites_total":len(main_sites),
      "n_original_30yr_site_month_source_ice":len(ice),
      "n_original_2017to2023_positive_mapped_land_sites":len(env),
      "n_original_observed_site_species_with_positive_land":len(land_records),
      "n_original_source_region_labels":len({z["source_region"] for z in env}),
      "n_250km_fixed_geographic_blocks":len({z["spatial_250km_block"] for z in env}),
      "source_count_rows_by_species":dict(sorted(Counter(z["species"] for z in land_records).items())),
      "environment_environment_173_unique_sites":{
         "r_raw_SIC_vs_log1p_static_mapped_area":envcorr["pooled"],
         "r_within_region_demeaned":envcorr["region_demeaned"],
         "r_region_demeaned_250km_block_bootstrap_95_pct":ci(corrs),
         "valid_block_bootstrap_replicates":len(corrs)
      },
      "fixed_3species_conditional_nest_count_median_model_197_site_species":{
         "formula":"log1p_nest_median ~ species + source_region + log1p_observed_seasons + mean_30yr_SIC_per10pp + log1p_static_mapped_plant_area",
         **fixed_fit,
         "SIC_per_10pp_250km_block_bootstrap_95_pct":ci([z["beta_sic_per_10pp"] for z in betas]),
         "vegetation_per_log_area_250km_block_bootstrap_95_pct":ci([z["beta_vegetation"] for z in betas]),
         "valid_block_bootstrap_replicates":len(betas)
      },
      "bootstrap_inference_status":bootstrap_status,
      "original_source_land_git_blob":SOURCE_GIT_BLOB,
      "original_source_ice_native_monthly_sha":ice_receipt["original_native_grid_geo_sha256"],
      "interpretation_limits":[
        "Cross-sectional breeding-count medians observed in the 2017-2023 era are not synchronized to a 1991-2020 ice mean year or annual vegetation change.",
        "Mapped Plantarctica polygon area is site-wide and can include lichen/moss and map detection bias; not validated botanical percent cover.",
        "Site codes are not uniformly surveyed or sampled background; a zero map detection is not plant absence and an unrecorded penguin species is not a biological absence.",
        "Large observed r can be driven by 8 region differences and 14 dependent spatial blocks; spatial bootstrap uncertainty should not be treated as independent confirmation or project-wide FDR.",
        "Static vegetation environment is not a causally estimated mediator of warming, sea ice or colony shifts.",
        "This is one fixed descriptive conditional model after prior analyses; no p-value selection, climate lag, threshold, Gaussian-GAM variant or projected future nest numbers."
      ]}
    save=OUT/"macroscopic_173site_marine_terrestrial_support.json"
    save.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    write(OUT/"original_land_positive_197_site_species_30year_ice.csv",land_records)
    write(OUT/"original_173_unique_site_marine_terrestrial_environment.csv",env)
    print("PANANTARCTIC_STATIC_LAND_MARINE_NICHE="+json.dumps(summary,ensure_ascii=False),flush=True)
if __name__=="__main__":
    main()
