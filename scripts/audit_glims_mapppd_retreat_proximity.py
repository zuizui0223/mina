#!/usr/bin/env python3
"""Original-source-only GLIMS glacier-change geometry × MAPPPD colony-site proximity.

Makes no claim of newly exposed rock, suitable breeding habitat, true site
absence, or climate effects. Glacier polygon differences may include oceanic
calving, positional offsets, mapping artefacts and nonuniform source dates.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr
from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform, unary_union

from scripts.audit_glims_antarctic_island_source import (
    GLACIER_KEY_FIELDS, PILOT_BBOXES, WFS, http_get, years_from_properties
)

PINNED_MAPPPDR_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"
TARGET_SPECIES = {"ADPE", "CHPE", "GEPE"}
MAX_FEATURES = 500


def load_rda(path: Path, name: str) -> pd.DataFrame:
    data = pyreadr.read_r(str(path))
    if name in data:
        return data[name]
    if len(data) == 1:
        return next(iter(data.values()))
    raise ValueError(f"{path}: unexpected R data objects {list(data)}")


def dated_grouped_features(data: dict, project) -> tuple[dict, dict]:
    """Group exact source GLIMS IDs with valid polygon geometry by year."""
    groups = defaultdict(lambda: defaultdict(list))
    issues = defaultdict(int)
    for feat in data.get("features", []):
        props = {str(k).lower(): v for k, v in (feat.get("properties") or {}).items()}
        glacier_id = next((str(props[k]) for k in GLACIER_KEY_FIELDS
                           if props.get(k) not in (None, "")), None)
        years = years_from_properties(props)
        if glacier_id is None or len(years) != 1:
            issues["missing_glacier_id_or_unique_source_year"] += 1
            continue
        try:
            obj = shape(feat["geometry"])
            if obj.is_empty or obj.geom_type not in ("Polygon", "MultiPolygon"):
                issues["non_polygon_or_empty"] += 1
                continue
            if not obj.is_valid:
                issues["invalid_source_polygon_not_repaired"] += 1
                continue
            proj = transform(project, obj)
            if not proj.is_valid or proj.area <= 0:
                issues["invalid_projected_polygon"] += 1
                continue
            groups[glacier_id][years[0]].append(proj)
        except (TypeError, ValueError, KeyError):
            issues["malformed_geometry"] += 1
    return groups, dict(issues)


def retreat_candidate_shapes(groups: dict) -> tuple[list[dict], dict]:
    """Earliest-vs-latest extent difference is a GEOMETRIC CANDIDATE only."""
    samples = []
    issues = defaultdict(int)
    for glacier_id, byyear in sorted(groups.items()):
        years = sorted(byyear)
        if len(years) < 2 or years[-1] - years[0] < 5:
            issues["no_valid_multi_epoch_pair_5plus_years"] += 1
            continue
        try:
            old = unary_union(byyear[years[0]])
            new = unary_union(byyear[years[-1]])
            if not (old.is_valid and new.is_valid):
                issues["invalid_epoch_union"] += 1
                continue
            # Not confirmed bare ground: new ocean coastline/ice mapping also matters.
            change = old.difference(new)
            if not change.is_valid:
                issues["invalid_ice_difference"] += 1
                continue
            if change.is_empty or change.area <= 0:
                issues["no_positive_apparent_old_minus_new_area"] += 1
                continue
            samples.append({
                "glims_id": glacier_id,
                "early_year": years[0], "late_year": years[-1],
                "early_glacier_km2": old.area / 1e6,
                "late_glacier_km2": new.area / 1e6,
                "apparent_old_minus_new_km2": change.area / 1e6,
                "geometry": change,
            })
        except Exception:
            issues["pair_geometry_failed"] += 1
    return samples, dict(issues)


def summarize_site_proximity(sites: pd.DataFrame, shapes: list[dict],
                             project) -> list[dict]:
    out = []
    for r in sites.itertuples(index=False):
        try:
            lon, lat = float(r.longitude), float(r.latitude)
            if not np.isfinite(lon) or not np.isfinite(lat):
                continue
            pt = Point(*project(lon, lat))
            if not shapes:
                continue
            best = min(shapes, key=lambda x: x["geometry"].distance(pt))
            dist = float(best["geometry"].distance(pt))
            out.append({
                "site_id": str(r.site_id),
                "site_name": str(r.site_name),
                "latitude": lat, "longitude": lon,
                "nearest_glims_id": best["glims_id"],
                "source_year_early": best["early_year"],
                "source_year_late": best["late_year"],
                "nearest_apparent_ice_loss_m": round(dist, 2),
                "within_1km": dist <= 1000,
                "within_5km": dist <= 5000,
                "proximity_not_exact_exposure": True,
            })
        except (ValueError, TypeError):
            continue
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    a = p.parse_args()
    sites = load_rda(a.mapppdr_dir / "data/sites.rda", "sites")
    links = load_rda(a.mapppdr_dir / "data/site_species.rda", "site_species")
    needed_cols = {"site_id", "site_name", "latitude", "longitude"}
    if not needed_cols.issubset(sites.columns) or not {"site_id", "species_id"}.issubset(links.columns):
        raise SystemExit("source MAPPPD site metadata schema mismatch")
    ids = set(links.loc[links["species_id"].isin(TARGET_SPECIES), "site_id"].astype(str))
    sites = sites[sites["site_id"].astype(str).isin(ids)].copy()
    result = {
        "status": "SOURCE_PROXIMITY_AUDIT_NO_BIOLOGICAL_EFFECT",
        "mapppdr_commit": PINNED_MAPPPDR_COMMIT,
        "source_layer": "GLIMS:GLIMS_Glacier_Outlines",
        "source_wfs": WFS,
        "geometry_crs": "EPSG:3031",
        "target_species": sorted(TARGET_SPECIES),
        "candidate_sites_count": int(len(sites)),
        "by_region": {},
        "limits": [
            "GLIMS ID may drift across inventory migrations; two dated outlines per ID are source candidates, not proven identical physical glacier boundaries.",
            "Old polygon minus new polygon is apparent ice extent difference, possibly in ocean or a georeferencing artefact; NOT newly exposed rock.",
            "MAPPPD site point may be a centroid, with uncalibrated location uncertainty; distance is provisional site-to-source support only.",
            "No site surveyed absence, actual new nesting, climate attribution, colony count, demographic or causal effect is computed.",
        ],
    }
    project = Transformer.from_crs(4326, 3031, always_xy=True).transform
    records = []
    for region, (west,south,east,north) in PILOT_BBOXES.items():
        raw = http_get({
            "service": "WFS", "version": "1.0.0", "request": "GetFeature",
            "typeName": "GLIMS:GLIMS_Glacier_Outlines",
            "maxFeatures": str(MAX_FEATURES),
            "outputFormat": "application/json", "srsName": "EPSG:4326",
            "bbox": f"{west},{south},{east},{north}",
        })
        data = json.loads(raw)
        total = data.get("totalFeatures", data.get("numberMatched"))
        if len(data.get("features", [])) >= MAX_FEATURES or (
            isinstance(total, int) and total > len(data.get("features", []))
        ):
            raise SystemExit(f"{region}: source page truncated; cannot identify multi-epoch pairs")
        groups, issues = dated_grouped_features(data, project)
        candidates, geom_issues = retreat_candidate_shapes(groups)
        local = sites[
            sites["latitude"].between(south, north)
            & sites["longitude"].between(west, east)
        ].copy()
        rows = summarize_site_proximity(local, candidates, project)
        for row in rows:
            row["bbox_region"] = region
            records.append(row)
        result["by_region"][region] = {
            "original_wfs_sha256": hashlib.sha256(raw).hexdigest(),
            "wfs_features": len(data.get("features", [])),
            "wfs_reported_total_features": total,
            "distinct_glims_ids_with_valid_geometry": len(groups),
            "glims_ids_with_apparent_old_minus_new_polygon": len(candidates),
            "raw_apparent_ice_loss_km2_sum": round(sum(x["apparent_old_minus_new_km2"] for x in candidates), 4),
            "mapppdr_site_points_in_bbox": len(local),
            "mapppdr_sites_with_a_comparable_pair": len(rows),
            "provisional_sites_within_1km": sum(x["within_1km"] for x in rows),
            "provisional_sites_within_5km": sum(x["within_5km"] for x in rows),
            "geometry_exclusions": issues,
            "pair_exclusions": geom_issues,
        }
    frame = pd.DataFrame.from_records(records)
    if frame.empty:
        frame = pd.DataFrame(columns=[
            "site_id", "site_name", "latitude", "longitude", "nearest_glims_id",
            "source_year_early", "source_year_late", "nearest_apparent_ice_loss_m",
            "within_1km", "within_5km", "proximity_not_exact_exposure", "bbox_region"
        ])
    frame = frame.sort_values(["bbox_region","site_id"]).reset_index(drop=True)
    a.out_csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(a.out_csv, index=False)
    result["all_region_site_rows"] = len(frame)
    result["any_site_within_1km"] = int(sum(x["within_1km"] for x in records))
    result["any_site_within_5km"] = int(sum(x["within_5km"] for x in records))
    result["out_csv"] = a.out_csv.name
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": result["status"], "by_region": result["by_region"],
        "all_region_site_rows": result["all_region_site_rows"],
        "any_site_within_5km": result["any_site_within_5km"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
