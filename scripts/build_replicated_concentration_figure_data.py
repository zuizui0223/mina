"""Build frozen figure-data tables for the replicated concentration manuscript."""
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

from mina.lter import load_colony_rows
from scripts.audit_signy_replication_support import read_official_zip, season_start

PALMER_ISLANDS = ("COR", "HUM", "LIT")
PALMER_NAMES = {
    "COR": "Cormorant",
    "HUM": "Humble",
    "LIT": "Litchfield",
}
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


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def _neff(matrix: np.ndarray) -> np.ndarray:
    arr = np.asarray(matrix, dtype=float)
    total = np.sum(arr, axis=0)
    sq = np.sum(arr**2, axis=0)
    out = np.full(total.shape, np.nan, dtype=float)
    ok = total > 0
    out[ok] = total[ok] ** 2 / sq[ok]
    return out


def _slope(years: np.ndarray, values: np.ndarray) -> float:
    x = np.asarray(years, dtype=float)
    y = np.asarray(values, dtype=float)
    xc = x - float(np.mean(x))
    return float(np.sum((y - float(np.mean(y))) * xc) / np.sum(xc**2))


def _assert_close(name: str, a: float, b: float, tol: float = 1e-10) -> None:
    if not math.isfinite(a) or not math.isfinite(b) or abs(a - b) > tol:
        raise AssertionError(f"{name}: {a} != {b}")


def _palmer_panels(census: Path) -> dict[str, tuple[list[str], np.ndarray, np.ndarray]]:
    rows = load_colony_rows(census)
    result = {}
    for island in PALMER_ISLANDS:
        local = [r for r in rows if str(r["island"]) == island]
        by_year: dict[int, dict[str, float]] = defaultdict(dict)
        for row in local:
            year = int(row["year"])
            unit = str(row["colony_code"])
            if unit in by_year[year]:
                raise ValueError(f"duplicate Palmer row: {(island, year, unit)}")
            by_year[year][unit] = float(row["breeding_pairs"])
        years_all = sorted(by_year)
        rosters = [set(by_year[y]) for y in years_all]
        if not rosters or any(x != rosters[0] for x in rosters[1:]):
            raise ValueError(f"Palmer roster drift in {island}")
        units = sorted(rosters[0])
        years = np.asarray(
            [y for y in years_all if sum(by_year[y].values()) > 0],
            dtype=int,
        )
        matrix = np.asarray(
            [[by_year[int(y)][u] for y in years] for u in units],
            dtype=float,
        )
        result[island] = (units, years, matrix)
    return result


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


def _canonical_adelie(label: str) -> str:
    x = re.sub(r"\s+", " ", str(label).strip())
    if x in {"A1", "A60", "A1 + A60", "A1+A60"}:
        return "A1+A60"
    return x


def _signy_panel(
    frame: pd.DataFrame,
    units: tuple[str, ...],
    *,
    canonicalize=None,
) -> tuple[np.ndarray, np.ndarray]:
    grouped: dict[tuple[int, str], float] = {}
    year_set = set(int(x) for x in SIGNY_YEARS)
    for _, row in frame.iterrows():
        year = season_start(row["SEASON"])
        if year is None or int(year) not in year_set:
            continue
        unit = str(row["COLONY"]).strip()
        if canonicalize is not None:
            unit = canonicalize(unit)
        if unit not in units:
            continue
        value = _number(row["TOTAL_NUMBER_OF_PAIRS"])
        if value is None or value < 0:
            raise ValueError(f"bad Signy count: {(year, unit, value)}")
        key = (int(year), unit)
        grouped[key] = grouped.get(key, 0.0) + float(value)
    expected = {(int(y), u) for y in SIGNY_YEARS for u in units}
    missing = sorted(expected - set(grouped))
    if missing:
        raise ValueError(f"incomplete Signy panel: {missing[:12]}")
    matrix = np.asarray(
        [[grouped[(int(y), u)] for y in SIGNY_YEARS] for u in units],
        dtype=float,
    )
    return SIGNY_YEARS.copy(), matrix


def _append_trajectory(
    out: list[dict[str, object]],
    *,
    system: str,
    species: str,
    population: str,
    years: np.ndarray,
    matrix: np.ndarray,
) -> None:
    total = np.sum(matrix, axis=0)
    neff = _neff(matrix)
    for year, n, e in zip(years, total, neff):
        out.append(
            {
                "system": system,
                "species": species,
                "population": population,
                "year": int(year),
                "breeding_pairs": float(n),
                "neff": float(e),
                "abundance_index_first100": float(100.0 * n / total[0]),
                "neff_index_first100": float(100.0 * e / neff[0]),
            }
        )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--palmer-census", required=True, type=Path)
    p.add_argument("--signy-adelie-zip", required=True, type=Path)
    p.add_argument("--signy-chinstrap-zip", required=True, type=Path)
    p.add_argument("--palmer-receipt", required=True, type=Path)
    p.add_argument("--signy-adelie-receipt", required=True, type=Path)
    p.add_argument("--signy-chinstrap-receipt", required=True, type=Path)
    p.add_argument("--dominance-receipt", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    a = p.parse_args()

    palmer_receipt = _read_json(a.palmer_receipt)
    ad_receipt = _read_json(a.signy_adelie_receipt)
    ch_receipt = _read_json(a.signy_chinstrap_receipt)
    dom_receipt = _read_json(a.dominance_receipt)

    trajectories: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []

    palmer = _palmer_panels(a.palmer_census)
    for island in PALMER_ISLANDS:
        units, years, matrix = palmer[island]
        _append_trajectory(
            trajectories,
            system="Palmer Archipelago",
            species="Adelie",
            population=PALMER_NAMES[island],
            years=years,
            matrix=matrix,
        )
        neff = _neff(matrix)
        slope = _slope(years, neff)
        rec = palmer_receipt["observed"][island]
        _assert_close(f"{island} first N_eff", float(neff[0]), float(rec["first_neff"]))
        _assert_close(f"{island} last N_eff", float(neff[-1]), float(rec["last_neff"]))
        _assert_close(f"{island} slope", slope, float(rec["slope_per_year"]))
        cv20 = palmer_receipt["null_slope_summaries"]["gamma_poisson_cv20"][island]
        summaries.append(
            {
                "system": "Palmer Archipelago",
                "species": "Adelie",
                "population": PALMER_NAMES[island],
                "first_year": int(years[0]),
                "last_year": int(years[-1]),
                "first_total": float(np.sum(matrix[:, 0])),
                "last_total": float(np.sum(matrix[:, -1])),
                "first_neff": float(neff[0]),
                "last_neff": float(neff[-1]),
                "fractional_neff_change": float(neff[-1] / neff[0] - 1.0),
                "observed_neff_slope": slope,
                "cv20_null_mean": float(cv20["mean"]),
                "cv20_null_q025": float(cv20["q_0_025"]),
                "cv20_null_q975": float(cv20["q_0_975"]),
                "cv20_p": float(cv20["p"]),
            }
        )

    ad_frame, ad_source = read_official_zip(a.signy_adelie_zip)
    if str(ad_source["selected_csv_sha256"]) != SIGNY_ADELIE_SHA:
        raise ValueError("Signy Adelie hash drift")
    ad_years, ad_matrix = _signy_panel(
        ad_frame, SIGNY_ADELIE_UNITS, canonicalize=_canonical_adelie
    )
    ad_neff = _neff(ad_matrix)
    ad_slope = _slope(ad_years, ad_neff)
    _assert_close("Signy Adelie first N_eff", float(ad_neff[0]), float(ad_receipt["observed"]["first_neff"]))
    _assert_close("Signy Adelie last N_eff", float(ad_neff[-1]), float(ad_receipt["observed"]["last_neff"]))
    _assert_close("Signy Adelie slope", ad_slope, float(ad_receipt["observed"]["neff_slope_per_year"]))
    _append_trajectory(
        trajectories,
        system="Signy Island",
        species="Adelie",
        population="Signy Adelie",
        years=ad_years,
        matrix=ad_matrix,
    )
    ad_cv20 = ad_receipt["error_models"]["gamma_poisson_cv20"]
    summaries.append(
        {
            "system": "Signy Island",
            "species": "Adelie",
            "population": "Signy Adelie",
            "first_year": int(ad_years[0]),
            "last_year": int(ad_years[-1]),
            "first_total": float(np.sum(ad_matrix[:, 0])),
            "last_total": float(np.sum(ad_matrix[:, -1])),
            "first_neff": float(ad_neff[0]),
            "last_neff": float(ad_neff[-1]),
            "fractional_neff_change": float(ad_neff[-1] / ad_neff[0] - 1.0),
            "observed_neff_slope": ad_slope,
            "cv20_null_mean": float(ad_cv20["null_slope_summary"]["mean"]),
            "cv20_null_q025": float(ad_cv20["null_slope_summary"]["q_0_025"]),
            "cv20_null_q975": float(ad_cv20["null_slope_summary"]["q_0_975"]),
            "cv20_p": float(ad_cv20["one_sided_probability_le_observed"]),
        }
    )

    ch_frame, ch_source = read_official_zip(a.signy_chinstrap_zip)
    if str(ch_source["selected_csv_sha256"]) != SIGNY_CHINSTRAP_SHA:
        raise ValueError("Signy chinstrap hash drift")
    ch_years, ch_matrix = _signy_panel(ch_frame, SIGNY_CHINSTRAP_UNITS)
    ch_neff = _neff(ch_matrix)
    ch_slope = _slope(ch_years, ch_neff)
    _assert_close(
        "Signy chinstrap first N_eff",
        float(ch_neff[0]),
        float(ch_receipt["observed"]["first_effective_breeding_patch_number"]),
    )
    _assert_close(
        "Signy chinstrap last N_eff",
        float(ch_neff[-1]),
        float(ch_receipt["observed"]["last_effective_breeding_patch_number"]),
    )
    _assert_close(
        "Signy chinstrap slope",
        ch_slope,
        float(ch_receipt["observed"]["effective_breeding_patch_slope_per_year"]),
    )
    _append_trajectory(
        trajectories,
        system="Signy Island",
        species="Chinstrap",
        population="Signy chinstrap",
        years=ch_years,
        matrix=ch_matrix,
    )
    ch_cv20 = ch_receipt["error_models"]["gamma_poisson_cv20"]
    summaries.append(
        {
            "system": "Signy Island",
            "species": "Chinstrap",
            "population": "Signy chinstrap",
            "first_year": int(ch_years[0]),
            "last_year": int(ch_years[-1]),
            "first_total": float(np.sum(ch_matrix[:, 0])),
            "last_total": float(np.sum(ch_matrix[:, -1])),
            "first_neff": float(ch_neff[0]),
            "last_neff": float(ch_neff[-1]),
            "fractional_neff_change": float(ch_neff[-1] / ch_neff[0] - 1.0),
            "observed_neff_slope": ch_slope,
            "cv20_null_mean": float(ch_cv20["null_slope_summary"]["mean"]),
            "cv20_null_q025": float(ch_cv20["null_slope_summary"]["q_0_025"]),
            "cv20_null_q975": float(ch_cv20["null_slope_summary"]["q_0_975"]),
            "cv20_p": float(ch_cv20["one_sided_probability_le_observed"]),
        }
    )

    dominance_rows: list[dict[str, object]] = []
    key_map = {
        "ADPE_PALMER_COR": ("Palmer Archipelago", "Adelie", "Cormorant"),
        "ADPE_PALMER_HUM": ("Palmer Archipelago", "Adelie", "Humble"),
        "ADPE_PALMER_LIT": ("Palmer Archipelago", "Adelie", "Litchfield"),
        "ADPE_SIGNY": ("Signy Island", "Adelie", "Signy Adelie"),
        "CHPE_SIGNY": ("Signy Island", "Chinstrap", "Signy chinstrap"),
    }
    for key, (system, species, population) in key_map.items():
        item = dom_receipt["populations"][key]
        dominance_rows.append(
            {
                "system": system,
                "species": species,
                "population": population,
                "route": "dominant code changes" if item["dominant_identity_turnover"] else "initial unit remains dominant",
                "initial_dominant": str(item["initial_dominant"]),
                "initial_dom_share_first": float(item["initial_dominant_share_first"]),
                "initial_dom_share_last": float(item["initial_dominant_share_last"]),
                "final_dominant": str(item["final_dominant"]),
                "final_dom_initial_rank": float(item["final_dominant_initial_rank"]),
                "final_dom_share_first": float(item.get("final_dominant_share_first", item["initial_dominant_share_first"])),
                "final_dom_share_last": float(item.get("final_dominant_share_last", item["initial_dominant_share_last"])),
                "rho_initial_share_vs_slope": float(item["spearman_rho_initial_share_vs_log1p_count_slope"]),
            }
        )

    a.out_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(a.out_dir / "figure1_trajectories.csv", trajectories)
    _write_csv(a.out_dir / "figure2_summary.csv", summaries)
    _write_csv(a.out_dir / "figure3_dominance_routes.csv", dominance_rows)

    receipt = {
        "schema_version": 1,
        "analysis_id": "mina-replicated-concentration-figure-data-v1",
        "n_trajectory_rows": len(trajectories),
        "n_summary_populations": len(summaries),
        "n_dominance_populations": len(dominance_rows),
        "populations": [r["population"] for r in summaries],
        "checks": "All recomputed Palmer and Signy N_eff endpoints and slopes matched frozen receipts.",
    }
    (a.out_dir / "FIGURE_DATA_RECEIPT_V1.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
