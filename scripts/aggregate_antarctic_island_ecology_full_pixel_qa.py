#!/usr/bin/env python3
"""Aggregate full Paper 2D pixel-QA shards and apply the frozen continuation gate."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import pandas as pd


def _read_many(pattern: str) -> pd.DataFrame:
    paths = sorted(glob.glob(pattern))
    if not paths:
        raise ValueError(f"no files match {pattern}")
    frames = [pd.read_csv(p) for p in paths]
    return pd.concat(frames, ignore_index=True, sort=False)


def candidate_units(optical: pd.DataFrame, options: pd.DataFrame) -> pd.DataFrame:
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
            f"candidate unit drift: units={len(x)}, sites={x['site_id'].nunique()}"
        )
    return x


def aggregate(shard_dir: Path, optical_csv: Path, options_csv: Path):
    sites = _read_many(str(shard_dir / "full_pixel_qa_sites_shard*.csv"))
    scenes = _read_many(str(shard_dir / "full_pixel_qa_scenes_shard*.csv"))

    if len(sites) != 84 or sites["site_id"].nunique() != 84:
        raise ValueError(
            f"full site roster drift: rows={len(sites)}, "
            f"unique={sites['site_id'].nunique()}"
        )
    if sites["site_id"].duplicated().any():
        raise ValueError("duplicate physical site across QA shards")

    optical = pd.read_csv(optical_csv)
    options = pd.read_csv(options_csv)
    units = candidate_units(optical, options)
    site_pass = sites.set_index("site_id")["site_pass"].astype(bool)
    site_error = sites.set_index("site_id")["site_error"]

    units["pixel_qa_site_pass"] = units["site_id"].map(site_pass).fillna(False)
    units["pixel_qa_site_error"] = units["site_id"].map(site_error)
    units["full_pixel_qa_eligible"] = (
        units["pixel_qa_site_pass"].astype(bool)
        & units["pixel_qa_site_error"].isna()
    )

    eligible = units[units["full_pixel_qa_eligible"]].copy()
    eligible_sites = set(eligible["site_id"].astype(str))
    eligible_species = sorted(set(eligible["species_id"].astype(str)))

    physical_by_region = (
        sites[sites["site_pass"].astype(bool) & sites["site_error"].isna()]
        .groupby("region")["site_id"]
        .nunique()
        .sort_index()
        .to_dict()
    )
    regional_replication_groups = sorted(
        region for region, n in physical_by_region.items() if int(n) >= 5
    )

    technical_site_errors = int(sites["site_error"].notna().sum())
    scene_read_errors = int(scenes["read_error"].notna().sum()) if "read_error" in scenes else 0

    continuation = bool(
        technical_site_errors == 0
        and len(eligible) >= 30
        and len(eligible_sites) >= 20
        and len(eligible_species) >= 2
        and len(regional_replication_groups) >= 2
    )

    failure_sites = (
        sites.loc[~sites["site_pass"].astype(bool), [
            "site_id", "site_name", "region",
            "early_good_scenes", "early_median_valid_fraction",
            "late_good_scenes", "late_median_valid_fraction",
            "site_error",
        ]]
        .sort_values("site_id")
        .to_dict(orient="records")
    )

    species_summary = {}
    for sp, local in units.groupby("species_id"):
        species_summary[str(sp)] = {
            "candidate_units": int(len(local)),
            "eligible_units": int(local["full_pixel_qa_eligible"].sum()),
            "eligible_fraction": float(local["full_pixel_qa_eligible"].mean()),
            "eligible_distinct_sites": int(
                local.loc[local["full_pixel_qa_eligible"], "site_id"].nunique()
            ),
        }

    result = {
        "schema_version": 1,
        "result_id": "mina-antarctic-island-ecology-paper2d-full-pixel-qa-v1",
        "status": "outcome_blind_full_local_pixel_qa",
        "candidate": {
            "site_species_units": 103,
            "physical_sites": 84,
        },
        "result": {
            "passing_physical_sites": int(
                (sites["site_pass"].astype(bool) & sites["site_error"].isna()).sum()
            ),
            "passing_site_species_units": int(len(eligible)),
            "species": species_summary,
            "passing_physical_sites_by_region": {
                str(k): int(v) for k, v in physical_by_region.items()
            },
            "regional_groups_with_at_least_5_passing_sites": regional_replication_groups,
            "failed_physical_sites": failure_sites,
            "site_level_technical_errors": technical_site_errors,
            "scene_read_errors": scene_read_errors,
        },
        "continuation_gate": {
            "minimum_eligible_site_species_units": 30,
            "minimum_distinct_sites": 20,
            "minimum_species": 2,
            "minimum_regions_with_at_least_5_sites": 2,
            "passed": continuation,
            "habitat_change_classifier_authorized": continuation,
            "demographic_magnitudes_opened": False,
        },
        "boundary": [
            "Pixel-QA support is not habitat change.",
            "Sites failing the frozen local-valid-pixel rule remain excluded; thresholds are not relaxed.",
            "Scene read errors are reported separately from ecological support.",
            "No population magnitude, trend, effective-component number, kappa, or concentration outcome is used."
        ],
    }
    return result, sites.sort_values("site_id"), units.sort_values(["species_id","site_id"]), scenes


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--shard-dir", required=True, type=Path)
    p.add_argument("--optical-csv", required=True, type=Path)
    p.add_argument("--options-csv", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-sites-csv", required=True, type=Path)
    p.add_argument("--out-units-csv", required=True, type=Path)
    p.add_argument("--out-scenes-csv", required=True, type=Path)
    a = p.parse_args()

    result, sites, units, scenes = aggregate(
        a.shard_dir, a.optical_csv, a.options_csv
    )
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    sites.to_csv(a.out_sites_csv, index=False)
    units.to_csv(a.out_units_csv, index=False)
    scenes.to_csv(a.out_scenes_csv, index=False)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
