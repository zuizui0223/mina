#!/usr/bin/env python3
"""Original 28 AADC colony-footprint bounds to SCAR physical land polygons.

Corrects V12's incompatible source site-ID namespace. Tier A complete bbox
containment is sufficient to prove that the entire mapped source polygon
lies within one land polygon; Tier B centroid only is provisional.
No new bird observations or P/A source data are read.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,tempfile
from collections import Counter,defaultdict
from pathlib import Path
from shapely.strtree import STRtree
from shapely.geometry import Point

from audit_aadc_repeated_landmass_support_v12 import read_frozen_v10_rows,validate_polygon_bbox
from derive_aadc_repeated_colony_boundaries_v10 import identify_source_geometry
import link_apbp_to_add_island_rock_v3 as bas
import validate_apbp_highres_coast_v4 as coast

ORIGINAL_HIGHRES_SHA="66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4"


def land_feature_assignment(rows:list,land_features:list):
    if len(rows)!=28:
        raise ValueError("SAMPLE_STOP source original repeated colony year count must remain 28")
    land_geom=[x[1] for x in land_features]
    tree=STRtree(land_geom)
    largest_land_id=max(land_features,key=lambda x:x[1].area)[0]
    output=[]
    for r in rows:
        source_bbox=validate_polygon_bbox(r)
        candidates=tree.query(source_bbox)
        exact=[int(i) for i in candidates if land_geom[int(i)].covers(source_bbox)]
        p=source_bbox.centroid
        center=[int(i) for i in tree.query(p) if land_geom[int(i)].covers(p)]
        if len(exact)==1:
            land_id=land_features[exact[0]][0]
            status="EXACT_ONE_LAND_FULL_BOUNDING_RECTANGLE"
        elif len(exact)>1:
            land_id=None
            status="HOLD_MULTIPLE_LAND_FEATURES_COVER_RECTANGLE"
        elif len(center)==1:
            land_id=None
            status="CENTER_ONLY_PROVISIONAL_NOT_ISLAND_ID"
        elif len(center)>1:
            land_id=None
            status="HOLD_MULTIPLE_LAND_FEATURES_CONTAIN_CENTER"
        else:
            land_id=None
            status="HOLD_NO_LAND_MATCHED_SOURCE_POLYGON_RECTANGLE"
        output.append({
            "original_site_id":str(r["site_id"]),
            "original_source_group":str(r["source_group"]),
            "original_season_start_year":int(r["season_start_year"]),
            "original_site_union_polygon_record_n":int(r["original_source_polygon_record_n"]),
            "original_full_bbox_match_status":status,
            "original_exact_parent_land_polygon_FID":land_id,
            "source_bbox_centroid_parent_land_FID_diagnostic":(
                 land_features[center[0]][0] if len(center)==1 else None),
            "original_bbox_evidence_of_same_true_island":False,
            "author_source_group_is_mapped_landmass":False,
            "source_parent_id_is_official_named_island":False,
            "mapped_polygon_source_area_decline_animal_count_decline":False,
        })
    by=defaultdict(list)
    for row in output:by[row["original_site_id"]].append(row)
    stable={}
    for sid,records in sorted(by.items()):
        years=sorted(r["original_season_start_year"] for r in records)
        parent={r["original_exact_parent_land_polygon_FID"] for r in records}
        if len(parent)==1 and None not in parent:
            stable[sid]={"status":"STABLE_EXACT_ONE_MAPPED_LAND_FID",
                         "mapped_land_source_FID":next(iter(parent)),
                         "source_season_years":years,
                         "group":records[0]["original_source_group"]}
        else:
            stable[sid]={"status":"HOLD_SOURCE_GEOMETRY_UNCERTAIN_OR_CONFLICTING_LAND",
                         "mapped_land_source_FID":None,
                         "source_season_years":years,
                         "group":records[0]["original_source_group"]}
    confirmed=defaultdict(list)
    for sid,st in stable.items():
        if st["mapped_land_source_FID"] is not None:
            confirmed[str(st["mapped_land_source_FID"])].append(sid)
    summary={
        "status":"AADC_REPEATED_COLONY_ORIGINAL_BBOX_MAPPED_LAND_QA_V13",
        "original_source_repeat_site_seasons":len(output),
        "original_source_repeat_unique_site_IDs":len(stable),
        "individual_source_colony_bbox_geographic_statuses":dict(Counter(
            r["original_full_bbox_match_status"] for r in output)),
        "unique_site_IDs_all_seasons_strict_same_parent_land":sum(
            x["status"]=="STABLE_EXACT_ONE_MAPPED_LAND_FID" for x in stable.values()),
        "unique_site_IDs_source_continuity_unresolved":sum(
            x["status"]!="STABLE_EXACT_ONE_MAPPED_LAND_FID" for x in stable.values()),
        "distinct_strictly_verified_source_land_features_with_repeated_sites":len(confirmed),
        "source_strict_mapped_land_features_with_original_sites":dict(sorted(confirmed.items())),
        "largest_original_SCAR_land_FID_is_continent_proxy_not_official_island":largest_land_id,
        "site_original_parent_land_fid_qa":stable,
        "only_geographical_location_metadata_read_from_prior_colony_source":True,
        "new_penguin_observations_or_colony_geometry_loaded":False,
        "new_island_effect_fitted":False,
        "source_polygon_buffer_or_spatial_tolerance_tuned":False,
    }
    return output,summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v9",type=Path,required=True)
    p.add_argument("--v10",type=Path,required=True)
    p.add_argument("--v10-site-metrics",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--site-years",type=Path,required=True)
    args=p.parse_args()
    manifest=json.loads(args.v9.read_text(encoding="utf-8"))
    receipt=json.loads(args.v10.read_text(encoding="utf-8"))
    selected,_=identify_source_geometry(manifest)
    original=read_frozen_v10_rows(args.v10_site_metrics,receipt,selected)
    oldmax=bas.MAX_BYTES
    try:
        bas.MAX_BYTES=coast.HIGH_ZIP_LIMIT
        zipped=bas.fetch_bas(coast.HIGH_URL)
    finally:
        bas.MAX_BYTES=oldmax
    source_sha=hashlib.sha256(zipped).hexdigest()
    if source_sha!=ORIGINAL_HIGHRES_SHA:
        raise ValueError("SOURCE_STOP original SCAR land source SHA drift")
    with tempfile.TemporaryDirectory(prefix="source-colony-land-") as tmp:
        land,qa=coast.original_highres_shapes(zipped,Path(tmp)/"coast",{})
    rows,summary=land_feature_assignment(original,land)
    summary["publisher_original_SCAR_land_v712_ZIP_SHA256"]=source_sha
    summary["original_V10_site_yr_metrics_sha256"]=receipt["derived_site_year_metrics_CSV_SHA256"]
    summary["source_original_land_polygon_QA"]=qa
    args.site_years.parent.mkdir(parents=True,exist_ok=True)
    with args.site_years.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    summary["derived_original_colony_siteyear_source_land_check_sha256"]=hashlib.sha256(
        args.site_years.read_bytes()).hexdigest()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))


if __name__=="__main__":
    main()
