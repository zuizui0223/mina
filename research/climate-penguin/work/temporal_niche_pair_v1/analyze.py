"""Source-backed exploratory temporal-niche gap audit (NOT a climate forecast).

Do not use same geographical code as an independent camera. Two-sided exact
permutation is a descriptive within-one-camera diagnostic, not a pre-registered
confirmatory test or a causal climate coefficient.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "outputs/climate_penguin/phenology_observed_cohort.csv"
COHORT = ROOT / "outputs/relationship_response_v1/cohort.csv"
OUT = ROOT / "outputs/temporal_niche_pair_v1"
PAIRS = (("Adelie", "Chinstrap"), ("Adelie", "Gentoo"),
         ("Chinstrap", "Gentoo"))


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def num(value: str) -> float:
    return float(value) if value not in ("", None) else float("nan")


def mean(values) -> float:
    return sum(values) / len(values)


def slope(rows: list[dict], x: str, y: str) -> float:
    xbar = mean([r[x] for r in rows])
    ybar = mean([r[y] for r in rows])
    den = sum((r[x] - xbar) ** 2 for r in rows)
    if den <= 1e-12:
        raise ValueError("insufficient predictor variation")
    return sum((r[x] - xbar) * (r[y] - ybar) for r in rows) / den


def exact_camera_pairs(raw: list[dict]) -> list[dict]:
    grouped = defaultdict(dict)
    seen = set()
    for row in raw:
        if row["source_row_1based"] in seen:
            raise ValueError("duplicate original row ID")
        seen.add(row["source_row_1based"])
        key = (row["colname3"], int(row["season_start_year"]))
        if row["species"] in grouped[key]:
            raise ValueError("duplicate species x exact camera x season")
        grouped[key][row["species"]] = row
    pairs = []
    for (camera, year), species_rows in sorted(grouped.items()):
        for a, b in PAIRS:
            if a not in species_rows or b not in species_rows:
                continue
            ra, rb = species_rows[a], species_rows[b]
            if abs(num(ra["lat"]) - num(rb["lat"])) > 1e-7 or abs(num(ra["long"]) - num(rb["long"])) > 1e-7:
                raise ValueError("coordinate conflict for exact camera")
            ice_a, ice_b = num(ra["mdn_veintewin"]), num(rb["mdn_veintewin"])
            if abs(ice_a - ice_b) > 1e-6:
                raise ValueError("winter SIC mismatch within exact camera/year")
            pairs.append(dict(pair=a + "-" + b, camera=camera, year=year,
                              gap_days=num(rb["settlement"]) - num(ra["settlement"]),
                              winter_sic_20km_pct=ice_a,
                              air_temp_september_c=num(ra["tmean_9"]),
                              source_left=ra["source_row_1based"],
                              source_right=rb["source_row_1based"]))
    return pairs


def site_year_pairs(cohort: list[dict]) -> list[dict]:
    grouped = defaultdict(dict)
    for row in cohort:
        key = (row["scope"], row["cam"], int(row["year"]))
        if row["species"] in grouped[key]:
            raise ValueError("duplicate cohort species x site x season")
        grouped[key][row["species"]] = row
    pairs = []
    for (scope, cam, year), species_rows in sorted(grouped.items()):
        for a, b in PAIRS:
            if a not in species_rows or b not in species_rows:
                continue
            ra, rb = species_rows[a], species_rows[b]
            ice_a, ice_b = num(ra["ice10"]), num(rb["ice10"])
            pairs.append(dict(scope=scope, pair=a + "-" + b, cam=cam, year=year,
                              gap_days=num(rb["y"]) - num(ra["y"]),
                              september_sic_10pp=mean([ice_a, ice_b]),
                              exposure_difference_10pp=abs(ice_a - ice_b),
                              camera_rows_a=int(ra["camera_rows"]),
                              camera_rows_b=int(rb["camera_rows"])))
    return pairs


def within_site_slope(rows: list[dict]) -> float | None:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["cam"]].append(row)
    xx, xy = 0.0, 0.0
    for group in grouped.values():
        if len(group) < 2:
            continue
        mx = mean([r["september_sic_10pp"] for r in group])
        my = mean([r["gap_days"] for r in group])
        xx += sum((r["september_sic_10pp"] - mx) ** 2 for r in group)
        xy += sum((r["september_sic_10pp"] - mx) *
                  (r["gap_days"] - my) for r in group)
    return xy / xx if xx > 1e-12 else None


def exact_two_sided_permutation(rows: list[dict], x: str, y: str) -> float:
    if len(rows) > 8:
        raise ValueError("exact enumeration allowed for at most 8 samples")
    observed = slope(rows, x, y)
    ys = [r[y] for r in rows]
    extreme, total = 0, 0
    for perm in itertools.permutations(ys):
        changed = [dict(r, **{y: v}) for r, v in zip(rows, perm)]
        alternative = slope(changed, x, y)
        extreme += abs(alternative) >= abs(observed) - 1e-12
        total += 1
    return extreme / total


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("cannot write empty paired table")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(raw_path: Path = RAW, cohort_path: Path = COHORT, out: Path = OUT) -> dict:
    raw, cohort = read_csv(raw_path), read_csv(cohort_path)
    exact = exact_camera_pairs(raw)
    site = site_year_pairs(cohort)
    target = sorted([r for r in exact if r["pair"] == "Adelie-Chinstrap"
                     and r["camera"] == "SIGNc"], key=lambda r: r["year"])
    if len(target) != 5 or [r["year"] for r in target] != list(range(2016, 2021)):
        raise ValueError("frozen Signy exact-camera support mismatch")
    target10 = [dict(r, ice10=r["winter_sic_20km_pct"] / 10) for r in target]
    main_slope = slope(target10, "ice10", "gap_days")
    result = {
        "status": "exploratory_source_reanalysis_not_independent_validation",
        "no_climate_causal_or_future_breeding_claim": True,
        "source_rows": len(raw),
        "original_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "complete_case_sha256": hashlib.sha256(cohort_path.read_bytes()).hexdigest(),
        "exact_camera_pair_counts": {
            a + "-" + b: len([r for r in exact if r["pair"] == a + "-" + b])
            for a, b in PAIRS},
        "site_year_pair_counts": {
            scope: {a + "-" + b: len([r for r in site if r["scope"] == scope
                                     and r["pair"] == a + "-" + b])
                    for a, b in PAIRS}
            for scope in ("all_source_labels", "appendix_consistent")},
        "site_year_within_site_slope_days_per_10pp": {
            scope: {a + "-" + b: within_site_slope([
                r for r in site if r["scope"] == scope
                and r["pair"] == a + "-" + b])
                    for a, b in PAIRS}
            for scope in ("all_source_labels", "appendix_consistent")},
        "signc_adelie_chinstrap": {
            "seasons": [r["year"] for r in target10],
            "mean_gap_days": mean([r["gap_days"] for r in target10]),
            "winter_sic_slope_days_per_10pp": main_slope,
            "permutation_two_sided_p": exact_two_sided_permutation(
                target10, "ice10", "gap_days"),
            "leave_one_year_out_slopes": {
                str(r["year"]): slope([v for v in target10 if v is not r],
                                       "ice10", "gap_days")
                for r in target10},
        },
        "limitations": ["single exact camera and five seasons for Adélie–Chinstrap",
                        "same-source reanalysis; not independent replication",
                        "site codes can contain distinct cameras and cannot be considered exact shared nests",
                        "source winter SIC is not the September coastal SIC product",
                        "no concurrent breeding stage overlap, competition, or fitness observation",
                        "weather timing and species-specific confounding not resolved"],
    }
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "exact_camera_pairs.csv", exact)
    write_csv(out / "site_year_september_pairs.csv", site)
    (out / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--cohort", type=Path, default=COHORT)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    print(json.dumps(run(args.raw, args.cohort, args.out), indent=2, ensure_ascii=False))
