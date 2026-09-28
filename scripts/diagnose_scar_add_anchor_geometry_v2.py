#!/usr/bin/env python3
"""Minimal anchor-FID geometry diagnostic for SCAR ADD.

Outcome-blind. For four known Antarctic locations, query matching land FIDs,
choose one deterministic representative FID, then fetch all representatives
in only two batched geometry calls (EPSG:3031 and EPSG:4326). This stays well
below the ArcGIS large-geometry quota.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests
from pyproj import Transformer
from requests.adapters import HTTPAdapter
from shapely.geometry import Point, Polygon
from urllib3.util.retry import Retry

LAYER=(
    "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
    "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer/1"
)

POINTS={
    "torgersen":{"lon":-64.073,"lat":-64.772,"distance_m":0},
    "king_george":{"lon":-58.40,"lat":-62.20,"distance_m":5000},
    "laurie_island":{"lon":-44.60,"lat":-60.75,"distance_m":5000},
    "cape_crozier":{"lon":169.23,"lat":-77.45,"distance_m":5000},
}


def session()->requests.Session:
    s=requests.Session()
    retry=Retry(
        total=6,
        backoff_factor=.6,
        status_forcelist=(429,500,502,503,504),
        allowed_methods=("GET","POST"),
        respect_retry_after_header=True,
    )
    s.mount("https://",HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent":"mina-scar-add-anchor-geometry-v2/1.0"})
    return s


def get(s,**params):
    r=s.get(LAYER+"/query",params={"f":"json",**params},timeout=120)
    r.raise_for_status()
    x=r.json()
    if "error" in x:
        raise RuntimeError(x["error"])
    return x


def post(s,**data):
    r=s.post(LAYER+"/query",data={"f":"json",**data},timeout=120)
    r.raise_for_status()
    x=r.json()
    if "error" in x:
        raise RuntimeError(x["error"])
    return x


def matching_fids(s,lon,lat,distance_m):
    geometry=json.dumps({
        "x":float(lon),
        "y":float(lat),
        "spatialReference":{"wkid":4326},
    })
    params={
        "where":"surface='land'",
        "geometry":geometry,
        "geometryType":"esriGeometryPoint",
        "inSR":4326,
        "spatialRel":"esriSpatialRelIntersects",
        "returnIdsOnly":"true",
    }
    if distance_m:
        params["distance"]=int(distance_m)
        params["units"]="esriSRUnit_Meter"
    return sorted(int(v) for v in (get(s,**params).get("objectIds") or []))


def fetch_batch(s,fids,out_sr):
    if not fids:
        return {}
    data=post(
        s,
        objectIds=",".join(str(v) for v in fids),
        outFields="FID,surface",
        returnGeometry="true",
        outSR=int(out_sr),
    )
    out={}
    for feature in data.get("features",[]):
        attrs=feature.get("attributes") or {}
        fid=int(attrs.get("FID"))
        out[fid]={
            "geometry":feature.get("geometry"),
            "attributes":attrs,
        }
    return {
        "response_spatial_reference":data.get("spatialReference"),
        "features":out,
    }


def odd_even_geometry(geometry):
    rings=(geometry or {}).get("rings") or []
    polys=[]
    for ring in rings:
        if len(ring)<4:
            continue
        coords=[(float(p[0]),float(p[1])) for p in ring if len(p)>=2]
        if len(coords)<4:
            continue
        poly=Polygon(coords)
        if not poly.is_valid:
            poly=poly.buffer(0)
        if not poly.is_empty:
            polys.append(poly)
    if not polys:
        return None
    geom=polys[0]
    for poly in polys[1:]:
        geom=geom.symmetric_difference(poly)
    if not geom.is_valid:
        geom=geom.buffer(0)
    return None if geom.is_empty else geom


def first_coord(geometry):
    rings=(geometry or {}).get("rings") or []
    for ring in rings:
        if ring:
            return [float(ring[0][0]),float(ring[0][1])]
    return None


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    s=session()

    selected={}
    service_matches={}
    for name,rec in POINTS.items():
        fids=matching_fids(s,rec["lon"],rec["lat"],rec["distance_m"])
        service_matches[name]=fids
        selected[name]=fids[0] if fids else None

    unique_fids=sorted({fid for fid in selected.values() if fid is not None})
    batch3031=fetch_batch(s,unique_fids,3031)
    batch4326=fetch_batch(s,unique_fids,4326)

    transformer=Transformer.from_crs(4326,3031,always_xy=True)
    results={}
    for name,rec in POINTS.items():
        fid=selected[name]
        px,py=transformer.transform(rec["lon"],rec["lat"])
        row={
            **rec,
            "service_match_count":len(service_matches[name]),
            "service_match_fids":service_matches[name],
            "representative_fid":fid,
            "local_point_3031":[px,py],
        }
        if fid is not None:
            f3031=(batch3031.get("features") or {}).get(fid,{})
            f4326=(batch4326.get("features") or {}).get(fid,{})
            geom=odd_even_geometry(f3031.get("geometry"))
            row.update({
                "service_response_sr_3031":batch3031.get("response_spatial_reference"),
                "service_response_sr_4326":batch4326.get("response_spatial_reference"),
                "first_coord_3031":first_coord(f3031.get("geometry")),
                "first_coord_4326":first_coord(f4326.get("geometry")),
                "local_polygon_bounds_3031":None if geom is None else list(geom.bounds),
                "local_distance_to_polygon_m":None if geom is None else float(Point(px,py).distance(geom)),
                "local_covers_point":False if geom is None else bool(geom.covers(Point(px,py))),
            })
        results[name]=row

    result={
        "schema_version":2,
        "diagnostic_id":"mina-scar-add-anchor-fid-geometry-v2",
        "large_geometry_calls":2,
        "representative_fids":unique_fids,
        "points":results,
        "interpretation_rule":{
            "geometry_consistent_if":"for exact/intersection anchors distance is ~0; for 5-km anchors local distance is <=5000 m",
            "no_demographic_outcomes_used":True,
        },
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
