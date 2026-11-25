#!/usr/bin/env python3
"""V35 observed adjacent-year breeding-nest counts from original ASI programme.

First-party ASI 2013 original N-stage Accuracy<=2 562 rows (562 original
nonduplicate site-taxonomy-season cells), plus V34 strict site→SCAR land
polygon QA. Report source phenology-matched one-year changes, not island
colonization or independent nest survival.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import Counter,defaultdict
from datetime import datetime,date
from pathlib import Path

import numpy as np
from audit_asi_original_census_v33 import (
    download_publisher_csv,parse_original_rows,parse_number
)
from audit_asi_source_landmass_v34 import source_quality_subset

ASI_SOURCE_SHA="e01ee9bfbd8337bcaca7c71aea0b00162f9015cf4954d3ad76eed536cad37634"
SOURCE_LAND_CSV_SHA="279c85ea8976493fe780c4996183f87ac362945933d5cb80d0435a20d3fbcb26"
ORIGINAL_SOURCE_GROUPS=("CW","EI","NE","NW","SH","SO","SW")
MATCH_DAYPART_WINDOW=30


def original_site_land_crosswalk(path:Path):
    blob=path.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=SOURCE_LAND_CSV_SHA:
        raise ValueError("SOURCE_STOP original V34 113-site coastline sample CSV SHA drift")
    with path.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=113:
        raise ValueError("SOURCE_STOP original 113 site crosswalk row count changed")
    result={}
    for r in rows:
        site=str(r["original_Site_ID"])
        if site in result:
            raise ValueError("SOURCE_STOP duplicated original four-character Site_ID")
        result[site]=r
    return result


def austral_season_day(date_string:str,season:int):
    if "xx" in str(date_string).lower() or not date_string:
        return None
    try:
        when=datetime.strptime(date_string,"%m/%d/%Y").date()
    except (TypeError,ValueError):
        return None
    if when.year not in (season,season+1):
        return None
    return (when-date(season,11,1)).days


def source_annual_observed_pairs(quality_rows:list,source_land:dict):
    if len(quality_rows)!=562:
        raise ValueError("SAMPLE_STOP original V33 562 stage-count cohort changed")
    grouped=defaultdict(list)
    for r in quality_rows:
        sid=r["Site_ID"]
        if sid not in source_land:
            raise ValueError("SOURCE_STOP ASI census site absent V34 geography crosswalk")
        group=r["Region"].upper()
        land=source_land[sid]
        if (land["source_original_region"] and
            land["source_original_region"]!=group and
            land["source_geographical_parent_land_status"]=="EXACT_ONE_SOURCE_LAND_POLYGON"):
            raise ValueError("SOURCE_STOP source site region drift between original years and V34")
        grouped[(sid,r["Species"].upper())].append({
            "source_Site_ID":sid,
            "original_taxon":r["Species"].upper(),
            "original_region":group,
            "original_breeding_season":int(r["Season"]),
            "original_counted_occupied_nests":int(round(parse_number(r["Count"]))),
            "original_source_exact_count_accuracy":r["Accuracy"],
            "source_date":r["Date"],
            "source_day_since_Nov_1":austral_season_day(r["Date"],int(r["Season"])),
            "original_source_parent_land_FID":land["source_exact_original_SCAR_land_FID"] or None,
            "source_land_assignment_status":land["source_geographical_parent_land_status"],
        })
    pairs=[]
    gaps=Counter()
    for (site,taxon),rowlist in sorted(grouped.items()):
        data=sorted(rowlist,key=lambda x:x["original_breeding_season"])
        if len({x["original_breeding_season"] for x in data})!=len(data):
            raise ValueError("SOURCE_STOP original ASI site taxon season duplicate after V33 gate")
        for left,right in zip(data[:-1],data[1:]):
            gap=right["original_breeding_season"]-left["original_breeding_season"]
            if gap<1:raise ValueError("SOURCE_STOP original ascending annual census wrong")
            gaps[gap]+=1
            if gap!=1:
                continue
            if left["original_region"]!=right["original_region"]:
                raise ValueError("SOURCE_STOP source survey region differs between within-site years")
            if left["original_source_parent_land_FID"]!=right["original_source_parent_land_FID"]:
                raise ValueError("SOURCE_STOP original land changed within the same Site_ID")
            day1=left["source_day_since_Nov_1"]
            day2=right["source_day_since_Nov_1"]
            daymatch=day1 is not None and day2 is not None and abs(day1-day2)<=MATCH_DAYPART_WINDOW
            n1=left["original_counted_occupied_nests"];n2=right["original_counted_occupied_nests"]
            pairs.append({
                "original_source_Site_ID":site,
                "original_source_species":taxon,
                "original_source_region":left["original_region"],
                "original_first_season":left["original_breeding_season"],
                "original_next_season":right["original_breeding_season"],
                "original_first_stage_N_count":n1,
                "original_next_stage_N_count":n2,
                "original_date_first":left["source_date"],
                "original_date_next":right["source_date"],
                "original_source_phenology_days_apart":abs(day1-day2)
                    if day1 is not None and day2 is not None else None,
                "source_dated_paired_within_30_days_of_same_austral_phase":bool(daymatch),
                "original_exact_SCAR_source_land_FID":left["original_source_parent_land_FID"],
                "original_source_strict_land_status":left["source_land_assignment_status"],
                "original_one_year_log_count_ratio":math.log(n2/n1),
                "source_animal_migration_or_recruitment_observed":False,
                "source_unvisited_years_imputed_as_absence":False,
            })
    return pairs,dict(sorted(gaps.items()))


def qsummary(pairs,key):
    selected=[r["original_one_year_log_count_ratio"] for r in pairs]
    vals=np.asarray(selected,dtype=float)
    return {
        "one_year_observed_source_pairs":len(pairs),
        "original_site_ID_n":len(set(x["original_source_Site_ID"] for x in pairs)),
        "original_source_site_taxon_series_n":len(set(
            (x["original_source_Site_ID"],x["original_source_species"]) for x in pairs)),
        "original_parent_SCAR_land_feature_FID_n":len(set(
            str(x["original_exact_SCAR_source_land_FID"]) for x in pairs
            if x["original_exact_SCAR_source_land_FID"])),
        "median_log_ratio":float(np.median(vals)) if len(vals) else None,
        "p10_log_ratio":float(np.percentile(vals,10)) if len(vals) else None,
        "p90_log_ratio":float(np.percentile(vals,90)) if len(vals) else None,
        "median_observed_count_ratio":float(np.exp(np.median(vals))) if len(vals) else None,
        "source_pairs_with_increase":int(np.sum(vals>0)),
        "source_pairs_with_decrease":int(np.sum(vals<0)),
        "source_pairs_unchanged":int(np.sum(vals==0)),
    }


def summarise(pairs,gaps):
    source=tuple(pairs)
    exact=[x for x in source if x["original_exact_SCAR_source_land_FID"]]
    phe=[x for x in source if x["source_dated_paired_within_30_days_of_same_austral_phase"]]
    both=[x for x in exact if x["source_dated_paired_within_30_days_of_same_austral_phase"]]
    byregion={}
    source_support={}
    for region in ORIGINAL_SOURCE_GROUPS:
        r=[x for x in both if x["original_source_region"]==region]
        byregion[region]=qsummary(r,"region")
        source_support[region]={
          "physical_source_land_feature_count":byregion[region]["original_parent_SCAR_land_feature_FID_n"],
          "source_site_taxon_series_n":byregion[region]["original_source_site_taxon_series_n"],
          "source_one_year_matched_phenology_pairs_n":len(r),
          "meets_frozen_pre_island_fit_source_region_gate":bool(
              byregion[region]["original_parent_SCAR_land_feature_FID_n"]>=3
              and byregion[region]["original_source_site_taxon_series_n"]>=3
              and len(r)>=5),
        }
    bytaxon={taxon:qsummary([x for x in both if x["original_source_species"]==taxon],"taxon")
             for taxon in ("ADPE","CHPE","GEPE","MCPE","BESH","KEGU","SOGP")}
    nregions=sum(z["meets_frozen_pre_island_fit_source_region_gate"]
                 for z in source_support.values())
    return {
        "status":"ASI_ORIGINAL_NEST_ANNUAL_DIRECT_GROWTH_COMPARABILITY_V35",
        "original_frozen_source_2013_asi_stage_N_accuracy_1_2_positive_rows":562,
        "original_observed_sequence_gap_year_distribution":{str(k):v for k,v in gaps.items()},
        "source_direct_adjacent_one_season_pairs_all_geography":qsummary(source,"all"),
        "source_direct_adjacent_pairs_strict_land_only":qsummary(exact,"land"),
        "source_direct_adjacent_pairs_phenology_30_days_only":qsummary(phe,"phase"),
        "source_direct_adjacent_pairs_strict_land_and_phenology_30_days":qsummary(both,"joint"),
        "source_strict_land_phenology_matched_pair_by_original_7_regions":byregion,
        "source_strict_land_phenology_matched_pair_by_original_taxon":bytaxon,
        "source_region_pre_ecological_island_effect_support_gates":source_support,
        "original_source_regions_passing_frozen_3_landmass_5_pair_support":nregions,
        "pre_island_causal_effect_source_gate_passed":nregions>=3,
        "source_original_census_count_N_is_individual_survival_or_emigration":False,
        "time_varying_icefree_colony_reproductive_substrate_measured":False,
        "reported_missing_island_season_is_surveyed_no_breeding":False,
        "source_original_source_stage_N_count_quality_preselected_before_growth_analysis":True,
        "ecological_landmass_or_fast_ice_effect_fitted":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v34-source-sites",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--pairs",type=Path,required=True)
    args=p.parse_args()
    report={"status":"HOLD_ORIGINAL_ASI_ANNUAL_CENSUS_V35",
            "ecological_landmass_or_fast_ice_effect_fitted":False}
    try:
        csv_bytes=download_publisher_csv()
        if hashlib.sha256(csv_bytes).hexdigest()!=ASI_SOURCE_SHA:
            raise ValueError("SOURCE_STOP original 2013 ASI census source changed")
        raw,_=parse_original_rows(csv_bytes)
        quality=source_quality_subset(raw)
        geo=original_site_land_crosswalk(args.v34_source_sites)
        pairs,gaps=source_annual_observed_pairs(quality,geo)
        report=summarise(pairs,gaps)
        args.pairs.parent.mkdir(parents=True,exist_ok=True)
        with args.pairs.open("w",newline="",encoding="utf-8") as f:
            if pairs:
                w=csv.DictWriter(f,fieldnames=list(pairs[0]))
                w.writeheader();w.writerows(pairs)
            else:f.write("")
        report["original_OBIS_status"]="separate original, not used for counts"
        report["original_asi_csv_SHA256"]=ASI_SOURCE_SHA
        report["original_asi_113_site_land_source_CSV_SHA256"]=SOURCE_LAND_CSV_SHA
        report["derived_only_observed_actual_adjacent_ASI_N_census_pairs_CSV_SHA256"]=hashlib.sha256(
            args.pairs.read_bytes()).hexdigest()
    except Exception as e:
        report["error_type"]=type(e).__name__
        report["error"]=str(e)[:1200]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
