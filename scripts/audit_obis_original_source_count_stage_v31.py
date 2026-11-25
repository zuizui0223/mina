#!/usr/bin/env python3
"""V31 original OBIS 1900–1996 historical seabird count/colony support audit.

Source observations were summarized in V30. Here the original reporter's
count-stage, named-site and historical years are audited; NO ecological
island-effect model and no unvisited-site-to-zero conversion.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import requests

from audit_obis_historical_penguin_dwca_v30 import (
    source_zip_from_publisher,safe_archive_files,original_dwc_core,
)

ORIGINAL_ZIP_SHA="c17670be07fed76492a30a59893d059f4ccb11d54f2f73bceeaf007c19e311d5"
ORIGINAL_ROWS=2787
ORIGINAL_NUMERIC_COUNTS=2377
PROVENANCE_FIELDS=(
    "lifeStage","dynamicProperties","occurrenceRemarks","recordedBy",
    "bibliographicCitation","associatedReferences","basisOfRecord",
    "collectionCode","institutionCode","catalogNumber","fieldNumber",
    "coordinatePrecision","verbatimCoordinates","waterBody","country",
    "stateProvince","county","locality","occurrenceStatus",
)
SOURCE_LOCATION_FIELDS=("waterBody","stateProvince","county","locality")
GEO_FIELD_VALUES_PREVIEW_LIMIT=9


def source_year(row):
    y=str(row.get("year","") or "").strip()
    if re.fullmatch(r"(?:18|19)\d{2}",y):
        value=int(y)
        if 1800<=value<=1996:return value
    date=str(row.get("eventDate","") or "").strip()
    parsed=re.match(r"^((?:18|19)\d{2})(?:-|$)",date)
    if parsed:
        value=int(parsed.group(1))
        if 1800<=value<=1996:return value
    return None


def source_count(row):
    raw=str(row.get("individualCount","") or "").strip()
    if not raw:return None,"MISSING"
    try:
        value=float(raw)
    except (ValueError,TypeError):
        return None,"NONNUMERIC"
    if not math.isfinite(value) or value<0:
        return None,"NONFINITE_OR_NEGATIVE"
    if abs(value-round(value))>1e-8:
        return value,"FINITE_NONINTEGER"
    return value,"NUMERIC_NONNEGATIVE_INTEGER"


def source_literal_context(rows):
    report={}
    for name in PROVENANCE_FIELDS:
        available=[str(r.get(name,"") or "").strip() for r in rows
                   if str(r.get(name,"") or "").strip()]
        values=Counter(available)
        report[name]={
            "original_nonblank_rows":len(available),
            "unique_exact_literal_values":len(values),
            "top_original_literal_values":[{
                "literal":v[:200],
                "source_record_n":n
            } for v,n in sorted(values.items(),key=lambda z:(-z[1],z[0]))[:GEO_FIELD_VALUES_PREVIEW_LIMIT]],
            "every_source_record_lacks_field_value":not bool(available),
        }
    return report


def audit_historical_source(rows):
    if len(rows)!=ORIGINAL_ROWS:
        raise ValueError("SOURCE_STOP original OBIS source 2787-row corpus changed")
    taxon_records=Counter()
    taxon_counts=defaultdict(Counter)
    zero_taxa=Counter()
    source_years=Counter()
    habitat_region=Counter()
    identical_source_rows=Counter()
    original_siteyear=defaultdict(list)
    source_locations=Counter()
    stage_count=Counter()
    years_missing=Counter()
    original_catalogs=Counter()
    counts_numeric=[]
    for r in rows:
        taxon=str(r.get("scientificName","") or "").strip() or "TAXON_MISSING"
        taxon_records[taxon]+=1
        value,kind=source_count(r)
        taxon_counts[taxon][kind]+=1
        if kind=="NUMERIC_NONNEGATIVE_INTEGER":
            counts_numeric.append(value)
            if value==0:zero_taxa[taxon]+=1
        stage=str(r.get("lifeStage","") or "").strip() or "ORIGINAL_STAGE_NOT_REPORTED"
        stage_count[(stage,kind)]+=1
        year=source_year(r)
        source_years[year if year is not None else "MISSING_OR_INVALID_YEAR"]+=1
        if year is None:years_missing[taxon]+=1
        location=tuple(str(r.get(z,"") or "").strip() for z in SOURCE_LOCATION_FIELDS)
        if any(location):
            source_locations[location]+=1
        state=location[1] or "NO_SOURCE_STATE_PROVINCE"
        habitat_region[state]+=1
        if (value is not None and kind=="NUMERIC_NONNEGATIVE_INTEGER"
            and year is not None and location[3]):
            key=(*location,taxon,stage,
                 str(r.get("basisOfRecord","") or "").strip())
            original_siteyear[key].append((year,value,str(r.get("catalogNumber","") or "").strip()))
        catalog=str(r.get("catalogNumber","") or "").strip()
        if catalog:original_catalogs[catalog]+=1
        row_fingerprint=tuple(sorted((str(k),str(v)) for k,v in r.items()))
        identical_source_rows[row_fingerprint]+=1

    n_numeric=sum(t["NUMERIC_NONNEGATIVE_INTEGER"] for t in taxon_counts.values())
    n_numeric_or_other=sum(t["FINITE_NONINTEGER"] for t in taxon_counts.values())+n_numeric
    if n_numeric_or_other!=ORIGINAL_NUMERIC_COUNTS:
        raise ValueError("SOURCE_STOP original 2377 finite count supporting records changed")
    repeated=[]
    n_same_year_multisource=0
    for key,values in original_siteyear.items():
        years=Counter(year for year,_,_ in values)
        repeated_n=sum(z>=2 for z in years.values())
        n_same_year_multisource+=repeated_n
        distinct=sorted(years)
        if len(distinct)>=2:
            loc=key[:4]
            examples=[{"year":year,"source_original_count_records":years[year]}
                      for year in distinct[:12]]
            repeated.append({
                "original_waterBody":loc[0],
                "original_stateProvince":loc[1],
                "original_county":loc[2],
                "original_locality":loc[3],
                "original_scientificName":key[4],
                "original_lifeStage_literal":key[5],
                "original_basisOfRecord":key[6],
                "source_unique_original_year_count":len(distinct),
                "source_original_count_rows":len(values),
                "original_min_recorded_year":min(distinct),
                "original_max_recorded_year":max(distinct),
                "year_source_record_count_preview":examples,
                "verified_independent_same_colony_original_count_stage":False,
            })
    repeated.sort(key=lambda x:(-x["source_unique_original_year_count"],
                                -x["source_original_count_rows"],
                                x["original_locality"]))
    stage_name_counts=Counter()
    for (stage,kind),n in stage_count.items():
        if kind=="NUMERIC_NONNEGATIVE_INTEGER":stage_name_counts[stage]+=n
    count_values_sorted=sorted(counts_numeric)
    return {
        "status":"OBIS_HISTORICAL_PENGUIN_SEABIRD_SOURCE_STAGE_LOCALITY_AUDIT_V31",
        "original_source_publisher_record_n":len(rows),
        "original_source_numeric_integer_count_field_n":n_numeric,
        "source_integer_counts_which_are_zero_n":sum(z==0 for z in counts_numeric),
        "original_species_record_n":dict(sorted(taxon_records.items())),
        "source_count_value_support_by_exact_species":{
            k:dict(sorted(v.items())) for k,v in sorted(taxon_counts.items())},
        "original_integer_explicit_zeros_by_taxon":dict(sorted(zero_taxa.items())),
        "source_count_stage_name_by_numeric_record":dict(sorted(stage_name_counts.items())),
        "source_original_year_record_n":{str(k):v for k,v in sorted(source_years.items(),key=lambda z:str(z[0]))},
        "original_source_missing_year_by_taxon":dict(sorted(years_missing.items())),
        "source_nonzero_integer_quantity_max":max(counts_numeric) if counts_numeric else None,
        "original_count_50pct":count_values_sorted[len(count_values_sorted)//2] if count_values_sorted else None,
        "source_original_state_province_record_n":dict(sorted(habitat_region.items())),
        "original_unique_exact_source_locality_tuple_n":len(source_locations),
        "original_site_stage_year_candidate_group_count":len(original_siteyear),
        "original_exact_locality_taxon_stage_candidate_groups_with_2plus_years":len(repeated),
        "original_exact_locality_taxon_stage_candidate_groups_with_3plus_years":sum(
            z["source_unique_original_year_count"]>=3 for z in repeated),
        "original_year_location_stage_groups_with_2plus_count_records":n_same_year_multisource,
        "source_original_repeated_site_year_candidate_examples":repeated[:25],
        "source_original_exact_full_row_repetition_n":sum(n-1 for n in identical_source_rows.values()),
        "source_original_catalogNumber_nonempty_rows":sum(original_catalogs.values()),
        "source_original_catalogNumber_duplicate_literals":sum(z-1 for z in original_catalogs.values()),
        "original_literal_source_field_distribution":source_literal_context(rows),
        "original_individualCount_is_verified_breeding_pair_count":False,
        "original_numeric_zero_is_independently_surveyed_absence":False,
        "original_locality_text_is_verified_unique_island":False,
        "original_MAPPPD_source_genealogy_deduplicated":False,
        "new_ecological_island_time_series_effect_fitted":False,
    }


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",type=Path,required=True)
    args=a.parse_args()
    result={"status":"HOLD_OBIS_ORIGINAL_STAGE_YEAR_SUPPORT_V31"}
    try:
        with requests.Session() as s:
            archive=source_zip_from_publisher(s)
        actual_sha=hashlib.sha256(archive).hexdigest()
        if actual_sha!=ORIGINAL_ZIP_SHA:
            raise ValueError("SOURCE_STOP original OBIS archive edition SHA256 drift")
        files,source_sha=safe_archive_files(archive)
        rows,receipt=original_dwc_core(files)
        result=audit_historical_source(rows)
        result["pinned_original_OBIS_IPT_ZIP_SHA256"]=actual_sha
        result["original_DwC_source_schema"]=receipt
    except Exception as e:
        result["error_type"]=type(e).__name__
        result["error"]=str(e)[:1100]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",
                        encoding="utf-8")
    if result["status"].startswith("HOLD"):
        print(json.dumps(result,ensure_ascii=False))
        raise SystemExit(2)
    print(json.dumps({
        "status":result["status"],
        "original_source_record_n":result["original_source_publisher_record_n"],
        "original_source_numeric_count_n":result["original_source_numeric_integer_count_field_n"],
        "original_source_explicit_zero_n":result["source_integer_counts_which_are_zero_n"],
        "count_stage_literal_distribution":result["source_count_stage_name_by_numeric_record"],
        "original_exact_source_site_taxon_stage_multi_year_candidates":result[
            "original_exact_locality_taxon_stage_candidate_groups_with_2plus_years"],
        "original_exact_source_site_taxon_stage_3_year_candidates":result[
            "original_exact_locality_taxon_stage_candidate_groups_with_3plus_years"],
        "examples":result["source_original_repeated_site_year_candidate_examples"][:12],
        "source_identifiability":result["original_literal_source_field_distribution"][
            "occurrenceRemarks"],
        "source_dynamicProperties":result["original_literal_source_field_distribution"][
            "dynamicProperties"],
        "source_basis":result["original_literal_source_field_distribution"]["basisOfRecord"],
        "source_coordinatePrecision":result["original_literal_source_field_distribution"][
            "coordinatePrecision"],
    },ensure_ascii=False))


if __name__=="__main__":
    main()
