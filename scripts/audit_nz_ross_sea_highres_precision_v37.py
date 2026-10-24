#!/usr/bin/env python3
"""V37 source-only high-res coastline position error audit for NZ Ross Sea Adélie.

NEVER loads numeric animal count magnitudes. Uses exact author locality source
and frozen V35 source observation-presence rosters; no V36 ecological effects.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path
import tempfile
from pyproj import Transformer
from shapely.geometry import Point,Polygon
from shapely.strtree import STRtree
import audit_nz_ross_sea_census_source_v33 as v33
import audit_nz_ross_sea_island_groups_v34 as v34
import audit_nz_ross_sea_add_island_geometry_v35 as v35
import validate_apbp_highres_coast_v4 as h4
import link_apbp_to_add_island_rock_v3 as v3

BASE=Path(__file__).resolve().parents[1]
FROZEN_V35=BASE/"results"/"NZ_ROSS_SEA_SCAR_ISLAND_GEO_V35.json"
HIGHSRC_DOI="10.5285/13c4d2f1-8903-4d7f-8977-592121975554"
PREVIOUS_MEDIUM_SHA="b0172d698436f871f49339cea5c7155e3d98648360521cc4bbc44a026c0edc38"
CENSUS_SHA="23a95d9e693dd095e085534f2c215b79880a72fe9cfb5a59337501192dae03e6"
LOCATION_SHA="d744e7493f85564f1b634f390a5e4a976b2d5359a6f93cdd9ef345639661b6a6"
FROZEN_UNITS=("Beaufort Island","Coulman Island","Inexpressible Island","Ross Island")
FROZEN_LAND_IDS={"Beaufort Island":50,"Coulman Island":37,
                  "Inexpressible Island":43,"Ross Island":59}
FROZEN_13=(1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,2001,2004,2005)
MAX_NEAR_M=2000.
MIN_GEOGRAPHIC_ISLANDS=3
MIN_ISLAND_YEARS=5
MIN_COINCIDENT_YEARS=8

def coordinate_envelope(latitude,longitude,transformer,arcminutes):
    delta=arcminutes/60.0
    corners=[(longitude-delta,latitude-delta),
             (longitude+delta,latitude-delta),
             (longitude+delta,latitude+delta),
             (longitude-delta,latitude+delta)]
    points=[transformer.transform(lon,lat) for lon,lat in corners]
    geom=Polygon(points)
    if geom.is_empty or not geom.is_valid or geom.area<=0:
        raise ValueError("COORD_STOP source rounded-coordinate envelope invalid")
    return geom

def classify_geo_point(point,latitude,longitude,transformer,polygons,tree,largest):
    found=list(map(int,tree.query(point.buffer(MAX_NEAR_M))))
    inside=[i for i in found if polygons[i].covers(point)]
    if len(inside)>1:
        return {"status":"HOLD_MULTIPLE_ORIGINAL_HIGHRES_LAND_POLYGONS","polygon_id":None}
    if len(inside)==1:
        fid=inside[0]
        kind="EXACT_ONE_LAND_POLYGON"
    else:
        nearby=[i for i in found if polygons[i].distance(point)<=MAX_NEAR_M]
        if len(nearby)!=1:
            return {"status":"HOLD_MULTIPLE_NEAR_LAND" if nearby else "HOLD_NO_LAND_WITHIN_2KM",
                    "polygon_id":None}
        fid=nearby[0]
        kind="NEAR_UNIQUE_LAND_WITHIN_2KM_PROVISIONAL"
    valid_land=fid!=largest
    exact=(kind=="EXACT_ONE_LAND_POLYGON" and valid_land)
    rect_half=coordinate_envelope(latitude,longitude,transformer,0.5)
    rect_one=coordinate_envelope(latitude,longitude,transformer,1.0)
    return {
       "status":kind,
       "polygon_id":fid,
       "landtype":"SEPARATE_LAND_POLYGON_PROXY" if valid_land else "CONTINENT_LARGEST_POLYGON_PROXY",
       "distance_to_polygon_m":round(float(polygons[fid].distance(point)),1),
       "distance_to_highres_land_boundary_m":round(float(point.distance(polygons[fid].boundary)),1),
       "source_reported_georef_center_exact_island":exact,
       "rounded_half_arcminute_rectangle_on_one_land_feature":bool(exact and polygons[fid].covers(rect_half)),
       "round_or_truncate_conservative_one_arcminute_rectangle_on_one_land_feature":bool(
           exact and polygons[fid].covers(rect_one)),
       "source_coordinates_only_full_arcminute_precision":True,
    }

def load_fixed_v35():
    receipt=json.loads(FROZEN_V35.read_text(encoding="utf-8"))
    if receipt.get("status")!="V35_ORIGINAL_NZ_ROSS_SEA_COASTLINE_ISLAND_PANEL_GEOMETRY_QA":
        raise ValueError("SOURCE_STOP frozen V35 status drift")
    if (receipt.get("publisher_census_sha256")!=CENSUS_SHA or
        receipt.get("publisher_location_sha256")!=LOCATION_SHA or
        receipt.get("original_SCAR_ADD_medium_ZIP_SHA256")!=PREVIOUS_MEDIUM_SHA):
        raise ValueError("SOURCE_STOP original publisher/GIS source provenance drift")
    expected={**FROZEN_LAND_IDS,"Possession Island":29}
    if receipt.get("original_group_to_GIS_landpolygonID")!=expected:
        raise ValueError("SOURCE_STOP frozen original island group roster drift")
    cohort=receipt["prespecified_original_GIS_locus_year_support"]
    if cohort["source_years_with_ge2_named_GIS_island_units"]!=list(FROZEN_13):
        raise ValueError("SOURCE_STOP V35 source year cohort drift")
    assert set(FROZEN_UNITS).issubset(cohort["source_named_GIS_island_temporal_support"])
    return receipt

def original_publisher_sites():
    with __import__("requests").Session() as session:
        found,meta=v33.ckandownloads(session)
    if (found["census"]["receipt"]["sha256"]!=CENSUS_SHA or
        found["locations"]["receipt"]["sha256"]!=LOCATION_SHA):
        raise ValueError("SOURCE_STOP official NZ colony/locations source changed")
    census=v33.workbook_original(found["census"]["raw"])
    loc=v33.workbook_original(found["locations"]["raw"])
    if set(census)!={"All data"} or len(loc)!=1:
        raise ValueError("SOURCE_STOP source original workbook sheets drift")
    return v34.source_crosswalk(census["All data"],next(iter(loc.values())))

def high_source_zip_and_shapes(sites):
    previous=v3.MAX_BYTES
    try:
        v3.MAX_BYTES=h4.HIGH_ZIP_LIMIT
        original=v3.fetch_bas(h4.HIGH_URL)
    finally:
        v3.MAX_BYTES=previous
    sha=hashlib.sha256(original).hexdigest()
    with tempfile.TemporaryDirectory(prefix="nz-ross-highres-v37-") as tmp:
        shapes,meta=h4.original_highres_shapes(original,Path(tmp),sites)
    return shapes,meta,{"sha256":sha,"original_bytes":len(original),"doi":HIGHSRC_DOI,
                        "source_url":h4.HIGH_URL,"source_version":"SCAR_ADD_7.12_2026"}

def source_geomatch(source,shapes):
    transf=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    land=[r[1] for r in shapes]
    tree=STRtree(land)
    mainland=max(range(len(land)),key=lambda i:land[i].area)
    source_links=[]
    for row in source["site_to_named_island_crosswalk"]:
        name=row["original_census_colony"]
        lat=row["original_site_coordinate_approx_lat"]
        lon=row["original_site_coordinate_approx_lon"]
        if lat is None or lon is None:
            match={"status":"HOLD_ORIGINAL_GEOREFERENCE_NOT_PARSED","polygon_id":None}
        else:
            x,y=transf.transform(lon,lat)
            match=classify_geo_point(Point(x,y),lat,lon,transf,land,tree,mainland)
        source_links.append({"original_colony":name,
            "original_source_named_island":row["publisher_explicit_island_group"],
            **match})
    return source_links,{"source_independent_highres_land_polygons":len(land),
                         "highres_largest_contiguous_land_polygon_proxy_index":mainland,
                         "site_match_categories":dict(Counter(z["status"] for z in source_links))}

def support_from_geo_links(frozen,links):
    source_panel=frozen["prespecified_original_GIS_locus_year_support"]["source_named_GIS_island_temporal_support"]
    source_named={name:row for name,row in ((r["original_colony"],r) for r in links)
                  if name}
    filters={
       "center_exact":"source_reported_georef_center_exact_island",
       "half_minute_stable":"rounded_half_arcminute_rectangle_on_one_land_feature",
       "one_minute_stable":"round_or_truncate_conservative_one_arcminute_rectangle_on_one_land_feature"
    }
    scores={}
    for variant,condition in filters.items():
        candidate={}
        for isle in FROZEN_UNITS:
            roster=source_panel[isle]["source_colony_roster"]
            matched=[source_named[c] for c in roster
                     if c in source_named and source_named[c].get(condition)]
            featureids={row["polygon_id"] for row in matched}
            # If source colony points on supposedly one island are split into
            # different features, the entire island's qualified subset HOLDS.
            if len(featureids)!=1:matched=[]
            candidate[isle]={"polygon_id":next(iter(featureids)) if len(featureids)==1 else None,
                             "source_colonies":sorted(x["original_colony"] for x in matched)}
        collisions={id for id,n in Counter(rec["polygon_id"] for rec in candidate.values()
                        if rec["polygon_id"] is not None).items() if n>1}
        for island in candidate:
            if candidate[island]["polygon_id"] in collisions:
                candidate[island]={"polygon_id":None,"source_colonies":[]}
        totals={}
        observed=defaultdict(list)
        for island in FROZEN_UNITS:
            allowed=set(candidate[island]["source_colonies"])
            yearly={}
            for year,original in source_panel[island]["original_fixed_source_colonies_by_annual_window"].items():
                pair=sorted(x for x in original if x in allowed)
                if pair:
                    yearly[int(year)]=pair
                    if int(year) in FROZEN_13:observed[int(year)].append(island)
            totals[island]={"highres_qualified_source_colony_labels":sorted(allowed),
                "original_highres_feature_id":candidate[island]["polygon_id"],
                "source_any_same_colony_original_year_windows":len(yearly),
                "same_original_year_roster":sorted(yearly)}
        aligned=sorted(y for y,names in observed.items() if len(names)>=2)
        eligible=sum(r["source_any_same_colony_original_year_windows"]>=MIN_ISLAND_YEARS for r in totals.values())
        scores[variant]={
            "islands_with_at_least_five_original_year_pairs":eligible,
            "coincident_year_starts_at_least_two_islands":aligned,
            "n_original_shared_source_year_starts":len(aligned),
            "island_source_metadata":totals,
            "passes_frozen_island_and_annual_coverage_gate":(
                eligible>=MIN_GEOGRAPHIC_ISLANDS and len(aligned)>=MIN_COINCIDENT_YEARS),
            "island_group_polygons_unique":True,
        }
    return scores

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",required=True,type=Path)
    args=p.parse_args()
    receipt={"status":"HOLD_ORIGINAL_HIGHRES_SOURCE","ecological_effects_fitted":0}
    try:
        frozen=load_fixed_v35()
        source=original_publisher_sites()
        earlier={r["original_colony"] for r in frozen["original_colony_geo_link_records"]}
        current={r["original_census_colony"] for r in source["site_to_named_island_crosswalk"]}
        if earlier!=current or len(earlier)!=33:
            raise ValueError("SOURCE_STOP 33 exact author named colony geo references changed")
        tr=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
        sites={}
        for r in source["site_to_named_island_crosswalk"]:
            lat=r["original_site_coordinate_approx_lat"]
            lon=r["original_site_coordinate_approx_lon"]
            if lat is None or lon is None:continue
            x,y=tr.transform(lon,lat)
            sites[r["original_census_colony"]]=[{"x":x,"y":y}]
        polygons,geometa,receiptgis=high_source_zip_and_shapes(sites)
        rows,linkmeta=source_geomatch(source,polygons)
        stage=support_from_geo_links(frozen,rows)
        robust=stage["one_minute_stable"]
        receipt={
            "status":"V37_HIGH_RESOLUTION_SCAR_GEOREFERENCE_ENVELOPE_AUDIT",
            "frozen_design":"contracts/NZ_ROSS_SEA_HIGHRES_SOURCE_UNCERTAINTY_V37.md",
            "original_publisher_2026_NZ_census_sha256":CENSUS_SHA,
            "original_publisher_2026_NZ_location_sha256":LOCATION_SHA,
            "medium_V35_source_sha256":PREVIOUS_MEDIUM_SHA,
            "original_new_highresolution_coast_source":receiptgis,
            "original_source_highres_polygon_metadata":geometa,
            "site_geometry_source_QA":linkmeta,
            "source_colony_geo_qualifications":rows,
            "geographic_rounded_source_precision_scenarios":stage,
            "publisher_census_population_magnitudes_read":0,
            "original_penguin_growth_correlations_fitted":0,
            "original_13year_V36_ecological_effect_unchanged":True,
            "scientific_decision":(
                "PROCEED_INDEPENDENT_GEOGRAPHY_STABLE_NEW_TEST_DESIGN_ONLY"
                if robust["passes_frozen_island_and_annual_coverage_gate"]
                else "HOLD_COARSE_COLONY_GEOREFERENCE_NOT_FULL_ISLAND_ROBUST")
        }
    except Exception as ex:
        receipt["error_type"]=type(ex).__name__
        receipt["error"]=str(ex)[:650]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_ORIGINAL_HIGHRES_SOURCE":
        raise SystemExit(2)

if __name__=="__main__":
    main()
