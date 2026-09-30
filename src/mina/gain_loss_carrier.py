"""Gain-versus-loss decomposition of Palmer performance-linked redistribution."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .performance_redistribution_lags import (
    ISLANDS,
    lag_panel,
    load_adult_rows,
    load_chick_rows,
    performance_rows,
)
from .performance_memory import (
    _colony_fixed_effects,
    _prepare_permutation_model,
    _permutation_test,
)

N_PERMUTATIONS = 100_000
PRIMARY_SEED = 20260990


def gain_loss_panel(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    minimum_prior_size: float = 0.0,
) -> list[dict[str, object]]:
    """Build the frozen lag-2 panel and decompose log growth within risk sets."""
    adult_lookup = {
        (str(r["island"]), str(r["colony"]), int(r["year"])): float(
            r["adult_pairs"]
        )
        for r in adults
    }
    base = lag_panel(
        adults,
        performance,
        2,
        allowed_islands=allowed_islands,
        minimum_prior_size=minimum_prior_size,
    )
    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in base:
        groups[(str(row["island"]), int(row["start_year"]))].append(row)

    out: list[dict[str, object]] = []
    for _, local in sorted(groups.items()):
        gain = np.asarray(
            [max(float(r["growth"]), 0.0) for r in local], dtype=float
        )
        avoid = np.asarray(
            [-max(-float(r["growth"]), 0.0) for r in local], dtype=float
        )
        entry_log: list[float] = []
        entry_pairs: list[float] = []
        for row in local:
            key = (
                str(row["island"]),
                str(row["colony"]),
                int(row["start_year"]) + 1,
            )
            if key not in adult_lookup:
                raise ValueError(f"missing end count for lag-2 row: {key!r}")
            n1 = float(adult_lookup[key])
            n0 = float(row["n0"])
            lplus = max(n1 - n0, 0.0)
            entry_pairs.append(lplus)
            entry_log.append(math.log1p(lplus))
        entry = np.asarray(entry_log, dtype=float)

        gain_rel = gain - float(np.mean(gain))
        avoid_rel = avoid - float(np.mean(avoid))
        entry_rel = entry - float(np.mean(entry))

        for row, gp, av, er, lp in zip(
            local, gain_rel, avoid_rel, entry_rel, entry_pairs
        ):
            out.append(
                {
                    **row,
                    "gain_relative": float(gp),
                    "loss_avoidance_relative": float(av),
                    "entry_log_relative": float(er),
                    "lplus_pairs": float(lp),
                }
            )
    return out


def _controls(panel: list[dict[str, object]]) -> np.ndarray:
    zsize = np.asarray([float(r["zsize"]) for r in panel], dtype=float)
    return np.column_stack([zsize, _colony_fixed_effects(panel)])


def component_test(
    panel: list[dict[str, object]],
    performance: list[dict[str, object]],
    y_field: str,
    *,
    permutations: int = N_PERMUTATIONS,
    seed: int = PRIMARY_SEED,
) -> dict[str, object]:
    model = _prepare_permutation_model(
        panel,
        performance,
        x_field="state",
        y_field=y_field,
        controls=_controls(panel),
    )
    return _permutation_test(
        model,
        permutations=permutations,
        seed=seed,
    )


def holm_two(p_a: float, p_b: float) -> tuple[float, float]:
    """Holm adjusted p-values for exactly two hypotheses."""
    values = [(float(p_a), 0), (float(p_b), 1)]
    values.sort()
    adjusted_sorted = [
        min(1.0, 2.0 * values[0][0]),
        min(1.0, max(2.0 * values[0][0], values[1][0])),
    ]
    out = [0.0, 0.0]
    for (_, original_index), adjusted in zip(values, adjusted_sorted):
        out[original_index] = adjusted
    return float(out[0]), float(out[1])


def _observed_component(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
    y_field: str,
    *,
    allowed_islands: tuple[str, ...],
) -> float:
    panel = gain_loss_panel(
        adults,
        performance,
        allowed_islands=allowed_islands,
    )
    model = _prepare_permutation_model(
        panel,
        performance,
        x_field="state",
        y_field=y_field,
        controls=_controls(panel),
    )
    return float(model["observed"])


def run_configuration(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    metric: str = "pearson",
    minimum_prior_size: float = 0.0,
    permutations: int = N_PERMUTATIONS,
    seed: int = PRIMARY_SEED,
) -> dict[str, object]:
    performance = performance_rows(
        adults,
        chicks,
        allowed_islands=allowed_islands,
        metric=metric,
    )
    panel = gain_loss_panel(
        adults,
        performance,
        allowed_islands=allowed_islands,
        minimum_prior_size=minimum_prior_size,
    )

    gain = component_test(
        panel,
        performance,
        "gain_relative",
        permutations=permutations,
        seed=seed,
    )
    avoid = component_test(
        panel,
        performance,
        "loss_avoidance_relative",
        permutations=permutations,
        seed=seed,
    )
    entry = component_test(
        panel,
        performance,
        "entry_log_relative",
        permutations=permutations,
        seed=seed,
    )

    gain_adj, avoid_adj = holm_two(
        float(gain["one_sided_upper_p"]),
        float(avoid["one_sided_upper_p"]),
    )
    gain["holm_p"] = gain_adj
    avoid["holm_p"] = avoid_adj
    gain["holm_supported"] = bool(
        float(gain["coefficient"]) > 0 and gain_adj <= 0.05
    )
    avoid["holm_supported"] = bool(
        float(avoid["coefficient"]) > 0 and avoid_adj <= 0.05
    )

    positive_rows = [r for r in panel if float(r["lplus_pairs"]) > 0]
    lplus_values = [float(r["lplus_pairs"]) for r in positive_rows]
    lower_bound = {
        "n_panel_rows": len(panel),
        "n_positive_net_addition_rows": len(positive_rows),
        "fraction_positive_net_addition": (
            len(positive_rows) / len(panel) if panel else None
        ),
        "total_lplus_pairs": float(sum(lplus_values)),
        "median_lplus_pairs_among_positive": (
            float(np.median(lplus_values)) if lplus_values else None
        ),
        "performance_link": {
            **entry,
            "role": "secondary descriptive permutation endpoint",
        },
    }

    if gain["holm_supported"] and avoid["holm_supported"]:
        pattern = "mixed_pattern"
    elif gain["holm_supported"]:
        pattern = "entry_dominant_pattern"
    elif avoid["holm_supported"]:
        pattern = "retention_dominant_pattern"
    else:
        pattern = "undifferentiated"

    return {
        "n_performance_rows": len(performance),
        "n_lag2_rows": len(panel),
        "gain": gain,
        "loss_avoidance": avoid,
        "net_addition_lower_bound": lower_bound,
        "decision": {
            "pattern": pattern,
            "retention_only_ruled_out": bool(gain["holm_supported"]),
        },
    }


def analyze(
    adult_path: str | Path,
    chick_path: str | Path,
    *,
    permutations: int = N_PERMUTATIONS,
) -> dict[str, object]:
    adults = load_adult_rows(adult_path)
    chicks = load_chick_rows(chick_path)
    primary = run_configuration(
        adults,
        chicks,
        permutations=permutations,
        seed=PRIMARY_SEED,
    )

    no_lit = tuple(x for x in ISLANDS if x != "LIT")
    no_lit_result = run_configuration(
        adults,
        chicks,
        allowed_islands=no_lit,
        permutations=permutations,
        seed=PRIMARY_SEED + 10,
    )
    ge2_result = run_configuration(
        adults,
        chicks,
        minimum_prior_size=2.0,
        permutations=permutations,
        seed=PRIMARY_SEED + 20,
    )
    logratio_result = run_configuration(
        adults,
        chicks,
        metric="logratio",
        permutations=permutations,
        seed=PRIMARY_SEED + 30,
    )

    loo: dict[str, object] = {}
    for island in ISLANDS:
        allowed = tuple(x for x in ISLANDS if x != island)
        perf = performance_rows(
            adults, chicks, allowed_islands=allowed
        )
        loo[island] = {
            "beta_gain": _observed_component(
                adults,
                perf,
                "gain_relative",
                allowed_islands=allowed,
            ),
            "beta_avoid": _observed_component(
                adults,
                perf,
                "loss_avoidance_relative",
                allowed_islands=allowed,
            ),
        }

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-gain-loss-carrier-v1",
        "contract_id": "mina-palmer-gain-loss-carrier-v1",
        "source_counts": {
            "adult_rows": len(adults),
            "usable_chick_rows": len(chicks),
        },
        "primary": primary,
        "sensitivities": {
            "exclude_litchfield": no_lit_result,
            "minimum_prior_size_2": ge2_result,
            "alternate_logratio_performance": logratio_result,
            "leave_one_island_out_observed": loo,
        },
        "interpretation_boundary": {
            "positive_net_addition_is_immigration": False,
            "gain_support_proves_public_information": False,
            "loss_avoidance_support_proves_individual_quality": False,
            "carrier_identified": False,
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
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
