#!/usr/bin/env python3
"""Original EUMETSAT–GLORYS Antarctic thermal-ice vs salinity temporal synchrony.

Use only previous publisher-verified 588-colony×28y physical source data and
fixed site/regional identifiers; verify exact 18×28 original physical PC1
reference. This is geographical/time covariance, not penguin demography.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from analyze_original_588_18region_marine_pca import readcsv, writecsv
from test_dual_marine_axis_paired_penguin_response import reconstruct_source_pcs

YEARS=tuple(range(1993,2021))
DECADES=((1993,2000),(2001,2010),(2011,2020))
ALL_N=18
SUPPORTED_N=13
PHASE_SHIFTS=1000
RNG_SEED=20261112
SOURCE_PC_KEYS=("PC1_warm_low_ice_original_score","PC2_saline_original_score")


def pearson(x,y):
    xx=np.asarray(x,dtype=float)
    yy=np.asarray(y,dtype=float)
    if xx.shape!=yy.shape or len(xx)<3 or not np.all(np.isfinite([xx,yy])):
        return None
    a=xx-xx.mean()
    b=yy-yy.mean()
    den=math.sqrt(float(a@a)*float(b@b))
    return float(a@b/den) if den>1e-13 else None


def verify_original_region_year(orig,aggregated):
    if len(orig)!=ALL_N*len(YEARS):
        raise ValueError("Original reported 18-region×28-year source panel changed")
    known=set()
    for row in orig:
        key=(row["source_region"],int(row["year"]))
        if key in known:
            raise ValueError("Original source region calendar year duplicated")
        known.add(key)
        calculated=aggregated.get(key)
        if calculated is None:
            raise ValueError("Missing original physical region/year source")
        for left,right,tolerance in (
            ("mean_marine_PC1_fixed_original_global_loadings","site_equal_PC1",1e-10),
            ("mean_source_SIC_pp","site_equal_SIC",1e-10),
            ("mean_GLORYS_salinity","site_equal_salinity",1e-10),
            ("mean_GLORYS_thetao_C","site_equal_thetao",1e-10)
        ):
            if abs(float(row[left])-float(calculated[right]))>tolerance:
                raise ValueError(
                    f"Original 18-region physical source drift {key} {left}: "
                    f"{row[left]} vs {calculated[right]}")
        if int(row["n_source_colonies"])!=calculated["n_colonies"]:
            raise ValueError("Original source colony region/year denominator changed")
        if int(row["n_unique_ocean_GLORYS_cells"])!=calculated["n_wet_cells"]:
            raise ValueError("Original source GLORYS marine-cell region/year denominator changed")
    if len(known)!=ALL_N*len(YEARS):
        raise ValueError("Not all original region-year identities audited")
    return {"n_original_source_region_years_exactly_reproduced":len(known),
            "max_abs_source_site_region_mean_error":1e-10,
            "every_source_SIC_salinity_thetao_PC1_regional_mean_verified":True}


def aggregate_regional(years,physical):
    if len(years)!=588*len(YEARS):
        raise ValueError("Balanced original 588 source colony year panel changed")
    groups=defaultdict(list)
    per_region_sites=defaultdict(set)
    per_region_blocks=defaultdict(set)
    all_cells=defaultdict(set)
    source_site_ids=set()
    for item in years:
        site=item["site_id"];year=int(item["year"])
        key=(site,year)
        if key not in physical:
            raise ValueError("Original source PCA 588 site-year identity mismatch")
        region=item["source_region"]
        phys=physical[key]
        if region!=phys["source_region"]:
            raise ValueError("Original physical source region changed")
        origcell=(int(item["GLORYS_cell_y"]),int(item["GLORYS_cell_x"]))
        if phys["GLORYS_cell"]!=f"{origcell[0]}:{origcell[1]}":
            raise ValueError("Original marine grid IDs changed in physical score reconstruction")
        if year not in YEARS:
            raise ValueError("Original 28-year source date changed")
        groupkey=(region,year)
        groups[groupkey].append({
            "site_id":site,"year":year,"source_region":region,
            "cell":origcell,"block":item["source_250km_block"],
            "PC1":phys["PC1_warm_low_ice_original_score"],
            "PC2":phys["PC2_saline_original_score"],
            "SIC":float(item["mean_source_SIC_pp"]),
            "salinity":float(item["mean_GLORYS_salinity"]),
            "thetao":float(item["mean_GLORYS_thetao_C"]),
        })
        per_region_sites[region].add(site)
        per_region_blocks[region].add(item["source_250km_block"])
        all_cells[origcell].add(region)
        source_site_ids.add(site)
    if len(source_site_ids)!=588 or len(groups)!=ALL_N*len(YEARS):
        raise ValueError("Original 18×28 region cell cohort or 588 sites changed")
    result={}
    for key,rs in sorted(groups.items()):
        cellrows=defaultdict(list)
        for row in rs:
            cellrows[row["cell"]].append(row)
        if len({r["site_id"] for r in rs})!=len(rs):
            raise ValueError("Duplicated source site within one calendar region-year")
        out={
            "source_region":key[0],"year":key[1],
            "n_colonies":len(rs),"n_wet_cells":len(cellrows),
            "n_blocks":len({r["block"] for r in rs}),
            "site_equal_PC1":float(np.mean([z["PC1"] for z in rs])),
            "site_equal_PC2":float(np.mean([z["PC2"] for z in rs])),
            "site_equal_SIC":float(np.mean([z["SIC"] for z in rs])),
            "site_equal_salinity":float(np.mean([z["salinity"] for z in rs])),
            "site_equal_thetao":float(np.mean([z["thetao"] for z in rs])),
            "wet_cell_equal_PC1":float(np.mean([
                np.mean([z["PC1"] for z in cell]) for cell in cellrows.values()])),
            "wet_cell_equal_PC2":float(np.mean([
                np.mean([z["PC2"] for z in cell]) for cell in cellrows.values()])),
            "wet_cell_equal_SIC":float(np.mean([
                np.mean([z["SIC"] for z in cell]) for cell in cellrows.values()])),
            "wet_cell_equal_salinity":float(np.mean([
                np.mean([z["salinity"] for z in cell]) for cell in cellrows.values()])),
            "wet_cell_equal_thetao":float(np.mean([
                np.mean([z["thetao"] for z in cell]) for cell in cellrows.values()])),
            "source_equal_GLORYS_cells_are_still_spatially_and_temporally_dependent":True
        }
        result[key]=out
    region_support={}
    for region,sites in sorted(per_region_sites.items()):
        rows=[r for (reg,y),r in result.items() if reg==region]
        n_blocks=len(per_region_blocks[region])
        n_wet=rows[0]["n_wet_cells"]
        if any(r["n_colonies"]!=len(sites) or r["n_wet_cells"]!=n_wet for r in rows):
            raise ValueError("Original fixed 28-year coastal geographical roster not constant")
        region_support[region]={
            "n_source_colonies":len(sites),
            "n_original_250km_blocks":n_blocks,
            "n_unique_wet_GLORYS_cells":n_wet,
            "geographically_supported_region":len(sites)>=3 and n_blocks>=2 and n_wet>=2,
            "source_years":len(rows)
        }
    if len(region_support)!=ALL_N:
        raise ValueError("Original 18-region physical source labels drift")
    supported=[r for r,z in region_support.items()
               if z["geographically_supported_region"]]
    if len(supported)!=SUPPORTED_N:
        raise ValueError("Original ≥3 colonies/≥2 blocks/≥2 cells region count changed")
    shared_cells={c:sorted(regions) for c,regions in all_cells.items() if len(regions)>1}
    return result, region_support, {
        "n_real_original_sites":len(source_site_ids),
        "n_original_region_source_labels":len(region_support),
        "n_original_source_region_years":len(groups),
        "n_original_unique_wet_ocean_cells":len(all_cells),
        "n_original_wet_ocean_cells_shared_across_reporting_region_labels":len(shared_cells),
        "n_geographically_supported_source_regions":len(supported),
        "source_geographically_supported_regions":sorted(supported),
        "source_wet_cells_shared_between_region_labels_example":[
            {"wet_cell":f"{lat}:{lon}","region_labels":regs}
            for (lat,lon),regs in list(sorted(shared_cells.items()))[:12]
        ]
    }


def matrix_from_regions(aggregate, regions, weighting, axis):
    if weighting not in ("site_equal","wet_cell_equal") or axis not in ("PC1","PC2"):
        raise ValueError("Only frozen original marine axis/weight options are supported")
    mat=np.asarray([[aggregate[region,year][f"{weighting}_{axis}"]
                     for region in regions] for year in YEARS],dtype=float)
    if mat.shape!=(28,len(regions)) or not np.all(np.isfinite(mat)):
        raise ValueError("Original annual physical source region matrix incomplete")
    return mat


def anomaly_standardized(matrix):
    mat=np.asarray(matrix,dtype=float)
    scale=np.std(mat,axis=0)
    if mat.shape[0]!=28 or mat.shape[1]<3 or np.any(scale<1e-10):
        raise ValueError("Original source regional year climate anomalies not identifiable")
    return (mat-np.mean(mat,axis=0))/scale


def synchrony_metrics(Z):
    """Equal-direction year-common variance and general possible signed EOF."""
    Z=np.asarray(Z,dtype=float)
    n_year,n_reg=Z.shape
    if n_year!=28 or n_reg<3:
        raise ValueError("Unexpected 28-year regional physical synchrony panel")
    if np.max(abs(np.mean(Z,axis=0)))>1e-9 or \
       np.max(abs(np.std(Z,axis=0)-1))>1e-9:
        raise ValueError("Not standardised region temporal anomalies")
    common=np.mean(Z,axis=1)
    ss=float(np.sum(Z**2))
    shared_fraction=float(n_reg*np.sum(common**2)/ss)
    U,S,Vh=np.linalg.svd(Z,full_matrices=False)
    frac=float(S[0]**2/np.sum(S**2))
    loadings=Vh[0].copy()
    if loadings.sum()<0:loadings*=-1
    region_corr=np.corrcoef(Z.T)
    ij=np.triu_indices(n_reg,1)
    pairs=region_corr[ij]
    return {
        "n_original_years":n_year,"n_original_region_labels":n_reg,
        "mean_region_temporal_anomaly_common_year_variance_fraction":shared_fraction,
        "first_source_temporal_EOF_explained_fraction":frac,
        "first_temporal_EOF_loadings_by_column":[float(x) for x in loadings],
        "n_regions_temporal_EOF1_positive_loading":sum(loadings>1e-10),
        "n_regions_temporal_EOF1_negative_loading":sum(loadings<-1e-10),
        "n_original_region_pairs":len(pairs),
        "regional_anomaly_correlation_median":float(np.median(pairs)),
        "regional_anomaly_correlation_q25":float(np.quantile(pairs,.25)),
        "regional_anomaly_correlation_q75":float(np.quantile(pairs,.75)),
        "n_positive_region_anomaly_correlations":int(np.sum(pairs>0)),
        "n_negative_region_anomaly_correlations":int(np.sum(pairs<0)),
        "source_region_pairs_share_climate_cells_and_are_NOT_independent_trials":True
    },common


def circular_phase_reference(Z,seed=RNG_SEED,n=PHASE_SHIFTS):
    """Fixed-seed phase-offset envelope, NOT a null-hypothesis p-value."""
    rng=np.random.default_rng(seed)
    times,regions=Z.shape
    observed,_=synchrony_metrics(Z)
    seen=[]
    for i in range(n):
        offsets=rng.integers(0,times,size=regions)
        shifted=np.column_stack([
            np.roll(Z[:,j],int(offsets[j])) for j in range(regions)])
        # Original region temporal shape (and autocorrelation up to cyclic
        # boundary) stays fixed; only between-region calendar alignment removed.
        sh,_=synchrony_metrics(shifted)
        seen.append((sh["mean_region_temporal_anomaly_common_year_variance_fraction"],
                    sh["first_source_temporal_EOF_explained_fraction"]))
    arr=np.asarray(seen)
    return {
        "n_original_calendar_phase_offsets":n,
        "source_phase_offset_seed":seed,
        "independent_circular_region_rolls_hold_within_region_year_order":True,
        "joint_region_alignment_removed_only_in_reference":True,
        "not_pvalues_and_not_a_prospective_causal_significance_test":True,
        "common_year_fraction_reference":{
            "observed":observed["mean_region_temporal_anomaly_common_year_variance_fraction"],
            "offset_median":float(np.median(arr[:,0])),
            "offset_q025":float(np.quantile(arr[:,0],.025)),
            "offset_q975":float(np.quantile(arr[:,0],.975)),
            "fraction_of_offsets_at_least_observed":float(np.mean(
                arr[:,0]>=observed["mean_region_temporal_anomaly_common_year_variance_fraction"]))
        },
        "temporal_EOF1_fraction_reference":{
            "observed":observed["first_source_temporal_EOF_explained_fraction"],
            "offset_median":float(np.median(arr[:,1])),
            "offset_q025":float(np.quantile(arr[:,1],.025)),
            "offset_q975":float(np.quantile(arr[:,1],.975)),
            "fraction_of_offsets_at_least_observed":float(np.mean(
                arr[:,1]>=observed["first_source_temporal_EOF_explained_fraction"]))
        }
    }


def period_regime_support(aggregated,support,weighting,axis):
    results=[]
    for region,geom in sorted(support.items()):
        series=np.asarray([aggregated[region,year][f"{weighting}_{axis}"]
                           for year in YEARS])
        averages=[]
        for a,b in DECADES:
            values=[aggregated[region,y][f"{weighting}_{axis}"]
                    for y in range(a,b+1)]
            if len(values)!=b-a+1:
                raise ValueError("Source original decade calendar incomplete")
            averages.append(float(np.mean(values)))
        first,mid,last=averages
        corr=pearson(
            [aggregated[region,y][f"{weighting}_PC1"] for y in YEARS],
            [aggregated[region,y][f"{weighting}_PC2"] for y in YEARS])
        results.append({
            "source_region":region,"source_original_weighting":weighting,
            "physical_marine_axis":axis,
            "n_original_sites":geom["n_source_colonies"],
            "n_original_polar_blocks":geom["n_original_250km_blocks"],
            "n_original_GLORYS_ocean_cells":geom["n_unique_wet_GLORYS_cells"],
            "geographic_multi_site_multi_block_support":geom["geographically_supported_region"],
            "mean_1993_2000_8yr":first,
            "mean_2001_2010_10yr":mid,
            "mean_2011_2020_10yr":last,
            "original_midperiod_mean_strict_peak":bool(mid>first and mid>last),
            "original_midperiod_mean_strict_trough":bool(mid<first and mid<last),
            "same_region_PC1_PC2_annual_1993_2020_Pearson":corr,
            "source_annually_standardized_temporal_paths_not_migration":True
        })
    return results


def evaluate(args):
    climate=readcsv(args.climate)
    reference=readcsv(args.original_region_year)
    regions=readcsv(args.original_region_trends)
    physical,receipt=reconstruct_source_pcs(climate)
    aggregated,geom,source=aggregate_regional(climate,physical)
    old=verify_original_region_year(reference,aggregated)
    if len(regions)!=ALL_N or {r["source_region"] for r in regions}!=set(geom):
        raise ValueError("Original 18 source region trend table changed")
    for item in regions:
        region=item["source_region"]
        support_original=str(item["source_region_multi_site_multi_block_support"]).lower()=="true"
        if support_original!=geom[region]["geographically_supported_region"]:
            raise ValueError("Geographic source support changed for region "+region)

    results={}
    timepoints=[]; period=[]
    for weighting in ("site_equal","wet_cell_equal"):
        period_audit={}
        for axis in ("PC1","PC2"):
            rr=period_regime_support(aggregated,geom,weighting,axis)
            period+=rr
            period_audit[axis]={r["source_region"]:r for r in rr}
        for cohort,rs in (
            ("all18",sorted(geom)),
            ("geographically_supported13",sorted(
                region for region,info in geom.items()
                if info["geographically_supported_region"]))):
            key=weighting+"__"+cohort
            results[key]={}
            source_matrices={}
            for axis in ("PC1","PC2"):
                observed=matrix_from_regions(aggregated,rs,weighting,axis)
                Z=anomaly_standardized(observed)
                stats,common=synchrony_metrics(Z)
                stats["source_region_order"]=rs
                stats["first_temporal_EOF1_loadings_by_region"]=dict(zip(
                    rs,stats.pop("first_temporal_EOF_loadings_by_column")))
                stats["source_period_peak_regions"]=[
                    r for r in rs if period_audit[axis][r]["original_midperiod_mean_strict_peak"]
                ]
                stats["source_period_trough_regions"]=[
                    r for r in rs if period_audit[axis][r]["original_midperiod_mean_strict_trough"]
                ]
                stats["n_regions_source_midperiod_peak"]=len(stats["source_period_peak_regions"])
                stats["n_regions_source_midperiod_trough"]=len(stats["source_period_trough_regions"])
                stats["fixed_phase_reference_1000"]=circular_phase_reference(Z)
                results[key][axis]=stats
                source_matrices[axis]=common
                for year,value in zip(YEARS,common):
                    timepoints.append({
                        "original_source_weighting":weighting,
                        "source_geographic_region_panel":cohort,
                        "original_source_year":year,
                        "source_marine_axis":axis,
                        "original_common_year_standardized_region_anomaly":float(value),
                        "n_source_regions":len(rs),
                        "not_an_external_climate_forcing_or_p-value":True
                    })
            results[key]["original_PC1_PC2_common_year_anomaly_correlation"]=pearson(
                source_matrices["PC1"],source_matrices["PC2"])
    # Physical peak in old report is exactly 13/18, 10/13 for SITE-equal
    # Antarctic marine PC1, before using unique reanalysis-cell weighting.
    source_site_a=results["site_equal__all18"]["PC1"]
    source_site_s=results["site_equal__geographically_supported13"]["PC1"]
    if (source_site_a["n_regions_source_midperiod_peak"]!=13
            or source_site_s["n_regions_source_midperiod_peak"]!=10):
        raise ValueError("Original 13/18 and 10/13 2000s source region PC1 peak no longer reproduces")

    change=[]
    for r in sorted(geom):
        src=next(x for x in period if x["source_region"]==r
                 and x["source_original_weighting"]=="site_equal"
                 and x["physical_marine_axis"]=="PC1")
        unique=next(x for x in period if x["source_region"]==r
                    and x["source_original_weighting"]=="wet_cell_equal"
                    and x["physical_marine_axis"]=="PC1")
        change.append({
            "source_region":r,
            "n_original_source_colonies":geom[r]["n_source_colonies"],
            "n_unique_original_ocean_cells":geom[r]["n_unique_wet_GLORYS_cells"],
            "geographically_source_supported":geom[r]["geographically_supported_region"],
            "site_equal_original_2000s_PC1_peak":src["original_midperiod_mean_strict_peak"],
            "wet_cell_equal_original_2000s_PC1_peak":unique["original_midperiod_mean_strict_peak"],
            "source_peak_label_changes_under_unique_wet_ocean_cell_weighting":
                src["original_midperiod_mean_strict_peak"]!=unique["original_midperiod_mean_strict_peak"],
        })
    verdict={
        "status":"ORIGINAL_18_REGION_28_YEAR_PHYSICAL_MARINE_TIME_SYNCHRONY_SOURCE_AUDITED",
        "source_original_PC1_PC2_reconstructed":receipt,
        "source_original_18_region_year_physical_values_exactly_reproduced":old,
        "source_unique_grid_cell_and_geographic_cohort":source,
        "fixed_original_source_panels":{
            "years":[YEARS[0],YEARS[-1]],
            "months":[8,9,10,11],
            "source_periods":list(DECADES),
            "n_actual_source_colonies":588,
            "n_actual_source_region_years":18*28,
            "n_actual_source_region_supported":SUPPORTED_N,
            "phase_offset_diagnostics_are_source_descriptive_not_prospective_tests":True
        },
        "source_marine_synchrony_by_weighting_and_geographic_support":results,
        "site_vs_unique_GLORYS_cell_2000s_peak_classification_change":change,
        "n_original_regions_2000s_PC1_midperiod_peak_changes_under_wet_cell_weighting":
            sum(r["source_peak_label_changes_under_unique_wet_ocean_cell_weighting"]
                for r in change),
        "source_wet_cell_duplicate_handling":{
            "one_weight_per_unique_GLORYS_cell_within_source_region_year":True,
            "some_unique_GLORYS_cells_may_be_shared_across_region_labels":True,
            "source_spatial_observation_weighting_is_not_independent_climate_experiment":True
        },
        "limits":[
            "Region/year EOF is a summary of GLORYS model reanalysis plus OSI SAF ice; not independently observed greenhouse attribution or a penguin response mechanism.",
            "Region means and PCA source scores are formed at observed known breeding locations, not area-unbiased continental coastal exposure.",
            "All 18 region labels and 13 supported region labels have some shared ocean forcing and cross-border spatial dependencies.",
            "The 1000 phase-offset references artificially rotate finite 28-year sequences, preserving their cyclic series but not all real-world climate teleconnections or boundary stationarity.",
            "The fraction of phase-offsets exceeding observed is not a formal independent ecological p-value.",
            "EOF1 may encode both in-phase and anti-phase groups, not one shared all-positive trajectory.",
            "Three fixed decade averages have unequal 8/10/10 calendar-year windows and need not follow a monotone trend.",
            "Physical PC1 and salinity-PC2 are orthogonal across all source 16464 siteyears by construction, but their 28-year regional-common temporal modes need not be orthogonal.",
            "Source survey counts, future breeding predictions, species niche, greening and colonization are not outcomes in this purely physical synchrony diagnostic."
        ]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    writecsv(args.out/"original_source_18_region_28year_PC1_PC2_site_vs_unique_cell.csv",
             list(aggregated.values()))
    writecsv(args.out/"original_source_region_year_common_temporal_thermal_salt_modes.csv",
             timepoints)
    writecsv(args.out/"original_source_18_region_2000s_peak_sampling_resolution.csv",
             change)
    writecsv(args.out/"original_region_phase_environment_decade_cohort.csv",
             period)
    (args.out/"original_18region_marine_temporal_synchrony_and_1000_phase_offsets.json").write_text(
        json.dumps(verdict,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("REGIONAL_MARINE_SOURCE_SYNCHRONY_QA="+json.dumps({
        "original":receipt,"old_18region":old,"source":source},ensure_ascii=False),flush=True)
    print("REGIONAL_MARINE_SOURCE_SYNCHRONY="+json.dumps({
        key:{
            axis:{
                "shared_common_year_fraction":x[axis]["mean_region_temporal_anomaly_common_year_variance_fraction"],
                "EOF1_fraction":x[axis]["first_source_temporal_EOF_explained_fraction"],
                "EOF1_positive_regions":x[axis]["n_regions_temporal_EOF1_positive_loading"],
                "EOF1_negative_regions":x[axis]["n_regions_temporal_EOF1_negative_loading"],
                "median_region_pair_r":x[axis]["regional_anomaly_correlation_median"],
                "n_2000s_peak_regions":x[axis]["n_regions_source_midperiod_peak"],
                "phase_reference":x[axis]["fixed_phase_reference_1000"],
            } for axis in ("PC1","PC2")
        } | {"PC1_PC2_year_mode_correlation":
                x["original_PC1_PC2_common_year_anomaly_correlation"]}
        for key,x in results.items()},ensure_ascii=False),flush=True)
    print("REGIONAL_MARINE_SOURCE_PC1_PEAK_WEIGHTING="+json.dumps(change,ensure_ascii=False),flush=True)
    return verdict


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--climate",type=Path,required=True)
    p.add_argument("--original-region-year",type=Path,required=True)
    p.add_argument("--original-region-trends",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    evaluate(p.parse_args())


if __name__=="__main__":
    main()
