#!/usr/bin/env python3
"""Independent equal-season OLS/HC3 and fractional-logit scenario verification.

This script imports no primary analysis helpers and does not use statsmodels.
OLS uses NumPy's least-squares solve and the HC3 sandwich explicitly. Fractional
logit solves the unweighted Bernoulli quasi-likelihood score with SciPy, retaining
observed endpoints (including p=1) without any response transformation.

Run from any directory; defaults are resolved relative to this file.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path
from typing import Any

import numpy as np
import scipy
from scipy import optimize, special, stats

BASE = Path(__file__).resolve().parents[3]
REFERENCE_SIC = 48.68273700076806
SUPPORT = (21.90128214834321, 66.68284803598858)
COMPONENTS = {
    "frequency": "positive_mass_frequency",
    "composition": "conditional_fish_fraction",
    "mean": "mean_fish_fraction",
}
TERMS = ("frequency", "composition", "covariation")
NUMERIC_ATOL = 1e-11
SCORE_TOLERANCE = 1e-10


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Refusing empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def require_close(actual: Any, expected: Any, name: str, atol: float = NUMERIC_ATOL) -> float:
    actual_arr, expected_arr = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
    if actual_arr.shape != expected_arr.shape:
        raise AssertionError(f"{name}: shape mismatch {actual_arr.shape} != {expected_arr.shape}")
    difference = float(np.max(np.abs(actual_arr - expected_arr)))
    if not np.all(np.isfinite(actual_arr)) or not np.allclose(actual_arr, expected_arr, atol=atol, rtol=0):
        raise AssertionError(f"{name}: max absolute difference {difference} exceeds {atol}")
    return difference


def ols_hc3(design: np.ndarray, outcome: np.ndarray) -> dict[str, Any]:
    n, k = design.shape
    beta, _, rank, _ = np.linalg.lstsq(design, outcome, rcond=None)
    if rank != k:
        raise ValueError("OLS design is rank deficient")
    bread = np.linalg.inv(design.T @ design)
    leverage = np.einsum("ij,jk,ik->i", design, bread, design)
    residual = outcome - design @ beta
    if np.any(leverage >= 1):
        raise ValueError("HC3 undefined with leverage >= 1")
    weighted_scores = design * (residual / (1 - leverage))[:, None]
    covariance = bread @ weighted_scores.T @ weighted_scores @ bread
    se = np.sqrt(np.diag(covariance))
    quantile = float(stats.t.ppf(0.975, n - k))
    interval = [float(beta[1] - quantile * se[1]), float(beta[1] + quantile * se[1])]
    return {
        "intercept": float(beta[0]),
        "slope_per_10pp": float(beta[1]),
        "hc3_slope_standard_error": float(se[1]),
        "hc3_slope_95_low": interval[0],
        "hc3_slope_95_high": interval[1],
        "hc3_covariance": covariance.tolist(),
        "df_residual": int(n - k),
        "t_critical_0_975": quantile,
        "max_leverage": float(leverage.max()),
        "ols_score_max_abs": float(np.max(np.abs(design.T @ residual))),
    }


def fractional_logit(design: np.ndarray, outcome: np.ndarray) -> dict[str, Any]:
    if np.any((outcome < 0) | (outcome > 1)):
        raise ValueError("Fractional-logit responses must be in [0,1]")

    def score(beta: np.ndarray) -> np.ndarray:
        return design.T @ (outcome - special.expit(design @ beta))

    def jacobian(beta: np.ndarray) -> np.ndarray:
        fitted = special.expit(design @ beta)
        return -(design.T * (fitted * (1 - fitted))) @ design

    result = optimize.root(score, np.zeros(design.shape[1]), jac=jacobian,
                           method="hybr", options={"xtol": 1e-12})
    score_max_abs = float(np.max(np.abs(score(result.x))))
    converged = bool(result.success and score_max_abs <= SCORE_TOLERANCE)
    if not converged:
        raise AssertionError(
            f"Fractional-logit score solve failed: success={result.success}; "
            f"score_max_abs={score_max_abs}; {result.message}"
        )
    information = -jacobian(result.x)
    eigenvalues = np.linalg.eigvalsh(information)
    if np.any(eigenvalues <= 0):
        raise AssertionError("Fractional-logit information not positive definite")
    eta = design @ result.x
    return {
        "intercept": float(result.x[0]),
        "slope_per_10pp": float(result.x[1]),
        "converged": converged,
        "solver": "scipy.optimize.root(method=hybr), analytic score Jacobian",
        "solver_success": bool(result.success),
        "solver_message": str(result.message),
        "solver_nfev": int(result.nfev),
        "solver_njev": int(result.njev),
        "solver_xtol": 1e-12,
        "score_tolerance": SCORE_TOLERANCE,
        "score_max_abs": score_max_abs,
        "information_eigenvalues": eigenvalues.tolist(),
        "quasi_log_likelihood": float(np.sum(outcome * eta - np.logaddexp(0, eta))),
        "point_sensitivity_only": True,
    }


def evaluate(fit: dict[str, Any], target_sic: float) -> dict[str, Any]:
    ols, logit = fit["ols"], fit["fractional_logit"]
    reference_ols = float(ols["intercept"] + ols["slope_per_10pp"] * REFERENCE_SIC / 10)
    reference_logit = float(special.expit(logit["intercept"] + logit["slope_per_10pp"] * REFERENCE_SIC / 10))
    supported = bool(SUPPORT[0] <= target_sic <= SUPPORT[1])
    output = {
        "reference_sic": REFERENCE_SIC,
        "target_sic": target_sic,
        "delta_sic_pp": target_sic - REFERENCE_SIC,
        "within_observed_diet_sic_range": supported,
        "reference_ols": reference_ols,
        "reference_fractional_logit": reference_logit,
        "future_ols": None,
        "change_ols": None,
        "change_coefficient_only_ci_low": None,
        "change_coefficient_only_ci_high": None,
        "future_fractional_logit": None,
        "change_fractional_logit": None,
    }
    if not supported:
        return output
    delta10 = (target_sic - REFERENCE_SIC) / 10
    change = ols["slope_per_10pp"] * delta10
    limits = sorted([ols["hc3_slope_95_low"] * delta10, ols["hc3_slope_95_high"] * delta10])
    future_logit = float(special.expit(logit["intercept"] + logit["slope_per_10pp"] * target_sic / 10))
    output.update({
        "future_ols": float(ols["intercept"] + ols["slope_per_10pp"] * target_sic / 10),
        "change_ols": float(change),
        "change_coefficient_only_ci_low": float(limits[0]),
        "change_coefficient_only_ci_high": float(limits[1]),
        "future_fractional_logit": future_logit,
        "change_fractional_logit": float(future_logit - reference_logit),
    })
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="research/climate-penguin directory")
    args = parser.parse_args()
    base = args.base.resolve()
    out = base / "outputs/signy_component_scenarios_v1/independent"
    out.mkdir(parents=True, exist_ok=True)
    input_paths = {
        "seasons": base / "outputs/signy_diet_components_v1/gentoo_primary_nine_seasons.csv",
        "accounting": base / "outputs/signy_diet_components_v1/annual_accounting_terms.csv",
        "prior_summary": base / "outputs/signy_diet_components_v1/summary.json",
        "climate_conditions": base / "outputs/diet_niche_scenarios_v1/conditional_scenarios.csv",
    }
    rows = read_rows(input_paths["seasons"])
    accounting_rows = read_rows(input_paths["accounting"])
    climates = read_rows(input_paths["climate_conditions"])
    prior = json.loads(input_paths["prior_summary"].read_text(encoding="utf-8"))
    years = [int(row["year"]) for row in rows]
    if years != list(range(2001, 2010)) or len(rows) != 9 or sum(int(row["n_stomachs"]) for row in rows) != 73:
        raise AssertionError("Changed observed sample; expected nine 2001-2009 seasons, 73 stomachs")
    if [int(row["year"]) for row in accounting_rows] != years:
        raise AssertionError("Accounting-season ordering differs")
    if len(climates) != 12 or len({(r["model"],r["member"],r["scenario"],r["period"]) for r in climates}) != 12:
        raise AssertionError("Expected exactly 12 distinct climate conditions")
    x = np.asarray([float(row["sic_aug_nov"]) for row in rows])
    require_close([x.min(), x.max()], SUPPORT, "Observed support")
    design = np.column_stack([np.ones(len(x)), x / 10])
    responses = {name: np.asarray([float(r[column]) for r in rows]) for name, column in COMPONENTS.items()}
    require_close(responses["frequency"] * responses["composition"], responses["mean"], "Observed m=p*c")
    if np.count_nonzero(responses["frequency"] == 1) != 1:
        raise AssertionError("Expected untransformed observed endpoint p=1")
    fits = {name: {"ols": ols_hc3(design, y), "fractional_logit": fractional_logit(design, y)}
            for name, y in responses.items()}
    prior_response_max_difference = 0.0
    for name, fit in fits.items():
        expected = prior["mean_response_association"] if name == "mean" else prior["component_associations"][name]
        fields = ("intercept", "slope_per_10pp", "hc3_slope_95_low", "hc3_slope_95_high")
        prior_response_max_difference = max(prior_response_max_difference, require_close(
            [fit["ols"][key] for key in fields], [expected[key] for key in fields], f"Previous {name} OLS/HC3"))
    pbar, cbar = responses["frequency"].mean(), responses["composition"].mean()
    term_arrays = {
        "frequency": cbar * (responses["frequency"] - pbar),
        "composition": pbar * (responses["composition"] - cbar),
        "covariation": (responses["frequency"] - pbar) * (responses["composition"] - cbar),
    }
    accounting_max_difference = 0.0
    for term, values in term_arrays.items():
        accounting_max_difference = max(accounting_max_difference, require_close(
            values, [float(r[term]) for r in accounting_rows], f"Reconstructed {term} accounting"))
    require_close(sum(term_arrays.values()) + pbar * cbar, responses["mean"], "Accounting identity")
    term_fits = {term: ols_hc3(design, values) for term, values in term_arrays.items()}
    require_close(sum(f["slope_per_10pp"] for f in term_fits.values()),
                  fits["mean"]["ols"]["slope_per_10pp"], "Additive accounting slopes")
    for term, fit in term_fits.items():
        require_close(fit["slope_per_10pp"], prior["slope_accounting"]["component_slopes_per_10pp"][term],
                      f"Previous {term} accounting slope")

    scenario_rows, controlled_rows, accounting_scenarios, nonproduct_rows = [], [], [], []
    max_sum_error = 0.0
    for climate in climates:
        key = {k: climate[k] for k in ("model", "member", "scenario", "period")}
        reference = float(climate["observed_reference_sic"])
        target = float(climate["delta_adjusted_sic"])
        require_close(reference, REFERENCE_SIC, "Climate reference")
        require_close(target, REFERENCE_SIC + float(climate["model_future_sic"]) - float(climate["model_historical_sic"]),
                      "Additive climate correction")
        require_close(target - REFERENCE_SIC, float(climate["model_delta_sic_pp"]), "Climate delta")
        evaluated = {name: evaluate(fit, target) for name, fit in fits.items()}
        supported = evaluated["mean"]["within_observed_diet_sic_range"]
        if supported != (climate["within_observed_diet_sic_range"].lower() == "true"):
            raise AssertionError(f"Changed climate support classification: {key}")
        for name, result in evaluated.items():
            scenario_rows.append({**key, "component": name, **result})
        change_terms = {term: fit["slope_per_10pp"] * (target - REFERENCE_SIC) / 10 if supported else None
                        for term, fit in term_fits.items()}
        summed = sum(change_terms.values()) if supported else None
        mean_change = evaluated["mean"]["change_ols"]
        error = abs(summed - mean_change) if supported else None
        if supported:
            max_sum_error = max(max_sum_error, require_close(summed, mean_change, "Scenario accounting contrast sum"))
        accounting_scenarios.append({**key, "reference_sic": REFERENCE_SIC, "target_sic": target,
                                    "delta_sic_pp": target - REFERENCE_SIC,
                                    "within_observed_diet_sic_range": supported,
                                    "frequency_change": change_terms["frequency"],
                                    "composition_change": change_terms["composition"],
                                    "covariation_change": change_terms["covariation"],
                                    "sum_accounting_changes": summed, "mean_change_ols": mean_change,
                                    "absolute_sum_error": error})
        nonproduct_rows.append({**key, "target_sic": target, "within_observed_diet_sic_range": supported,
                               "fitted_m_ols": evaluated["mean"]["future_ols"],
                               "product_fitted_p_c_ols": evaluated["frequency"]["future_ols"] * evaluated["composition"]["future_ols"] if supported else None,
                               "fitted_m_fractional_logit": evaluated["mean"]["future_fractional_logit"],
                               "product_fitted_p_c_fractional_logit": evaluated["frequency"]["future_fractional_logit"] * evaluated["composition"]["future_fractional_logit"] if supported else None})
    for reduction in (5, 10, 20, 30):
        for name, fit in fits.items():
            result = evaluate(fit, REFERENCE_SIC - reduction)
            controlled_rows.append({"reduction_sic_pp": reduction, "component": name, **result})
    supported_rows = [r for r in scenario_rows if r["within_observed_diet_sic_range"]]
    withheld_rows = [r for r in scenario_rows if not r["within_observed_diet_sic_range"]]
    future_fields = ("future_ols", "change_ols", "change_coefficient_only_ci_low", "change_coefficient_only_ci_high",
                     "future_fractional_logit", "change_fractional_logit")
    if len(supported_rows) != 33 or len(withheld_rows) != 3:
        raise AssertionError("Expected 33 supported and three withheld response rows")
    for row in withheld_rows:
        if (row["model"],row["scenario"],row["period"]) != ("CESM2","ssp585","2081-2100"):
            raise AssertionError("Unexpected withheld climate condition")
        if any(row[k] is not None for k in future_fields):
            raise AssertionError("Unsupported scenario leaked a future response")
    for row in controlled_rows:
        if row["reduction_sic_pp"] == 30:
            if row["within_observed_diet_sic_range"] or any(row[k] is not None for k in future_fields):
                raise AssertionError("Controlled -30 pp case must be wholly withheld")
        elif not row["within_observed_diet_sic_range"]:
            raise AssertionError("Unexpected withheld controlled reduction")
    for row in supported_rows:
        if not (row["change_coefficient_only_ci_low"] <= row["change_ols"] <= row["change_coefficient_only_ci_high"]):
            raise AssertionError("Contrast interval incorrectly ordered")
        if not 0 <= row["future_fractional_logit"] <= 1:
            raise AssertionError("Fractional-logit response outside [0,1]")
        require_close(row["future_ols"] - row["reference_ols"], row["change_ols"], "Linear contrast")

    fit_rows = []
    for name, fit in fits.items():
        for method, result in fit.items():
            fit_rows.append({"component": name, "method": method,
                             "intercept": result["intercept"], "slope_per_10pp": result["slope_per_10pp"],
                             "hc3_slope_95_low": result.get("hc3_slope_95_low"),
                             "hc3_slope_95_high": result.get("hc3_slope_95_high"),
                             "df_residual": result.get("df_residual"),
                             "score_max_abs": result.get("score_max_abs",result.get("ols_score_max_abs"))})
    outputs = {
        "diet_response_fits.csv": fit_rows,
        "diet_conditional_scenarios.csv": scenario_rows,
        "diet_controlled_reductions.csv": controlled_rows,
        "diet_accounting_scenarios.csv": accounting_scenarios,
        "diet_nonproduct_diagnostics.csv": nonproduct_rows,
    }
    for filename, data in outputs.items():
        write_rows(out / filename, data)
    hashes = [{"path": str(path.relative_to(base)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
              for path in input_paths.values()]
    summary = {
        "status": "passed",
        "implementation": "Independent NumPy least squares + explicit HC3 sandwich; SciPy analytic fractional-logit score solve; no primary imports",
        "sample": {"n_seasons": 9, "n_stomachs": 73, "years": years, "equal_season_weights": True,
                   "response_transformation": "none; observed endpoints retained"},
        "reference_sic": REFERENCE_SIC,
        "support_sic": list(SUPPORT),
        "fits": fits,
        "accounting_fits": term_fits,
        "checks": {"previous_ols_hc3_max_absolute_difference": prior_response_max_difference,
                   "previous_annual_accounting_max_absolute_difference": accounting_max_difference,
                   "accounting_scenario_sum_max_absolute_error": max_sum_error,
                   "n_scenario_response_rows": len(scenario_rows), "n_supported_future_response_rows": len(supported_rows),
                   "n_wholly_withheld_response_rows": len(withheld_rows),
                   "controlled_reduction_support": {str(v): SUPPORT[0] <= REFERENCE_SIC-v <= SUPPORT[1] for v in (5,10,20,30)},
                   "fractional_logit_all_converged": all(f["fractional_logit"]["converged"] for f in fits.values()),
                   "all_csv_lf": all(b"\r" not in (out / filename).read_bytes() for filename in outputs),
                   "numeric_comparison_atol": NUMERIC_ATOL},
        "scope": "Responses are conditional evaluations at future mean SIC, not mean of future annual diets. HC3 t7 intervals describe coefficient-only fixed-delta contrasts; no absolute future-level intervals or logit inferential claims.",
        "input_hashes": hashes,
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
    }
    write_json(out / "diet_response_verification.json", summary)
    print(json.dumps({"status":summary["status"], "checks":summary["checks"], "fits":fit_rows}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
