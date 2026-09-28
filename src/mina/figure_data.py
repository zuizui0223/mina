"""Build manuscript figure data from frozen receipts and frozen-source tables.

This module does not create new ecological endpoints. It regenerates plotting
tables from the same source data and asserts that key quantities reproduce the
frozen result receipts before writing anything.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from itertools import combinations
from pathlib import Path

import numpy as np

from .colony_network import colony_states, transition_rows
from .longterm import canonical_species
from .lter import (
    ISLANDS,
    ISLAND_NAMES,
    annual_growth,
    common_component,
    growth_synchrony,
    island_year_totals,
    load_colony_rows,
)
from .network import (
    ANALYSIS_SITES,
    PRIMARY_ISLAND_SITES,
    breeding_membership,
)

RESULT_FILES = {
    "network": "PALMER_NETWORK_STAGE2_RESULT_V1.json",
    "synchrony": "PALMER_LTER_FIVE_ISLAND_SYNCHRONY_RESULT_V1.json",
    "seaice": "PALMER_SEAICE_HABITAT_MECHANISM_RESULT_V1.json",
    "timescale": "PALMER_SEAICE_TIMESCALE_SEPARATION_RESULT_V1.json",
    "weather": "PALMER_WEATHER_X_HABITAT_MECHANISM_RESULT_V2.json",
    "colony": "PALMER_COLONY_NETWORK_EROSION_RESULT_V1.json",
    "large": "PALMER_LARGE_BREEDING_GROUP_THRESHOLD_RESULT_V1.json",
    "spatial": "PALMER_EXTERNAL_SPATIAL_TRIANGULATION_RESULT_V1.json",
    "neff_perm": "PALMER_NEFF_YEAR_BLOCK_PERMUTATION_RESULT_V1.json",
    "neff_coupling": "PALMER_NEFF_MECHANICAL_COUPLING_RESULT_V1.json",
    "neff_circular": "PALMER_NEFF_CIRCULAR_SHIFT_RESULT_V1.json",
    "neff_circular_coupling": "PALMER_NEFF_CIRCULAR_COUPLING_RESULT_V1.json",
    "hierarchy": "PALMER_HIERARCHICAL_VARIABILITY_RESULT_V1.json",
    "hierarchy_component_audit": "PALMER_HIERARCHY_COMPONENT_COUNT_AUDIT_RESULT_V1.json",
    "hierarchy_count_error": "PALMER_HIERARCHY_COUNT_ERROR_NULL_RESULT_V1.json",
    "breeding_concentration": "PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
}


def _read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_results(results_dir: str | Path) -> dict[str, dict]:
    root = Path(results_dir)
    return {
        key: json.loads((root / name).read_text(encoding="utf-8"))
        for key, name in RESULT_FILES.items()
    }


def _sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _stringify(value: object) -> str | int | float:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ";".join(str(x) for x in value)
    return value  # type: ignore[return-value]


def _write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _stringify(row.get(field)) for field in fields})


def _figure1_sites(
    sites_csv: str | Path,
    species_csv: str | Path,
    site_species_csv: str | Path,
    network: dict,
) -> list[dict[str, object]]:
    sites = {
        row["site_id"]: row
        for row in _read_csv(sites_csv)
        if row.get("site_id") in ANALYSIS_SITES
    }
    if set(sites) != set(ANALYSIS_SITES):
        raise ValueError("figure-1 site table does not contain the frozen seven sites")

    members = breeding_membership(site_species_csv, species_csv)
    output: list[dict[str, object]] = []
    for site_id in ANALYSIS_SITES:
        meta = sites[site_id]
        endpoints = network["abundance_endpoints"].get(site_id, {})
        row: dict[str, object] = {
            "site_id": site_id,
            "site_name": meta["site_name"],
            "site_role": (
                "primary_true_island"
                if site_id in PRIMARY_ISLAND_SITES
                else "non_island_benchmark"
            ),
            "latitude": float(meta["latitude"]),
            "longitude": float(meta["longitude"]),
            "known_breeders": sorted(members.get(site_id, set())),
        }
        for species in ("Adelie", "Chinstrap", "Gentoo"):
            item = endpoints.get(species, {})
            prefix = species.lower()
            row[f"{prefix}_first_year"] = item.get("first_year")
            row[f"{prefix}_first_count"] = item.get("first_count")
            row[f"{prefix}_last_year"] = item.get("last_year")
            row[f"{prefix}_last_count"] = item.get("last_count")
        output.append(row)
    return output


def _figure2_tables(
    census_csv: str | Path,
    synchrony: dict,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, float]]:
    raw = load_colony_rows(census_csv)
    totals = island_year_totals(raw)
    lookup = {
        (int(r["year"]), str(r["island"])): float(r["breeding_pairs"])
        for r in totals
    }
    years = list(range(1991, 2018))
    if any((year, island) not in lookup for year in years for island in ISLANDS):
        raise ValueError("figure-2 requires the frozen complete 1991-2017 five-island panel")

    values = {
        island: np.asarray([lookup[(year, island)] for year in years], dtype=float)
        for island in ISLANDS
    }
    pc = common_component(years, values)
    frozen_pc = float(
        synchrony["common_long_term_component"]["pc1_variance_fraction"]
    )
    if abs(float(pc["pc1_variance_fraction"]) - frozen_pc) > 1e-12:
        raise ValueError("PC1 variance drifted from frozen receipt")

    log_matrix = np.column_stack(
        [np.log1p(values[island]) for island in ISLANDS]
    )
    z = (log_matrix - np.mean(log_matrix, axis=0)) / np.std(
        log_matrix, axis=0, ddof=1
    )
    loadings = np.asarray(
        [float(pc["pc1_loadings"][island]) for island in ISLANDS]
    )
    scores = z @ loadings

    trajectory: list[dict[str, object]] = []
    for j, year in enumerate(years):
        for i, island in enumerate(ISLANDS):
            first = values[island][0]
            count = float(values[island][j])
            trajectory.append(
                {
                    "year": year,
                    "island": island,
                    "island_name": ISLAND_NAMES[island],
                    "breeding_pairs": count,
                    "fraction_of_1991": count / first if first > 0 else None,
                    "log1p_breeding_pairs": math.log1p(count),
                    "standardized_log_abundance": float(z[j, i]),
                    "common_pc1_score": float(scores[j]),
                }
            )

    interval_years, growth = annual_growth(years, values)
    sync = growth_synchrony(growth)
    frozen_median = float(
        synchrony["annual_growth_synchrony"]["median_pairwise_correlation"]
    )
    if abs(float(sync["median_pairwise_correlation"]) - frozen_median) > 1e-12:
        raise ValueError("annual synchrony drifted from frozen receipt")

    pair_rows: list[dict[str, object]] = []
    for a, b in combinations(ISLANDS, 2):
        pair_rows.append(
            {
                "island_a": a,
                "island_b": b,
                "correlation": float(np.corrcoef(growth[a], growth[b])[0, 1]),
                "n_intervals": len(interval_years),
            }
        )
    checks = {
        "pc1_variance_fraction": float(pc["pc1_variance_fraction"]),
        "median_pairwise_growth_correlation": float(
            sync["median_pairwise_correlation"]
        ),
    }
    return trajectory, pair_rows, checks


def _error_row(
    label: str,
    family: str,
    beta: float,
    expected: str,
    baseline_error: float,
    full_error: float,
    metric: str,
    supported: bool,
) -> dict[str, object]:
    observed = "positive" if beta > 0 else "negative" if beta < 0 else "zero"
    gain = baseline_error - full_error
    return {
        "test": label,
        "family": family,
        "coefficient": beta,
        "expected_direction": expected,
        "observed_direction": observed,
        "direction_matches": observed == expected,
        "baseline_error": baseline_error,
        "full_error": full_error,
        "error_metric": metric,
        "absolute_error_gain": gain,
        "relative_error_reduction": gain / baseline_error,
        "decision_supported": supported,
    }


def _figure3_hierarchy(
    hierarchy: dict,
    component_audit: dict,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    primary = hierarchy["primary_raw_abundance"]
    fixed = hierarchy["fixed_raw_sensitivities"]
    raw = [
        {
            "analysis": "Primary 1991-2017 COR/HUM/LIT",
            "beta_within": float(primary["beta_within_islands"]),
            "beta_among": float(primary["beta_among_islands"]),
            "beta_total": float(primary["beta_total_subcolony_to_archipelago"]),
            "within_log_beta_share": float(primary["log_beta_share_within_islands"]),
        },
        {
            "analysis": "Pre-extinction 1991-2006",
            "beta_within": float(
                fixed["pre_litchfield_extinction_1991_2006"]["beta_within_islands"]
            ),
            "beta_among": float(
                fixed["pre_litchfield_extinction_1991_2006"]["beta_among_islands"]
            ),
            "beta_total": float(
                fixed["pre_litchfield_extinction_1991_2006"]["beta_total"]
            ),
            "within_log_beta_share": float(
                fixed["pre_litchfield_extinction_1991_2006"][
                    "log_beta_share_within_islands"
                ]
            ),
        },
        {
            "analysis": "Persistent stable COR/HUM",
            "beta_within": float(
                fixed["persistent_stable_roster_COR_HUM"]["beta_within_islands"]
            ),
            "beta_among": float(
                fixed["persistent_stable_roster_COR_HUM"]["beta_among_islands"]
            ),
            "beta_total": float(
                fixed["persistent_stable_roster_COR_HUM"]["beta_total"]
            ),
            "within_log_beta_share": float(
                fixed["persistent_stable_roster_COR_HUM"][
                    "log_beta_share_within_islands"
                ]
            ),
        },
    ]

    pairwise = []
    source = component_audit["pairwise_mean_correlation"]
    for key, label in (
        ("raw_abundance", "Raw abundance"),
        ("linear_detrended_log1p", "Detrended log1p"),
        ("annual_log1p_growth", "Annual log1p growth"),
    ):
        item = source[key]
        pairwise.append(
            {
                "analysis": label,
                "among_islands": float(item["among_islands"]),
                "COR": float(item["COR"]),
                "HUM": float(item["HUM"]),
                "LIT": float(item["LIT"]),
            }
        )
    return raw, pairwise


def _figure3_count_error(
    receipt: dict,
) -> list[dict[str, object]]:
    labels = (
        ("poisson", "Poisson"),
        ("gamma_poisson_cv10", "Gamma-Poisson CV10%"),
        ("gamma_poisson_cv20", "Gamma-Poisson CV20%"),
    )
    observed = float(receipt["observed"]["raw_log_beta_contrast"])
    rows: list[dict[str, object]] = []
    for key, label in labels:
        item = receipt["error_models"][key]
        rows.append(
            {
                "error_model": key,
                "label": label,
                "multiplicative_cv": (
                    0.0 if key == "poisson"
                    else 0.10 if key.endswith("cv10")
                    else 0.20
                ),
                "observed_log_beta_contrast": observed,
                "null_mean_log_beta_contrast": float(
                    item["raw_log_beta_contrast_null_mean"]
                ),
                "null_q975_log_beta_contrast": float(
                    item["raw_log_beta_contrast_null_q_0_975"]
                ),
                "one_sided_p": float(
                    item["raw_log_beta_contrast_p"]
                ),
                "observed_beta_within": float(
                    receipt["observed"]["raw_beta_within"]
                ),
                "null_mean_beta_within": float(
                    item["raw_beta_within_null_mean"]
                ),
                "null_q975_beta_within": float(
                    item["raw_beta_within_null_q_0_975"]
                ),
                "beta_within_one_sided_p": float(
                    item["raw_beta_within_p"]
                ),
            }
        )
    return rows

def _figure3_concentration(
    census_csv: str | Path,
    receipt: dict,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    states = colony_states(census_csv)
    eligible = ("COR", "HUM", "LIT")
    trajectories: list[dict[str, object]] = []
    first_neff: dict[str, float] = {}
    for island in eligible:
        local = sorted(
            [
                row for row in states
                if str(row["island"]) == island
                and row["effective_colony_number"] is not None
                and float(row["total_breeding_pairs"]) > 0
            ],
            key=lambda row: int(row["year"]),
        )
        if not local:
            raise ValueError(f"no positive N_eff trajectory for {island}")
        first = float(local[0]["effective_colony_number"])
        first_neff[island] = first
        for row in local:
            value = float(row["effective_colony_number"])
            trajectories.append(
                {
                    "island": island,
                    "year": int(row["year"]),
                    "effective_colony_number": value,
                    "relative_to_first": value / first,
                    "breeding_pairs": float(row["total_breeding_pairs"]),
                }
            )

    slopes: list[dict[str, object]] = []
    cv20 = receipt["null_slope_summaries"]["gamma_poisson_cv20"]
    for island in eligible:
        obs = receipt["observed"][island]
        null = cv20[island]
        slopes.append(
            {
                "island": island,
                "observed_slope": float(obs["slope_per_year"]),
                "null_mean_slope_cv20": float(null["mean"]),
                "null_q025_slope_cv20": float(null["q_0_025"]),
                "null_q975_slope_cv20": float(null["q_0_975"]),
                "cv20_one_sided_p": float(null["p"]),
                "first_neff": float(obs["first_neff"]),
                "last_neff": float(obs["last_neff"]),
                "fractional_change": float(obs["fractional_change"]),
            }
        )
    return trajectories, slopes


def _figure3_mechanisms(r: dict[str, dict]) -> list[dict[str, object]]:
    sea = r["seaice"]["primary_result"]
    time = r["timescale"]["primary_K5"]
    weather = r["weather"]
    colony = r["colony"]
    large = r["large"]
    neff_perm = r["neff_perm"]

    base_colony = float(colony["primary"]["loyo"]["c0_mse"])
    active_gain = float(
        colony["sensitivities"]["active_colony_count"]["mse_gain_c0_minus_c1"]
    )
    return [
        _error_row(
            "Annual sea-ice duration",
            "regional marine",
            float(sea["regional_beta_M1"]),
            "positive",
            float(sea["mse"]["M0_island_only"]),
            float(sea["mse"]["M1_plus_seaice"]),
            "MSE",
            bool(sea["decision"]["regional_support"]),
        ),
        _error_row(
            "Five-year sea-ice duration",
            "regional marine",
            float(time["full_fit"]["seaice_beta_T1"]),
            "positive",
            float(time["purged_validation"]["mse_T0"]),
            float(time["purged_validation"]["mse_T1"]),
            "MSE",
            bool(r["timescale"]["decision"]["timescale_separation_supported"]),
        ),
        _error_row(
            "October snowfall x habitat",
            "terrestrial weather",
            float(weather["model"]["full"]["interaction_coefficient"]),
            "negative",
            float(weather["leave_one_year_out"]["null_rmse"]),
            float(weather["leave_one_year_out"]["full_rmse"]),
            "RMSE",
            weather["decision"] == "supported",
        ),
        {
            **_error_row(
                "Effective colony number",
                "internal colony state",
                float(colony["primary"]["full_data_coefficient"]),
                "positive",
                float(colony["primary"]["loyo"]["c0_mse"]),
                float(colony["primary"]["loyo"]["c1_mse"]),
                "MSE",
                False,
            ),
            "permutation_p": float(
                neff_perm["gain_null"]["one_sided_permutation_p"]
            ),
            "diagnostic_note": "held-out gain not unusual under year-block permutation",
        },
        _error_row(
            "Active colony count",
            "specificity",
            float(colony["sensitivities"]["active_colony_count"]["coefficient"]),
            "positive",
            base_colony,
            base_colony - active_gain,
            "MSE",
            active_gain > 0,
        ),
        _error_row(
            ">50-pair group count",
            "external threshold",
            float(large["primary"]["coefficient"]),
            "positive",
            float(large["primary"]["loyo"]["g0_mse"]),
            float(large["primary"]["loyo"]["g1_mse"]),
            "MSE",
            large["primary"]["decision"] == "supported",
        ),
        _error_row(
            ">50-pair breeder fraction",
            "external threshold",
            float(large["fixed_sensitivity"]["coefficient"]),
            "positive",
            float(large["fixed_sensitivity"]["loyo"]["g0_mse"]),
            float(large["fixed_sensitivity"]["loyo"]["g1_mse"]),
            "MSE",
            bool(
                large["fixed_sensitivity"]["directional_prediction_met"]
                and large["fixed_sensitivity"]["predictive_improvement"]
            ),
        ),
    ]


def _baseline_matrix(rows: list[dict[str, object]]) -> np.ndarray:
    x = np.zeros((len(rows), len(ISLANDS)), dtype=float)
    lookup = {name: i for i, name in enumerate(ISLANDS)}
    for j, row in enumerate(rows):
        x[j, lookup[str(row["island"])]] = 1.0

    abundance = np.asarray(
        [math.log1p(float(row["current_total"])) for row in rows]
    )
    year = np.asarray([float(row["start_year"]) for row in rows])
    abundance = (abundance - np.mean(abundance)) / np.std(abundance, ddof=1)
    year = (year - np.mean(year)) / np.std(year, ddof=1)
    return np.column_stack([x, abundance, year])


def _residualize(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    if rank != x.shape[1]:
        raise ValueError("figure residualization baseline is rank deficient")
    return y - x @ beta


def _figure4_tables(
    census_csv: str | Path,
    colony_receipt: dict,
    spatial: dict,
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    float,
]:
    states = colony_states(census_csv)
    transitions = transition_rows(census_csv)
    xbase = _baseline_matrix(transitions)
    y = np.asarray([float(row["next_growth"]) for row in transitions])
    topo = np.asarray(
        [math.log1p(float(row["effective_colony_number"])) for row in transitions]
    )
    topo_z = (topo - np.mean(topo)) / np.std(topo, ddof=1)
    y_resid = _residualize(xbase, y)
    x_resid = _residualize(xbase, topo_z)
    denom = float(x_resid @ x_resid)
    if denom <= 0:
        raise ValueError("zero conditional topology variance")
    slope = float((x_resid @ y_resid) / denom)
    frozen = float(colony_receipt["primary"]["full_data_coefficient"])
    if abs(slope - frozen) > 1e-10:
        raise ValueError(
            f"conditional topology slope drifted: {slope} vs {frozen}"
        )

    transition_rows_out: list[dict[str, object]] = []
    for row, xr, yr, tz in zip(transitions, x_resid, y_resid, topo_z):
        transition_rows_out.append(
            {
                **row,
                "topology_z": float(tz),
                "conditional_topology_residual": float(xr),
                "conditional_growth_residual": float(yr),
            }
        )

    state_rows = [
        {
            **row,
            "effective_fraction_of_reported_rows": (
                float(row["effective_colony_number"])
                / float(row["reported_colony_rows"])
                if row["effective_colony_number"] is not None
                and int(row["reported_colony_rows"]) > 0
                else None
            ),
        }
        for row in states
    ]

    ext = spatial["external_torgersen_spatial"]
    external_rows = [
        {
            "historic_active_subcolonies": ext["historic_active_subcolonies"],
            "active_subcolonies_2022": ext["active_subcolonies_2022"],
            "active_footprint_fraction": ext["active_footprint_fraction"],
            "south_extinction_fraction": ext["south_extinction_fraction"],
            "north_extinction_fraction": ext["north_extinction_fraction"],
            "active_to_extinct_historic_area_ratio": ext[
                "active_to_extinct_historic_area_ratio"
            ],
            "area_extinction_year_correlation_R": ext[
                "area_extinction_year_correlation_R"
            ],
            "area_extinction_year_p": ext["area_extinction_year_p"],
            "identifier_level_validation": spatial["decision"][
                "identifier_level_validation"
            ],
        }
    ]
    return state_rows, transition_rows_out, external_rows, slope


def build(
    census_csv: str | Path,
    sites_csv: str | Path,
    species_csv: str | Path,
    site_species_csv: str | Path,
    results_dir: str | Path,
    out_dir: str | Path,
) -> dict[str, object]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = _load_results(results_dir)

    fig1 = _figure1_sites(
        sites_csv, species_csv, site_species_csv, results["network"]
    )
    fig2, fig2_pairs, checks2 = _figure2_tables(
        census_csv, results["synchrony"]
    )
    fig3_raw, fig3_pairwise = _figure3_hierarchy(
        results["hierarchy"], results["hierarchy_component_audit"]
    )
    fig3_count_error = _figure3_count_error(
        results["hierarchy_count_error"]
    )
    fig3_concentration, fig3_concentration_slopes = _figure3_concentration(
        census_csv, results["breeding_concentration"]
    )
    fig4 = _figure3_mechanisms(results)
    fig5_states, fig5_transitions, fig5_external, topology_slope = (
        _figure4_tables(census_csv, results["colony"], results["spatial"])
    )
    neff_perm_p = float(results["neff_perm"]["gain_null"]["one_sided_permutation_p"])
    circular_independent_p = float(
        results["neff_circular"]["primary_independent_island_circular_shift"]
        ["coefficient_null"]["one_sided_p"]
    )
    circular_joint_p = float(
        results["neff_circular"]["joint_persistent_island_shift_sensitivity"]
        ["coefficient_null"]["exact_one_sided_p"]
    )
    circular_coupling_max_p = max(
        float(
            results["neff_circular_coupling"]["error_models"][name]
            ["coupled_beta"]["one_sided_probability_ge_observed"]
        )
        for name in ("poisson", "gamma_poisson_cv10", "gamma_poisson_cv20")
    )
    fig5_external[0]["neff_gain_permutation_p"] = neff_perm_p
    fig5_external[0]["neff_beta_circular_independent_p"] = circular_independent_p
    fig5_external[0]["neff_beta_circular_joint_p"] = circular_joint_p
    fig5_external[0]["neff_max_circular_coupling_null_p"] = circular_coupling_max_p

    _write_csv(out / "figure1_sites.csv", fig1)
    _write_csv(out / "figure2_trajectories.csv", fig2)
    _write_csv(out / "figure2_pairwise_synchrony.csv", fig2_pairs)
    _write_csv(out / "figure3_hierarchy_raw.csv", fig3_raw)
    _write_csv(out / "figure3_hierarchy_pairwise.csv", fig3_pairwise)
    _write_csv(
        out / "figure3_hierarchy_count_error.csv",
        fig3_count_error,
    )
    _write_csv(
        out / "figure3_concentration_trajectories.csv",
        fig3_concentration,
    )
    _write_csv(
        out / "figure3_concentration_slopes.csv",
        fig3_concentration_slopes,
    )
    _write_csv(out / "figure4_mechanism_audit.csv", fig4)
    _write_csv(out / "figure5_colony_states.csv", fig5_states)
    _write_csv(out / "figure5_colony_transitions.csv", fig5_transitions)
    _write_csv(out / "figure5_external_torgersen.csv", fig5_external)

    manifest = {
        "schema_version": 2,
        "package_id": "mina-manuscript-figure-data-v2",
        "source_fingerprints": {
            "census_sha256": _sha256(census_csv),
            "sites_sha256": _sha256(sites_csv),
            "species_sha256": _sha256(species_csv),
            "site_species_sha256": _sha256(site_species_csv),
            "receipt_files": RESULT_FILES,
        },
        "row_counts": {
            "figure1_sites": len(fig1),
            "figure2_trajectories": len(fig2),
            "figure2_pairwise_synchrony": len(fig2_pairs),
            "figure3_hierarchy_raw": len(fig3_raw),
            "figure3_hierarchy_centered": len(fig3_pairwise),
            "figure3_hierarchy_count_error": len(fig3_count_error),
            "figure3_concentration_trajectories": len(fig3_concentration),
            "figure3_concentration_slopes": len(fig3_concentration_slopes),
            "figure4_mechanism_audit": len(fig4),
            "figure5_colony_states": len(fig5_states),
            "figure5_colony_transitions": len(fig5_transitions),
        },
        "frozen_checks": {
            **checks2,
            "hierarchy_beta_within": float(
                results["hierarchy"]["primary_raw_abundance"]["beta_within_islands"]
            ),
            "hierarchy_beta_among": float(
                results["hierarchy"]["primary_raw_abundance"]["beta_among_islands"]
            ),
            "hierarchy_beta_total": float(
                results["hierarchy"]["primary_raw_abundance"][
                    "beta_total_subcolony_to_archipelago"
                ]
            ),
            "hierarchy_within_log_beta_share": float(
                results["hierarchy"]["primary_raw_abundance"][
                    "log_beta_share_within_islands"
                ]
            ),
            "hierarchy_component_count_audit_pass": bool(
                results["hierarchy_component_audit"]["decision"][
                    "hierarchy_not_explained_only_by_more_within_island_units"
                ]
            ),
            "hierarchy_count_error_robust_all_models": bool(
                results["hierarchy_count_error"]["decision"][
                    "raw_hierarchy_measurement_error_robust"
                ]
            ),
            "hierarchy_count_error_cv20_contrast_p": float(
                results["hierarchy_count_error"]["error_models"][
                    "gamma_poisson_cv20"
                ]["raw_log_beta_contrast_p"]
            ),
            "breeding_concentration_supported": bool(
                results["breeding_concentration"]["decision"][
                    "progressive_concentration_supported_under_all_frozen_error_models"
                ]
            ),
            "breeding_concentration_cv20_joint_p": float(
                results["breeding_concentration"]["cv20"][
                    "joint_three_island_p"
                ]
            ),
            "conditional_effective_colony_slope": topology_slope,
            "effective_colony_gain_permutation_p": neff_perm_p,
            "effective_colony_beta_circular_independent_p": circular_independent_p,
            "effective_colony_beta_circular_joint_p": circular_joint_p,
            "effective_colony_max_circular_coupling_null_p": circular_coupling_max_p,
            "spatial_phenomenon_convergence": bool(
                results["spatial"]["decision"][
                    "phenomenon_level_spatial_convergence"
                ]
            ),
            "spatial_identifier_level_validation": bool(
                results["spatial"]["decision"]["identifier_level_validation"]
            ),
        },
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--census", required=True, type=Path)
    p.add_argument("--sites", required=True, type=Path)
    p.add_argument("--species", required=True, type=Path)
    p.add_argument("--site-species", required=True, type=Path)
    p.add_argument("--results", default=Path("results"), type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    a = p.parse_args()
    manifest = build(
        a.census,
        a.sites,
        a.species,
        a.site_species,
        a.results,
        a.out_dir,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
