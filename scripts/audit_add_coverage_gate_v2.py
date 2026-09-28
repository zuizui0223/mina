#!/usr/bin/env python3
"""Outcome-blind SCAR ADD coverage gate for APBP Pygoscelis candidate sites."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import pyreadr
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PINNED = "88c73a507e0921b2541c218c71eaf16721bc6502"
SERVICE_ROOT = (
    "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
    "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer"
)
SPECIES = ("ADPE", "CHPE", "GEPE")
DISTANCES_M = (0, 500, 1000, 2000, 5000)


def _load(path: Path, expected: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(path))
    if expected in result:
        value = result[expected]
    elif len(result) == 1:
        value = next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(result)}")
    if not isinstance(value, pd.DataFrame):
        raise TypeError(expected)
    return value


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
    session.headers.update({"User-Agent": "mina-add-coverage-gate/2.0"})
    return session


def _get_json(session: requests.Session, url: str, **params):
    for attempt in range(4):
        response = session.get(url, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()
        error = data.get("error")
        if not error:
            return data
        if int(error.get("code", -1)) == 429 and attempt < 3:
            time.sleep(65)
            continue
        raise RuntimeError(f"ArcGIS error: {error}")
    raise RuntimeError("ArcGIS retry exhausted")


def _discover_layer(session: requests.Session):
    root = _get_json(session, SERVICE_ROOT, f="json")
    candidates = []
    for layer in root.get("layers", []):
        url = f"{SERVICE_ROOT}/{layer['id']}"
        meta = _get_json(session, url, f="json")
        fields = [str(x.get("name", "")) for x in meta.get("fields", [])]
        surface = [name for name in fields if name.lower() == "surface"]
        if surface:
            candidates.append((url, meta, surface[0]))
    if len(candidates) != 1:
        raise RuntimeError(f"surface layer count={len(candidates)}")
    return candidates[0]


def _candidate_sites(root: Path) -> pd.DataFrame:
    sites = _load(root / "data" / "sites.rda", "sites")
    obs = _load(root / "data" / "penguin_obs.rda", "penguin_obs")
    nest = obs[
        obs["species_id"].isin(SPECIES)
        & (obs["type"] == "nests")
        & obs["count"].notna()
    ].copy()
    nest["year"] = pd.to_numeric(nest["year"], errors="coerce")
    nest = nest.dropna(subset=["year"])

    units = []
    for (site_id, species_id), local in nest.groupby(["site_id", "species_id"]):
        years = sorted(set(int(v) for v in local["year"]))
        if len(years) >= 5 and max(years) - min(years) >= 10:
            units.append((str(site_id), str(species_id)))
    if len(units) != 152:
        raise ValueError(f"candidate unit drift: {len(units)} != 152")

    ids = sorted({site for site, _ in units})
    if len(ids) != 122:
        raise ValueError(f"candidate site drift: {len(ids)} != 122")
    out = sites[sites["site_id"].isin(ids)].copy()
    if len(out) != 122:
        raise ValueError("candidate site coordinate coverage drift")
    return out[["site_id", "site_name", "region", "latitude", "longitude"]]


def _query_ids(
    session: requests.Session,
    layer_url: str,
    surface_field: str,
    lon: float,
    lat: float,
    distance_m: int,
):
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


def audit(root: Path, throttle_seconds: float = 1.1) -> dict:
    sites = _candidate_sites(root)
    session = _session()
    layer_url, meta, surface_field = _discover_layer(session)

    rows = {
        str(row["site_id"]): {
            "site_id": str(row["site_id"]),
            "site_name": str(row["site_name"]),
            "region": str(row["region"]),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "first_match_distance_m": None,
            "first_match_land_object_ids": [],
        }
        for row in sites.to_dict(orient="records")
    }

    unmatched = set(rows)
    coverage = {}
    selected_distance = None

    for distance in DISTANCES_M:
        for site_id in sorted(unmatched):
            row = rows[site_id]
            ids = _query_ids(
                session,
                layer_url,
                surface_field,
                row["longitude"],
                row["latitude"],
                distance,
            )
            if ids:
                row["first_match_distance_m"] = distance
                row["first_match_land_object_ids"] = ids
            time.sleep(throttle_seconds)

        unmatched = {
            site_id
            for site_id, row in rows.items()
            if row["first_match_distance_m"] is None
        }
        matched_n = len(rows) - len(unmatched)
        coverage[str(distance)] = {
            "distance_m": distance,
            "candidate_sites": len(rows),
            "matched_sites": matched_n,
            "match_fraction": matched_n / len(rows),
            "unmatched_sites": len(unmatched),
        }
        if matched_n / len(rows) >= 0.95:
            selected_distance = distance
            break

    regions = {}
    for region in sorted({row["region"] for row in rows.values()}):
        local = [row for row in rows.values() if row["region"] == region]
        regions[region] = {
            "candidate_sites": len(local),
            "matched_by_selected_distance": (
                sum(
                    row["first_match_distance_m"] is not None
                    and selected_distance is not None
                    and row["first_match_distance_m"] <= selected_distance
                    for row in local
                )
                if selected_distance is not None
                else 0
            ),
            "unmatched_after_largest_queried_distance": [
                row["site_id"]
                for row in local
                if row["first_match_distance_m"] is None
            ],
        }

    first_distance_counts = {}
    for row in rows.values():
        key = (
            "unmatched"
            if row["first_match_distance_m"] is None
            else str(row["first_match_distance_m"])
        )
        first_distance_counts[key] = first_distance_counts.get(key, 0) + 1

    return {
        "schema_version": 1,
        "audit_id": "mina-antarctic-add-coverage-gate1a-v2",
        "mapppdr_commit": PINNED,
        "candidate_site_species_units": 152,
        "distinct_candidate_sites": 122,
        "scar_add_layer_url": layer_url,
        "scar_add_layer_name": meta.get("name"),
        "scar_add_object_id_field": meta.get("objectIdField"),
        "request_throttle_seconds": throttle_seconds,
        "queried_distances_m": [int(k) for k in coverage],
        "coverage_by_distance": coverage,
        "first_match_distance_counts": first_distance_counts,
        "selected_distance_m": selected_distance,
        "gate1a_v2_passed": selected_distance is not None,
        "region_summary": regions,
        "sites": [rows[key] for key in sorted(rows)],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--throttle-seconds", type=float, default=1.1)
    a = p.parse_args()
    result = audit(a.mapppdr_dir, a.throttle_seconds)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(
        {k: v for k, v in result.items() if k != "sites"},
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
