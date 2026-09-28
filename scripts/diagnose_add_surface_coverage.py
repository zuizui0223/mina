#!/usr/bin/env python3
"""Diagnose SCAR ADD surface categories and regional service coverage.

Outcome-blind: no penguin demographic response is read. This checks whether
the FeatureServer itself returns land polygons near well-known Antarctic
regions/sites, independently of local geometry reconstruction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SERVICE_URL = (
    "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
    "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer"
)

POINTS = {
    "palmer_torgersen_approx": (-64.07, -64.77),
    "king_george_south_shetlands": (-58.4, -62.2),
    "laurie_south_orkneys": (-44.6, -60.75),
    "cape_crozier_ross": (169.23, -77.45),
}

ENVELOPES = {
    "south_shetlands": (-63.5, -64.0, -54.0, -60.0),
    "palmer": (-66.5, -66.0, -62.0, -63.5),
    "south_orkneys": (-48.0, -61.5, -43.0, -60.0),
    "ross_sea_west": (160.0, -79.0, 175.0, -74.5),
}


def session() -> requests.Session:
    s=requests.Session()
    retry=Retry(
        total=6,
        backoff_factor=0.5,
        status_forcelist=(429,500,502,503,504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    s.mount("https://",HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent":"mina-add-surface-coverage-diagnostic/1.0"})
    return s


def get(s,url,**params):
    r=s.get(url,params=params,timeout=120)
    r.raise_for_status()
    x=r.json()
    if "error" in x:
        raise RuntimeError(x["error"])
    return x


def discover(s):
    root=get(s,SERVICE_URL,f="json")
    found=[]
    for item in root.get("layers",[]):
        url=f"{SERVICE_URL}/{item['id']}"
        meta=get(s,url,f="json")
        names=[str(f.get("name","")) for f in meta.get("fields",[])]
        if any(name.lower()=="surface" for name in names):
            found.append((url,meta))
    if len(found)!=1:
        raise RuntimeError(f"surface layer count={len(found)}")
    return found[0]


def count_query(s,layer_url,where="1=1",**extra):
    params={
        "f":"json",
        "where":where,
        "returnCountOnly":"true",
    }
    params.update(extra)
    return int(get(s,f"{layer_url}/query",**params).get("count") or 0)


def point_counts(s,layer_url,lon,lat):
    geometry=json.dumps({
        "x":lon,
        "y":lat,
        "spatialReference":{"wkid":4326},
    })
    base={
        "geometry":geometry,
        "geometryType":"esriGeometryPoint",
        "inSR":4326,
        "spatialRel":"esriSpatialRelIntersects",
    }
    out={}
    for distance in (0,5000):
        params=dict(base)
        if distance:
            params["distance"]=distance
            params["units"]="esriSRUnit_Meter"
        out[str(distance)]={
            "all":count_query(s,layer_url,"1=1",**params),
            "land":count_query(s,layer_url,"surface='land'",**params),
        }
    return out


def envelope_counts(s,layer_url,bounds):
    xmin,ymin,xmax,ymax=bounds
    geometry=json.dumps({
        "xmin":xmin,"ymin":ymin,"xmax":xmax,"ymax":ymax,
        "spatialReference":{"wkid":4326},
    })
    base={
        "geometry":geometry,
        "geometryType":"esriGeometryEnvelope",
        "inSR":4326,
        "spatialRel":"esriSpatialRelIntersects",
    }
    return {
        "all":count_query(s,layer_url,"1=1",**base),
        "land":count_query(s,layer_url,"surface='land'",**base),
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    s=session()
    layer_url,meta=discover(s)

    distinct=get(
        s,
        f"{layer_url}/query",
        f="json",
        where="1=1",
        outFields="surface",
        returnDistinctValues="true",
        returnGeometry="false",
    )
    surfaces=sorted({
        str((f.get("attributes") or {}).get("surface"))
        for f in distinct.get("features",[])
    })

    total_count=count_query(s,layer_url,"1=1")
    land_count=count_query(s,layer_url,"surface='land'")

    result={
        "schema_version":1,
        "diagnostic_id":"mina-scar-add-surface-coverage-v1",
        "layer_url":layer_url,
        "layer_name":meta.get("name"),
        "declared_extent":meta.get("extent"),
        "surface_values":surfaces,
        "total_feature_count":total_count,
        "land_feature_count":land_count,
        "points":{
            name:{
                "longitude":lon,
                "latitude":lat,
                "counts":point_counts(s,layer_url,lon,lat),
            }
            for name,(lon,lat) in POINTS.items()
        },
        "envelopes":{
            name:{
                "bounds_wgs84":list(bounds),
                "counts":envelope_counts(s,layer_url,bounds),
            }
            for name,bounds in ENVELOPES.items()
        },
        "decision_rule":{
            "service_content_problem_if":"known island regions have zero land polygons in FeatureServer envelope/point queries",
            "local_geometry_problem_if":"FeatureServer returns land near known regions/sites but local reconstructed geometries fail to match them",
            "no_demographic_outcomes_used":True,
        },
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
