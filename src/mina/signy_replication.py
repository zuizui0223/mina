"""Independent Signy replication of Palmer performance-linked redistribution."""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.audit_signy_replication_support import read_official_zip, season_start
from mina.performance_redistribution_lags import (
    _beta_from_batch,
    _prepare_model,
    lag_panel,
    performance_rows,
)
from mina.win_stay_lose_switch import p3_freedman_lane

EXPECTED_CSV_SHA256 = "585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62"
PRIMARY_PERMUTATIONS = 100_000
PRIMARY_SEED = 20261010
HINGE_SEED = 20261011
ATOMIC_LAG2_SEED = 20261012
ATOMIC_HINGE_SEED = 20261013
COMMENT_LAG2_SEED = 20261014
COMMENT_HINGE_SEED = 20261015
COMMENT_FLAG_RE = re.compile(
    r"(unreliable|logistical constraint|optimum time|late count|late survey|"
    r"base.*open.*late|base.*shut.*early|prevented.*count)",
    flags=re.IGNORECASE,
)
WINDOW_START = 1996
WINDOW_END = 2019


def _number(value) -> float | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if text in {"", "NA", "NaN", "nan"}:
        return None
    try:
        out = float(text)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def build_signy_rows(
    frame: pd.DataFrame,
    *,
    atomic_only: bool = False,
    exclude_comment_flagged_seasons: bool = False,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    required = {
        "SEASON",
        "COLONY",
        "TOTAL_NUMBER_OF_PAIRS",
        "TOTAL_NUMBER_OF_CHICKS",
        "COMMENTS",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing official Signy columns: {sorted(missing)}")

    rows = []
    for idx, row in frame.iterrows():
        season = season_start(row["SEASON"])
        if season is None or not WINDOW_START <= season <= WINDOW_END:
            continue
        colony = str(row["COLONY"]).strip()
        if not colony or colony.lower() in {"nan", "none", "na"}:
            continue
        comment = "" if pd.isna(row["COMMENTS"]) else str(row["COMMENTS"])
        rows.append(
            {
                "source_row": int(idx),
                "season": int(season),
                "colony": colony,
                "pairs": _number(row["TOTAL_NUMBER_OF_PAIRS"]),
                "chicks": _number(row["TOTAL_NUMBER_OF_CHICKS"]),
                "comment": comment,
            }
        )

    flagged_seasons = sorted(
        {
            int(row["season"])
            for row in rows
            if COMMENT_FLAG_RE.search(str(row["comment"]))
        }
    )

    if atomic_only:
        rows = [row for row in rows if "+" not in str(row["colony"])]
    if exclude_comment_flagged_seasons:
        flagged = set(flagged_seasons)
        rows = [row for row in rows if int(row["season"]) not in flagged]

    seen: set[tuple[int, str]] = set()
    adults: list[dict[str, object]] = []
    chicks: list[dict[str, object]] = []
    for row in rows:
        key = (int(row["season"]), str(row["colony"]))
        if key in seen:
            raise ValueError(f"duplicate literal colony-season in Signy source: {key}")
        seen.add(key)

        pairs = row["pairs"]
        chick_count = row["chicks"]
        if pairs is not None:
            if float(pairs) < 0:
                raise ValueError(f"negative Signy breeding pairs: {key}")
            adults.append(
                {
                    "island": "SIG",
                    "colony": str(row["colony"]),
                    "year": int(row["season"]),
                    "adult_pairs": float(pairs),
                }
            )
        if (
            pairs is not None
            and float(pairs) > 0
            and chick_count is not None
            and float(chick_count) >= 0
        ):
            chicks.append(
                {
                    "island": "SIG",
                    "colony": str(row["colony"]),
                    "season": int(row["season"]),
                    "chicks": float(chick_count),
                    "chick_denominator": float(pairs),
                }
            )

    meta = {
        "atomic_only": bool(atomic_only),
        "exclude_comment_flagged_seasons": bool(exclude_comment_flagged_seasons),
        "comment_flagged_seasons": flagged_seasons,
        "retained_source_rows": int(len(rows)),
        "adult_rows": int(len(adults)),
        "performance_input_rows": int(len(chicks)),
        "literal_labels": sorted({str(row["colony"]) for row in rows}),
        "seasons": sorted({int(row["season"]) for row in rows}),
    }
    return adults, chicks, meta


def _performance_groups(
    performance: list[dict[str, object]],
) -> dict[tuple[str, int], tuple[list[str], np.ndarray]]:
    by_perf: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in performance:
        by_perf[(str(row["island"]), int(row["season"]))].append(row)
    groups = {}
    for key, local in by_perf.items():
        local = sorted(local, key=lambda r: str(r["colony"]))
        groups[key] = (
            [str(r["colony"]) for r in local],
            np.asarray([float(r["state"]) for r in local], dtype=float),
        )
    return groups


def permutation_single_lag(
    panel: list[dict[str, object]],
    performance: list[dict[str, object]],
    *,
    permutations: int,
    seed: int,
    batch_size: int = 1000,
) -> dict[str, object]:
    if not panel:
        raise ValueError("empty Signy lag panel")
    model = _prepare_model(panel, performance)
    observed = float(model["observed"])
    perf_groups = _performance_groups(performance)
    rng = np.random.default_rng(seed)
    null = np.empty(permutations, dtype=float)

    offset = 0
    keys = sorted(perf_groups)
    while offset < permutations:
        batch = min(batch_size, permutations - offset)
        x = np.empty((batch, len(panel)), dtype=float)
        for key in keys:
            info = model["group_rows"].get(key)
            if info is None:
                continue
            _, values = perf_groups[key]
            row_indices, source_positions = info
            order = np.argsort(rng.random((batch, len(values))), axis=1)
            assigned = values[order]
            x[:, row_indices] = assigned[:, source_positions]
        null[offset : offset + batch] = _beta_from_batch(x, model)
        offset += batch

    p = float((1 + int(np.sum(null >= observed))) / (permutations + 1))
    return {
        "n_rows": int(len(panel)),
        "beta": observed,
        "permutations": int(permutations),
        "seed": int(seed),
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": p,
        "supported": bool(observed > 0 and p <= 0.05),
    }


def _observed_lag(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
    lag: int,
) -> dict[str, object]:
    panel = lag_panel(
        adults,
        performance,
        lag,
        allowed_islands=("SIG",),
    )
    model = _prepare_model(panel, performance)
    return {
        "lag": int(lag),
        "n_rows": int(len(panel)),
        "beta": float(model["observed"]),
    }


def run_configuration(
    frame: pd.DataFrame,
    *,
    atomic_only: bool,
    exclude_comment_flagged_seasons: bool,
    lag2_seed: int,
    hinge_seed: int,
    permutations: int,
) -> dict[str, object]:
    adults, chicks, source_meta = build_signy_rows(
        frame,
        atomic_only=atomic_only,
        exclude_comment_flagged_seasons=exclude_comment_flagged_seasons,
    )
    performance = performance_rows(
        adults,
        chicks,
        allowed_islands=("SIG",),
        metric="pearson",
    )
    panel2 = lag_panel(
        adults,
        performance,
        2,
        allowed_islands=("SIG",),
    )
    predictor_seasons = sorted({int(r["season"]) for r in panel2})
    colonies = sorted({str(r["colony"]) for r in panel2})

    lag2 = permutation_single_lag(
        panel2,
        performance,
        permutations=permutations,
        seed=lag2_seed,
    )
    hinge = p3_freedman_lane(
        panel2,
        permutations=permutations,
        seed=hinge_seed,
    )
    return {
        "source_meta": source_meta,
        "performance_rows": int(len(performance)),
        "performance_seasons": int(
            len({int(r["season"]) for r in performance})
        ),
        "lag2_support": {
            "rows": int(len(panel2)),
            "predictor_seasons": predictor_seasons,
            "n_predictor_seasons": int(len(predictor_seasons)),
            "colonies": colonies,
            "n_colonies": int(len(colonies)),
        },
        "lag_profile_descriptive": {
            "lag_1": _observed_lag(adults, performance, 1),
            "lag_2": {
                "lag": 2,
                "n_rows": int(len(panel2)),
                "beta": float(lag2["beta"]),
            },
            "lag_3": _observed_lag(adults, performance, 3),
        },
        "primary_lag2": lag2,
        "secondary_hinge": hinge,
    }


def analyze_official_zip(
    path: Path,
    *,
    permutations: int = PRIMARY_PERMUTATIONS,
) -> dict[str, object]:
    frame, source = read_official_zip(path)
    actual_sha = str(source["selected_csv_sha256"])
    if actual_sha != EXPECTED_CSV_SHA256:
        raise ValueError(
            f"official Signy CSV hash drift: {actual_sha} != {EXPECTED_CSV_SHA256}"
        )

    primary = run_configuration(
        frame,
        atomic_only=False,
        exclude_comment_flagged_seasons=False,
        lag2_seed=PRIMARY_SEED,
        hinge_seed=HINGE_SEED,
        permutations=permutations,
    )
    support = primary["lag2_support"]
    if not (
        int(support["n_predictor_seasons"]) >= 8
        and int(support["n_colonies"]) >= 4
        and int(support["rows"]) >= 40
    ):
        raise ValueError(f"Signy primary support gate drift: {support}")

    atomic = run_configuration(
        frame,
        atomic_only=True,
        exclude_comment_flagged_seasons=False,
        lag2_seed=ATOMIC_LAG2_SEED,
        hinge_seed=ATOMIC_HINGE_SEED,
        permutations=permutations,
    )
    comment = run_configuration(
        frame,
        atomic_only=False,
        exclude_comment_flagged_seasons=True,
        lag2_seed=COMMENT_LAG2_SEED,
        hinge_seed=COMMENT_HINGE_SEED,
        permutations=permutations,
    )

    primary_supported = bool(primary["primary_lag2"]["supported"])
    hinge_supported = bool(primary["secondary_hinge"]["supported"])
    if primary_supported:
        if hinge_supported:
            interpretation = (
                "Signy independently replicates the Palmer-supported lag-2 "
                "performance-linked redistribution signal and additionally "
                "shows the prespecified lose-switch asymmetry that Palmer did not."
            )
        else:
            interpretation = (
                "Signy independently replicates the Palmer-supported lag-2 "
                "performance-linked redistribution signal, while the specific "
                "lose-switch asymmetry remains unsupported."
            )
    else:
        interpretation = (
            "The Palmer lag-2 performance-linked redistribution signal does "
            "not replicate at Signy under the frozen comparable design; the "
            "secondary hinge cannot rescue the failed primary replication."
        )

    return {
        "schema_version": 1,
        "analysis_id": "mina-signy-performance-redistribution-replication-v1",
        "contract_id": "mina-signy-win-stay-lose-switch-replication-v1",
        "source": {
            "official_doi": "10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
            "selected_csv": source["selected_csv"],
            "selected_csv_sha256": actual_sha,
            "rows": int(len(frame)),
        },
        "primary": primary,
        "sensitivities": {
            "atomic_label_only": atomic,
            "comment_flag_exclusion": comment,
        },
        "decision": {
            "primary_lag2_replication_supported": primary_supported,
            "secondary_lose_switch_hinge_supported": hinge_supported,
            "atomic_lag2_direction_consistent": bool(
                float(atomic["primary_lag2"]["beta"]) > 0
            ),
            "comment_filtered_lag2_direction_consistent": bool(
                float(comment["primary_lag2"]["beta"]) > 0
            ),
        },
        "ecological_interpretation": interpretation,
        "claim_boundary": [
            "Do not infer individual breeding dispersal, prospecting or cue use from colony counts.",
            "Do not call a positive Signy hinge replication of a Palmer lose-switch mechanism because Palmer P3 was not supported.",
            "Do not let the secondary hinge rescue a null lag-2 primary replication.",
            "Treat literal colony labels exactly as published; the pooled A1 + A60 label is never split post hoc.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official-zip", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=PRIMARY_PERMUTATIONS)
    args = parser.parse_args()

    result = analyze_official_zip(
        args.official_zip,
        permutations=args.permutations,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
