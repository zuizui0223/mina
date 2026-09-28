#!/usr/bin/env python3
"""Outcome-blind APBP site-to-SCAR-ADD land-polygon matching audit.

Gate 1A deliberately uses server-side point-distance queries only. Polygon
geometry is not downloaded until the matching tolerance itself is frozen.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
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
        total=6,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        respect_retry_after_header=True,
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


def _discover_layer(session: requests.Session) -> tuple[str, dict, str]:
    root = _get_json(session, SERVICE_URL, f="json")
    candidates = []
    for item in root.get("layers", []):
        layer_url = f"{SERVICE_URL}/{item['id']}"
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

    units = []
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


def _count_land(
    session: requests.Session,
    layer_url: str,
    surface_field: str,
    longitude: float,
    latitude: float,
    distance_m: int,
) -> int:
    geometry = json.dumps(
        {
            "x": float(longitude),
            "y": float(latitude),
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
        "returnCountOnly": "true",
    }
    if distance_m > 0:
        params["distance"] = distance_m
        params["units"] = "esriSRUnit_Meter"

    data = _get_json(session, f"{layer_url}/query", **params)
    return int(data.get("count", 0))


def _query_site(
    site: dict,
    layer_url: str,
    surface_field: str,
    distances: tuple[int, ...],
) -> dict:
    session = _session()
    counts = {}
    for distance in distances:
        counts[str(distance)] = _count_land(
            session,
            layer_url,
            surface_field,
            float(site["longitude"]),
            float(site["latitude"]),
            distance,
        )

    return {
        "site_id": str(site["site_id"]),
        "site_name": str(site["site_name"]),
        "region": str(site["region"]),
        "latitude": float(site["latitude"]),
        "longitude": float(site["longitude"]),
        "land_match_counts": counts,
    }


def audit(root: Path, workers: int = 12) -> dict:
    sites = _candidate_sites(root)
    session = _session()
    layer_url, meta, surface_field = _discover_layer(session)

    records = sites.to_dict(orient="records")

    def run_distances(distances: tuple[int, ...]) -> list[dict]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            return list(
                pool.map(
                    lambda site: _query_site(
                        site,
                        layer_url,
                        surface_field,
                        distances,
                    ),
                    records,
                )
            )

    # Exact and the maximum frozen tolerance are sufficient to decide whether
    # any smaller tolerance can possibly pass the >=95% coverage rule.
    matched = run_distances((0, 5000))
    n_sites = len(matched)

    def summarize(distance: int) -> dict:
        key = str(distance)
        counts = [int(r["land_match_counts"][key]) for r in matched]
        any_count = sum(v >= 1 for v in counts)
        multiple_count = sum(v > 1 for v in counts)
        return {
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

    summaries = {
        "0": summarize(0),
        "5000": summarize(5000),
    }

    five_k_passes_coverage = (
        summaries["5000"]["land_match_fraction"] is not None
        and summaries["5000"]["land_match_fraction"] >= 0.95
    )

    # Only if 5 km has sufficient coverage can a smaller distance satisfy the
    # frozen rule. Query the intermediate distances then.
    if five_k_passes_coverage:
        intermediate = run_distances((500, 1000, 2000))
        by_id = {r["site_id"]: r for r in matched}
        for row in intermediate:
            by_id[row["site_id"]]["land_match_counts"].update(
                row["land_match_counts"]
            )
        matched = [by_id[str(site["site_id"])] for site in records]
        for distance in (500, 1000, 2000):
            summaries[str(distance)] = summarize(distance)

    selected_distance = None
    for distance in DISTANCES_M:
        key = str(distance)
        if key not in summaries:
            continue
        summary = summaries[key]
        if (
            summary["land_match_fraction"] >= 0.95
            and summary["multiple_land_match_fraction"] <= 0.05
        ):
            selected_distance = distance
            break

    region_summary = {}
    for region in sorted({str(r["region"]) for r in matched}):
        local = [r for r in matched if str(r["region"]) == region]
        region_summary[region] = {
            "candidate_sites": len(local),
            "exact_land_matches": sum(
                int(r["land_match_counts"]["0"]) >= 1 for r in local
            ),
            "within_5km_land_matches": sum(
                int(r["land_match_counts"]["5000"]) >= 1 for r in local
            ),
            "unmatched_within_5km": [
                str(r["site_id"])
                for r in local
                if int(r["land_match_counts"]["5000"]) == 0
            ],
            "multiple_within_5km": [
                str(r["site_id"])
                for r in local
                if int(r["land_match_counts"]["5000"]) > 1
            ],
        }

    fields = [str(f.get("name", "")) for f in meta.get("fields", [])]
    return {
        "schema_version": 3,
        "audit_id": "mina-antarctic-add-site-match-audit-v1",
        "implementation": (
            "ArcGIS server-side point-distance count query; exact + 5 km "
            "queried first, intermediate frozen distances queried only if "
            "5 km meets the frozen coverage gate"
        ),
        "mapppdr_commit": PINNED_MAPPPDR_COMMIT,
        "candidate_species_ids": list(PRIMARY_SPECIES),
        "candidate_site_species_units": 152,
        "distinct_candidate_sites": n_sites,
        "scar_add_feature_service": SERVICE_URL,
        "scar_add_layer_url": layer_url,
        "scar_add_layer_name": meta.get("name"),
        "scar_add_object_id_field": meta.get("objectIdField"),
        "scar_add_surface_field": surface_field,
        "scar_add_fields": fields,
        "distance_summaries": summaries,
        "region_summary": region_summary,
        "selected_distance_m": selected_distance,
        "gate1a_passed": selected_distance is not None,
        "site_matches": matched,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapppdr-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    result = audit(args.mapppdr_dir, workers=args.workers)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {k: v for k, v in result.items() if k != "site_matches"},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
