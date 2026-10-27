#!/usr/bin/env python3
"""V36 primary V32 full-resolution GSHHG original geometry source-only gate.

Read authentic GSHHG 2.3.7 L1 full resolution, join original JNCC site
COORDINATES and original RSPB 2014 island point source on strict same land
polygon only, then original Stanbury lowid predator label. Never open JNCC
bird count magnitudes, E, or infer surveyed absence from Stanbury 0.
"""
from __future__ import annotations
import argparse,hashlib,io,json,math,zipfile
from pathlib import Path,PurePosixPath
from urllib.parse import urlparse
import requests, shapefile
from shapely.geometry import shape,box
from shapely.ops import transform
from pyproj import Transformer

import audit_jncc_two_censuses_source_v28 as v28
import audit_jncc_comparable_site_panels_v29 as v29
import model_jncc_component_concentration_v30 as v30
import audit_jncc_naturalearth_landmass_v31 as geo
import model_jncc_predator_reported_niche_v34 as pred
import audit_jncc_predator_island_source_v33 as source
import audit_jncc_predator_ne_land_v35 as v35

SOURCE_URL="https://github.com/GenericMappingTools/gshhg-gmt/releases/download/2.3.7/gshhg-shp-2.3.7.zip"
SOURCE_SHA256="8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41"
STEM="GSHHS_f_L1"
MAX_DOWNLOAD_BYTES=200_000_000
MAX_SELECTED_UNCOMPRESSED_BYTES=700_000_000
ROI=(-13.5,48.0,3.5,63.5)
MAX_LARGE_LAND_GLOBAL_KM2=50_000

def download_gshhg() -> bytes:
    blocks=[];total=0
    with requests.get(SOURCE_URL,timeout=(15,120),stream=True,
                      headers={"User-Agent":"mina-jncc-full-resolution-original-gshhg-v36/1.0"}) as r:
        r.raise_for_status()
        parsed=urlparse(r.url)
        if parsed.scheme!="https" or not(
            parsed.hostname=="github.com"
            or parsed.hostname.endswith(".githubusercontent.com")
            or parsed.hostname.endswith(".github.com")
        ):
            raise ValueError("GSHHG_SOURCE_REDIRECT_HOST_NOT_GITHUB")
        for block in r.iter_content(chunk_size=1024*1024):
            if block:
                total+=len(block)
                if total>MAX_DOWNLOAD_BYTES:raise ValueError("GSHHG_DOWNLOAD_LIMIT")
                blocks.append(block)
    data=b"".join(blocks)
    if hashlib.sha256(data).hexdigest()!=SOURCE_SHA256:
        raise ValueError("GSHHG_SHA256_NOT_PINNED")
    return data

def shapefile_source(raw:bytes):
    if not raw.startswith(b"PK"):raise ValueError("GSHHG_NOT_ZIP")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        files={}
        for f in z.infolist():
            p=PurePosixPath(f.filename)
            if p.is_absolute() or ".." in p.parts:
                raise ValueError("GSHHG_UNSAFE_PATH")
        for extension in (".shp",".shx",".dbf"):
            names=[name for name in z.namelist()
                   if PurePosixPath(name).name==STEM+extension]
            if len(names)!=1:raise ValueError("GSHHG_ORIGINAL_F_L1_FILE_MISSING "+extension)
            obj=z.getinfo(names[0])
            if obj.file_size>MAX_SELECTED_UNCOMPRESSED_BYTES:
                raise ValueError("GSHHG_SELECTED_SOURCE_TOO_LARGE "+extension)
            files[extension]=z.read(names[0])
    return shapefile.Reader(shp=io.BytesIO(files[".shp"]),
                            shx=io.BytesIO(files[".shx"]),
                            dbf=io.BytesIO(files[".dbf"]))

def precise_UK_geography(reader):
    tr=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    fn=tr.transform
    shapes=[];areas=[]
    region=box(*ROI)
    total=0; large_clipped=0;invalid=0
    source_area_present=0
    for shaperecord in reader.iterShapeRecords(bbox=ROI):
        total+=1
        native=shaperecord.shape
        rec=shaperecord.record.as_dict()
        geom=shape(native.__geo_interface__)
        if geom.is_empty:
            invalid+=1;continue
        if not geom.is_valid:
            geom=geom.buffer(0)
        if geom.is_empty or not geom.intersects(region):
            continue
        km = rec.get("area") or rec.get("AREA") or rec.get("area_full")
        try:km=float(km)
        except (ValueError,TypeError):km=float("nan")
        if math.isfinite(km) and km>0:source_area_present+=1
        # Efficiently clip original continental landmass to study envelope.
        # Only classify as LARGE when its original, global source area is large;
        # never estimate a continent area from the clipped local rectangle.
        if math.isfinite(km) and km>=MAX_LARGE_LAND_GLOBAL_KM2:
            geom=geom.intersection(region)
            large_clipped+=1
        projected=transform(fn,geom)
        if projected.is_empty or not projected.is_valid:
            projected=projected.buffer(0)
        if projected.is_empty:invalid+=1;continue
        area = km if math.isfinite(km) and km>0 else projected.area/1e6
        shapes.append(projected)
        areas.append(area)
    if len(shapes)<50:
        raise ValueError("GSHHG_ROI_UNEXPECTEDLY_FEW_POLYGONS")
    return shapes,areas,{
      "global_source_resolution":"GSHHS_f_L1",
      "ROI_original_WGS84":ROI,
      "source_shape_records_intersecting_ROI":total,
      "source_original_area_field_positive":source_area_present,
      "matched_physical_land_polygons":len(shapes),
      "large_global_original_polygon_geometry_clipped_ONLY_for_point_query":large_clipped,
      "invalid_or_empty_source_features":invalid,
      "source_full_resolution_polygon_is_not_true_JNCC_nest_point_GPS":True,
    }

def source_only():
    raw,srcmeta=v28.download_original()
    if hashlib.sha256(raw).hexdigest()!=v29.ORIGINAL_SHA:
        raise ValueError("JNCC_SOURCE_CHANGED")
    parents,qa=v30.extract_structural(v29.original_rows(raw))
    if not qa["pre_count_structural_gate_pass"] or len(parents)!=1483:
        raise ValueError("JNCC_STRUCTURAL_GATE_CHANGED")
    graw=download_gshhg()
    shapes,area,geography=precise_UK_geography(shapefile_source(graw))
    rspb=pred.source_islands()
    if len(rspb)!=9688:raise ValueError("RSPB_FRAME_CHANGED")
    rlocations={id:(site["lat"],site["lon"]) for id,site in rspb.items()}
    rlabels,_=geo.attach_points(shapes,area,rlocations)
    strict,bridge=v35.strict_RSPB_landmass_bridge(rlabels,area)
    esm_raw=source.bounded_get(source.SUPPLEMENTS["ESM5"],source.MAX_SUPP_BYTES)
    esm,sourceqa=pred.load_original_ESM5(esm_raw)
    if set(esm)!=set(rspb):
        raise ValueError("ORIGINAL_LOWID_JOIN_CHANGED")
    sites={}
    for parent,children in parents.items():
        for r,_ in children:
            key=(r["species"],r["country"],r["master"],r["unit"],r["site_id"])
            coordinate=(r["lat"],r["lon"])
            if key in sites and sites[key]!=coordinate:
                raise ValueError("ORIGINAL_SITE_COORDINATE_INCONSISTENT")
            sites[key]=coordinate
    states,_=geo.attach_points(shapes,area,sites)
    sample=v35.panel_support(parents,states,strict,esm)
    return {
      "status":"JNCC_V36_FULL_GSHHG_SOURCE_ONLY_TEST_COMPLETED",
      "source_SHA256_GSHHG_f_2_3_7":SOURCE_SHA256,
      "source_SHA256_Stanbury":sourceqa["sha256"],
      "original_JNCC_SHA256":v29.ORIGINAL_SHA,
      "GSHHG_source_geography":geography,
      "RSPB_unique_lowid_source_island_to_polygon":bridge,
      "original_JNCC_site_geometry_cohort":sample,
      "scientific_decision":(
        "SOURCE_SUPPORT_POSSIBLE_BUT_EPOCH_STATUS_UNVERIFIED_HOLD"
        if sample["predeclared_within_parent_mixed_island_support_pass"]
        else "STOP_JNCC_WITHIN_PARENT_MAMMALIAN_REFUGE_GEO_SUPPORT_V36"
      ),
      "JNCC_seabird_count_magnitudes_opened":0,
      "JNCC_predator_population_effect_fitted":False,
      "source_2014_status_is_not_dated_both_JNCC_census_epochs":True,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    try:
        result=source_only()
    except Exception as exc:
        result={
           "status":"SOURCE_OR_GEOMETRY_HOLD",
           "error":type(exc).__name__+": "+str(exc)[:500],
           "JNCC_seabird_count_magnitudes_opened":0,
           "JNCC_predator_population_effect_fitted":False,
        }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]!="JNCC_V36_FULL_GSHHG_SOURCE_ONLY_TEST_COMPLETED":
        raise SystemExit(2)

if __name__=="__main__":main()
