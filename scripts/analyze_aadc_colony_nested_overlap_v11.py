#!/usr/bin/env python3
"""Derive area-conditional mapped-colony geometric reassembly, AADC V11.

The original colony polygon outcomes in V10 were previously viewed; this
is POST-RESULT DESCRIPTION, not a new causal or independent confirmation.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics


def load_original_pairs(path,receipt):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=receipt["derived_site_pair_metrics_CSV_SHA256"]:
        raise ValueError("SOURCE_STOP original AADC V10 pair CSV checksum differs from frozen result")
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if len(rows)!=15 or len({r["original_site_id"] for r in rows})!=13:
        raise ValueError("SAMPLE_STOP original V10 15 pair, 13 site frozen observation grain changed")
    if {r["original_source_group"] for r in rows}!={"HBE","HBW"}:
        raise ValueError("SAMPLE_STOP original V10 source groups changed")
    if len({(r["original_site_id"],r["earlier_season_start_year"],r["later_season_start_year"]) for r in rows})!=15:
        raise ValueError("SOURCE_STOP duplicated original site observation pair")
    if receipt["status"]!="AADC_REPEATED_ADELIE_ORIGINAL_COLONY_GIS_V10_EXPLORATORY":
        raise ValueError("SOURCE_STOP original AADC source receipt is not successful V10")
    return rows


def derive_area_conditional_overlap(rows):
    calculated=[]
    for row in rows:
        try:
            a=float(row["earlier_mapped_colony_area_m2"])
            b=float(row["later_mapped_colony_area_m2"])
            intersection=float(row["mapped_polygon_intersection_area_m2"])
            reported_j=float(row["mapped_overlap_jaccard"])
        except (TypeError,ValueError,KeyError) as e:
            raise ValueError("SOURCE_STOP original mapped polygon numeric input invalid") from e
        if not all(map(math.isfinite,(a,b,intersection,reported_j))):
            raise ValueError("SOURCE_STOP nonfinite polygon source geometry")
        if min(a,b)<=0 or intersection<0 or intersection>min(a,b)+1e-5:
            raise ValueError("GEOMETRY_STOP contradictory positive source polygon areas")
        union=a+b-intersection
        if union<=0 or abs(intersection/union-reported_j)>1e-6:
            raise ValueError("GEOMETRY_STOP actual V10 original mapped Jaccard inconsistent")
        jmax=min(a,b)/max(a,b)
        inclusion=min(1.,max(0.,intersection/min(a,b)))
        record={
            "original_site_id":row["original_site_id"],
            "original_source_group":row["original_source_group"],
            "earlier_season_start_year":int(row["earlier_season_start_year"]),
            "later_season_start_year":int(row["later_season_start_year"]),
            "observed_mapped_area_ratio":b/a,
            "mapped_jaccard":reported_j,
            "maximum_possible_jaccard_conditional_on_area":jmax,
            "smaller_year_footprint_fully_contained_fraction":inclusion,
            "residual_mapped_spatial_mismatch_beyond_area_ratio":1-inclusion,
            "jaccard_fraction_of_area_constrained_maximum":reported_j/jmax,
            "permutation_test_performed":False,
            "field_site_fidelity_demonstrated":False,
        }
        calculated.append(record)
    return calculated


def quantiles(xs):
    vals=sorted(float(x) for x in xs)
    if not vals:
        return {"n":0,"median":None,"p10":None,"p90":None}
    def q(p):
        k=(len(vals)-1)*p
        a=math.floor(k)
        b=math.ceil(k)
        return float(vals[a]+(vals[b]-vals[a])*(k-a))
    return {"n":len(vals),"median":q(.5),"p10":q(.1),"p90":q(.9)}


def report_summary(rows):
    if not rows:raise ValueError("SAMPLE_STOP no site-pair geometry")
    sites=defaultdict(list)
    for r in rows:sites[r["original_site_id"]].append(r)
    def case_report(records):
        return {
          "original_observation_pairs":len(records),
          "mapped_area_ratio":quantiles(r["observed_mapped_area_ratio"] for r in records),
          "mapped_jaccard":quantiles(r["mapped_jaccard"] for r in records),
          "area_maximum_jaccard":quantiles(
            r["maximum_possible_jaccard_conditional_on_area"] for r in records),
          "smaller_footprint_inclusion":quantiles(
            r["smaller_year_footprint_fully_contained_fraction"] for r in records),
          "residual_geometric_mismatch":quantiles(
            r["residual_mapped_spatial_mismatch_beyond_area_ratio"] for r in records),
          "area_decreased_pairs":sum(r["observed_mapped_area_ratio"]<1-1e-8 for r in records),
          "area_increased_pairs":sum(r["observed_mapped_area_ratio"]>1+1e-8 for r in records),
          "area_unchanged_pairs":sum(abs(r["observed_mapped_area_ratio"]-1)<=1e-8 for r in records),
        }
    site_entries=[]
    for site,rs in sorted(sites.items()):
        site_entries.append({
            "original_site_id":site,
            "source_group":rs[0]["original_source_group"],
            "observed_map_pair_count":len(rs),
            "mean_smaller_footprint_inclusion":statistics.mean(
                r["smaller_year_footprint_fully_contained_fraction"] for r in rs),
            "mean_residual_mapped_spatial_mismatch":statistics.mean(
                r["residual_mapped_spatial_mismatch_beyond_area_ratio"] for r in rs),
            "mean_mapped_colony_Jaccard":statistics.mean(
                r["mapped_jaccard"] for r in rs)
        })
    groups=sorted(set(r["original_source_group"] for r in rows))
    return {
      "status":"AADC_NESTED_MAPPED_COLONY_CONTRACTION_DESCRIPTIVE_V11_POST_RESULT",
      "original_site_IDs":len(site_entries),
      "original_site_year_observation_pairs":len(rows),
      "original_source_groups":groups,
      "all_site_pair_descriptions":case_report(rows),
      "by_original_source_group":{
        g:case_report([r for r in rows if r["original_source_group"]==g])
        for g in groups
      },
      "by_unique_original_site_ID_equal_weight":{
        "n":len(site_entries),
        "site_mean_smaller_footprint_inclusion":quantiles(
           r["mean_smaller_footprint_inclusion"] for r in site_entries),
        "site_mean_residual_geometric_mismatch":quantiles(
           r["mean_residual_mapped_spatial_mismatch"] for r in site_entries),
        "site_mean_mapped_colony_Jaccard":quantiles(
           r["mean_mapped_colony_Jaccard"] for r in site_entries),
        "unique_site_group_counts":{
           g:sum(r["source_group"]==g for r in site_entries)
           for g in groups
        },
      },
      "actual_nest_survival_or_social_site_fidelity_measured":False,
      "source_polygon_intersection_identifies_real_colonisation":False,
      "source_region_groups_are_independent_island_clusters":False,
      "original_coverage_and_delineation_precision_adjusted":False,
      "post_V10_discovery_not_pre_outcome_confirmatory":True,
      "ecological_model_or_permutation_significance_tested":False,
    },site_entries


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--receipt",type=Path,required=True)
    ap.add_argument("--source-pairs",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--pairs",type=Path,required=True)
    ap.add_argument("--sites",type=Path,required=True)
    args=ap.parse_args()
    original=json.loads(args.receipt.read_text(encoding="utf-8"))
    source=load_original_pairs(args.source_pairs,original)
    pairs=derive_area_conditional_overlap(source)
    summary,site=report_summary(pairs)
    import csv
    for output,data in ((args.pairs,pairs),(args.sites,site)):
        output.parent.mkdir(parents=True,exist_ok=True)
        with output.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]))
            writer.writeheader();writer.writerows(data)
    summary["original_source_pair_CSV_SHA256"]=hashlib.sha256(
        args.source_pairs.read_bytes()).hexdigest()
    summary["derived_sitepair_fraction_CSV_SHA256"]=hashlib.sha256(
        args.pairs.read_bytes()).hexdigest()
    summary["derived_siteID_equal_weight_CSV_SHA256"]=hashlib.sha256(
        args.sites.read_bytes()).hexdigest()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))


if __name__=="__main__":
    main()
