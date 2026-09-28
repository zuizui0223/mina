#!/usr/bin/env python3
"""Gate 1A v4: outcome-blind unique SCAR land-FID assignment.

Exact point containment is preferred. Sites that do not intersect land exactly
are assigned only to the unique land FID appearing at the minimum service-native
distance, found by integer-meter binary search. Raw FIDs are geometric anchors,
not biological islands.
"""
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

MAPPPDR_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"
LAYER = (
    "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
    "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer/1"
)
PRIMARY_SPECIES = ("ADPE", "CHPE", "GEPE")
MAX_DISTANCE_M = 5000


def load_rda(path: Path, expected: str) -> pd.DataFrame:
    x = pyreadr.read_r(str(path))
    if expected in x:
        frame = x[expected]
    elif len(x) == 1:
        frame = next(iter(x.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(x)}")
    if not isinstance(frame, pd.DataFrame):
        raise TypeError(expected)
    return frame


def candidate_sites(root: Path) -> pd.DataFrame:
    sites = load_rda(root / "data" / "sites.rda", "sites")
    obs = load_rda(root / "data" / "penguin_obs.rda", "penguin_obs")
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
    if len(out) != 122:
        raise ValueError(f"candidate site drift: {len(out)} != 122")
    return out[
        ["site_id", "site_name", "region", "ccamlr_id", "latitude", "longitude"]
    ]


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=8,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": "mina-antarctic-island-atlas-gate1a-v4/1.0"})
    return s


def query_ids(
    s: requests.Session,
    lon: float,
    lat: float,
    distance: int,
    cache: dict[int, list[int]],
    delay_s: float,
    max_attempts: int = 20,
) -> list[int]:
    if distance in cache:
        return cache[distance]

    geometry = json.dumps(
        {
            "x": float(lon),
            "y": float(lat),
            "spatialReference": {"wkid": 4326},
        }
    )
    params = {
        "f": "json",
        "where": "surface='land'",
        "geometry": geometry,
        "geometryType": "esriGeometryPoint",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "returnIdsOnly": "true",
    }
    if distance > 0:
        params["distance"] = int(distance)
        params["units"] = "esriSRUnit_Meter"

    for _ in range(max_attempts):
        r = s.get(LAYER + "/query", params=params, timeout=120)
        if r.status_code == 429:
            retry_after = float(r.headers.get("Retry-After", "65"))
            time.sleep(max(65.0, retry_after))
            continue
        r.raise_for_status()
        x = r.json()
        error = x.get("error")
        if error:
            if int(error.get("code", 0)) == 429:
                time.sleep(65.0)
                continue
            raise RuntimeError(error)
        ids = sorted(int(v) for v in (x.get("objectIds") or []))
        cache[distance] = ids
        if delay_s > 0:
            time.sleep(delay_s)
        return ids

    raise RuntimeError(
        f"ArcGIS retry exhausted at lon={lon}, lat={lat}, distance={distance}"
    )


def resolve_site(
    s: requests.Session,
    row: dict,
    delay_s: float,
) -> tuple[dict, int]:
    lon = float(row["longitude"])
    lat = float(row["latitude"])
    cache: dict[int, list[int]] = {}

    exact = query_ids(s, lon, lat, 0, cache, delay_s)
    if len(exact) == 1:
        status = "assigned_exact"
        assigned = exact[0]
        distance = 0
    elif len(exact) > 1:
        status = "ambiguous_exact"
        assigned = None
        distance = 0
    else:
        at_max = query_ids(s, lon, lat, MAX_DISTANCE_M, cache, delay_s)
        if not at_max:
            status = "unresolved_no_land_within_5km"
            assigned = None
            distance = None
        else:
            low, high = 1, MAX_DISTANCE_M
            while low < high:
                mid = (low + high) // 2
                if query_ids(s, lon, lat, mid, cache, delay_s):
                    high = mid
                else:
                    low = mid + 1
            distance = low
            first_ids = query_ids(s, lon, lat, distance, cache, delay_s)
            if len(first_ids) == 1:
                status = "assigned_nearest"
                assigned = first_ids[0]
            else:
                status = "ambiguous_minimum_distance"
                assigned = None

    record = {
        "site_id": str(row["site_id"]),
        "site_name": str(row["site_name"]),
        "region": str(row["region"]),
        "ccamlr_id": None if pd.isna(row["ccamlr_id"]) else str(row["ccamlr_id"]),
        "latitude": lat,
        "longitude": lon,
        "assignment_status": status,
        "assigned_fid": assigned,
        "assignment_distance_m": distance,
        "exact_fids": exact,
        "minimum_distance_fids": (
            cache.get(distance, []) if distance is not None else []
        ),
        "queried_distances_m": sorted(cache),
    }
    return record, len(cache)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--delay-s", type=float, default=0.05)
    a = p.parse_args()

    sites = candidate_sites(a.mapppdr_dir)
    s = session()
    records = []
    api_calls = 0

    for row in sites.to_dict(orient="records"):
        rec, calls = resolve_site(s, row, a.delay_s)
        records.append(rec)
        api_calls += calls
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(
            json.dumps(
                {
                    "schema_version": 4,
                    "audit_id": "mina-antarctic-add-site-assignment-v4",
                    "status": "running",
                    "completed_sites": len(records),
                    "expected_sites": 122,
                    "api_calls": api_calls,
                    "site_assignments": records,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    unique = [
        r for r in records
        if r["assignment_status"] in {"assigned_exact", "assigned_nearest"}
    ]
    unresolved = [r for r in records if r not in unique]
    n = len(records)

    status_counts = {}
    for r in records:
        status_counts[r["assignment_status"]] = (
            status_counts.get(r["assignment_status"], 0) + 1
        )

    region_summary = {}
    for region in sorted({r["region"] for r in records}):
        local = [r for r in records if r["region"] == region]
        local_unique = [
            r for r in local
            if r["assignment_status"] in {"assigned_exact", "assigned_nearest"}
        ]
        region_summary[region] = {
            "candidate_sites": len(local),
            "unique_assignments": len(local_unique),
            "unique_assignment_fraction": len(local_unique) / len(local),
            "unresolved_site_ids": [
                r["site_id"]
                for r in local
                if r["assignment_status"] not in {"assigned_exact", "assigned_nearest"}
            ],
        }

    assignment_distances = sorted(
        int(r["assignment_distance_m"])
        for r in unique
        if r["assignment_distance_m"] is not None
    )

    result = {
        "schema_version": 4,
        "audit_id": "mina-antarctic-add-site-assignment-v4",
        "implementation": (
            "FeatureServer returnIdsOnly; exact containment first; exact misses "
            "resolved by integer-meter binary search for the first land match"
        ),
        "mapppdr_commit": MAPPPDR_COMMIT,
        "candidate_species_ids": list(PRIMARY_SPECIES),
        "candidate_site_species_units": 152,
        "distinct_candidate_sites": n,
        "api_calls": api_calls,
        "maximum_search_distance_m": MAX_DISTANCE_M,
        "assignment_status_counts": status_counts,
        "unique_assignment_count": len(unique),
        "unique_assignment_fraction": len(unique) / n,
        "unresolved_count": len(unresolved),
        "unresolved_fraction": len(unresolved) / n,
        "assignment_distance_m_summary": {
            "max": max(assignment_distances) if assignment_distances else None,
            "median": assignment_distances[len(assignment_distances)//2]
            if assignment_distances else None,
            "exact_count": sum(
                r["assignment_status"] == "assigned_exact" for r in records
            ),
            "nearest_count": sum(
                r["assignment_status"] == "assigned_nearest" for r in records
            ),
        },
        "region_summary": region_summary,
        "gate1a_passed": (
            len(unique) / n >= 0.95
            and len(unresolved) / n <= 0.05
        ),
        "site_assignments": records,
    }

    a.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {k: v for k, v in result.items() if k != "site_assignments"},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
