#!/usr/bin/env python3
"""V33 first-party Antarctic Site Inventory 1994–2013 original census audit.

Publisher original CSV: 1124 source records, 113 site IDs, seven seabird taxa,
explicit nest-vs-chick Counted_object, accuracy rank and original Source.
This is a source feasibility and genealogy QA, not an island effect fit.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
from urllib.parse import urlparse

import requests

PUBLISHER_URL="https://esapubs.org/archive/ecol/E094/243/Antarctic_Site_Inventory_census_data_1994_2012.csv"
EXPECTED_MD5="00871bd47b6ec30cda68d1506120bfb3"
EXPECTED_ROWS=1124
EXPECTED_SITE_COUNT=113
EXPECTED_SPECIES=("ADPE","CHPE","GEPE","MCPE","BESH","KEGU","SOGP")
EXPECTED_REGIONS=("CW","EI","NE","NW","SH","SO","SW")
MAX_BYTES=2_000_000
REQ_FIELDS=("Site_ID","Region","Site_name","Latitude","Longitude",
            "Species","Date","Season","Count","Counted_object","Accuracy",
            "Notes","Source")
PENGUINS={"ADPE","CHPE","GEPE","MCPE"}
FLYING={"BESH","KEGU","SOGP"}


def normalize(k):
    return re.sub(r"[^a-z0-9]","",str(k).casefold())


def download_publisher_csv():
    with requests.Session() as session:
        with session.get(PUBLISHER_URL,timeout=(20,90),stream=True,
             allow_redirects=True,
             headers={"User-Agent":"mina-Antarctic-Site-Inventory-original-2013-publisher-census-source-v33/1.0"}) as resp:
            for h in [*resp.history,resp]:
                u=urlparse(h.url)
                if u.scheme!="https" or u.hostname not in ("esapubs.org","www.esapubs.org"):
                    raise ValueError("SOURCE_STOP ASI census download left original publisher HTTPS")
            resp.raise_for_status()
            data=bytearray()
            for chunk in resp.iter_content(chunk_size=16384):
                data.extend(chunk)
                if len(data)>MAX_BYTES:
                    raise ValueError("SOURCE_STOP original ASI CSV larger than 2 MB")
    raw=bytes(data)
    if not raw or raw.lstrip()[:100].lower().startswith((b"<html",b"<!doctype")):
        raise ValueError("SOURCE_STOP ASI original source is empty or HTML interstitial")
    if hashlib.md5(raw).hexdigest()!=EXPECTED_MD5:
        raise ValueError("SOURCE_STOP publisher original ASI 2013 CSV MD5 does not match published E094-243-D1")
    return raw


def parse_original_rows(raw):
    try:
        decoded=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded=raw.decode("latin-1")
    reader=csv.DictReader(io.StringIO(decoded,newline=""))
    source_headers=list(reader.fieldnames or [])
    normal_lookup={}
    for original in source_headers:
        if original is None:continue
        k=normalize(original)
        if k in normal_lookup:
            raise ValueError("SCHEMA_STOP publisher original source has duplicate canonical field "+k)
        normal_lookup[k]=original
    absent=[field for field in REQ_FIELDS if normalize(field) not in normal_lookup]
    if absent:
        raise ValueError("SCHEMA_STOP missing source canonical ASI columns "+str(absent)+
                         " original_header="+str(source_headers))
    rename={original:field for field in REQ_FIELDS
            for original in [normal_lookup[normalize(field)]]}
    output=[]
    for row in reader:
        if None in row:
            raise ValueError("SCHEMA_STOP ASI source row has extra values not in publisher header")
        if not any(str(z).strip() for z in row.values() if z):continue
        output.append({name:str(row.get(orig,"") or "").strip()
                       for orig,name in rename.items()})
    return output,source_headers


def parse_number(raw):
    text=str(raw or "").strip()
    if not text:return None
    try:n=float(text.replace(",",""))
    except (TypeError,ValueError):return None
    if not math.isfinite(n) or n<0:return None
    return n


def accuracy_code(raw):
    value=str(raw or "").strip()
    if not value:return None
    try:
        n=float(value)
        if n.is_integer() and 1<=n<=5:return int(n)
    except (TypeError,ValueError):pass
    return None


def source_record_audit(rows,original_headers):
    n=len(rows)
    if n!=EXPECTED_ROWS:
        raise ValueError("SAMPLE_STOP original ASI source 1124 survey record count changed: "+str(n))
    species=Counter(x["Species"].upper() for x in rows)
    regions=Counter(x["Region"].upper() for x in rows)
    source_labels=Counter(x["Source"] for x in rows)
    stages=Counter(x["Counted_object"].upper() for x in rows)
    grades=Counter(str(accuracy_code(x["Accuracy"])) for x in rows)
    source_sites={r["Site_ID"] for r in rows if r["Site_ID"]}
    if len(source_sites)!=EXPECTED_SITE_COUNT:
        raise ValueError("SOURCE_STOP original 2013 metadata 113 unique site IDs changed")
    if not set(species).issubset(EXPECTED_SPECIES):
        raise ValueError("SOURCE_STOP unseen original 2013 ASI taxon code")
    if not set(regions).issubset(EXPECTED_REGIONS):
        raise ValueError("SOURCE_STOP unseen original ASI geographical region")
    valid_position=0
    source_date_unknown=0
    source_valid_breeding_year=0
    records_counted=0
    counts_zero=0
    qualified=[]
    nesting_source={}
    stage_keys=Counter()
    for r in rows:
        geo=None
        try:
            lat=float(r["Latitude"]);lon=float(r["Longitude"])
            if math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=-50 and -180<=lon<=180:
                geo=(lat,lon)
        except (TypeError,ValueError):pass
        if geo is not None:valid_position+=1
        if "xx" in r["Date"].lower() or not r["Date"]:
            source_date_unknown+=1
        season=r["Season"].strip()
        season_valid=bool(re.fullmatch(r"(?:19|20)\d{2}",season))
        if season_valid:source_valid_breeding_year+=1
        original_number=parse_number(r["Count"])
        if original_number is not None:
            records_counted+=1
            counts_zero+=original_number==0
        stage=r["Counted_object"].upper()
        grade=accuracy_code(r["Accuracy"])
        if season_valid and r["Site_ID"] and original_number is not None:
            stage_keys[(r["Site_ID"],r["Species"].upper(),season,stage)]+=1
        if (r["Source"].upper()=="ASI" and stage=="N" and
            grade is not None and grade<=2 and
            original_number is not None and original_number>0 and
            season_valid and geo is not None and
            r["Site_ID"] and r["Species"].upper() in EXPECTED_SPECIES):
            qualified.append(r)
    qualified_keys=Counter((r["Site_ID"],r["Species"].upper(),r["Season"])
                           for r in qualified)
    unique_qualified=[r for r in qualified if qualified_keys[
        (r["Site_ID"],r["Species"].upper(),r["Season"])]==1]
    years_by_site_taxon=defaultdict(set)
    sites_by_region=defaultdict(set)
    sites_by_taxon=defaultdict(set)
    primary_group=Counter()
    for r in unique_qualified:
        yr=int(r["Season"])
        site=r["Site_ID"];taxon=r["Species"].upper()
        years_by_site_taxon[(site,taxon)].add(yr)
        sites_by_region[r["Region"].upper()].add(site)
        sites_by_taxon[taxon].add(site)
        primary_group["PENGUIN" if taxon in PENGUINS else "FLYING_SEABIRD"]+=1
    report={
        "status":"ASI_ORIGINAL_2013_FIELD_CENSUS_SOURCE_QA_V33",
        "original_first_party_publisher_site_census_rows":n,
        "original_source_unique_author_site_IDs":len(source_sites),
        "original_source_taxa_counts":dict(sorted(species.items())),
        "original_source_geographic_region_counts":dict(sorted(regions.items())),
        "original_source_field_census_origins":dict(source_labels.most_common()),
        "original_counted_object_stage_literal_counts":dict(sorted(stages.items())),
        "original_accuracy_literal_code_counts":dict(sorted(grades.items())),
        "source_date_incomplete_day_month_or_missing_n":source_date_unknown,
        "original_source_valid_season_start_year_n":source_valid_breeding_year,
        "source_original_valid_geographic_coordinate_rows":valid_position,
        "source_nonnegative_numeric_count_rows":records_counted,
        "source_original_literal_zeros_not_assumed_survey_absence":counts_zero,
        "source_site_taxon_season_stage_duplicate_cells_n":sum(v>1 for v in stage_keys.values()),
        "source_original_asi_primary_nest_accuracy_1_or_2_positive_eligible_rows_before_duplicate_gate":len(qualified),
        "source_original_asi_primary_accurate_nest_source_rows_unambiguous_site_species_season":len(unique_qualified),
        "source_original_asi_qualified_rows_penguin_vs_flying":dict(sorted(primary_group.items())),
        "source_asi_qualified_distinct_sites_per_region":{k:len(v) for k,v in sorted(sites_by_region.items())},
        "source_asi_qualified_distinct_sites_per_taxon":{k:len(v) for k,v in sorted(sites_by_taxon.items())},
        "source_asi_qualified_site_taxon_histories_with_2_or_more_seasons":sum(
            len(v)>=2 for v in years_by_site_taxon.values()),
        "source_asi_qualified_distinct_site_taxon_year_series_count":len(years_by_site_taxon),
        "source_asi_qualified_distinct_site_taxon_season_count":sum(len(v) for v in years_by_site_taxon.values()),
        "source_asi_observed_all_7_original_geographic_regions":set(sites_by_region)==set(EXPECTED_REGIONS),
        "original_source_metadata_declared_site_not_verified_independent_physical_island":True,
        "original_no_surveyed_absence_column_confirmed":True,
        "original_C_chick_count_mixed_with_N_pair_count":False,
        "original_secondhand_source_records_count_as_ASI_new_field_observation":False,
        "original_asi_source_MAPPD_lineage_independent_replication_demonstrated":False,
        "new_island_breeding_ecological_effect_fit":False,
        "publisher_original_header_fields":original_headers,
    }
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result={"status":"HOLD_ORIGINAL_ASI_FIRST_PARTY_2013_SOURCE_V33",
            "new_island_breeding_ecological_effect_fit":False}
    try:
        raw=download_publisher_csv()
        rows,header=parse_original_rows(raw)
        result=source_record_audit(rows,header)
        result["publisher_original_CSV_MD5"]=hashlib.md5(raw).hexdigest()
        result["publisher_original_CSV_SHA256"]=hashlib.sha256(raw).hexdigest()
        result["original_source_CSV_file_bytes"]=len(raw)
        result["original_source_CSV_link"]=PUBLISHER_URL
        result["original_source_author_dataset_doi"]="10.1890/13-1108.1"
    except Exception as e:
        result["error_type"]=type(e).__name__
        result["error"]=str(e)[:1500]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):raise SystemExit(2)

if __name__=="__main__":
    main()
