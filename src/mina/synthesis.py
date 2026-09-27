"""Build a drift-resistant ecological synthesis from frozen mina receipts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FILES = {
    "exploratory": "EXPLORATORY_RESULT_V1.json",
    "network": "PALMER_NETWORK_STAGE2_RESULT_V1.json",
    "synchrony": "PALMER_LTER_FIVE_ISLAND_SYNCHRONY_RESULT_V1.json",
    "seaice": "PALMER_SEAICE_HABITAT_MECHANISM_RESULT_V1.json",
    "timescale": "PALMER_SEAICE_TIMESCALE_SEPARATION_RESULT_V1.json",
    "weather": "PALMER_WEATHER_X_HABITAT_MECHANISM_RESULT_V2.json",
    "colony": "PALMER_COLONY_NETWORK_EROSION_RESULT_V1.json",
    "neff_permutation": "PALMER_NEFF_YEAR_BLOCK_PERMUTATION_RESULT_V1.json",
    "neff_coupling": "PALMER_NEFF_MECHANICAL_COUPLING_RESULT_V1.json",
    "large": "PALMER_LARGE_BREEDING_GROUP_THRESHOLD_RESULT_V1.json",
    "spatial": "PALMER_EXTERNAL_SPATIAL_TRIANGULATION_RESULT_V1.json",
}


def load(results_dir: str | Path) -> dict[str, dict]:
    root = Path(results_dir)
    return {
        key: json.loads((root / name).read_text(encoding="utf-8"))
        for key, name in FILES.items()
    }


def build(results_dir: str | Path) -> dict[str, object]:
    r = load(results_dir)
    sync = r["synchrony"]
    sea = r["seaice"]
    time = r["timescale"]
    weather = r["weather"]
    colony = r["colony"]
    perm = r["neff_permutation"]
    coupling = r["neff_coupling"]
    large = r["large"]
    exploratory = r["exploratory"]
    network = r["network"]
    spatial = r["spatial"]

    if sea["primary_result"]["decision"]["regional_support"] is not False:
        raise ValueError("annual sea-ice decision drifted")
    if time["decision"]["timescale_separation_supported"] is not False:
        raise ValueError("sea-ice timescale decision drifted")
    if weather["decision"] != "not_supported":
        raise ValueError("snowfall x habitat decision drifted")
    if large["primary"]["decision"] != "not_supported":
        raise ValueError("external >50-pair directional decision drifted")
    if spatial["decision"]["phenomenon_level_spatial_convergence"] is not True:
        raise ValueError("external spatial convergence endpoint drifted")
    if spatial["decision"]["identifier_level_validation"] is not False:
        raise ValueError("colony-code crosswalk boundary drifted")
    if perm["decision"]["held_out_gain_unusual"] is not False:
        raise ValueError("N_eff permutation gain decision drifted")
    if perm["decision"]["coefficient_unusual"] is not True:
        raise ValueError("N_eff coefficient permutation decision drifted")
    if coupling["decision"]["observed_beta_unusual_under_all_coupled_nulls"] is not True:
        raise ValueError("N_eff mechanical-coupling decision drifted")

    endpoint_fractions = {
        island: float(row["fraction_remaining"])
        for island, row in sync["endpoints"].items()
    }

    coupled_p = {
        model: float(values["coupled_beta"]["one_sided_probability_ge_observed"])
        for model, values in coupling["error_models"].items()
    }
    paired_bias_fraction = {
        model: float(
            values["paired_coupling_bias"]["median_fraction_of_observed_beta"]
        )
        for model, values in coupling["error_models"].items()
    }

    return {
        "schema_version": 3,
        "synthesis_id": "mina-palmer-island-ecology-synthesis-v3",
        "core_claim": (
            "Five neighboring Adelie breeding islands share a strong long-term decline "
            "but differ in annual dynamics and local extinction. The common low-frequency "
            "component is descriptive rather than mechanistically diagnostic. Predeclared "
            "sea-ice-duration and snowfall formulations fail their directional validation "
            "tests. Effective colony number shows a positive conditional association with "
            "next-year growth that survives fixed year-block and stylized count-error "
            "diagnostics, but its small held-out-year MSE improvement is not unusual under "
            "year-block permutation and is therefore not robust predictive evidence."
        ),
        "origin": {
            "role": "supplementary motivation only; not part of the core manuscript argument",
            "pooled_morphology_gain": exploratory["frozen_odsp_context"][
                "naive_pooled_morphology_gain"
            ],
            "species_layer_gain": exploratory["frozen_odsp_context"][
                "species_layer_gain"
            ],
            "species_conditioned_morphology_gain": exploratory["frozen_odsp_context"][
                "species_conditioned_morphology_gain"
            ],
        },
        "assembly_endpoints": {
            "litchfield_local_extinction": network["abundance_endpoints"]["LITC"]["Adelie"],
            "biscoe_benchmark_adélie": network["abundance_endpoints"]["BISC"]["Adelie"],
            "biscoe_benchmark_gentoo": network["abundance_endpoints"]["BISC"]["Gentoo"],
            "biscoe_functional_reassembly": network["benchmark_functional_reassembly"],
        },
        "five_island_decline": {
            "n_years": sync["synchronized_panel"]["n_years"],
            "pc1_variance_fraction": sync["common_long_term_component"][
                "pc1_variance_fraction"
            ],
            "median_annual_growth_correlation": sync["annual_growth_synchrony"][
                "median_pairwise_correlation"
            ],
            "unique_year_fraction": sync["additive_decomposition"][
                "unique_year_fraction"
            ],
            "unique_island_fraction": sync["additive_decomposition"][
                "unique_island_fraction"
            ],
            "residual_fraction": sync["additive_decomposition"]["residual_fraction"],
            "endpoint_fraction_remaining": endpoint_fractions,
            "interpretation": (
                "descriptive scale decomposition; a high common component is expected "
                "for strongly declining series and is not itself a novel synchrony result"
            ),
        },
        "prospective_mechanism_tests": {
            "annual_seaice_duration": {
                "gain": sea["primary_result"]["predictive_gain_M0_minus_M1"],
                "beta": sea["primary_result"]["regional_beta_M1"],
                "supported": sea["primary_result"]["decision"]["regional_support"],
            },
            "five_year_seaice_duration": {
                "gain": time["primary_K5"]["purged_validation"]["gain_T0_minus_T1"],
                "beta": time["primary_K5"]["full_fit"]["seaice_beta_T1"],
                "supported": time["decision"]["timescale_separation_supported"],
            },
            "october_snow_x_habitat": {
                "loyo_rmse_change_full_minus_null": weather["leave_one_year_out"][
                    "rmse_change_full_minus_null"
                ],
                "interaction_beta": weather["model"]["full"][
                    "interaction_coefficient"
                ],
                "supported": weather["decision"] == "supported",
            },
        },
        "local_colony_state": {
            "effective_colony_number": {
                "gain": colony["primary"]["loyo"]["mse_gain_c0_minus_c1"],
                "beta": colony["primary"]["full_data_coefficient"],
                "original_decision": colony["primary"]["decision"],
                "year_block_permutation": {
                    "gain_p": perm["gain_null"]["one_sided_permutation_p"],
                    "gain_observed_percentile": perm["gain_null"]["observed_percentile"],
                    "gain_null_q95": perm["gain_null"]["q_0_95"],
                    "coefficient_p": perm["coefficient_null"][
                        "one_sided_permutation_p"
                    ],
                },
                "mechanical_coupling": {
                    "coupled_beta_p": coupled_p,
                    "median_bias_fraction_of_observed_beta": paired_bias_fraction,
                },
                "robust_predictive_gain": False,
                "conditional_association_survives_fixed_diagnostics": True,
            },
            "active_colony_count": {
                "gain": colony["sensitivities"]["active_colony_count"][
                    "mse_gain_c0_minus_c1"
                ],
                "beta": colony["sensitivities"]["active_colony_count"]["coefficient"],
            },
            "external_gt50_group_count": {
                "gain": large["primary"]["loyo"]["mse_gain_g0_minus_g1"],
                "beta": large["primary"]["coefficient"],
                "directional_supported": large["primary"]["decision"] == "supported",
            },
            "external_gt50_group_fraction": {
                "gain": large["fixed_sensitivity"]["loyo"]["mse_gain_g0_minus_g1"],
                "beta": large["fixed_sensitivity"]["coefficient"],
            },
            "external_spatial_triangulation": {
                "phenomenon_level_convergence": spatial["decision"][
                    "phenomenon_level_spatial_convergence"
                ],
                "identifier_level_validation": spatial["decision"][
                    "identifier_level_validation"
                ],
                "torgersen_active_footprint_fraction": spatial[
                    "external_torgersen_spatial"
                ]["active_footprint_fraction"],
                "south_extinction_fraction": spatial["external_torgersen_spatial"][
                    "south_extinction_fraction"
                ],
                "north_extinction_fraction": spatial["external_torgersen_spatial"][
                    "north_extinction_fraction"
                ],
            },
        },
        "terminal_interpretation": {
            "regional": (
                "Long-term common decline and moderate annual synchrony are a "
                "timescale-dependent descriptive pattern consistent with established "
                "spatial-synchrony theory; they do not identify a new synchrony mechanism."
            ),
            "mechanism": (
                "The tested sea-ice-duration and annual snowfall formulations do not "
                "prospectively explain the observed demographic variation in their "
                "predeclared directions."
            ),
            "local": (
                "Effective colony number has a positive conditional association with "
                "next-year growth, but the +0.00103 held-out MSE gain is compatible with "
                "the frozen year-block permutation null (p≈0.262)."
            ),
            "measurement_boundary": (
                "The observed N_eff coefficient remains unusual under the predeclared "
                "Poisson and 10%/20% Gamma-Poisson mechanical-coupling simulations, "
                "but these are stylized sensitivities rather than calibrated observer-error models."
            ),
            "external_triangulation": (
                "Independent Torgersen mapping demonstrates real habitat-structured "
                "sub-colony attrition at the phenomenon level."
            ),
            "causal_boundary": (
                "No one-to-one LTER colony_code to GIS-polygon crosswalk is available, "
                "so causal habitat-fragmentation and identifier-level validation remain out of scope."
            ),
        },
        "submission_status": {
            "jae": "hold",
            "reason": (
                "the sole positive held-out predictive claim failed the frozen "
                "year-block uncertainty diagnostic"
            ),
        },
    }


def markdown(x: dict[str, object]) -> str:
    d = x["five_island_decline"]
    m = x["prospective_mechanism_tests"]
    c = x["local_colony_state"]
    n = c["effective_colony_number"]
    endpoints = d["endpoint_fraction_remaining"]
    spatial = c["external_spatial_triangulation"]

    return f"""# Palmer island-ecology synthesis v3

## What remains robust

Across 27 synchronized census years, the five islands share a strong low-frequency
decline. PC1 explains **{100*d["pc1_variance_fraction"]:.1f}%** of standardized
log-abundance variation, while median annual-growth correlation is
**{d["median_annual_growth_correlation"]:.3f}**. This is a descriptive
timescale contrast, not the novelty claim.

By 2017, the fraction of 1991 abundance remaining is Christine
**{100*endpoints["CHR"]:.1f}%**, Cormorant **{100*endpoints["COR"]:.1f}%**,
Humble **{100*endpoints["HUM"]:.1f}%**, Litchfield
**{100*endpoints["LIT"]:.1f}%**, and Torgersen **{100*endpoints["TOR"]:.1f}%**.

## Finite mechanism tests

- Annual sea-ice duration: held-out gain **{m["annual_seaice_duration"]["gain"]:+.4f}**,
  beta **{m["annual_seaice_duration"]["beta"]:+.3f}**; predeclared positive
  mechanism not supported.
- Five-year sea-ice duration: purged gain
  **{m["five_year_seaice_duration"]["gain"]:+.4f}**, beta
  **{m["five_year_seaice_duration"]["beta"]:+.3f}**; timescale rescue not supported.
- October snowfall × habitat: LOYO RMSE full-minus-null
  **{m["october_snow_x_habitat"]["loyo_rmse_change_full_minus_null"]:+.4f}**,
  interaction beta **{m["october_snow_x_habitat"]["interaction_beta"]:+.3f}**;
  directional interaction not supported.

## N_eff after uncertainty diagnostics

The original standardized coefficient is **{n["beta"]:+.4f}** and the original
held-out MSE gain is **{n["gain"]:+.6f}**. These no longer support one combined
“predictive” claim.

- Year-block permutation p for the held-out gain:
  **{n["year_block_permutation"]["gain_p"]:.3f}**; the gain is not unusual.
- Year-block permutation p for the full-data coefficient:
  **{n["year_block_permutation"]["coefficient_p"]:.5f}**.
- Coupled-null probabilities of a coefficient at least as large as observed are
  Poisson **{n["mechanical_coupling"]["coupled_beta_p"]["poisson"]:.4f}**,
  CV10% **{n["mechanical_coupling"]["coupled_beta_p"]["gamma_poisson_cv10"]:.4f}**,
  and CV20% **{n["mechanical_coupling"]["coupled_beta_p"]["gamma_poisson_cv20"]:.4f}**.

Therefore N_eff is retained only as a conditional same-census association that
survives the fixed diagnostics. It is **not** retained as robust held-out-year
predictive evidence.

## External spatial evidence

Independent mapped Torgersen footprints retain only
**{100*spatial["torgersen_active_footprint_fraction"]:.1f}%** of the historic
active sub-colony count by 2022. This is phenomenon-level spatial triangulation,
not validation of the exact LTER colony-code metric.

## Submission consequence

The JAE package is on hold. The manuscript must be reframed around a bounded
multi-scale Palmer case study and the distinction between association and
prediction, with synchrony placed explicitly in the established Moran-effect /
timescale-dependent synchrony literature.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=Path("results"))
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()
    x = build(args.results)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(x, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.out_md.write_text(markdown(x), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
