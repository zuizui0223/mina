#!/usr/bin/env python3
"""V39 source island feature-name ontology; animal counts and geocoding never used."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
V35=ROOT/"results"/"NZ_ROSS_SEA_SCAR_ISLAND_GEO_V35.json"
SOURCES={
    "Beaufort Island":112759,
    "Coulman Island":113061,
    "Inexpressible Island":113617,
    "Ross Island":130958
}
ORIGINAL_YEAR_ROSTER=tuple(list(range(1983,1993))+[2001,2004,2005])
ORIGIN="https://data.aad.gov.au/aadc/gaz/display_name.cfm?gaz_id="

def original_gazetteer_html(session,name,source_id):
    url=ORIGIN+str(source_id)
    with session.get(url,timeout=(15,55),stream=True,headers={
        "User-Agent":"mina-scar-composite-gazetteer-name-only-audit-v39/1.0"}) as r:
        r.raise_for_status()
        f=urlparse(r.url)
        if f.scheme!="https" or f.hostname!="data.aad.gov.au":
            raise ValueError("SOURCE_STOP official SCAR name source redirect")
        raw=bytearray()
        for chunk in r.iter_content(8192):
            raw.extend(chunk)
            if len(raw)>120000:
                raise ValueError("SOURCE_STOP original gazetteer HTML unexpectedly large")
        return bytes(raw),{"original_source_url":url,
                           "original_source_sha256":hashlib.sha256(bytes(raw)).hexdigest(),
                           "original_source_html_bytes":len(raw)}

def validate_island_feature(raw,name,feature_id):
    soup=BeautifulSoup(raw,"html.parser")
    header=soup.find("h2")
    observed=header.get_text(" ",strip=True) if header else None
    if observed!=name:
        raise ValueError("SOURCE_STOP exact SCAR official original place-name record drift "+name)
    flat=" ".join(soup.get_text(" ",strip=True).split())
    if not re.search(r"\bFeature type:\s*Island\s*\(5\)",flat):
        raise ValueError("SOURCE_STOP source geographic feature not exact Island (5) "+name)
    if "SCAR Composite Gazetteer of Antarctica" not in flat:
        raise ValueError("SOURCE_STOP original source not within official SCAR composite")
    if not re.search(r"\b(?:United States|New Zealand) Gazetteer Id\s+"+str(feature_id)+r"\b",flat):
        raise ValueError("SOURCE_STOP official gazetteer identity number mismatch "+name)
    return {"original_official_feature_name":observed,
            "original_exact_feature_type":"Island (5)",
            "original_source_gazetteer_id":feature_id,
            "publisher_SCAR_CGA_record_membership_confirmed":True,
            "original_feature_centroid_position_precision_certified":False,
            "original_nest_colony_GPS_or_animal_count_evidence":False}

def fixed_source_landmass_panel(v35):
    if v35.get("status")!="V35_ORIGINAL_NZ_ROSS_SEA_COASTLINE_ISLAND_PANEL_GEOMETRY_QA":
        raise ValueError("SOURCE_STOP original V35 outcome-blind geolink status changed")
    gis=v35.get("original_group_to_GIS_landpolygonID",{})
    expected={**{"Possession Island":29},
              **{"Ross Island":59,"Coulman Island":37,"Beaufort Island":50,
                 "Inexpressible Island":43}}
    if gis!=expected:
        raise ValueError("SOURCE_STOP original four verified source named GIS polygons changed")
    years=v35["prespecified_original_GIS_locus_year_support"]["source_years_with_ge2_named_GIS_island_units"]
    if years!=list(ORIGINAL_YEAR_ROSTER):
        raise ValueError("SOURCE_STOP original fixed 13 source year roster changed")
    grouprows=v35["prespecified_original_GIS_locus_year_support"]["source_named_GIS_island_temporal_support"]
    for name in SOURCES:
        if name not in grouprows or grouprows[name]["original_same_colony_adjacent_year_window_count"]<5:
            raise ValueError("SOURCE_STOP original survey island-count availability drift "+name)
    return {name:{"source_original_medium_land_polygon_id":gis[name],
                  "source_named_island_original_colony_roster":grouprows[name]["source_colony_roster"],
                  "original_annual_window_source_count":grouprows[name]["original_same_colony_adjacent_year_window_count"]}
            for name in SOURCES}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",required=True,type=Path)
    args=p.parse_args()
    receipt={"status":"HOLD_OFFICIAL_SCAR_CGA_CATEGORICAL_IDENTITY","biological_effects_fitted":0}
    try:
        v35=json.loads(V35.read_text(encoding="utf-8"))
        fixed=fixed_source_landmass_panel(v35)
        verified={}
        with requests.Session() as session:
            for name,gaz_id in SOURCES.items():
                raw,meta=original_gazetteer_html(session,name,gaz_id)
                verified[name]={**validate_island_feature(raw,name,gaz_id),**meta}
        receipt={
            "status":"V39_OFFICIAL_SCAR_CGA_FOUR_SOURCE_ISLAND_FEATURES_CONFIRMED",
            "frozen_contract":"contracts/NZ_ROSS_SEA_SCAR_GAZETTEER_ISLAND_IDENTITY_V39.md",
            "source_feature_IDs_are_different":len(set(SOURCES.values()))==4,
            "separate_NZ_original_census_landmass_names_match_ScarOfficialIsland":sorted(verified),
            "SCAR_official_original_island_feature_records":verified,
            "unmodified_V35_original_island_colony_year_source_rosters":fixed,
            "V36_original_13_common_annual_start_years":list(ORIGINAL_YEAR_ROSTER),
            "V36_original_penguin_census_count_values_opened":0,
            "V36_ecological_coefficients_recomputed":False,
            "original_NZ_and_MAPPPD_nest_point_GPS_accuracy_remains_unverified":True,
            "causal_water_barrier_or_island_habitat_effect_identified":False,
            "scientific_decision":"CATEGORICAL_FOUR_ISLAND_NAMES_VERIFIED_BUT_COLONY_POINT_PRECISION_UNRESOLVED"
        }
    except Exception as exc:
        receipt["error_type"]=type(exc).__name__
        receipt["error"]=str(exc)[:550]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_OFFICIAL_SCAR_CGA_CATEGORICAL_IDENTITY":
        raise SystemExit(2)

if __name__=="__main__":
    main()
