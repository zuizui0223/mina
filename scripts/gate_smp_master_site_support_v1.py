#!/usr/bin/env python3
"""Outcome-blind SMP MasterSite support gate.

IMPORTANT: This script intentionally does not use count magnitudes. The Count
column, if present, is dropped immediately after loading. It evaluates only
sampling structure, identifiers, metadata, and missingness under
contracts/SMP_MASTER_SITE_ELIGIBILITY_V1.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import pandas as pd


MIN_SITE_YEARS = 10
MIN_SITES = 3
MIN_COMPLETE_YEARS = 10
MIN_SPAN = 10

SENSITIVE = {
    "leach's storm-petrel",
    "leachs storm-petrel",
    "mediterranean gull",
    "roseate tern",
    "little tern",
}

EXPOSED_MASTER = "flamborough and filey coast spa"


def _norm(x: object) -> str:
    if pd.isna(x):
        return ""
    return re.sub(r"\s+", " ", str(x).strip()).casefold()


def _find_column(df: pd.DataFrame, names: list[str], *, required: bool = True) -> str | None:
    norm = {_norm(c).replace("_", " "): c for c in df.columns}
    for name in names:
        key = _norm(name).replace("_", " ")
        if key in norm:
            return norm[key]
    if required:
        raise ValueError(f"Missing required field; tried {names}")
    return None


def _year_from_date(value: object) -> int | None:
    if pd.isna(value):
        return None
    s = str(value).strip()
    # direct year
    m = re.fullmatch(r"(19|20)\d{2}", s)
    if m:
        return int(s)
    dt = pd.to_datetime(s, errors="coerce", dayfirst=True)
    if pd.isna(dt):
        return None
    return int(dt.year)


def _load(path: Path) -> pd.DataFrame:
    suffix = path.suffix.casefold()
    if suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        # sep=None delegates delimiter detection to python engine.
        df = pd.read_csv(path, sep=None, engine="python")
    if df.empty:
        raise ValueError("empty SMP extract")
    return df


def _direct_record_mask(df: pd.DataFrame, accuracy_col: str, estimate_col: str | None) -> pd.Series:
    acc = df[accuracy_col].map(_norm)
    # 2022 guide: C = Count, E = Estimate. Current portal also uses textual labels.
    direct = acc.isin({"c", "count", "accurate", "accuracy: accurate", "direct"})
    if estimate_col is not None:
        est = df[estimate_col].map(_norm)
        direct &= est.isin({"", "none", "na", "n/a", "not applicable"})
    return direct


def _whole_colony_mask(df: pd.DataFrame, plot_col: str | None, assume_whole_colony_extract: bool) -> pd.Series:
    if plot_col is None:
        if not assume_whole_colony_extract:
            raise ValueError(
                "No Plot/spatial-level field found. Re-run only if BTO confirms this extract "
                "contains Whole Colony / Site-level records only, using --assume-whole-colony-extract."
            )
        return pd.Series(True, index=df.index)
    plot = df[plot_col].map(_norm)
    accepted = {
        "",
        "(whole colony)",
        "whole colony",
        "count at site level - whole colony count",
        "site level - whole colony count",
    }
    return plot.isin(accepted)


def _not_merged_mask(df: pd.DataFrame, comments_col: str | None) -> pd.Series:
    if comments_col is None:
        return pd.Series(True, index=df.index)
    text = df[comments_col].map(_norm)
    return ~text.str.contains(r"merged?\s+sites?|total count after merging", regex=True)


def _roster_from_missingness(panel: pd.DataFrame) -> tuple[list[str], list[int]] | None:
    """Apply frozen deterministic roster algorithm using only observation presence."""
    site_years = (
        panel[["site_id", "year"]]
        .drop_duplicates()
        .groupby("site_id")["year"]
        .agg(lambda x: sorted(set(int(v) for v in x)))
        .to_dict()
    )
    roster = sorted([site for site, years in site_years.items() if len(years) >= MIN_SITE_YEARS])
    if len(roster) < MIN_SITES:
        return None

    while len(roster) >= MIN_SITES:
        common = sorted(set.intersection(*(set(site_years[s]) for s in roster)))
        if len(common) >= MIN_COMPLETE_YEARS:
            return roster, common

        counts = {s: len(site_years[s]) for s in roster}
        fewest = min(counts.values())
        tied = sorted([s for s, n in counts.items() if n == fewest])
        # frozen tiebreak: remove lexicographically greatest SiteID
        roster.remove(tied[-1])

    return None


def analyze(path: Path, *, assume_whole_colony_extract: bool = False) -> dict[str, object]:
    raw_bytes = path.read_bytes()
    source_sha = hashlib.sha256(raw_bytes).hexdigest()
    df = _load(path)

    # Resolve schema before dropping count.
    species_col = _find_column(df, ["Species"])
    country_col = _find_column(df, ["Country"])
    site_id_col = _find_column(df, ["SiteID", "Site ID", "Site code"])
    site_col = _find_column(df, ["Site", "Site name"])
    master_col = _find_column(df, ["MasterSite", "Master Site"])
    method_col = _find_column(df, ["Method"], required=False)
    unit_col = _find_column(df, ["Unit"])
    accuracy_col = _find_column(df, ["Accuracy"])
    estimate_col = _find_column(df, ["Estimate", "Estimate type"], required=False)
    comments_col = _find_column(df, ["Comments", "Comment"], required=False)
    plot_col = _find_column(df, ["Plot", "Plot site name", "Spatial level"], required=False)
    year_col = _find_column(df, ["Year"], required=False)
    date_col = _find_column(df, ["Start date", "Date", "StartDate"], required=year_col is None)

    # Hard blind: drop count magnitude before any grouping/calculation.
    count_col = _find_column(df, ["Count"], required=False)
    count_field_present = count_col is not None
    if count_col is not None:
        df = df.drop(columns=[count_col])

    year = (
        df[year_col].map(_year_from_date)
        if year_col is not None
        else df[date_col].map(_year_from_date)
    )
    df = df.assign(_year=year)
    df = df[df["_year"].between(1986, 2024, inclusive="both")].copy()

    direct = _direct_record_mask(df, accuracy_col, estimate_col)
    whole = _whole_colony_mask(df, plot_col, assume_whole_colony_extract)
    not_merged = _not_merged_mask(df, comments_col)

    df = df[direct & whole & not_merged].copy()
    df["_species"] = df[species_col].map(_norm)
    df["_country"] = df[country_col].map(lambda x: str(x).strip() if not pd.isna(x) else "")
    df["_site_id"] = df[site_id_col].map(lambda x: str(x).strip())
    df["_site"] = df[site_col].map(lambda x: str(x).strip())
    df["_master"] = df[master_col].map(lambda x: str(x).strip())
    df["_master_norm"] = df[master_col].map(_norm)
    df["_unit"] = df[unit_col].map(lambda x: str(x).strip())
    df["_method"] = df[method_col].map(lambda x: str(x).strip()) if method_col else ""
    df["year"] = df["_year"].astype(int)

    # Sensitive and exposed pilot exclusions.
    df = df[~df["_species"].isin(SENSITIVE)].copy()
    pilot = df["_species"].str.contains("kittiwake", regex=False) & (df["_master_norm"] == EXPOSED_MASTER)
    df = df[~pilot].copy()

    # Competing rows at Site x year x species x master x unit are unavailable.
    key = ["_species", "_master", "_unit", "_site_id", "year"]
    dup_n = df.groupby(key, dropna=False).size().rename("_n").reset_index()
    unique_keys = dup_n[dup_n["_n"] == 1][key]
    df = df.merge(unique_keys, on=key, how="inner")

    # Method stability within child Site: <=1 non-missing method over the primary record set.
    if method_col:
        method_n = (
            df[df["_method"].map(_norm) != ""]
            .groupby(["_species", "_master", "_unit", "_site_id"])["_method"]
            .nunique()
            .rename("_method_n")
            .reset_index()
        )
        df = df.merge(method_n, on=["_species", "_master", "_unit", "_site_id"], how="left")
        df["_method_n"] = df["_method_n"].fillna(0)
        df = df[df["_method_n"] <= 1].copy()

    eligible = []
    group_cols = ["_species", "_master", "_unit"]
    for (species, master, unit), g in df.groupby(group_cols, sort=True):
        panel = g.rename(columns={"_site_id": "site_id"})
        outcome = _roster_from_missingness(panel)
        if outcome is None:
            continue
        roster, common_years = outcome
        span = max(common_years) - min(common_years)
        if span < MIN_SPAN:
            continue

        retained = g[g["_site_id"].isin(roster) & g["year"].isin(common_years)].copy()
        countries = sorted(set(x for x in retained["_country"] if x))
        site_names = {
            site_id: sorted(set(retained.loc[retained["_site_id"] == site_id, "_site"]))[0]
            for site_id in roster
        }
        methods = {}
        for site_id in roster:
            vals = sorted(
                set(
                    x for x in retained.loc[retained["_site_id"] == site_id, "_method"].astype(str)
                    if _norm(x)
                )
            )
            methods[site_id] = vals[0] if vals else None

        eligible.append({
            "species": species,
            "master_site": master,
            "unit": unit,
            "countries": countries,
            "retained_site_ids": roster,
            "retained_site_names": site_names,
            "stable_method_by_site": methods,
            "n_sites": len(roster),
            "n_complete_years": len(common_years),
            "first_complete_year": min(common_years),
            "last_complete_year": max(common_years),
            "calendar_span_years": span,
            "complete_years": common_years,
        })

    species_n = len(set(x["species"] for x in eligible))
    regions = sorted(set(r for x in eligible for r in x["countries"]))
    go = len(eligible) >= 20 and species_n >= 5 and len(regions) >= 3

    return {
        "schema_version": 1,
        "analysis_id": "mina-smp-master-site-support-gate-v1",
        "status": "outcome_blind_support_gate_only",
        "source": {
            "path": path.name,
            "sha256": source_sha,
            "raw_rows": int(len(_load(path))),
            "count_field_present_but_dropped_before_analysis": bool(count_field_present),
            "plot_field_present": bool(plot_col is not None),
            "assume_whole_colony_extract": bool(assume_whole_colony_extract),
        },
        "frozen_thresholds": {
            "minimum_site_years": MIN_SITE_YEARS,
            "minimum_sites": MIN_SITES,
            "minimum_complete_years": MIN_COMPLETE_YEARS,
            "minimum_calendar_span_years": MIN_SPAN,
        },
        "eligible_panel_count": len(eligible),
        "eligible_species_count": species_n,
        "broad_regions": regions,
        "broad_region_count": len(regions),
        "eligible_panels": eligible,
        "decision": {
            "go_macro": bool(go),
            "rule": ">=20 panels, >=5 species, >=3 broad geographic regions",
            "if_failed": "No threshold relaxation; keep Ecology Report standalone and close this SMP macro route.",
        },
        "forbidden_outputs_confirmed_absent": [
            "count magnitudes",
            "total abundance slopes",
            "decline/increase classification",
            "N_eff",
            "kappa",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--assume-whole-colony-extract", action="store_true")
    a = p.parse_args()
    result = analyze(a.input, assume_whole_colony_extract=a.assume_whole_colony_extract)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
