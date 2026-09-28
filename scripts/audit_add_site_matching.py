#!/usr/bin/env python3
"""Outcome-blind APBP site-to-SCAR-ADD land-polygon matching audit."""
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
SERVICE_URL = (
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
        total=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "mina-antarctic-island-atlas/1.0"})
    return session


def _get_json(session: requests.Session, url: str, **params):
    response = session.get(url, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(f"ArcGIS error: {data['error']}")
    return data


def _discover_layer(session: requests.Session) -> tuple[str, dict]:
    root = _get_json(session, SERVICE_URL, f="json")
    layers = root.get("layers", [])
    if not layers:
        raise RuntimeError("FeatureServer has no layers")
    candidates = []
    for item in layers:
        layer_url = f"{SERVICE_URL}/{item['id']}"
        meta = _get_json(session, layer_url, f="json")
        fields = [str(f.get("name", "")).lower() for f in meta.get("fields", [])]
        if "surface" in fields:
            candidates.append((layer_url, meta))
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

    rows = []
    for (site_id, species_id), local in nest.groupby(["site_id", "species_id"]):
        years = sorted(set(int(y) for y in local["year"]))
        n_years = len(years)
        span = max(years) - min(years) if years else 0
        if n_years >= 5 and span >= 10:
            rows.append(
                {
                    "site_id": str(site_id),
                    "species_id": str(species_id),
                    "n_years": n_years,
                    "first_year": min(years),
                    "last_year": max(years),
                    "span_years": span,
                }
            )
    units = pd.DataFrame(rows)
    if len(units) != 152:
        raise ValueError(f"candidate unit drift: {len(units)} != 152")

    candidate_site_ids = sorted(units["site_id"].unique())
    site_rows = sites[sites["site_id"].isin(candidate_site_ids)].copy()
    if len(site_rows) != len(candidate_site_ids):
        raise ValueError("candidate site coordinates are incomplete")
    return site_rows[["site_id", "site_name", "region", "latitude", "longitude"]]


def _query_one(
    site: dict,
    layer_url: str,
    surface_field: str,
) -> dict:
    session = _session()
    geometry = json.dumps(
        {
            "x": float(site["longitude"]),
            "y": float(site["latitude"]),
            "spatialReference": {"wkid": 4326},
        }
    )
    result = {
        "site_id": str(site["site_id"]),
        "site_name": str(site["site_name"]),
        "region": str(site["region"]),
        "latitude": float(site["latitude"]),
        "longitude": float(site["longitude"]),
        "matches": {},
    }

    for distance in DISTANCES_M:
        params = {
            "f": "json",
            "where": "1=1",
            "geometry": geometry,
            "geometryType": "esriGeometryPoint",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "false",
        }
        if distance > 0:
            params["distance"] = distance
            params["units"] = "esriSRUnit_Meter"
        data = _get_json(session, f"{layer_url}/query", **params)
        features = data.get("features", [])
        land = []
        for feature in features:
            attrs = feature.get("attributes", {})
            value = attrs.get(surface_field)
            if value is not None and str(value).strip().lower() == "land":
                land.append(attrs)
        result["matches"][str(distance)] = {
            "feature_count": len(features),
            "land_count": len(land),
            "land_attributes": land,
        }
        time.sleep(0.02)
    return result


def audit(root: Path, workers: int = 4) -> dict:
    sites = _candidate_sites(root)
    session = _session()
    layer_url, meta = _discover_layer(session)

    field_names = [str(f.get("name", "")) for f in meta.get("fields", [])]
    surface_field = next(
        name for name in field_names if name.lower() == "surface"
    )

    records = sites.to_dict(orient="records")
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        matched = list(
            pool.map(
                lambda site: _query_one(site, layer_url, surface_field),
                records,
            )
        )

    summaries = {}
    n_sites = len(matched)
    selected = None
    for distance in DISTANCES_M:
        key = str(distance)
        land_counts = [int(r["matches"][key]["land_count"]) for r in matched]
        any_count = sum(v >= 1 for v in land_counts)
        multiple_count = sum(v > 1 for v in land_counts)
        summaries[key] = {
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
        if (
            selected is None
            and n_sites
            and any_count / n_sites >= 0.95
            and multiple_count / n_sites <= 0.05
        ):
            selected = distance

    return {
        "schema_version": 1,
        "audit_id": "mina-antarctic-add-site-match-audit-v1",
        "mapppdr_commit": PINNED_MAPPPDR_COMMIT,
        "candidate_species_ids": list(PRIMARY_SPECIES),
        "candidate_site_species_units": 152,
        "distinct_candidate_sites": n_sites,
        "scar_add_feature_service": SERVICE_URL,
        "scar_add_layer_url": layer_url,
        "scar_add_layer_name": meta.get("name"),
        "scar_add_object_id_field": meta.get("objectIdField"),
        "scar_add_surface_field": surface_field,
        "scar_add_fields": field_names,
        "distance_summaries": summaries,
        "selected_distance_m": selected,
        "gate1a_passed": selected is not None,
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
    print(json.dumps(
        {
            k: v
            for k, v in result.items()
            if k != "site_matches"
        },
        indent=2,
        sort_keys=True,
    ))
    if not result["gate1a_passed"]:
        raise SystemExit("Gate 1A failed: no spatial tolerance met the frozen rule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
