#!/usr/bin/env python3
"""V19 original BAS Hart South Sandwich 2019-20 individual nest CSV schema.

Data source: publisher's original V16 164-file archive object list.
Reads header line ONLY from likely nest-coordinate CSVs; never nest values,
count rows or orthotiff payload. Source site/season lineage kept literal.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests

SOURCE_ARCHIVE_STATUS="VERIFIED_ORIGINAL_SOURCE_FILES_PUBLISHER_SUMMARY_COUNT_DISCREPANCY"
SOURCE_LOCALITIES={
    "Ashen_Hills","Beach_Point","Bellingshausen","Candlemas_Island",
    "Herd_Point","Hewison_Point","Zavodovski"
}
BAS_HOSTS={"ramadda.data.bas.ac.uk","194.66.5.50"}
YEAR_RX=re.compile(r"(?<!\d)(19\d\d|20\d\d)(?!\d)")
SPECIES_NAMES=("adelie","chinstrap","gentoo","macaroni")
MAX_FIRST_LINE=15000
MAX_WORKERS=6


def classify_filename(meta:dict):
    rel=meta["original_archive_relative_path"]
    base=rel.split("/")[-1]
    stem=base.lower()
    locality=meta["top_level_source_locality_folder"]
    if locality not in SOURCE_LOCALITIES and rel!="SSI_count_results.csv":
        raise ValueError("SOURCE_STOP unpublished original source locality")
    years=YEAR_RX.findall(base)
    if len(set(years))>1:
        raise ValueError("SOURCE_STOP contradictory years in original nest source name")
    if rel=="SSI_count_results.csv":kind="ROOT_COUNTS_NOT_NEST_POINT"
    elif base.lower().endswith(".csv") and "outline" in stem:
        kind="SOURCE_COLONY_OUTLINE_VERTEX_NOT_NEST"
    elif base.lower().endswith(".csv") and ("coord" in stem):
        kind="POTENTIAL_INDIVIDUAL_NEST_COORDINATE_CSV"
    elif base.lower().endswith(".csv"):
        kind="OTHER_ORIGINAL_CSV_NOT_ASSUMED_NEST"
    else:
        kind="NON_CSV_SOURCE"
    labels=[x for x in SPECIES_NAMES if x in stem]
    if "mixed" in stem:
        group="MIXED_UNASSIGNED"
    elif "unknown" in stem or "pengiun" in stem:
        group="UNKNOWN_UNASSIGNED"
    elif len(labels)==1:
        group=labels[0].upper()
    elif labels:
        group="CONFLICTING_SPECIES_FILENAME"
    else:
        group="NO_SPECIES_FILENAME"
    year=int(years[0]) if years else None
    return {
        "original_source_archive_path":rel,
        "original_source_file_id":meta["original_publisher_archive_id"],
        "official_publisher_https_URL":meta["source_file_url_https"],
        "source_archive_locality":locality,
        "file_source_type":kind,
        "original_filename_reported_year":year,
        "species_source_filename_label":group,
        "2022_Zavodovski_chinstrap_not_2020":bool(
            locality=="Zavodovski" and year==2022 and group=="CHINSTRAP"),
        "source_nested_archive_file_data_rows_read":0,
    }


def bounded_original_csv_header(meta):
    info=classify_filename(meta)
    if info["file_source_type"]!="POTENTIAL_INDIVIDUAL_NEST_COORDINATE_CSV":
        return info
    src=info["official_publisher_https_URL"]
    uri=urlparse(src)
    if uri.scheme!="https" or uri.hostname not in BAS_HOSTS:
        raise ValueError("SOURCE_STOP nest CSV source URL not original publisher HTTPS")
    with requests.Session() as s:
        with s.get(src,timeout=(20,60),stream=True,headers={
            "User-Agent":"mina-original-bas-Hart-nest-coordinate-header-only-v19/1.0"
        }) as r:
            r.raise_for_status()
            actual=urlparse(r.url)
            if actual.scheme!="https" or actual.hostname not in BAS_HOSTS:
                raise ValueError("SOURCE_STOP original nest point file redirected outside BAS")
            raw=r.raw.readline(MAX_FIRST_LINE+1)
    if not raw or len(raw)>MAX_FIRST_LINE or b"\n" not in raw:
        raise ValueError("SCHEMA_STOP source nest-point CSV first line absent or oversized")
    if raw.lstrip().lower().startswith((b"<html",b"<!doctype")):
        raise ValueError("SOURCE_STOP publisher served HTML instead of original nest points")
    try:
        line=raw.decode("utf-8-sig").rstrip("\r\n")
        header=next(csv.reader(io.StringIO(line)))
    except Exception as e:
        raise ValueError("SCHEMA_STOP original nest-point source header cannot be decoded") from e
    fields=[re.sub(r"[^a-z0-9]+","_",x.strip().lower()).strip("_") for x in header]
    xy=(bool(set(fields)&{"lat","latitude","gps_lat","lat_dd"}) and
        bool(set(fields)&{"lon","longitude","long","lng","gps_lon","lon_dd"}))
    return {
        **info,
        "original_first_line_SHA256":hashlib.sha256(raw).hexdigest(),
        "source_original_header_columns":header,
        "original_csv_has_unambiguous_coordinate_column_pair":xy,
        "source_csv_has_nest_label_column":any(x in fields for x in ("nest_number","nest_id","nest_no","point_id")),
        "observation_row_count_verified":False,
        "animal_coordinate_values_read":0,
    }


def source_first_headers(manifest):
    if manifest.get("status")!=SOURCE_ARCHIVE_STATUS:
        raise ValueError("SOURCE_STOP V16 official original live archive source status not verified")
    files=manifest["original_all_file_metadata_only"]
    if len(files)!=164:
        raise ValueError("SOURCE_STOP original publisher South Sandwich archive file count changed")
    origcsv=[x for x in files if x["original_source_file_type"]=="csv"]
    if len(origcsv)!=32:
        raise ValueError("SOURCE_STOP original publisher 32 CSV file registry changed")
    out=[]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        fut={pool.submit(bounded_original_csv_header,r):r for r in origcsv}
        for f in as_completed(fut):
            source=fut[f]
            try:
                out.append(f.result())
            except Exception as e:
                part=classify_filename(source)
                part["source_header_status"]="HOLD_HEADER_OR_SOURCE_ACCESS"
                part["error_type"]=type(e).__name__
                part["error"]=str(e)[:500]
                out.append(part)
    out.sort(key=lambda x:x["original_source_archive_path"])
    classes=Counter(z["file_source_type"] for z in out)
    candidates=[z for z in out
                if z["file_source_type"]=="POTENTIAL_INDIVIDUAL_NEST_COORDINATE_CSV"]
    ready=[z for z in candidates
           if z.get("original_csv_has_unambiguous_coordinate_column_pair")]
    eligible=[z for z in ready
              if z["original_filename_reported_year"] in (2019,2020)
              and z["species_source_filename_label"] in tuple(x.upper() for x in SPECIES_NAMES)]
    bysite=defaultdict(list)
    for row in eligible:
        bysite[row["source_archive_locality"]].append(row["species_source_filename_label"])
    return {
        "status":"BAS_HART_2019_20_PUBLISHER_ORIGINAL_COORDINATE_CSV_HEADER_V19",
        "original_source_2026_current_archive_file_n":len(files),
        "original_csv_file_n":len(out),
        "source_original_csv_classes":dict(sorted(classes.items())),
        "original_potential_nest_coordinate_csv_n":len(candidates),
        "original_possible_coordinate_header_pair_n":len(ready),
        "simultaneous_2019_20_direct_filename_species_header_n":len(eligible),
        "source_locality_direct_taxa_filename_candidate":{
            k:sorted(v) for k,v in sorted(bysite.items())
        },
        "original_source_csvs_by_file_path":out,
        "original_individual_nest_coordinate_records_opened":0,
        "source_2022_Zavodovski_chinstrap_is_2019_20_contemporaneous":False,
        "other_original_CSV_not_all_assumed_individual_nests":True,
        "source_original_habitat_or_nest_coordinates_used_to_fit_any_effect":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    r={"status":"HOLD_BAS_HART_POINT_HEADER_V19"}
    try:
        source=json.loads(args.manifest.read_text(encoding="utf-8"))
        r=source_first_headers(source)
    except Exception as e:
        r["error_type"]=type(e).__name__
        r["error"]=str(e)[:700]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        k:v for k,v in r.items() if k!="original_source_csvs_by_file_path"},ensure_ascii=False))
    if r["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
