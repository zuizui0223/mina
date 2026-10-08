#!/usr/bin/env python3
"""Actual author original image CENTERS, not penguin nesting coordinates.

Pinned LaRue et al. 2024 original 2009-2018 satellite workbook only.
The image centroid and WGS84 referenced colony coordinates are different
measurement supports; scene center cannot establish polygon or nest location.
"""
from __future__ import annotations
import argparse
from datetime import date
import json
import math
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_larue_original_satellite_image_support_v1 import sheet_records,git_blob,SOURCE_SHA

REFS={
    "LaRue_static_colony":(-74.228,-130.784),
    "Fretwell_2021_colony":(-74.272,-131.243)
}

def geodistance(a,b,c,d):
    vals=(a,b,c,d)
    if any(not math.isfinite(v) for v in vals):
        raise ValueError("Bad coordinate")
    if abs(a)>90 or abs(c)>90 or abs(b)>180 or abs(d)>180:
        raise ValueError("Outside WGS84 bounds")
    p=math.pi/180
    e=(math.sin((c-a)*p/2)**2+
       math.cos(a*p)*math.cos(c*p)*math.sin((d-b)*p/2)**2)
    return 12742.0176*math.asin(min(1,math.sqrt(max(0,e))))


def parse_coord(value):
    try:
        f=float(value)
        return f if math.isfinite(f) else None
    except (TypeError,ValueError):
        return None


def audit(rows):
    ledda=sorted((r for r in rows if r.get("site_id")=="LEDD"),
                 key=lambda r:int(float(r["img_year"])))
    if len(ledda)!=10 or [int(r["img_year"]) for r in ledda]!=list(range(2009,2019)):
        raise ValueError("Not the expected original Ledda author record")
    result=[]
    for r in ledda:
        year=int(r["img_year"])
        la=parse_coord(r.get("img_lat"))
        lo=parse_coord(r.get("img_long"))
        try:
            image_date=date(year,int(float(r["img_month"])),int(float(r["img_day"]))).isoformat()
        except (ValueError,TypeError):
            image_date=None
        coord_valid=(la is not None and lo is not None and abs(la)<=90 and abs(lo)<=180)
        # In an Antarctic site-specific source, blank/zero geographic
        # placeholders may otherwise resemble a real Greenwich/Equator scene.
        raw_la,raw_lo=la,lo
        reason=None
        if coord_valid and (la==0 or lo==0):
            coord_valid=False
            reason="ZERO_SENTINEL_OR_AMBIGUOUS_COORDINATE"
        if coord_valid:
            near=min(geodistance(la,lo,*value) for value in REFS.values())
            if near>200:
                coord_valid=False
                reason="SOURCE_SCENE_CENTER_OVER_200KM_FROM_BOTH_PREPRINTED_LEDD_REFERENCES"
        if not coord_valid:
            if reason is None:reason="MISSING_OR_INVALID_WGS84_IMAGE_CENTER"
            la=lo=None
        dists={key:geodistance(la,lo,*value) if coord_valid else None
               for key,value in REFS.items()}
        result.append({
            "year":year,"author_img_date":image_date,
            "bpresent_original":r.get("bpresent"),
            "image_scene_centroid_lat":la,
            "image_scene_centroid_lon":lo,
            "raw_img_lat_parsed":raw_la,
            "raw_img_lon_parsed":raw_lo,
            "coordinate_within_predeclared_spatial_quality_gate":coord_valid,
            "coordinate_hold_reason":reason,
            "original_satellite_catalog_id":str(r.get("catalog_id","") or "")[:100],
            "distance_scene_center_to_reference_km":dists,
            "scene_center_not_guano_or_bird_location":True,
            "does_not_verify_whether_point_inside_scene_footprint":True
        })
    item=next(r for r in result if r["year"]==2014)
    if item["author_img_date"]!="2014-10-13" or str(item["bpresent_original"]).lower()!="no":
        raise ValueError("2014 historically frozen source image changed")
    return {
        "status":"AUTHOR_IMAGE_SCENE_CENTROIDS_CROSSWALKED_NOT_NESTING_POLYGONS",
        "source_blob_sha":SOURCE_SHA,
        "reference_coords":{k:list(v) for k,v in REFS.items()},
        "source_years":[r["year"] for r in result],
        "all_ten_records":result,
        "focus_2014":item,
        "image_scene_center_is_not_penguin_center":True,
        "2014_scene_extent_verified":False,
        "2014_Zhang_polygon_verified":False,
        "new_breeding_event_or_migration_claim":False,
        "Ecology_PR189_changed":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    data=args.input.read_bytes()
    if git_blob(data)!=SOURCE_SHA:
        raise ValueError("SOURCE_HASH_MISMATCH")
    result=audit(sheet_records(data))
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("2014_SCENE_COORDINATES",result["focus_2014"]["image_scene_centroid_lat"],
          result["focus_2014"]["image_scene_centroid_lon"])
    print("2014_SCENE_DISTANCE_TO_REF",
          json.dumps(result["focus_2014"]["distance_scene_center_to_reference_km"]))
    for r in result["all_ten_records"]:
        print("SCENE_YEAR",r["year"],r["author_img_date"],
              r["image_scene_centroid_lat"],r["image_scene_centroid_lon"],
              json.dumps(r["distance_scene_center_to_reference_km"]))
    print("SCENE_CENTER_IS_NOT_NEST_OR_SATELLITE_FOOTPRINT")


if __name__=="__main__":
    main()
