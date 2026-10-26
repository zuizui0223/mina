#!/usr/bin/env python3
"""V31 original OBIS Antarctic historic penguin+flying seabird source QA.

After V30 schema confirmation; source count-stage, duplicate survey lineage,
site-year precision and zero/negative sentinel semantics audited separately.
No island/colonisation/competition or population model is fitted.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path
import re

from audit_obis_original_penguin_dwc_v30 import (
    download_source,safe_source_zip,parse_dwc_core
)

PENGUIN_GENERA={"Aptenodytes","Pygoscelis","Eudyptes"}
FLYING_GENERA={"Macronectes","Pagodroma","Thalassoica"}
RECEIPT_STATUS="OBIS_ORIGINAL_1900_1996_PENGUIN_CORE_SOURCE_AUDIT_V30"
VALUE_FIELDS=(
    "lifeStage","sex","occurrenceRemarks","dynamicProperties","preparations",
    "coordinatePrecision","georeferenceSources","georeferenceProtocol",
    "verbatimCoordinates","catalogNumber","recordNumber","otherCatalogNumbers",
    "fieldNumber","recordedBy","associatedReferences","bibliographicCitation",
    "collectionCode","institutionCode","county","stateProvince",
    "basisOfRecord","dateIdentified"
)


def source_count_class(value):
    raw=str(value or "").strip()
    if not raw:return "ORIGINAL_BLANK_UNOBSERVED_COUNT"
    try:n=float(raw.replace(",",""))
    except (ValueError,TypeError):return "ORIGINAL_NONNUMERIC_COUNT"
    if not math.isfinite(n):return "ORIGINAL_NONFINITE_COUNT"
    if n<0:
        return "SOURCE_NEGATIVE_MINUS_ONE_UNKNOWN" if n==-1 else "SOURCE_OTHER_NEGATIVE_COUNT_CODE"
    if n==0:return "ORIGINAL_REPORTED_ZERO_ABSENCE_UNVERIFIED"
    return "ORIGINAL_POSITIVE_NUMERIC_COUNT"


def source_year(row):
    raw=str(row.get("year","") or "")
    if re.fullmatch(r"(?:18|19|20)\d{2}",raw):
        return int(raw)
    value=str(row.get("eventDate","") or "")
    match=re.match(r"^((?:18|19|20)\d{2})",value)
    return int(match.group(1)) if match else None


def source_geo(row):
    try:
        lat=float(row.get("decimalLatitude",""))
        lon=float(row.get("decimalLongitude",""))
        if not(math.isfinite(lat) and math.isfinite(lon) and
               -90<=lat<=-50 and -180<=lon<=180):
            return None
        return lat,lon
    except (TypeError,ValueError):
        return None


def source_taxon_group(name):
    genus=str(name or "").split(" ",1)[0]
    if genus in PENGUIN_GENERA:return "PENGUIN"
    if genus in FLYING_GENERA:return "FLYING_SEABIRD"
    return "UNCLASSIFIED_SOURCE_TAXON"


def literal_field_profile(rows,col,limit=8):
    raw=[str(r.get(col,"") or "").strip() for r in rows]
    c=Counter(x for x in raw if x)
    return {
        "original_field_nonempty_records":sum(c.values()),
        "original_field_literal_value_count":len(c),
        "publisher_literal_field_value_examples":[
             {"value":str(a)[:150],"source_n":n} for a,n in c.most_common(limit)
        ],
        "source_field_is_verified_nest_count_stage":False
    }


def source_audit(rows,original):
    cols=list(rows[0]) if rows else []
    required={"scientificName","individualCount","year","locality",
              "decimalLatitude","decimalLongitude","core_id"}
    if not required.issubset(cols):
        raise ValueError("SCHEMA_STOP unexpected original historic OBIS required columns absent")
    expected=original.get("original_archive_row_count")
    if len(rows)!=expected or len(rows)!=2787:
        raise ValueError("SOURCE_STOP original 2787-row version corpus mismatch")
    total_class=Counter()
    by_group=defaultdict(Counter)
    by_taxon=defaultdict(Counter)
    by_year=Counter()
    place_year_species=Counter()
    geo_year_species=Counter()
    original_id=Counter()
    observed_site_years=defaultdict(set)
    observed_geo_years=defaultdict(set)
    duplicated_signatures=Counter()
    original_year_valid=0
    valid_geo=0
    source_candidate_with_count=0
    date_jan1_no_daily_effort=0
    for r in rows:
        name=str(r.get("scientificName","") or "")
        species_group=source_taxon_group(name)
        state=source_count_class(r.get("individualCount",""))
        total_class[state]+=1
        by_group[species_group][state]+=1
        by_taxon[name][state]+=1
        y=source_year(r)
        place=str(r.get("locality","") or "").strip()
        geo=source_geo(r)
        if y is not None:
            original_year_valid+=1
            by_year[y]+=1
        if geo is not None:
            valid_geo+=1
        if y is not None and place and name:
            place_year_species[(place,name,y)]+=1
        if y is not None and geo is not None and name:
            geo_year_species[(geo,name,y)]+=1
        if state=="ORIGINAL_POSITIVE_NUMERIC_COUNT" and y is not None and place and name:
            observed_site_years[(place,name)].add(y)
            if geo is not None:
                observed_geo_years[(geo,name)].add(y)
                source_candidate_with_count+=1
        rawid=str(r.get("core_id","") or "")
        if rawid:original_id[rawid]+=1
        original_date=str(r.get("eventDate","") or "")
        if re.match(r"^(?:18|19|20)\d{2}-01-01",original_date):
            date_jan1_no_daily_effort+=1
        sig=(name,y,place,geo,str(r.get("individualCount","") or ""),
             str(r.get("catalogNumber","") or ""),
             str(r.get("recordNumber","") or ""),
             str(r.get("bibliographicCitation","") or ""))
        duplicated_signatures[sig]+=1
    original_species_group_taxa={
        group:sorted(t for t in by_taxon if source_taxon_group(t)==group)
        for group in ("PENGUIN","FLYING_SEABIRD","UNCLASSIFIED_SOURCE_TAXON")
    }
    positive_repeated=Counter()
    for (_site,taxon),yrs in observed_site_years.items():
        positive_repeated[(source_taxon_group(taxon),len(yrs))]+=1
    correlated={}
    for species_group in ("PENGUIN","FLYING_SEABIRD","UNCLASSIFIED_SOURCE_TAXON"):
        count=by_group[species_group]
        correlated[species_group]={
            "original_source_row_total":sum(count.values()),
            "source_classified_count_rows":dict(sorted(count.items())),
            "distinct_source_taxon_labels":original_species_group_taxa[species_group]
        }
    fields={k:literal_field_profile(rows,k)
            for k in VALUE_FIELDS if k in cols}
    duplicate_identity=sum(v-1 for v in original_id.values() if v>1)
    dup_signature=sum(v-1 for v in duplicated_signatures.values() if v>1)
    location_pair_years=sum(len(years) for years in observed_site_years.values())
    geo_pair_years=sum(len(years) for years in observed_geo_years.values())
    return {
      "status":"OBIS_ORIGINAL_HISTORIC_PENGUIN_SEABIRD_SOURCE_IDENTIFIABILITY_V31",
      "original_source_record_n":len(rows),
      "first_party_source_original_archive_SHA256":original["original_zip_SHA256"],
      "first_party_source_original_occurrence_TXT_SHA256":original["source_original_DwC_core_SHA256"],
      "first_party_original_count_value_classes":dict(sorted(total_class.items())),
      "source_penguin_flying_seabird_count_semantics_by_original_group":correlated,
      "observed_original_nonempty_year_records":original_year_valid,
      "original_source_year_distribution":dict(sorted(by_year.items())),
      "source_original_eventDates_nominal_Jan1_records_no_daily_effort":date_jan1_no_daily_effort,
      "source_original_geographically_valid_coordinate_rows":valid_geo,
      "source_positive_count_year_and_source_named_locality_plus_geo_rows":source_candidate_with_count,
      "source_locality_taxon_year_nonempty_cells":len(place_year_species),
      "source_locality_taxon_year_cells_with_multiple_source_records":
          sum(v>1 for v in place_year_species.values()),
      "source_geo_pair_taxon_year_cells":len(geo_year_species),
      "source_geo_pair_taxon_year_cells_with_multiple_records":
          sum(v>1 for v in geo_year_species.values()),
      "source_locality_taxon_combinations_with_two_or_more_positive_count_seasons":
          sum(len(v)>=2 for v in observed_site_years.values()),
      "source_loc_taxon_positive_count_distinct_site_year_cells":location_pair_years,
      "source_geo_taxon_positive_count_distinct_site_year_cells":geo_pair_years,
      "source_geo_taxon_combinations_with_two_or_more_positive_count_seasons":
          sum(len(v)>=2 for v in observed_geo_years.values()),
      "original_source_ID_unique_nonempty_n":len(original_id),
      "source_original_record_ID_repeated_extra_records":duplicate_identity,
      "source_original_full_record_signature_repeated_extra_records":dup_signature,
      "original_source_fields_and_observation_semantics":fields,
      "original_count_stage_adult_nests_breeding_pair_confirmed":False,
      "original_dataset_independent_field_lineage_from_MAPPPD_verified":False,
      "raw_source_geography_from_gazetteer_not_same_as_individual_nest_GPS":True,
      "source_original_23_zero_count_rows_as_true_searched_absence_verified":False,
      "source_original_negative_codes_are_true_absences":False,
      "individual_nests_or_islands_treated_as_independent_field_surveys":False,
      "ecological_island_breeding_model_fitted":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v30",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result={"status":"HOLD_ORIGINAL_OBIS_SOURCE_IDENTITY_V31",
            "ecological_island_breeding_model_fitted":False}
    try:
        source=json.loads(a.v30.read_text(encoding="utf-8"))
        if source["status"]!="OBIS_ORIGINAL_1900_1996_PENGUIN_CORE_SOURCE_AUDIT_V30":
            raise ValueError("SOURCE_STOP expected successful original V30 source receipt")
        blob=download_source()
        if hashlib.sha256(blob).hexdigest()!=source["original_zip_SHA256"]:
            raise ValueError("SOURCE_STOP frozen publisher ZIP SHA drift from V30 source")
        z,_=safe_source_zip(blob)
        with z:
            rows,doc=parse_dwc_core(z)
        if doc["source_original_DwC_core_SHA256"]!=source["source_original_DwC_core_SHA256"]:
            raise ValueError("SOURCE_STOP publisher core occurrence txt SHA drift")
        result=source_audit(rows,source)
        result["original_publisher_resource_url"]="https://ipt.obis.org/nonode/resource?r=iasb"
    except Exception as e:
        result["error_type"]=type(e).__name__
        result["error"]=str(e)[:1300]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):raise SystemExit(2)

if __name__=="__main__":
    main()
