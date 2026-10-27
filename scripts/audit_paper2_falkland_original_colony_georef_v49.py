#!/usr/bin/env python3
"""V49 FIG original colony location provenance on known G1 source breeding pairs.

Check whether original "Colony latitude/longitude" fields provide distinct
spatial nesting-patch coordinates, or merely repeat original island/source
point. Exactly three original authenticated FIBD XLS. No mammal SDM and no
bird effect fit; never export source colony coordinates, names, or surveyors.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import re

import audit_paper2_falkland_guild_breeding_source_v47 as v47

EXPECTED_G1_YEAR = 69
EXPECTED_G1_LOCALITIES = 66
EXPECTED_SAME_DATE = 63
COLON_LAT_COL = 19
COLON_LON_COL = 18
BIRD_LAT_COL = 2
BIRD_LON_COL = 3
COLON_CODE_COL = 17
MIN_G4_LOCALITIES = 10
MIN_G4_REGIONS = 2


def finite_float(x):
    if isinstance(x,bool) or x is None:return None
    try:a=float(x)
    except (TypeError,ValueError):return None
    return a if math.isfinite(a) else None


def coordinate_state(latvalue,lonvalue):
    lat=finite_float(latvalue);lon=finite_float(lonvalue)
    if lat is None and lon is None:return "TWO_FIELDS_MISSING",None
    if lat is None or lon is None:return "ONE_FIELD_MISSING",None
    if not (-54.0<=lat<=-50.0 and -63.0<=lon<=-56.0):
        return "OUTSIDE_FIXED_FALKLAND_WGS84_OR_SENTINEL",None
    return "VALID_BOTH_SOURCE_FIELDS",(lat,lon)


def distance_m(loc1,loc2):
    if loc1 is None or loc2 is None:return None
    from math import radians,sin,cos,sqrt,atan2
    a,b=map(radians,loc1)
    c,d=map(radians,loc2)
    h=sin((c-a)/2)**2+cos(a)*cos(c)*sin((d-b)/2)**2
    return float(6371008.8*2*atan2(sqrt(h),sqrt(max(0.,1-h))))


def distribution(summary):
    values=[v for v in summary if v is not None and math.isfinite(v)]
    if not values:return {"n":0,"p05":None,"median":None,"p95":None}
    import numpy as np
    return {
        "n":len(values),"p05":float(np.quantile(values,.05)),
        "median":float(np.median(values)),"p95":float(np.quantile(values,.95)),
        "n_distance_le20m":sum(v<=20 for v in values),
        "n_distance_20_to_100m":sum(20<v<=100 for v in values),
        "n_distance_100_to_250m":sum(100<v<=250 for v in values),
        "n_distance_gt250m":sum(v>250 for v in values),
    }


def numeric_profile(numbers):
    vals=[finite_float(x) for x in numbers]
    valid=[v for v in vals if v is not None and v>0]
    if not valid:return {"positive_original_area_n":0}
    import numpy as np
    return {
        "positive_original_area_n":len(valid),
        "source_area_hectares_p05_median_p95":[
            float(v) for v in np.quantile(valid,[.05,.5,.95])
        ],
        "area_ge10000ha_source_named_locations":sum(v>=10000 for v in valid),
        "area_ge100000ha_source_named_locations":sum(v>=100000 for v in valid),
    }


def source_bird_colony_geo(records,loc,matched_year,matched_day):
    orig_head=[v47.norm(z) for z in records[0]]
    required={0:"location name",7:"english name",16:"breeding status",
              17:"colony code",18:"colony longitude",19:"colony latitude"}
    for index,label in required.items():
        if orig_head[index]!=label:
            raise ValueError("V49_FIBD_COLONY_FIELD_HEADER_SCHEMA_DRIFT:"+str(index+1))
    source_all=Counter()
    source_target=Counter()
    source_day=Counter()
    dists_all_centroid=[];dists_all_bird=[]
    dists_target_centroid=[];dists_target_bird=[]
    byyear=defaultdict(lambda:defaultdict(lambda:defaultdict(set)))
    byday=defaultdict(lambda:defaultdict(lambda:defaultdict(set)))
    guild_types=defaultdict(Counter)
    for r in records[1:]:
        guild=v47.bird_guild(r[7])
        if guild not in ("PENGUIN_FLIGHTLESS","SEABIRD_FLYING"):
            continue
        source_all["flight_group_source_records"]+=1
        name=v47.norm(r[0])
        if name not in loc:
            source_all["flight_group_original_location_not_unambiguous"]+=1
            continue
        yr,dt=v47.source_date(r,9,10,11)
        if yr is None:
            source_all["flight_group_year_outside_reliable_source_window"]+=1
            continue
        source_all["flight_group_source_rows_eligible_year_and_place"]+=1
        confirmed=v47.original_breeding_status(r[16])=="DEFINITE_RECORDED_BREEDING"
        if confirmed:source_all["flight_group_definite_breeding_rows"]+=1
        source_code_present=bool(v47.norm(r[COLON_CODE_COL]))
        cstat,coord=coordinate_state(r[COLON_LAT_COL],r[COLON_LON_COL])
        source_all["colony_"+cstat]+=1
        if source_code_present:source_all["colony_code_nonempty"]+=1
        islandstat,islandpt=coordinate_state(loc[name]["lat"],loc[name]["lon"])
        birdstat,birdpt=coordinate_state(r[BIRD_LAT_COL],r[BIRD_LON_COL])
        if coord is not None:
            islanddistance=distance_m(coord,islandpt)
            birddistance=distance_m(coord,birdpt)
            if islanddistance is not None:dists_all_centroid.append(islanddistance)
            if birddistance is not None:dists_all_bird.append(birddistance)
        key=(name,yr)
        if key not in matched_year or not confirmed:
            continue
        source_target["confirmed_guild_records_in_matched_V47_island_year"]+=1
        source_target["colony_"+cstat]+=1
        if source_code_present:source_target["colony_code_nonempty"]+=1
        if coord is not None:
            source_target["colony_has_both_finite_WGS84"]+=1
        distance=distance_m(coord,islandpt) if coord is not None else None
        birddistance=distance_m(coord,birdpt) if coord is not None else None
        if distance is not None:dists_target_centroid.append(distance)
        if birddistance is not None:dists_target_bird.append(birddistance)
        if coord is not None:
            byyear[key][guild]["valid"].add((round(coord[0],8),round(coord[1],8)))
            if distance is not None and distance>100:
                byyear[key][guild]["noncentroid"].add((round(coord[0],8),round(coord[1],8)))
        guild_types[guild][v47.norm(r[7])]+=1
        if dt and (name,dt) in matched_day:
            source_day["matched_confirmed_guild_original_day_rows"]+=1
            if coord is not None:
                byday[(name,dt)][guild]["valid"].add((round(coord[0],8),round(coord[1],8)))
                if distance is not None and distance>100:
                    byday[(name,dt)][guild]["noncentroid"].add((round(coord[0],8),round(coord[1],8)))

    pairs=list(matched_year)
    allboth=[pair for pair in pairs if all(byyear[pair][g]["valid"]
                          for g in ("PENGUIN_FLIGHTLESS","SEABIRD_FLYING"))]
    noncentroid=[pair for pair in pairs if all(byyear[pair][g]["noncentroid"]
                          for g in ("PENGUIN_FLIGHTLESS","SEABIRD_FLYING"))]
    allsame=[pair for pair in matched_day if all(byday[pair][g]["valid"]
                          for g in ("PENGUIN_FLIGHTLESS","SEABIRD_FLYING"))]
    exactnoncentroid=[pair for pair in matched_day if all(byday[pair][g]["noncentroid"]
                          for g in ("PENGUIN_FLIGHTLESS","SEABIRD_FLYING"))]
    comparable_regions={loc[pair[0]]["wider_area"]
                        for pair in exactnoncentroid if loc[pair[0]]["wider_area"]}
    g4=(len({pair[0] for pair in exactnoncentroid})>=MIN_G4_LOCALITIES
        and len(comparable_regions)>=MIN_G4_REGIONS)
    def names_to_source_category_counts(names):
        # Categories are source STRINGs and may include notes; export only
        # fixed non-sensitive generic whitelist categories, aggregate otherwise.
        keys=Counter()
        for name in names:
            info=loc[name]
            original=v47.norm(info.get("category",""))
            if re.fullmatch(r"(island|islet|rock|mainland|peninsula|coast|headland|group|tussac island|coastal island)",original):
                keys[original]+=1
            elif not original:
                keys["BLANK_OR_UNKNOWN"]+=1
            else:
                keys["OTHER_SOURCE_CATEGORY_UNINTERPRETED"]+=1
        return dict(sorted(keys.items()))
    candidate_names=sorted({n for n,y in matched_year})
    return {
      "source_row_source_all_guilds":dict(source_all),
      "source_rows_at_definite_matched_island_year":dict(source_target),
      "source_rows_at_matched_definite_date":dict(source_day),
      "source_original_colony_distance_to_island_reference_m_all_guild_records":
          distribution(dists_all_centroid),
      "source_original_colony_distance_to_bird_record_georeference_m_all_guild_records":
          distribution(dists_all_bird),
      "source_original_colony_distance_to_island_reference_m_V47_matched":
          distribution(dists_target_centroid),
      "source_original_colony_distance_to_bird_record_georeference_m_V47_matched":
          distribution(dists_target_bird),
      "V47_original_same_island_year_confirmed_source_pairs":len(matched_year),
      "V47_original_same_island_date_confirmed_source_pairs":len(matched_day),
      "same_year_both_guild_valid_colony_latlon_pairs":len(allboth),
      "same_year_both_guild_noncentroid_gt100m_colony_source_pairs":len(noncentroid),
      "same_year_both_guild_noncentroid_gt100m_distinct_source_locations":len({n for n,y in noncentroid}),
      "same_day_both_guild_valid_colony_latlon_pairs":len(allsame),
      "same_day_both_guild_noncentroid_gt100m_colony_source_pairs":len(exactnoncentroid),
      "same_day_both_guild_noncentroid_gt100m_distinct_source_locations":len({n for n,d in exactnoncentroid}),
      "same_day_both_guild_noncentroid_gt100m_publisher_region_groups":len(comparable_regions),
      "source_original_candidate_location_categories":names_to_source_category_counts(candidate_names),
      "source_original_candidate_location_areas":numeric_profile([loc[n]["area_ha"] for n in candidate_names]),
      "original_V47_66_named_sites_not_verified_independent_physical_island_polygons":True,
      "source_colony_coordinate_may_still_be_approximate_and_not_nest_GPS":True,
      "no_observer_or_colony_coordinates_exported":True,
      "G4_two_guild_noncentroid_original_colony_georef_support_pass":g4,
      "G2_field_verified_mammal_negative_exposure_support":False,
      "G3_common_bird_survey_detection_effort_support":False,
      "physical_shore_to_nest_route_estimated":False,
      "mammal_predation_or_penguin_flight_effect_fitted":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    result={
      "status":"V49_FALKLAND_ORIGINAL_COLONY_SITE_SOURCE_HOLD",
      "date":"2026-10-28",
      "contract":"contracts/PAPER2_FALKLAND_FIBD_ORIGINAL_COLONY_COORDINATE_V49.md",
      "original_Paper2_Q":"Can islands function as both mammalian refuges and flightless-breeder access bottlenecks?",
      "not_biological_effect_or_field_nest_positional_accuracy":True,
    }
    try:
        slugs=("fibdv8-20140601-locations","fibdv8-20140601-birds","fibdv8-20140601-visits")
        with ThreadPoolExecutor(max_workers=3) as pool:
            data={k:(rs,manifest) for k,rs,manifest in
                  pool.map(v47.fetch_first_party_workbook,slugs)}
        result["source_original_publisher_SHA_and_shape"]={k:v[1] for k,v in data.items()}
        loc,metadata=v47.locations_source(data["fibdv8-20140601-locations"][0])
        y,d,vis=v47.visits_source(data["fibdv8-20140601-visits"][0],loc)
        bird_v47,year,day=v47.birds_source(data["fibdv8-20140601-birds"][0],loc,y,d)
        if (len(year)!=EXPECTED_G1_YEAR or len({k[0] for k in year})!=EXPECTED_G1_LOCALITIES
            or len(day)!=EXPECTED_SAME_DATE):
            raise ValueError("V49_FROZEN_SOURCE_V47_69_66_63_REPRODUCTION_FAILED")
        result["source_original_named_places_metadata"]=metadata
        result["source_original_year_and_day_visit_metadata"]=vis
        result["V47_original_source_confirmed_guild_G1_pass"]=bird_v47["G1_predeclared_both_definite_guild_sample_gate_pass"]
        result["source_geolocation"]=source_bird_colony_geo(
            data["fibdv8-20140601-birds"][0],loc,year,day)
        result["status"]="V49_ORIGINAL_FALKLAND_COLONY_GEOREFERENCE_PROVENANCE_AUDITED"
    except Exception as e:
        result["status"]="V49_FIRST_PARTY_COLONY_GEOREFERENCE_SOURCE_HOLD"
        result["error"]=type(e).__name__+": "+str(e)[:650]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    s=result.get("source_geolocation",{})
    print(json.dumps({
        "status":result["status"],"source_G1":s.get("V47_original_same_island_year_confirmed_source_pairs"),
        "valid_source_colonies_both_guilds":s.get("same_year_both_guild_valid_colony_latlon_pairs"),
        "noncentroid_site_year":s.get("same_year_both_guild_noncentroid_gt100m_colony_source_pairs"),
        "same_day_noncentroid":s.get("same_day_both_guild_noncentroid_gt100m_colony_source_pairs"),
        "G4":s.get("G4_two_guild_noncentroid_original_colony_georef_support_pass"),
        "candidate_categories":s.get("source_original_candidate_location_categories"),
        "row_geo":s.get("source_rows_at_definite_matched_island_year"),
        "error":result.get("error")
    },ensure_ascii=False))
    if result["status"]!="V49_ORIGINAL_FALKLAND_COLONY_GEOREFERENCE_PROVENANCE_AUDITED":
        raise SystemExit(2)


if __name__=="__main__":
    main()
