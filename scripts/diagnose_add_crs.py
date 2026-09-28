#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests

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


def main():
    p = argparse.ArgumentParser()
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

    out = {
        "layer_name": meta.get("name"),
        "extent": meta.get("extent"),
        "sourceSpatialReference": meta.get("sourceSpatialReference"),
        "spatialReference": meta.get("spatialReference"),
        "fullExtent": meta.get("fullExtent"),
        "object_id": oid,
        "samples": samples,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
