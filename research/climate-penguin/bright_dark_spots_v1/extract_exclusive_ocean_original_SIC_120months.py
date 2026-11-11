#!/usr/bin/env python3
"""Actual monthly publisher NetCDF SIC in non-overlapping frozen ocean pixels.

Exploratory Antarctic colony-pair MEASUREMENT diagnostic, not ice mechanism or
penguin niche estimation. Reuses original EUMETSAT 25km pixel memberships,
site-month source values and original monthly publisher SHA manifest.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"macro_panantarctic_v1"))
from extract_original_595_monthly_SIC import source, read_source
from discover_bright_dark_colonies import readcsv, savecsv
from audit_neighbor_colony_vs_local_ice import linear_value_slope
from audit_pair_nesting_ice_buffer_overlap import source_pixel_memberships,overlap

YEARS=range(1991,2021)
MONTHS=(8,9,10,11)
N_PAIRS=147
MIN_PIXELS=3
MIN_VALID_FRACTION=.8
MIN_CLIMATE_YEARS=5
MIN_CLIMATE_YEAR_SPAN=10
LABELS={
    ("ADPE",frozenset(("CRZW","ROYD"))):"Cape Crozier West / Cape Royds (known iceberg benchmark)",
    ("GEPE",frozenset(("BISC","LOCK"))):"Biscoe Point / Port Lockroy",
    ("CHPE",frozenset(("BART","DEMA"))):"Barton Peninsula / Demay Point",
}


def prepare_pairs(pair_csv, members):
    original=readcsv(pair_csv)
    if len(original)!=N_PAIRS:
        raise ValueError("Frozen 147 original coobserved local source pair roster drift")
    out=[];ids=set()
    for idx,r in enumerate(original):
        species=r["species"];a=r["left_site_id"];b=r["right_site_id"]
        if a==b or a not in members or b not in members or species not in ("ADPE","CHPE","GEPE"):
            raise ValueError("Invalid original species or frozen source site pair")
        years=tuple(int(x) for x in r["exact_original_common_count_seasons"].split(";"))
        if len(years)!=int(r["n_same_original_count_seasons"]) or len(set(years))!=len(years):
            raise ValueError("Frozen original paired census-year identity drift")
        if len(years)<5 or max(years)-min(years)<10 or any(y not in YEARS for y in years):
            raise ValueError("No real common census years in frozen local pair")
        L=members[a]-members[b]
        R=members[b]-members[a]
        C=members[a]&members[b]
        geometry=overlap(members[a],members[b])
        out.append({
            "id":idx,"source":r,"species":species,
            "a":a,"b":b,"years":years,
            "fixed_L":np.array(sorted(L),dtype=np.int32),
            "fixed_R":np.array(sorted(R),dtype=np.int32),
            "fixed_C":np.array(sorted(C),dtype=np.int32),
            "geometry":geometry
        })
        ids.add(a);ids.add(b)
    return out,sorted(ids)


def subset_source_mean(sic,valid,subset):
    n=len(subset)
    if n < MIN_PIXELS:
        return None
    mask=valid[subset]
    n_valid=int(np.count_nonzero(mask))
    if n_valid<MIN_PIXELS or n_valid/n < MIN_VALID_FRACTION:
        return None
    value=float(np.mean(sic[subset[mask]]))
    if not 0<=value<=100:
        raise ValueError("Source exclusive ocean SIC outside physical 0–100%")
    return value


def annual_four_month_means(entries,year):
    series=[]
    for month in MONTHS:
        row=entries.get((year,month))
        if row is None or row["l"] is None or row["r"] is None:
            return None
        series.append(row)
    return {
        "left":mean(row["l"] for row in series),
        "right":mean(row["r"] for row in series),
        "shared":mean(row["s"] for row in series) if all(row["s"] is not None for row in series) else None,
    }


def original_site_month_index(path,sites):
    allrows=readcsv(path)
    if len(allrows)!=595*30*4:
        raise ValueError("Original 71,400 monthly source record table drift")
    by={};selected=set(sites)
    for r in allrows:
        site=r["site_id"];year=int(r["year"]);month=int(r["month"])
        if site not in selected:continue
        key=(site,year,month)
        if key in by:raise ValueError("Repeated original source site-month")
        by[key]=r
    if len(by)!=len(sites)*30*4:
        raise ValueError("Source monthly records missing for selected frozen site IDs")
    return by


def qa_original_site_month(site,year,month,reference,native_ix,sic,valid):
    """Every original recorded site/month must equal source SIC in same cells."""
    r=reference[site,year,month]
    mask=valid[native_ix]
    yes=int(np.count_nonzero(mask))
    frozen_count=len(native_ix)
    ready=frozen_count>=MIN_PIXELS and yes>=MIN_PIXELS and yes/frozen_count>=MIN_VALID_FRACTION
    old=r["source_full_595_site_monthly_support"]=="OK"
    if ready!=old:
        raise ValueError(f"Official original 100km site monthly SIC QA status changed: {site} {year}-{month}")
    if int(r["original_reference_ocean_pixels_within_100km"])!=frozen_count:
        raise ValueError("Official original fixed ocean pixel denominator changed")
    if int(r["original_valid_same_pixels_this_month"])!=yes:
        raise ValueError("Official original monthly valid pixel count changed")
    if not old:
        return False,None
    found=float(np.mean(sic[native_ix[mask]]))
    prior=float(r["source_25km_buffer_mean_SIC_pct"])
    if abs(found-prior)>1e-8:
        raise ValueError(f"Original fixed-source full buffer mean drift {site} {year}-{month} "
                         f"{found:.11f} != {prior:.11f}")
    return True,found


def aggregate_on_original_years(pair,monthly,reference):
    orig=pair["source"]
    a,b=pair["a"],pair["b"]
    supported=[]
    detail=[]
    for year in pair["years"]:
        annual=annual_four_month_means(monthly[ pair["id"] ],year)
        site_ref=[]
        for site in (a,b):
            v=[reference[site,year,m] for m in MONTHS]
            if all(row["source_full_595_site_monthly_support"]=="OK" for row in v):
                site_ref.append(mean(float(row["source_25km_buffer_mean_SIC_pct"]) for row in v))
            else:
                site_ref.append(None)
        if None in site_ref:
            raise ValueError("Previously supported original local pair source SIC not valid")
        vals={
            "species":pair["species"],"left":a,"right":b,"year":year,
            "original_full_left_pp":site_ref[0],"original_full_right_pp":site_ref[1],
            "original_full_signed_diff_pp":site_ref[0]-site_ref[1],
            "source_exclusive_pair_year_supported":annual is not None
        }
        if annual is not None:
            vals.update({"exclusive_left_SIC_pp":annual["left"],
                         "exclusive_right_SIC_pp":annual["right"],
                         "exclusive_shared_pixels_SIC_pp":annual["shared"],
                         "original_exclusive_signed_diff_pp":annual["left"]-annual["right"]})
            supported.append((year,annual["left"],annual["right"],site_ref[0],site_ref[1]))
        detail.append(vals)

    original_all=mean(abs(row["original_full_signed_diff_pp"]) for row in detail)
    if abs(original_all-float(orig["mean_absolute_site_sic_difference_pp"]))>1e-8:
        raise ValueError("Prior original 147-pair mean absolute full 100km SIC did not reproduce")
    original_slopes=(
        linear_value_slope([(r["year"],r["original_full_left_pp"]) for r in detail]),
        linear_value_slope([(r["year"],r["original_full_right_pp"]) for r in detail]))
    if abs(original_slopes[0]-original_slopes[1]-
           float(orig["site_minus_peer_SIC_slope_difference_pp_per_decade"]))>1e-8:
        raise ValueError("Prior original 147-pair full-site SIC source slope did not reproduce")

    r={
        "species":pair["species"],
        "source_region":orig["source_region"],
        "original_polar_250km_block":orig["polar_250km_fixed_block"],
        "left_site_id":a,"left_site_name":orig["left_site_name"],
        "right_site_id":b,"right_site_name":orig["right_site_name"],
        "real_common_count_census_years":len(pair["years"]),
        "first_original_common_census_year":min(pair["years"]),
        "last_original_common_census_year":max(pair["years"]),
        "n_valid_same_census_year_exclusive_SIC":len(supported),
        "n_exclusive_years_dropped_due_to_source_QA":len(pair["years"])-len(supported),
        "source_exclusive_left_frozen_marine_pixels":len(pair["fixed_L"]),
        "source_exclusive_right_frozen_marine_pixels":len(pair["fixed_R"]),
        "source_shared_frozen_marine_pixels":len(pair["fixed_C"]),
        "source_native_ocean_cell_Jaccard":pair["geometry"]["native_ocean_pixel_jaccard"],
        "original_count_slope_log1p_diff_decadal":
            float(orig["left_minus_right_nest_log1p_slope_difference_decade"]),
        "original_site_distance_km":float(orig["observed_site_distance_km"]),
        "original_source_count_method_same":str(orig["same_source_method"]).lower()=="true",
        "original_zero_in_any_full_count_series":(
            int(orig["original_focal_recorded_zero_seasons"])>0
            or int(orig["original_peer_recorded_zero_seasons"])>0),
        "original_full_buffer_mean_abs_SIC_difference_all_common_years_pp":original_all,
    }
    if len(pair["fixed_L"])<MIN_PIXELS or len(pair["fixed_R"])<MIN_PIXELS:
        r["exclusive_source_support"]="SOURCE_EXCLUSIVE_GRID_SUPPORT_INSUFFICIENT"
        return r,detail
    if (len(supported)<MIN_CLIMATE_YEARS
        or supported[-1][0]-supported[0][0]<MIN_CLIMATE_YEAR_SPAN):
        r["exclusive_source_support"]="INSUFFICIENT_VALID_EXCLUSIVE_CLIMATE_YEARS"
        return r,detail
    def ice_slope(idx):
        return linear_value_slope([(row[0],row[idx]) for row in supported])
    r.update({
        "exclusive_source_support":"SOURCE_FULL_120MONTH_EXCLUSIVE_MARINE_COMPARISON",
        "exclusive_source_year_first":supported[0][0],
        "exclusive_source_year_last":supported[-1][0],
        "original_full_buffer_abs_SIC_diff_on_exclusive_years_pp":mean(
            abs(z[3]-z[4]) for z in supported),
        "exclusive_nonoverlapping_SIC_abs_diff_on_same_years_pp":mean(
            abs(z[1]-z[2]) for z in supported),
        "exclusive_nonoverlapping_SIC_mean_signed_diff_pp":mean(
            z[1]-z[2] for z in supported),
        "original_full_buffer_left_SIC_slope_restricted_pp_decade":ice_slope(3),
        "original_full_buffer_right_SIC_slope_restricted_pp_decade":ice_slope(4),
        "exclusive_left_SIC_slope_pp_decade":ice_slope(1),
        "exclusive_right_SIC_slope_pp_decade":ice_slope(2),
    })
    r["exclusive_minus_original_full_mean_abs_difference_pp"]=(
        r["exclusive_nonoverlapping_SIC_abs_diff_on_same_years_pp"]-
        r["original_full_buffer_abs_SIC_diff_on_exclusive_years_pp"])
    if r["original_full_buffer_abs_SIC_diff_on_exclusive_years_pp"]>1e-9:
        r["exclusive_divided_by_full_buffer_abs_difference_ratio"]=(
            r["exclusive_nonoverlapping_SIC_abs_diff_on_same_years_pp"]/
            r["original_full_buffer_abs_SIC_diff_on_exclusive_years_pp"])
    r["exclusive_site_SIC_trend_difference_pp_decade"]=(
        r["exclusive_left_SIC_slope_pp_decade"]-
        r["exclusive_right_SIC_slope_pp_decade"])
    r["original_full_site_SIC_trend_difference_same_years_pp_decade"]=(
        r["original_full_buffer_left_SIC_slope_restricted_pp_decade"]-
        r["original_full_buffer_right_SIC_slope_restricted_pp_decade"])
    return r,detail


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pairs",type=Path,required=True)
    parser.add_argument("--original-595-pixel-membership",type=Path,required=True)
    parser.add_argument("--original-595-site-month",type=Path,required=True)
    parser.add_argument("--original-month-SHA-receipts",type=Path,required=True)
    parser.add_argument("--original-ice-metadata",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()

    members=source_pixel_memberships(args.original_595_pixel_membership)
    pairs,used_sites=prepare_pairs(args.pairs,members)
    old=original_site_month_index(args.original_595_site_month,used_sites)
    receipts=json.loads(args.original_month_SHA_receipts.read_text(encoding="utf-8"))
    metadata=json.loads(args.original_ice_metadata.read_text(encoding="utf-8"))
    if len(receipts)!=120 or metadata["status"]!="PANANTARCTIC_ORIGINAL_30YR_MONTHLY_SIC_MACRO_SOURCE_COMPLETE":
        raise ValueError("Source original 120 monthly CDR receipts unavailable or incomplete")
    manifest={(int(r["year"]),int(r["month"])):r["sha256"] for r in receipts}
    if len(manifest)!=120 or metadata["n_original_source_netCDF_files"]!=120:
        raise ValueError("Original 120 month SHA receipt identity drift")
    if any((y,m) not in manifest for y in YEARS for m in MONTHS):
        raise ValueError("Incomplete 1991–2020 August–November official SHA time coverage")
    geo=metadata["original_native_grid_geo_sha256"]

    full_ids={site:np.asarray(sorted(members[site]),dtype=np.int32) for site in used_sites}
    monthly=defaultdict(dict)
    n_verified_site_months=0;n_original_full_supported=0
    output_receipts=[]
    total=120
    for k,(year,month) in enumerate((y,m) for y in YEARS for m in MONTHS):
        original=source(year,month)
        if original["sha256"]!=manifest[year,month]:
            raise ValueError(f"Original official publisher NetCDF SHA drift {year}-{month:02d}")
        lat,lon,sic,valid,fingerprint=read_source(original)
        if fingerprint!=geo:
            raise ValueError(f"Original source 25km native marine grid coordinate identity drift {year}-{month:02d}")
        for site in used_sites:
            supported,val=qa_original_site_month(
                site,year,month,old,full_ids[site],sic,valid)
            n_verified_site_months+=1
            n_original_full_supported+=int(supported)
        for pair in pairs:
            if len(pair["fixed_L"])<MIN_PIXELS or len(pair["fixed_R"])<MIN_PIXELS:
                continue
            monthly[pair["id"]][year,month]={
                "l":subset_source_mean(sic,valid,pair["fixed_L"]),
                "r":subset_source_mean(sic,valid,pair["fixed_R"]),
                "s":subset_source_mean(sic,valid,pair["fixed_C"]),
            }
        output_receipts.append({
            "year":year,"month":month,
            "official_publisher_original_URL":original["publisher_url"],
            "original_netCDF_sha256":original["sha256"],
            "original_native_grid_geolocation_sha256":fingerprint,
            "all_used_original_100km_colony_months_recomputed":len(used_sites),
        })
        if (k+1)%10==0 or k==0 or k+1==120:
            print(f"EXCLUSIVE_SOURCE_MONTH={k+1}/{total} original={year}-{month:02d} "
                  f"sha={original['sha256']} unique_source_sites={len(used_sites)}",flush=True)
        Path(original["path"]).unlink(missing_ok=True)
    if n_verified_site_months!=120*len(used_sites):
        raise AssertionError("Source-independent original site monthly cross-validation incomplete")
    rows=[];details=[]
    for pair in pairs:
        row,evidence=aggregate_on_original_years(pair,monthly,old)
        rows.append(row);details+=evidence
    supported=[r for r in rows if r["exclusive_source_support"]=="SOURCE_FULL_120MONTH_EXCLUSIVE_MARINE_COMPARISON"]
    groups=defaultdict(list)
    for row in rows:
        groups[row["species"],row["source_region"],row["original_polar_250km_block"]].append(row)
    strata=[]
    for (species,region,block),part in sorted(groups.items()):
        eligible=[r for r in part if r in supported]
        strata.append({
            "species":species,"source_region":region,"polar_250km_block":block,
            "original_local_pairs":len(part),"exclusive_ice_supported_pairs":len(eligible),
            "n_unique_original_colony_ids":len({site for r in part
                for site in (r["left_site_id"],r["right_site_id"])}),
            "median_original_full_100km_diff_pp_on_comparable_years":median(
                r["original_full_buffer_abs_SIC_diff_on_exclusive_years_pp"]
                for r in eligible) if eligible else None,
            "median_exclusive_25km_source_ocean_cell_diff_pp":median(
                r["exclusive_nonoverlapping_SIC_abs_diff_on_same_years_pp"]
                for r in eligible) if eligible else None,
            "n_pairs_exclusive_difference_gt_original_full":
                sum(r["exclusive_minus_original_full_mean_abs_difference_pp"]>1e-10 for r in eligible),
            "not_independent_pairwise_statistical_samples":True
        })
    named={}
    for (sp,sites),label in LABELS.items():
        matches=[r for r in rows if r["species"]==sp
                 and frozenset((r["left_site_id"],r["right_site_id"]))==sites]
        if len(matches)!=1:
            raise ValueError(f"Original named pair missing {label}")
        named[label]=matches[0]

    summary={
        "status":"ORIGINAL_120_MONTH_NONOVERLAPPING_ICE_CELLS_ALL_147_PENGUIN_PAIRS_AUDITED",
        "source":{
            "producer":"EUMETSAT OSI SAF OSI-450-a1 v3.1 25km EASE2",
            "citation_DOI":"10.15770/EUM_SAF_OSI_0023",
            "SHA256_verified_original_monthly_NetCDF_files":len(output_receipts),
            "geolocation_fingerprint_verified":True,
            "original_source_full_100km_site_month_means_independently_recomputed":
                n_verified_site_months,
            "original_source_full_100km_site_months_supported":
                n_original_full_supported,
            "n_unique_original_paired_sites":len(used_sites),
            "source_original_fixed_site_atlas_size":len(members),
            "all_147_prior_mean_full_site_sic_differences_reproduced":True,
            "all_147_prior_full_site_sic_trend_differences_reproduced":True,
        },
        "pair_support":{
            "original_147_same_year_matched_pairs":len(rows),
            "n_source_exclusive_SIC_supported_pairs":len(supported),
            "n_source_exclusive_grid_too_few_pixels":sum(
                r["exclusive_source_support"]=="SOURCE_EXCLUSIVE_GRID_SUPPORT_INSUFFICIENT"
                for r in rows),
            "n_source_exclusive_valid_years_insufficient":sum(
                r["exclusive_source_support"]=="INSUFFICIENT_VALID_EXCLUSIVE_CLIMATE_YEARS"
                for r in rows),
            "n_unique_species_region_250km_blocks":len(strata),
            "n_supported_pairs_exclusive_larger_ice_difference":sum(
                r["exclusive_minus_original_full_mean_abs_difference_pp"]>1e-10
                for r in supported),
            "n_supported_pairs_exclusive_smaller_ice_difference":sum(
                r["exclusive_minus_original_full_mean_abs_difference_pp"]<-1e-10
                for r in supported),
            "median_exclusive_pp_diff":median(
                r["exclusive_nonoverlapping_SIC_abs_diff_on_same_years_pp"]
                for r in supported) if supported else None,
            "median_original_full_pp_diff_on_same_years":median(
                r["original_full_buffer_abs_SIC_diff_on_exclusive_years_pp"]
                for r in supported) if supported else None,
            "median_per_pair_ratio_exclusive_to_full":median(
                r["exclusive_divided_by_full_buffer_abs_difference_ratio"]
                for r in supported
                if r.get("exclusive_divided_by_full_buffer_abs_difference_ratio") is not None)
                if supported else None
        },
        "named_source_pairs_all_reported":named,
        "species_region_block_source_support":strata,
        "inference_limits":[
            "Overlapping original 100km site marine buffers can mathematically reduce source SIC differences.",
            "Nonoverlapping 25km ocean grid cell sets do not imply independent satellite footprints or penguin foraging habitat.",
            "Reported source-exclusive SIC is an Aug–Nov environmental context, not a colony iceberg-accessibility or prey variable.",
            "Any difference between exclusive and whole buffer averages does not causally explain colony nest-count change.",
            "Source-biased selection of long-monitored sites and overlapping colony pairs prevents species-wide p-values.",
            "One original pixel may itself be a spatially filtered satellite product; grid resolution not true physical resolution.",
            "Unobserved colony count remains missing; no true occupancy, colonization, emigrants or climate debt inferred.",
        ]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    savecsv(args.out/"all_147_original_pair_exclusive_vs_full_ice_1991_2020.csv",rows)
    savecsv(args.out/"all_original_pair_actual_census_year_exclusive_marine_SIC.csv",details)
    savecsv(args.out/"source_species_region_250km_block_exclusive_support.csv",strata)
    (args.out/"official_120_original_netCDF_SHA256_source_receipts.json").write_text(
        json.dumps(output_receipts,indent=2)+"\n",encoding="utf-8")
    (args.out/"exclusive_original_ocean_pixels_147_pairs_result.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("EXCLUSIVE_ORIGINAL_120_MONTH_SUPPORT="+json.dumps({
        **summary["source"],**summary["pair_support"]},ensure_ascii=False),flush=True)
    print("EXCLUSIVE_ORIGINAL_LOCAL_NAMED_PAIRS="+json.dumps(named,ensure_ascii=False),flush=True)
    print("EXCLUSIVE_ORIGINAL_10_SOURCE_BLOCKS="+json.dumps(strata,ensure_ascii=False),flush=True)
    return summary


if __name__=="__main__":
    main()
