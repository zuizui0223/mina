"""Exploratory Signy challenge of the Palmer short adult-memory lag window."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.audit_signy_replication_support import read_official_zip
from mina.performance_redistribution_lags import (
    _beta_from_batch,
    _prepare_model,
    lag_panel,
    performance_rows,
)
from mina.signy_replication import (
    EXPECTED_CSV_SHA256,
    build_signy_rows,
)

N_PERMUTATIONS = 100_000
SEED_PRIMARY = 20261020
SEED_ATOMIC = 20261021
SEED_COMMENT = 20261022


def _perf_groups(performance: list[dict[str, object]]):
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in performance:
        grouped[(str(row["island"]), int(row["season"]))].append(row)
    out = {}
    for key, rows in grouped.items():
        rows = sorted(rows, key=lambda r: str(r["colony"]))
        out[key] = np.asarray([float(r["state"]) for r in rows], dtype=float)
    return out


def run_temporal_shape(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
    *,
    permutations: int,
    seed: int,
    batch_size: int = 1000,
) -> dict[str, object]:
    performance = performance_rows(
        adults,
        chicks,
        allowed_islands=("SIG",),
        metric="pearson",
    )
    models = {}
    for lag in (2, 3, 4, 5):
        panel = lag_panel(
            adults,
            performance,
            lag,
            allowed_islands=("SIG",),
        )
        if not panel:
            raise ValueError(f"empty Signy panel at lag {lag}")
        models[lag] = _prepare_model(panel, performance)

    observed = {lag: float(model["observed"]) for lag, model in models.items()}
    contrast = 0.5 * (observed[2] + observed[3]) - 0.5 * (
        observed[4] + observed[5]
    )

    groups = _perf_groups(performance)
    keys = sorted(groups)
    rng = np.random.default_rng(seed)
    null_contrast = np.empty(permutations, dtype=float)
    null_lags = {lag: np.empty(permutations, dtype=float) for lag in models}

    offset = 0
    while offset < permutations:
        batch = min(batch_size, permutations - offset)
        x = {
            lag: np.empty((batch, len(model["panel"])), dtype=float)
            for lag, model in models.items()
        }
        for key in keys:
            values = groups[key]
            order = np.argsort(rng.random((batch, len(values))), axis=1)
            assigned = values[order]
            for lag, model in models.items():
                info = model["group_rows"].get(key)
                if info is None:
                    continue
                row_indices, source_positions = info
                x[lag][:, row_indices] = assigned[:, source_positions]
        batch_beta = {}
        for lag, model in models.items():
            beta = _beta_from_batch(x[lag], model)
            null_lags[lag][offset : offset + batch] = beta
            batch_beta[lag] = beta
        null_contrast[offset : offset + batch] = (
            0.5 * (batch_beta[2] + batch_beta[3])
            - 0.5 * (batch_beta[4] + batch_beta[5])
        )
        offset += batch

    p = float(
        (1 + int(np.sum(null_contrast >= contrast))) / (permutations + 1)
    )
    lag_summary = {}
    for lag in (2, 3, 4, 5):
        vals = null_lags[lag]
        lag_summary[f"lag_{lag}"] = {
            "n_rows": int(len(models[lag]["panel"])),
            "beta": observed[lag],
            "null_q025": float(np.quantile(vals, 0.025)),
            "null_q975": float(np.quantile(vals, 0.975)),
        }

    return {
        "performance_rows": int(len(performance)),
        "performance_seasons": int(
            len({int(r["season"]) for r in performance})
        ),
        "lags": lag_summary,
        "adult_memory_contrast": {
            "definition": "mean(beta2,beta3)-mean(beta4,beta5)",
            "observed": float(contrast),
            "null_mean": float(np.mean(null_contrast)),
            "null_q025": float(np.quantile(null_contrast, 0.025)),
            "null_q975": float(np.quantile(null_contrast, 0.975)),
            "one_sided_upper_p": p,
            "supported": bool(contrast > 0 and p <= 0.05),
        },
        "permutations": int(permutations),
        "seed": int(seed),
    }


def analyze(path: Path, *, permutations: int = N_PERMUTATIONS):
    frame, source = read_official_zip(path)
    actual_sha = str(source["selected_csv_sha256"])
    if actual_sha != EXPECTED_CSV_SHA256:
        raise ValueError(
            f"official Signy CSV hash drift: {actual_sha} != {EXPECTED_CSV_SHA256}"
        )

    def cfg(*, atomic_only: bool, exclude_comments: bool, seed: int):
        adults, chicks, meta = build_signy_rows(
            frame,
            atomic_only=atomic_only,
            exclude_comment_flagged_seasons=exclude_comments,
        )
        result = run_temporal_shape(
            adults,
            chicks,
            permutations=permutations,
            seed=seed,
        )
        result["source_meta"] = meta
        return result

    primary = cfg(
        atomic_only=False,
        exclude_comments=False,
        seed=SEED_PRIMARY,
    )
    atomic = cfg(
        atomic_only=True,
        exclude_comments=False,
        seed=SEED_ATOMIC,
    )
    comment = cfg(
        atomic_only=False,
        exclude_comments=True,
        seed=SEED_COMMENT,
    )
    supported = bool(primary["adult_memory_contrast"]["supported"])
    return {
        "schema_version": 1,
        "analysis_id": "mina-signy-adult-memory-window-v1",
        "contract_id": "mina-signy-adult-memory-window-v1",
        "source": {
            "doi": "10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
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
            "primary_short_window_over_recruitment_window_supported": supported,
            "atomic_direction_consistent": bool(
                atomic["adult_memory_contrast"]["observed"] > 0
            ),
            "comment_filtered_direction_consistent": bool(
                comment["adult_memory_contrast"]["observed"] > 0
            ),
            "confirmatory_independent_replication": False,
        },
        "interpretation": (
            "Signy supports the same short 2-3 year over 4-5 year temporal shape."
            if supported
            else "Signy does not support the Palmer-generated short 2-3 year over 4-5 year temporal shape."
        ),
        "claim_boundary": [
            "Exploratory external challenge: Signy lag2 and lag3 were already known before this contract.",
            "Do not infer individual movement, public-information use, prospecting or causal cue use.",
            "Do not promote a sensitivity over a failed primary contrast.",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--official-zip", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    a = p.parse_args()
    result = analyze(a.official_zip, permutations=a.permutations)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
