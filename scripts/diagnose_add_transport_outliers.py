#!/usr/bin/env python3
"""Diagnose mixed/invalid coordinate transport in the SCAR ADD FeatureServer.

Outcome-blind: reads no penguin demographic response. It scans the frozen land
layer for coordinates outside the layer-declared EPSG:3031 extent, then
re-queries a small deterministic sample of offending FIDs in 3031, 4326 and
3857 to identify transport inconsistencies.
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


def _session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=6,
        backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": "mina-add-transport-audit/1.0"})
    return s


def _get(s: requests.Session, url: str, **params):
    r = s.get(url, params=params, timeout=120)
    r.raise_for_status()
    x = r.json()
    if "error" in x:
        raise RuntimeError(x["error"])
    return x


def _layer(s: requests.Session):
    root = _get(s, SERVICE_URL, f="json")
    found = []
    for item in root.get("layers", []):
        url = f"{SERVICE_URL}/{item['id']}"
        meta = _get(s, url, f="json")
        names = [str(f.get("name","")) for f in meta.get("fields",[])]
        if any(name.lower()=="surface" for name in names):
            found.append((url,meta))
    if len(found)!=1:
        raise RuntimeError(f"surface layer count={len(found)}")
    return found[0]


def _coords(geometry: dict):
    for ring in (geometry or {}).get("rings") or []:
        for point in ring:
            if len(point)>=2:
                yield float(point[0]), float(point[1])


def _query_ids(s, layer_url, ids, out_sr):
    return _get(
        s,
        f"{layer_url}/query",
        f="json",
        objectIds=",".join(str(v) for v in ids),
        outFields="FID,surface",
        returnGeometry="true",
        outSR=out_sr,
        maxAllowableOffset=5000,
        geometryPrecision=0,
    )


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    s=_session()
    layer_url,meta=_layer(s)
    oid=str(meta.get("objectIdField") or "FID")
    extent=meta.get("extent") or {}
    xmin=float(extent["xmin"]); xmax=float(extent["xmax"])
    ymin=float(extent["ymin"]); ymax=float(extent["ymax"])
    margin=10000.0

    ids=_get(
        s,
        f"{layer_url}/query",
        f="json",
        where="surface='land'",
        returnIdsOnly="true",
    ).get("objectIds") or []
    ids=sorted(int(v) for v in ids)

    offenders=[]
    scanned=0
    response_srs={}
    for start in range(0,len(ids),1000):
        chunk=ids[start:start+1000]
        data=_query_ids(s,layer_url,chunk,3031)
        sr=data.get("spatialReference")
        response_srs[str(start)]=sr
        for feature in data.get("features",[]):
            attrs=feature.get("attributes") or {}
            fid=int(attrs.get(oid,attrs.get("FID")))
            bad=[]
            first=None
            minx=miny=float("inf"); maxx=maxy=float("-inf")
            for x,y in _coords(feature.get("geometry") or {}):
                if first is None: first=[x,y]
                minx=min(minx,x); maxx=max(maxx,x)
                miny=min(miny,y); maxy=max(maxy,y)
                if (
                    x < xmin-margin or x > xmax+margin
                    or y < ymin-margin or y > ymax+margin
                ):
                    bad.append([x,y])
                    if len(bad)>=3:
                        break
            scanned+=1
            if bad:
                offenders.append({
                    "fid":fid,
                    "first_coord":first,
                    "observed_bounds_partial":{
                        "minx":minx,"miny":miny,"maxx":maxx,"maxy":maxy
                    },
                    "outlier_coords":bad,
                })
        if len(offenders)>=20:
            break

    sample_ids=[o["fid"] for o in offenders[:10]]
    requery={}
    for sr in (3031,4326,3857):
        data=_query_ids(s,layer_url,sample_ids,sr) if sample_ids else {}
        rows=[]
        for feature in data.get("features",[]):
            attrs=feature.get("attributes") or {}
            coords=list(_coords(feature.get("geometry") or {}))
            rows.append({
                "fid":int(attrs.get(oid,attrs.get("FID"))),
                "first_coord":list(coords[0]) if coords else None,
                "coord_count":len(coords),
            })
        requery[str(sr)]={
            "response_spatial_reference":data.get("spatialReference"),
            "features":rows,
        }

    result={
        "schema_version":1,
        "diagnostic_id":"mina-scar-add-transport-outlier-audit-v1",
        "layer_url":layer_url,
        "declared_extent":extent,
        "land_feature_count":len(ids),
        "features_scanned_until_stop":scanned,
        "response_spatial_references_by_chunk":response_srs,
        "outlier_feature_count_found":len(offenders),
        "outlier_sample":offenders[:20],
        "sample_fids_requeried":sample_ids,
        "requery_by_out_sr":requery,
        "interpretation_rule":{
            "transport_problem_if":"same FID requested in EPSG:3031 returns coordinates outside declared EPSG:3031 extent while 4326/3857 coordinates are geographically plausible",
            "no_threshold_changes":true,
        },
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
