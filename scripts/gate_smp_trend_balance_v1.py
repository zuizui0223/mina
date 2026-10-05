#!/usr/bin/env python3
"""Stage-B total-abundance-only trend balance gate for the SMP symmetry test.

This script opens Count magnitudes only after the Stage-A panel roster is frozen.
It emits panel-level abundance trend slopes and labels, but never component
shares, E, kappa, gamma, or delta_gamma.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.gate_smp_master_site_support_v1 import (
    SENSITIVE,
    EXPOSED_MASTER,
    _direct_record_mask,
    _find_column,
    _load,
    _norm,
    _not_merged_mask,
    _whole_colony_mask,
    _year_from_date,
)


MIN_INCREASING = 6
MIN_DECLINING = 6
MIN_SPECIES_EACH = 3
MIN_MASTERS_EACH = 5


def _prepare_raw(path: Path, *, assume_whole_colony_extract: bool) -> pd.DataFrame:
    df = _load(path)

    species_col = _find_column(df, ["Species"])
    country_col = _find_column(df, ["Country"])
    site_id_col = _find_column(df, ["SiteID", "Site ID", "Site code"])
    master_col = _find_column(df, ["MasterSite", "Master Site"])
    method_col = _find_column(df, ["Method"], required=False)
    unit_col = _find_column(df, ["Unit"])
    accuracy_col = _find_column(df, ["Accuracy"])
    estimate_col = _find_column(df, ["Estimate", "Estimate type"], required=False)
    comments_col = _find_column(df, ["Comments", "Comment"], required=False)
    plot_col = _find_column(df, ["Plot", "Plot site name", "Spatial level"], required=False)
    count_col = _find_column(df, ["Count"])
    year_col = _find_column(df, ["Year"], required=False)
    date_col = _find_column(df, ["Start date", "Date", "StartDate"], required=year_col is None)

    year = (
        df[year_col].map(_year_from_date)
        if year_col is not None
        else df[date_col].map(_year_from_date)
    )
    x = df.assign(_year=year)
    x = x[x["_year"].between(1986, 2024, inclusive="both")].copy()

    direct = _direct_record_mask(x, accuracy_col, estimate_col)
    whole = _whole_colony_mask(x, plot_col, assume_whole_colony_extract)
    not_merged = _not_merged_mask(x, comments_col)
    x = x[direct & whole & not_merged].copy()

    x["_species"] = x[species_col].map(_norm)
    x["_country"] = x[country_col].map(lambda z: str(z).strip() if not pd.isna(z) else "")
    x["_site_id"] = x[site_id_col].map(lambda z: str(z).strip())
    x["_master"] = x[master_col].map(lambda z: str(z).strip())
    x["_master_norm"] = x[master_col].map(_norm)
    x["_unit"] = x[unit_col].map(lambda z: str(z).strip())
    x["_method"] = x[method_col].map(lambda z: str(z).strip()) if method_col else ""
    x["year"] = x["_year"].astype(int)
    x["_count"] = pd.to_numeric(x[count_col], errors="coerce")

    x = x[~x["_species"].isin(SENSITIVE)].copy()
    pilot = x["_species"].str.contains("kittiwake", regex=False) & (x["_master_norm"] == EXPOSED_MASTER)
    x = x[~pilot].copy()

    key = ["_species", "_master", "_unit", "_site_id", "year"]
    dup_n = x.groupby(key, dropna=False).size().rename("_n").reset_index()
    unique_keys = dup_n[dup_n["_n"] == 1][key]
    x = x.merge(unique_keys, on=key, how="inner")

    if method_col:
        method_n = (
            x[x["_method"].map(_norm) != ""]
            .groupby(["_species", "_master", "_unit", "_site_id"])["_method"]
            .nunique()
            .rename("_method_n")
            .reset_index()
        )
        x = x.merge(method_n, on=["_species", "_master", "_unit", "_site_id"], how="left")
        x["_method_n"] = x["_method_n"].fillna(0)
        x = x[x["_method_n"] <= 1].copy()

    if x["_count"].isna().any():
        raise ValueError("Non-numeric or missing Count in records needed for Stage-B trend totals")
    if (x["_count"] < 0).any():
        raise ValueError("Negative Count values are not allowed")

    return x


def _panel_trend(x: pd.DataFrame, panel: dict) -> dict:
    species = str(panel["species"])
    master = str(panel["master_site"])
    unit = str(panel["unit"])
    roster = {str(v) for v in panel["retained_site_ids"]}
    years = [int(v) for v in panel["complete_years"]]

    g = x[
        x["_species"].eq(species)
        & x["_master_norm"].eq(_norm(master))
        & x["_unit"].eq(unit)
        & x["_site_id"].isin(roster)
        & x["year"].isin(years)
    ].copy()

    expected = len(roster)
    per_year_n = g.groupby("year")["_site_id"].nunique()
    if set(per_year_n.index.astype(int)) != set(years):
        raise ValueError(f"Complete-year drift for {species}|{master}|{unit}")
    if not (per_year_n == expected).all():
        raise ValueError(f"Roster completeness drift for {species}|{master}|{unit}")

    totals = g.groupby("year")["_count"].sum().sort_index()
    yy = totals.index.to_numpy(float)
    logn = np.log1p(totals.to_numpy(float))
    xc = yy - yy.mean()
    denom = float(np.sum(xc * xc))
    if denom <= 0:
        raise ValueError("Zero year variance")
    b = float(np.sum(xc * (logn - logn.mean())) / denom)

    label = "increasing" if b > 0 else ("declining" if b < 0 else "zero")
    return {
        "panel_id": f"{species}|{master}|{unit}",
        "species": species,
        "master_site": master,
        "unit": unit,
        "n_components": int(len(roster)),
        "n_complete_years": int(len(years)),
        "first_year": int(min(years)),
        "last_year": int(max(years)),
        "b_log1pN_per_year": b,
        "trend_label": label,
    }


def run(
    input_path: Path,
    support_json: Path,
    *,
    assume_whole_colony_extract: bool = False,
) -> dict:
    support = json.loads(support_json.read_text(encoding="utf-8"))
    if not support.get("decision", {}).get("structural_gate_passed"):
        raise ValueError("Stage-A structural gate did not pass")

    x = _prepare_raw(
        input_path,
        assume_whole_colony_extract=assume_whole_colony_extract,
    )
    rows = [_panel_trend(x, p) for p in support["eligible_panels"]]
    frame = pd.DataFrame(rows)

    inc = frame[frame["trend_label"].eq("increasing")]
    dec = frame[frame["trend_label"].eq("declining")]

    inc_species = int(inc["species"].nunique())
    dec_species = int(dec["species"].nunique())
    inc_masters = int(inc["master_site"].nunique())
    dec_masters = int(dec["master_site"].nunique())

    passed = bool(
        len(inc) >= MIN_INCREASING
        and len(dec) >= MIN_DECLINING
        and inc_species >= MIN_SPECIES_EACH
        and dec_species >= MIN_SPECIES_EACH
        and inc_masters >= MIN_MASTERS_EACH
        and dec_masters >= MIN_MASTERS_EACH
    )

    return {
        "schema_version": 1,
        "analysis_id": "mina-smp-trend-balance-gate-v1",
        "status": "panel_total_trend_only_component_composition_locked",
        "source_support_analysis_id": support["analysis_id"],
        "panel_trends": rows,
        "trend_support": {
            "increasing_panels": int(len(inc)),
            "declining_panels": int(len(dec)),
            "zero_panels": int((frame["trend_label"] == "zero").sum()),
            "increasing_species": inc_species,
            "declining_species": dec_species,
            "increasing_master_sites": inc_masters,
            "declining_master_sites": dec_masters,
        },
        "frozen_thresholds": {
            "minimum_increasing_panels": MIN_INCREASING,
            "minimum_declining_panels": MIN_DECLINING,
            "minimum_species_each_direction": MIN_SPECIES_EACH,
            "minimum_master_sites_each_direction": MIN_MASTERS_EACH,
        },
        "decision": {
            "symmetry_identifiability_gate_passed": passed,
            "component_concentration_execution_authorized": passed,
            "if_failed": "Do not open the trend-symmetry concentration endpoint or relax trend-balance thresholds.",
        },
        "forbidden_outputs_confirmed_absent": [
            "annual panel total abundance values",
            "SiteID-level count magnitudes",
            "component proportions",
            "effective component number E",
            "kappa",
            "gamma_obs",
            "gamma_null",
            "delta_gamma",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--support-json", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--assume-whole-colony-extract", action="store_true")
    a = p.parse_args()
    result = run(
        a.input,
        a.support_json,
        assume_whole_colony_extract=a.assume_whole_colony_extract,
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
