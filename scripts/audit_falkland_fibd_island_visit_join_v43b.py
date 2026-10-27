#!/usr/bin/env python3
"""V43b FIG source-only island identity × invasive-mammal status × survey visit audit.

Uses public original XLS SHA pins from completed V43. No bird outcomes opened,
no raw site names/coordinates/surveyor identities emitted, no unsurveyed 0s
converted to biological absences or detection-corrected occupancy probabilities.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import math
from pathlib import Path
import re
import unicodedata

import requests
import xlrd

import audit_falkland_fibd_original_predator_v43 as original

SOURCE={
    "fibdv8-20140601-invasives":("980cb424b356e524c4c5f15f5a2ec942882530ce8b3b283719148595800205e1",1212,18),
    "fibdv8-20140601-locations":("4e87141f8819dd7b513400f166cd2a8e7369e08cdf0a8ae7d76023199fb7b56c",535,17),
    "fibdv8-20140601-visits":("1a01e2a321e7a45a07a8a864d98c8bff079fb4d789b2493c2c693eed6c562209",4965,13),
}
COMMON_TAXA=(
    "Norway rat","Brown rat","Rattus norvegicus","Black rat","Rattus rattus",
    "House mouse","Mus musculus","Feral cat","Domestic cat","Cat",
    "Patagonian fox","Lycalopex griseus","Rabbit","European rabbit","European hare",
    "Hare","Sheep","Reindeer","Guinea pig","Goat","Ferret","Mouse",
)
STATUS_WORDS={
    "present","absent","probable","probable presence","probable absence",
    "suspected present","suspected absent","possible","unknown","uncertain",
    "confirmed","confirmed presence","confirmed absence","yes","no","positive",
    "negative","not recorded","not present","inferred absent","inferred present",
    "eradicated","no evidence","breeding","nonbreeding","occasional","rare",
}
MAMMAL_PATTERN=re.compile(r"\brat\b|\bmouse\b|\bcat\b|\bfox\b|\bferret\b",re.I)
DESKTOP_PATTERN=re.compile(r"\bdesktop\b|\bgoogle\s*earth\b|\bsatellite\b|\baerial\s*photo\b",re.I)
FIELD_PATTERN=re.compile(r"\bon.?site\b|\bfield\s*survey\b|\bwalked\b|\btransect\b|\bGPS\b",re.I)


def normalized_name(value):
    """Minimal original-name join only: whitespace, Unicode and case."""
    s=unicodedata.normalize("NFKC",str(value or "")).casefold()
    return re.sub(r"\s+"," ",s).strip()


def numeric(value):
    if isinstance(value,bool):return None
    try:x=float(value)
    except (ValueError,TypeError):return None
    return x if math.isfinite(x) else None


def source_table_public(slug):
    if slug not in SOURCE:raise ValueError("OUTSIDE_FROZEN_ORIGINAL_SOURCE_SET")
    with requests.Session() as session:
        item,meta=original.get_official_package(session,slug)
        raw=original.bounded_https(session,item["url"],original.MAX_XLS_BYTES)
    digest=hashlib.sha256(raw).hexdigest()
    sha,nrows,ncols=SOURCE[slug]
    if digest!=sha:
        raise ValueError("FIBD_BINARY_SHA_CHANGED "+slug)
    book=xlrd.open_workbook(file_contents=raw,on_demand=True,ragged_rows=True)
    try:
        if book.nsheets!=1:raise ValueError("FIBD_ORIGINAL_EXPECTED_ONE_SHEET "+slug)
        sh=book.sheet_by_index(0)
        if sh.nrows!=nrows or sh.ncols!=ncols:
            raise ValueError("FIBD_ORIGINAL_SHEET_DIMENSION_CHANGED "+slug)
        result=[
            tuple(sh.cell_value(i,c) if c<sh.row_len(i) else None
                  for c in range(ncols))
            for i in range(nrows)
        ]
    finally:
        book.release_resources()
    return result,{
        "source_slug":slug,"verified_SHA256":digest,
        "source_rows_including_any_header":nrows,"source_columns":ncols,
        "public_CC_BY_SA_4_0_verified":meta["license"]=="CC-BY-SA-4.0",
        "downloaded_native_original_XLS":True,
    }


def schema_profile_invasives(rows):
    """Discover source taxon COLUMN without peeking at avian responses."""
    taxon_codes={normalized_name(x):x for x in COMMON_TAXA}
    candidates=[]
    percol=[]
    for col in range(len(rows[0])):
        vals=[normalized_name(row[col]) for row in rows]
        present=[v for v in vals if v]
        counter=Counter(present)
        spp={v:n for v,n in counter.items() if v in taxon_codes}
        safe_status={v:n for v,n in counter.items() if v in STATUS_WORDS}
        col_observation={
            "column_1indexed":col+1,
            "nonempty":len(present),
            "original_distinct_values":len(counter),
            "count_of_known_mammal_species_names":sum(spp.values()),
            "known_common_mammal_taxa":{taxon_codes[v]:n for v,n in spp.items() if n>0},
            "repeated_explicit_status_vocabulary":safe_status,
            "top_frequency_safely_redacted":(
                "<REDACTED_LONG_STRING_OR_ISLAND_NAME>"
                if counter and max(counter.values())>=2
                   and not spp and not safe_status else None
            ),
        }
        percol.append(col_observation)
        if len(spp)>=2 and sum(spp.values())>=10:
            candidates.append((sum(spp.values()),col))
    candidates.sort(reverse=True)
    tax_col=None
    if len(candidates)==1 or (len(candidates)>1 and candidates[0][0]>=3*candidates[1][0]):
        tax_col=candidates[0][1]
    species=Counter()
    if tax_col is not None:
        for row in rows:
            name=normalized_name(row[tax_col])
            if name in taxon_codes:species[taxon_codes[name]]+=1
    return {
        "native_source_first_row_has_NO_EXPLICIT_HEADERS":True,
        "native_original_row_count":len(rows),
        "source_candidate_taxon_column_1indexed":tax_col+1 if tax_col is not None else None,
        "original_species_status_distributions_by_source_column":percol,
        "known_original_mammal_labels_by_source_row":dict(species),
        "all_source_blanks_are_UNKNOWN_not_negative":True,
    },tax_col


def source_location_reference(rows):
    if normalized_name(rows[0][0])!="location name":
        raise ValueError("LOCATION_NAME_ORIGINAL_FIRST_COLUMN_SCHEMA_DRIFT")
    locations=defaultdict(list)
    geometry_valid=0
    for row in rows[1:]:
        name=normalized_name(row[0])
        if not name:continue
        lat=numeric(row[4]);lon=numeric(row[5]);area=numeric(row[7])
        if (lat is not None and lon is not None and -54<=lat<=-50
            and -63<=lon<=-56):
            geometry_valid+=1
        locations[name].append((lat,lon,area))
    unique={name:xs[0] for name,xs in locations.items() if len(xs)==1}
    qa={
        "original_location_rows_excluding_header":len(rows)-1,
        "nonempty_distinct_canonical_source_location_names":len(locations),
        "unique_name_reference_islands":len(unique),
        "colliding_names_excluded_from_exact_match":sum(len(xs)>1 for xs in locations.values()),
        "WGS84_source_centroids_valid_Falklands_envelope":geometry_valid,
        "island_polygon_boundaries_not_in_original_XLS":True,
    }
    return unique,qa


def haversine_m(lat1,lon1,lat2,lon2):
    from math import radians,cos,atan2,sin,sqrt
    if any(v is None for v in (lat1,lon1,lat2,lon2)):return None
    a,b,c,d=map(radians,(lat1,lon1,lat2,lon2))
    h=sin((c-a)/2)**2+cos(a)*cos(c)*sin((d-b)/2)**2
    return 6371008.8*2*atan2(sqrt(h),sqrt(max(0,1-h)))


def infer_coordinate_columns(rows):
    candidates={"latitude":[],"longitude":[]}
    for col in range(len(rows[0])):
        values=[numeric(row[col]) for row in rows]
        lat=sum(-54<=v<=-50 for v in values if v is not None)
        lon=sum(-63<=v<=-56 for v in values if v is not None)
        if lat>=max(30,.2*len(rows)):candidates["latitude"].append((lat,col))
        if lon>=max(30,.2*len(rows)):candidates["longitude"].append((lon,col))
    return {
        "latitude_candidates":sorted(candidates["latitude"],reverse=True),
        "longitude_candidates":sorted(candidates["longitude"],reverse=True),
    }


def identify_exact_invasive_location_links(rows,locations):
    names=[normalized_name(row[0]) for row in rows]
    counts=Counter(names)
    matched=[name for name in names if name and name in locations]
    coord=infer_coordinate_columns(rows)
    lat_c=coord["latitude_candidates"];lon_c=coord["longitude_candidates"]
    lc=lat_c[0][1] if len(lat_c)==1 or (len(lat_c)>=2 and lat_c[0][0]>2*lat_c[1][0]) else None
    oc=lon_c[0][1] if len(lon_c)==1 or (len(lon_c)>=2 and lon_c[0][0]>2*lon_c[1][0]) else None
    distances=[]
    unknown_coord=0
    if lc is not None and oc is not None:
        for row in rows:
            name=normalized_name(row[0])
            if name not in locations:continue
            lat,lon,_=locations[name]
            d=haversine_m(lat,lon,numeric(row[lc]),numeric(row[oc]))
            if d is None:unknown_coord+=1
            else:distances.append(d)
    return {
        "original_invasive_record_rows":len(rows),
        "distinct_original_invasive_location_name_labels":len(counts),
        "source_invasive_rows_unique_exact_location_name_in_original_reference":len(matched),
        "original_invasive_distinct_exactly_matched_island_names":len(set(matched)),
        "unmatched_original_invasive_observation_rows":len(rows)-len(matched),
        "number_of_invasive_location_names_with_repeated_source_rows":sum(n>1 for n in counts.values()),
        "source_coordinate_candidate_column_positions":coord,
        "invasive_lat_col_1indexed":lc+1 if lc is not None else None,
        "invasive_lon_col_1indexed":oc+1 if oc is not None else None,
        "name_matched_rows_with_both_coordinates_usable":len(distances),
        "name_matched_rows_with_coordinate_unknown":unknown_coord,
        "name_matched_rows_with_coordinate_difference_le250m":sum(x<=250 for x in distances),
        "source_location_names_only_not_independent_two_period_nesting_site_identity":True,
    }


def original_visit_summary(rows,locations):
    headers=[normalized_name(x) for x in rows[0]]
    if len(headers)!=13 or headers[:2]!=["id","location name"] or headers[8]!="year":
        raise ValueError("ORIGINAL_VISIT_SCHEMA_DRIFT")
    years=Counter();notes=Counter();namecounts=Counter()
    matched=0;repeated=Counter();rat_visit_mentions=0
    for row in rows[1:]:
        name=normalized_name(row[1])
        if name and name in locations:
            matched+=1
            namecounts[name]+=1
        val=numeric(row[8])
        if val is not None and float(val).is_integer():
            years[int(val)]+=1
        note=str(row[11] or "")
        desktop=bool(DESKTOP_PATTERN.search(note))
        field=bool(FIELD_PATTERN.search(note))
        category=("AMBIGUOUS_BOTH" if desktop and field else
                  "TEXT_HINT_DESKTOP_NOT_VERIFIED_FIELD_VISIT" if desktop else
                  "TEXT_HINT_FIELD_NOT_TARGETED_PREDATOR_SURVEY" if field else
                  "UNSPECIFIED_METHOD")
        notes[category]+=1
        if MAMMAL_PATTERN.search(note):
            rat_visit_mentions+=1
    return {
        "original_visits_after_native_header":len(rows)-1,
        "original_visit_name_exactly_matched_to_unique_reference_island":matched,
        "distinct_original_exactly_matched_islands_with_any_visits":len(namecounts),
        "distinct_islands_with_multiple_original_visit_entries":sum(n>=2 for n in namecounts.values()),
        "original_year_counts":dict(sorted(years.items())),
        "survey_method_note_text_nonexclusive_hints":dict(notes),
        "source_notes_with_generic_mammal_mention_not_a_rat_detection_or_non_detection":rat_visit_mentions,
        "original_explicit_rat_survey_negative_test_results_detected":False,
        "island_visit_does_NOT_imply_targeted_mammal_negative":True,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    result={
      "status":"FIBD_V43B_ORIGINAL_SOURCE_NEEDS_GEOGRAPHIC_IDENTITY_JOIN",
      "frozen_contract":"contracts/ISLAND_PREDATOR_FALKLAND_FIBD_V43B_FIELD_JOIN_SOURCE_ONLY.md",
      "original_FIBD_first_party_three_sources":list(SOURCE),
      "original_statistical_mammal_true_occupancy_fitted":False,
      "original_bird_breeding_outcomes_opened":False,
      "no_source_personal_surveyor_names_island_names_raw_notes_emitted":True,
    }
    def read(slug):
        return slug,source_table_public(slug)
    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            data=dict(pool.map(read,SOURCE))
        result["verified_original_FIG_XLS_SHA_and_shape"]={
            k:v[1] for k,v in data.items()
        }
        inv=data["fibdv8-20140601-invasives"][0]
        loc=data["fibdv8-20140601-locations"][0]
        visits=data["fibdv8-20140601-visits"][0]
        locations,qa=source_location_reference(loc)
        invasion,taxcol=schema_profile_invasives(inv)
        exact=identify_exact_invasive_location_links(inv,locations)
        visit=original_visit_summary(visits,locations)
        result.update({
            "native_source_invasive_species_and_status":invasion,
            "original_source_island_location_qa":qa,
            "original_invasive_to_source_island_exact_join_qa":exact,
            "original_visits_to_location_qa":visit,
            "status":"FIBD_V43B_ISLAND_INVASIVE_VISIT_ORIGINAL_SOURCE_JOIN_AUDITED",
            "field_surveyed_rat_non_detection_records_confirmed":False,
            "ecological_occupancy_likelihood_identified":False,
            "scientific_decision":"SOURCE_SPATIAL_AND_SURVEY_METADATA_ONLY; no verified rat-negative visit/station effort or measured detection probabilities; true occupancy probability remains NOT_IDENTIFIED."
        })
    except Exception as exc:
        result["status"]="FIBD_V43B_ORIGINAL_SOURCE_JOIN_HOLD"
        result["error"]=type(exc).__name__+": "+str(exc)[:480]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]!="FIBD_V43B_ISLAND_INVASIVE_VISIT_ORIGINAL_SOURCE_JOIN_AUDITED":
        raise SystemExit(2)

if __name__=="__main__":
    main()
