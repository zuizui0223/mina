"""Year-block permutation diagnostic for the effective-colony result."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .colony_network import full_coefficient, loyo, transition_rows

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
    rng = np.random.default_rng(seed)
    gains = np.empty(permutations, dtype=float)
    betas = np.empty(permutations, dtype=float)

    for index in range(permutations):
        schedule = draw_schedule(rows, rng)
        permuted = apply_schedule(rows, schedule)
        p = loyo(permuted, "effective")
        gains[index] = float(p["mse_gain_C0_minus_C1"])
        betas[index] = float(full_coefficient(permuted, "effective"))

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
