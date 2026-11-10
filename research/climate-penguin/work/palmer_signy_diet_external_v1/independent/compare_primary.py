"""Compare independently frozen calculations against primary output files."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path


OUTPUT_PATH = Path("research/climate-penguin/outputs/palmer_signy_diet_external_v1")


def portable_path(path, repo_root):
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.name


def load_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(independent_directory, primary_directory, repo_root):
    independent_path = independent_directory / "independent_results.json"
    primary_path = primary_directory / "summary.json"
    independent = json.loads(independent_path.read_text())
    primary = json.loads(primary_path.read_text())
    failures = []
    counts = {"numeric_comparisons": 0, "exact_comparisons": 0}
    maximum_absolute_difference = {"difference": 0.0, "field": None}

    def compare_values(observed, expected, label):
        if isinstance(expected, bool) or isinstance(expected, (str, int)):
            counts["exact_comparisons"] += 1
            if observed != expected:
                failures.append({"field": label, "primary": observed, "independent": expected})
        elif isinstance(expected, float):
            counts["numeric_comparisons"] += 1
            difference = abs(float(observed) - expected)
            if difference > maximum_absolute_difference["difference"]:
                maximum_absolute_difference.update({"difference": difference, "field": label})
            if not math.isclose(float(observed), expected, rel_tol=1e-12, abs_tol=1e-12):
                failures.append({"field": label, "primary": observed, "independent": expected})
        elif isinstance(expected, dict):
            for key in set(expected).intersection(observed):
                compare_values(observed[key], expected[key], f"{label}.{key}")
        elif isinstance(expected, list):
            if len(observed) != len(expected):
                failures.append({"field": label + ".length", "primary": len(observed), "independent": len(expected)})
                return
            for index, (p, q) in enumerate(zip(observed, expected)):
                compare_values(p, q, f"{label}[{index}]")

    for field in ("regions", "transport", "sensitivity", "source_audit"):
        compare_values(primary[field], independent[field], field)

    inputs = [independent_path, primary_path]
    comparison_specs = [
        ("annual_pair_comparison.csv", "annual_pair_comparison", ("region", "year")),
        ("annual_ice_proxies.csv", "annual_ice_proxies", ("site_id", "year")),
        ("signy_species_seasons.csv", "signy_species_seasons", ("species", "year")),
        ("palmer_species_seasons.csv", "palmer_species_seasons", ("species", "year")),
        ("signy_to_palmer_transport.csv", "predictions", ("region", "year")),
    ]
    compared_tables = {}
    for filename, independent_key, key_columns in comparison_specs:
        primary_file = primary_directory / filename
        inputs.append(primary_file)
        p_rows = load_csv(primary_file)
        p_lookup = {tuple(str(r[col]) for col in key_columns): r for r in p_rows}
        i_rows = independent[independent_key]
        i_lookup = {tuple(str(r[col]) for col in key_columns): r for r in i_rows}
        if len(p_lookup) != len(p_rows) or set(p_lookup) != set(i_lookup):
            raise ValueError(f"missing or duplicated keys: {filename}")
        fields_compared = set()
        for key, expected_row in i_lookup.items():
            observed_row = p_lookup[key]
            for column in set(expected_row).intersection(observed_row):
                expected = expected_row[column]
                value = observed_row[column]
                if isinstance(expected, bool):
                    if value.lower() not in ("true", "false"):
                        raise ValueError(f"invalid boolean: {filename} {column}")
                    value = value.lower() == "true"
                elif isinstance(expected, int):
                    value = int(value)
                elif isinstance(expected, float):
                    value = float(value)
                compare_values(value, expected, f"{filename}.{key}.{column}")
                fields_compared.add(column)
        compared_tables[filename] = {"rows": len(i_lookup), "fields": sorted(fields_compared)}

    predictions = independent["predictions"]
    residuals = [r["predicted_distance"] - r["distance"] for r in predictions]
    all_scores = independent["transport"]["all_target_seasons"]
    support_scores = independent["transport"]["within_training_ice_range"]
    primary_mean = independent["regions"]["Signy"]["mean_distance"]
    legacy_mean = next(r["mean_distance"] for r in independent["sensitivity"]
                       if r["scope"] == "Signy_denominator" and r["variant"] == "legacy_fish_crustacean_mean")
    diagnostics = {
        "all_six_target_seasons_overpredicted": all(r > 0 for r in residuals) and len(residuals) == 6,
        "overprediction_count": sum(r > 0 for r in residuals),
        "minimum_overprediction_fraction": min(residuals),
        "maximum_overprediction_fraction": max(residuals),
        "all_predictions_within_0_1_without_clipping": all(r["prediction_in_response_range"] for r in predictions),
        "only_out_of_training_ice_support_years": [r["year"] for r in predictions if not r["in_training_ice_range"]],
        "model_mae_worse_than_training_mean_all_six": all_scores["model_mae"] > all_scores["training_mean_mae"],
        "model_rmse_worse_than_training_mean_all_six": all_scores["model_rmse"] > all_scores["training_mean_rmse"],
        "model_mae_worse_than_training_mean_within_support_five": support_scores["model_mae"] > support_scores["training_mean_mae"],
        "model_rmse_worse_than_training_mean_within_support_five": support_scores["model_rmse"] > support_scores["training_mean_rmse"],
        "primary_minus_legacy_mean_distance": primary_mean - legacy_mean,
        "primary_and_legacy_are_not_exactly_identical": primary_mean != legacy_mean,
        "signy_valid_stomachs": sum(r["n_valid"] for r in independent["source_audit"]),
        "season_counts": {region: values["n_seasons"] for region, values in independent["regions"].items()},
        "unique_season_start_years": len(set(r["year"] for r in independent["annual_pair_comparison"])),
        "method_notes": [
            "Main three-species result is not this two-species contrast; keep its original value unchanged.",
            "Palmer exact p is 560/720 using absolute Pearson statistic, not a doubled one-sided tail.",
            "HC3 t intervals use 7 degrees of freedom for Signy and 4 for Palmer; they do not account for serial dependence.",
            "Different significance within each region does not itself establish a between-region difference in slopes.",
            "Both baseline and regression overpredict the target level; the failure diagnoses uncalibrated geographic transfer, not absence of any local ice response.",
        ],
    }
    checks = [value for key, value in diagnostics.items() if isinstance(value, bool)]
    if not all(checks):
        failures.append({"field": "claimed_result_diagnostics", "diagnostics": diagnostics})
    result = {
        "status": "PASS" if not failures else "FAIL",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "independent_recalculation_script": "recalculate.py",
        "comparison_script": "compare_primary.py",
        "absolute_tolerance": 1e-12, "relative_tolerance": 1e-12,
        **counts, "maximum_numeric_absolute_difference": maximum_absolute_difference,
        "compared_tables": compared_tables,
        "diagnostics": diagnostics,
        "comparison_input_hashes": [{"file": portable_path(p, repo_root), "sha256": sha256(p)} for p in inputs],
        "failures": failures,
    }
    out = independent_directory / "primary_comparison.json"
    out.write_text(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[5],
                        help="Repository root; defaults to the checkout containing this script")
    parser.add_argument("--independent-dir", type=Path,
                        help="Independent output directory; defaults to <primary-dir>/independent")
    parser.add_argument("--primary-dir", type=Path,
                        help="Primary output directory; defaults to the repo's analysis output directory")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    primary_directory = args.primary_dir.resolve() if args.primary_dir else repo_root / OUTPUT_PATH
    independent_directory = args.independent_dir.resolve() if args.independent_dir else primary_directory / "independent"
    run(independent_directory, primary_directory, repo_root)
