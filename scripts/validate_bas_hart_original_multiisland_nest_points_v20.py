#!/usr/bin/env python3
"""V20 source-verified 10 first-party BAS Hart individual nest point CSVs.

Four 2019–20 site-localities, three provisional physical islands, source-frozen
species roster. No spatial segregation statistic in this source QA stage.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from urllib.parse import urlparse,unquote

import numpy as np
from pyproj import Transformer
import requests

MANIFEST_STATUS="VERIFIED_ORIGINAL_SOURCE_FILES_PUBLISHER_SUMMARY_COUNT_DISCREPANCY"
EXACT_SOURCE_FILES={
 "Ashen_Hills":("ASHE_Adelie_coordinates.csv","ASHE_Chinstrap_coordinates.csv",
                "ASHE_Gentoo_coordinates.csv","ASHE_Macaroni_coordinates.csv"),
 "Bellingshausen":("BELG_Adelie_coordinates.csv","BELG_Chinstrap_coordinates.csv"),
 "Beach_Point":("BEAC_Adelie_coordinates.csv","BEAC_Chinstrap_coordinates.csv"),
 "Hewison_Point":("HEWI_Adelie_coordinates.csv","HEWI_Chinstrap_coordinates.csv"),
}
LOCALITIES=tuple(EXACT_SOURCE_FILES)
SPECIES=("ADELIE","CHINSTRAP","GENTOO","MACARONI")
SOURCE_SPECIES_TO_CODE={name:i for i,name in enumerate(SPECIES)}
SITE_CODE={name:i for i,name in enumerate(LOCALITIES)}
SOURCE_ALLOWED_HOSTS={"ramadda.data.bas.ac.uk","194.66.5.50"}
MAX_SOURCE_BYTES=15_000_000
SOURCE_CRS="EPSG:4326"
UTM_CRS="EPSG:32726"
SITE_GAZETTEER_PARENT={
 "Ashen_Hills":"Saunders_Island",
 "Bellingshausen":"Bellingshausen_Island",
 "Beach_Point":"Thule_Island",
 "Hewison_Point":"Thule_Island",
}


def select_original_files(manifest:dict):
    if manifest.get("status")!=MANIFEST_STATUS:
        raise ValueError("SOURCE_STOP original V16 publisher 164-file roster changed")
    if manifest.get("original_filename_inventory_total")!=164:
        raise ValueError("SOURCE_STOP original archive record count changed")
    files=manifest["original_all_file_metadata_only"]
    if len(files)!=164:
        raise ValueError("SOURCE_STOP original source file manifest incomplete")
    sample=[]
    for locality,names in EXACT_SOURCE_FILES.items():
        for name in names:
            matching=[f for f in files
                      if f["top_level_source_locality_folder"]==locality
                      and f["original_archive_relative_path"]==f"{locality}/coordinates/{name}"
                      and f["original_publisher_file_name"]==name
                      and f["original_source_file_type"]=="csv"]
            if len(matching)!=1:
                raise ValueError("SOURCE_STOP expected original nest file missing or ambiguous: "+locality+"/"+name)
            source=matching[0]
            uri=urlparse(source["source_file_url_https"])
            if uri.scheme!="https" or uri.hostname not in SOURCE_ALLOWED_HOSTS:
                raise ValueError("SOURCE_STOP original BAS publisher HTTPS URL invalid")
            if unquote(uri.path)!=f"/repository/entry/get/{name}":
                raise ValueError("SOURCE_STOP original BAS nesting filename does not match publisher URL")
            label=name.split("_")[1].upper()
            if label not in SPECIES:
                raise ValueError("SOURCE_STOP unexpected taxon in source-frozen 10 original nest files")
            sample.append({**source,"source_original_locality":locality,
                           "taxon":label,"source_dataset_campaign":"2019_2020",
                           "source_named_observation_day_verified":False})
    if len(sample)!=10:
        raise ValueError("SOURCE_STOP original V20 nest source cohort was changed")
    return sample


def download_original_csv(src:dict):
    url=src["source_file_url_https"]
    with requests.Session() as session:
        with session.get(url,timeout=(15,110),stream=True,headers={
            "User-Agent":"mina-BAS-original-nest-point-V20/1.0"}) as response:
            response.raise_for_status()
            final=urlparse(response.url)
            if final.scheme!="https" or final.hostname not in SOURCE_ALLOWED_HOSTS:
                raise ValueError("SOURCE_STOP BAS original nest point redirected outside publisher")
            buff=bytearray()
            for block in response.iter_content(chunk_size=32768):
                buff.extend(block)
                if len(buff)>MAX_SOURCE_BYTES:
                    raise ValueError("SOURCE_STOP source nest point CSV exceeds bounded original size")
    content=bytes(buff)
    if not content or content.lstrip()[:80].lower().startswith((b"<html",b"<!doctype")):
        raise ValueError("SOURCE_STOP BAS original publisher did not serve CSV bytes")
    return content


def source_csv_points(raw:bytes,src:dict):
    try:
        text=raw.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise ValueError("SOURCE_STOP original nest point coordinates not UTF8") from e
    reader=csv.DictReader(io.StringIO(text,newline=""))
    if list(reader.fieldnames or [])!=["nest_number","lat","lon"]:
        raise ValueError("SCHEMA_STOP original publisher nest source header unexpectedly changed")
    original_ids=set()
    coords=[]
    original_total_rows=0
    missing_position_rows=[]
    for i,row in enumerate(reader):
        original_total_rows+=1
        if None in row:
            raise ValueError(f"SCHEMA_STOP source row {i+2} has more values than original three-column header")
        number=str(row.get("nest_number") or "").strip()
        if not number:
            raise ValueError(f"SOURCE_STOP original nest row {i+2} missing unique nest label")
        if number in original_ids:
            raise ValueError(f"SOURCE_STOP original nest row {i+2} duplicate nest_number within file")
        original_ids.add(number)
        lat_str=str(row.get("lat") or "").strip()
        lon_str=str(row.get("lon") or "").strip()
        if not lat_str or not lon_str:
            missing_position_rows.append(i+2)
            continue
        try:
            lat=float(lat_str)
            lon=float(lon_str)
        except (ValueError,TypeError) as e:
            raise ValueError(f"SOURCE_STOP invalid latitude/longitude in original nest row {i+2}") from e
        if not(math.isfinite(lat) and math.isfinite(lon) and -61<=lat<=-54 and -30<=lon<=-24):
            raise ValueError(f"GEOMETRY_STOP original nest row {i+2} outside fixed SSI bounds")
        coords.append((lon,lat))
    missing_fraction=len(missing_position_rows)/original_total_rows if original_total_rows else 1
    if missing_fraction>.01:
        raise ValueError("SOURCE_MISSINGNESS_GATE source coordinate rows with missing original positions exceed 1%"+
                         f" missing={len(missing_position_rows)}, original_rows={original_total_rows}, "+
                         f"fraction={missing_fraction:.6f}, first_missing_source_rows={missing_position_rows[:15]}")
    if not coords:
        raise ValueError("SOURCE_STOP original nest point source empty")
    raw_coords=np.asarray(coords,dtype=float)
    transform=Transformer.from_crs(SOURCE_CRS,UTM_CRS,always_xy=True)
    east,north=transform.transform(raw_coords[:,0],raw_coords[:,1])
    xy=np.column_stack((east,north)).astype(np.float64)
    if not np.all(np.isfinite(xy)):
        raise ValueError("GEOMETRY_STOP original nest source projection invalid")
    if len(xy)!=len(set(map(tuple,xy))):
        # Do not auto-delete/choose duplicated coordinates; audit permits
        # genuine duplicate rounded original points and V21 excludes ties.
        duplicate_n=len(xy)-len(set(map(tuple,xy)))
    else:
        duplicate_n=0
    return xy,{
        "original_row_count":len(xy),
        "original_source_nest_identifier_rows_including_missing_coordinates":original_total_rows,
        "source_rows_with_missing_original_lat_or_lon":len(missing_position_rows),
        "source_missing_original_position_fraction":missing_fraction,
        "first_original_line_numbers_with_missing_position":missing_position_rows[:15],
        "unlocated_source_nests_never_assigned_synthetic_positions":True,
        "unique_original_nest_number_label_count":len(original_ids),
        "source_exact_duplicate_projected_coordinates_within_file_n":duplicate_n,
        "source_original_lon_range":list(map(float,(np.min(raw_coords[:,0]),np.max(raw_coords[:,0])))),
        "source_original_lat_range":list(map(float,(np.min(raw_coords[:,1]),np.max(raw_coords[:,1])))),
        "source_projected_easting_range":list(map(float,(np.min(east),np.max(east)))),
        "source_projected_northing_range":list(map(float,(np.min(north),np.max(north)))),
        "original_source_coordinate_columns":["nest_number","lat","lon"],
        "original_SSI_coord_reference":SOURCE_CRS,
        "source_projected_coordinate_reference":UTM_CRS,
        "source_observation_datetime_from_file_verified":False,
    }


def build_source_points(manifest:dict,ledger:dict):
    files=select_original_files(manifest)
    if ledger.get("status")!="BAS_SOUTH_SANDWICH_ORIGINAL_SOURCE_2019_2020_NEST_LEDGER_V18":
        raise ValueError("SOURCE_STOP original first-party SSI census count receipt changed")
    expected={r["original_survey_locality"]:r["original_reported_species_labelled_nest_cells"]
              for r in ledger["reported_source_count_data_by_original_survey_locality"]}
    results=[]
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures={pool.submit(download_original_csv,file):file for file in files}
        for future in as_completed(futures):
            source=futures[future]
            raw=future.result()
            try:
                xy,qa=source_csv_points(raw,source)
            except Exception as e:
                raise ValueError("SOURCE_FILE_HOLD "+source["original_archive_relative_path"]+" :: "+str(e)) from e
            publisher_count=expected[source["source_original_locality"]][source["taxon"].title()]
            qa.update({
                "source_original_file_path":source["original_archive_relative_path"],
                "source_original_file_id":source["original_publisher_archive_id"],
                "source_original_locality":source["source_original_locality"],
                "source_taxon":source["taxon"],
                "source_original_raw_CSV_sha256":hashlib.sha256(raw).hexdigest(),
                "source_original_raw_CSV_bytes":len(raw),
                "source_root_census_labelled_count_for_same_locality_taxon":publisher_count,
                "source_points_minus_original_reported_labelled_count":(
                    len(xy)-publisher_count if publisher_count is not None else None),
                "source_total_nest_ID_rows_minus_original_reported_labelled_count":(
                    qa["original_source_nest_identifier_rows_including_missing_coordinates"]-publisher_count
                    if publisher_count is not None else None),
                "source_row_count_identical_to_reported_census_taxon":(
                    len(xy)==publisher_count if publisher_count is not None else None)
            })
            results.append((source,xy,qa))
    results.sort(key=lambda z:(SITE_CODE[z[0]["source_original_locality"]],
                               SOURCE_SPECIES_TO_CODE[z[0]["taxon"]]))
    if len(results)!=10:
        raise ValueError("SOURCE_STOP not all fixed original coordinate sources loaded")
    arrays={}
    for locality in LOCALITIES:
        sourceparts=[(src,xy,meta) for src,xy,meta in results
                     if src["source_original_locality"]==locality]
        merged=np.vstack([x[1] for x in sourceparts])
        labels=np.concatenate([
            np.full(len(xy),SOURCE_SPECIES_TO_CODE[src["taxon"]],dtype=np.uint8)
            for src,xy,meta in sourceparts])
        arrays[f"{locality}_xy"]=merged
        arrays[f"{locality}_label"]=labels
    summary={
        "status":"BAS_HART_ORIGINAL_10_SPECIES_NEST_CSV_SOURCE_V20",
        "original_publisher_source_document_doi":"10.5285/28222725-c53d-40f4-9350-49c368899f0b",
        "source_location_to_candidate_physical_island":SITE_GAZETTEER_PARENT,
        "source_2019_2020_campaign":True,
        "individual_original_species_NEST_CSV_source_count":len(results),
        "source_original_locality_count":len(LOCALITIES),
        "candidate_named_physical_island_count":len(set(SITE_GAZETTEER_PARENT.values())),
        "source_nest_point_sum":sum(len(xy) for _,xy,_ in results),
        "source_species_original_file_validation":[z[2] for z in results],
        "source_specimen_lineage":["BAS original on-imagery nest coordinates"] ,
        "original_single_nest_filenames_do_not_encode_precise_acquisition_date":True,
        "source_original_source_archive_csv_count":manifest["original_file_types"]["csv"],
        "source_root_original_total_counts_recoded_as_species_absence":False,
        "mixed_or_unknown_taxon_csv_read_or_imputed":0,
        "original_ZAVO_2022_Chinstrap_coordinate_records_read":0,
        "original_real_point_cloud_cross_taxon_geometry_effect_fit":False,
        "surveyed_absent_habitat_observed":False,
    }
    return arrays,summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v16",type=Path,required=True)
    p.add_argument("--v18",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--point-cache",type=Path,required=True)
    args=p.parse_args()
    report={"status":"HOLD_BAS_ORIGINAL_DIRECT_NEST_CSV_V20","effect_fitted":False}
    try:
        manifest=json.loads(args.v16.read_text(encoding="utf-8"))
        ledger=json.loads(args.v18.read_text(encoding="utf-8"))
        arrays,report=build_source_points(manifest,ledger)
        args.point_cache.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(args.point_cache,**arrays)
        report["derived_source_geography_NPZ_SHA256"]=hashlib.sha256(
            args.point_cache.read_bytes()).hexdigest()
        report["derived_nest_points_NPZ_array_keys"]=sorted(arrays)
    except Exception as e:
        report["error_type"]=type(e).__name__
        report["error"]=str(e)[:1300]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
