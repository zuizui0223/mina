"""Independently verify Palmer's reported-detection conditional reference.

Read fish mean/occurrence cells directly from the saved primary-source XML.
Derive decimal rounding intervals from the displayed cells, then compare the
separate long-form transcription and, when present, the main reference output.
No primary analysis or extraction helper is imported.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET


SOURCE_PATH = Path("research/climate-penguin/work/palmer_signy_diet_external_v1/sources")
OUTPUT_PATH = Path("research/climate-penguin/outputs/signy_diet_components_v1")
XML_SHA256 = "7d074d865cb6cf187f4aad56f7535179a8de9832c54b46783d6013dad7efd97d"
TABLE_ID = "ece34445-tbl-0001"
CELL_PATTERN = re.compile(
    r"^([0-9]+(?:\.[0-9]+)?)\s*±\s*([0-9]+(?:\.[0-9]+)?)\s*"
    r"\(([0-9]+(?:\.[0-9]+)?)\)$"
)


def file_label(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.name


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def displayed_bounds(token: str):
    value = Decimal(token)
    quantum = Decimal(1).scaleb(value.as_tuple().exponent)
    half = quantum / 2
    return value, max(Decimal(0), value - half), min(Decimal(100), value + half), quantum


def xml_fish_rows(path: Path):
    tree = ET.parse(path)
    table = tree.find(f".//table-wrap[@id='{TABLE_ID}']/table/tbody")
    if table is None:
        raise ValueError("Primary XML Table 1 is missing")
    result = []
    category = None
    for row_number, tr in enumerate(table.findall("tr"), start=1):
        cells = tr.findall("td")
        if cells[0].get("rowspan") == "6":
            category = " ".join("".join(cells.pop(0).itertext()).split())
        if len(cells) != 7:
            raise ValueError(f"Unexpected primary table structure in row {row_number}")
        if category != "Unidentified fish (%)":
            continue
        text = ["".join(cell.itertext()).strip() for cell in cells]
        year = int(text[0])
        for species, value_index, n_index in (("Adelie", 1, 2), ("Gentoo", 3, 4)):
            cell = text[value_index]
            match = CELL_PATTERN.fullmatch(cell)
            if match is None:
                raise ValueError(f"Unrecognized fish cell: {species} {year}: {cell}")
            mean_token, sd_token, occurrence_token = match.groups()
            mean, mean_low, mean_high, mean_quantum = displayed_bounds(mean_token)
            occurrence, occurrence_low, occurrence_high, occurrence_quantum = displayed_bounds(occurrence_token)
            if occurrence_low <= 0:
                raise ValueError("Occurrence lower rounding bound must be positive for this reference")
            if mean > occurrence or mean_low > occurrence_high:
                raise ValueError("Fish mean exceeds occurrence, violating the stated conditional interpretation")
            with localcontext() as context:
                context.prec = 40
                reference = mean / occurrence
                lower = mean_low / occurrence_high
                upper = min(Decimal(1), mean_high / occurrence_low)
            if not Decimal(0) <= lower <= reference <= upper <= Decimal(1):
                raise ValueError("Conditional reference or its rounding interval is outside 0–1")
            result.append({
                "species": species,
                "year": year,
                "reported_mean_fish_pct": mean,
                "reported_occurrence_pct": occurrence,
                "detection_conditioned_fish_fraction_reference": reference,
                "rounding_lower_fraction": lower,
                "rounding_upper_fraction": upper,
                "n_table": int(text[n_index]),
                "source_table_row": row_number,
                "mean_rounding_lower_pct": mean_low,
                "mean_rounding_upper_pct": mean_high,
                "occurrence_rounding_lower_pct": occurrence_low,
                "occurrence_rounding_upper_pct": occurrence_high,
                "mean_display_quantum_pp": mean_quantum,
                "occurrence_display_quantum_pp": occurrence_quantum,
                "reported_sd_pct": Decimal(sd_token),
                "raw_cell": cell,
                "reference_unit": "fraction_0_to_1",
                "reference_scope": "reported detection; assumes identical sample set and zero fish fraction in nondetections; not positive-mass conditional fraction",
            })
    expected_keys = {(species, year) for species in ("Adelie", "Gentoo") for year in range(2009, 2015)}
    actual_keys = {(row["species"], row["year"]) for row in result}
    if len(result) != 12 or actual_keys != expected_keys:
        raise ValueError("Incomplete or duplicated fish species-season keys in primary XML")
    return result


def verify_transcription(reference_rows, long_path: Path):
    extracted = [row for row in csv_rows(long_path) if row["prey_category"] == "fish"]
    lookup = {(row["species"], int(row["season_start_year"])): row for row in extracted}
    if len(lookup) != len(extracted) or len(extracted) != len(reference_rows):
        raise ValueError("Long-form extraction has missing or duplicate fish keys")
    comparisons = 0
    fields = {
        "reported_mean_fish_pct": "mean_pct",
        "reported_occurrence_pct": "occurrence_pct",
        "reported_sd_pct": "sd_pct",
        "n_table": "n",
        "source_table_row": "source_table_row",
        "mean_rounding_lower_pct": "mean_rounding_lower_pct",
        "mean_rounding_upper_pct": "mean_rounding_upper_pct",
        "occurrence_rounding_lower_pct": "occurrence_rounding_lower_pct",
        "occurrence_rounding_upper_pct": "occurrence_rounding_upper_pct",
        "mean_display_quantum_pp": "mean_display_quantum_pp",
        "occurrence_display_quantum_pp": "occurrence_display_quantum_pp",
    }
    for original in reference_rows:
        key = original["species"], original["year"]
        derived = lookup[key]
        if int(derived["season_end_year"]) != original["year"] + 1:
            raise ValueError(f"Incorrect season label in long extraction: {key}")
        comparisons += 1
        for original_name, derived_name in fields.items():
            if Decimal(str(original[original_name])) != Decimal(derived[derived_name]):
                raise ValueError(f"Long-extraction mismatch: {key} {derived_name}")
            comparisons += 1
    return {"status": "PASS", "rows": len(reference_rows), "exact_numeric_comparisons": comparisons}


def compare_primary(reference_rows, path: Path):
    if not path.exists():
        return {"status": "PRIMARY_OUTPUT_NOT_YET_AVAILABLE", "rows": 0}
    primary = csv_rows(path)
    lookup = {(row["species"], int(row["year"])): row for row in primary}
    expected_keys = {(row["species"], row["year"]) for row in reference_rows}
    if len(lookup) != len(primary) or set(lookup) != expected_keys:
        raise ValueError("Primary reference has missing or duplicate fish keys")
    names = ["reported_mean_fish_pct", "reported_occurrence_pct",
             "detection_conditioned_fish_fraction_reference", "rounding_lower_fraction",
             "rounding_upper_fraction"]
    differences = []
    for row in reference_rows:
        key = row["species"], row["year"]
        main_row = lookup[key]
        for name in names:
            expected, observed = float(row[name]), float(main_row[name])
            difference = abs(expected - observed)
            if not math.isclose(expected, observed, abs_tol=1e-12, rel_tol=1e-12):
                raise ValueError(f"Primary numeric mismatch: {key} {name}: {expected} vs {observed}")
            differences.append({"species": key[0], "year": key[1], "field": name, "absolute_difference": difference})
        if "not positive-mass conditional fraction" not in main_row.get("scope", ""):
            raise ValueError(f"Primary reference omits detection-versus-positive-mass distinction: {key}")
    worst = max(differences, key=lambda item: item["absolute_difference"])
    return {"status": "PASS", "rows": len(reference_rows), "numeric_comparisons": len(differences),
            "scope_checks": len(reference_rows), "absolute_tolerance": 1e-12,
            "relative_tolerance": 1e-12, "maximum_absolute_difference": worst}


def write_csv(path: Path, rows):
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: float(value) if isinstance(value, Decimal) else value for key, value in row.items()})


def run(repo_root: Path, out: Path, primary_directory: Path | None = None):
    output = out
    if primary_directory is None:
        primary_directory = repo_root / OUTPUT_PATH
    xml_path = repo_root / SOURCE_PATH / "pickett2018_europepmc.xml"
    long_path = repo_root / SOURCE_PATH / "pickett2018_table1_long.csv"
    primary_path = primary_directory / "palmer_reported_detection_reference.csv"
    if digest(xml_path) != XML_SHA256:
        raise ValueError("Primary XML hash changed")
    rows = xml_fish_rows(xml_path)
    transcription = verify_transcription(rows, long_path)
    comparison = compare_primary(rows, primary_path)
    inputs = [xml_path, long_path] + ([primary_path] if primary_path.exists() else [])
    result = {
        "status": "PASS" if comparison["status"] == "PASS" else "INDEPENDENT_REFERENCE_COMPLETE",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "source_doi": "10.1002/ece3.4445", "source_table_id": TABLE_ID,
        "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6202752/",
        "independence": "Primary XML cells parsed directly; Decimal precision inferred from raw tokens; no main analysis or extraction helper used.",
        "source_manifest": [{"file": file_label(path, repo_root), "sha256": digest(path)} for path in inputs],
        "long_transcription_verification": transcription,
        "primary_output_verification": comparison,
        "formulas": {
            "reference_fraction": "reported_mean_pct / reported_occurrence_pct",
            "lower_fraction": "mean_rounding_lower_pct / occurrence_rounding_upper_pct",
            "upper_fraction": "min(1, mean_rounding_upper_pct / occurrence_rounding_lower_pct)",
            "conditional_mean_identity": "E[q] = P(D=1) E[q|D=1] if the same observations/weights are used and q=0 when D=0",
        },
        "unit_checks": {
            "input_means_and_occurrence": "percent_0_to_100",
            "output_reference_and_bounds": "fraction_0_to_1",
            "all_bounds_contain_reported_reference": True,
            "all_bounds_within_0_1": True,
            "occurrence_lower_bounds_positive": True,
        },
        "reported_table_sample_n_totals": {
            species: sum(row["n_table"] for row in rows if row["species"] == species)
            for species in ("Adelie", "Gentoo")
        },
        "reported_methods_sample_n_totals": {"Adelie": 136, "Gentoo": 128},
        "review_notes": [
            "Palmer occurrence is reported detection, not established to mean positive fish wet mass; methods also record otolith/bone evidence.",
            "The conditional identity requires the same sample set and weighting, with zero fish fraction in nondetections; the published table alone cannot verify every individual record.",
            "Intervals concern nearest rounding to displayed precision only, not sampling uncertainty or confidence intervals.",
            "The ratio is in 0–1 fraction units; multiplying by 100 would express conditional composition in percent.",
            "Gentoo table n sums to 129 while methods report 128. These totals remain unresolved; no individual data or exact detection counts are reconstructed.",
            "No Signy–Palmer component effect comparison or Palmer component–SIC test is performed.",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "palmer_reference_independent.csv", rows)
    (output / "palmer_reference_verification.json").write_text(
        json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    return {
        "verification": result,
        "rows": [{key: float(value) if isinstance(value, Decimal) else value
                  for key, value in row.items()} for row in rows],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[5])
    parser.add_argument("--out", type=Path,
                        help="Independent output directory; defaults to the analysis output's independent/ directory")
    parser.add_argument("--primary-dir", type=Path,
                        help="Primary output directory to compare; defaults to the analysis output directory")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output_directory = args.out.resolve() if args.out else repo / OUTPUT_PATH / "independent"
    primary_directory = args.primary_dir.resolve() if args.primary_dir else repo / OUTPUT_PATH
    result = run(repo, output_directory, primary_directory)
    print(json.dumps(result["verification"], ensure_ascii=False, allow_nan=False, indent=2))
