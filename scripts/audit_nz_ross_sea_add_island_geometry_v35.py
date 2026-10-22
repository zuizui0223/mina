#!/usr/bin/env python3
"""V35. Source verified SCAR-ADD 2026 land polygon IDs for NZ Ross Sea colonies.

Strictly source metadata and count PRESENCE only. Original bird count magnitudes
cannot influence polygon selection, island identity or the fixed year support.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import tempfile
import requests
from pyproj import Transformer
from shapely.geometry import Point
from shapely.strtree import STRtree
import audit_nz_ross_sea_census_source_v33 as v33
import audit_nz_ross_sea_island_groups_v34 as v34
import link_apbp_to_add_island_rock_v3 as v3

GIS_SHA="b0172d698436f871f49339cea5c7155e3d98648360521cc4bbc44a026c0edc38"
GIS_DOI="10.5285/c9c6d671-ad19-4a78-96b2-7d47e9bac46a"
SOURCE_CENSUS_SHA=v34.CENSUS_SHA
SOURCE_LOCATION_SHA=v34.LOCATION_SHA
MAX_NEAR_COAST_M=2000.
LAST_STRICT_Y_START=2016
MIN_ISLANDS=3
MIN_ISLAND_WINDOWS=5
MIN_CONCURRENT_YEARS=8

def link_geometry(point,polygons,tree,continental_idx):
    nearest=list(map(int,tree.query(point.buffer(MAX_NEAR_COAST_M))))
    inside=[i for i in nearest if polygons[i].covers(point)]
    if len(inside)==1:
        choice=inside[0];status="EXACT_ONE_LAND_POLYGON"
    elif len(inside)>1:
        return {"status":"HOLD_MULTIPLE_OVERLAPPING_LAND",
                "land_polygon_feature_id":None}
    else:
        candidates=[i for i in nearest if polygons[i].distance(point)<=MAX_NEAR_COAST_M]
        if len(candidates)!=1:
            return {"status":("HOLD_MULTIPLE_NEAR_LAND" if candidates
                              else "HOLD_NO_LAND_IN_2KM"),
                    "land_polygon_feature_id":None}
        choice=candidates[0];status="NEAR_UNIQUE_LAND_WITHIN_2KM_PROVISIONAL"
    return {"status":status,
            "land_polygon_feature_id":int(choice),
            "provisional_land_class":("CONTINENT_LARGEST_POLYGON_PROXY"
                if choice==continental_idx else "SEPARATE_LAND_POLYGON_PROXY"),
            "distance_source_georeference_to_land_m":round(float(polygons[choice].distance(point)),2),
            "original_land_area_km2":round(float(polygons[choice].area/1e6),3),
            "source_location_original_minutes_not_centimetre_precise":True}

def original_and_add_source():
    with requests.Session() as session:
        found,meta=v33.ckandownloads(session)
    if found["census"]["receipt"]["sha256"]!=SOURCE_CENSUS_SHA or \
       found["locations"]["receipt"]["sha256"]!=SOURCE_LOCATION_SHA:
        raise ValueError("SOURCE_STOP pinned NZ 2026 census/site source changed")
    src=v33.workbook_original(found["census"]["raw"])
    loc=v33.workbook_original(found["locations"]["raw"])
    if set(src)!={"All data"} or len(loc)!=1:
        raise ValueError("SOURCE_STOP original NZ source sheets changed")
    original=v34.source_crosswalk(src["All data"],next(iter(loc.values())))
    blob=v3.fetch_bas(v3.COAST_ZIP)
    if hashlib.sha256(blob).hexdigest()!=GIS_SHA:
        raise ValueError("SOURCE_STOP original 2026 SCAR medium coastline SHA changed")
    return original,blob,meta

def geographic_eligibility(original,features):
    geoms=[f[1] for f in features]
    tree=STRtree(geoms)
    mainland_idx=max(range(len(geoms)),key=lambda x:geoms[x].area)
    transform=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    linked=[]
    for r in original["site_to_named_island_crosswalk"]:
        name=r["original_census_colony"]
        group=r["publisher_explicit_island_group"]
        lat=r["original_site_coordinate_approx_lat"]
        lon=r["original_site_coordinate_approx_lon"]
        if lat is None or lon is None or not -90<=lat<=-60 or not -180<=lon<=180:
            row={"original_colony":name,"source_named_landmass":group,
                 "status":"HOLD_COARSE_SOURCE_LAT_LON_NOT_PARSED","land_polygon_feature_id":None}
        else:
            px,py=transform.transform(lon,lat)
            geo=link_geometry(Point(px,py),geoms,tree,mainland_idx)
            row={"original_colony":name,"source_named_landmass":group,
                 **geo}
        linked.append(row)
    grouped=defaultdict(list)
    for item in linked:
        if item["source_named_landmass"]:
            grouped[item["source_named_landmass"]].append(item)
    groupedIDs={}
    site_island={}
    for landmass,rows in sorted(grouped.items()):
        valid=[r for r in rows if r.get("land_polygon_feature_id") is not None and
               r.get("provisional_land_class")=="SEPARATE_LAND_POLYGON_PROXY"]
        ids={r["land_polygon_feature_id"] for r in valid}
        if len(ids)==1 and valid:
            polygon=next(iter(ids))
            groupedIDs[landmass]=polygon
            for r in valid:
                site_island[r["original_colony"]]=landmass
    # Explicit different island name cannot share same original land polygon ID.
    duplicatepolygons={poly for poly,n in Counter(groupedIDs.values()).items() if n>1}
    groups_on_bad_polygons=[name for name,poly in groupedIDs.items() if poly in duplicatepolygons]
    for bad in groups_on_bad_polygons:
        groupedIDs.pop(bad,None)
        for k in list(site_island):
            if site_island[k]==bad:site_island.pop(k)
    return linked,groupedIDs,site_island,{
        "original_source_geo_eligible_names":len(site_island),
        "original_source_named_islands_with_geographically_unambiguous_polygon":len(groupedIDs),
        "GIS_land_features_available":len(geoms),
        "GIS_largest_land_polygon_is_mainland_proxy_not_island":True,
        "publisher_named_islands_in_conflict_with_original_polygon_ID":groups_on_bad_polygons,
        "GIS_link_types":dict(Counter(r["status"] for r in linked)),
        "geographic_unit_recognition_incomplete_due_1arcmin_source_coordinates":True,
    }

def temporal_support(source_sites,site_island):
    bysite,_=v34.colony_year_presence(source_sites)
    source_present={name:obs for name,obs in (record for record in bysite.values())
                    if name in site_island}
    islands=defaultdict(dict)
    for name,years in source_present.items():
        islands[site_island[name]][name]=years
    byisland={}
    yearislands=defaultdict(list)
    for area,sites in sorted(islands.items()):
        windows={}
        for y in range(1981,LAST_STRICT_Y_START+1):
            paired=sorted(name for name,ys in sites.items() if y in ys and y+1 in ys)
            if paired:
                windows[y]=paired
                yearislands[y].append(area)
        byisland[area]={
            "GIS_source_named_island":area,
            "GIS_colony_count":len(sites),
            "source_colony_roster":sorted(sites),
            "original_same_colony_adjacent_year_window_count":len(windows),
            "original_pair_start_year_roster":sorted(windows),
            "original_fixed_source_colonies_by_annual_window":{
                str(y):names for y,names in windows.items()},
        }
    qualified=sum(row["original_same_colony_adjacent_year_window_count"]>=MIN_ISLAND_WINDOWS
                  for row in byisland.values())
    aligned=sorted(y for y,n in yearislands.items() if len(n)>=2)
    return {
        "source_original_GIS_island_units_with_ge5_annual_windows":qualified,
        "source_years_with_ge2_named_GIS_island_units":aligned,
        "source_original_calendar_year_start_upper_bound_due_method_document":LAST_STRICT_Y_START,
        "n_source_annual_windows_with_ge2_polygon_distinct_islands":len(aligned),
        "source_named_GIS_island_temporal_support":byisland,
        "source_geography_and_calendar_gate_pass":(
            qualified>=MIN_ISLANDS and len(aligned)>=MIN_CONCURRENT_YEARS),
        "original_animal_count_magnitudes_opened":0,
        "original_2020_missing_is_not_biological_zero":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",type=Path,required=True)
    args=p.parse_args()
    receipt={"status":"HOLD_ORIGINAL_GIS_OR_GEOREF","ecological_effects_fitted":0}
    try:
        metadata,blob,src=original_and_add_source()
        with tempfile.TemporaryDirectory(prefix="ross-sea-v35-") as path:
            shp=v3.unpack_shapefile(blob,Path(path))
            features,shapemeta=v3.mapped_features(shp,require_surface=True)
            linked,landmasses,site_island,geo_qa=geographic_eligibility(metadata,features)
        with requests.Session() as session:
            found,_=v33.ckandownloads(session)
        source=v33.workbook_original(found["census"]["raw"])
        support=temporal_support(source["All data"],site_island)
        receipt={
            "status":"V35_ORIGINAL_NZ_ROSS_SEA_COASTLINE_ISLAND_PANEL_GEOMETRY_QA",
            "frozen_contract":"contracts/NZ_ROSS_SEA_GIS_PHYSICAL_ISLANDS_V35.md",
            "publisher_census_sha256":SOURCE_CENSUS_SHA,
            "publisher_location_sha256":SOURCE_LOCATION_SHA,
            "original_SCAR_ADD_medium_coast_DOI":GIS_DOI,
            "original_SCAR_ADD_medium_ZIP_SHA256":GIS_SHA,
            "original_SCAR_ADD_field_metadata":shapemeta,
            "original_colony_geo_link_records":linked,
            "original_group_to_GIS_landpolygonID":landmasses,
            "original_geographic_source_support":geo_qa,
            "prespecified_original_GIS_locus_year_support":support,
            "source_group_names_not_true_historic_nesting_capacity":True,
            "no_sea_ice_wind_animal_effects_fitted":True,
            "scientific_decision":(
                "PROCEED_SEPARATELY_FROZEN_DESCRIPTIVE_ISLAND_GROWTH_ONLY"
                if support["source_geography_and_calendar_gate_pass"]
                else "HOLD_INSUFFICIENT_GIS_PHYSICAL_ISLAND_YEAR_SUPPORT")
        }
    except Exception as e:
        receipt["error_type"]=type(e).__name__
        receipt["error"]=str(e)[:700]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_ORIGINAL_GIS_OR_GEOREF":
        raise SystemExit(2)

if __name__=="__main__":
    main()
