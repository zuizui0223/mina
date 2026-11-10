#!/usr/bin/env python3
"""Observed identical-year nest contrast of near co-regional penguin colonies
with independently source-verified original 1991–2020 nearshore SIC records.

This is observational source comparison not climate causal identification.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean

from discover_bright_dark_colonies import readcsv, savecsv, original_source_rows, slope
from audit_common_year_bright_dark import pair_original_years


def distance_km(lat0, lon0, lat1, lon1):
    r=6371.0088
    a0,a1=map(math.radians,(float(lat0),float(lat1)))
    dlat=a1-a0
    dlon=math.radians(float(lon1)-float(lon0))
    h=math.sin(dlat/2)**2 + math.cos(a0)*math.cos(a1)*math.sin(dlon/2)**2
    return 2*r*math.asin(math.sqrt(min(max(h,0.0),1.0)))


def linear_value_slope(values):
    if len(values)<5:
        return None
    x=[float(y) for y,v in values]
    z=[float(v) for y,v in values]
    mx,mz=mean(x),mean(z)
    den=sum((v-mx)**2 for v in x)
    if den<=0:
        return None
    return 10*sum((yr-mx)*(v-mz) for yr,v in zip(x,z))/den


def annual_source_ice(path,summary):
    all_=readcsv(path)
    metadata=json.loads(summary.read_text(encoding="utf-8"))
    if metadata["status"]!="PANANTARCTIC_ORIGINAL_30YR_MONTHLY_SIC_MACRO_SOURCE_COMPLETE":
        raise ValueError("Not original completed 120-source satellite file record")
    if len(all_)!=595*30*4:
        raise ValueError("Original monthly SIC count not 595x30x4")
    months=defaultdict(dict)
    for r in all_:
        site,year,mo=r["site_id"],int(r["year"]),int(r["month"])
        if year<1991 or year>2020 or mo not in (8,9,10,11):
            raise ValueError("Original CDR monthly source identity drift")
        key=(site,year)
        if mo in months[key]:raise ValueError("Duplicate original SIC month")
        ok=r["source_full_595_site_monthly_support"]=="OK"
        v=float(r["source_25km_buffer_mean_SIC_pct"]) if ok else None
        if v is not None and (not math.isfinite(v) or not 0<=v<=100):
            raise ValueError("Invalid original marine source SIC")
        months[key][mo]=v
    if len(months)!=595*30:
        raise ValueError("Incomplete source site-year panel")
    annually={}
    for key,by in months.items():
        if set(by)!={8,9,10,11}:
            raise ValueError("Inconsistent 4-month calendar")
        annually[key]=mean(by.values()) if all(v is not None for v in by.values()) else None
    return annually


def pair_climate(pair,ice,site0,site1):
    if pair["status"]!="EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED":
        raise ValueError("Cannot fit climate on unobserved survey years")
    years=pair["years"]
    values=[]
    for year in years:
        a=ice.get((site0,year))
        b=ice.get((site1,year))
        if a is None or b is None:
            return {
                "status":"SOURCE_MISSING_AUG_NOV_SIC_ON_ONE_OR_MORE_EXACT_SHARED_COUNT_YEARS",
                "n_original_common_census_years":len(years),
                "n_paired_valid_climate_years":sum(
                    ice.get((site0,y)) is not None and ice.get((site1,y)) is not None for y in years)
            }
        values.append((year,a,b))
    delta=[a-b for _,a,b in values]
    slope_a=linear_value_slope([(y,a) for y,a,b in values])
    slope_b=linear_value_slope([(y,b) for y,a,b in values])
    if slope_a is None or slope_b is None:
        raise AssertionError("Original source annual climate linear slope failed on known valid span")
    return {
        "status":"EXACT_ORIGINAL_MATCHED_COUNT_YEAR_LOCAL_MARINE_SIC",
        "n_original_common_census_years":len(years),
        "n_paired_valid_climate_years":len(years),
        "focal_sic_mean_pp_on_exact_count_years":mean(a for _,a,b in values),
        "peer_sic_mean_pp_on_exact_count_years":mean(b for _,a,b in values),
        "mean_signed_site_minus_peer_sic_pp":mean(delta),
        "mean_absolute_site_sic_difference_pp":mean(abs(v) for v in delta),
        "max_absolute_site_sic_difference_pp":max(abs(v) for v in delta),
        "focal_SIC_slope_pp_per_decade_on_exact_count_years":slope_a,
        "peer_SIC_slope_pp_per_decade_on_exact_count_years":slope_b,
        "site_minus_peer_SIC_slope_difference_pp_per_decade":slope_a-slope_b,
        "original_ice_window":"Aug-Nov 100km native valid 25km marine pixel site mean",
        "non_causal_without_foraging_and_iceberg_access":True
    }


def run(args):
    rows=readcsv(args.previous)
    if len(rows)!=100:
        raise ValueError("Original full 100 candidate table lost")
    candidates=readcsv(args.common_year)
    if len(candidates)!=100:
        raise ValueError("Original 100 full common-year audit lost")
    byid={(r["site_id"],r["species"]):r for r in candidates}
    if len(byid)!=100:
        raise ValueError("Original common-year candidate site duplicates")
    geo,counts=original_source_rows(args.census,args.atlas)
    ice=annual_source_ice(args.ice,args.ice_summary)
    groups=defaultdict(list)
    for row in rows:
        if row["source_peer_eligibility"]!="SAME_SPECIES_REGION_PAIRED_REFERENCE_AVAILABLE":
            continue
        if (row["site_id"],row["species"]) not in byid:
            raise ValueError("Mismatched frozen source candidate identities")
        groups[row["species"],row["source_region"],row["polar_250km_block"]].append(row)

    results=[]
    source_groups=[]
    for key,records in sorted(groups.items()):
        species,region,block=key
        group_pairs=0
        for left,right in combinations(sorted(records,key=lambda r:r["site_id"]),2):
            a,b=left["site_id"],right["site_id"]
            leftcounts=dict(counts[a,species]);rightcounts=dict(counts[b,species])
            equal=pair_original_years(leftcounts,rightcounts)
            if equal["status"]!="EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED":
                continue
            left_c=byid[(a,species)];right_c=byid[(b,species)]
            climate=pair_climate(equal,ice,a,b)
            sep=distance_km(left["latitude"],left["longitude"],right["latitude"],right["longitude"])
            rec={
                "species":species,"source_region":region,"polar_250km_fixed_block":block,
                "left_site_id":a,"left_site_name":left["site_name"],
                "right_site_id":b,"right_site_name":right["site_name"],
                "left_site_latitude":float(left["latitude"]),"left_site_longitude":float(left["longitude"]),
                "right_site_latitude":float(right["latitude"]),"right_site_longitude":float(right["longitude"]),
                "observed_site_distance_km":sep,
                "site_separation_le_100km_buffer_radius":sep<=100,
                "n_same_original_count_seasons":len(equal["years"]),
                "first_exact_coobserved_season":equal["first_common_year"],
                "last_exact_coobserved_season":equal["last_common_year"],
                "exact_original_common_count_seasons":";".join(str(y) for y in equal["years"]),
                "left_counting_method":left["observed_original_nest_method"],
                "right_counting_method":right["observed_original_nest_method"],
                "same_source_method":left["observed_original_nest_method"]==right["observed_original_nest_method"],
                "left_nest_log1p_slope_decade_same_years":
                    equal["focal_log1p_nest_slope_per_decade_same_years"],
                "right_nest_log1p_slope_decade_same_years":
                    equal["peer_log1p_nest_slope_per_decade_same_years"],
                "left_minus_right_nest_log1p_slope_difference_decade":
                    equal["paired_relative_log1p_nest_decadal_slope"],
                "left_initial_bright_dark_direction":left_c["original_relative_direction"],
                "right_initial_bright_dark_direction":right_c["original_relative_direction"],
                "left_time_year_and_external_block_supported":
                    left_c.get("outside_spatial_block_replicated_lead","").lower()=="true",
                "right_time_year_and_external_block_supported":
                    right_c.get("outside_spatial_block_replicated_lead","").lower()=="true",
                "left_source_strict_and_same_year_supported":
                    left_c.get("same_year_sign_qualified_candidate","").lower()=="true",
                "right_source_strict_and_same_year_supported":
                    right_c.get("same_year_sign_qualified_candidate","").lower()=="true",
                "original_focal_recorded_zero_seasons":int(left["original_observed_zero_count_years"]),
                "original_peer_recorded_zero_seasons":int(right["original_observed_zero_count_years"]),
                "source_count_years_unobserved_not_imputed":True
            }
            rec.update(climate)
            results.append(rec);group_pairs+=1
        source_groups.append({
            "species":species,"source_region":region,"original_250km_block":block,
            "n_original_source_long_series_sites":len(records),
            "n_original_site_pairs_common_5plus_years_10plus_span":group_pairs,
            "not_independent_pairwise_replicates":True
        })
    strong=[r for r in results if r["left_time_year_and_external_block_supported"]
               and r["right_time_year_and_external_block_supported"] and
               r["left_initial_bright_dark_direction"] != r["right_initial_bright_dark_direction"]]
    named=[r for r in results if r["species"]=="ADPE"
           and {r["left_site_id"],r["right_site_id"]}=={"CRZW","ROYD"}]
    state="IDENTICAL_YEAR_SAME_BLOCK_PAIR_AVAILABLE" if named else "NAMED_PAIR_NOT_SUPPORTED_BY_SOURCE_GEOGRAPHY_AND_YEARS"
    met={
        "status":"ORIGINAL_SAME_BLOCK_COMMON_CENSUS_YEAR_SIC_COMPARABILITY_COMPLETED",
        "source_original":{
            "same_verified_100_long_series":True,"same_fixed_595_site_original_colony_atlas":True,
            "same_original_2456_observed_fixed_method_counts":True,
            "source_original_monthly_SIC_rows":71400,
            "source_ice_1991_to_2020_months":[8,9,10,11],
            "source_ice_only_current_100km_nearshore_not_foraging":True
        },
        "n_same_species_same_source_region_same_250km_block_original_groups":len(groups),
        "n_source_matched_5year_10span_colony_pairs":len(results),
        "n_source_matched_local_100km_or_less_colony_pairs":sum(
            x["site_separation_le_100km_buffer_radius"] for x in results),
        "n_original_ice_full_observation_pair_rows":sum(
            x["status"]=="EXACT_ORIGINAL_MATCHED_COUNT_YEAR_LOCAL_MARINE_SIC" for x in results),
        "n_strict_strong_bright_dark_opposite_direction_pairs_in_same_block":len(strong),
        "named_cape_crozier_west_vs_cape_royds_source_status":state,
        "named_cape_crozier_west_vs_cape_royds_pair":named,
        "all_strong_spatially_local_opposite_lead_pairs":strong,
        "source_group_pair_availability":source_groups,
        "limitations":[
            "Pairwise contrasts share colonies, blocks, environmental data, survey programs; not independent observations.",
            "Nearby original 100km source SIC averages are only partial seasonal environmental exposure, not annual sea-ice front, polynya access, or foraging quality.",
            "No identified climatic mechanism, colony transition, occupancy, true dispersal or conservation refuge.",
            "Census-year matching prevents calendar differences only; systematic observation error and colony footprints remain.",
            "The focal bright/dark identities were selected in prior data exploration; this is postselection diagnostic, not independent replicative causal evidence."
        ]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    savecsv(args.out/"all_same_region_same_250km_block_common_year_colony_pairs.csv",results)
    savecsv(args.out/"source_within_block_pair_availability.csv",source_groups)
    savecsv(args.out/"source_strong_bright_dark_opposite_colony_pairs.csv",strong)
    (args.out/"source_observed_neighbor_colony_ice_receipt.json").write_text(
        json.dumps(met,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("NEIGHBOR_ICE_SUPPORT="+json.dumps({
        key:val for key,val in met.items() if key.startswith("n_") or key.startswith("named_cape")
    },ensure_ascii=False),flush=True)
    print("NEIGHBOR_STRONG_OPPOSITE="+json.dumps(strong,ensure_ascii=False),flush=True)
    return met


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--previous",type=Path,required=True)
    p.add_argument("--common-year",type=Path,required=True)
    p.add_argument("--census",type=Path,required=True)
    p.add_argument("--atlas",type=Path,required=True)
    p.add_argument("--ice",type=Path,required=True)
    p.add_argument("--ice-summary",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    run(p.parse_args())


if __name__=="__main__":
    main()
