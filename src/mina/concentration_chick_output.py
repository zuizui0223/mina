"""Test whether Palmer breeder concentration predicts denominator-free chick output."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ISLANDS = ("CHR", "COR", "HUM", "LIT", "TOR")
N_PERMUTATIONS = 20_000
SEED = 20260929


def _finite(v):
    if v in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def load_adult(path):
    with Path(path).open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        raw = list(csv.DictReader(handle))
    out = []
    seen = set()
    for row in raw:
        island = str(
            row.get("island_name", "")
        ).strip()
        if (
            island not in ISLANDS
            or not _finite(
                row.get("num_breeding_pairs")
            )
        ):
            continue
        year_text = str(
            row.get("time", "")
        ).strip()
        try:
            year = int(year_text[:4])
        except (TypeError, ValueError):
            continue
        code = str(
            row.get("colony_code", "")
        ).strip()
        study = str(
            row.get("study_name", "")
        ).strip()
        count = float(
            row["num_breeding_pairs"]
        )
        if count < 0:
            raise ValueError(
                "negative adult count"
            )
        key = (
            study,
            year,
            island,
            code,
        )
        if key in seen:
            raise ValueError(
                f"duplicate adult key {key!r}"
            )
        seen.add(key)
        out.append(
            {
                "year": year,
                "island": island,
                "code": code,
                "count": count,
            }
        )
    if not out:
        raise ValueError("no adult rows")
    return out


def load_chicks(path):
    with Path(path).open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        raw = list(csv.DictReader(handle))
    out = []
    seen = set()
    for row in raw:
        island = str(
            row.get("island_name", "")
        ).strip()
        if (
            island not in ISLANDS
            or not _finite(
                row.get("num_chicks")
            )
        ):
            continue
        study = str(
            row.get("study_name", "")
        ).strip()
        if (
            len(study) != 7
            or not study.startswith("PAL")
            or not study[3:].isdigit()
        ):
            raise ValueError(
                f"unparseable PAL study season: {study!r}"
            )
        start_yy = int(study[3:5])
        end_yy = int(study[5:7])
        season = (
            1900 + start_yy
            if start_yy >= 90
            else 2000 + start_yy
        )
        if end_yy != (season + 1) % 100:
            raise ValueError(
                f"non-consecutive PAL study season: {study!r}"
            )
        code = str(
            row.get("colony_code", "")
        ).strip()
        chicks = float(row["num_chicks"])
        if chicks < 0:
            raise ValueError(
                "negative chick count"
            )
        key = (
            island,
            code,
            season,
        )
        if key in seen:
            raise ValueError(
                f"duplicate chick key {key!r}"
            )
        seen.add(key)
        out.append(
            {
                "season": season,
                "island": island,
                "code": code,
                "chicks": chicks,
            }
        )
    if not out:
        raise ValueError("no chick rows")
    return out


def adult_states(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[
            (
                row["island"],
                row["year"],
            )
        ].append(row)
    out = {}
    for (island, year), local in sorted(
        groups.items()
    ):
        total = float(
            sum(
                row["count"]
                for row in local
            )
        )
        by_code = {
            str(row["code"]): float(
                row["count"]
            )
            for row in local
        }
        positive = np.asarray(
            [
                value
                for value in by_code.values()
                if value > 0
            ],
            dtype=float,
        )
        if total > 0 and positive.size:
            shares = positive / total
            neff = float(
                1.0
                / np.sum(
                    shares**2
                )
            )
            largest = float(
                np.max(shares)
            )
            concentration = -math.log(
                neff
            )
        else:
            neff = None
            largest = None
            concentration = None
        out[(island, year)] = {
            "island": island,
            "season": year,
            "adult_total_pairs": total,
            "by_code": by_code,
            "effective_colony_number": neff,
            "concentration": concentration,
            "largest_colony_share": largest,
        }
    return out


def chick_states(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[
            (
                row["island"],
                row["season"],
            )
        ].append(row)
    out = {}
    for (
        island,
        season,
    ), local in sorted(groups.items()):
        out[(island, season)] = {
            "total_chicks": float(
                sum(
                    row["chicks"]
                    for row in local
                )
            ),
            "codes": {
                str(row["code"])
                for row in local
            },
            "n_rows": len(local),
        }
    return out


def build_panel(
    adults,
    chicks,
    coverage_threshold=0.90,
    allowed_islands=ISLANDS,
):
    adult = adult_states(adults)
    chick = chick_states(chicks)
    allowed = set(allowed_islands)
    out = []
    for key, astate in sorted(
        adult.items()
    ):
        island, season = key
        if (
            island not in allowed
            or key not in chick
        ):
            continue
        total = float(
            astate["adult_total_pairs"]
        )
        if (
            total <= 0
            or astate[
                "concentration"
            ] is None
        ):
            continue
        cstate = chick[key]
        represented = sum(
            astate["by_code"].get(
                code, 0.0
            )
            for code in cstate["codes"]
        )
        coverage = (
            represented / total
            if total > 0
            else 0.0
        )
        if coverage < coverage_threshold:
            continue
        out.append(
            {
                "island": island,
                "season": season,
                "adult_total_pairs": total,
                "concentration": float(
                    astate[
                        "concentration"
                    ]
                ),
                "largest_colony_share": float(
                    astate[
                        "largest_colony_share"
                    ]
                ),
                "effective_colony_number": float(
                    astate[
                        "effective_colony_number"
                    ]
                ),
                "total_chicks": float(
                    cstate[
                        "total_chicks"
                    ]
                ),
                "represented_adult_fraction": float(
                    coverage
                ),
                "chick_rows": int(
                    cstate["n_rows"]
                ),
            }
        )
    return out


def _design(
    panel,
    predictor="concentration",
    ratio=False,
):
    if len(panel) < 8:
        raise ValueError(
            "too few island-season rows"
        )
    islands = sorted(
        {
            row["island"]
            for row in panel
        }
    )
    seasons = sorted(
        {
            int(row["season"])
            for row in panel
        }
    )
    columns = [
        np.ones(len(panel)),
        np.asarray(
            [
                float(
                    row[predictor]
                )
                for row in panel
            ]
        ),
    ]
    labels = [
        "intercept",
        predictor,
    ]
    if not ratio:
        columns.append(
            np.asarray(
                [
                    math.log1p(
                        float(
                            row[
                                "adult_total_pairs"
                            ]
                        )
                    )
                    for row in panel
                ]
            )
        )
        labels.append(
            "log1p_adult_total_pairs"
        )
    for island in islands[1:]:
        columns.append(
            np.asarray(
                [
                    1.0
                    if row[
                        "island"
                    ]
                    == island
                    else 0.0
                    for row in panel
                ]
            )
        )
        labels.append(
            f"island_{island}"
        )
    for season in seasons[1:]:
        columns.append(
            np.asarray(
                [
                    1.0
                    if int(
                        row[
                            "season"
                        ]
                    )
                    == season
                    else 0.0
                    for row in panel
                ]
            )
        )
        labels.append(
            f"season_{season}"
        )
    x = np.column_stack(
        columns
    )
    y = np.asarray(
        [
            (
                float(
                    row[
                        "total_chicks"
                    ]
                )
                / float(
                    row[
                        "adult_total_pairs"
                    ]
                )
            )
            if ratio
            else math.log1p(
                float(
                    row[
                        "total_chicks"
                    ]
                )
            )
            for row in panel
        ]
    )
    return x, y, labels


def _fit(
    panel,
    predictor="concentration",
    ratio=False,
):
    x, y, labels = _design(
        panel,
        predictor,
        ratio,
    )
    beta, _, rank, _ = np.linalg.lstsq(
        x,
        y,
        rcond=None,
    )
    if rank != x.shape[1]:
        raise ValueError(
            "rank deficient chick-output model"
        )
    residual = y - x @ beta
    sse = float(
        residual @ residual
    )
    dof = len(y) - x.shape[1]
    if dof <= 0:
        raise ValueError(
            "non-positive residual degrees of freedom"
        )
    sigma2 = sse / dof
    covariance = (
        sigma2
        * np.linalg.inv(
            x.T @ x
        )
    )
    se = np.sqrt(
        np.diag(covariance)
    )
    idx = labels.index(
        predictor
    )
    return {
        "n_rows": len(panel),
        "n_islands": len(
            {
                row["island"]
                for row in panel
            }
        ),
        "n_seasons": len(
            {
                row["season"]
                for row in panel
            }
        ),
        "predictor": predictor,
        "coefficient": float(
            beta[idx]
        ),
        "naive_se": float(
            se[idx]
        ),
        "wald_95ci": [
            float(
                beta[idx]
                - 1.96
                * se[idx]
            ),
            float(
                beta[idx]
                + 1.96
                * se[idx]
            ),
        ],
        "residual_dof": int(dof),
    }


def _permuted_panel(
    panel,
    predictor,
    rng,
):
    out = [
        dict(row)
        for row in panel
    ]
    indices = defaultdict(list)
    for index, row in enumerate(
        panel
    ):
        indices[
            str(
                row["island"]
            )
        ].append(index)
    for island, idx in indices.items():
        idx = sorted(
            idx,
            key=lambda i: int(
                panel[i][
                    "season"
                ]
            ),
        )
        n = len(idx)
        if n < 2:
            raise ValueError(
                "too few eligible seasons "
                f"for circular shift: {island}"
            )
        shift = int(
            rng.integers(
                1, n
            )
        )
        values = np.asarray(
            [
                float(
                    panel[i][
                        predictor
                    ]
                )
                for i in idx
            ]
        )
        shifted = np.roll(
            values,
            shift,
        )
        for i, value in zip(
            idx,
            shifted,
        ):
            out[i][
                predictor
            ] = float(value)
    return out


def circular_shift_test(
    panel,
    predictor="concentration",
    n_permutations=N_PERMUTATIONS,
    seed=SEED,
):
    observed = _fit(
        panel,
        predictor,
    )["coefficient"]
    rng = np.random.default_rng(
        seed
    )
    null = np.empty(
        n_permutations
    )
    for index in range(
        n_permutations
    ):
        null[index] = _fit(
            _permuted_panel(
                panel,
                predictor,
                rng,
            ),
            predictor,
        )["coefficient"]
    p = float(
        (
            1
            + np.sum(
                np.abs(null)
                >= abs(
                    observed
                )
            )
        )
        / (
            n_permutations
            + 1
        )
    )
    return {
        "observed_coefficient": float(
            observed
        ),
        "null_mean": float(
            np.mean(null)
        ),
        "null_q025": float(
            np.quantile(
                null, 0.025
            )
        ),
        "null_q975": float(
            np.quantile(
                null, 0.975
            )
        ),
        "two_sided_p": p,
        "n_permutations": n_permutations,
        "seed": seed,
    }


def _run(
    adults,
    chicks,
    coverage=0.90,
    allowed_islands=ISLANDS,
    predictor="concentration",
    n_permutations=N_PERMUTATIONS,
    seed=SEED,
):
    panel = build_panel(
        adults,
        chicks,
        coverage,
        allowed_islands,
    )
    fit = _fit(
        panel,
        predictor,
    )
    permutation = circular_shift_test(
        panel,
        predictor,
        n_permutations,
        seed,
    )
    return {
        "eligibility": {
            "coverage_threshold": coverage,
            "islands": list(
                allowed_islands
            ),
            "n_rows": len(panel),
        },
        "fit": fit,
        "permutation": permutation,
        "panel_summary": {
            "season_range": [
                min(
                    row["season"]
                    for row in panel
                ),
                max(
                    row["season"]
                    for row in panel
                ),
            ],
            "coverage_min": min(
                row[
                    "represented_adult_fraction"
                ]
                for row in panel
            ),
            "coverage_median": float(
                np.median(
                    [
                        row[
                            "represented_adult_fraction"
                        ]
                        for row in panel
                    ]
                )
            ),
        },
    }


def analyze(
    adult_path,
    chick_path,
    n_permutations=N_PERMUTATIONS,
    seed=SEED,
):
    adults = load_adult(
        adult_path
    )
    chicks = load_chicks(
        chick_path
    )
    primary_panel = build_panel(
        adults,
        chicks,
        0.90,
        ISLANDS,
    )
    primary = _run(
        adults,
        chicks,
        0.90,
        ISLANDS,
        "concentration",
        n_permutations,
        seed,
    )
    loo = {}
    for island in ISLANDS:
        allowed = tuple(
            value
            for value in ISLANDS
            if value != island
        )
        panel = build_panel(
            adults,
            chicks,
            0.90,
            allowed,
        )
        loo[island] = _fit(
            panel,
            "concentration",
        )

    coefficient = float(
        primary["fit"][
            "coefficient"
        ]
    )
    p = float(
        primary[
            "permutation"
        ][
            "two_sided_p"
        ]
    )
    loo_signs = [
        math.copysign(
            1,
            float(
                value[
                    "coefficient"
                ]
            ),
        )
        for value in loo.values()
        if float(
            value[
                "coefficient"
            ]
        )
        != 0
    ]
    same_positive = sum(
        sign > 0
        for sign in loo_signs
    )
    same_negative = sum(
        sign < 0
        for sign in loo_signs
    )

    ratio = _fit(
        primary_panel,
        "concentration",
        ratio=True,
    )
    largest_panel = []
    for row in primary_panel:
        enriched = dict(row)
        share = min(
            max(
                float(
                    row[
                        "largest_colony_share"
                    ]
                ),
                1e-6,
            ),
            1 - 1e-6,
        )
        enriched[
            "largest_logit"
        ] = math.log(
            share
            / (1 - share)
        )
        largest_panel.append(
            enriched
        )
    largest_fit = _fit(
        largest_panel,
        "largest_logit",
    )

    return {
        "schema_version": 1,
        "analysis_id": (
            "mina-palmer-concentration-chick-output-v1"
        ),
        "source": {
            "adult_sha256": hashlib.sha256(
                Path(
                    adult_path
                ).read_bytes()
            ).hexdigest(),
            "chick_sha256": hashlib.sha256(
                Path(
                    chick_path
                ).read_bytes()
            ).hexdigest(),
            "adult_rows": len(
                adults
            ),
            "chick_rows": len(
                chicks
            ),
        },
        "primary": primary,
        "sensitivities": {
            "coverage_095": _run(
                adults,
                chicks,
                0.95,
                ISLANDS,
                "concentration",
                n_permutations,
                seed + 1,
            ),
            "exclude_litchfield": _run(
                adults,
                chicks,
                0.90,
                tuple(
                    value
                    for value in ISLANDS
                    if value
                    != "LIT"
                ),
                "concentration",
                n_permutations,
                seed + 2,
            ),
            "largest_share_fit": largest_fit,
            "ratio_endpoint_fit": ratio,
            "leave_one_island_out": loo,
        },
        "decision": {
            "quality_refuge_supported": bool(
                coefficient > 0
                and p <= 0.05
                and same_positive >= 4
            ),
            "performance_erosion_supported": bool(
                coefficient < 0
                and p <= 0.05
                and same_negative >= 4
            ),
            "same_positive_loo": same_positive,
            "same_negative_loo": same_negative,
            "no_coherent_effect_supported": bool(
                not (
                    coefficient > 0
                    and p <= 0.05
                    and same_positive
                    >= 4
                )
                and not (
                    coefficient < 0
                    and p <= 0.05
                    and same_negative
                    >= 4
                )
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--adult-census",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--chicks",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--permutations",
        type=int,
        default=N_PERMUTATIONS,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
    )
    args = parser.parse_args()
    result = analyze(
        args.adult_census,
        args.chicks,
        args.permutations,
        args.seed,
    )
    args.out.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    args.out.write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
