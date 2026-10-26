#!/usr/bin/env python3
"""V10 actual original AADC repeated breeding-colony boundary geometry.

Publisher GIS filenames (V9) fixed before opening *any* original geometry.
Download 13 site IDs / 28 original site-years from AADC, no paper effect sizes,
no AADC P/A/NR records, no invented surveyed nonoccupancy.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import io
import json
import math
from pathlib import Path
import re
from urllib.parse import quote

from pyproj import CRS,Transformer
import requests
import shapefile
from shapely.geometry import shape
from shapely.ops import transform,unary_union
from shapely.validation import make_valid

from audit_aadc_original_workbook_headers_v11 import (
    HOST, trusted_response_get
)

DOI="10.4225/15/58f59b52edfef"
SOURCE_MANIFEST_STATUS="V9_ORIGINAL_MULTIISLAND_AADC_BOUNDARY_SHA_RECEIPTS"
MAX_SOURCE_BYTES=15_000_000
EXTS=(".shp",".shx",".dbf",".prj")
SOURCE_SITE_REGEX=re.compile(r"(?:^|/)IS_(\d+)(?:/|$)",re.I)
SOURCE_YEAR_REGEX=re.compile(r"(?:^|/)([A-Z]{2,8})_(\d{4})_(\d{2})(?:/|$)",re.I)


def identify_source_geometry(manifest:dict):
    """Strict repeated original site/year inputs frozen by source file names."""
    datasets=manifest["AADC"]["original_shapefile_footprints"]
    collected=[]
    for d in datasets:
        if not d.get("uuid") or not d.get("original_manifest_sha256"):
            raise ValueError("SOURCE_STOP V9 dataset UUID/manifest receipt missing")
        for obj in d.get("source_survey_polygon_shapes",[]):
            path=obj["original_path"]
            idmatch=SOURCE_SITE_REGEX.search(path)
            yearmatch=SOURCE_YEAR_REGEX.search(path)
            if not idmatch or not yearmatch:
                continue
            collected.append({
                "site_id":idmatch.group(1),
                "source_group":yearmatch.group(1).upper(),
                "season_start_year":int(yearmatch.group(2)),
                "original_shape_path":path,
                "source_uuid":d["uuid"],
                "source_eds_id":d["eds_id"],
                "source_metadata_id":d["metadata"],
                "publisher_expected_shp_bytes":obj.get("publisher_declared_bytes"),
                "original_dataset_manifest_sha256":d["original_manifest_sha256"],
            })
    cohorts=defaultdict(set)
    for row in collected:
        cohorts[row["site_id"]].add(row["season_start_year"])
    repeated={site for site,years in cohorts.items() if len(years)>=2}
    selected=sorted(
        [r for r in collected if r["site_id"] in repeated],
        key=lambda r:(r["site_id"],r["season_start_year"],r["original_shape_path"])
    )
    k=Counter((r["site_id"],r["season_start_year"]) for r in selected)
    if any(v!=1 for v in k.values()):
        raise ValueError("SOURCE_STOP source site-year has multiple ambiguous polygon versions")
    if len(selected)!=28 or len(repeated)!=13 or len(k)!=28 or {
        r["source_group"] for r in selected}!={"HBW","HBE"}:
        raise ValueError("SAMPLE_STOP V9 source-frozen repeated 13-site, 28-geometry cohort drift")
    if any("2mbuff" not in r["original_shape_path"].lower() for r in selected):
        raise ValueError("SOURCE_STOP repeated source input has noncanonical map-buffer stage")
    if sorted(k for k in cohorts["74585"])!=[2012,2013,2015,2016]:
        raise ValueError("SOURCE_STOP source 4-season reference identity changed")
    return selected,{
        "status":SOURCE_MANIFEST_STATUS,
        "original_AADC_subdataset_count":len(datasets),
        "original_repeated_site_IDs":len(repeated),
        "original_season_site_layer_count":len(selected),
        "original_source_group_count":2,
        "source_groups":sorted({r["source_group"] for r in selected}),
        "original_site_years_from_paths_only":{
            site:sorted(cohorts[site]) for site in sorted(repeated)
        },
        "original_colony_polygon_features_read_before_site_selection":0,
    }


def publisher_source_index(session,uuid:str):
    url=(f"https://{HOST}/eds/api/dataset/{quote(uuid)}"
         "/objects?recursive=true&removeBasePath=true")
    blob,receipt=trusted_response_get(session,url,18_000_000,True)
    objects=json.loads(blob)
    if not isinstance(objects,list):
        raise ValueError("SCHEMA_STOP original AADC source object list not array")
    valid={}
    for obj in objects:
        if not isinstance(obj,dict) or not obj.get("name"):continue
        name=str(obj["name"])
        if name in valid:raise ValueError("SOURCE_STOP duplicated original publisher source object")
        valid[name]=obj
    return valid,receipt["source_sha256"]


def original_file_url(uuid,path):
    return (
        f"https://{HOST}/eds/api/dataset/{quote(uuid)}"
        "/object/download?prefix="+quote(path,safe="")
    )


def retrieve_layer(task:dict,live_manifests:dict):
    uuid=task["source_uuid"]
    stem=task["original_shape_path"][:-4]
    available=live_manifests[uuid]
    paths=[stem+ext for ext in EXTS]
    if any(p not in available for p in paths):
        raise ValueError("SOURCE_STOP source layer missing original SHP+SHX+DBF+PRJ sidecars")
    downloaded={}
    receipts={}
    with requests.Session() as session:
        for path,ext in zip(paths,EXTS):
            meta=available[path]
            declared=meta.get("size")
            if declared is not None and int(declared)>MAX_SOURCE_BYTES:
                raise ValueError("SOURCE_STOP original AADC source component unexpectedly oversized")
            raw,receipt=trusted_response_get(
                session,original_file_url(uuid,path),MAX_SOURCE_BYTES)
            if declared is not None and int(declared)!=len(raw):
                raise ValueError("SOURCE_STOP original AADC bytes disagree with source manifest")
            if not raw:
                raise ValueError("SOURCE_STOP original publisher source component empty")
            downloaded[ext]=raw
            receipts[ext]={"source_bytes":len(raw),"sha256":receipt["source_sha256"]}
    return downloaded,receipts


def _polygonal_parts(geo):
    if geo.is_empty:return None
    if geo.geom_type in ("Polygon","MultiPolygon"):return geo
    groups=[x for x in getattr(geo,"geoms",())
            if x.geom_type in ("Polygon","MultiPolygon") and x.area>0]
    if not groups:return None
    out=unary_union(groups)
    return out if out.geom_type in ("Polygon","MultiPolygon") and not out.is_empty else None


def read_original_geometry(downloaded):
    """Return projected mapped colony polygon and strictly source-only QA."""
    try:
        source_crs=CRS.from_wkt(downloaded[".prj"].decode("utf-8-sig",errors="strict"))
    except Exception as exc:
        raise ValueError("CRS_STOP original AADC polygon projection unreadable") from exc
    if not source_crs.is_projected:
        raise ValueError("CRS_STOP original colony boundary source CRS not projected")
    projection=Transformer.from_crs(source_crs,CRS.from_epsg(3031),always_xy=True)
    shapes=[]
    shape_repair=0
    shape_original_count=0
    with shapefile.Reader(
        shp=io.BytesIO(downloaded[".shp"]),
        shx=io.BytesIO(downloaded[".shx"]),
        dbf=io.BytesIO(downloaded[".dbf"])
    ) as reader:
        dbf_fields=[str(x[0]) for x in reader.fields[1:]]
        if reader.shapeType not in (shapefile.POLYGON,shapefile.POLYGONZ,shapefile.POLYGONM):
            raise ValueError("SCHEMA_STOP original AADC colony layer not polygon")
        if len(reader)==0:
            raise ValueError("SAMPLE_STOP source shape has zero polygon records")
        for shape_record in reader.iterShapeRecords():
            shape_original_count+=1
            src=shape(shape_record.shape.__geo_interface__)
            if src.is_empty:
                raise ValueError("GEOMETRY_STOP empty observed colony polygon")
            if not src.is_valid:
                src=make_valid(src)
                src=_polygonal_parts(src)
                shape_repair+=1
            if src is None or src.is_empty or src.geom_type not in ("Polygon","MultiPolygon") or src.area<=0:
                raise ValueError("GEOMETRY_STOP nonrepairable mapped colony polygon")
            projected=transform(projection.transform,src)
            if not projected.is_valid:
                projected=_polygonal_parts(make_valid(projected))
            if projected is None or projected.is_empty or not projected.is_valid:
                raise ValueError("GEOMETRY_STOP original polygon invalid after projected transform")
            bounds=projected.bounds
            if not all(math.isfinite(v) and abs(v)<1.5e7 for v in bounds):
                raise ValueError("GEOMETRY_STOP impossible Antarctic projected longitude/latitude or extent")
            shapes.append(projected)
    geom=unary_union(shapes)
    if geom.is_empty or not geom.is_valid or not geom.area>0:
        raise ValueError("GEOMETRY_STOP original surveyed polygon union invalid")
    return geom,{
        "original_source_crs":source_crs.to_string(),
        "original_DBf_fields":dbf_fields,
        "original_source_polygon_record_n":shape_original_count,
        "individual_original_polygon_geometries_repaired_by_make_valid":shape_repair,
        "original_union_polygon_area_epsg3031_m2":float(geom.area),
        "original_union_polygon_components_n":len(getattr(geom,"geoms",[geom])),
        "source_polygon_bounds_epsg3031_m":list(map(float,geom.bounds)),
        "original_polygon_union_wkb_SHA256":hashlib.sha256(geom.wkb).hexdigest(),
    }


def compare_pairs(source_layers):
    """Successive available observation dates, never inferred annual zeros."""
    bysite=defaultdict(list)
    for row,geom in source_layers:
        bysite[row["site_id"]].append((row,geom))
    out=[]
    for site in sorted(bysite):
        entries=sorted(bysite[site],key=lambda a:a[0]["season_start_year"])
        for (a,ga),(b,gb) in zip(entries[:-1],entries[1:]):
            if a["source_group"]!=b["source_group"]:
                raise ValueError("SAMPLE_STOP source group changed for original site")
            aarea=float(ga.area);barea=float(gb.area)
            inter=float(ga.intersection(gb).area)
            union=float(ga.union(gb).area)
            if not (union>0 and 0<=inter<=min(aarea,barea)*(1+1e-8)):
                raise ValueError("GEOMETRY_STOP contradictory source breeding polygon overlap")
            # Never call gain biological colonisation; it is observed mapped gain.
            out.append({
                "original_site_id":site,
                "original_source_group":a["source_group"],
                "earlier_season_start_year":a["season_start_year"],
                "later_season_start_year":b["season_start_year"],
                "gap_between_observed_seasons_years":b["season_start_year"]-a["season_start_year"],
                "earlier_mapped_colony_area_m2":aarea,
                "later_mapped_colony_area_m2":barea,
                "later_divided_by_earlier_mapped_area":barea/aarea,
                "log_mapped_colony_area_ratio":math.log(barea/aarea),
                "mapped_polygon_intersection_area_m2":inter,
                "mapped_polygon_union_area_m2":union,
                "mapped_overlap_jaccard":inter/union,
                "earlier_mapped_area_retained_in_later":inter/aarea,
                "later_mapped_area_outside_earlier":max(0,barea-inter)/barea,
                "source_same_polygon_geometric_equals":bool(ga.equals(gb)),
                "original_site_year_polygon_outcomes_are_true_abundance_counts":False,
                "mapped_breeding_gain_is_individual_colonisation":False,
                "observation_footprint_completed_or_verified":False,
            })
    return out


def percentiles(values):
    if not values:return {"n":0,"median":None,"p10":None,"p90":None}
    import numpy as np
    v=np.array(values,dtype=float)
    return {"n":len(v),"median":float(np.median(v)),
            "p10":float(np.percentile(v,10)),"p90":float(np.percentile(v,90))}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v9",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--site-metrics",type=Path,required=True)
    ap.add_argument("--pair-metrics",type=Path,required=True)
    args=ap.parse_args()
    report={"status":"HOLD_AADC_ORIGINAL_VECTOR_V10","original_bird_population_effect_fitted":False}
    try:
        manifest=json.loads(args.v9.read_text(encoding="utf-8"))
        selected,source_contract=identify_source_geometry(manifest)
        uuid_expected={
            x["source_uuid"]:x["original_dataset_manifest_sha256"]
            for x in selected
        }
        live={}
        with requests.Session() as session:
            for uuid,expected_sha in sorted(uuid_expected.items()):
                objects,sha=publisher_source_index(session,uuid)
                if sha!=expected_sha:
                    raise ValueError("SOURCE_STOP AADC original object source manifest version drift")
                live[uuid]=objects
        output=[]
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures={pool.submit(retrieve_layer,task,live):task for task in selected}
            for f in as_completed(futures):
                task=futures[f]
                blobs,sha=f.result()
                geometry,qa=read_original_geometry(blobs)
                output.append(({
                    **task,
                    **qa,
                    "original_publisher_component_SHA256":sha,
                },geometry))
        output.sort(key=lambda t:(t[0]["site_id"],t[0]["season_start_year"]))
        pair_metrics=compare_pairs(output)
        if len(output)!=28 or len(pair_metrics)!=15:
            raise ValueError("SAMPLE_STOP repeated source polygons or observation pairs drift")
        # Do not save raw third-party polygon geometry; compact metrics and receipt only.
        site_rows=[x for x,_geom in output]
        regions={g:sum(r["source_group"]==g for r in site_rows)
                 for g in source_contract["source_groups"]}
        result_by_region={}
        for g in source_contract["source_groups"]:
            data=[p for p in pair_metrics if p["original_source_group"]==g]
            result_by_region[g]={
                "original_source_site_paired_n":len(set(p["original_site_id"] for p in data)),
                "successive_original_site_pair_n":len(data),
                "mapped_breeding_area_ratio":percentiles([p["later_divided_by_earlier_mapped_area"] for p in data]),
                "mapped_polygon_Jaccard":percentiles([p["mapped_overlap_jaccard"] for p in data]),
            }
        report={
            "status":"AADC_REPEATED_ADELIE_ORIGINAL_COLONY_GIS_V10_EXPLORATORY",
            "source_doi":DOI,
            "original_source_manifest":"results/ANTARCTIC_SOURCE_BOUNDARY_MANIFEST_V9.json",
            "source_file_selection_pre_geometry_fixed":source_contract,
            "original_publisher_dataset_object_manifests_checked":len(live),
            "original_source_site_seasons":len(site_rows),
            "original_distinct_repeated_original_site_IDs":len(set(r["site_id"] for r in site_rows)),
            "original_source_breeding_polygon_rows_total":sum(r["original_source_polygon_record_n"] for r in site_rows),
            "original_polygon_features_tagged_repaired":sum(r["individual_original_polygon_geometries_repaired_by_make_valid"] for r in site_rows),
            "successive_source_site_observation_pairs":len(pair_metrics),
            "original_source_group_siteyear_counts":regions,
            "source_region_descriptive_distributions":result_by_region,
            "overall_original_mapped_polygon_Jaccard":percentiles(
                [p["mapped_overlap_jaccard"] for p in pair_metrics]),
            "overall_observed_mapped_area_ratio":percentiles(
                [p["later_divided_by_earlier_mapped_area"] for p in pair_metrics]),
            "observed_geometry_identical_across_years_pairs":sum(
                p["source_same_polygon_geometric_equals"] for p in pair_metrics),
            "original_AADC_presence_absence_or_nonreporting_read":0,
            "original_site_ID_equals_verified_independent_physical_island":False,
            "original_breeding_mapping_footprint_and_precision_verified_same_across_seasons":False,
            "multiple_source_groups_support_Antarctic_wide_macro_causal_generalisation":False,
            "evidence_boundary":"Mapped colony boundary geometry differs in time at original site; digitization, imagery coverage, and physical substrate confound ecological interpretation."
        }
        import csv
        for path,rows in ((args.site_metrics,site_rows),(args.pair_metrics,pair_metrics)):
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open("w",newline="",encoding="utf-8") as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]))
                writer.writeheader();writer.writerows(rows)
        report["derived_site_year_metrics_CSV_SHA256"]=hashlib.sha256(
            args.site_metrics.read_bytes()).hexdigest()
        report["derived_site_pair_metrics_CSV_SHA256"]=hashlib.sha256(
            args.pair_metrics.read_bytes()).hexdigest()
    except Exception as exc:
        report["error_type"]=type(exc).__name__
        report["error"]=str(exc)[:1000]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
