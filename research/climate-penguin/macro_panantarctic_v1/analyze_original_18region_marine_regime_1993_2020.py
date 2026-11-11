#!/usr/bin/env python3
"""Original 595-site Antarctic 18-region SIC/GLORYS climate-regime PCA, 1993–2020.

Interpret multi-axis marine climate, local/region temporal separation and
strict source-recorded penguin co-census WITHOUT biological pseudoabsences or
fabricated annual vegetation changes. Exploratory, not causal or a climate debt.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from test_joint_marine_regime_axis import pca,pearson,align_cosine

YEARS=tuple(range(1993,2021))
MONTHS=(8,9,10,11)
COLUMNS=("SIC_pp","GLORYS_salinity","GLORYS_thetao_C")
COUNT_PAIRS=(("ADPE","GEPE"),("CHPE","GEPE"),("ADPE","CHPE"))
OLD_PCA_PC1=0.7094310203120341
SOURCE_SITE_COUNT=595
SOURCE_GLORYS_COUNT=588
EXPECTED_GLORYS_MONTHS=588*112
EXPECTED_ICE_MONTHS=595*120
SOURCE_REGION_COUNT=18


def array_pca(df,columns=COLUMNS):
    return pca(df[list(columns)].to_numpy(dtype=np.float64))


def fit_slope(years,vals):
    x=np.asarray(years,dtype=np.float64);y=np.asarray(vals,dtype=np.float64)
    if len(x)<5 or len(x)!=len(y) or not np.isfinite(x).all() or not np.isfinite(y).all():
        return None
    xc=x-x.mean()
    return float(10*np.dot(xc,y-y.mean())/np.dot(xc,xc))


def original_monthly_joint(hydro_csv,ice_csv,atlas_csv):
    atlas=pd.read_csv(atlas_csv)
    gl=pd.read_csv(hydro_csv)
    ice=pd.read_csv(ice_csv)
    if (len(atlas)!=SOURCE_SITE_COUNT or len(gl)!=EXPECTED_GLORYS_MONTHS
        or len(ice)!=EXPECTED_ICE_MONTHS):
        raise ValueError("Pinned source atlas / 28-year GLORYS / 30-year OSI SAF rows changed")
    if not (atlas.site_id.nunique()==SOURCE_SITE_COUNT
           and gl.site_id.nunique()==SOURCE_GLORYS_COUNT
           and gl.groupby("site_id").size().eq(len(YEARS)*4).all()):
        raise ValueError("Original GLORYS 588 fixed site/month calendar source drift")
    ice=ice.loc[ice.year.isin(YEARS)&ice.month.isin(MONTHS)]
    if ice.duplicated(["site_id","year","month"]).any() or gl.duplicated(["site_id","year","month"]).any():
        raise ValueError("Original repeated monthly marine source key")
    merged=gl.merge(ice[["site_id","year","month","source_full_595_site_monthly_support",
                         "source_25km_buffer_mean_SIC_pct"]],
                    on=["site_id","year","month"],how="left",validate="one_to_one")
    if len(merged)!=len(gl) or merged.source_full_595_site_monthly_support.isna().any():
        raise ValueError("Original 1993–2020 ocean GLORYS/SIC site-month join incomplete")
    merged["source_all_marine_months_valid"]=(
        merged["source_both_ocean_variables_valid"].astype(str).str.lower().eq("true")
        & merged["source_full_595_site_monthly_support"].eq("OK")
        & merged[["source_25km_buffer_mean_SIC_pct","surface_GLORYS_salinity",
                  "surface_GLORYS_thetao_C"]].notna().all(axis=1))
    original_region=atlas.set_index("site_id")["source_region"].to_dict()
    if any(original_region[r.site_id]!=r.source_region for r in gl[["site_id","source_region"]].drop_duplicates().itertuples(index=False)):
        raise ValueError("Source GLORYS/method-fixed original source-region mismatches")
    source_year_support=merged.groupby(["site_id","year"],as_index=False).agg(
        source_region=("source_region","first"),
        source_250km_block=("source_250km_block","first"),
        source_original_wet_grid_y=("source_original_wet_grid_y","first"),
        source_original_wet_grid_x=("source_original_wet_grid_x","first"),
        months=("month","nunique"),
        valid_months=("source_all_marine_months_valid","sum"),
        SIC_pp=("source_25km_buffer_mean_SIC_pct","mean"),
        GLORYS_salinity=("surface_GLORYS_salinity","mean"),
        GLORYS_thetao_C=("surface_GLORYS_thetao_C","mean"))
    if len(source_year_support)!=SOURCE_GLORYS_COUNT*len(YEARS) or not source_year_support.months.eq(4).all():
        raise ValueError("Original 588×28 site/year grain not preserved")
    years=source_year_support.loc[source_year_support.valid_months.eq(4)].copy()
    full_sites=years.groupby("site_id").year.nunique()
    full_sites=set(full_sites.index[full_sites==len(YEARS)])
    balanced=years.loc[years.site_id.isin(full_sites)].copy()
    if balanced.empty or not np.isfinite(balanced[list(COLUMNS)].to_numpy()).all():
        raise ValueError("No common complete 1993–2020 marine site-year source panel")
    if balanced.duplicated(["site_id","year"]).any():
        raise ValueError("Original balanced site-year source rows duplicated")
    eligible_regions=balanced.source_region.nunique()
    return balanced,source_year_support,{
        "original_595_fixed_observed_colony_atlas_sites":SOURCE_SITE_COUNT,
        "original_source_588_within25km_nearest_GLORYS_wet_sites":SOURCE_GLORYS_COUNT,
        "original_source_1993_2020_588_times_112_GLORYS_months":len(gl),
        "original_sic_1991_2020_595_times_120_months":EXPECTED_ICE_MONTHS,
        "n_GLORYS_SIC_months_both_valid":int(merged.source_all_marine_months_valid.sum()),
        "n_source_any_complete_four_month_years":len(years),
        "n_original_sites_with_all_28_years_complete":balanced.site_id.nunique(),
        "n_complete_1993_2020_source_site_years":len(balanced),
        "n_original_regions_with_fixed_complete_28year_marine_sites":eligible_regions,
        "original_region_site_count_fixed":dict(
            sorted(balanced[["site_id","source_region"]].drop_duplicates().groupby("source_region").size().to_dict().items())),
        "source_not_penguin_true_absence_or_species_climate_response":True
    }


def fixed_pca_and_region_temporal(st):
    df=st.copy()
    pooled=array_pca(df)
    df["pooled_PC1"]=pooled["scores"][:,0]
    # Original 18-region site composition is highly uneven. For the
    # continental MARINE climate axis, one source region-year is one vote:
    ry=df.groupby(["source_region","year"],as_index=False).agg(
        n_original_source_sites=("site_id","nunique"),
        mean_SIC_pp=("SIC_pp","mean"),
        mean_GLORYS_salinity=("GLORYS_salinity","mean"),
        mean_GLORYS_thetao_C=("GLORYS_thetao_C","mean"))
    if ry.source_region.nunique()<10:
        raise ValueError("Continental original source regional marine climatic evidence insufficient")
    if ry.groupby("source_region").year.nunique().min()!=len(YEARS):
        raise ValueError("Not every source region has all 28 true observed joint marine years")
    for index,field in enumerate(COLUMNS):
        ry[field]=ry[["mean_SIC_pp","mean_GLORYS_salinity","mean_GLORYS_thetao_C"]].to_numpy()[:,index]
    reference=array_pca(ry)
    ry["equal_region_marine_PC1"]=reference["scores"][:,0]
    # Fix the actual original PCA transformation for projected colony-year
    # scores, rather than fitting one PCA per region and inventing comparability.
    originals=df[list(COLUMNS)].to_numpy(dtype=float)
    df["equal_region_PC1"]=(
        ((originals-reference["means"])/reference["stds"])
        @ reference["loadings"][:,0])
    # Same unique source native wet grid can be reused by many original
    # colony records. Keep an independent cell-year equal-weight sensitivity.
    unique=df.groupby(["source_original_wet_grid_y","source_original_wet_grid_x","year"],
                as_index=False)[list(COLUMNS)].mean()
    native=array_pca(unique)
    sites=df.groupby("site_id",as_index=False)[list(COLUMNS)].mean()
    means=array_pca(sites)
    # Site-demeaned temporal matrix removes local geographic differences
    # before each variable is globally standardized.
    site_means=df.groupby("site_id")[list(COLUMNS)].transform("mean")
    site_anom=df[list(COLUMNS)]-site_means
    temporal=pca(site_anom.to_numpy())
    base_loading=reference["loadings"][:,0]
    out={
        "status":"ORIGINAL_18REGION_1993_2020_CONTINENTAL_MARINE_REGIME_SOURCE_PCA_COMPLETE",
        "original_marine_variables":list(COLUMNS),
        "n_original_balanced_actual_sites":df.site_id.nunique(),
        "n_real_site_year_rows":len(df),
        "n_actual_source_regions":df.source_region.nunique(),
        "n_actual_source_native_wet_cells":df[["source_original_wet_grid_y","source_original_wet_grid_x"]].drop_duplicates().shape[0],
        "n_equal_weight_original_region_years":len(ry),
        "equal_18region_year_marine_PCA_PC_explained":[float(z) for z in reference["explained"]],
        "equal_18region_PC1_loadings":dict(zip(COLUMNS,map(float,base_loading))),
        "equal_18region_PC2_loadings":dict(zip(COLUMNS,map(float,reference["loadings"][:,1]))),
        "original_region_year_equal_PCA_means":dict(zip(COLUMNS,map(float,reference["means"]))),
        "original_region_year_equal_PCA_sds":dict(zip(COLUMNS,map(float,reference["stds"]))),
        "all_site_year_pooled_PCA_PC_explained":[float(z) for z in pooled["explained"]],
        "all_site_year_PC1_loadings":dict(zip(COLUMNS,map(float,pooled["loadings"][:,0]))),
        "pooled_loading_alignment_with_equal_region":align_cosine(base_loading,pooled["loadings"][:,0]),
        "unique_native_marine_cell_year_PCA_PC_explained":[float(z) for z in native["explained"]],
        "unique_native_marine_cell_PC1_loadings":dict(zip(COLUMNS,map(float,native["loadings"][:,0]))),
        "site_equal_28year_climatology_PCA_PC_explained":[float(z) for z in means["explained"]],
        "within_site_temporal_1993_2020_PCA_PC_explained":[float(z) for z in temporal["explained"]],
        "within_site_temporal_PC1_loadings":dict(zip(COLUMNS,map(float,temporal["loadings"][:,0]))),
        "within_site_vs_equal_region_PC1_cosine":align_cosine(base_loading,temporal["loadings"][:,0]),
        "source_GLORYS_reanalysis_not_independent_marine_measurement":True,
        "site_years_and_regions_not_independent_climate_interventions":True,
        "pairwise_equal_region_year_variable_Pearson_r":{
            f"{COLUMNS[i]}__{COLUMNS[j]}":pearson(ry[COLUMNS[i]],ry[COLUMNS[j]])
            for i in range(3) for j in range(i+1,3)
        }
    }
    score=np.asarray(df["equal_region_PC1"])
    grand=float(score.mean())
    total=float(np.sum((score-grand)**2))
    between=sum(len(group)*(float(group.equal_region_PC1.mean())-grand)**2
                for _,group in df.groupby("source_region"))
    out["site_year_PC1_variance_between_reporting_regions_fraction"]=between/total
    out["site_year_PC1_variance_within_reporting_regions_fraction"]=1-between/total
    loo=[]
    for region in sorted(ry.source_region.unique()):
        drop=ry.loc[ry.source_region!=region]
        fit=array_pca(drop)
        loo.append({
            "omitted_original_source_region":region,
            "n_other_source_regions":drop.source_region.nunique(),
            "remaining_region_years":len(drop),
            "PC1_explained_after_region_removed":float(fit["explained"][0]),
            **align_cosine(base_loading,fit["loadings"][:,0])
        })
    out["leave_one_original_region_out_marine_PC1_sensitivity"]=loo
    trend=[]
    for region,g in ry.groupby("source_region"):
        g=g.sort_values("year")
        ys=g.year.to_numpy()
        slopes={}
        for v in ("equal_region_marine_PC1","SIC_pp","GLORYS_salinity","GLORYS_thetao_C"):
            vals=g[v].to_numpy(dtype=float)
            slopes[v+"_OLS_per_decade"]=fit_slope(ys,vals)
            if v=="equal_region_marine_PC1":
                omissions=[fit_slope(ys[ys!=y],vals[ys!=y]) for y in ys]
                slopes["PC1_leave_one_actual_year_out_slope_per_decade_range"]=[
                    min(omissions),max(omissions)]
        years_geos=[z["site_id"] for z in df.loc[df.source_region==region][["site_id"]].drop_duplicates().to_dict("records")]
        if len(g)!=len(YEARS):
            raise ValueError("Original climate regional annual temporal source incomplete")
        summary={
            "source_region":region,
            "n_original_complete_28year_breeding_site_coordinates":len(years_geos),
            "n_unique_original_GLORYS_wet_ocean_cells":df.loc[df.source_region==region][
               ["source_original_wet_grid_y","source_original_wet_grid_x"]].drop_duplicates().shape[0],
            **slopes,
            "mean_1993_2000_PC1":float(g.loc[g.year.between(1993,2000),"equal_region_marine_PC1"].mean()),
            "mean_2001_2010_PC1":float(g.loc[g.year.between(2001,2010),"equal_region_marine_PC1"].mean()),
            "mean_2011_2020_PC1":float(g.loc[g.year.between(2011,2020),"equal_region_marine_PC1"].mean()),
            "first_source_decade_is_8years_not_10years":True,
            "n_real_calendar_years":len(g),
            "region_geographic_replication_limited_to_single_original_site":
                len(years_geos)==1,
            "not_phenotypic_penguin_shift_or_green_vegetation_trajectory":True
        }
        trend.append(summary)
    out["region_28year_direction_support"]= {
        "n_eligible_original_regions":len(trend),
        "n_PC1_positive_28year_OLS":sum(x["equal_region_marine_PC1_OLS_per_decade"]>0 for x in trend),
        "n_PC1_negative_28year_OLS":sum(x["equal_region_marine_PC1_OLS_per_decade"]<0 for x in trend),
        "n_regions_source_site_count_ge_3":sum(x["n_original_complete_28year_breeding_site_coordinates"]>=3 for x in trend),
        "n_region_PC1_slope_remains_positive_after_any_one_year_deletion":sum(
            x["PC1_leave_one_actual_year_out_slope_per_decade_range"][0]>0 for x in trend),
        "n_region_PC1_slope_remains_negative_after_any_one_year_deletion":sum(
            x["PC1_leave_one_actual_year_out_slope_per_decade_range"][1]<0 for x in trend),
        "n_region_PC1_slope_year_delete_sign_ambiguous":sum(
            x["PC1_leave_one_actual_year_out_slope_per_decade_range"][0]<=0<=
            x["PC1_leave_one_actual_year_out_slope_per_decade_range"][1] for x in trend)
    }
    return df,ry,trend,out


def static_plants(full,source):
    src=pd.read_csv(source)
    if len(src)!=246:
        raise ValueError("Original 246 mapped land site×species source cohort changed")
    group=src.groupby("site_id")
    if group.ngroups!=222:
        raise ValueError("Original 222 mapped land source site IDs changed")
    # Positive-mapped polygon area attached to same site across species is
    # one physical measurement, not replicated independent species evidence.
    mismatched=group.mapped_terrestrial_union_area_2km_m2.nunique().gt(1)
    if mismatched.any():
        raise ValueError("Original static plant polygon map site area differed by species")
    land=src.drop_duplicates("site_id").copy()
    means=full.groupby(["site_id","source_region"],as_index=False)["equal_region_PC1"].mean()
    joined=means.merge(land[["site_id","mapped_terrestrial_union_area_2km_m2",
                             "positive_mapped_detection","map_status"]],
                       on="site_id",how="inner",validate="one_to_one")
    positive=joined.loc[(joined.positive_mapped_detection.astype(str).str.lower()=="true")
                        &(joined.mapped_terrestrial_union_area_2km_m2>0)].copy()
    raw=pearson(rankdata(positive.equal_region_PC1),
                rankdata(positive.mapped_terrestrial_union_area_2km_m2)) if len(positive)>=3 else None
    informative=positive.groupby("source_region").filter(lambda g:len(g)>=2).copy()
    if not informative.empty:
        informative["x"]=informative.equal_region_PC1 - informative.groupby(
            "source_region").equal_region_PC1.transform("mean")
        informative["y"]=np.log1p(informative.mapped_terrestrial_union_area_2km_m2)
        informative["y"]=informative.y-informative.groupby("source_region").y.transform("mean")
        conditioned=pearson(informative.x,informative.y)
    else:conditioned=None
    summary={
        "n_original_246_site_species_land_observations":len(src),
        "n_original_222_distinct_sites_with_static_map":222,
        "n_original_source_land_sites_with_full_1993_2020_marine_cohort":len(joined),
        "n_actual_mapped_vegetation_positive_sites":len(positive),
        "n_original_regions_with_positive_vegetation_polygon_sites":positive.source_region.nunique(),
        "static_positive_mapped_2km_area_vs_marine_climate_mean_rank_rho":raw,
        "n_region_informative_positive_vegetation_sites":len(informative),
        "n_region_informative_vegetation_regions":informative.source_region.nunique(),
        "region_demeaned_log1p_mapped_area_vs_marine_PC1_pearson_r":conditioned,
        "original_map_is_2017_2023_composite_without_annual_plant_change":True,
        "mapped_polygon_non_detection_is_not_true_vegetation_absence":True
    }
    return joined,summary


def original_penguin_cocensus(full,counts_csv):
    src=pd.read_csv(counts_csv)
    if len(src)!=2456 or src.duplicated(["site_id","species","season"]).any():
        raise ValueError("Original MAPPPD 2456 observed count source duplicated")
    count=src.loc[src.season.isin(YEARS)&src.species.isin(("ADPE","CHPE","GEPE"))].copy()
    original_year=full[["site_id","year","source_region","source_250km_block","equal_region_PC1"]]
    original_year=original_year.rename(columns={"year":"season"})
    combined=count.merge(original_year,on=["site_id","season"],how="inner",validate="many_to_one")
    records=[];summary={}
    for a,b in COUNT_PAIRS:
        x=combined.loc[combined.species==a,["site_id","season","observed_nest_count",
                      "source_region","source_250km_block","equal_region_PC1"]]
        y=combined.loc[combined.species==b,["site_id","season","observed_nest_count"]]
        paired=x.merge(y,on=["site_id","season"],validate="one_to_one",suffixes=("_A","_B"))
        paired["species_pair"]=a+"__"+b
        paired["log1p_B_minus_A_observed_nests"]=np.log1p(paired.observed_nest_count_B) - np.log1p(paired.observed_nest_count_A)
        paired["original_unrecorded_species_not_filled_with_zero"]=True
        records.append(paired)
        nsites=paired.site_id.nunique()
        raw=pearson(paired.equal_region_PC1,paired.log1p_B_minus_A_observed_nests)
        by=paired.groupby("site_id")
        valid=paired.loc[paired.site_id.isin(by.size().index[by.size()>=2])].copy()
        if nsites>=3 and len(valid)>=5:
            valid["x"]=valid.equal_region_PC1-valid.groupby("site_id").equal_region_PC1.transform("mean")
            valid["y"]=valid.log1p_B_minus_A_observed_nests-valid.groupby("site_id").log1p_B_minus_A_observed_nests.transform("mean")
            within=pearson(valid.x,valid.y)
        else:within=None
        summary[a+"__"+b]={
            "n_original_same_colony_same_year_both_species_actual_counts":len(paired),
            "n_unique_original_breeding_site_codes":nsites,
            "n_original_source_regions":paired.source_region.nunique(),
            "n_original_250km_spatial_blocks":paired.source_250km_block.nunique(),
            "n_original_individual_sites_repeated_at_least_twice":valid.site_id.nunique() if len(valid)>0 else 0,
            "n_actual_site_years_contributing_within_site_r":len(valid),
            "raw_marine_PC1_vs_site_log1p_species_nest_ratio_pearson_r":raw,
            "within_site_demeaned_r":within,
            "n_source_regions_with_two_or_more_distinct_sites":sum(
                paired.groupby("source_region").site_id.nunique()>=2) if len(paired)>0 else 0,
            "not_equivalent_to_18region_same_year_community_population_share":True,
            "not_same_census_date_or_observer_source_verified":True,
            "no_unknown_or_unobserved_species_filled_as_true_zero":True
        }
    return pd.concat(records,ignore_index=True) if records else pd.DataFrame(),summary


def verify_original_34_2011_2020(data,grid):
    support=pd.read_csv(grid)
    legacy=support.loc[(support.cohort=="macro_40")
              &(support.grid_within_25km)].site_id
    if len(legacy)!=34:
        raise ValueError("Original legacy 34 ocean source sites changed")
    sub=data.loc[data.site_id.isin(set(legacy))&data.year.between(2011,2020)]
    if len(sub)!=340:
        raise ValueError("Original legacy 34×10 true hydro/ice 2011–2020 panel not reproduced")
    fit=array_pca(sub)
    err=abs(float(fit["explained"][0])-OLD_PCA_PC1)
    if err>1e-8:
        raise ValueError(f"Original 34-site baseline 2011–2020 SIC GLORYS PC1 value drift {err}")
    return {
       "original_full_34_nearshore_valid_sites_repeated":34,
       "original_2011_2020_340_site_year_source_rows":340,
       "baseline_34_site_pooled_PC1_explained_recomputed":float(fit["explained"][0]),
       "baseline_34_site_PC1_explained_max_abs_difference":err,
       "original_benchmark_PC1_explained":OLD_PCA_PC1,
       "status":"PREVIOUS_ORIGINAL_34_SITE_MARINE_PCA_REPRODUCED"
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--glorys-monthly",required=True,type=Path)
    p.add_argument("--osi-monthly",required=True,type=Path)
    p.add_argument("--atlas",required=True,type=Path)
    p.add_argument("--original40-grid",required=True,type=Path)
    p.add_argument("--counts",required=True,type=Path)
    p.add_argument("--mapped-land",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    marine,allsiteyear,source=original_monthly_joint(
        a.glorys_monthly,a.osi_monthly,a.atlas)
    legacy=verify_original_34_2011_2020(marine,a.original40_grid)
    df,ry,reg,physical=fixed_pca_and_region_temporal(marine)
    land,plants=static_plants(df,a.mapped_land)
    biological,biop=original_penguin_cocensus(df,a.counts)
    result={
        "status":"ORIGINAL_18REGION_HISTORICAL_MARINE_SIC_GLORYS_AND_TRUE_COCENSUS_EXPLORATORY_COMPLETE",
        "data_sources":{
            "original_species":"MAPPPD source 595 sites 18 regions fixed count method",
            "sea_ice":"EUMETSAT OSI SAF v3.1 original 25km grid 100km marine pixel buffer site average",
            "ocean":"Copernicus GLOBAL_MULTIYEAR_PHY_001_030 GLORYS12V1 202311 original 0.083degree wet nearest surface model reanalysis",
            "vegetation":"Plantarctica 2017–2023 STATIC 2km mapped source site area; no year observations",
            "original_years":[YEARS[0],YEARS[-1]],"months":list(MONTHS)
        },
        "original_source_595site_28year_join":source,
        "previous_source_34site_10year_exact_benchmark":legacy,
        "physical_18_source_region_marine_PCA":physical,
        "static_original_222site_map_crossover":plants,
        "actual_same_site_same_season_penguin_species_composition":biop,
        "limits":[
            "Surface salinity and thetao originate in GLORYS reanalysis assimilating observations including SIC/SST, not independent mechanisms.",
            "PCA may describe seawater environmental co-variation but not identify a unique warming causal axis or marine niche preference.",
            "18 region-year hydro/ice values do NOT mean every region has independently simultaneous two-species breeding censuses.",
            "Regions and mapped source colonies vary in numbers and many sites share original model cells.",
            "1993–2000 first decade has only 8 years, 2001–2010 and 2011–2020 10; avoid comparable decade velocities without adjustment.",
            "Static 2017–2023 mapped vegetation is not 1993–2020 local greening and non-detection is not genuine plant absence.",
            "Original counts are positive-known site observations with no unknown absences, so no inferred true penguin range boundary or species turnover percentages.",
            "No causal warmer sea ice salinity decomposition, temperature-only effects, niche tracking debts, or future CMIP6 breeding numbers."
        ]
    }
    a.out.mkdir(parents=True,exist_ok=True)
    df.to_csv(a.out/"all_original_18region_1993_2020_real_joint_marine_3var_site_year.csv",index=False)
    ry.to_csv(a.out/"all_original_18region_1993_2020_real_joint_marine_region_year.csv",index=False)
    pd.DataFrame(reg).to_csv(a.out/"original_18region_1993_2020_marine_PC1_28year_trends.csv",index=False)
    allsiteyear.to_csv(a.out/"all_original_site_year_4month_physical_source_support.csv",index=False)
    land.to_csv(a.out/"static_source_vegetation_18region_marine_climate_cooccurrence.csv",index=False)
    biological.to_csv(a.out/"original_true_cocensus_3species_pairs_1993_2020_with_18region_marine_PC1.csv",index=False)
    (a.out/"ORIGINAL_18REGION_28YEAR_SIC_GLORYS_MARINE_AND_PENGUIN_VERDICT.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PENGUIN_18REGION_28YR_SOURCE="+json.dumps(source,ensure_ascii=False),flush=True)
    print("PENGUIN_18REGION_28YR_LEGACY="+json.dumps(legacy,ensure_ascii=False),flush=True)
    print("PENGUIN_18REGION_28YR_PCA="+json.dumps(physical,ensure_ascii=False),flush=True)
    print("PENGUIN_18REGION_28YR_REGION_TRENDS="+json.dumps(reg,ensure_ascii=False),flush=True)
    print("PENGUIN_18REGION_28YR_STATIC_VEGETATION="+json.dumps(plants,ensure_ascii=False),flush=True)
    print("PENGUIN_18REGION_28YR_GENUINE_COCENSUS="+json.dumps(biop,ensure_ascii=False),flush=True)


if __name__=="__main__":
    main()
