#!/usr/bin/env python3
"""Outcome-blind APBP site-to-SCAR-ADD land-polygon matching audit.

Gate 1A downloads the complete SCAR ADD v7.12 land layer through simple
paginated attribute queries, then performs all distance calculations locally
in EPSG:3031. No penguin demographic outcome is used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyreadr
import requests
from pyproj import Transformer
from requests.adapters import HTTPAdapter
from shapely.geometry import Point, shape
from shapely.ops import transform as shapely_transform
from shapely.strtree import STRtree
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


def _download_all_land(
    session: requests.Session,
    layer_url: str,
    surface_field: str,
    object_id_field: str,
    chunk_size: int = 100,
) -> tuple[list, list[dict], int, dict, object]:
    id_data = _get_json(
        session,
        f"{layer_url}/query",
        f="json",
        where=f"{surface_field}='land'",
        returnIdsOnly="true",
    )
    object_ids = sorted(int(v) for v in (id_data.get("objectIds") or []))
    if not object_ids:
        raise RuntimeError("SCAR ADD returned zero land polygon IDs")

    features = []
    geojson_crs = None
    for start in range(0, len(object_ids), chunk_size):
        chunk = object_ids[start : start + chunk_size]
        data = _get_json(
            session,
            f"{layer_url}/query",
            f="geojson",
            objectIds=",".join(str(v) for v in chunk),
            outFields="*",
            returnGeometry="true",
            outSR=4326,
            maxAllowableOffset=0.0001,
        )
        if geojson_crs is None:
            geojson_crs = data.get("crs")
        batch = data.get("features", [])
        if len(batch) != len(chunk):
            raise RuntimeError(
                f"ADD object-ID chunk drift at {start}: "
                f"{len(batch)} != {len(chunk)}"
            )
        features.extend(batch)

    if len(features) != len(object_ids):
        raise RuntimeError(
            f"ADD retrieval drift: {len(features)} != {len(object_ids)}"
        )

    transformer = Transformer.from_crs(4326, 3031, always_xy=True)
    geoms = []
    attrs = []
    repaired = 0
    raw_minx = float("inf")
    raw_miny = float("inf")
    raw_maxx = float("-inf")
    raw_maxy = float("-inf")
    for feature in features:
        geom_value = feature.get("geometry")
        if not geom_value:
            continue
        geom = shape(geom_value)
        bx0, by0, bx1, by1 = geom.bounds
        raw_minx = min(raw_minx, float(bx0))
        raw_miny = min(raw_miny, float(by0))
        raw_maxx = max(raw_maxx, float(bx1))
        raw_maxy = max(raw_maxy, float(by1))
        if not geom.is_valid:
            geom = geom.buffer(0)
            repaired += 1
        projected = shapely_transform(transformer.transform, geom)
        if projected.is_empty:
            continue
        geoms.append(projected)
        attrs.append(feature.get("properties", {}))

    raw_bounds = {
        "min_x": raw_minx,
        "min_y": raw_miny,
        "max_x": raw_maxx,
        "max_y": raw_maxy,
    }
    return geoms, attrs, repaired, raw_bounds, geojson_crs


def audit(root: Path) -> dict:
    sites = _candidate_sites(root)
    session = _session()
    layer_url, meta, surface_field = _discover_layer(session)
    object_id_field = str(meta.get("objectIdField") or "")
    if not object_id_field:
        raise RuntimeError("SCAR ADD layer has no objectIdField")

    geoms, attrs, repaired, raw_bounds, geojson_crs = _download_all_land(
        session,
        layer_url,
        surface_field,
        object_id_field,
    )
    tree = STRtree(geoms)
    transformer = Transformer.from_crs(4326, 3031, always_xy=True)

    matched = []
    for site in sites.to_dict(orient="records"):
        point = shapely_transform(
            transformer.transform,
            Point(float(site["longitude"]), float(site["latitude"])),
        )
        nearby_indices = tree.query(point.buffer(max(DISTANCES_M)))
        local = []
        for index in nearby_indices:
            idx = int(index)
            distance = float(point.distance(geoms[idx]))
            local.append((distance, attrs[idx]))
        local.sort(key=lambda item: item[0])

        counts = {}
        for distance in DISTANCES_M:
            counts[str(distance)] = sum(
                d <= float(distance) + 1e-6 for d, _ in local
            )

        matched.append(
            {
                "site_id": str(site["site_id"]),
                "site_name": str(site["site_name"]),
                "region": str(site["region"]),
                "latitude": float(site["latitude"]),
                "longitude": float(site["longitude"]),
                "nearest_land_distance_m": (
                    local[0][0] if local else None
                ),
                "nearest_land_attributes": (
                    local[0][1] if local else None
                ),
                "land_match_counts": counts,
            }
        )

    n_sites = len(matched)
    summaries = {}
    selected_distance = None
    for distance in DISTANCES_M:
        key = str(distance)
        counts = [int(r["land_match_counts"][key]) for r in matched]
        any_count = sum(v >= 1 for v in counts)
        multiple_count = sum(v > 1 for v in counts)
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

    finite = sorted(
        float(r["nearest_land_distance_m"])
        for r in matched
        if r["nearest_land_distance_m"] is not None
    )
    quantiles = {}
    if finite:
        for label, q in (
            ("q0", 0.0),
            ("q25", 0.25),
            ("q50", 0.5),
            ("q75", 0.75),
            ("q90", 0.9),
            ("q95", 0.95),
            ("q100", 1.0),
        ):
            idx = round(q * (len(finite) - 1))
            quantiles[label] = finite[idx]

    fields = [str(f.get("name", "")) for f in meta.get("fields", [])]
    return {
        "schema_version": 4,
        "audit_id": "mina-antarctic-add-site-match-audit-v1",
        "implementation": (
            "complete paginated SCAR ADD land layer downloaded through "
            "simple attribute queries; distances calculated locally in EPSG:3031"
        ),
        "mapppdr_commit": PINNED_MAPPPDR_COMMIT,
        "candidate_species_ids": list(PRIMARY_SPECIES),
        "candidate_site_species_units": 152,
        "distinct_candidate_sites": n_sites,
        "scar_add_feature_service": SERVICE_URL,
        "scar_add_layer_url": layer_url,
        "scar_add_layer_name": meta.get("name"),
        "scar_add_object_id_field": object_id_field,
        "scar_add_surface_field": surface_field,
        "scar_add_fields": fields,
        "downloaded_land_polygon_count": len(geoms),
        "geometry_generalization_degrees": 0.0001,
        "repaired_invalid_polygon_count": repaired,
        "raw_geojson_coordinate_bounds": raw_bounds,
        "raw_geojson_crs": geojson_crs,
        "nearest_land_distance_quantiles_m": quantiles,
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
    args = parser.parse_args()

    result = audit(args.mapppdr_dir)
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
