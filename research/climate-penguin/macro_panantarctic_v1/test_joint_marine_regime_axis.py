#!/usr/bin/env python3
"""Test empirical 2011–2020 marine co-gradient without inventing vegetation years.

Original 595 MAPPPD site source, OSI SAF monthly SIC and GLORYS12V1
2011–2020 salinity/thetao on exact 34/40 nearshore source-matched sites.
Uses PCA as descriptive exploration; survey-years are not zero-filled.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

import numpy as np
from scipy.stats import rankdata

COLUMNS=("source_SIC_pp","source_glorys_salinity","source_glorys_thetao_C")
REGION_MIN_FOR_TRAJECTORY=3
YEARS=tuple(range(2011,2021))
MONTHS=(8,9,10,11)
PAIRS=(("ADPE","GEPE"),("CHPE","GEPE"))


def readcsv(path):
    with path.open(encoding="utf-8",newline="") as src:
        return list(csv.DictReader(src))


def writecsv(path,records):
    if not records:
        path.write_text("no_supported_original_observations\n",encoding="utf-8")
        return
    cols=list(dict.fromkeys(k for z in records for k in z))
    with path.open("w",encoding="utf-8",newline="") as src:
        writer=csv.DictWriter(src,fieldnames=cols)
        writer.writeheader();writer.writerows(records)


def pearson(x,y):
    xx=np.asarray(x,dtype=float); yy=np.asarray(y,dtype=float)
    if len(xx)<3 or xx.shape!=yy.shape:
        return None
    dx=xx-np.mean(xx);dy=yy-np.mean(yy)
    den=float(np.sqrt(np.dot(dx,dx)*np.dot(dy,dy)))
    return float(np.dot(dx,dy)/den) if den>1e-12 else None


def pca(data):
    arr=np.asarray(data,dtype=float)
    if arr.ndim!=2 or arr.shape[1]!=3 or arr.shape[0]<4 or not np.all(np.isfinite(arr)):
        raise ValueError("PCA requires full complete 3-column original marine observations")
    mu=np.mean(arr,axis=0)
    sd=np.std(arr,axis=0)
    if np.any(sd<1e-12):
        raise ValueError("One physical marine source variable is constant")
    Z=(arr-mu)/sd
    cov=Z.T@Z/len(Z)
    eigenvalues,vec=np.linalg.eigh(cov)
    order=np.argsort(eigenvalues)[::-1]
    eig=eigenvalues[order]; vec=vec[:,order]
    if vec[2,0]<0:
        vec[:,0]*=-1
    scores=Z@vec
    return {
        "means":mu,"stds":sd,"eigenvalues":eig,
        "explained":eig/eig.sum(),"loadings":vec,"scores":scores
    }


def align_cosine(ref,alt):
    r=np.asarray(ref,dtype=float)
    a=np.asarray(alt,dtype=float)
    cos=float(np.dot(r,a)/np.linalg.norm(r)/np.linalg.norm(a))
    return {"signed_cosine_original_orientation":cos,"absolute_loading_cosine":abs(cos)}


def source_support(atlas,grid,monthly,marine):
    if len(atlas)!=595 or len({r["site_id"] for r in atlas})!=595:
        raise ValueError("Original 595-site source atlas drift")
    bysite={r["site_id"]:r for r in atlas}
    macro=[r for r in grid if r["cohort"]=="macro_40"]
    if len(macro)!=40 or len({r["site_id"] for r in macro})!=40:
        raise ValueError("Original source 40 macro geography labels changed")
    if any(r["site_id"] not in bysite for r in macro):
        raise ValueError("Unrecognized original macro site")
    good=[r for r in macro if r["grid_within_25km"]=="True"]
    bad=[r for r in macro if r["grid_within_25km"]!="True"]
    if len(good)+len(bad)!=40:
        raise ValueError("GLORYS original geographic source support changed")
    # Do not use phenology-only locations or treat a site assigned to multiple
    # sea surface grids as extra independent macro colony replication.
    location={r["site_id"]:r["location_id"] for r in good}
    if len(location)!=len(good):
        raise ValueError("Duplicate good macro source sites")
    original_marine={}
    for row in marine:
        if row["site_id"] not in location: continue
        site=row["site_id"];year=int(row["year"]);month=int(row["month"])
        if year not in YEARS or month not in MONTHS:
            continue
        key=(site,year,month)
        if key in original_marine:
            raise ValueError("Duplicate original sea-ice site×year×month")
        original_marine[key]=None
        if row["source_full_595_site_monthly_support"]=="OK":
            x=float(row["source_25km_buffer_mean_SIC_pct"])
            if not 0<=x<=100:raise ValueError("Outside original SIC physical bounds")
            original_marine[key]=x
    if len(original_marine)!=len(good)*len(YEARS)*len(MONTHS):
        raise ValueError("Original source monthly SIC incomplete")
    original_ocean={}
    for row in monthly:
        if row["location_id"] not in set(location.values()):continue
        year=int(row["year"]);month=int(row["month"])
        if year not in YEARS or month not in MONTHS:continue
        key=(row["location_id"],year,month)
        if key in original_ocean:raise ValueError("Duplicate GLORYS source ocean month")
        original_ocean[key]=row
    if len(original_ocean)!=len(good)*len(YEARS)*len(MONTHS):
        raise ValueError("Original GLORYS source monthly calendar incomplete")
    siteyears=[]
    audit=[]
    for r in good:
        site=r["site_id"];loc=r["location_id"]
        for year in YEARS:
            vals=[];ok=True
            for month in MONTHS:
                sic=original_marine[site,year,month]
                z=original_ocean[loc,year,month]
                if sic is None:ok=False;break
                sal=float(z["surface_salinity"])
                theta=float(z["surface_potential_temperature_c"])
                if not np.isfinite([sal,theta]).all() or not 30<=sal<=40 or not -3<=theta<=15:
                    ok=False;break
                vals.append((sic,sal,theta))
            audit.append({"site_id":site,"source_region":bysite[site]["source_region"],
                          "year":year,"source_months_valid":len(vals),
                          "source_4month_valid":ok})
            if ok and len(vals)==4:
                array=np.asarray(vals,dtype=float).mean(axis=0)
                siteyears.append({
                    "site_id":site,"source_region":bysite[site]["source_region"],
                    "source_250km_block":bysite[site]["polar_250km_fixed_grid_block"],
                    "latitude":float(bysite[site]["latitude"]),
                    "longitude":float(bysite[site]["longitude"]),
                    "year":year,"source_SIC_pp":float(array[0]),
                    "source_glorys_salinity":float(array[1]),
                    "source_glorys_thetao_C":float(array[2]),
                    "source_GLORYS_grid_distance_km":float(r["grid_distance_km"]),
                    "original_ice_100km_native_marine_months":4,
                    "original_GLORYS_months":4
                })
    return siteyears,audit,{
        "total_source_MACRO_observed_sites":40,
        "n_original_GLORYS_breeding_sites_within_25km":len(good),
        "n_GLORYS_breeding_sites_outside_25km_excluded":len(bad),
        "n_source_regions_with_nearshore_GLORYS":len({bysite[r["site_id"]]["source_region"] for r in good}),
        "source_sites_per_region":{
            region:n for region,n in sorted(Counter(bysite[r["site_id"]]["source_region"] for r in good).items())
        },
        "original_source_2011_2020_valid_site_year_rows":len(siteyears),
        "sites_with_any_complete_source_year":len({x["site_id"] for x in siteyears}),
        "original_ice_full_595_site_month_source_consistent":True,
        "excluded_source_site_ids":[r["site_id"] for r in bad]
    }


def fit_regime(siteyears):
    x=np.asarray([[row[k] for k in COLUMNS] for row in siteyears])
    fit=pca(x)
    for row,value in zip(siteyears,fit["scores"][:,0]):
        row["empirical_warm_oriented_marine_PC1"]=float(value)
    reg=defaultdict(list);site=defaultdict(list)
    for i,r in enumerate(siteyears):
        reg[r["source_region"]].append(i)
        site[r["site_id"]].append(i)
    scores=np.asarray(fit["scores"][:,0])
    means=np.mean(scores)
    total=float(np.sum((scores-means)**2))
    between=sum(len(ids)*(float(np.mean(scores[ids]))-means)**2 for ids in reg.values())
    within=total-between
    decomp={
       "between_source_regions_fraction_of_pooled_original_PC1_variance":
          between/total if total>0 else None,
       "within_source_regions_fraction":within/total if total>0 else None,
       "n_original_region_labels":len(reg),
       "n_original_sites":len(site),
       "site_years_not_independent_regional_replicates":True
    }
    # The sensitivity uses the SAME source sites, same years, demeaned within
    # site before PCA, then restandardized to distinguish geography from time.
    centered=np.stack([x[ids]-x[ids].mean(axis=0) for ids in site.values()])
    # Each site has exactly 10 observed annual rows in the primary fixed panel.
    for v in site.values():
        if len(v)!=len(YEARS):
            raise ValueError("Temporal PCA requires all 10 annual source years per site")
    anomalies=np.empty_like(x)
    for ids in site.values():
        anomalies[ids]=x[ids]-x[ids].mean(axis=0)
    temp=pca(anomalies)
    score_trajectory={}
    regionyears=[]
    for region,ids in sorted(reg.items()):
        yeargroup=defaultdict(list)
        for i in ids:
            yeargroup[siteyears[i]["year"]].append(i)
        for year,ix in sorted(yeargroup.items()):
            regionyears.append({
                "source_region":region,"year":year,
                "source_site_count":len(ix),
                "mean_empirical_marine_PC1":float(np.mean(scores[ix])),
                "mean_source_SIC_pp":float(np.mean(x[ix,0])),
                "mean_source_GLORYS_salinity":float(np.mean(x[ix,1])),
                "mean_source_GLORYS_thetao_C":float(np.mean(x[ix,2])),
                "within_region_source_exposure_not_an_independent_climate_experiment":True
            })
        if len(yeargroup)!=len(YEARS):
            raise ValueError("Source region not complete over 2011–2020")
        seq=[v for v in regionyears if v["source_region"]==region]
        start=seq[0]["mean_empirical_marine_PC1"]
        end=seq[-1]["mean_empirical_marine_PC1"]
        shift=end-start
        # Full ten-year temporal trends, NOT just endpoint 2011 and 2020.
        ys=np.asarray([r["year"] for r in seq],dtype=float)
        xc=ys-ys.mean()
        def time_slope_per_decade(key, omit_year=None):
            sub=[r for r in seq if omit_year is None or r["year"]!=omit_year]
            if len(sub)<5:return None
            tx=np.asarray([r["year"] for r in sub],dtype=float)
            ty=np.asarray([r[key] for r in sub],dtype=float)
            xx=tx-tx.mean()
            return float(10*np.dot(xx,ty-ty.mean())/np.dot(xx,xx))
        annual_PC1_slope=time_slope_per_decade("mean_empirical_marine_PC1")
        leave_years=[time_slope_per_decade("mean_empirical_marine_PC1",omit_year=y)
                     for y in YEARS]
        score_trajectory[region]={
            "n_sites":len({siteyears[i]["site_id"] for i in ids}),
            "2011_PC1":start,"2020_PC1":end,
            "2011_to_2020_PC1_change":shift,
            "OLS_2011_2020_PC1_change_per_decade":annual_PC1_slope,
            "leave_one_actual_source_year_out_PC1_slope_range_per_decade":[
                min(leave_years),max(leave_years)],
            "OLS_2011_2020_source_SIC_change_pp_per_decade":
                time_slope_per_decade("mean_source_SIC_pp"),
            "OLS_2011_2020_GLORYS_salinity_change_per_decade":
                time_slope_per_decade("mean_source_GLORYS_salinity"),
            "OLS_2011_2020_GLORYS_thetao_change_C_per_decade":
                time_slope_per_decade("mean_source_GLORYS_thetao_C"),
            "n_actual_source_years":len(seq),
            "single_site_source_region_not_an_independent_regional_trend":
                len({siteyears[i]["site_id"] for i in ids})<3,
            "not_causal_temperature_or_colony_distribution_change":True
        }
    # Geographic-sampling sensitivity: each original source region gets
    # equal total weight, rather than Victoria Land's many mapped colony sites.
    region_year_means = np.asarray([
        np.mean(x[yearids],axis=0)
        for region,ids in sorted(reg.items())
        for year in YEARS
        for yearids in [[i for i in ids if siteyears[i]["year"]==year]]
    ],dtype=float)
    if region_year_means.shape!=(len(reg)*len(YEARS),3):
        raise ValueError("Equal-source-region PCA temporal panel dimension changed")
    region_year_equal = pca(region_year_means)
    # The strictly geographic case: one climate observation per region,
    # averaging over real mapped source sites and over real 10-year means.
    region_mean = pca(np.asarray([
        np.mean(x[ids],axis=0) for region,ids in sorted(reg.items())
    ],dtype=float))
    site_mean = pca(np.asarray([
        np.mean(x[ids],axis=0) for site_code,ids in sorted(site.items())
    ],dtype=float))
    l1=fit["loadings"][:,0]; lt=temp["loadings"][:,0]
    result={
        "status":"EXPLORATORY_ORIGINAL_MARINE_PCA_COMPLETE",
        "marine_columns":list(COLUMNS),
        "source_site_year_count":len(siteyears),
        "original_sites":len(site),
        "source_regions":len(reg),
        "pooled_standardized_PCA_explained":[float(v) for v in fit["explained"]],
        "pooled_PC1_loadings":dict(zip(COLUMNS,[float(v) for v in l1])),
        "pooled_PC2_loadings":dict(zip(COLUMNS,[float(v) for v in fit["loadings"][:,1]])),
        "pooled_PCA_variable_means":dict(zip(COLUMNS,[float(v) for v in fit["means"]])),
        "pooled_PCA_variable_stds":dict(zip(COLUMNS,[float(v) for v in fit["stds"]])),
        "pairwise_marine_source_variable_correlations":{
            f"{COLUMNS[i]}___{COLUMNS[j]}":pearson(x[:,i],x[:,j])
            for i in range(3) for j in range(i+1,3)
        },
        "within_site_temporal_PCA_explained":[float(v) for v in temp["explained"]],
        "within_site_temporal_PC1_loadings":dict(zip(COLUMNS,[float(v) for v in lt])),
        "pooled_vs_within_site_PC1_loading_alignment":align_cosine(l1,lt),
        "region_equal_site_year_PCA_explained":[float(v) for v in region_year_equal["explained"]],
        "region_equal_site_year_PC1_loadings":dict(zip(COLUMNS,[
            float(v) for v in region_year_equal["loadings"][:,0]])),
        "pooled_vs_region_equal_PC1_loading_alignment":align_cosine(
            l1,region_year_equal["loadings"][:,0]),
        "equal_six_source_region_decadal_climatology_PCA_explained":[
            float(v) for v in region_mean["explained"]],
        "equal_six_source_region_PC1_loadings":dict(zip(COLUMNS,[
            float(v) for v in region_mean["loadings"][:,0]])),
        "one_site_one_vote_ten_year_mean_PCA_explained":[
            float(v) for v in site_mean["explained"]],
        "region_equality_warning":"Six original regions include three with one only one ocean-glorys matched colony",
        "region_difference_decomposition":decomp,
        "source_region_climate_PC1_2011_to_2020":score_trajectory,
        "site_years_in_PCA_are_not_geographic_independent_samples":True
    }
    loo=[]
    for region,ids in sorted(reg.items()):
        y=[r for r in siteyears if r["source_region"]!=region]
        if len(y)<10:continue
        ly=pca(np.asarray([[r[k] for k in COLUMNS] for r in y]))
        loo.append({
            "region_omitted":region,"n_remaining_original_sites":len({r["site_id"] for r in y}),
            "n_remaining_source_region_labels":len({r["source_region"] for r in y}),
            "PC1_explained_after_drop":float(ly["explained"][0]),
            **align_cosine(l1,ly["loadings"][:,0])
        })
    result["leave_one_source_region_out_PC1_sensitivity"]=loo
    return result,regionyears


def static_plants(siteyears,source):
    observed={r["site_id"]:r for r in source
        if r["cohort"]=="macro_40" and r["radius_m"]=="2000"
        and r["vegetation_class"]=="Vegetation"}
    if len(observed)!=40:
        raise ValueError("Original 40-site static vegetation map cohort drift")
    site_scores=defaultdict(list)
    site_regions={}
    for r in siteyears:
        site_scores[r["site_id"]].append(r["empirical_warm_oriented_marine_PC1"])
        site_regions[r["site_id"]]=r["source_region"]
    res=[]
    for site,vals in sorted(site_scores.items()):
        row=observed[site]
        if row["time_support"]!="2017-2023_composite" or row["annual_change_available"]!="False":
            raise ValueError("Static land map improperly labeled as annual change")
        area=float(row["mapped_area_m2"])
        if area<0:
            raise ValueError("Invalid original mapped positive polygon area")
        res.append({
            "site_id":site,"source_region":site_regions[site],
            "marine_PC1_2011_2020_mean":mean(vals),
            "mapped_positive_2km_polygon_area_m2":area,
            "mapped_vegetation_detection_positive":area>0,
            "map_is_static_2017_2023_NOT_an_annual_trend":True,
            "zero_mapped_polygons_is_not_vegetation_absence":True
        })
    positive=[r for r in res if r["mapped_vegetation_detection_positive"]]
    rho=pearson(rankdata([r["marine_PC1_2011_2020_mean"] for r in positive]),
                rankdata([r["mapped_positive_2km_polygon_area_m2"] for r in positive])) \
                if len(positive)>=3 else None
    # Source region-demeaned site-level correlation is a geographic
    # sensitivity; 2017-2023 vegetation remains static, not an annual outcome.
    rg=defaultdict(list)
    for r in positive:
        rg[r["source_region"]].append(r)
    rx=[];ry=[]
    for region,part in rg.items():
        if len(part)<2:continue
        x=np.asarray([r["marine_PC1_2011_2020_mean"] for r in part])
        y=np.log1p(np.asarray([r["mapped_positive_2km_polygon_area_m2"] for r in part]))
        rx.extend(x-x.mean());ry.extend(y-y.mean())
    regional_r=pearson(rx,ry)
    return res,{
        "n_marine_cohort_sites_with_static_2km_map":len(res),
        "n_sites_with_positive_mapped_vegetation_polygon_detection":len(positive),
        "n_source_regions_with_positive_static_map":len({r["source_region"] for r in positive}),
        "positive_mapped_area_vs_site_mean_2011_2020_marine_PC1_spearman_r":rho,
        "region_demeaned_log1p_positive_mapped_area_vs_site_mean_marine_PC1_pearson_r":regional_r,
        "n_region_informative_positive_mapped_sites":len(rx),
        "n_region_informative_positive_map_regions":sum(len(q)>=2 for q in rg.values()),
        "correlation_is_cross_sectional_and_region_confounded":True,
        "source_static_vegetation_2017_2023_composite":True,
        "vegetation_1986_to_2021_year_change_inferred":False
    }


def penguin_composition(siteyears,counts):
    # No "gentoo share" unless focal and comparator species were BOTH
    # genuinely counted for the same colony site and season.
    countmap={}
    for r in counts:
        y=int(r["season"])
        if y not in YEARS or r["species"] not in ("ADPE","GEPE","CHPE"):continue
        key=r["site_id"],y,r["species"]
        if key in countmap:raise ValueError("Duplicated original site year species")
        n=int(r["observed_nest_count"])
        if n<0:raise ValueError("Invalid observed original nests")
        countmap[key]=n
    matched={}
    for r in siteyears:
        matched[r["site_id"],r["year"]]=r
    out=[];summ={}
    for baseline,gentoo in PAIRS:
        subset=[]
        for (site,year),r in matched.items():
            n0=countmap.get((site,year,baseline))
            n1=countmap.get((site,year,gentoo))
            if n0 is None or n1 is None:continue
            record={
                "site_id":site,"source_region":r["source_region"],
                "source_250km_block":r["source_250km_block"],
                "year":year,"species_pair":baseline+"__"+gentoo,
                "nests_source_baseline_species":n0,
                "nests_source_gentoo":n1,
                "log1p_gentoo_minus_baseline_observed_nests":float(
                    np.log1p(n1)-np.log1p(n0)),
                "marine_PC1":r["empirical_warm_oriented_marine_PC1"],
                "no_missing_species_census_translated_to_zero":True
            }
            subset.append(record);out.append(record)
        bysite=defaultdict(list)
        for r in subset:bysite[r["site_id"]].append(r)
        valid=[r for r in subset if len(bysite[r["site_id"]])>=2]
        raw=pearson([r["marine_PC1"] for r in subset],
                    [r["log1p_gentoo_minus_baseline_observed_nests"] for r in subset])
        xs=[];ys=[]
        for site,rr in bysite.items():
            if len(rr)<2:continue
            mu1=mean(r["marine_PC1"] for r in rr)
            mu2=mean(r["log1p_gentoo_minus_baseline_observed_nests"] for r in rr)
            xs.extend([r["marine_PC1"]-mu1 for r in rr])
            ys.extend([r["log1p_gentoo_minus_baseline_observed_nests"]-mu2 for r in rr])
        within=pearson(xs,ys) if len(bysite)>=3 and len(xs)>=5 else None
        # Post-result geographic site influence: a repeated census year is
        # not independent information about the species' climate preference.
        within_leave_one_site=[]
        for omitted_site in sorted(bysite):
            retained={site_code:rr for site_code,rr in bysite.items()
                      if site_code != omitted_site and len(rr)>=2}
            xoo=[];yoo=[]
            for site_code,rr in retained.items():
                m1=mean(r["marine_PC1"] for r in rr)
                m2=mean(r["log1p_gentoo_minus_baseline_observed_nests"] for r in rr)
                xoo.extend(r["marine_PC1"]-m1 for r in rr)
                yoo.extend(r["log1p_gentoo_minus_baseline_observed_nests"]-m2 for r in rr)
            rr=pearson(xoo,yoo) if len(retained)>=3 and len(xoo)>=5 else None
            within_leave_one_site.append({
                "omitted_original_colony_site":omitted_site,
                "n_remaining_informative_sites":len(retained),
                "n_remaining_same_year_count_records":len(xoo),
                "within_site_demeaned_r":rr})
        loovalues=[r["within_site_demeaned_r"] for r in within_leave_one_site
                   if r["within_site_demeaned_r"] is not None]
        summ[baseline+"__"+gentoo]={
            "n_exact_source_same_site_same_season_pairs":len(subset),
            "n_original_sites":len(bysite),
            "n_original_source_regions":len({r["source_region"] for r in subset}),
            "n_original_polar_250km_blocks":len({r["source_250km_block"] for r in subset}),
            "n_sites_with_more_than_one_true_cocensus_year":sum(len(v)>=2 for v in bysite.values()),
            "raw_same_season_record_correlation_r":raw,
            "within_site_demeaned_same_season_correlation_r":within,
            "leave_one_actual_colony_out_within_site_r_range":[
                min(loovalues),max(loovalues)] if loovalues else None,
            "n_valid_leave_one_actual_colony_out_diagnostics":len(loovalues),
            "leave_one_site_out_diagnostics":within_leave_one_site,
            "only_two_spatial_blocks_no_climate_replication":len({
                r["source_250km_block"] for r in subset})<=2,
            "source_support_only_not_a_18_region_abundance_proportion_model":True,
            "not_independently_held_out_or_a_causal_warming_test":True
        }
    return out,summ


def analyze(args):
    atlas=readcsv(args.atlas)
    grid=readcsv(args.ocean_grid)
    ocean=readcsv(args.ocean)
    sic=readcsv(args.sic)
    vegetation=readcsv(args.vegetation)
    counts=readcsv(args.counts)
    if len(sic)!=71400 or len(counts)!=2456:
        raise ValueError("Source-pinned satellite or original penguin 595-site universe drift")
    siteyears,audit,support=source_support(atlas,grid,ocean,sic)
    if len(siteyears)<50:
        raise ValueError("Insufficient original common observed 2011–2020 climate site-years")
    # Consistent 10-year source panel only: this is an exploratory fixed 2011–2020
    # source feasibility gate, not outcome-selected interpolation across gaps.
    fullsites=Counter(r["site_id"] for r in siteyears)
    siteyears=[r for r in siteyears if fullsites[r["site_id"]]==10]
    if len(siteyears)<40:
        raise ValueError("Insufficient all-ten-year matched source sites")
    support["n_complete_10year_original_GLORYS_and_SIC_sites"]=len({r["site_id"] for r in siteyears})
    support["n_complete_10year_siteyear_rows"]=len(siteyears)
    fit,regionyears=fit_regime(siteyears)
    plantpoints,plant=static_plants(siteyears,vegetation)
    crows,ratios=penguin_composition(siteyears,counts)
    verdict={
        "status":"EXPLORATORY_ANTARCTIC_MARINE_ENVIRONMENT_ONE_AXIS_FEASIBILITY_AND_COUNT_SUPPORT_COMPLETE",
        "primary_observation_years":[2011,2020],
        "observed_months":[8,9,10,11],
        "original_full_18region_5variable_joint_PCA_status":"NO_GO_MISSING_REGION_BY_YEAR_SALINITY_AND_TEMPORAL_LAND_VEGETATION",
        "original_595_colonies_and_18_regions_are_geographic_source_denominator_not_34site_PCA_replication":True,
        "marine_source":support,
        "pooled_and_within_site_marine_PCA":fit,
        "vegetation_STATIC_composite_cross_sectional":plant,
        "genuine_penguin_cocensus_logratio_support":ratios,
        "warnings":[
            "GLORYS12V1 salinity and thetao are ocean REANALYSIS, not independent measured pure greenhouse warming.",
            "2011–2020 joint marine co-variation cannot establish climatic trends for 1991–2010.",
            "40 source macro mapped sites, 34 within 25km of nearest reanalysis marine grid; many are in one region.",
            "Across site, region, and year all geographical samples are spatially/temporally non-independent.",
            "The original 2017–2023 vegetation positive polygon composite is STATIC, never 2011–2020 annual greening.",
            "Species ratios require observed same colony and season in both species, not 18-region sampling fractions.",
            "No biological causation, niche tracking, climate debt, 18-region future forecast, or new subantarcticization index is established by PCA."
        ]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    writecsv(args.out/"original_GLORYS_OSISAF_2011_2020_real_3var_site_year_marine_PCA.csv",siteyears)
    writecsv(args.out/"original_marine_source_all_macro_site_year_quality.csv",audit)
    writecsv(args.out/"marine_joint_PC1_6region_2011_2020_year_summary.csv",regionyears)
    writecsv(args.out/"static_2017_2023_plantarctica_paired_site_context.csv",plantpoints)
    writecsv(args.out/"observed_2species_same_site_same_year_joint_marine_PC1.csv",crows)
    (args.out/"marine_joint_PCA_environment_and_penguin_macro_feasibility.json").write_text(
        json.dumps(verdict,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("REGIME_AXIS_SOURCE_SUPPORT="+json.dumps(support,ensure_ascii=False),flush=True)
    print("REGIME_AXIS_PCA="+json.dumps(fit,ensure_ascii=False),flush=True)
    print("REGIME_AXIS_STATIC_VEGETATION="+json.dumps(plant,ensure_ascii=False),flush=True)
    print("REGIME_AXIS_OBSERVED_PENGUIN_COCENSUS="+json.dumps(ratios,ensure_ascii=False),flush=True)
    return verdict


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--atlas",type=Path,required=True)
    p.add_argument("--counts",type=Path,required=True)
    p.add_argument("--sic",type=Path,required=True)
    p.add_argument("--ocean-grid",type=Path,required=True)
    p.add_argument("--ocean",type=Path,required=True)
    p.add_argument("--vegetation",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    analyze(p.parse_args())


if __name__=="__main__":
    main()
