#!/usr/bin/env python3
"""MAPPPD v4.4 public DownloadAll census: independently updated breeding seasons.

SOURCE COVERAGE ONLY. Does not refit V6, test ecological relations, or
treat older APBP / newer MAPPPD database republications as independent birds.
Provenance is original Oceanites URL + retrieval date + source SHA256.  The
CSV contains original cited sources in HTML strings; never render as HTML.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import csv
from datetime import datetime,timezone
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

URL = "https://www.penguinmap.com/mapppd/DownloadAll/"
OLD_CSV_SHA = "75c98ad9174f6ca8b88ae915adb8bb39de5d279099b45ce1ae7d1b2e25d5ba59"
MAX_BYTES = 25_000_000
HEADER = (
    "site_name","site_id","cammlr_region","longitude_epsg_4326",
    "latitude_epsg_4326","common_name","day","month","year",
    "season_starting","penguin_count","accuracy","count_type",
    "vantage","reference"
)
SPECIES = {
    "adelie penguin":"Pygoscelis adeliae",
    "adélie penguin":"Pygoscelis adeliae",
    "chinstrap penguin":"Pygoscelis antarcticus",
    "gentoo penguin":"Pygoscelis papua",
    "emperor penguin":"Aptenodytes forsteri",
    "king penguin":"Aptenodytes patagonicus",
    "macaroni penguin":"Eudyptes chrysolophus",
}
PRIMARY_SPECIES = frozenset((
    "Pygoscelis adeliae","Pygoscelis antarcticus","Pygoscelis papua"
))
ALLOWED_DATE_MONTHS = frozenset((1,2,12))
NEW_BREEDING_SEASONS = frozenset((2022,2023,2024))


def integer_or_none(value):
    s=str(value or "").strip()
    if not re.fullmatch(r"(0|[1-9]\d*)",s):
        return None
    return int(s)


def download_original():
    with requests.get(URL,timeout=(18,85),stream=True,
                      headers={"User-Agent":"mina-penguin-public-MAPPPD-macro-source-coverage/1.0"}) as r:
        r.raise_for_status()
        final=urlparse(r.url)
        if final.scheme!="https" or final.hostname not in ("penguinmap.com","www.penguinmap.com"):
            raise ValueError("SOURCE_STOP redirected outside MAPPPD public curator")
        raw=bytearray()
        for data in r.iter_content(chunk_size=65536):
            if not data:continue
            raw.extend(data)
            if len(raw)>MAX_BYTES:
                raise ValueError("SOURCE_STOP mutable publisher CSV exceeds source cap")
    if len(raw)<1000 or raw[:256].lstrip().lower().startswith((b"<html",b"<!doctype html")):
        raise ValueError("SOURCE_STOP original public DownloadAll endpoint did not serve CSV")
    return bytes(raw)


def source_rows(raw):
    text=raw.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text, newline=""),strict=True)
    if tuple(reader.fieldnames or ())!=HEADER:
        raise ValueError("SCHEMA_STOP mutable MAPPPD header changed: "+str(reader.fieldnames))
    output=list(reader)
    if not output or len(output)>500_000:
        raise ValueError("SCHEMA_STOP empty or implausibly many source rows")
    if any(None in row for row in output):
        raise ValueError("SCHEMA_STOP original CSV has more columns than declared")
    return output


def original_apbp_rows(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=OLD_CSV_SHA:
        raise ValueError("SOURCE_STOP original APBP v2.3 joined records SHA drift")
    with io.StringIO(raw.decode("utf-8-sig"),newline="") as f:
        source=list(csv.DictReader(f))
    site_ids=set()
    comparable_keys=set()
    historic_groups=defaultdict(set)
    original_last={}
    for r in source:
        site=r.get("site_id_original","").strip()
        if not site:continue
        site_ids.add(site)
        if r.get("eligibility")!="ELIGIBLE_NEST_RECORD_ONLY":
            continue
        taxon=r.get("scientificName_accepted","").strip()
        date=r.get("event_date","").strip()
        m=re.match(r"^(\d{4})-(\d{2})(?:-\d{2})?$",date)
        if m and int(m.group(2)) in ALLOWED_DATE_MONTHS:
            yr=int(m.group(1))
            season=yr-1 if int(m.group(2)) in (1,2) else yr
            if 1979<=season<=2024:
                try:
                    count=integer_or_none(r.get("nest_numeric_candidate"))
                except Exception:
                    count=None
                if count is not None:
                    key=(site,taxon,season)
                    comparable_keys.add((*key,count))
                    historic_groups[(site,taxon)].add(season)
    return site_ids,comparable_keys,historic_groups


def audit(raw,older_site_ids,old_exact,old_hist):
    rows=source_rows(raw)
    site_codes=set()
    records=[]
    species=Counter()
    count_types=Counter()
    accuracy=Counter()
    recent_source=Counter()
    date_consistency=Counter()
    data_issues=Counter()
    all_site_species_seasons=defaultdict(list)
    strict_by_key=defaultdict(list)
    original_overlap_exact=0
    original_overlap_conflicting=0

    old_site_species_years=defaultdict(set)
    for site,taxon,year,count in old_exact:
        old_site_species_years[(site,taxon,year)].add(count)

    for index,row in enumerate(rows):
        site=str(row["site_id"] or "").strip().upper()
        if not site or not re.fullmatch(r"[A-Z0-9_-]{2,12}",site):
            data_issues["INVALID_SITE_ID"]+=1
            continue
        site_codes.add(site)
        label=str(row["common_name"] or "").strip().casefold()
        taxon=SPECIES.get(label)
        species[taxon or "UNKNOWN:"+label]+=1
        count_type=str(row["count_type"] or "").strip().lower()
        count_types[count_type or "<EMPTY>"]+=1
        grade=str(row["accuracy"] or "").strip()
        accuracy[grade or "<EMPTY>"]+=1
        season=integer_or_none(row["season_starting"])
        year=integer_or_none(row["year"])
        month=integer_or_none(row["month"])
        day=integer_or_none(row["day"])
        n=integer_or_none(row["penguin_count"])

        if season is None or not 1850<=season<=2026:
            data_issues["INVALID_OR_MISSING_SEASON"]+=1
            continue
        if n is None:
            data_issues["INVALID_COUNT"]+=1
            continue
        if year is not None and month in ALLOWED_DATE_MONTHS:
            expected=year-1 if month in (1,2) else year
            if expected!=season:
                date_consistency["CONFLICT_EXACT_MONTH_VS_SEASON"]+=1
                match=False
            else:
                date_consistency["MATCHED_EXACT_MONTH_VS_SEASON"]+=1
                match=True
        else:
            date_consistency["NO_UNAMBIGUOUS_DEC_JAN_FEB_DATE"]+=1
            match=False

        key=(site,taxon,season)
        if taxon and count_type=="nests":
            all_site_species_seasons[key].append(index)
            if season in NEW_BREEDING_SEASONS:
                recent_source[season]+=1
            if n in old_site_species_years.get(key,set()):
                original_overlap_exact+=1
            elif key in old_site_species_years:
                original_overlap_conflicting+=1
        if taxon in PRIMARY_SPECIES and count_type=="nests" and match and grade in {"1","2","3","4","5"}:
            strict_by_key[key].append((index,n,grade))
        records.append({
            "site_code":site,
            "scientific_name":taxon or "",
            "season":season,
            "survey_year":year,
            "survey_month":month,
            "measured_nests":n if count_type=="nests" else None,
            "count_type":count_type,
            "accuracy":grade,
            "is_dated_dec_jan_feb":match,
            "is_post_v23_new_season":season in NEW_BREEDING_SEASONS,
            "overlaps_original_APBP_v23":(site,taxon,season,n) in old_exact,
            "source_site_in_original_v23":site in older_site_ids,
        })

    strict_nonduplicates={key:items[0] for key,items in strict_by_key.items() if len(items)==1}
    repeated=defaultdict(set)
    for site,taxon,year in strict_nonduplicates:
        repeated[(site,taxon)].add(year)
    new_strict={key:val for key,val in strict_nonduplicates.items() if key[2] in NEW_BREEDING_SEASONS}
    new_site_species=defaultdict(set)
    for site,taxon,year in new_strict:
        new_site_species[(site,taxon)].add(year)
    recent_pairs=0
    old_to_new_bridge=0
    for (site,taxon),years in repeated.items():
        for year in NEW_BREEDING_SEASONS:
            if year in years and year-1 in years:
                recent_pairs+=1
                if year==2022:
                    old_to_new_bridge+=1
    allgroups_recent=[(key,items) for key,items in all_site_species_seasons.items() if key[2] in NEW_BREEDING_SEASONS]
    duplicate_recent=sum(len(items)>1 for key,items in allgroups_recent)
    return {
        "status":"MAPPPD_V44_CURRENT_PUBLIC_CENSUS_EXTENSION_QA_ONLY",
        "publisher":"Oceanites MAPPPD",
        "source_download_all_url":URL,
        "access_time_utc":datetime.now(timezone.utc).isoformat(),
        "official_portal_product":"MAPPPD v4.4, public bulk count CSV through 2024/25",
        "source_raw_csv_SHA256":hashlib.sha256(raw).hexdigest(),
        "source_original_bytes":len(raw),
        "original_source_columns":list(HEADER),
        "original_csv_count_rows":len(rows),
        "original_distinct_site_ids":len(site_codes),
        "source_siteIDs_shared_with_APBP_v2_3":len(site_codes&older_site_ids),
        "source_siteIDs_absent_from_APBP_v2_3":len(site_codes-older_site_ids),
        "APBP_original_site_ID_count":len(older_site_ids),
        "source_species_record_rows":dict(species),
        "source_count_type_record_rows":dict(count_types),
        "source_survey_accuracy_values":dict(accuracy),
        "source_date_quality":dict(date_consistency),
        "source_metadata_holds":dict(data_issues),
        "source_breeding_nest_rows_in_2022_2023_2024":dict(recent_source),
        "n_all_site_species_season_groups":len(all_site_species_seasons),
        "n_new_2022_2024_any_nest_groups":len(allgroups_recent),
        "n_new_2022_2024_duplicate_nest_groups":duplicate_recent,
        "original_APBP_v2_3_exact_nest_count_source_overlaps":original_overlap_exact,
        "same_site_species_season_count_conflicts_with_original":original_overlap_conflicting,
        "n_strict_primary_species_dated_single_survey_seasons":len(strict_nonduplicates),
        "n_strict_post_2022_primary_species_site_years":len(new_strict),
        "n_distinct_primary_site_species_with_new_2022_2024_records":len(new_site_species),
        "n_primary_site_species_with_2plus_distinct_new_2022_2024_seasons":sum(len(y)>=2 for y in new_site_species.values()),
        "n_primary_strict_consecutive_pairs_ending_2022_to_2024":recent_pairs,
        "n_primary_strict_consecutive_pairs_bridging_2021_to_2022":old_to_new_bridge,
        "original_census_data_were_not_inferred_zero":True,
        "ecological_effect_models_fitted":0,
        "not_a_replicate_of_apbp_v23":"Source overlaps and 2022+ genuinely newer years must be separated before model fit.",
        "terms":"MAPPPD copyright terms require source attribution and no unlicensed commercial copying."
    },records


def export_strict(records,out):
    with Path(out).open("w",newline="",encoding="utf-8") as f:
        cols=list(records[0])
        writer=csv.DictWriter(f,fieldnames=cols)
        writer.writeheader()
        writer.writerows(records)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--old-csv",type=Path,required=True)
    ap.add_argument("--out-json",type=Path,required=True)
    ap.add_argument("--out-csv",type=Path,required=True)
    args=ap.parse_args()
    result={"status":"HOLD_MAPPPD_MUTABLE_PUBLIC_SOURCE","ecological_effect_models_fitted":0}
    try:
        old_sites,old_keys,old_hist=original_apbp_rows(args.old_csv)
        source=download_original()
        result,records=audit(source,old_sites,old_keys,old_hist)
        if not records: raise ValueError("SCHEMA_STOP no MAPPPD valid source metadata records")
        args.out_csv.parent.mkdir(parents=True,exist_ok=True)
        export_strict(records,args.out_csv)
        result["derivative_coverage_csv_sha256"]=hashlib.sha256(args.out_csv.read_bytes()).hexdigest()
        result["derived_source_rows_with_valid_metadata"]=len(records)
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:500]
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
