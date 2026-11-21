#!/usr/bin/env python3
"""Three frozen-decade climate legacy against actual site-nest changes.

Uses the identical source readings and component arithmetic in the existing
decadal fixed-network code; never creates survey absences or a species niche.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median, mean

from analyze_decadal_fixed_network_reweighting import (
    PERIODS, SPECIES, label, decompose, source_data, write_csv
)


def region_center_corr(records, x, y, min_n=5):
    """Observed-site equal weight; de-mean within source region, exclude singletons."""
    groups = defaultdict(list)
    for r in records:
        groups[r["source_region"]].append(r)
    valid = [item for vals in groups.values() if len(vals) >= 2 for item in vals]
    informative = {r["source_region"] for r in valid}
    xx = []; yy = []
    for region, vals in groups.items():
        if len(vals) < 2: continue
        mx = mean(r[x] for r in vals)
        my = mean(r[y] for r in vals)
        for item in vals:
            xx.append(item[x]-mx)
            yy.append(item[y]-my)
    if len(valid)<min_n or len(informative)<1:
        return {"r":None,"n_sites":len(valid),"n_regions":len(informative),
                "n_blocks":len({r["polar_250km_block"] for r in valid}),
                "reason":"INSUFFICIENT_MULTISITE_REGIONS"}
    vx=sum(v*v for v in xx);vy=sum(v*v for v in yy)
    if vx<1e-12 or vy<1e-12:
        return {"r":None,"n_sites":len(valid),"n_regions":len(informative),
                "n_blocks":len({r["polar_250km_block"] for r in valid}),
                "reason":"ZERO_REGION_RESIDUAL_VARIATION"}
    return {"r":sum(a*b for a,b in zip(xx,yy))/math.sqrt(vx*vy),
            "n_sites":len(valid),"n_regions":len(informative),
            "n_blocks":len({r["polar_250km_block"] for r in valid}),
            "reason":"DESCRIPTIVE_ONLY_NO_INDEPENDENT_LAG_INFERENCE"}


def dropout_range(records, x, y, key):
    units=sorted({r[key] for r in records})
    values=[]
    for omit in units:
        others=[r for r in records if r[key]!=omit]
        d=region_center_corr(others,x,y)
        if d["r"] is not None:
            values.append({"omitted":omit,"r":d["r"],"n_sites":d["n_sites"],"n_regions":d["n_regions"]})
    return {
        "n_original_units":len(units),"n_valid_omissions":len(values),
        "r_min":min((v["r"] for v in values),default=None),
        "r_max":max((v["r"] for v in values),default=None),
        "per_omission":values
    }


def site_roster(sites, observed, sic, species):
    rows=[]
    for site, meta in sorted(sites.items()):
        series=[observed.get((site,species,j),[]) for j in range(3)]
        ice=[sic[site,j] for j in range(3)]
        if any(len(obs)<2 for obs in series) or any(x is None for x in ice):
            continue
        nest=[median(n for _,n in obs) for obs in series]
        sector=int(math.floor(((float(meta["longitude"])+180)%360)/10))
        rows.append({
            "site_id":site,"species":species,"source_region":meta["source_region"],
            "polar_250km_block":meta["polar_250km_fixed_grid_block"],
            "latitude":float(meta["latitude"]),"longitude":float(meta["longitude"]),
            "longitude_sector_10deg":sector,
            **{f"n_census_years_{j}":len(series[j]) for j in range(3)},
            **{f"median_original_census_year_{j}":median(y for y,_ in series[j]) for j in range(3)},
            **{f"median_original_nest_count_{j}":nest[j] for j in range(3)},
            **{f"mean_original_aug_nov_SIC_{j}_pp":ice[j] for j in range(3)},
            "delta_nest_log_recent":math.log1p(nest[2])-math.log1p(nest[1]),
            "delta_nest_log_early":math.log1p(nest[1])-math.log1p(nest[0]),
            "delta_ice_pp_earlier":ice[1]-ice[0],
            "delta_ice_pp_concurrent":ice[2]-ice[1],
            "no_original_unobserved_absences_imputed":True
        })
    return rows


def triple_same_roster_components(rows, first, last):
    transfer=[]
    for r in rows:
        transfer.append({
           "site_id":r["site_id"],"source_region":r["source_region"],
           "polar_250km_block":r["polar_250km_block"],
           "latitude":r["latitude"],
           "n_original_count_years_early":r[f"n_census_years_{first}"],
           "n_original_count_years_late":r[f"n_census_years_{last}"],
           "site_median_observed_nests_early":r[f"median_original_nest_count_{first}"],
           "site_median_observed_nests_late":r[f"median_original_nest_count_{last}"],
           "decadal_original_aug_nov_SIC_early_pp":r[f"mean_original_aug_nov_SIC_{first}_pp"],
           "decadal_original_aug_nov_SIC_late_pp":r[f"mean_original_aug_nov_SIC_{last}_pp"]
        })
    return decompose(transfer,first,last)


def front_join_diagnostic(rows, fronts, species):
    fixed={(r["start_period"],r["end_period"],int(r["longitude_sector_10deg"])):r
           for r in fronts if r["climate_month_basis"]=="aug_nov"
             and r["status"]=="PAIRED_ORIGINAL_MARINE_FRONT"}
    period_pairs=[(0,1),(1,2)]
    info={}
    for a,b in period_pairs:
        key=f"{label(a)}_to_{label(b)}"
        selected=[]
        for r in rows:
            x=fixed.get((label(a),label(b),r["longitude_sector_10deg"]))
            if x is not None:
                selected.append((r,x))
        ice_by_sector={}
        counts_by_sector=defaultdict(list)
        for site,edge in selected:
            sec=site["longitude_sector_10deg"]
            ice_by_sector[sec]=float(edge["southward_positive_ice_edge_meridional_km"])
            counts_by_sector[sec].append(site["site_id"])
        physical_weighted = None
        physical_weight_total = sum(float(site[f"median_original_nest_count_{a}"])
                                    for site,_ in selected)
        if physical_weight_total > 0:
            physical_weighted = sum(
                float(site[f"median_original_nest_count_{a}"]) *
                float(edge["southward_positive_ice_edge_meridional_km"])
                for site,edge in selected) / physical_weight_total
        info[key]={
            "species":species,"paired_sites":len(selected),
            "same_triple_roster_early_nest_weighted_physical_front_shift_km":physical_weighted,
            "paired_sectors":len(ice_by_sector),
            "paired_regions":len({r["source_region"] for r,_ in selected}),
            "sectors":[{"sector":k,"n_sites":len(counts_by_sector[k]),
                       "front_shift_km":v} for k,v in sorted(ice_by_sector.items())],
            "gate":"NO_INDEPENDENT_FRONT_LEAD_LAG_INFERENCE" if len(ice_by_sector)<5
                   else "DESCRIPTIVE_SECTOR_COVERAGE_ONLY",
            "note":"Original marine front displacement, not the biological site-level SIC predictor."
        }
    return info


def analyze(args):
    sites,observed,sic,years,source=source_data(
        args.census,args.atlas,args.ice,args.ice_summary)
    fronts=[]
    if args.front:
        with args.front.open(encoding="utf-8",newline="") as stream:
            fronts=list(csv.DictReader(stream))
    results=[];allrows=[];allframes=[]
    for species in SPECIES:
        roster=site_roster(sites,observed,sic,species)
        allrows.extend(roster)
        computed={}
        for key,x,y in (
           ("earlier_ice_change_vs_recent_nest_change","delta_ice_pp_earlier","delta_nest_log_recent"),
           ("concurrent_ice_change_vs_recent_nest_change","delta_ice_pp_concurrent","delta_nest_log_recent"),
           ("future_ice_negative_time_placebo_vs_earlier_nest_change","delta_ice_pp_concurrent","delta_nest_log_early")
        ):
            score=region_center_corr(roster,x,y)
            score["leave_one_250km_block_out"]=dropout_range(roster,x,y,"polar_250km_block")
            score["leave_one_region_out"]=dropout_range(roster,x,y,"source_region")
            computed[key]=score
        prior=computed["earlier_ice_change_vs_recent_nest_change"]
        same=computed["concurrent_ice_change_vs_recent_nest_change"]
        future=computed["future_ice_negative_time_placebo_vs_earlier_nest_change"]
        baseline={
            "species":species,"strict_triple_census_roster":len(roster),
            "source_regions":len({r["source_region"] for r in roster}),
            "source_250km_blocks":len({r["polar_250km_block"] for r in roster}),
            "marine_10deg_sectors":len({r["longitude_sector_10deg"] for r in roster}),
            "same_site_marine_SIC_decade_0_to_1":None,
            "same_site_marine_SIC_decade_1_to_2":None,
            "model_identifies_species_level_warming_climate_debt":False,
            "model_identifies_true_distribution_advance":False,
        }
        if len(roster)>=3:
            f01=triple_same_roster_components(roster,0,1)
            f12=triple_same_roster_components(roster,1,2)
            f02=triple_same_roster_components(roster,0,2)
            if f01 and f12 and f02:
                baseline["same_roster_components"]={"1990s_to_2000s":f01,
                        "2000s_to_2010s":f12,"1990s_to_2010s":f02}
                summed=f01["southward_positive_latitudinal_reweighting_km"]+f12["southward_positive_latitudinal_reweighting_km"]
                if not math.isclose(summed,f02["southward_positive_latitudinal_reweighting_km"],rel_tol=1e-10,abs_tol=1e-8):
                    raise AssertionError("Identical triple-roster southward trajectory does not telescope")
                baseline["exact_three_decade_centroid_telescope_max_difference_km"]=abs(summed-f02["southward_positive_latitudinal_reweighting_km"])
        if prior["r"] is not None and same["r"] is not None:
            delta=abs(prior["r"])-abs(same["r"])
        else:
            delta=None
        # Post-result timing support audit; survey years are not decade midpoints.
        baseline["original_observation_timing_support"]={
          "actual_original_census_year_median_by_decade":{
              label(j):median(r[f"median_original_census_year_{j}"] for r in roster)
              if roster else None for j in range(3)},
          "site_year_gap_1990s_to_2000s_median":
              median(r["median_original_census_year_1"]-r["median_original_census_year_0"]
                     for r in roster) if roster else None,
          "site_year_gap_2000s_to_2010s_median":
              median(r["median_original_census_year_2"]-r["median_original_census_year_1"]
                     for r in roster) if roster else None,
          "n_sites_year_gap_1990s_to_2000s_under_5":
              sum(r["median_original_census_year_1"]-r["median_original_census_year_0"]<5
                  for r in roster),
          "n_sites_year_gap_2000s_to_2010s_under_5":
              sum(r["median_original_census_year_2"]-r["median_original_census_year_1"]<5
                  for r in roster)}
        baseline["lag_vs_concurrent_abs_region_demeaned_r_advantage"]=delta
        enough=(len(roster)>=10 and prior["n_blocks"]>=5 and
                prior["n_regions"]>=2 and prior["r"] is not None and same["r"] is not None)
        if not enough:
            verdict="SOURCE_SUPPORT_INSUFFICIENT_FOR_REGION_CONDITIONED_TEMPORAL_LEGACY"
        elif delta is not None and delta>0:
            omit=prior["leave_one_region_out"]
            if (omit["r_min"] is not None and omit["r_max"] is not None
                    and omit["r_min"] < 0 < omit["r_max"]):
                verdict="DESCRIPTIVE_EARLIER_SIGNAL_CHANGES_SIGN_AFTER_REGION_OMISSION"
            else:
                verdict="DESCRIPTIVE_EARLIER_CLIMATE_ALIGNMENT_ONLY_NOT_VALIDATED_LAG"
        else:
            verdict="NO_DESCRIPTIVE_EARLIER_CLIMATE_ALIGNMENT_ADVANTAGE"
        baseline["time_lag_gate"]=verdict
        baseline["temporal_association_checks"]=computed
        baseline["original_marine_front_overlap"]=front_join_diagnostic(roster,fronts,species)
        results.append(baseline)
        allframes.append({
            "species":species,"n_strict_triple_sites":len(roster),
            "n_250km_blocks":baseline["source_250km_blocks"],
            "n_regions":baseline["source_regions"],"n_marine_front_sectors":baseline["marine_10deg_sectors"],
            "r_prior_ice_vs_recent_nest":prior["r"],
            "r_concurrent_ice_vs_recent_nest":same["r"],
            "r_negative_time_control_future_ice_vs_past_nest":future["r"],
            "absolute_prior_minus_concurrent_r":delta,
            "lag_claim_gate":verdict
        })
    if len({r["site_id"] for r in allrows})>595:
        raise AssertionError("Original site IDs exceeded input reference")
    output={
      "result_id":"mina-penguin-triple-decade-original-climate-legacy-v1",
      "source":{
         "original_count_roster":{"sites":595,"original_observed_method_consistent_records":2456},
         "original_sea_ice":{"years":[1991,2020],"source_months":120,
                 "site_months":71400,"readout":source["status"]},
         "original_predeclared_periods":[label(k) for k in range(3)],
         "source_250km_block_geo":"EPSG3031 polar fixed blocks",
         "all_three_decades_required":{"actual_years_per_decade":2,
             "same_fixed_sites_across_decades":True,
             "complete_10year_SIC_climate":True},
      },
      "species":results,
      "positive_climate_lag_claim_supported":False,
      "original_marine_front_is_not_coastal_tracking_velocity":True,
      "inference_limits":[
        "Three ten-year bins cannot identify a 5-year recruitment lag or a robust temporal response kernel.",
        "Region-demeaned correlations only describe 1-to-2-decade intervals, not a climatic debt.",
        "Past and concurrent marine SIC changes are correlated and spatially clustered.",
        "Negative-time control checks spatial confounding but is not a randomized test.",
        "Population redistribution of count weights among known colonies is not true distribution edge change.",
        "No species preferred sea ice threshold or local survey detection mechanism was calibrated.",
        "No future breeding forecast, independent temporal transfer or validated causal warming coefficient was fitted."
      ]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    write_csv(args.out/"original_three_decade_census_climate_roster.csv",allrows)
    write_csv(args.out/"original_three_decade_lag_comparison.csv",allframes)
    (args.out/"original_three_decade_climate_legacy_result.json").write_text(
        json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("TRIPLE_DECADE_CLIMATE_LEGACY="+json.dumps(allframes,ensure_ascii=False),flush=True)
    print("TRIPLE_DECADE_SOURCE_PANEL="+json.dumps([
        {"species":r["species"],"n":r["strict_triple_census_roster"],
         "regions":r["source_regions"],
         "blocks":r["source_250km_blocks"],
         "sectors":r["marine_10deg_sectors"],
         "centroid":{k:v["southward_positive_latitudinal_reweighting_km"] for k,v in r.get("same_roster_components",{}).items()},
         "source_support_status":r["time_lag_gate"]}
         for r in results],ensure_ascii=False),flush=True)
    print("TRIPLE_DECADE_LAG_SENSITIVITY="+json.dumps([
        {
            "species":r["species"],
            "original_census_time_support":r["original_observation_timing_support"],
            "r_checks":{k:{"r":v["r"],"informative_sites":v["n_sites"],
                       "source_regions":v["n_regions"],"spatial_blocks":v["n_blocks"],
                       "leave_block_range":[v["leave_one_250km_block_out"]["r_min"],
                                            v["leave_one_250km_block_out"]["r_max"]],
                       "leave_region_range":[v["leave_one_region_out"]["r_min"],
                                             v["leave_one_region_out"]["r_max"]]}
              for k,v in r["temporal_association_checks"].items()},
            "same_3_decade_roster_marine_front":{k:{
                "sites":v["paired_sites"],"sectors":v["paired_sectors"],
                "early_nest_weighted_physical_front_shift_km":
                   v["same_triple_roster_early_nest_weighted_physical_front_shift_km"]}
                for k,v in r["original_marine_front_overlap"].items()},
        } for r in results],ensure_ascii=False),flush=True)
    return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--census",type=Path,required=True)
    p.add_argument("--atlas",type=Path,required=True)
    p.add_argument("--ice",type=Path,required=True)
    p.add_argument("--ice-summary",type=Path,required=True)
    p.add_argument("--front",type=Path)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    analyze(args)


if __name__=="__main__":
    main()
