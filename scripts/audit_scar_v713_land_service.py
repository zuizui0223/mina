#!/usr/bin/env python3
"""Source-only source-fitness audit for SCAR ADD v7.13 ArcGIS land polygons.

This is static LAND (can be ice covered), not ROCK OUTCROP and not a time-
specific map of newly exposed rock. The goal is only to establish if an
authoritative contemporaneous-looking terrestrial mask can be retrieved for
the three GLIMS source pilot boxes. No new-land estimates or penguin effects.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.parse
import urllib.request

BASE = ("https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
        "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer")
DOI = "10.5285/1c81cf24-576f-43df-be72-a5c7dbb51ffb"
# Stable same geographic source-only boxes as original GLIMS WFS pilot
BOXES = {
    "south_shetland_king_george_area": (-59.0, -62.35, -57.9, -61.6),
    "south_shetland_livingston_area": (-61.5, -63.1, -59.4, -62.2),
    "palmer_anvers_area": (-65.5, -65.0, -63.3, -64.2),
}

def get_json(endpoint: str, params: dict | None = None) -> dict:
    url = endpoint + (("?" + urllib.parse.urlencode(params)) if params else "")
    req = urllib.request.Request(url, headers={"User-Agent": "mina-scar-7.13-gis-source-gate/1.0",
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=35) as resp:
        payload = resp.read(2_000_001)
        if len(payload) > 2_000_000:
            raise RuntimeError("metadata/count response exceeds 2MB")
        data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("non-object SCAR response")
    if "error" in data:
        raise ValueError(f"ArcGIS error: {data['error']}")
    return data

def choose_layer(service: dict) -> int | None:
    layers = service.get("layers", [])
    if not isinstance(layers, list):
        return None
    valid = [x["id"] for x in layers
             if x.get("type") == "Feature Layer" and isinstance(x.get("id"), int)]
    return valid[0] if len(valid) == 1 else None

def schema_support(layer: dict) -> dict:
    names = {str(f.get("name", "")).lower(): f
             for f in layer.get("fields", []) if isinstance(f, dict)}
    surface_field = next((f["name"] for k, f in names.items() if k == "surface"), None)
    return {
        "feature_type": layer.get("type"),
        "surface_field": surface_field,
        "source_max_record_count": layer.get("maxRecordCount"),
        "geographic_extent": layer.get("extent"),
        "capabilities": layer.get("capabilities"),
        "object_id_field": layer.get("objectIdField"),
    }

def source_count(layer_url: str, bbox: tuple, field: str) -> int:
    w, s, e, n = bbox
    params = {
        "f": "json",
        "where": f"{field} = 'land'",
        "geometry": json.dumps({"xmin": w, "ymin": s, "xmax": e, "ymax": n,
                                 "spatialReference": {"wkid": 4326}}),
        "geometryType": "esriGeometryEnvelope", "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "returnCountOnly": "true",
    }
    resp = get_json(layer_url + "/query", params)
    if not isinstance(resp.get("count"), int):
        raise ValueError(f"ArcGIS returned no integer count: {str(resp)[:200]}")
    return resp["count"]

def audit() -> dict:
    report = {
        "source": BASE, "doi": DOI, "source_edition": "7.13",
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_scope": "SOURCE_ONLY_STATIC_LAND_MASK_NOT_ICE_FREE_NOT_SETTLEMENT",
        "biology_opened": False,
        "new_rock_claim": False,
        "regions": {},
    }
    try:
        service = get_json(BASE, {"f": "pjson"})
        layer_id = choose_layer(service)
        report["available_service_layers"] = service.get("layers")
        report["chosen_layer_id"] = layer_id
        if layer_id is None:
            report["status"] = "HOLD_UNAMBIGUOUS_FEATURE_LAYER"
            return report
        layer_url = f"{BASE}/{layer_id}"
        meta = get_json(layer_url, {"f": "pjson"})
        report["layer_schema"] = schema_support(meta)
        field = report["layer_schema"]["surface_field"]
        if field is None:
            report["status"] = "HOLD_NO_SURFACE_LAND_FIELD"
            return report
        for label, bbox in BOXES.items():
            try:
                count = source_count(layer_url, bbox, field)
                report["regions"][label] = {
                    "queried_land_polygon_feature_count": count,
                    "bbox_wgs84_lonlat": list(bbox),
                    "query_status": "SCAR_GIS_LAND_FEATURE_SOURCE_COUNT_ONLY",
                    "land_is_not_icefree_rock": True,
                }
            except Exception as exc:
                report["regions"][label] = {"status": "HOLD_QUERY_FAILED",
                                            "reason": str(exc)[:240]}
        report["status"] = ("SCAR_LAND_COUNTS_RETRIEVED"
                            if all(x.get("query_status") for x in report["regions"].values())
                            else "HOLD_PARTIAL_GIS_SOURCE")
    except Exception as exc:
        report["status"] = "HOLD_SCAR_GIS_SOURCE"
        report["error"] = str(exc)[:240]
    report["warnings"] = [
        "Surface land != bare-rock outcrop, and != prior-to-later confirmed ice-to-land transition.",
        "Static ADD v7.13 land polygons are a composite with mapping dates from 1990s to 2026.",
        "BBOX counts and FIDs are neither distinct physical islands nor biological independent units.",
        "No glacier difference was clipped to these polygons in this source-count gate.",
    ]
    return report

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out-json", required=True, type=Path)
    a = p.parse_args()
    r = audit()
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": r["status"], "regions": r["regions"],
                      "chosen_layer_id": r.get("chosen_layer_id")}, sort_keys=True))

if __name__ == "__main__":
    main()
