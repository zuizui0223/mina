#!/usr/bin/env python3
"""Outcome-blind APBP site-to-SCAR-ADD land-polygon matching audit.

Gate 1A uses the SCAR ADD FeatureServer itself for the spatial relationship.
This avoids reconstructing a continent-scale polygon layer locally before the
matching tolerance has been frozen. No penguin demographic outcome is used.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import time
from pathlib import Path

import pandas as pd
import pyreadr
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PINNED_MAPPPDR_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"
SERVICE_ROOT = (
    "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
    "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer"
)
DISTANCES_M = (0, 500, 1000, 2000, 5000)
PRIMARY_SPECIES = ("ADPE", "CHPE", "GEPE")


def _load(path: Path, expected: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(path))
    if expected in result:
        frame = result[expected]
    elif len(result) == 1:
        frame = next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected} in {path}: {list(result)}")
    if not isinstance(frame, pd.DataFrame):
        raise TypeError(expected)
    return frame


def _session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=6,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "mina-antarctic-island-atlas/1.0"})
    return session


def _get_json(session: requests.Session, url: str, **params):
    response = session.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(f"ArcGIS error: {data['error']}")
    return data


def _discover_layer(session: requests.Session) -> tuple[str, dict, str]:
    root = _get_json(session, SERVICE_ROOT, f="json")
    candidates = []
    for item in root.get("layers", []):
        layer_url = f"{SERVICE_ROOT}/{item['id']}"
        meta = _get_json(session, layer_url, f="json")
        fields = [str(f.get("name", "")) for f in meta.get("fields", [])]
        surface_fields = [name for name in fields if name.lower() == "surface"]
        if surface_fields:
            candidates.append((layer_url, meta, surface_fields[0]))
    if len(candidates) != 1:
        raise RuntimeError(f"expected one surface layer, found {len(candidates)}")
    return candidates[0]


def _candidate_sites(root: Path) -> pd.DataFrame:
    data = root / "data"
    sites = _load(data / "sites.rda", "sites")
    obs = _load(data / "penguin_obs.rda", "penguin_obs")

    nest = obs[
        obs["species_id"].isin(PRIMARY_SPECIES)
        & (obs["type"] == "nests")
        & obs["count"].notna()
    ].copy()
    nest["year"] = pd.to_numeric(nest["year"], errors="coerce")
    nest = nest.dropna(subset=["year"])

    units: list[tuple[str, str]] = []
    for (site_id, species_id), local in nest.groupby(["site_id", "species_id"]):
        years = sorted(set(int(y) for y in local["year"]))
        if len(years) >= 5 and max(years) - min(years) >= 10:
            units.append((str(site_id), str(species_id)))

    if len(units) != 152:
        raise ValueError(f"candidate unit drift: {len(units)} != 152")

    ids = sorted({site_id for site_id, _ in units})
    out = sites[sites["site_id"].isin(ids)].copy()
    if len(out) != len(ids):
        raise ValueError("candidate site coordinates are incomplete")
    return out[["site_id", "site_name", "region", "latitude", "longitude"]]


def _query_land_ids(
    session: requests.Session,
    layer_url: str,
    surface_field: str,
    lon: float,
    lat: float,
    distance_m: int,
) -> list[int]:
    geometry = json.dumps(
        {
            "x": float(lon),
            "y": float(lat),
            "spatialReference": {"wkid": 4326},
        }
    )
    params = {
        "f": "json",
        "where": f"{surface_field}='land'",
        "geometry": geometry,
        "geometryType": "esriGeometryPoint",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "returnIdsOnly": "true",
    }
    if distance_m > 0:
        params["distance"] = int(distance_m)
        params["units"] = "esriSRUnit_Meter"

    data = _get_json(session, f"{layer_url}/query", **params)
    return sorted(int(v) for v in (data.get("objectIds") or []))


def _query_site(
    site: dict,
    layer_url: str,
    surface_field: str,
) -> dict:
    session = _session()
    matches = {}
    for distance in DISTANCES_M:
        ids = _query_land_ids(
            session,
            layer_url,
            surface_field,
            float(site["longitude"]),
            float(site["latitude"]),
            distance,
        )
        matches[str(distance)] = {
            "land_count": len(ids),
            "land_object_ids": ids,
        }
        time.sleep(0.01)

    return {
        "site_id": str(site["site_id"]),
        "site_name": str(site["site_name"]),
        "region": str(site["region"]),
        "latitude": float(site["latitude"]),
        "longitude": float(site["longitude"]),
        "matches": matches,
    }


def audit(root: Path, workers: int = 4) -> dict:
    sites = _candidate_sites(root)
    session = _session()
    layer_url, meta, surface_field = _discover_layer(session)

    records = sites.to_dict(orient="records")
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        matched = list(
            pool.map(
                lambda site: _query_site(site, layer_url, surface_field),
                records,
            )
        )
    matched.sort(key=lambda row: row["site_id"])

    n_sites = len(matched)
    summaries = {}
    selected_distance = None
    for distance in DISTANCES_M:
        key = str(distance)
        counts = [int(row["matches"][key]["land_count"]) for row in matched]
        any_count = sum(value >= 1 for value in counts)
        multiple_count = sum(value > 1 for value in counts)
        summary = {
            "distance_m": distance,
            "candidate_sites": n_sites,
            "land_match_count": any_count,
            "land_match_fraction": any_count / n_sites if n_sites else None,
            "multiple_land_match_count": multiple_count,
            "multiple_land_match_fraction": (
                multiple_count / n_sites if n_sites else None
            ),
            "unmatched_count": n_sites - any_count,
        }
        summaries[key] = summary
        if (
            selected_distance is None
            and n_sites
            and summary["land_match_fraction"] >= 0.95
            and summary["multiple_land_match_fraction"] <= 0.05
        ):
            selected_distance = distance

    region_summary = {}
    for region in sorted({str(row["region"]) for row in matched}):
        local = [row for row in matched if str(row["region"]) == region]
        region_summary[region] = {
            "candidate_sites": len(local),
            "exact_land_matches": sum(
                int(row["matches"]["0"]["land_count"]) >= 1
                for row in local
            ),
            "within_5km_land_matches": sum(
                int(row["matches"]["5000"]["land_count"]) >= 1
                for row in local
            ),
            "unmatched_exact": [
                str(row["site_id"])
                for row in local
                if int(row["matches"]["0"]["land_count"]) == 0
            ],
            "unmatched_within_5km": [
                str(row["site_id"])
                for row in local
                if int(row["matches"]["5000"]["land_count"]) == 0
            ],
            "multiple_exact": [
                str(row["site_id"])
                for row in local
                if int(row["matches"]["0"]["land_count"]) > 1
            ],
            "multiple_within_5km": [
                str(row["site_id"])
                for row in local
                if int(row["matches"]["5000"]["land_count"]) > 1
            ],
        }

    assigned = {}
    if selected_distance is not None:
        key = str(selected_distance)
        for row in matched:
            ids = row["matches"][key]["land_object_ids"]
            assigned[row["site_id"]] = (
                ids[0] if len(ids) == 1 else None
            )

    return {
        "schema_version": 6,
        "audit_id": "mina-antarctic-add-site-match-audit-v1",
        "implementation": (
            "authoritative ArcGIS FeatureServer point-to-land spatial queries; "
            "no local continent-scale polygon reconstruction"
        ),
        "mapppdr_commit": PINNED_MAPPPDR_COMMIT,
        "candidate_species_ids": list(PRIMARY_SPECIES),
        "candidate_site_species_units": 152,
        "distinct_candidate_sites": n_sites,
        "scar_add_feature_service": SERVICE_ROOT,
        "scar_add_layer_url": layer_url,
        "scar_add_layer_name": meta.get("name"),
        "scar_add_object_id_field": meta.get("objectIdField"),
        "scar_add_surface_field": surface_field,
        "scar_add_layer_extent": meta.get("extent"),
        "distance_summaries": summaries,
        "region_summary": region_summary,
        "selected_distance_m": selected_distance,
        "gate1a_passed": selected_distance is not None,
        "assigned_land_object_id_if_unique": assigned,
        "site_matches": matched,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapppdr-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    result = audit(args.mapppdr_dir, workers=args.workers)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {key: value for key, value in result.items() if key != "site_matches"},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
