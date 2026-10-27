#!/usr/bin/env python3
"""V52 original BAS/SCAR 2020 sub-Antarctic coast SOURCE ONLY.

After global GSHHG v51 failed exact Saunders/Bellingshausen/Thule polygon
support 1/0/0, this DOI-specific coastline's original geographic domain is
50-60 S and South Sandwich from SGGIS. No penguin guild outcomes,
concentration, access-score model, flight or mammal ecological effect opened.
Save original source SHA, native EPSG and strict all-nest land containment.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs,urlparse

import numpy as np
import requests
import shapefile
from pyproj import CRS,Transformer
from shapely import contains_xy
from shapely.geometry import Point, shape
from shapely.ops import transform

import analyze_paper2_three_island_penguin_coast_access_v51 as v51

DOI="10.5285/c1d83502-8799-4e3c-bdca-21db6a4405d4"
URL=("https://ramadda.data.bas.ac.uk/repository/entry/get/"
     "sub_antarctic_coastline_high_res_polygon_v1.0.zip"
     "?entryid=synth%3Ac1d83502-8799-4e3c-bdca-21db6a4405d4%3A"
     "L3N1Yl9hbnRhcmN0aWNfY29hc3RsaW5lX2hpZ2hfcmVzX3BvbHlnb25fdjEuMC56aXA%3D")
HOST="ramadda.data.bas.ac.uk"
ALLOWED_HOSTS={HOST,"194.66.5.50"}
MAX_BYTES=8_000_000
MAX_UNCOMPRESSED=30_000_000
NATIVE_CRS_PREFERRED=3031
MIN_INSIDE=.95
MIN_AREA_KM2=.02
MAX_AREA_KM2=1000


def official_source_url_verified(url):
    u=urlparse(url)
    if (u.scheme!="https" or u.hostname!=HOST or
        not u.path.endswith("/sub_antarctic_coastline_high_res_polygon_v1.0.zip")):
        raise ValueError("V52_SOURCE_NOT_ORIGINAL_BAS_URL")
    p=parse_qs(u.query)
    if len(p.get("entryid",[]))!=1 or p["entryid"][0]!=(
        "synth:c1d83502-8799-4e3c-bdca-21db6a4405d4:"
        "L3N1Yl9hbnRhcmN0aWNfY29hc3RsaW5lX2hpZ2hfcmVzX3BvbHlnb25fdjEuMC56aXA="):
        raise ValueError("V52_SOURCE_ENTRY_ID_NOT_FROZEN")
    return True


def original_download():
    official_source_url_verified(URL)
    with requests.get(URL,timeout=(18,80),allow_redirects=True,stream=True,
                      headers={"User-Agent":"mina-original-BAS-Subantarctic-coast-V52-source-only/1.0"}) as response:
        response.raise_for_status()
        parsed=urlparse(response.url)
        if parsed.scheme!="https" or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError("V52_SOURCE_CROSS_DOMAIN_REDIRECT_DENIED")
        chunks=[];size=0
        for piece in response.iter_content(chunk_size=65536):
            size+=len(piece)
            if size>MAX_BYTES:
                raise ValueError("V52_SOURCE_PUBLISHER_ZIP_SIZE_EXCEEDS_8MB")
            chunks.append(piece)
    data=b"".join(chunks)
    if len(data)<100 or not data.startswith(b"PK"):
        raise ValueError("V52_PUBLISHER_SHAPEFILE_ARCHIVE_NOT_ZIP")
    return data


def original_native_land_geometry(data:bytes,original_medians):
    """Return source-original feature IDs and candidate original coast shapes.

    No biological species information used; original_medians are pooled
    source-species blind, known site-to-island mapping fixed before opening
    source geometry.
    """
    source_zip_SHA=hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for f in z.infolist():
            p=PurePosixPath(f.filename)
            if p.is_absolute() or ".." in p.parts or f.file_size>MAX_UNCOMPRESSED:
                raise ValueError("V52_UNSAFE_OR_OVERSIZE_GEO_ORIGINAL_ARCHIVE_ENTRY")
        names=z.namelist()
        shps=[n for n in names if n.lower().endswith(".shp")]
        if len(shps)!=1:
            raise ValueError("V52_ORIGINAL_POLYGON_SOURCE_NOT_ONE_SHAPEFILE")
        shp=shps[0];stem=shp[:-4]
        members={}
        for ext in (".shp",".shx",".dbf",".prj"):
            actual=[n for n in names if n.casefold()==(stem+ext).casefold()]
            if len(actual)!=1:
                raise ValueError("V52_SOURCE_GIS_SIDECAR_MISSING:"+ext)
            members[ext]=z.read(actual[0])
    try:
        orig_crs=CRS.from_wkt(members[".prj"].decode("utf-8-sig"))
    except Exception as exc:
        raise ValueError("V52_ORIGINAL_BAS_CRS_UNREADABLE") from exc
    if orig_crs.to_epsg()!=NATIVE_CRS_PREFERRED:
        raise ValueError("V52_ORIGINAL_BAS_CRS_NOT_CATALOGUE_EPSG3031")
    from_utm=Transformer.from_crs(32726,orig_crs,always_xy=True)
    to_utm=Transformer.from_crs(orig_crs,32726,always_xy=True)
    median_points={}
    for island,xy in original_medians.items():
        a,b=from_utm.transform(*xy)
        median_points[island]=Point(a,b)
    found={name:[] for name in original_medians}
    reader=shapefile.Reader(shp=io.BytesIO(members[".shp"]),
                            shx=io.BytesIO(members[".shx"]),
                            dbf=io.BytesIO(members[".dbf"]))
    if reader.shapeType not in (shapefile.POLYGON,shapefile.POLYGONZ):
        raise ValueError("V52_SHAPEFILE_NOT_ORIGINAL_LAND_POLYGON")
    total=0;candidate=0
    for i,sr in enumerate(reader.iterShapeRecords()):
        total+=1
        original_shp=sr.shape
        bb=getattr(original_shp,"bbox",None)
        if not bb:continue
        maybe=[name for name,p in median_points.items()
               if bb[0]<=p.x<=bb[2] and bb[1]<=p.y<=bb[3]]
        if not maybe:continue
        candidate+=1
        native=shape(original_shp.__geo_interface__)
        if not native.is_valid or native.is_empty:
            # Do not "repair" original polygon to force an island assignment.
            raise ValueError("V52_SOURCE_CANDIDATE_POLYGON_INVALID")
        sid=sr.record.as_dict().get("id")
        if sid is None:sid=sr.record.as_dict().get("ID")
        if sid is None:sid="original_v1_file_shape_index_"+str(i)
        for name in maybe:
            if native.contains(median_points[name]):
                found[name].append({
                    "id":str(sid), "source_file_shape_index":i,"geometry":native,
                })
    ids={k:len(v) for k,v in found.items()}
    cohort={
        "original_public_BAS_Scar_coastline_version":"1.0",
        "original_public_BAS_subantarctic_coastline_DOI":DOI,
        "original_source_SGGIS_South_Sandwich_lineage":True,
        "original_source_zip_SHA256":source_zip_SHA,
        "original_source_zip_bytes":len(data),
        "original_source_native_crs_EPSG":orig_crs.to_epsg(),
        "original_total_shapefile_polygons":total,
        "original_polygons_with_original_bbox_covering_a_site_median":candidate,
        "original_three_island_strict_polygon_counts":ids,
        "geometry_original_not_adjusted_to_nest_points":True,
    }
    usable={}
    shapes={}
    for name,matches in found.items():
        if len(matches)!=1:
            continue
        source=matches[0]
        proj=transform(to_utm.transform,source["geometry"])
        area_km2=float(proj.area/1e6)
        usable[name]={
            "original_publisher_source_shape_id":source["id"],
            "original_shape_index":source["source_file_shape_index"],
            "original_island_projected_area_km2":area_km2,
        }
        shapes[name]=proj
    cohort["provisionally_strict_source_coast_shapes"]=usable
    cohort["all_three_candidates_unique_containing_polygons"]=all(
        len(v)==1 for v in found.values())
    cohort["distinct_physical_publisher_polygon_ids"]=len({
        v["original_shape_index"] for v in usable.values()})
    return shapes,cohort


def source_sample_without_species_outcomes(source_data,shape):
    isles=sorted(set(v51.PARENT.values()))
    outcome={}
    for name,island in v51.PARENT.items():
        obj=source_data[name]
        xy=obj["xy"]
        if island not in shape:
            outcome[name]={
                "source_nest_coordinates_after_duplicate_exclusion":len(xy),
                "original_STRICT_island_land_polygon_matched":False,
                "original_inside_land_n":None,
                "fraction_source_nests_inside":None,
            }
            continue
        g=shape[island]
        inside=contains_xy(g,xy[:,0],xy[:,1])
        outcome[name]={
            "source_nest_coordinates_after_duplicate_exclusion":len(xy),
            "original_STRICT_island_land_polygon_matched":True,
            "original_inside_land_n":int(np.sum(inside)),
            "original_outside_land_n":int(len(inside)-np.sum(inside)),
            "fraction_source_nests_inside":float(np.mean(inside)),
        }
    return outcome


def science_gates(original,cont):
    unique=bool(original["all_three_candidates_unique_containing_polygons"])
    three=original["distinct_physical_publisher_polygon_ids"]==3
    areas=all(MIN_AREA_KM2<=v["original_island_projected_area_km2"]<=MAX_AREA_KM2
              for v in original["provisionally_strict_source_coast_shapes"].values())
    over=all(v["original_STRICT_island_land_polygon_matched"] and
             v["fraction_source_nests_inside"]>=MIN_INSIDE
             for v in cont.values())
    return {
      "three_strict_original_BAS_land_polygon_source_coverage":unique and three,
      "three_original_land_polygon_areas_source_plausible":areas,
      "per_original_locality_all_species_blind_inside_ge95_percent":over,
      "source_only_Paper2_Geography_gate_pass":bool(unique and three and areas and over),
      "new_species_by_coast_distance_or_terrain_effect_opened":False,
      "no_animal_nest_locations_changed_to_fit_reference_shoreline":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v26-npz",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    r={
       "status":"V52_ORIGINAL_BAS_SUBANTARCTIC_GEOGRAPHY_ACCESS_HOLD",
       "source_contract":"contracts/PAPER2_THREE_ISLAND_BAS_SUBANTARCTIC_COAST_V52_SOURCE.md",
       "date":"2026-10-28",
       "original_nest_V26_source_SHA":v51.SOURCE_NPZ_SHA,
       "no_penguin_species_coast_distances_or_flying_mammal_effect_fitted":True
    }
    try:
        obj,info=v51.read_original_npz(args.v26_npz)
        r["original_BAS_nesting_source"]=info
        medians={}
        for island in sorted(set(v51.PARENT.values())):
            arr=np.vstack([v["xy"] for k,v in obj.items() if v51.PARENT[k]==island])
            medians[island]=tuple(np.median(arr,axis=0))
        source=original_download()
        polygons,meta=original_native_land_geometry(source,medians)
        r["independently_versioned_original_BAS_subantarctic_coast"]=meta
        r["species_blind_original_nest_to_source_polygons"]=source_sample_without_species_outcomes(obj,polygons)
        r["original_pre_effect_support_gates"]=science_gates(
           meta,r["species_blind_original_nest_to_source_polygons"])
        r["status"]=(
          "V52_BAS_OFFICIAL_3_ISLAND_EXACT_COAST_SOURCE_PASS_READY_TO_PIN_SHA"
          if r["original_pre_effect_support_gates"]["source_only_Paper2_Geography_gate_pass"]
          else "STOP_V52_BAS_OFFICIAL_SUBANTARCTIC_GEOGRAPHY_SUPPORT"
        )
    except Exception as exc:
        r["status"]="V52_BAS_PUBLISHER_SOURCE_FETCH_OR_SCHEMA_HOLD"
        r["source_error"]=type(exc).__name__+": "+str(exc)[:650]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(r,ensure_ascii=False))
    if r["status"]=="V52_BAS_PUBLISHER_SOURCE_FETCH_OR_SCHEMA_HOLD":
        raise SystemExit(2)

if __name__=="__main__":
    main()
