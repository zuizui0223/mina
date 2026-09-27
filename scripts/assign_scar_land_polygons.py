#!/usr/bin/env python3
"""Assign pinned MAPPPD site points to SCAR ADD v7.12 high-resolution land polygons."""
from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

SERVICE = (
    "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
    "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer/1/query"
)
SOURCE_DOI = "10.5285/13c4d2f1-8903-4d7f-8977-592121975554"
USER_AGENT = "mina-island-reassembly/0.15 (+https://github.com/zuizui0223/mina)"


def query_land(lon: float, lat: float, retries: int = 4) -> dict:
    params = {
        "where": "surface='land'",
        "geometry": f"{lon:.8f},{lat:.8f}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "FID,surface",
        "returnGeometry": "false",
        "f": "json",
    }
    url = SERVICE + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if "error" in payload:
                raise RuntimeError(json.dumps(payload["error"], sort_keys=True))
            return payload
        except Exception as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"SCAR query failed: {last!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sites", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--meta", required=True, type=Path)
    args = parser.parse_args()

    with args.sites.open(encoding="utf-8-sig", newline="") as handle:
        sites = list(csv.DictReader(handle))

    rows = []
    n_match = n_zero = n_multi = n_error = 0
    for index, site in enumerate(sites, start=1):
        try:
            lat = float(site["latitude"])
            lon = float(site["longitude"])
            payload = query_land(lon, lat)
            features = payload.get("features", [])
            fids = sorted(
                int(feature["attributes"]["FID"])
                for feature in features
                if feature.get("attributes", {}).get("FID") is not None
            )
            if len(fids) == 1:
                status = "unique_direct_land_match"
                n_match += 1
            elif len(fids) == 0:
                status = "no_direct_land_match"
                n_zero += 1
            else:
                status = "multiple_direct_land_matches"
                n_multi += 1
            error = ""
        except Exception as exc:
            fids = []
            status = "query_error"
            error = repr(exc)
            n_error += 1

        rows.append(
            {
                "site_id": site["site_id"],
                "site_name": site["site_name"],
                "region": site["region"],
                "latitude": site["latitude"],
                "longitude": site["longitude"],
                "land_fid": fids[0] if len(fids) == 1 else "",
                "match_count": len(fids),
                "all_land_fids": ";".join(str(fid) for fid in fids),
                "status": status,
                "error": error,
            }
        )
        if index % 100 == 0:
            print(f"queried={index}/{len(sites)}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    meta = {
        "schema_version": 1,
        "source": {
            "dataset": "SCAR Antarctic Digital Database high-resolution coastline polygons",
            "edition": "7.12",
            "doi": SOURCE_DOI,
            "feature_service": SERVICE.rsplit("/query", 1)[0],
            "surface_filter": "land",
        },
        "assignment": {
            "method": "point-in-polygon via esriSpatialRelIntersects",
            "input_crs": "EPSG:4326",
            "distance_tolerance_m": 0,
            "nearest_polygon_fallback": False,
        },
        "counts": {
            "sites": len(sites),
            "unique_direct_land_match": n_match,
            "no_direct_land_match": n_zero,
            "multiple_direct_land_matches": n_multi,
            "query_error": n_error,
        },
    }
    args.meta.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(meta, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
