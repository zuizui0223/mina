#!/usr/bin/env python3
"""Build integrated manuscript v0.3 figure-data tables from frozen receipts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def build(root: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)

    concentration = load(
        root, "results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json"
    )
    lag = load(
        root, "results/PALMER_PERFORMANCE_REDISTRIBUTION_LAGS_RESULT_V2.json"
    )
    repro = load(
        root, "results/PALMER_REPRO_REDISTRIBUTION_RESULT_V1.json"
    )
    same = load(
        root, "results/PALMER_REPRO_SAME_PANEL_METRIC_DIAGNOSTIC_RESULT_V1.json"
    )
    memory = load(
        root, "results/PALMER_PERFORMANCE_MEMORY_RESULT_V1.json"
    )

    p2 = load(root, "results/PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json")
    scale = load(root, "results/PAPER2_SCALE_TRAIT_SENSITIVITY_RESULT_V1.json")
    mde = load(root, "results/PAPER2_DETECTABLE_EFFECT_RESULT_V1.json")
    radius = load(root, "results/PAPER2_RADIUS_SIGN_SWITCH_NULL_RESULT_V1.json")
    real = load(root, "results/PAPER2_FIRST_REAL_V3_FIT_RESULT_V1.json")

    # Figure 2A: concentration.
    rows = []
    name_map = {"COR": "Cormorant", "HUM": "Humble", "LIT": "Litchfield"}
    for code, name in name_map.items():
        obs = concentration["observed"][code]
        cv20 = concentration["null_slope_summaries"]["gamma_poisson_cv20"][code]
        rows.append(
            {
                "island_code": code,
                "island": name,
                "first_neff": obs["first_neff"],
                "last_neff": obs["last_neff"],
                "fractional_change": obs["fractional_change"],
                "observed_slope_per_year": obs["slope_per_year"],
                "cv20_null_mean_slope": cv20["mean"],
                "cv20_q025": cv20["q_0_025"],
                "cv20_q975": cv20["q_0_975"],
                "cv20_p": cv20["p"],
            }
        )
    pd.DataFrame(rows).to_csv(
        out_dir / "figure2a_palmer_concentration.csv", index=False
    )

    # Figure 2B: frozen lag profile.
    lag_rows = []
    for k in range(1, 6):
        item = lag["primary_lag_profile"][f"lag_{k}"]
        lag_rows.append(
            {
                "lag_years": k,
                "n_rows": item["n_rows"],
                "beta": item["beta"],
                "one_sided_p": item["one_sided_upper_p"],
                "mechanically_coupled": k == 1,
                "primary_bias_resistant": k == 2,
                "fixed_specification_validation": True,
                "fully_preregistered_confirmatory": False,
            }
        )
    pd.DataFrame(lag_rows).to_csv(
        out_dir / "figure2b_palmer_lag_profile.csv", index=False
    )
    pd.DataFrame(
        [
            {
                "contrast": "mean_beta_45_minus_mean_beta_23",
                "observed": lag["delayed_recruitment_echo"][
                    "contrast_mean_beta45_minus_mean_beta23"
                ],
                "null_q025": lag["delayed_recruitment_echo"][
                    "null_95_interval"
                ][0],
                "null_q975": lag["delayed_recruitment_echo"][
                    "null_95_interval"
                ][1],
                "one_sided_p": lag["delayed_recruitment_echo"][
                    "one_sided_upper_p"
                ],
                "supported": lag["delayed_recruitment_echo"]["supported"],
            }
        ]
    ).to_csv(out_dir / "figure2b_recruitment_echo.csv", index=False)

    # Figure 2C: independent REPRO test plus explicitly post-hoc same-panel diagnostic.
    validation_rows = [
        {
            "estimate_id": "REPRO mean creched chicks/nest, lag 1",
            "source": "frozen_REPRO_primary",
            "beta": repro["primary_lag1"]["beta"],
            "one_sided_p": repro["primary_lag1"]["one_sided_upper_p"],
            "null_q025": repro["primary_lag1"]["null_95_interval"][0],
            "null_q975": repro["primary_lag1"]["null_95_interval"][1],
            "inference_role": "primary_independent_validation",
            "supported": repro["primary_lag1"]["supported"],
        },
        {
            "estimate_id": "REPRO mean creched chicks/nest, lag 2",
            "source": "frozen_REPRO_secondary",
            "beta": repro["secondary_lag2"]["beta"],
            "one_sided_p": repro["secondary_lag2"]["one_sided_upper_p"],
            "null_q025": repro["secondary_lag2"]["null_95_interval"][0],
            "null_q975": repro["secondary_lag2"]["null_95_interval"][1],
            "inference_role": "secondary",
            "supported": repro["secondary_lag2"]["supported"],
        },
        {
            "estimate_id": "REPRO any-creche sensitivity",
            "source": "frozen_REPRO_sensitivity",
            "beta": repro["sensitivities"]["binary_any_creche"]["beta"],
            "one_sided_p": repro["sensitivities"]["binary_any_creche"][
                "one_sided_upper_p"
            ],
            "null_q025": None,
            "null_q975": None,
            "inference_role": "sensitivity_cannot_rescue_primary",
            "supported": repro["sensitivities"]["binary_any_creche"][
                "supported_on_its_own"
            ],
        },
        {
            "estimate_id": "Common-panel colony-wide state",
            "source": "posthoc_same_panel_diagnostic",
            "beta": same["single_predictor_coefficients"][
                "colony_wide_chick_state"
            ],
            "one_sided_p": same["posthoc_common_panel_permutation"][
                "colony_wide_chick_state"
            ]["one_sided_upper_p"],
            "null_q025": same["posthoc_common_panel_permutation"][
                "colony_wide_chick_state"
            ]["null_95_interval"][0],
            "null_q975": same["posthoc_common_panel_permutation"][
                "colony_wide_chick_state"
            ]["null_95_interval"][1],
            "inference_role": "posthoc_diagnostic_only",
            "supported": None,
        },
        {
            "estimate_id": "Common-panel mean nest success",
            "source": "posthoc_same_panel_diagnostic",
            "beta": same["single_predictor_coefficients"][
                "mean_creched_chicks_per_nest"
            ],
            "one_sided_p": same["posthoc_common_panel_permutation"][
                "mean_creched_chicks_per_nest"
            ]["one_sided_upper_p"],
            "null_q025": same["posthoc_common_panel_permutation"][
                "mean_creched_chicks_per_nest"
            ]["null_95_interval"][0],
            "null_q975": same["posthoc_common_panel_permutation"][
                "mean_creched_chicks_per_nest"
            ]["null_95_interval"][1],
            "inference_role": "posthoc_diagnostic_only",
            "supported": None,
        },
    ]
    pd.DataFrame(validation_rows).to_csv(
        out_dir / "figure2c_palmer_metric_validation.csv", index=False
    )

    # Supplementary/local-history diagnostic table.
    memory_rows = []
    for k in (1, 2, 3):
        item = memory["performance_memory"][f"lag_{k}"]
        memory_rows.append(
            {
                "statistic": f"state_memory_lag_{k}",
                "estimate": item["rho"],
                "one_sided_p": item["one_sided_upper_p"],
                "supported": item["supported"],
            }
        )
    memory_rows.append(
        {
            "statistic": "bridge_delta_past",
            "estimate": memory["bridge_diagnostic"]["delta_past"],
            "one_sided_p": memory["bridge_diagnostic"]["one_sided_upper_p"],
            "supported": memory["bridge_diagnostic"]["supported"],
        }
    )
    pd.DataFrame(memory_rows).to_csv(
        out_dir / "supp_palmer_state_memory_bridge.csv", index=False
    )

    # Figure 3A: species effects.
    rows = []
    for sp in ("ADPE", "CHPE", "GEPE"):
        pt = real["primary"][sp]
        inf = p2["species"][sp]
        rows.append(
            {
                "species_id": sp,
                "gamma_a": pt["gamma_a"],
                "gamma_h": pt["gamma_h"],
                "gamma_ah": pt["gamma_ah"],
                "low_area_H_slope": pt["low_area_H_slope"],
                "high_area_H_slope": pt["high_area_H_slope"],
                "crossover_classification": pt["crossover_classification"],
                "raw_p_value": inf["raw_p_value"],
                "holm_p_value": inf["holm_p_value"],
            }
        )
    pd.DataFrame(rows).to_csv(
        out_dir / "figure3_species_interactions.csv", index=False
    )

    # Figure 3B: paper-level observed statistic + frozen permutation quantiles.
    pd.DataFrame(
        [
            {
                "observed_median_gamma_ah": p2["primary"]["observed"],
                "permutation_p": p2["primary"]["p_value"],
                "null_q01": p2["primary"]["permutation_distribution"]["q01"],
                "null_q05": p2["primary"]["permutation_distribution"]["q05"],
                "null_median": p2["primary"]["permutation_distribution"]["median"],
                "null_q95": p2["primary"]["permutation_distribution"]["q95"],
                "null_q99": p2["primary"]["permutation_distribution"]["q99"],
            }
        ]
    ).to_csv(out_dir / "figure3_paper_level_null.csv", index=False)

    # Figure 4A: radius/metric sensitivity.
    scale_rows = [
        {
            "variant": "1 km richness",
            "radius_m": 1000,
            "metric": "tier2_richness",
            "median_gamma_ah": scale["variants"]["radius_1000m"][
                "cross_species_median_gamma_ah"
            ],
            "negative_species": scale["variants"]["radius_1000m"][
                "negative_species"
            ],
        },
        {
            "variant": "2 km richness (primary)",
            "radius_m": 2000,
            "metric": "tier2_richness",
            "median_gamma_ah": scale["primary_reference"][
                "cross_species_median_gamma_ah"
            ],
            "negative_species": 3,
        },
        {
            "variant": "5 km richness",
            "radius_m": 5000,
            "metric": "tier2_richness",
            "median_gamma_ah": scale["variants"]["radius_5000m"][
                "cross_species_median_gamma_ah"
            ],
            "negative_species": scale["variants"]["radius_5000m"][
                "negative_species"
            ],
        },
        {
            "variant": "2 km Shannon",
            "radius_m": 2000,
            "metric": "tier2_shannon",
            "median_gamma_ah": scale["variants"]["shannon_2000m"][
                "cross_species_median_gamma_ah"
            ],
            "negative_species": scale["variants"]["shannon_2000m"][
                "negative_species"
            ],
        },
    ]
    pd.DataFrame(scale_rows).to_csv(
        out_dir / "figure4_scale_sensitivity.csv", index=False
    )

    # Figure 4B: detectable effect curve.
    mde_rows = []
    for item in mde["effects"]:
        mde_rows.append(
            {
                "truth_gamma_ah": item["truth_gamma_ah"],
                "abs_truth_gamma_ah": abs(item["truth_gamma_ah"]),
                "detection_fraction": item["detection_fraction"],
                "wilson_low": item["wilson95"][0],
                "wilson_high": item["wilson95"][1],
                "median_fitted_gamma_ah": item["median_fitted"],
            }
        )
    pd.DataFrame(mde_rows).to_csv(
        out_dir / "figure4_detectable_effect.csv", index=False
    )

    manifest = {
        "schema_version": 2,
        "manuscript": "docs/MANUSCRIPT_INTEGRATED_V0_3.md",
        "figure1": {
            "source": "existing frozen Palmer map and 1991-2017 trajectory package",
            "note": "No new data derivation.",
        },
        "figure2": {
            "concentration": "figure2a_palmer_concentration.csv",
            "lag_profile": "figure2b_palmer_lag_profile.csv",
            "recruitment_echo": "figure2b_recruitment_echo.csv",
            "metric_validation": "figure2c_palmer_metric_validation.csv",
            "memory_supplement": "supp_palmer_state_memory_bridge.csv",
            "joint_concentration_cv20_p": concentration["cv20"][
                "joint_three_island_p"
            ],
            "lag2_beta": lag["primary_lag_profile"]["lag_2"]["beta"],
            "lag2_p": lag["primary_lag_profile"]["lag_2"][
                "one_sided_upper_p"
            ],
            "repro_primary_supported": repro["decision"][
                "independent_nest_validation_supported"
            ],
            "same_panel_state_vs_mean_nest_r": same["state_alignment"][
                "pearson_r_chick_state_vs_mean_nest_success"
            ],
        },
        "figure3": {
            "species_data": "figure3_species_interactions.csv",
            "paper_null_data": "figure3_paper_level_null.csv",
        },
        "figure4": {
            "scale_data": "figure4_scale_sensitivity.csv",
            "detectability_data": "figure4_detectable_effect.csv",
            "radius_joint_switch_plus_contrast_p": radius["decision"][
                "joint_switch_plus_contrast_probability"
            ],
            "MDE80_abs_gamma_ah": mde["thresholds"]["MDE80_abs_gamma_ah"],
            "MDE90_abs_gamma_ah": mde["thresholds"]["MDE90_abs_gamma_ah"],
        },
        "provenance": {
            "concentration": "results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
            "lag_profile": "results/PALMER_PERFORMANCE_REDISTRIBUTION_LAGS_RESULT_V2.json",
            "repro_validation": "results/PALMER_REPRO_REDISTRIBUTION_RESULT_V1.json",
            "same_panel_diagnostic": "results/PALMER_REPRO_SAME_PANEL_METRIC_DIAGNOSTIC_RESULT_V1.json",
            "state_memory": "results/PALMER_PERFORMANCE_MEMORY_RESULT_V1.json",
            "paper2_primary": "results/PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json",
            "paper2_real_fit": "results/PAPER2_FIRST_REAL_V3_FIT_RESULT_V1.json",
            "scale": "results/PAPER2_SCALE_TRAIT_SENSITIVITY_RESULT_V1.json",
            "detectability": "results/PAPER2_DETECTABLE_EFFECT_RESULT_V1.json",
            "radius_null": "results/PAPER2_RADIUS_SIGN_SWITCH_NULL_RESULT_V1.json",
        },
    }
    (out_dir / "figure_data_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.root, args.out_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
