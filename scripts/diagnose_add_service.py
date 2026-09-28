#!/usr/bin/env python3
"""Diagnose SCAR ADD FeatureServer coverage at known APBP site coordinates.

This is an outcome-blind service/geometry diagnostic. It uses only site
coordinates and region labels; no penguin population response is read.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pyreadr
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SERVICE_URL = (
    "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
    "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer"
)
DIAGNOSTIC_SITE_IDS = (
    "TORG",
    "CORM",
    "HUMB",
    "LITC",
    "BISC",
    "PENG",
    "ARDL",
    "GOPT",
    "FRAW",
    "FRAE",
)
REGION_ENVELOPES = {
    "south_shetlands": (-61.5, -63.5, -56.5, -60.0),
    "palmer": (-65.5, -65.5, -60.0, -63.0),
    "south_orkneys": (-47.0, -61.5, -43.0, -60.0),
    "ross_sea_west": (164.0, -78.5, 171.0, -75.0),
}


def _session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": "mina-add-service-diagnostic/1.0"})
    return s


def _get(session: requests.Session, url: str, **params):
    r = session.get(url, params=params, timeout=120)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data


def _load_sites(root: Path):
    data = pyreadr.read_r(str(root / "data" / "sites.rda"))
    if "sites" in data:
        return data["sites"]
    if len(data) == 1:
        return next(iter(data.values()))
    raise ValueError(f"cannot resolve sites table: {list(data)}")


def _layer(session: requests.Session):
    root = _get(session, SERVICE_URL, f="json")
    out = []
    for item in root.get("layers", []):
        url = f"{SERVICE_URL}/{item['id']}"
        meta = _get(session, url, f="json")
        fields = [f.get("name") for f in meta.get("fields", [])]
        if any(str(x).lower() == "surface" for x in fields):
            out.append((url, meta))
    if len(out) != 1:
        raise RuntimeError(f"surface layer count={len(out)}")
    return out[0]


def _surface_counts(features):
    return dict(
        Counter(
            str((f.get("attributes") or {}).get("surface"))
            for f in features
        )
    )


def _point_query(session, layer_url, lon, lat, distance=None):
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
    if distance is not None:
        params["distance"] = int(distance)
        params["units"] = "esriSRUnit_Meter"
    return _get(session, f"{layer_url}/query", **params)


def _envelope_query(session, layer_url, bounds):
    xmin, ymin, xmax, ymax = bounds
    geometry = json.dumps(
        {
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax,
            "spatialReference": {"wkid": 4326},
        }
    )
    return _get(
        session,
        f"{layer_url}/query",
        f="json",
        where="1=1",
        geometry=geometry,
        geometryType="esriGeometryEnvelope",
        inSR=4326,
        spatialRel="esriSpatialRelIntersects",
        outFields="FID,surface",
        returnGeometry="false",
        resultRecordCount=2000,
    )


def diagnose(root: Path) -> dict:
    session = _session()
    layer_url, meta = _layer(session)
    sites = _load_sites(root)
    site_rows = sites[sites["site_id"].isin(DIAGNOSTIC_SITE_IDS)]

    field_meta = {}
    for field in meta.get("fields", []):
        if str(field.get("name", "")).lower() == "surface":
            field_meta = field
            break

    site_results = {}
    for _, row in site_rows.iterrows():
        rec = {
            "site_name": str(row["site_name"]),
            "region": str(row["region"]),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
        }
        for distance in (None, 5000, 50000, 150000):
            data = _point_query(
                session,
                layer_url,
                row["longitude"],
                row["latitude"],
                distance=distance,
            )
            label = "intersect" if distance is None else f"within_{distance}m"
            rec[label] = {
                "feature_count": len(data.get("features", [])),
                "surface_counts": _surface_counts(data.get("features", [])),
                "sample_attributes": [
                    f.get("attributes", {})
                    for f in data.get("features", [])[:5]
                ],
            }
        site_results[str(row["site_id"])] = rec

    envelope_results = {}
    for name, bounds in REGION_ENVELOPES.items():
        data = _envelope_query(session, layer_url, bounds)
        envelope_results[name] = {
            "bounds_wgs84": list(bounds),
            "feature_count": len(data.get("features", [])),
            "surface_counts": _surface_counts(data.get("features", [])),
            "sample_attributes": [
                f.get("attributes", {})
                for f in data.get("features", [])[:10]
            ],
            "exceeded_transfer_limit": bool(data.get("exceededTransferLimit")),
        }

    all_count = _get(
        session,
        f"{layer_url}/query",
        f="json",
        where="1=1",
        returnCountOnly="true",
    ).get("count")
    land_count = _get(
        session,
        f"{layer_url}/query",
        f="json",
        where="surface='land'",
        returnCountOnly="true",
    ).get("count")

    return {
        "schema_version": 1,
        "diagnostic_id": "mina-scar-add-service-diagnostic-v1",
        "layer_url": layer_url,
        "layer_name": meta.get("name"),
        "layer_extent": meta.get("extent"),
        "source_spatial_reference": meta.get("sourceSpatialReference"),
        "spatial_reference": meta.get("spatialReference"),
        "max_record_count": meta.get("maxRecordCount"),
        "surface_field_metadata": field_meta,
        "all_feature_count": all_count,
        "land_feature_count": land_count,
        "site_results": site_results,
        "region_envelopes": envelope_results,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    result = diagnose(a.mapppdr_dir)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
