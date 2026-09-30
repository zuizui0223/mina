"""Palmer Humble arrival-timing mechanism diagnostic."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .performance_redistribution_lags import (
    _study_season,
    load_adult_rows,
    load_chick_rows,
    performance_rows,
)

HUMBLE = ("HUM",)
N_PERMUTATIONS = 100_000
SEED = 20260970
EXCLUDED_ARRIVAL_SEASONS = {1992}  # PAL9293 source-key collision; frozen V3 repair
FROZEN_MINIMUM_MATCHED_ROWS = 150
FROZEN_MAX_STRUCTURAL_MATCHED_ROWS = 64


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_arrival_rows(path: str | Path) -> list[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        expected = ["studyName", "Date", "Island", "Colony", "Adults"]
        if reader.fieldnames != expected:
            raise ValueError(
                f"unexpected arrival header: {reader.fieldnames!r}"
            )
        rows = list(reader)

    out: list[dict[str, object]] = []
    for row in rows:
        island = str(row.get("Island", "")).strip()
        if island != "HUM":
            continue
        if not _finite(row.get("Adults")):
            continue
        adults = float(row["Adults"])
        if adults < 0:
            raise ValueError("negative arrival adult count")
        season = _study_season(str(row.get("studyName", "")).strip())
        date = dt.date.fromisoformat(str(row.get("Date", "")).strip()[:10])
        colony = str(row.get("Colony", "")).strip()
        out.append(
            {
                "season": season,
                "date": date,
                "island": island,
                "colony": colony,
                "adults": adults,
            }
        )
    if not out:
        raise ValueError("no usable Humble arrival rows")
    return out


def _threshold_day(
    dates: list[dt.date],
    q: np.ndarray,
    threshold: float,
    origin: dt.date,
) -> float:
    crossing = np.flatnonzero(q >= threshold)
    if crossing.size == 0:
        raise ValueError("threshold never crossed")
    idx = int(crossing[0])
    current_day = float((dates[idx] - origin).days)
    if idx == 0:
        return current_day
    previous_q = float(q[idx - 1])
    current_q = float(q[idx])
    previous_day = float((dates[idx - 1] - origin).days)
    if current_q <= previous_q:
        return current_day
    fraction = (threshold - previous_q) / (current_q - previous_q)
    fraction = min(1.0, max(0.0, fraction))
    return previous_day + fraction * (current_day - previous_day)


def arrival_metrics(
    rows: list[dict[str, object]],
    *,
    minimum_observations: int = 5,
) -> list[dict[str, object]]:
    groups: dict[tuple[int, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        season = int(row["season"])
        if season in EXCLUDED_ARRIVAL_SEASONS:
            continue
        date = row["date"]
        assert isinstance(date, dt.date)
        if date < dt.date(season, 10, 1) or date > dt.date(season, 11, 15):
            continue
        groups[(season, str(row["colony"]))].append(row)

    raw: list[dict[str, object]] = []
    for (season, colony), local in sorted(groups.items()):
        date_counts: dict[dt.date, float] = {}
        for row in local:
            date = row["date"]
            assert isinstance(date, dt.date)
            value = float(row["adults"])
            if date in date_counts and date_counts[date] != value:
                raise ValueError(
                    f"discordant duplicate arrival count: "
                    f"{season} {colony} {date}"
                )
            date_counts[date] = value
        dates = sorted(date_counts)
        if len(dates) < minimum_observations or len(set(dates)) < 3:
            continue
        if (dates[-1] - dates[0]).days < 10:
            continue
        values = np.asarray([date_counts[d] for d in dates], dtype=float)
        maximum = float(np.max(values))
        if maximum <= 0:
            continue
        envelope = np.maximum.accumulate(values)
        q = envelope / maximum
        origin = dt.date(season, 10, 1)
        t25 = _threshold_day(dates, q, 0.25, origin)
        t50 = _threshold_day(dates, q, 0.50, origin)
        t75 = _threshold_day(dates, q, 0.75, origin)
        raw.append(
            {
                "season": season,
                "colony": colony,
                "n_observations": len(dates),
                "first_date": dates[0].isoformat(),
                "last_date": dates[-1].isoformat(),
                "max_adults": maximum,
                "t25": t25,
                "t50": t50,
                "t75": t75,
                "arrival_span": t75 - t25,
            }
        )

    by_season: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in raw:
        by_season[int(row["season"])].append(row)
    out: list[dict[str, object]] = []
    for season, local in sorted(by_season.items()):
        means = {
            key: float(np.mean([float(r[key]) for r in local]))
            for key in ("t25", "t50", "t75")
        }
        for row in local:
            out.append(
                {
                    **row,
                    "relative_t25": float(row["t25"]) - means["t25"],
                    "relative_t50": float(row["t50"]) - means["t50"],
                    "relative_t75": float(row["t75"]) - means["t75"],
                }
            )
    return out


def matched_panel(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
    arrival: list[dict[str, object]],
    *,
    minimum_observations: int = 5,
    performance_metric: str = "pearson",
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    perf = performance_rows(
        adults,
        chicks,
        allowed_islands=HUMBLE,
        metric=performance_metric,
    )
    metrics = arrival_metrics(
        arrival, minimum_observations=minimum_observations
    )
    arrival_lookup = {
        (int(r["season"]), str(r["colony"])): r for r in metrics
    }
    adult_lookup = {
        (str(r["island"]), str(r["colony"]), int(r["year"])): float(
            r["adult_pairs"]
        )
        for r in adults
    }

    raw: list[dict[str, object]] = []
    for row in perf:
        season = int(row["season"])
        colony = str(row["colony"])
        target = arrival_lookup.get((season + 1, colony))
        size = adult_lookup.get(("HUM", colony, season))
        if target is None or size is None:
            continue
        raw.append(
            {
                "season": season,
                "colony": colony,
                "state": float(row["state"]),
                "prior_pairs": float(size),
                "target_season": season + 1,
                "relative_t25": float(target["relative_t25"]),
                "relative_t50": float(target["relative_t50"]),
                "relative_t75": float(target["relative_t75"]),
                "arrival_span": float(target["arrival_span"]),
            }
        )

    groups: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in raw:
        groups[int(row["season"])].append(row)
    panel: list[dict[str, object]] = []
    for season, local in sorted(groups.items()):
        size = np.log1p(
            np.asarray([float(r["prior_pairs"]) for r in local], dtype=float)
        )
        sd = float(np.std(size, ddof=1)) if len(local) > 1 else 0.0
        zsize = (
            (size - float(np.mean(size))) / sd
            if sd > 0
            else np.zeros_like(size)
        )
        for row, z in zip(local, zsize):
            panel.append({**row, "zsize": float(z)})
    return panel, perf


def _prepare_model(
    panel: list[dict[str, object]],
    response: str,
    *,
    extra_controls: tuple[str, ...] = (),
) -> dict[str, object]:
    if not panel:
        raise ValueError("empty arrival model panel")
    colonies = sorted({str(r["colony"]) for r in panel})
    cmap = {name: idx for idx, name in enumerate(colonies)}
    n = len(panel)
    fe = np.zeros((n, len(colonies)), dtype=float)
    for idx, row in enumerate(panel):
        fe[idx, cmap[str(row["colony"])]] = 1.0

    control_columns = [
        np.asarray([float(r["zsize"]) for r in panel], dtype=float)
    ]
    for key in extra_controls:
        control_columns.append(
            np.asarray([float(r[key]) for r in panel], dtype=float)
        )
    controls = np.column_stack(control_columns + [fe])
    x = np.asarray([float(r["state"]) for r in panel], dtype=float)
    y = np.asarray([float(r[response]) for r in panel], dtype=float)

    inverse = np.linalg.pinv(controls.T @ controls)
    y_residual = y - controls @ (inverse @ (controls.T @ y))
    ztx = controls.T @ x
    denominator = float(x @ x - ztx @ (inverse @ ztx))
    if denominator <= 0:
        raise ValueError("non-positive residual predictor variance")
    observed = float((x @ y_residual) / denominator)

    groups: dict[int, list[int]] = defaultdict(list)
    for idx, row in enumerate(panel):
        groups[int(row["season"])].append(idx)
    return {
        "panel": panel,
        "controls": controls,
        "inverse": inverse,
        "y_residual": y_residual,
        "x": x,
        "groups": groups,
        "observed": observed,
        "response": response,
    }


def permutation_test(
    model: dict[str, object],
    *,
    permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
    lower_tail: bool = True,
    batch_size: int = 1000,
) -> dict[str, object]:
    panel = model["panel"]
    controls = np.asarray(model["controls"], dtype=float)
    inverse = np.asarray(model["inverse"], dtype=float)
    y_residual = np.asarray(model["y_residual"], dtype=float)
    original = np.asarray(model["x"], dtype=float)
    groups = model["groups"]
    observed = float(model["observed"])

    rng = np.random.default_rng(seed)
    null = np.empty(permutations, dtype=float)
    offset = 0
    while offset < permutations:
        batch = min(batch_size, permutations - offset)
        x = np.empty((batch, len(panel)), dtype=float)
        for indices in groups.values():
            idx = np.asarray(indices, dtype=int)
            values = original[idx]
            order = np.argsort(rng.random((batch, len(idx))), axis=1)
            x[:, idx] = values[order]
        ztx = x @ controls
        numerator = x @ y_residual
        denominator = np.sum(x * x, axis=1) - np.einsum(
            "bi,ij,bj->b", ztx, inverse, ztx, optimize=True
        )
        null[offset : offset + batch] = numerator / denominator
        offset += batch

    if lower_tail:
        p = float((1 + int(np.sum(null <= observed))) / (permutations + 1))
    else:
        p = float((1 + int(np.sum(null >= observed))) / (permutations + 1))
    return {
        "n_rows": len(panel),
        "n_seasons": len({int(r["season"]) for r in panel}),
        "n_colonies": len({str(r["colony"]) for r in panel}),
        "coefficient": observed,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_p": p,
    }


def _run_configuration(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
    arrival: list[dict[str, object]],
    *,
    minimum_observations: int = 5,
    performance_metric: str = "pearson",
    permutations: int = N_PERMUTATIONS,
) -> dict[str, object]:
    panel, perf = matched_panel(
        adults,
        chicks,
        arrival,
        minimum_observations=minimum_observations,
        performance_metric=performance_metric,
    )
    results: dict[str, object] = {}
    for response in ("relative_t25", "relative_t50", "relative_t75"):
        results[response] = permutation_test(
            _prepare_model(panel, response),
            permutations=permutations,
            seed=SEED,
            lower_tail=True,
        )
    primary = results["relative_t50"]
    primary["supported"] = bool(
        len(panel) >= 150
        and float(primary["coefficient"]) < 0
        and float(primary["one_sided_p"]) <= 0.05
    )
    coherent = bool(
        float(results["relative_t25"]["coefficient"]) < 0
        and float(results["relative_t75"]["coefficient"]) < 0
    )
    results["timing_coherent"] = coherent
    results["panel_rows"] = len(panel)
    results["performance_rows"] = len(perf)
    return {"panel": panel, "performance": perf, "results": results}


def _leave_one_colony_out(
    panel: list[dict[str, object]],
) -> dict[str, object]:
    counts = Counter(str(r["colony"]) for r in panel)
    out: dict[str, object] = {}
    for colony, count in sorted(counts.items()):
        if count < 5:
            continue
        local = [r for r in panel if str(r["colony"]) != colony]
        out[colony] = {
            "removed_n": count,
            "remaining_n": len(local),
            "alpha_t50": float(
                _prepare_model(local, "relative_t50")["observed"]
            ),
        }
    return out


def _current_performance_bridge(
    panel: list[dict[str, object]],
    performance: list[dict[str, object]],
) -> dict[str, object]:
    lookup = {
        (str(r["colony"]), int(r["season"])): float(r["state"])
        for r in performance
    }
    local: list[dict[str, object]] = []
    for row in panel:
        key = (str(row["colony"]), int(row["season"]) + 1)
        if key not in lookup:
            continue
        local.append({**row, "current_state": lookup[key]})
    if not local:
        return {"estimable": False, "n_rows": 0}
    model = _prepare_model(
        local,
        "relative_t50",
        extra_controls=("current_state",),
    )
    return {
        "estimable": True,
        "n_rows": len(local),
        "past_performance_coefficient": float(model["observed"]),
        "role": "descriptive post-arrival bridge only; not causal adjustment",
    }


def analyze(
    adult_path: str | Path,
    chick_path: str | Path,
    arrival_path: str | Path,
    *,
    permutations: int = N_PERMUTATIONS,
) -> dict[str, object]:
    adults = load_adult_rows(adult_path)
    chicks = load_chick_rows(chick_path)
    arrival = load_arrival_rows(arrival_path)

    # Frozen estimability gate. Do not derive t25/t50/t75 or scientific
    # coefficients when the predeclared sample-size requirement is impossible.
    if FROZEN_MAX_STRUCTURAL_MATCHED_ROWS < FROZEN_MINIMUM_MATCHED_ROWS:
        return {
            "schema_version": 3,
            "analysis_id": "mina-palmer-arrival-memory-v3",
            "contract_id": "mina-palmer-arrival-memory-v3",
            "status": "not_estimable_under_frozen_design",
            "source_counts": {
                "adult_rows": len(adults),
                "usable_chick_rows": len(chicks),
                "arrival_rows": len(arrival),
            },
            "estimability_gate": {
                "frozen_minimum_rows": FROZEN_MINIMUM_MATCHED_ROWS,
                "maximum_structurally_possible_rows": FROZEN_MAX_STRUCTURAL_MATCHED_ROWS,
                "passed": False,
                "derived_arrival_metrics_computed": False,
                "scientific_coefficients_computed": False,
            },
            "decision": {
                "primary_P5_estimable": False,
                "lower_minimum_rows_post_hoc": False,
            },
        }

    primary = _run_configuration(
        adults, chicks, arrival, permutations=permutations
    )
    min7 = _run_configuration(
        adults,
        chicks,
        arrival,
        minimum_observations=7,
        permutations=permutations,
    )
    logratio = _run_configuration(
        adults,
        chicks,
        arrival,
        performance_metric="logratio",
        permutations=permutations,
    )
    panel = primary["panel"]
    metrics5 = arrival_metrics(arrival, minimum_observations=5)
    decision = bool(primary["results"]["relative_t50"]["supported"])
    return {
        "schema_version": 2,
        "analysis_id": "mina-palmer-arrival-memory-v3",
        "contract_id": "mina-palmer-arrival-memory-v3",
        "source_counts": {
            "adult_rows": len(adults),
            "usable_chick_rows": len(chicks),
            "arrival_rows": len(arrival),
            "eligible_arrival_colony_seasons_min5": len(metrics5),
            "excluded_arrival_seasons": sorted(EXCLUDED_ARRIVAL_SEASONS),
        },
        "arrival_coverage": {
            "season_range": [
                min(int(r["season"]) for r in arrival),
                max(int(r["season"]) for r in arrival),
            ],
            "colonies": sorted({str(r["colony"]) for r in arrival}),
        },
        "primary": primary["results"],
        "sensitivities": {
            "minimum_observations_7": min7["results"],
            "alternate_logratio_performance": logratio["results"],
            "leave_one_colony_out_observed": _leave_one_colony_out(panel),
            "current_performance_bridge": _current_performance_bridge(
                panel, primary["performance"]
            ),
        },
        "decision": {
            "prior_performance_predicts_earlier_next_season_arrival": decision,
            "timing_coherent_t25_t75": bool(
                primary["results"]["timing_coherent"]
            ),
            "individual_movement_or_public_information_proven": False,
        },
        "interpretation_boundary": {
            "colony_level_arrival_counts_not_individual_resights": True,
            "prebreeding_timing_carrier_only_if_primary_supported": decision,
            "t25_t75_cannot_rescue_t50": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adult-census", required=True, type=Path)
    parser.add_argument("--chicks", required=True, type=Path)
    parser.add_argument("--arrival", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    args = parser.parse_args()
    result = analyze(
        args.adult_census,
        args.chicks,
        args.arrival,
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
