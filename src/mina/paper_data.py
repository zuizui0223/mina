"""Build manuscript-ready figure/table data from frozen receipts and LTER census."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

from .colony_network import colony_states
from .lter import ISLANDS, ISLAND_NAMES, island_year_totals, load_colony_rows
from .synthesis import load as load_receipts


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build(results_dir: str | Path, census_path: str | Path, out_dir: str | Path) -> dict[str, object]:
    receipts = load_receipts(results_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    totals = island_year_totals(load_colony_rows(census_path))
    by_island: dict[str, list[dict[str, object]]] = {island: [] for island in ISLANDS}
    for row in totals:
        by_island[str(row["island"])].append(row)

    trajectory_rows: list[dict[str, object]] = []
    for island in ISLANDS:
        local = sorted(by_island[island], key=lambda row: int(row["year"]))
        log_values = np.asarray([math.log1p(float(row["breeding_pairs"])) for row in local])
        mean = float(np.mean(log_values))
        sd = float(np.std(log_values, ddof=1))
        for row, log_value in zip(local, log_values):
            trajectory_rows.append({
                "year": int(row["year"]),
                "island": island,
                "island_name": ISLAND_NAMES[island],
                "breeding_pairs": float(row["breeding_pairs"]),
                "log1p_breeding_pairs": float(log_value),
                "standardized_log1p": (float(log_value) - mean) / sd,
            })
    _write_csv(
        out / "figure2_five_island_trajectories.csv",
        trajectory_rows,
        ["year", "island", "island_name", "breeding_pairs", "log1p_breeding_pairs", "standardized_log1p"],
    )

    sync = receipts["synchrony"]
    endpoint_rows = []
    for island in ISLANDS:
        row = sync["endpoints"][island]
        endpoint_rows.append({
            "island": island,
            "island_name": row["name"],
            "first_count_1991": row["first_count"],
            "last_count_2017": row["last_count"],
            "fraction_remaining": row["fraction_remaining"],
            "first_zero_year": row.get("first_zero_year", ""),
            "linear_annual_multiplicative_change": sync["trend_slopes_annual_multiplicative_change"][island],
        })
    _write_csv(
        out / "table1_island_endpoints.csv",
        endpoint_rows,
        ["island", "island_name", "first_count_1991", "last_count_2017", "fraction_remaining", "first_zero_year", "linear_annual_multiplicative_change"],
    )

    sea = receipts["seaice"]
    timescale = receipts["timescale"]
    weather = receipts["weather"]
    colony = receipts["colony"]
    large = receipts["large"]
    mechanism_rows = [
        {
            "test_id": "annual_seaice_duration",
            "ecological_scale": "regional marine",
            "predictor": "preceding sea-ice season duration",
            "expected_direction": "positive",
            "coefficient": sea["primary_result"]["regional_beta_M1"],
            "heldout_gain": sea["primary_result"]["predictive_gain_M0_minus_M1"],
            "gain_metric": "MSE reduction",
            "direction_met": False,
            "supported": False,
        },
        {
            "test_id": "five_year_seaice_duration",
            "ecological_scale": "regional marine",
            "predictor": "trailing 5-year sea-ice duration",
            "expected_direction": "positive",
            "coefficient": timescale["primary_K5"]["full_fit"]["seaice_beta_T1"],
            "heldout_gain": timescale["primary_K5"]["purged_validation"]["gain_T0_minus_T1"],
            "gain_metric": "purged MSE reduction",
            "direction_met": False,
            "supported": False,
        },
        {
            "test_id": "october_snow_x_habitat",
            "ecological_scale": "terrestrial weather x island filter",
            "predictor": "October snow days x suboptimal habitat",
            "expected_direction": "negative interaction",
            "coefficient": weather["model"]["full"]["interaction_coefficient"],
            "heldout_gain": -weather["leave_one_year_out"]["rmse_change_full_minus_null"],
            "gain_metric": "RMSE reduction",
            "direction_met": weather["model"]["directional_prediction_met"],
            "supported": False,
        },
        {
            "test_id": "effective_colony_number",
            "ecological_scale": "within-island breeding network",
            "predictor": "log1p effective colony number",
            "expected_direction": "positive",
            "coefficient": colony["primary"]["full_data_coefficient"],
            "heldout_gain": colony["primary"]["loyo"]["mse_gain_c0_minus_c1"],
            "gain_metric": "MSE reduction",
            "direction_met": colony["primary"]["full_data_coefficient"] > 0,
            "supported": colony["primary"]["decision"] == "supported",
        },
        {
            "test_id": "active_colony_count",
            "ecological_scale": "within-island breeding network",
            "predictor": "log1p active positive-colony count",
            "expected_direction": "positive",
            "coefficient": colony["sensitivities"]["active_colony_count"]["coefficient"],
            "heldout_gain": colony["sensitivities"]["active_colony_count"]["mse_gain_c0_minus_c1"],
            "gain_metric": "MSE reduction",
            "direction_met": colony["sensitivities"]["active_colony_count"]["coefficient"] > 0,
            "supported": False,
        },
        {
            "test_id": "external_gt50_pair_groups",
            "ecological_scale": "within-island breeding groups",
            "predictor": "log1p count of >50-pair groups",
            "expected_direction": "positive",
            "coefficient": large["primary"]["coefficient"],
            "heldout_gain": large["primary"]["loyo"]["mse_gain_g0_minus_g1"],
            "gain_metric": "MSE reduction",
            "direction_met": large["primary"]["directional_prediction_met"],
            "supported": False,
        },
    ]
    _write_csv(
        out / "figure3_prospective_mechanism_tests.csv",
        mechanism_rows,
        ["test_id", "ecological_scale", "predictor", "expected_direction", "coefficient", "heldout_gain", "gain_metric", "direction_met", "supported"],
    )

    state_rows = []
    for row in colony_states(census_path):
        state_rows.append({
            "year": row["year"],
            "island": row["island"],
            "island_name": ISLAND_NAMES[str(row["island"])],
            "total_breeding_pairs": row["total"],
            "reported_colony_rows": row["reported_colony_rows"],
            "active_positive_colonies": row["active_positive_colonies"],
            "effective_colony_number": row["effective_colony_number"] if row["effective_colony_number"] is not None else "",
            "largest_colony_share": row["largest_colony_share"] if row["largest_colony_share"] is not None else "",
        })
    _write_csv(
        out / "figure4_colony_network_state.csv",
        state_rows,
        ["year", "island", "island_name", "total_breeding_pairs", "reported_colony_rows", "active_positive_colonies", "effective_colony_number", "largest_colony_share"],
    )

    network = receipts["network"]
    assembly_rows = []
    for site, species_rows in network["abundance_endpoints"].items():
        role = species_rows.get("role", "primary_true_island")
        for species in ("Adelie", "Chinstrap", "Gentoo"):
            if species not in species_rows:
                continue
            r = species_rows[species]
            assembly_rows.append({
                "site": site,
                "site_role": role,
                "species": species,
                "first_year": r.get("first_year", ""),
                "first_count": r.get("first_count", ""),
                "last_year": r.get("last_year", ""),
                "last_count": r.get("last_count", ""),
                "fraction_remaining": r.get("fraction_remaining", ""),
                "fold_change": r.get("fold_change", ""),
            })
    _write_csv(
        out / "supplement_assembly_endpoints.csv",
        assembly_rows,
        ["site", "site_role", "species", "first_year", "first_count", "last_year", "last_count", "fraction_remaining", "fold_change"],
    )

    manifest = {
        "schema_version": 1,
        "paper_data_id": "mina-palmer-paper-data-v0.1",
        "files": [
            "figure2_five_island_trajectories.csv",
            "figure3_prospective_mechanism_tests.csv",
            "figure4_colony_network_state.csv",
            "table1_island_endpoints.csv",
            "supplement_assembly_endpoints.csv",
        ],
        "source_census_sha256": sync["source"]["downloaded_sha256"],
        "frozen_result_ids": {key: value["result_id"] for key, value in receipts.items()},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--results", type=Path, default=Path("results"))
    p.add_argument("--census", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()
    manifest = build(args.results, args.census, args.out_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
