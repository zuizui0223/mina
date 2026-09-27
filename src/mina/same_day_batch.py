"""Test whether exact same-day census batching predicts within-island synchrony."""
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

YEARS = tuple(range(1991, 2018))
MIN_SHARED = 4
N_PERMUTATIONS = 20_000
SEED = 20260927


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _parse_date(value: str) -> date:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date()


def load_units(path: str | Path) -> list[dict[str, object]]:
    raw: dict[tuple[str, str, int], list[tuple[date, float]]] = defaultdict(list)
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            island = str(row.get("island_name", "")).strip()
            if island not in ISLANDS or not _finite(row.get("num_breeding_pairs")):
                continue
            try:
                census_date = _parse_date(str(row.get("time", "")).strip())
            except (TypeError, ValueError):
                continue
            year = census_date.year
            if year not in YEARS:
                continue
            code = str(row.get("colony_code", "")).strip()
            count = float(row["num_breeding_pairs"])
            if count < 0:
                raise ValueError("negative breeding-pair count")
            raw[(island, code, year)].append((census_date, count))

    series: dict[tuple[str, str], dict[int, tuple[date, float]]] = defaultdict(dict)
    for (island, code, year), local in raw.items():
        dates = {d for d, _ in local}
        if len(dates) != 1:
            raise ValueError(
                f"same colony code has multiple dates within year: {island} {code} {year}"
            )
        series[(island, code)][year] = (
            next(iter(dates)),
            float(sum(value for _, value in local)),
        )

    units: list[dict[str, object]] = []
    for (island, code), values in sorted(series.items()):
        if not any(count > 0 for _, count in values.values()):
            continue
        growth: dict[int, float] = {}
        for year in YEARS[1:]:
            if year in values and year - 1 in values:
                growth[year] = (
                    math.log1p(values[year][1]) - math.log1p(values[year - 1][1])
                )
        units.append(
            {
                "island": island,
                "colony_code": code,
                "series": values,
                "growth": growth,
            }
        )
    return units


def _same_both_fraction(
    pair: dict[str, object],
    units: list[dict[str, object]],
    date_override: dict[tuple[int, int], date] | None = None,
) -> float:
    i = int(pair["i"])
    j = int(pair["j"])
    shared = tuple(int(y) for y in pair["_shared_years"])
    same_both = 0
    for year in shared:
        if date_override is None:
            a0 = units[i]["series"][year - 1][0]
            a1 = units[i]["series"][year][0]
            b0 = units[j]["series"][year - 1][0]
            b1 = units[j]["series"][year][0]
        else:
            a0 = date_override[(i, year - 1)]
            a1 = date_override[(i, year)]
            b0 = date_override[(j, year - 1)]
            b1 = date_override[(j, year)]
        same_both += int(a0 == b0 and a1 == b1)
    return same_both / len(shared)


def build_pair_records(
    units: list[dict[str, object]],
    date_override: dict[tuple[int, int], date] | None = None,
) -> list[dict[str, object]]:
    pairs: list[dict[str, object]] = []
    for i in range(len(units)):
        a = units[i]
        for j in range(i + 1, len(units)):
            b = units[j]
            if str(a["island"]) != str(b["island"]):
                continue
            shared = tuple(sorted(set(a["growth"]) & set(b["growth"])))
            if len(shared) < MIN_SHARED:
                continue
            xa = np.asarray([float(a["growth"][y]) for y in shared], dtype=float)
            xb = np.asarray([float(b["growth"][y]) for y in shared], dtype=float)
            if float(np.std(xa, ddof=1)) <= 0 or float(np.std(xb, ddof=1)) <= 0:
                continue
            r = float(np.clip(np.corrcoef(xa, xb)[0, 1], -0.999999, 0.999999))
            pair = {
                "i": i,
                "j": j,
                "island": str(a["island"]),
                "n_shared": len(shared),
                "weight": float(len(shared) - 3),
                "z_r": float(np.arctanh(r)),
                "r": r,
                "_shared_years": shared,
            }
            pair["same_both_endpoint_fraction"] = _same_both_fraction(
                pair, units, date_override
            )
            pairs.append(pair)
    if not pairs:
        raise ValueError("no informative within-island colony pairs")
    return pairs


def update_date_predictors(
    base_pairs: list[dict[str, object]],
    units: list[dict[str, object]],
    date_override: dict[tuple[int, int], date],
) -> list[dict[str, object]]:
    """Update only timing predictors; growth correlations and Fisher weights are invariant."""
    out: list[dict[str, object]] = []
    for row in base_pairs:
        copied = dict(row)
        copied["same_both_endpoint_fraction"] = _same_both_fraction(
            row, units, date_override
        )
        out.append(copied)
    return out


def focal_beta(pairs: list[dict[str, object]]) -> float:
    islands = tuple(
        island for island in ISLANDS
        if any(str(row["island"]) == island for row in pairs)
    )
    lookup = {island: k for k, island in enumerate(islands)}
    x = np.zeros((len(pairs), len(islands) + 1), dtype=float)
    y = np.empty(len(pairs), dtype=float)
    w = np.empty(len(pairs), dtype=float)
    for row_index, row in enumerate(pairs):
        x[row_index, lookup[str(row["island"])]] = 1.0
        x[row_index, -1] = float(row["same_both_endpoint_fraction"])
        y[row_index] = float(row["z_r"])
        w[row_index] = float(row["weight"])
    root = np.sqrt(w)
    beta, _, rank, _ = np.linalg.lstsq(x * root[:, None], y * root, rcond=None)
    if rank != x.shape[1]:
        raise ValueError("rank-deficient same-day batch model")
    return float(beta[-1])


def permuted_dates(
    units: list[dict[str, object]],
    rng: np.random.Generator,
) -> dict[tuple[int, int], date]:
    override: dict[tuple[int, int], date] = {}
    by_island_year: dict[tuple[str, int], list[int]] = defaultdict(list)
    for idx, unit in enumerate(units):
        for year in unit["series"]:
            by_island_year[(str(unit["island"]), int(year))].append(idx)
    for (_, year), indices in by_island_year.items():
        dates = [units[idx]["series"][year][0] for idx in indices]
        shuffled = rng.permutation(np.asarray(dates, dtype=object))
        for idx, value in zip(indices, shuffled.tolist()):
            override[(idx, year)] = value
    return override


def analyze(
    path: str | Path,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    units = load_units(path)
    observed_pairs = build_pair_records(units)
    beta = focal_beta(observed_pairs)
    rng = np.random.default_rng(seed)
    null = np.empty(n_permutations, dtype=float)
    for k in range(n_permutations):
        override = permuted_dates(units, rng)
        null_pairs = update_date_predictors(observed_pairs, units, override)
        null[k] = focal_beta(null_pairs)
    p_upper = float((1 + np.sum(null >= beta)) / (n_permutations + 1))
    same = np.asarray(
        [float(row["same_both_endpoint_fraction"]) for row in observed_pairs],
        dtype=float,
    )
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-same-day-batch-v1",
        "n_units": len(units),
        "n_within_island_pairs": len(observed_pairs),
        "observed": {
            "same_day_fraction_mean": float(np.mean(same)),
            "same_day_fraction_median": float(np.median(same)),
            "same_day_fraction_min": float(np.min(same)),
            "same_day_fraction_max": float(np.max(same)),
            "focal_beta_fisher_z_per_fraction": beta,
        },
        "null": {
            "n_permutations": n_permutations,
            "seed": seed,
            "mean": float(np.mean(null)),
            "sd": float(np.std(null, ddof=1)),
            "q05": float(np.quantile(null, 0.05)),
            "q95": float(np.quantile(null, 0.95)),
            "upper_p": p_upper,
        },
        "decision": {
            "simple_same_day_batch_pattern_supported": bool(beta > 0 and p_upper <= 0.05),
            "direction": "positive" if beta > 0 else "negative" if beta < 0 else "zero",
        },
        "interpretation_boundary": {
            "tests_exact_same_day_pairing_only": True,
            "does_not_rule_out_observer_or_protocol_error": True,
            "positive_slope_not_unique_to_observation_error": True,
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
