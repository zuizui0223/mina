#!/usr/bin/env python3
"""V4 SCAR ADD high-resolution coastline cross-check of 719 APBP sites.

Authoritative polygon source snapshots are 2026, not 1970s-2022 breeding
habitat. Output is purely geography/position-uncertainty QA; no ecological
outcomes are calculated and no missing site is treated as continental land.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
import math
from pathlib import Path,PurePosixPath
import tempfile
import zipfile

from pyproj import CRS
from shapely.geometry import Point,shape
from shapely.strtree import STRtree
import shapefile

from link_apbp_to_add_island_rock_v3 import (
    COAST_ZIP, COAST_DOI, APBP_SHA, NEAR_M, DRIFT_STOP_M,
    event_sites, fetch_original, fetch_bas, unpack_shapefile,
    mapped_features, unique_match,
)

HIGH_DOI="10.5285/13c4d2f1-8903-4d7f-8977-592121975554"
HIGH_URL=(
    "https://ramadda.data.bas.ac.uk/repository/entry/get/"
    "add_coastline_high_res_polygon_v7_12.shp.zip?"
    "entryid=synth%3A13c4d2f1-8903-4d7f-8977-592121975554"
    "%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfcG9seWdvbl92N18xMi5zaHAuemlw"
)
MEDIUM_SHA="b0172d698436f871f49339cea5c7155e3d98648360521cc4bbc44a026c0edc38"
HIGH_ZIP_LIMIT=90_000_000
HIGH_UNZIPPED_LIMIT=1_000_000_000
PRECISE_CUTOFF=250


def original_highres_shapes(blob,directory,sites):
    if not blob.startswith(b"PK") or len(blob)>HIGH_ZIP_LIMIT:
        raise ValueError("SOURCE_STOP publisher high-res ZIP missing/oversized")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        entries=z.infolist()
        if len(entries)>60 or sum(e.file_size for e in entries)>HIGH_UNZIPPED_LIMIT or z.testzip() is not None:
            raise ValueError("SOURCE_STOP unexpectedly large/invalid high-res GIS ZIP")
        directory.mkdir(parents=True,exist_ok=True)
        for member in entries:
            rel=PurePosixPath(member.filename)
            if rel.is_absolute() or ".." in rel.parts or len(rel.parts)>5:
                raise ValueError("SOURCE_STOP unsafe source ZIP path")
            if member.is_dir():continue
            target=directory.joinpath(*rel.parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(member))
    candidates=list(directory.rglob("*.shp"))
    if len(candidates)!=1:
        raise ValueError("SOURCE_STOP original high-res ZIP must have one SHP")
    src=candidates[0]
    prj=src.with_suffix(".prj")
    if not prj.is_file() or not CRS.from_wkt(prj.read_text(encoding="utf-8",errors="ignore")).equals(CRS.from_epsg(3031)):
        raise ValueError("SOURCE_STOP high-res original projection is not EPSG:3031")
    reader=shapefile.Reader(str(src))
    fields=[i[0] for i in reader.fields[1:]]
    if "surface" not in [s.lower() for s in fields]:
        raise ValueError("SOURCE_STOP original GIS lacks land/ice-shelf indicator")
    all_surfaces=Counter()
    shapes=[]
    invalid_source_count=0
    invalid_near_site_count=0
    coords=[(e["x"],e["y"]) for records in sites.values() for e in records[:1]]
    for index, sr in enumerate(reader.iterShapeRecords()):
        attributes={fields[i].lower():sr.record[i] for i in range(len(fields))}
        surface=str(attributes.get("surface","")).strip().lower()
        all_surfaces[surface]+=1
        if surface!="land":
            continue
        try:
            geom=shape(sr.shape.__geo_interface__)
        except Exception:
            geom=None
        if geom is None or geom.is_empty or not geom.is_valid or geom.geom_type not in ("Polygon","MultiPolygon"):
            invalid_source_count+=1
            bbox=getattr(sr.shape,"bbox",None)
            if bbox and any(
                bbox[0]-NEAR_M<=x<=bbox[2]+NEAR_M and
                bbox[1]-NEAR_M<=y<=bbox[3]+NEAR_M
                for x,y in coords
            ):
                invalid_near_site_count+=1
            continue
        shapes.append((index,geom,attributes))
    if not shapes or invalid_near_site_count:
        raise ValueError("GEOMETRY_STOP high-res invalid/empty polygon near original APBP sites")
    return shapes,{
        "polygon_attributes":fields,
        "original_surface_counts":dict(all_surfaces),
        "valid_source_land_features":len(shapes),
        "invalid_original_land_polygons_far_from_sites":invalid_source_count,
    }


def original_uncertainty(records):
    values=[e.get("uncertainty_m") for e in records
            if e.get("uncertainty_m") is not None and
            math.isfinite(e["uncertainty_m"])]
    return max(values) if values else None


def location_quality(point,geom,match_type,uncertainty):
    if match_type!="EXACT_ONE_LAND_POLYGON":
        return "HOLD_NOT_EXACT_LAND_POINT"
    if uncertainty is None or uncertainty<=0:
        return "HOLD_PRECISION_MISSING"
    # Require all plausible location points to remain within ONE continuous
    # land polygon, not just the source georeference center.
    if geom.covers(point.buffer(float(uncertainty))):
        return "ISLAND_OR_CONTINENT_ASSIGNMENT_STABLE_UNDER_REPORTED_POSITION_RADIUS"
    return "HOLD_POSITION_RADIUS_CROSSES_LAND_BOUNDARY"


def classify_site(point,records,features,tree,largest):
    drift=max(Point(e["x"],e["y"]).distance(point) for e in records)
    uncertainty=original_uncertainty(records)
    if drift>DRIFT_STOP_M:
        return {
            "status":"HOLD_SOURCE_COORDINATE_DRIFT",
            "provisional_landtype":"HOLD_UNMATCHED",
            "land_id":None,"land_area_km2":None,
            "location_precision_status":"HOLD_SOURCE_COORDINATE_DRIFT",
            "boundary_clearance_m":None,
            "uncertainty_m":uncertainty,"drift_m":drift
        }
    match,status=unique_match(point,features,tree)
    if match is None:
        return {"status":status,"provisional_landtype":"HOLD_UNMATCHED",
                "land_id":None,"land_area_km2":None,
                "location_precision_status":"HOLD_NOT_ASSIGNED",
                "boundary_clearance_m":None,
                "uncertainty_m":uncertainty,"drift_m":drift}
    fid,poly,attributes=features[match]
    typ=("CONTINENT_LARGEST_POLYGON_PROXY" if match==largest
         else "ISLAND_SEPARATE_LAND_POLYGON_PROXY")
    quality=location_quality(point,poly,status,uncertainty)
    clear=float(point.distance(poly.boundary)) if poly.covers(point) else 0.
    return {
        "status":status,"provisional_landtype":typ,
        "land_id":fid,"land_area_km2":poly.area/1e6,
        "location_precision_status":quality,
        "boundary_clearance_m":clear,
        "uncertainty_m":uncertainty,"drift_m":drift
    }


def compare_site_maps(sites,medium,high):
    def prepare(features):
        geoms=[r[1] for r in features]
        tree=STRtree(geoms)
        largest=max(range(len(features)),key=lambda i:geoms[i].area)
        return tree,largest
    midtree,midbig=prepare(medium)
    hitree,hibig=prepare(high)
    rows=[]
    for site,events in sorted(sites.items()):
        p=Point(events[0]["x"],events[0]["y"])
        mid=classify_site(p,events,medium,midtree,midbig)
        hi=classify_site(p,events,high,hitree,hibig)
        rows.append({
            "source_locationID":site,
            "source_event_records":len(events),
            "source_locality":events[0].get("locality"),
            "source_islandGroup_NOT_ISLAND_ID":events[0].get("source_islandGroup"),
            "original_APBP_max_uncertainty_m":hi["uncertainty_m"],
            "within_site_max_drift_m":round(hi["drift_m"],3),
            "medium_class":mid["provisional_landtype"],
            "medium_status":mid["status"],
            "high_class":hi["provisional_landtype"],
            "high_status":hi["status"],
            "high_original_feature_id":hi["land_id"],
            "high_land_area_km2":round(hi["land_area_km2"],6) if hi["land_area_km2"] is not None else None,
            "high_location_confidence":hi["location_precision_status"],
            "high_boundary_clearance_m":round(hi["boundary_clearance_m"],3) if hi["boundary_clearance_m"] is not None else None,
            "formerly_unmatched_and_rescued":(
                mid["provisional_landtype"]=="HOLD_UNMATCHED" and
                hi["provisional_landtype"]!="HOLD_UNMATCHED"),
            "medium_to_high_class_disagreement":(
                mid["provisional_landtype"]!="HOLD_UNMATCHED" and
                hi["provisional_landtype"]!="HOLD_UNMATCHED" and
                mid["provisional_landtype"]!=hi["provisional_landtype"]),
        })
    return rows


def summarise(rows,medium_hash,high_hash,medium_meta,high_meta):
    mid=Counter(r["medium_class"] for r in rows)
    hi=Counter(r["high_class"] for r in rows)
    rescued=[r for r in rows if r["formerly_unmatched_and_rescued"]]
    src_prec=[r["original_APBP_max_uncertainty_m"] for r in rows]
    return {
        "status":"V4_HIGHRES_ISLAND_RESCUE_AND_SOURCE_COORDINATE_QA_ONLY",
        "no_ecological_effects_fitted":True,
        "APBP_source_sha256":APBP_SHA,
        "medium_coast_2026": {"doi":COAST_DOI,"sha256":medium_hash,"original_QA":medium_meta},
        "high_coast_2026": {"doi":HIGH_DOI,"sha256":high_hash,"original_QA":high_meta},
        "n_source_locationIDs":len(rows),
        "medium_source_geography":dict(mid),
        "high_source_geography":dict(hi),
        "n_medium_unmatched":sum(r["medium_class"]=="HOLD_UNMATCHED" for r in rows),
        "n_formerly_unmatched_rescued":len(rescued),
        "rescued_highland_class":dict(Counter(r["high_class"] for r in rescued)),
        "n_newly_unmatched_when_switching_to_high":sum(
            r["medium_class"]!="HOLD_UNMATCHED" and
            r["high_class"]=="HOLD_UNMATCHED" for r in rows),
        "n_medium_vs_high_land_class_conflict":sum(r["medium_to_high_class_disagreement"] for r in rows),
        "original_coordinate_precision": {
            "site_ids_missing_uncertainty":sum(x is None for x in src_prec),
            "site_ids_with_uncertainty_le250m":sum(x is not None and x<=250 for x in src_prec),
            "site_ids_uncertainty_250_to_1000m":sum(x is not None and 250<x<=1000 for x in src_prec),
            "site_ids_uncertainty_over_1000m":sum(x is not None and x>1000 for x in src_prec),
            "site_ids_uncertainty_over_2000m":sum(x is not None and x>2000 for x in src_prec),
            "original_median_reported_uncertainty_m":(
                sorted(x for x in src_prec if x is not None)[len([x for x in src_prec if x is not None])//2]
                if any(x is not None for x in src_prec) else None),
        },
        "high_polygon_match_precision":dict(Counter(r["high_location_confidence"] for r in rows)),
        "high_land_features_with_site":len({
            r["high_original_feature_id"] for r in rows if r["high_original_feature_id"] is not None}),
        "warning":"Highres modern mapped land ≠ historical yearly nesting capacity, and original APBP coordinate uncertainty can exceed entire small island.",
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-json",required=True)
    ap.add_argument("--out-csv",required=True)
    args=ap.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix="apbp-highres-v4-") as tmp:
            base=Path(tmp)
            sites=event_sites(fetch_original())
            med=fetch_bas(COAST_ZIP)
            if hashlib.sha256(med).hexdigest()!=MEDIUM_SHA:
                raise ValueError("SOURCE_VERSION_STOP medium original coast SHA changed")
            # V3 network helper is bounded to 30MB; authentic high-res needs 90 MB.
            import link_apbp_to_add_island_rock_v3 as v3
            previous=v3.MAX_BYTES
            try:
                v3.MAX_BYTES=HIGH_ZIP_LIMIT
                high=fetch_bas(HIGH_URL)
            finally:
                v3.MAX_BYTES=previous
            med_path=unpack_shapefile(med,base/"med")
            med_features,med_meta=mapped_features(med_path,require_surface=True)
            high_features,high_meta=original_highres_shapes(high,base/"high",sites)
            rows=compare_site_maps(sites,med_features,high_features)
        result=summarise(rows,hashlib.sha256(med).hexdigest(),
                         hashlib.sha256(high).hexdigest(),med_meta,high_meta)
        target=Path(args.out_csv)
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open("w",encoding="utf-8",newline="") as file:
            writer=csv.DictWriter(file,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        result["source_matched_site_CSV_SHA256"]=hashlib.sha256(target.read_bytes()).hexdigest()
    except Exception as exc:
        result={"status":"HOLD_ORIGINAL_HIGHRES_COAST_OR_GEOREF",
                "error_type":type(exc).__name__,
                "error":str(exc)[:550],
                "no_ecological_effects_fitted":True}
    output=Path(args.out_json)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
