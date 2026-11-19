#!/usr/bin/env python3
"""AADC 2025 original 8-species survey SOURCE-SUPPORT audit, not an effect fit.

Source files and SHA256 are fixed before any original animal states are read.
Every P/A/NR is preserved; no reported search is never an absence. Annual
A->P counts are observed site/source transitions, not first colonization.
This does NOT reopen the previously frozen AADC Adélie P/A transition gate.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
import requests
import openpyxl
import xlrd

from scripts.audit_aadc_2025_seabird_riskset_original_schema import SETS, download_original

ORIGINAL_SHA256={
    "2025_seabird":"4a03d8efc8f1579b2eafd982811c39edc00d2c87d49e990f93c6411db6860360",
    "2025_penguin":"8b38aa86f0ef2a0a9fe8c5bb13da904a9f2431cd503644b962b6e116ac3187ac",
    "2025_geographic_sites":"ed5f59d11a0e2ca7491ecf32dc8b04de524e83edf7acd268702963c3b7561294",
    "2025_certainty":"b7aba52732102441b4edbe438b854cb9d2dbf39542fd6fbfcd62647ae9fdd156",
    "2016_icefree_site_atlas":"2236269e754962f9af082a0853993fc65a4afd20c7489a65fae81bdd1899ffaa",
}
SOURCE_COUNTS={"2025_seabird":22018,"2025_penguin":11089,
               "2025_geographic_sites":7785,"2025_certainty":216,
               "2016_icefree_site_atlas":4884}
PUBLICATION_REPORTED_EVENTS=33297
SOURCE_EXPECTED_EVENTS=33107
PUBLISHER_2025="10.26179/5n29-r073"
PUBLISHER_2016="10.26179/53yk-8z83"
TARGET_SHEETS={"2025_seabird":"2_search events",
               "2025_penguin":"2_search events",
               "2025_geographic_sites":"2_geog_sites_all",
               "2025_certainty":"2_occurrence certainty",
               "2016_icefree_site_atlas":"2_Geographic sites"}
OCC={"P","A","NR"}
GEOG_COLS={"geog_site_id","geog_site_feature","sub_group","geog_site_area_cat3"}
REQ_EVENT={"geog_site_id","species_code","season","occurrence","sub_group",
           "vantage","site_expert_validation","occurrence_expert_validation",
           "species_expert_validation"}

def txt(value)->str:
    if value is None:return ""
    if isinstance(value,float) and value.is_integer():return str(int(value))
    return str(value).strip()

def read_source_rows(raw:bytes,filename:str,sheet:str,expected:int):
    """Read only named original sheets, don't identify animal rows as islands."""
    if filename.lower().endswith(".xls"):
        book=xlrd.open_workbook(file_contents=raw,on_demand=True)
        try:
            ws=book.sheet_by_name(sheet)
            cols=[txt(x).lower() for x in ws.row_values(0)]
            if len(cols)!=len(set(cols)):
                raise ValueError("ambiguous original XLS header")
            body=[dict(zip(cols,ws.row_values(i))) for i in range(1,ws.nrows)]
        finally:book.release_resources()
    else:
        wb=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
        try:
            ws=wb[sheet]
            stream=ws.iter_rows(values_only=True)
            cols=[txt(x).lower() for x in next(stream)]
            nonempty=[x for x in cols if x]
            if len(nonempty)!=len(set(nonempty)):
                raise ValueError("ambiguous nonblank original XLSX header")
            body=[dict(zip(cols,row)) for row in stream]
        finally:wb.close()
    if len(body)!=expected:
        raise ValueError(f"original record count drift {filename}: {len(body)} != {expected}")
    return body,cols

def season_year(value)->int|None:
    x=txt(value)
    m=re.fullmatch(r"((?:18|19|20)\d{2})(?:[-/]\d{2,4})?",x)
    if not m:return None
    year=int(m.group(1))
    return year if 1850<=year<=2025 else None

def strict_state(values:set[str])->str:
    """Resolve only unambiguous original source states, not underlying ecology."""
    if "P" in values and "A" in values:return "CONFLICT_P_AND_A"
    if values=={"A"}:return "A_REPORTED_ONLY"
    if "P" in values and "A" not in values:return "P_REPORTED_NO_A"
    if values=={"NR"}:return "NR_ONLY"
    if "A" in values:return "MIXED_A_WITH_NR_OR_INVALID"
    return "NO_KNOWN_STATE"

def audit_source(source:dict[str,list[dict]]):
    geo=source["2025_geographic_sites"]
    old=source["2016_icefree_site_atlas"]
    certainty=source["2025_certainty"]
    fly=source["2025_seabird"]
    peng=source["2025_penguin"]
    ids=defaultdict(list)
    for row in geo:
        key=txt(row.get("geog_site_id"))
        if key:ids[key].append(row)
    duplicate_geo=sum(len(x)>1 for x in ids.values())
    geog_index={k:x[0] for k,x in ids.items() if len(x)==1}
    old_ids={txt(r.get("geog_site_id")) for r in old if txt(r.get("geog_site_id"))}
    old_source_col_counts=Counter(
        ("geog_site_id" in r, "sub_group" in r) for r in old[:1])
    by_geo_source=Counter(txt(r.get("geog_site_feature")).lower() or "<missing>" for r in geo)
    certainty_exact=defaultdict(list)
    for row in certainty:
        key=tuple(txt(row.get(k)).upper() for k in
                  ("species_code","occurrence","vantage","geog_site_area_cat3"))
        certainty_exact[key].append(row)
    raw=(("2025_seabird",fly),("2025_penguin",peng))
    event_counts=Counter()
    species_counts=Counter()
    species_event_states=defaultdict(Counter)
    feature_event_states=defaultdict(Counter)
    with_publisher_validated=Counter()
    survey_keys=defaultdict(set)
    precision_lookup=Counter()
    geography_coverage=Counter()
    years=Counter()
    event_key_duplicates=Counter()
    prior_year_event_count=0
    for family,records in raw:
        for row in records:
            occ=txt(row.get("occurrence")).upper()
            species=txt(row.get("species_code")).upper()
            site=txt(row.get("geog_site_id"))
            year=season_year(row.get("season"))
            event_counts[(family,"rows")]+=1
            event_counts[("occurrence",occ or "<missing>")]+=1
            species_counts[species or "<missing>"]+=1
            species_event_states[species][occ or "<missing>"]+=1
            if site in geog_index:
                feature=txt(geog_index[site].get("geog_site_feature")).lower() or "<missing>"
                geography_coverage["exact_unique_geo_id"]+=1
            elif site in ids:
                feature="<ambiguous-id>"
                geography_coverage["duplicate_geo_id"]+=1
            else:
                feature="<unmatched-site>"
                geography_coverage["no_geo_id"]+=1
            feature_event_states[feature][occ or "<missing>"]+=1
            if year is None:
                geography_coverage["invalid_season"]+=1
            else:
                years[year]+=1
            validation=tuple(txt(row.get(x)).upper() for x in
                             ("species_expert_validation","site_expert_validation","occurrence_expert_validation"))
            if all(x=="Y" for x in validation):
                with_publisher_validated[(species,"all_three_Y")]+=1
            elif "N" in validation:
                with_publisher_validated[(species,"any_N")]+=1
            else:
                with_publisher_validated[(species,"not_all_Y")]+=1
            # Exact certainty source-table linkage requires all four source classes.
            area_cat=txt(geog_index[site].get("geog_site_area_cat3")).upper() if site in geog_index else ""
            cert_key=(species,occ,txt(row.get("vantage")).upper(),area_cat)
            entries=certainty_exact.get(cert_key,[])
            precision_lookup["exact_unique"]+=int(len(entries)==1)
            precision_lookup["ambiguous"]+=int(len(entries)>1)
            precision_lookup["unmatched"]+=int(not entries)
            if site and species and year is not None:
                survey_keys[(site,species,year)].add(occ)
            if year is not None and year>=2024:
                prior_year_event_count+=1
    if event_counts[("2025_seabird","rows")]+event_counts[("2025_penguin","rows")]!=SOURCE_EXPECTED_EVENTS:
        raise ValueError("original source count total unexpectedly changed")
    resolved=Counter()
    species_resolved=defaultdict(Counter)
    byyear=defaultdict(dict)
    for (site,sp,yr),values in survey_keys.items():
        state=strict_state(values)
        resolved[state]+=1
        species_resolved[sp][state]+=1
        byyear[(site,sp)][yr]=state
    transitions=defaultdict(Counter)
    transition_land=defaultdict(Counter)
    candidate_events=[]
    for (site,sp),states in byyear.items():
        cls=txt(geog_index[site].get("geog_site_feature")).lower() if site in geog_index else "<unmatched>"
        for y,a in states.items():
            b=states.get(y+1)
            if not b:continue
            if a not in {"A_REPORTED_ONLY","P_REPORTED_NO_A"} or b not in {"A_REPORTED_ONLY","P_REPORTED_NO_A"}:
                continue
            transitions[sp][a+"__to__"+b]+=1
            transition_land[cls][a+"__to__"+b]+=1
            if a=="A_REPORTED_ONLY" and b=="P_REPORTED_NO_A":
                candidate_events.append({"site":site,"species":sp,"start_year":y,
                   "end_year":y+1,"geog_site_feature":cls,
                   "unverified_colonization":True})
    byfeature_sites=defaultdict(set)
    byfeature_explicit_siteyears=defaultdict(set)
    for (site,sp,yr),values in survey_keys.items():
        if site not in geog_index:continue
        cls=txt(geog_index[site].get("geog_site_feature")).lower() or "<missing>"
        byfeature_sites[cls].add(site)
        if strict_state(values) in {"A_REPORTED_ONLY","P_REPORTED_NO_A"}:
            byfeature_explicit_siteyears[cls].add((site,yr))
    actual_sites={k[0] for k in survey_keys}
    return {
        "status":"PUBLISHER_EIGHT_SPECIES_SOURCE_SUPPORT_NO_BIOLOGICAL_EFFECT",
        "source_files":{"2025_seabird":"occupancy_seabird.xls",
                        "2025_penguin":"occupancy_penguin.xlsx",
                        "geographic_sites":"geog_sites_all.xlsx",
                        "certainty":"occupancy_certainty.xlsx",
                        "old_potential_sites":"Spatial reference systemn coastal East Antarctica.xlsx"},
        "source_event_rows":SOURCE_EXPECTED_EVENTS,
        "publication_reported_rows":PUBLICATION_REPORTED_EVENTS,
        "publication_minus_original_source_event_rows":PUBLICATION_REPORTED_EVENTS-SOURCE_EXPECTED_EVENTS,
        "source_discrepancy_resolved":False,
        "source_family_event_counts":{k[0]:v for k,v in event_counts.items() if k[1]=="rows"},
        "distinct_species_codes":dict(sorted(species_counts.items())),
        "event_original_occurrence_codes":{
            k[1]:v for k,v in event_counts.items() if k[0]=="occurrence"},
        "event_source_geographic_join":dict(geography_coverage),
        "original_2025_geog_reference_rows":len(geo),
        "unique_geog_ids":len(ids),
        "duplicate_geog_ids":duplicate_geo,
        "geog_feature_row_counts":dict(sorted(by_geo_source.items())),
        "original_2016_geog_reference_rows":len(old),
        "old_source_header_presence":{str(k):v for k,v in old_source_col_counts.items()},
        "old_2016_identified_ids":len(old_ids),
        "old_2016_ids_exactly_in_2025":len(old_ids&set(ids)),
        "source_2025_event_geosites_seen":len(actual_sites),
        "site_ids_with_any_event_and_valid_geo":len(actual_sites&set(geog_index)),
        "geographic_feature_sampled_site_counts":{
           c:len(v) for c,v in sorted(byfeature_sites.items())},
        "geographic_feature_explicit_state_site_years":{
           c:len(v) for c,v in sorted(byfeature_explicit_siteyears.items())},
        "occurrence_event_counts_by_species":{s:dict(sorted(d.items()))
                                              for s,d in sorted(species_event_states.items())},
        "occurrence_event_counts_by_feature":{s:dict(sorted(d.items()))
                                              for s,d in sorted(feature_event_states.items())},
        "source_expert_validation_support":{
            f"{s}:{q}":v for (s,q),v in sorted(with_publisher_validated.items())},
        "original_source_certainty_rows":len(certainty),
        "source_certainty_exact_key_unique":sum(len(v)==1 for v in certainty_exact.values()),
        "source_certainty_duplicate_keys":sum(len(v)>1 for v in certainty_exact.values()),
        "event_certainty_table_exact_tuple_match":dict(precision_lookup),
        "source_year_min_max":[min(years) if years else None,max(years) if years else None],
        "source_years_count":len(years),
        "events_in_or_after_2024":prior_year_event_count,
        "unique_site_species_year_combinations":len(survey_keys),
        "resolved_annual_site_species_status":dict(resolved),
        "resolved_annual_status_by_species":{s:dict(d)
                                              for s,d in sorted(species_resolved.items())},
        "consecutive_strict_state_pairs_by_species":{s:dict(d) for s,d in sorted(transitions.items())},
        "consecutive_strict_state_pairs_by_land_feature":{s:dict(d) for s,d in sorted(transition_land.items())},
        "observed_site_species_A_then_P_pairs":len(candidate_events),
        "observed_A_to_P_distinct_sites":len(set(x["site"] for x in candidate_events)),
        "observed_A_to_P_distinct_subgroups":None,
        "observed_A_to_P_are_true_colonization":False,
        "individual_A_to_P_event_rows_exported":False,
        "ecological_effects_or_p_values_fitted":False,
        "hard_interpretation_limits":[
            "A means source-reported breeding absence during a search, not verified animal true absence from a precisely mapped nest patch.",
            "NR is never interpreted as A. Conflicting within-year P and A are not used in annual A/P transitions.",
            "Event rows are observations, not independent sites or patches. Source files share original survey history with previously audited AADC PR180 Adélie.",
            "The 2025 source atlas includes unvisited potential geographies; unvisited never means surveyed absent.",
            "Publisher certainty classification is a separate 216-row lookup with matched source fields; source validity is not equivalent to high detection probability.",
            "Original event support differs by 190 records from published 33,297 events; cannot claim exact reproduction without explanation.",
            "The 2025 East Antarctic geographical domain does not overlap 25 Western Antarctic Peninsula GLIMS-rock sites.",
            "The 2024 Antarctic rock map postdates this historical survey archive; no post-2024 detection at a freshly exposed patch can be linked.",
            "No predator-mammal presence measure and no new bare-rock exposure date are contained in these source event files.",
        ]
    }

def run():
    originals={}
    provenance={}
    with requests.Session() as session:
        for tag,spec in SETS.items():
            data,meta=download_original(session,spec)
            if meta["sha256"]!=ORIGINAL_SHA256[tag]:
                raise ValueError(f"STOP original publisher source sha drift {tag}")
            rows,fields=read_source_rows(data,spec["name"],
                        TARGET_SHEETS[tag],SOURCE_COUNTS[tag])
            originals[tag]=rows
            provenance[tag]={"sha256":meta["sha256"],"bytes":meta["bytes"],
                             "rows":len(rows),"columns":fields,
                             "original_publisher_filename":spec["name"]}
    for tag in ("2025_seabird","2025_penguin"):
        if not REQ_EVENT.issubset(set(provenance[tag]["columns"])):
            raise ValueError(f"missing original event fields {tag}")
    if not GEOG_COLS.issubset(set(provenance["2025_geographic_sites"]["columns"])):
        raise ValueError("geographic site reference original schema drift")
    a=audit_source(originals)
    a["source_sha256_and_rows"]=provenance
    a["publisher_doi_2025"]=PUBLISHER_2025
    a["publisher_doi_2016"]=PUBLISHER_2016
    return a

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",required=True,type=Path)
    args=p.parse_args()
    try:
        result=run()
    except Exception as e:
        result={"status":"HOLD_EIGHT_SPECIES_ORIGINAL_SOURCE_JOIN",
                "error":f"{type(e).__name__}: {str(e)}"[:350],
                "ecological_effects_or_p_values_fitted":False}
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print(json.dumps({
        "status":result.get("status"),
        "source_events":result.get("source_event_rows"),
        "geographic_feature_sampled_sites":result.get("geographic_feature_sampled_site_counts"),
        "strict_obs_AtoP_pairs":result.get("observed_site_species_A_then_P_pairs"),
        "error":result.get("error"),
    },sort_keys=True))

if __name__=="__main__":
    main()
