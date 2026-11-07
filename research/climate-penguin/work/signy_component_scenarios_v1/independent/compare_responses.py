#!/usr/bin/env python3
"""Compare primary scenario exports with independently computed response exports.

No primary implementation is imported or executed. This verifies full-precision
numbers, row identities, withholding, parameter uncertainty, and accounting.
Run diet_responses.py first, then run this script after primary exports exist.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.special import expit

BASE = Path(__file__).resolve().parents[3]
OLS_ATOL = 1e-11
LOGIT_ATOL = 1e-8
PRIMARY_SCORE_ATOL = 1e-7
NAMES = {"frequency": "frequency", "composition": "composition", "mean_response": "mean"}
KEYS = ("model", "member", "scenario", "period")
FIELD_MAP = {
    "reference_sic": "reference_sic", "target_sic": "target_sic", "delta_sic_pp": "delta_sic_pp",
    "reference_ols": "reference_ols", "reference_fractional_logit": "reference_fractional_logit",
    "future_ols": "future_ols", "change_ols": "change_ols",
    "change_ci_low": "change_coefficient_only_ci_low", "change_ci_high": "change_coefficient_only_ci_high",
    "future_fractional_logit": "future_fractional_logit", "change_fractional_logit": "change_fractional_logit",
}
FUTURE_FIELDS = ("future_ols", "change_ols", "change_ci_low", "change_ci_high",
                 "future_fractional_logit", "change_fractional_logit")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    parsed = float(value)
    return None if np.isnan(parsed) else parsed


def boolean(value: Any) -> bool:
    if value not in (True, False, "True", "False", "true", "false"):
        raise AssertionError(f"Invalid boolean: {value!r}")
    return str(value).lower() == "true"


def check_number(actual: Any, expected: Any, field: str, atol: float) -> float | None:
    a, b = number(actual), number(expected)
    if a is None or b is None:
        if a is not None or b is not None:
            raise AssertionError(f"NA mismatch for {field}: {actual!r} vs {expected!r}")
        return None
    if not np.isfinite(a) or not np.isfinite(b) or abs(a-b) > atol:
        raise AssertionError(f"Mismatch for {field}: {a} vs {b}; abs difference {abs(a-b)} > {atol}")
    return abs(a-b)


def keyed(rows: list[dict[str, str]], key_builder) -> dict[tuple, dict[str, str]]:
    result = {key_builder(row): row for row in rows}
    if len(result) != len(rows):
        raise AssertionError("Duplicate response row key")
    return result


def compare_responses(primary: list[dict[str, str]], independent: list[dict[str, str]], controlled: bool = False) -> dict[str, Any]:
    if controlled:
        pkey = lambda r: (float(r["reduction_sic_pp"]), NAMES[r["response"]])
        ikey = lambda r: (float(r["reduction_sic_pp"]), r["component"])
    else:
        pkey = lambda r: tuple(r[key] for key in KEYS) + (NAMES[r["response"]],)
        ikey = lambda r: tuple(r[key] for key in KEYS) + (r["component"],)
    pmap, imap = keyed(primary, pkey), keyed(independent, ikey)
    if pmap.keys() != imap.keys():
        raise AssertionError("Primary/independent response row identities differ")
    maxima = {key: 0.0 for key in FIELD_MAP}
    finite, na_pairs, withheld = 0, 0, 0
    for key, p in pmap.items():
        i = imap[key]
        support = boolean(p["within_observed_sic"])
        if support != boolean(i["within_observed_diet_sic_range"]):
            raise AssertionError(f"Support differs for {key}")
        if not support:
            withheld += 1
            if any(number(p[name]) is not None for name in FUTURE_FIELDS):
                raise AssertionError(f"Unsupported primary response leaked a value: {key}")
        for pfield, ifield in FIELD_MAP.items():
            tolerance = LOGIT_ATOL if "fractional_logit" in pfield else OLS_ATOL
            difference = check_number(p[pfield], i[ifield], f"{key}:{pfield}", tolerance)
            if difference is None:
                na_pairs += 1
            else:
                finite += 1
                maxima[pfield] = max(maxima[pfield], difference)
    return {"n_rows": len(pmap), "n_finite_numeric_pairs": finite, "n_matching_na_pairs": na_pairs,
            "n_wholly_withheld_rows": withheld, "max_absolute_difference_by_field": maxima}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="research/climate-penguin directory")
    args = parser.parse_args()
    base = args.base.resolve()
    root = base / "outputs/signy_component_scenarios_v1"
    independent = root / "independent"
    fit_path = root / "fit_parameters.json"
    primary_fits = json.loads(fit_path.read_text(encoding="utf-8"))
    own_path = independent / "diet_response_verification.json"
    own = json.loads(own_path.read_text(encoding="utf-8"))
    if own["status"] != "passed":
        raise AssertionError("Independent response verification is not passed")
    season_path = base / "outputs/signy_diet_components_v1/gentoo_primary_nine_seasons.csv"
    seasons = read_csv(season_path)
    design = np.column_stack([np.ones(len(seasons)), [float(row["sic_aug_nov"])/10 for row in seasons]])
    response_columns = {"frequency": "positive_mass_frequency", "composition": "conditional_fish_fraction", "mean": "mean_fish_fraction"}
    fits_result = {}
    if set(primary_fits) != set(NAMES):
        raise AssertionError("Unexpected set of primary response fits")
    for p_name, i_name in NAMES.items():
        p, i = primary_fits[p_name], own["fits"][i_name]
        if p["n_seasons"] != 9 or p["hc3_t_df"] != 7:
            raise AssertionError("Sample size or HC3 df differs")
        ols_param_error = max(check_number(a, b, f"{p_name} OLS beta", OLS_ATOL)
                             for a,b in zip(p["ols_params"], [i["ols"]["intercept"],i["ols"]["slope_per_10pp"]], strict=True))
        interval_error = max(check_number(p[field], i["ols"][field], f"{p_name} {field}", OLS_ATOL)
                             for field in ("slope_per_10pp","hc3_slope_95_low","hc3_slope_95_high"))
        covariance_error = float(np.max(np.abs(np.asarray(p["hc3_covariance"]) - np.asarray(i["ols"]["hc3_covariance"]))))
        if covariance_error > OLS_ATOL:
            raise AssertionError("HC3 covariance differs")
        logit_param_error = max(check_number(a, b, f"{p_name} logit beta", LOGIT_ATOL)
                               for a,b in zip(p["fractional_logit_params"], [i["fractional_logit"]["intercept"],i["fractional_logit"]["slope_per_10pp"]], strict=True))
        if not p["fractional_logit_converged"] or not i["fractional_logit"]["converged"]:
            raise AssertionError("A fractional-logit fit did not converge")
        outcome = np.asarray([float(r[response_columns[i_name]]) for r in seasons])
        score_max_abs = float(np.max(np.abs(design.T @ (outcome - expit(design @ p["fractional_logit_params"])))))
        if score_max_abs > PRIMARY_SCORE_ATOL:
            raise AssertionError(f"Primary fractional-logit score residual too large: {score_max_abs}")
        fits_result[p_name] = {"ols_params_max_absolute_difference": ols_param_error,
                              "ols_slope_and_hc3_interval_max_absolute_difference": interval_error,
                              "hc3_covariance_max_absolute_difference": covariance_error,
                              "fractional_logit_params_max_absolute_difference": logit_param_error,
                              "primary_fractional_logit_score_max_abs": score_max_abs,
                              "independent_fractional_logit_score_max_abs": i["fractional_logit"]["score_max_abs"]}

    scenario_result = compare_responses(read_csv(root / "component_scenarios.csv"),
                                        read_csv(independent / "diet_conditional_scenarios.csv"))
    controlled_result = compare_responses(read_csv(root / "controlled_reductions.csv"),
                                          read_csv(independent / "diet_controlled_reductions.csv"), controlled=True)
    paccount = keyed(read_csv(root / "slope_accounting_scenarios.csv"), lambda r: tuple(r[k] for k in KEYS))
    iaccount = keyed(read_csv(independent / "diet_accounting_scenarios.csv"), lambda r: tuple(r[k] for k in KEYS))
    if paccount.keys() != iaccount.keys():
        raise AssertionError("Accounting scenario identities differ")
    account_fields = {"frequency_change":"frequency_change", "composition_change":"composition_change",
                      "covariation_change":"covariation_change", "sum_component_changes":"sum_accounting_changes",
                      "mean_response_change":"mean_change_ols"}
    accounting_maxima = {k:0.0 for k in account_fields}
    accounting_na_pairs = 0
    for key, p in paccount.items():
        i = iaccount[key]
        if boolean(p["within_observed_diet_sic_range"]) != boolean(i["within_observed_diet_sic_range"]):
            raise AssertionError("Accounting support differs")
        for pfield, ifield in account_fields.items():
            difference = check_number(p[pfield], i[ifield], f"{key} {pfield}", OLS_ATOL)
            if difference is None:
                accounting_na_pairs += 1
            else:
                accounting_maxima[pfield] = max(accounting_maxima[pfield], difference)

    summary_path = root / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    for field, expected in {"n_seasons":9, "n_stomachs":73, "n_climate_conditions":12,
                            "n_supported_mean_conditions":11, "n_supported_response_rows":33}.items():
        if summary[field] != expected:
            raise AssertionError(f"Incorrect summary {field}")
    check_number(summary["reference_sic"], own["reference_sic"], "Summary reference", OLS_ATOL)
    for p_name, i_name in NAMES.items():
        ols = own["fits"][i_name]["ols"]
        expected = ols["intercept"] + ols["slope_per_10pp"] * own["reference_sic"] / 10
        check_number(summary["ols_reference_responses"][p_name], expected, "Summary reference response", OLS_ATOL)
    own_rows = read_csv(independent / "diet_conditional_scenarios.csv")
    shape_max = 0.0
    for p_name, i_name in NAMES.items():
        selected = [r for r in own_rows if r["component"]==i_name and boolean(r["within_observed_diet_sic_range"])]
        shape = {
            "n_conditions":len(selected),
            "n_negative_ols_changes":sum(float(r["change_ols"])<0 for r in selected),
            "n_negative_fractional_logit_changes":sum(float(r["change_fractional_logit"])<0 for r in selected),
            "max_absolute_future_level_difference":max(abs(float(r["future_ols"])-float(r["future_fractional_logit"])) for r in selected),
            "max_absolute_change_difference":max(abs(float(r["change_ols"])-float(r["change_fractional_logit"])) for r in selected),
            "ols_future_min":min(float(r["future_ols"]) for r in selected),
            "ols_future_max":max(float(r["future_ols"]) for r in selected),
            "ols_change_min":min(float(r["change_ols"]) for r in selected),
            "ols_change_max":max(float(r["change_ols"]) for r in selected),
        }
        for field,value in shape.items():
            shape_max=max(shape_max,check_number(summary["shape_sensitivity"][p_name][field],value,f"Shape {p_name} {field}",LOGIT_ATOL))
    if scenario_result["n_rows"] != 36 or scenario_result["n_wholly_withheld_rows"] != 3:
        raise AssertionError("Incorrect scenario row counts")
    if controlled_result["n_rows"] != 12 or controlled_result["n_wholly_withheld_rows"] != 3:
        raise AssertionError("Incorrect controlled-reduction row counts")
    checked_paths = [fit_path, summary_path, own_path, season_path,
                     root/"component_scenarios.csv",root/"controlled_reductions.csv",root/"slope_accounting_scenarios.csv",
                     independent/"diet_conditional_scenarios.csv",independent/"diet_controlled_reductions.csv",independent/"diet_accounting_scenarios.csv",
                     base/"work/signy_component_scenarios_v1/analyze.py",Path(__file__).resolve(),
                     Path(__file__).resolve().with_name("diet_responses.py")]
    result = {
        "status":"passed",
        "scope":"Full-precision independent response checks; no primary helper imports and no report/text claim verification by this script",
        "tolerances":{"ols_and_hc3_absolute":OLS_ATOL,"fractional_logit_absolute":LOGIT_ATOL,
                      "primary_fractional_logit_score_absolute":PRIMARY_SCORE_ATOL,
                      "relative":0.0,
                      "reason":"OLS/HC3 differ at floating-point precision; independent exact score solve and primary default GLM stopping rule can differ slightly for fractional-logit parameters."},
        "fits":fits_result,
        "conditional_scenarios":scenario_result,
        "controlled_reductions":controlled_result,
        "accounting":{"n_rows":len(paccount),"matching_na_pairs":accounting_na_pairs,
                      "max_absolute_difference_by_field":accounting_maxima},
        "summary_shape_max_absolute_difference":shape_max,
        "checked_file_hashes":[{"path":str(path.relative_to(base)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()} for path in checked_paths],
    }
    path=independent/"response_comparison.json"
    with path.open("w",encoding="utf-8",newline="\n") as handle:
        json.dump(result,handle,ensure_ascii=False,indent=2,allow_nan=False)
        handle.write("\n")
    print(json.dumps({key:value for key,value in result.items() if key!="checked_file_hashes"},indent=2,allow_nan=False))


if __name__ == "__main__":
    main()
