#!/usr/bin/env python3
"""Paper 2 V56: first-party AADC Macquarie bird-guild GIS SOURCE-ONLY intake.

2023/24 indicative penguin+volant points, legacy hand-digitized flying
polygons, older penguin polygon collection and independent 1:50k coast GIS.
Read exact anonymous public first-party AADC publication downloads only.
Original file SHA256, physical row/shape count & field HEADER NAMES ONLY.
NEVER fit bird flight/rat effects, never publish source coordinates or rows.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse,urljoin
import zipfile

import requests
import shapefile
from pyproj import CRS

ORIGINAL={
  "Macquarie_2023_24_both_bird_guilds":{
    "download_url":"https://data.aad.gov.au/eds/6113/download",
    "source_doi":"10.26179/98ra-0751",
    "original_grain":"INDICATIVE_POINTS_REFERENCING_DIFFERENT_2023_2024_SPECIES_CENSUSES",
    "source_metadata":"https://data.aad.gov.au/metadata/records/macca_wildlife_gis",
  },
  "Macquarie_2000_flying_bird_colony_GIS":{
    "download_url":"https://data.aad.gov.au/eds/1379/download",
    "source_doi":"10.26179/5c494b686370e",
    "original_grain":"2000_1_TO_50000_HAND_SKETCH_DIGITIZED_FLYING_COLONY_POLYGONS",
    "source_metadata":"https://data.aad.gov.au/metadata/records/macca_flyingbirds_gis",
  },
  "Macquarie_historical_penguin_colony_GIS":{
    "download_url":"https://data.aad.gov.au/eds/4192/download",
    "source_doi":"NO_DOI_LISTED_IN_PUBLISHER_METADATA",
    "original_grain":"1979_ONWARDS_HISTORIC_EPOCH_PENGUIN_COLONY_POLYGONS",
    "source_metadata":"https://data.aad.gov.au/metadata/records/macca_penguins_gis",
  },
  "Macquarie_original_1_to_50k_coast_GIS":{
    "download_url":"https://data.aad.gov.au/eds/2812/download",
    "source_doi":"NO_DOI_LISTED_IN_PUBLISHER_METADATA",
    "original_grain":"INDEPENDENT_STATIC_1_TO_50000_COAST_ISLAND_GEOMETRY",
    "source_metadata":"https://data.aad.gov.au/metadata/records/macca_coast_ambis_gis",
  },
}
ALLOWED_DOMAIN_SUFFIXES=("aad.gov.au","antarctica.gov.au")
MAX_REDIRECTS=4
MAX_SOURCE_BYTES=40_000_000
MAX_ZIP_FILES=500
MAX_ZIP_UNCOMPRESSED=120_000_000
MAX_ZIP_ONE=60_000_000
MAX_FIELDS=250
ORIGINAL_LICENCE="CC BY 4.0"


def official_source_host(url):
    p=urlparse(url)
    if p.scheme!="https" or not p.hostname:
        return False
    host=p.hostname.casefold().rstrip(".")
    return any(host==d or host.endswith("."+d) for d in ALLOWED_DOMAIN_SUFFIXES)


def get_public_source_bytes(session,url):
    if not official_source_host(url):
        raise ValueError("AADC_SOURCE_NOT_OFFICIAL_HTTPS")
    last_url=url
    for hop in range(MAX_REDIRECTS+1):
        if not official_source_host(last_url):
            raise ValueError("AADC_PUBLISHER_REDIRECT_NOT_FIRST_PARTY")
        with session.get(
            last_url,headers={"User-Agent":"mina-Paper2-Macquarie-original-AADC-GIS-V56/1.0"},
            stream=True,timeout=(12,45),allow_redirects=False
        ) as resp:
            if resp.status_code in (301,302,303,307,308):
                redirect=resp.headers.get("Location")
                if not redirect or hop==MAX_REDIRECTS:
                    raise ValueError("AADC_PUBLISHER_MISSING_OR_EXCESSIVE_REDIRECTS")
                new_url=urljoin(last_url,redirect)
                if not official_source_host(new_url):
                    raise ValueError("AADC_PUBLISHER_REDIRECT_NOT_FIRST_PARTY")
                last_url=new_url
                continue
            if resp.status_code in (401,403):
                raise ValueError("AADC_ANONYMOUS_DOWNLOAD_ACCESS_NOT_AUTHORIZED_"+str(resp.status_code))
            resp.raise_for_status()
            if resp.status_code!=200:
                raise ValueError("AADC_PUBLISHER_FILE_NOT_HTTP_200")
            original_length=resp.headers.get("Content-Length")
            if original_length and int(original_length)>MAX_SOURCE_BYTES:
                raise ValueError("AADC_ORIGINAL_SOURCE_DECLARED_TOO_LARGE")
            chunks=[];n=0
            for block in resp.iter_content(chunk_size=65536):
                if not block:continue
                n+=len(block)
                if n>MAX_SOURCE_BYTES:
                    raise ValueError("AADC_ORIGINAL_SOURCE_EXCEEDS_40MB")
                chunks.append(block)
            data=b"".join(chunks)
            if not data or data[:256].lstrip().lower().startswith(
                (b"<html",b"<!doctype",b"<head",b"<body")):
                raise ValueError("AADC_SOURCE_NOT_ACTUAL_PUBLIC_FILE")
            return data,{
                "first_party_final_hostname":urlparse(last_url).hostname,
                "official_source_redirect_steps":hop,
                "source_http_status":200,
                "original_size_bytes":len(data),
                "original_SHA256":hashlib.sha256(data).hexdigest(),
                "publisher_content_type":str(resp.headers.get("Content-Type",""))[:110],
            }
    raise ValueError("AADC_SOURCE_REDIRECT_LOOP")


def original_source_shapefile_metadata(shp,shx,dbf,prj):
    # Source shape metadata only. Do not iterate native records or coordinates.
    reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf))
    try:
        fields=[str(f[0])[:80] for f in reader.fields
                if f[0]!="DeletionFlag"]
        if len(fields)>MAX_FIELDS:
            raise ValueError("AADC_GIS_DB_FIELD_COUNT_TOO_HIGH")
        record_count=len(reader)
        shape_type=int(reader.shapeType)
    finally:
        reader.close()
    source_epsg=None
    if prj:
        try:
            source_epsg=CRS.from_wkt(prj.decode("utf-8-sig","replace")).to_epsg()
        except Exception:
            # Missing/obsolete projection means source-position audit must
            # STOP; do not silently assume WGS84/UTM from island bounding box.
            source_epsg=None
    return {
        "original_source_record_count":record_count,
        "original_shape_type_code":shape_type,
        "original_source_DBF_field_names_only":fields,
        "original_PRJ_EPSG_if_unambiguous":source_epsg,
        "original_site_names_and_coordinates_published":False,
        "original_precision_or_target_species_survey_effort_estimated":False,
    }


def original_zip_structure(data):
    if not data.startswith(b"PK"):
        raise ValueError("AADC_EXPECTED_SOURCE_ZIP_SIGNATURE")
    results=[]
    with zipfile.ZipFile(io.BytesIO(data)) as arc:
        files=[f for f in arc.infolist() if not f.is_dir()]
        if len(files)>MAX_ZIP_FILES or sum(f.file_size for f in files)>MAX_ZIP_UNCOMPRESSED:
            raise ValueError("AADC_ORIGINAL_ZIP_UNBOUNDED")
        filenames={f.filename:f for f in files}
        for f in files:
            p=PurePosixPath(f.filename)
            if (p.is_absolute() or ".." in p.parts or
                f.file_size>MAX_ZIP_ONE or f.flag_bits&1):
                raise ValueError("AADC_ORIGINAL_ZIP_UNSAFE_OR_ENCRYPTED")
        extent=Counter(PurePosixPath(f.filename).suffix.lower() or "NO_EXTENSION"
                       for f in files)
        shapefiles=[f for f in files if f.filename.lower().endswith(".shp")]
        for item in shapefiles:
            stem=item.filename[:-4]
            siblings={}
            for ext in (".shp",".shx",".dbf",".prj"):
                match=[name for name in filenames if name.casefold()==(stem+ext).casefold()]
                if len(match)==1:siblings[ext]=arc.read(match[0])
            if not all(x in siblings for x in (".shp",".shx",".dbf")):
                results.append({"layer_no":len(results)+1,"status":"GEORECORD_MISSING_SHP_SHX_OR_DBF"})
                continue
            if not siblings[".shp"].startswith(bytes.fromhex("0000270a")):
                raise ValueError("ORIGINAL_SHP_MAGIC_INVALID")
            desc=original_source_shapefile_metadata(
                siblings[".shp"],siblings[".shx"],siblings[".dbf"],siblings.get(".prj"))
            results.append({"layer_no":len(results)+1,"status":"ORIGINAL_GIS_HEADER_READ",
                           **desc})
    return {
        "source_file_format":"ZIP_ARCHIVE",
        "original_zip_entries_total":len(files),
        "source_original_extension_counts":dict(extent),
        "native_shapefile_layers_n":len(shapefiles),
        "original_readable_shapefile_header_layers_n":sum(
            x["status"]=="ORIGINAL_GIS_HEADER_READ" for x in results),
        "native_source_layer_structures_without_raw_rows":results,
        "original_archive_site_or_species_feature_values_not_republished":True
    }


def source_file_structure(raw):
    if raw.startswith(b"PK"):
        return original_zip_structure(raw)
    if raw.startswith(b"SQLite format 3"):
        return {"source_file_format":"GPKG_SQLITE","source_deep_feature_schema_verified":False}
    if raw[:4]==bytes.fromhex("0000270a"):
        return {"source_file_format":"SHP_ALONE","native_related_DBF_AND_PRJ_NOT_VERIFIED":True}
    if raw[:2] in (b"II",b"MM"):
        return {"source_file_format":"TIFF_OR_BIFF_UNKNOWN","native_GIS_SCHEMA_NOT_VERIFIED":True}
    body=raw[:512].lstrip()
    if body.startswith(b"{"):
        try:
            meta=json.loads(raw)
            if meta.get("type")=="FeatureCollection" and isinstance(meta.get("features"),list):
                features=meta["features"]
                field=set()
                for f in features:
                    field.update(f.get("properties",{}).keys())
                return {
                    "source_file_format":"GEOJSON",
                    "original_source_features_n":len(features),
                    "original_source_property_FIELD_NAMES_ONLY":sorted(str(x)[:80] for x in field)[:MAX_FIELDS],
                    "original_coordinates_and_values_exported":False
                }
        except (UnicodeDecodeError,ValueError,TypeError):
            pass
    if not b"\x00" in body and (b"," in body or b"\t" in body):
        head=raw.decode("utf-8-sig","replace").splitlines()[0]
        try:fields=next(csv.reader(io.StringIO(head)))
        except csv.Error:fields=[]
        if fields and len(fields)<=MAX_FIELDS:
            return {
                "source_file_format":"TABULAR_TEXT_HEADER_ONLY",
                "original_safe_column_count":len(fields),
                "original_raw_rows_not_opened":True,
            }
    return {"source_file_format":"UNRECOGNIZED_NATIVE_SOURCE","no_bird_values_or_coordinates_read":True}


def audit():
    output={
        "status":"V56_NEW_AADC_ORIGINAL_SOURCE_ACCESS_QUALITY_AUDITED",
        "original_four_AADC_source_datasets_exact":list(ORIGINAL),
        "original_source_public_reuse_licence":ORIGINAL_LICENCE,
        "date":"2026-10-29",
        "contract":"contracts/PAPER2_MACQUARIE_ORIGINAL_FLIGHT_PENGUIN_GIS_V56_SOURCE.md",
        "scientific_scope":"Source-only spatial-temporal comparability of flightless penguin, flying seabird, original coastline, historical rat eradication one-island records",
        "original_animal_population_or_predator_guild_effect_fitted":False,
        "source_island_independent_ecological_replicates":1,
        "no_original_record_level_names_nest_GPS_or_animal_values_published":True,
    }
    def each(item):
        tag,meta=item
        info={
            "source_metadata_record_url":meta["source_metadata"],
            "source_original_data_doi":meta["source_doi"],
            "source_original_observational_grain":meta["original_grain"],
            "source_original_primary_AADC_download_url":meta["download_url"],
            "status":"SOURCE_CONTENT_NOT_VERIFIED_HOLD",
        }
        try:
            with requests.Session() as session:
                raw,receipt=get_public_source_bytes(session,meta["download_url"])
            info.update(receipt)
            info["source_structure"]=source_file_structure(raw)
            info["status"]="AADC_ORIGINAL_PUBLIC_SOURCE_HEADER_VERIFIED"
        except Exception as e:
            info["error"]=type(e).__name__+": "+str(e)[:420]
        return tag,info
    with ThreadPoolExecutor(max_workers=2) as pool:
        output["datasets"]=dict(pool.map(each,ORIGINAL.items()))
    status={k:v["status"] for k,v in output["datasets"].items()}
    sufficient=(
        status["Macquarie_2023_24_both_bird_guilds"]=="AADC_ORIGINAL_PUBLIC_SOURCE_HEADER_VERIFIED"
        and status["Macquarie_original_1_to_50k_coast_GIS"]=="AADC_ORIGINAL_PUBLIC_SOURCE_HEADER_VERIFIED"
    )
    output["G1_modern_penguin_volant_original_with_coast_source_access_pass"]=sufficient
    output["G2_same_2023_24_island_breeding_field_effort_and_exact_nest_position_verified"]=False
    output["G3_field_mammal_presence_and_negative_identified"]=False
    output["G4_multiple_independent_real_physical_islands_in_this_source"]=False
    output["full_asymmetric_access_predator_by_flight_interaction_identified"]=False
    output["source_access_qa_decision"]=(
        "SOURCE_HEADERS_AVAILABLE_FOR_SEPARATE_FIELD_GRAIN_VALIDATION"
        if sufficient else "SOURCE_ACCESS_OR_NATIVE_GIS_COHORT_HOLD"
    )
    return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    d=audit()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":d["status"],"source_access_qa_decision":d["source_access_qa_decision"],
        "source_files":{k:{"status":v["status"],"sha":v.get("original_SHA256"),
                           "bytes":v.get("original_size_bytes"),
                           "source_format":v.get("source_structure",{}).get("source_file_format"),
                           "native_layer_count":v.get("source_structure",{}).get("native_shapefile_layers_n"),
                           "error":v.get("error")}
                       for k,v in d["datasets"].items()},
        "G1":d["G1_modern_penguin_volant_original_with_coast_source_access_pass"],
    },ensure_ascii=False))

if __name__=="__main__":
    main()
