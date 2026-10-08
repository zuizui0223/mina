#!/usr/bin/env python3
"""Original source field-role audit across all emperor 2009-2018 image records.

Tests whether img_lat/img_long are independent observation-specific coordinates
or fixed approximate site coordinates reattached across survey years.
It NEVER assumes they are actual satellite scene centers or nest footprints.
No new penguin outcome model is fitted; raw image value counts are not effect
sizes and 2014 Ledda alone cannot prove bird emigration.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import argparse
import csv
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_larue_original_satellite_image_support_v1 import (
    git_blob, sheet_records, SOURCE_SHA
)

ATTR_SHA="b27e18d5746a03279661748cbb427fa76183cd67"
YEARS=range(2009,2019)
TOL=1e-9


def number(raw):
    try:
        x=float(raw)
    except (TypeError,ValueError):
        return None
    return x if math.isfinite(x) else None


def verify_coords(a,b):
    return a is not None and b is not None and -90<=a<=90 and -180<=b<=180


def geodesic_km(lat1,lon1,lat2,lon2):
    p=math.pi/180
    h=math.sin((lat2-lat1)*p/2)**2+math.cos(lat1*p)*math.cos(lat2*p)*math.sin((lon2-lon1)*p/2)**2
    return 12742.0176*math.asin(min(1,math.sqrt(max(0,h))))


def audit(image_rows,site_rows):
    if len(image_rows)!=599:
        raise ValueError("Source raw 2009-18 image row count unexpectedly changed")
    sites={}
    for row in site_rows:
        key=str(row.get("site_id","")).strip()
        if not key or key in sites:
            raise ValueError("Invalid or duplicate original colony lookup key")
        lat=number(row.get("lat"))
        lon=number(row.get("lon"))
        sites[key]={"latitude":lat,"longitude":lon,"site_name":row.get("site_name","")}
    valid_counts=Counter()
    by_site=defaultdict(list)
    for row in image_rows:
        site=str(row.get("site_id","")).strip()
        if site not in sites:
            raise ValueError("Image site not found in pinned original colony attribute lookup: "+site)
        yr=int(float(row.get("img_year","nan")))
        if yr not in YEARS:
            raise ValueError("Unexpected image year")
        ilat=number(row.get("img_lat"))
        ilon=number(row.get("img_long"))
        alat=sites[site]["latitude"]
        alon=sites[site]["longitude"]
        if not verify_coords(alat,alon):
            raise ValueError("Original site lacks proper geographic coordinates")
        is_valid=verify_coords(ilat,ilon)
        has_zeros=is_valid and (ilat==0 or ilon==0)
        identity=(is_valid and abs(ilat-alat)<=TOL and abs(ilon-alon)<=TOL)
        if not is_valid:
            typ="MISSING_OR_INVALID_SOURCE_IMAGE_COORD"
        elif has_zeros:
            typ="VALID_RANGE_BUT_ZERO_AMBIGUOUS_IMAGE_COORD"
        elif identity:
            typ="EXACTLY_SITE_STATIC_COORD"
        else:
            typ="NONSTATIC_IMAGE_COORD_UNVERIFIED_ROLE"
        valid_counts[typ]+=1
        by_site[site].append({
            "year":yr,
            "source_coord_class":typ,
            "is_equal_static":bool(identity),
            "image_lat":ilat if is_valid else None,
            "image_lon":ilon if is_valid else None,
            "separation_km":geodesic_km(ilat,ilon,alat,alon) if is_valid else None
        })
    summary=[]
    for site in sorted(by_site):
        z=by_site[site]
        valid=[v for v in z if v["separation_km"] is not None]
        nonzero_valid=[v for v in valid if v["image_lat"]!=0 and v["image_lon"]!=0]
        distinct={(v["image_lat"],v["image_lon"]) for v in valid}
        summary.append({
            "site_id":site,
            "site_name":sites[site]["site_name"],
            "n_original_images":len(z),
            "n_valid_image_coordinates":len(valid),
            "n_exactly_equal_site_static":sum(v["is_equal_static"] for v in z),
            "n_coord_pairs":len(distinct),
            "n_nonstatic_nonzero_image_coords":sum(
                v["source_coord_class"]=="NONSTATIC_IMAGE_COORD_UNVERIFIED_ROLE" for v in z),
            "max_dist_km_raw_valid":max((v["separation_km"] for v in valid),default=None),
            "all_valid_nonzero_coordinates_identical_to_static":(
                bool(nonzero_valid) and all(v["is_equal_static"] for v in nonzero_valid)
            ),
            "unknown_actual_scene_footprint_or_nest_location":True
        })
    led=[v for v in summary if v["site_id"]=="LEDD"]
    if len(led)!=1 or led[0]["n_original_images"]!=10:
        raise ValueError("Ledda 10-year original row audit changed")
    result={
        "source":"LaRue et al. 2024 2009–18 original image rows and colony_attributes.csv pinned commit",
        "status":"ORIGINAL_IMAGE_COORDINATE_FIELDS_IDENTIFIABILITY_AUDITED_NOT_TRUE_NEST_GEOMETRY",
        "source_observations":len(image_rows),
        "source_sites":len(summary),
        "original_image_coord_field_classes":dict(sorted(valid_counts.items())),
        "sites_all_nonzero_valid_image_coordinates_identical_to_static":sum(
            z["all_valid_nonzero_coordinates_identical_to_static"] for z in summary),
        "sites_with_multiple_distinct_valid_image_coord_pairs":sum(
            z["n_coord_pairs"]>1 for z in summary),
        "sites_with_any_nonstatic_nonzero_image_coordinates":sum(
            z["n_nonstatic_nonzero_image_coords"]>0 for z in summary),
        "Ledda_summary":led[0],
        "per_site":summary,
        "actual_satellite_scene_georeference_proven_by_these_fields":False,
        "actual_bird_or_guano_polygons_proven_by_these_fields":False,
        "real_colony_immobility_or_movement_inferred":False,
        "biological_causal_effect_fitted":False,
        "PR189_science_changed":False
    }
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--satellite-xlsx",type=Path,required=True)
    p.add_argument("--static-csv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    raw=args.satellite_xlsx.read_bytes()
    if git_blob(raw)!=SOURCE_SHA:
        raise ValueError("Original author XLSX SHA mismatched")
    static_bytes=args.static_csv.read_bytes()
    if git_blob(static_bytes)!=ATTR_SHA:
        raise ValueError("Original author colony attributes blob mismatch")
    with args.static_csv.open(newline="",encoding="utf-8-sig") as handle:
        attrs=list(csv.DictReader(handle))
    data=audit(sheet_records(raw),attrs)
    args.out.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8")
    print("RAW_IMAGE_COORD_AUDIT",data["status"])
    print("SOURCE_ROWS",data["source_observations"],"SITES",data["source_sites"])
    print("COORD_FIELD_CLASSES",json.dumps(data["original_image_coord_field_classes"],sort_keys=True))
    print("ALL_COORDS_STATIC_SITES",data["sites_all_nonzero_valid_image_coordinates_identical_to_static"])
    print("SITES_WITH_MULTIPLE_IMAGE_COORDS",data["sites_with_multiple_distinct_valid_image_coord_pairs"])
    print("LEDDA",json.dumps(data["Ledda_summary"],sort_keys=True))
    print("NOT_A_MOVEMENT_OR_COLONIZATION_RESULT")


if __name__=="__main__":
    main()
