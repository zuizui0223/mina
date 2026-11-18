#!/usr/bin/env python3
"""Compare primary Signy climate outputs with the existing independent outputs.

This performs no climate reconstruction, raw-monthly reads, diet prediction, or
network access. It joins the two output sets by scientific identifiers rather
than row order, checks every primary column, and writes a deterministic report.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path


BASE = Path("outputs/signy_component_scenarios_v1")
TOLERANCE = 1e-10
MODEL_KEY = ("model", "member", "location_id")
PERIOD_KEY = MODEL_KEY + ("scenario", "period")
SOURCE_KEY = MODEL_KEY + ("scenario",)
FILES = {
    "primary_scenarios": BASE / "climate_scenarios.csv",
    "primary_reference": BASE / "climate_reference.csv",
    "primary_annual": BASE / "annual_climate_support.csv",
    "primary_observed": BASE / "observed_reference_annual_sic.csv",
    "independent_scenarios": BASE / "independent/climate_inputs_scenarios.csv",
    "independent_support": BASE / "independent/climate_inputs_support.csv",
    "independent_annual": BASE / "independent/climate_inputs_annual.csv",
    "independent_observed": BASE / "independent/climate_inputs_observed_annual.csv",
    "independent_sources": BASE / "independent/climate_inputs_sources.csv",
}


def key(row, fields):
    return tuple(str(row[field]) for field in fields)


def unique_index(rows, fields):
    result = {}
    for row in rows:
        row_key = key(row, fields)
        if row_key in result:
            raise ValueError(f"Duplicate key {dict(zip(fields, row_key))}")
        result[row_key] = row
    return result


def boolean(value):
    if str(value).lower() == "true":
        return True
    if str(value).lower() == "false":
        return False
    raise ValueError(f"Invalid boolean: {value!r}")


def read_inputs(root):
    rows, columns, provenance = {}, {}, {}
    for name, relative in FILES.items():
        raw = (root / relative).read_bytes()
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
        columns[name] = reader.fieldnames or []
        if len(columns[name]) != len(set(columns[name])):
            raise ValueError(f"Duplicate CSV column in {relative}")
        rows[name] = list(reader)
        if any(None in row or None in row.values() for row in rows[name]):
            raise ValueError(f"Malformed CSV row in {relative}")
        provenance[name] = {
            "path": relative.as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "row_count": len(rows[name]),
            "columns": columns[name],
            "lf_line_endings": b"\r" not in raw,
        }
    return rows, columns, provenance


def expected_primary_rows(inputs):
    sources = unique_index(inputs["independent_sources"], SOURCE_KEY)
    support = unique_index(inputs["independent_support"], PERIOD_KEY)
    scenarios, reference, annual = [], [], []

    for row in inputs["independent_scenarios"]:
        summary = support[key(row, PERIOD_KEY)]
        source = sources[key(row, SOURCE_KEY)]
        expected = {name: row[name] for name in PERIOD_KEY}
        for name in (
            "observed_reference_sic", "model_historical_sic",
            "historical_model_bias_pp", "model_future_sic", "model_delta_sic_pp",
            "delta_adjusted_sic", "model_cell_distance_km",
            "within_observed_diet_sic_range",
        ):
            expected[name] = row[name]
        expected.update({
            "grid_cell_id": source["grid_cell_id"],
            "future_annual_support_count": row["annual_n_within_support"],
            "future_annual_support_fraction": (
                int(summary["n_years_within_support"]) / int(summary["n_years"])
            ),
            "future_annual_sic_min": summary["adjusted_annual_min"],
            "future_annual_sic_max": summary["adjusted_annual_max"],
            "future_annual_unphysical_count": (
                int(summary["n_years_below_physical_zero"])
                + int(summary["n_years_above_physical_100"])
            ),
            "n_future_years": summary["n_years"],
        })
        scenarios.append(expected)

    for summary in inputs["independent_support"]:
        if summary["scenario"] != "historical":
            continue
        if summary["period"] != "1995-2014":
            raise ValueError("Unexpected independent historical period")
        source = sources[key(summary, SOURCE_KEY)]
        observed_values = {
            row["observed_reference_sic"] for row in inputs["independent_annual"]
            if key(row, PERIOD_KEY) == key(summary, PERIOD_KEY)
        }
        if len(observed_values) != 1:
            raise ValueError("Independent observed reference is inconsistent")
        expected = {name: summary[name] for name in MODEL_KEY}
        expected.update({
            "grid_cell_id": source["grid_cell_id"],
            "model_cell_distance_km": source["distance_km"],
            "observed_reference_sic": observed_values.pop(),
            "model_historical_sic": summary["raw_mean_sic"],
            "historical_model_bias_pp": -float(summary["additive_correction_pp"]),
            "n_years": summary["n_years"],
            "mean_sic": summary["adjusted_mean_sic"],
            "annual_min_sic": summary["adjusted_annual_min"],
            "annual_max_sic": summary["adjusted_annual_max"],
            "mean_within_observed_range": summary["mean_within_support"],
            "n_in_observed_range": summary["n_years_within_support"],
            "fraction_in_observed_range": (
                int(summary["n_years_within_support"]) / int(summary["n_years"])
            ),
            "n_outside_physical_range": (
                int(summary["n_years_below_physical_zero"])
                + int(summary["n_years_above_physical_100"])
            ),
        })
        reference.append(expected)

    for row in inputs["independent_annual"]:
        source = sources[key(row, SOURCE_KEY)]
        expected = {name: row[name] for name in MODEL_KEY + ("period", "year")}
        expected.update({
            "experiment": row["scenario"],
            "grid_cell_id": source["grid_cell_id"],
            "model_cell_distance_km": row["model_cell_distance_km"],
            "model_annual_sic": row["raw_annual_sic"],
            "delta_adjusted_sic": row["adjusted_annual_sic"],
            "within_observed_diet_sic_range": row["within_diet_sic_support"],
            "within_physical_range": row["within_physical_percent_range"],
        })
        annual.append(expected)

    observed = [
        {"year": row["year"], "sic_aug_nov": row["observed_annual_sic"]}
        for row in inputs["independent_observed"]
    ]
    return {
        "scenarios": scenarios, "reference": reference,
        "annual": annual, "observed": observed,
    }


def compare_table(primary, expected, columns, key_fields, integer_fields,
                  flag_fields, text_fields, expected_count):
    primary_index = unique_index(primary, key_fields)
    expected_index = unique_index(expected, key_fields)
    primary_keys, expected_keys = set(primary_index), set(expected_index)
    common = sorted(primary_keys & expected_keys)
    expected_columns = set(expected[0])
    all_fields = sorted(expected_columns - set(key_fields))
    row_matches = {row_key: True for row_key in common}
    field_reports = {}

    for name in all_fields:
        kind = ("boolean" if name in flag_fields else "integer" if name in integer_fields
                else "text" if name in text_fields else "number")
        stats = {"type": kind, "compared_count": 0, "matching_count": 0,
                 "exactly_equal_count": 0, "mismatches": []}
        if kind in ("number", "integer"):
            stats.update({"max_absolute_difference": 0.0, "worst_case": None})
        if kind == "number":
            stats["unit"] = ("km" if name == "model_cell_distance_km" else
                             "fraction" if "fraction" in name else
                             "percentage_points")
        if kind == "boolean":
            stats.update({"primary_true_count": 0, "independent_true_count": 0})
        for row_key in common:
            identifiers = dict(zip(key_fields, row_key))
            p, e = primary_index[row_key].get(name), expected_index[row_key][name]
            try:
                if kind == "number":
                    p, e = float(p), float(e)
                    if not math.isfinite(p) or not math.isfinite(e):
                        raise ValueError("Nonfinite comparison value")
                    difference = abs(p - e)
                    matched = difference <= TOLERANCE
                elif kind == "integer":
                    p, e = int(p), int(e)
                    difference = abs(p - e)
                    matched = p == e
                elif kind == "boolean":
                    p, e = boolean(p), boolean(e)
                    stats["primary_true_count"] += int(p)
                    stats["independent_true_count"] += int(e)
                    matched = p == e
                else:
                    p, e = str(p), str(e)
                    matched = p == e
                stats["compared_count"] += 1
                stats["matching_count"] += int(matched)
                stats["exactly_equal_count"] += int(p == e)
                if kind in ("number", "integer"):
                    if difference > stats["max_absolute_difference"]:
                        stats["max_absolute_difference"] = difference
                        stats["worst_case"] = {
                            "key": identifiers, "primary": p, "independent": e,
                        }
                if not matched:
                    stats["mismatches"].append({
                        "key": identifiers, "primary": p, "independent": e,
                    })
            except (ValueError, TypeError) as exc:
                matched = False
                stats["mismatches"].append({"key": identifiers, "error": str(exc)})
            row_matches[row_key] = row_matches[row_key] and matched
        field_reports[name] = stats

    missing = [dict(zip(key_fields, k)) for k in sorted(expected_keys - primary_keys)]
    extra = [dict(zip(key_fields, k)) for k in sorted(primary_keys - expected_keys)]
    unmatched_columns = sorted(set(columns) - expected_columns)
    missing_columns = sorted(expected_columns - set(columns))
    max_difference = max(
        (r["max_absolute_difference"] for r in field_reports.values()
         if r["type"] in ("number", "integer")), default=0.0
    )
    max_sic_difference = max(
        (r["max_absolute_difference"] for r in field_reports.values()
         if r.get("unit") == "percentage_points"), default=0.0
    )
    matched_rows = sum(row_matches.values())
    return {
        "status": "passed" if (
            len(primary) == len(expected) == expected_count == matched_rows
            and not missing and not extra and not unmatched_columns and not missing_columns
        ) else "failed",
        "key_fields": list(key_fields), "expected_row_count": expected_count,
        "primary_row_count": len(primary), "independent_row_count": len(expected),
        "matched_key_count": len(common), "matching_row_count": matched_rows,
        "missing_primary_keys": missing, "extra_primary_keys": extra,
        "uncompared_primary_columns": unmatched_columns,
        "missing_primary_columns": missing_columns,
        "max_absolute_numeric_difference": max_difference,
        "max_absolute_sic_difference_pp": max_sic_difference,
        "fields": field_reports,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.out or root / BASE / "independent/climate_primary_comparison.json"
    inputs, columns, provenance = read_inputs(root)
    expected = expected_primary_rows(inputs)
    configurations = {
        "scenarios": (PERIOD_KEY,
                      {"future_annual_support_count", "future_annual_unphysical_count", "n_future_years"},
                      {"within_observed_diet_sic_range"}, {"grid_cell_id"}, 12),
        "reference": (MODEL_KEY, {"n_years", "n_in_observed_range", "n_outside_physical_range"},
                      {"mean_within_observed_range"}, {"grid_cell_id"}, 3),
        "annual": (MODEL_KEY + ("experiment", "period", "year"), set(),
                   {"within_observed_diet_sic_range", "within_physical_range"}, {"grid_cell_id"}, 300),
        "observed": (("year",), set(), set(), set(), 20),
    }
    comparisons = {
        name: compare_table(inputs[f"primary_{name}"], expected[name],
                            columns[f"primary_{name}"], *configuration)
        for name, configuration in configurations.items()
    }
    annual_fields = comparisons["annual"]["fields"]
    all_passed = all(result["status"] == "passed" for result in comparisons.values())
    summary = {
        "status": "passed" if all_passed else "failed",
        "total_matching_rows": sum(result["matching_row_count"] for result in comparisons.values()),
        "total_expected_rows": 335,
        "max_absolute_sic_difference_pp": max(
            result["max_absolute_sic_difference_pp"] for result in comparisons.values()
        ),
        "annual_diet_support_flags_matching": annual_fields["within_observed_diet_sic_range"]["matching_count"],
        "annual_physical_range_flags_matching": annual_fields["within_physical_range"]["matching_count"],
        "annual_flag_count_expected": 300,
    }
    report = {
        "schema_version": 1,
        "purpose": "Compare four primary climate outputs against previously reconstructed independent outputs.",
        "summary": summary,
        "comparison_policy": {
            "floating_point_absolute_tolerance": TOLERANCE,
            "relative_tolerance": 0,
            "integers_booleans_identifiers": "Exact equality; unique identifier joins; no row-order dependency.",
            "coverage": "Every primary column is compared, including source grid identifiers and distances.",
            "reference_mapping": "Independent historical 1995-2014 support rows provide the three reference summaries.",
            "summary_derivations": "Fractions are support counts divided by n_years; physical violations sum the independent below-zero and above-100 counts.",
            "observed_support_flags": "The primary observed file has no support flag; all 20 SIC values and year identifiers are compared.",
            "scope": "Existing CSV outputs only; no raw monthly reads, reconstruction, downloads, or future diet predictions.",
        },
        "script": {
            "path": Path(__file__).resolve().relative_to(root).as_posix(),
            "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "inputs": provenance,
        "comparisons": comparisons,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"output": str(output), **summary}, ensure_ascii=False))
    for name, result in comparisons.items():
        print(json.dumps({"table": name, **{field: result[field] for field in (
            "status", "matching_row_count", "expected_row_count", "max_absolute_sic_difference_pp"
        )}}))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
