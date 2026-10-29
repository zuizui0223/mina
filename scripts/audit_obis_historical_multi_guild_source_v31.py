#!/usr/bin/env python3
"""V31 original 2018 IPT/OBIS Antarctic multispecies quantity/lineage audit.

The source reveals six penguin and six flying-petrel source taxa; audit
each raw record's source year, locality, count stage, original observer
and precision. No causal model or false surveyed-absences fitted.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

import requests
from audit_obis_historical_penguin_dwca_v30 import (
    source_zip_from_publisher,safe_archive_files,original_dwc_core
)

ORIGINAL_ZIP_SHA="c17670be07fed76492a30a59893d059f4ccb11d54f2f73bceeaf007c19e311d5"
ORIGINAL_EXPECTED_ROWS=2787
SOURCE_PENGUIN_GENERA=("Aptenodytes","Eudyptes","Pygoscelis")
SOURCE_FLYING_GENERA=("Macronectes","Pagodroma","Thalassoica")
SOURCE_QUAL_FIELDS=(
    "lifeStage","basisOfRecord","dynamicProperties","occurrenceRemarks",
    "coordinatePrecision","associatedReferences","bibliographicCitation",
    "recordedBy","waterBody","country","stateProvince","county",
)
MAX_EXAMPLE_LEN=200


def source_species_guild(name:str):
    name=(name or "").strip()
    genus=name.split(" ",1)[0]
    if genus in SOURCE_PENGUIN_GENERA:return "FLIGHTLESS_PENGUIN"
    if genus in SOURCE_FLYING_GENERA:return "FLYING_PETREL"
    return "UNKNOWN_GUILD_HOLD"


def original_year_value(row):
    y=(row.get("year") or "").strip()
    if re.fullmatch(r"(?:18|19|20)\d\d",y):
        return int(y)
    event=(row.get("eventDate") or "")
    match=re.search(r"\b(?:18|19|20)\d\d\b",event)
    return int(match.group()) if match else None


def finite_nonnegative_original_quantity(row):
    n=(row.get("individualCount") or "").strip()
    if not n:return None
    try:
        val=float(n)
    except ValueError:return None
    return val if math.isfinite(val) and val>=0 else None


def q(values):
    v=sorted(float(x) for x in values if x is not None and math.isfinite(float(x)))
    def at(p):
        if not v:return None
        ix=(len(v)-1)*p
        low=math.floor(ix)
        high=math.ceil(ix)
        return float(v[low]+(v[high]-v[low])*(ix-low))
    return {
        "n":len(v),
        "median":at(.5),"p10":at(.1),"p90":at(.9),
        "maximum":v[-1] if v else None,
    }


def source_group_audit(records):
    if len(records)!=ORIGINAL_EXPECTED_ROWS:
        raise ValueError("SOURCE_STOP IPT 2018 original source observation count changed")
    groups=defaultdict(list)
    for rec in records:
        guild=source_species_guild(rec.get("scientificName",""))
        groups[guild].append(rec)
    if groups.get("UNKNOWN_GUILD_HOLD"):
        raise ValueError("SCHEMA_STOP unknown first-party Antarctic bird taxon genus")
    result_guilds={}
    year_guild=defaultdict(Counter)
    species_receipts={}
    stages=defaultdict(Counter)
    cited=Counter()
    for guild,rows in sorted(groups.items()):
        years=Counter(original_year_value(x) for x in rows)
        quantities=[finite_nonnegative_original_quantity(x) for x in rows]
        good=[v for v in quantities if v is not None]
        lats=[]
        null_lats=0
        north=0
        geo_valid=0
        for r in rows:
            try:
                lat=float(r.get("decimalLatitude",""))
                lon=float(r.get("decimalLongitude",""))
                if math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180:
                    lats.append(lat)
                    geo_valid+=1
                    if lat> -60:
                        north+=1
                else:null_lats+=1
            except ValueError:null_lats+=1
        unique_localities=set((z.get("locality") or "").strip() for z in rows if z.get("locality"))
        repeated=Counter((
            x.get("scientificName",""),
            original_year_value(x),
            (x.get("locality") or "").strip(),
        ) for x in rows)
        source_references=Counter(
            (r.get("associatedReferences") or r.get("bibliographicCitation") or "").strip()
            for r in rows
        )
        zero=sum(v==0 for v in good)
        million=sum(v>=1e6 for v in good)
        tags=Counter(x.get("lifeStage","").strip() for x in rows)
        basis=Counter(x.get("basisOfRecord","").strip() for x in rows)
        species=Counter(x.get("scientificName","") for x in rows)
        result_guilds[guild]={
            "original_guild_record_count":len(rows),
            "original_taxon_literal_counts":dict(sorted(species.items())),
            "original_year_available_rows":len(rows)-years.get(None,0),
            "original_distinct_source_year_n":sum(x is not None for x in years),
            "source_first_last_year":(
                [min(x for x in years if x is not None),max(x for x in years if x is not None)]
                if len(years)>years.get(None,0)*0 + (1 if None in years else 0) else None),
            "source_year_observation_record_counts":{
                str(key) if key is not None else "MISSING_SOURCE_YEAR":n
                for key,n in sorted(years.items(),key=lambda kv:(kv[0] is None,kv[0] or 0))
            },
            "first_party_numeric_quantity_rows":len(good),
            "original_reported_numeric_zero_rows_UNVERIFIED_SURVEY_ABSENCE":zero,
            "original_quantity_values_gte_one_million_RISK":million,
            "quantity_descriptive_distribution_NOT_NEST_COUNTS":q(good),
            "original_source_valid_coordinates_rows":geo_valid,
            "original_source_geo_lat_north_of_60S_rows":north,
            "original_source_geo_lat_60S_or_south_rows":geo_valid-north,
            "original_source_geo_lat_missing_or_outside_range_rows":null_lats,
            "original_source_unique_nonempty_literal_locality_strings":len(unique_localities),
            "original_duplicate_species_year_literal_locality_group_n":sum(
                n>1 for k,n in repeated.items()
                if k[1] is not None and k[2]),
            "original_duplicate_species_year_literal_locality_rows":sum(
                n for k,n in repeated.items() if n>1 and k[1] is not None and k[2]),
            "source_top_lifeStage_values":tags.most_common(16),
            "source_basis_of_record_values":basis.most_common(16),
            "source_distinct_nonempty_observer_citation_labels":sum(
                k!="" for k in source_references),
            "source_top_reference_labels_truncated":[{
                "citation_literal_excerpt":k[:MAX_EXAMPLE_LEN],"record_count":n}
                for k,n in source_references.most_common(12)],
        }
        for x in rows:
            y=original_year_value(x)
            if y is not None:
                year_guild[y][guild]+=1
    all_columns=set(records[0])
    for field in SOURCE_QUAL_FIELDS:
        if field not in all_columns:continue
        vals=[(x.get(field) or "").strip() for x in records]
        count=Counter(vals)
        stages[field]=count
        species_receipts[field]={
            "original_rows_with_value":len(vals)-count.get("",0),
            "original_distinct_values_including_blank":len(count),
            "source_top_literal_examples":[
                {"value_excerpt":k[:MAX_EXAMPLE_LEN],"original_records":n}
                for k,n in count.most_common(12)
            ]
        }
    original_zero_records=[
        {"species":x.get("scientificName"),"year":original_year_value(x),
         "lifeStage":x.get("lifeStage"),"locality":(x.get("locality") or "")[:100],
         "quantity":finite_nonnegative_original_quantity(x),
         "original_occurrence_status_field_available":"occurrenceStatus" in all_columns}
        for x in records if finite_nonnegative_original_quantity(x)==0
    ]
    extreme=[
        {"species":x.get("scientificName"),"year":original_year_value(x),
         "quantity":finite_nonnegative_original_quantity(x),
         "lifeStage":x.get("lifeStage"),"reference_excerpt":(
              x.get("associatedReferences") or "")[:140]}
        for x in records
        if finite_nonnegative_original_quantity(x) is not None and
           finite_nonnegative_original_quantity(x)>=1e6
    ]
    return {
        "status":"OBIS_ORIGINAL_ANTARCTIC_MULTI_GUILD_SOURCE_YEAR_AND_COUNT_GRAIN_V31",
        "original_record_n":len(records),
        "original_obis_archive_has_true_flying_birds":True,
        "original_all_12_source_species_guild_metrics":result_guilds,
        "original_source_original_FIELD_distribution":species_receipts,
        "all_records_source_year_x_guild_counts":{
            str(y):dict(sorted(counter.items()))
            for y,counter in sorted(year_guild.items())
        },
        "original_zero_quantity_rows_UNVERIFIED_SURVEYED_ABSENCE":original_zero_records,
        "million_count_outliers_NOT_ACCEPTED_DIRECT_NEST_CENSUS":extreme,
        "original_occurrenceStatus_field_present":"occurrenceStatus" in all_columns,
        "no_authoritative_breeding_count_stage_evidenced_by_quantity_field_alone":True,
        "no_original_observation_values_reclassified_as_absence":True,
        "same_locality_names_not_independent_islands":True,
        "source_archived_observations_not_independent_of_MAPPPD_by_default":True,
        "biological_island_effect_models_fitted":0,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    report={"status":"HOLD_OBIS_HISTORIC_MULTI_GUILD_SOURCE_V31"}
    try:
        with requests.Session() as session:
            raw=source_zip_from_publisher(session)
        files,digest=safe_archive_files(raw)
        if digest!=ORIGINAL_ZIP_SHA:
            raise ValueError("SOURCE_STOP original IPT first-party historical ZIP SHA drift")
        rows,core=original_dwc_core(files)
        report=source_group_audit(rows)
        report["source_original_IPT_archived_SHA256"]=digest
        report["original_source_archive_core_member_SHA256"]=core["source_original_core_member_SHA256"]
        report["original_source_DwC_core_schema"]=core["source_original_DwC_term_name_indices"]
    except Exception as e:
        report["error_type"]=type(e).__name__
        report["error"]=str(e)[:1300]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    # GitHub log prints compact data, full source audit is artifact.
    print(json.dumps({
        "status":report["status"],
        "guilds":{k:{
            "original_records":v["original_guild_record_count"],
            "numeric_counts":v["first_party_numeric_quantity_rows"],
            "source_localities":v["original_source_unique_nonempty_literal_locality_strings"],
            "source_years":v["original_distinct_source_year_n"],
            "year_range":v["source_first_last_year"],
            "lat_north_60S":v["original_source_geo_lat_north_of_60S_rows"],
            "lat_south_60S":v["original_source_geo_lat_60S_or_south_rows"],
            "duplicate_location_year_group_n":v["original_duplicate_species_year_literal_locality_group_n"],
            "quantity_summary":v["quantity_descriptive_distribution_NOT_NEST_COUNTS"],
            "lifeStages":v["source_top_lifeStage_values"][:12],
        } for k,v in report.get("original_all_12_source_species_guild_metrics",{}).items()},
        "risk_qty_zero":len(report.get("original_zero_quantity_rows_UNVERIFIED_SURVEYED_ABSENCE",[])),
        "risk_qty_ge_1m":report.get("million_count_outliers_NOT_ACCEPTED_DIRECT_NEST_CENSUS",[])[:8],
        "source_count_method_citation_and_precision_literal_fields":{
            name:{"nonempty":m.get("original_rows_with_value"),
                  "unique":m.get("original_distinct_values_including_blank"),
                  "top":m.get("source_top_literal_examples",[])[:6]}
            for name,m in report.get("original_source_original_FIELD_distribution",{}).items()
            if name in ("lifeStage","basisOfRecord","dynamicProperties",
                        "occurrenceRemarks","associatedReferences",
                        "bibliographicCitation","recordedBy","coordinatePrecision")
        },
        "year_n":len(report.get("all_records_source_year_x_guild_counts",{})),
        "error":report.get("error"),
    },ensure_ascii=False))
    if report["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
