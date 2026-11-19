#!/usr/bin/env python3
"""Link original APBP Event / Occurrence / eMoF at occurrenceID level.

Counts and source-sample coverage ONLY; no climate, land or species effects.
A source site is NOT equivalent to an island; a missing record is NEVER zero.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re

from audit_apbp_darwincore_source_v1 import (
    EXPECTED_ROW_COUNTS, SOURCE_DOI, SOURCE_URL,
    TAXON_CANONICAL, audited_schema, event_year, fetch_original, metadata,
    rows_for, safe_zip,
)

PINNED_SHA = "afa947f39d9ad7382266d5be64c70f9fe4e84ffb6e2838c1369e043caae09abf"
NEST_TYPE = "the number of nests (equivalently, breeding pairs)"
CHICK_ADULT_TYPE = "the number of chicks or adults"

COLUMNS = (
    "original_event_core_id","original_eventID",
    "original_occurrenceID","original_measurementID",
    "site_id_original","locality","islandGroup_NOT_ISLAND_ID",
    "event_date","parsed_year","decimalLatitude","decimalLongitude",
    "coordinateUncertaintyInMeters","samplingProtocol",
    "scientificName_original","scientificName_accepted",
    "organismQuantity_raw","organismQuantityType_original",
    "lifeStage","occurrenceStatus",
    "measurementType","measurementValue_original",
    "measurementAccuracy_original","measurementUnit_original",
    "source_associatedReferences",
    "nest_numeric_candidate","eligibility",
)


def numeric(raw):
    x=str(raw or "").strip()
    if not x or not re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?",x):
        return None
    n=float(x)
    if not (0<=n<1e9 and n.is_integer()):
        return None
    return int(n)


def raw_join(source, expected_sha=PINNED_SHA, expected_rows=EXPECTED_ROW_COUNTS):
    actual=hashlib.sha256(source).hexdigest()
    if actual!=expected_sha:
        raise ValueError("SOURCE_VERSION_STOP original zip SHA changed since outcome-blind schema audit")
    audited_schema(source,expected_counts=expected_rows)
    with safe_zip(source) as z:
        tables=metadata(z)
        raw={t["rowtype"]:list(rows_for(z,t)) for t in tables}

    events={}
    for eid,ref,row in raw["Event"]:
        if not eid or eid in events:
            raise ValueError("JOIN_STOP duplicate/empty Event core key")
        events[eid]=row

    occurrences={}
    count_by_event=Counter()
    for empty,event_id,row in raw["Occurrence"]:
        oid=row.get("occurrenceID","").strip()
        if not oid or oid in occurrences:
            raise ValueError("JOIN_STOP missing or duplicate original Occurrence.occurrenceID")
        if event_id not in events:
            raise ValueError("JOIN_STOP Occurrence foreign key not in Event")
        occurrences[oid]=(event_id,row)
        count_by_event[event_id]+=1

    joined=[]
    orphan_measure=0
    orphan_wrong_event=0
    for empty,event_id,measurement in raw["ExtendedMeasurementOrFact"]:
        oid=measurement.get("occurrenceID","").strip()
        if oid not in occurrences:
            orphan_measure+=1
            continue
        occ_event,occ=occurrences[oid]
        if event_id!=occ_event:
            orphan_wrong_event+=1
            continue
        row_event=events[event_id]
        orig_name=occ.get("scientificName","").strip()
        accepted=TAXON_CANONICAL.get(orig_name)
        qtype=occ.get("organismQuantityType","").strip()
        measure_type=measurement.get("measurementType","").strip()
        quantity=occ.get("organismQuantity","").strip()
        n=numeric(quantity)
        year=event_year(row_event.get("eventDate") or row_event.get("year"))
        site=row_event.get("locationID","").strip()
        # If a SOURCE-TYPED nest measurement and a clearly compatible original
        # occurrence unit agree, allow this as a candidate, not a fitted effect.
        has_nest_unit=bool(re.search(r"\b(?:nest|nests|breeding pair|breeding pairs)\b",qtype,re.I))
        if not accepted:
            eligibility="HOLD_UNKNOWN_TAXON"
        elif measure_type!=NEST_TYPE:
            eligibility="NOT_NEST_MEASUREMENT"
        elif n is None:
            eligibility="HOLD_COUNT_NOT_EXACT_NONNEGATIVE_INTEGER"
        elif not has_nest_unit:
            eligibility="HOLD_ORGANISM_QUANTITY_UNIT"
        elif year is None or not site:
            eligibility="HOLD_SITE_OR_YEAR_MISSING"
        else:
            eligibility="ELIGIBLE_NEST_RECORD_ONLY"
        joined.append({
            "original_event_core_id":event_id,
            "original_eventID":row_event.get("eventID",""),
            "original_occurrenceID":oid,
            "original_measurementID":measurement.get("measurementID",""),
            "site_id_original":site,
            "locality":row_event.get("locality",""),
            "islandGroup_NOT_ISLAND_ID":row_event.get("islandGroup",""),
            "event_date":row_event.get("eventDate",""),
            "parsed_year":year,
            "decimalLatitude":row_event.get("decimalLatitude",""),
            "decimalLongitude":row_event.get("decimalLongitude",""),
            "coordinateUncertaintyInMeters":row_event.get("coordinateUncertaintyInMeters",""),
            "samplingProtocol":row_event.get("samplingProtocol",""),
            "scientificName_original":orig_name,
            "scientificName_accepted":accepted or "",
            "organismQuantity_raw":quantity,
            "organismQuantityType_original":qtype,
            "lifeStage":occ.get("lifeStage",""),
            "occurrenceStatus":occ.get("occurrenceStatus",""),
            "measurementType":measure_type,
            "measurementValue_original":measurement.get("measurementValue",""),
            "measurementAccuracy_original":measurement.get("measurementAccuracy",""),
            "measurementUnit_original":measurement.get("measurementUnit",""),
            "source_associatedReferences":occ.get("associatedReferences",""),
            "nest_numeric_candidate":n if eligibility=="ELIGIBLE_NEST_RECORD_ONLY" else "",
            "eligibility":eligibility,
        })

    if orphan_measure or orphan_wrong_event:
        raise ValueError(f"JOIN_STOP eMoF orphan occurrenceIDs={orphan_measure}, wrong core Event IDs={orphan_wrong_event}")
    if len(joined)!=expected_rows["ExtendedMeasurementOrFact"]:
        raise ValueError("JOIN_STOP lost originally published eMoF rows")
    return joined,events,occurrences,count_by_event


def summarize(joined,events,occurrences,count_by_event,sha):
    status=Counter(r["eligibility"] for r in joined)
    qtypes=Counter(r["organismQuantityType_original"] or "<EMPTY>" for r in joined)
    precision=Counter(r["measurementAccuracy_original"] or "<EMPTY>" for r in joined)
    unit=Counter(r["measurementUnit_original"] or "<EMPTY>" for r in joined)
    types=Counter(r["measurementType"] or "<EMPTY>" for r in joined)
    ntyped={r["organismQuantity_raw"] for r in joined}
    eligible=[r for r in joined if r["eligibility"]=="ELIGIBLE_NEST_RECORD_ONLY"]
    sitespecies_year=defaultdict(list)
    site_years=defaultdict(set)
    matched_species=Counter()
    for r in eligible:
        sp=r["scientificName_accepted"]
        site=r["site_id_original"]
        year=r["parsed_year"]
        sitespecies_year[(site,sp,year)].append(r)
        site_years[(site,sp)].add(year)
        matched_species[sp]+=1
    duplicates={key:value for key,value in sitespecies_year.items() if len(value)>1}
    positive=sum(float(r["nest_numeric_candidate"])>0 for r in eligible)
    explicit_zero=sum(float(r["nest_numeric_candidate"])==0 for r in eligible)
    year_n=Counter(r["parsed_year"] for r in eligible)
    site_species_repeated=Counter()
    for (site,species),ys in site_years.items():
        if len(ys)>=2:site_species_repeated[species]+=1

    return {
        "status":"ORIGINAL_APBP_NEST_RECORD_QA_NO_ENVIRONMENT_EFFECT",
        "source_doi":SOURCE_DOI,"source_version":"2.3",
        "source_sha256":sha,
        "relation":"eMoF original occurrenceID → uniquely identifiable occurrence → verified shared original Event core",
        "source_rows":{"Event":len(events),"Occurrence":len(occurrences),
                       "ExtendedMeasurementOrFact":len(joined)},
        "original_events_with_multiple_species_or_occurrences":
            sum(value>1 for value in count_by_event.values()),
        "original_organism_quantity_types":dict(qtypes.most_common(35)),
        "original_measurement_units":dict(unit.most_common(30)),
        "original_precision_values":dict(precision.most_common(35)),
        "measurement_types":dict(types),
        "eligibility_by_original_measurement":dict(status),
        "eligible_nest_records_by_taxon":dict(sorted(matched_species.items())),
        "eligible_nest_rows":len(eligible),
        "explicit_measured_nest_zeros":explicit_zero,
        "positive_nest_records":positive,
        "unique_site_species_years":len(sitespecies_year),
        "same_site_species_year_duplicate_groups":len(duplicates),
        "same_site_species_year_duplicate_record_rows":
            sum(len(z) for z in duplicates.values()),
        "site_species_histories_with_2plus_distinct_years":
            sum(len(ys)>=2 for ys in site_years.values()),
        "site_species_histories_with_5plus_distinct_years":
            sum(len(ys)>=5 for ys in site_years.values()),
        "repeated_2plus_year_site_species_histories_by_taxon":
            dict(sorted(site_species_repeated.items())),
        "eligible_year_range":[min(year_n),max(year_n)] if year_n else None,
        "study_value_interpretation":{
            "original_source_event_key":"not equivalent to a site-year abundance replicate",
            "island_group":"publisher geographical group only, NOT a georeferenced island identifier",
            "eligible_count":"a measured nest/breeding-pair source candidate, not a corrected true abundance estimate",
            "observed_zero":"only directly supplied zero nest rows, not inferred non-observation",
            "duplicate_count":"all retained: no best-looking event chosen",
        },
        "environmental_covariates_joined":False,
        "penguin_ecological_slopes_or_pvalues_fitted":0,
    }


def export_csv(rows,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=COLUMNS,extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",required=True)
    p.add_argument("--out-csv",required=True)
    args=p.parse_args()
    out=Path(args.out_json)
    out.parent.mkdir(parents=True,exist_ok=True)
    try:
        source=fetch_original()
        rows,events,occurrences,eventgroup=raw_join(source)
        result=summarize(rows,events,occurrences,eventgroup,hashlib.sha256(source).hexdigest())
        export_csv(rows,Path(args.out_csv))
        result["derived_csv_sha256"]=hashlib.sha256(Path(args.out_csv).read_bytes()).hexdigest()
        result["derived_public_record_rows"]=len(rows)
        result["derived_csv_artifact_only"]="Complete public-derived table is in CI artifact, NOT published into PR code tree."
    except Exception as exc:
        result={"status":"HOLD_ORIGINAL_SOURCE_JOIN_OR_UNIT","error_type":type(exc).__name__,
                "error":str(exc)[:450],"penguin_ecological_slopes_or_pvalues_fitted":0}
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
