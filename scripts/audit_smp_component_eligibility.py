#!/usr/bin/env python3
"""Outcome-blind structural eligibility audit for SMP component panels.

IMPORTANT: this script intentionally never reads count magnitudes. It reads the
CSV header first and then loads only structural metadata columns.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


ALIASES = {
    "record_id": ["smp_recordid", "recordid", "record_id"],
    "species": ["species"],
    "master_site": ["smp_mastersite", "master site", "master_site", "mastersite"],
    "site_code": ["smp_sitecode", "site code", "site_code", "sitecode"],
    "site_name": ["smp_sitename", "site name", "site_name", "site"],
    "plot_name": ["smp_plotname", "plot name", "plot_name", "plot"],
    "date": ["startdate", "date", "survey date", "survey_date"],
    "year": ["year", "count year", "count_year"],
    "method": ["method", "count method", "count_method"],
    "unit": ["count_unit", "count unit", "unit"],
    "accuracy": ["accuracy", "countaccuracy", "count accuracy", "count_accuracy"],
    "estimate_type": ["estimatetype", "estimate type", "estimate_type"],
    "comments": ["comments", "comment"],
}

FORBIDDEN_COUNT_ALIASES = {
    "count",
    "count value",
    "count_value",
    "abundance",
    "total",
    "number",
}


def _norm(x: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(x).strip().lower()).strip()


def _resolve(columns: list[str]) -> dict[str, str]:
    by_norm = {_norm(c): c for c in columns}
    out = {}
    for key, aliases in ALIASES.items():
        for alias in aliases:
            n = _norm(alias)
            if n in by_norm:
                out[key] = by_norm[n]
                break
    return out


def _is_whole_colony(value: object) -> bool:
    if value is None or pd.isna(value):
        return True
    x = _norm(str(value))
    return x in {
        "",
        "whole colony",
        "whole colony count",
        "count at site level whole colony count",
        "site level whole colony",
    }


def _is_accurate(value: object) -> bool:
    if value is None or pd.isna(value):
        return True
    x = _norm(str(value))
    return x in {"acc", "accurate", "accurate count"}


def _year_series(df: pd.DataFrame, cols: dict[str, str]) -> pd.Series:
    if "year" in cols:
        return pd.to_numeric(df[cols["year"]], errors="coerce").astype("Int64")
    if "date" not in cols:
        raise ValueError("Need a year or date field for structural audit")
    return pd.to_datetime(df[cols["date"]], errors="coerce", dayfirst=True).dt.year.astype("Int64")


def audit(path: Path, min_components: int, min_complete: int, min_span: int) -> dict[str, object]:
    header = pd.read_csv(path, nrows=0)
    columns = list(header.columns)

    forbidden_present = [
        c for c in columns
        if _norm(c) in FORBIDDEN_COUNT_ALIASES
    ]

    resolved = _resolve(columns)
    required = {"species", "master_site", "site_code", "method", "unit"}
    missing = sorted(required - set(resolved))
    if missing:
        raise ValueError(f"Missing required structural columns: {missing}. Resolved={resolved}")

    structural_cols = sorted(set(resolved.values()))
    # Explicitly exclude any column whose normalized name looks like a count magnitude.
    structural_cols = [
        c for c in structural_cols
        if _norm(c) not in FORBIDDEN_COUNT_ALIASES
    ]

    df = pd.read_csv(path, usecols=structural_cols, dtype=str)
    df["_year"] = _year_series(df, resolved)

    # Primary route: whole-colony counts at stable SMP SiteCodes.
    if "plot_name" in resolved:
        whole = df[resolved["plot_name"]].map(_is_whole_colony)
        df = df[whole].copy()

    if "accuracy" in resolved:
        df["_accurate"] = df[resolved["accuracy"]].map(_is_accurate)
    else:
        df["_accurate"] = True

    # Do not allow one SiteCode to drift among MasterSites.
    site_master = (
        df[[resolved["site_code"], resolved["master_site"]]]
        .dropna()
        .drop_duplicates()
        .groupby(resolved["site_code"])[resolved["master_site"]]
        .nunique()
    )
    drifting_site_codes = sorted(site_master[site_master > 1].index.astype(str).tolist())

    # Exact duplicate structural records by site/species/year are flagged.
    dup_keys = [resolved["site_code"], resolved["species"], "_year"]
    duplicate_rows = int(df.duplicated(dup_keys, keep=False).sum())

    panel_rows = []
    group_cols = [resolved["master_site"], resolved["species"]]
    for (master, species), g0 in df.groupby(group_cols, dropna=False):
        g = g0[
            g0["_accurate"]
            & g0["_year"].notna()
            & ~g0[resolved["site_code"]].astype(str).isin(drifting_site_codes)
        ].copy()
        if g.empty:
            continue

        # Primary panels require one unit and one method across the panel.
        units = sorted(x for x in g[resolved["unit"]].dropna().astype(str).unique())
        methods = sorted(x for x in g[resolved["method"]].dropna().astype(str).unique())

        # Candidate core SiteCodes must individually meet the time-support minimums.
        eligible_sites = []
        for site, sg in g.groupby(resolved["site_code"]):
            years = sorted(set(int(y) for y in sg["_year"].dropna()))
            if len(years) >= min_complete and (max(years) - min(years) + 1) >= min_span:
                eligible_sites.append(str(site))

        eligible_sites = sorted(set(eligible_sites))
        if not eligible_sites:
            complete_years = []
        else:
            by_site_years = {
                site: set(int(y) for y in g[g[resolved["site_code"]].astype(str) == site]["_year"].dropna())
                for site in eligible_sites
            }
            complete_years = sorted(set.intersection(*(years for years in by_site_years.values())))

        span = (max(complete_years) - min(complete_years) + 1) if complete_years else 0
        compatible = len(units) == 1 and len(methods) == 1
        qualifies = (
            compatible
            and len(eligible_sites) >= min_components
            and len(complete_years) >= min_complete
            and span >= min_span
        )

        panel_rows.append({
            "master_site": None if pd.isna(master) else str(master),
            "species": None if pd.isna(species) else str(species),
            "candidate_component_count": len(eligible_sites),
            "candidate_site_codes": eligible_sites,
            "complete_season_count": len(complete_years),
            "first_complete_year": complete_years[0] if complete_years else None,
            "last_complete_year": complete_years[-1] if complete_years else None,
            "calendar_span_years": span,
            "unit_categories": units,
            "method_categories": methods,
            "compatible_single_unit_method": compatible,
            "primary_structurally_eligible": qualifies,
            "accurate_record_count_structural_only": int(len(g)),
        })

    eligible = [x for x in panel_rows if x["primary_structurally_eligible"]]
    species = sorted(set(x["species"] for x in eligible if x["species"] is not None))
    masters = sorted(set(x["master_site"] for x in eligible if x["master_site"] is not None))

    if len(eligible) >= 20 and len(species) >= 5 and len(masters) >= 15:
        decision = "pass"
    elif len(eligible) >= 8:
        decision = "marginal"
    else:
        decision = "fail"

    return {
        "schema_version": 1,
        "analysis_id": "mina-smp-component-structural-audit-v1",
        "status": "outcome_blind_no_count_magnitudes_loaded",
        "source_file": path.name,
        "header_count_like_columns_present_but_not_loaded": forbidden_present,
        "resolved_structural_columns": resolved,
        "primary_definition": {
            "parent": "SMP MasterSite x species",
            "component": "SMP SiteCode",
            "count_scope": "Whole Colony only",
            "accuracy": "ACC/accurate only where accuracy field exists",
        },
        "flags": {
            "site_codes_assigned_to_multiple_master_sites": drifting_site_codes,
            "duplicate_site_species_year_structural_rows": duplicate_rows,
        },
        "thresholds": {
            "min_components": min_components,
            "min_complete_seasons": min_complete,
            "min_calendar_span_years": min_span,
        },
        "summary": {
            "candidate_panel_count_all": len(panel_rows),
            "eligible_panel_count": len(eligible),
            "eligible_species_count": len(species),
            "eligible_species": species,
            "eligible_master_site_count": len(masters),
            "decision": decision,
        },
        "panels": panel_rows,
        "interpretation_boundary": [
            "No count magnitude column is loaded by this script.",
            "Eligibility is structural only and does not reveal decline direction, N_eff or kappa.",
            "Method/unit incompatibility fails the primary panel rather than being repaired after outcomes are seen.",
            "Plot-level colony-count analyses, if available, require a separate frozen audit and are not mixed with MasterSite > Site panels.",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--min-components", type=int, default=3)
    p.add_argument("--min-complete-seasons", type=int, default=10)
    p.add_argument("--min-span-years", type=int, default=12)
    a = p.parse_args()

    result = audit(a.csv, a.min_components, a.min_complete_seasons, a.min_span_years)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
