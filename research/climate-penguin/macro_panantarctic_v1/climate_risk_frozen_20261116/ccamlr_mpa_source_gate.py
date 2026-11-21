#!/usr/bin/env python3
"""Potential colony access zones vs officially adopted CCAMLR MPA polygons.

A colony POINT in a terrestrial setting is never interpreted as presence
inside a marine protected foraging area. Marine buffer fractions are only
hypothetical accessible ocean, not actual tracked bird foraging.
Strictly fails closed when independently checked CCAMLR zone geometries and
marine-mask provenance cannot be supplied.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
RADII=(50,100,200)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--sites",type=Path,required=True)
    parser.add_argument("--ccamlr-geojson",type=Path)
    parser.add_argument("--marine-mask-geojson",type=Path)
    parser.add_argument("--official-source-manifest",type=Path)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    sites=pd.read_csv(args.sites)
    assert {"site_id","latitude","longitude"}.issubset(sites.columns)
    assert sites.site_id.is_unique and sites.latitude.between(-90,-55).all()
    gate={
      "status":"NO_GO_PROTECTION_COVERAGE",
      "n_known_colony_identifiers":len(sites),
      "source_site_sha256":hashlib.sha256(args.sites.read_bytes()).hexdigest(),
      "protected_area_polygons_supplied":bool(args.ccamlr_geojson),
      "marine_mask_supplied":bool(args.marine_mask_geojson),
      "official_provenance_manifest_supplied":bool(args.official_source_manifest),
      "not_a_direct_bird_foraging_distribution":True,
      "historical_MPA_vs_ASPA_or_proposed_MPA_not_conflated":True,
      "no_real_protected_fraction_without_verified_shapes":True,
      "does_not_estimate_population_protection_or_climate_impact":True
    }
    if not all([args.ccamlr_geojson,args.marine_mask_geojson,args.official_source_manifest]):
        gate["reason"]="Official adopted CCAMLR zone polygons, marine ocean mask and source/version/management manifest required; terrestrial colony points are not MPA foraging overlap."
        (args.out/"protection_source_gate.json").write_text(json.dumps(gate,indent=2)+"\n")
        print(json.dumps(gate,ensure_ascii=False))
        return
    from shapely.geometry import shape,Polygon
    from shapely.ops import transform,unary_union
    from pyproj import Geod,Transformer
    sources=json.loads(args.official_source_manifest.read_text())
    keys={"publisher","publisher_url","publication_date","source_dataset_version",
          "file_sha256","marine_mask_sha256","ccamlr_adopted_zones_verified"}
    if not keys.issubset(sources) or sources["publisher"]!="CCAMLR" or sources["ccamlr_adopted_zones_verified"] is not True:
        raise ValueError("Only source-verified adopted CCAMLR zone polygons accepted")
    if hashlib.sha256(args.ccamlr_geojson.read_bytes()).hexdigest()!=sources["file_sha256"]:
        raise ValueError("Official CCAMLR geometry SHA256 mismatch")
    if hashlib.sha256(args.marine_mask_geojson.read_bytes()).hexdigest()!=sources["marine_mask_sha256"]:
        raise ValueError("Official marine mask SHA256 mismatch")
    zones=json.loads(args.ccamlr_geojson.read_text())
    mask=json.loads(args.marine_mask_geojson.read_text())
    assert zones.get("type")=="FeatureCollection" and mask.get("type")=="FeatureCollection"
    def original_declared_crs(data, source_name):
        prop=data.get("crs",{}).get("properties",{})
        declared=prop.get("name", "")
        if declared in ("EPSG:4326","urn:ogc:def:crs:EPSG::4326","urn:ogc:def:crs:OGC:1.3:CRS84"):
            return "EPSG:4326"
        if declared in ("EPSG:6932","urn:ogc:def:crs:EPSG::6932"):
            return "EPSG:6932"
        raise ValueError(source_name+" has missing/unknown source CRS; cannot assign a geographic interpretation")
    # The genuine CCAMLR v0.9 MPA GeoJSON is **EPSG:6932**, not longitude and
    # latitude. Ocean mask may use a different source CRS, but must declare it.
    zone_crs=original_declared_crs(zones,"official CCAMLR protected zones")
    marine_crs=original_declared_crs(mask,"marine mask")
    zone_proj=Transformer.from_crs(zone_crs,"EPSG:3031",always_xy=True)
    marine_proj=Transformer.from_crs(marine_crs,"EPSG:3031",always_xy=True)
    proj=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    geo=Geod(ellps="WGS84")
    ocean=unary_union([transform(marine_proj.transform,shape(f["geometry"])) for f in mask["features"]])
    if ocean.is_empty or not ocean.is_valid:raise ValueError("No valid ocean-mask geometry")
    safe=[];knownzones=[]
    for feature in zones["features"]:
        p=feature["properties"]
        mandatory={"legal_status","zone_id","management_rule","adoption_year"}
        if not mandatory.issubset(p):raise ValueError("MPA source has no per-zone legal management metadata")
        if p["legal_status"]!="adopted":raise ValueError("Cannot classify proposal or unverified zone as adopted MPA")
        if p["management_rule"] not in ("no_take","fishing_restricted","managed_research"):
            raise ValueError("Unknown fishing management restriction; do not infer no-take")
        if not (2000<=int(p["adoption_year"])<=2100):raise ValueError("Invalid adoption year")
        geom=transform(zone_proj.transform,shape(feature["geometry"])).intersection(ocean)
        if not geom.is_valid:raise ValueError("Invalid original CCAMLR polygon")
        knownzones.append(p["zone_id"])
        if p["management_rule"] in ("no_take","fishing_restricted"):safe.append(geom)
    controlled=unary_union(safe).intersection(ocean) if safe else Polygon()
    rows=[]
    for s in sites.itertuples(index=False):
        for radius in RADII:
            bearings=np.linspace(0,360,721)[:-1]
            lon,lat,_=geo.fwd(np.full(len(bearings),s.longitude),
                              np.full(len(bearings),s.latitude),bearings,
                              np.full(len(bearings),radius*1000))
            area=transform(proj.transform,Polygon(zip(lon,lat)))
            sea=area.intersection(ocean)
            if sea.is_empty or sea.area<=0:
                rows.append({"site_id":s.site_id,"radius_km":radius,"status":"NO_GO_NO_MARINE_AREA"})
                continue
            fraction=float(sea.intersection(controlled).area/sea.area)
            if not 0<=fraction<=1+1e-9:raise ValueError("Area overlap outside 0-1")
            rows.append({"site_id":s.site_id,"radius_km":radius,
                         "marine_area_km2":float(sea.area/1e6),
                         "adopted_fishing_restricted_marine_area_km2":float(sea.intersection(controlled).area/1e6),
                         "protected_fraction_potential_marine_access":min(1.,fraction),
                         "status":"MODEL_POTENTIAL_MARINE_ACCESS_NOT_OBSERVED_FORAGING"})
    pd.DataFrame(rows).to_csv(args.out/"source_site_potential_marine_MPA_overlap_not_foraging.csv",index=False)
    gate.update({"status":"SOURCE_VERIFIED_POTENTIAL_MARINE_ACCESS_ONLY",
                 "n_verified_zone_features":len(zones["features"]),
                 "n_eligible_fishing_restriction_zone_features":len(safe),
                 "n_verified_source_sites":len(sites),
                 "not_full_population_protection_estimate":True})
    (args.out/"protection_source_gate.json").write_text(json.dumps(gate,indent=2)+"\n")
    print(json.dumps(gate,ensure_ascii=False))
if __name__=="__main__":main()
