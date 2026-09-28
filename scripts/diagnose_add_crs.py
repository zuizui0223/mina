#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests
import pyreadr

SERVICE_URL = (
    "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
    "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer/1"
)


def get(url: str, **params):
    r = requests.get(url, params=params, timeout=120)
    r.raise_for_status()
    d = r.json()
    if "error" in d:
        raise RuntimeError(d["error"])
    return d


def first_coord(geometry):
    rings = (geometry or {}).get("rings") or []
    for ring in rings:
        if ring:
            return ring[0][:2]
    return None


def geometry_bounds(geometry):
    coords = [
        coord[:2]
        for ring in ((geometry or {}).get("rings") or [])
        for coord in ring
        if len(coord) >= 2
    ]
    if not coords:
        return None
    xs = [float(x) for x, _ in coords]
    ys = [float(y) for _, y in coords]
    return {
        "min_x": min(xs),
        "min_y": min(ys),
        "max_x": max(xs),
        "max_y": max(ys),
    }


def _load_sites(root: Path):
    data = pyreadr.read_r(str(root / "data" / "sites.rda"))
    if "sites" in data:
        return data["sites"]
    if len(data) == 1:
        return next(iter(data.values()))
    raise ValueError(f"cannot resolve sites table: {list(data)}")


def _point_query(lon: float, lat: float, distance_m: int | None):
    geometry = json.dumps(
        {
            "x": float(lon),
            "y": float(lat),
            "spatialReference": {"wkid": 4326},
        }
    )
    params = {
        "f": "json",
        "where": "1=1",
        "geometry": geometry,
        "geometryType": "esriGeometryPoint",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "FID,surface",
        "returnGeometry": "false",
    }
    if distance_m is not None:
        params["distance"] = int(distance_m)
        params["units"] = "esriSRUnit_Meter"
    d = get(SERVICE_URL + "/query", **params)
    features = d.get("features", [])
    counts = {}
    for feat in features:
        surface = str((feat.get("attributes") or {}).get("surface"))
        counts[surface] = counts.get(surface, 0) + 1
    return {
        "feature_count": len(features),
        "surface_counts": counts,
        "sample_attributes": [
            feat.get("attributes", {}) for feat in features[:10]
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()

    meta = get(SERVICE_URL, f="json")
    ids = get(
        SERVICE_URL + "/query",
        f="json",
        where="surface='land'",
        returnIdsOnly="true",
    ).get("objectIds") or []
    if not ids:
        raise RuntimeError("no land ids")
    oid = int(ids[0])

    samples = {}
    for sr in (3031, 3857, 4326):
        d = get(
            SERVICE_URL + "/query",
            f="json",
            objectIds=str(oid),
            outFields="FID,surface",
            returnGeometry="true",
            outSR=sr,
        )
        feat = d["features"][0]
        samples[str(sr)] = {
            "response_spatial_reference": d.get("spatialReference"),
            "geometry_spatial_reference": (feat.get("geometry") or {}).get(
                "spatialReference"
            ),
            "first_coord": first_coord(feat.get("geometry")),
            "attributes": feat.get("attributes"),
        }

    sites = _load_sites(a.mapppdr_dir)
    known_ids = ("TORG", "HUMB", "LITC", "CORM", "PENG", "ARDL", "GOPT", "FRAE", "CRZE")
    known = {}
    for site_id in known_ids:
        rows = sites[sites["site_id"] == site_id]
        if len(rows) != 1:
            known[site_id] = {"error": f"site rows={len(rows)}"}
            continue
        row = rows.iloc[0]
        probes = {}
        for distance in (None, 5000, 50000):
            key = "intersect" if distance is None else f"within_{distance}m"
            probes[key] = _point_query(
                float(row["longitude"]),
                float(row["latitude"]),
                distance,
            )
        known[site_id] = {
            "site_name": str(row["site_name"]),
            "region": str(row["region"]),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "queries": probes,
        }

    known_fids = []
    for rec in known.values():
        if not isinstance(rec, dict):
            continue
        query = ((rec.get("queries") or {}).get("intersect") or {})
        attrs = query.get("sample_attributes") or []
        if attrs and attrs[0].get("FID") is not None:
            known_fids.append(int(attrs[0]["FID"]))
    known_fids = sorted(set(known_fids))

    single_fid_geometry = {}
    for fid in known_fids:
        d = get(
            SERVICE_URL + "/query",
            f="json",
            objectIds=str(fid),
            outFields="FID,surface",
            returnGeometry="true",
            outSR=3031,
        )
        feat = d["features"][0]
        geom = feat.get("geometry")
        single_fid_geometry[str(fid)] = {
            "response_spatial_reference": d.get("spatialReference"),
            "first_coord": first_coord(geom),
            "bounds": geometry_bounds(geom),
        }

    batch_fid_geometry = {}
    if known_fids:
        d = get(
            SERVICE_URL + "/query",
            f="json",
            objectIds=",".join(str(fid) for fid in known_fids),
            outFields="FID,surface",
            returnGeometry="true",
            outSR=3031,
        )
        for feat in d.get("features", []):
            attrs = feat.get("attributes") or {}
            fid = attrs.get("FID")
            geom = feat.get("geometry")
            batch_fid_geometry[str(fid)] = {
                "response_spatial_reference": d.get("spatialReference"),
                "first_coord": first_coord(geom),
                "bounds": geometry_bounds(geom),
            }

    transport_comparison = {}
    for fid in known_fids:
        key = str(fid)
        one = single_fid_geometry.get(key)
        many = batch_fid_geometry.get(key)
        same_first_coord = (
            one is not None
            and many is not None
            and one.get("first_coord") == many.get("first_coord")
        )
        transport_comparison[key] = {
            "single": one,
            "batch": many,
            "same_first_coord": same_first_coord,
        }

    out = {
        "layer_name": meta.get("name"),
        "extent": meta.get("extent"),
        "sourceSpatialReference": meta.get("sourceSpatialReference"),
        "spatialReference": meta.get("spatialReference"),
        "fullExtent": meta.get("fullExtent"),
        "object_id": oid,
        "samples": samples,
        "known_site_service_queries": known,
        "known_fid_geometry_transport": transport_comparison,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
