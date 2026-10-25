#!/usr/bin/env python3
"""Original AADC potential-site geography network (no biological response).

Uses all 7,785 verified 2025 publisher geographic site IDs independently of
known penguin/other seabird survey P/A/NR, counts or historical census outcomes.
Same source *class* is not the same physical island.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import numpy as np
from pyproj import Transformer
from scipy.spatial import cKDTree
from audit_aadc_geography_editions_v1 import source_geography_only,parse_geo

RADII_M=(2000,10000,50000)
SOURCE_CLASSES=("island","continent")


def site_point_network(projected:list[dict], older_ids:set[str]):
    """Build deterministic nearest-neighbor and fixed-radius candidate-site graph."""
    if len({r["site_id"] for r in projected})!=len(projected):
        raise ValueError("SOURCE_STOP duplicate original site identifiers")
    if not projected:
        raise ValueError("SOURCE_STOP original geographic source empty")
    data=sorted(projected,key=lambda r:r["site_id"])
    classes=np.asarray([r["source_class"] for r in data])
    if any(c not in SOURCE_CLASSES for c in classes):
        raise ValueError("SOURCE_STOP unknown original candidate site geographic class")
    coords=np.asarray([[float(r["x"]),float(r["y"])] for r in data],dtype=float)
    if not np.isfinite(coords).all():
        raise ValueError("GEOMETRY_STOP invalid source coordinate projection")
    tree=cKDTree(coords)
    if len(coords)>1:
        dist,_index=tree.query(coords,k=2)
        nearest=dist[:,1]
    else:
        nearest=np.full(len(coords),np.nan,dtype=float)
    same=np.full(len(coords),np.nan,dtype=float)
    other=np.full(len(coords),np.nan,dtype=float)
    for cat in SOURCE_CLASSES:
        mask=classes==cat
        local=np.flatnonzero(mask)
        complement=np.flatnonzero(~mask)
        if len(local)>1:
            d,_=cKDTree(coords[local]).query(coords[local],k=2)
            same[local]=d[:,1]
        if len(complement):
            d,_=cKDTree(coords[complement]).query(coords[local],k=1)
            other[local]=d
    radii={
        rad:tree.query_ball_point(coords,r=rad,return_length=True)-1
        for rad in RADII_M
    }
    result=[]
    for i,r in enumerate(data):
        def finite_or_none(x):
            return float(x) if np.isfinite(x) else None
        item={
            "geog_site_id":r["site_id"],
            "source_site_class":r["source_class"],
            "original_site_id_present_in_2021_edition":r["site_id"] in older_ids,
            "nearest_any_other_source_site_point_m":finite_or_none(nearest[i]),
            "nearest_same_author_class_site_point_m":finite_or_none(same[i]),
            "nearest_other_author_class_site_point_m":finite_or_none(other[i]),
            "other_original_potential_site_centres_within_2km":int(radii[2000][i]),
            "other_original_potential_site_centres_within_10km":int(radii[10000][i]),
            "other_original_potential_site_centres_within_50km":int(radii[50000][i]),
        }
        result.append(item)

    summaries={}
    for name, idx in (
        ("all_2025",np.arange(len(data))),
        ("2021_2025_shared_site_ids",np.asarray([i for i,r in enumerate(data) if r["site_id"] in older_ids],dtype=int)),
        ("new_only_in_2025_edition",np.asarray([i for i,r in enumerate(data) if r["site_id"] not in older_ids],dtype=int)),
        *((f"source_class_{cat}",np.flatnonzero(classes==cat)) for cat in SOURCE_CLASSES)
    ):
        near=nearest[idx]
        def quant(x):
            val=np.asarray(x,dtype=float)
            val=val[np.isfinite(val)]
            return None if not len(val) else {
                "median":float(np.median(val)),
                "p10":float(np.percentile(val,10)),
                "p90":float(np.percentile(val,90)),
            }
        summaries[name]={
            "unique_original_site_ids":len(idx),
            "nearest_other_potential_site_point_distance_m":quant(near),
            "other_candidate_points_within_2km":quant(radii[2000][idx]),
            "other_candidate_points_within_10km":quant(radii[10000][idx]),
            "other_candidate_points_within_50km":quant(radii[50000][idx]),
            "source_centroids_without_other_potential_site_within_2km":int(
                np.count_nonzero(radii[2000][idx]==0)
            )
        }
    report={
        "status":"AADC_ORIGINAL_POTENTIAL_SITE_GEOGRAPHICAL_NETWORK_V1",
        "author_original_geographic_site_total":len(data),
        "source_geographic_site_classes":{
            cat:int(np.count_nonzero(classes==cat)) for cat in SOURCE_CLASSES
        },
        "frozen_planar_candidate_site_centroid_radii_m":list(RADII_M),
        "network_descriptive_summaries":summaries,
        "reported_nearest_different_class_is_water_barrier_distance":False,
        "reported_nearest_same_class_is_within_same_physical_island":False,
        "original_site_geography_is_actual_penguin_nesting_location":False,
        "source_potential_site_network_is_complete_habitat_census":False,
        "P_A_NR_or_breeding_count_outcomes_opened":0,
        "ecological_effect_models_fitted":0,
    }
    return result,report


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--summary",type=Path,required=True)
    a.add_argument("--features",type=Path,required=True)
    args=a.parse_args()
    data,receipts,manifest_sha=source_geography_only()
    old,oldqa=parse_geo(data["potential_geography_2021"],old=True)
    new,newqa=parse_geo(data["potential_geography_2025"],old=False)
    if len(old)!=4884 or len(new)!=7785:
        raise ValueError("SOURCE_STOP original geographical source edition count changed")
    transformer=Transformer.from_crs(4326,3031,always_xy=True)
    projected=[]
    for sid,entry in new.items():
        if entry["lat"] is None or entry["lon"] is None:
            raise ValueError("SOURCE_STOP missing original candidate geographic site coordinate")
        x,y=transformer.transform(entry["lon"],entry["lat"])
        projected.append({"site_id":sid,"source_class":entry["feature"],"x":x,"y":y})
    rows,report=site_point_network(projected,set(old))
    report["source_original_workbook_receipts"]=receipts
    report["original_AADC_public_manifest_SHA256"]=manifest_sha
    report["geometry_coordinate_system"]="EPSG:3031 site-centre projected planar distance"
    report["source_edition_2021_site_count"]=len(old)
    report["source_edition_2025_site_count"]=len(new)
    report["original_input_geography_2025_qa"]=newqa
    args.features.parent.mkdir(parents=True,exist_ok=True)
    args.summary.parent.mkdir(parents=True,exist_ok=True)
    with args.features.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    report["derived_source_site_network_features_CSV_SHA256"]=hashlib.sha256(
        args.features.read_bytes()).hexdigest()
    args.summary.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))


if __name__=="__main__":
    main()
