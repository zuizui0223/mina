#!/usr/bin/env python3
"""Paper2 V47: native Falkland Islands Government bird x invasion x visit coverage.

This audits OBSERVED bird guild breeding records (penguin vs volant seabirds)
within the same published island/year using four original SHA-pinned FIBD XLS.
No bird ecological regression, no assumed absences, no true mammal occupancy,
no source site/observer identities in output. Raw public source stays ephemeral.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlparse

import requests
import xlrd

HOST="dataportal.saeri.org"
ROOT="https://dataportal.saeri.org"
SOURCE={
 "fibdv8-20140601-locations":("4e87141f8819dd7b513400f166cd2a8e7369e08cdf0a8ae7d76023199fb7b56c",535,17),
 "fibdv8-20140601-birds":("207065a69d8b16d5f5c7889bfff40912fe6660ca2947e937317094eb23625103",4959,26),
 "fibdv8-20140601-invasives":("980cb424b356e524c4c5f15f5a2ec942882530ce8b3b283719148595800205e1",1212,18),
 "fibdv8-20140601-visits":("1a01e2a321e7a45a07a8a864d98c8bff079fb4d789b2493c2c693eed6c562209",4965,13),
}
MAX_BYTES=8_000_000
MIN_YEAR=1997
MAX_YEAR=2013
PENGUIN=re.compile(r"\bpenguin\b",re.I)
VOLANT=re.compile(r"\b(?:albatross|petrel|prion|shearwater|skua|gull|tern|cormorant|shag|fulmar)\b",re.I)
CONFIRMED_BREED={
 "breeding","confirmed breeding","breeding confirmed",
 "confirmed breeder","breeding pairs","confirmed breeding pairs",
}
STATUS_ALLOW={
 "breeding","confirmed breeding","breeding confirmed","confirmed breeder",
 "breeding pairs","confirmed breeding pairs","probable breeding","possibly breeding",
 "possible breeding","probably breeding","non breeding","non-breeding",
 "not breeding","not known","unknown","uncertain","present","absent",
 "yes","no","breeding?","possible","probable","confirmed","b","pb",
 "cb","nb","n","p","a","1","0","2","3","4",
}
RAT_NAMES={"norway rat","brown rat","rattus norvegicus"}
MOUSE_NAMES={"house mouse","mus musculus"}
CAT_NAMES={"cat","feral cat","domestic cat","felis catus"}
DESKTOP_TERMS=re.compile(r"\bdesktop\b|\bgoogle\s*earth\b|\baerial imagery\b|\bsatellite\b",re.I)
FIELD_TERMS=re.compile(r"\bfield survey\b|\bon.?site\b|\btransect\b|\bwalked\b|\bGPS\b",re.I)


def norm(value):
    return " ".join(unicodedata.normalize("NFKC",str(value or "")).casefold().split())


def read_url(session,url,maxbytes):
    """Read the SAME verified original publisher URL; retry truncated transport only."""
    parsed=urlparse(url)
    if parsed.hostname!=HOST or parsed.scheme not in ("http","https"):
        raise ValueError("SOURCE_UNAPPROVED_HOST")
    if parsed.scheme=="http":
        url=parsed._replace(scheme="https").geturl()
    import time
    last=None
    for attempt in range(3):
        try:
            with session.get(
                url,stream=True,timeout=(15,75),
                headers={"User-Agent":"mina-Paper2-Falklands-FIBD-source-only-V47/1.0"},
                allow_redirects=True
            ) as r:
                r.raise_for_status()
                target=urlparse(r.url)
                if target.scheme!="https" or target.hostname!=HOST:
                    raise ValueError("SOURCE_REDIRECT_NOT_FIRST_PARTY_HTTPS")
                chunks=[];size=0
                for chunk in r.iter_content(chunk_size=131072):
                    size+=len(chunk)
                    if size>maxbytes:
                        raise ValueError("SOURCE_TOO_LARGE")
                    chunks.append(chunk)
                return b"".join(chunks)
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError) as e:
            last=e
            if attempt==2:
                break
            time.sleep(1+attempt)
    raise ValueError(
        "SOURCE_PUBLIC_TRANSPORT_INCOMPLETE_AFTER_3_ATTEMPTS_"
        +type(last).__name__
    )


def fetch_first_party_workbook(slug):
    if slug not in SOURCE:
        raise ValueError("UNFROZEN_DATASET")
    with requests.Session() as session:
        doc=json.loads(read_url(session,ROOT+"/api/3/action/package_show?id="+slug,2_000_000))
        if not doc.get("success"):
            raise ValueError("SOURCE_REGISTRY_QUERY_FAILED")
        x=doc["result"]
        if x.get("private") is not False or x.get("name")!=slug:
            raise ValueError("SOURCE_IS_PRIVATE_OR_SLUG_CHANGED")
        if x.get("license_id")!="CC-BY-SA-4.0":
            raise ValueError("SOURCE_REUSE_LICENCE_CHANGED")
        resources=[]
        for r in x.get("resources",[]):
            if (str(r.get("format","")).lower()!="xls"
                or not str(r.get("name","")).lower().endswith(".xls")
                or r.get("state") not in ("active",None)):
                continue
            access=r.get("restricted") or "{}"
            if isinstance(access,str):
                try:access=json.loads(access)
                except json.JSONDecodeError:continue
            if access and access.get("level")!="public":continue
            resources.append(r)
        if len(resources)!=1:
            raise ValueError("EXPECTED_EXACT_ONE_FIRST_PARTY_PUBLIC_XLS")
        r=resources[0]
        if r.get("size") and int(r["size"])>MAX_BYTES:
            raise ValueError("FIRST_PARTY_ORIGINAL_SOURCE_SIZE_LIMIT")
        raw=read_url(session,str(r["url"]),MAX_BYTES)
    source_sha,nrows,ncols=SOURCE[slug]
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=source_sha:
        raise ValueError("ORIGINAL_XLS_SHA_PIN_FAILED_"+slug)
    book=xlrd.open_workbook(file_contents=raw,ragged_rows=True,on_demand=True)
    try:
        if book.nsheets!=1:raise ValueError("ORIGINAL_FIBD_WORKSHEET_COUNT_CHANGED")
        sheet=book.sheet_by_index(0)
        if (sheet.nrows,sheet.ncols)!=(nrows,ncols):
            raise ValueError("ORIGINAL_FIBD_ROW_COLUMN_SCHEMA_CHANGED")
        rows=[
            tuple(sheet.cell_value(i,c) if c<sheet.row_len(i) else None
                  for c in range(ncols))
            for i in range(nrows)
        ]
    finally:
        book.release_resources()
    return slug,rows,{
      "slug":slug,"original_SHA256":sha,"original_rows":nrows,
      "original_columns":ncols,"first_party_licence":"CC-BY-SA-4.0",
      "raw_source_rows_committed":False
    }


def intval(v):
    if isinstance(v,bool):return None
    try:
        x=float(v)
    except (ValueError,TypeError):return None
    if not math.isfinite(x) or not x.is_integer():return None
    return int(x)


def source_date(row,d,m,y):
    year=intval(row[y])
    if year is None or year<MIN_YEAR or year>MAX_YEAR:return None,None
    day=intval(row[d]);month=intval(row[m])
    if day is None or month is None:
        return year,None
    try:
        from datetime import date
        return year,date(year,month,day).isoformat()
    except ValueError:
        return year,None


def bird_guild(name):
    v=norm(name)
    if PENGUIN.search(v):return "PENGUIN_FLIGHTLESS"
    if VOLANT.search(v):return "SEABIRD_FLYING"
    return "OTHER_OR_AMBIGUOUS"


def original_breeding_status(v):
    x=norm(v)
    if x in CONFIRMED_BREED:return "DEFINITE_RECORDED_BREEDING"
    if not x:return "SOURCE_BLANK_UNKNOWN"
    return "UNVERIFIED_OR_NOT_DEFINITE"


def safe_status_hist(values):
    c=Counter(norm(v) or "<BLANK>" for v in values)
    approved={k:int(n) for k,n in c.items()
              if k in STATUS_ALLOW or k=="<BLANK>"}
    return {
      "total_source_rows":sum(c.values()),
      "literal_predefined_nonidentifying_codes":dict(sorted(approved.items())),
      "uninterpreted_source_code_or_text_rows":int(sum(c.values())-sum(approved.values())),
      "total_source_unique_literal_categories":len(c),
      "original_raw_free_text_disclosed":False,
    }


def locations_source(rows):
    hdr=[norm(x) for x in rows[0]]
    if not (hdr[0]=="location name" and hdr[1]=="wider area" and hdr[4]=="latitude"
            and hdr[5]=="longitude"):
        raise ValueError("SOURCE_LOCATION_ORIGINAL_SCHEMA_CHANGED")
    ids=defaultdict(list)
    for r in rows[1:]:
        name=norm(r[0])
        if name:
            ids[name].append({
              "wider_area":norm(r[1]),
              "area_ha":r[7],
              "lat":r[4],"lon":r[5],
            })
    uniques={k:v[0] for k,v in ids.items() if len(v)==1}
    return uniques,{
      "source_locations_excluding_header":len(rows)-1,
      "unique_normalized_named_source_island_locations":len(uniques),
      "ambiguous_or_duplicate_source_place_names_excluded":sum(len(x)!=1 for x in ids.values()),
      "original_island_names_exported":False
    }


def visits_source(rows,loc):
    h=[norm(x) for x in rows[0]]
    if h[:2]!=["id","location name"] or h[6:9]!=["day","month","year"]:
        raise ValueError("SOURCE_VISITS_ORIGINAL_SCHEMA_CHANGED")
    by_yr=defaultdict(list)
    by_date=defaultdict(list)
    qa=Counter();method=Counter()
    for r in rows[1:]:
        name=norm(r[1])
        if name not in loc:
            qa["original_visit_unresolved_source_place"]+=1
            continue
        year,day=source_date(r,6,7,8)
        if year is None:
            qa["original_visit_outside_reliable_1997_2013_window"]+=1
            continue
        record=(name,year)
        by_yr[record].append(1)
        if day:
            by_date[(name,day)].append(1)
        note=str(r[11] or "")
        desktop=bool(DESKTOP_TERMS.search(note))
        field=bool(FIELD_TERMS.search(note))
        cat=("BOTH_DESKTOP_AND_FIELD_TEXT_HINT" if desktop and field
             else "DESKTOP_ASSESSMENT_HINT" if desktop
             else "FIELD_METHOD_HINT_NOT_TARGETED_MAMMAL_SURVEY" if field
             else "UNSPECIFIED_METHOD")
        method[cat]+=1
        qa["original_visit_source_matched_window"]+=1
    return set(by_yr),set(by_date),{
      "source_visit_rows_excluding_header":len(rows)-1,
      **dict(qa),
      "matched_distinct_island_year_visit_opportunities":len(by_yr),
      "matched_distinct_island_date_visit_opportunities":len(by_date),
      "visit_method_from_free_notes_nonexclusive_hints":dict(method),
      "visit_not_proof_of_targeted_mammal_non_detection":True
    }


def birds_source(rows,loc,visited_year,visited_date):
    h=[norm(x) for x in rows[0]]
    required={0:"location name",7:"english name",9:"day",10:"month",11:"year",
              13:"presence",16:"breeding status",21:"time surveying"}
    for i,name in required.items():
        if h[i]!=name:
            raise ValueError(f"ORIGINAL_BIRD_SOURCE_HEADER_CHANGED_{i+1}_{name}")
    by_year=defaultdict(lambda:defaultdict(list))
    by_date=defaultdict(lambda:defaultdict(list))
    all_status=defaultdict(list)
    species=defaultdict(Counter)
    qa=Counter();bird_year_guilds=defaultdict(set)
    for r in rows[1:]:
        g=bird_guild(r[7])
        qa["bird_source_all_rows"]+=1
        qa["bird_guild_"+g]+=1
        if g=="OTHER_OR_AMBIGUOUS":continue
        name=norm(r[0])
        if name not in loc:
            qa["bird_source_unmatched_source_island"]+=1
            continue
        y,dt=source_date(r,9,10,11)
        if y is None:
            qa["bird_source_valid_guild_year_missing_or_outside_source_window"]+=1
            continue
        status=original_breeding_status(r[16])
        species[g][norm(r[7])]+=1
        all_status[g].append(r[16])
        row={"status":status,"species":norm(r[7]),"observed_day":bool(dt),
             "original_presence_source_code":norm(r[13]),"source_time_surveying_nonempty":bool(norm(r[21]))}
        by_year[(name,y)][g].append(row)
        if dt:
            by_date[(name,dt)][g].append(row)
    def overlap(pool,have_visit):
        both_recorded=set()
        both_definite=set()
        with_visit=set()
        species_guild=defaultdict(set)
        for key,group in pool.items():
            if all(group.get(g) for g in ("PENGUIN_FLIGHTLESS","SEABIRD_FLYING")):
                both_recorded.add(key)
                if all(any(p["status"]=="DEFINITE_RECORDED_BREEDING" for p in group[g])
                       for g in ("PENGUIN_FLIGHTLESS","SEABIRD_FLYING")):
                    both_definite.add(key)
                    for g in ("PENGUIN_FLIGHTLESS","SEABIRD_FLYING"):
                        species_guild[g].update(
                            x["species"] for x in group[g]
                            if x["status"]=="DEFINITE_RECORDED_BREEDING")
                    if key in have_visit:with_visit.add(key)
        return both_recorded,both_definite,with_visit,species_guild
    year_any,year_def,year_with_visit,year_sp=overlap(by_year,visited_year)
    day_any,day_def,day_with_visit,day_sp=overlap(by_date,visited_date)
    regions={loc[isl]["wider_area"] for isl,_ in year_with_visit
             if loc[isl]["wider_area"]}
    event_summary={
      "original_bird_records_after_native_header":len(rows)-1,
      "classed_flightless_penguin_source_records":qa["bird_guild_PENGUIN_FLIGHTLESS"],
      "classed_flying_seabird_source_records":qa["bird_guild_SEABIRD_FLYING"],
      "other_bird_source_records_without_breeding_flight_guild":qa["bird_guild_OTHER_OR_AMBIGUOUS"],
      "original_distinct_guild_species_labels_by_source":{
          g:len(c) for g,c in species.items()},
      "safe_repeated_bird_english_names_in_original_guilds":{
          g:{n:k for n,k in c.items() if k>=5 and len(n)<=65
             and re.fullmatch(r"[a-z0-9 .()'/+-]+",n)}
          for g,c in species.items()},
      "all_bird_guild_source_breeding_status_literal_frequency":{
          g:safe_status_hist(vals) for g,vals in all_status.items()},
      "bird_source_year_site_opportunities_with_either_class":len(by_year),
      "bird_source_same_island_year_BOTH_guilds_ANY_recorded":len(year_any),
      "bird_source_same_island_year_BOTH_guilds_DEFINITE":len(year_def),
      "bird_source_same_island_year_BOTH_guilds_DEFINITE_and_visit_same_year":len(year_with_visit),
      "bird_source_distinct_islands_BOTH_guilds_DEFINITE_and_visit":len({a for a,y in year_with_visit}),
      "bird_source_distinct_publisher_wider_area_regions_for_same_year_pairs":len(regions),
      "bird_source_same_island_day_BOTH_guilds_ANY_recorded":len(day_any),
      "bird_source_same_island_day_BOTH_guilds_DEFINITE":len(day_def),
      "bird_source_same_island_day_BOTH_guilds_DEFINITE_AND_same_day_original_visit":len(day_with_visit),
      "definite_same_year_pairs_distinct_species_by_guild":{
          g:len(s) for g,s in year_sp.items()},
      "guild_date_checks":dict(qa),
      "source_2014_XLS_sample_is_not_all_Falkland_islands_surveyed":True,
      "blank_species_no_observed_record_NOT_absent":True,
      "matched_year_not_proven_same_seabird_detection_protocol":True,
    }
    source_gate=(len(year_with_visit)>=20 and
                 len({a for a,y in year_with_visit})>=10 and
                 len(regions)>=2 and
                 all(len(year_sp.get(g,set()))>=2
                     for g in ("PENGUIN_FLIGHTLESS","SEABIRD_FLYING")))
    event_summary["G1_predeclared_both_definite_guild_sample_gate_pass"]=bool(source_gate)
    # Private, ephemeral return only for matched-source positive overlap counts; never saved.
    return event_summary,year_with_visit,day_with_visit


def invasives_source(rows,loc,matched_years):
    # Original invasion workbook NO HEADERS, each row is a source record.
    if not rows or any(len(row)!=18 for row in rows):
        raise ValueError("SOURCE_INVADER_EXPECTED_18_COLUMN_HEADERLESS_ROWS")
    taxa=Counter()
    matched=defaultdict(Counter)
    codecols=defaultdict(list)
    infer_years=Counter()
    for r in rows:
        tax=norm(r[7])
        if tax in RAT_NAMES:family="NORWAY_RAT_LITERAL_SOURCE_RECORD"
        elif tax in MOUSE_NAMES:family="HOUSE_MOUSE_LITERAL_SOURCE_RECORD"
        elif tax in CAT_NAMES:family="CAT_LITERAL_SOURCE_RECORD"
        else:continue
        taxa[family]+=1
        island=norm(r[0])
        if island not in loc:continue
        matched[island][family]+=1
        for j in range(8,15):
            v=norm(r[j])
            if v in STATUS_ALLOW or v in ("<blank>",""):
                codecols[j+1].append(v or "<BLANK>")
            else:
                codecols[j+1].append("<UNRECOGNIZED_NOT_PUBLISHED>")
            num=intval(r[j])
            if num is not None and MIN_YEAR<=num<=MAX_YEAR:
                infer_years[j+1]+=1
    matched_islands={isl for isl,y in matched.items() if y["NORWAY_RAT_LITERAL_SOURCE_RECORD"]>0}
    overlap={isl for isl,yr in matched_years if isl in matched_islands}
    return {
      "original_predator_record_rows_per_taxon_not_occupied_islands":dict(taxa),
      "original_distinct_source_island_names_with_any_mammal_label":len(matched),
      "original_distinct_islands_with_Norway_rat_SOURCE_RECORD_not_confirmation":len(matched_islands),
      "same_year_guild_definite_eligible_islands_with_any_Norway_rat_RECORD":len(overlap),
      "source_original_invasion_columns_9_to_15_safe_literal_code_profile":{
          str(k):dict(Counter(v)) for k,v in codecols.items()},
      "source_invasion_possible_calendar_year_field_candidate_columns_9_to_15":dict(infer_years),
      "source_invasion_rows_are_NOT_surveyed_true_predator_absence":True,
      "published_Norway_rat_unsurveyed_desktop_inferred_absence_exists":True,
      "source_original_mammal_field_verified_positive_and_negative_same_year_pair_support":False,
      "G2_original_matched_mammal_surveyed_positive_and_negative_gate_pass":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    result={
       "schema":"MINA_PAPER2_FALKLAND_FIBD_V47_OBSERVED_BREEDING_SOURCE_GATE",
       "status":"V47_FIRST_PARTY_SOURCE_ACQUISITION_HOLD",
       "as_of":"2026-10-27",
       "contract":"contracts/PAPER2_FALKLAND_FIBD_GUILD_BREEDING_SOURCE_V47_FROZEN.md",
       "no_original_mammal_absences_imputed":True,
       "no_raw_sensitive_island_or_surveyor_names_or_coordinates_exported":True,
       "no_bird_species_or_mammal_causal_effect_fitted":True,
       "no_199_regression_or_OOB_specification_tuned_after_reading_new_guild_results":True,
    }
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            data={slug:(rows,manifest) for slug,rows,manifest in
                  executor.map(fetch_first_party_workbook,SOURCE)}
        result["publisher_verified_original_XLS_source_pins"]={
            k:v[1] for k,v in data.items()}
        loc,locq=locations_source(data["fibdv8-20140601-locations"][0])
        yr,dates,visq=visits_source(data["fibdv8-20140601-visits"][0],loc)
        bird,paired,paired_day=birds_source(data["fibdv8-20140601-birds"][0],loc,yr,dates)
        mammal=invasives_source(data["fibdv8-20140601-invasives"][0],loc,paired)
        result["original_island_geometry_identifier_QA"]=locq
        result["original_visit_survey_effort_QA"]=visq
        result["original_flightless_v_flying_recorded_breeding_support"]=bird
        result["original_invasion_status_QA_without_assumed_absence"]=mammal
        result["gate_summary"]={
            "G1_recorded_both_guild_definite_breeding_sample":
                bird["G1_predeclared_both_definite_guild_sample_gate_pass"],
            "G2_field_confirmed_true_mammal_present_and_surveyed_negative":
                mammal["G2_original_matched_mammal_surveyed_positive_and_negative_gate_pass"],
            "G3_same_day_and_coverage_surveyed_flight_guild_interaction":
                bool(bird["bird_source_same_island_day_BOTH_guilds_DEFINITE_AND_same_day_original_visit"]>=10
                     and False), # no proven true negative or common coverage denominators
            "ALL_gates_for_predator_flightless_interaction_fitting":False,
        }
        result["status"]="V47_ORIGINAL_FALKLAND_SOURCE_BREEDING_GUILD_OVERLAP_AUDITED"
        result["scientific_decision"]=(
            "SOURCE_COMPARABILITY_ONLY: positive bird breeding records may share island/year, "
            "but mammalian rat absences include unsurveyed assessments and bird absence/effort "
            "is not validated; STOP ecological predator×flight effect regardless of number of rows."
        )
    except Exception as exc:
        result["status"]="V47_ORIGINAL_SOURCE_OR_SCHEMA_HOLD"
        result["error"]=type(exc).__name__+": "+str(exc)[:750]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]!="V47_ORIGINAL_FALKLAND_SOURCE_BREEDING_GUILD_OVERLAP_AUDITED":
        raise SystemExit(2)


if __name__=="__main__":
    main()
