"""Stage-4 Palmer weather × island physical-habitat interaction."""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

from .lter import ISLANDS, island_year_totals, load_colony_rows

HABITAT_SUBOPTIMAL_PERCENT = {
    "CHR": 46.8,
    "COR": 63.0,
    "HUM": 44.2,
    "LIT": 89.5,
    "TOR": 44.3,
}


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def _dialect(text: str):
    sample = "\n".join(text.splitlines()[:20])
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t;")
    except csv.Error:
        return csv.excel


def _numeric(text: str | None) -> float | None:
    if text is None:
        return None
    value = text.strip()
    if value in {"", "NA", "NaN", "nan", "-999", "-9999", "null", "NULL"}:
        return None
    try:
        x = float(value)
    except ValueError:
        return None
    return x if math.isfinite(x) else None


def _parse_date(text: str) -> datetime | None:
    value = text.strip()
    for fmt in (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%d-%b-%Y",
        "%d-%b-%y",
    ):
        try:
            return datetime.strptime(value[:20], fmt)
        except ValueError:
            pass
    # ISO timestamps.
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def weather_schema(path: str | Path) -> tuple[list[dict[str, str]], str, str]:
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text), dialect=_dialect(text))
    if not reader.fieldnames:
        raise ValueError("weather table has no header")
    fields = [field.strip() for field in reader.fieldnames]
    rows = [
        {str(k).strip(): str(v).strip() if v is not None else "" for k, v in row.items()}
        for row in reader
    ]

    date_rank = []
    precip_rank = []
    for field in fields:
        n = _norm(field)
        if "date" in n:
            date_rank.append((0 if n == "date" else 1, field))
        if "precip" in n:
            penalty = 0
            for flag in ("flag", "qc", "quality", "code"):
                if flag in n:
                    penalty += 10
            precip_rank.append((penalty + len(n), field))

    if not date_rank:
        raise ValueError(f"no date-like weather field; fields={fields!r}")
    if not precip_rank:
        raise ValueError(f"no precipitation-like weather field; fields={fields!r}")

    date_field = sorted(date_rank)[0][1]
    precip_field = sorted(precip_rank)[0][1]

    # Validate that chosen fields actually parse often enough.
    valid_date = sum(_parse_date(row.get(date_field, "")) is not None for row in rows[:500])
    valid_precip = sum(_numeric(row.get(precip_field)) is not None for row in rows[:500])
    if valid_date < 100:
        raise ValueError(
            f"chosen date field {date_field!r} parses too rarely ({valid_date}/500); fields={fields!r}"
        )
    if valid_precip < 100:
        raise ValueError(
            f"chosen precipitation field {precip_field!r} numeric too rarely "
            f"({valid_precip}/500); precip candidates={precip_rank!r}"
        )
    return rows, date_field, precip_field


def october_precip_days(path: str | Path) -> dict[int, dict[str, object]]:
    rows, date_field, precip_field = weather_schema(path)
    by_year: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        date = _parse_date(row.get(date_field, ""))
        if date is None or date.month != 10:
            continue
        value = _numeric(row.get(precip_field))
        if value is None:
            continue
        by_year[date.year].append(value)

    result: dict[int, dict[str, object]] = {}
    for year, values in sorted(by_year.items()):
        result[year] = {
            "numeric_october_days": len(values),
            "october_precip_days": sum(value > 0 for value in values),
            "eligible": len(values) >= 25,
        }
    result["_schema"] = {
        "date_field": date_field,
        "precipitation_field": precip_field,
    }
    return result


def _five_island_counts(census_path: str | Path) -> dict[int, dict[str, float]]:
    totals = island_year_totals(load_colony_rows(census_path))
    result: dict[int, dict[str, float]] = defaultdict(dict)
    for row in totals:
        result[int(row["year"])][str(row["island"])] = float(row["breeding_pairs"])
    return dict(result)


def annual_local_deviations(
    census_path: str | Path,
    weather_path: str | Path,
) -> tuple[list[dict[str, object]], dict[int, dict[str, object]], dict[str, object]]:
    counts = _five_island_counts(census_path)
    weather = october_precip_days(weather_path)
    years = sorted(counts)
    rows: list[dict[str, object]] = []

    for previous, year in zip(years, years[1:]):
        if year - previous != 1:
            continue
        weather_row = weather.get(year)
        if not isinstance(weather_row, dict) or not weather_row.get("eligible"):
            continue

        growth: dict[str, float] = {}
        for island in ISLANDS:
            if island not in counts[previous] or island not in counts[year]:
                continue
            n0 = counts[previous][island]
            n1 = counts[year][island]
            # Keep the transition into extinction but not subsequent 0->0 years.
            if n0 == 0.0 and n1 == 0.0:
                continue
            growth[island] = math.log1p(n1) - math.log1p(n0)

        if len(growth) < 3:
            continue
        for island, value in growth.items():
            others = [g for key, g in growth.items() if key != island]
            if len(others) < 2:
                continue
            rows.append(
                {
                    "year": year,
                    "island": island,
                    "growth": value,
                    "other_island_mean_growth": float(np.mean(others)),
                    "local_deviation": value - float(np.mean(others)),
                    "habitat_suboptimal_percent": HABITAT_SUBOPTIMAL_PERCENT[island],
                    "october_precip_days": int(weather_row["october_precip_days"]),
                    "numeric_october_days": int(weather_row["numeric_october_days"]),
                }
            )

    eligible_weather = {
        year: row
        for year, row in weather.items()
        if isinstance(year, int) and row.get("eligible")
    }
    if len({int(row["year"]) for row in rows}) < 15:
        raise ValueError("fewer than 15 eligible annual intervals after weather join")
    return rows, eligible_weather, weather["_schema"]


def _z(values: np.ndarray) -> tuple[np.ndarray, float, float]:
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1))
    if sd <= 0:
        raise ValueError("zero standard deviation")
    return (values - mean) / sd, mean, sd


def _design(rows: list[dict[str, object]], full: bool) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    y = np.asarray([float(row["local_deviation"]) for row in rows], dtype=float)
    islands = [str(row["island"]) for row in rows]
    x = np.ones((len(rows), 1 + len(ISLANDS) - 1 + int(full)), dtype=float)
    for r, island in enumerate(islands):
        idx = ISLANDS.index(island)
        if idx > 0:
            x[r, idx] = 1.0

    habitat = np.asarray([float(row["habitat_suboptimal_percent"]) for row in rows])
    precip = np.asarray([float(row["october_precip_days"]) for row in rows])
    # Habitat standardization is across the five islands, not weighted by row count.
    hvals = np.asarray([HABITAT_SUBOPTIMAL_PERCENT[i] for i in ISLANDS], dtype=float)
    hmean = float(np.mean(hvals))
    hsd = float(np.std(hvals, ddof=1))
    pz, pmean, psd = _z(precip)
    hz = (habitat - hmean) / hsd
    interaction = hz * pz
    if full:
        x[:, -1] = interaction
    return x, y, {
        "habitat_mean": hmean,
        "habitat_sd": hsd,
        "precip_mean": pmean,
        "precip_sd": psd,
    }


def _fit(rows: list[dict[str, object]], full: bool) -> dict[str, object]:
    x, y, scales = _design(rows, full)
    beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    if rank != x.shape[1]:
        raise ValueError("rank deficient mechanism model")
    residual = y - x @ beta
    sse = float(residual @ residual)
    tss = float(np.sum((y - np.mean(y)) ** 2))
    result = {
        "n": len(rows),
        "p": x.shape[1],
        "sse": sse,
        "r2": 1.0 - sse / tss if tss > 0 else None,
        "rmse_in_sample": math.sqrt(sse / len(rows)),
        "scales": scales,
    }
    if full:
        result["interaction_coefficient"] = float(beta[-1])
    return result


def _loyo_rmse(rows: list[dict[str, object]], full: bool) -> dict[str, object]:
    years = sorted({int(row["year"]) for row in rows})
    errors: list[float] = []
    by_year: dict[int, float] = {}

    # The scientific z-scaling must be training-only for held-out prediction.
    for year in years:
        train = [row for row in rows if int(row["year"]) != year]
        test = [row for row in rows if int(row["year"]) == year]
        xtr, ytr, scales = _design(train, full)
        beta, _, rank, _ = np.linalg.lstsq(xtr, ytr, rcond=None)
        if rank != xtr.shape[1]:
            raise ValueError("rank deficient LOYO mechanism model")

        hmean = float(scales["habitat_mean"])
        hsd = float(scales["habitat_sd"])
        pmean = float(scales["precip_mean"])
        psd = float(scales["precip_sd"])
        local_errors: list[float] = []
        for row in test:
            vec = [1.0] + [0.0] * (len(ISLANDS) - 1)
            idx = ISLANDS.index(str(row["island"]))
            if idx > 0:
                vec[idx] = 1.0
            if full:
                hz = (float(row["habitat_suboptimal_percent"]) - hmean) / hsd
                pz = (float(row["october_precip_days"]) - pmean) / psd
                vec.append(hz * pz)
            pred = float(np.asarray(vec) @ beta)
            error = float(row["local_deviation"]) - pred
            errors.append(error)
            local_errors.append(error)
        by_year[year] = math.sqrt(float(np.mean(np.square(local_errors))))
    return {
        "rmse": math.sqrt(float(np.mean(np.square(errors)))),
        "by_year_rmse": by_year,
        "n_years": len(years),
    }


def analyze(census_path: str | Path, weather_path: str | Path) -> dict[str, object]:
    rows, eligible_weather, schema = annual_local_deviations(census_path, weather_path)
    null = _fit(rows, False)
    full = _fit(rows, True)
    cv_null = _loyo_rmse(rows, False)
    cv_full = _loyo_rmse(rows, True)

    by_island: dict[str, object] = {}
    for island in ISLANDS:
        local = [row for row in rows if row["island"] == island]
        x = np.asarray([float(row["october_precip_days"]) for row in local])
        y = np.asarray([float(row["local_deviation"]) for row in local])
        corr = float(np.corrcoef(x, y)[0, 1]) if len(local) >= 3 and np.std(x) > 0 and np.std(y) > 0 else None
        by_island[island] = {
            "n": len(local),
            "precip_deviation_correlation": corr,
            "mean_local_deviation": float(np.mean(y)) if len(local) else None,
        }

    coefficient = float(full["interaction_coefficient"])
    rmse_change = float(cv_full["rmse"] - cv_null["rmse"])
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-weather-x-habitat-mechanism-v1",
        "weather_schema": schema,
        "eligible_weather_years": eligible_weather,
        "analysis_rows": rows,
        "model": {
            "null": null,
            "full": full,
            "delta_r2": float(full["r2"] - null["r2"]),
            "interaction_coefficient": coefficient,
            "directional_prediction_met": coefficient < 0,
        },
        "leave_one_year_out": {
            "null": cv_null,
            "full": cv_full,
            "rmse_change_full_minus_null": rmse_change,
            "prediction_improved": rmse_change < 0,
        },
        "descriptive_by_island": by_island,
        "decision": (
            "supported"
            if coefficient < 0 and rmse_change < 0
            else "not_supported"
        ),
        "interpretation_boundary": {
            "precipitation_is_not_measured_island_snow_depth": True,
            "habitat_modifier_is_external_published_covariate": True,
            "causal_claim": False,
            "post_extinction_zero_to_zero_excluded": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--weather", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = analyze(args.census, args.weather)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
