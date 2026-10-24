#!/usr/bin/env python3
"""V38: APBP original Event source site GPS/uncertainty vs 33 NZ author colony names.

No original animal abundance or nesting response read; no fuzzy source IDs.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
import math
from pathlib import Path
import unicodedata
from pyproj import Transformer
import audit_nz_ross_sea_island_groups_v34 as v34
import audit_nz_ross_sea_census_source_v33 as v33
import link_apbp_to_add_island_rock_v3 as v3

SOURCE_APBP_SHA="afa947f39d9ad7382266d5be64c70f9fe4e84ffb6e2838c1369e043caae09abf"
SOURCE_NZ_CENSUS_SHA="23a95d9e693dd095e085534f2c215b79880a72fe9cfb5a59337501192dae03e6"
SOURCE_NZ_LOCATION_SHA="d744e7493f85564f1b634f390a5e4a976b2d5359a6f93cdd9ef345639661b6a6"
V35=Path(__file__).resolve().parents[1]/"results"/"NZ_ROSS_SEA_SCAR_ISLAND_GEO_V35.json"
FROZEN_UNITS=("Beaufort Island","Coulman Island","Inexpressible Island","Ross Island")
# Historical V38 cutoff retained only for exact rerun. The APBP field is
# mean original polygon-vertex-to-colony-centre distance (footprint extent),
# NOT independently calibrated GPS coordinate error; >250m does NOT prove
# poorly surveyed geolocation. See V38_RESULT methodological correction.
MAX_SOURCE_UNCERT_M=250.
MAX_REPEATED_SITE_DRIFT_M=250.
MAX_COARSE_POINT_DIFFERENCE_M=3000.
POSSIBLE_COPIED_COARSE_THRESHOLD_M=10.
MIN_ISLANDS=3
MIN_PER_ISLAND_WINDOWS=5
MIN_COOBSERVATION_YEARS=8
FROZEN_SHARED_YEARS=tuple(list(range(1983,1993))+[2001,2004,2005])

def source_33_original():
    from requests import Session
    with Session() as session:
        sources,manifest=v33.ckandownloads(session)
    if (sources["census"]["receipt"]["sha256"]!=SOURCE_NZ_CENSUS_SHA or
        sources["locations"]["receipt"]["sha256"]!=SOURCE_NZ_LOCATION_SHA):
        raise ValueError("SOURCE_STOP original NZ author workbooks changed")
    census=v33.workbook_original(sources["census"]["raw"])
    places=v33.workbook_original(sources["locations"]["raw"])
    if set(census)!={"All data"} or len(places)!=1:
        raise ValueError("SOURCE_STOP author geography schema drift")
    sites=v34.source_crosswalk(census["All data"],next(iter(places.values())))
    if sites["exact_colony_location_ID_matches"]!=33:
        raise ValueError("SOURCE_STOP author original exact site identity count changed")
    return sites

def apbp_sites():
    original=v3.fetch_original()
    sites=v3.event_sites(original)   # original event only, no animal counts
    return sites

def choose_original_APBP_georef(nz_original,apbp):
    normal=v34.key
    possible={normal(r["original_census_colony"]):r
              for r in nz_original["site_to_named_island_crosswalk"]}
    converter=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    by_label=defaultdict(list)
    ambiguous_source_IDs=0
    for siteID,events in apbp.items():
        source_text_names={normal(event.get("locality",""))
                           for event in events if event.get("locality","")}
        if len(source_text_names)!=1:
            if source_text_names & set(possible):ambiguous_source_IDs+=1
            continue
        label=next(iter(source_text_names))
        if label in possible:
            by_label[label].append((str(siteID),events))
    included=[]
    for label,source in sorted(possible.items()):
        candidate_ids=by_label.get(label,[])
        note={
            "NZ_original_colony":source["original_census_colony"],
            "NZ_publisher_named_island":source["publisher_explicit_island_group"],
            "n_APBP_exact_locality_source_locationIDs":len(candidate_ids),
            "source_original_APBP_locationIDs":[key for key,_ in candidate_ids],
            "source_original_penguin_count_records_read":0
        }
        if len(candidate_ids)!=1:
            note["status"]="HOLD_NO_EXACT_SINGLE_APBP_LOCALITY" if not candidate_ids else "HOLD_AMBIGUOUS_APBP_LOCATION_IDS"
            included.append(note);continue
        original_id,events=candidate_ids[0]
        coords=[(e.get("x"),e.get("y"),e.get("uncertainty_m")) for e in events]
        if not coords or any(x is None or y is None or not math.isfinite(x) or not math.isfinite(y)
                             for x,y,unc in coords):
            note["status"]="HOLD_SOURCE_EVENT_MISSING_COORDINATES"
            included.append(note);continue
        xs=[x for x,y,u in coords];ys=[y for x,y,u in coords]
        refx,refy=xs[0],ys[0]
        drift=max(math.hypot(x-refx,y-refy) for x,y,_ in coords)
        uncs=[u for x,y,u in coords]
        note.update({
            "APBP_original_geo_source_event_rows":len(events),
            "source_same_locationID_drift_m":round(drift,2),
            "source_position_uncertainty_m_max":max(uncs) if all(u is not None and math.isfinite(u) for u in uncs) else None,
            "source_position_uncertainty_missing_events":sum(u is None or not math.isfinite(u) for u in uncs)
        })
        nzlat=source.get("original_site_coordinate_approx_lat")
        nzlon=source.get("original_site_coordinate_approx_lon")
        if nzlat is None or nzlon is None:
            note["status"]="HOLD_NZ_COARSE_POSITION_NOT_PARSED"
            included.append(note);continue
        coarx,coary=converter.transform(nzlon,nzlat)
        separation=math.hypot(refx-coarx,refy-coary)
        note["distance_APBP_to_original_NZ_one_minute_coordinate_m"]=round(separation,2)
        if separation>MAX_COARSE_POINT_DIFFERENCE_M:
            note["status"]="HOLD_EXACT_NAME_DIFFERENT_SOURCE_LOCATION"
        elif note["source_position_uncertainty_missing_events"]>0:
            note["status"]="HOLD_APBP_UNKNOWN_ORIGINAL_POSITION_UNCERTAINTY"
        elif note["source_position_uncertainty_m_max"]>MAX_SOURCE_UNCERT_M:
            note["status"]="HOLD_APBP_REPORTED_SOURCE_UNCERTAINTY_OVER_250M"
        elif drift>MAX_REPEATED_SITE_DRIFT_M:
            note["status"]="HOLD_APBP_SOURCE_COORDINATES_DRIFT"
        elif separation<POSSIBLE_COPIED_COARSE_THRESHOLD_M:
            note["status"]="HOLD_APBP_COORDINATE_EQUALS_COARSE_NZ_LOCATION"
        else:
            note["status"]="APBP_REPORTED_POSITION_PRECISION_CANDIDATE_ONLY_NOT_GPS_PROOF"
        included.append(note)
    return included,{
        "APBP_total_original_location_IDs":len(apbp),
        "APBP_source_IDs_with_ambiguous_multiple_locality_texts":ambiguous_source_IDs,
        "NZ_original_exact_source_colonies":len(possible),
        "original_NZ_to_APBP_exact_colonies_matched_with_one_site_ID":sum(
            r["n_APBP_exact_locality_source_locationIDs"]==1 for r in included),
        "source_classification":dict(Counter(r["status"] for r in included))
    }

def source_coverage(original,links,v35):
    accepted={r["NZ_original_colony"] for r in links
             if r["status"]=="APBP_REPORTED_POSITION_PRECISION_CANDIDATE_ONLY_NOT_GPS_PROOF"}
    panel=v35["prespecified_original_GIS_locus_year_support"]["source_named_GIS_island_temporal_support"]
    totals={}
    common=defaultdict(list)
    for island in FROZEN_UNITS:
        yearly={}
        for y,sites in panel[island]["original_fixed_source_colonies_by_annual_window"].items():
            keep=[name for name in sites if name in accepted]
            if keep:
                yearly[int(y)]=keep
                if int(y) in FROZEN_SHARED_YEARS:common[int(y)].append(island)
        totals[island]={
            "APBP_source_precision_supported_site_names":sorted(
                accepted & set(panel[island]["source_colony_roster"])),
            "source_year_windows_with_same_site_precise_APBP_georeference":len(yearly),
            "source_year_start_roster":sorted(yearly)
        }
    qualified=sum(v["source_year_windows_with_same_site_precise_APBP_georeference"]>=MIN_PER_ISLAND_WINDOWS
                  for v in totals.values())
    matches=sorted(y for y,areas in common.items() if len(areas)>=2)
    return {
        "source_named_islands_with_ge5_APBP_candidate_precise_site_year_windows":qualified,
        "source_years_with_ge2_qualified_original_islands":matches,
        "n_source_years_with_ge2_APBP_precision_candidate_named_islands":len(matches),
        "original_APBP_reported_precision_source_support_by_frozen_landmass":totals,
        "strict_next_PUBLISHER_GIS_gate_passed":qualified>=MIN_ISLANDS and len(matches)>=MIN_COOBSERVATION_YEARS,
        "independently_GPS_surveyed_source_coordinates_proven":False,
        "no_animal_counts_redistributed":True
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--json",required=True,type=Path)
    args=a.parse_args()
    out={"status":"HOLD_ORIGINAL_NZ_OR_APBP_SOURCE","ecological_effect_fitted":False}
    try:
        nz=source_33_original()
        v35=json.loads(V35.read_text(encoding="utf-8"))
        if v35.get("publisher_census_sha256")!=SOURCE_NZ_CENSUS_SHA or \
           v35.get("publisher_location_sha256")!=SOURCE_NZ_LOCATION_SHA or \
           v35["prespecified_original_GIS_locus_year_support"]["source_years_with_ge2_named_GIS_island_units"]!=list(FROZEN_SHARED_YEARS):
            raise ValueError("SOURCE_STOP immutable V35 shared 13-year cohort changed")
        apbp=apbp_sites()
        links,qa=choose_original_APBP_georef(nz,apbp)
        coverage=source_coverage(nz,links,v35)
        out={
            "status":"V38_APBP_ORIGINAL_SOURCE_GEOREFERENCE_TO_NZ_COLONY_EXACT_NAMES",
            "source_nz_census_sha256":SOURCE_NZ_CENSUS_SHA,
            "source_nz_locations_sha256":SOURCE_NZ_LOCATION_SHA,
            "source_apbp_v23_SHA256":SOURCE_APBP_SHA,
            "source_APBP_DOI":"10.48361/zftxkr",
            "original_source_exact_colony_record_match_QA":qa,
            "original_33_colony_APBP_publisher_georeference_audit":links,
            "source_geography_temporal_support":coverage,
            "original_adélie_animal_abundance_values_opened":0,
            "independent_animal_population_replication_claimed":False,
            "scientific_decision":("PROCEED_SEPARATELY_FROZEN_NEW_GIS_JOIN_ONLY"
                 if coverage["strict_next_PUBLISHER_GIS_gate_passed"]
                 else "HOLD_NO_INDEPENDENT_APBP_PRECISE_GEOLOCATION_SOURCE_SUPPORT")
        }
    except Exception as err:
        out["error_type"]=type(err).__name__
        out["error"]=str(err)[:600]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False))
    if out["status"]=="HOLD_ORIGINAL_NZ_OR_APBP_SOURCE":
        raise SystemExit(2)

if __name__=="__main__":
    main()
