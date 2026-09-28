#!/usr/bin/env python3
"""Outcome-blind APBP site-to-SCAR-ADD land-polygon matching audit."""
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
        total=5,
        backoff_factor=1.0,
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


def _discover_layer(session: requests.Session) -> tuple[str, dict]:
    root = _get_json(session, SERVICE_URL, f="json")
    candidates = []
    for item in root.get("layers", []):
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


def _download_land_polygons(
    session: requests.Session,
    layer_url: str,
    meta: dict,
    sites: pd.DataFrame,
) -> tuple[list, list[dict]]:
    field_names = [str(f.get("name", "")) for f in meta.get("fields", [])]
    surface_field = next(name for name in field_names if name.lower() == "surface")
    object_id = str(meta.get("objectIdField") or "")
    if not object_id:
        raise RuntimeError("missing object ID field")

    multipoint = {
        "points": [
            [float(row.longitude), float(row.latitude)]
            for row in sites.itertuples(index=False)
        ],
        "spatialReference": {"wkid": 4326},
    }
    filter_params = {
        "where": f"{surface_field}='land'",
        "geometry": json.dumps(multipoint),
        "geometryType": "esriGeometryMultipoint",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "distance": max(DISTANCES_M),
        "units": "esriSRUnit_Meter",
    }

    id_data = _get_json(
        session,
        f"{layer_url}/query",
        f="json",
        returnIdsOnly="true",
        **filter_params,
    )
    object_ids = sorted(int(v) for v in id_data.get("objectIds", []) or [])
    if not object_ids:
        raise RuntimeError("no SCAR land polygons found within 5 km of candidate sites")

    features = []
    for start in range(0, len(object_ids), 200):
        chunk = object_ids[start : start + 200]
        data = _get_json(
            session,
            f"{layer_url}/query",
            f="geojson",
            objectIds=",".join(str(v) for v in chunk),
            outFields=f"{object_id},{surface_field}",
            returnGeometry="true",
            outSR=4326,
            maxAllowableOffset=0.0005,
        )
        features.extend(data.get("features", []))

    if len(features) != len(object_ids):
        raise RuntimeError(
            f"candidate-neighborhood polygon retrieval drift: "
            f"{len(features)} != {len(object_ids)}"
        )

    transformer = Transformer.from_crs(4326, 3031, always_xy=True)
    geoms = []
    attrs = []
    for feature in features:
        value = feature.get("geometry")
        if not value:
            continue
        geom = shape(value)
        projected = shapely_transform(transformer.transform, geom)
        if projected.is_empty:
            continue
        geoms.append(projected)
        attrs.append(feature.get("properties", {}))
    return geoms, attrs


def audit(root: Path) -> dict:
    sites = _candidate_sites(root)
    session = _session()
    layer_url, meta = _discover_layer(session)
    geoms, attrs = _download_land_polygons(session, layer_url, meta, sites)
    tree = STRtree(geoms)
    transformer = Transformer.from_crs(4326, 3031, always_xy=True)

    matched = []
    for site in sites.to_dict(orient="records"):
        point = shapely_transform(
            transformer.transform,
            Point(float(site["longitude"]), float(site["latitude"])),
        )
        nearby_indices = tree.query(point.buffer(max(DISTANCES_M)))
        distances = []
        nearby_attrs = []
        for index in nearby_indices:
            geom = geoms[int(index)]
            distances.append(float(point.distance(geom)))
            nearby_attrs.append(attrs[int(index)])

        record = {
            "site_id": str(site["site_id"]),
            "site_name": str(site["site_name"]),
            "region": str(site["region"]),
            "latitude": float(site["latitude"]),
            "longitude": float(site["longitude"]),
            "nearest_land_distance_m": min(distances) if distances else None,
            "matches": {},
        }
        for distance in DISTANCES_M:
            selected = [
                a
                for d, a in zip(distances, nearby_attrs)
                if d <= float(distance) + 1e-6
            ]
            record["matches"][str(distance)] = {
                "land_count": len(selected),
                "land_attributes": selected,
            }
        matched.append(record)

    summaries = {}
    n_sites = len(matched)
    selected_distance = None
    for distance in DISTANCES_M:
        key = str(distance)
        counts = [int(r["matches"][key]["land_count"]) for r in matched]
        any_count = sum(v >= 1 for v in counts)
        multiple_count = sum(v > 1 for v in counts)
        summary = {
            "distance_m": distance,
            "candidate_sites": n_sites,
            "land_match_count": any_count,
            "land_match_fraction": any_count / n_sites,
            "multiple_land_match_count": multiple_count,
            "multiple_land_match_fraction": multiple_count / n_sites,
            "unmatched_count": n_sites - any_count,
        }
        summaries[key] = summary
        if (
            selected_distance is None
            and summary["land_match_fraction"] >= 0.95
            and summary["multiple_land_match_fraction"] <= 0.05
        ):
            selected_distance = distance

    fields = [str(f.get("name", "")) for f in meta.get("fields", [])]
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
        "scar_add_fields": fields,
        "candidate_neighborhood_land_polygon_count": len(geoms),
        "geometry_generalization_degrees": 0.0005,
        "distance_summaries": summaries,
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
    print(json.dumps(
        {k: v for k, v in result.items() if k != "site_matches"},
        indent=2,
        sort_keys=True,
    ))
    if not result["gate1a_passed"]:
        raise SystemExit("Gate 1A failed: no spatial tolerance met the frozen rule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
