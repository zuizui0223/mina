"""Palmer island concentration and breeding-success analysis."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .colony_extinction_hazard import load_rows as load_adult_rows
from .lter import ISLANDS

PRIMARY_ISLANDS = ("COR", "HUM", "LIT")
N_PERMUTATIONS = 100_000
SEED = 20260930


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def chick_island_totals(path: str | Path) -> dict[tuple[str, int], float]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    totals: dict[tuple[str, int], float] = defaultdict(float)
    for row in rows:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS or not _finite(row.get("num_chicks")):
            continue
        chicks = float(row["num_chicks"])
        if chicks < 0:
            raise ValueError("negative chick count")
        try:
            season = int(str(row.get("time", ""))[:4]) - 1
        except (TypeError, ValueError):
            continue
        totals[(island, season)] += chicks
    if not totals:
        raise ValueError("no chick island totals parsed")
    return dict(totals)


def adult_island_metrics(path: str | Path) -> dict[tuple[str, int], dict[str, float]]:
    rows = load_adult_rows(path)
    groups: dict[tuple[str, int], list[float]] = defaultdict(list)
    for row in rows:
        groups[(str(row["island"]), int(row["year"]))].append(float(row["count"]))
    out: dict[tuple[str, int], dict[str, float]] = {}
    for key, counts in sorted(groups.items()):
        total = float(sum(counts))
        if total <= 0:
            continue
        positive = np.asarray([value for value in counts if value > 0], dtype=float)
        shares = positive / total
        neff = float(1.0 / np.sum(shares**2))
        out[key] = {
            "adult_total": total,
            "effective_colony_number": neff,
            "active_positive_colonies": int(positive.size),
        }
    return out


def joined_panel(
    adult_census: str | Path,
    chick_census: str | Path,
    islands: tuple[str, ...] = ISLANDS,
) -> list[dict[str, object]]:
    adult = adult_island_metrics(adult_census)
    chicks = chick_island_totals(chick_census)
    out: list[dict[str, object]] = []
    for key, metrics in sorted(adult.items()):
        island, year = key
        if island not in islands or key not in chicks:
            continue
        success = float(chicks[key] / metrics["adult_total"])
        if success < 0 or success > 2:
            raise ValueError(
                f"island breeding success outside 0-2 range: {key} {success}"
            )
        out.append(
            {
                "island": island,
                "year": year,
                "adult_total": float(metrics["adult_total"]),
                "effective_colony_number": float(metrics["effective_colony_number"]),
                "active_positive_colonies": int(metrics["active_positive_colonies"]),
                "chick_total": float(chicks[key]),
                "breeding_success": success,
            }
        )
    if not out:
        raise ValueError("no joined island-season panel")
    return out


def _within_island_z(
    rows: list[dict[str, object]], field: str, transform
) -> np.ndarray:
    values = np.zeros(len(rows), dtype=float)
    by_island: dict[str, list[int]] = defaultdict(list)
    for idx, row in enumerate(rows):
        by_island[str(row["island"])].append(idx)
    for island, indices in by_island.items():
        x = np.asarray([transform(float(rows[i][field])) for i in indices], dtype=float)
        sd = float(np.std(x, ddof=1))
        if sd <= 0:
            raise ValueError(f"zero within-island variance for {field}: {island}")
        z = (x - float(np.mean(x))) / sd
        values[np.asarray(indices, dtype=int)] = z
    return values


def _control_matrix(
    rows: list[dict[str, object]],
    abundance_z: np.ndarray,
) -> np.ndarray:
    islands = sorted({str(row["island"]) for row in rows})
    years = sorted({int(row["year"]) for row in rows})
    columns = [np.ones(len(rows), dtype=float), abundance_z]
    for island in islands[1:]:
        columns.append(
            np.asarray([1.0 if str(row["island"]) == island else 0.0 for row in rows])
        )
    for year in years[1:]:
        columns.append(
            np.asarray([1.0 if int(row["year"]) == year else 0.0 for row in rows])
        )
    return np.column_stack(columns)


def _residualize(matrix: np.ndarray, value: np.ndarray) -> np.ndarray:
    beta, _, _, _ = np.linalg.lstsq(matrix, value, rcond=None)
    return value - matrix @ beta


def fit_partial_coefficient(
    rows: list[dict[str, object]],
) -> dict[str, object]:
    neff_z = _within_island_z(rows, "effective_colony_number", np.log)
    abundance_z = _within_island_z(rows, "adult_total", np.log1p)
    y = np.asarray([float(row["breeding_success"]) for row in rows], dtype=float)
    controls = _control_matrix(rows, abundance_z)
    x_resid = _residualize(controls, neff_z)
    y_resid = _residualize(controls, y)
    denom = float(np.dot(x_resid, x_resid))
    if denom <= 1e-12:
        raise ValueError("Neff coefficient not estimable after controls")
    beta = float(np.dot(x_resid, y_resid) / denom)
    return {
        "beta_neff": beta,
        "x_resid": x_resid,
        "y_resid": y_resid,
        "denom": denom,
        "neff_z": neff_z,
        "abundance_z": abundance_z,
    }


def circular_shift_test(
    rows: list[dict[str, object]],
    *,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    fit = fit_partial_coefficient(rows)
    observed = float(fit["beta_neff"])
    x_resid = np.asarray(fit["x_resid"], dtype=float)
    y_resid = np.asarray(fit["y_resid"], dtype=float)
    denom = float(fit["denom"])

    by_island: dict[str, list[int]] = defaultdict(list)
    for idx, row in enumerate(rows):
        by_island[str(row["island"])].append(idx)

    rng = np.random.default_rng(seed)
    null_num = np.zeros(n_permutations, dtype=float)
    shift_diagnostics: dict[str, object] = {}
    for island, indices in sorted(by_island.items()):
        indices = sorted(indices, key=lambda idx: int(rows[idx]["year"]))
        x = x_resid[np.asarray(indices, dtype=int)]
        y = y_resid[np.asarray(indices, dtype=int)]
        contributions = np.asarray(
            [float(np.dot(x, np.roll(y, shift))) for shift in range(len(indices))],
            dtype=float,
        )
        shifts = rng.integers(0, len(indices), size=n_permutations)
        null_num += contributions[shifts]
        shift_diagnostics[island] = {
            "n_years": len(indices),
            "year_range": [
                int(rows[indices[0]]["year"]),
                int(rows[indices[-1]]["year"]),
            ],
        }

    null = null_num / denom
    p = (1 + int(np.sum(np.abs(null) >= abs(observed)))) / (n_permutations + 1)
    return {
        "n_rows": len(rows),
        "n_islands": len(by_island),
        "beta_neff": observed,
        "null_mean": float(np.mean(null)),
        "null_sd": float(np.std(null, ddof=1)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q50": float(np.quantile(null, 0.5)),
        "null_q975": float(np.quantile(null, 0.975)),
        "two_sided_p": float(p),
        "supported": bool(p <= 0.05),
        "shift_diagnostics": shift_diagnostics,
    }


def first_difference_sensitivity(rows: list[dict[str, object]]) -> dict[str, object]:
    by_island: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_island[str(row["island"])].append(row)

    changes: list[dict[str, float | int | str]] = []
    for island, local in sorted(by_island.items()):
        local = sorted(local, key=lambda row: int(row["year"]))
        for previous, current in zip(local[:-1], local[1:]):
            if int(current["year"]) - int(previous["year"]) != 1:
                continue
            changes.append(
                {
                    "island": island,
                    "end_year": int(current["year"]),
                    "dy": float(current["breeding_success"])
                    - float(previous["breeding_success"]),
                    "dx": math.log(float(current["effective_colony_number"]))
                    - math.log(float(previous["effective_colony_number"])),
                    "dn": math.log1p(float(current["adult_total"]))
                    - math.log1p(float(previous["adult_total"])),
                }
            )
    if len(changes) < 10:
        raise ValueError("too few first differences")

    by_year: dict[int, list[int]] = defaultdict(list)
    for idx, row in enumerate(changes):
        by_year[int(row["end_year"])].append(idx)
    dy = np.asarray([float(row["dy"]) for row in changes], dtype=float)
    dx = np.asarray([float(row["dx"]) for row in changes], dtype=float)
    dn = np.asarray([float(row["dn"]) for row in changes], dtype=float)
    for indices in by_year.values():
        ii = np.asarray(indices, dtype=int)
        dy[ii] -= float(np.mean(dy[ii]))
        dx[ii] -= float(np.mean(dx[ii]))
        dn[ii] -= float(np.mean(dn[ii]))

    x = np.column_stack([dx, dn])
    beta, _, rank, _ = np.linalg.lstsq(x, dy, rcond=None)
    if rank < 2:
        raise ValueError("rank-deficient first-difference sensitivity")
    return {
        "n_changes": len(changes),
        "beta_delta_log_neff": float(beta[0]),
        "beta_delta_log_abundance": float(beta[1]),
    }


def coefficient_only(rows: list[dict[str, object]]) -> dict[str, object]:
    fit = fit_partial_coefficient(rows)
    return {
        "n_rows": len(rows),
        "beta_neff": float(fit["beta_neff"]),
    }


def analyze(
    adult_census: str | Path,
    chick_census: str | Path,
    *,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_permutations < 999:
        raise ValueError("at least 999 permutations required")

    primary_rows = joined_panel(adult_census, chick_census, PRIMARY_ISLANDS)
    primary = circular_shift_test(
        primary_rows,
        n_permutations=n_permutations,
        seed=seed,
    )
    first_diff = first_difference_sensitivity(primary_rows)
    cor_hum = joined_panel(adult_census, chick_census, ("COR", "HUM"))
    cor_hum_result = circular_shift_test(
        cor_hum,
        n_permutations=n_permutations,
        seed=seed + 1,
    )
    all_five = joined_panel(adult_census, chick_census, ISLANDS)
    all_five_result = coefficient_only(all_five)

    success_values = np.asarray(
        [float(row["breeding_success"]) for row in all_five], dtype=float
    )
    association = bool(primary["supported"])
    beta = float(primary["beta_neff"])
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-concentration-chick-success-v1",
        "contract_id": "mina-palmer-concentration-chick-success-v1",
        "source": {
            "adult_sha256": hashlib.sha256(Path(adult_census).read_bytes()).hexdigest(),
            "chick_sha256": hashlib.sha256(Path(chick_census).read_bytes()).hexdigest(),
        },
        "primary": primary,
        "sensitivities": {
            "first_difference": first_diff,
            "cor_hum_only": cor_hum_result,
            "all_five_descriptive": all_five_result,
        },
        "success_denominator_check": {
            "all_five_n": len(all_five),
            "min": float(np.min(success_values)),
            "median": float(np.median(success_values)),
            "max": float(np.max(success_values)),
            "n_outside_0_2": int(np.sum((success_values < 0) | (success_values > 2))),
        },
        "decision": {
            "association_supported": association,
            "reproductive_deterioration_supported": bool(association and beta > 0),
            "selective_retreat_supported": bool(association and beta < 0),
            "breeding_success_pathway_nonconfirmatory": bool(not association),
        },
        "direction": (
            "concentration_associated_with_lower_success"
            if association and beta > 0
            else "concentration_associated_with_higher_success"
            if association and beta < 0
            else "nonconfirmatory"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adult-census", required=True, type=Path)
    parser.add_argument("--chick-census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = analyze(
        args.adult_census,
        args.chick_census,
        n_permutations=args.permutations,
        seed=args.seed,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
