"""Year-block permutation diagnostic for the effective-colony result."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .colony_network import full_coefficient, loyo, transition_rows
from .lter import ISLANDS

EXPECTED_GAIN = 0.0010288409158503153
EXPECTED_BETA = 0.11679896749684501
EXPECTED_C0 = 0.07311311591779704
EXPECTED_C1 = 0.07208427500194672


def _year_blocks(rows: list[dict[str, object]]) -> dict[int, dict[str, dict[str, object]]]:
    out: dict[int, dict[str, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        year = int(row["start_year"])
        island = str(row["island"])
        if island in out[year]:
            raise ValueError(f"duplicate island/year transition: {island} {year}")
        out[year][island] = row
    return dict(out)


def availability_strata(rows: list[dict[str, object]]) -> dict[tuple[str, ...], list[int]]:
    blocks = _year_blocks(rows)
    strata: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for year, by_island in sorted(blocks.items()):
        key = tuple(sorted(by_island))
        strata[key].append(year)
    return {key: years for key, years in sorted(strata.items(), key=lambda x: x[0])}


def draw_schedule(
    rows: list[dict[str, object]],
    rng: np.random.Generator,
) -> dict[int, int]:
    schedule: dict[int, int] = {}
    for _, years in availability_strata(rows).items():
        donor = rng.permutation(np.asarray(years, dtype=int)).tolist()
        schedule.update({target: int(source) for target, source in zip(years, donor)})
    return schedule


def apply_schedule(
    rows: list[dict[str, object]],
    schedule: dict[int, int],
) -> list[dict[str, object]]:
    blocks = _year_blocks(rows)
    out: list[dict[str, object]] = []
    for row in rows:
        target_year = int(row["start_year"])
        donor_year = int(schedule[target_year])
        island = str(row["island"])
        if donor_year not in blocks or island not in blocks[donor_year]:
            raise ValueError(
                f"invalid donor mapping for {island}: {target_year}->{donor_year}"
            )
        donor = blocks[donor_year][island]
        copied = dict(row)
        copied["effective_colony_number"] = float(donor["effective_colony_number"])
        out.append(copied)
    return out




def _baseline_design(
    train: list[dict[str, object]],
    test: list[dict[str, object]],
) -> tuple[np.ndarray, np.ndarray]:
    present = {str(row["island"]) for row in train}
    levels = tuple(island for island in ISLANDS if island in present)
    lookup = {island: index for index, island in enumerate(levels)}

    def island_matrix(local: list[dict[str, object]]) -> np.ndarray:
        x = np.zeros((len(local), len(levels)), dtype=float)
        for row_index, row in enumerate(local):
            island = str(row["island"])
            if island not in lookup:
                raise ValueError(f"test island absent from training: {island}")
            x[row_index, lookup[island]] = 1.0
        return x

    xtr = island_matrix(train)
    xte = island_matrix(test)

    def train_z(
        train_values: np.ndarray,
        test_values: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        mean = float(np.mean(train_values))
        sd = float(np.std(train_values, ddof=1))
        if sd <= 0:
            raise ValueError("zero baseline predictor variance")
        return (train_values - mean) / sd, (test_values - mean) / sd

    abundance_tr = np.asarray(
        [math.log1p(float(row["current_total"])) for row in train], dtype=float
    )
    abundance_te = np.asarray(
        [math.log1p(float(row["current_total"])) for row in test], dtype=float
    )
    atr, ate = train_z(abundance_tr, abundance_te)

    year_tr = np.asarray([float(row["start_year"]) for row in train], dtype=float)
    year_te = np.asarray([float(row["start_year"]) for row in test], dtype=float)
    ytr, yte = train_z(year_tr, year_te)

    return (
        np.column_stack([xtr, atr, ytr]),
        np.column_stack([xte, ate, yte]),
    )


def _permutation_predictor_matrix(
    rows: list[dict[str, object]],
    permutations: int,
    seed: int,
) -> np.ndarray:
    blocks = _year_blocks(rows)
    row_index = {
        (int(row["start_year"]), str(row["island"])): index
        for index, row in enumerate(rows)
    }
    topology = {
        (int(row["start_year"]), str(row["island"])): math.log1p(
            float(row["effective_colony_number"])
        )
        for row in rows
    }
    strata = availability_strata(rows)
    rng = np.random.default_rng(seed)
    matrix = np.empty((len(rows), permutations), dtype=float)

    for permutation in range(permutations):
        for islands, years in strata.items():
            donors = rng.permutation(np.asarray(years, dtype=int)).tolist()
            for target, donor in zip(years, donors):
                for island in islands:
                    if island not in blocks[donor]:
                        raise ValueError(
                            f"donor island unavailable: {island} in {donor}"
                        )
                    matrix[row_index[(target, island)], permutation] = topology[
                        (donor, island)
                    ]
    return matrix


def _fast_permutation_statistics(
    rows: list[dict[str, object]],
    predictor_matrix: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Exact FWL re-expression of the frozen OLS/LOYO pipeline.

    Standardizing one added predictor does not change predictions because the
    baseline island dummies span an intercept. The standardized full-data
    coefficient is recovered by multiplying the raw FWL coefficient by that
    permutation's predictor SD.
    """
    permutations = predictor_matrix.shape[1]
    end_years = sorted({int(row["end_year"]) for row in rows})
    full_sse = np.zeros(permutations, dtype=float)
    baseline_sse = 0.0

    for held in end_years:
        train_index = np.asarray(
            [i for i, row in enumerate(rows) if int(row["end_year"]) != held],
            dtype=int,
        )
        test_index = np.asarray(
            [i for i, row in enumerate(rows) if int(row["end_year"]) == held],
            dtype=int,
        )
        train = [rows[i] for i in train_index]
        test = [rows[i] for i in test_index]
        xtr, xte = _baseline_design(train, test)
        ytr = np.asarray([float(row["next_growth"]) for row in train], dtype=float)
        yte = np.asarray([float(row["next_growth"]) for row in test], dtype=float)

        projection = np.linalg.solve(xtr.T @ xtr, xtr.T)
        beta0 = projection @ ytr
        baseline_prediction = xte @ beta0
        y_residual = ytr - xtr @ beta0

        ptr = predictor_matrix[train_index, :]
        pte = predictor_matrix[test_index, :]
        alpha = projection @ ptr
        p_residual = ptr - xtr @ alpha
        denominator = np.sum(p_residual * p_residual, axis=0)
        if np.any(denominator <= 0):
            raise ValueError("zero residual topology variance in permutation")
        gamma = (p_residual.T @ y_residual) / denominator
        test_p_residual = pte - xte @ alpha
        error = yte[:, None] - (
            baseline_prediction[:, None] + test_p_residual * gamma[None, :]
        )
        full_sse += np.sum(error * error, axis=0)
        baseline_sse += float(
            np.sum((yte - baseline_prediction) ** 2)
        )

    baseline_mse = baseline_sse / len(rows)
    gains = baseline_mse - full_sse / len(rows)

    xall, _ = _baseline_design(rows, rows)
    yall = np.asarray([float(row["next_growth"]) for row in rows], dtype=float)
    projection = np.linalg.solve(xall.T @ xall, xall.T)
    beta0 = projection @ yall
    y_residual = yall - xall @ beta0
    alpha = projection @ predictor_matrix
    p_residual = predictor_matrix - xall @ alpha
    denominator = np.sum(p_residual * p_residual, axis=0)
    raw_gamma = (p_residual.T @ y_residual) / denominator
    predictor_sd = np.std(predictor_matrix, axis=0, ddof=1)
    betas = raw_gamma * predictor_sd

    return gains, betas


def _summary(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "sd": float(np.std(values, ddof=1)),
        "q_0_025": float(np.quantile(values, 0.025)),
        "q_0_50": float(np.quantile(values, 0.50)),
        "q_0_95": float(np.quantile(values, 0.95)),
        "q_0_975": float(np.quantile(values, 0.975)),
        "q_0_99": float(np.quantile(values, 0.99)),
    }


def diagnose(
    census_path: str | Path,
    permutations: int = 20000,
    seed: int = 20260927,
) -> dict[str, object]:
    rows = transition_rows(census_path)
    observed = loyo(rows, "effective")
    observed_beta = full_coefficient(rows, "effective")
    observed_gain = float(observed["mse_gain_C0_minus_C1"])

    if len(rows) != 120 or int(observed["n_years"]) != 26:
        raise ValueError(
            f"frozen row/year drift: rows={len(rows)}, years={observed['n_years']}"
        )
    for name, got, expected in (
        ("gain", observed_gain, EXPECTED_GAIN),
        ("beta", observed_beta, EXPECTED_BETA),
        ("C0", float(observed["mse"]["C0"]), EXPECTED_C0),
        ("C1", float(observed["mse"]["C1"]), EXPECTED_C1),
    ):
        if not math.isclose(got, expected, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(f"frozen {name} drift: {got} != {expected}")

    strata = availability_strata(rows)
    predictor_matrix = _permutation_predictor_matrix(
        rows, permutations=permutations, seed=seed
    )
    gains, betas = _fast_permutation_statistics(rows, predictor_matrix)

    exceed_gain = int(np.sum(gains >= observed_gain))
    exceed_beta = int(np.sum(betas >= observed_beta))
    p_gain = (1.0 + exceed_gain) / (permutations + 1.0)
    p_beta = (1.0 + exceed_beta) / (permutations + 1.0)
    percentile = float((np.sum(gains < observed_gain) + 0.5*np.sum(gains == observed_gain)) / permutations)

    return {
        "schema_version": 1,
        "analysis_id": "mina-neff-year-block-permutation-v1",
        "status": "post_positive_uncertainty_diagnostic",
        "permutations": permutations,
        "seed": seed,
        "strata": [
            {
                "islands": list(key),
                "years": years,
                "n_years": len(years),
            }
            for key, years in strata.items()
        ],
        "observed": {
            "n_rows": len(rows),
            "n_end_years": int(observed["n_years"]),
            "c0_mse": float(observed["mse"]["C0"]),
            "c1_mse": float(observed["mse"]["C1"]),
            "mse_gain_c0_minus_c1": observed_gain,
            "full_data_coefficient": observed_beta,
        },
        "gain_null": {
            **_summary(gains),
            "proportion_gain_positive": float(np.mean(gains > 0)),
            "observed_percentile": percentile,
            "exceedances_ge_observed": exceed_gain,
            "one_sided_permutation_p": p_gain,
        },
        "coefficient_null": {
            **_summary(betas),
            "proportion_beta_positive": float(np.mean(betas > 0)),
            "exceedances_ge_observed": exceed_beta,
            "one_sided_permutation_p": p_beta,
        },
        "decision": {
            "gain_unusual_at_0_05": bool(p_gain <= 0.05),
            "coefficient_unusual_at_0_05": bool(p_beta <= 0.05),
        },
        "boundary": {
            "post_positive_diagnostic_not_independent_confirmation": True,
            "baseline_response_and_loyo_folds_fixed": True,
            "only_effective_colony_number_year_alignment_permuted": True,
            "causal_inference": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=20260927)
    args = parser.parse_args()
    result = diagnose(args.census, args.permutations, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
