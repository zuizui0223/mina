"""Paired *physical-only* Ledda 2011/2014 fast-ice trajectories at published centroids.

This is an EXPLORATORY post-source-exposure analysis, comparing already-fixed
Fraser/Massom 1km / 15-day seasonal ice pixels at TWO independent publication
coordinates. It reuses the identical years, radii, season indices and no-future
windows from the existing PR195 source contracts. It cannot locate nests or
infer viable unused habitat, island recolonization, or penguin social selection.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_fraser_ledda_frozen_2011_2014_fastice_v1 as primary
import extract_ledda_fretwell_secondary_centroid_fastice_v1 as secondary

YEARS=(2011,2014)
RADII=(1,3,5)


def summaries_for_radius(year, left, right, radius):
    """Fail-closed paired comparison of two *preimage-only* fixed trajectories."""
    timing=primary.FROZEN_YEAR[year]
    allowed=list(timing["preimage_indices"])
    def records(report):
        if report["year"]!=year:
            raise ValueError("Unexpected year on fixed response-free map")
        all_entries=report["composite_records"]
        got=[i["time_index"] for i in all_entries]
        if got!=sorted(set(allowed+[timing["overlap_t"]])):
            raise ValueError("Unfrozen or missing date indices; cannot compare")
        return {e["time_index"]:e for e in all_entries}
    a,b=records(left),records(right)
    rows=[]
    for t in allowed:
        p=a[t]["radius_summaries_km"][str(radius)]
        s=b[t]["radius_summaries_km"][str(radius)]
        if a[t]["composite_start_yyyymmdd"]!=b[t]["composite_start_yyyymmdd"]:
            raise ValueError("Centroids not sampled at the same date")
        for z in (p,s):
            if z["n_class_valid"]<=0 or z["n_class_valid"]!=z["n_cells_spatial_mask"]:
                raise ValueError("Unresolved pixel classes; fail closed")
            if z["n_fastice_class4"]>z["n_class_valid"]:
                raise ValueError("Impossible frozen class-4 count")
        rows.append({
            "time_index":t,
            "composite_start_yyyymmdd":a[t]["composite_start_yyyymmdd"],
            "original_LaRue_class4_cells":p["n_fastice_class4"],
            "original_LaRue_n_cells":p["n_class_valid"],
            "alternative_Fretwell_class4_cells":s["n_fastice_class4"],
            "alternative_Fretwell_n_cells":s["n_class_valid"],
            "original_class4_fraction":p["fraction_fastice_over_valid_cells"],
            "alternative_class4_fraction":s["fraction_fastice_over_valid_cells"],
            "fraction_difference_alt_minus_original":s["fraction_fastice_over_valid_cells"]-p["fraction_fastice_over_valid_cells"],
            "original_any_class4":p["n_fastice_class4"]>0,
            "alternative_any_class4":s["n_fastice_class4"]>0,
            "original_edges":p["n_edge_classes_5_or_6"],
            "alternative_edges":s["n_edge_classes_5_or_6"],
        })
    return rows


def trajectory_readout(year, rows):
    if len(rows)!=len(primary.FROZEN_YEAR[year]["preimage_indices"]):
        raise ValueError("Incomplete frozen preimage season")
    statuses=[(bool(r["original_any_class4"]),bool(r["alternative_any_class4"])) for r in rows]
    totals={
        "both_class4_any":sum(p and q for p,q in statuses),
        "only_original_class4_any":sum(p and not q for p,q in statuses),
        "only_alternative_class4_any":sum(q and not p for p,q in statuses),
        "neither_class4_any":sum(not p and not q for p,q in statuses),
    }
    assert sum(totals.values())==len(rows)
    def trajectory_side(key):
        booleans=[q[0] if key=="original" else q[1] for q in statuses]
        return {
            "number_composites_any_class4":sum(booleans),
            "transitions_any_to_none_or_none_to_any":sum(x!=y for x,y in zip(booleans,booleans[1:])),
            "longest_consecutive_class4_composites":max(
                (len(v) for v in _runs(booleans,True)),default=0),
            "trailing_consecutive_no_class4_composites":sum(
                1 for b in _prefix_until_true(reversed(booleans))),
            "last_preimage_class4_detected":booleans[-1]
        }
    union=totals["both_class4_any"]+totals["only_original_class4_any"]+totals["only_alternative_class4_any"]
    return {
        "year":year,
        "n_preimage_composites":len(rows),
        "temporal_state_counts":totals,
        "temporal_any_ice_jaccard":totals["both_class4_any"]/union if union else None,
        "original_site":trajectory_side("original"),
        "alternative_site":trajectory_side("alternative"),
        "last_completed_preimage_composite":rows[-1],
        "seasonal_timeline":rows,
        "causal_penguin_conclusion_available":False,
    }


def _prefix_until_true(items):
    for v in items:
        if v:
            break
        yield v


def _runs(items,value):
    ans=[]
    running=[]
    for a in items:
        if a==value:
            running.append(a)
        elif running:
            ans.append(running)
            running=[]
    if running: ans.append(running)
    return ans


def compare_year(year, original, alternative):
    if year not in YEARS or not secondary.is_frozen_plan():
        raise ValueError("Cannot alter frozen source plan")
    if original["status"]!="EXPLORATORY_INDEPENDENT_FASTICE_GRID_EXTRACTED":
        raise ValueError("Original centroid source HOLD")
    if alternative["status"]!="ALTERNATIVE_PUBLISHED_CENTROID_ICE_PIXEL_CONTEXT_READ":
        raise ValueError("Alternative centroid source HOLD")
    return {str(radius):trajectory_readout(year,summaries_for_radius(year,original,alternative,radius))
            for radius in RADII}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result={
        "status":"HOLD_PHYSICAL_DUAL_COORDINATE_READOUT",
        "years":list(YEARS),
        "original_coordinate": [primary.LAT,primary.LON],
        "alternative_coordinate": [secondary.ALT_LAT,secondary.ALT_LON],
        "comparison_radius_km":list(RADII),
        "science_scope":"EXPLORATORY_ALREADY_EXPOSED_ICE_READOUT_NO_NEW_PENGUIN_OUTCOME",
        "new_penguin_biological_rows_opened":0,
        "penguin_causal_social_or_rescue_effect_fitted":False,
        "PR189_science_changed":False
    }
    reports=[]
    try:
        for year in YEARS:
            original=primary.read_one_year(year)
            alternative=secondary.read_one_year(year)
            if original["status"]!="EXPLORATORY_INDEPENDENT_FASTICE_GRID_EXTRACTED" or alternative["status"]!="ALTERNATIVE_PUBLISHED_CENTROID_ICE_PIXEL_CONTEXT_READ":
                raise ValueError(f"HOLD_{year} source: {original.get('error_message')} | {alternative.get('error_message')}")
            reports.append({
                "year":year,
                "original":original,
                "alternative":alternative,
                "trajectory_by_radius":compare_year(year,original,alternative)
            })
        result["status"]="PAIRED_PREIMAGE_PHYSICAL_TRAJECTORIES_EXTRACTED_NOT_BREEDING_HABITABILITY"
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error_message"]=str(exc)[:300]
    result["year_results"]=reports
    result["total_remote_bytes"]=sum(
        z["original"]["http_body_bytes"]+z["alternative"]["http_body_bytes"] for z in reports)
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("PAIRED_LEDDA_PHYSICAL_RESULT",result["status"])
    for record in reports:
        y=record["year"]
        r=record["trajectory_by_radius"]["3"]
        print("YEAR",y,"PREIMAGE_N",r["n_preimage_composites"],
              "JOINT",r["temporal_state_counts"])
        print("ORIGINAL",r["original_site"])
        print("ALTERNATIVE",r["alternative_site"])
        for t in r["seasonal_timeline"]:
            print("TIMELINE_3KM",y,t["composite_start_yyyymmdd"],
                  t["original_LaRue_class4_cells"],"/",t["original_LaRue_n_cells"],
                  t["alternative_Fretwell_class4_cells"],"/",t["alternative_Fretwell_n_cells"])
    if "error_message" in result: print("HOLD_ERROR",result["error_message"])


if __name__=="__main__":
    main()
