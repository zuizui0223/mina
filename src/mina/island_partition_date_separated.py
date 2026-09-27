"""Date-separated sensitivity for Palmer island-partition synchrony."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import numpy as np

from .lter import ISLANDS
from .island_partition_overlap import (
    N_SIZE_STRATA,
    _p_two_sided,
    _permute_labels,
    _size_strata,
    contrast_for_labels,
)

YEARS = tuple(range(1991, 2018))
N_PERMUTATIONS = 20_000
SEED = 20260927
MIN_SHARED = 4


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _date(value: str) -> date:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date()


def observed_units(path: str | Path) -> list[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    records: dict[tuple[str, str, int], list[tuple[date, float]]] = defaultdict(list)
    for row in rows:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS or not _finite(row.get("num_breeding_pairs")):
            continue
        try:
            census_date = _date(str(row.get("time", "")).strip())
        except (TypeError, ValueError):
            continue
        year = census_date.year
        if year not in YEARS:
            continue
        code = str(row.get("colony_code", "")).strip()
        count = float(row["num_breeding_pairs"])
        if count < 0:
            raise ValueError("negative breeding-pair count")
        records[(island, code, year)].append((census_date, count))

    by_unit: dict[tuple[str, str], dict[int, tuple[date, float]]] = defaultdict(dict)
    for (island, code, year), local in records.items():
        unique_dates = {item[0] for item in local}
        if len(unique_dates) != 1:
            raise ValueError(
                f"same colony_code has multiple census dates in one year: "
                f"{island} {code} {year} {sorted(str(x) for x in unique_dates)}"
            )
        by_unit[(island, code)][year] = (
            next(iter(unique_dates)),
            float(sum(item[1] for item in local)),
        )

    units = []
    for (island, code), series in sorted(by_unit.items()):
        if not any(count > 0 for _, count in series.values()):
            continue
        growth = {}
        for year in YEARS[1:]:
            if year not in series or year - 1 not in series:
                continue
            start_date, start_count = series[year - 1]
            end_date, end_count = series[year]
            growth[year] = {
                "value": math.log1p(end_count) - math.log1p(start_count),
                "start_date": start_date,
                "end_date": end_date,
            }
        units.append(
            {
                "island": island,
                "colony_code": code,
                "mean_log1p_abundance": float(
                    np.mean([math.log1p(count) for _, count in series.values()])
                ),
                "growth": growth,
            }
        )
    return units


def _pair_record(
    a: dict[str, object],
    b: dict[str, object],
    mode: str,
) -> dict[str, object] | None:
    ga = a["growth"]
    gb = b["growth"]
    shared = sorted(set(ga) & set(gb))
    retained = []
    for year in shared:
        aa = ga[year]
        bb = gb[year]
        start_diff = aa["start_date"] != bb["start_date"]
        end_diff = aa["end_date"] != bb["end_date"]
        if mode == "strict":
            keep = start_diff and end_diff
        elif mode == "relaxed":
            keep = start_diff or end_diff
        else:
            raise ValueError(mode)
        if keep:
            retained.append(year)
    if len(retained) < MIN_SHARED:
        return None
    xa = np.asarray([float(ga[y]["value"]) for y in retained], dtype=float)
    xb = np.asarray([float(gb[y]["value"]) for y in retained], dtype=float)
    if float(np.std(xa, ddof=1)) <= 0 or float(np.std(xb, ddof=1)) <= 0:
        return None
    r = float(np.clip(np.corrcoef(xa, xb)[0, 1], -0.999999, 0.999999))
    return {
        "r": r,
        "z": float(np.arctanh(r)),
        "weight": float(len(retained) - 3),
        "n_shared": len(retained),
    }


def pair_table(
    units: list[dict[str, object]],
    mode: str,
) -> list[dict[str, object]]:
    out = []
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            record = _pair_record(units[i], units[j], mode)
            if record is not None:
                out.append({"i": i, "j": j, **record})
    return out


def _run_mode(
    units: list[dict[str, object]],
    mode: str,
    n_permutations: int,
    seed: int,
) -> dict[str, object]:
    labels = np.asarray([str(unit["island"]) for unit in units], dtype=object)
    pairs = pair_table(units, mode)
    if not pairs:
        return {
            "mode": mode,
            "validity_pass": False,
            "reason": "no informative date-separated colony pairs",
            "n_informative_pairs": 0,
        }
    try:
        observed = contrast_for_labels(pairs, labels)
    except ValueError as exc:
        return {
            "mode": mode,
            "validity_pass": False,
            "reason": str(exc),
            "n_informative_pairs": len(pairs),
        }

    contributing = sorted(
        {
            str(labels[int(pair["i"])])
            for pair in pairs
            if labels[int(pair["i"])] == labels[int(pair["j"])]
        }
    )
    sizes = np.asarray(
        [float(unit["mean_log1p_abundance"]) for unit in units], dtype=float
    )
    strata = _size_strata(sizes, N_SIZE_STRATA)
    rng = np.random.default_rng(seed)
    null = []
    attempts = 0
    max_attempts = n_permutations * 2
    while len(null) < n_permutations and attempts < max_attempts:
        attempts += 1
        permuted = _permute_labels(labels, strata, rng)
        try:
            stat = contrast_for_labels(pairs, permuted)
        except ValueError:
            continue
        null.append(float(stat["partition_contrast_r"]))
    if len(null) < n_permutations:
        return {
            "mode": mode,
            "validity_pass": False,
            "reason": "insufficient valid label permutations",
            "n_informative_pairs": len(pairs),
            "n_valid_permutations": len(null),
        }

    arr = np.asarray(null, dtype=float)
    contrast = float(observed["partition_contrast_r"])
    p = _p_two_sided(arr, contrast)
    return {
        "mode": mode,
        "validity_pass": True,
        "n_informative_pairs": len(pairs),
        "within_contributing_islands": contributing,
        "observed": observed,
        "null": {
            "n_permutations": n_permutations,
            "seed": seed,
            "mean": float(np.mean(arr)),
            "sd": float(np.std(arr, ddof=1)),
            "q025": float(np.quantile(arr, 0.025)),
            "q975": float(np.quantile(arr, 0.975)),
            "two_sided_p": p,
        },
    }


def analyze(
    path: str | Path,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    units = observed_units(path)
    strict = _run_mode(units, "strict", n_permutations, seed)
    relaxed = _run_mode(units, "relaxed", n_permutations, seed + 1)
    supported = bool(
        strict.get("validity_pass")
        and float(strict["null"]["two_sided_p"]) <= 0.05
    )
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-island-partition-date-separated-v1",
        "n_units": len(units),
        "strict": strict,
        "relaxed_descriptive": relaxed,
        "decision": {
            "strict_same_day_batch_explanation_insufficient": supported,
            "strict_result_inconclusive": not bool(strict.get("validity_pass")),
        },
        "interpretation_boundary": {
            "tests_exact_same_date_batching_only": True,
            "does_not_rule_out_shared_observer_or_protocol_error": True,
            "does_not_identify_biological_mechanism": True,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--census", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    p.add_argument("--seed", type=int, default=SEED)
    args = p.parse_args()
    result = analyze(args.census, args.permutations, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
