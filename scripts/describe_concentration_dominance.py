"""Post-hoc descriptive decomposition of replicated breeding-space concentration.

No inferential p-values are computed here. The script only describes whether
concentration reflects persistence of initially dominant breeding components or
turnover in which components dominate the remaining breeding population.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.audit_signy_replication_support import read_official_zip, season_start

PALMER_ISLANDS = ("COR", "HUM", "LIT")
SIGNY_YEARS = np.asarray(
    [
        1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007,
        2008, 2009, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
    ],
    dtype=int,
)
SIGNY_ADELIE_UNITS = ("A1+A60", "A2", "A3", "A4", "A64")
SIGNY_CHINSTRAP_UNITS = ("C15", "C16", "C17", "C18", "C46", "C47", "C79", "C80", "C81")
SIGNY_ADELIE_SHA = "585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62"
SIGNY_CHINSTRAP_SHA = "e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b"


def _number(value: object) -> float | None:
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


def _slope(years: np.ndarray, values: np.ndarray) -> float:
    x = np.asarray(years, dtype=float)
    y = np.asarray(values, dtype=float)
    xc = x - float(np.mean(x))
    denom = float(np.sum(xc**2))
    if denom <= 0:
        raise ValueError("zero time variance")
    return float(np.sum((y - float(np.mean(y))) * xc) / denom)


def _ranks_desc(values: np.ndarray) -> np.ndarray:
    return pd.Series(-np.asarray(values, dtype=float)).rank(method="average").to_numpy(dtype=float)


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx = pd.Series(np.asarray(x, dtype=float)).rank(method="average")
    ry = pd.Series(np.asarray(y, dtype=float)).rank(method="average")
    return float(rx.corr(ry))


def summarize_panel(
    label: str,
    units: list[str],
    years: np.ndarray,
    matrix: np.ndarray,
) -> dict[str, object]:
    if matrix.shape != (len(units), len(years)):
        raise ValueError(f"{label}: matrix shape mismatch")
    totals = np.sum(matrix, axis=0)
    if np.any(totals <= 0):
        raise ValueError(f"{label}: nonpositive total in descriptive panel")

    first_share = matrix[:, 0] / totals[0]
    last_share = matrix[:, -1] / totals[-1]
    slopes = np.asarray(
        [_slope(years, np.log1p(matrix[i])) for i in range(len(units))],
        dtype=float,
    )
    initial_ranks = _ranks_desc(first_share)

    initial_max = float(np.max(first_share))
    final_max = float(np.max(last_share))
    initial_dom = [units[i] for i in np.where(np.isclose(first_share, initial_max))[0]]
    final_dom = [units[i] for i in np.where(np.isclose(last_share, final_max))[0]]

    components = []
    for i, unit in enumerate(units):
        components.append(
            {
                "unit": unit,
                "first_count": float(matrix[i, 0]),
                "last_count": float(matrix[i, -1]),
                "first_share": float(first_share[i]),
                "last_share": float(last_share[i]),
                "initial_share_rank": float(initial_ranks[i]),
                "log1p_count_slope_per_year": float(slopes[i]),
            }
        )

    initial_dom_details = []
    for unit in initial_dom:
        i = units.index(unit)
        initial_dom_details.append(
            {
                "unit": unit,
                "first_share": float(first_share[i]),
                "last_share": float(last_share[i]),
                "first_count": float(matrix[i, 0]),
                "last_count": float(matrix[i, -1]),
                "log1p_count_slope_per_year": float(slopes[i]),
            }
        )

    final_dom_details = []
    for unit in final_dom:
        i = units.index(unit)
        final_dom_details.append(
            {
                "unit": unit,
                "last_share": float(last_share[i]),
                "first_share": float(first_share[i]),
                "initial_share_rank": float(initial_ranks[i]),
                "first_count": float(matrix[i, 0]),
                "last_count": float(matrix[i, -1]),
                "log1p_count_slope_per_year": float(slopes[i]),
            }
        )

    return {
        "population": label,
        "first_year": int(years[0]),
        "last_year": int(years[-1]),
        "n_years": int(len(years)),
        "n_units": int(len(units)),
        "first_total": float(totals[0]),
        "last_total": float(totals[-1]),
        "initial_dominant": initial_dom_details,
        "final_dominant": final_dom_details,
        "dominant_identity_turnover": bool(set(initial_dom).isdisjoint(set(final_dom))),
        "spearman_rho_initial_share_vs_log1p_count_slope": _spearman(first_share, slopes),
        "components": components,
        "inferential_status": "posthoc_descriptive_only_no_p_value",
    }


def load_palmer(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out = []
    for row in rows:
        island = str(row.get("island_name", "")).strip()
        if island not in PALMER_ISLANDS:
            continue
        time = str(row.get("time", ""))
        if len(time) < 4 or not time[:4].isdigit():
            continue
        count = _number(row.get("num_breeding_pairs"))
        if count is None or count < 0:
            continue
        out.append(
            {
                "island": island,
                "year": int(time[:4]),
                "unit": str(row.get("colony_code", "")).strip(),
                "count": float(count),
            }
        )
    return out


def palmer_panels(rows: list[dict[str, object]]) -> dict[str, tuple[list[str], np.ndarray, np.ndarray]]:
    result = {}
    for island in PALMER_ISLANDS:
        local = [r for r in rows if r["island"] == island]
        by_year: dict[int, dict[str, float]] = defaultdict(dict)
        for row in local:
            y = int(row["year"])
            u = str(row["unit"])
            if u in by_year[y]:
                raise ValueError(f"duplicate Palmer row: {(island, y, u)}")
            by_year[y][u] = float(row["count"])

        all_years = sorted(by_year)
        rosters = [set(by_year[y]) for y in all_years]
        if not rosters or any(r != rosters[0] for r in rosters[1:]):
            raise ValueError(f"{island}: roster not stable")
        units = sorted(rosters[0])
        positive_years = [y for y in all_years if sum(by_year[y].values()) > 0]
        years = np.asarray(positive_years, dtype=int)
        matrix = np.asarray(
            [[by_year[y][u] for y in positive_years] for u in units],
            dtype=float,
        )
        result[island] = (units, years, matrix)
    return result


def canonical_adelie(label: str) -> str:
    x = re.sub(r"\s+", " ", str(label).strip())
    if x in {"A1", "A60", "A1 + A60", "A1+A60"}:
        return "A1+A60"
    return x


def signy_panel(
    frame: pd.DataFrame,
    *,
    units: tuple[str, ...],
    canonicalize=None,
) -> tuple[list[str], np.ndarray, np.ndarray]:
    required = {"SEASON", "COLONY", "TOTAL_NUMBER_OF_PAIRS"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing Signy columns: {sorted(missing)}")

    grouped: dict[tuple[int, str], float] = {}
    for _, row in frame.iterrows():
        year = season_start(row["SEASON"])
        if year is None or int(year) not in set(int(x) for x in SIGNY_YEARS):
            continue
        unit = str(row["COLONY"]).strip()
        if canonicalize is not None:
            unit = canonicalize(unit)
        if unit not in units:
            continue
        value = _number(row["TOTAL_NUMBER_OF_PAIRS"])
        if value is None or value < 0:
            raise ValueError(f"non-numeric frozen Signy count: {(year, unit)}")
        key = (int(year), unit)
        grouped[key] = grouped.get(key, 0.0) + float(value)

    expected = {(int(y), u) for y in SIGNY_YEARS for u in units}
    missing_keys = sorted(expected - set(grouped))
    if missing_keys:
        raise ValueError(f"incomplete frozen Signy panel: {missing_keys[:12]}")

    matrix = np.asarray(
        [[grouped[(int(y), u)] for y in SIGNY_YEARS] for u in units],
        dtype=float,
    )
    return list(units), SIGNY_YEARS.copy(), matrix


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--palmer-census", required=True, type=Path)
    p.add_argument("--signy-adelie-zip", required=True, type=Path)
    p.add_argument("--signy-chinstrap-zip", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()

    results = {}

    palmer = palmer_panels(load_palmer(a.palmer_census))
    for island, (units, years, matrix) in palmer.items():
        results[f"ADPE_PALMER_{island}"] = summarize_panel(
            f"Adelie Palmer {island}", units, years, matrix
        )

    ad_frame, ad_source = read_official_zip(a.signy_adelie_zip)
    if str(ad_source["selected_csv_sha256"]) != SIGNY_ADELIE_SHA:
        raise ValueError("Signy Adelie source hash drift")
    units, years, matrix = signy_panel(
        ad_frame,
        units=SIGNY_ADELIE_UNITS,
        canonicalize=canonical_adelie,
    )
    results["ADPE_SIGNY"] = summarize_panel(
        "Adelie Signy", units, years, matrix
    )

    ch_frame, ch_source = read_official_zip(a.signy_chinstrap_zip)
    if str(ch_source["selected_csv_sha256"]) != SIGNY_CHINSTRAP_SHA:
        raise ValueError("Signy chinstrap source hash drift")
    units, years, matrix = signy_panel(
        ch_frame,
        units=SIGNY_CHINSTRAP_UNITS,
        canonicalize=None,
    )
    results["CHPE_SIGNY"] = summarize_panel(
        "Chinstrap Signy", units, years, matrix
    )

    out = {
        "schema_version": 1,
        "analysis_id": "mina-concentration-dominance-descriptive-v1",
        "status": "posthoc_descriptive_only",
        "no_inferential_p_values": True,
        "populations": results,
        "interpretation_boundary": [
            "These summaries describe how previously supported concentration patterns are composed internally.",
            "They do not alter the frozen concentration decisions.",
            "No pooled significance test across populations is performed.",
        ],
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
