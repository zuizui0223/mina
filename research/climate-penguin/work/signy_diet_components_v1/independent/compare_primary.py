"""Compare independent source calculations to all primary numeric tables."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

import palmer_reference


OUTPUT_PATH = Path("research/climate-penguin/outputs/signy_diet_components_v1")


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def file_record(path, repo_root):
    try:
        label = path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        label = path.name
    return {"file": label, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run(repo_root, primary_directory, independent_directory):
    primary_path = primary_directory / "summary.json"
    independent_path = independent_directory / "independent_results.json"
    primary = json.loads(primary_path.read_text())
    independent = json.loads(independent_path.read_text())
    counts = {"numeric_comparisons": 0, "exact_comparisons": 0}
    maximum = {"absolute_difference": 0.0, "field": None}
    failures = []
    input_files = [primary_path, independent_path]

    def compare(observed, expected, label):
        if isinstance(observed, dict):
            if not isinstance(expected, dict):
                failures.append({"field": label, "reason": "independent object missing"})
                return
            for key, value in observed.items():
                if key not in expected:
                    failures.append({"field": f"{label}.{key}", "reason": "independent key missing"})
                else:
                    compare(value, expected[key], f"{label}.{key}")
        elif isinstance(observed, list):
            if not isinstance(expected, list) or len(observed) != len(expected):
                failures.append({"field": label, "reason": "array length mismatch"})
                return
            for index, (value, reference) in enumerate(zip(observed, expected)):
                compare(value, reference, f"{label}[{index}]")
        elif isinstance(observed, bool) or isinstance(observed, (str, int)) or observed is None:
            counts["exact_comparisons"] += 1
            if observed != expected:
                failures.append({"field": label, "primary": observed, "independent": expected})
        elif isinstance(observed, float):
            counts["numeric_comparisons"] += 1
            difference = abs(observed - expected)
            if difference > maximum["absolute_difference"]:
                maximum.update({"absolute_difference": difference, "field": label})
            if not math.isclose(observed, expected, rel_tol=1e-12, abs_tol=1e-12):
                failures.append({"field": label, "primary": observed, "independent": expected})
        else:
            raise TypeError(type(observed))

    summary_fields = ("primary_species", "n_seasons", "n_stomachs", "source_audit",
                      "component_associations", "mean_response_association", "permutation_family",
                      "slope_accounting", "recovered_mass_descriptives")
    for key in summary_fields:
        compare(primary[key], independent[key], key)

    compared_tables = {}
    table_specs = (("species_season_components", ("species", "year")),
                   ("gentoo_primary_nine_seasons", ("year",)),
                   ("annual_accounting_terms", ("year",)),
                   ("leave_one_season_accounting", ("omitted_year",)))
    for table, key_columns in table_specs:
        path = primary_directory / f"{table}.csv"
        input_files.append(path)
        primary_rows = read_csv(path)
        primary_lookup = {tuple(row[key] for key in key_columns): row for row in primary_rows}
        independent_lookup = {tuple(str(row[key]) for key in key_columns): row for row in independent[table]}
        if len(primary_lookup) != len(primary_rows) or set(primary_lookup) != set(independent_lookup):
            failures.append({"field": table, "reason": "missing or duplicated keys"})
            continue
        columns = set()
        for key, row in primary_lookup.items():
            reference = independent_lookup[key]
            for column, value in row.items():
                columns.add(column)
                if column not in reference:
                    failures.append({"field": f"{table}.{key}.{column}", "reason": "independent column missing"})
                    continue
                expected = reference[column]
                if expected is None:
                    observed = None if not value or value.lower() == "nan" else value
                elif isinstance(expected, int):
                    observed = int(value)
                elif isinstance(expected, float):
                    observed = float(value)
                else:
                    observed = value
                compare(observed, expected, f"{table}.{key}.{column}")
        compared_tables[table] = {"rows": len(primary_rows), "columns": sorted(columns)}

    palmer = palmer_reference.run(repo_root, independent_directory, primary_directory)["verification"]
    if palmer["status"] != "PASS":
        failures.append({"field": "palmer_reference", "reason": palmer["status"]})
    input_files += [primary_directory / "palmer_reported_detection_reference.csv",
                    independent_directory / "palmer_reference_verification.json"]
    source_manifest_path = primary_directory / "source_manifest.json"
    manifest = json.loads(source_manifest_path.read_text())
    primary_hashes = {row.get("summary_sha256", row.get("sha256")) for row in manifest}
    for source in independent["source_manifest"]:
        if source["sha256"] not in primary_hashes:
            failures.append({"field": "source_manifest", "reason": "source hash absent from primary manifest", "source": source})
    input_files.append(source_manifest_path)
    support = independent["support_checks"]
    gentoo = independent["gentoo_primary_nine_seasons"]
    accounting = independent["slope_accounting"]
    allocation_loo = independent["leave_one_season_accounting"]
    diagnostics = {
        "same_nine_season_73_stomach_cohort": independent["n_seasons"] == 9 and independent["n_stomachs"] == 73,
        **support,
        "n_positive_fish_mass_over_all_valid_stomachs": sum(row["n_positive_fish_mass"] for row in gentoo),
        "max_annual_accounting_reconstruction_error": accounting["max_value_identity_error"],
        "accounting_slope_identity_error": accounting["slope_identity_error"],
        "leave_one_season_accounting_ranges": {
            key: {"min": min(row[key] for row in allocation_loo), "max": max(row[key] for row in allocation_loo)}
            for key in ("frequency", "composition", "covariation", "mean_response")
        },
        "both_frequency_and_composition_full_sample_slopes_positive":
            all(accounting["component_slopes_per_10pp"][key] > 0 for key in ("frequency", "composition")),
        "single_common_x_permutation_family": True,
        "hc3_t_df": {key: value["hc3_t_df"] for key, value in independent["component_associations"].items()},
        "method_limits": [
            "The two-component max statistic uses one common exposure permutation and does not adjust the whole project.",
            "Exact p remains conditional on exchangeable years; HC3 does not remove serial dependence.",
            "Both accounting slopes are positive; stronger evidence for frequency does not mean only frequency contributes.",
            "Recovered gram measurements are meals recovered at sampling, not intake rates or prey availability.",
            "Palmer reference conditions on reported detection; it is not a harmonized positive-mass comparison.",
        ],
    }
    result = {
        "status": "PASS" if not failures else "FAIL", "checked_utc": datetime.now(timezone.utc).isoformat(),
        "absolute_tolerance": 1e-12, "relative_tolerance": 1e-12,
        "signy_numeric_comparisons": counts["numeric_comparisons"],
        "signy_exact_comparisons": counts["exact_comparisons"],
        "maximum_signy_numeric_absolute_difference": maximum,
        "palmer_reference_primary_comparison": palmer["primary_output_verification"],
        "palmer_reference_xml_to_long_comparison": palmer["long_transcription_verification"],
        "compared_summary_fields": list(summary_fields), "compared_tables": compared_tables,
        "diagnostics": diagnostics,
        "input_file_hashes": [file_record(path, repo_root) for path in input_files], "failures": failures,
    }
    output = independent_directory / "primary_comparison.json"
    output.write_text(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    if failures:
        raise SystemExit(1)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[5])
    parser.add_argument("--primary-dir", type=Path)
    parser.add_argument("--independent-dir", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    primary = args.primary_dir.resolve() if args.primary_dir else root / OUTPUT_PATH
    independent = args.independent_dir.resolve() if args.independent_dir else primary / "independent"
    run(root, primary, independent)
