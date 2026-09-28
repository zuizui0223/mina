#!/usr/bin/env python3
"""Outcome-blind geographic coverage audit for the MAPPPD Pygoscelis lane."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyreadr

PINNED = "88c73a507e0921b2541c218c71eaf16721bc6502"
SPECIES = ("ADPE", "CHPE", "GEPE")


def _load(path: Path, expected: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(path))
    if expected in result:
        value = result[expected]
    elif len(result) == 1:
        value = next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(result)}")
    if not isinstance(value, pd.DataFrame):
        raise TypeError(expected)
    return value


def _eligible_units(root: Path, n_min: int, span_min: int) -> pd.DataFrame:
    obs = _load(root / "data" / "penguin_obs.rda", "penguin_obs")
    nest = obs[
        obs["species_id"].isin(SPECIES)
        & (obs["type"] == "nests")
        & obs["count"].notna()
    ].copy()
    nest["year"] = pd.to_numeric(nest["year"], errors="coerce")
    nest = nest.dropna(subset=["year"])

    rows = []
    for (site_id, species_id), local in nest.groupby(["site_id", "species_id"]):
        years = sorted(set(int(v) for v in local["year"]))
        if not years:
            continue
        span = max(years) - min(years)
        if len(years) >= n_min and span >= span_min:
            rows.append(
                {
                    "site_id": str(site_id),
                    "species_id": str(species_id),
                    "n_years": len(years),
                    "first_year": min(years),
                    "last_year": max(years),
                    "span_years": span,
                }
            )
    return pd.DataFrame(rows)


def _clean(value) -> str:
    if pd.isna(value):
        return "NA"
    return str(value)


def _region_summary(units: pd.DataFrame, sites: pd.DataFrame) -> list[dict]:
    joined = units.merge(
        sites[["site_id", "region", "ccamlr_id", "latitude", "longitude"]],
        on="site_id",
        how="left",
        validate="many_to_one",
    )
    out = []
    all_sites_by_region = (
        sites.assign(region_clean=sites["region"].map(_clean))
        .groupby("region_clean")["site_id"]
        .nunique()
        .to_dict()
    )
    for region, local in joined.assign(
        region_clean=joined["region"].map(_clean)
    ).groupby("region_clean"):
        species_counts = (
            local["species_id"].value_counts().sort_index().to_dict()
        )
        candidate_sites = int(local["site_id"].nunique())
        all_sites = int(all_sites_by_region.get(region, 0))
        out.append(
            {
                "region": region,
                "site_species_units": int(len(local)),
                "distinct_candidate_sites": candidate_sites,
                "all_apbp_sites_in_region": all_sites,
                "candidate_site_fraction_of_all_sites": (
                    candidate_sites / all_sites if all_sites else None
                ),
                "species_units": {
                    str(k): int(v) for k, v in species_counts.items()
                },
                "latitude_min": float(local["latitude"].min()),
                "latitude_max": float(local["latitude"].max()),
            }
        )
    return sorted(out, key=lambda row: (-row["site_species_units"], row["region"]))


def _ccamlr_summary(units: pd.DataFrame, sites: pd.DataFrame) -> list[dict]:
    joined = units.merge(
        sites[["site_id", "ccamlr_id"]],
        on="site_id",
        how="left",
        validate="many_to_one",
    )
    joined["ccamlr_clean"] = joined["ccamlr_id"].map(_clean)
    out = []
    for ccamlr, local in joined.groupby("ccamlr_clean"):
        out.append(
            {
                "ccamlr_id": ccamlr,
                "site_species_units": int(len(local)),
                "distinct_candidate_sites": int(local["site_id"].nunique()),
                "species_units": {
                    str(k): int(v)
                    for k, v in local["species_id"]
                    .value_counts()
                    .sort_index()
                    .to_dict()
                    .items()
                },
            }
        )
    return sorted(out, key=lambda row: (-row["site_species_units"], row["ccamlr_id"]))


def _latitude_bands(units: pd.DataFrame, sites: pd.DataFrame) -> list[dict]:
    joined = units.merge(
        sites[["site_id", "latitude"]],
        on="site_id",
        how="left",
        validate="many_to_one",
    )
    bins = [
        ("60-65S", -65.0, -60.0),
        ("65-70S", -70.0, -65.0),
        ("70-75S", -75.0, -70.0),
        ("75-80S", -80.0, -75.0),
        ("80-90S", -90.0, -80.0),
    ]
    out = []
    for label, low, high in bins:
        local = joined[(joined["latitude"] >= low) & (joined["latitude"] < high)]
        out.append(
            {
                "band": label,
                "site_species_units": int(len(local)),
                "distinct_candidate_sites": int(local["site_id"].nunique()),
            }
        )
    return out


def audit(root: Path) -> dict:
    sites = _load(root / "data" / "sites.rda", "sites")
    candidate = _eligible_units(root, 5, 10)
    strict = _eligible_units(root, 10, 20)

    if len(candidate) != 152:
        raise ValueError(f"candidate unit drift: {len(candidate)} != 152")
    if candidate["site_id"].nunique() != 122:
        raise ValueError(
            f"candidate site drift: {candidate['site_id'].nunique()} != 122"
        )
    if len(strict) != 92:
        raise ValueError(f"strict unit drift: {len(strict)} != 92")

    candidate_regions = _region_summary(candidate, sites)
    strict_regions = _region_summary(strict, sites)
    candidate_ccamlr = _ccamlr_summary(candidate, sites)
    strict_ccamlr = _ccamlr_summary(strict, sites)

    region_unit_counts = sorted(
        [int(row["site_species_units"]) for row in candidate_regions],
        reverse=True,
    )
    total = int(len(candidate))
    top1 = region_unit_counts[0] / total if total else None
    top3 = sum(region_unit_counts[:3]) / total if total else None

    species_region = {}
    joined = candidate.merge(
        sites[["site_id", "region"]],
        on="site_id",
        how="left",
        validate="many_to_one",
    )
    joined["region_clean"] = joined["region"].map(_clean)
    for species_id in SPECIES:
        local = joined[joined["species_id"] == species_id]
        species_region[species_id] = {
            str(k): int(v)
            for k, v in local["region_clean"]
            .value_counts()
            .sort_index()
            .to_dict()
            .items()
        }

    non_na_regions = {
        row["region"]
        for row in candidate_regions
        if row["region"] != "NA"
    }
    non_na_ccamlr = {
        row["ccamlr_id"]
        for row in candidate_ccamlr
        if row["ccamlr_id"] != "NA"
    }

    return {
        "schema_version": 1,
        "audit_id": "mina-mapppd-macro-geography-audit-v1",
        "mapppdr_commit": PINNED,
        "candidate_gate": {
            "site_species_units": int(len(candidate)),
            "distinct_sites": int(candidate["site_id"].nunique()),
            "regions": len(non_na_regions),
            "ccamlr_units": len(non_na_ccamlr),
            "largest_region_unit_fraction": top1,
            "top_three_regions_unit_fraction": top3,
        },
        "stricter_gate": {
            "site_species_units": int(len(strict)),
            "distinct_sites": int(strict["site_id"].nunique()),
        },
        "candidate_region_summary": candidate_regions,
        "stricter_region_summary": strict_regions,
        "candidate_ccamlr_summary": candidate_ccamlr,
        "stricter_ccamlr_summary": strict_ccamlr,
        "candidate_latitude_bands": _latitude_bands(candidate, sites),
        "species_by_region_candidate_units": species_region,
        "decision": {
            "broad_coverage_flag": (
                len(non_na_regions) >= 5 and len(non_na_ccamlr) >= 3
            ),
            "strong_regional_concentration_flag": (
                top1 is not None and top1 > 0.50
            ),
            "outcome_models_opened": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapppdr-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.mapppdr_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
