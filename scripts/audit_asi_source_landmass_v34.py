#!/usr/bin/env python3
"""V34 all 113 original ASI published census sites × SCAR original land polygons.

Original 2013 source geography only selects land IDs; breeding abundance not
used for polygon matching. Independently QA previously locked 562 nest-stage
original ASI count series support, no island ecological model fitted.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import hashlib
import csv
import json
import math
from pathlib import Path
import tempfile

from pyproj import Transformer,Geod
from shapely.geometry import Point
from shapely.strtree import STRtree

from audit_asi_original_census_v33 import (
    download_publisher_csv,parse_original_rows,parse_number,accuracy_code
)
import link_apbp_to_add_island_rock_v3 as bas
import validate_apbp_highres_coast_v4 as coast

CSV_SHA="e01ee9bfbd8337bcaca7c71aea0b00162f9015cf4954d3ad76eed536cad37634"
LAND_ZIP_SHA="66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4"
WGS84_TO_3031=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
GEO=Geod(ellps="WGS84")
GAPS=(250,2000)
ASI_ORIGINAL_REGIONS=("CW","EI","NE","NW","SH","SO","SW")


def original_site_coordinates(rows):
    source=defaultdict(list)
    for r in rows:
        sid=r.get("Site_ID","")
        if not sid:raise ValueError("SOURCE_STOP original ASI source row missing Site_ID")
        source[sid].append(r)
    mapping={}
    for sid,rs in sorted(source.items()):
        coords=set()
        valid=0
        for r in rs:
            try:
                lat=float(r["Latitude"]);lon=float(r["Longitude"])
                if (math.isfinite(lat) and math.isfinite(lon)
                    and -90<=lat<=-50 and -180<=lon<=180):
                    coords.add((lat,lon))
                    valid+=1
            except (ValueError,TypeError):pass
        regions=set(str(x.get("Region","")).upper() for x in rs)
        names=set(str(x.get("Site_name","")).strip() for x in rs)
        status=(
            "EXACT_ONE_ORIGINAL_SITE_LATLON_AND_REGION"
            if len(coords)==1 and len(regions)==1 and not "" in regions
            else "HOLD_UNSTABLE_SOURCE_SITE_COORDINATE_OR_REGION"
        )
        mapping[sid]={
            "original_site_id":sid,
            "source_original_rows_total":len(rs),
            "source_original_distinct_coordinate_pairs":len(coords),
            "source_original_rows_with_valid_coordinates":valid,
            "source_original_region_labels":sorted(regions),
            "source_original_distinct_site_names":len(names),
            "source_coordinate_status":status,
            "author_latlon":next(iter(coords)) if len(coords)==1 else None,
        }
    return mapping


def source_geography_to_land(site_locations:dict,land:list):
    landgeom=[x[1] for x in land]
    idx=STRtree(landgeom)
    largestland=max(land,key=lambda x:x[1].area)[0]
    output=[]
    for sid,source in sorted(site_locations.items()):
        p=None
        assigned_id=None
        nearest=None
        is_largest=None
        category=source["source_coordinate_status"]
        latlon=source["author_latlon"]
        if source["source_coordinate_status"]=="EXACT_ONE_ORIGINAL_SITE_LATLON_AND_REGION":
            lat,lon=latlon
            x,y=WGS84_TO_3031.transform(lon,lat)
            if not all(map(math.isfinite,(x,y))):
                raise ValueError("GEOMETRY_STOP original site source geographic projection invalid")
            p=Point(x,y)
            covered=[int(i) for i in idx.query(p) if landgeom[int(i)].covers(p)]
            if len(covered)==1:
                assigned_id=land[covered[0]][0]
                is_largest=bool(assigned_id==largestland)
                category="EXACT_ONE_SOURCE_LAND_POLYGON"
                nearest=0.0
            elif len(covered)>1:
                category="HOLD_MULTIPLE_LAND_POLYGONS_COVER_POINT"
            else:
                best_idx=int(idx.nearest(p))
                nearest=float(landgeom[best_idx].distance(p))
                if nearest<=GAPS[0]:
                    category="HOLD_OUTSIDE_LAND_WITHIN_250M"
                elif nearest<=GAPS[1]:
                    category="HOLD_OUTSIDE_LAND_250_TO_2000M"
                else:
                    category="HOLD_OUTSIDE_LAND_OVER_2000M"
        output.append({
            "original_Site_ID":sid,
            "source_original_region":next(iter(source["source_original_region_labels"]))
                if len(source["source_original_region_labels"])==1 else None,
            "source_geographic_source_author_coordinates_stable":bool(
                source["source_coordinate_status"]=="EXACT_ONE_ORIGINAL_SITE_LATLON_AND_REGION"),
            "source_original_coordinate_pair_variants":source["source_original_distinct_coordinate_pairs"],
            "source_original_record_count":source["source_original_rows_total"],
            "source_geographical_parent_land_status":category,
            "source_exact_original_SCAR_land_FID":assigned_id,
            "source_parent_land_polygon_is_largest_continental_proxy":is_largest,
            "source_minimum_land_polygon_boundary_gap_m":nearest,
            "provisional_near_coast_not_assigned_to_landmass":assigned_id is None,
            "source_SiteID_is_official_distinct_island":False,
            "source_observed_point_is_exact_nest_GPS":False,
        })
    mapped={r["original_Site_ID"]:r for r in output}
    parents=defaultdict(list)
    for r in output:
        if r["source_exact_original_SCAR_land_FID"] is not None:
            parents[str(r["source_exact_original_SCAR_land_FID"])].append(r["original_Site_ID"])
    q=Counter(r["source_geographical_parent_land_status"] for r in output)
    regions=defaultdict(Counter)
    for r in output:
        regions[str(r["source_original_region"])][r["source_geographical_parent_land_status"]]+=1
    report={
        "source_original_Site_ID_count":len(output),
        "source_original_site_land_status":dict(sorted(q.items())),
        "original_geographic_region_by_land_polygon_match_status":{
            k:dict(sorted(x.items())) for k,x in sorted(regions.items())},
        "original_distinct_mapped_parent_land_FIDs":len(parents),
        "original_parent_land_polygons_with_two_or_more_original_Site_IDs":
            sum(len(v)>=2 for v in parents.values()),
        "original_Site_IDs_with_exact_mapped_parent_land":sum(
            r["source_exact_original_SCAR_land_FID"] is not None for r in output),
        "original_source_site_groups_with_identical_land_feature_FID":{
            k:sorted(v) for k,v in sorted(parents.items()) if len(v)>=2},
        "original_largest_source_mapped_land_FID_continental_proxy":largestland,
        "source_reported_site_centroid_is_verified_colony_nest_GPS":False,
        "original_source_land_polygon_is_named_independent_island":False,
        "ecological_breeding_growth_or_island_effect_fitted":False,
    }
    return output,report


def source_quality_subset(rows):
    sample=[]
    for r in rows:
        if (r["Source"].upper()!="ASI" or
            r["Counted_object"].upper()!="N" or
            accuracy_code(r["Accuracy"]) not in (1,2) or
            not r["Site_ID"] or not r["Species"] or
            not r["Season"].isdecimal() or len(r["Season"])!=4):
            continue
        value=parse_number(r["Count"])
        if value is not None and value>0:
            try:
                lat=float(r["Latitude"]);lon=float(r["Longitude"])
            except ValueError:continue
            if math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=-50 and -180<=lon<=180:
                sample.append(r)
    dups=Counter((r["Site_ID"],r["Species"].upper(),r["Season"]) for r in sample)
    exact=[r for r in sample if dups[(r["Site_ID"],r["Species"].upper(),r["Season"])]==1]
    if len(exact)!=562:
        raise ValueError("SOURCE_STOP original V33 frozen 562 ASI nest stage cohort not reproducible")
    return exact


def support_highquality_breeding_sources(sample,site_land):
    land_lookup={r["original_Site_ID"]:r for r in site_land}
    accepted=[r for r in sample
              if land_lookup[r["Site_ID"]]["source_exact_original_SCAR_land_FID"] is not None]
    byregion=defaultdict(set)
    byland=defaultdict(set)
    byplace_taxon=defaultdict(set)
    for r in accepted:
        name=r["Site_ID"];taxon=r["Species"].upper()
        byregion[r["Region"]].add(name)
        landid=str(land_lookup[name]["source_exact_original_SCAR_land_FID"])
        byland[landid].add(name)
        byplace_taxon[(name,taxon)].add(int(r["Season"]))
    # Source-only support gate: author Site_ID may not be same as island;
    # this is not inference about site-size/stability.
    return {
      "original_V33_exact_stage_primary_ASI_nest_source_rows":len(sample),
      "original_V33_original_site_IDs_in_qualifying_sample":len(
         {r["Site_ID"] for r in sample}),
      "qualified_rows_with_strict_source_land_polygon":len(accepted),
      "qualified_original_site_IDs_with_strict_parent_land":len(
         {r["Site_ID"] for r in accepted}),
      "qualified_sample_distinct_matched_parent_land_polygon_FIDs":len(byland),
      "qualified_source_sites_by_original_region_with_strict_land_match":{
          k:len(v) for k,v in sorted(byregion.items())},
      "qualified_sample_parent_land_features_with_two_or_more_Site_IDs":sum(
          len(v)>=2 for v in byland.values()),
      "qualified_matched_site_taxon_2_or_more_nest_seasons":sum(
          len(v)>=2 for v in byplace_taxon.values()),
      "original_three_region_landmass_breeding_effect_ready_without_effort_or_habitat":False,
      "unmatched_source_field_colonies_dropped_as_true_absence":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--sites",type=Path,required=True)
    a=p.parse_args()
    result={"status":"HOLD_SOURCE_ASI_ORIGINAL_LAND_MATCH_V34",
            "ecological_breeding_growth_or_island_effect_fitted":False}
    try:
        source=download_publisher_csv()
        if hashlib.sha256(source).hexdigest()!=CSV_SHA:
            raise ValueError("SOURCE_STOP original 2013 first-party ASI SHA drift")
        rows,_=parse_original_rows(source)
        original_sites=original_site_coordinates(rows)
        if len(original_sites)!=113:
            raise ValueError("SOURCE_STOP original 113 ASI Site_ID cohort drift")
        oldmax=bas.MAX_BYTES
        try:
            bas.MAX_BYTES=coast.HIGH_ZIP_LIMIT
            landblob=bas.fetch_bas(coast.HIGH_URL)
        finally:
            bas.MAX_BYTES=oldmax
        if hashlib.sha256(landblob).hexdigest()!=LAND_ZIP_SHA:
            raise ValueError("SOURCE_STOP original SCAR coastline ZIP SHA changed")
        with tempfile.TemporaryDirectory(prefix="ASI-physical-land-") as tmp:
            land,metadata=coast.original_highres_shapes(landblob,Path(tmp)/"land",{})
        sites,geography=source_geography_to_land(original_sites,land)
        frozen=source_quality_subset(rows)
        nstar=support_highquality_breeding_sources(frozen,sites)
        result={
            "status":"ASI_ORIGINAL_113_FIELD_SITE_SCAR_PARENT_LAND_SOURCE_V34",
            "original_ASI_CSV_SHA256":CSV_SHA,
            "original_SCAR_land_v712_ZIP_SHA256":LAND_ZIP_SHA,
            "original_SCAR_land_polygon_feature_n":len(land),
            "original_source_ASI_all_site_geography":geography,
            "original_2013_N_stage_accurate_ASI_breeding_sample_land_support":nstar,
            "original_source_land_geometry_QA":metadata,
            "historical_colony_GPS_survey_uncertainty_currently_unverified":True,
            "source_parent_land_equals_oceanic_island_or_nunatak_unverified":True,
            "original_source_nests_not_reclassified_to_visited_absence":True,
            "new_island_macro_population_model_fit":False,
        }
        a.sites.parent.mkdir(parents=True,exist_ok=True)
        with a.sites.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(sites[0]))
            writer.writeheader();writer.writerows(sites)
        result["derived_original_113_site_source_land_CSV_SHA256"]=hashlib.sha256(
            a.sites.read_bytes()).hexdigest()
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:1400]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
