#!/usr/bin/env python3
"""Six-year Ledda sea-ice presence and original penguin detection comparison.

Post-source-exposure descriptive synthesis ONLY, not a new confirmatory test.
Requires direct physical cell records from source-verified GitHub workflows.
Never use a positive class-4 pixel as proof of a safe breeding site or an
original satellite 'yes' as verified successful breeding.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

YEARS=(2009,2010,2011,2012,2013,2014)
BIOLOGICAL_SOURCE={
    2009:("no","ice_absent","2009-10-27"),
    2010:("yes","unknown","2010-10-08"),
    2011:("no","author_ice_present","2011-09-23"),
    2012:("no","ice_absent","2012-10-22"),
    2013:("yes","unknown","2013-11-30"),
    2014:("no","author_ice_present","2014-10-13")
}
CENTERS=("LaRue_original","Fretwell_alternative")
RADIUS="3"


def _finite_fraction(n, d):
    if not isinstance(n, int) or not isinstance(d, int) or d<=0 or not (0<=n<=d):
        raise ValueError("Invalid physical class4 class count")
    return n/d


def from_historical(item):
    if item["status"]!="EXPLORATORY_HISTORIC_INDEPENDENT_PHYSICAL_GRID_READ":
        raise ValueError("Historical source HOLD")
    year=item["year"]
    if year not in (2009,2010,2012,2013):
        raise ValueError("Historical year outside frozen subset")
    if item["source_image"]["image_date"]!=BIOLOGICAL_SOURCE[year][2]:
        raise ValueError("Historical image date changed")
    out={}
    for center in CENTERS:
        physical=item["preimage_physical_by_site_and_radius"][center][RADIUS]
        last=physical["last_fully_preimage"]
        frac=_finite_fraction(last["class4_pixels"],last["valid_pixels"])
        out[center]={
            "last_preimage_class4_pixels":last["class4_pixels"],
            "last_preimage_grid_cells":last["valid_pixels"],
            "last_preimage_fraction":frac,
            "n_preimage_intervals":physical["n_preimage_15day_composites"],
            "intervals_any_class4":physical["n_composites_with_any_class4"],
            "longest_contiguous_intervals_any_class4":physical["longest_consecutive_composites_any_class4"],
            "trailing_no_class4_intervals":physical["trailing_composites_no_class4"],
            "last_preimage_interval_start":last["composite_start_yyyymmdd"],
            "last_preimage_interval_end":last["composite_end_yyyymmdd"]
        }
    return {"year":year,"centers":out}


def from_paired(item):
    year=item["year"]
    if year not in (2011,2014):
        raise ValueError("Paired year outside frozen subset")
    original=item["original"]
    alternate=item["alternative"]
    if original["status"]!="EXPLORATORY_INDEPENDENT_FASTICE_GRID_EXTRACTED":
        raise ValueError("Original-centroid source HOLD")
    if alternate["status"]!="ALTERNATIVE_PUBLISHED_CENTROID_ICE_PIXEL_CONTEXT_READ":
        raise ValueError("Alternate-centroid source HOLD")
    z=item["trajectory_by_radius"][RADIUS]
    if z["n_preimage_composites"]!=(9 if year==2011 else 11):
        raise ValueError("Missing frozen physical time bins")
    last=z["last_completed_preimage_composite"]
    lag=z["one_extra_15day_ahead_auxiliary_guard_composite"]
    sites={}
    for center, short in (("LaRue_original","original"),("Fretwell_alternative","alternative")):
        field="original" if short=="original" else "alternative"
        cells=last[field+"_class4_cells"]
        denom=last[field+"_n_cells"]
        fraction=_finite_fraction(cells,denom)
        series=z[short+"_site"]
        sites[center]={
            "last_preimage_class4_pixels":cells,
            "last_preimage_grid_cells":denom,
            "last_preimage_fraction":fraction,
            "n_preimage_intervals":z["n_preimage_composites"],
            "intervals_any_class4":series["number_composites_any_class4"],
            "longest_contiguous_intervals_any_class4":series["longest_consecutive_class4_composites"],
            "trailing_no_class4_intervals":series["trailing_consecutive_no_class4_composites"],
            "last_preimage_interval_start":str(last["composite_start_yyyymmdd"]),
            "pre_previous_class4_pixels":lag[field+"_class4_cells"],
            "pre_previous_grid_cells":lag[field+"_n_cells"]
        }
    joint=z["temporal_state_counts"]
    n=sum(joint.values())
    if n!=z["n_preimage_composites"]:
        raise ValueError("Invalid temporal ice overlap classes")
    return {"year":year,"centers":sites,"paired_ice_state_count":joint}


def synthesize(paired, historical):
    if paired["status"]!="PAIRED_PREIMAGE_PHYSICAL_TRAJECTORIES_EXTRACTED_NOT_BREEDING_HABITABILITY":
        raise ValueError("Incomplete frozen paired physical data")
    if historical["decision"]!="EXPLORATORY_PHYSICAL_ANCHOR_SERIES_AVAILABLE_ONLY":
        raise ValueError("Incomplete frozen historical physical data")
    if not historical["all_years_read"]:
        raise ValueError("Historical physical map gate failed")
    rows=[from_paired(r) for r in paired["year_results"]]
    rows += [from_historical(r) for r in historical["year_results"]]
    by_year={r["year"]:r for r in rows}
    if len(rows)!=6 or tuple(sorted(by_year))!=YEARS:
        raise ValueError("Missing six unique source years")
    output=[]
    for year in YEARS:
        result=by_year[year]
        original_code, author_ice, image_date=BIOLOGICAL_SOURCE[year]
        record={
            "year":year,
            "author_image_date":image_date,
            "author_bpresent":original_code,
            "author_ice_annotation":author_ice,
            "author_yes_does_not_prove_breeding_success":True,
            "differing_image_stages_not_treated_exchangeably":True,
            **result
        }
        for center in CENTERS:
            z=result["centers"][center]
            n=z["n_preimage_intervals"]
            present=z["intervals_any_class4"]
            if not (0<=present<=n):
                raise ValueError("Impossible ice persistence count")
            # Strict complete seasonal class4, intentionally a negative-control
            # proxy rather than a claim of actual biological viability.
            z["strict_all_preimage_intervals_any_class4"]=present==n
            z["observed_ice_source_class4_and_raw_image_birds_agree"]=(
                (z["last_preimage_class4_pixels"]>0)==(original_code=="yes")
            )
            if z["last_preimage_class4_pixels"] >0 and z["trailing_no_class4_intervals"]>0:
                raise ValueError("Trailing ice-absent run contradicts positive last bin")
        output.append(record)

    positive=[x for x in output if x["author_bpresent"]=="yes"]
    secondary2014=by_year[2014]["centers"]["Fretwell_alternative"]
    primary2014=by_year[2014]["centers"]["LaRue_original"]
    extra={
        "source_year_count":len(output),
        "author_raw_yes_years":[v["year"] for v in positive],
        "strict_all_preimage_intervals_class4_at_either_point_for_any_raw_yes_year":any(
            v["centers"][center]["strict_all_preimage_intervals_any_class4"]
            for v in positive for center in CENTERS),
        "2014_last_both_centers_disagree_on_class4":(
            primary2014["last_preimage_class4_pixels"]==0 and
            secondary2014["last_preimage_class4_pixels"]==secondary2014["last_preimage_grid_cells"]),
        "2014_lag_one_additional_interval_still_class4_discordant":(
            primary2014["pre_previous_class4_pixels"]==0 and
            secondary2014["pre_previous_class4_pixels"]==secondary2014["pre_previous_grid_cells"]),
        "2014_3km_class4_secondary_dominance_without_complementarity":(
            by_year[2014]["paired_ice_state_count"]["only_original_class4_any"]==0
            and by_year[2014]["paired_ice_state_count"]["only_alternative_class4_any"]>0),
        "2013_late_november_positive_without_preceding_class4_at_both_centers":(
            all(by_year[2013]["centers"][k]["last_preimage_class4_pixels"]==0 for k in CENTERS)
            and BIOLOGICAL_SOURCE[2013][0]=="yes"),
        "source_label_to_latent_successful_breeding_deduced":False,
        "usable_ice_capacity_or_colony_social_mechanism_identified":False
    }

    return {
        "status":"COMPLETE_DESCRIPTIVE_TWO_CENTROID_SIX_YEAR_ICE_CROSSWALK",
        "source":"Fraser/Massom 2020 v2.2 independent ice classifications and LaRue et al. original image notes",
        "statistical_inference":"NONE_SINGLE_SITE_OUTCOME_EXPOSED_NONINDEPENDENT",
        "years":list(YEARS),
        "radius_km":3,
        "results":output,
        "physical_source_checks":extra,
        "causal_effect_estimated":False,
        "new_breeding_success_data_opened":False,
        "actual_2014_nesting_polygon_identified":False,
        "stationary_colony_location_validated":False,
        "PR189_science_modified":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--paired",type=Path,required=True)
    p.add_argument("--historical",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result=synthesize(
        json.loads(args.paired.read_text()),
        json.loads(args.historical.read_text())
    )
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    for z in result["results"]:
        print("YEAR",z["year"],"RAW_BIRDS",z["author_bpresent"],
              "AUTHOR_ICE",z["author_ice_annotation"])
        for c in CENTERS:
            a=z["centers"][c]
            print("CENTER",c,"ICE_PREIMAGE",a["last_preimage_class4_pixels"],"/",
                  a["last_preimage_grid_cells"],"ICE_PERIODS",a["intervals_any_class4"],"/",
                  a["n_preimage_intervals"],"LONGEST_ICE_RUN",a["longest_contiguous_intervals_any_class4"])
    print("SOURCE_CHECKS",json.dumps(result["physical_source_checks"],sort_keys=True))
    print("NO_SUCCESSFUL_BREEDING_OR_CAUSAL_RESULT")


if __name__=="__main__":
    main()
