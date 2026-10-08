#!/usr/bin/env python3
"""2024 SAR emperor huddle centroids vs 2024 author roster's historic fixed sites.

Secondary AFTER DATA EXPOSURE comparison. Does not measure successful breeding,
natal dispersal, population turnover, or true spatial range of all potential
site positions. SAR winter-2024 samples came from selected known colonies.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
import math
from pathlib import Path
import statistics

EARTH_MEAN_RADIUS_KM = 6371.0088
THRESHOLDS_KM = (1, 2, 3, 5)
SITES = {
    "Atka Bay": "Atka",
    "Cape Crozier": "Cape Crozier",
    "Cape Roget": "Cape Roget",
    "Cape Washington": "Cape Washington",
    "Coulman Island": "Coulman Island",
    "Franklin Island": "Franklin Island",
}
EXPECTED_DYNAMIC_ROWS = 64
EXPECTED_POSITIVE_ROWS = 54
LEDDA_TWO_PUBLISHED_CENTROID_DISTANCE_KM = 14.692


def great_circle_km(lat_a:float, lon_a:float, lat_b:float, lon_b:float)->float:
    for lat,lon in ((lat_a,lon_a),(lat_b,lon_b)):
        if not math.isfinite(lat) or not math.isfinite(lon) or not (-90<=lat<=90 and -180<=lon<=180):
            raise ValueError("Invalid WGS84 geodetic input")
    dlat=math.radians(lat_b-lat_a)
    dlon=math.radians(lon_b-lon_a)
    z=(math.sin(dlat/2)**2+
       math.cos(math.radians(lat_a))*math.cos(math.radians(lat_b))*math.sin(dlon/2)**2)
    return 2*EARTH_MEAN_RADIUS_KM*math.asin(math.sqrt(max(0,min(1,z))))


def finite_number(s):
    try:
        x=float(s)
    except (ValueError,TypeError):
        return None
    return x if math.isfinite(x) else None


def audited_table(path:Path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    if not rows:
        raise ValueError("Missing frozen source CSV")
    return rows


def calculate(original_site_rows:list[dict], sar_scene_rows:list[dict])->dict:
    stationary={}
    for row in original_site_rows:
        name=row.get("site_name")
        if name not in SITES.values():
            continue
        if name in stationary:
            raise ValueError("Duplicated historic site in original author source")
        la,lo=finite_number(row.get("lat")),finite_number(row.get("lon"))
        if la is None or lo is None:
            raise ValueError("Unknown author site coordinates")
        great_circle_km(la,lo,la,lo)
        stationary[name]=(la,lo)
    if set(stationary)!=set(SITES.values()):
        raise ValueError("Expected six known reference sites missing")

    if len(sar_scene_rows)!=EXPECTED_DYNAMIC_ROWS:
        raise ValueError("Unrecognized pinned 2024 SAR rows")
    records={name:[] for name in SITES}
    n_zero=0
    for row in sar_scene_rows:
        name=row.get("colony")
        if name not in SITES:
            raise ValueError("Unrecognized SAR colony site")
        when=datetime.strptime(row["yyyymmdd"], "%d/%m/%Y")
        if when.year!=2024:
            raise ValueError("Unfrozen SAR year")
        area=finite_number(row.get("areasum"))
        if area is None or area<0:
            raise ValueError("Invalid area in published SAR summary")
        if area==0:
            n_zero+=1
            continue
        # Zero-area convenience image records are NOT observed biological absences.
        lat,lon=finite_number(row.get("ycoordmean")),finite_number(row.get("xcoordmean"))
        if lat is None or lon is None:
            raise ValueError("Positive huddle area missing actual scene centroid")
        src_lat,src_lon=stationary[SITES[name]]
        dist=great_circle_km(src_lat,src_lon,lat,lon)
        records[name].append({"image_date":when.date().isoformat(),"centroid_distance_km":dist})

    all_valid=[item for xs in records.values() for item in xs]
    if len(all_valid)!=EXPECTED_POSITIVE_ROWS or n_zero!=EXPECTED_DYNAMIC_ROWS-EXPECTED_POSITIVE_ROWS:
        raise ValueError("Original published SAR scene eligibility count changed")

    summaries=[]
    for name,points in records.items():
        if not points:
            raise ValueError("Expected actual SAR scenes at every frozen colony")
        distances=sorted(x["centroid_distance_km"] for x in points)
        la,lo=stationary[SITES[name]]
        summaries.append({
            "colony":name,
            "source_static_name":SITES[name],
            "historic_author_site_lat":la,
            "historic_author_site_lon":lo,
            "n_positive_sar_scene_dates":len(distances),
            "minimum_km":min(distances),
            "median_km":statistics.median(distances),
            "maximum_km":max(distances),
            "scene_count_centroid_distance_over_km":{
                str(radius):sum(d>radius for d in distances)
                for radius in THRESHOLDS_KM
            }
        })
    distances=sorted(v["centroid_distance_km"] for v in all_valid)
    result={
        "status":"SOURCE_BACKED_SAR_2024_STATIC_SITE_COMPARISON_EXPLORATORY",
        "original_static_source":"davidiles/EMPE_Global pinned colony_attributes.csv",
        "sar_source":"mla150/SAR-Emperor published 2024 six-colony summary",
        "sar_scene_total":len(sar_scene_rows),
        "sar_scene_positive_centroid_eligible":len(distances),
        "zero_area_or_not_detected_sar_rows_EXCLUDED_not_absence":n_zero,
        "n_colonies":len(summaries),
        "colony_summaries":summaries,
        "overall_median_km":statistics.median(distances),
        "overall_max_km":max(distances),
        "pooled_sar_scene_centroids_outside_threshold":{
            str(radius):sum(d>radius for d in distances) for radius in THRESHOLDS_KM
        },
        "ledda_cross_publication_disagreement_km":LEDDA_TWO_PUBLISHED_CENTROID_DISTANCE_KM,
        "ledda_cross_publication_distance_divided_by_largest_2024_sample_distance":LEDDA_TWO_PUBLISHED_CENTROID_DISTANCE_KM/max(distances),
        "never_equate_cross_publication_distance_to_true_ledda_movement":True,
        "SAR_2024_source_sites_selected_nonrandomly":True,
        "not_an_independent_general_penguin_dispersal_test":True,
        "not_a_2024_fast_ice_test":True,
        "new_penguin_causal_or_breeding_success_effect_identified":False,
        "PR189_scientific_freeze_preserved":True
    }
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--static-csv",type=Path,required=True)
    p.add_argument("--sar-csv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    data=calculate(audited_table(a.static_csv),audited_table(a.sar_csv))
    a.out.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print("SAR_SITE_SUPPORT_COMPARATOR",data["status"])
    print("SOURCE_SCENES",data["sar_scene_total"],"POSITIVE_SCENES",data["sar_scene_positive_centroid_eligible"])
    for item in data["colony_summaries"]:
        print("COLONY",item["colony"],"n",item["n_positive_sar_scene_dates"],
              "median_distance_km",round(item["median_km"],4),
              "max_distance_km",round(item["maximum_km"],4),
              "count_beyond_3km",item["scene_count_centroid_distance_over_km"]["3"])
    print("MAX_ALL_SAR_KM",round(data["overall_max_km"],4))
    print("LEDDA_PUBLISHED_COORDINATE_RATIO",round(data["ledda_cross_publication_distance_divided_by_largest_2024_sample_distance"],2))
    print("CAUSAL_OR_BREEDING_SUCCESS_EFFECT",False)


if __name__=="__main__":
    main()
