"""Pre-extinction reproductive-success test for Palmer Adelie colonies."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .colony_extinction_hazard import ISLANDS, build_transitions, load_rows

N_PERMUTATIONS = 100_000
PRIMARY_SEED = 20260940
SIZE_SEED = 20260941


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_chick_rows(path: str | Path) -> list[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out: list[dict[str, object]] = []
    seen: set[tuple[str, str, int]] = set()
    for row in rows:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS:
            continue
        if not _finite(row.get("num_breeding_pairs")) or not _finite(
            row.get("num_chicks")
        ):
            continue
        adults = float(row["num_breeding_pairs"])
        chicks = float(row["num_chicks"])
        if adults <= 0 or chicks < 0:
            continue
        time = str(row.get("time", "")).strip()
        try:
            census_year = int(time[:4])
        except (TypeError, ValueError):
            continue
        season = census_year - 1
        code = str(row.get("colony_code", "")).strip()
        key = (island, code, season)
        if key in seen:
            raise ValueError(f"duplicate usable chick-success row: {key!r}")
        seen.add(key)
        out.append(
            {
                "island": island,
                "colony_code": code,
                "season": season,
                "adult_pairs": adults,
                "chicks": chicks,
                "chicks_per_pair": chicks / adults,
                "census_time": str(row.get("census_time", "")).strip(),
            }
        )
    if not out:
        raise ValueError("no usable chick-success rows")
    return out


def matched_rows(
    adult_path: str | Path,
    chick_path: str | Path,
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    minimum_prior_count: float = 1.0,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    adult_rows = load_rows(adult_path)
    transitions = build_transitions(
        adult_rows,
        followup_zero_years=2,
        allowed_islands=allowed_islands,
        minimum_prior_count=minimum_prior_count,
    )
    chick = load_chick_rows(chick_path)
    chick_lookup = {
        (str(r["island"]), str(r["colony_code"]), int(r["season"])): r
        for r in chick
    }
    out: list[dict[str, object]] = []
    compared = 0
    exact = 0
    abs_diff: list[float] = []
    for row in transitions:
        key = (
            str(row["island"]),
            str(row["colony_code"]),
            int(row["start_year"]),
        )
        c = chick_lookup.get(key)
        if c is None:
            continue
        prior = float(row["prior_count"])
        chick_adults = float(c["adult_pairs"])
        compared += 1
        if prior == chick_adults:
            exact += 1
        abs_diff.append(abs(prior - chick_adults))
        out.append(
            {
                "island": str(row["island"]),
                "colony_code": str(row["colony_code"]),
                "season": int(row["start_year"]),
                "event_next_year": int(row["event"]),
                "adult_prior_count": prior,
                "adult_prior_share": float(row["prior_share"]),
                "chick_dataset_adult_pairs": chick_adults,
                "chicks": float(c["chicks"]),
                "chicks_per_pair": float(c["chicks_per_pair"]),
            }
        )
    if not out:
        raise ValueError("no adult-transition/chick-success matches")
    return out, {
        "n_matched": compared,
        "n_exact_adult_denominator": exact,
        "exact_fraction": exact / compared if compared else None,
        "median_absolute_pair_difference": (
            float(np.median(abs_diff)) if abs_diff else None
        ),
    }


def _rank_fraction(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=float)
    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and values[order[end]] == values[order[start]]:
            end += 1
        avg_rank = 0.5 * ((start + 1) + end)
        ranks[order[start:end]] = avg_rank
        start = end
    return ranks / (values.size + 1.0)


def informative_sets(
    rows: list[dict[str, object]],
    *,
    transform: str = "raw",
) -> list[dict[str, object]]:
    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["island"]), int(row["season"]))].append(row)

    out: list[dict[str, object]] = []
    for (island, season), local in sorted(groups.items()):
        if len(local) < 3:
            continue
        event = np.asarray([int(r["event_next_year"]) for r in local], dtype=int)
        k = int(np.sum(event))
        if k <= 0 or k >= len(local):
            continue
        raw = np.asarray([float(r["chicks_per_pair"]) for r in local], dtype=float)
        if transform == "raw":
            y = raw
        elif transform == "log1p":
            y = np.log1p(raw)
        elif transform == "rank":
            y = _rank_fraction(raw)
        else:
            raise ValueError(transform)
        sd = float(np.std(y, ddof=1))
        if sd <= 0:
            continue
        z_success = (y - float(np.mean(y))) / sd

        size = np.log1p(
            np.asarray([float(r["adult_prior_count"]) for r in local], dtype=float)
        )
        size_sd = float(np.std(size, ddof=1))
        z_size = (
            (size - float(np.mean(size))) / size_sd
            if size_sd > 0
            else np.zeros_like(size)
        )
        out.append(
            {
                "island": island,
                "season": season,
                "n": len(local),
                "k": k,
                "event": event,
                "z_success": z_success,
                "z_size": z_size,
                "raw_success": raw,
                "rows": local,
                "observed_contrast": float(
                    np.mean(z_success[event == 1]) - np.mean(z_success[event == 0])
                ),
            }
        )
    return out


def event_success_test(
    rows: list[dict[str, object]],
    *,
    transform: str = "raw",
    permutations: int = N_PERMUTATIONS,
    seed: int = PRIMARY_SEED,
) -> dict[str, object]:
    sets = informative_sets(rows, transform=transform)
    if len(sets) < 3:
        return {
            "estimable": False,
            "reason": "fewer than three informative event-bearing matched risk sets",
            "n_event_risk_sets": len(sets),
        }
    observed = float(np.mean([float(s["observed_contrast"]) for s in sets]))
    rng = np.random.default_rng(seed)
    null = np.zeros(permutations, dtype=float)
    for risk in sets:
        y = np.asarray(risk["z_success"], dtype=float)
        n = int(risk["n"])
        k = int(risk["k"])
        scores = rng.random((permutations, n))
        idx = np.argpartition(scores, k - 1, axis=1)[:, :k]
        event_sum = y[idx].sum(axis=1)
        null += event_sum / k - (float(np.sum(y)) - event_sum) / (n - k)
    null /= len(sets)
    p = float((1 + int(np.sum(null <= observed))) / (permutations + 1))
    return {
        "estimable": True,
        "transform": transform,
        "n_event_risk_sets": len(sets),
        "n_matched_rows_in_event_sets": int(sum(int(s["n"]) for s in sets)),
        "n_events": int(sum(int(s["k"]) for s in sets)),
        "observed_contrast": observed,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_lower_p": p,
        "supported": bool(observed < 0 and p <= 0.05),
    }


def size_success_gradient(
    rows: list[dict[str, object]],
    *,
    permutations: int = N_PERMUTATIONS,
    seed: int = SIZE_SEED,
) -> dict[str, object]:
    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["island"]), int(row["season"]))].append(row)

    prepared: list[tuple[np.ndarray, np.ndarray]] = []
    for _, local in sorted(groups.items()):
        if len(local) < 3:
            continue
        x = np.log1p(
            np.asarray([float(r["adult_prior_count"]) for r in local], dtype=float)
        )
        y = np.asarray([float(r["chicks_per_pair"]) for r in local], dtype=float)
        sx = float(np.std(x, ddof=1))
        sy = float(np.std(y, ddof=1))
        if sx <= 0 or sy <= 0:
            continue
        x = (x - float(np.mean(x))) / sx
        y = (y - float(np.mean(y))) / sy
        prepared.append((x, y))
    if len(prepared) < 3:
        return {"estimable": False, "n_risk_sets": len(prepared)}

    denom = float(sum(float(x @ x) for x, _ in prepared))
    observed_num = float(sum(float(x @ y) for x, y in prepared))
    observed = observed_num / denom

    rng = np.random.default_rng(seed)
    null_num = np.zeros(permutations, dtype=float)
    for x, y in prepared:
        n = x.size
        random_order = np.argsort(rng.random((permutations, n)), axis=1)
        null_num += np.sum(x[None, :] * y[random_order], axis=1)
    null = null_num / denom
    p = float((1 + int(np.sum(null >= observed))) / (permutations + 1))
    return {
        "estimable": True,
        "n_risk_sets": len(prepared),
        "slope": observed,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": p,
        "supported": bool(observed > 0 and p <= 0.05),
    }


def event_effect_after_size(rows: list[dict[str, object]]) -> dict[str, object]:
    sets = informative_sets(rows, transform="raw")
    flat: list[tuple[str, int, float, float, float]] = []
    for risk in sets:
        for idx, row in enumerate(risk["rows"]):
            flat.append(
                (
                    str(row["island"]),
                    int(row["season"]),
                    float(risk["z_success"][idx]),
                    float(risk["z_size"][idx]),
                    float(risk["event"][idx]),
                )
            )
    if len(flat) < 10:
        return {"estimable": False, "n_rows": len(flat)}
    years = np.asarray([float(x[1]) for x in flat], dtype=float)
    year_center = years - float(np.mean(years))
    columns = [
        np.ones(len(flat), dtype=float),
        np.asarray([x[4] for x in flat], dtype=float),
        np.asarray([x[3] for x in flat], dtype=float),
        year_center,
    ]
    for island in ISLANDS[1:]:
        columns.append(
            np.asarray([1.0 if x[0] == island else 0.0 for x in flat], dtype=float)
        )
    xmat = np.column_stack(columns)
    y = np.asarray([x[2] for x in flat], dtype=float)
    beta, _, rank, _ = np.linalg.lstsq(xmat, y, rcond=None)
    if rank != xmat.shape[1]:
        return {"estimable": False, "reason": "rank-deficient OLS", "n_rows": len(flat)}
    resid = y - xmat @ beta
    dof = len(y) - xmat.shape[1]
    sigma2 = float((resid @ resid) / dof)
    cov = sigma2 * np.linalg.inv(xmat.T @ xmat)
    se = np.sqrt(np.diag(cov))
    return {
        "estimable": True,
        "n_rows": len(flat),
        "event_coefficient": float(beta[1]),
        "event_se": float(se[1]),
        "size_coefficient": float(beta[2]),
        "size_se": float(se[2]),
        "model": "z(chicks_per_pair) ~ next-year event + within-risk-set z(log1p adult pairs) + centered year + island indicators",
    }


def survivor_trajectory(
    rows: list[dict[str, object]],
) -> dict[str, object]:
    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["island"]), int(row["season"]))].append(row)
    annual: list[dict[str, object]] = []
    for (island, season), local in sorted(groups.items()):
        adult = np.asarray([float(r["adult_prior_count"]) for r in local], dtype=float)
        if float(np.sum(adult)) <= 0:
            continue
        shares = adult / float(np.sum(adult))
        neff = 1.0 / float(np.sum(shares**2))
        chicks = float(sum(float(r["chicks"]) for r in local))
        denom = float(sum(float(r["chick_dataset_adult_pairs"]) for r in local))
        if denom <= 0:
            continue
        annual.append(
            {
                "island": island,
                "season": season,
                "effective_colony_number": neff,
                "chicks_per_pair_island": chicks / denom,
                "n_matched_colonies": len(local),
            }
        )
    if len(annual) < 5:
        return {"estimable": False, "annual": annual}

    island_means: dict[str, tuple[float, float]] = {}
    for island in ISLANDS:
        local = [r for r in annual if r["island"] == island]
        if not local:
            continue
        island_means[island] = (
            float(np.mean([math.log(float(r["effective_colony_number"])) for r in local])),
            float(np.mean([float(r["chicks_per_pair_island"]) for r in local])),
        )
    x: list[float] = []
    y: list[float] = []
    for row in annual:
        island = str(row["island"])
        if island not in island_means:
            continue
        mx, my = island_means[island]
        x.append(math.log(float(row["effective_colony_number"])) - mx)
        y.append(float(row["chicks_per_pair_island"]) - my)
    xx = np.asarray(x, dtype=float)
    yy = np.asarray(y, dtype=float)
    denom = float(xx @ xx)
    slope = float((xx @ yy) / denom) if denom > 0 else None
    return {
        "estimable": slope is not None,
        "within_island_slope_success_on_log_neff": slope,
        "interpretation_direction": (
            "positive slope means reproductive success tends to decline as breeding distributions concentrate (Neff falls); negative means success tends to improve as Neff falls"
        ),
        "annual": annual,
    }


def analyze(
    adult_path: str | Path,
    chick_path: str | Path,
    *,
    permutations: int = N_PERMUTATIONS,
) -> dict[str, object]:
    matched, overlap = matched_rows(adult_path, chick_path)
    primary = event_success_test(
        matched, transform="raw", permutations=permutations, seed=PRIMARY_SEED
    )
    log_sens = event_success_test(
        matched, transform="log1p", permutations=permutations, seed=PRIMARY_SEED + 2
    )
    rank_sens = event_success_test(
        matched, transform="rank", permutations=permutations, seed=PRIMARY_SEED + 3
    )

    no_lit_rows = [r for r in matched if str(r["island"]) != "LIT"]
    no_lit = event_success_test(
        no_lit_rows, transform="raw", permutations=permutations, seed=PRIMARY_SEED + 4
    )
    ge2, _ = matched_rows(
        adult_path,
        chick_path,
        minimum_prior_count=2.0,
    )
    ge2_result = event_success_test(
        ge2, transform="raw", permutations=permutations, seed=PRIMARY_SEED + 5
    )

    size_grad = size_success_gradient(
        matched, permutations=permutations, seed=SIZE_SEED
    )
    adjusted = event_effect_after_size(matched)
    trajectory = survivor_trajectory(matched)

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-preextinction-chick-success-v1",
        "contract_id": "mina-palmer-preextinction-chick-success-v1",
        "matched_rows": len(matched),
        "season_range": [
            min(int(r["season"]) for r in matched),
            max(int(r["season"]) for r in matched),
        ],
        "denominator_overlap": overlap,
        "primary_preextinction_success": primary,
        "sensitivities": {
            "log1p_success": log_sens,
            "rank_success": rank_sens,
            "exclude_litchfield": no_lit,
            "prior_count_ge2": ge2_result,
        },
        "secondary_size_success_gradient": size_grad,
        "event_effect_after_size": adjusted,
        "survivor_island_trajectory": trajectory,
        "decision": {
            "preextinction_reproductive_failure_supported": bool(
                primary.get("supported", False)
            ),
            "social_facilitation_consistent": bool(
                size_grad.get("supported", False)
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adult-census", required=True, type=Path)
    parser.add_argument("--chicks", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    args = parser.parse_args()
    result = analyze(
        args.adult_census,
        args.chicks,
        permutations=args.permutations,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
