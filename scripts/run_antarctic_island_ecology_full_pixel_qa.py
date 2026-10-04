#!/usr/bin/env python3
"""Full outcome-blind local-pixel QA across the 84 physical-site Paper 2D roster."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import rasterio

try:
    from scripts.audit_antarctic_island_ecology_pixel_qa import (
        AEI_MD5,
    MIN_GOOD_SCENES,
    MIN_SELECTED_SCENES,
    PILOT_SITE_IDS,
    aei_support,
    inspect_scene,
    md5,
    query_features,
    select_scenes,
        summarize_epoch,
    )
except ModuleNotFoundError:
    # When executed as `python scripts/<file>.py`, the scripts directory itself
    # is sys.path[0], so import the sibling module directly.
    from audit_antarctic_island_ecology_pixel_qa import (
        AEI_MD5,
        MIN_GOOD_SCENES,
        MIN_SELECTED_SCENES,
        PILOT_SITE_IDS,
        aei_support,
        inspect_scene,
        md5,
        query_features,
        select_scenes,
        summarize_epoch,
    )


def candidate_sites(optical: pd.DataFrame, options: pd.DataFrame) -> pd.DataFrame:
    static = options[
        ["site_id", "site_name", "mapped_ice_free_pixel_count_2000m"]
    ].drop_duplicates("site_id")
    x = optical.merge(static, on="site_id", how="left", validate="many_to_one")
    x = x[
        x["catalog_gate_pass"].astype(bool)
        & (
            pd.to_numeric(
                x["mapped_ice_free_pixel_count_2000m"], errors="coerce"
            ).fillna(0)
            > 0
        )
    ].copy()
    if len(x) != 103 or x["site_id"].nunique() != 84:
        raise ValueError(
            f"combined candidate roster drift: units={len(x)}, "
            f"sites={x['site_id'].nunique()}"
        )
    x = x.sort_values(["site_id", "early_landsat_n_scenes_le80", "unit_id"])
    reps = x.groupby("site_id", as_index=False).first()
    if len(reps) != 84:
        raise ValueError(f"representative physical-site roster drift: {len(reps)}")
    return reps.sort_values("site_id").reset_index(drop=True)


def shard_sites(frame: pd.DataFrame, shard_index: int, n_shards: int) -> pd.DataFrame:
    if not (0 <= shard_index < n_shards):
        raise ValueError("invalid shard index")
    keep = [i % n_shards == shard_index for i in range(len(frame))]
    return frame.loc[keep].reset_index(drop=True)


def inspect_site(row: dict, aei) -> tuple[dict, list[dict]]:
    support_mask, support_transform, support_crs = aei_support(
        aei, float(row["longitude"]), float(row["latitude"])
    )
    n_aei = int(support_mask.sum())
    if n_aei <= 0:
        raise ValueError("no positive AEI support in frozen 2 km radius")

    scene_records: list[dict] = []
    epoch_results = {}
    for epoch in ("early", "late"):
        start = int(row[f"{epoch}_window_start"])
        end = int(row[f"{epoch}_window_end"])
        features = query_features(
            float(row["longitude"]), float(row["latitude"]), start, end
        )
        selected = select_scenes(features)
        local_rows = []
        for feature in selected:
            base = {
                "site_id": row["site_id"],
                "site_name": row["site_name"],
                "unit_id": row["unit_id"],
                "species_id": row["species_id"],
                "region": row["region"],
                "epoch": epoch,
                "epoch_start": start,
                "epoch_end": end,
                "aei_support_cells_100m": n_aei,
            }
            try:
                rec = {
                    **base,
                    **inspect_scene(
                        feature,
                        support_mask,
                        support_transform,
                        support_crs,
                    ),
                    "read_error": None,
                }
            except Exception as exc:
                dt = feature.get("properties", {}).get("datetime")
                rec = {
                    **base,
                    "item_id": str(feature.get("id")),
                    "date": str(dt)[:10] if dt else None,
                    "year": int(str(dt)[:4]) if dt else None,
                    "scene_cloud_percent": feature.get("properties", {}).get("eo:cloud_cover"),
                    "aei_support_pixels_on_landsat_grid": None,
                    "locally_valid_pixels": None,
                    "locally_valid_fraction": None,
                    "snow_fraction_among_valid": None,
                    "water_fraction_among_valid": None,
                    "local_valid_ge_0_50": False,
                    "read_error": repr(exc),
                }
            scene_records.append(rec)
            local_rows.append(rec)
        epoch_results[epoch] = summarize_epoch(local_rows, len(selected))

    site_pass = bool(epoch_results["early"]["pass"] and epoch_results["late"]["pass"])
    site_record = {
        "site_id": row["site_id"],
        "site_name": row["site_name"],
        "unit_id": row["unit_id"],
        "species_id": row["species_id"],
        "region": row["region"],
        "latitude": float(row["latitude"]),
        "longitude": float(row["longitude"]),
        "aei_support_cells_100m": n_aei,
        "early_window_start": int(row["early_window_start"]),
        "early_window_end": int(row["early_window_end"]),
        "late_window_start": int(row["late_window_start"]),
        "late_window_end": int(row["late_window_end"]),
        "early_selected_scenes": epoch_results["early"]["selected_distinct_year_scenes"],
        "early_successful_reads": epoch_results["early"]["successful_scene_reads"],
        "early_median_valid_fraction": epoch_results["early"]["median_locally_valid_fraction"],
        "early_good_scenes": epoch_results["early"]["scenes_locally_valid_ge_0_50"],
        "early_pass": epoch_results["early"]["pass"],
        "late_selected_scenes": epoch_results["late"]["selected_distinct_year_scenes"],
        "late_successful_reads": epoch_results["late"]["successful_scene_reads"],
        "late_median_valid_fraction": epoch_results["late"]["median_locally_valid_fraction"],
        "late_good_scenes": epoch_results["late"]["scenes_locally_valid_ge_0_50"],
        "late_pass": epoch_results["late"]["pass"],
        "site_pass": site_pass,
        "site_error": None,
    }
    return site_record, scene_records


def audit_shard(
    optical_csv: Path,
    options_csv: Path,
    aei_raster: Path,
    shard_index: int,
    n_shards: int,
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    if md5(aei_raster) != AEI_MD5:
        raise ValueError("AEI raster md5 drift")
    optical = pd.read_csv(optical_csv)
    options = pd.read_csv(options_csv)
    full = candidate_sites(optical, options)
    local = shard_sites(full, shard_index, n_shards)

    site_records = []
    scene_records = []
    with rasterio.open(aei_raster) as aei:
        for row in local.to_dict(orient="records"):
            try:
                site, scenes = inspect_site(row, aei)
            except Exception as exc:
                site = {
                    "site_id": row["site_id"],
                    "site_name": row["site_name"],
                    "unit_id": row["unit_id"],
                    "species_id": row["species_id"],
                    "region": row["region"],
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "early_window_start": int(row["early_window_start"]),
                    "early_window_end": int(row["early_window_end"]),
                    "late_window_start": int(row["late_window_start"]),
                    "late_window_end": int(row["late_window_end"]),
                    "site_pass": False,
                    "site_error": repr(exc),
                }
                scenes = []
            site_records.append(site)
            scene_records.extend(scenes)
            print(
                f"shard {shard_index}/{n_shards} {row['site_id']}: "
                f"pass={site.get('site_pass')} error={site.get('site_error')}",
                flush=True,
            )

    sites = pd.DataFrame(site_records)
    scenes = pd.DataFrame(scene_records)
    result = {
        "schema_version": 1,
        "result_id": f"mina-paper2d-full-pixel-qa-shard-{shard_index}-v1",
        "shard_index": shard_index,
        "n_shards": n_shards,
        "candidate_sites_total": int(len(full)),
        "sites_in_shard": int(len(sites)),
        "site_errors": int(sites["site_error"].notna().sum()) if len(sites) else 0,
        "passing_sites": int(sites["site_pass"].fillna(False).sum()) if len(sites) else 0,
        "scene_read_errors": int(scenes["read_error"].notna().sum()) if len(scenes) else 0,
        "demographic_magnitudes_opened": False,
        "rule": {
            "minimum_selected_scenes_per_epoch": MIN_SELECTED_SCENES,
            "minimum_good_scenes_per_epoch": MIN_GOOD_SCENES,
            "same_as_pilot": True,
        },
    }
    return result, sites, scenes


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--optical-csv", required=True, type=Path)
    p.add_argument("--options-csv", required=True, type=Path)
    p.add_argument("--aei-raster", required=True, type=Path)
    p.add_argument("--shard-index", required=True, type=int)
    p.add_argument("--n-shards", required=True, type=int)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-sites-csv", required=True, type=Path)
    p.add_argument("--out-scenes-csv", required=True, type=Path)
    a = p.parse_args()

    result, sites, scenes = audit_shard(
        a.optical_csv,
        a.options_csv,
        a.aei_raster,
        a.shard_index,
        a.n_shards,
    )
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    sites.to_csv(a.out_sites_csv, index=False)
    scenes.to_csv(a.out_scenes_csv, index=False)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
