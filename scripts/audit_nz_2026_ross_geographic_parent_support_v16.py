#!/usr/bin/env python3
"""Author-source geography audit: 40 location rows vs 39 original count sites.

Uses location XLSX from NZ publisher resource ID f82... with *no published
MD5*: record SHA256 only, never claim original-hash authentication.
Uses census official MD5 195a... explicitly verified before parsing.
Coordinates are approximate text DMS SITE LABELS, not breeding boundaries.
Never claim separate capes are separate islands.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlencode
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_nz_2026_ross_39_colony_census_source_v13 as base
import audit_nz_39_colony_location_source_v15 as location

YEARS=(1999,2001,2005,2024)

def norm(s):
    return re.sub(r"\s+"," ",str(s or "").strip().lower())

def dms(text,axis):
    # Original source uses approximate degrees+minutes such as 77°14'S,
    # and sometimes typographic right single quotation mark 66°39’S.
    s=str(text or "").strip().upper().replace("’","'").replace("′","'").replace("‘","'")
    m=re.fullmatch(r"(\d{1,3})\s*[°º]\s*(\d{1,2})\s*['\s]*([NSEW])",s)
    if m is None:
        return None
    deg,minutes,hem=int(m[1]),int(m[2]),m[3]
    if axis=="latitude" and hem not in ("N","S"):return None
    if axis=="longitude" and hem not in ("E","W"):return None
    if minutes>=60 or (axis=="latitude" and deg>90) or (axis=="longitude" and deg>180):
        return None
    return (deg+minutes/60)*(-1 if hem in ("W","S") else 1)

def location_rows(raw):
    rows=base.workbook_first_table(raw)["rows"]
    locations={}
    for row in rows:
        if not row or not row.get(0):
            continue
        # The published "Colony locations" workbook has NO header; col A
        # is named site and col B is descriptor, C/D are textual DMS values.
        name=str(row.get(0,"")).strip()
        if len(row)<4:
            raise ValueError("Site location line lacks one of four source fields")
        key=norm(name)
        if key in locations:
            raise ValueError("Duplicate original source name in location table")
        lat=dms(row.get(2),"latitude")
        lon=dms(row.get(3),"longitude")
        locations[key]={
            "site":name,"parent_geographic_descriptor":str(row.get(1,"")).strip(),
            "latitude_source_text":str(row.get(2,"")).strip(),
            "longitude_source_text":str(row.get(3,"")).strip(),
            "lat":lat,"lon":lon
        }
    return locations

def audited_census_siteyears(raw):
    if hashlib.md5(raw).hexdigest()!=base.SOURCE_MD5:
        raise ValueError("Original census MD5 mismatch; no count extraction")
    rows=base.workbook_first_table(raw)["rows"]
    head=next((i for i,row in enumerate(rows[:18]) if
       any(str(x).strip().lower()=="colony" for x in row.values()) and
       sum(str(x).strip().isdigit() and int(str(x).strip()) in range(1981,2025)
           for x in row.values())>=25),None)
    if head is None:raise ValueError("Original census source year header not found")
    mapping={k:int(str(v).strip()) for k,v in rows[head].items()
             if str(v).strip().isdigit() and int(str(v).strip()) in YEARS}
    if set(mapping.values())!=set(YEARS):
        raise ValueError("Missing requested source year for geographic census audit")
    col=next(k for k,v in rows[head].items() if str(v).strip().lower()=="colony")
    output={}
    for row in rows[head+1:]:
        name=str(row.get(col,"")).strip()
        if not name or name.lower().startswith(("total","sum of","grand total")):
            continue
        key=norm(name)
        if key in output:raise ValueError("Duplicate 39-site official census name")
        values={}
        for ci,yr in mapping.items():
            v=str(row.get(ci,"")).strip()
            if not v:
                values[yr]=None
                continue
            try:x=float(v.replace(",",""))
            except ValueError:
                raise ValueError("Non-numeric source text in fixed comparison years")
            if x<0 or int(x)!=x:raise ValueError("Invalid count in geographic audit")
            values[yr]=int(x)
        output[key]={"name":name,"values":values}
    if len(output)!=39:raise ValueError("Expected 39 actual publisher count-site rows")
    return output

def compare(loc,census):
    loc_only=sorted(set(loc)-set(census))
    census_only=sorted(set(census)-set(loc))
    matched=sorted(set(loc)&set(census))
    parent=defaultdict(list)
    coord=defaultdict(list)
    year_by_parent=defaultdict(lambda:{y:{"surveyed_numeric":0,"zero":0,"positive":0} for y in YEARS})
    for key in matched:
        rec=loc[key]
        descriptor=rec["parent_geographic_descriptor"] or "UNKNOWN_DESCRIPTOR"
        parent[descriptor].append(rec["site"])
        if rec["lat"] is not None and rec["lon"] is not None:
            coord[(rec["lat"],rec["lon"])].append(rec["site"])
        for yr, n in census[key]["values"].items():
            if n is None:continue
            year_by_parent[descriptor][yr]["surveyed_numeric"]+=1
            year_by_parent[descriptor][yr]["zero" if n==0 else "positive"]+=1
    duplicate_geocode=[
        {"coordinate_approx":list(pos),"site_labels":sorted(sites)}
        for pos,sites in coord.items() if len(sites)>1
    ]
    all_census_numeric_counts_by_year={
        str(year):sum(census[k]["values"][year] is not None for k in census)
        for year in YEARS
    }
    all_census_numeric_site_names_by_year={
        str(year):sorted(census[k]["name"] for k in census
                         if census[k]["values"][year] is not None)
        for year in YEARS
    }
    matched_2024_sites=[k for k in matched if census[k]["values"][2024] is not None]
    matched_2024_parent_descriptors=sorted(set(
        loc[k]["parent_geographic_descriptor"] for k in matched_2024_sites))
    paircounts={f"{a}_{b}":sum(
       census[k]["values"][a] is not None and census[k]["values"][b] is not None
       for k in matched) for a,b in [(1999,2024),(2001,2024),(2005,2024)]}
    return {
        "status":("EXACT_AUTHOR_2026_LOCATION_COUNTS_CROSSWALK_GEOGRAPHY_NOT_CAUSAL"
                  if len(census_only)==0 else
                  "PARTIAL_LITERAL_SOURCE_NAME_CROSSWALK_NO_GUESSED_SYNONYMS"),
        "published_2026_count_sites":len(census),
        "official_location_rows":len(loc),
        "literal_name_matched_sites":len(matched),
        "only_in_location_not_census":[loc[k]["site"] for k in loc_only],
        "only_in_census_not_location":[census[k]["name"] for k in census_only],
        "parent_geographic_descriptor_membership":{
           p:sorted(vals) for p,vals in sorted(parent.items())},
        "named_2026_census_sites_with_unparseable_source_DMS":[
           loc[k]["site"] for k in matched if loc[k]["lat"] is None or loc[k]["lon"] is None],
        "distinct_site_labels_with_identical_source_representative_DMS":duplicate_geocode,
        "year_site_sample_coverage_by_geographic_descriptor":{
           p:{str(yr):vals for yr,vals in sorted(y.items())}
           for p,y in sorted(year_by_parent.items())},
        "n_site_pairs_with_valid_both_years":paircounts,
        "all_39_census_site_numeric_coverage_by_selected_year":all_census_numeric_counts_by_year,
        "all_39_census_site_names_with_numeric_records_by_year":all_census_numeric_site_names_by_year,
        "matched_2024_parent_geographic_descriptors":matched_2024_parent_descriptors,
        "2024_geographic_outgroup_for_Ross_with_numeric_census_exists":any(
            x!="Ross Island" for x in matched_2024_parent_descriptors),
        "exact_name_crosswalk_complete":len(census_only)==0 and len(matched)==len(census),
        "true_geographic_independent_island_count_confirmed":None,
        "geographic_descriptor_archipelago_or_peninsula_not_equated_to_island":True,
        "source_coordinate_identity_not_site_boundary_or_colony_migration":True,
        "no_immigration_recruitment_fitness_or_causal_effect_fitted":True,
        "source_date_gaps_remain_missing_not_zero":True
    }

def run():
    out={"status":"HOLD_LOCATION_SOURCE_OR_JOIN",
         "location_source_SHA256_recorded":None,
         "location_publisher_MD5_not_provided":True,
         "original_census_publisher_MD5_verified":False,
         "no_immigration_recruitment_fitness_or_causal_effect_fitted":True,
         "source_date_gaps_remain_missing_not_zero":True,
         "PR189_unmodified":True}
    try:
        locmeta=location.resource_metadata(base.fetch_bounded(location.API+"?"+urlencode({"id":location.LOC_ID}),base.MAX_SOURCE_METADATA))
        b=base.fetch_bounded(locmeta["official_url"])
        if locmeta["md5"] and hashlib.md5(b).hexdigest()!=locmeta["md5"]:
            raise ValueError("Publisher location file hash conflict")
        out["location_source_SHA256_recorded"]=hashlib.sha256(b).hexdigest()
        out["location_publisher_MD5_not_provided"]=not bool(locmeta["md5"])
        loc=location_rows(b)
        srcmeta=base.official_metadata(base.fetch_bounded(base.API+"?"+urlencode({"id":base.RESOURCE_ID}),base.MAX_SOURCE_METADATA))
        source_data=base.fetch_bounded(srcmeta["url"])
        cen=audited_census_siteyears(source_data)
        out["original_census_publisher_MD5_verified"]=True
        out.update(compare(loc,cen))
    except Exception as e:
        out["status"]="HOLD_LOCATION_GEOGRAPHIC_CROSSWALK_OR_SOURCE"
        out["error_type"]=type(e).__name__
        out["error_message"]=str(e)[:200]
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    z=run()
    args.out.write_text(json.dumps(z,indent=2,ensure_ascii=False)+"\n")
    print("GEO_V16_STATUS",z["status"])
    print("LOCATION_CENSUS_N",z.get("official_location_rows"),z.get("published_2026_count_sites"),z.get("literal_name_matched_sites"))
    print("UNMATCHED_LOCATION",z.get("only_in_location_not_census"))
    print("UNMATCHED_COUNT",z.get("only_in_census_not_location"))
    print("PARENT_DESCRIPTOR_MEMBERSHIP",json.dumps({k:len(v) for k,v in z.get("parent_geographic_descriptor_membership",{}).items()},ensure_ascii=False))
    print("SOURCE_COORDINATE_COLLISIONS",json.dumps(z.get("distinct_site_labels_with_identical_source_representative_DMS",[]),ensure_ascii=False))
    print("MATCHED_PERIOD_SITE_SUPPORT",z.get("n_site_pairs_with_valid_both_years"))
    print("ALL_39_YEAR_COVERAGE",z.get("all_39_census_site_numeric_coverage_by_selected_year"))
    print("ALL_39_YEAR_SITES",json.dumps(z.get("all_39_census_site_names_with_numeric_records_by_year",{}),ensure_ascii=False))
    print("MATCHED_2024_SOURCE_PARENT",z.get("matched_2024_parent_geographic_descriptors"))
    print("2024_NON_ROSS_GEO_OUTGROUP",z.get("2024_geographic_outgroup_for_Ross_with_numeric_census_exists"))
    print("SOURCE_ERROR",z.get("error_type",""),z.get("error_message",""))
    print("ISLAND_IMMIGRATION_CAUSAL_RESULT",False)
if __name__=="__main__":main()
