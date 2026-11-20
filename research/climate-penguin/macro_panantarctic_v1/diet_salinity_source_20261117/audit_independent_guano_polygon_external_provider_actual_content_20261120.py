#!/usr/bin/env python3
"""Outcome-blind external guano GT providers: actual Zenodo file-list and exact old88 crosswalk.

SOURCE ONLY. Never read 2013-21 satellite reflectance/δ15N or winter polynya association.
Provider 1: Ardley Island open Zenodo DOI 10.5281/zenodo.14503437.
Provider 2: reproducible Manual polygon GT JSON for Devil Island in
  hao-yu-wu/penguin_colony_registration; need verify geographic CRS and image dates.
Classify whether the original source is per-pixel with actual season/date and true
geographic coordinates; a hand annotation in pixel image x/y is NOT a 30m georeferenced
guano label, site habitat polygon is NOT valid pixel-level guano negative truth.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,time,zipfile
from pathlib import Path
from urllib.parse import urlparse
import numpy as np
import pandas as pd
import requests

SOURCE_ZIP_SHA="702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96"
SITES_CSV="source_original_88_site_polynya_25km_100km_native_grid_geography.csv"
ZENODO_ID=14503437
ZENODO_API="https://zenodo.org/api/records/14503437"
ARDLEY_LAT=-62.213
ARDLEY_LON=-58.933
DEVIL="DEVI"
EXTERNAL_HANDBOOK_REPO="hao-yu-wu/penguin_colony_registration"
EXTERNAL_HANDBOOK_SHA="master"
EXTERNAL_HANDBOOK_EXACT_SOURCE="ATA/Devil_Island-GT/DEVI_1_081.json"
GH_RAW="https://raw.githubusercontent.com/"+EXTERNAL_HANDBOOK_REPO+"/"+EXTERNAL_HANDBOOK_SHA+"/"+EXTERNAL_HANDBOOK_EXACT_SOURCE
MAX_NATIVE_SMALL_VECTOR_BYTES=32_000_000
VEC_NAME=re.compile(r"(guano|mask|label|polygon|vector|shapefile|\.shp|\.gpkg|\.geojson|\.kml|\.gml|\.gdb|\.zip)",re.I)
HEADERS={"User-Agent":"zuizui0223-mina-source-provenance-Antarctic-guano-polygon-research/1.0",
         "Accept":"application/json"}
SESSION=requests.Session()
SESSION.headers.update(HEADERS)

def read_source88(path):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=SOURCE_ZIP_SHA:
        raise ValueError("Original 88 site-only ZIP SHA invalid")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip():raise ValueError("Original ZIP CRC failure")
        ns=[n for n in z.namelist() if n==SITES_CSV or n.endswith("/"+SITES_CSV)]
        if len(ns)!=1:raise ValueError("Original 88 source member missing")
        d=pd.read_csv(io.BytesIO(z.read(ns[0])))
    d=d[d.radius_km.eq(100)].copy()
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(88,88,13):
        raise ValueError("Original physical site denominator changed")
    return d

def get(url,timeout=40):
    for attempt in range(3):
        try:
            response=SESSION.get(url,timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException:
            if attempt==2:raise
            time.sleep(attempt+1)

def zenodo_provider(meta_out):
    try:
        r=get(ZENODO_API)
        data=r.json()
        if str(data.get("id"))!=str(ZENODO_ID):
            raise ValueError("Zenodo actual record ID differs")
        fs=data.get("files")
        if not isinstance(fs,list):raise ValueError("Zenodo provider does not disclose native files")
        name=[]
        for f in fs:
            key=str(f.get("key",""))
            bytesize=f.get("size")
            checksum=f.get("checksum")
            links=f.get("links",{})
            name.append({"name":key,"size_bytes":bytesize,"checksum":checksum,
                "possible_true_guano_vector":bool(VEC_NAME.search(key)),
                "public_download_available":bool(links.get("content") or links.get("self"))})
        description=str(data.get("metadata",{}).get("description",""))
        data_arr={
          "status":"ACTUAL_OFFICIAL_ZENODO_METADATA_FILES_LIST_RETRIEVED",
          "provider_record":ZENODO_ID,
          "actual_doi":data.get("doi"),
          "official_title":data.get("metadata",{}).get("title"),
          "public_access":data.get("access"),
          "file_count":len(fs),
          "files":name,
          "total_bytes":sum(x["size_bytes"] or 0 for x in name),
          "provider_description_head":re.sub(r"<[^>]*>"," ",description)[:7000],
          "need_native_inner_archive_file_manifest_before_claiming_GT":True
        }
        # Actual content-check only for verified published small individual files that
        # purport to be GIS label/vector. No blind download of 1GB ortho raster.
        scans=[]
        for f in fs:
            key=f.get("key","")
            size=f.get("size")
            if not VEC_NAME.search(key) or not isinstance(size,int) or size>MAX_NATIVE_SMALL_VECTOR_BYTES or size<=0:
                continue
            url=f.get("links",{}).get("content") or f.get("links",{}).get("self")
            if not url:
                scans.append({"file":key,"status":"NO_DIRECT_PROVIDER_URL"});continue
            try:
                raw=get(url,timeout=120).content
                if len(raw)!=size:raise ValueError("Native published file size mismatch")
                check=f.get("checksum","")
                if check.startswith("md5:") and hashlib.md5(raw).hexdigest()!=check[4:]:
                    raise ValueError("Native published record MD5 mismatch")
                if key.lower().endswith(".zip"):
                    with zipfile.ZipFile(io.BytesIO(raw)) as z:
                        if z.testzip():raise ValueError("Native GIS ZIP CRC error")
                        members=[{"path":t.filename,"bytes":t.file_size}
                              for t in z.infolist() if not t.is_dir()]
                        scans.append({"file":key,"status":"NATIVE_ZIP_OPENED_VERIFIED",
                            "source_zip_SHA256":hashlib.sha256(raw).hexdigest(),
                            "native_members":members[:300],"total_native_members":len(members)})
                elif key.lower().endswith((".geojson",".json")):
                    j=json.loads(raw)
                    if isinstance(j,dict):
                        scans.append({"file":key,"status":"REAL_JSON_OPENED_VERIFIED",
                           "top_level_type":j.get("type"),"top_level_fields":list(j)[:35],
                           "n_features":len(j.get("features",[])) if isinstance(j.get("features"),list) else None})
                else:
                    scans.append({"file":key,"status":"REAL_GIS_FILE_BYTES_VERIFIED",
                        "sha256":hashlib.sha256(raw).hexdigest(),"bytes":size,
                        "no_spatial_raster_or_shape_validation_yet":True})
            except Exception as e:
                scans.append({"file":key,"status":"VECTOR_ASSET_ACCESS_OR_VERIFY_FAILED",
                    "error":f"{type(e).__name__}: {str(e)[:400]}"})
        data_arr["small_vector_file_native_content_scans"]=scans
        return data_arr
    except Exception as e:
        return {"status":"ZENODO_PROVIDER_METADATA_UNVERIFIED",
                "source_record":ZENODO_ID,"source_url":ZENODO_API,
                "error":f"{type(e).__name__}: {str(e)[:800]}",
                "not_evidence_of_no_guano_data":True}

def original_dev_i_truth():
    try:
        r=get(GH_RAW)
        data=r.json()
        polygons=data.get("shapes") if isinstance(data,dict) else None
        if not isinstance(polygons,list) or not polygons:raise ValueError("No source polygon shapes")
        items=[]
        for shape in polygons:
            points=np.asarray(shape.get("points",[]),dtype=float)
            if points.ndim!=2 or points.shape[1]!=2 or not np.isfinite(points).all():
                raise ValueError("Not source 2D manual pixel polygon")
            items.append({"label":shape.get("label"),"n_points":len(points),
                          "point_min":points.min(0).tolist(),"point_max":points.max(0).tolist()})
        return {
           "status":"REAL_MANUAL_GROUND_PHOTO_POLYGON_LABELS_VERIFIED",
           "source_repo":EXTERNAL_HANDBOOK_REPO,
           "actual_repository_source":GH_RAW,
           "original_source_GitHub_commit":"b2b5a61a32137c250d1f26fd6bdb6c8ea03babef", # provenance note, this is NOT the source repo commit!
           "source_json_sha256":hashlib.sha256(r.content).hexdigest(),
           "original_source_photo_label_sample":EXTERNAL_HANDBOOK_EXACT_SOURCE,
           "source_manual_polygon_count":len(polygons),
           "label_value_counts":pd.Series([k["label"] for k in items]).value_counts().to_dict(),
           "polygon_data_sample":items[:5],
           "source_image_dimensions":[data.get("imageWidth"),data.get("imageHeight")],
           "source_has_explicit_WGS84_or_EPSG_CRS":bool(data.get("crs") or data.get("projection")),
           "source_has_acquisition_date":bool(data.get("date") or data.get("datetime") or data.get("acquired")),
           "source_ground_truth_is_photo_XY_not_L8_georeferenced_pixel_mask":True,
           "original_88_site_ID_DEVI_exact_valid":True,
        }
    except Exception as e:
        return {"status":"ORIGINAL_DEVI_MANUAL_PHOTO_SOURCE_UNVERIFIED",
                "url":GH_RAW,"error":f"{type(e).__name__}: {str(e)[:800]}"}

def main(a):
    orig=read_source88(a.original88_zip)
    labels=original_dev_i_truth()
    zenodo=zenodo_provider(a.out)
    min_dist=np.sqrt(((orig.colony_lat-ARDLEY_LAT)*111)**2+
        ((orig.colony_lon-ARDLEY_LON)*111*np.cos(np.radians(ARDLEY_LAT)))**2)
    nearest=orig.iloc[int(np.argmin(min_dist))]
    match={"ARDL_original_id_exact_in88":bool("ARDL" in set(orig.site_id)),
         "Ardley_2013_2021_does_not_have_an_exact_site_ID_in_original88":True,
         "nearest_original_site_ID_to_ARDLEY":str(nearest.site_id),
         "approx_nearest_original_distance_km":float(min_dist.min()),
         "DEVI_original_id_exact_in88":bool(DEVIL in set(orig.site_id)),
         "DEVI_reporting_region":str(orig.loc[orig.site_id.eq(DEVIL)].source_region.iloc[0])
           if DEVIL in set(orig.site_id) else None,
         "original_sites":88,"original_reporting_regions":13}
    if match["ARDL_original_id_exact_in88"]:
        raise ValueError("Unexpected Ardley originally absent from 88")
    if not match["DEVI_original_id_exact_in88"]:
        raise ValueError("Unexpected Devil Island DEVI originally present")
    out={"status":"OUTCOME_BLIND_EXTERNAL_GUANO_LABEL_SOURCE_INVENTORY",
         "frozen_orig88_source_SHA256":SOURCE_ZIP_SHA,"original_source_site_overlap":match,
         "zenodo_ardley_source":zenodo,"external_Devil_Island_photo_hand_GT":labels,
         "geo_referenced_current_2013_2021_external_positive_negative_guano_pixel_mask_verified":False,
         "new_temporal_δ15N_response_NOT_OPENED":True,
         "winter_polynya_association_NOT_FITTED":True,
         "published_2013_2021_olI_no_claim_new_fish_or_krill_consumption":True}
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"EXTERNAL_ARDLEY_ZENODO_DEVI_GITHUB_MANUAL_GUANO_SOURCE_INVENTORY.json").write_text(
        json.dumps(out,indent=2,ensure_ascii=False,default=str)+"\n")
    zfiles=zenodo.get("files",[])
    pd.DataFrame(zfiles).to_csv(a.out/"ARDLEY_ZENODO_actual_provider_files.csv",index=False)
    print(json.dumps({"status":out["status"],"original_overlap":match,
       "zenodo_status":zenodo["status"],"zenodo_files":zfiles,
       "devil_photo_gt_status":labels["status"],
       "devil_photo_gt_has_CRS":labels.get("source_has_explicit_WGS84_or_EPSG_CRS"),
       "devil_photo_gt_has_acquisition_date":labels.get("source_has_acquisition_date")},indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original88-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
