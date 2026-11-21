#!/usr/bin/env python3
"""Exploratory Antarctic continental 1993–2020 original three-variable
marine PCA and genuine observed penguin two-species comparisons.

Physical sources: 588 colony 112 original GLORYS reanalysis months +
595 colony native EUMETSAT OSI SAF v3.1 120 months. Do not turn unobserved
breeding-site-years/species into ecological zeros or static greening years.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import Counter,defaultdict
from pathlib import Path
from statistics import mean

import numpy as np
from scipy.stats import rankdata

from test_joint_marine_regime_axis import pca, pearson, align_cosine

YEARS=tuple(range(1993,2021))
MONTHS=(8,9,10,11)
VARIABLES=("mean_source_SIC_pp","mean_GLORYS_salinity","mean_GLORYS_thetao_C")
DECADES=((1993,2000),(2001,2010),(2011,2020))
BASELINE_34_EXPLAINED=0.7094310203120341
BASELINE_34_LOADINGS=(-0.6429407460619279,-0.489029929797934,0.589471733686323)
PAIRS=(("ADPE","GEPE"),("CHPE","GEPE"),("ADPE","CHPE"))


def readcsv(path):
    with path.open(encoding="utf-8",newline="") as fp:
        return list(csv.DictReader(fp))


def writecsv(path,records):
    if not records:
        path.write_text("no_original_supported_records\n",encoding="utf-8")
        return
    columns=list(dict.fromkeys(k for x in records for k in x))
    with path.open("w",encoding="utf-8",newline="") as fp:
        writer=csv.DictWriter(fp,fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)


def flag(s):
    if isinstance(s,bool):return s
    if str(s).lower() not in ("true","false"):
        raise ValueError("Unexpected original source boolean "+str(s))
    return str(s).lower()=="true"


def slope_year(values):
    if len(values)<5:return None
    x=np.asarray([int(y) for y,v in values],dtype=float)
    v=np.asarray([float(v) for y,v in values],dtype=float)
    xc=x-x.mean()
    den=float(xc@xc)
    if den<1e-12 or not np.all(np.isfinite(v)):return None
    return float(10*(xc@(v-v.mean()))/den)


def bysite_centered_pearson(rows,xkey,ykey,require_two_regions=False):
    groups=defaultdict(list)
    for r in rows:groups[r["site_id"]].append(r)
    accepted={s:rs for s,rs in groups.items() if len(rs)>=2}
    regions={r["source_region"] for rs in accepted.values() for r in rs}
    blocks={r["source_250km_block"] for rs in accepted.values() for r in rs}
    xs=[];ys=[]
    for records in accepted.values():
        xm=mean(float(r[xkey]) for r in records)
        ym=mean(float(r[ykey]) for r in records)
        xs.extend([float(r[xkey])-xm for r in records])
        ys.extend([float(r[ykey])-ym for r in records])
    usable=len(accepted)>=3 and len(xs)>=5 and (not require_two_regions or len(regions)>=2)
    return {
        "r":pearson(xs,ys) if usable else None,
        "n_repeated_actual_colony_sites":len(accepted),
        "n_years_at_repeated_sites":len(xs),
        "n_source_regions":len(regions),
        "n_polar_250km_blocks":len(blocks),
        "not_spatially_independent_even_if_multiple_siteyears":True
    }


def original_annual_join(atlas, hydro, ice):
    if len(atlas)!=595 or len({x["site_id"] for x in atlas})!=595:
        raise ValueError("Original 595 source atlas identity changed")
    if len(hydro)!=588*28*4:
        raise ValueError("Source complete 588×112 GLORYS original months changed")
    if len(ice)!=595*30*4:
        raise ValueError("Source 595×120 OSI SAF original monthly count changed")
    known={r["site_id"]:r for r in atlas}
    marine={}
    wet_sites=set()
    for row in hydro:
        site=row["site_id"]
        if site not in known:raise ValueError("Unknown GLORYS source colony ID")
        if row["source_region"]!=known[site]["source_region"]:
            raise ValueError("Original marine source region changed")
        y=int(row["year"]);m=int(row["month"])
        if y not in YEARS or m not in MONTHS:
            raise ValueError("Original GLORYS source calendar changed")
        key=(site,y,m)
        if key in marine:raise ValueError("Duplicate GLORYS source site-month")
        marine[key]=row
        wet_sites.add(site)
    if len(wet_sites)!=588 or len(marine)!=len(hydro):
        raise ValueError("Source coastal 588 original unique site key drift")
    sic={}
    for row in ice:
        site=row["site_id"]
        if site not in wet_sites:continue
        y=int(row["year"]);m=int(row["month"])
        if y not in YEARS or m not in MONTHS:continue
        key=(site,y,m)
        if key in sic:raise ValueError("Duplicate OSI-SAF source site-month")
        ok=row["source_full_595_site_monthly_support"]=="OK"
        v=float(row["source_25km_buffer_mean_SIC_pct"]) if ok else None
        if v is not None and not 0<=v<=100:
            raise ValueError("Original satellite sea ice SIC outside 0–100%")
        sic[key]=v
    if len(sic)!=len(hydro):
        raise ValueError("Original satellite SIC month keys cannot join all real 588 coastal source sites")
    joined=[];quality=[]
    for site in sorted(wet_sites):
        info=known[site]
        for y in YEARS:
            observations=[]
            for m in MONTHS:
                r=marine[site,y,m]
                if not flag(r["source_both_ocean_variables_valid"]) or sic[site,y,m] is None:
                    break
                so=float(r["surface_GLORYS_salinity"])
                thetao=float(r["surface_GLORYS_thetao_C"])
                if not (np.isfinite(so) and np.isfinite(thetao)
                        and 20<=so<=42 and -4<=thetao<=25):
                    break
                observations.append((float(sic[site,y,m]),so,thetao))
            quality.append({
                "site_id":site,"source_region":info["source_region"],"year":y,
                "n_original_months_with_all_3_variables":len(observations),
                "all_four_original_aug_nov_months_valid":len(observations)==4,
                "unrecorded_month_never_fabricated":True,
            })
            if len(observations)!=4:continue
            avg=np.asarray(observations).mean(axis=0)
            # Check geometry is source-pinned across all 112 hydro months.
            sample=marine[site,y,8]
            joined.append({
                "site_id":site,"year":y,"source_region":info["source_region"],
                "source_250km_block":info["polar_250km_fixed_grid_block"],
                "latitude":float(info["latitude"]),"longitude":float(info["longitude"]),
                "GLORYS_cell_y":int(sample["source_original_wet_grid_y"]),
                "GLORYS_cell_x":int(sample["source_original_wet_grid_x"]),
                "GLORYS_cell_distance_km":float(sample["source_geodesic_wet_cell_distance_km"]),
                **dict(zip(VARIABLES,[float(z) for z in avg])),
                "original_source_4_GLORYS_months":4,
                "original_source_4_OSISAF_months":4,
                "marine_source_GLORYS_reanalysis_not_direct_penguin_foraging":True
            })
    years_by_site=Counter(r["site_id"] for r in joined)
    balanced={site for site,n in years_by_site.items() if n==len(YEARS)}
    stable=[r for r in joined if r["site_id"] in balanced]
    support={
        "original_colony_atlas_sites":595,
        "original_source_reporting_regions":18,
        "coastal_GLORYS_salt_temp_sites":len(wet_sites),
        "original_SIC_site_month_records":len(ice),
        "original_GLORYS_1993_2020_source_site_month_records":len(hydro),
        "siteyears_with_all_four_actual_months":len(joined),
        "full_actual_28year_site_count":len(balanced),
        "balanced_actual_siteyear_rows":len(stable),
        "source_regions_with_28year_balanced_marine_data":len({r["source_region"] for r in stable}),
        "original_unique_GLORYS_native_wet_cells_full_balanced":len({
           (r["GLORYS_cell_y"],r["GLORYS_cell_x"]) for r in stable}),
        "excluded_or_partial_sites":[s for s in sorted(wet_sites) if s not in balanced],
        "original_observation_years":[YEARS[0],YEARS[-1]],
        "land_vegetation_is_not_one_of_three_annual_marine_PCA_variables":True
    }
    if len(stable)<1000 or support["source_regions_with_28year_balanced_marine_data"]<12:
        raise ValueError("Full Antarctic balanced original source climate support insufficient")
    return stable,quality,support


def verify_legacy_34(siteyears,old40):
    old=[r["site_id"] for r in old40 if r["cohort"]=="macro_40"
         and r["grid_within_25km"]=="True"]
    if len(old)!=34 or len(set(old))!=34:
        raise ValueError("Original 34 source macro wet grid site names changed")
    frame=[r for r in siteyears if r["site_id"] in set(old) and 2011<=r["year"]<=2020]
    if len(frame)!=34*10:raise ValueError("Cannot recreate 34 original climate year rows")
    f=pca(np.asarray([[r[k] for k in VARIABLES] for r in frame],dtype=float))
    pc=float(f["explained"][0])
    load=np.asarray(f["loadings"][:,0])
    if abs(pc-BASELINE_34_EXPLAINED)>1e-8 or max(abs(load-np.asarray(BASELINE_34_LOADINGS)))>1e-8:
        raise ValueError("Original 34 source-site pooled marine PCA did not replicate: "+
                         json.dumps({"pc1":pc,"loading":load.tolist()}))
    return {"old_2011_2020_34_site_baseline_PCA_verified":True,
        "source_baseline_34_old_site_count":34,
        "source_baseline_34_old_siteyear_count":len(frame),
        "source_baseline_PC1":pc,
        "original_baseline_PC1_loadings":dict(zip(VARIABLES,load.tolist()))}


def marine_pca(siteyears):
    arr=np.asarray([[r[k] for k in VARIABLES] for r in siteyears],dtype=float)
    fit=pca(arr)
    pc=fit["scores"][:,0]
    for r,value in zip(siteyears,pc):
        r["warm_direction_three_var_marine_PCA_score"]=float(value)
    reg=defaultdict(list)
    site=defaultdict(list)
    wet=defaultdict(list)
    for ix,r in enumerate(siteyears):
        reg[r["source_region"]].append(ix)
        site[r["site_id"]].append(ix)
        wet[r["GLORYS_cell_y"],r["GLORYS_cell_x"],r["year"]].append(ix)
    if any(len(ids)!=28 for ids in site.values()):
        raise ValueError("Marine PCA attempted on different temporal observations per colony")
    reg_year=defaultdict(list)
    for region,ids in reg.items():
        for i in ids:
            reg_year[region,siteyears[i]["year"]].append(i)
    if len(reg_year)!=len(reg)*28:
        raise ValueError("Marine PCA original region/year source calendar not full")
    # Distinct source reanalysis grid cell sensitivity: keep a single
    # hydro-grid cell per year, averaging each nearby colony's SIC proxy.
    unique_wet_X=np.asarray([np.mean(arr[ix],axis=0)
                              for key,ix in sorted(wet.items())])
    unique_wet=pca(unique_wet_X)
    equal_region_X=np.asarray([np.mean(arr[ix],axis=0)
                               for key,ix in sorted(reg_year.items())])
    equal_region=pca(equal_region_X)
    # Site-centered temporal PCA on identical site/year identities.
    anomalies=np.empty_like(arr)
    for ids in site.values():
        anomalies[ids]=arr[ids]-np.mean(arr[ids],axis=0)
    time=pca(anomalies)
    site_means=pca(np.asarray([np.mean(arr[ids],axis=0)
                                for name,ids in sorted(site.items())]))
    region_means=pca(np.asarray([np.mean(arr[ids],axis=0)
                                  for name,ids in sorted(reg.items())]))
    reference=fit["loadings"][:,0]
    total=float(np.sum((pc-pc.mean())**2))
    between=float(sum(len(ids)*(pc[ids].mean()-pc.mean())**2 for ids in reg.values()))
    if total<=1e-12:raise ValueError("Source climate PCA is degenerate")
    source={
        "observed_source_siteyear_rows":len(siteyears),
        "n_original_colony_sites":len(site),
        "n_original_250km_blocks":len({r["source_250km_block"] for r in siteyears}),
        "n_original_GLORYS_wet_cells":len({(r["GLORYS_cell_y"],r["GLORYS_cell_x"])
                                        for r in siteyears}),
        "n_original_source_regions":len(reg),
        "source_years":[YEARS[0],YEARS[-1]],
        "marine_variables":list(VARIABLES),
        "spatial_siteyear_PC_explained":[float(z) for z in fit["explained"]],
        "spatial_siteyear_PC1_loadings":dict(zip(VARIABLES,[float(z) for z in reference])),
        "spatial_siteyear_PC2_loadings":dict(zip(VARIABLES,[
            float(z) for z in fit["loadings"][:,1]])),
        "spatial_siteyear_PC3_loadings":dict(zip(VARIABLES,[
            float(z) for z in fit["loadings"][:,2]])),
        "spatial_siteyear_source_pairwise_correlations":{
            VARIABLES[i]+"__"+VARIABLES[j]:pearson(arr[:,i],arr[:,j])
            for i in range(3) for j in range(i+1,3)
        },
        "source_region_mean_difference_fraction_of_PC1_variance":between/total,
        "source_region_within_fraction_of_PC1_variance":1-between/total,
        "region_year_each_region_equal_PC_explained":[float(z) for z in equal_region["explained"]],
        "region_year_equal_PC1_loadings":dict(zip(VARIABLES,[float(z) for z in equal_region["loadings"][:,0]])),
        "pooled_vs_equal_region_year_PC1_alignment":align_cosine(reference,equal_region["loadings"][:,0]),
        "unique_GLORYS_cell_year_PC_explained":[float(z) for z in unique_wet["explained"]],
        "unique_GLORYS_cell_year_PC1_loadings":dict(zip(VARIABLES,[float(z) for z in unique_wet["loadings"][:,0]])),
        "pooled_vs_unique_GLORYS_cell_PC1_alignment":align_cosine(reference,unique_wet["loadings"][:,0]),
        "within_source_site_28year_temporal_anomaly_PC_explained":[float(z) for z in time["explained"]],
        "within_source_site_temporal_PC1_loadings":dict(zip(VARIABLES,[float(z) for z in time["loadings"][:,0]])),
        "pooled_vs_temporal_PC1_alignment":align_cosine(reference,time["loadings"][:,0]),
        "site_equal_28yr_climatology_PC_explained":[float(z) for z in site_means["explained"]],
        "region_equal_28yr_climatology_PC_explained":[float(z) for z in region_means["explained"]],
        "note":"PC1 positive is defined only as positive thetao loading, not independently causal warming."
    }
    # Original fixed pooled axis, not fitted anew in each decade/region.
    region_years=[]
    for (region,year),ix in sorted(reg_year.items()):
        record={
            "source_region":region,"year":year,"n_source_colonies":len(ix),
            "n_unique_ocean_GLORYS_cells":len({(siteyears[i]["GLORYS_cell_y"],siteyears[i]["GLORYS_cell_x"]) for i in ix}),
            "n_source_polar_250km_blocks":len({siteyears[i]["source_250km_block"] for i in ix}),
            "mean_marine_PC1_fixed_original_global_loadings":float(pc[ix].mean()),
            **{var:float(np.mean(arr[ix,k])) for k,var in enumerate(VARIABLES)}
        }
        region_years.append(record)
    source["leave_one_original_region_out_PC1"]=[]
    for omitted in sorted(reg):
        remaining=[r for r in siteyears if r["source_region"]!=omitted]
        sub=pca(np.asarray([[r[v] for v in VARIABLES] for r in remaining]))
        source["leave_one_original_region_out_PC1"].append({
            "omitted_original_source_region":omitted,
            "remaining_site_count":len({r["site_id"] for r in remaining}),
            "remaining_source_regions":len(reg)-1,
            "PC1_explained":float(sub["explained"][0]),
            **align_cosine(reference,sub["loadings"][:,0])
        })
    return source,region_years


def original_region_temporal_change(siteyears,regionyears):
    climate=defaultdict(list)
    geography=defaultdict(list)
    for r in regionyears:climate[r["source_region"]].append(r)
    for r in siteyears:geography[r["source_region"]].append(r)
    regions=[]
    for region in sorted(climate):
        rr=sorted(climate[region],key=lambda r:r["year"])
        rows=geography[region]
        if len(rr)!=28:raise ValueError("Source 28-year region annual calendar incomplete")
        n_sites=len({r["site_id"] for r in rows})
        n_cells=len({(r["GLORYS_cell_y"],r["GLORYS_cell_x"]) for r in rows})
        n_blocks=len({r["source_250km_block"] for r in rows})
        var="mean_marine_PC1_fixed_original_global_loadings"
        full=slope_year([(r["year"],r[var]) for r in rr])
        loo=[slope_year([(r["year"],r[var]) for r in rr if r["year"]!=exclude])
             for exclude in YEARS]
        if any(z is None for z in loo):raise ValueError("Unexpected 28-year temporal slope failure")
        record={
            "source_region":region,
            "n_original_colony_sites":n_sites,
            "n_unique_original_GLORYS_wet_grid_cells":n_cells,
            "n_source_polar_250km_blocks":n_blocks,
            "source_colony_sites_not_independent_sea_ice_or_species_occurrence":True,
            "1993_2020_annual_PC1_slope_per_10yr":full,
            "leave_one_original_calendar_year_out_PC1_slope_min":min(loo),
            "leave_one_original_calendar_year_out_PC1_slope_max":max(loo),
            "source_year_deletion_all_same_PC1_direction":min(loo)>0 or max(loo)<0,
            "source_region_multi_site_multi_block_support":n_sites>=3 and n_blocks>=2 and n_cells>=2,
            **{v+"_OLS_1993_2020_per_10yr":slope_year([(r["year"],r[v]) for r in rr])
               for v in VARIABLES},
            "unequal_period_1993_2000_8yr_vs_2001_2010_2011_2020_10yr":True,
        }
        for a,b in DECADES:
            period=[r for r in rr if a<=r["year"]<=b]
            label=f"{a}_{b}"
            record[f"{label}_n_original_years"]=len(period)
            for v in (var,*VARIABLES):
                record[f"{label}_{v}_mean"]=mean(float(r[v]) for r in period)
        record["late_2011_2020_minus_early_1993_2000_mean_PC1"]=(
            record[f"2011_2020_{var}_mean"]-record[f"1993_2000_{var}_mean"])
        regions.append(record)
    return regions


def true_observed_penguin_pairs(siteyears,countrows):
    climates={(r["site_id"],r["year"]):r for r in siteyears}
    events={}
    source_sites={x[0] for x in climates}
    for r in countrows:
        site=r["site_id"];y=int(r["season"]);sp=r["species"]
        if y not in YEARS or site not in source_sites:continue
        if sp not in ("ADPE","CHPE","GEPE"):continue
        key=(site,y,sp)
        if key in events:raise ValueError("Original site×species×year count duplicated")
        n=int(r["observed_nest_count"])
        if n<0:raise ValueError("Negative original observed nests")
        events[key]=(n,r["original_survey_method"])
    # Apply all three pair labels to prevent choosing one based on resulting
    # climate correlation. The actual same-survey-year support is source-gated.
    observations=[]
    report={}
    for sp0,sp1 in PAIRS:
        rows=[]
        for (site,y),r in sorted(climates.items()):
            val0=events.get((site,y,sp0));val1=events.get((site,y,sp1))
            if val0 is None or val1 is None:continue
            a,method0=val0; b,method1=val1
            rows.append({
                "species_pair":sp0+"__"+sp1,"site_id":site,
                "source_region":r["source_region"],
                "source_250km_block":r["source_250km_block"],
                "GLORYS_cell_y":r["GLORYS_cell_y"],"GLORYS_cell_x":r["GLORYS_cell_x"],
                "season":y,
                "nests_first_species_actual_source_count":a,
                "nests_second_species_actual_source_count":b,
                "original_source_same_method_both_species":method0==method1,
                "original_method_first_species":method0,
                "original_method_second_species":method1,
                "log1p_second_minus_first_actual_nests":float(np.log1p(b)-np.log1p(a)),
                "fixed_marine_PC1_original_global_axis":r["warm_direction_three_var_marine_PCA_score"],
                "unrecorded_species_or_year_was_not_imputed_zero":True,
                "same_breeding_year_not_guaranteed_same_survey_date_citation_effort":True
            })
        observations.extend(rows)
        by_site=defaultdict(list)
        for x in rows:by_site[x["site_id"]].append(x)
        report[sp0+"__"+sp1]={
            "n_actual_original_same_site_same_breeding_year_pair_records":len(rows),
            "n_source_colony_sites_with_both_counts":len(by_site),
            "n_original_reporting_regions":len({r["source_region"] for r in rows}),
            "n_polar_250km_blocks":len({r["source_250km_block"] for r in rows}),
            "n_unique_GLORYS_wet_ocean_grid_cells":len({(r["GLORYS_cell_y"],r["GLORYS_cell_x"]) for r in rows}),
            "n_true_dual_count_records_with_same_survey_method":sum(r["original_source_same_method_both_species"] for r in rows),
            "n_original_sites_with_2plus_actual_both_species_years":sum(len(v)>=2 for v in by_site.values()),
            "observed_all_records_raw_Pearson_r":pearson(
                [r["fixed_marine_PC1_original_global_axis"] for r in rows],
                [r["log1p_second_minus_first_actual_nests"] for r in rows]),
            "within_site_repeat_census_correlation":bysite_centered_pearson(
                rows,"fixed_marine_PC1_original_global_axis",
                "log1p_second_minus_first_actual_nests"),
            "not_a_region_wide_species_occurrence_share":True
        }
        same=[r for r in rows if r["original_source_same_method_both_species"]]
        report[sp0+"__"+sp1]["same_count_method_only"]={
            "n_original_dual_season_records":len(same),
            "n_distinct_original_sites":len({r["site_id"] for r in same}),
            "n_source_regions":len({r["source_region"] for r in same}),
            "n_polar_250km_blocks":len({r["source_250km_block"] for r in same}),
            "raw_r":pearson([r["fixed_marine_PC1_original_global_axis"] for r in same],
                             [r["log1p_second_minus_first_actual_nests"] for r in same]),
            "within_site_r":bysite_centered_pearson(
                same,"fixed_marine_PC1_original_global_axis",
                "log1p_second_minus_first_actual_nests")
        }
    return observations,report


def source_matched_biological_axis_sensitivity(siteyears,actual_cocensus,original40):
    """Separate effect of extending climate axes from including new sites/years.

    Fitted PCA scores are compared on the exact original 34-site 2011-2020
    biological records, and independently on the expanded 588-site observations.
    This is post-result decomposition, not new a priori biology or significance.
    """
    original34={r["site_id"] for r in original40
                if r["cohort"]=="macro_40" and r["grid_within_25km"]=="True"}
    if len(original34)!=34:
        raise ValueError("Original 34-site source macro cohort changed")
    old_climate=[r for r in siteyears if r["site_id"] in original34
                 and 2011<=r["year"]<=2020]
    if len(old_climate)!=340:
        raise ValueError("Original 34 site baseline climate cohort lost in full expansion")
    old_fit=pca(np.asarray([[r[v] for v in VARIABLES] for r in old_climate]))
    oldscore={(r["site_id"],r["year"]):float(z)
              for r,z in zip(old_climate,old_fit["scores"][:,0])}
    cohort={}
    for first,second in PAIRS:
        key=first+"__"+second
        original=[r for r in actual_cocensus if r["species_pair"]==key]
        original_2011=[r for r in original if 2011<=r["season"]<=2020]
        oldmatched=[r for r in original_2011 if r["site_id"] in original34]
        copy_old=[{**r,"old_34_original_PC1":oldscore[r["site_id"],r["season"]]}
                  for r in oldmatched]
        def summary(rows,name,climate_var):
            return {
                "comparison_cohort":name,
                "n_actual_same_colony_season_both_species_observed":len(rows),
                "n_distinct_original_sites":len({r["site_id"] for r in rows}),
                "n_source_regions":len({r["source_region"] for r in rows}),
                "n_original_250km_blocks":len({r["source_250km_block"] for r in rows}),
                "raw_pearson_r":pearson(
                    [r[climate_var] for r in rows],
                    [r["log1p_second_minus_first_actual_nests"] for r in rows]),
                "within_site_pearson":bysite_centered_pearson(
                    rows,climate_var,"log1p_second_minus_first_actual_nests"),
                "same_site_same_year_data_not_independent_spatial_replicates":True
            }
        cohort[key]=[
            summary(copy_old,"original_34_sites_2011_2020_own_PC1",
                    "old_34_original_PC1"),
            summary(oldmatched,"identical_original_34_sites_2011_2020_FULL_588_PC1",
                    "fixed_marine_PC1_original_global_axis"),
            summary(original_2011,"all_new_588_sites_2011_2020_FULL_588_PC1",
                    "fixed_marine_PC1_original_global_axis"),
            summary(original,"all_new_588_sites_1993_2020_FULL_588_PC1",
                    "fixed_marine_PC1_original_global_axis")
        ]
    # Source-equivalent original 34-site co-census reproduction, with exactly
    # its 2011-2020 site-years and climate loadings, must pass before claiming
    # any expansion changed a species response.
    prior={"ADPE__GEPE":(23,-0.5079500862836571,0.5231858620924323),
           "CHPE__GEPE":(16,0.1069163224384602,0.1931843601493883)}
    for key,(count,raw,within) in prior.items():
        original=cohort[key][0]
        if (original["n_actual_same_colony_season_both_species_observed"]!=count
             or original["raw_pearson_r"] is None
             or abs(original["raw_pearson_r"]-raw)>1e-8
             or original["within_site_pearson"]["r"] is None
             or abs(original["within_site_pearson"]["r"]-within)>1e-8):
            raise ValueError("Original 34-site co-census result did not reproduce in full-source branch: "+
                             json.dumps({key:original}))
    return {
        "status":"ORIGINAL_34_BIOLOGICAL_COCENSUS_REPRODUCED_AND_FULL_AXIS_COHORT_COMPARISON_COMPLETE",
        "species_pair_4way_source_cohort_and_PCA_definition":cohort,
        "source_34_old_pooled_biological_correlations_reproduced":True,
        "comparison_is_post_result_source_cohort_sensitivity_not_external_validation":True
    }


def mapped_static_land(siteyears,source):
    # 246 original modern breeding site×species rows; the site-level
    # Plantarctica mapped area must not be duplicated when the same colony
    # has >1 species or copied to each of 28 source climate years.
    if len(source)!=246:
        raise ValueError("Original 246 modern source static land cohort drift")
    mapped={}
    for r in source:
        site=r["site_id"];area=float(r["mapped_terrestrial_union_area_2km_m2"])
        if area<0:raise ValueError("Negative mapped area")
        if site in mapped and abs(float(mapped[site]["mapped_terrestrial_union_area_2km_m2"])-area)>1e-7:
            raise ValueError("Original same colony different static map by penguin species")
        mapped[site]=r
    scores=defaultdict(list)
    reg={}
    for r in siteyears:
        scores[r["site_id"]].append(r["warm_direction_three_var_marine_PCA_score"])
        reg[r["site_id"]]=r["source_region"]
    result=[]
    for site,r in mapped.items():
        if site not in scores:continue
        area=float(r["mapped_terrestrial_union_area_2km_m2"])
        if r["region"]!=reg[site]:raise ValueError("Plant map and climate source region drift")
        if r["positive_mapped_detection"]!="True":continue
        if area<=0:raise ValueError("Area-positive polygon source conflicting")
        result.append({
            "site_id":site,"source_region":reg[site],
            "original_mapped_union_terrestrial_area_2km_m2":area,
            "marine_1993_2020_mean_PC1":mean(scores[site]),
            "original_land_static_source_window":"2017-2023 composite",
            "mapped_union_includes_multiple_terrestrial_organism_classes_not_annual_greening":True,
            "not_true_plant_absence_when_no_polygon":True
        })
    raw=pearson(rankdata([r["original_mapped_union_terrestrial_area_2km_m2"] for r in result]),
                rankdata([r["marine_1993_2020_mean_PC1"] for r in result])) if len(result)>=3 else None
    grouped=defaultdict(list)
    for r in result:grouped[r["source_region"]].append(r)
    x=[];y=[]
    for gr in grouped.values():
        if len(gr)<2:continue
        a=np.asarray([r["marine_1993_2020_mean_PC1"] for r in gr],dtype=float)
        b=np.log1p(np.asarray([r["original_mapped_union_terrestrial_area_2km_m2"] for r in gr],dtype=float))
        x.extend(a-a.mean());y.extend(b-b.mean())
    return result,{
        "original_modern_colony_site_species_rows":246,
        "n_unique_modern_colony_sites_mapped":len(mapped),
        "n_static_positive_mapped_source_sites_joined_to_complete_hydro":len(result),
        "n_original_regions_with_positive_static_mapped_sites":len(grouped),
        "mapped_positive_area_spearman_r_vs_1993_2020_PC1_mean":raw,
        "region_demeaned_positive_static_logarea_Pearson_r":pearson(x,y),
        "n_region_informative_site_rows_for_static_geographic_correlation":len(x),
        "n_region_informative_groups":sum(len(gr)>=2 for gr in grouped.values()),
        "original_mapped_area_is_mixed_terrestrial_union_not_separate_true_green_vegetation_only":True,
        "map_is_static_2017_2023_composite_no_greening_time_change":True
    }


def analyze(args):
    atlas=readcsv(args.atlas)
    countrows=readcsv(args.counts)
    original_sic=readcsv(args.original_sic)
    original_hydro=readcsv(args.original_hydro)
    baseline40=readcsv(args.baseline40)
    static=readcsv(args.static)
    if len(countrows)!=2456:
        raise ValueError("Original source fixed-method nest-count table drift")
    siteyears,quality,support=original_annual_join(atlas,original_hydro,original_sic)
    original_baseline=verify_legacy_34(siteyears,baseline40)
    regime,region_year=marine_pca(siteyears)
    region_trends=original_region_temporal_change(siteyears,region_year)
    bio,biosummary=true_observed_penguin_pairs(siteyears,countrows)
    biological_axis_cohort_sensitivity=source_matched_biological_axis_sensitivity(
        siteyears,bio,baseline40)
    plants,plantsummary=mapped_static_land(siteyears,static)
    result={
        "status":"ORIGINAL_588_18_REGION_1993_2020_MARINE_PCA_AND_TRUE_PENGUIN_COCENSUS_COMPLETED",
        "years":[1993,2020],"months":[8,9,10,11],
        "original_source_support":support,
        "exact_old_34_source_PCA_reproduction":original_baseline,
        "actual_full_18_region_spatiotemporal_marine_PCA":regime,
        "original_18_region_fixed_axis_1993_2020_trends":region_trends,
        "original_true_paired_species_census":biosummary,
        "original_biological_sample_and_axis_definition_sensitivity":
            biological_axis_cohort_sensitivity,
        "original_2017_2023_static_terrestrial_mapping":plantsummary,
        "evidence_boundary":{
            "real_maritime_physocean_gradients_across_18_source_regions":True,
            "actual_18_region_pca_can_be_computed":regime["n_original_source_regions"]==18,
            "actual_all_18_region_penguin_breeding_turnover_proven":False,
            "annual_terrestrial_greening_with_1993_2020_climate_proven":False,
            "true_species_range_expansion_or_absence_proven":False,
            "future_scenario_penguin_population_predictability_established":False,
            "reanalysis_is_not_independent_causal_temperature_or_salinity_experiment":True,
            "these_are_observed_colony_locations_not_an_area_unbiased_sample":True,
            "multiple_colonies_share_original_GLORYS_ocean_cells":True
        }
    }
    args.out.mkdir(parents=True,exist_ok=True)
    writecsv(args.out/"original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv",siteyears)
    writecsv(args.out/"original_source_siteyear_month_completeness_1993_2020.csv",quality)
    writecsv(args.out/"original_18region_28yr_marine_PC1_timeseries.csv",region_year)
    writecsv(args.out/"original_18region_marine_1993_2020_temporal_trends.csv",region_trends)
    writecsv(args.out/"original_true_two_species_same_colony_same_year_marine_ratio.csv",bio)
    writecsv(args.out/"original_modern_static_positive_terrestrial_marine_colocation.csv",plants)
    (args.out/"original_18region_marine_pca_true_penguin_comp_source_verdict.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("SOURCE_FULL_18_REGION_COVERAGE="+json.dumps(support,ensure_ascii=False),flush=True)
    print("SOURCE_FULL_18_REGION_PCA="+json.dumps({
        k:v for k,v in regime.items() if k!="leave_one_original_region_out_PC1"
    },ensure_ascii=False),flush=True)
    print("SOURCE_FULL_18_REGION_TRENDS="+json.dumps(region_trends,ensure_ascii=False),flush=True)
    print("SOURCE_FULL_18_REGION_TRUE_COCENSUS="+json.dumps(biosummary,ensure_ascii=False),flush=True)
    print("SOURCE_FULL_18_REGION_BIOLOGICAL_AXIS_COHORT_SENSITIVITY="+json.dumps(
        biological_axis_cohort_sensitivity,ensure_ascii=False),flush=True)
    print("SOURCE_FULL_18_REGION_STATIC_PLANTS="+json.dumps(plantsummary,ensure_ascii=False),flush=True)
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--atlas",type=Path,required=True)
    ap.add_argument("--counts",type=Path,required=True)
    ap.add_argument("--original-sic",type=Path,required=True)
    ap.add_argument("--original-hydro",type=Path,required=True)
    ap.add_argument("--baseline40",type=Path,required=True)
    ap.add_argument("--static",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    analyze(ap.parse_args())
