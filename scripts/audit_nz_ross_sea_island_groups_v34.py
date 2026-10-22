#!/usr/bin/env python3
"""V34: exact-source Ross Sea colony→named-landmass crosswalk, source observations only."""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata
import requests
import audit_nz_ross_sea_census_source_v33 as v33

CENSUS_SHA="23a95d9e693dd095e085534f2c215b79880a72fe9cfb5a59337501192dae03e6"
LOCATION_SHA="d744e7493f85564f1b634f390a5e4a976b2d5359a6f93cdd9ef345639661b6a6"
EXACT_SHEET="All data"
MIN_ISLAND_UNITS_WITH_FIVE_PAIRS=3
MIN_MULTI_ISLAND_YEAR_WINDOWS=8
MIN_STRONG_COMPARATIVE_WINDOWS=6

def key(value):
    return " ".join(unicodedata.normalize("NFC",str(value or "")).strip().casefold().split())

def source_record_label(value):
    return str(value).strip() if isinstance(value,str) and value.strip() else None

def colony_year_presence(matrix):
    # Original V33 certified workbook is ROWS_COLONY_COLUMNS_YEAR, not invertible.
    if not matrix or 0 not in matrix:
        raise ValueError("SOURCE_STOP original source orientation changed")
    header=matrix[0]
    years={idx:v33.parse_year(v) for idx,v in header.items()
           if v33.parse_year(v) is not None}
    if len(years)!=44 or sorted(years.values())!=list(v33.YEARS):
        raise ValueError("SOURCE_STOP original V33 44-calendar-year publisher roster changed")
    values=defaultdict(list)
    for rowidx,row in matrix.items():
        if rowidx==0:continue
        name=source_record_label(row.get(0))
        if not name:continue
        present={yr for col,yr in years.items() if v33.num_present(row.get(col))}
        values[key(name)].append((name,present))
    duplicates={k for k,items in values.items() if len(items)>1}
    good={k:items[0] for k,items in values.items() if len(items)==1}
    return good,{"source_census_colony_ids":len(values),
                 "source_duplicate_colony_ids_excluded":len(duplicates),
                 "matched_original_year_column_count":len(years),
                 "original_count_magnitudes_opened":0}

def parse_angle(text):
    # Source format e.g. 76°56'S, 167°03'E, no more precise claim.
    txt=str(text or "").strip().replace("’","'").replace("′","'")
    m=re.fullmatch(r"(\d{1,3})°\s*(\d{1,2})(?:'\s*)?([NSEW])",txt,re.I)
    if not m:return None
    degrees,minute,hemi=int(m.group(1)),int(m.group(2)),m.group(3).upper()
    limit=90 if hemi in ("N","S") else 180
    if degrees>limit or minute>=60:return None
    x=degrees+minute/60
    return -x if hemi in ("S","W") else x

def location_rows(matrix):
    source=defaultdict(list)
    for row in matrix.values():
        name=source_record_label(row.get(0))
        if not name:continue
        label=source_record_label(row.get(1))
        lat=parse_angle(row.get(2))
        lon=parse_angle(row.get(3))
        source[key(name)].append({"original_colony":name,
                                  "publisher_named_place":label,
                                  "published_location_lat_approx":lat,
                                  "published_location_lon_approx":lon})
    duplicates={k for k,vals in source.items() if len(vals)>1}
    valid={k:records[0] for k,records in source.items() if len(records)==1}
    return valid,{"original_distinct_colony_site_names":len(source),
                  "duplicate_source_location_name_keys_excluded":len(duplicates),
                  "original_location_rows":sum(len(r) for r in source.values()),
                  "unparseable_source_latitudes":sum(x["published_location_lat_approx"] is None
                                                       for x in valid.values()),
                  "unparseable_source_longitudes":sum(x["published_location_lon_approx"] is None
                                                       for x in valid.values())}

def named_landmass(colony,place):
    """Only explicit singular 'Island' names; no fuzzy/nearest-shore reconstruction."""
    place=source_record_label(place)
    colony=source_record_label(colony)
    if place and re.search(r"\bIsland$",place,re.I) and not re.search(r"\bIslands$",place,re.I):
        return place,"SOURCE_EXPLICIT_NAMED_SINGULAR_ISLAND"
    if colony and re.search(r"\bIsland$",colony,re.I) and not re.search(r"\bIslands$",colony,re.I):
        return colony,"SOURCE_COLONY_ITSELF_SINGULAR_ISLAND"
    return None,"NO_SOURCE_EXPLICIT_SINGULAR_ISLAND"

def source_crosswalk(census,locations):
    cols,source_qa=colony_year_presence(census)
    loc,geo_qa=location_rows(locations)
    intersect=sorted(set(cols)&set(loc))
    missing_sites=sorted(cols[k][0] for k in set(cols)-set(loc))
    unused_geography=sorted(loc[k]["original_colony"] for k in set(loc)-set(cols))
    cross=[]
    bygroup=defaultdict(dict)
    for k in intersect:
        colony,present=cols[k]
        point=loc[k]
        landmass,classif=named_landmass(colony,point["publisher_named_place"])
        item={
            "original_census_colony":colony,
            "original_site_map_colony":point["original_colony"],
            "published_named_region_or_landmass":point["publisher_named_place"],
            "publisher_explicit_island_group":landmass,
            "island_source_classification":classif,
            "original_source_year_observation_count":len(present),
            "original_site_coordinate_approx_lat":point["published_location_lat_approx"],
            "original_site_coordinate_approx_lon":point["published_location_lon_approx"],
        }
        cross.append(item)
        if landmass:
            bygroup[landmass][colony]=present
    # Preserve original named island group identity; no merging by approximate positions.
    groups=[]
    island_window_presence={}
    for name,members in sorted(bygroup.items()):
        windows={}
        for y in range(1981,2024):
            roster=sorted(site for site,ys in members.items() if y in ys and y+1 in ys)
            if roster:
                windows[y]=roster
        island_window_presence[name]=windows
        groups.append({
            "publisher_explicit_named_island":name,
            "source_colonies":sorted(members),
            "source_colony_count":len(members),
            "source_colony_year_presence_by_site":{
                site:len(obs) for site,obs in members.items()},
            "number_original_adjacent_windows_at_least_one_same_colony":len(windows),
            "number_original_adjacent_windows_at_least_two_same_colonies":
                sum(len(v)>=2 for v in windows.values()),
            "source_original_windows_with_any_repeat":[int(y) for y in windows],
            "original_names_are_not_verified_GIS_land_polygon_IDs":True,
        })
    support=Counter()
    strong=Counter()
    for y in range(1981,2024):
        n=sum(y in grp for grp in island_window_presence.values())
        support[y]=n
        strong[y]=sum(len(grp.get(y,[]))>=2 for grp in island_window_presence.values())
    nstrong=sum(g["number_original_adjacent_windows_at_least_one_same_colony"]>=5 for g in groups)
    candidate_years=sorted(y for y,n in support.items() if n>=2)
    strong_years=sorted(y for y,n in strong.items() if n>=2)
    qa={
        "original_census":source_qa,
        "original_location":geo_qa,
        "exact_colony_location_ID_matches":len(intersect),
        "unmatched_original_census_colony_names":missing_sites,
        "location_names_without_exact_census_match":unused_geography,
        "site_to_named_island_crosswalk":cross,
        "named_source_singular_island_candidate_groups":groups,
        "n_distinct_explicit_named_source_island_candidate_groups":len(groups),
        "n_named_islands_with_ge5_original_adjacent_growth_windows":nstrong,
        "years_with_ge2_named_islands_annual_colony_pair_observations":candidate_years,
        "n_years_with_ge2_named_islands":len(candidate_years),
        "years_with_ge2_named_islands_each_ge2_original_colonies":strong_years,
        "n_strict_within_vs_between_years":len(strong_years),
        "original_count_magnitudes_opened":0,
        "numeric_source_colony_year_values_never_published":True,
        "true_GIS_island_identities_or_boundaries_independently_verified":False,
        "source_named_island_panel_gate":(
            nstrong>=MIN_ISLAND_UNITS_WITH_FIVE_PAIRS and
            len(candidate_years)>=MIN_MULTI_ISLAND_YEAR_WINDOWS),
        "stricter_multi_colony_island_comparison_gate":len(strong_years)>=MIN_STRONG_COMPARATIVE_WINDOWS,
    }
    return qa

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",type=Path,required=True)
    args=parser.parse_args()
    receipt={"status":"HOLD_ORIGINAL_NZ_GEO_AND_CENSUS","ecological_effects_computed":0}
    try:
        with requests.Session() as s:
            sources,meta=v33.ckandownloads(s)
        if sources["census"]["receipt"]["sha256"]!=CENSUS_SHA or sources["locations"]["receipt"]["sha256"]!=LOCATION_SHA:
            raise ValueError("SOURCE_STOP original 2026 NZ colony or geography workbook SHA changed")
        counts=v33.workbook_original(sources["census"]["raw"])
        geo=v33.workbook_original(sources["locations"]["raw"])
        if set(counts)!={EXACT_SHEET} or not geo:
            raise ValueError("SOURCE_STOP original 2026 worksheet name drift")
        locsheet=next(iter(geo.values())) if len(geo)==1 else None
        if locsheet is None:
            raise ValueError("SCHEMA_STOP ambiguous original location sheet list")
        support=source_crosswalk(counts[EXACT_SHEET],locsheet)
        receipt={
            "status":"V34_ORIGINAL_NZ_COLONY_TO_PUBLISHER_NAMED_ISLAND_SOURCE_AUDIT",
            "source_census_sha256":CENSUS_SHA,
            "source_location_sha256":LOCATION_SHA,
            "source_DOI":v33.DOI,
            "frozen_contract":"contracts/NZ_ROSS_SEA_COLONY_ISLAND_CROSSWALK_V34.md",
            "source_geography_and_year_support":support,
            "counts_or_synchrony_estimated":0,
            "scientific_decision":(
                "HOLD_GIS_ISLAND_POLYGONS_AND_COUNT_STAGE_BEFORE_BIOLOGY"
                if support["source_named_island_panel_gate"]
                else "STOP_INSUFFICIENT_SOURCE_NAMED_ISLAND_TEMPORAL_COVERAGE"
            )
        }
    except Exception as e:
        receipt["error_type"]=type(e).__name__
        receipt["error"]=str(e)[:700]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_ORIGINAL_NZ_GEO_AND_CENSUS":
        raise SystemExit(2)

if __name__=="__main__":
    main()
