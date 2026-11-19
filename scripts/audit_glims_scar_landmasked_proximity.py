#!/usr/bin/env python3
"""SCAR v7.13 STATIC-LAND support filter of GLIMS apparent outline differences.

This is a source-only geography gate. Land may be ice-covered. Neither land
clipping nor same-SCAR-feature proximity proves newly exposed rock, consistent
surveyed absence, actual nesting, causality or a biological island.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
import pandas as pd
import pyreadr
from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform, unary_union
from shapely.strtree import STRtree

from scripts.audit_glims_antarctic_island_source import PILOT_BBOXES, WFS, http_get
from scripts.audit_glims_mapppd_retreat_proximity import (
    dated_grouped_features, retreat_candidate_shapes, TARGET_SPECIES, load_rda)
from scripts.audit_scar_v713_land_service import BASE

LAYER_URL=BASE+"/1"
GLIMS_LAYER="GLIMS:GLIMS_Glacier_Outlines"
GLIMS_CAP=500
SCAR_CAP=2000

def get_scar_land_geojson(bbox:tuple) -> tuple[dict, str]:
    west,south,east,north=bbox
    params={
        "f":"geojson",
        "where":"surface = 'land'",
        "geometry":json.dumps({"xmin":west,"ymin":south,"xmax":east,"ymax":north,
                               "spatialReference":{"wkid":4326}}),
        "geometryType":"esriGeometryEnvelope",
        "inSR":"4326", "outSR":"4326",
        "spatialRel":"esriSpatialRelIntersects",
        "outFields":"FID,surface",
        "returnGeometry":"true",
        "resultRecordCount":str(SCAR_CAP),
        "geometryPrecision":"5",
    }
    url=LAYER_URL+"/query?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"User-Agent":"mina-glims-scar-static-land-support/1.0",
                                            "Accept":"application/geo+json, application/json"})
    with urllib.request.urlopen(req,timeout=75) as response:
        raw=response.read(60_000_001)
        if len(raw)>60_000_000:
            raise ValueError("SCAR GeoJSON response exceeds 60 MB; STOP")
    data=json.loads(raw)
    if data.get("error"):
        raise ValueError("SCAR GIS service error: "+str(data["error"])[:180])
    if data.get("type")!="FeatureCollection" or not isinstance(data.get("features"),list):
        raise ValueError("SCAR GIS response not GeoJSON FeatureCollection")
    if len(data["features"])>=SCAR_CAP:
        raise ValueError("SCAR GIS reached page limit; STOP (do not use incomplete mask)")
    return data,hashlib.sha256(raw).hexdigest()

def build_lands(data:dict,project):
    lands=[]; labels=[]; fail=Counter()
    for feature in data.get("features",[]):
        props={str(k).lower():v for k,v in (feature.get("properties") or {}).items()}
        if props.get("surface")!="land":
            fail["unexpected_surface_not_land"]+=1;continue
        fid=props.get("fid")
        if fid is None:
            fail["missing_fid"]+=1;continue
        try:
            geom=shape(feature["geometry"])
            if geom.is_empty or geom.geom_type not in ("Polygon","MultiPolygon"):
                fail["invalid_type_or_empty"]+=1; continue
            if not geom.is_valid:
                fail["invalid_scar_polygon_not_repaired"]+=1; continue
            mapped=transform(project,geom)
            if not mapped.is_valid or mapped.area<=0:
                fail["invalid_projected_geometry"]+=1;continue
            lands.append(mapped);labels.append(str(fid))
        except (ValueError,TypeError,KeyError):
            fail["unreadable_geometry"]+=1
    return lands,labels,dict(fail)

def clip_to_current_terrestrial(shapes:list[dict],lands:list,labels:list):
    """Clip GLIMS apparent change into official land features, preserving FIDs."""
    tree=STRtree(lands)
    parts=defaultdict(list)
    issues=Counter()
    for row in shapes:
        g=row["geometry"]
        try:
            ix=tree.query(g,predicate="intersects")
            if not len(ix):
                issues["apparent_diff_off_terrestrial_mask"]+=1
                continue
            for i in ix:
                mask=lands[int(i)]
                clipped=g.intersection(mask)
                if clipped.is_empty or clipped.area<=0:
                    continue
                if not clipped.is_valid:
                    issues["invalid_land_intersection"]+=1;continue
                parts[labels[int(i)]].append(clipped)
        except Exception:
            issues["mask_intersection_error"]+=1
    dissolved={}
    for k, poly in parts.items():
        try:
            v=unary_union(poly)
            if not v.is_valid:
                issues["invalid_feature_union"]+=1;continue
            dissolved[k]=v
        except Exception:
            issues["invalid_feature_union"]+=1
    return dissolved,dict(issues)

def sites_with_same_feature(sites:pd.DataFrame,lands:list,labels:list,
                            land_diff:dict,project) -> list[dict]:
    tree=STRtree(lands)
    result=[]
    for r in sites.itertuples(index=False):
        pt=Point(*project(float(r.longitude),float(r.latitude)))
        feature_ix=[int(i) for i in tree.query(pt,predicate="intersects")
                    if lands[int(i)].covers(pt)]
        chosen=sorted(set(labels[i] for i in feature_ix))
        if len(chosen)!=1:
            status="SITE_NO_EXACT_UNIQUE_LAND_FEATURE"
            dist=None;fid=None
        else:
            fid=chosen[0]
            if fid not in land_diff:
                status="SITE_FEATURE_WITHOUT_MATCHED_GLIMS_DIFFERENCE"
                dist=None
            else:
                status="SITE_EXACT_SAME_SCAR_LAND_FEATURE_GEOGRAPHY_ONLY"
                dist=float(pt.distance(land_diff[fid]))
        result.append({
            "site_id":str(r.site_id),"site_name":str(r.site_name),
            "latitude":float(r.latitude),"longitude":float(r.longitude),
            "land_source_feature_id":fid if len(chosen)==1 else None,
            "feature_assignment_status":status,
            "distance_m_same_feature_terrestrial_glims_difference":round(dist,2) if dist is not None else None,
            "within_1km_source_only":bool(dist is not None and dist<=1000),
            "within_5km_source_only":bool(dist is not None and dist<=5000),
            "landmask_proves_new_rock":False,
        })
    return result

def run(mapppdr:Path) -> tuple[dict,pd.DataFrame]:
    sites=load_rda(mapppdr/"data/sites.rda","sites")
    links=load_rda(mapppdr/"data/site_species.rda","site_species")
    ids=set(links.loc[links["species_id"].isin(TARGET_SPECIES),"site_id"].astype(str))
    sites=sites[sites["site_id"].astype(str).isin(ids)]
    project=Transformer.from_crs(4326,3031,always_xy=True).transform
    report={
       "source_layer_scar":LAYER_URL,
       "source_edition":"7.13",
       "doi_scar":"10.5285/1c81cf24-576f-43df-be72-a5c7dbb51ffb",
       "source_layer_glims":GLIMS_LAYER,
       "analysis_class":"SOURCE_ONLY_LAND_MASK_NOT_ROCK_NOT_NEW_SETTLEMENT",
       "date_utc":datetime.now(timezone.utc).isoformat(),
       "count_outcome_opened":False,
       "regions":{},
    }
    rows=[]
    for label,bbox in PILOT_BBOXES.items():
        west,south,east,north=bbox
        scar,scar_sha=get_scar_land_geojson(bbox)
        lands,fids,scar_exclusions=build_lands(scar,project)
        if not lands:raise ValueError(f"{label}: zero valid SCAR land polygons")
        glims=http_get({
            "service":"WFS","version":"1.0.0","request":"GetFeature",
            "typeName":GLIMS_LAYER,"maxFeatures":str(GLIMS_CAP),
            "outputFormat":"application/json","srsName":"EPSG:4326",
            "bbox":f"{west},{south},{east},{north}",
        })
        original=json.loads(glims)
        if len(original.get("features",[]))>=GLIMS_CAP:
            raise ValueError(f"{label}: GLIMS page limit reached")
        grouped,glims_exclusions=dated_grouped_features(original,project)
        diffs,glims_pair_exclusions=retreat_candidate_shapes(grouped)
        parts,clip_exclusions=clip_to_current_terrestrial(diffs,lands,fids)
        sel=sites[sites["latitude"].between(south,north)
                  & sites["longitude"].between(west,east)].copy()
        local=sites_with_same_feature(sel,lands,fids,parts,project)
        for row in local: row["region_bbox"]=label
        rows+=local
        report["regions"][label]={
           "source_scar_sha256":scar_sha,
           "source_glims_sha256":hashlib.sha256(glims).hexdigest(),
           "scar_features_returned":len(scar["features"]),
           "scar_valid_land_features":len(lands),
           "scar_source_exclusions":scar_exclusions,
           "glims_features_returned":len(original.get("features",[])),
           "glims_apparent_difference_ids":len(diffs),
           "scar_land_features_with_apparent_glims_difference":len(parts),
           "glims_geometry_exclusions":glims_exclusions,
           "glims_pair_exclusions":glims_pair_exclusions,
           "clip_source_exclusions":clip_exclusions,
           "source_site_points":len(local),
           "site_exact_unique_scar_land_features":sum(x["land_source_feature_id"] is not None for x in local),
           "site_same_scar_feature_landfiltered_1km":sum(x["within_1km_source_only"] for x in local),
           "site_same_scar_feature_landfiltered_5km":sum(x["within_5km_source_only"] for x in local),
        }
    frame=pd.DataFrame(rows).sort_values(["region_bbox","site_id"]).reset_index(drop=True)
    report["summary"]={
       "site_rows":len(frame),
       "unique_site_ids":int(frame["site_id"].nunique()),
       "site_exact_unique_land_feature":int(frame["land_source_feature_id"].notna().sum()),
       "site_1km_landfiltered_same_feature":int(frame["within_1km_source_only"].sum()),
       "site_5km_landfiltered_same_feature":int(frame["within_5km_source_only"].sum()),
    }
    report["source_limits"]=[
       "SCAR land mask is static and can be ice-covered; not bare rock, and not a new ice-free patch.",
       "SCAR polygon feature IDs are map features, NOT verified biological islands or physical landmass identities.",
       "GLIMS old-minus-new can be real glacier loss, calving at sea or cartographic discrepancy.",
       "Same-feature proximity is a conservative geography support check, not penguin nesting access.",
       "Date-specific exposure, inhabited physical patch, and independent visited A/P series not measured.",
    ]
    return report,frame

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-csv",required=True,type=Path)
    a=p.parse_args()
    try:
        report,frame=run(a.mapppdr_dir)
        report["status"]="SOURCE_LAND_MASK_GEOGRAPHY_COMPLETED_NO_BIOLOGICAL_INFERENCE"
    except Exception as e:
        report={"status":"HOLD_SCAR_LAND_MASK_SOURCE_OR_GEOMETRY",
                "reason":str(e)[:500],"biology_opened":False}
        frame=pd.DataFrame()
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    if not frame.empty:
        a.out_csv.parent.mkdir(parents=True,exist_ok=True)
        frame.to_csv(a.out_csv,index=False)
    print(json.dumps({"status":report["status"],"summary":report.get("summary"),
                      "reason":report.get("reason")},sort_keys=True))

if __name__=="__main__":
    main()
