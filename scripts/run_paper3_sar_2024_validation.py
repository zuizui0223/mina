#!/usr/bin/env python3
"""External 2024 SAR validation of Paper 3 within-season node aliasing."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.compute_emperor_mobile_node_aliasing import summarize

EXPECTED_COLONIES = (
    "Atka Bay",
    "Coulman Island",
    "Cape Roget",
    "Cape Washington",
    "Franklin Island",
    "Cape Crozier",
)


def standardize(raw: pd.DataFrame) -> pd.DataFrame:
    required = {"colony", "image", "xcoord", "ycoord", "b_pres"}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"missing source fields: {sorted(missing)}")

    x = raw.copy()
    x["xcoord"] = pd.to_numeric(x["xcoord"], errors="coerce")
    x["ycoord"] = pd.to_numeric(x["ycoord"], errors="coerce")
    x["b_pres"] = x["b_pres"].astype(str).str.strip().str.lower()

    x = x[
        x["b_pres"].eq("yes")
        & x["xcoord"].notna()
        & x["ycoord"].notna()
    ].copy()

    x["obs_date"] = pd.to_datetime(
        x["image"].astype(str).str.slice(0, 10),
        format="%Y-%m-%d",
        errors="raise",
    )
    x["colony_id"] = x["colony"].astype(str)
    x["season"] = 2024
    x["longitude"] = x["xcoord"].astype(float)
    x["latitude"] = x["ycoord"].astype(float)
    x["group_id"] = np.arange(len(x), dtype=int).astype(str)
    x["source_file"] = x["image"].astype(str)

    unexpected = sorted(set(x["colony_id"]) - set(EXPECTED_COLONIES))
    if unexpected:
        raise ValueError(f"unexpected colony names: {unexpected}")

    out = x[
        [
            "colony_id",
            "season",
            "obs_date",
            "longitude",
            "latitude",
            "group_id",
            "source_file",
        ]
    ].sort_values(["colony_id", "obs_date", "group_id"]).reset_index(drop=True)

    if out.empty:
        raise ValueError("no finite detected huddle centroids")
    return out


def strip_interannual(result: dict) -> dict:
    # This external source is deliberately one-season only.
    result = dict(result)
    alias = {}
    for r, vals in result["aliasing_curve"].items():
        alias[r] = {
            "within_season_false_absence_fraction": vals["within_season_false_absence_fraction"],
            "within_season_false_absence_n": vals["within_season_false_absence_n"],
            "within_season_post_anchor_date_n": vals["within_season_post_anchor_date_n"],
        }
    result["aliasing_curve"] = alias
    result["identity_preserving_radii_km"] = {
        "within_season_min_group_distance": result["identity_preserving_radii_km"][
            "within_season_min_group_distance"
        ]
    }
    result["support"].pop("consecutive_interannual_transitions", None)
    for row in result["by_colony"]:
        row.pop("consecutive_transitions", None)
        row.pop("interannual_q95_km", None)
    result["analysis_id"] = "mina-paper3-sar-2024-within-season-validation-v1"
    result["boundary"] = [
        "This independent SAR source covers one 2024 winter season and is used only for within-season aliasing.",
        "No interannual false-turnover inference is made.",
        "The radius set and minimum-group detection rule were frozen before this source was introduced.",
        "Named colony identity is source-provided and is not demographic closure.",
        "No abundance, breeding success, sea-ice, or other environmental variable enters the calculation.",
    ]
    return result


def add_source_support(result: dict, standardized: pd.DataFrame) -> dict:
    by_colony = []
    for colony, g in standardized.groupby("colony_id", sort=True):
        by_colony.append(
            {
                "colony_id": str(colony),
                "mapped_huddles": int(len(g)),
                "observation_dates": int(g["obs_date"].nunique()),
                "first_detected_date": g["obs_date"].min().date().isoformat(),
                "last_detected_date": g["obs_date"].max().date().isoformat(),
            }
        )
    result["source_support"] = {
        "colonies": int(standardized["colony_id"].nunique()),
        "mapped_huddles": int(len(standardized)),
        "observation_dates_colony_date": int(
            standardized[["colony_id", "obs_date"]].drop_duplicates().shape[0]
        ),
        "by_colony": by_colony,
    }
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--raw-csv", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-standardized-csv", required=True, type=Path)
    p.add_argument("--out-dates-csv", required=True, type=Path)
    args = p.parse_args()

    raw = pd.read_csv(args.raw_csv)
    standardized = standardize(raw)

    full = summarize(standardized)
    dates = full.pop("_dates")
    full.pop("_anchors")
    full.pop("_interannual")
    result = add_source_support(strip_interannual(full), standardized)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    standardized.to_csv(args.out_standardized_csv, index=False)
    dates.to_csv(args.out_dates_csv, index=False)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
