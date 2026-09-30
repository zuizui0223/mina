#!/usr/bin/env python3
"""Build only the frozen Figure 1 display tables for JBI v0.5.

This script does not define a new ecological endpoint. It regenerates the five
Palmer island locations and the complete 1991-2017 island-total trajectories,
then verifies the frozen PC1 fraction from the committed Palmer receipt.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from mina.lter import (
    ISLANDS,
    ISLAND_NAMES,
    common_component,
    island_year_totals,
    load_colony_rows,
)

PINNED_MAPPPDR_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"
FOCAL_SITE_NAMES = {
    "Christine Island",
    "Cormorant Island",
    "Humble Island",
    "Litchfield Island",
    "Torgersen Island",
}


def _load_rda(path: Path, expected: str) -> pd.DataFrame:
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


def build(
    census_path: Path,
    mapppdr_dir: Path,
    receipt_path: Path,
    out_dir: Path,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)

    sites = _load_rda(mapppdr_dir / "data" / "sites.rda", "sites")
    focal = sites[sites["site_name"].astype(str).isin(FOCAL_SITE_NAMES)].copy()
    if len(focal) != 5:
        raise ValueError(
            f"expected five Palmer site rows, observed {len(focal)}: "
            f"{sorted(focal['site_name'].astype(str))}"
        )
    required = {"site_id", "site_name", "latitude", "longitude"}
    missing = required - set(focal.columns)
    if missing:
        raise ValueError(f"site metadata missing columns: {sorted(missing)}")
    focal = focal[
        ["site_id", "site_name", "latitude", "longitude"]
    ].sort_values("site_name")
    focal.to_csv(out_dir / "figure1_sites.csv", index=False)

    colony_rows = load_colony_rows(census_path)
    totals = island_year_totals(colony_rows)
    lookup = {
        (int(row["year"]), str(row["island"])): float(row["breeding_pairs"])
        for row in totals
    }
    years = list(range(1991, 2018))
    missing_cells = [
        (year, island)
        for year in years
        for island in ISLANDS
        if (year, island) not in lookup
    ]
    if missing_cells:
        raise ValueError(f"incomplete frozen five-island panel: {missing_cells[:10]}")

    output_rows: list[dict[str, object]] = []
    values: dict[str, np.ndarray] = {}
    for island in ISLANDS:
        series = np.asarray([lookup[(year, island)] for year in years], dtype=float)
        values[island] = series
        for year, count in zip(years, series):
            output_rows.append(
                {
                    "year": year,
                    "island": island,
                    "island_name": ISLAND_NAMES[island],
                    "breeding_pairs": float(count),
                }
            )

    with (out_dir / "figure1_trajectories.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["year", "island", "island_name", "breeding_pairs"],
        )
        writer.writeheader()
        writer.writerows(output_rows)

    pc = common_component(years, values)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    frozen_pc = float(
        receipt["common_long_term_component"]["pc1_variance_fraction"]
    )
    observed_pc = float(pc["pc1_variance_fraction"])
    if abs(observed_pc - frozen_pc) > 1e-12:
        raise ValueError(
            f"PC1 fraction drifted: regenerated={observed_pc}, frozen={frozen_pc}"
        )

    manifest = {
        "schema_version": 1,
        "builder_id": "mina-jbi-v0.5-figure1-display-data",
        "mapppdr_commit": PINNED_MAPPPDR_COMMIT,
        "site_rows": len(focal),
        "trajectory_rows": len(output_rows),
        "years": [1991, 2017],
        "islands": list(ISLANDS),
        "pc1_variance_fraction_verified": observed_pc,
        "new_ecological_endpoint_created": False,
    }
    (out_dir / "figure1_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--mapppdr-dir", required=True, type=Path)
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("results/PALMER_LTER_FIVE_ISLAND_SYNCHRONY_RESULT_V1.json"),
    )
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    result = build(args.census, args.mapppdr_dir, args.receipt, args.out_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
